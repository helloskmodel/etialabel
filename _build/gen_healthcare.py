#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ETIA · Healthcare & Life Sciences label materials (FLEXcon + BIO TECH) — dual-path.

Find by Application (5) + Find by Requirement / 工况 (9) -> one canonical product page.
Reuses the shared brand shell from gen_heatproof. Runs AFTER gen_heatproof.

Compliance (brief §6): ETIA = supplier/solution-provider, not manufacturer; biocompat /
UL / IEC / FDA bound to named series/part only; Omni-Wave conductive shown separately;
blood-bag routing enforced in data; nulls -> "confirm via data sheet"; no Product schema.
"""
import json, os, sys
BUILD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BUILD)
import gen_heatproof as hp

ROOT=hp.ROOT; SITE=hp.SITE; LANGS=hp.LANGS; PREFIX=hp.PREFIX; HREFLANG=hp.HREFLANG
esc=hp.esc; L=hp.L; page=hp.page

DATA=json.load(open(os.path.join(BUILD,"data","healthcare.json")))
PRODUCTS={p["id"]:p for p in DATA["products"]}
APPS={a["slug"]:a for a in DATA["applications"]}
REQS={r["slug"]:r for r in DATA["requirements"]}
BRANDS=DATA["brands"]

HC_URLS=[]
def track(path,group): HC_URLS.append((path,group))

HUB="/industries/healthcare-life-sciences/"
def u_hub(): return HUB
def u_app(slug): return "%s%s/"%(HUB,slug)
def u_req(slug): return "/label-materials/%s/"%slug
def u_req_hub(): return "/label-materials/healthcare-requirements/"
def u_brand(b): return "/brands/%s/healthcare-life-sciences/"%b
def u_prod(slug): return "/products/%s/"%slug

def brand_key(p): return "bio-tech" if p["brand"]=="BIO TECH" else "flexcon"

VERIFY_EN="Brochure information is selection guidance, not a production specification. Verify the current data sheet, exact construction, biocompatibility and regulatory status before final claims."
VERIFY_ZH="手册信息为选型指导,非量产规格。发布最终声明前,请核对最新数据表、具体结构、生物相容性与法规状态。"
QUALIFY_EN="ETIA supplies and supports material selection for healthcare and life-science identification. ETIA is not the manufacturer, and does not present FLEXcon or BIO TECH manufacturing, R&D or certification as ETIA's own."
QUALIFY_ZH="ETIA 为医疗与生命科学标识提供材料供应与选型支持。ETIA 并非制造商,亦不将 FLEXcon 或 BIO TECH 的制造、研发与认证能力写作 ETIA 自有。"

def temp_summary(p, lang):
    mn,mx=p["min_service_temperature_c"],p["max_service_temperature_c"]
    if mn is not None and mx is not None:
        return ("服务 %d–%d°C"%(mn,mx)) if lang=="zh" else ("Service %d to %d°C"%(mn,mx))
    if mn is not None:
        return ("最低至 %d°C"%mn) if lang=="zh" else ("Down to %d°C"%mn)
    return "温度待数据表确认" if lang=="zh" else "temperature per data sheet"

def prod_temp_cards(p, lang):
    mn,mx=p["min_service_temperature_c"],p["max_service_temperature_c"]
    if mn is not None:
        label=("最低服务温度" if lang=="zh" else "Minimum service temperature")
        val=("%d°C"%mn) + (" … %d°C"%mx if mx is not None else "")
        return '<div class="tcard"><div class="k">%s</div><div class="v">%s</div></div>'%(label,val)
    return '<div class="tcard"><div class="k">%s</div><div class="v" style="font-size:14px;color:var(--mut)">%s</div></div>'%(
        ("温度数据" if lang=="zh" else "Temperature data"),
        ("按最新数据表确认" if lang=="zh" else "Per current data sheet"))

def ver_badge(p, lang):
    if p["verification_status"]=="verified_brochure":
        return '<span class="pill">%s</span>'%("手册确认" if lang=="zh" else "Brochure-verified")
    return '<span class="pill tag">%s</span>'%("待核对" if lang=="zh" else "Needs verification")

def brand_pill(p, lang):
    return '<span class="pill" style="background:#eef2ff;color:#3730a3;border-color:#c7d2fe">%s</span>'%esc(p["brand"])

def prod_card(p, lang):
    return ('<a class="card" href="%s"><h3>%s</h3><div class="rows">%s %s · <b>%s</b></div><p>%s</p></a>')%(
        L(lang,u_prod(p["slug"])), esc(p["product_name"]), brand_pill(p,lang), ver_badge(p,lang),
        esc(temp_summary(p,lang)), esc(p["brochure_direction_zh"] if lang=="zh" else p["brochure_direction_en"]))

def products_for_app(slug): return [PRODUCTS[i] for i in PRODUCTS if slug in PRODUCTS[i]["application_categories"]]
def products_for_req(slug): return [PRODUCTS[i] for i in PRODUCTS if slug in PRODUCTS[i]["requirement_paths"]]
def products_for_brand(bk): return [PRODUCTS[i] for i in PRODUCTS if brand_key(PRODUCTS[i])==bk]

def itemlist(items, lang):
    return {"@context":"https://schema.org","@type":"ItemList","itemListElement":[
        {"@type":"ListItem","position":i+1,"name":n,"url":SITE+PREFIX[lang]+u} for i,(n,u) in enumerate(items)]}

def brand_blocks(prods, lang):
    out=""
    for bk in ["flexcon","bio-tech"]:
        bp=[p for p in prods if brand_key(p)==bk]
        if not bp: continue
        cards="".join(prod_card(p,lang) for p in bp)
        out+='<section class="blk"><div class="wrap"><h2>%s %s</h2><div class="grid">%s</div></div></section>'%(
            esc(BRANDS[bk]["name"]), ("推荐材料" if lang=="zh" else "recommended materials"), cards)
    return out

def neutral_table(prods, lang):
    head=(["产品","品牌","类型","温度方向","核验"] if lang=="zh" else ["Product","Brand","Type","Temperature","Verification"])
    rows="".join('<tr><td class="mono"><a href="%s">%s</a></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'%(
        L(lang,u_prod(p["slug"])), esc(p["product_name"]), esc(p["brand"]),
        esc(p["product_type"].replace("_"," ")), esc(temp_summary(p,lang)),
        (("手册" if lang=="zh" else "Brochure") if p["verification_status"]=="verified_brochure" else ("待核对" if lang=="zh" else "Verify")))
        for p in prods)
    note=("对比仅说明应用层面适配,不表示品牌间技术等效。" if lang=="zh" else "Comparison describes application fit only — not technical equivalence between brands.")
    return ('<div class="tablewrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
            '<p style="font-size:13px;color:var(--mut);margin-top:8px">%s</p>')%("".join("<th>%s</th>"%h for h in head),rows,note)

def cta_hc(lang):
    if lang=="zh":
        return ('<div class="cta"><div class="ic">⚡</div><h3>说明您的医疗/实验室识别需求,我们协助选型并寄样。</h3>'
                '<p>告知应用、温度(冷冻/液氮)、灭菌方式、化学暴露、是否贴肤或导电,我们从 FLEXcon 与 BIO TECH 材料中给出选型建议。</p>'
                '<div class="btns"><a class="btn pri" href="%s">申请材料样品</a><a class="btn on-dark" href="%s">咨询工程师</a></div></div>')%(L(lang,"/contact/"),L(lang,"/contact/"))
    return ('<div class="cta"><div class="ic">⚡</div><h3>Tell us your medical or lab identification need. We\'ll support selection and samples.</h3>'
            '<p>Share the application, temperature (freeze / LN2), sterilization method, chemical exposure, skin-contact or conductivity — we\'ll recommend from FLEXcon and BIO TECH materials.</p>'
            '<div class="btns"><a class="btn pri" href="%s">Request Material Samples</a><a class="btn on-dark" href="%s">Talk to an Engineer</a></div></div>')%(L(lang,"/contact/"),L(lang,"/contact/"))

APP_CTX={
 "wearable-devices":{"en":"Gentle removal, regular or long-term wear; soft, breathable, stretchable and conformable; skin type, body location, motion, shower and sweat; single-sided, double-sided and transfer adhesive forms.","zh":"温和移除、常规或长期佩戴;柔软、透气、可延展、贴合曲面;皮肤类型、身体部位、运动、淋浴与出汗;单面、双面与转移胶形式。"},
 "diagnostics-testing":{"en":"Biosignal acquisition or therapeutic stimulation; electrical connection and conductivity; gentle removal, short- or longer-term wear; multi-layer electrode, sensor and skin-contact builds.","zh":"生物信号采集或治疗刺激;电气连接与导电;温和移除、短期或较长期佩戴;电极、传感器与贴肤结构的多层组合。"},
 "pharmaceutical":{"en":"Small- and large-diameter container labels; cover labels; cold-chain pharmaceutical labels; tamper-evident and security labels; blood-bag and transfusion labels.","zh":"大小直径容器标签;遮盖标签;冷链药品标签;防拆与安全标签;血袋及输血制品标签。"},
 "medical-devices":{"en":"Long-term device identification and tracking; fine text and barcode printing; abrasion, wipe and cleaning-agent resistance; edge-lift resistance and durable bonding; clear gloss or matte overlaminates.","zh":"医疗器械长期识别与追踪;精细文字与条码打印;耐磨、耐擦拭与耐清洁剂;防翘边、耐久粘接;透明光面或哑面保护膜。"},
 "laboratory":{"en":"-20/-40/-80°C frozen storage and -196°C liquid-nitrogen storage; direct application to frozen, moist or frosted surfaces; histology slides; autoclave, dry-heat, gamma or EtO sterilization; xylene, alcohol, stain and disinfectant exposure; temporary and water-dissolvable identification.","zh":"-20/-40/-80°C 冷冻与 -196°C 液氮存储;冻结、潮湿或结霜表面直接贴附;组织学载玻片;高压蒸汽、干热、伽马或环氧乙烷灭菌;二甲苯、乙醇、染色剂与消毒剂;临时与水溶识别。"},
}
REQ_CTX={
 "low-temperature-frozen-storage":{"en":"-20°C to -80°C storage and application to frozen surfaces — blood bags, plasma, pharmaceuticals and samples.","zh":"-20°C 至 -80°C 存储与冻结表面贴附 —— 血袋、血浆、药品与样本。"},
 "cryogenic-liquid-nitrogen-storage":{"en":"-196°C liquid-nitrogen vapor and liquid phase — cryovials, tubes, metal racks and glass capillaries.","zh":"-196°C 液氮气相与液相 —— 冻存管、试管、金属架与玻璃细管。"},
 "chemical-resistant-identification":{"en":"Xylene, alcohol, histology chemicals, disinfectants and cleaning agents.","zh":"二甲苯、乙醇、组织学化学品、消毒剂与清洁剂。"},
 "sterilization-resistant-identification":{"en":"Autoclave (steam), dry heat, gamma irradiation and ethylene oxide.","zh":"高压蒸汽、干热、伽马射线与环氧乙烷。"},
 "skin-contact-biocompatible-materials":{"en":"Skin-worn devices, catheter securement, sensitive skin and long-term wear. Biocompatibility per the adhesive supplier's ISO 10993 testing — not a guarantee for every user.","zh":"贴肤设备、导管固定、敏感皮肤与长期佩戴。生物相容性依胶黏剂供应商 ISO 10993 测试,不对所有使用者构成保证。"},
 "conductive-biosensing-materials":{"en":"ECG, sEMG, EDA, diagnostic electrodes and TENS. Conductive transfer materials, described separately from print labels.","zh":"ECG、sEMG、EDA、诊断电极与 TENS。导电转移材料,与打印标签分开说明。"},
 "abrasion-cleaning-resistant-labels":{"en":"Long-term device identification, repeated wiping, barcode and small-text legibility.","zh":"医疗设备长期识别、反复擦拭、条码与小字可读性。"},
 "pharmaceutical-packaging-security":{"en":"Vials, small/large-diameter containers, cover labels, tamper-evident and security identification. (Blood bags are handled under Low-Temperature, not here.)","zh":"药瓶、大小直径容器、遮盖、防拆与安全识别。(血袋归“低温与冷冻存储”,不在此项。)"},
 "removable-dissolvable-labels":{"en":"Temporary sample identification, reusable containers and wash-off removal.","zh":"临时样本识别、可重复使用容器与水洗移除。"},
}

def build_hub(lang):
    path=u_hub()
    appcards="".join('<a class="card" href="%s"><h3>%s</h3></a>'%(L(lang,u_app(a["slug"])),esc(a["title_zh"] if lang=="zh" else a["title_en"])) for a in DATA["applications"])
    reqcards="".join('<a class="card" href="%s"><h3>%s</h3></a>'%(L(lang,u_req(r["slug"])),esc(r["title_zh"] if lang=="zh" else r["title_en"])) for r in DATA["requirements"])
    brandcards="".join('<a class="card" href="%s"><h3>%s</h3><p>%s</p></a>'%(
        L(lang,u_brand(bk)),esc(BRANDS[bk]["name"]),
        ("%d materials"%len(products_for_brand(bk)) if lang=="en" else "%d 款材料"%len(products_for_brand(bk)))) for bk in ["flexcon","bio-tech"])
    body=(
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="sub">%s</div><div class="grid">%s</div></div></section>'
      '<section class="blk" style="background:var(--bg)"><div class="wrap"><h2>%s</h2><div class="sub">%s</div><div class="grid">%s</div></div></section>'
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="grid">%s</div></div></section>'
      '<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'
      '<div class="wrap">%s</div>')%(
        ("按应用查找" if lang=="zh" else "Find by Application"),
        ("从可穿戴设备、诊断检测、医药制药、医疗器械到实验室识别,按实际使用场景寻找标签材料。" if lang=="zh"
         else "Explore label materials for wearable devices, diagnostics, pharmaceutical applications, medical devices, and laboratories."), appcards,
        ("按工况查找" if lang=="zh" else "Find by Requirement"),
        ("根据低温、液氮、化学品、灭菌、贴肤、导电、清洁和包装安全等要求筛选材料。" if lang=="zh"
         else "Filter materials by low-temperature storage, cryogenic exposure, chemicals, sterilization, skin contact, conductivity, cleaning, and packaging security."), reqcards,
        ("按品牌浏览" if lang=="zh" else "Browse by brand"), brandcards,
        (VERIFY_ZH if lang=="zh" else VERIFY_EN), cta_hc(lang))
    lst=itemlist([(a["title_en"],u_app(a["slug"])) for a in DATA["applications"]], lang)
    crumb=[("Home","/"),("Industries & Applications","/industries/"),("Healthcare & Life Sciences",path)]
    h1="医疗与生命科学标签材料" if lang=="zh" else "Healthcare & Life Sciences Label Materials"
    lede=("面向可穿戴、诊断、制药、医疗器械与实验室的标签材料。两条链路:按应用、按工况。ETIA 供应 FLEXcon 与 BIO TECH 材料并协助选型。" if lang=="zh"
          else "Label materials for wearables, diagnostics, pharmaceutical, medical devices and laboratories. Two paths — by application and by requirement. ETIA supplies FLEXcon and BIO TECH materials with selection support.")
    title=("医疗与生命科学标签材料｜FLEXcon 与 BIO TECH｜ETIA" if lang=="zh" else "Healthcare & Life Sciences Label Materials | ETIA")
    desc=("按应用与工况选择医疗、制药与实验室标签材料:低温/液氮、灭菌、耐化学、贴肤、导电、耐清洁与包装安全。" if lang=="zh"
          else "Select healthcare, pharmaceutical and laboratory label materials by application and requirement: cryogenic, sterilization, chemical, skin-contact, conductive, cleaning and packaging security.")
    hp.write(lang,path,page(lang,path,title,desc,h1,lede,body,crumb,schema_extra=[lst],active="industries"))
    if lang=="en": track(path,"healthcare")

def build_app(lang, a):
    slug=a["slug"]; path=u_app(slug); prods=products_for_app(slug); ctx=APP_CTX[slug]
    reqs_here=sorted({r for p in prods for r in p["requirement_paths"]})
    reqlinks="".join('<a href="%s">%s</a>'%(L(lang,u_req(x)),esc(REQS[x]["title_zh"] if lang=="zh" else REQS[x]["title_en"])) for x in reqs_here)
    other=[x for x in APPS if x!=slug]
    applinks="".join('<a href="%s">%s</a>'%(L(lang,u_app(x)),esc(APPS[x]["title_zh"] if lang=="zh" else APPS[x]["title_en"])) for x in other)
    body=(
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="sub">%s</div></div></section>'
      '%s'
      '<section class="blk" style="background:var(--bg)"><div class="wrap"><h2>%s</h2>%s</div></section>'
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="xlinks">%s</div></div></section>'
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="xlinks">%s</div></div></section>'
      '<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'
      '<div class="wrap">%s</div>')%(
        ("选择维度" if lang=="zh" else "Key selection dimensions"), esc(ctx["zh" if lang=="zh" else "en"]),
        brand_blocks(prods, lang),
        ("品牌中立对比" if lang=="zh" else "Brand-neutral comparison"), neutral_table(prods, lang),
        ("相关工况" if lang=="zh" else "Related requirements"), reqlinks or "—",
        ("其他医疗应用" if lang=="zh" else "Other healthcare applications"), applinks,
        (VERIFY_ZH if lang=="zh" else VERIFY_EN), cta_hc(lang))
    lst=itemlist([(p["product_name"],u_prod(p["slug"])) for p in prods], lang)
    title=a["title_zh"] if lang=="zh" else a["title_en"]
    crumb=[("Home","/"),("Industries & Applications","/industries/"),("Healthcare & Life Sciences",u_hub()),(a["title_en"],path)]
    hp.write(lang,path,page(lang,path,"%s | ETIA"%title,esc(ctx["zh" if lang=="zh" else "en"])[:157],title,"",body,crumb,schema_extra=[lst],active="industries"))
    if lang=="en": track(path,"healthcare")

def build_req_hub(lang):
    path=u_req_hub()
    cards="".join('<a class="card" href="%s"><h3>%s</h3><div class="rows"><b>%d</b> %s</div></a>'%(
        L(lang,u_req(r["slug"])),esc(r["title_zh"] if lang=="zh" else r["title_en"]),
        len(products_for_req(r["slug"])),("款材料" if lang=="zh" else "materials")) for r in DATA["requirements"])
    body=('<section class="blk"><div class="wrap"><h2>%s</h2><div class="sub">%s</div><div class="grid">%s</div></div></section><div class="wrap">%s</div>')%(
        ("按工况查找" if lang=="zh" else "Find by Requirement"),
        ("从工况出发,反向找到适配的医疗应用与具体产品。" if lang=="zh" else "Start from the requirement and reach the applicable healthcare uses and products."),
        cards, cta_hc(lang))
    crumb=[("Home","/"),("Healthcare & Life Sciences",u_hub()),("By Requirement",path)]
    hp.write(lang,path,page(lang,path,
        ("医疗标签材料 — 按工况 | ETIA" if lang=="zh" else "Healthcare Label Materials by Requirement | ETIA"),
        ("按低温、液氮、耐化学、耐灭菌、贴肤、导电、耐清洁、包装安全与水溶等工况选材。" if lang=="zh"
         else "Select by low-temperature, cryogenic, chemical, sterilization, skin-contact, conductive, cleaning, packaging-security and dissolvable requirements."),
        ("医疗与生命科学标签材料 —— 按工况" if lang=="zh" else "Healthcare & Life Sciences Materials by Requirement"),
        "",body,crumb,active="products"))
    if lang=="en": track(path,"healthcare")

def build_req(lang, r):
    slug=r["slug"]; path=u_req(slug); prods=products_for_req(slug); ctx=REQ_CTX[slug]
    apps_here=sorted({a for p in prods for a in p["application_categories"]})
    applinks="".join('<a href="%s">%s</a>'%(L(lang,u_app(x)),esc(APPS[x]["title_zh"] if lang=="zh" else APPS[x]["title_en"])) for x in apps_here)
    body=(
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="sub">%s</div></div></section>'
      '%s'
      '<section class="blk" style="background:var(--bg)"><div class="wrap"><h2>%s</h2>%s</div></section>'
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="xlinks">%s</div></div></section>'
      '<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'
      '<div class="wrap">%s</div>')%(
        ("工况说明" if lang=="zh" else "Requirement"), esc(ctx["zh" if lang=="zh" else "en"]),
        brand_blocks(prods, lang),
        ("品牌中立对比" if lang=="zh" else "Brand-neutral comparison"), neutral_table(prods, lang),
        ("适用医疗应用" if lang=="zh" else "Applicable healthcare applications"), applinks or "—",
        (VERIFY_ZH if lang=="zh" else VERIFY_EN), cta_hc(lang))
    lst=itemlist([(p["product_name"],u_prod(p["slug"])) for p in prods], lang)
    title=r["title_zh"] if lang=="zh" else r["title_en"]
    crumb=[("Home","/"),("Healthcare & Life Sciences",u_hub()),("By Requirement",u_req_hub()),(r["title_en"],path)]
    hp.write(lang,path,page(lang,path,"%s | ETIA"%title,esc(ctx["zh" if lang=="zh" else "en"])[:157],title,"",body,crumb,schema_extra=[lst],active="products"))
    if lang=="en": track(path,"healthcare")

def build_brand(lang, bk):
    b=BRANDS[bk]; path=u_brand(bk); prods=products_for_brand(bk)
    cards="".join(prod_card(p,lang) for p in prods)
    fams=", ".join(b["families"])
    body=(
      '<section class="blk"><div class="wrap"><div class="sub">%s</div></div></section>'
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="grid">%s</div></div></section>'
      '<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'
      '<div class="wrap">%s</div>')%(
        ((("ETIA 供应 %s 医疗与生命科学标签材料并协助选型;ETIA 非制造商。系列:%s。以下方向取自原厂手册,需核对最新数据表。"%(b["name"],fams))) if lang=="zh"
         else ("ETIA supplies %s healthcare and life-science label materials and supports selection; ETIA is not the manufacturer. Families: %s. Directions below are from the manufacturer brochure and must be verified against the current data sheet."%(b["name"],fams))),
        ("%s 医疗与生命科学材料"%b["name"] if lang=="zh" else "%s healthcare & life-science materials"%b["name"]), cards,
        (VERIFY_ZH if lang=="zh" else VERIFY_EN), cta_hc(lang))
    lst=itemlist([(p["product_name"],u_prod(p["slug"])) for p in prods], lang)
    crumb=[("Home","/"),("Healthcare & Life Sciences",u_hub()),(b["name"],path)]
    hp.write(lang,path,page(lang,path,
        "%s | ETIA"%(("%s 医疗标签材料"%b["name"]) if lang=="zh" else ("%s Healthcare Label Materials"%b["name"])),
        ((("对比 %s 医疗与生命科学标签材料及应用方向。"%b["name"])) if lang=="zh" else ("Browse %s healthcare and life-science label materials and application directions."%b["name"])),
        ("%s 医疗与生命科学标签材料"%b["name"] if lang=="zh" else "%s Healthcare & Life Sciences Label Materials"%b["name"]),
        "",body,crumb,schema_extra=[lst],active="products"))
    if lang=="en": track(path,"healthcare")

def build_product(lang, p):
    slug=p["slug"]; path=u_prod(slug); bk=brand_key(p)
    appbadges="".join('<a class="pill" href="%s">%s</a>'%(L(lang,u_app(a)),esc(APPS[a]["title_zh"] if lang=="zh" else APPS[a]["title_en"])) for a in p["application_categories"])
    reqbadges="".join('<a class="pill" href="%s">%s</a>'%(L(lang,u_req(x)),esc(REQS[x]["title_zh"] if lang=="zh" else REQS[x]["title_en"])) for x in p["requirement_paths"])
    facts=[]
    def add(ke,kz,v):
        if v: facts.append((kz if lang=="zh" else ke,v))
    add("Brand","品牌",p["brand"]); add("Product type","产品类型",p["product_type"].replace("_"," "))
    add("Product family","产品系列",p["product_family"]); add("Part number","料号",p["part_number"])
    add("Film colour","膜色",p["film_color"]); add("Finish","表面",p["finish"])
    factrows="".join('<li><span>%s</span><span>%s</span></li>'%(esc(k),esc(v)) for k,v in facts)
    same=[q for q in products_for_brand(bk) if q["id"]!=p["id"] and set(q["application_categories"])&set(p["application_categories"])][:4]
    samelinks="".join('<a href="%s">%s</a>'%(L(lang,u_prod(q["slug"])),esc(q["product_name"])) for q in same) or "—"
    cnote=p["compliance_note_zh"] if lang=="zh" else p["compliance_note_en"]
    cnote_html=('<div class="verify">%s</div>'%esc(cnote)) if cnote else ""
    body=(
      '<section class="blk"><div class="wrap"><div class="xlinks">%s %s</div>'
      '<p style="color:var(--mut);max-width:48em;margin-top:12px">%s</p>%s</div></section>'
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="two">%s</div></div></section>'
      '<section class="blk" style="background:var(--bg)"><div class="wrap"><h2>%s</h2><ul class="specs">%s</ul></div></section>'
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="xlinks">%s</div>'
      '<h2 style="margin-top:20px">%s</h2><div class="xlinks">%s</div></div></section>'
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="xlinks">%s</div></div></section>'
      '<section class="blk"><div class="wrap"><div class="verify"><b>%s</b><br>%s<br><span style="font-size:12px">%s</span></div></div></section>'
      '<div class="wrap">%s</div>')%(
        brand_pill(p,lang), ver_badge(p,lang),
        esc(p["brochure_direction_zh"] if lang=="zh" else p["brochure_direction_en"]), cnote_html,
        ("温度数据" if lang=="zh" else "Temperature data"), prod_temp_cards(p,lang),
        ("材料结构" if lang=="zh" else "Material construction"), factrows,
        ("推荐应用" if lang=="zh" else "Recommended applications"), appbadges or "—",
        ("工况路径" if lang=="zh" else "Requirement paths"), reqbadges or "—",
        ("同品牌相关材料" if lang=="zh" else "Related materials from the same brand"), samelinks,
        ("资格声明" if lang=="zh" else "Qualification"), (QUALIFY_ZH if lang=="zh" else QUALIFY_EN),
        ("来源手册,需核对最新数据表。" if lang=="zh" else "Brochure source — verify current data sheet."),
        cta_hc(lang))
    name=p["product_name"]
    crumb=[("Home","/"),("Products","/products/"),(BRANDS[bk]["name"],u_brand(bk)),(name,path)]
    desc=(("%s。%s"%(name,p["brochure_direction_zh"]))[:157] if lang=="zh" else ("%s — %s"%(name,p["brochure_direction_en"]))[:157])
    # NOTE: no Product structured data (no real offer/availability).
    hp.write(lang,path,page(lang,path,"%s | ETIA"%name,desc,name,"",body,crumb,active="products"))
    if lang=="en": track(path,"healthcare")

def build_sitemap():
    fn="sitemap-healthcare.xml"
    xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    for p,_ in HC_URLS:
        xml+='  <url><loc>%s%s</loc>'%(SITE,p)
        for lg in LANGS: xml+='<xhtml:link rel="alternate" hreflang="%s" href="%s%s%s"/>'%(HREFLANG[lg],SITE,PREFIX[lg],p)
        xml+='</url>\n'
    xml+='</urlset>\n'
    open(os.path.join(ROOT,fn),"w").write(xml)
    idxp=os.path.join(ROOT,"sitemap-index.xml")
    if os.path.isfile(idxp):
        idx=open(idxp).read()
        if fn not in idx:
            idx=idx.replace('</sitemapindex>','  <sitemap><loc>%s/%s</loc></sitemap>\n</sitemapindex>'%(SITE,fn))
            open(idxp,"w").write(idx)

def merge_redirects():
    vp=os.path.join(ROOT,"vercel.json")
    cfg=json.load(open(vp)) if os.path.isfile(vp) else {"cleanUrls":True,"trailingSlash":True,"redirects":[]}
    extra=[{"source":"/healthcare","destination":u_hub(),"permanent":True},
           {"source":"/medical","destination":u_hub(),"permanent":True}]
    have={r["source"] for r in cfg.get("redirects",[])}
    for r in extra:
        if r["source"] not in have: cfg.setdefault("redirects",[]).append(r)
    open(vp,"w").write(json.dumps(cfg,indent=2)+"\n")

def build_all():
    for lang in LANGS:
        build_hub(lang)
        for a in DATA["applications"]: build_app(lang,a)
        build_req_hub(lang)
        for r in DATA["requirements"]: build_req(lang,r)
        for bk in ["flexcon","bio-tech"]: build_brand(lang,bk)
        for p in DATA["products"]: build_product(lang,p)

def main():
    build_all(); build_sitemap(); merge_redirects()
    from collections import Counter
    print("HEALTHCARE EN canonical URLs:", len(HC_URLS)); print(Counter(g for _,g in HC_URLS))

if __name__=="__main__":
    main()
