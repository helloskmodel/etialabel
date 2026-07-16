#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ETIALABEL overseas (Google SEO) 3-path static site generator."""
import json, os, re, html, shutil

# _build/ holds this script + data; site output goes to the repo root (its parent).
BUILD_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BUILD_DIR)
DATA_DIR = os.path.join(BUILD_DIR, "data")
SITE = "https://www.etialabel.com"
BRAND = "ETIA Label"

# ---- language / i18n scaffolding (English default; zh/th/vi layer in later) ----
LANGS = ["en"]            # add "zh", "th", "vi" when translated content is ready
DEFAULT_LANG = "en"
LANG_PREFIX = {"en": ""}  # default language served at root; others go under /<lang>/
HREFLANG = {"en": "en"}   # BCP-47 codes for <link rel="alternate" hreflang>

# ---------------------------------------------------------------- load data
tree = json.load(open(os.path.join(DATA_DIR, "site_tree.json")))
prods = json.load(open(os.path.join(DATA_DIR, "cn_products.json")))
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
   "Aluminum-foil, stainless and nickel high-temperature tags surviving 300–1300 °C heat treatment, forging and billet tracking."),
 "taoci-boli": ("ceramic-glass", "Ceramic & Glass",
   "Inorganic ultra-high-temperature (up to 1300 °C) kiln and batch labels for ceramic and glass processing."),
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
   "Aluminum-foil and metal tags surviving 300–1300 °C furnaces, forging and annealing."),
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
   "Aluminum, brass, nickel and stainless tags for 350–1300 °C metallurgy and ceramics."),
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

# Chinese variant annotations that ride along in model numbers -> English suffix.
# Kept (translated) rather than dropped, so e.g. E-8531 and E-8531彩色 stay distinct.
VARIANT_EN = [("激光镭射","Laser"),("镭射","Laser"),("彩色","Color"),("底纸","Liner")]

def model_variants(m):
    out = []
    for cn, en in VARIANT_EN:
        if cn in (m or "") and en not in out:
            out.append(en)
    return out

def prod_slug(m):
    s = m.strip().lower()
    s = re.sub(r"[（(].*?[)）]", "", s)      # drop parenthetical
    s = s.replace("+", "-plus-").replace("/", "-")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    base = s or "label"
    for v in model_variants(m):
        base += "-" + v.lower()
    return base

def clean_model(m):
    """Display name for a model number: drop Chinese annotations like （激光镭射） or
    底纸 that ride along in the source data, keep the ASCII part number (incl +PET)."""
    s = (m or "").strip()
    vs = model_variants(s)
    s = re.sub(r"[（(][^)）]*[)）]", "", s)          # parentheticals (Chinese or ASCII)
    s = re.sub(r"[一-鿿　-〿]+", "", s)  # any remaining CJK
    s = re.sub(r"\s+", " ", s).strip(" -")
    if vs:
        s += " (%s)" % "/".join(vs)
    return s

def _fmt_c(n):
    return ("−%d °C" % abs(n)) if n < 0 else (("+%d °C" % n) if n > 0 else "0 °C")

def fmt_temp(t):
    """'-40℃-350℃' -> '−40 °C to +350 °C'. The separator between low and high is a
    hyphen, so it must not be read as the high value's sign."""
    if not t:
        return "—"
    # split on the degree mark; each segment is one endpoint (may carry a leading separator)
    segs = [s for s in re.split(r"[℃°]C?", t) if s.strip()]
    def endpoint(seg, is_hi):
        seg = seg.strip()
        if is_hi:
            seg = seg.lstrip("-–~ ")   # leading char here is the range separator, not a sign
        m = re.search(r"-?\d+", seg)
        return int(m.group()) if m else None
    if len(segs) >= 2:
        lo, hi = endpoint(segs[0], False), endpoint(segs[1], True)
        if lo is not None and hi is not None:
            return "%s to %s" % (_fmt_c(lo), _fmt_c(hi))
    m = re.search(r"-?\d+", t)
    return _fmt_c(int(m.group())) if m else t

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

# The source `seo` field is Chinese positioning copy (zh source, kept in data but
# never rendered in the English site). Derive an English attribute set from it so
# product pages read as native English, not translated Chinese.
SEO_ATTR = [
 ("高性能","high-performance"),("经济型","economy-grade"),("低成本","economy-grade"),
 ("超粘","aggressive-adhesive"),("防静电","ESD anti-static"),("esd","ESD anti-static"),
 ("耐油污","oil-resistant"),("耐油","oil-resistant"),("陶瓷","ceramic ultra-high-temperature"),
 ("轮胎硫化","tire-vulcanization"),("阻燃","flame-retardant"),
 ("ul94vtm-0","UL94 VTM-0 flame-retardant"),("ul94","UL94 flame-retardant"),("vtm-0","UL94 VTM-0 flame-retardant"),
 ("线缆","cable-marking"),("可移除","removable"),("尼龙布","nylon-cloth"),
 ("液氮","cryogenic LN2"),("血袋","blood-bag"),("血液","blood-tube"),
 ("热处理","heat-treatment"),("耐腐蚀","corrosion-resistant"),
 ("耐户外","outdoor-weatherable"),("户外","outdoor-weatherable"),("耐高温","high-temperature"),
]

