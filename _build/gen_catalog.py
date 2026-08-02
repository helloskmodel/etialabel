#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Find a Label Material — a client-side product catalog with search + facets.

Reads every data/products/*.json, derives facets (Industry, Brand, Facestock,
Application, Temperature) from the real content, and renders /products/find/ in
all four languages. Search matches part numbers, materials and application
keywords across all languages (the index is a lowercased text blob per product).

Facets shown are the ones reliably derivable today. A product may also carry an
explicit "facets" object to override/extend derived values (e.g. adhesive,
printing, compliance, surface) — those render automatically when present.
"""
import json, os, re, html
import gen_heatproof as hp
import gen_product as gp

BUILD = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.join(BUILD, "data", "products")
PATH = "/products/find/"
esc = hp.esc
LANGS = ["en", "zh", "vi", "th"]

# ---- Generated product image: a 4:3 Code 39 barcode-label tile (barcode on top,
# model code below). Defined in gen_product so both modules share one generator;
# aliased here for the finder/brand cards. ----
_CODE39 = gp._CODE39
_model_code = gp._model_code
barcode_label_svg = gp.barcode_label_svg

# Entries excluded from the finder + brand grid because they are NOT a single
# product: the environment Solution hubs, and the series-overview pages (APEX,
# XF-58, XF-78, E-series) whose individual models are already listed on their own.
# Their pages still exist and are reached from the "Products › By Industry" pages.
EXCLUDE = set(gp.SOLUTION_SLUGS) | {"apex", "xf58", "xf78", "e-series"}

IND_NAME = {
    "pcb":     {"en": "PCB & Electronics", "zh": "PCB 电子", "vi": "PCB & Điện tử", "th": "PCB และอิเล็กทรอนิกส์"},
    "auto":    {"en": "Automotive", "zh": "汽车", "vi": "Ô tô", "th": "ยานยนต์"},
    "cable":   {"en": "Wire & Cable", "zh": "线缆", "vi": "Cáp & Dây", "th": "สายเคเบิล"},
    "steel":   {"en": "Steel & Metal", "zh": "钢铁金属", "vi": "Thép & Kim loại", "th": "เหล็กและโลหะ"},
    "medical": {"en": "Medical & Pharma", "zh": "医疗医药", "vi": "Y tế & Dược", "th": "การแพทย์และยา"},
    "outdoor": {"en": "Outdoor & Energy", "zh": "户外能源", "vi": "Ngoài trời & Năng lượng", "th": "กลางแจ้งและพลังงาน"},
}

# Application categories: label (4-lang) + keyword triggers (searched in the blob).
APP_CATS = [
    ("esd",     {"en": "ESD / Anti-static", "zh": "防静电", "vi": "Chống tĩnh điện", "th": "ป้องกันไฟฟ้าสถิต"}, ["esd", "anti-static", "static-dissipative", "防静电", "静电"]),
    ("washreflow", {"en": "Wash & Reflow PI", "zh": "耐焊洗 PI", "vi": "Chịu rửa & reflow (PI)", "th": "ทนล้าง & รีโฟลว์ (PI)"}, ["reflow", "wave-solder", "wave solder", "wave soldering", "solder flux", "回流焊", "波峰焊", "焊洗", "过炉"]),
    ("flame",   {"en": "Flame-Retardant", "zh": "阻燃", "vi": "Chống cháy", "th": "หน่วงไฟ"}, ["flame-retardant", "flame retardant", "ul94", "ul 94", "vtm-0", "halogen-free", "阻燃", "无卤"]),
    ("chem",    {"en": "Chemical-Resistant", "zh": "耐化学", "vi": "Kháng hóa chất", "th": "ทนสารเคมี"}, ["chemical-resistant", "chemical resistant", "solvent-resistant", "solvent resistant", "acid and alkali", "耐化学", "耐溶剂"]),
    ("steril",  {"en": "Sterilization", "zh": "灭菌", "vi": "Tiệt trùng", "th": "การฆ่าเชื้อ"}, ["sterilization", "sterilize", "autoclave", "gamma", "灭菌", "高压灭菌"]),
    ("laser",   {"en": "Laser-Markable", "zh": "激光可刻", "vi": "Khắc laser", "th": "แกะสลักด้วยเลเซอร์"}, ["laser-mark", "laser mark", "laser-etch", "laser etch", "laser engrav", "激光刻", "激光打"]),
    ("blood",   {"en": "Blood Bag", "zh": "血袋", "vi": "Túi máu", "th": "ถุงเลือด"}, ["blood bag", "blood-bag", "血袋"]),
    ("vin",     {"en": "Automotive VIN", "zh": "汽车 VIN", "vi": "VIN ô tô", "th": "VIN ยานยนต์"}, ["vin code", "vin label", "vin plate", "vin identif", "车架号", "汽车 vin"]),
    ("cablew",  {"en": "Wire & Cable ID", "zh": "线缆标识", "vi": "Nhận diện cáp", "th": "ระบุสายเคเบิล"}, ["wire", "cable", "harness", "线缆", "束线", "电缆"]),
    ("outdoor", {"en": "Solar & Battery Outdoor Warning", "zh": "光伏/新能源电池户外警示", "vi": "Cảnh báo ngoài trời điện mặt trời & pin", "th": "คำเตือนกลางแจ้งโซลาร์และแบตเตอรี่"}, ["outdoor", "weatherable", "weather resist", "solar", "photovoltaic", "pv module", "new energy", "户外", "耐候", "光伏", "太阳能", "储能", "新能源"]),
]

# Facestock keyword triggers (search title + positioning + spec).
FACESTOCKS = [
    ({"en": "Polyimide (PI)", "zh": "聚酰亚胺 PI", "vi": "Polyimide (PI)", "th": "โพลีอิไมด์ (PI)"}, ["polyimide", "pi film", "聚酰亚胺"]),
    ({"en": "PET", "zh": "PET", "vi": "PET", "th": "PET"}, ["pet ", " pet", "polyester", "聚酯"]),
    ({"en": "PP", "zh": "PP", "vi": "PP", "th": "PP"}, ["polypropylene", " pp ", "pp label", "pp 标签", "聚丙烯"]),
    ({"en": "PE", "zh": "PE", "vi": "PE", "th": "PE"}, ["polyethylene", " pe ", "pe 材料", "聚乙烯"]),
    ({"en": "Vinyl", "zh": "乙烯基", "vi": "Vinyl", "th": "ไวนิล"}, ["vinyl", "乙烯基"]),
    ({"en": "Nylon cloth", "zh": "尼龙布", "vi": "Vải nylon", "th": "ผ้าไนลอน"}, ["nylon", "尼龙布"]),
    ({"en": "Synthetic paper", "zh": "合成纸", "vi": "Giấy tổng hợp", "th": "กระดาษสังเคราะห์"}, ["synthetic paper", "合成纸"]),
    ({"en": "Ceramic", "zh": "陶瓷", "vi": "Gốm", "th": "เซรามิก"}, ["ceramic", "陶瓷"]),
]

UI = {
    "en": {"title": "Find a Label Material", "lede": "Search by part number, material or application — or filter by the facets below.",
           "search": "Search part number, material or application… (e.g. E-4812, polyimide, blood bag)",
           "reset": "Clear all", "results": "materials", "none": "No materials match your filters.",
           "view": "View product →", "filters": "Filters", "home": "Home", "products": "Products",
           "fac": {"industry": "Industry", "brand": "Brand", "application": "Application", "facestock": "Facestock", "thick": "Thickness", "temp": "Temperature"}},
    "zh": {"title": "查找标签материал".replace("материал", "材料"), "lede": "按料号、材料或应用搜索 —— 或使用下方维度筛选。",
           "search": "搜索料号、材料或应用……（如 E-4812、聚酰亚胺、血袋）",
           "reset": "清除全部", "results": "款材料", "none": "没有符合条件的材料。",
           "view": "查看产品 →", "filters": "筛选", "home": "首页", "products": "产品",
           "fac": {"industry": "行业", "brand": "品牌", "application": "应用", "facestock": "面材", "thick": "厚度", "temp": "温度"}},
    "vi": {"title": "Tìm vật liệu nhãn", "lede": "Tìm theo mã sản phẩm, vật liệu hoặc ứng dụng — hoặc lọc theo các tiêu chí bên dưới.",
           "search": "Tìm mã, vật liệu hoặc ứng dụng… (vd: E-4812, polyimide, túi máu)",
           "reset": "Xóa tất cả", "results": "vật liệu", "none": "Không có vật liệu phù hợp.",
           "view": "Xem sản phẩm →", "filters": "Bộ lọc", "home": "Trang chủ", "products": "Sản phẩm",
           "fac": {"industry": "Ngành", "brand": "Thương hiệu", "application": "Ứng dụng", "facestock": "Vật liệu mặt", "thick": "Độ dày", "temp": "Nhiệt độ"}},
    "th": {"title": "ค้นหาวัสดุฉลาก", "lede": "ค้นหาด้วยรหัสสินค้า วัสดุ หรือการใช้งาน — หรือกรองตามหมวดด้านล่าง",
           "search": "ค้นหารหัส วัสดุ หรือการใช้งาน… (เช่น E-4812, โพลีอิไมด์, ถุงเลือด)",
           "reset": "ล้างทั้งหมด", "results": "วัสดุ", "none": "ไม่มีวัสดุที่ตรงกับตัวกรอง",
           "view": "ดูสินค้า →", "filters": "ตัวกรอง", "home": "หน้าแรก", "products": "ผลิตภัณฑ์",
           "fac": {"industry": "อุตสาหกรรม", "brand": "แบรนด์", "application": "การใช้งาน", "facestock": "วัสดุหน้า", "thick": "ความหนา", "temp": "อุณหภูมิ"}},
}
TEMP_BANDS = {
    "xhot":  {"en": "Extreme (≥ 500°C)", "zh": "极高温 (≥ 500°C)", "vi": "Cực cao (≥ 500°C)", "th": "สูงมาก (≥ 500°C)"},
    "vhot":  {"en": "Very High (300–500°C)", "zh": "超高温 (300–500°C)", "vi": "Rất cao (300–500°C)", "th": "สูงพิเศษ (300–500°C)"},
    "hot":   {"en": "High-Temp (150–300°C)", "zh": "高温 (150–300°C)", "vi": "Cao (150–300°C)", "th": "สูง (150–300°C)"},
    "std":   {"en": "Standard (≤ 150°C)", "zh": "常规 (≤ 150°C)", "vi": "Tiêu chuẩn (≤ 150°C)", "th": "มาตรฐาน (≤ 150°C)"},
    "cryo":  {"en": "Low / Cryogenic (≤ −40°C)", "zh": "低温 / 冻存 (≤ −40°C)", "vi": "Thấp / Đông lạnh (≤ −40°C)", "th": "ต่ำ / แช่แข็ง (≤ −40°C)"},
}
THICK_BANDS = {
    "t1": {"en": "1 mil (25 µm)", "zh": "1 mil (25 µm)", "vi": "1 mil (25 µm)", "th": "1 mil (25 µm)"},
    "t2": {"en": "2 mil (50 µm)", "zh": "2 mil (50 µm)", "vi": "2 mil (50 µm)", "th": "2 mil (50 µm)"},
    "t3": {"en": "3–4 mil", "zh": "3–4 mil", "vi": "3–4 mil", "th": "3–4 mil"},
    "t5": {"en": "5 mil +", "zh": "5 mil +", "vi": "5 mil +", "th": "5 mil +"},
}
BRAND = gp.BRAND_NAMES  # {"polyonics":{...}, "etia":{...}} — shared brand axis


def _blob(d):
    parts = []
    def walk(o):
        if isinstance(o, str): parts.append(o)
        elif isinstance(o, list): [walk(x) for x in o]
        elif isinstance(o, dict): [walk(v) for v in o.values()]
    for k in ("title", "tagline", "positioning", "features", "applications", "spec_table", "certifications"):
        walk(d.get(k, ""))
    parts.append(d.get("slug", ""))
    return " ".join(parts).lower()


def _temps(blob):
    """Return (min, max) °C found in the text, or (None, None). A leading ASCII/
    Unicode minus means negative; an en-dash (range separator, e.g. 700–750℃) or a
    minus sitting between two digits does NOT — so ranges aren't misread as negative."""
    vals = []
    for m in re.finditer(r"(\d{2,4})\s?(?:°\s?c|℃)", blob):
        j = m.start() - 1
        if j >= 0 and blob[j] == " ":
            j -= 1
        neg = j >= 0 and blob[j] in "-−" and (j == 0 or not blob[j - 1].isdigit())
        n = int(m.group(1))
        vals.append(-n if neg else n)
    if not vals:
        return None, None
    return min(vals), max(vals)


# Coloured facestocks — detected from the product title, shown as a small dot chip
# on the product card. (White/black are the defaults and are not chipped.)
COLOR_WORDS = [
    ("blue",   {"en": "Blue", "zh": "蓝色", "vi": "Xanh dương", "th": "น้ำเงิน"}, "#1e5fd8"),
    ("green",  {"en": "Green", "zh": "绿色", "vi": "Xanh lá", "th": "เขียว"}, "#2e9e3f"),
    ("yellow", {"en": "Yellow", "zh": "黄色", "vi": "Vàng", "th": "เหลือง"}, "#e0a800"),
    ("red",    {"en": "Red", "zh": "红色", "vi": "Đỏ", "th": "แดง"}, "#d23b3b"),
    ("orange", {"en": "Orange", "zh": "橙色", "vi": "Cam", "th": "ส้ม"}, "#e8720c"),
    ("amber",  {"en": "Amber", "zh": "琥珀色", "vi": "Hổ phách", "th": "อำพัน"}, "#cf8a00"),
    ("silver", {"en": "Silver", "zh": "银色", "vi": "Bạc", "th": "เงิน"}, "#8a94a6"),
]


def build_record(d):
    slug = d["slug"]
    blob = _blob(d)
    ind = gp.product_industry(d, slug)
    brand = gp.product_brand(d, slug)  # 'polyonics' | 'etia'
    apps = [key for key, lab, kws in APP_CATS if any(k in blob for k in kws)]
    facestocks = [fs for fs, kws in FACESTOCKS if any(k in blob for k in kws)]
    tmin, tmax = _temps(blob)
    temps = []
    if tmax is not None:
        if tmax >= 500:   temps.append("xhot")   # hot steel / billet
        elif tmax >= 300: temps.append("vhot")   # reflow-class PI (up to 300 °C)
        elif tmax >= 150: temps.append("hot")    # general high-heat
        else:             temps.append("std")
    if tmin is not None and tmin <= -40: temps.append("cryo")  # low-temp / cryogenic
    if not temps: temps.append("std")
    # thickness band from the film (headline) thickness — title first, then blob
    ttitle = (d.get("title", {}) or {}).get("en", "")
    mm = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*mil', ttitle) or re.search(r'([0-9]+(?:\.[0-9]+)?)\s*mil', blob)
    thick = []
    if mm:
        v = float(mm.group(1))
        if v <= 1.4:   thick.append("t1")
        elif v <= 2.4: thick.append("t2")
        elif v <= 4.9: thick.append("t3")
        else:          thick.append("t5")
    # colour of a coloured facestock (mark the "colourful PI" products on the card)
    color = None
    tlow = ttitle.lower()
    for kw, lab, dot in COLOR_WORDS:
        if re.search(r'\b%s\b' % kw, tlow):
            color = {"lab": lab, "dot": dot}; break
    explicit = d.get("facets", {}) or {}
    return {
        "slug": slug, "url": "/products/item/%s/" % slug,
        "title": d.get("title", {}), "tagline": d.get("tagline", {}),
        "industry": ind, "brand": brand, "apps": apps, "facestocks": facestocks,
        "temps": temps, "thick": thick, "color": color,
        "product_img": d.get("product_img", ""),
        "blob": blob, "explicit": explicit,
    }


def build_lang(records, lang):
    ui = UI[lang]

    def L(node):
        if isinstance(node, dict):
            return node.get(lang) or node.get("en") or node.get("zh") or ""
        return node or ""

    # ---- facet option sets (only values that actually occur) ----
    def collect(getter, table):
        seen = []
        for r in records:
            for v in getter(r):
                if v not in seen:
                    seen.append(v)
        return seen

    ind_opts = collect(lambda r: [r["industry"]] if r["industry"] else [], IND_NAME)
    brand_opts = sorted({r["brand"] for r in records}, reverse=True)
    app_opts = collect(lambda r: r["apps"], None)
    fs_opts = collect(lambda r: [json.dumps(f, ensure_ascii=False) for f in r["facestocks"]], None)
    thick_opts = collect(lambda r: r["thick"], None)
    temp_opts = collect(lambda r: r["temps"], None)

    def chk(group, value, label):
        return ('<label class="fchk"><input type="checkbox" data-g="%s" data-v="%s" onchange="cpick(this)"> %s</label>'
                % (group, esc(value), esc(label)))

    fpanels = ""
    # Order: Brand first, then the spec spine (Temperature, Material, Application),
    # and Thickness last.
    if len(brand_opts) > 1:
        fpanels += '<div class="fgrp"><h4>%s</h4>%s</div>' % (esc(ui["fac"]["brand"]),
            "".join(chk("brand", b, L(BRAND[b])) for b in brand_opts))
    if temp_opts:
        fpanels += '<div class="fgrp"><h4>%s</h4>%s</div>' % (esc(ui["fac"]["temp"]),
            "".join(chk("temp", t, L(TEMP_BANDS[t])) for t in ["xhot", "vhot", "hot", "std", "cryo"] if t in temp_opts))
    if fs_opts:
        fpanels += '<div class="fgrp"><h4>%s</h4>%s</div>' % (esc(ui["fac"]["facestock"]),
            "".join(chk("fs", f, L(json.loads(f))) for f in fs_opts))
    if app_opts:
        applab = {key: lab for key, lab, kws in APP_CATS}
        fpanels += '<div class="fgrp"><h4>%s</h4>%s</div>' % (esc(ui["fac"]["application"]),
            "".join(chk("app", key, L(applab[key])) for key, lab, kws in APP_CATS if key in app_opts))
    # Industry is intentionally NOT a filter here: a product serves several
    # industries, so industry-based discovery lives on the "Products › By Industry"
    # pages. This finder is the product/spec angle (temperature, material, application).
    if thick_opts:
        fpanels += '<div class="fgrp"><h4>%s</h4>%s</div>' % (esc(ui["fac"]["thick"]),
            "".join(chk("thick", t, L(THICK_BANDS[t])) for t in ["t1", "t2", "t3", "t5"] if t in thick_opts))

    # ---- cards ----
    applab = {key: lab for key, lab, kws in APP_CATS}
    cards = ""
    for r in sorted(records, key=lambda x: L(x["title"]).lower()):
        chips = ""
        for f in r["facestocks"][:1]:
            chips += '<span class="cchip mat">%s</span>' % esc(L(f))
        for t in r["temps"]:
            if t in ("xhot", "vhot", "hot"):
                chips += '<span class="cchip temphi">%s</span>' % esc(L(TEMP_BANDS[t]).split("(")[0].strip())
            elif t == "cryo":
                chips += '<span class="cchip templo">%s</span>' % esc(L(TEMP_BANDS[t]).split("(")[0].strip())
        if "esd" in r["apps"]:
            chips += '<span class="cchip esd">ESD</span>'
        if "flame" in r["apps"]:
            chips += '<span class="cchip fr">%s</span>' % esc(L(applab["flame"]))
        if r.get("color"):
            chips += '<span class="cchip clr"><i style="background:%s"></i>%s</span>' % (
                r["color"]["dot"], esc(L(r["color"]["lab"])))
        data = {
            "industry": [r["industry"]] if r["industry"] else [],
            "brand": [r["brand"]], "app": r["apps"],
            "fs": [json.dumps(f, ensure_ascii=False) for f in r["facestocks"]],
            "thick": r["thick"], "temp": r["temps"], "q": r["blob"],
        }
        cards += ('<a class="pcell" href="%s" data-f="%s"><div class="pcell-t">%s</div>'
                  '<div class="pcell-chips">%s</div>'
                  '<span class="pcell-go">%s</span></a>') % (
            hp.Lx(lang, r["url"]),
            esc(json.dumps(data, ensure_ascii=False)),
            esc(L(r["title"])), chips, esc(ui["view"]))

    CSS = """<style>
.cwrap{max-width:1180px;margin:0 auto;padding:26px 22px 48px}
.chead h1{font-size:32px;color:#143C96;font-family:var(--sans);font-weight:800;margin:0 0 6px}
.chead p{color:#51607e;font-size:15.5px;margin:0 0 18px;max-width:60ch}
.csearch{position:relative;margin:0 0 20px}
.csearch input{width:100%;box-sizing:border-box;font-size:16px;padding:14px 16px 14px 44px;border:1.5px solid #cdd8ec;border-radius:12px;background:#fff url('data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'20\\' height=\\'20\\' viewBox=\\'0 0 24 24\\' fill=\\'none\\' stroke=\\'%235a6884\\' stroke-width=\\'2\\'><circle cx=\\'11\\' cy=\\'11\\' r=\\'7\\'/><path d=\\'M21 21l-4-4\\'/></svg>') no-repeat 14px center}
.csearch input:focus{outline:none;border-color:#1A56DB;box-shadow:0 0 0 3px rgba(26,86,219,.14)}
.clayout{display:grid;grid-template-columns:236px 1fr;gap:26px;align-items:start}
.cfilters{position:sticky;top:86px;max-height:calc(100vh - 100px);overflow-y:auto;padding-right:6px}
.cfilters .fhd{display:flex;justify-content:space-between;align-items:center;margin:0 0 10px}
.cfilters .fhd h3{font-size:13px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:#143C96;margin:0}
.cfilters .freset{font-size:12.5px;font-weight:700;color:#1A56DB;background:none;border:none;cursor:pointer}
.fgrp{border-top:1px solid #e6ecf7;padding:12px 0}
.fgrp h4{font-size:13px;color:#17203a;margin:0 0 8px;font-weight:800}
.fchk{display:flex;align-items:center;gap:8px;font-size:13.5px;color:#41506e;padding:3px 0;cursor:pointer}
.fchk input{width:15px;height:15px;accent-color:#1A56DB}
.cresults{}
.ccount{font-size:13.5px;color:#5a6884;font-weight:700;margin:0 0 12px}
.pgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(232px,1fr));gap:16px}
.pcell{display:flex;flex-direction:column;gap:7px;background:#fff;border:1px solid #dbe3f1;border-radius:14px;padding:15px 16px 16px;text-decoration:none;color:#17203a;transition:box-shadow .15s,transform .15s,border-color .15s}
.pcell:hover{box-shadow:0 12px 30px rgba(20,60,150,.13);transform:translateY(-2px);border-color:#1A56DB}
.pcell-t{font-size:15.5px;font-weight:800;color:#143C96;line-height:1.28}
.pcell-s{font-size:12.5px;color:#5a6884;line-height:1.5;flex:1}
.pcell-chips{display:flex;flex-wrap:wrap;gap:5px}
.cchip{font-size:10.5px;font-weight:800;padding:2px 8px;border-radius:999px}
.cchip.ind{color:#fff;background:#1A56DB}.cchip.mat{color:#2c7a1e;background:#e6f5e0}
.cchip.esd{color:#1A56DB;background:#eaf1ff}.cchip.fr{color:#b4520a;background:#fdeede}
.cchip.temphi{color:#b4520a;background:#fdeede}.cchip.templo{color:#0e7490;background:#e0f2fe}
.cchip.clr{color:#3a4763;background:#f1f4fa;display:inline-flex;align-items:center}
.cchip.clr i{width:8px;height:8px;border-radius:50%;margin-right:5px;box-shadow:0 0 0 1px rgba(0,0,0,.18)}
.pcell-go{font-size:12px;font-weight:800;color:#41A62A;margin-top:2px}
.cnone{padding:40px 8px;color:#5a6884;font-size:15px}
.fmob{display:none}
@media(max-width:860px){.clayout{grid-template-columns:1fr}.cfilters{position:static}
  .fmob{display:block;width:100%;padding:11px 14px;border:1.5px solid #cdd8ec;border-radius:10px;background:#fff;font-weight:800;color:#143C96;cursor:pointer;margin-bottom:12px}
  .cfilters .fbody{display:none}.cfilters.open .fbody{display:block}}
</style>"""

    body = CSS + (
        '<div class="cwrap">'
        '<div class="csearch"><input id="cq" type="search" placeholder="%s" oninput="cf()" autocomplete="off"></div>'
        '<button class="fmob" onclick="this.nextElementSibling.classList.toggle(\'open\')">%s</button>'
        '<div class="clayout"><aside class="cfilters"><div class="fbody">'
        '<div class="fhd"><h3>%s</h3><button class="freset" onclick="cReset()">%s</button></div>%s</div></aside>'
        '<div class="cresults"><p class="ccount"><span id="ccount">0</span> %s</p>'
        '<div class="pgrid" id="pgrid">%s</div><p class="cnone" id="cnone" style="display:none">%s</p>'
        '</div></div></div>') % (
        esc(ui["search"]), esc(ui["filters"]),
        esc(ui["filters"]), esc(ui["reset"]), fpanels, esc(ui["results"]), cards, esc(ui["none"]))

    body += """<script>
function cpick(el){
  /* one choice per facet group: selecting a new option clears the others in that group */
  if(el.checked){
    document.querySelectorAll('.cfilters input[data-g="'+el.dataset.g+'"]').forEach(function(o){if(o!==el)o.checked=false;});
  }
  cf();
}
function cf(){
  var qEl=document.getElementById('cq');
  var q=((qEl&&qEl.value)||'').toLowerCase().trim();
  var terms=q.split(/\\s+/).filter(Boolean);
  var sel={};
  document.querySelectorAll('.cfilters input:checked').forEach(function(c){
    (sel[c.dataset.g]=sel[c.dataset.g]||[]).push(c.dataset.v);});
  var active=terms.length>0; for(var _g in sel){active=true;break;}
  var cells=document.querySelectorAll('.pcell'), n=0;
  cells.forEach(function(el){
    var ok=true, f=null;
    try{ f=JSON.parse(el.getAttribute('data-f')); }catch(e){ f=null; }
    if(f){
      for(var g in sel){ if(!sel[g].some(function(v){return (f[g]||[]).indexOf(v)>=0;})){ok=false;break;} }
      if(ok && terms.length){ ok=terms.every(function(t){return (f.q||'').indexOf(t)>=0;}); }
    } else { ok=!active; }   /* unparseable card: show it unless a filter is active */
    el.style.display=ok?'':'none'; if(ok)n++;
  });
  /* safety net: with nothing selected, never show an empty list */
  if(!active && n===0 && cells.length){ cells.forEach(function(el){el.style.display='';}); n=cells.length; }
  var cc=document.getElementById('ccount'); if(cc) cc.textContent=n;
  var cn=document.getElementById('cnone'); if(cn) cn.style.display=n?'none':'block';
}
function cReset(){var q=document.getElementById('cq'); if(q) q.value='';
  document.querySelectorAll('.cfilters input:checked').forEach(function(c){c.checked=false;});cf();}
