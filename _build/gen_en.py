#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ETIALABEL overseas (Google SEO) 3-path static site generator."""
import json, os, re, html, shutil

import os
ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://www.etialabel.com"
BRAND = "ETIA Label"

# ---------------------------------------------------------------- load data
tree = json.load(open("/workspace/etialabel/_build/data/site_tree.json"))
prods = json.load(open("/workspace/etialabel/_build/data/cn_products.json"))
PROD = {}
for p in prods:
    PROD[p["m"].strip()] = p

# ---------------------------------------------------------------- EN mapping
# industry L2 : cn-slug -> (en-slug, en-title, blurb)
IND_MAP = {
 "dianzi-bandaoti": ("electronics-semiconductor", "Electronics & Semiconductor",
   "Polyimide and PET labels engineered for PCB reflow, wave soldering, ESD cleanrooms and component traceability."),
 "qiche-zhengche": ("automotive", "Automotive",
   "Under-hood high-temperature, oil- and chemical-resistant, and flame-retardant labels for vehicle assembly and parts traceability."),
 "xinnengyuan-dianche": ("ev-battery", "EV & Battery",
   "Flame-retardant, high-voltage insulation and thermal-runaway-safe identification for battery packs, BMS and charging systems."),
 "xianlan-tongxin": ("cable-fiber-optic", "Cable & Fiber Optic",
   "Self-laminating wrap-around, flame-rated and outdoor-weatherable labels for cable, fiber and datacenter identification."),
 "yiliao-shengwu": ("medical-biotech", "Medical & Biotech",
   "Autoclave-sterilizable, cryogenic LN2 and chemical-resistant labels for laboratory, diagnostic and medical-device traceability."),
 "gangtie-yejin": ("steel-metallurgy", "Steel & Metallurgy",
   "Aluminum-foil, stainless and nickel high-temperature tags surviving 300–1200 °C heat treatment, forging and billet tracking."),
 "taoci-boli": ("ceramic-glass", "Ceramic & Glass",
   "Inorganic ultra-high-temperature (up to 1280 °C) kiln and batch labels for ceramic and glass processing."),
 "huwai-shebei": ("outdoor-equipment", "Outdoor Equipment",
   "UV-stable, waterproof and oil-resistant weatherproof nameplates for outdoor machinery, chargers and field assets."),
}

# industry L3 leaf : cn-slug -> (en-slug, en-title)
LEAF_MAP = {
 # electronics
 "pi-liuhuhan-biaoqian": ("pcb-reflow-polyimide-labels", "PCB Reflow Polyimide Labels"),
 "esd-fangjingdian-biaoqian": ("esd-pcb-labels", "ESD PCB Labels"),
 "banma-sanjiao-biaoqian": ("pcb-barcode-traceability-labels", "PCB Barcode Traceability Labels"),
 "laser-dabiao-biaoqian": ("laser-marking-high-temp-labels", "Laser-Marking High-Temp Labels"),
 "xiaoxing-yuanqi-jian-biaoqian": ("micro-component-labels", "Micro-Component Labels"),
 "naihuaxue-qingxi-biaoqian": ("flux-wash-resistant-labels", "Flux-Wash Resistant Labels"),
 "baomi-mian-biaoqian": ("smt-masking-pi-tape", "SMT Masking PI Tape"),
 # automotive
 "fache-jicang-gaowen-biaoqian": ("engine-bay-high-temp-labels", "Engine-Bay High-Temp Labels"),
 "xianshu-biaoshi-biaoqian": ("wire-harness-labels", "Wire Harness Labels"),
 "neishi-zuran-biaoqian": ("interior-fmvss302-flame-labels", "Interior FMVSS-302 Flame-Retardant Labels"),
 "lingjian-xulie-biaoqian": ("component-traceability-nameplates", "Component Traceability Nameplates"),
 "youxiang-naiyou-biaoqian": ("oil-resistant-waterproof-labels", "Oil-Resistant Waterproof Labels"),
 # ev-battery
 "dianchi-fengbian-zuran-biaoqian": ("battery-edge-ul94-flame-labels", "Battery-Edge UL94 V-0 Flame-Retardant PI Labels"),
 "hongxian-bao-hu-biaoqian": ("hv-harness-insulation-labels", "High-Voltage Harness Insulation Labels"),
 "diankong-qi-jian-biaoqian": ("bms-module-high-temp-labels", "BMS Module High-Temp Labels"),
 "chongdian-duan-biaoqian": ("charging-component-labels", "Charging-Component Traceability Labels"),
 "chegui-fanghuo-biaoqian": ("low-smoke-fireproof-labels", "Vehicle Low-Smoke Fireproof Labels"),
 # cable-fiber
 "guangxian-raoxian-biaoqian": ("fiber-wrap-around-labels", "Fiber Wrap-Around Labels"),
 "tongxin-xianlan-zuran-biaoqian": ("telecom-cable-flame-labels", "Telecom Cable Flame-Retardant Labels"),
 "dianli-xianlan-naihou-biaoqian": ("power-cable-outdoor-labels", "Power-Cable Outdoor Weatherable Labels"),
 "jiguang-ji-duan-biaoqian": ("optical-module-high-temp-labels", "Optical-Module High-Temp Labels"),
 "ji-fang-xian-shu-biaoqian": ("datacenter-cable-wrap-labels", "Datacenter Cable Wrap-Around Labels"),
 # medical
 "121du-miejun-biaoqian": ("autoclave-sterilization-labels", "121 °C Autoclave Sterilization Labels"),
 "yiwan-yedan-nidan-biaoqian": ("cryogenic-ln2-sample-labels", "Cryogenic LN2 Sample Labels"),
 "shoushu-qixie-zhuisu-biaoqian": ("surgical-instrument-labels", "Surgical-Instrument Traceability Labels"),
 "shiji-ping-naihuaxue-biaoqian": ("reagent-chemical-resistant-labels", "Reagent-Bottle Chemical-Resistant Labels"),
 "wu-lu-su-yiliao-biaoqian": ("halogen-free-medical-pi-labels", "Halogen-Free Medical PI Labels"),
 # steel
 "300du-gaowen-liuhua-biaoqian": ("heat-treatment-300c-labels", "300 °C Heat-Treatment Labels"),
 "gangpi-pi-ci-shu-biaoqian": ("billet-foil-high-temp-labels", "Billet & Aluminum-Foil High-Temp Labels"),
 "moju-nai-mo-sun-biaoqian": ("mold-abrasion-resistant-labels", "Mold Abrasion-Resistant Labels"),
 "yejin-shebei-mingpai-biaoqian": ("metallurgy-metal-nameplates", "Metallurgy Metal Nameplates"),
 # ceramic
 "yao-lu-gaowen-biaoqian": ("kiln-ultra-high-temp-labels", "Kiln Ultra-High-Temp Labels"),
 "boli-jia-gong-zhebi-biaoqian": ("glass-masking-pi-tape", "Glass-Processing Masking PI Tape"),
 "gongyi-pin-pi-ci-biaoqian": ("ceramic-batch-labels", "Ceramic Batch Labels"),
 # outdoor
 "nai-zi-wai-xian-biaoqian": ("uv-weatherproof-nameplates", "UV-Resistant Weatherproof Nameplates"),
 "fangshui-nai-lao-hua-biaoqian": ("waterproof-anti-aging-labels", "Waterproof Anti-Aging Labels"),
 "gongcheng-jixie-biaoqian": ("construction-machinery-labels", "Construction-Machinery Oil-Resistant Labels"),
 "ting-che-chang-she-bei-biaoqian": ("ev-charger-outdoor-labels", "EV-Charger Outdoor Labels"),
}