def seo_attrs_en(seo):
    """Ordered, de-duplicated English attribute phrases pulled from the zh seo string."""
    s = (seo or "").lower()
    out = []
    for cn, en in SEO_ATTR:
        if cn in s and en not in out:
            out.append(en)
    return out

def app_en_short(app_s):
    """English application phrase (without a trailing 'Labels'), or ''."""
    am = APP_MAP.get(app_s)
    if not am:
        return ""
    t = am[1]
    for suf in (" Labels"," Label"," High-Temp Labels"):
        if t.endswith(suf):
            t = t[:-len(suf)]
    return t.strip()

def product_desc_en(p, brand):
    """Native-English one-line descriptor for a product hero / meta."""
    if not p:
        return "%s industrial specialty label" % brand
    attrs = seo_attrs_en(p.get("seo",""))
    ul = any(a.startswith("UL94") for a in attrs)
    lead = ", ".join(a for a in attrs if not a.startswith("UL94"))
    matname = mat_en(p["mat"])
    temp = fmt_temp(p["t"])
    app = app_en_short(p.get("app_s",""))
    parts = []
    if p.get("seo","").startswith("符合ul") or ul:
        parts.append("UL-recognized")
    if lead:
        parts.append(lead)
    parts.append(matname)
    desc = " ".join(parts)
    if app:
        desc += " label for %s" % app
    else:
        desc += " industrial label"
    desc += ", rated %s." % temp
    # Capitalize first letter
    return desc[0].upper() + desc[1:]

