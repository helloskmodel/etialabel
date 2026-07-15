#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ETIA · Selected Harsh Environment Labels (Featured Solutions). Runs after gen_heatproof.

Builds /featured-solutions/ center (all 8, filter by harsh condition) + landing pages for
products without an existing canonical page (6). Products that map to an existing product
page (HP900->hp-900, HP CX->hp-cbr-cx2) link there — no duplicate. Only verified claims
render; unknown performance fields show 'Contact ETIA'. No values invented.
"""
import json, os, sys
BUILD=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,BUILD)
import gen_heatproof as hp
ROOT=hp.ROOT; SITE=hp.SITE; LANGS=hp.LANGS; PREFIX=hp.PREFIX; HREFLANG=hp.HREFLANG
esc=hp.esc; L=hp.L; page=hp.page
DATA=json.load(open(os.path.join(BUILD,"data","featured.json")))
PRODUCTS=DATA["products"]
CONDS={c["slug"]:c for c in DATA["conditions"]}
CENTER=DATA["center_route"]
URLS=[]
def track(p,g): URLS.append((p,g))
def u_land(p): return "/products/%s/"%p["maps_to"] if p["maps_to"] else "%s%s/"%(CENTER,p["slug"])

VERIFY_EN="Performance depends on the real process. Test the actual material through your printer, surface, chemistry and exposure before production. A peak temperature is not a continuous-use rating; chemical resistance must be validated by medium and time."
VERIFY_ZH="性能取决于真实工况。量产前请以实际材料通过您的打印机、表面、化学品与暴露条件测试。峰值温度不等于长期使用温度;耐化学性须按介质与时间验证。"

def cond_pills(p,lang):
    return "".join('<a class="pill tag" href="%s?c=%s">%s</a>'%(L(lang,CENTER),c,esc(CONDS[c]["zh"] if lang=="zh" else CONDS[c]["en"])) for c in p["harsh_conditions"])
def perf_tags(p,lang):
    return "".join('<span class="pill">%s</span>'%esc(t) for t in (p["tags_zh"] if lang=="zh" else p["tags_en"]))

def card(p,lang):
    verified=('<div class="rows" style="color:var(--green-d)"><b>✓ %s</b></div>'%esc(p["verified_claim_zh"] if lang=="zh" else p["verified_claim_en"])) if p["verified_claim_en"] else ""
    cta_label=("查看方案" if lang=="zh" else "View Solution")
    return ('<div class="card fs" data-c="%s"><div class="rows"><b>%s</b></div>'
            '<div class="eyebrow" style="margin:2px 0">%s</div>'
            '<h3>%s</h3><p>%s</p>%s<div class="xlinks">%s</div>'
            '<div style="margin-top:12px"><a class="btn pri" style="padding:8px 16px;font-size:13px" href="%s">%s</a></div></div>')%(
        esc(" ".join(p["harsh_conditions"])),
        esc(p["harsh_zh"] if lang=="zh" else p["harsh_en"]),
        esc(p["industry_zh"] if lang=="zh" else p["industry_en"]),
        esc(p["model"]),esc(p["one_liner_zh"] if lang=="zh" else p["one_liner_en"]),
        verified, perf_tags(p,lang), L(lang,u_land(p)), cta_label)

FILTER_JS="""<script>
(function(){var cur=null;
 function apply(){document.querySelectorAll('.fs').forEach(function(c){
   var v=(c.getAttribute('data-c')||'').split(' ');c.style.display=(!cur||v.indexOf(cur)>=0)?'':'none';});}
 document.querySelectorAll('.cchip').forEach(function(b){b.addEventListener('click',function(){
   var s=b.getAttribute('data-s');
   if(cur===s){cur=null;b.classList.remove('on');}else{cur=s;document.querySelectorAll('.cchip').forEach(function(x){x.classList.remove('on');});b.classList.add('on');}
   apply();});});
 var q=(location.search.match(/[?&]c=([^&]+)/)||[])[1];
 if(q){var b=document.querySelector('.cchip[data-s="'+q+'"]');if(b)b.click();}
})();
</script>"""
FS_CSS="""<style>.cchip{font-size:13px;font-weight:600;padding:7px 13px;border-radius:20px;background:#fff;border:1px solid var(--line);color:var(--mut);cursor:pointer;margin:0 4px 6px 0}.cchip:hover{border-color:var(--blue);color:var(--blue)}.cchip.on{background:var(--blue);color:#fff;border-color:var(--blue)}.card.fs .eyebrow{color:var(--blue)}</style>"""

def cta_fs(lang):
    if lang=="zh":
        return ('<div class="cta"><div class="ic">⚡</div><h3>在您的真实工艺中测试材料。</h3>'
                '<p>提交温度、表面、化学品、打印方式与标签尺寸,申请进一步选型或样品测试。</p>'
                '<div class="btns"><a class="btn pri" href="%s">申请样品</a><a class="btn on-dark" href="%s">咨询工程师</a></div></div>')%(L(lang,"/contact/"),L(lang,"/contact/"))
    return ('<div class="cta"><div class="ic">⚡</div><h3>Test the material in your real process.</h3>'
            '<p>Send your temperature, surface, chemicals, print method and label size to request selection support or sample testing.</p>'
            '<div class="btns"><a class="btn pri" href="%s">Request a Sample</a><a class="btn on-dark" href="%s">Discuss Your Application</a></div></div>')%(L(lang,"/contact/"),L(lang,"/contact/"))

def build_center(lang):
    path=CENTER
    chips="".join('<button type="button" class="cchip" data-s="%s">%s</button>'%(c["slug"],esc(c["zh"] if lang=="zh" else c["en"])) for c in DATA["conditions"])
    cards="".join(card(p,lang) for p in sorted(PRODUCTS,key=lambda x:x["featured_order"]))
    body=(FS_CSS+
      '<section class="blk"><div class="wrap"><div class="sub">%s</div>'
      '<div style="margin:10px 0 4px">%s</div><div class="grid">%s</div></div></section>'
      '<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'
      '<div class="wrap">%s</div>'+FILTER_JS)%(
        ("面向极端温度、化学品、磨损、油污与防篡改要求的严苛环境标签材料。按严苛工况筛选。" if lang=="zh"
         else "Label materials selected for demanding temperatures, chemicals, abrasion, challenging surfaces and secure identification. Filter by harsh condition."),
        chips, cards, (VERIFY_ZH if lang=="zh" else VERIFY_EN), cta_fs(lang))
    lst={"@context":"https://schema.org","@type":"ItemList","itemListElement":[
        {"@type":"ListItem","position":i+1,"name":"%s — %s"%(p["model"],p["harsh_en"]),"url":SITE+PREFIX[lang]+u_land(p)} for i,p in enumerate(sorted(PRODUCTS,key=lambda x:x["featured_order"]))]}
    crumb=[("Home","/"),("Featured Solutions",path)]
    hp.write(lang,path,page(lang,path,
        ("ETIA严苛环境标签精选 | ETIA" if lang=="zh" else "ETIA Selected Harsh Environment Labels | ETIA"),
        ("超低温、超高温、耐化学、耐磨与防篡改的严苛环境标签材料精选,按行业与工况筛选。" if lang=="zh"
         else "A selection of harsh-environment label materials for cryogenic, high-heat, chemical, abrasion and tamper-evident needs — filter by industry and condition."),
        ("ETIA严苛环境标签精选" if lang=="zh" else "ETIA Selected Harsh Environment Labels"),
        ("面向极端温度、化学品、磨损、油污与防篡改要求的严苛环境标签材料。" if lang=="zh"
         else "Label materials selected for demanding temperatures, chemicals, abrasion, challenging surfaces and secure identification."),
        body,crumb,schema_extra=[lst],active="products"))
    if lang=="en": track(path,"featured")

PERF_ROWS=[("Temperature / exposure","温度/暴露"),("Application temperature","贴标温度"),
 ("Surface / substrate","表面/基材"),("Adhesive","胶黏剂"),("Facestock","面材"),
 ("Printing method","打印方式"),("Chemical resistance","耐化学"),("Abrasion resistance","耐磨"),
 ("Outdoor durability","户外耐久"),("Certifications / compliance","认证/合规"),("Recommended ribbon","推荐碳带")]

def build_landing(lang,p):
    path="%s%s/"%(CENTER,p["slug"])
    verified=('<div class="verify" style="background:#eef7ea;border-color:#bfe0b0;color:#276527"><b>✓ %s</b></div>'%esc(p["verified_claim_zh"] if lang=="zh" else p["verified_claim_en"])) if p["verified_claim_en"] else ""
    # performance table — unknown fields show Contact ETIA (never invented)
    contact=("联系 ETIA" if lang=="zh" else "Contact ETIA")
    prows="".join('<tr><td>%s</td><td>%s</td></tr>'%(esc(z if lang=="zh" else e),contact) for e,z in PERF_ROWS)
    apps="".join('<li>%s</li>'%esc(a) for a in (p["applications_zh"] if lang=="zh" else p["applications_en"]))
    # related: link to industry/material hubs (max 3)
    rel=[("/featured-solutions/",("全部严苛环境标签" if lang=="zh" else "All Harsh Environment Labels"))]
    if "pcb" in " ".join(p["harsh_conditions"]) or p["id"] in ("fps-xf-581","fps-apex"):
        rel.append(("/materials/polyimide-pi-label-materials/",("聚酰亚胺材料中心" if lang=="zh" else "Polyimide Material Center")))
    rel.append(("/contact/",("咨询工程师" if lang=="zh" else "Talk to an Engineer")))
    rellinks="".join('<a href="%s">%s</a>'%(L(lang,u),esc(t)) for u,t in rel[:3])
    faq=build_faq(p,lang)
    body=(
      '<section class="blk"><div class="wrap"><div class="xlinks">%s</div>%s'
      '<div style="margin-top:10px">%s</div></div></section>'
      '<section class="blk"><div class="wrap"><h2>%s</h2><p style="color:var(--mut);max-width:48em">%s</p></div></section>'
      '<section class="blk" style="background:var(--bg)"><div class="wrap"><h2>%s</h2><ul class="checks">%s</ul></div></section>'
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="tablewrap"><table><tbody>%s</tbody></table></div>'
      '<p style="font-size:13px;color:var(--mut);margin-top:8px">%s</p></div></section>'
      '<section class="blk"><div class="wrap"><h2>%s</h2>%s</div></section>'
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="xlinks">%s</div></div></section>'
      '<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'
      '<div class="wrap">%s</div>')%(
        perf_tags(p,lang), verified,
        cond_pills(p,lang),
        ("识别挑战" if lang=="zh" else "The Identification Challenge"),
        esc(p["challenge_zh"] if lang=="zh" else p["challenge_en"]) if p["challenge_en"] else "",
        ("典型应用" if lang=="zh" else "Typical Applications"), apps or "<li>—</li>",
        ("性能概览" if lang=="zh" else "Performance Overview"), prows,
        ("未列出的字段请联系 ETIA 获取核验数据,不作推测。" if lang=="zh" else "Fields shown as Contact ETIA are provided on request with verified data — never estimated."),
        ("选型与验证说明" if lang=="zh" else "Selection & Validation Notes"),
        '<p style="color:var(--mut);max-width:48em">%s</p>'%(VERIFY_ZH if lang=="zh" else VERIFY_EN),
        ("相关方案" if lang=="zh" else "Related Solutions"), rellinks,
        faq, cta_fs(lang))
    ind=p["industry_zh"] if lang=="zh" else p["industry_en"]
    h1="%s %s"%(p["harsh_zh"] if lang=="zh" else p["harsh_en"], p["model"])
    crumb=[("Home","/"),("Featured Solutions",CENTER),(ind,CENTER),("%s"%p["model"],path)]
    hp.write(lang,path,page(lang,path,
        "%s %s | ETIA"%((p["harsh_zh"] if lang=="zh" else p["harsh_en"]),p["model"]),
        esc(p["one_liner_zh"] if lang=="zh" else p["one_liner_en"])[:157],
        h1, esc(p["one_liner_zh"] if lang=="zh" else p["one_liner_en"]),
        body, crumb, active="products"))
    if lang=="en": track(path,"featured")

def build_faq(p,lang):
    # 3 honest, product-specific Q&A; no invented specs
    qs=[]
    if lang=="zh":
        qs.append(("这些温度是长期使用温度吗?","不是。列出的温度为制程/暴露条件,不等同于长期连续使用温度,请以实际工况验证。"))
        qs.append(("能提供样品测试吗?","可以。请提供温度、表面、化学品、打印方式与标签尺寸,我们安排样品与选型建议。"))
        qs.append(("认证信息如何获取?","认证与合规须绑定具体型号与结构;请联系 ETIA 获取该型号的核验资料。"))
    else:
        qs.append(("Are these temperatures continuous-use ratings?","No. Listed temperatures are process/exposure conditions, not continuous-use ratings — validate against your real process."))
        qs.append(("Can I get a sample to test?","Yes. Share temperature, surface, chemistry, print method and label size and we'll arrange samples and selection support."))
        qs.append(("How do I get certification data?","Certifications bind to the specific model and construction — contact ETIA for the verified data sheet for this model."))
    items="".join('<details><summary>%s</summary><p>%s</p></details>'%(esc(q),esc(a)) for q,a in qs)
    return '<div class="faq">%s</div>'%items

def build_sitemap():
    fn="sitemap-featured.xml"
    xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    for p,_ in URLS:
        xml+='  <url><loc>%s%s</loc>'%(SITE,p)
        for lg in LANGS: xml+='<xhtml:link rel="alternate" hreflang="%s" href="%s%s%s"/>'%(HREFLANG[lg],SITE,PREFIX[lg],p)
        xml+='</url>\n'
    xml+='</urlset>\n'; open(os.path.join(ROOT,fn),"w").write(xml)
    idxp=os.path.join(ROOT,"sitemap-index.xml")
    if os.path.isfile(idxp):
        idx=open(idxp).read()
        if fn not in idx: idx=idx.replace('</sitemapindex>','  <sitemap><loc>%s/%s</loc></sitemap>\n</sitemapindex>'%(SITE,fn)); open(idxp,"w").write(idx)

def build_all():
    for lang in LANGS:
        build_center(lang)
        for p in PRODUCTS:
            if not p["maps_to"]: build_landing(lang,p)

def main():
    build_all(); build_sitemap()
    from collections import Counter
    print("FEATURED EN canonical URLs:",len(URLS)); print(Counter(g for _,g in URLS))

if __name__=="__main__": main()
