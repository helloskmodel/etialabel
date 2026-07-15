#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ETIA · Automotive label materials (3M + FLEXcon) — dual-path generator.

Implements the automotive brief: Application path + Performance path -> one canonical
product page each. Reuses the shared brand shell from gen_heatproof (same design/CSS).
Runs AFTER gen_heatproof (which does the wholesale clean); this script layers the
automotive section on top and never deletes heatproof output.

Compliance (brief §10):
 - 3M and FLEXcon are separate brands, never merged; cross-brand items are described as
   application alternatives, not technical equivalents.
 - ETIA supplies/supports selection; not the manufacturer.
 - Service temperature vs short-term peak are shown distinctly; nulls -> "confirm via TDS".
 - No Product structured data (no real offer/availability). BreadcrumbList + ItemList only.
"""
import json, os, sys
BUILD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BUILD)
import gen_heatproof as hp   # import-safe: its run block is guarded by __main__

ROOT = hp.ROOT
SITE = hp.SITE
LANGS = hp.LANGS
PREFIX = hp.PREFIX
HREFLANG = hp.HREFLANG
esc = hp.esc
L = hp.L
page = hp.page

DATA = json.load(open(os.path.join(BUILD, "data", "automotive.json")))
PRODUCTS = {p["id"]: p for p in DATA["products"]}
APPS = {a["slug"]: a for a in DATA["applications"]}
PERF = {p["slug"]: p for p in DATA["performance"]}
BRANDS = DATA["brands"]

AUTO_URLS = []   # (path, group) English canonical set for the automotive sitemap
def track(path, group): AUTO_URLS.append((path, group))

# ---------------------------------------------------------------- URLs
def u_hub(): return "/industries/automotive-label-materials/"
def u_app(slug): return "/industries/automotive/%s/" % slug
def u_perf_hub(): return "/label-materials/automotive-performance/"
def u_perf(slug): return "/label-materials/%s/" % slug
def u_brand(b): return "/brands/%s/automotive-label-materials/" % b
def u_prod(slug): return "/products/%s/" % slug

def brand_key(p): return "3m" if p["brand"] == "3M" else "flexcon"

VERIFY_EN = "Brochure information is selection guidance, not a production specification. Verify the current technical data sheet (TDS), exact construction and regional availability before final performance claims."
VERIFY_ZH = "手册信息为选型指导,非量产规格。发布最终性能声明前,请核对最新技术数据表(TDS)、具体结构与区域供货情况。"
QUALIFY_EN = "ETIA supplies and supports material selection for this application. ETIA is not the manufacturer. Cross-brand options are application alternatives, not tested technical equivalents."
QUALIFY_ZH = "ETIA 为该应用提供材料供应与选型支持,并非制造商。跨品牌选项为应用层面的替代方案,而非经测试的技术等效品。"

# ---------------------------------------------------------------- helpers
def temp_summary(p, lang):
    """Return a short human string for a product's temperature, honoring null->TDS."""
    parts = []
    mn, mx = p["min_service_temperature_c"], p["max_service_temperature_c"]
    if mn is not None and mx is not None:
        parts.append(("服务温度 %d–%d°C" % (mn, mx)) if lang == "zh" else ("Service %d to %d°C" % (mn, mx)))
    if p["short_term_peak_temperature_c"] is not None:
        dur = p["short_term_peak_duration"] or ""
        parts.append((("短时峰值 %d°C(%s)" % (p["short_term_peak_temperature_c"], "短时,30分钟" if dur else "")) )
                     if lang == "zh" else ("peak %d°C (%s)" % (p["short_term_peak_temperature_c"], dur)))
    if not parts:
        return "温度待TDS确认" if lang == "zh" else "temperature to be confirmed via TDS"
    return " · ".join(parts)

def prod_temp_cards(p, lang):
    cards = ""
    mn, mx = p["min_service_temperature_c"], p["max_service_temperature_c"]
    if mn is not None and mx is not None:
        cards += '<div class="tcard"><div class="k">%s</div><div class="v">%d°C … %d°C</div></div>' % (
            ("持续服务温度" if lang == "zh" else "Continuous service temperature"), mn, mx)
    if p["short_term_peak_temperature_c"] is not None:
        dur = p["short_term_peak_duration"] or ("短时" if lang == "zh" else "short term")
        dur_zh = "短时,约30分钟" if p["short_term_peak_duration"] else "短时"
        cards += '<div class="tcard"><div class="k">%s</div><div class="v">%d°C <span style="font-size:12px;color:var(--mut)">(%s)</span></div></div>' % (
            ("短时峰值温度" if lang == "zh" else "Short-term peak temperature"),
            p["short_term_peak_temperature_c"], (dur_zh if lang == "zh" else dur))
    if not cards:
        cards = '<div class="tcard"><div class="k">%s</div><div class="v" style="font-size:14px;color:var(--mut)">%s</div></div>' % (
            ("温度数据" if lang == "zh" else "Temperature data"),
            ("待最新TDS确认" if lang == "zh" else "To be confirmed against current TDS"))
    return cards