APP_MAP = {
 "smt-liuhuhan-bofuhan": ("smt-reflow-wave-soldering", "SMT Reflow & Wave-Soldering Labels",
   "Labels that survive full reflow ovens, IR and wave-soldering with no lift, char or barcode loss."),
 "fangjingdian-esd": ("esd-cleanroom", "ESD & Cleanroom Labels",
   "Surface-resistant 10⁶–10¹¹ Ω labels for static-controlled electronics assembly and cleanrooms."),
 "zuran-ul94v0": ("ul94-v0-flame-retardant", "UL94 V-0 Flame-Retardant Labels",
   "UL94 V-0 / VTM-0 rated label stock for battery, wire and electrical-safety marking."),
 "chao-di-wen-ye-dan": ("cryogenic-ln2", "Cryogenic LN2 Labels",
   "Direct-apply labels validated to −196 °C liquid-nitrogen and dry-ice storage."),
 "gaowen-rechuli": ("high-temp-heat-treatment", "High-Temp Heat-Treatment Labels",
   "Aluminum-foil and metal tags surviving 300–1200 °C furnaces, forging and annealing."),
 "yiliao-miejun": ("medical-sterilization", "Medical Sterilization Labels",
   "Autoclave, EtO and blood-bag labels holding print through 121 °C steam sterilization."),
 "xianlan-raoxian-biaoshi": ("cable-wrap-marking", "Cable Wrap-Around Marking Labels",
   "Self-laminating wrap-around labels that protect print on wire, cable and fiber."),
 "huwai-naihou": ("outdoor-uv-weatherproof", "Outdoor UV Weatherproof Labels",
   "Vinyl and PET labels resisting UV, moisture and corrosion for multi-year outdoor service."),
}

MAT_MAP = {
 "pi-juyaxianya-biaoqian": ("polyimide-pi-labels", "Polyimide (PI) High-Temp Labels",
   "The industry standard for 260–400 °C electronics: reflow, ESD, flux-wash and masking."),
 "pet-yinzi-biaoqian": ("polyester-pet-labels", "Polyester (PET) Labels",
   "Durable matte-silver and metallized PET for asset, VIN, cable and chemical-resistant marking."),
 "pp-hechengzhi-biaoqian": ("synthetic-pp-labels", "Synthetic Paper (PP) Waterproof Labels",
   "Waterproof, tear-resistant PP/PO film for cryogenic, blood-bag and removable applications."),
 "jinshu-lvfo-biaoqian": ("metal-foil-labels", "Metal & Aluminum-Foil Labels",
   "Aluminum, brass, nickel and stainless tags for 350–1280 °C metallurgy and ceramics."),
 "zhishi-biaoqian": ("paper-specialty-labels", "Paper & Specialty Labels",
   "Nylon-cloth, vinyl and paper-composite stock for cryo cable, outdoor and tag applications."),
}

# --------------------------------------------------------- helpers
def brand_of(m):
    mm = m.upper()
    if mm.startswith("XF") or mm.startswith("X"):
        return "Polyonics"
    if mm.startswith("HP") or "CX" in mm:
        return "YS Tech"
    return "ETIA"

BRAND_CLASS = {"Polyonics": "poly", "YS Tech": "ys", "ETIA": "etia"}

def prod_slug(m):
    s = m.strip().lower()
    s = re.sub(r"[（(].*?[)）]", "", s)      # drop parenthetical
    s = s.replace("+", "-plus-").replace("/", "-")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "label"

def esc(s):
    return html.escape(str(s), quote=True)

def temp_hi(t):
    m = re.findall(r"(-?\d+)", t or "")
    return int(m[-1]) if m else None

def temp_lo(t):
    m = re.findall(r"(-?\d+)", t or "")
    return int(m[0]) if m else None

MAT_EN = {"PI":"Polyimide (PI)","PET":"Polyester (PET)","PP":"Synthetic PP","PO":"Polyolefin (PO)",
 "PE":"Polyethylene (PE)","VINYL":"Vinyl","AL":"Aluminum foil","BRASS":"Brass","NICKEL":"Nickel",
 "不锈钢":"Stainless steel","尼龙":"Nylon cloth","纸":"Paper composite","inorganic":"Inorganic ceramic"}

def mat_en(m):
    return MAT_EN.get(m, m)

