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

# ---- Generated product image: a Code 39 barcode label carrying the model code ----
# These products are labels, so a clean barcode + part-number tile is an on-brand,
# consistent, zero-photography "product image". Rendered as inline SVG (no files).
_CODE39 = {
    '0':'nnnwwnwnn','1':'wnnwnnnnw','2':'nnwwnnnnw','3':'wnwwnnnnn','4':'nnnwwnnnw',
    '5':'wnnwwnnnn','6':'nnwwwnnnn','7':'nnnwnnwnw','8':'wnnwnnwnn','9':'nnwwnnwnn',
    'A':'wnnnnwnnw','B':'nnwnnwnnw','C':'wnwnnwnnn','D':'nnnnwwnnw','E':'wnnnwwnnn',
    'F':'nnwnwwnnn','G':'nnnnnwwnw','H':'wnnnnwwnn','I':'nnwnnwwnn','J':'nnnnwwwnn',
    'K':'wnnnnnnww','L':'nnwnnnnww','M':'wnwnnnnwn','N':'nnnnwnnww','O':'wnnnwnnwn',
    'P':'nnwnwnnwn','Q':'nnnnnnwww','R':'wnnnnnwwn','S':'nnwnnnwwn','T':'nnnnwnwwn',
    'U':'wwnnnnnnw','V':'nwwnnnnnw','W':'wwwnnnnnn','X':'nwnnwnnnw','Y':'wwnnwnnnn',
    'Z':'nwwnwnnnn','-':'nwnnnnwnw','.':'wwnnnnwnn',' ':'nwwnnnwnn','*':'nwnnwnwnn',
}
def _model_code(slug):
    c = slug.upper()
    return re.sub(r'^XF(\d)', r'XF-\1', c)   # xf58 -> XF-58, xf-504 -> XF-504, apex -> APEX

def barcode_label_svg(code):
    """Inline SVG: a printed-label tile with a Code 39 barcode + the model code."""
    seq = "*" + "".join(ch for ch in code.upper() if ch in _CODE39) + "*"
    N, W = 1.0, 2.6
    x = 0.0; bars = []
    for ch in seq:
        pat = _CODE39.get(ch)
        if not pat:
            continue
        for i, e in enumerate(pat):
            w = W if e == 'w' else N
            if i % 2 == 0:      # even elements are bars
                bars.append((x, w))
            x += w
        x += N                  # narrow inter-character gap
    total = x or 1.0
    TARGET, X0, BY, BH = 208.0, 56.0, 66.0, 60.0
    sc = TARGET / total
    rects = "".join('<rect x="%.2f" y="%d" width="%.2f" height="%d" fill="#101828"/>'
                    % (X0 + bx * sc, BY, max(bw * sc, 0.4), BH) for bx, bw in bars)
    return (
        '<svg class="bclbl" viewBox="0 0 320 200" preserveAspectRatio="xMidYMid meet" '
        'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="%s">'
        '<rect width="320" height="200" fill="#eef3fc"/>'
        '<rect x="34" y="34" width="252" height="132" rx="10" fill="#fff" stroke="#dbe3f1"/>'
        '<text x="60" y="54" font-family="ui-monospace,Menlo,Consolas,monospace" font-size="8" '
        'letter-spacing="2.5" fill="#9fb0cf">POLYONICS</text>'
        '%s'
        '<text x="160" y="150" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace" '
        'font-size="22" font-weight="700" letter-spacing="2" fill="#143C96">%s</text>'
        '</svg>') % (esc(code), rects, esc(code))

