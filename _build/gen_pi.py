#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ETIA · Polyimide (PI) Material & Application Center. Runs after gen_heatproof/gen_pcb.

Phase 1 (CODEX BUILD SPEC): one Featured-Material page at
/materials/polyimide-pi-label-materials/ with three on-page pathways (Process/Performance/
Industry) + 8 Featured Solution families (POLYONICS/ETIA) + Avery/Brady/LINTEC related +
a client-side family filter. Also builds a /materials/ By-Material hub. No specs invented.
"""
import json, os, sys
BUILD=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,BUILD)
import gen_heatproof as hp
ROOT=hp.ROOT; SITE=hp.SITE; LANGS=hp.LANGS; PREFIX=hp.PREFIX; HREFLANG=hp.HREFLANG
esc=hp.esc; L=hp.L; page=hp.page
DATA=json.load(open(os.path.join(BUILD,"data","pi_center.json")))
CENTER=DATA["route"]; MATHUB="/materials/"
URLS=[]
def track(p,g): URLS.append((p,g))
def u_prod(slug): return "/products/%s/"%slug

VERIFY_EN="Temperatures, certifications and biocompatibility bind to the specific model and construction. Unlisted values are pending verification and are not shown. Confirm the current TDS before production."
VERIFY_ZH="温度、认证与生物相容性绑定具体型号与结构。未列出的数值为待核验状态,不予展示。量产前请核对最新技术数据表。"

def chip(kind,slug,label):
    return '<button type="button" class="fchip" data-k="%s" data-s="%s">%s</button>'%(kind,slug,esc(label))

def member_tag(m,lang):
    label="%s %s"%(m["brand"],m["model"])
    if m.get("slug"):
        return '<a class="pill" href="%s">%s</a>'%(L(lang,u_prod(m["slug"])),esc(label))
    return '<span class="pill">%s</span>'%esc(label)

def family_card(f,lang):
    tags="".join(member_tag(m,lang) for m in f["members"])
    dp=" ".join(f["process"]); dr=" ".join(f["performance"]); di=" ".join(f["industry"])
    brands=" · ".join(f["brands"])
    return ('<div class="card fam" data-p="%s" data-r="%s" data-i="%s">'
            '<div class="rows"><b>%s</b> · %s</div><h3>%s</h3><p>%s</p>'
            '<div class="xlinks">%s</div></div>')%(
        esc(dp),esc(dr),esc(di),esc(f["id"]),esc(brands),
        esc(f["zh"] if lang=="zh" else f["en"]),esc(f["note_zh"] if lang=="zh" else f["note_en"]),tags)

def related_table(lang):
    head=(["类别","Avery Dennison","Brady","LINTEC"] if lang=="zh" else ["Category","Avery Dennison","Brady","LINTEC"])
    rows="".join('<tr><td>%s</td><td class="mono">%s</td><td class="mono">%s</td><td class="mono">%s</td></tr>'%(
        esc(r["cat_zh"] if lang=="zh" else r["cat_en"]),esc(r["avery"]),esc(r["brady"]),esc(r["lintec"])) for r in DATA["related"])
    note=("对应关系基于材料构造等效,非逐一官方认证;量产前样品验证。PI 中心仅展示 POLYONICS/ETIA 与上述相关品牌。" if lang=="zh"
          else "Equivalence-by-construction, not certified 1:1; confirm by sample. The PI center shows only POLYONICS/ETIA and the related brands above.")
    return ('<div class="tablewrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
            '<p style="font-size:13px;color:var(--mut);margin-top:8px">%s</p>')%(
        "".join("<th>%s</th>"%h for h in head),rows,note)

FILTER_JS="""<script>
(function(){
 var cur={p:null,r:null,i:null};
 function apply(){
  document.querySelectorAll('.fam').forEach(function(c){
   var ok=true;
   ['p','r','i'].forEach(function(k){
     if(cur[k]){var v=(c.getAttribute('data-'+k)||'').split(' ');if(v.indexOf(cur[k])<0)ok=false;}
   });
   c.style.display=ok?'':'none';
  });
 }
 document.querySelectorAll('.fchip').forEach(function(b){
  b.addEventListener('click',function(){
   var k={process:'p',performance:'r',industry:'i'}[b.getAttribute('data-k')];
   var s=b.getAttribute('data-s');
   if(cur[k]===s){cur[k]=null;b.classList.remove('on');}
   else{cur[k]=s;document.querySelectorAll('.fchip[data-k="'+b.getAttribute('data-k')+'"]').forEach(function(x){x.classList.remove('on');});b.classList.add('on');}
   apply();
  });
 });
 var clr=document.getElementById('pi-clear');
 if(clr)clr.addEventListener('click',function(){cur={p:null,r:null,i:null};document.querySelectorAll('.fchip').forEach(function(x){x.classList.remove('on');});apply();});
})();
</script>"""

PI_CSS="""<style>
.pathtabs{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0 16px}
.pathtabs a{font-size:14px;font-weight:700;padding:8px 16px;border-radius:22px;background:var(--bg);border:1px solid var(--line);color:var(--ink)}
.pathtabs a:hover{border-color:var(--blue);color:var(--blue);text-decoration:none}
.fchip{font-size:13px;font-weight:600;padding:7px 13px;border-radius:20px;background:#fff;border:1px solid var(--line);color:var(--mut);cursor:pointer;margin:0 4px 6px 0}
.fchip:hover{border-color:var(--blue);color:var(--blue)}
.fchip.on{background:var(--blue);color:#fff;border-color:var(--blue)}
.fam .rows b{color:var(--blue)}
#pi-clear{font-size:12.5px;color:var(--green);font-weight:700;cursor:pointer;background:none;border:none}
</style>"""

def cta_pi(lang):
    if lang=="zh":
        return ('<div class="cta"><div class="ic">⚡</div><h3>始于应用。终于选对材料。</h3>'
                '<p>提供制程温度、持续/峰值温度、ESD、耐化学、阻燃与打印要求,我们从 POLYONICS 与 ETIA 聚酰亚胺中给出建议。</p>'
                '<div class="btns"><a class="btn pri" href="%s">咨询专家</a><a class="btn on-dark" href="%s">咨询材料工程师</a></div></div>')%(L(lang,"/contact/"),L(lang,"/contact/"))
    return ('<div class="cta"><div class="ic">⚡</div><h3>Start with the Application. Finish with the Right Material.</h3>'
            '<p>Share process, continuous/peak temperature, ESD, chemical, flame and print requirements — we\'ll recommend from POLYONICS and ETIA polyimide materials.</p>'
            '<div class="btns"><a class="btn pri" href="%s">Talk to a Specialist</a><a class="btn on-dark" href="%s">Talk to a Materials Engineer</a></div></div>')%(L(lang,"/contact/"),L(lang,"/contact/"))

def taxo_section(lang, anchor, title_en, title_zh, sub_en, sub_zh, items, kind):
    chips="".join(chip(kind,it["slug"],(it["zh"] if lang=="zh" else it["en"])) for it in items)
    return ('<section class="blk" id="%s"><div class="wrap"><h2>%s</h2><div class="sub">%s</div>'
            '<div>%s</div></div></section>')%(
        anchor, esc(title_zh if lang=="zh" else title_en), esc(sub_zh if lang=="zh" else sub_en), chips)

def build_center(lang):
    path=CENTER
    eyebrow=("重点材料 · 聚酰亚胺 PI" if lang=="zh" else "Featured Material · Polyimide PI")
    pathnav=('<div class="pathtabs"><a href="#process">%s</a><a href="#performance">%s</a><a href="#industry">%s</a><a href="#featured">%s</a></div>'%(
        ("按制造工艺" if lang=="zh" else "By Process"),("按性能要求" if lang=="zh" else "By Performance"),
        ("按行业应用" if lang=="zh" else "By Industry"),("重点方案" if lang=="zh" else "Featured Solutions")))
    p_sec=taxo_section(lang,"process","Explore by Process","按制造工艺",
        "Select the manufacturing process; the featured solutions below filter to match.","选择制造工艺,下方重点方案随之筛选。",
        DATA["process"],"process")
    r_sec=taxo_section(lang,"performance","Explore by Performance","按性能要求",
        "Select the performance requirement. '300°C' is a process-exposure condition, not a continuous rating.","选择性能要求。'300℃'为制程暴露条件,非长期使用温度。",
        DATA["performance"],"performance")
    i_sec=taxo_section(lang,"industry","Explore by Industry","按行业应用",
        "Where PI materials are used; recommendations show only where verified products exist.","PI 材料的应用行业;仅在存在验证产品时显示推荐。",
        DATA["industry"],"industry")
    fams="".join(family_card(f,lang) for f in DATA["families"])
    feat=('<section class="blk" id="featured"><div class="wrap">'
          '<h2>%s</h2><div class="sub">%s</div>'
          '<div style="margin-bottom:12px">%s <button id="pi-clear" type="button">%s</button></div>'
          '<div class="grid">%s</div></div></section>')%(
        ("重点方案 —— POLYONICS / ETIA" if lang=="zh" else "Featured Solutions — POLYONICS / ETIA"),
        ("先展示产品族;点上方任一工艺/性能/行业筛选。" if lang=="zh" else "Product families first; click any Process / Performance / Industry chip above to filter."),
        ("筛选中:" if lang=="zh" else "Filtering:"),("清除" if lang=="zh" else "Clear"),
        fams)
    related=('<section class="blk" style="background:var(--bg)"><div class="wrap"><h2>%s</h2>%s</div></section>')%(
        ("市场相关产品 —— Avery Dennison · Brady · LINTEC" if lang=="zh" else "Related Products — Avery Dennison · Brady · LINTEC"),
        related_table(lang))
    body=(PI_CSS+
      '<div class="wrap"><div class="eyebrow" style="margin-top:6px">%s</div></div>%s'
      '<div class="wrap">%s</div>%s%s%s%s%s<div class="wrap">%s</div>%s')%(
        esc(eyebrow),
        '<div class="wrap">%s</div>'%pathnav,
        "", p_sec, r_sec, i_sec, feat, related, cta_pi(lang), FILTER_JS)
    lst={"@context":"https://schema.org","@type":"ItemList","itemListElement":[
        {"@type":"ListItem","position":i+1,"name":f["en"]} for i,f in enumerate(DATA["families"])]}
    crumb=[("Home","/"),("Products","/products/"),("Polyimide (PI)",path)]
    title=("聚酰亚胺PI耐高温标签材料｜PCB回流焊·防静电标签｜ETIA" if lang=="zh"
           else "Polyimide (PI) High-Temperature PCB Label Materials | ETIA")
    desc=("ETIA提供POLYONICS及ETIA聚酰亚胺PI耐高温标签材料,适用于PCB、SMT、回流焊、波峰焊、电子元件及高温制程追踪。可按温度、ESD、耐化学、阻燃、厚度、颜色和打印要求选型。" if lang=="zh"
          else "Explore POLYONICS and ETIA polyimide label materials for PCB assembly, SMT reflow, wave soldering and high-temperature process tracking. Filter by temperature, ESD, chemical resistance, flame retardancy and print requirements.")
    h1=("聚酰亚胺（PI）耐高温标签材料" if lang=="zh" else "Polyimide (PI) High-Temperature Label Materials")
    lede=("面向PCB、SMT、电子元件、半导体、汽车电子及工业高温制程的耐久标识材料。" if lang=="zh"
          else "Durable identification for PCB, SMT, electronic components, semiconductor, automotive electronics and industrial high-temperature processes.")
    hp.write(lang,path,page(lang,path,title,desc,h1,lede,body,crumb,schema_extra=[lst],active="products"))
    if lang=="en": track(path,"materials")

MATERIALS=[("polyimide-pi-label-materials","Polyimide (PI) High-Temperature Label Materials","聚酰亚胺（PI）耐高温标签材料",True),
 ("polyester-pet","Polyester (PET)","聚酯 (PET)",False),("vinyl","Vinyl","乙烯基",False),
 ("polypropylene-pp","Polypropylene (PP)","聚丙烯 (PP)",False),("paper","Paper","纸质",False),
 ("other-specialty","Other Specialty Materials","其他特种材料",False)]

def build_material_hub(lang):
    path=MATHUB
    cards=""
    for slug,en,zh,featured in MATERIALS:
        href=CENTER if featured else L(lang,"/contact/")
        badge=('<span class="pill tag">%s</span>'%("重点材料" if lang=="zh" else "Featured Material")) if featured else ('<span class="pill">%s</span>'%("即将上线" if lang=="zh" else "Coming soon"))
        cards+='<a class="card" href="%s"><div class="rows">%s</div><h3>%s</h3></a>'%(
            (L(lang,href) if featured else href), badge, esc(zh if lang=="zh" else en))
    body='<section class="blk"><div class="wrap"><div class="grid">%s</div></div></section><div class="wrap">%s</div>'%(cards,cta_pi(lang))
    crumb=[("Home","/"),("Products","/products/"),("By Material",path)]
    hp.write(lang,path,page(lang,path,
        ("按材料查找标签材料 | ETIA" if lang=="zh" else "Label Materials by Material | ETIA"),
        ("按材料浏览:聚酰亚胺(重点)、聚酯、乙烯基、聚丙烯、纸质及其他特种材料。" if lang=="zh"
         else "Browse by material: polyimide (featured), polyester, vinyl, polypropylene, paper and other specialty materials."),
        ("按材料查找" if lang=="zh" else "Label Materials by Material"),
        ("从材料角度选择标签结构;聚酰亚胺为重点材料中心。" if lang=="zh" else "Choose the label construction by material; polyimide is the featured material center."),
        body,crumb,active="products"))
    if lang=="en": track(path,"materials")

def build_sitemap():
    fn="sitemap-materials.xml"
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

def merge_redirects():
    import json as _j
    vp=os.path.join(ROOT,"vercel.json")
    cfg=_j.load(open(vp)) if os.path.isfile(vp) else {"cleanUrls":True,"trailingSlash":True,"redirects":[]}
    extra=[{"source":"/materials/polyimide","destination":CENTER,"permanent":True},
           {"source":"/pi","destination":CENTER,"permanent":True}]
    have={r["source"] for r in cfg.get("redirects",[])}
    for r in extra:
        if r["source"] not in have: cfg.setdefault("redirects",[]).append(r)
    open(vp,"w").write(_j.dumps(cfg,indent=2)+"\n")

def build_all():
    for lang in LANGS:
        build_material_hub(lang)
        build_center(lang)

def main():
    build_all(); build_sitemap(); merge_redirects()
    from collections import Counter
    print("PI-CENTER EN canonical URLs:",len(URLS)); print(Counter(g for _,g in URLS))

if __name__=="__main__": main()