# --------------------------------------------------------- HTML shell
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{--green:#44B549;--blue:#1A56DB;--navy:#0f2444;--amber:#c2410c;--ink:#1a2233;--mut:#5b6676;--line:#e3e8ef;--bg:#f7f9fc}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:#fff;line-height:1.6;-webkit-font-smoothing:antialiased}
a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}
header.site{background:var(--navy);color:#fff;position:sticky;top:0;z-index:20}
header.site .wrap{display:flex;align-items:center;justify-content:space-between;height:62px}
.logo{font-weight:800;font-size:20px;color:#fff;letter-spacing:.3px}
.logo span{color:var(--green)}
nav.main a{color:#dbe4f0;font-weight:600;font-size:14px;margin-left:22px}
nav.main a:hover{color:#fff;text-decoration:none}
.hero{background:linear-gradient(160deg,#0f2444 0%,#173463 60%,#1a3d78 100%);color:#fff;padding:56px 0 48px}
.hero h1{font-size:34px;line-height:1.2;font-weight:800;max-width:820px}
.hero p{color:#c6d4e8;margin-top:14px;max-width:720px;font-size:17px}
.crumb{font-size:13px;color:var(--mut);padding:14px 0}
.crumb a{color:var(--mut)}.crumb b{color:var(--ink)}
.paths{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin:34px 0}
.pcard{border:1px solid var(--line);border-radius:14px;padding:22px;background:var(--bg)}
.pcard h3{font-size:18px;margin-bottom:6px}
.pcard .tag{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:var(--green)}
.pcard ul{list-style:none;margin-top:12px}
.pcard li{padding:5px 0;border-top:1px solid var(--line);font-size:14px}
.sec{padding:36px 0}
.sec h2{font-size:23px;margin-bottom:6px}
.sec .lede{color:var(--mut);margin-bottom:18px;max-width:760px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}
.card{border:1px solid var(--line);border-radius:12px;padding:16px;background:#fff;transition:.15s}
.card:hover{border-color:var(--blue);box-shadow:0 4px 18px rgba(26,86,219,.08)}
.card h4{font-size:15px;margin-bottom:4px}
.card p{font-size:13px;color:var(--mut)}
.card .n{font-size:12px;color:var(--green);font-weight:700;margin-top:8px}
table.matrix{width:100%;border-collapse:collapse;font-size:14px;margin-top:8px}
table.matrix th,table.matrix td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line)}
table.matrix th{background:var(--bg);font-size:12px;text-transform:uppercase;letter-spacing:.4px;color:var(--mut)}
table.matrix td.mono{font-family:ui-monospace,Menlo,monospace;font-weight:600}
.bchip{display:inline-block;font-size:11px;font-weight:700;padding:2px 8px;border-radius:20px;color:#fff}
.bchip.poly{background:#1A56DB}.bchip.ys{background:#b45309}.bchip.etia{background:#44B549}
.pain{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:8px}
.pain .item{background:var(--bg);border-left:3px solid var(--amber);padding:12px 14px;border-radius:0 8px 8px 0;font-size:14px}
.pain .item b{display:block;color:var(--amber);margin-bottom:2px}
.certs{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
.cert{font-size:12px;font-weight:700;background:#eef4ff;color:var(--blue);padding:6px 12px;border-radius:8px}
.faq{margin-top:8px}
.faq details{border:1px solid var(--line);border-radius:10px;padding:4px 16px;margin-bottom:10px}
.faq summary{font-weight:700;padding:12px 0;cursor:pointer;font-size:15px}
.faq p{padding:0 0 14px;color:var(--mut);font-size:14px}
.cta{background:var(--navy);color:#fff;border-radius:16px;padding:34px;text-align:center;margin:24px 0}
.cta h3{font-size:22px}.cta p{color:#c6d4e8;margin:8px 0 16px}
.btn{display:inline-block;background:var(--green);color:#fff;font-weight:700;padding:12px 26px;border-radius:10px}
.btn:hover{text-decoration:none;filter:brightness(1.05)}
.btn.ghost{background:transparent;border:1px solid #3a5788;color:#dbe4f0;margin-left:10px}
.xlinks{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
.xlinks a{font-size:13px;background:var(--bg);border:1px solid var(--line);padding:7px 13px;border-radius:20px;color:var(--ink)}
.xlinks a:hover{border-color:var(--blue);text-decoration:none}
.specs{list-style:none}.specs li{display:flex;justify-content:space-between;padding:11px 0;border-bottom:1px solid var(--line);font-size:14px}
.specs li span:first-child{color:var(--mut)}
.specs li span:last-child{font-weight:700}
.note{background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:14px 16px;font-size:14px;color:#92400e;margin-top:8px}
footer.site{background:var(--navy);color:#9fb0c9;padding:34px 0;margin-top:40px;font-size:13px}
footer.site .wrap{display:flex;justify-content:space-between;flex-wrap:wrap;gap:16px}
footer.site a{color:#c6d4e8}
@media(max-width:760px){.paths{grid-template-columns:1fr}.pain{grid-template-columns:1fr}.hero h1{font-size:26px}nav.main a{margin-left:14px;font-size:13px}}
"""

def page(title, desc, canonical, body, schema=None, crumb=None):
    schema_js = ""
    if schema:
        schema_js = '<script type="application/ld+json">%s</script>' % json.dumps(schema, ensure_ascii=False)
    nav = ('<a href="/industries/">Industries</a><a href="/applications/">Applications</a>'
           '<a href="/materials/">Materials</a><a href="/technical-resources/">Resources</a>'
           '<a href="/brands/">Brands</a>')
    cr = ""
    if crumb:
        parts = []
        for i,(t,u) in enumerate(crumb):
            if u and i < len(crumb)-1:
                parts.append('<a href="%s">%s</a>' % (u, esc(t)))
            else:
                parts.append('<b>%s</b>' % esc(t))
        cr = '<div class="wrap crumb">%s</div>' % ' &rsaquo; '.join(parts)
    return """<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="%s">
<meta property="og:title" content="%s"><meta property="og:type" content="website">
<style>%s</style>%s</head><body>
<header class="site"><div class="wrap"><a class="logo" href="/">ETIA<span>Label</span></a>
<nav class="main">%s</nav></div></header>
%s
%s
<footer class="site"><div class="wrap">
<div><strong style="color:#fff">ETIA Label</strong> — Industrial specialty labels for extreme environments.<br>
Authorized distribution &amp; conversion · Polyonics · YS Tech · ETIA</div>
<div><a href="/industries/">Industries</a> · <a href="/applications/">Applications</a> · <a href="/materials/">Materials</a> · <a href="/brands/">Brand Cross-Reference</a></div>
</div></footer></body></html>""" % (esc(title), esc(desc), canonical, esc(title), CSS, schema_js, nav, cr, body)

def write(path, content):
    full = os.path.join(ROOT, path.strip("/"), "index.html") if not path.endswith(".xml") and not path.endswith(".txt") else os.path.join(ROOT, path.strip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(content)

def breadcrumb_schema(items):
    return {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":i+1,"name":n,"item":SITE+u} for i,(n,u) in enumerate(items)]}

def faq_schema(qas):
    return {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in qas]}

def faq_html(qas):
    h = '<div class="faq">'
    for q,a in qas:
        h += '<details><summary>%s</summary><p>%s</p></details>' % (esc(q), esc(a))
    return h + '</div>'

def cta():
    return """<div class="cta"><h3>Need a spec match or a Brady equivalent?</h3>
<p>Send us the temperature range, substrate and print method — we'll return the exact ETIA / Polyonics / YS Tech part and free samples.</p>
<a class="btn" href="/technical-resources/">Request Samples &amp; Datasheet</a>
<a class="btn ghost" href="/brands/">Find Brady Cross-Reference</a></div>"""

# --------------------------------------------------------- product matrix
def matrix(models, limit=None):
    rows = []
    seen = set()
    for m in models:
        key = m.strip()
        if key in seen: continue
        seen.add(key)
        p = PROD.get(key)
        b = brand_of(key)
        bc = BRAND_CLASS[b]
        slug = prod_slug(key)
        if p:
            desc = mat_en(p["mat"]); temp = p["t"].replace("℃","°C"); th = p["th"]; brady = p.get("brady","")
        else:
            desc = "—"; temp = "—"; th = "—"; brady = ""
        bradyc = ('<a href="/brands/brady-cross-reference/">%s</a>' % esc(brady)) if brady else '—'
        rows.append('<tr><td class="mono"><a href="/products/%s/">%s</a></td>'
                    '<td><span class="bchip %s">%s</span></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
                    % (slug, esc(key), bc, b, esc(desc), esc(temp), esc(th), bradyc))
    if not rows:
        return None
    body = ('<table class="matrix"><thead><tr><th>Model</th><th>Brand</th><th>Material</th>'
            '<th>Temp Range</th><th>Thickness</th><th>Brady Cross-Ref</th></tr></thead><tbody>%s</tbody></table>'
            % "".join(rows))
    return body

# collect certs from product set
def collect_certs(models):
    c = set()
    for m in models:
        p = PROD.get(m.strip())
        if not p: continue
        s = (p.get("seo","")+p.get("app","")).lower()
        if "ul94" in s or "94v" in s or "阻燃" in s: c.add("UL94 V-0")
        if "ul" in s: c.add("UL Recognized")
        if "esd" in p.get("app_s","") or "防静电" in s: c.add("ESD 10⁶–10¹¹ Ω")
        if "灭菌" in s or "血袋" in s: c.add("Autoclave 121 °C")
        if "-196" in p.get("t",""): c.add("LN2 −196 °C validated")
    return c

# ============================================================ PAGE BUILDERS
all_urls = []   # (loc, group)

def track(u, grp): all_urls.append((u, grp))

# --- product detail pages -------------------------------------------------
built_products = set()
def build_product(m):
    key = m.strip()
    if key in built_products: return
    built_products.add(key)
    p = PROD.get(key)
    b = brand_of(key); bc = BRAND_CLASS[b]
    slug = prod_slug(key)
    url = "/products/%s/" % slug
    if p:
        desc = mat_en(p["mat"]); temp = p["t"].replace("℃","°C"); th = p["th"]
        brady = p.get("brady",""); ind = IND_MAP.get(p["ind_s"]); seo = p.get("seo","")
    else:
        desc="—";temp="—";th="—";brady="";ind=None;seo=""
    title = "%s — %s %s Label | ETIA Label" % (key, b, desc if desc!="—" else "Industrial")
    metad = "%s %s industrial label. Material %s, temperature %s, thickness %s.%s Datasheet, samples and Brady cross-reference from ETIA Label." % (
        b, key, desc, temp, th, (" Brady equivalent "+brady+"." if brady else ""))
    specs = '<ul class="specs">'
    specs += '<li><span>Brand</span><span><span class="bchip %s">%s</span></span></li>' % (bc,b)
    specs += '<li><span>Base material</span><span>%s</span></li>' % esc(desc)
    specs += '<li><span>Temperature range</span><span>%s</span></li>' % esc(temp)
    specs += '<li><span>Thickness</span><span>%s</span></li>' % esc(th)
    if brady:
        specs += '<li><span>Brady cross-reference</span><span><a href="/brands/brady-cross-reference/">%s</a></span></li>' % esc(brady)
    specs += '</ul>'
    xl = ""
    if p:
        links = []
        if ind: links.append('<a href="/industries/%s/">%s</a>' % (ind[0], esc(ind[1])))
        am = APP_MAP.get(p["app_s"])
        if am: links.append('<a href="/applications/%s/">%s</a>' % (am[0], esc(am[1])))
        mm = MAT_MAP.get(p["mat_s"]+"-biaoqian") or MAT_MAP.get(p["mat_s"])
        # mat_s in product uses e.g. pi-juyaxianya ; MAT_MAP keys end -biaoqian
        for k,(es,et,_) in MAT_MAP.items():
            if k.startswith(p["mat_s"]):
                links.append('<a href="/materials/%s/">%s</a>' % (es, esc(et))); break
        xl = '<div class="xlinks">%s</div>' % "".join(links)
    faqs = [
        ("What is the maximum temperature of %s?" % key,
         "%s is rated for %s. For continuous exposure stay within the upper limit; brief peaks (e.g. reflow) can exceed it — contact us for the peak profile." % (key, temp)),
        ("Is there a Brady equivalent for %s?" % key,
         ("Yes. %s cross-references to Brady %s. ETIA supplies the equivalent with free samples for qualification." % (key, brady)) if brady
         else "Send us your current Brady part number and we'll identify the closest ETIA / Polyonics / YS Tech equivalent."),
        ("Can I get samples of %s?" % key,
         "Yes — we ship free qualification samples and the full datasheet. Use the request form and include your substrate and print method."),
    ]
    body = '<section class="hero"><div class="wrap"><h1>%s</h1><p>%s</p></div></section>' % (esc(key), esc(seo or (b+" industrial specialty label")))
    body += ('<div class="wrap sec"><div style="display:grid;grid-template-columns:1fr 1fr;gap:30px">'
             '<div><h2>Specifications</h2>%s%s</div>'
             '<div><h2>Common uses</h2><p style="color:var(--mut)">%s</p>%s</div></div>' % (
             specs, xl, esc(seo or "High-performance identification for demanding industrial environments."), ""))
    body += '<h2 style="margin-top:30px">FAQ</h2>' + faq_html(faqs) + cta() + '</div>'
    crumb = [("Home","/"),("Products","/products/"),(key,url)]
    sch = [breadcrumb_schema(crumb), faq_schema(faqs),
           {"@context":"https://schema.org","@type":"Product","name":key,"brand":{"@type":"Brand","name":b},
            "description":metad,"category":desc}]
    write(url, page(title, metad, SITE+url, body, sch, crumb))
    track(url, "products")

# --- generic leaf/hub landing template ------------------------------------
def landing(url, h1, lede, models, crumb, kind, parent=None, siblings=None, extra_pain=None):
    """kind: industry-leaf / industry-hub / application / material"""
    for m in models: build_product(m)
    mat = matrix(models)
    certs = collect_certs(models)
    # pain points derived from title/kind
    pains = extra_pain or default_pains(h1)
    body = '<section class="hero"><div class="wrap"><h1>%s</h1><p>%s</p></div></section>' % (esc(h1), esc(lede))
    body += '<div class="wrap">'
    # pain
    body += '<div class="sec"><h2>The challenge</h2><div class="pain">'
    for t,d in pains:
        body += '<div class="item"><b>%s</b>%s</div>' % (esc(t), esc(d))
    body += '</div></div>'
    # product matrix
    body += '<div class="sec"><h2>Recommended products</h2>'
    if mat:
        body += '<p class="lede">%d matched parts. Every part ships with a datasheet and free qualification samples.</p>%s' % (len(set(x.strip() for x in models)), mat)
    else:
        body += ('<div class="note"><b>Engineered to spec.</b> This is a specified application in our range; '
                 'the exact stock is matched to your temperature, substrate and certification requirement. '
                 'Send your spec (or a competitor part number) and we\'ll return a validated part and samples — '
                 'often within one working day.</div>')
    body += '</div>'
    # certs
    if certs:
        body += '<div class="sec"><h2>Certifications &amp; validated performance</h2><div class="certs">'
        for c in sorted(certs):
            body += '<span class="cert">%s</span>' % esc(c)
        body += '</div></div>'
    # cross-path internal links
    if siblings:
        body += '<div class="sec"><h2>Related</h2><div class="xlinks">'
        for t,u in siblings:
            body += '<a href="%s">%s</a>' % (u, esc(t))
        body += '</div></div>'
    # FAQ
    faqs = default_faqs(h1, models)
    body += '<div class="sec"><h2>Frequently asked questions</h2>%s</div>' % faq_html(faqs)
    body += cta() + '</div>'
    title = "%s | ETIA Label" % h1
    desc = lede[:157]
    sch = [breadcrumb_schema(crumb), faq_schema(faqs)]
    write(url, page(title, desc, SITE+url, body, sch, crumb))

def default_pains(h1):
    return [
        ("Print loss under heat / solvent", "Standard labels char, curl or lose barcode legibility. Our stock holds print through the full process window."),
        ("Adhesive lift & edge peel", "Aggressive acrylic and silicone adhesives keep edges down on low-energy, oily and textured surfaces."),
        ("Traceability compliance", "Scannable 1D/2D codes survive the entire lifecycle so parts stay traceable end-to-end."),
        ("Sourcing & lead time", "In-stock convertible material and direct distribution mean short lead times and free qualification samples."),
    ]

def default_faqs(h1, models):
    temps = [temp_hi(PROD[m.strip()]["t"]) for m in models if m.strip() in PROD]
    temps = [t for t in temps if t is not None]
    hi = max(temps) if temps else None
    los = [temp_lo(PROD[m.strip()]["t"]) for m in models if m.strip() in PROD]
    los = [t for t in los if t is not None]
    lo = min(los) if los else None
    qas = [
        ("What temperature range do %s cover?" % h1.lower(),
         ("These parts span roughly %s°C to %s°C depending on model — see the temperature column in the product matrix." % (lo, hi)) if hi is not None
         else "The range is matched to your process; send your peak and continuous temperatures and we'll specify the right stock."),
        ("Do you provide free samples?",
         "Yes. Every listed part ships with free qualification samples and the full datasheet so you can validate before ordering."),
        ("Can you match a Brady / competitor part number?",
         "Yes — send the competitor part number and we'll return the closest ETIA, Polyonics or YS Tech equivalent with a spec comparison."),
    ]
    return qas

# ============================================================ BUILD
# homepage
def build_home():
    ind_cards = "".join('<div class="card"><h4><a href="/industries/%s/">%s</a></h4><p>%s</p></div>'
                        % (IND_MAP[i["slug"]][0], esc(IND_MAP[i["slug"]][1]), esc(IND_MAP[i["slug"]][2][:70]+"…"))
                        for i in tree["industries"])
    body = """<section class="hero"><div class="wrap">
<h1>Industrial specialty labels that survive reflow, cryo, acid and 1200&nbsp;°C furnaces.</h1>
<p>Find the exact label three ways — by your industry, by your process, or by base material. Every path lands on a datasheet-backed part with a Brady cross-reference and free samples.</p>
<div style="margin-top:20px"><a class="btn" href="/industries/">Browse by Industry</a>
<a class="btn ghost" href="/brands/">Brady Cross-Reference</a></div></div></section>
<div class="wrap"><div class="paths">
<div class="pcard"><div class="tag">Path 1</div><h3><a href="/industries/">By Industry</a></h3>
<p style="color:var(--mut);font-size:14px">Start from your sector — electronics, automotive, medical, steel and more.</p>
<ul><li>Electronics &amp; Semiconductor</li><li>Automotive · EV &amp; Battery</li><li>Medical &amp; Biotech</li><li>Steel · Ceramic · Cable</li></ul></div>
<div class="pcard"><div class="tag">Path 2</div><h3><a href="/applications/">By Application</a></h3>
<p style="color:var(--mut);font-size:14px">Start from your process — the heat, chemistry or environment the label must survive.</p>
<ul><li>SMT Reflow &amp; Wave Soldering</li><li>Cryogenic LN2 · Sterilization</li><li>Heat-Treatment 300–1200&nbsp;°C</li><li>ESD · UL94 V-0 · Outdoor UV</li></ul></div>
<div class="pcard"><div class="tag">Path 3</div><h3><a href="/materials/">By Base Material</a></h3>
<p style="color:var(--mut);font-size:14px">Start from the substrate — polyimide, PET, PP, metal foil or specialty.</p>
<ul><li>Polyimide (PI) High-Temp</li><li>Polyester (PET)</li><li>Synthetic PP · Paper/Specialty</li><li>Metal &amp; Aluminum Foil</li></ul></div>
</div>
<div class="sec"><h2>All industries</h2><div class="grid">%s</div></div>
%s</div>""" % (ind_cards, cta())
    sch = {"@context":"https://schema.org","@type":"Organization","name":"ETIA Label","url":SITE,
           "description":"Industrial specialty labels for extreme temperature, cryogenic, chemical and outdoor environments."}
    write("/", page("ETIA Label — Industrial Specialty Labels for Extreme Environments",
        "Find high-temperature, cryogenic, chemical-resistant and flame-retardant industrial labels by industry, application or material. Polyimide, PET, metal-foil. Brady cross-reference and free samples.",
        SITE+"/", body, sch))
    track("/", "root")

def build_industries():
    # index
    cards = "".join('<div class="card"><h4><a href="/industries/%s/">%s</a></h4><p>%s</p><div class="n">%d application pages</div></div>'
                    % (IND_MAP[i["slug"]][0], esc(IND_MAP[i["slug"]][1]), esc(IND_MAP[i["slug"]][2]), len(i["sub"]))
                    for i in tree["industries"])
    crumb=[("Home","/"),("Industries","/industries/")]
    body='<section class="hero"><div class="wrap"><h1>Labels by Industry</h1><p>Eight industries, each with process-specific application pages that land on datasheet-backed parts.</p></div></section><div class="wrap"><div class="sec"><div class="grid">%s</div></div>%s</div>'%(cards,cta())
    write("/industries/", page("Industrial Labels by Industry | ETIA Label",
        "Browse industrial specialty labels by industry: electronics, automotive, EV & battery, medical, steel, ceramic, cable and outdoor.",
        SITE+"/industries/", body, [breadcrumb_schema(crumb)], crumb))
    track("/industries/","industries")
    # hubs + leaves
    for i in tree["industries"]:
        es, et, blurb = IND_MAP[i["slug"]]
        hub_url = "/industries/%s/" % es
        crumb=[("Home","/"),("Industries","/industries/"),(et,hub_url)]
        leaf_cards=""
        for sub in i["sub"]:
            ls, lt = LEAF_MAP[sub["slug"]]
            n=len(set(x.strip() for x in sub["products"]))
            leaf_cards+='<div class="card"><h4><a href="/industries/%s/%s/">%s</a></h4><div class="n">%s</div></div>'%(
                es, ls, esc(lt), ("%d products"%n) if n else "Engineered to spec")
        # hub aggregate products
        agg=[]
        for sub in i["sub"]: agg+=sub["products"]
        sib=[("%s (Application)"%APP_MAP[a["slug"]][1], "/applications/%s/"%APP_MAP[a["slug"]][0]) for a in tree["applications"][:4]]
        mat=matrix(agg)
        body='<section class="hero"><div class="wrap"><h1>%s Labels</h1><p>%s</p></div></section><div class="wrap">'%(esc(et),esc(blurb))
        body+='<div class="sec"><h2>Application areas</h2><p class="lede">Select your process to reach matched parts.</p><div class="grid">%s</div></div>'%leaf_cards
        if mat:
            body+='<div class="sec"><h2>Featured parts across %s</h2>%s</div>'%(esc(et),mat)
        body+='<div class="sec"><h2>Explore other paths</h2><div class="xlinks"><a href="/applications/">By Application</a><a href="/materials/">By Material</a><a href="/brands/">Brady Cross-Reference</a></div></div>'
        faqs=default_faqs("%s labels"%et, agg)
        body+='<div class="sec"><h2>FAQ</h2>%s</div>'%faq_html(faqs)+cta()+'</div>'
        sch=[breadcrumb_schema(crumb),faq_schema(faqs)]
        write(hub_url, page("%s Labels — High-Temp, Traceability & More | ETIA Label"%et, blurb[:157], SITE+hub_url, body, sch, crumb))
        track(hub_url,"industries")
        for sub in i["sub"]:
            ls, lt = LEAF_MAP[sub["slug"]]
            lurl="/industries/%s/%s/"%(es,ls)
            lcrumb=[("Home","/"),("Industries","/industries/"),(et,hub_url),(lt,lurl)]
            lede="%s for %s applications — matched to temperature, substrate and certification, with free qualification samples."%(lt, et.lower())
            sib=[(et+" (hub)",hub_url)]
            for sub2 in i["sub"]:
                if sub2["slug"]!=sub["slug"]:
                    ls2,lt2=LEAF_MAP[sub2["slug"]]
                    sib.append((lt2,"/industries/%s/%s/"%(es,ls2)))
            landing(lurl, lt, lede, sub["products"], lcrumb, "industry-leaf", siblings=sib[:6])
            track(lurl,"industries")

def build_applications():
    cards="".join('<div class="card"><h4><a href="/applications/%s/">%s</a></h4><p>%s</p></div>'
                  %(APP_MAP[a["slug"]][0],esc(APP_MAP[a["slug"]][1]),esc(APP_MAP[a["slug"]][2][:70]+"…")) for a in tree["applications"])
    crumb=[("Home","/"),("Applications","/applications/")]
    body='<section class="hero"><div class="wrap"><h1>Labels by Application</h1><p>Start from the process and its stresses — heat, cryo, chemistry, static or weather — and reach the parts validated for it.</p></div></section><div class="wrap"><div class="sec"><div class="grid">%s</div></div>%s</div>'%(cards,cta())
    write("/applications/", page("Industrial Labels by Application | ETIA Label",
        "Browse labels by process: SMT reflow, cryogenic LN2, heat-treatment, sterilization, ESD, UL94 V-0 flame and outdoor UV.",
        SITE+"/applications/", body, [breadcrumb_schema(crumb)], crumb))
    track("/applications/","applications")
    for a in tree["applications"]:
        es,et,blurb=APP_MAP[a["slug"]]
        url="/applications/%s/"%es
        crumb=[("Home","/"),("Applications","/applications/"),(et,url)]
        sib=[(IND_MAP[i["slug"]][1]+" (Industry)","/industries/%s/"%IND_MAP[i["slug"]][0]) for i in tree["industries"][:5]]
        sib+=[("By Material","/materials/")]
        landing(url, et, blurb, a["products"], crumb, "application", siblings=sib)
        track(url,"applications")

def build_materials():
    cards="".join('<div class="card"><h4><a href="/materials/%s/">%s</a></h4><p>%s</p></div>'
                  %(MAT_MAP[m["slug"]][0],esc(MAT_MAP[m["slug"]][1]),esc(MAT_MAP[m["slug"]][2][:70]+"…")) for m in tree["materials"])
    crumb=[("Home","/"),("Materials","/materials/")]
    body='<section class="hero"><div class="wrap"><h1>Labels by Base Material</h1><p>Start from the substrate — the film or metal decides temperature ceiling, chemical resistance and print method.</p></div></section><div class="wrap"><div class="sec"><div class="grid">%s</div></div>%s</div>'%(cards,cta())
    write("/materials/", page("Industrial Labels by Base Material | ETIA Label",
        "Browse by substrate: polyimide (PI), polyester (PET), synthetic PP, metal & aluminum foil, and paper/specialty label stock.",
        SITE+"/materials/", body, [breadcrumb_schema(crumb)], crumb))
    track("/materials/","materials")
    for m in tree["materials"]:
        es,et,blurb=MAT_MAP[m["slug"]]
        url="/materials/%s/"%es
        crumb=[("Home","/"),("Materials","/materials/"),(et,url)]
        sib=[(APP_MAP[a["slug"]][1]+" (Application)","/applications/%s/"%APP_MAP[a["slug"]][0]) for a in tree["applications"][:5]]
        sib+=[("By Industry","/industries/")]
        landing(url, et, blurb, m["products"], crumb, "material", siblings=sib)
        track(url,"materials")

def build_products_index():
    # gather all
    allm=set(built_products)
    rows=[]
    for m in sorted(allm):
        b=brand_of(m);bc=BRAND_CLASS[b];p=PROD.get(m)
        temp=p["t"].replace("℃","°C") if p else "—"
        desc=mat_en(p["mat"]) if p else "—"
        rows.append('<tr><td class="mono"><a href="/products/%s/">%s</a></td><td><span class="bchip %s">%s</span></td><td>%s</td><td>%s</td></tr>'%(prod_slug(m),esc(m),bc,b,esc(desc),esc(temp)))
    crumb=[("Home","/"),("Products","/products/")]
    body='<section class="hero"><div class="wrap"><h1>Product Index</h1><p>All %d parts in the ETIA Label V1.0 catalog — Polyonics, YS Tech and ETIA.</p></div></section><div class="wrap"><div class="sec"><table class="matrix"><thead><tr><th>Model</th><th>Brand</th><th>Material</th><th>Temp</th></tr></thead><tbody>%s</tbody></table></div>%s</div>'%(len(allm),"".join(rows),cta())
    write("/products/", page("Product Index — Industrial Specialty Labels | ETIA Label",
        "Full index of ETIA Label industrial parts across polyimide, PET, PP, metal-foil and specialty stock.",
        SITE+"/products/", body, [breadcrumb_schema(crumb)], crumb))
    track("/products/","products")

def build_brands():
    crumb=[("Home","/"),("Brands","/brands/")]
    # brady cross ref table
    rows=[]
    for m,p in sorted(PROD.items()):
        if p.get("brady"):
            b=brand_of(m);bc=BRAND_CLASS[b]
            rows.append('<tr><td class="mono">%s</td><td class="mono"><a href="/products/%s/">%s</a></td><td><span class="bchip %s">%s</span></td><td>%s</td></tr>'
                        %(esc(p["brady"]),prod_slug(m),esc(m),bc,b,esc(mat_en(p["mat"]))))
    body='<section class="hero"><div class="wrap"><h1>Brand Cross-Reference</h1><p>Searching a Brady part number? Find the equivalent ETIA, Polyonics or YS Tech label — same performance, free samples.</p></div></section><div class="wrap">'
    body+='<div class="sec"><h2>Brady &rarr; ETIA equivalents</h2><p class="lede">%d cross-referenced parts. Send any part number not listed and we\'ll match it.</p><table class="matrix"><thead><tr><th>Brady Part</th><th>ETIA Equivalent</th><th>Brand</th><th>Material</th></tr></thead><tbody>%s</tbody></table></div>'%(len(rows),"".join(rows))
    body+='<div class="sec"><h2>Our brands</h2><div class="grid"><div class="card"><h4><span class="bchip poly">Polyonics</span></h4><p>Ultra-thin polyimide for PCB reflow, ESD and flame-retardant electronics labeling.</p></div><div class="card"><h4><span class="bchip ys">YS Tech</span></h4><p>Metal, foil and inorganic ceramic tags for 300–1280 °C metallurgy and kilns.</p></div><div class="card"><h4><span class="bchip etia">ETIA</span></h4><p>Full-range PET, PP and specialty converter stock — cryo, medical, cable and outdoor.</p></div></div></div>'
    body+=cta()+'</div>'
    write("/brands/", page("Brady Cross-Reference & Brand Guide | ETIA Label",
        "Find ETIA, Polyonics and YS Tech equivalents for Brady industrial label part numbers, with material and temperature match.",
        SITE+"/brands/", body, [breadcrumb_schema(crumb)], crumb))
    track("/brands/","tech-resources")
    write("/brands/brady-cross-reference/", page("Brady Label Cross-Reference Table | ETIA Label",
        "Complete Brady-to-ETIA industrial label cross-reference with temperature and material match.",
        SITE+"/brands/brady-cross-reference/", body, [breadcrumb_schema([("Home","/"),("Brands","/brands/"),("Brady Cross-Reference","/brands/brady-cross-reference/")])], [("Home","/"),("Brands","/brands/"),("Brady Cross-Reference","/brands/brady-cross-reference/")]))
    track("/brands/brady-cross-reference/","tech-resources")

def build_resources():
    crumb=[("Home","/"),("Technical Resources","/technical-resources/")]
    faqs=[
        ("How do I choose a high-temperature label?","Match three things: peak process temperature, exposure time, and the surface + print method. Polyimide covers ~260–400 °C; above that use metal foil or inorganic ceramic stock. Send us the numbers and we'll specify it."),
        ("What's the difference between continuous and peak temperature?","Continuous is what the label sees for hours/days in service; peak is a brief spike such as a reflow oven. A label can survive a higher peak than its continuous rating — always spec both."),
        ("Can I get free samples before ordering?","Yes. Every part ships with free qualification samples and the datasheet so you can validate on your process first."),
        ("Do you supply Brady equivalents?","Yes — send the Brady part number and we'll return the closest ETIA, Polyonics or YS Tech match with a side-by-side spec comparison."),
    ]
    body='<section class="hero"><div class="wrap"><h1>Technical Resources</h1><p>Selection guides, datasheets and sample requests for industrial specialty labels.</p></div></section><div class="wrap">'
    body+='<div class="sec"><h2>Selection guide</h2><div class="pain">'
    for t,d in [("By temperature","Under 150 °C: PET/PP. 150–300 °C: polyimide. 300–600 °C: aluminum/nickel foil. Above 600 °C: inorganic ceramic (to 1280 °C)."),
                ("By environment","Cryo/LN2 → PP or nylon-cloth to −196 °C. Chemical/oil → topcoated PET or PI. Outdoor → UV-stable vinyl/PET."),
                ("By print method","Thermal transfer, laser, or pre-print — each needs a compatible topcoat. Tell us your printer and ribbon."),
                ("By compliance","UL94 V-0, ESD 10⁶–10¹¹ Ω, FMVSS-302, autoclave 121 °C — filterable across the catalog.")]:
        body+='<div class="item"><b>%s</b>%s</div>'%(esc(t),esc(d))
    body+='</div></div>'
    body+='<div class="sec"><h2>FAQ</h2>%s</div>'%faq_html(faqs)+cta()+'</div>'
    write("/technical-resources/", page("Technical Resources — Label Selection Guide | ETIA Label",
        "How to choose industrial labels by temperature, environment, print method and compliance. Datasheets and free samples.",
        SITE+"/technical-resources/", body, [breadcrumb_schema(crumb),faq_schema(faqs)], crumb))
    track("/technical-resources/","tech-resources")

# --------------------------------------------------------- sitemaps
def build_sitemaps():
    groups={}
    for u,g in all_urls:
        groups.setdefault(g,[]).append(u)
    smap={"root":"sitemap-core.xml","industries":"sitemap-industries.xml","applications":"sitemap-applications.xml",
          "materials":"sitemap-materials.xml","products":"sitemap-products.xml","tech-resources":"sitemap-tech-resources.xml"}
    for g,fname in smap.items():
        urls=groups.get(g,[])
        if g=="root": urls=groups.get("root",[])
        xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for u in urls:
            xml+='  <url><loc>%s%s</loc><changefreq>weekly</changefreq></url>\n'%(SITE,u)
        xml+='</urlset>\n'
        open(os.path.join(ROOT,fname),"w").write(xml)
    idx='<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for fname in smap.values():
        idx+='  <sitemap><loc>%s/%s</loc></sitemap>\n'%(SITE,fname)
    idx+='</sitemapindex>\n'
    open(os.path.join(ROOT,"sitemap-index.xml"),"w").write(idx)
    open(os.path.join(ROOT,"robots.txt"),"w").write("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap-index.xml\n"%SITE)

# --------------------------------------------------------- run
# clean old build dirs (keep .git, README)
for d in ["industries","applications","materials","products","brands","technical-resources"]:
    p=os.path.join(ROOT,d)
    if os.path.isdir(p): shutil.rmtree(p)
for f in os.listdir(ROOT):
    if f.startswith("sitemap") or f=="robots.txt": os.remove(os.path.join(ROOT,f))

build_home()
build_industries()
build_applications()
build_materials()
build_products_index()
build_brands()
build_resources()
build_sitemaps()

print("Pages tracked:", len(all_urls))
print("Products built:", len(built_products))
from collections import Counter
print(Counter(g for _,g in all_urls))