def ver_badge(p, lang):
    if p["verification_status"] == "verified_brochure":
        return '<span class="pill">%s</span>' % ("手册确认" if lang == "zh" else "Brochure-verified")
    return '<span class="pill tag">%s</span>' % ("待TDS核对" if lang == "zh" else "Needs TDS verification")

def brand_pill(p, lang):
    return '<span class="pill" style="background:#eef2ff;color:#3730a3;border-color:#c7d2fe">%s</span>' % esc(p["brand"])

def prod_card(p, lang):
    return ('<a class="card" href="%s"><h3>%s</h3><div class="rows">%s %s · <b>%s</b></div>'
            '<p>%s</p></a>') % (
        L(lang, u_prod(p["slug"])), esc(p["product_name"]),
        brand_pill(p, lang), ver_badge(p, lang), esc(temp_summary(p, lang)),
        esc(p["brochure_direction_zh"] if lang == "zh" else p["brochure_direction_en"]))

def products_for_app(slug):
    return [PRODUCTS[i] for i in PRODUCTS if slug in PRODUCTS[i]["application_categories"]]
def products_for_perf(slug):
    return [PRODUCTS[i] for i in PRODUCTS if slug in PRODUCTS[i]["performance_paths"]]
def products_for_brand(bkey):
    return [PRODUCTS[i] for i in PRODUCTS if brand_key(PRODUCTS[i]) == bkey]

def itemlist(items, lang):
    return {"@context":"https://schema.org","@type":"ItemList","itemListElement":[
        {"@type":"ListItem","position":i+1,"name":n,"url":SITE+PREFIX[lang]+u} for i,(n,u) in enumerate(items)]}

def two_brand_blocks(prods, lang, heading_ctx):
    """Render 3M and FLEXcon recommended materials as SEPARATE blocks (never merged)."""
    out = ""
    for bkey, bname in [("3m","3M"),("flexcon","FLEXcon")]:
        bp = [p for p in prods if brand_key(p)==bkey]
        if not bp: continue
        cards = "".join(prod_card(p, lang) for p in bp)
        out += '<section class="blk"><div class="wrap"><h2>%s %s</h2><div class="grid">%s</div></div></section>' % (
            esc(bname), ("推荐材料" if lang=="zh" else "recommended materials"), cards)
    return out

def neutral_table(prods, lang):
    head = (["产品","品牌","类型","温度方向","核验"] if lang=="zh"
            else ["Product","Brand","Type","Temperature direction","Verification"])
    rows = "".join('<tr><td class="mono"><a href="%s">%s</a></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
        L(lang,u_prod(p["slug"])), esc(p["product_name"]), esc(p["brand"]),
        esc(p["product_type"].replace("_"," ")), esc(temp_summary(p,lang)),
        (("手册" if lang=="zh" else "Brochure") if p["verification_status"]=="verified_brochure"
         else ("待TDS" if lang=="zh" else "Needs TDS")) )
        for p in prods)
    note = ("对比仅说明应用层面的适配差异,不表示技术等效。" if lang=="zh"
            else "Comparison describes application fit only — not technical equivalence between brands.")
    return ('<div class="tablewrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
            '<p style="font-size:13px;color:var(--mut);margin-top:8px">%s</p>') % (
        "".join("<th>%s</th>"%h for h in head), rows, note)

