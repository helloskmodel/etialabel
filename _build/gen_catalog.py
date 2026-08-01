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
BRAND = {"Polyonics": {"en": "Polyonics", "zh": "Polyonics", "vi": "Polyonics", "th": "Polyonics"},
         "ETIA": {"en": "ETIA (in-house)", "zh": "ETIA 自研", "vi": "ETIA (tự sản xuất)", "th": "ETIA (ผลิตเอง)"}}


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
    brand = "Polyonics" if "polyonics" in blob else "ETIA"
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
  var q=(document.getElementById('cq').value||'').toLowerCase().trim();
  var terms=q.split(/\\s+/).filter(Boolean);
  var sel={};
  document.querySelectorAll('.cfilters input:checked').forEach(function(c){
    (sel[c.dataset.g]=sel[c.dataset.g]||[]).push(c.dataset.v);});
  var n=0;
  document.querySelectorAll('.pcell').forEach(function(el){
    var f=JSON.parse(el.getAttribute('data-f'));
    var ok=true;
    for(var g in sel){ if(!sel[g].some(function(v){return (f[g]||[]).indexOf(v)>=0;})){ok=false;break;} }
    if(ok && terms.length){ ok=terms.every(function(t){return f.q.indexOf(t)>=0;}); }
    el.style.display=ok?'':'none'; if(ok)n++;
  });
  document.getElementById('ccount').textContent=n;
  document.getElementById('cnone').style.display=n?'none':'block';
}
function cReset(){document.getElementById('cq').value='';
  document.querySelectorAll('.cfilters input:checked').forEach(function(c){c.checked=false;});cf();}
cf();
</script>"""

    crumb = [(ui["home"], "/"), (ui["products"], "/products/"), (ui["title"], PATH)]
    content = hp.page(lang, PATH, ui["title"] + " | ETIA", ui["lede"], ui["title"], "", body, crumb,
                      active="products", trust=False, langs=hp.NAV_PILLAR_LANGS)
    hp.write(lang, PATH, content)
    if lang == "en":
        hp.track(PATH, "core")


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
    print("catalog: /products/find/ x4 langs —", len(records), "materials")


if __name__ == "__main__":
    main()