# Series/hub pages that are not a single material — kept in the catalog but the
# environment Solution hubs are excluded (they already have "browse by environment").
EXCLUDE = set(gp.SOLUTION_SLUGS)

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
    ("flame",   {"en": "Flame-Retardant", "zh": "阻燃", "vi": "Chống cháy", "th": "หน่วงไฟ"}, ["flame-retardant", "flame retardant", "ul94", "ul 94", "vtm-0", "halogen-free", "阻燃", "无卤"]),
    ("cryo",    {"en": "Cryogenic / Low-Temp", "zh": "低温冻存", "vi": "Đông lạnh", "th": "อุณหภูมิต่ำ"}, ["cryo", "-196", "-80", "−196", "−80", "liquid nitrogen", "液氮", "低温", "冻存", "cold chain", "cold-chain"]),
    ("hot",     {"en": "High-Temp", "zh": "高温", "vi": "Nhiệt độ cao", "th": "อุณหภูมิสูง"}, ["reflow", "high-temp", "high-temperature", "heat-treatment", "heat treatment", "wave solder", "hot steel", "hot billet", "hot-application", "annealing", "耐高温", "高温工艺", "回流焊", "热处理"]),
    ("chem",    {"en": "Chemical-Resistant", "zh": "耐化学", "vi": "Kháng hóa chất", "th": "ทนสารเคมี"}, ["chemical-resistant", "chemical resistant", "solvent-resistant", "solvent resistant", "acid and alkali", "耐化学", "耐溶剂"]),
    ("steril",  {"en": "Sterilization", "zh": "灭菌", "vi": "Tiệt trùng", "th": "การฆ่าเชื้อ"}, ["sterilization", "sterilize", "autoclave", "gamma", "灭菌", "高压灭菌"]),
    ("laser",   {"en": "Laser-Markable", "zh": "激光可刻", "vi": "Khắc laser", "th": "แกะสลักด้วยเลเซอร์"}, ["laser-mark", "laser mark", "laser-etch", "laser etch", "laser engrav", "激光刻", "激光打"]),
    ("blood",   {"en": "Blood Bag", "zh": "血袋", "vi": "Túi máu", "th": "ถุงเลือด"}, ["blood bag", "blood-bag", "血袋"]),
    ("vin",     {"en": "Automotive VIN", "zh": "汽车 VIN", "vi": "VIN ô tô", "th": "VIN ยานยนต์"}, ["vin code", "vin label", "vin plate", "vin identif", "车架号", "汽车 vin"]),
    ("cablew",  {"en": "Wire & Cable ID", "zh": "线缆标识", "vi": "Nhận diện cáp", "th": "ระบุสายเคเบิล"}, ["wire", "cable", "harness", "线缆", "束线", "电缆"]),
    ("outdoor", {"en": "Outdoor / Weatherable", "zh": "户外耐候", "vi": "Ngoài trời", "th": "กลางแจ้ง"}, ["outdoor", "weatherable", "weather resist", "户外", "耐候"]),
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
           "fac": {"industry": "Industry", "brand": "Brand", "application": "Application", "facestock": "Facestock", "temp": "Temperature"}},
    "zh": {"title": "查找标签материал".replace("материал", "材料"), "lede": "按料号、材料或应用搜索 —— 或使用下方维度筛选。",
           "search": "搜索料号、材料或应用……（如 E-4812、聚酰亚胺、血袋）",
           "reset": "清除全部", "results": "款材料", "none": "没有符合条件的材料。",
           "view": "查看产品 →", "filters": "筛选", "home": "首页", "products": "产品",
           "fac": {"industry": "行业", "brand": "品牌", "application": "应用", "facestock": "面材", "temp": "温度"}},
    "vi": {"title": "Tìm vật liệu nhãn", "lede": "Tìm theo mã sản phẩm, vật liệu hoặc ứng dụng — hoặc lọc theo các tiêu chí bên dưới.",
           "search": "Tìm mã, vật liệu hoặc ứng dụng… (vd: E-4812, polyimide, túi máu)",
           "reset": "Xóa tất cả", "results": "vật liệu", "none": "Không có vật liệu phù hợp.",
           "view": "Xem sản phẩm →", "filters": "Bộ lọc", "home": "Trang chủ", "products": "Sản phẩm",
           "fac": {"industry": "Ngành", "brand": "Thương hiệu", "application": "Ứng dụng", "facestock": "Vật liệu mặt", "temp": "Nhiệt độ"}},
    "th": {"title": "ค้นหาวัสดุฉลาก", "lede": "ค้นหาด้วยรหัสสินค้า วัสดุ หรือการใช้งาน — หรือกรองตามหมวดด้านล่าง",
           "search": "ค้นหารหัส วัสดุ หรือการใช้งาน… (เช่น E-4812, โพลีอิไมด์, ถุงเลือด)",
           "reset": "ล้างทั้งหมด", "results": "วัสดุ", "none": "ไม่มีวัสดุที่ตรงกับตัวกรอง",
           "view": "ดูสินค้า →", "filters": "ตัวกรอง", "home": "หน้าแรก", "products": "ผลิตภัณฑ์",
           "fac": {"industry": "อุตสาหกรรม", "brand": "แบรนด์", "application": "การใช้งาน", "facestock": "วัสดุหน้า", "temp": "อุณหภูมิ"}},
}
TEMP_BANDS = {
    "cryo":  {"en": "Cryogenic (≤ −40°C)", "zh": "低温 (≤ −40°C)", "vi": "Đông lạnh (≤ −40°C)", "th": "อุณหภูมิต่ำ (≤ −40°C)"},
    "high":  {"en": "High-Temp (≥ 200°C)", "zh": "高温 (≥ 200°C)", "vi": "Nhiệt cao (≥ 200°C)", "th": "อุณหภูมิสูง (≥ 200°C)"},
    "std":   {"en": "Standard (−40 to 200°C)", "zh": "常规 (−40 至 200°C)", "vi": "Tiêu chuẩn (−40 đến 200°C)", "th": "มาตรฐาน (−40 ถึง 200°C)"},
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


def build_record(d):
    slug = d["slug"]
    blob = _blob(d)
    ind = gp.product_industry(d, slug)
    brand = gp.product_brand(d, slug)  # 'polyonics' | 'etia'
    apps = [key for key, lab, kws in APP_CATS if any(k in blob for k in kws)]
    facestocks = [fs for fs, kws in FACESTOCKS if any(k in blob for k in kws)]
    tmin, tmax = _temps(blob)
    temps = []
    if tmin is not None and tmin <= -60: temps.append("cryo")   # genuinely deep-cold only
    if tmax is not None and tmax >= 200: temps.append("high")
    if not temps: temps.append("std")
    explicit = d.get("facets", {}) or {}
    return {
        "slug": slug, "url": "/products/item/%s/" % slug,
        "title": d.get("title", {}), "tagline": d.get("tagline", {}),
        "industry": ind, "brand": brand, "apps": apps, "facestocks": facestocks, "temps": temps,
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
    temp_opts = collect(lambda r: r["temps"], None)

    def chk(group, value, label):
        return ('<label class="fchk"><input type="checkbox" data-g="%s" data-v="%s" onchange="cf()"> %s</label>'
                % (group, esc(value), esc(label)))

    fpanels = ""
    if ind_opts:
        fpanels += '<div class="fgrp"><h4>%s</h4>%s</div>' % (esc(ui["fac"]["industry"]),
            "".join(chk("industry", k, L(IND_NAME[k])) for k in ["pcb", "auto", "cable", "steel", "medical", "outdoor"] if k in ind_opts))
    if len(brand_opts) > 1:
        fpanels += '<div class="fgrp"><h4>%s</h4>%s</div>' % (esc(ui["fac"]["brand"]),
            "".join(chk("brand", b, L(BRAND[b])) for b in brand_opts))
    if app_opts:
        applab = {key: lab for key, lab, kws in APP_CATS}
        fpanels += '<div class="fgrp"><h4>%s</h4>%s</div>' % (esc(ui["fac"]["application"]),
            "".join(chk("app", key, L(applab[key])) for key, lab, kws in APP_CATS if key in app_opts))
    if fs_opts:
        fpanels += '<div class="fgrp"><h4>%s</h4>%s</div>' % (esc(ui["fac"]["facestock"]),
            "".join(chk("fs", f, L(json.loads(f))) for f in fs_opts))
    if temp_opts:
        fpanels += '<div class="fgrp"><h4>%s</h4>%s</div>' % (esc(ui["fac"]["temp"]),
            "".join(chk("temp", t, L(TEMP_BANDS[t])) for t in ["cryo", "std", "high"] if t in temp_opts))

    # ---- cards ----
    cards = ""
    for r in sorted(records, key=lambda x: L(x["title"]).lower()):
        chips = ""
        if r["industry"]:
            chips += '<span class="cchip ind">%s</span>' % esc(L(IND_NAME[r["industry"]]))
        for f in r["facestocks"][:1]:
            chips += '<span class="cchip mat">%s</span>' % esc(L(f))
        data = {
            "industry": [r["industry"]] if r["industry"] else [],
            "brand": [r["brand"]], "app": r["apps"],
            "fs": [json.dumps(f, ensure_ascii=False) for f in r["facestocks"]],
            "temp": r["temps"], "q": r["blob"],
        }
        cards += ('<a class="pcell" href="%s" data-f="%s"><div class="pcell-t">%s</div>'
                  '<div class="pcell-s">%s</div><div class="pcell-chips">%s</div>'
                  '<span class="pcell-go">%s</span></a>') % (
            hp.Lx(lang, r["url"]),
            esc(json.dumps(data, ensure_ascii=False)),
            esc(L(r["title"])), esc(L(r["tagline"])), chips, esc(ui["view"]))

    CSS = """<style>
.cwrap{max-width:1180px;margin:0 auto;padding:26px 22px 48px}
.chead h1{font-size:32px;color:#143C96;font-family:var(--sans);font-weight:800;margin:0 0 6px}
.chead p{color:#51607e;font-size:15.5px;margin:0 0 18px;max-width:60ch}
.csearch{position:relative;margin:0 0 20px}
.csearch input{width:100%;box-sizing:border-box;font-size:16px;padding:14px 16px 14px 44px;border:1.5px solid #cdd8ec;border-radius:12px;background:#fff url('data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'20\\' height=\\'20\\' viewBox=\\'0 0 24 24\\' fill=\\'none\\' stroke=\\'%235a6884\\' stroke-width=\\'2\\'><circle cx=\\'11\\' cy=\\'11\\' r=\\'7\\'/><path d=\\'M21 21l-4-4\\'/></svg>') no-repeat 14px center}
.csearch input:focus{outline:none;border-color:#1A56DB;box-shadow:0 0 0 3px rgba(26,86,219,.14)}
.clayout{display:grid;grid-template-columns:236px 1fr;gap:26px;align-items:start}
.cfilters{position:sticky;top:86px}
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
.pcell-go{font-size:12px;font-weight:800;color:#41A62A;margin-top:2px}
.cnone{padding:40px 8px;color:#5a6884;font-size:15px}
.fmob{display:none}
@media(max-width:860px){.clayout{grid-template-columns:1fr}.cfilters{position:static}
  .fmob{display:block;width:100%;padding:11px 14px;border:1.5px solid #cdd8ec;border-radius:10px;background:#fff;font-weight:800;color:#143C96;cursor:pointer;margin-bottom:12px}
  .cfilters .fbody{display:none}.cfilters.open .fbody{display:block}}
</style>"""

    body = CSS + (
        '<div class="cwrap"><div class="chead"><h1>%s</h1><p>%s</p></div>'
        '<div class="csearch"><input id="cq" type="search" placeholder="%s" oninput="cf()" autocomplete="off"></div>'
        '<button class="fmob" onclick="this.nextElementSibling.classList.toggle(\'open\')">%s</button>'
        '<div class="clayout"><aside class="cfilters"><div class="fbody">'
        '<div class="fhd"><h3>%s</h3><button class="freset" onclick="cReset()">%s</button></div>%s</div></aside>'
        '<div class="cresults"><p class="ccount"><span id="ccount">0</span> %s</p>'
        '<div class="pgrid" id="pgrid">%s</div><p class="cnone" id="cnone" style="display:none">%s</p>'
        '</div></div></div>') % (
        esc(ui["title"]), esc(ui["lede"]), esc(ui["search"]), esc(ui["filters"]),
        esc(ui["filters"]), esc(ui["reset"]), fpanels, esc(ui["results"]), cards, esc(ui["none"]))

    body += """<script>
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
    content = hp.page(lang, PATH, ui["title"] + " | ETIA", ui["lede"], ui["title"], "", body, crumb,
                      active="products", trust=False, langs=hp.NAV_PILLAR_LANGS)
    hp.write(lang, PATH, content)
    if lang == "en":
        hp.track(PATH, "core")


# ---- Brand page (e.g. Polyonics): one card per product, scanned from the DB ----
# E-commerce layout: the Polyonics brand page groups products into four series
# (PCB Polyimide · ESD-Safe · Flame-Retardant · Cable & Wire), each a browsable
# aisle of product cards with a "compare specs" link to its selector table.
# Each product is assigned to exactly one aisle (most-specific series wins).
POLY_SERIES = [
    {"key": "pcb", "table": "pcb-labels",
     "name": {"en": "PCB Polyimide Labels", "zh": "PCB 聚酰亚胺标签", "vi": "Nhãn Polyimide PCB", "th": "ฉลากโพลีอิไมด์ PCB"}},
    {"key": "esd", "table": "esd-safe",
     "name": {"en": "ESD-Safe Series", "zh": "防静电系列", "vi": "Dòng ESD-Safe", "th": "ซีรีส์ ESD-Safe"}},
    {"key": "fr", "table": "flame-retardant",
     "name": {"en": "Flame-Retardant Series", "zh": "阻燃系列", "vi": "Dòng chống cháy", "th": "ซีรีส์หน่วงไฟ"}},
    {"key": "cable", "table": "wire-cable",
     "name": {"en": "Cable & Wire Marking", "zh": "线缆标识系列", "vi": "Đánh dấu dây & cáp", "th": "ซีรีส์ทำเครื่องหมายสายไฟ"}},
]
POLY_COMPARE = {"en": "Compare specs →", "zh": "对比规格 →", "vi": "So sánh thông số →", "th": "เปรียบเทียบสเปก →"}
_SERIES_FR = {"xf-603", "xf-611"}
_SERIES_ESD = {"xf-781", "xf-782", "xf-784", "xf-446", "xf78"}
_SERIES_CABLE = {"xf-300", "xf-302"}
def poly_series_key(slug):
    if slug in _SERIES_FR: return "fr"
    if slug in _SERIES_ESD: return "esd"
    if slug in _SERIES_CABLE: return "cable"
    return "pcb"

BRAND_PATH = {"polyonics": "/products/polyonics/"}
BRAND_UI = {
    "en": {"eyebrow": "By Brand", "view": "View product →", "home": "Home", "products": "Products",
           "empty": "Products coming soon.",
           "lede": {"polyonics": "Genuine imported Polyonics polyimide label materials — stocked and application-supported by ETIA for reflow, cleaning and ESD-controlled electronics processes."}},
    "zh": {"eyebrow": "按品牌", "view": "查看产品 →", "home": "首页", "products": "产品",
           "empty": "产品即将上线。",
           "lede": {"polyonics": "Polyonics 原装进口聚酰亚胺标签材料 —— 由 ETIA 备货并提供应用支持，适配回流焊、清洗与防静电电子制程。"}},
    "vi": {"eyebrow": "Theo thương hiệu", "view": "Xem sản phẩm →", "home": "Trang chủ", "products": "Sản phẩm",
           "empty": "Sản phẩm sắp ra mắt.",
           "lede": {"polyonics": "Vật liệu nhãn polyimide Polyonics nhập khẩu chính hãng — được ETIA lưu kho và hỗ trợ ứng dụng cho reflow, làm sạch và quy trình điện tử kiểm soát ESD."}},
    "th": {"eyebrow": "ตามแบรนด์", "view": "ดูสินค้า →", "home": "หน้าแรก", "products": "ผลิตภัณฑ์",
           "empty": "สินค้าเร็วๆ นี้",
           "lede": {"polyonics": "วัสดุฉลากโพลีอิไมด์ Polyonics นำเข้าแท้ — สต๊อกและสนับสนุนการใช้งานโดย ETIA สำหรับรีโฟลว์ การล้าง และกระบวนการอิเล็กทรอนิกส์ที่ควบคุม ESD"}},
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
POLY_OVERVIEW = {
    "en": [
        "Polyonics is a U.S.-based specialty coatings manufacturer that engineers high-performance polyimide label materials for PCB and electronic component identification. Its materials are designed to withstand reflow temperatures up to 300°C, wave soldering, aggressive fluxes, and demanding cleaning processes.",
        "As an authorized Polyonics distributor, ETIA provides genuine materials, local supply, sample support, and application-based material selection for OEMs, contract manufacturers, label converters, and printers.",
    ],
    "zh": [
        "Polyonics 是美国特种涂层材料制造商，专注于研发适用于 PCB 与电子元器件标识的高性能聚酰亚胺标签材料。其产品可耐受高达 300°C 的回流焊、波峰焊、活性助焊剂及严苛清洗工艺。",
        "ETIA 是 Polyonics 授权经销商，为 OEM、电子制造企业、模切厂及标签印刷厂提供正品材料、本地供货、样品支持与应用选型服务。",
    ],
    "vi": [
        "Polyonics là nhà sản xuất lớp phủ đặc chủng của Mỹ, chuyên phát triển vật liệu nhãn polyimide hiệu năng cao cho nhận diện PCB và linh kiện điện tử. Vật liệu của hãng được thiết kế để chịu nhiệt độ reflow lên đến 300°C, hàn sóng, flux hoạt tính mạnh và các quy trình làm sạch khắc nghiệt.",
        "Là nhà phân phối được ủy quyền của Polyonics, ETIA cung cấp vật liệu chính hãng, nguồn cung tại chỗ, hỗ trợ mẫu và tư vấn chọn vật liệu theo ứng dụng cho các OEM, nhà sản xuất hợp đồng (EMS), nhà gia công nhãn và nhà in.",
    ],
    "th": [
        "Polyonics เป็นผู้ผลิตสารเคลือบเฉพาะทางจากสหรัฐฯ ที่พัฒนาวัสดุฉลากโพลีอิไมด์ประสิทธิภาพสูงสำหรับการระบุ PCB และชิ้นส่วนอิเล็กทรอนิกส์ วัสดุของบริษัทออกแบบมาให้ทนอุณหภูมิรีโฟลว์สูงถึง 300°C การบัดกรีแบบเวฟ ฟลักซ์ที่มีฤทธิ์รุนแรง และกระบวนการทำความสะอาดที่เข้มงวด",
        "ในฐานะตัวแทนจำหน่ายที่ได้รับอนุญาตของ Polyonics ETIA จัดหาวัสดุของแท้ การจัดหาในพื้นที่ การสนับสนุนตัวอย่าง และการเลือกวัสดุตามการใช้งาน ให้แก่ OEM ผู้ผลิตรับจ้าง ผู้แปรรูปฉลาก และโรงพิมพ์",
    ],
}
BRAND_CSS = """<style>
.bwrap{max-width:1120px;margin:0 auto;padding:34px 22px 54px}
.bover{color:#41506e;font-size:15.5px;line-height:1.7;max-width:80ch;margin:0 0 22px}
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
.bcard-img.lbl{background:#eef3fc}
.bcard-img.lbl svg.bclbl{width:100%;height:100%;display:block}
.bcard-img.ph span{color:#fff;font-family:var(--sans);font-weight:800;font-size:22px;letter-spacing:.02em;padding:0 16px;text-align:center}
.bcard-b{padding:16px 18px 18px;display:flex;flex-direction:column;gap:8px;flex:1}
.bcard-b h3{margin:0;font-size:17px;color:#143C96;font-weight:800;line-height:1.28}
.bcard-b p{margin:0;font-size:13.5px;color:#5a6884;line-height:1.5;flex:1}
.bchips{display:flex;flex-wrap:wrap;gap:6px}
.bchip{font-size:11px;font-weight:800;color:#2c7a1e;background:#e6f5e0;border-radius:999px;padding:3px 9px}
.bchip.t{color:#1A56DB;background:#eaf1ff}
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
            media = ('<div class="bcard-img"><img src="%s" alt="%s" loading="lazy" '
                     'onerror="var p=this.parentNode;p.classList.add(\'ph\');p.innerHTML=\'<span>%s</span>\'"></div>') % (
                esc(img), esc(L(r["title"])), esc(L(r["title"])))
        else:
            media = '<div class="bcard-img lbl">%s</div>' % barcode_label_svg(_model_code(r["slug"]))
        chips = ""
        for f in r["facestocks"][:1]:
            chips += '<span class="bchip">%s</span>' % esc(L(f))
        for t in r["temps"][:1]:
            chips += '<span class="bchip t">%s</span>' % esc(L(TEMP_BANDS[t]))
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
        overview = ('<div class="bsechd">%s</div>%s' %
                    (esc(POLY_OVERVIEW_LABEL.get(lang) or POLY_OVERVIEW_LABEL["en"]),
                     "".join('<p class="bover">%s</p>' % esc(p) for p in paras)))
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
    npoly = sum(1 for r in records if r["brand"] == "polyonics")
    ncat = sum(len(c["rows"]) for c in POLY_CATS)
    print("catalog: /products/find/ x4 langs —", len(records), "materials")
    print("brand page: /products/polyonics/ x4 langs —", npoly, "featured products +",
          len(POLY_CATS), "categories /", ncat, "catalogue rows")


if __name__ == "__main__":
    main()