# --------------------------------------------------------- HTML shell
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{
  /* AGENTS.md design tokens — single palette, shared with the UV site */
  --blue-deep:#143C96;   /* brand navy — headings + the one dark region */
  --blue:#1A56DB;        /* brand blue — links, primary accent */
  --green:#41A62A;       /* brand green — CTA buttons, tags */
  --green-d:#358B22;     /* green hover */
  --accent-green:#63C94A;/* bright green — glow / decoration */
  --ink:#111827;         /* body text */
  --mut:#667085;         /* muted / secondary text */
  --soft-blue:#EEF6FF;   /* soft-blue block bg / hero gradient */
  --soft-green:#F1FAEF;  /* soft-green block bg / hero gradient */
  --bg:#f6f8fb;          /* light-gray content bg */
  --line:#D9E4EA;        /* card / divider borders */
  --line-soft:#EAF0F5;
  --amber:#b45309;
}
html{scroll-behavior:smooth}
body{font-family:"Inter","PingFang SC","Microsoft YaHei","Noto Sans SC","Noto Sans Thai",system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:#fff;line-height:1.6;-webkit-font-smoothing:antialiased}
a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}
img{max-width:100%}
h1,h2,h3{letter-spacing:-.018em;text-wrap:balance}
.wrap{max-width:1200px;margin:0 auto;padding:0 20px}
/* ---- Nav (AGENTS 2.1): white, sticky, border-b ---- */
header.site{background:#fff;border-bottom:1px solid #e5e7eb;box-shadow:0 1px 2px rgba(16,24,40,.04);position:sticky;top:0;z-index:50}
header.site .wrap{display:flex;align-items:center;justify-content:space-between;height:64px;gap:16px}
.logo{font-weight:800;font-size:20px;color:var(--blue-deep);letter-spacing:.2px;display:flex;align-items:center;gap:9px}
.logo:hover{text-decoration:none}
.logo .mark{width:28px;height:28px;border-radius:7px;background:var(--green);display:inline-flex;align-items:center;justify-content:center;color:#fff;font-size:15px;font-weight:900}
.logo span{color:var(--green)}
.nav-right{display:flex;align-items:center;gap:4px;flex-wrap:wrap;justify-content:flex-end}
nav.main{display:flex;flex-wrap:wrap;align-items:center}
nav.main a{color:#4b5563;font-weight:500;font-size:14px;margin-left:22px;padding:20px 0;border-bottom:2px solid transparent}
nav.main a:hover{color:var(--blue);text-decoration:none;border-bottom-color:var(--blue)}
.lang{margin-left:20px;font-size:13px;font-weight:600;color:#4b5563;border:1px solid #e5e7eb;border-radius:8px;padding:6px 10px;background:#fff}
.nav-cta{margin-left:16px;background:var(--green);color:#fff;font-weight:700;font-size:14px;padding:10px 16px;border-radius:10px;transition:.15s;white-space:nowrap}
.nav-cta:hover{background:var(--green-d);text-decoration:none;color:#fff}
/* CSS-only mobile hamburger (no JS) */
.navtoggle{display:none}
.hamb{display:none;flex-direction:column;gap:4px;cursor:pointer;padding:9px;border:1px solid #e5e7eb;border-radius:9px;background:#fff}
.hamb span{display:block;width:20px;height:2px;background:#374151;border-radius:2px}
/* ---- Hero (AGENTS 3.1): LIGHT gradient, never dark ---- */
.hero{background:linear-gradient(135deg,#fff 0%,var(--soft-blue) 55%,var(--soft-green) 100%);border-bottom:1px solid var(--line);padding:60px 0 54px}
.eyebrow{font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.18em;color:var(--green);display:block}
.hero h1{font-size:40px;line-height:1.14;font-weight:800;color:var(--blue-deep);max-width:860px;margin-top:14px}
.hero p{color:var(--mut);margin-top:16px;max-width:730px;font-size:17px}
.hero .btns{margin-top:26px;display:flex;flex-wrap:wrap;gap:12px}
/* ---- Trust strip (AGENTS 4.1): one row of authorization / proof points ---- */
.tstrip{background:var(--bg);border-bottom:1px solid var(--line)}
.tstrip .wrap{display:flex;flex-wrap:wrap;gap:10px 26px;padding:16px 20px;justify-content:center}
.tstrip .ti{display:flex;align-items:center;gap:8px;font-size:13px;font-weight:600;color:#374151}
.tstrip .ti .dot{width:7px;height:7px;border-radius:50%;background:var(--green);flex:none}
.crumb{font-size:13px;color:var(--mut);padding:14px 0}
.crumb a{color:var(--mut)}.crumb b{color:var(--ink)}
.paths{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin:36px 0}
.pcard{border:1px solid var(--line);border-radius:18px;padding:24px;background:#fff;box-shadow:0 10px 35px rgba(20,60,150,.05);transition:.15s}
.pcard:hover{border-color:var(--blue);box-shadow:0 16px 44px rgba(20,60,150,.12);transform:translateY(-2px)}
.pcard h3{font-size:18px;margin:2px 0 6px}.pcard h3 a{color:var(--blue-deep)}
.pcard .tag{font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.14em;color:var(--green)}
.pcard ul{list-style:none;margin-top:12px}
.pcard li{padding:6px 0;border-top:1px solid var(--line-soft);font-size:14px;color:var(--mut)}
.sec{padding:36px 0}
.sec h2{font-size:26px;margin-bottom:6px;color:var(--blue-deep);text-wrap:balance}
.sec .lede{color:var(--mut);margin-bottom:18px;max-width:760px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px}
.card{border:1px solid var(--line);border-top:3px solid var(--blue);border-radius:16px;padding:18px;background:#fff;box-shadow:0 10px 35px rgba(20,60,150,.06);transition:.15s}
.card:nth-child(even){border-top-color:var(--green)}
.card:hover{border-color:var(--blue);box-shadow:0 16px 44px rgba(20,60,150,.12);transform:translateY(-2px)}
.card h4{font-size:15px;margin-bottom:4px}.card h4 a{color:var(--blue-deep)}
.card p{font-size:13px;color:var(--mut)}
.card .n{font-size:12px;color:var(--green-d);font-weight:700;margin-top:8px}
.trust{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:8px}
.trust .t{background:#fff;border:1px solid var(--line);border-top:3px solid var(--blue);border-radius:16px;padding:22px;box-shadow:0 10px 35px rgba(20,60,150,.06)}
.trust .t:nth-child(even){border-top-color:var(--green)}
.trust .t b{display:block;color:var(--blue-deep);font-size:16px;margin-bottom:4px}
.trust .t p{color:var(--mut);font-size:14px}
.offices{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-top:8px}
.office{border:1px solid var(--line);border-top:3px solid var(--green);border-radius:12px;padding:20px;background:#fff}
.office h3{font-size:17px;color:var(--blue-deep);margin-bottom:4px}
.office .role{font-weight:700;font-size:14px;margin-bottom:8px}
.office .role span{color:var(--mut);font-weight:600}
.office .addr{color:var(--mut);font-size:14px;margin-bottom:12px}
.office .crows{list-style:none;display:flex;flex-direction:column;gap:7px}
.office .crows li{font-size:14px;display:flex;gap:8px;align-items:baseline}
.office .crows .ic{color:var(--blue);font-weight:700;width:16px;flex:none;text-align:center}
table.matrix{width:100%;border-collapse:collapse;font-size:14px;margin-top:8px}
.tablewrap{overflow-x:auto}
table.matrix th,table.matrix td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line)}
table.matrix th{background:var(--bg);font-size:12px;text-transform:uppercase;letter-spacing:.4px;color:var(--mut)}
table.matrix td.mono{font-family:ui-monospace,Menlo,monospace;font-weight:600}
.bchip{display:inline-block;font-size:11px;font-weight:700;padding:2px 9px;border-radius:20px;color:#fff}
.bchip.poly{background:var(--blue)}.bchip.ys{background:var(--amber)}.bchip.etia{background:var(--green)}
.bchip.flexcon{background:#0f766e}.bchip.computype{background:#6d28d9}
.pain{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:8px}
.pain .item{background:var(--bg);border-left:3px solid var(--amber);padding:12px 14px;border-radius:0 8px 8px 0;font-size:14px}
.pain .item b{display:block;color:var(--amber);margin-bottom:2px}
.certs{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
.cert{font-size:12px;font-weight:700;background:#eaf1ff;color:var(--blue);padding:6px 12px;border-radius:8px;border:1px solid #d6e2fb}
.faq{margin-top:8px}
.faq details{border:1px solid var(--line);border-radius:10px;padding:4px 16px;margin-bottom:10px}
.faq summary{font-weight:700;padding:12px 0;cursor:pointer;font-size:15px}
.faq p{padding:0 0 14px;color:var(--mut);font-size:14px}
/* ---- Case / CTA — the ONE dark region (AGENTS 4.1) ---- */
.cta{background:linear-gradient(135deg,var(--blue-deep),var(--blue));color:#fff;border-radius:22px;padding:44px 40px;text-align:center;margin:28px 0}
.cta h3{font-size:24px;text-wrap:balance}.cta p{color:#cfdcf5;margin:12px auto 18px;max-width:640px}
.cta .btns{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.btn{display:inline-block;background:var(--green);color:#fff;font-weight:700;padding:13px 26px;border-radius:12px;border:1.5px solid var(--green);transition:.15s}
.btn:hover{text-decoration:none;background:var(--green-d);border-color:var(--green-d);transform:translateY(-1px)}
.btn.ghost{background:#fff;color:var(--blue-deep);border:1.5px solid #D4DFEC}
.btn.ghost:hover{background:#fff;border-color:var(--blue-deep);color:var(--blue);transform:translateY(-1px)}
/* on the dark CTA, the secondary button stays dark-friendly */
.cta .btn.ghost{background:transparent;color:#e3ebfb;border-color:#5c7fd6}
.cta .btn.ghost:hover{background:rgba(255,255,255,.08);border-color:#8aa6e8;color:#fff}
.xlinks{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
.xlinks a{font-size:13px;background:var(--bg);border:1px solid var(--line);padding:7px 13px;border-radius:20px;color:var(--ink)}
.xlinks a:hover{border-color:var(--blue);text-decoration:none}
.specs{list-style:none}.specs li{display:flex;justify-content:space-between;padding:11px 0;border-bottom:1px solid var(--line);font-size:14px}
.specs li span:first-child{color:var(--mut)}
.specs li span:last-child{font-weight:700}
.note{background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:14px 16px;font-size:14px;color:#92400e;margin-top:8px}
/* ---- Footer (AGENTS 2.2): light, 4-column + bottom bar ---- */
footer.site{background:#f8f9fb;border-top:1px solid #e5e7eb;color:var(--mut);margin-top:56px;font-size:13px}
footer.site .fcols{display:grid;grid-template-columns:1.5fr 1fr 1fr 1.2fr;gap:32px;padding:48px 0 32px}
footer.site .fcol h4{font-size:14px;font-weight:700;color:var(--blue);margin-bottom:12px}
footer.site .fcol a{display:block;color:#6b7280;font-size:13px;padding:4px 0}
footer.site .fcol a:hover{color:var(--blue);text-decoration:none}
footer.site .flogo{font-weight:800;font-size:18px;color:var(--blue-deep);display:flex;align-items:center;gap:8px}
footer.site .flogo:hover{text-decoration:none}
footer.site .flogo .mark{width:26px;height:26px;border-radius:6px;background:var(--green);display:inline-flex;align-items:center;justify-content:center;color:#fff;font-weight:900;font-size:14px}
footer.site .flogo span{color:var(--green)}
footer.site .ftag{color:var(--mut);font-size:13px;margin-top:14px;max-width:280px;line-height:1.55}
footer.site .fmail{color:var(--green);font-weight:700}
footer.site .fbar{border-top:1px solid #e5e7eb;padding:18px 0;display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;color:#9aa4b2;font-size:12px}
footer.site .fbar a{color:#9aa4b2}
@media(max-width:900px){footer.site .fcols{grid-template-columns:1fr 1fr}}
@media(max-width:760px){
  .paths{grid-template-columns:1fr}.pain{grid-template-columns:1fr}.trust{grid-template-columns:1fr}.hero h1{font-size:29px}
  .hamb{display:flex}
  .nav-right{display:none;position:absolute;top:64px;left:0;right:0;background:#fff;border-bottom:1px solid #e5e7eb;box-shadow:0 10px 28px rgba(16,24,40,.10);flex-direction:column;align-items:stretch;gap:0;padding:8px 20px 18px;z-index:60}
  #navtoggle:checked ~ .nav-right{display:flex}
  nav.main{flex-direction:column;align-items:stretch;width:100%}
  nav.main a{margin-left:0;font-size:15px;padding:13px 0;border-bottom:1px solid var(--line-soft)}
  nav.main a:hover{border-bottom-color:var(--line-soft)}
  .lang{margin:14px 0 0;align-self:flex-start}
  .nav-cta{margin:14px 0 0;text-align:center}
}
@media(max-width:560px){footer.site .fcols{grid-template-columns:1fr}}
"""

def hreflang_tags(canonical):
    """<link rel=alternate hreflang> for every language + x-default.
    English is served at root; other languages live under /<lang>/. With one
    language today this self-references, and extends cleanly as langs are added."""
    path = canonical[len(SITE):] if canonical.startswith(SITE) else canonical
    tags = []
    for lg in LANGS:
        tags.append('<link rel="alternate" hreflang="%s" href="%s">' % (HREFLANG[lg], SITE + LANG_PREFIX[lg] + path))
    tags.append('<link rel="alternate" hreflang="x-default" href="%s">' % (SITE + LANG_PREFIX[DEFAULT_LANG] + path))
    return "".join(tags)

def page(title, desc, canonical, body, schema=None, crumb=None):
    schema_js = ""
    if schema:
        schema_js = '<script type="application/ld+json">%s</script>' % json.dumps(schema, ensure_ascii=False)
    nav = ('<a href="/industries/">Industries</a><a href="/applications/">Applications</a>'
           '<a href="/materials/">Materials</a><a href="/brands/">Brands</a>'
           '<a href="/about/">About</a><a href="/contact/">Contact</a>')
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
<link rel="canonical" href="%s">%s
<meta property="og:title" content="%s"><meta property="og:type" content="website"><meta property="og:site_name" content="ETIA Label">
<style>%s</style>%s</head><body>
<header class="site"><div class="wrap"><a class="logo" href="/"><span class="mark">E</span>ETIA&nbsp;<span>Label</span></a>
<input type="checkbox" id="navtoggle" class="navtoggle"><label class="hamb" for="navtoggle" aria-label="Open menu"><span></span><span></span><span></span></label>
<div class="nav-right"><nav class="main">%s</nav><span class="lang" title="More languages coming soon">&#127760; EN</span><a class="nav-cta" href="/contact/">Talk to an Engineer</a></div></div></header>
%s
%s
<footer class="site"><div class="wrap"><div class="fcols">
<div class="fcol"><a class="flogo" href="/"><span class="mark">E</span>ETIA&nbsp;<span>Label</span></a>
<p class="ftag">Your Solution Partner for labels that perform where ordinary ones fail. Sole agent for Polyonics (USA) &amp; YS&nbsp;Tech (Japan), with our own die-cutting &amp; slitting factory. Engineering Success.</p></div>
<div class="fcol"><h4>Explore</h4><a href="/industries/">Industries</a><a href="/applications/">Applications</a><a href="/materials/">Materials</a><a href="/products/">Product Index</a></div>
<div class="fcol"><h4>Company</h4><a href="/brands/">Brands &amp; Cross-Reference</a><a href="/technical-resources/">Technical Resources</a><a href="/about/">About</a><a href="/contact/">Contact</a></div>
<div class="fcol"><h4>Contact</h4><a class="fmail" href="mailto:label@etia-tech.com">label@etia-tech.com</a><a href="/contact/">Global offices — CN · HK · TH · VN</a></div>
</div><div class="fbar"><span>© ETIA Label — Your Solution Partner. Engineering Success.</span><span><a href="/about/">About</a> · <a href="/contact/">Contact</a> · <a href="/brands/">Brady Cross-Reference</a></span></div></div></footer></body></html>""" % (esc(title), esc(desc), canonical, hreflang_tags(canonical), esc(title), CSS, schema_js, nav, cr, body)

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
    return """<div class="cta"><h3>Tell us the application — we'll engineer the label.</h3>
<p>Send your temperature range, surface, chemical exposure and print method. We'll return the matched Polyonics, YS&nbsp;Tech or ETIA part with a datasheet and free qualification samples — often within one working day.</p>
<div class="btns"><a class="btn" href="/contact/">Request Samples &amp; Datasheet</a>
<a class="btn ghost" href="/brands/">Find a Brady Equivalent</a></div></div>"""

# Reusable "authorized brands" agency matrix (used on Brands + About pages).
BRANDS_MATRIX = """<div class="sec"><h2>Authorized brands we represent</h2>
<p class="lede">Genuine, brand-authorized materials — never grey-market substitutes. This is the core of a reliable label: the right engineered stock, sourced direct from the manufacturer.</p>
<div class="grid">
<div class="card"><h4><span class="bchip poly">Polyonics</span> &nbsp;USA</h4><p>Ultra-thin polyimide and PET for PCB reflow, ESD, flame-retardant and laser-marking electronics labels. <b>Sole agent — 20 years.</b></p></div>
<div class="card"><h4><span class="bchip ys">YS&nbsp;Tech</span> &nbsp;Japan</h4><p>Metal, aluminum-foil and inorganic ceramic tags for 300–1300&nbsp;°C metallurgy, heat-treatment and kilns. <b>Sole agent, Asia-Pacific.</b></p></div>
<div class="card"><h4><span class="bchip flexcon">FlexCon</span> &nbsp;USA</h4><p>Pressure-sensitive films, adhesives and specialty face-stocks — the material base for demanding converted labels.</p></div>
<div class="card"><h4><span class="bchip computype">Computype</span> &nbsp;USA</h4><p>Barcode, traceability and identification systems for regulated, high-mix production environments.</p></div>
<div class="card"><h4><span class="bchip etia">ETIA</span> &nbsp;Own brand</h4><p>Full-range PET, PP and specialty converter stock — cryogenic, medical, cable and outdoor — cut in our own die-cutting &amp; slitting factory.</p></div>
</div></div>"""

# Reusable trust triangle (used on Home + About).
TRUST_TRIANGLE = """<div class="sec"><h2>Why buyers choose ETIA</h2>
<div class="trust">
<div class="t"><b>20 years, two sole agencies</b><p>Sole agent for Polyonics (USA) and YS&nbsp;Tech (Japan) across the region — genuine, brand-authorized material, never grey-market.</p></div>
<div class="t"><b>Our own factory</b><p>In-house die-cutting and slitting plus local stock means faster delivery to printers, converters and end users alike.</p></div>
<div class="t"><b>Application-first partnership</b><p>We start from your environment — surface, heat, chemistry, print method, lifecycle — then engineer the label, and stay with you from sample to production.</p></div>
</div></div>"""

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
            desc = mat_en(p["mat"]); temp = fmt_temp(p["t"]); th = p["th"]; brady = p.get("brady","")
        else:
            desc = "—"; temp = "—"; th = "—"; brady = ""
        bradyc = ('<a href="/brands/brady-cross-reference/">%s</a>' % esc(brady)) if brady else '—'
        rows.append('<tr><td class="mono"><a href="/products/%s/">%s</a></td>'
                    '<td><span class="bchip %s">%s</span></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
                    % (slug, esc(clean_model(key)), bc, b, esc(desc), esc(temp), esc(th), bradyc))
    if not rows:
        return None
    body = ('<div class="tablewrap"><table class="matrix"><thead><tr><th>Model</th><th>Brand</th><th>Material</th>'
            '<th>Temp Range</th><th>Thickness</th><th>Brady Cross-Ref</th></tr></thead><tbody>%s</tbody></table></div>'
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
    mdisp = clean_model(key)   # display name, Chinese annotations stripped
    url = "/products/%s/" % slug
    if p:
        desc = mat_en(p["mat"]); temp = fmt_temp(p["t"]); th = p["th"]
        brady = p.get("brady",""); ind = IND_MAP.get(p["ind_s"])
    else:
        desc="—";temp="—";th="—";brady="";ind=None
    en_desc = product_desc_en(p, b)
    # native-English "common uses" sentence from industry + application
    if p:
        _app = app_en_short(p.get("app_s",""))
        _ind = ind[1] if ind else None
        if _ind and _app:
            en_uses = "Specified in %s for %s, where labels must stay bonded and scannable across %s." % (_ind, _app, temp)
        elif _app:
            en_uses = "Engineered for %s, holding print and adhesion across %s." % (_app, temp)
        else:
            en_uses = "High-performance identification for demanding industrial environments, rated %s." % temp
    else:
        en_uses = "High-performance identification for demanding industrial environments."
    title = "%s — %s %s Label | ETIA Label" % (mdisp, b, desc if desc!="—" else "Industrial")
    metad = "%s %s industrial label. Material %s, temperature %s, thickness %s.%s Datasheet, samples and Brady cross-reference from ETIA Label." % (
        b, mdisp, desc, temp, th, (" Brady equivalent "+brady+"." if brady else ""))
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
        ("What is the maximum temperature of %s?" % mdisp,
         "%s is rated for %s. For continuous exposure stay within the upper limit; brief peaks (e.g. reflow) can exceed it — contact us for the peak profile." % (mdisp, temp)),
        ("Is there a Brady equivalent for %s?" % mdisp,
         ("Yes. %s cross-references to Brady %s. ETIA supplies the equivalent with free samples for qualification." % (mdisp, brady)) if brady
         else "Send us your current Brady part number and we'll identify the closest ETIA / Polyonics / YS Tech equivalent."),
        ("Can I get samples of %s?" % mdisp,
         "Yes — we ship free qualification samples and the full datasheet. Use the request form and include your substrate and print method."),
    ]
    body = '<section class="hero"><div class="wrap"><h1>%s</h1><p>%s</p></div></section>' % (esc(mdisp), esc(en_desc))
    body += ('<div class="wrap sec"><div style="display:grid;grid-template-columns:1fr 1fr;gap:30px">'
             '<div><h2>Specifications</h2>%s%s</div>'
             '<div><h2>Common uses</h2><p style="color:var(--mut)">%s</p>%s</div></div>' % (
             specs, xl, esc(en_uses), ""))
    body += '<h2 style="margin-top:30px">FAQ</h2>' + faq_html(faqs) + cta() + '</div>'
    crumb = [("Home","/"),("Products","/products/"),(mdisp,url)]
    sch = [breadcrumb_schema(crumb), faq_schema(faqs),
           {"@context":"https://schema.org","@type":"Product","name":mdisp,"brand":{"@type":"Brand","name":b},
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
<span class="eyebrow">Industrial Specialty Labels · 20 Years</span>
<h1>Your solution partner for labels that perform where ordinary ones fail.</h1>
<p>For over 20 years we've engineered durable and specialty labels for the toughest conditions — extreme heat to 1300&nbsp;°C, cryogenic cold to −196&nbsp;°C, harsh chemicals, oily surfaces and lead-free PCB assembly. We start from your application, not a catalog.</p>
<div class="btns"><a class="btn" href="/contact/">Request Samples &amp; Datasheet</a>
<a class="btn ghost" href="/industries/">Browse by Industry</a></div></div></section>
<section class="tstrip"><div class="wrap">
<span class="ti"><span class="dot"></span>Sole agent — Polyonics (USA)</span>
<span class="ti"><span class="dot"></span>Sole agent — YS&nbsp;Tech (Japan)</span>
<span class="ti"><span class="dot"></span>In-house die-cutting &amp; slitting</span>
<span class="ti"><span class="dot"></span>1300&nbsp;°C to −196&nbsp;°C envelope</span>
<span class="ti"><span class="dot"></span>Free qualification samples</span>
</div></section>
<div class="wrap"><div class="paths">
<div class="pcard"><div class="tag">Path 1</div><h3><a href="/industries/">By Industry</a></h3>
<p style="color:var(--mut);font-size:14px">Start from your sector — electronics, automotive, medical, steel and more.</p>
<ul><li>Electronics &amp; Semiconductor</li><li>Automotive · EV &amp; Battery</li><li>Medical &amp; Biotech</li><li>Steel · Ceramic · Cable</li></ul></div>
<div class="pcard"><div class="tag">Path 2</div><h3><a href="/applications/">By Application</a></h3>
<p style="color:var(--mut);font-size:14px">Start from your process — the heat, chemistry or environment the label must survive.</p>
<ul><li>SMT Reflow &amp; Wave Soldering</li><li>Cryogenic LN2 · Sterilization</li><li>Heat-Treatment 300–1300&nbsp;°C</li><li>ESD · UL94 V-0 · Outdoor UV</li></ul></div>
<div class="pcard"><div class="tag">Path 3</div><h3><a href="/materials/">By Base Material</a></h3>
<p style="color:var(--mut);font-size:14px">Start from the substrate — polyimide, PET, PP, metal foil or specialty.</p>
<ul><li>Polyimide (PI) High-Temp</li><li>Polyester (PET)</li><li>Synthetic PP · Paper/Specialty</li><li>Metal &amp; Aluminum Foil</li></ul></div>
</div>
%s
<div class="sec"><h2>All industries</h2><div class="grid">%s</div></div>
%s</div>""" % (TRUST_TRIANGLE, ind_cards, cta())
    sch = {"@context":"https://schema.org","@type":"Organization","name":"ETIA Label","url":SITE,
           "slogan":"Your Solution Partner. Engineering Success.",
           "description":"ETIA is a solution partner for durable and specialty industrial labels engineered for extreme heat, cryogenic cold, chemicals and lead-free PCB assembly. Sole agent for Polyonics (USA) and YS Tech (Japan), with in-house die-cutting and slitting.",
           "brand":["Polyonics","YS Tech","FlexCon","Computype","ETIA"],
           "contactPoint":contact_points()}
    write("/", page("ETIA Label — Your Solution Partner for Industrial Specialty Labels",
        "Durable, high-performance industrial labels for extreme heat to 1300°C, cryogenic cold, chemicals and lead-free PCB assembly. Sole agent for Polyonics (USA) & YS Tech (Japan). Browse by industry, application or material — free samples.",
        SITE+"/", body, sch))
    track("/", "root")

def build_about():
    crumb=[("Home","/"),("About","/about/")]
    body="""<section class="hero"><div class="wrap">
<h1>Your solution partner for labels that perform where ordinary ones fail.</h1>
<p>For over 20 years, ETIA has been a trusted partner for the labeling challenges most suppliers avoid.</p>
</div></section>
<div class="wrap">
<div class="sec"><h2>High-complexity is our specialty</h2>
<p class="lede">While others chase high-volume, standardized runs, we specialize in high-complexity requirements — durable and specialty labels engineered for the toughest conditions. As your solution partner, we start from your application, not a product catalog.</p>
<p style="color:var(--mut);max-width:760px">We study the full environment — surface, temperature, chemical exposure, printing method, barcode requirement and product lifecycle — then engineer labels that stay bonded, readable and reliable where ordinary labels fail: through extreme heat up to <b>1300&nbsp;°C</b>, cryogenic cold down to <b>−196&nbsp;°C</b>, harsh chemicals, oily surfaces and modern lead-free PCB assembly.</p></div>
%s
%s
<div class="sec"><h2>The details behind every solution</h2>
<p style="color:var(--mut);max-width:760px">We supply genuine, brand-authorized materials — never grey-market substitutes. With full in-house slitting and die-cutting capability plus local stock, we deliver faster to printers, converters and end users alike. From material selection and sample testing to ongoing technical support, we stay with you for the long term to keep your identification reliable throughout production.</p>
<p style="max-width:760px;font-size:17px;color:var(--blue-deep);font-weight:700;margin-top:14px">We don't just supply labels. We partner with you to solve identification problems where failure is not an option.</p>
<p style="color:var(--mut);margin-top:8px">ETIA — Your Solution Partner. Engineering Success.</p></div>
%s</div>""" % (TRUST_TRIANGLE, BRANDS_MATRIX, cta())
    sch={"@context":"https://schema.org","@type":"AboutPage","name":"About ETIA Label",
         "description":"ETIA is a solution partner for durable and specialty industrial labels, with 20 years' experience, sole agencies for Polyonics and YS Tech, and in-house die-cutting and slitting."}
    write("/about/", page("About ETIA — Your Solution Partner | ETIA Label",
        "For over 20 years ETIA has engineered durable, specialty labels for the toughest conditions. Sole agent for Polyonics (USA) & YS Tech (Japan), with in-house die-cutting, slitting and long-term technical partnership.",
        SITE+"/about/", body, [breadcrumb_schema(crumb), sch], crumb))
    track("/about/","tech-resources")

# Regional sales/technical offices (English addresses only — the site is English).
OFFICES = [
 {"loc":"China · Shanghai","name":"Mark Tang","role":"",
  "addr":"Rm. 1903, 2# Building, Guoson Centre, No. 388 Zhongjiang Rd, Putuo District, Shanghai, China",
  "phones":[("400 990 8448","tel:4009908448"),("+86-21-6432-7144 ext. 106","tel:+862164327144")],
  "email":"label@etia-tech.com","cc":"CN"},
 {"loc":"Hong Kong","name":"Mark Tang","role":"",
  "addr":"Room 1003, 10/F, Tower 1, Lippo Centre, 89 Queensway, Admiralty, Hong Kong",
  "phones":[("+86 151 2119 7091","tel:+8615121197091")],
  "email":"label@etia-tech.com","cc":"HK"},
 {"loc":"Thailand · Bangkok","name":"Mr. Sompoch Ratchakom (Job)","role":"Sales Director",
  "addr":"22/41 H-Cape Biz Center, Sukhaphiban 2 Road, Prawet Subdistrict, Prawet District, Bangkok 10250, Thailand",
  "phones":[("+66 811 746 947","tel:+66811746947")],
  "email":"label@etia-tech.com","cc":"TH"},
 {"loc":"Vietnam · Bac Ninh","name":"Tien Nguyen","role":"Technical Engineer",
  "addr":"No. 10 Thanh Nien Street, Area 5, Vo Cuong Ward, Bac Ninh Province, Viet Nam",
  "phones":[("+84 344 590 091","tel:+84344590091")],
  "email":"label@etia-tech.com","cc":"VN"},
]

def office_cards():
    out = []
    for o in OFFICES:
        role = esc(o["name"]) + ((" · <span>%s</span>" % esc(o["role"])) if o["role"] else "")
        phones = "".join('<li><span class="ic">☎</span><a href="%s">%s</a></li>' % (u, esc(p)) for p,u in o["phones"])
        out.append('<div class="office"><h3>%s</h3><div class="role">%s</div>'
                   '<p class="addr">%s</p><ul class="crows">'
                   '<li><span class="ic">✉</span><a href="mailto:%s">%s</a></li>%s</ul></div>'
                   % (esc(o["loc"]), role, esc(o["addr"]), o["email"], esc(o["email"]), phones))
    return '<div class="offices">%s</div>' % "".join(out)

def contact_points():
    return [{"@type":"ContactPoint","contactType":"sales","areaServed":o["cc"],
             "telephone":o["phones"][0][0],"email":o["email"]} for o in OFFICES]

def build_contact():
    crumb=[("Home","/"),("Contact","/contact/")]
    body="""<section class="hero"><div class="wrap">
<h1>Talk to your local ETIA team.</h1>
<p>Tell us your application — surface, temperature, chemical exposure and print method — and we'll return the matched part with a datasheet and free qualification samples, often within one working day.</p>
</div></section>
<div class="wrap">
<div class="sec"><h2>Global contacts</h2>
<p class="lede">Local sales and technical support across Greater China and Southeast Asia.</p>
%s</div>
<div class="cta"><h3>Prefer to send your spec now?</h3>
<p>Email your temperature range, substrate and a competitor part number if you have one — we'll match it and ship samples.</p>
<div class="btns"><a class="btn" href="mailto:label@etia-tech.com">Email ETIA</a>
<a class="btn ghost" href="/brands/">Find a Brady Equivalent</a></div></div>
</div>""" % office_cards()
    sch=[breadcrumb_schema(crumb),
         {"@context":"https://schema.org","@type":"ContactPage","name":"Contact ETIA Label",
          "description":"Local ETIA sales and technical offices in Shanghai, Hong Kong, Bangkok and Bac Ninh.",
          "mainEntity":{"@type":"Organization","name":"ETIA Label","url":SITE,"contactPoint":contact_points()}}]
    write("/contact/", page("Contact ETIA — Global Offices (China, HK, Thailand, Vietnam) | ETIA Label",
        "Contact your local ETIA team in Shanghai, Hong Kong, Bangkok or Bac Ninh for industrial specialty labels, spec matching and free samples.",
        SITE+"/contact/", body, sch, crumb))
    track("/contact/","tech-resources")

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
        temp=fmt_temp(p["t"]) if p else "—"
        desc=mat_en(p["mat"]) if p else "—"
        rows.append('<tr><td class="mono"><a href="/products/%s/">%s</a></td><td><span class="bchip %s">%s</span></td><td>%s</td><td>%s</td></tr>'%(prod_slug(m),esc(clean_model(m)),bc,b,esc(desc),esc(temp)))
    crumb=[("Home","/"),("Products","/products/")]
    body='<section class="hero"><div class="wrap"><h1>Product Index</h1><p>All %d parts in the ETIA catalog — Polyonics (USA), YS Tech (Japan) and ETIA own-brand stock. Every part ships with a datasheet and free qualification samples.</p></div></section><div class="wrap"><div class="sec"><div class="tablewrap"><table class="matrix"><thead><tr><th>Model</th><th>Brand</th><th>Material</th><th>Temp</th></tr></thead><tbody>%s</tbody></table></div></div>%s</div>'%(len(allm),"".join(rows),cta())
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
                        %(esc(p["brady"]),prod_slug(m),esc(clean_model(m)),bc,b,esc(mat_en(p["mat"]))))
    body='<section class="hero"><div class="wrap"><h1>Brand Cross-Reference</h1><p>Searching a Brady part number? Find the equivalent Polyonics, YS Tech or ETIA label — matched on material and temperature, with free qualification samples.</p></div></section><div class="wrap">'
    body+=BRANDS_MATRIX
    body+='<div class="sec"><h2>Brady &rarr; ETIA equivalents</h2><p class="lede">%d cross-referenced parts. Send any part number not listed and we\'ll match it.</p><div class="tablewrap"><table class="matrix"><thead><tr><th>Brady Part</th><th>ETIA Equivalent</th><th>Brand</th><th>Material</th></tr></thead><tbody>%s</tbody></table></div></div>'%(len(rows),"".join(rows))
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
    for t,d in [("By temperature","Under 150 °C: PET/PP. 150–300 °C: polyimide. 300–600 °C: aluminum/nickel foil. Above 600 °C: inorganic ceramic (to 1300 °C)."),
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
for d in ["industries","applications","materials","products","brands","technical-resources","about","contact"]:
    p=os.path.join(ROOT,d)
    if os.path.isdir(p): shutil.rmtree(p)
for f in os.listdir(ROOT):
    if f.startswith("sitemap") or f=="robots.txt": os.remove(os.path.join(ROOT,f))

build_home()
build_about()
build_contact()
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