# ---------------------------------------------------------------- builders
def build_hub(lang):
    path = u_hub()
    appcards = "".join('<a class="card" href="%s"><h3>%s</h3></a>' % (
        L(lang,u_app(a["slug"])), esc(a["title_zh"] if lang=="zh" else a["title_en"])) for a in DATA["applications"])
    perfcards = "".join('<a class="card" href="%s"><h3>%s</h3></a>' % (
        L(lang,u_perf(p["slug"])), esc(p["title_zh"] if lang=="zh" else p["title_en"])) for p in DATA["performance"])
    brandcards = "".join('<a class="card" href="%s"><h3>%s</h3><p>%s</p></a>' % (
        L(lang,u_brand(bk)), esc(BRANDS[bk]["name"]),
        ("%d materials"%len(products_for_brand(bk)) if lang=="en" else "%d 款材料"%len(products_for_brand(bk))))
        for bk in ["3m","flexcon"])
    body = (
        '<section class="blk"><div class="wrap"><h2>%s</h2><div class="sub">%s</div></div></section>'
        '<section class="blk"><div class="wrap"><h2>%s</h2><div class="grid">%s</div></div></section>'
        '<section class="blk" style="background:var(--bg)"><div class="wrap"><h2>%s</h2><div class="sub">%s</div><div class="grid">%s</div></div></section>'
        '<section class="blk"><div class="wrap"><h2>%s</h2><div class="grid">%s</div></div></section>'
        '<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'
        '<div class="wrap">%s</div>') % (
        ("汽车标识挑战" if lang=="zh" else "Automotive identification challenges"),
        ("从线束、发动机舱到EV电池、VIN与警示标识,汽车标签面临高温、油污化学、振动与法规追溯等严苛要求。ETIA 供应 3M 与 FLEXcon 材料并协助选型。" if lang=="zh"
         else "From wire harnesses and underhood parts to EV batteries, VIN and warning identification, automotive labels face heat, oils and chemicals, abrasion and traceability demands. ETIA supplies 3M and FLEXcon materials and supports selection."),
        ("按车辆区域与应用选择" if lang=="zh" else "Select by vehicle area and application"), appcards,
        ("按材料性能选择" if lang=="zh" else "Select by material performance"),
        ("同一款产品可从应用或性能两条路径抵达。" if lang=="zh" else "Every material is reachable by application or by performance."), perfcards,
        ("按品牌浏览" if lang=="zh" else "Browse by brand"), brandcards,
        (VERIFY_ZH if lang=="zh" else VERIFY_EN),
        cta_auto(lang))
    lst = itemlist([(a["title_en"], u_app(a["slug"])) for a in DATA["applications"]], lang)
    crumb = [("Home","/"),("Industries & Applications","/industries/"),
             ("Automotive Label Materials", path)]
    h1 = "汽车标识与追溯用耐久标签材料" if lang=="zh" else "Durable Automotive Label Materials for Vehicle Identification and Traceability"
    lede = ("从汽车线束、发动机舱零件到EV电池、VIN安全标识和操作警示,ETIA供应适用于严苛汽车表面与环境的3M及FLEXcon标签材料,并根据应用、温度、化学品、安全要求和打印方式协助选型。" if lang=="zh"
            else "From wire harnesses and underhood components to EV batteries, VIN security and safety instructions, ETIA supplies 3M and FLEXcon label materials engineered for demanding automotive surfaces and environments. Compare by application, temperature, chemical exposure, security requirement and printing method.")
    title = ("汽车耐久标签材料｜3M与FLEXcon汽车标识解决方案｜ETIA" if lang=="zh"
             else "Automotive Label Materials for Harsh Environments | ETIA")
    desc = ("对比适用于发动机舱、EV电池、汽车线束、VIN、安全警示及零部件追溯的3M与FLEXcon汽车标签材料,并按耐温、化学品、表面及耐久性选材。" if lang=="zh"
            else "Explore 3M and FLEXcon automotive label materials for underhood, EV battery, wire harness, VIN, safety and parts identification. Select by heat, chemicals, surface and durability.")
    hp.write(lang, path, page(lang, path, title, desc, h1, lede, body, crumb, schema_extra=[lst], active="industries"))
    if lang=="en": track(path,"automotive")

def cta_auto(lang):
    if lang=="zh":
        return ('<div class="cta"><div class="ic">⚡</div><h3>始于应用。终于选对材料。</h3>'
                '<p>告知车辆区域、表面、温度、化学暴露、安全要求与打印方式,我们从 3M 与 FLEXcon 材料中给出选型建议并安排样品。</p>'
                '<div class="btns"><a class="btn pri" href="%s">申请材料样品</a><a class="btn on-dark" href="%s">咨询工程师</a></div></div>') % (L(lang,"/contact/"),L(lang,"/contact/"))
    return ('<div class="cta"><div class="ic">⚡</div><h3>Start with the Application. Finish with the Right Material.</h3>'
            '<p>Share the vehicle area, surface, temperature, chemical exposure, security requirement and print method — we\'ll recommend from 3M and FLEXcon materials and arrange samples.</p>'
            '<div class="btns"><a class="btn pri" href="%s">Request Material Samples</a><a class="btn on-dark" href="%s">Talk to an Engineer</a></div></div>') % (L(lang,"/contact/"),L(lang,"/contact/"))

