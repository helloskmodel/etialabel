#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ETIA · Electronics & PCB / Polyimide (Polyonics-led). Runs after gen_heatproof.

Two entries: By Industry (Electronics & PCB) process categories + By Material (Polyimide)
product line -> shared Polyonics product pages. Each page carries a 'Related Products in the
Market' cross-reference (equivalence-by-construction). No numeric temperatures invented.
"""
import json, os, sys
BUILD=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,BUILD)
import gen_heatproof as hp
ROOT=hp.ROOT; SITE=hp.SITE; LANGS=hp.LANGS; PREFIX=hp.PREFIX; HREFLANG=hp.HREFLANG
esc=hp.esc; L=hp.L; page=hp.page
DATA=json.load(open(os.path.join(BUILD,"data","pcb.json")))
PRODUCTS={p["id"]:p for p in DATA["products"]}
CATS={c["slug"]:c for c in DATA["categories"]}
CATMKT=DATA["category_market"]

URLS=[]
def track(p,g): URLS.append((p,g))
HUB="/industries/electronics-pcb/"; MAT="/materials/polyimide-pi-label-materials/"  # PI center (gen_pi)
def u_cat(s): return "%s%s/"%(HUB,s)
def u_prod(s): return "/products/%s/"%s
def u_brand(): return "/brands/polyonics/electronics-pcb/"

VERIFY_EN="Material performance depends on the complete construction and process. Confirm face material, adhesive, liner, print or laser settings, surface, temperature profile, chemistry, dwell time and application method through testing before production."
VERIFY_ZH="材料表现取决于完整结构与工艺。量产前请通过测试确认面材、胶黏剂、离型层、打印或激光参数、表面、温度曲线、化学品、停留时间与贴标方式。"
XREF_EN='Cross-references are equivalence-by-construction (facestock, adhesive class, temperature tier, finish, ESD), not one-to-one certified equivalents. Confirm by sample testing before production.'
XREF_ZH='对应关系基于材料构造等效(面材/胶系/耐温档/表面/ESD),非逐一官方认证。量产前请通过样品测试确认。'

def esd_pill(p,lang):
    return '<span class="pill tag">%s</span>'%("ESD 静电耗散" if lang=="zh" else "ESD") if p["esd"] else ""
def onreq_pill(p,lang):
    return '<span class="pill">%s</span>'%("按需供应" if lang=="zh" else "On request") if p["on_request"] else ""

def prod_card(p,lang):
    return ('<a class="card" href="%s"><h3>%s</h3><div class="rows">%s %s</div><p>%s</p></a>')%(
        L(lang,u_prod(p["slug"])), esc(p["product_name"]), esd_pill(p,lang), onreq_pill(p,lang),
        esc(p["brochure_direction_zh"] if lang=="zh" else p["brochure_direction_en"]))

def products_for_cat(slug): return [PRODUCTS[i] for i in PRODUCTS if slug in PRODUCTS[i]["application_categories"]]

def market_table_product(p,lang):
    e=p["market_equivalents"]
    head=(["品牌","对应型号"] if lang=="zh" else ["Brand","Equivalent model"])
    rows=[("Polyonics ("+("本页主推" if lang=="zh" else "this page")+")", p["product_name"].replace("Polyonics ",""))]
    for k,label in [("brady","Brady"),("etia","ETIA"),("3m","3M"),("avery","Avery Dennison")]:
        if e.get(k): rows.append((label,e[k]))
    tr="".join('<tr><td>%s</td><td class="mono">%s</td></tr>'%(esc(b),esc(m)) for b,m in rows)
    return ('<div class="tablewrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
            '<p style="font-size:13px;color:var(--mut);margin-top:8px">%s</p>')%(
        "".join("<th>%s</th>"%h for h in head), tr, (XREF_ZH if lang=="zh" else XREF_EN))

def market_table_category(slug,lang):
    rows=CATMKT.get(slug)
    if not rows: return ""
    head=(["类别","Polyonics","Brady","ETIA","3M","Avery Dennison"] if lang=="zh"
          else ["Category","Polyonics","Brady","ETIA","3M","Avery Dennison"])
    tr="".join('<tr><td>%s</td><td class="mono">%s</td><td class="mono">%s</td><td class="mono">%s</td><td class="mono">%s</td><td class="mono">%s</td></tr>'%(
        esc(r["cat_zh"] if lang=="zh" else r["cat_en"]),esc(r["polyonics"]),esc(r["brady"]),esc(r["etia"]),esc(r["3m"]),esc(r["avery"])) for r in rows)
    return ('<div class="tablewrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
            '<p style="font-size:13px;color:var(--mut);margin-top:8px">%s</p>')%(
        "".join("<th>%s</th>"%h for h in head),tr,(XREF_ZH if lang=="zh" else XREF_EN))

def itemlist(items,lang):
    return {"@context":"https://schema.org","@type":"ItemList","itemListElement":[
        {"@type":"ListItem","position":i+1,"name":n,"url":SITE+PREFIX[lang]+u} for i,(n,u) in enumerate(items)]}

def cta_pcb(lang):
    if lang=="zh":
        return ('<div class="cta"><div class="ic">⚡</div><h3>始于应用。终于选对材料。</h3>'
                '<p>提供峰值/持续温度、回流或波峰焊路线、清洗化学品与循环次数、ESD要求与条码密度,我们从 Polyonics 聚酰亚胺中给出选型建议。</p>'
                '<div class="btns"><a class="btn pri" href="%s">咨询专家</a><a class="btn on-dark" href="%s">咨询工程师</a></div></div>')%(L(lang,"/contact/"),L(lang,"/contact/"))
    return ('<div class="cta"><div class="ic">⚡</div><h3>Start with the Application. Finish with the Right Material.</h3>'
            '<p>Share peak/continuous temperature, reflow or wave-solder route, wash chemistry and cycles, ESD needs and barcode density — we\'ll recommend from Polyonics polyimide materials.</p>'
            '<div class="btns"><a class="btn pri" href="%s">Talk to a Specialist</a><a class="btn on-dark" href="%s">Talk to an Engineer</a></div></div>')%(L(lang,"/contact/"),L(lang,"/contact/"))

def build_hub(lang):
    path=HUB
    catcards="".join('<a class="card" href="%s"><h3>%s</h3><p>%s</p></a>'%(
        L(lang,u_cat(c["slug"])),esc(c["title_zh"] if lang=="zh" else c["title_en"]),
        esc(c["lede_zh"] if lang=="zh" else c["lede_en"])[:96]) for c in DATA["categories"])
    body=(
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="sub">%s</div><div class="grid">%s</div></div></section>'
      '<section class="blk" style="background:var(--bg)"><div class="wrap"><h2>%s</h2><div class="sub">%s</div>'
      '<div class="xlinks"><a class="pill" href="%s">%s</a><a class="pill" href="%s">%s</a></div></div></section>'
      '<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'
      '<div class="wrap">%s</div>')%(
        ("按工艺查找" if lang=="zh" else "Find by process"),
        ("按 PCB 制造工艺选择聚酰亚胺标签:回流/波峰焊、非回流、后制程、自动剥离、遮蔽圆点、激光可标记。" if lang=="zh"
         else "Choose polyimide labels by PCB manufacturing process: reflow/wave-solder, non-reflow, post-process, auto-dispense, masking dots, laser-markable."), catcards,
        ("按材料查找" if lang=="zh" else "Find by material"),
        ("从材料角度浏览 Polyonics 聚酰亚胺产品线。" if lang=="zh" else "Browse the Polyonics polyimide product line from the material angle."),
        L(lang,MAT),("聚酰亚胺产品线" if lang=="zh" else "Polyimide product line"),
        L(lang,u_brand()),("Polyonics 品牌" if lang=="zh" else "Polyonics brand"),
        (VERIFY_ZH if lang=="zh" else VERIFY_EN), cta_pcb(lang))
    lst=itemlist([(c["title_en"],u_cat(c["slug"])) for c in DATA["categories"]],lang)
    crumb=[("Home","/"),("Industries & Applications","/industries/"),("Electronics & PCB",path)]
    hp.write(lang,path,page(lang,path,
        ("电子制造与PCB标签材料 | ETIA" if lang=="zh" else "Electronics & PCB Label Materials | ETIA"),
        ("面向回流焊、波峰焊与严苛清洗的 Polyonics 聚酰亚胺 PCB 标签,按工艺或材料查找。" if lang=="zh"
         else "Polyonics polyimide PCB labels for reflow, wave solder and harsh washes — find by process or material."),
        ("电子制造与PCB标签材料" if lang=="zh" else "Electronics & PCB Label Materials"),
        ("在高温、助焊剂、焊接和多轮清洗中保持 PCB 标识清晰与可追溯。ETIA 供应 Polyonics 聚酰亚胺材料并提供选型支持。" if lang=="zh"
         else "Keep PCB identification readable and traceable through heat, flux, solder and repeated washes. ETIA supplies Polyonics polyimide materials with selection support."),
        body,crumb,schema_extra=[lst],active="industries"))
    if lang=="en": track(path,"pcb")

def build_material(lang):
    path=MAT
    # group by process requirement
    reqs=[("General low-profile","通用低厚度",["polyonics-xf-533"]),
          ("Ultra-high-heat amber","琥珀超耐高温",["polyonics-xf-542"]),
          ("Ultra-thin ESD","超薄ESD",["polyonics-xf-101se","polyonics-xf-101me","polyonics-xf-101m"]),
          ("Standard-profile ESD","标准厚ESD",["polyonics-xf-102se"]),
          ("Harsh-wash without preheat","不依赖预热的耐清洗",["polyonics-xf-102g"]),
          ("Colour-coded high-temp","颜色区分耐高温",["polyonics-xf-505"]),
          ("Chemical/solvent (PET)","耐化学/溶剂(PET)",["polyonics-xf-446"])]
    blocks=""
    for en,zh,ids in reqs:
        cards="".join(prod_card(PRODUCTS[i],lang) for i in ids if i in PRODUCTS)
        blocks+='<section class="blk"><div class="wrap"><h2>%s</h2><div class="grid">%s</div></div></section>'%(esc(zh if lang=="zh" else en),cards)
    body=blocks+'<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section><div class="wrap">%s</div>'%(
        (VERIFY_ZH if lang=="zh" else VERIFY_EN),cta_pcb(lang))
    lst=itemlist([(PRODUCTS[i]["product_name"],u_prod(PRODUCTS[i]["slug"])) for i in PRODUCTS],lang)
    crumb=[("Home","/"),("Products","/products/"),("Polyimide",path)]
    hp.write(lang,path,page(lang,path,
        ("PCB聚酰亚胺标签材料 | ETIA" if lang=="zh" else "PCB Polyimide Label Materials | ETIA"),
        ("按工艺要求选择 Polyonics 聚酰亚胺:标准、超薄、ESD、耐高温与耐清洗结构。" if lang=="zh"
         else "Choose Polyonics polyimide by process requirement: standard, ultra-thin, ESD, high-temperature and harsh-wash constructions."),
        ("聚酰亚胺标签材料 —— 按材料" if lang=="zh" else "Polyimide Label Materials"),
        ("从材料角度浏览 Polyonics 聚酰亚胺产品线,先选材料再定尺寸。" if lang=="zh"
         else "Browse the Polyonics polyimide product line from the material angle — select material first, size second."),
        body,crumb,schema_extra=[lst],active="products"))
    if lang=="en": track(path,"pcb")

def build_category(lang,c):
    slug=c["slug"]; path=u_cat(slug); prods=products_for_cat(slug)
    cards="".join(prod_card(p,lang) for p in prods)
    prod_section=('<section class="blk"><div class="wrap"><h2>%s</h2><div class="grid">%s</div></div></section>'%(
        ("Polyonics 推荐材料" if lang=="zh" else "Polyonics recommended materials"),cards)) if prods else \
        ('<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'%(
        ("该类别 Polyonics 型号按需供应;具体产品选择须通过样品测试确认(confirmed by sample)。" if lang=="zh"
         else "Polyonics grades for this category are available on request; product selection to be confirmed by sample testing.")))
    mkt=market_table_category(slug,lang)
    mkt_section=('<section class="blk" style="background:var(--bg)"><div class="wrap"><h2>%s</h2>%s</div></section>'%(
        ("市场对应型号" if lang=="zh" else "Related products in the market"),mkt)) if mkt else ""
    others="".join('<a href="%s">%s</a>'%(L(lang,u_cat(x)),esc(CATS[x]["title_zh"] if lang=="zh" else CATS[x]["title_en"])) for x in CATS if x!=slug)
    body=(prod_section+mkt_section+
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="xlinks">%s</div></div></section>'
      '<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'
      '<div class="wrap">%s</div>')%(
        ("其他PCB类别" if lang=="zh" else "Other PCB categories"),others,
        (VERIFY_ZH if lang=="zh" else VERIFY_EN),cta_pcb(lang))
    lst=itemlist([(p["product_name"],u_prod(p["slug"])) for p in prods],lang) if prods else None
    title=c["title_zh"] if lang=="zh" else c["title_en"]
    crumb=[("Home","/"),("Industries & Applications","/industries/"),("Electronics & PCB",HUB),(c["title_en"],path)]
    hp.write(lang,path,page(lang,path,"%s | ETIA"%title,esc(c["lede_zh"] if lang=="zh" else c["lede_en"])[:157],
        title,esc(c["lede_zh"] if lang=="zh" else c["lede_en"]),body,crumb,schema_extra=[lst] if lst else None,active="industries"))
    if lang=="en": track(path,"pcb")

def build_brand(lang):
    path=u_brand(); prods=list(PRODUCTS.values())
    cards="".join(prod_card(p,lang) for p in prods)
    body=('<section class="blk"><div class="wrap"><div class="sub">%s</div></div></section>'
          '<section class="blk"><div class="wrap"><h2>%s</h2><div class="grid">%s</div></div></section>'
          '<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'
          '<div class="wrap">%s</div>')%(
        esc(DATA["brand"]["note_zh"] if lang=="zh" else DATA["brand"]["note_en"]),
        ("Polyonics 聚酰亚胺材料" if lang=="zh" else "Polyonics polyimide materials"),cards,
        (VERIFY_ZH if lang=="zh" else VERIFY_EN),cta_pcb(lang))
    lst=itemlist([(p["product_name"],u_prod(p["slug"])) for p in prods],lang)
    crumb=[("Home","/"),("Electronics & PCB",HUB),("Polyonics",path)]
    hp.write(lang,path,page(lang,path,
        ("Polyonics 聚酰亚胺PCB标签材料 | ETIA" if lang=="zh" else "Polyonics Polyimide PCB Label Materials | ETIA"),
        ("ETIA 供应的 Polyonics 聚酰亚胺 PCB 标签材料全系。" if lang=="zh" else "The Polyonics polyimide PCB label materials supplied by ETIA."),
        ("Polyonics 聚酰亚胺PCB标签材料" if lang=="zh" else "Polyonics Polyimide PCB Label Materials"),
        "",body,crumb,schema_extra=[lst],active="products"))
    if lang=="en": track(path,"pcb")

def build_product(lang,p):
    slug=p["slug"]; path=u_prod(slug)
    catbadges="".join('<a class="pill" href="%s">%s</a>'%(L(lang,u_cat(a)),esc(CATS[a]["title_zh"] if lang=="zh" else CATS[a]["title_en"])) for a in p["application_categories"])
    facts=[]
    def add(ke,kz,v):
        if v and v!="—": facts.append((kz if lang=="zh" else ke,v))
    add("Brand","品牌","Polyonics"); add("Construction","结构",p["construction"])
    add("Heat direction","耐热方向",p["heat_tier"]); add("Film colour","膜色",p["film_color"])
    add("Finish","表面",p["finish"])
    add("ESD","静电耗散",(("是" if lang=="zh" else "Yes") if p["esd"] else None))
    add("Availability","供货",(("按需供应" if lang=="zh" else "On request") if p["on_request"] else None))
    factrows="".join('<li><span>%s</span><span>%s</span></li>'%(esc(k),esc(v)) for k,v in facts)
    body=(
      '<section class="blk"><div class="wrap"><div class="xlinks">%s %s</div>'
      '<p style="color:var(--mut);max-width:48em;margin-top:12px">%s</p></div></section>'
      '<section class="blk" style="background:var(--bg)"><div class="wrap"><h2>%s</h2><ul class="specs">%s</ul></div></section>'
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="xlinks">%s</div></div></section>'
      '<section class="blk"><div class="wrap"><h2>%s</h2>%s</div></section>'
      '<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'
      '<div class="wrap">%s</div>')%(
        esd_pill(p,lang), onreq_pill(p,lang),
        esc(p["brochure_direction_zh"] if lang=="zh" else p["brochure_direction_en"]),
        ("材料结构" if lang=="zh" else "Material construction"),factrows,
        ("适用PCB工艺" if lang=="zh" else "Applicable PCB processes"),catbadges or "—",
        ("市场对应型号" if lang=="zh" else "Related products in the market"),market_table_product(p,lang),
        (VERIFY_ZH if lang=="zh" else VERIFY_EN),hp.cta2(lang,"product-detail"))
    name=p["product_name"]
    crumb=[("Home","/"),("Products","/products/"),("Polyonics",u_brand()),(name,path)]
    # no Product structured data (no offer/availability)
    hp.write(lang,path,page(lang,path,"%s | ETIA"%name,
        (("%s。%s"%(name,p["brochure_direction_zh"]))[:157] if lang=="zh" else ("%s — %s"%(name,p["brochure_direction_en"]))[:157]),
        name,"",body,crumb,active="products"))
    if lang=="en": track(path,"pcb")

def build_sitemap():
    fn="sitemap-pcb.xml"
    xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    for p,_ in URLS:
        xml+='  <url><loc>%s%s</loc>'%(SITE,p)
        for lg in LANGS: xml+='<xhtml:link rel="alternate" hreflang="%s" href="%s%s%s"/>'%(HREFLANG[lg],SITE,PREFIX[lg],p)
        xml+='</url>\n'
    xml+='</urlset>\n'; open(os.path.join(ROOT,fn),"w").write(xml)
    idxp=os.path.join(ROOT,"sitemap-index.xml")
    if os.path.isfile(idxp):
        idx=open(idxp).read()
        if fn not in idx:
            idx=idx.replace('</sitemapindex>','  <sitemap><loc>%s/%s</loc></sitemap>\n</sitemapindex>'%(SITE,fn)); open(idxp,"w").write(idx)

def build_all():
    for lang in LANGS:
        build_hub(lang)  # /materials/polyimide-pi-label-materials/ is built by gen_pi (PI center)
        for c in DATA["categories"]: build_category(lang,c)
        build_brand(lang)
        for p in DATA["products"]: build_product(lang,p)

def main():
    build_all(); build_sitemap()
    from collections import Counter
    print("PCB EN canonical URLs:",len(URLS)); print(Counter(g for _,g in URLS))

if __name__=="__main__": main()
