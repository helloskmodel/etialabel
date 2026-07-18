#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HEATPROOF™ Metals & Ceramics — 3 sector Application Landings (Steel / Aluminum /
Ceramics) + HEATPROOF product pages. Mirrors the Electronics/PCB methodology:
  Sector (Application Landing, FLEXcon case tabs) -> Product page.
Content: _build/data/heatproof_en.json (from the client HEATPROOF_Cases Excel).
Runs AFTER gen_ind_landing so it owns /industries/<sector>/. EN + ZH (ZH UI labels;
case/product body copy is EN pending client translation)."""
import os, json
import gen_heatproof as hp
from gen_heatproof import esc, L, page, write, LANGS

_HP = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "heatproof_en.json"), encoding="utf-8"))
CASES = {c["code"]: c for c in _HP["cases"]}
PRODUCTS = {p["slug"]: p for p in _HP["products"]}

BANNER = "https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com/A%E3%83%BBHERO%20banner%206%20%E7%BB%84/HP9001609.jpg"
def _t(lang, en, zh): return zh if lang == "zh" else en

def _svg(p): return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">%s</svg>' % p)
IC_PROC = _svg('<path d="M3 12h4l2-7 4 14 2-7h6"/>')
IC_CHAL = _svg('<path d="M12 3 2 20h20L12 3z"/><path d="M12 10v5M12 18h.01"/>')
IC_SOL  = _svg('<path d="M12 3 4 6.5v5c0 4.6 3.2 7.7 8 9.5 4.8-1.8 8-4.9 8-9.5v-5L12 3z"/><path d="m9 12 2 2 4-4"/>')
CHK = _svg('<path d="m5 12 4 4L19 7"/>')

# --- sector config: slug -> (en name, zh name, en H1, zh H1, en intro, zh intro, [case codes]) ---
SECTORS = {
 "steel": ("Steel", "钢铁",
   "Steel — Extreme Heat-Resistant Labels &amp; Tags", "钢铁 —— 极端耐高温标签与挂牌",
   "Heat-resistant identification across the steel process chain — continuous casting, hot rolling, pickling, annealing and forging heat treatment.",
   "覆盖钢铁全流程的耐高温标识 —— 连铸、热轧、酸洗、退火与锻件热处理。",
   ["S-1", "S-2", "S-3", "S-4", "S-5"]),
 "aluminum": ("Aluminum", "铝",
   "Aluminum — Heat-Resistant Labels &amp; Tags", "铝 —— 耐高温标签与挂牌",
   "Traceability across aluminum casting, homogenizing and heat treatment — direct hot labeling and reusable jig tags.",
   "覆盖铝铸造、均质化与热处理的可追溯 —— 热态直贴与可复用工装挂牌。",
   ["A-1", "A-2", "A-3"]),
 "ceramics": ("Ceramics", "陶瓷",
   "Ceramics — Extreme-Temperature Tags &amp; Fired-In Marks", "陶瓷 —— 极端高温挂牌与烧结标记",
   "Identification for extreme kiln firing — mechanically fixed tags and fired-in marks that survive 1000℃+ prolonged cycles.",
   "面向极端窑炉烧成的标识 —— 机械固定挂牌与烧结永久标记,耐受 1000℃+ 长时循环。",
   ["C-1", "C-2"]),
}
CASE_TAB = {
 "S-1": ("Hot Slab · 800℃", "热态板坯 · 800℃"), "S-2": ("Hot Coil · 550℃", "热态钢卷 · 550℃"),
 "S-3": ("Hot Billet · 750℃", "热态钢坯 · 750℃"), "S-4": ("Wire Pickling + Anneal", "线材酸洗 + 退火"),
 "S-5": ("Forged Heat-Treatment", "锻件热处理"), "A-1": ("Aluminum Sow · 550℃", "铝锭 · 550℃"),
 "A-2": ("Billet Homogenizing", "铝坯均质化"), "A-3": ("Heat-Treat Jigs", "热处理工装"),
 "C-1": ("Kiln Jigs · 1000℃", "窑炉工装 · 1000℃"), "C-2": ("Crucible", "坩埚"),
}
CASE_PROD = {
 "S-1": ("HP-700T", "hp-700t"), "S-2": ("HP-600", "hp-600"), "S-3": ("HP-700T", "hp-700t"),
 "S-4": ("HP-M83", "hp-m83"), "S-5": ("HP-L90", "hp-l90"), "A-1": ("HP-600", "hp-600"),
 "A-2": ("HP-350N / 380N+ / 360", "hp-350n"), "A-3": ("HP-T42 + HP-CBR Tag", "hp-t42-hp-cbr-tag"),
 "C-1": ("HP-CBR CX2 / HB", "hp-cbr-cx2"), "C-2": ("HP-CBR CX2 / HB", "hp-cbr-cx2"),
}
PROD_URL = "/products/heatproof/%s/"

CSS = """<style>
.hphero{background:linear-gradient(115deg,rgba(10,30,80,.90),rgba(20,60,150,.50) 55%,rgba(26,86,219,.10)),url('__BANNER__') center/cover no-repeat #0e2a63;color:#fff}
.hphero .wrap{padding:56px 24px}.hphero .eyebrow{color:#9dbcff}
.hphero h1{color:#fff;font-size:38px;font-weight:800;line-height:1.14;margin:6px 0 12px;max-width:20em}
.hphero p{color:#eef3ff;font-size:16px;line-height:1.6;max-width:56em}
.hpbadge{display:inline-block;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.3);color:#fff;font-weight:700;font-size:12.5px;border-radius:20px;padding:5px 13px;margin:0 7px 8px 0}
.plsub{color:var(--mut);font-size:15px;margin:-6px 0 16px;max-width:66em}
.ovbody{max-width:66em}.ovbody p{font-size:17px;line-height:1.7;color:var(--ink)}
.hpmod{margin-top:8px}
.hptabsrow{display:flex;align-items:center;gap:6px;border-bottom:1px solid var(--line)}
.hptabs{display:flex;gap:24px;overflow-x:auto;scrollbar-width:none;flex:1}.hptabs::-webkit-scrollbar{display:none}
.hptab{white-space:nowrap;background:none;border:none;padding:12px 0;font-size:15px;font-weight:700;color:var(--mut);cursor:pointer;border-bottom:3px solid transparent;margin-bottom:-1px}
.hptab.on{color:var(--blue-deep);border-bottom-color:var(--blue)}
.hparrow{background:none;border:none;font-size:20px;color:var(--mut);cursor:pointer;padding:4px 6px}
.hppanel{padding-top:24px}
.hp3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}
.hpbox{border:1px solid var(--line);border-radius:12px;padding:18px 20px;background:#fff}
.hpbox .h{display:flex;align-items:center;gap:12px;margin-bottom:8px}
.hpbox .h .i{width:30px;height:30px;flex:0 0 auto}.hpbox .h .i svg{width:30px;height:30px}
.hpbox .h .e{font-size:12px;font-weight:800;letter-spacing:.04em;text-transform:uppercase}
.hpbox p{font-size:14px;color:var(--ink);line-height:1.55}
.plw{margin-top:26px}.plh{font-size:12px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--mut);margin-bottom:12px}
.plcard{display:inline-flex;flex-direction:column;border:1px solid var(--line);border-radius:12px;padding:16px 18px;background:#fff;text-decoration:none;transition:.16s;min-width:260px}
.plcard:hover{border-color:var(--blue);box-shadow:0 12px 30px rgba(20,40,90,.12);transform:translateY(-3px)}
.plcard .t{font-weight:800;color:var(--blue-deep);font-size:16px}
.plcard .go{font-size:12.5px;font-weight:700;color:var(--blue);margin-top:8px}
.flist{display:grid;grid-template-columns:1fr 1fr;gap:2px 44px}
.frow{display:flex;gap:14px;align-items:flex-start;padding:13px 0;border-bottom:1px solid var(--line)}
.frow .c{flex:0 0 auto;width:22px;height:22px;color:var(--green-d)}.frow .c svg{width:22px;height:22px}
.frow p{font-size:14.5px;color:var(--ink);line-height:1.5}
.spectbl{width:100%;border-collapse:collapse;font-size:15px;max-width:820px}
.spectbl th{text-align:left;width:230px;background:#f4f7fd;color:var(--blue-deep);font-weight:800;padding:13px 16px;vertical-align:top}
.spectbl td{padding:13px 16px;border-bottom:1px solid var(--line);color:var(--ink)}
@media(max-width:820px){.hp3,.flist{grid-template-columns:1fr}}
</style>""".replace("__BANNER__", BANNER)

UI = {"process": ("Process", "工艺"), "challenge": ("Challenge", "挑战"),
      "solution": ("Recommended Solution", "推荐方案"), "lines": ("Product Lines", "产品系列"),
      "browse": ("Browse by Process", "按工艺浏览"), "view": ("View product →", "查看产品 →"),
      "overview": ("Overview", "概述"), "features": ("Features", "特性"),
      "benefits": ("Benefits", "收益"), "spec": ("Specification", "规格"),
      "application": ("Application", "应用"), "talk": ("Talk to a Specialist", "咨询专家"),
      "sample": ("FREE SAMPLE", "免费样品"), "eyebrow": ("HEATPROOF™ · Extreme Temperature Identification Solutions", "HEATPROOF™ · 极端温度标识解决方案"),
      "subhead": ("Extreme Heat-Resistant Labels and Tags", "极端耐高温标签与挂牌")}

def build_sector(lang, key):
    zh = (lang == "zh")
    def H(e, z): return esc(_t(lang, e, z))
    def U(k): return H(*UI[k])
    name_en, name_zh, h1e, h1z, ine, inz, codes = SECTORS[key]
    contact = L(lang, "/contact/")
    hero = ('<section class="hphero"><div class="wrap"><div class="eyebrow">%s</div>'
            '<h1>%s</h1><p>%s</p><div style="margin-top:20px"><a class="btn pri" href="%s">%s</a></div>'
            '</div></section>') % (U("eyebrow"), _t(lang, h1e, h1z), H(*UI["subhead"]), contact, U("talk"))
    overview = '<section class="blk"><div class="wrap"><div class="ovbody"><p>%s</p></div></div></section>' % _t(lang, ine, inz)
    tabs = ""; panels = ""
    for i, code in enumerate(codes):
        c = CASES[code]
        tabs += '<button class="hptab%s" onclick="hpTab(this,%d)">%s</button>' % (" on" if i == 0 else "", i, H(*CASE_TAB[code]))
        def box(ic, lbl, col, txt, tint=False):
            return ('<div class="hpbox"%s><div class="h"><span class="i" style="color:%s">%s</span>'
                    '<span class="e" style="color:%s">%s</span></div><p>%s</p></div>') % (
                (' style="background:#f4f9f2"' if tint else ''), col, ic, col, lbl, esc(txt))
        cols = '<div class="hp3">%s%s%s</div>' % (
            box(IC_PROC, U("process"), "var(--blue)", c["process"]),
            box(IC_CHAL, U("challenge"), "#c2621f", c["challenge"]),
            box(IC_SOL, U("solution"), "var(--green-d)", c["solution"], tint=True))
        pn, ps = CASE_PROD[code]
        card = ('<a class="plcard" href="%s"><div class="t">%s</div><div class="go">%s</div></a>') % (
            L(lang, PROD_URL % ps), esc(pn), U("view"))
        panels += ('<div class="hppanel" data-i="%d" style="display:%s">%s'
                   '<div class="plw"><div class="plh">%s</div>%s</div></div>') % (
            i, "block" if i == 0 else "none", cols, U("lines"), card)
    js = ("<script>function hpTab(b,i){var m=b.closest('.hpmod');"
          "m.querySelectorAll('.hptab').forEach(function(x,j){x.classList.toggle('on',j===i);});"
          "m.querySelectorAll('.hppanel').forEach(function(p){p.style.display=(+p.getAttribute('data-i')===i)?'block':'none';});}"
          "function hpScroll(b,d){b.closest('.hptabsrow').querySelector('.hptabs').scrollBy({left:d*240,behavior:'smooth'});}</script>")
    mod = ('<section class="blk"><div class="wrap"><h2>%s</h2><div class="hpmod">'
           '<div class="hptabsrow"><button class="hparrow" onclick="hpScroll(this,-1)">&lsaquo;</button>'
           '<div class="hptabs">%s</div><button class="hparrow" onclick="hpScroll(this,1)">&rsaquo;</button></div>'
           '%s</div></div></section>%s') % (U("browse"), tabs, panels, js)
    body = CSS + overview + mod + ('<div class="wrap">%s</div>' % hp.cta2(lang, "applications"))
    path = "/industries/%s/" % key
    crumb = [("Home" if not zh else "首页", "/"), ("Industries" if not zh else "行业", "/industries/"),
             (name_en if not zh else name_zh, path)]
    write(lang, path, page(lang, path,
        _t(lang, "%s Heat-Resistant Labels & Tags — HEATPROOF™ | ETIA" % name_en,
                 "%s 耐高温标签与挂牌 —— HEATPROOF™ | ETIA" % name_zh),
        _t(lang, "HEATPROOF™ heat-resistant labels and tags for the %s industry — direct hot application, heat treatment and durable tags across the process chain." % name_en.lower(),
                 "面向%s行业的 HEATPROOF™ 耐高温标签与挂牌 —— 热态直贴、热处理与耐用挂牌,覆盖全流程。" % name_zh),
        _t(lang, h1e.replace("&amp;", "&"), h1z), "", body, crumb, active="", hero=hero))
    if lang == "en": hp.track(path, "industries")

def build_product(lang, slug):
    zh = (lang == "zh")
    def H(e, z): return esc(_t(lang, e, z))
    def U(k): return H(*UI[k])
    p = PRODUCTS[slug]
    contact = L(lang, "/contact/")
    hero = ('<section class="hphero"><div class="wrap"><div class="eyebrow">%s</div>'
            '<h1>%s</h1><p>%s</p><div style="margin-top:18px"><a class="btn pri" href="%s">%s</a> '
            '<a class="btn on-dark" href="%s">%s</a></div></div></section>') % (
        H("HEATPROOF™ · PRODUCT", "HEATPROOF™ · 产品"), esc(p["name"]), H(*UI["subhead"]),
        L(lang, "/contact/?product=%s&type=sample" % p["name"].split()[0]), U("sample"), contact, U("talk"))
    sec = lambda h, inner, bg="": '<section class="blk"%s><div class="wrap"><h2>%s</h2>%s</div></section>' % (
        (' style="background:#f4f7fd"' if bg else ''), h, inner)
    ov = sec(U("overview"), '<p class="plsub" style="font-size:16px;color:var(--ink)">%s</p>' % esc(p["overview"]))
    def flist(items): return '<div class="flist">%s</div>' % "".join(
        '<div class="frow"><div class="c">%s</div><p>%s</p></div>' % (CHK, esc(x)) for x in items)
    feat = sec(U("features"), flist(p["features"]), bg=1) if p["features"] else ""
    ben = sec(U("benefits"), flist(p["benefits"])) if p["benefits"] else ""
    # spec: split "k: v"
    srows = ""
    for s in p["spec"]:
        if ":" in s:
            k, v = s.split(":", 1); srows += '<tr><th>%s</th><td>%s</td></tr>' % (esc(k.strip()), esc(v.strip()))
        else:
            srows += '<tr><th></th><td>%s</td></tr>' % esc(s)
    spec = sec(U("spec"), '<div class="ptable-wrap" style="overflow-x:auto"><table class="spectbl"><tbody>%s</tbody></table></div>' % srows, bg=1) if p["spec"] else ""
    app = sec(U("application"), '<p class="plsub" style="font-size:15.5px;color:var(--ink);line-height:1.7">%s</p>' % esc(p["application"])) if p["application"] else ""
    body = CSS + ov + feat + ben + spec + app + ('<div class="wrap">%s</div>' % hp.cta2(lang, "product-detail"))
    path = PROD_URL % slug
    crumb = [("Home" if not zh else "首页", "/"), ("Products" if not zh else "产品", "/products/"),
             ("HEATPROOF™", "/products/heatproof/"), (p["name"], path)]
    write(lang, path, page(lang, path,
        _t(lang, "%s — HEATPROOF™ Heat-Resistant Label | ETIA" % p["name"], "%s —— HEATPROOF™ 耐高温标签 | ETIA" % p["name"]),
        (p["overview"][:150]),
        p["name"], "", body, crumb, active="products", hero=hero))
    if lang == "en": hp.track(path, "products")

def build_hub(lang):
    zh = (lang == "zh")
    def H(e, z): return esc(_t(lang, e, z))
    contact = L(lang, "/contact/")
    hero = ('<section class="hphero"><div class="wrap"><div class="eyebrow">%s</div>'
            '<h1>%s</h1><p>%s</p><div style="margin-top:20px"><a class="btn pri" href="%s">%s</a></div>'
            '</div></section>') % (H(*UI["eyebrow"]),
        H("HEATPROOF™ Heat-Resistant Labels & Tags", "HEATPROOF™ 耐高温标签与挂牌"),
        H("Direct hot application labels, heat-treatment labels and durable tags for steel, aluminum and ceramics — from ambient to 1000℃+.",
          "面向钢铁、铝与陶瓷的热态直贴标签、热处理标签与耐用挂牌 —— 从常温到 1000℃ 以上。"), contact, H(*UI["talk"]))
    cards = "".join('<a class="plcard" style="min-width:0;display:flex" href="%s"><div class="t">%s</div>'
                    '<p style="font-size:12.5px;color:var(--mut);line-height:1.5;margin:6px 0 8px">%s</p>'
                    '<div class="go">%s</div></a>' % (
        L(lang, PROD_URL % s), esc(PRODUCTS[s]["name"]), esc((PRODUCTS[s]["overview"] or "")[:110]), H(*UI["view"]))
        for s in PRODUCTS)
    grid = ('<section class="blk"><div class="wrap"><h2>%s</h2>'
            '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px">%s</div>'
            '</div></section>') % (H("Product Range", "产品系列"), cards)
    body = CSS + grid + ('<div class="wrap">%s</div>' % hp.cta2(lang, "products"))
    path = "/products/heatproof/"
    crumb = [("Home" if not zh else "首页", "/"), ("Products" if not zh else "产品", "/products/"),
             ("HEATPROOF™", path)]
    write(lang, path, page(lang, path,
        _t(lang, "HEATPROOF™ Heat-Resistant Labels & Tags | ETIA", "HEATPROOF™ 耐高温标签与挂牌 | ETIA"),
        _t(lang, "HEATPROOF™ heat-resistant labels and tags for steel, aluminum and ceramics — direct hot application, heat treatment and durable tags from ambient to 1000℃+.",
                 "面向钢铁、铝与陶瓷的 HEATPROOF™ 耐高温标签与挂牌 —— 热态直贴、热处理与耐用挂牌,从常温到 1000℃ 以上。"),
        "HEATPROOF™", "", body, crumb, active="products", hero=hero))
    if lang == "en": hp.track(path, "products")

URLS = []
def main():
    for lang in LANGS:
        build_hub(lang)
        for key in SECTORS:
            build_sector(lang, key)
        for slug in PRODUCTS:
            build_product(lang, slug)
    URLS.extend(["/products/heatproof/"] + ["/industries/%s/" % k for k in SECTORS] + [PROD_URL % s for s in PRODUCTS])

if __name__ == "__main__":
    main()