APP_CONTEXT = {
 "underhood-powertrain-labels": {
   "chal_en":"Heat and thermal cycling; grease, oil and automotive fluids; moisture and abrasion; smooth, powder-coated, bare-metal, plastic and slightly oily surfaces; permanent warning, service and component identification.",
   "chal_zh":"高温与热循环;油脂、机油与汽车油液;潮湿与磨损;光滑、粉末涂层、裸金属、塑料及轻微油污表面;永久性警示、维修与部件标识。"},
 "ev-battery-charging-labels": {
   "chal_en":"Battery warning and service information; charger operating instructions; flexible battery materials and curved surfaces; chemical and solvent resistance; permanent traceability and barcodes; high-voltage safety communication.",
   "chal_zh":"电池警示与维修信息;充电器操作说明;柔性电池材料与曲面;耐化学与耐溶剂;永久追溯与条码;高压安全提示。"},
 "cable-wire-harness-labels": {
   "chal_en":"Cable diameter and bend radius; flag or wrap format; flexibility; oily surfaces; temperature; fluids; abrasion; print ribbon; barcode and text density.",
   "chal_zh":"电缆直径与弯曲半径;旗形或缠绕形式;柔韧性;油污表面;温度;油液;磨损;打印碳带;条码与文字密度。"},
 "vin-security-compliance-labels": {
   "chal_en":"Serialization, anti-theft, anti-counterfeit and evidence of attempted removal. Do not state that a material meets a national VIN regulation unless the exact construction and jurisdiction are verified.",
   "chal_zh":"序列化、防盗、防伪与拆除痕迹。除非具体结构与适用法域已核实,否则不声称材料满足某国 VIN 法规。"},
 "door-jamb-information-labels": {
   "chal_en":"VIN; tire-pressure information; load information; service information; regulatory text; vehicle configuration data on shaped surfaces.",
   "chal_zh":"VIN;胎压信息;载荷信息;维修信息;法规文本;曲面上的车辆配置数据。"},
 "warning-instruction-labels": {
   "chal_en":"Radiator, battery and jump-start warnings; charger and fuel/charging-flap instructions; safety and service labels; durable, legible, permanent.",
   "chal_zh":"散热器、电池与跨接启动警示;充电器与加油/充电口说明;安全与维修标签;耐久、清晰、永久。"},
 "parts-marking-nameplate-labels": {
   "chal_en":"Barcode, serial and part numbers; supplier and brand identity; reflective identification; equipment nameplates; hard-to-bond and slightly oily surfaces.",
   "chal_zh":"条码、序列号与零件号;供应商与品牌标识;反光标识;设备铭牌;难粘与轻微油污表面。"},
 "paint-masking-overlaminate": {
   "chal_en":"Paint-process masking; protection of printed information; overlamination; high-temperature paint bake; chemical and abrasion protection. Masking (usually temporary) and protective overlamination (usually permanent) are separate needs.",
   "chal_zh":"涂装遮蔽;印刷信息保护;覆膜;高温烤漆;耐化学与耐磨保护。遮蔽(通常临时)与保护性覆膜(通常永久)是不同需求。"},
 "removable-surface-protection": {
   "chal_en":"Substrate and surface finish; outdoor exposure and UV; moisture; maximum dwell time; removal temperature; acceptable residue; abrasion; forming or transport process.",
   "chal_zh":"基材与表面处理;户外暴露与UV;潮湿;最长贴附时间;移除温度;可接受残胶;磨损;成形或运输过程。"},
}

