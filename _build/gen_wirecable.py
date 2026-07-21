#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ETIA · Wire & Cable (three pathways). Runs after gen_heatproof.

Explore by Application (8) + by Industry (8) + by Environment (6 site-wide).
Products = Avery Dennison flag/wrap; product-level environment specs bound to TDS
(marked needs_verification, not invented). Environment association carried at the
application level. Brady application methods referenced without inventing SKUs.
"""
import json, os, sys
BUILD=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,BUILD)
import gen_heatproof as hp
ROOT=hp.ROOT; SITE=hp.SITE; LANGS=hp.LANGS; PREFIX=hp.PREFIX; HREFLANG=hp.HREFLANG
esc=hp.esc; L=hp.L; page=hp.page
DATA=json.load(open(os.path.join(BUILD,"data","wirecable.json")))
PRODUCTS={p["id"]:p for p in DATA["products"]}
APPS={a["slug"]:a for a in DATA["applications"]}
INDS={i["slug"]:i for i in DATA["industries"]}
ENVS={e["slug"]:e for e in DATA["environments"]}

URLS=[]
def track(p,g): URLS.append((p,g))
HUB="/industries/wire-cable/"
def u_app(s): return "%s%s/"%(HUB,s)
def u_ind(s): return "%ssector/%s/"%(HUB,s)
def u_env(s): return "%senvironment/%s/"%(HUB,s)
def u_prod(s): return "/products/%s/"%s
def u_brand(): return "/brands/avery-dennison/wire-cable/"

VERIFY_EN="Industry names do not by themselves grant flame-retardant, UL, UV, low-smoke or sterilization performance. Product environment performance is bound to each TDS — verify before final claims."
VERIFY_ZH="行业名称本身不赋予阻燃、UL、UV、低烟或耐灭菌性能。产品的环境性能须绑定各自 TDS,发布最终声明前请核对。"
PENDING_EN="Product selection for this application is matched from verified materials and to be confirmed by sample testing."
PENDING_ZH="该应用的产品选择从已验证材料中匹配,并须通过样品测试确认(confirmed by sample)。"

def prod_card(p,lang):
    return ('<a class="card" href="%s"><h3>%s</h3><div class="rows"><b>%s</b> · %s</div><p>%s</p></a>')%(
        L(lang,u_prod(p["slug"])),esc(p["product_name"]),esc(p["part_number"]),esc(p["face_material"]),
        esc(p["product_description"]))
def products_for_app(slug): return [PRODUCTS[i] for i in PRODUCTS if slug in PRODUCTS[i]["application_categories"]]
def itemlist(items,lang):
    return {"@context":"https://schema.org","@type":"ItemList","itemListElement":[
        {"@type":"ListItem","position":i+1,"name":n,"url":SITE+PREFIX[lang]+u} for i,(n,u) in enumerate(items)]}

def cta_wc(lang):
    if lang=="zh":
        return ('<div class="cta"><div class="ic">⚡</div><h3>始于应用。终于选对材料。</h3>'
                '<p>提供线径与形式(旗型/缠绕/自覆膜/热缩/吊牌)、行业、环境(耐磨/潮湿/化学/高温)与打印方式,我们从 Avery Dennison 材料中给出建议。</p>'
                '<div class="btns"><a class="btn pri" href="%s">咨询专家</a><a class="btn on-dark" href="%s">咨询工程师</a></div></div>')%(L(lang,"/contact/"),L(lang,"/contact/"))
    return ('<div class="cta"><div class="ic">⚡</div><h3>Start with the Application. Finish with the Right Material.</h3>'
            '<p>Share cable size and format (flag / wrap / self-laminating / heat-shrink / tag), industry, environment (abrasion / moisture / chemical / heat) and print method — we\'ll recommend from Avery Dennison materials.</p>'
            '<div class="btns"><a class="btn pri" href="%s">Talk to a Specialist</a><a class="btn on-dark" href="%s">Talk to an Engineer</a></div></div>')%(L(lang,"/contact/"),L(lang,"/contact/"))

def build_hub(lang):
    path=HUB
    appcards="".join('<a class="card" href="%s"><h3>%s</h3><p>%s</p></a>'%(
        L(lang,u_app(a["slug"])),esc(a["title_zh"] if lang=="zh" else a["title_en"]),
        esc(a["desc_zh"] if lang=="zh" else a["desc_en"])[:88]) for a in DATA["applications"])
    indcards="".join('<a class="card" href="%s"><h3>%s</h3></a>'%(
        L(lang,u_ind(i["slug"])),esc(i["title_zh"] if lang=="zh" else i["title_en"])) for i in DATA["industries"])
    # environment: priority shown prominent, conditional noted
    envcards="".join('<a class="card" href="%s"><h3>%s</h3></a>'%(
        L(lang,u_env(s)),esc(ENVS[s]["title_zh"] if lang=="zh" else ENVS[s]["title_en"])) for s in DATA["priority_environments"])
    cond="".join('<a class="pill" href="%s">%s</a>'%(L(lang,u_env(s)),esc(ENVS[s]["title_zh"] if lang=="zh" else ENVS[s]["title_en"])) for s in DATA["conditional_environments"])
    body=(
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="sub">%s</div><div class="grid">%s</div></div></section>'
      '<section class="blk" style="background:var(--bg)"><div class="wrap"><h2>%s</h2><div class="sub">%s</div><div class="grid">%s</div></div></section>'
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="sub">%s</div><div class="grid">%s</div>'
      '<div class="xlinks" style="margin-top:10px">%s %s</div></div></section>'
      '<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'
      '<div class="wrap">%s</div>')%(
        ("按应用探索" if lang=="zh" else "Explore by Application"),
        ("旗型、缠绕、自覆膜、热缩套管、电缆吊牌及具体布线应用。" if lang=="zh" else "Flag, wrap-around, self-laminating, heat-shrink, cable tags and application-specific identification."),appcards,
        ("按行业探索" if lang=="zh" else "Explore by Industry"),
        ("工业制造、汽车、数据通信、电气系统、交通运输、能源与医疗设备。" if lang=="zh" else "Industrial manufacturing, automotive, data communications, electrical systems, transportation, energy and medical equipment."),indcards,
        ("按环境探索" if lang=="zh" else "Explore by Environment"),
        ("全站统一的环境入口。线缆页优先显示耐磨、潮湿、化学与高温。" if lang=="zh" else "The site-wide environment set. Wire & cable prioritizes abrasion, moisture, chemical and heat."),envcards,
        ("条件显示:" if lang=="zh" else "Conditional:"),cond,
        (VERIFY_ZH if lang=="zh" else VERIFY_EN),cta_wc(lang))
    lst=itemlist([(a["title_en"],u_app(a["slug"])) for a in DATA["applications"]],lang)
    crumb=[("Home","/"),("Industries & Applications","/industries/"),("Wire & Cable",path)]
    hp.write(lang,path,page(lang,path,
        ("电线电缆标签材料 | ETIA" if lang=="zh" else "Wire & Cable Label Materials | ETIA"),
        ("用于导线、电缆、线束、控制柜与网络基础设施的识别材料。三条链路:按应用、按行业、按环境。" if lang=="zh"
         else "Identification materials for wires, cables, harnesses, cabinets and network infrastructure. Three paths: by application, industry and environment."),
        ("电线电缆标签材料" if lang=="zh" else "Wire & Cable Label Materials"),
        ("用于导线、电缆、线束、控制柜与网络基础设施的可靠识别材料。ETIA 供应 Avery Dennison 材料并提供选型支持。" if lang=="zh"
         else "Reliable identification for wires, cables, harnesses, cabinets and network infrastructure. ETIA supplies Avery Dennison materials with selection support."),
        body,crumb,schema_extra=[lst],active="industries"))
    if lang=="en": track(path,"wirecable")

def build_app(lang,a):
    slug=a["slug"]; path=u_app(slug); prods=products_for_app(slug)
    if prods:
        cards="".join(prod_card(p,lang) for p in prods)
        psec='<section class="blk"><div class="wrap"><h2>%s</h2><div class="grid">%s</div></div></section>'%(
            ("Avery Dennison 材料" if lang=="zh" else "Avery Dennison materials"),cards)
    else:
        psec='<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'%(PENDING_ZH if lang=="zh" else PENDING_EN)
    envs=a["environments"]; envlinks="".join('<a href="%s">%s</a>'%(L(lang,u_env(e)),esc(ENVS[e]["title_zh"] if lang=="zh" else ENVS[e]["title_en"])) for e in envs)
    condlinks="".join('<a class="pill" href="%s">%s</a>'%(L(lang,u_env(e)),esc(ENVS[e]["title_zh"] if lang=="zh" else ENVS[e]["title_en"])) for e in a["environments_conditional"])
    others="".join('<a href="%s">%s</a>'%(L(lang,u_app(x)),esc(APPS[x]["title_zh"] if lang=="zh" else APPS[x]["title_en"])) for x in APPS if x!=slug)
    body=(psec+
      '<section class="blk" style="background:var(--bg)"><div class="wrap"><h2>%s</h2><div class="xlinks">%s</div>%s</div></section>'
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="xlinks">%s</div></div></section>'
      '<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'
      '<div class="wrap">%s</div>')%(
        ("相关环境" if lang=="zh" else "Related environments"),envlinks or "—",
        (('<div class="xlinks" style="margin-top:8px"><span style="font-size:12px;color:var(--faint)">%s</span> %s</div>'%(("条件:" if lang=="zh" else "Conditional:"),condlinks)) if condlinks else ""),
        ("其他线缆应用" if lang=="zh" else "Other wire & cable applications"),others,
        (VERIFY_ZH if lang=="zh" else VERIFY_EN),cta_wc(lang))
    lst=itemlist([(p["product_name"],u_prod(p["slug"])) for p in prods],lang) if prods else None
    title=a["title_zh"] if lang=="zh" else a["title_en"]
    crumb=[("Home","/"),("Industries & Applications","/industries/"),("Wire & Cable",HUB),(a["title_en"],path)]
    hp.write(lang,path,page(lang,path,"%s | ETIA"%title,esc(a["desc_zh"] if lang=="zh" else a["desc_en"])[:157],
        title,esc(a["desc_zh"] if lang=="zh" else a["desc_en"]),body,crumb,schema_extra=[lst] if lst else None,active="industries"))
    if lang=="en": track(path,"wirecable")

def build_industry(lang,i):
    slug=i["slug"]; path=u_ind(slug)
    applinks="".join('<a href="%s">%s</a>'%(L(lang,u_app(x)),esc(APPS[x]["title_zh"] if lang=="zh" else APPS[x]["title_en"])) for x in i["applications"])
    envlinks="".join('<a href="%s">%s</a>'%(L(lang,u_env(e)),esc(ENVS[e]["title_zh"] if lang=="zh" else ENVS[e]["title_en"])) for e in i["priority_environments"])
    # products only where verified relation (show_products) — via application overlap
    if i["show_products"]:
        prods=[]
        for x in i["applications"]:
            for p in products_for_app(x):
                if p not in prods: prods.append(p)
        psec=('<section class="blk"><div class="wrap"><h2>%s</h2><div class="grid">%s</div></div></section>'%(
            ("推荐材料" if lang=="zh" else "Recommended materials"),"".join(prod_card(p,lang) for p in prods))) if prods else ""
    else:
        psec='<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'%(
            ("该行业的产品推荐仅在存在对应验证材料时显示;当前按应用与环境聚合。" if lang=="zh"
             else "Product recommendations for this industry appear only where verified materials exist; currently aggregated by application and environment."))
    body=(
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="sub">%s</div></div></section>'
      '<section class="blk" style="background:var(--bg)"><div class="wrap"><h2>%s</h2><div class="xlinks">%s</div>'
      '<h2 style="margin-top:18px">%s</h2><div class="xlinks">%s</div></div></section>'
      '%s'
      '<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'
      '<div class="wrap">%s</div>')%(
        ("典型对象与场景" if lang=="zh" else "Typical objects & scenarios"),esc(i["objects_zh"] if lang=="zh" else i["objects_en"]),
        ("相关应用" if lang=="zh" else "Related applications"),applinks,
        ("重点环境" if lang=="zh" else "Key environments"),envlinks,
        psec,(VERIFY_ZH if lang=="zh" else VERIFY_EN),cta_wc(lang))
    title=i["title_zh"] if lang=="zh" else i["title_en"]
    crumb=[("Home","/"),("Wire & Cable",HUB),(i["title_en"],path)]
    hp.write(lang,path,page(lang,path,"%s — %s | ETIA"%(title,("线缆标识" if lang=="zh" else "Wire & Cable")),
        esc(i["objects_zh"] if lang=="zh" else i["objects_en"])[:157],
        ("%s线缆标识" % title if lang=="zh" else "%s — Wire & Cable Identification"%title),"",body,crumb,active="industries"))
    if lang=="en": track(path,"wirecable")

def build_env(lang,slug):
    e=ENVS[slug]; path=u_env(slug)
    apps=[a for a in DATA["applications"] if slug in a["environments"]]
    cond_apps=[a for a in DATA["applications"] if slug in a["environments_conditional"]]
    applinks="".join('<a href="%s">%s</a>'%(L(lang,u_app(a["slug"])),esc(a["title_zh"] if lang=="zh" else a["title_en"])) for a in apps)
    is_conditional=slug in DATA["conditional_environments"]
    if apps:
        note=("在电线电缆中,该环境通常与以下应用相关;具体产品的环境性能须按 TDS 确认。" if lang=="zh"
              else "In wire & cable, this environment typically relates to the applications below; product-level environment performance is confirmed per TDS.")
    else:
        note=("该环境保留为全站统一入口;仅在存在已验证线缆材料时显示产品结果。" if lang=="zh"
              else "This environment is kept as a site-wide entry; product results appear only where verified wire & cable materials exist.")
    body=(
      '<section class="blk"><div class="wrap"><div class="sub">%s</div></div></section>'
      '<section class="blk" style="background:var(--bg)"><div class="wrap"><h2>%s</h2><div class="xlinks">%s</div></div></section>'
      '<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'
      '<div class="wrap">%s</div>')%(
        note,
        ("相关线缆应用" if lang=="zh" else "Related wire & cable applications"),applinks or "—",
        (VERIFY_ZH if lang=="zh" else VERIFY_EN),cta_wc(lang))
    title=e["title_zh"] if lang=="zh" else e["title_en"]
    crumb=[("Home","/"),("Wire & Cable",HUB),(e["title_en"],path)]
    hp.write(lang,path,page(lang,path,"%s — %s | ETIA"%(title,("线缆" if lang=="zh" else "Wire & Cable")),
        esc(note)[:157],("%s(线缆)"%title if lang=="zh" else "%s — Wire & Cable"%title),"",body,crumb,active="industries"))
    if lang=="en": track(path,"wirecable")

def build_brand(lang):
    path=u_brand(); prods=list(PRODUCTS.values())
    cards="".join(prod_card(p,lang) for p in prods)
    body=('<section class="blk"><div class="wrap"><div class="sub">%s</div></div></section>'
          '<section class="blk"><div class="wrap"><h2>%s</h2><div class="grid">%s</div></div></section>'
          '<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'
          '<div class="wrap">%s</div>')%(
        esc(DATA["brand"]["note_zh"] if lang=="zh" else DATA["brand"]["note_en"]),
        ("Avery Dennison 电线电缆材料" if lang=="zh" else "Avery Dennison wire & cable materials"),cards,
        (VERIFY_ZH if lang=="zh" else VERIFY_EN),cta_wc(lang))
    lst=itemlist([(p["product_name"],u_prod(p["slug"])) for p in prods],lang)
    crumb=[("Home","/"),("Wire & Cable",HUB),("Avery Dennison",path)]
    hp.write(lang,path,page(lang,path,
        ("Avery Dennison 电线电缆标签材料 | ETIA" if lang=="zh" else "Avery Dennison Wire & Cable Label Materials | ETIA"),
        ("ETIA 供应选型支持的 Avery Dennison 电线电缆标签材料。" if lang=="zh" else "Avery Dennison wire & cable label materials with ETIA selection support."),
        ("Avery Dennison 电线电缆标签材料" if lang=="zh" else "Avery Dennison Wire & Cable Label Materials"),
        "",body,crumb,schema_extra=[lst],active="products"))
    if lang=="en": track(path,"wirecable")

def build_product(lang,p):
    slug=p["slug"]; path=u_prod(slug)
    appbadges="".join('<a class="pill" href="%s">%s</a>'%(L(lang,u_app(a)),esc(APPS[a]["title_zh"] if lang=="zh" else APPS[a]["title_en"])) for a in p["application_categories"])
    facts=[("品牌" if lang=="zh" else "Brand","Avery Dennison"),
           ("料号" if lang=="zh" else "Part number",p["part_number"]),
           ("面材" if lang=="zh" else "Face material",p["face_material"]),
           ("规格描述" if lang=="zh" else "Spec description",p["product_description"])]
    factrows="".join('<li><span>%s</span><span>%s</span></li>'%(esc(k),esc(v)) for k,v in facts)
    envnote=("环境性能(耐磨/潮湿/化学/高温/阻燃/UL/UV)须按本料号 TDS 确认,未在此赋值。" if lang=="zh"
             else "Environment performance (abrasion / moisture / chemical / heat / flame / UL / UV) is confirmed per this part's TDS and is not asserted here.")
    body=(
      '<section class="blk"><div class="wrap"><div class="xlinks"><span class="pill" style="background:#eef2ff;color:#3730a3;border-color:#c7d2fe">Avery Dennison</span> <span class="pill tag">%s</span></div>'
      '<p style="color:var(--mut);max-width:48em;margin-top:12px">%s</p></div></section>'
      '<section class="blk" style="background:var(--bg)"><div class="wrap"><h2>%s</h2><ul class="specs">%s</ul></div></section>'
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="xlinks">%s</div></div></section>'
      '<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'
      '<div class="wrap">%s</div>')%(
        ("待TDS核对" if lang=="zh" else "Needs TDS verification"),
        esc(p["product_description"]),
        ("材料信息" if lang=="zh" else "Material information"),factrows,
        ("适用应用" if lang=="zh" else "Applicable applications"),appbadges or "—",
        esc(envnote),hp.cta2(lang,"product-detail"))
    name=p["product_name"]
    crumb=[("Home","/"),("Products","/products/"),("Avery Dennison",u_brand()),(name,path)]
    hp.write(lang,path,page(lang,path,"%s | ETIA"%name,
        ("%s(%s)— Avery Dennison 电线电缆材料。"%(name,p["part_number"]))[:157] if lang=="zh" else ("%s (%s) — Avery Dennison wire & cable material."%(name,p["part_number"]))[:157],
        name,"",body,crumb,active="products"))
    if lang=="en": track(path,"wirecable")

def build_sitemap():
    fn="sitemap-wirecable.xml"
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
        build_hub(lang)
        for a in DATA["applications"]: build_app(lang,a)
        for i in DATA["industries"]: build_industry(lang,i)
        for s in [e["slug"] for e in DATA["environments"]]: build_env(lang,s)
        build_brand(lang)
        for p in DATA["products"]: build_product(lang,p)

def main():
    build_all(); build_sitemap()
    from collections import Counter
    print("WIRECABLE EN canonical URLs:",len(URLS)); print(Counter(g for _,g in URLS))

if __name__=="__main__": main()