if(document.readyState!=='loading') cf();
else document.addEventListener('DOMContentLoaded',cf);
</script>"""

    crumb = [(ui["home"], "/"), (ui["products"], "/products/"), (ui["title"], PATH)]
    content = hp.page(lang, PATH, ui["title"] + " | ETIA", ui["lede"], ui["title"], ui["lede"], body, crumb,
                      active="products", trust=False, langs=hp.NAV_PILLAR_LANGS)
    hp.write(lang, PATH, content)
    if lang == "en":
        hp.track(PATH, "core")


# ---- Brand page (e.g. Polyonics): one card per product, scanned from the DB ----
# E-commerce layout: the Polyonics brand page groups products into four series
# (PCB Polyimide · ESD-Safe · Flame-Retardant · Cable & Wire), each a browsable
# aisle of product cards with a "compare specs" link to its selector table.
# Each product is assigned to exactly one aisle (most-specific series wins).
# Polyonics landing page — grouped by product FAMILY (SEM landing structure).
POLY_SERIES = [
    {"key": "apex", "table": "pcb-labels",
     "name": {"en": "APEX Series", "zh": "APEX 系列", "vi": "Dòng APEX", "th": "ซีรีส์ APEX"}},
    {"key": "xf5", "table": "pcb-labels",
     "name": {"en": "XF5 Series · PCB Polyimide", "zh": "XF5 系列 · PCB 聚酰亚胺", "vi": "Dòng XF5 · Polyimide PCB", "th": "ซีรีส์ XF5 · โพลีอิไมด์ PCB"}},
    {"key": "esd7", "table": "esd-safe",
     "name": {"en": "ESD XF7 Series", "zh": "ESD XF7 系列", "vi": "Dòng ESD XF7", "th": "ซีรีส์ ESD XF7"}},
    {"key": "fr", "table": "flame-retardant",
     "name": {"en": "Flame-Retardant Series", "zh": "阻燃系列", "vi": "Dòng chống cháy", "th": "ซีรีส์หน่วงไฟ"}},
    {"key": "cable", "table": "wire-cable",
     "name": {"en": "Cable & Wire Marking", "zh": "线缆标识系列", "vi": "Đánh dấu dây & cáp", "th": "ซีรีส์ทำเครื่องหมายสายไฟ"}},
]
POLY_COMPARE = {"en": "Compare specs →", "zh": "对比规格 →", "vi": "So sánh thông số →", "th": "เปรียบเทียบสเปก →"}
# XF-446 (ESD PET) folds into the ESD family — we lead PET with our own E-2712.
_FAM_ESD7 = {"xf-781", "xf-782", "xf-784", "xf-446"}
_FAM_FR = {"xf-603", "xf-611"}
_FAM_CABLE = {"xf-300", "xf-302", "xf-731", "xf-732"}
def poly_series_key(slug):
    if slug.startswith("xf-101") or slug.startswith("xf-102"): return "apex"
    if slug in _FAM_ESD7: return "esd7"
    if slug in _FAM_FR: return "fr"
    if slug in _FAM_CABLE: return "cable"
    return "xf5"

BRAND_PATH = {"polyonics": "/products/polyonics/", "heatproof": "/products/heatproof/"}
# HEATPROOF functional segments (browsing aisles on the brand page).
HP_SEGMENTS = [
    {"key": "direct", "name": {"en": "Direct Hot Application", "zh": "热态直贴", "vi": "Dán trực tiếp khi nóng", "th": "ติดขณะร้อนโดยตรง"},
     "slugs": ["hp-700t", "hp-800c", "hp-901", "hp-x2049"]},
    {"key": "heatmgmt", "name": {"en": "Heat Management Labels", "zh": "热管理标签", "vi": "Nhãn quản lý nhiệt", "th": "ฉลากการจัดการความร้อน"},
     "slugs": ["hp-360", "hp-x2080", "hp-120s"]},
    {"key": "ceramic", "name": {"en": "Ceramic Labels", "zh": "陶瓷标签", "vi": "Nhãn gốm", "th": "ฉลากเซรามิก"},
     "slugs": ["hp-cbr11", "hp-cbr13", "hp-cbr-cx2"]},
    {"key": "tags", "name": {"en": "Heat-Treatment Tags", "zh": "热处理吊牌", "vi": "Thẻ xử lý nhiệt", "th": "แท็กอบชุบความร้อน"},
     "slugs": ["hp-l90", "hp-l80", "hp-m83"]},
]
# HEATPROOF brand (ETIA's own extreme-temperature line) — steel banner, grouped by temp tier.
HP_BANNER = hp._COS + "INDUSTRY/STEEL-BANNER"
HP_HEAD = {
    "en": "HEATPROOF — Extreme-Temperature Labels & Tags",
    "zh": "HEATPROOF —— 极端高温标签与吊牌",
    "vi": "HEATPROOF — Nhãn & thẻ nhiệt độ cực cao",
    "th": "HEATPROOF — ฉลากและแท็กอุณหภูมิสูงสุดขั้ว",
}
HP_OVERVIEW = {
    "en": [
        "HEATPROOF labels and tags provide reliable identification and traceability through extreme heat and harsh industrial processes, helping prevent material mix-ups and shipping errors.",
        "The line spans metal-foil, stainless-steel and ceramic-transfer constructions for heat treatment, hot-metal application, pickling and firing — from around 200 °C up to 1200 °C.",
    ],
    "zh": [
        "HEATPROOF 标签与吊牌在极端高温与严苛工业工艺中提供可靠的标识与追溯，帮助避免物料混淆与发货错误。",
        "产品线涵盖金属箔、不锈钢与陶瓷转印结构，适用于热处理、热金属直贴、酸洗与烧制 —— 温度范围约 200 °C 至 1200 °C。",
    ],
    "vi": [
        "Nhãn và thẻ HEATPROOF cung cấp khả năng nhận diện và truy xuất đáng tin cậy qua nhiệt độ khắc nghiệt và các quy trình công nghiệp khắc nghiệt, giúp ngăn nhầm lẫn vật liệu và sai sót giao hàng.",
        "Dòng sản phẩm gồm cấu tạo lá kim loại, thép không gỉ và chuyển in gốm cho xử lý nhiệt, dán kim loại nóng, tẩy gỉ và nung — từ khoảng 200 °C đến 1200 °C.",
    ],
    "th": [
        "ฉลากและแท็ก HEATPROOF ให้การระบุและการตรวจสอบย้อนกลับที่เชื่อถือได้ผ่านความร้อนสุดขั้วและกระบวนการอุตสาหกรรมที่รุนแรง ช่วยป้องกันการสับสนของวัสดุและข้อผิดพลาดในการจัดส่ง",
        "ไลน์ผลิตภัณฑ์ครอบคลุมโครงสร้างฟอยล์โลหะ สแตนเลส และถ่ายโอนเซรามิก สำหรับการอบชุบ การติดโลหะร้อน การกัดกรด และการเผา — ตั้งแต่ประมาณ 200 °C ถึง 1200 °C",
    ],
}
BRAND_UI = {
    "en": {"eyebrow": "By Brand", "view": "View product →", "home": "Home", "products": "Products",
           "empty": "Products coming soon.",
           "lede": {"polyonics": "Genuine imported Polyonics polyimide label materials — stocked and application-supported by ETIA for reflow, cleaning and ESD-controlled electronics processes.", "heatproof": "ETIA\u2019s own extreme-temperature label and tag line for heat treatment, hot-metal application and ceramic firing \u2014 from 200 \u00b0C to 1200 \u00b0C."}},
    "zh": {"eyebrow": "按品牌", "view": "查看产品 →", "home": "首页", "products": "产品",
           "empty": "产品即将上线。",
           "lede": {"polyonics": "Polyonics 原装进口聚酰亚胺标签材料 —— 由 ETIA 备货并提供应用支持，适配回流焊、清洗与防静电电子制程。", "heatproof": "ETIA 自研的极端高温标签与吊牌系列，适用于热处理、热金属直贴与陶瓷烧制 —— 200 °C 至 1200 °C。"}},
    "vi": {"eyebrow": "Theo thương hiệu", "view": "Xem sản phẩm →", "home": "Trang chủ", "products": "Sản phẩm",
           "empty": "Sản phẩm sắp ra mắt.",
           "lede": {"polyonics": "Vật liệu nhãn polyimide Polyonics nhập khẩu chính hãng — được ETIA lưu kho và hỗ trợ ứng dụng cho reflow, làm sạch và quy trình điện tử kiểm soát ESD.", "heatproof": "Dòng nhãn và thẻ nhiệt độ cực cao của ETIA cho xử lý nhiệt, dán kim loại nóng và nung gốm — từ 200 °C đến 1200 °C."}},
    "th": {"eyebrow": "ตามแบรนด์", "view": "ดูสินค้า →", "home": "หน้าแรก", "products": "ผลิตภัณฑ์",
           "empty": "สินค้าเร็วๆ นี้",
           "lede": {"polyonics": "วัสดุฉลากโพลีอิไมด์ Polyonics นำเข้าแท้ — สต๊อกและสนับสนุนการใช้งานโดย ETIA สำหรับรีโฟลว์ การล้าง และกระบวนการอิเล็กทรอนิกส์ที่ควบคุม ESD", "heatproof": "ไลน์ฉลากและแท็กอุณหภูมิสูงสุดขั้วของ ETIA สำหรับการอบชุบ การติดโลหะร้อน และการเผาเซรามิก — 200 °C ถึง 1200 °C"}},
}
# Polyonics brand banner + overview. Per client decision the Polyonics page
# reuses the PCB banner (Polyonics is a PCB/electronics-centric line) — no
# bespoke banner.
POLY_BANNER = hp._COS + "INDUSTRY/PCB-BANNERNEW.jpg"
POLY_HEAD = {
    "en": "Polyonics — High-Performance Label Materials",
    "zh": "Polyonics —— 高性能标签材料",
    "vi": "Polyonics — Vật liệu nhãn hiệu năng cao",
    "th": "Polyonics — วัสดุฉลากประสิทธิภาพสูง",
}
POLY_OVERVIEW_LABEL = {"en": "Overview", "zh": "品牌概述", "vi": "Tổng quan", "th": "ภาพรวม"}
# Two-paragraph brand overview (client-supplied EN + ZH; VN/TH translated).
POLY_IMG = hp._COS + "PRODUCT/POLYONICSNETIA"
POLY_OVERVIEW = {
    "en": [
        "For over 30 years, Polyonics has specialized in high-performance polyimide label materials engineered for PCB and electronics manufacturing. Its materials withstand demanding processes including high-temperature reflow, aggressive fluxes, chemical cleaning and ESD-sensitive production.",
        "ETIA has partnered with Polyonics for over 20 years and is its exclusive distributor in China and authorized distributor in Southeast Asia. We provide genuine materials, local supply and application support for customers in China, Thailand and Vietnam.",
    ],
    "zh": [
        "30 多年来，Polyonics 专注于面向 PCB 与电子制造的高性能聚酰亚胺标签材料。其材料可耐受高温回流焊、活性助焊剂、化学清洗及静电敏感（ESD）制程等严苛工艺。",
        "ETIA 与 Polyonics 合作已超过 20 年，是其在中国的独家经销商及东南亚授权代理。我们为中国、泰国与越南的客户提供正品材料、本地供货与应用支持。",
    ],
    "vi": [
        "Hơn 30 năm qua, Polyonics chuyên về vật liệu nhãn polyimide hiệu năng cao cho sản xuất PCB và điện tử. Vật liệu của hãng chịu được các quy trình khắc nghiệt gồm reflow nhiệt độ cao, flux hoạt tính mạnh, làm sạch hóa chất và sản xuất nhạy ESD.",
        "ETIA đã hợp tác với Polyonics hơn 20 năm và là nhà phân phối độc quyền tại Trung Quốc và đại lý ủy quyền tại Đông Nam Á. Chúng tôi cung cấp vật liệu chính hãng, nguồn cung tại chỗ và hỗ trợ ứng dụng cho khách hàng tại Trung Quốc, Thái Lan và Việt Nam.",
    ],
    "th": [
        "กว่า 30 ปีที่ Polyonics เชี่ยวชาญด้านวัสดุฉลากโพลีอิไมด์ประสิทธิภาพสูงสำหรับการผลิต PCB และอิเล็กทรอนิกส์ วัสดุทนกระบวนการที่เข้มงวด ได้แก่ รีโฟลว์อุณหภูมิสูง ฟลักซ์ฤทธิ์รุนแรง การล้างด้วยสารเคมี และการผลิตที่ไวต่อ ESD",
        "ETIA ร่วมมือกับ Polyonics มากว่า 20 ปี และเป็นตัวแทนจำหน่ายแต่เพียงผู้เดียวในจีนและตัวแทนจำหน่ายที่ได้รับอนุญาตในเอเชียตะวันออกเฉียงใต้ เราจัดหาวัสดุของแท้ การจัดหาในพื้นที่ และการสนับสนุนการใช้งานให้ลูกค้าในจีน ไทย และเวียดนาม",
    ],
}
BRAND_CSS = """<style>
.bwrap{max-width:1120px;margin:0 auto;padding:34px 22px 54px}
.bover{color:#41506e;font-size:15.5px;line-height:1.7;max-width:80ch;margin:0 0 16px}
.bover-2col{display:grid;grid-template-columns:1.4fr .9fr;gap:34px;align-items:center;margin:0 0 22px}
.bover-2col .bover{margin-bottom:14px}
.bover-img{margin:0}
.bover-img img{width:100%;height:auto;border-radius:14px;border:1px solid #e6ecf6;box-shadow:0 12px 30px rgba(16,34,58,.10);display:block;background:#f3f6fc}
@media(max-width:820px){.bover-2col{grid-template-columns:1fr;gap:18px}.bover-img{max-width:460px}}
.bsec{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin:34px 0 14px;padding-top:18px;border-top:1px solid #e6ecf6}
.bsec h2{font-family:var(--sans);font-weight:800;color:#143C96;font-size:21px;margin:0}
.bsec .cnt{font-size:12px;font-weight:800;color:#1A56DB;background:#eaf1ff;border-radius:999px;padding:2px 10px}
.bsec .tbl{margin-left:auto;font-size:13.5px;font-weight:800;color:#1A56DB;text-decoration:none;white-space:nowrap}
.bsec .tbl:hover{text-decoration:underline}
.bhead .eyebrow{font-size:12px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:#1A56DB}
.bhead h1{font-family:var(--sans);font-weight:800;color:#143C96;font-size:clamp(30px,4vw,44px);margin:8px 0 8px}
.bhead p{color:#51607e;font-size:16px;max-width:70ch;margin:0 0 8px}
.bgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px;margin-top:26px}
.bcard{display:flex;flex-direction:column;background:#fff;border:1px solid #dbe3f1;border-radius:16px;overflow:hidden;text-decoration:none;color:#17203a;transition:box-shadow .15s,transform .15s,border-color .15s}
.bcard:hover{box-shadow:0 16px 38px rgba(20,60,150,.15);transform:translateY(-3px);border-color:#1A56DB}
.bcard-img{aspect-ratio:16/10;background:#eef3fc;position:relative;display:grid;place-items:center;overflow:hidden}
.bcard-img img{width:100%;height:100%;object-fit:cover;display:block}
.bcard-img.ph{background:linear-gradient(150deg,#1A56DB,#143C96)}
.bcard-img.lbl{background:#eef3fc;aspect-ratio:4/3}
.bcard-img.photo{background:#fff;padding:12px;box-sizing:border-box}
.bcard-img.photo img{object-fit:contain}
.bcard-img.lbl svg.bclbl{width:100%;height:100%;display:block}
.bcard-img.ph span{color:#fff;font-family:var(--sans);font-weight:800;font-size:22px;letter-spacing:.02em;padding:0 16px;text-align:center}
.bcard-b{padding:16px 18px 18px;display:flex;flex-direction:column;gap:8px;flex:1}
.bcard-b h3{margin:0;font-size:17px;color:#143C96;font-weight:800;line-height:1.28}
.bcard-b p{margin:0;font-size:13.5px;color:#5a6884;line-height:1.5;flex:1}
.bchips{display:flex;flex-wrap:wrap;gap:6px}
.bchip{font-size:11px;font-weight:800;color:#2c7a1e;background:#e6f5e0;border-radius:999px;padding:3px 9px}
.bchip.t{color:#1A56DB;background:#eaf1ff}
.bchip.esd{color:#1A56DB;background:#eaf1ff}
.bchip.clr{color:#3a4763;background:#f1f4fa;display:inline-flex;align-items:center}
.bchip.clr i{width:8px;height:8px;border-radius:50%;margin-right:5px;box-shadow:0 0 0 1px rgba(0,0,0,.18)}
.bgo{font-size:13px;font-weight:800;color:#41A62A}
.bempty{color:#5a6884;font-size:15px;padding:30px 4px}
</style>"""

# ---- Polyonics catalog: category selector tables (from Polyonics brochures) ----
def _ml(en, zh, vi, th): return {"en": en, "zh": zh, "vi": vi, "th": th}
POLY_FILM = {
    "pi1": _ml("1 mil (25µm) Polyimide", "1 mil（25µm）聚酰亚胺", "Polyimide 1 mil (25µm)", "โพลีอิไมด์ 1 mil (25µm)"),
    "pi2": _ml("2 mil (50µm) Polyimide", "2 mil（50µm）聚酰亚胺", "Polyimide 2 mil (50µm)", "โพลีอิไมด์ 2 mil (50µm)"),
    "pet15": _ml("1.5 mil (38µm) Polyester", "1.5 mil（38µm）聚酯", "Polyester 1.5 mil (38µm)", "โพลีเอสเตอร์ 1.5 mil (38µm)"),
    "pet2": _ml("2 mil (50µm) Polyester", "2 mil（50µm）聚酯", "Polyester 2 mil (50µm)", "โพลีเอสเตอร์ 2 mil (50µm)"),
    "nyl5": _ml("5 mil (125µm) Nylon", "5 mil（125µm）尼龙", "Nylon 5 mil (125µm)", "ไนลอน 5 mil (125µm)"),
}
POLY_FIN = {
    "sgw": _ml("Semi-gloss white", "半光白", "Trắng bán bóng", "สีขาวกึ่งเงา"),
    "mw": _ml("Matte white", "哑光白", "Trắng mờ", "สีขาวด้าน"),
    "hgw": _ml("High-gloss white", "高光白", "Trắng bóng cao", "สีขาวเงาสูง"),
    "sgb": _ml("Semi-gloss blue", "半光蓝", "Xanh bán bóng", "สีน้ำเงินกึ่งเงา"),
    "sgg": _ml("Semi-gloss green", "半光绿", "Xanh lá bán bóng", "สีเขียวกึ่งเงา"),
    "sgy": _ml("Semi-gloss yellow", "半光黄", "Vàng bán bóng", "สีเหลืองกึ่งเงา"),
    "hgy": _ml("High-gloss yellow", "高光黄", "Vàng bóng cao", "สีเหลืองเงาสูง"),
    "mbuff": _ml("Matte buff", "哑光米黄", "Be mờ", "สีน้ำตาลอ่อนด้าน"),
    "gw": _ml("Gloss white", "亮白", "Trắng bóng", "สีขาวเงา"),
    "woven": _ml("White woven cloth", "白色机织布", "Vải dệt trắng", "ผ้าทอสีขาว"),
    "clear": _ml("Clear (amber)", "透明（琥珀）", "Trong suốt (hổ phách)", "ใส (สีอำพัน)"),
}
POLY_TEMP = {
    "hi": "150 °C/100h · 260 °C/5min · 300 °C/90s",
    "pet611": "−40 to 150 °C",
    "pet446": "150 °C/100h · −40 to 204 °C op",
    "ovl": "−40 to 500 °C",
    "nyl": "180 °C/5min · 110 °C/30d · −196 °C cryo",
}
POLY_FEAT = {
    "esd": _ml("ESD-Safe", "防静电", "ESD-Safe", "ESD-Safe"),
    "fr": _ml("Flame-Retardant", "阻燃", "Chống cháy", "หน่วงไฟ"),
    "flux": _ml("Flux-Resistant", "耐助焊剂", "Kháng flux", "ทนฟลักซ์"),
    "uv": _ml("UV & Chemical", "耐 UV 与化学", "UV & Hóa chất", "UV และสารเคมี"),
    "ul94": _ml("UL94 VTM-0", "UL94 VTM-0", "UL94 VTM-0", "UL94 VTM-0"),
    "ul969": _ml("UL969", "UL969", "UL969", "UL969"),
    "fmvss": _ml("FMVSS 302", "FMVSS 302", "FMVSS 302", "FMVSS 302"),
    "bss": _ml("BSS 7238 / FAR 25.853", "BSS 7238 / FAR 25.853", "BSS 7238 / FAR 25.853", "BSS 7238 / FAR 25.853"),
    "reach": _ml("REACH / RoHS", "REACH / RoHS", "REACH / RoHS", "REACH / RoHS"),
}
POLY_CATS = [
    {"slug": "pcb-labels",
     "title": _ml("PCB Polyimide Label Materials", "PCB 聚酰亚胺标签材料", "Vật liệu nhãn Polyimide PCB", "วัสดุฉลากโพลีอิไมด์ PCB"),
     "lede": _ml("Polyonics polyimide & polyester labels for reflow, wave solder and PCB cleaning — 1 & 2 mil, in multiple finishes and colours.",
                 "Polyonics 聚酰亚胺与聚酯标签，适配回流焊、波峰焊与 PCB 清洗 —— 1 与 2 mil，多种表面与颜色。",
                 "Nhãn polyimide & polyester Polyonics cho reflow, hàn sóng và làm sạch PCB — 1 & 2 mil, nhiều bề mặt và màu sắc.",
                 "ฉลากโพลีอิไมด์และโพลีเอสเตอร์ Polyonics สำหรับรีโฟลว์ เวฟโซลเดอร์ และการล้าง PCB — 1 และ 2 mil หลายพื้นผิวและสี"),
     "rows": [
        ["XF-504","pi1","sgb","1 mil (25 µm) acrylic","hi",["ul969","reach"]],
        ["XF-505","pi1","sgg","1 mil (25 µm) acrylic","hi",["ul969","reach"]],
        ["XF-518","pi1","mw","1 mil (25 µm) acrylic","hi",["ul969","reach"]],
        ["XF-528","pi1","hgw","1 mil (25 µm) acrylic","hi",["ul969","reach"]],
        ["XF-581","pi1","sgw","1 mil (25 µm) acrylic","hi",["ul969","reach"]],
        ["XF-583","pi1","mw","1 mil (25 µm) acrylic","hi",["ul969","reach"]],
        ["XF-603","pi1","sgw","1.1 mil (28 µm) acrylic","hi",["fr","ul969","reach"]],
        ["XF-731","pi1","sgw","1 mil (25 µm) acrylic","hi",["flux","ul969","reach"]],
        ["XF-781","pi1","sgw","1 mil (25 µm) acrylic","hi",["esd","ul969","reach"]],
        ["XF-519","pi2","mw","1.5 mil (38 µm) acrylic","hi",["ul969","reach"]],
        ["XF-520","pi2","sgy","2 mil (50 µm) acrylic","hi",["ul969","reach"]],
        ["XF-525","pi2","sgg","2 mil (50 µm) acrylic","hi",["ul969","reach"]],
        ["XF-529","pi2","hgw","1.5 mil (38 µm) acrylic","hi",["ul969","reach"]],
        ["XF-541","pi2","mbuff","2 mil (50 µm) acrylic","hi",["ul969","reach"]],
        ["XF-552","pi2","hgy","2.4 mil (61 µm) acrylic","hi",["reach"]],
        ["XF-555","pi2","hgw","2 mil (50 µm) acrylic","hi",["ul969","reach"]],
        ["XF-582","pi2","sgw","2 mil (50 µm) acrylic","hi",["ul969","reach"]],
        ["XF-584","pi2","mw","2 mil (50 µm) acrylic","hi",["ul969","reach"]],
        ["XF-592","pi2","sgw","2.4 mil (61 µm) acrylic","hi",["ul969","reach"]],
        ["XF-732","pi2","sgw","2 mil (50 µm) acrylic","hi",["flux","ul969","reach"]],
        ["XF-782","pi2","sgw","2 mil (50 µm) acrylic","hi",["esd","ul969","reach"]],
        ["XF-611","pet15","sgw","1.1 mil (28 µm) acrylic","pet611",["fr","ul969","reach"]],
        ["XF-446","pet2","gw","1 mil (25 µm) acrylic","pet446",["esd","ul969","reach"]],
     ]},
    {"slug": "flame-retardant",
     "title": _ml("Flame Retardant Label Materials", "阻燃标签材料", "Vật liệu nhãn chống cháy", "วัสดุฉลากหน่วงไฟ"),
     "lede": _ml("UL94 VTM-0 rated polyimide and polyester labels with char-forming chemistry for PCB, battery, power-supply and under-the-hood identification.",
                 "UL94 VTM-0 认证的聚酰亚胺与聚酯标签，采用成炭化学，适用于 PCB、电池、电源与发动机舱标识。",
                 "Nhãn polyimide và polyester đạt UL94 VTM-0 với hóa học tạo lớp than, cho nhận diện PCB, pin, nguồn điện và khoang động cơ.",
                 "ฉลากโพลีอิไมด์และโพลีเอสเตอร์ที่ได้รับ UL94 VTM-0 ด้วยเคมีสร้างชั้นถ่าน สำหรับระบุ PCB แบตเตอรี่ พาวเวอร์ซัพพลาย และห้องเครื่อง"),
     "rows": [
        ["XF-603","pi1","sgw","1.1 mil (28 µm) acrylic","hi",["fr","ul94","ul969","fmvss","reach"]],
        ["XF-611","pet15","sgw","1.1 mil (28 µm) acrylic","pet611",["fr","ul94","ul969","bss","reach"]],
     ]},
    {"slug": "wire-cable",
     "title": _ml("Wire Marking Label Materials", "线缆标识标签材料", "Vật liệu nhãn đánh dấu dây", "วัสดุฉลากทำเครื่องหมายสายไฟ"),
     "lede": _ml("Flame-retardant polyimide and woven-nylon labels for wire, cable and harness identification.",
                 "阻燃聚酰亚胺与机织尼龙标签，用于线缆与束线标识。",
                 "Nhãn polyimide chống cháy và nylon dệt cho nhận diện dây, cáp và bó dây.",
                 "ฉลากโพลีอิไมด์หน่วงไฟและไนลอนทอ สำหรับระบุสายไฟ สายเคเบิล และชุดสายไฟ"),
     "rows": [
        ["XF-603","pi1","sgw","1 mil (25 µm) acrylic","hi",["fr"]],
        ["XF-300","nyl5","woven","2 mil (50 µm) high-temp acrylic","nyl",["fr"]],
        ["XF-302","nyl5","woven","1 mil (25 µm) high-temp acrylic","nyl",["fr"]],
     ]},
    {"slug": "esd-safe",
     "title": _ml("ESD Safe Label Materials", "防静电标签材料", "Vật liệu nhãn ESD-Safe", "วัสดุฉลาก ESD-Safe"),
     "lede": _ml("Static-dissipative, low-charging polyimide and polyester labels for ESD-protected areas (ANSI/ESD S20.20).",
                 "静电耗散、低起电聚酰亚胺与聚酯标签，适用于静电防护区（ANSI/ESD S20.20）。",
                 "Nhãn polyimide & polyester tiêu tán tĩnh, ít tích điện cho khu vực bảo vệ tĩnh điện (ANSI/ESD S20.20).",
                 "ฉลากโพลีอิไมด์และโพลีเอสเตอร์แบบกระจายประจุ ประจุต่ำ สำหรับพื้นที่ป้องกันไฟฟ้าสถิต (ANSI/ESD S20.20)"),
     "rows": [
        ["XF-781","pi1","sgw","1 mil (25 µm) acrylic","hi",["esd"]],
        ["XF-784","pi1","mw","1 mil (25 µm) acrylic","hi",["esd"]],
        ["XF-782","pi2","sgw","2 mil (50 µm) acrylic","hi",["esd"]],
        ["XF-446","pet2","gw","1 mil (25 µm) acrylic","pet446",["esd"]],
     ]},
]
POLY_CAT_UI = {
    "en": {"cols": ["Product","Film","Finish","Adhesive","Temperature","Features"], "back": "← All Polyonics", "eyebrow": "Polyonics catalogue", "browse": "Browse the catalogue", "count": "products", "home": "Home", "products": "Products", "note": "Full temperature, adhesion, chemical and compliance data are on each product datasheet — contact us for the TDS."},
    "zh": {"cols": ["型号","面材","表面","胶粘剂","温度","特性"], "back": "← 返回 Polyonics", "eyebrow": "Polyonics 产品目录", "browse": "浏览目录", "count": "款", "home": "首页", "products": "产品", "note": "完整的温度、粘着、化学与合规数据见各产品数据表 —— 索取 TDS 请联系我们。"},
    "vi": {"cols": ["Mã","Màng","Bề mặt","Keo","Nhiệt độ","Tính năng"], "back": "← Tất cả Polyonics", "eyebrow": "Danh mục Polyonics", "browse": "Xem danh mục", "count": "sản phẩm", "home": "Trang chủ", "products": "Sản phẩm", "note": "Dữ liệu đầy đủ về nhiệt độ, độ bám, hóa chất và tuân thủ có trong datasheet từng sản phẩm — liên hệ để nhận TDS."},
    "th": {"cols": ["รุ่น","ฟิล์ม","พื้นผิว","กาว","อุณหภูมิ","คุณสมบัติ"], "back": "← Polyonics ทั้งหมด", "eyebrow": "แคตตาล็อก Polyonics", "browse": "ดูแคตตาล็อก", "count": "รายการ", "home": "หน้าแรก", "products": "ผลิตภัณฑ์", "note": "ข้อมูลอุณหภูมิ การยึดเกาะ สารเคมี และการรับรองฉบับเต็มอยู่ในเอกสารข้อมูลของแต่ละสินค้า — ติดต่อขอ TDS"},
}
POLY_CAT_CSS = """<style>
.pcat{max-width:1080px;margin:0 auto;padding:30px 22px 54px}
.pcat .eyebrow{font-size:12px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:#1A56DB}
.pcat h1{font-family:var(--sans);font-weight:800;color:#143C96;font-size:clamp(26px,3.4vw,38px);margin:8px 0 8px}
.pcat .lede{color:#51607e;font-size:16px;max-width:74ch;margin:0 0 20px}
.ptable-wrap{overflow-x:auto;border:1px solid #dbe3f1;border-radius:14px}
.ptable{border-collapse:collapse;width:100%;min-width:680px;font-size:13.5px}
.ptable th{background:#f2f6fd;color:#143C96;font-weight:800;text-align:left;padding:11px 14px;border-bottom:2px solid #dbe3f1;white-space:nowrap;position:sticky;top:0}
.ptable td{padding:10px 14px;border-bottom:1px solid #eef2f8;color:#33425e;vertical-align:top}
.ptable tr:hover td{background:#f8fbff}
.ptable .mdl{font-weight:800;color:#143C96;white-space:nowrap}
.ptable .matchip{font-size:10px;font-weight:800;border-radius:5px;padding:1px 6px;margin-left:5px;vertical-align:middle}
.ptable .matchip.m-pi{color:#143C96;background:#dfe8fb}
.ptable .matchip.m-pet{color:#6b3fb0;background:#efe8fb}
.ptable .matchip.m-nylon{color:#2c7a1e;background:#e6f5e0}
.ptable .feat{display:inline-block;font-size:10.5px;font-weight:800;border-radius:999px;padding:2px 8px;margin:1px 3px 1px 0;white-space:nowrap}
.ptable .feat.esd{color:#1A56DB;background:#eaf1ff}
.ptable .feat.fr{color:#b4520a;background:#fdeede}
.ptable .feat.flux{color:#2c7a1e;background:#e6f5e0}
.ptable .feat.uv{color:#6b3fb0;background:#f0e9fb}
.ptable .feat.ul94,.ptable .feat.ul969,.ptable .feat.fmvss,.ptable .feat.bss,.ptable .feat.reach{color:#334a78;background:#eef2fb}
.pcat .pnote{color:#5a6884;font-size:13px;margin:14px 2px 0}
.pcat .pback{display:inline-block;margin:18px 0 0;font-size:14px;font-weight:800;color:#1A56DB;text-decoration:none}
/* category cards on the Polyonics landing */
.pcatcards{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:16px;margin:6px 0 30px}
.pcatcard{display:block;background:#143C96;background:linear-gradient(140deg,#1A56DB,#143C96);border-radius:14px;padding:18px 18px 16px;text-decoration:none;color:#fff;transition:transform .15s,box-shadow .15s}
.pcatcard:hover{transform:translateY(-3px);box-shadow:0 14px 32px rgba(20,60,150,.24)}
.pcatcard b{display:block;font-size:16.5px;font-weight:800;line-height:1.25}
.pcatcard span{display:block;font-size:12.5px;color:#cfe0ff;margin-top:5px}
.pcatcard .n{display:inline-block;margin-top:10px;font-size:11.5px;font-weight:800;background:rgba(255,255,255,.16);border-radius:999px;padding:3px 10px}
.bsechd{font-size:12px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#1A56DB;margin:4px 0 12px}
</style>"""

def _poly_cat_by_slug(slug):
    for c in POLY_CATS:
        if c["slug"] == slug:
            return c
    return None

def poly_category_cards(lang):
    ui = POLY_CAT_UI[lang]
    cards = ""
    for c in POLY_CATS:
        title = c["title"].get(lang) or c["title"]["en"]
        lede = c["lede"].get(lang) or c["lede"]["en"]
        cards += ('<a class="pcatcard" href="%s"><b>%s</b><span>%s</span>'
                  '<span class="n">%d %s</span></a>') % (
            hp.Lx(lang, "/products/polyonics/%s/" % c["slug"]), esc(title), esc(lede),
            len(c["rows"]), esc(ui["count"]))
    return ('<div class="bsechd">%s</div><div class="pcatcards">%s</div>' % (esc(ui["browse"]), cards))

def build_poly_cat(lang, slug):
    c = _poly_cat_by_slug(slug); ui = POLY_CAT_UI[lang]
    path = "/products/polyonics/%s/" % slug
    title = c["title"].get(lang) or c["title"]["en"]
    lede = c["lede"].get(lang) or c["lede"]["en"]
    def L(d): return d.get(lang) or d["en"]
    head = "".join("<th>%s</th>" % esc(h) for h in ui["cols"])
    mat = lambda f: "PI" if f.startswith("pi") else ("PET" if f.startswith("pet") else "Nylon")
    landing = set(os.path.splitext(f)[0] for f in os.listdir(PDIR) if f.endswith(".json"))
    body_rows = ""
    for model, film, fin, adh, temp, feats in c["rows"]:
        fb = "".join('<span class="feat %s">%s</span>' % (k, esc(L(POLY_FEAT[k]))) for k in feats)
        mtag = '<span class="matchip m-%s">%s</span>' % (mat(film).lower(), mat(film))
        mslug = model.lower()
        mcell = ('<a href="%s">%s</a>' % (hp.Lx(lang, "/products/item/%s/" % mslug), esc(model))) \
            if mslug in landing else esc(model)
        body_rows += ("<tr><td class=\"mdl\">%s %s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>") % (
            mcell, mtag, esc(L(POLY_FILM[film])), esc(L(POLY_FIN[fin])), esc(adh), esc(POLY_TEMP[temp]), fb or "—")
    table = ('<div class="ptable-wrap"><table class="ptable"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
             % (head, body_rows))
    body = POLY_CAT_CSS + ('<div class="pcat"><div class="eyebrow">%s</div><h1>%s</h1><p class="lede">%s</p>'
            '%s<p class="pnote">%s</p><a class="pback" href="%s">%s</a></div>') % (
        esc(ui["eyebrow"]), esc(title), esc(lede), table, esc(ui["note"]),
        hp.Lx(lang, "/products/polyonics/"), esc(ui["back"]))
    crumb = [(ui["home"], "/"), (ui["products"], "/products/"), ("Polyonics", "/products/polyonics/"), (title, path)]
    content = hp.page(lang, path, title + " | Polyonics | ETIA", lede, title, "", body, crumb,
                      active="products", trust=False, langs=hp.NAV_PILLAR_LANGS)
    hp.write(lang, path, content)
    if lang == "en":
        hp.track(path, "products")

def build_brand(records, lang, bkey):
    ui = BRAND_UI[lang]
    path = BRAND_PATH[bkey]
    bname = gp.BRAND_NAMES[bkey].get(lang) or gp.BRAND_NAMES[bkey]["en"]
    def L(node):
        if isinstance(node, dict):
            return node.get(lang) or node.get("en") or node.get("zh") or ""
        return node or ""
    items = [r for r in records if r["brand"] == bkey]
    def card(r):
        img = r.get("product_img", "")
        # A real product photo (under the COS PRODUCT/ folder) wins; every other
        # card falls back to the generated barcode-label tile.
        if img and "/PRODUCT/" in img:
            media = ('<div class="bcard-img photo"><img src="%s" alt="%s" loading="lazy" '
                     'onerror="var p=this.parentNode;p.classList.add(\'ph\');p.innerHTML=\'<span>%s</span>\'"></div>') % (
                esc(img), esc(L(r["title"])), esc(L(r["title"])))
        else:
            eyebrow = "ETIA" if bkey == "heatproof" else "POLYONICS"
            media = '<div class="bcard-img lbl">%s</div>' % barcode_label_svg(_model_code(r["slug"]), eyebrow)
        chips = ""
        for f in r["facestocks"][:1]:
            chips += '<span class="bchip">%s</span>' % esc(L(f))
        for t in r["temps"][:1]:
            chips += '<span class="bchip t">%s</span>' % esc(L(TEMP_BANDS[t]))
        if "esd" in r["apps"]:
            chips += '<span class="bchip esd">ESD</span>'
        if r.get("color"):
            chips += '<span class="bchip clr"><i style="background:%s"></i>%s</span>' % (
                r["color"]["dot"], esc(L(r["color"]["lab"])))
        return ('<a class="bcard" href="%s">%s<div class="bcard-b"><h3>%s</h3><p>%s</p>'
                '<div class="bchips">%s</div><span class="bgo">%s</span></div></a>') % (
            hp.Lx(lang, r["url"]), media, esc(L(r["title"])), esc(L(r["tagline"])), chips, esc(ui["view"]))
    lede = ui["lede"].get(bkey, "")
    hero = None
    if bkey == "polyonics":
        # brand hero banner (PCB banner + single green CTA) + client overview
        head = POLY_HEAD.get(lang) or POLY_HEAD["en"]
        hero = hp.home_banner(lang, POLY_BANNER, ui["eyebrow"], head, lede, "", "", "", "", "")
        paras = POLY_OVERVIEW.get(lang) or POLY_OVERVIEW["en"]
        ov_txt = ('<div class="bsechd">%s</div>%s' %
                  (esc(POLY_OVERVIEW_LABEL.get(lang) or POLY_OVERVIEW_LABEL["en"]),
                   "".join('<p class="bover">%s</p>' % esc(p) for p in paras)))
        ov_img = ('<div class="bover-img"><img src="%s" alt="Polyonics × ETIA" loading="lazy" '
                  'onerror="this.parentNode.remove()"></div>' % esc(POLY_IMG))
        overview = '<div class="bover-2col">%s%s</div>' % (ov_txt, ov_img)
        # e-commerce aisles: one section per series, product cards + compare-specs link
        sections = ""
        for s in POLY_SERIES:
            members = sorted((r for r in items if poly_series_key(r["slug"]) == s["key"]),
                             key=lambda r: r["slug"])
            if not members:
                continue
            nm = s["name"].get(lang) or s["name"]["en"]
            tbl = hp.Lx(lang, "/products/polyonics/%s/" % s["table"])
            sections += ('<div class="bsec"><h2>%s</h2><span class="cnt">%d</span>'
                         '<a class="tbl" href="%s">%s</a></div><div class="bgrid">%s</div>') % (
                esc(nm), len(members), tbl, esc(POLY_COMPARE.get(lang) or POLY_COMPARE["en"]),
                "".join(card(r) for r in members))
        body = BRAND_CSS + POLY_CAT_CSS + ('<div class="bwrap">%s%s</div>' % (overview, sections))
    elif bkey == "heatproof":
        # brand hero (steel banner) + overview + aisles grouped by temperature tier
        head = HP_HEAD.get(lang) or HP_HEAD["en"]
        hero = hp.home_banner(lang, HP_BANNER, ui["eyebrow"], head, lede, "", "", "", "", "")
        paras = HP_OVERVIEW.get(lang) or HP_OVERVIEW["en"]
        overview = ('<div class="bsechd">%s</div>%s' %
                    (esc(POLY_OVERVIEW_LABEL.get(lang) or POLY_OVERVIEW_LABEL["en"]),
                     "".join('<p class="bover">%s</p>' % esc(p) for p in paras)))
        by_slug = {r["slug"]: r for r in items}
        sections = ""
        placed = set()
        for seg in HP_SEGMENTS:
            members = [by_slug[s] for s in seg["slugs"] if s in by_slug]
            if not members:
                continue
            placed.update(seg["slugs"])
            nm = seg["name"].get(lang) or seg["name"]["en"]
            sections += ('<div class="bsec"><h2>%s</h2><span class="cnt">%d</span></div>'
                         '<div class="bgrid">%s</div>') % (esc(nm), len(members), "".join(card(r) for r in members))
        # any HP product not mapped to a segment falls into a catch-all "More"
        extra = sorted((r for r in items if r["slug"] not in placed), key=lambda r: r["slug"])
        if extra:
            nm = {"en": "More", "zh": "更多", "vi": "Khác", "th": "อื่นๆ"}.get(lang, "More")
            sections += ('<div class="bsec"><h2>%s</h2><span class="cnt">%d</span></div>'
                         '<div class="bgrid">%s</div>') % (esc(nm), len(extra), "".join(card(r) for r in extra))
        body = BRAND_CSS + POLY_CAT_CSS + ('<div class="bwrap">%s%s</div>' % (overview, sections))
    else:
        grid = ('<div class="bgrid">%s</div>' % "".join(card(r) for r in sorted(items, key=lambda x: L(x["title"]).lower()))) \
            if items else ('<p class="bempty">%s</p>' % esc(ui["empty"]))
        body = BRAND_CSS + POLY_CAT_CSS + ('<div class="bwrap"><div class="bhead"><div class="eyebrow">%s</div>'
                            '<h1>%s</h1><p>%s</p></div>%s</div>') % (
            esc(ui["eyebrow"]), esc(bname), esc(lede), grid)
    crumb = [(ui["home"], "/"), (ui["products"], "/products/"), (bname, path)]
    content = hp.page(lang, path, bname + " | ETIA", esc(lede), bname, "", body, crumb,
                      active="products", trust=False, hero=hero, langs=hp.NAV_PILLAR_LANGS)
    hp.write(lang, path, content)
    if lang == "en":
        hp.track(path, "core")


def main():
    records = []
    for f in sorted(os.listdir(PDIR)):
        if not f.endswith(".json"):
            continue
        slug = f[:-5]
        if slug in EXCLUDE:
            continue
        d = json.load(open(os.path.join(PDIR, f), encoding="utf-8"))
        if not d.get("title"):
            continue
        records.append(build_record(d))
    for lang in LANGS:
        build_lang(records, lang)
        for c in POLY_CATS:
            build_poly_cat(lang, c["slug"])
        build_brand(records, lang, "polyonics")
        build_brand(records, lang, "heatproof")
    npoly = sum(1 for r in records if r["brand"] == "polyonics")
    nhp = sum(1 for r in records if r["brand"] == "heatproof")
    ncat = sum(len(c["rows"]) for c in POLY_CATS)
    print("catalog: /products/find/ x4 langs —", len(records), "materials")
    print("brand page: /products/polyonics/ x4 langs —", npoly, "featured products +",
          len(POLY_CATS), "categories /", ncat, "catalogue rows")
    print("brand page: /products/heatproof/ x4 langs —", nhp, "products")


if __name__ == "__main__":
    main()