def build_app(lang, a):
    slug=a["slug"]; path=u_app(slug)
    prods=products_for_app(slug)
    ctx=APP_CONTEXT[slug]
    perf_here=sorted({pf for p in prods for pf in p["performance_paths"]})
    perflinks="".join('<a href="%s">%s</a>'%(L(lang,u_perf(x)),esc(PERF[x]["title_zh"] if lang=="zh" else PERF[x]["title_en"])) for x in perf_here)
    other_apps=[x for x in APPS if x!=slug][:6]
    applinks="".join('<a href="%s">%s</a>'%(L(lang,u_app(x)),esc(APPS[x]["title_zh"] if lang=="zh" else APPS[x]["title_en"])) for x in other_apps)
    body=(
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="sub">%s</div></div></section>'
      '%s'
      '<section class="blk" style="background:var(--bg)"><div class="wrap"><h2>%s</h2>%s</div></section>'
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="xlinks">%s</div></div></section>'
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="xlinks">%s</div></div></section>'
      '<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'
      '<div class="wrap">%s</div>') % (
        ("环境与工艺挑战" if lang=="zh" else "Environmental and process challenges"),
        esc(ctx["chal_zh"] if lang=="zh" else ctx["chal_en"]),
        two_brand_blocks(prods, lang, slug),
        ("品牌中立对比" if lang=="zh" else "Brand-neutral comparison"), neutral_table(prods, lang),
        ("相关性能路径" if lang=="zh" else "Related performance paths"), perflinks or "—",
        ("相邻汽车应用" if lang=="zh" else "Adjacent automotive applications"), applinks,
        (VERIFY_ZH if lang=="zh" else VERIFY_EN),
        cta_auto(lang))
    lst=itemlist([(p["product_name"],u_prod(p["slug"])) for p in prods], lang)
    title=a["title_zh"] if lang=="zh" else a["title_en"]
    crumb=[("Home","/"),("Industries & Applications","/industries/"),
           ("Automotive Label Materials",u_hub()),(a["title_en"],path)]
    hp.write(lang, path, page(lang, path, "%s | ETIA"%title,
        esc(ctx["chal_zh"] if lang=="zh" else ctx["chal_en"])[:157],
        title, "", body, crumb, schema_extra=[lst], active="industries"))
    if lang=="en": track(path,"automotive")

def build_perf_hub(lang):
    path=u_perf_hub()
    cards="".join('<a class="card" href="%s"><h3>%s</h3><div class="rows"><b>%d</b> %s</div></a>'%(
        L(lang,u_perf(p["slug"])), esc(p["title_zh"] if lang=="zh" else p["title_en"]),
        len(products_for_perf(p["slug"])), ("款材料" if lang=="zh" else "materials")) for p in DATA["performance"])
    body=('<section class="blk"><div class="wrap"><h2>%s</h2><div class="sub">%s</div><div class="grid">%s</div></div></section>'
          '<div class="wrap">%s</div>')%(
        ("按性能选材" if lang=="zh" else "Label materials by performance"),
        ("从性能出发,反向找到适配的汽车应用与具体产品。" if lang=="zh" else "Start from the required property and reach the applicable automotive uses and products."),
        cards, cta_auto(lang))
    crumb=[("Home","/"),("Automotive Label Materials",u_hub()),("By Performance",path)]
    hp.write(lang, path, page(lang, path,
        ("汽车标签材料性能中心 | ETIA" if lang=="zh" else "Automotive Label Materials by Performance | ETIA"),
        ("按耐高温、耐化学油污、难粘表面、防拆、激光可标记、耐候、可移除、柔性与遮蔽覆膜等性能选材。" if lang=="zh"
         else "Select automotive label materials by high temperature, chemical/oil resistance, difficult surfaces, tamper-evidence, laser marking, weathering, removability, conformability and masking."),
        ("汽车标签材料 —— 按性能" if lang=="zh" else "Automotive Label Materials by Performance"),
        "", body, crumb, active="products"))
    if lang=="en": track(path,"automotive")

PERF_INTENT = {
 "high-temperature-automotive-labels":{"en":"Distinguish application temperature, continuous service temperature, short-term/peak temperature and duration, thermal cycling, and reflow or paint-bake exposure.","zh":"区分贴标温度、持续服务温度、短时/峰值温度及持续时间、热循环,以及回流或烤漆暴露。"},
 "chemical-fuel-oil-resistant-labels":{"en":"Filter by brake fluid, gasoline, diesel, engine oil, power-steering fluid, coolant and cleaning agents, plus exposure method, temperature and dwell time.","zh":"按刹车油、汽油、柴油、机油、动力转向油、冷却液与清洁剂筛选,并考虑暴露方式、温度与停留时间。"},
 "labels-for-difficult-automotive-surfaces":{"en":"Hard-to-bond structured plastics, low-surface-energy and shaped surfaces. A strong adhesive is not the same as verified low-surface-energy compatibility.","zh":"难粘结构化塑料、低表面能与曲面。强粘胶并不等于经验证的低表面能适配。"},
 "automotive-tamper-evident-labels":{"en":"Separate VOID transfer, destructible face, partial destruction, laser-marked security, and serialization/barcode traceability.","zh":"区分 VOID 转移、易碎面材、部分破坏、激光防伪,以及序列化/条码追溯。"},
 "automotive-laser-markable-labels":{"en":"Consider laser type and wavelength, marking contrast, code density, chemical resistance, abrasion, substrate, tamper behavior and regulatory use.","zh":"考虑激光类型与波长、打标对比度、码密度、耐化学、耐磨、基材、防拆特性与法规用途。"},
 "weather-resistant-automotive-labels":{"en":"Include outdoor duration only where supported by the current TDS. Do not generalize one statement to every construction.","zh":"仅在当前 TDS 支持时给出户外耐久时长,不将单一说法推广到所有结构。"},
 "removable-automotive-labels":{"en":"Consider maximum dwell time, removal temperature, acceptable residue and substrate.","zh":"考虑最长贴附时间、移除温度、可接受残胶与基材。"},
 "flexible-conformable-automotive-labels":{"en":"For curved and irregular surfaces — cast and flexible films that conform without lifting.","zh":"用于曲面与不规则表面 —— 可贴合而不翘边的浇铸与柔性薄膜。"},
 "automotive-masking-overlaminate":{"en":"Keep masking (commonly temporary) and protective overlamination (normally remains with the label) as separate filters.","zh":"将遮蔽(通常临时)与保护性覆膜(通常随标签保留)作为独立筛选项。"},
}

def build_perf(lang, pf):
    slug=pf["slug"]; path=u_perf(slug)
    prods=products_for_perf(slug)
    intent=PERF_INTENT[slug]
    apps_here=sorted({a for p in prods for a in p["application_categories"]})
    applinks="".join('<a href="%s">%s</a>'%(L(lang,u_app(x)),esc(APPS[x]["title_zh"] if lang=="zh" else APPS[x]["title_en"])) for x in apps_here)
    body=(
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="sub">%s</div></div></section>'
      '%s'
      '<section class="blk" style="background:var(--bg)"><div class="wrap"><h2>%s</h2>%s</div></section>'
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="xlinks">%s</div></div></section>'
      '<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'
      '<div class="wrap">%s</div>')%(
        ("选型要点" if lang=="zh" else "Selection considerations"), esc(intent["zh" if lang=="zh" else "en"]),
        two_brand_blocks(prods, lang, slug),
        ("品牌中立对比" if lang=="zh" else "Brand-neutral comparison"), neutral_table(prods, lang),
        ("适用汽车应用" if lang=="zh" else "Applicable automotive applications"), applinks or "—",
        (VERIFY_ZH if lang=="zh" else VERIFY_EN),
        cta_auto(lang))
    lst=itemlist([(p["product_name"],u_prod(p["slug"])) for p in prods], lang)
    title=pf["title_zh"] if lang=="zh" else pf["title_en"]
    crumb=[("Home","/"),("Automotive Label Materials",u_hub()),
           ("By Performance",u_perf_hub()),(pf["title_en"],path)]
    hp.write(lang, path, page(lang, path, "%s | ETIA"%title,
        esc(intent["zh" if lang=="zh" else "en"])[:157], title, "", body, crumb, schema_extra=[lst], active="products"))
    if lang=="en": track(path,"automotive")

def build_brand(lang, bkey):
    b=BRANDS[bkey]; path=u_brand(bkey)
    prods=products_for_brand(bkey)
    cards="".join(prod_card(p, lang) for p in prods)
    body=(
      '<section class="blk"><div class="wrap"><div class="sub">%s</div></div></section>'
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="grid">%s</div></div></section>'
      '<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'
      '<div class="wrap">%s</div>')%(
        (("ETIA 供应 %s 汽车标签材料并协助选型;ETIA 非制造商。以下方向取自 %s 手册,需按最新 TDS 核对。" % (b["name"], b["name"])) if lang=="zh"
         else ("ETIA supplies %s automotive label materials and supports selection; ETIA is not the manufacturer. Directions below are taken from the %s brochure and must be verified against the current TDS." % (b["name"], b["name"]))),
        ("%s 汽车标签材料" % b["name"] if lang=="zh" else "%s automotive label materials" % b["name"]), cards,
        (VERIFY_ZH if lang=="zh" else VERIFY_EN),
        cta_auto(lang))
    lst=itemlist([(p["product_name"],u_prod(p["slug"])) for p in prods], lang)
    h1=b["h1_zh"] if lang=="zh" else b["h1_en"]
    crumb=[("Home","/"),("Automotive Label Materials",u_hub()),(b["name"],path)]
    hp.write(lang, path, page(lang, path,
        "%s | ETIA" % (("%s汽车标签材料"%b["name"]) if lang=="zh" else ("%s Automotive Label Materials"%b["name"])),
        (("对比 %s 汽车标签材料及其应用方向,按温度、化学、表面与安全要求选型。"%b["name"]) if lang=="zh"
         else ("Browse %s automotive label materials and their application directions; select by temperature, chemical, surface and security needs."%b["name"])),
        h1, "", body, crumb, schema_extra=[lst], active="products"))
    if lang=="en": track(path,"automotive")

def build_product(lang, p):
    slug=p["slug"]; path=u_prod(slug); bkey=brand_key(p)
    appbadges="".join('<a class="pill" href="%s">%s</a>'%(L(lang,u_app(a)),esc(APPS[a]["title_zh"] if lang=="zh" else APPS[a]["title_en"])) for a in p["application_categories"])
    perfbadges="".join('<a class="pill" href="%s">%s</a>'%(L(lang,u_perf(x)),esc(PERF[x]["title_zh"] if lang=="zh" else PERF[x]["title_en"])) for x in p["performance_paths"])
    # construction facts (only non-null)
    facts=[]
    def add(k_en,k_zh,v):
        if v: facts.append((k_zh if lang=="zh" else k_en, v))
    add("Brand","品牌",p["brand"])
    add("Product type","产品类型",p["product_type"].replace("_"," "))
    add("Product family","产品系列",p["product_family"])
    add("Construction ID","结构编号",p["construction_id"])
    add("Film colour","膜色",p["film_color"])
    add("Finish","表面",p["finish"])
    if p["regional_equivalent_ids"]:
        add("Regional equivalent","区域等效型号",", ".join(p["regional_equivalent_ids"]))
    if p["tamper_evidence_type"]: add("Tamper evidence","防拆类型",p["tamper_evidence_type"])
    if p["removability"]: add("Removability","可移除性",p["removability"])
    factrows="".join('<li><span>%s</span><span>%s</span></li>'%(esc(k),esc(v)) for k,v in facts)
    # same-brand alternatives + other-brand application alternatives (non-equivalence)
    same=[q for q in products_for_brand(bkey) if q["id"]!=p["id"] and set(q["application_categories"])&set(p["application_categories"])][:4]
    other_bkey="flexcon" if bkey=="3m" else "3m"
    other=[q for q in products_for_brand(other_bkey) if set(q["application_categories"])&set(p["application_categories"])][:4]
    samelinks="".join('<a href="%s">%s</a>'%(L(lang,u_prod(q["slug"])),esc(q["product_name"])) for q in same) or "—"
    otherlinks="".join('<a href="%s">%s</a>'%(L(lang,u_prod(q["slug"])),esc(q["product_name"])) for q in other) or "—"
    is_ribbon = p["product_type"]=="ribbon"
    ribbon_note = ('<div class="verify">%s</div>' % (("这是打印碳带耗材,并非标签面材。" if lang=="zh" else "This is a thermal-transfer printing ribbon (consumable), not a label face material."))) if is_ribbon else ""
    body=(
      '<section class="blk"><div class="wrap">'
      '<div class="xlinks">%s %s</div>'
      '<p style="color:var(--mut);max-width:48em;margin-top:12px">%s</p>%s</div></section>'
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="two">%s</div>'
      '<div class="verify">%s</div></div></section>'
      '<section class="blk" style="background:var(--bg)"><div class="wrap"><h2>%s</h2><ul class="specs">%s</ul></div></section>'
      '<section class="blk"><div class="wrap"><h2>%s</h2><div class="xlinks">%s</div>'
      '<h2 style="margin-top:20px">%s</h2><div class="xlinks">%s</div></div></section>'
      '<section class="blk"><div class="wrap"><h2>%s</h2>'
      '<div class="xlinks">%s</div><h2 style="margin-top:20px">%s</h2><div class="xlinks">%s</div>'
      '<p style="font-size:13px;color:var(--mut);margin-top:8px">%s</p></div></section>'
      '<section class="blk"><div class="wrap"><div class="verify"><b>%s</b><br>%s<br><span style="font-size:12px">%s · %s</span></div></div></section>'
      '<div class="wrap">%s</div>')%(
        brand_pill(p,lang), ver_badge(p,lang),
        esc(p["brochure_direction_zh"] if lang=="zh" else p["brochure_direction_en"]), ribbon_note,
        ("温度数据" if lang=="zh" else "Temperature data"), prod_temp_cards(p,lang),
        ("持续服务温度与短时峰值温度为不同参数,请分别确认。" if lang=="zh" else "Continuous service temperature and short-term peak temperature are distinct parameters — confirm each separately."),
        ("材料结构" if lang=="zh" else "Material construction"), factrows,
        ("推荐应用" if lang=="zh" else "Recommended applications"), appbadges or "—",
        ("性能路径" if lang=="zh" else "Performance paths"), perfbadges or "—",
        ("同品牌替代材料" if lang=="zh" else "Alternative materials from the same brand"), samelinks,
        ("另一品牌的应用替代" if lang=="zh" else "Application alternatives from the other brand"), otherlinks,
        ("跨品牌为应用替代,非技术等效。" if lang=="zh" else "Cross-brand items are application alternatives, not technical equivalents."),
        ("资格声明" if lang=="zh" else "Qualification"), (QUALIFY_ZH if lang=="zh" else QUALIFY_EN),
        esc(p["source_document"]), (VERIFY_ZH[:0] and "" or ("来源手册,需核对最新TDS。" if lang=="zh" else "Brochure source — verify current TDS.")),
        cta_auto(lang))
    name=p["product_name"]
    crumb=[("Home","/"),("Products","/products/"),(BRANDS[bkey]["name"],u_brand(bkey)),(name,path)]
    title=("%s | ETIA" % name)
    desc=(("%s。%s" % (name, p["brochure_direction_zh"]))[:157] if lang=="zh"
          else ("%s — %s" % (name, p["brochure_direction_en"]))[:157])
    # NOTE: no Product structured data (no real offer/availability) — brief §10 rule 9.
    hp.write(lang, path, page(lang, path, title, desc, name, "", body, crumb, active="products"))
    if lang=="en": track(path,"automotive")

# ---------------------------------------------------------------- sitemap + redirects merge
def build_sitemap():
    fn="sitemap-automotive.xml"
    xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    for p,_ in AUTO_URLS:
        xml+='  <url><loc>%s%s</loc>'%(SITE,p)
        for lg in LANGS: xml+='<xhtml:link rel="alternate" hreflang="%s" href="%s%s%s"/>'%(HREFLANG[lg],SITE,PREFIX[lg],p)
        xml+='</url>\n'
    xml+='</urlset>\n'
    open(os.path.join(ROOT,fn),"w").write(xml)
    # add to sitemap-index.xml if present
    idxp=os.path.join(ROOT,"sitemap-index.xml")
    if os.path.isfile(idxp):
        idx=open(idxp).read()
        loc='  <sitemap><loc>%s/%s</loc></sitemap>\n'%(SITE,fn)
        if fn not in idx:
            idx=idx.replace('</sitemapindex>', loc+'</sitemapindex>')
            open(idxp,"w").write(idx)

def merge_redirects():
    vp=os.path.join(ROOT,"vercel.json")
    cfg=json.load(open(vp)) if os.path.isfile(vp) else {"cleanUrls":True,"trailingSlash":True,"redirects":[]}
    extra=[
      {"source":"/automotive","destination":u_hub(),"permanent":True},
      {"source":"/automotive/:path*","destination":u_hub(),"permanent":True},
    ]
    have={(r["source"]) for r in cfg.get("redirects",[])}
    for r in extra:
        if r["source"] not in have: cfg.setdefault("redirects",[]).append(r)
    open(vp,"w").write(json.dumps(cfg,indent=2)+"\n")

# ---------------------------------------------------------------- run
def build_all():
    for lang in LANGS:
        build_hub(lang)
        for a in DATA["applications"]: build_app(lang, a)
        build_perf_hub(lang)
        for pf in DATA["performance"]: build_perf(lang, pf)
        for bk in ["3m","flexcon"]: build_brand(lang, bk)
        for p in DATA["products"]: build_product(lang, p)

def main():
    build_all()
    build_sitemap()
    merge_redirects()
    from collections import Counter
    print("AUTOMOTIVE EN canonical URLs:", len(AUTO_URLS))
    print(Counter(g for _,g in AUTO_URLS))

if __name__ == "__main__":
    main()
