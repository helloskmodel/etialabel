#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Automotive Label Solutions — application sector landing at
/industries/automotive-label-materials/. 19 flat applications (no Level-1 layering)
shown as FLEXcon tabs; each tab has a single Introduction box + product cards below.
Product detail landing pages are future work. Content: _build/data/automotive_apps.json.
Runs AFTER gen_ind_landing so it owns /industries/automotive-label-materials/."""
import os, json
from urllib.parse import quote
import gen_heatproof as hp
from gen_heatproof import esc, L, page, write, LANGS

_D = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "automotive_apps.json"), encoding="utf-8"))
APPS = _D["apps"]
BANNER = _D["banner"]
PATH = "/industries/automotive-label-materials/"

def _t(lang, en, zh): return zh if lang == "zh" else en

# Shared property vocabulary — same terms as the "By Environment" / "By Feature" nav
# axes, so translations are authored once and reused across the whole site.
PROP_ZH = {
 "Abrasion-Resistant": "耐磨", "Chemical-Resistant": "耐化学", "Corrosion-Resistant": "耐腐蚀",
 "Heat-Resistant": "耐热", "High-Temperature-Resistant": "耐高温", "Humidity-Resistant": "耐潮湿",
 "Oil-Resistant": "耐油污", "Temperature-Resistant": "耐温变", "UV-Resistant": "耐紫外",
 "Water-Resistant": "耐水", "Weather-Resistant": "耐候", "Laser-Markable": "激光打标",
 "Tamper-Evident": "防拆", "Flexible": "柔性",
}
# each property (Solution) paired with the challenge (stressor) it answers — one
# controlled, corresponding vocabulary so Challenge and Solution chips always match.
PROP_CHALLENGE = {
 "Heat-Resistant": ("High Temperature", "高温"), "High-Temperature-Resistant": ("High Temperature", "高温"),
 "Chemical-Resistant": ("Chemicals", "化学品"), "Oil-Resistant": ("Oil / Fluids", "油污"),
 "Humidity-Resistant": ("Moisture", "潮湿"), "UV-Resistant": ("UV Exposure", "紫外线"),
 "Weather-Resistant": ("Weather / Outdoor", "户外候变"), "Abrasion-Resistant": ("Abrasion", "磨损"),
 "Water-Resistant": ("Water", "水"), "Corrosion-Resistant": ("Corrosion", "腐蚀"),
 "Temperature-Resistant": ("Temperature Cycling", "温度变化"), "Tamper-Evident": ("Tamper Risk", "防拆需求"),
 "Laser-Markable": ("Permanent Marking", "永久标识"), "Flexible": ("Flexing / Bending", "弯曲变形"),
}

def _svg(p): return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">%s</svg>' % p)
IC_INTRO = _svg('<circle cx="12" cy="12" r="9"/><path d="M12 16v-5M12 8h.01"/>')
IC_CHAL = _svg('<path d="M12 3 2 20h20L12 3z"/><path d="M12 10v5M12 18h.01"/>')
IC_SOL  = _svg('<path d="M12 3 4 6.5v5c0 4.6 3.2 7.7 8 9.5 4.8-1.8 8-4.9 8-9.5v-5L12 3z"/><path d="m9 12 2 2 4-4"/>')

UI = {
 "browse": ("Browse by Application", "按应用浏览"),
 "intro": ("Introduction", "介绍"),
 "products": ("Recommended Products", "推荐产品"),
 "solutions": ("Solutions", "解决方案"),
 "talk": ("Talk to a Specialist", "咨询专家"),
 "soon": ("Landing page coming soon — talk to a specialist →", "产品页即将上线 —— 咨询专家 →"),
 "eyebrow": ("AUTOMOTIVE · LABEL SOLUTIONS", "汽车 · 标签解决方案"),
 "subhead": ("Durable identification across the whole vehicle — engine bay, battery, fuel & charging, interior, exterior and rubber components.",
             "覆盖整车的耐用标识 —— 发动机舱、电池、燃油与充电、内饰、外饰与橡胶部件。"),
}

CSS = """<style>
.avhero{background:linear-gradient(115deg,rgba(10,30,80,.90),rgba(20,60,150,.50) 55%,rgba(26,86,219,.10)),url('__BANNER__') center/cover no-repeat #0e2a63;color:#fff}
.avhero .wrap{padding:56px 24px}.avhero .eyebrow{color:#9dbcff}
.avhero h1{color:#fff;font-size:38px;font-weight:800;line-height:1.14;margin:6px 0 12px;max-width:20em}
.avhero p{color:#eef3ff;font-size:16px;line-height:1.6;max-width:56em}
.avovbody{max-width:70em}.avovbody p{font-size:17px;line-height:1.7;color:var(--ink)}
.avmod{margin-top:8px}
.avtabsrow{display:flex;align-items:center;gap:6px;border-bottom:1px solid var(--line)}
.avtabs{display:flex;gap:24px;overflow-x:auto;scrollbar-width:none;flex:1}.avtabs::-webkit-scrollbar{display:none}
.avtab{white-space:nowrap;background:none;border:none;padding:12px 0;font-size:15px;font-weight:700;color:var(--mut);cursor:pointer;border-bottom:3px solid transparent;margin-bottom:-1px}
.avtab.on{color:var(--blue-deep);border-bottom-color:var(--blue)}
.avarrow{background:none;border:none;font-size:20px;color:var(--mut);cursor:pointer;padding:4px 6px}
.avpanel{padding-top:24px}
.av3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;align-items:start}
.avbox{border:1px solid var(--line);border-radius:12px;padding:18px 20px;background:#fff}
.avbox .h{display:flex;align-items:center;gap:12px;margin-bottom:10px}
.avbox .h .i{width:28px;height:28px;flex:0 0 auto}.avbox .h .i svg{width:28px;height:28px}
.avbox .h .e{font-size:12px;font-weight:800;letter-spacing:.04em;text-transform:uppercase}
.avbox .area{display:inline-block;background:var(--tint-blue);color:var(--blue-deep);font-size:11.5px;font-weight:700;border-radius:20px;padding:4px 12px;margin-bottom:10px}
.avbox p{font-size:14px;color:var(--ink);line-height:1.55}
.avchips{display:flex;flex-wrap:wrap;gap:7px;margin-top:2px}
.avchip{font-size:12px;font-weight:700;border-radius:20px;padding:5px 12px;line-height:1.25}
.avchip.ch{background:#fff1e8;color:#b4531a;border:1px solid #f4cdb0}
.avchip.so{background:var(--mint);color:var(--green-d);border:1px solid #cfe6c5}
.avplw{margin-top:26px}.avplh{font-size:12px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--mut);margin-bottom:12px}
.avplg{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}
.avplc{display:flex;flex-direction:column;border:1px solid var(--line);border-radius:12px;padding:18px 20px;background:#fff;text-decoration:none;transition:.16s}
.avplc:hover{border-color:var(--blue);box-shadow:0 12px 30px rgba(20,40,90,.12);transform:translateY(-3px)}
.avplc .t{font-weight:800;color:var(--blue-deep);font-size:16px;line-height:1.3}
.avplc .m{font-size:13px;font-weight:700;color:var(--blue);margin-top:7px}
.avplc .sp{font-size:12.5px;color:var(--ink);margin-top:7px;line-height:1.4}
.avplc .sp span{display:block;color:var(--faint);font-weight:800;text-transform:uppercase;font-size:10px;letter-spacing:.04em;margin-bottom:1px}
.avplc .go{font-size:12.5px;font-weight:700;color:var(--green-d);margin-top:12px}
.avplc.avfc{cursor:default}
.avplc.avfc:hover{transform:none;box-shadow:none;border-color:var(--line)}
.avplc.avfc .fd{font-size:13.5px;color:var(--mut);line-height:1.6;margin-top:9px}
@media(max-width:820px){.av3,.avplg{grid-template-columns:1fr}}
</style>""".replace("__BANNER__", BANNER)

def build_sector(lang):
    zh = (lang == "zh")
    def H(e, z): return esc(_t(lang, e, z))
    def U(k): return H(*UI[k])
    contact = L(lang, "/contact/")
    hero = ('<section class="avhero"><div class="wrap"><div class="eyebrow">%s</div>'
            '<h1>%s</h1><p>%s</p><div style="margin-top:20px"><a class="btn pri" href="%s">%s</a></div>'
            '</div></section>') % (U("eyebrow"),
        H("Automotive Label Solutions", "汽车标签解决方案"), H(*UI["subhead"]), contact, U("talk"))
    overview = ('<section class="blk"><div class="wrap"><div class="avovbody"><p>%s</p></div></div></section>') % H(
        "ETIA supplies durable automotive label materials matched to each application on the vehicle — from high-temperature engine-bay warnings and VIN traceability to EV charging labels and tire & rubber vulcanization. Browse the 19 applications below; product-line pages follow.",
        "ETIA 提供与整车各应用相匹配的耐用汽车标签材料 —— 从发动机舱高温警示标签、VIN 可追溯，到电动车充电标签与轮胎及橡胶硫化标签。下方可浏览 19 个应用，产品系列页陆续上线。")
    tabs = ""; panels = ""
    for i, a in enumerate(APPS):
        tabs += '<button class="avtab%s" onclick="avTab(this,%d)">%s</button>' % (
            " on" if i == 0 else "", i, esc(a["name"]))
        # three side-by-side boxes: Introduction (prose) / Challenge (chips) / Solution (chips)
        def box_wrap(ic, lbl, col, inner, tint=False):
            return ('<div class="avbox"%s><div class="h"><span class="i" style="color:%s">%s</span>'
                    '<span class="e" style="color:%s">%s</span></div>%s</div>') % (
                (' style="background:#f4f9f2"' if tint else ''), col, ic, col, lbl, inner)
        def chips(items, cls):
            return '<div class="avchips">%s</div>' % "".join('<span class="avchip %s">%s</span>' % (cls, esc(x)) for x in items)
        area = ('<span class="area">%s</span>' % esc(a["area"])) if a.get("area") else ""
        intro_inner = area + '<p>%s</p>' % esc(a.get("overview") or a["purpose"])
        # challenge chips derived from the paired vocabulary (dedup, order-stable) so they
        # always correspond to the Solution chips; fall back to raw text if unmapped.
        seen = set(); ch_items = []
        for pr in a.get("props", []):
            pair = PROP_CHALLENGE.get(pr)
            if pair and pair[0] not in seen:
                seen.add(pair[0]); ch_items.append(_t(lang, pair[0], pair[1]))
        if not ch_items:
            ch_items = [(c.strip()[0].upper() + c.strip()[1:]) for c in a.get("challenges", "").split(",") if c.strip()]
        ch_inner = chips(ch_items, "ch") if ch_items else ""
        so_items = [_t(lang, pr, PROP_ZH.get(pr, pr)) for pr in a.get("props", [])]
        so_inner = chips(so_items, "so") if so_items else ('<p>%s</p>' % esc(a.get("solution", "")))
        box = '<div class="av3">%s%s%s</div>' % (
            box_wrap(IC_INTRO, U("intro"), "var(--blue)", intro_inner),
            box_wrap(IC_CHAL, H("Challenge", "挑战"), "#c2621f", ch_inner),
            box_wrap(IC_SOL, H("Recommended Solution", "推荐方案"), "var(--green-d)", so_inner, tint=True))
        # cards below the intro: custom value cards (title + desc) OR a material product card
        cards = ""; heading = U("products")
        if a.get("cards"):
            heading = U("solutions")
            for c in a["cards"]:
                cards += '<div class="avplc avfc"><div class="t">%s</div><p class="fd">%s</p></div>' % (
                    esc(c["title"]), esc(c["desc"]))
        elif a.get("product"):
            url = L(lang, "/contact/?product=%s&industry=automotive" % quote(a["product"], safe=""))
            lines = ""
            if a.get("tds_3m"): lines += '<div class="m">%s</div>' % esc(a["tds_3m"])
            if a.get("facestock"): lines += '<div class="sp"><span>%s</span>%s</div>' % (H("Facestock", "面材"), esc(a["facestock"]))
            if a.get("adhesive"): lines += '<div class="sp"><span>%s</span>%s</div>' % (H("Adhesive", "胶粘剂"), esc(a["adhesive"]))
            cards = ('<a class="avplc" href="%s"><div class="t">%s</div>%s<div class="go">%s</div></a>') % (
                url, esc(a["product"]), lines, U("soon"))
        plw = ('<div class="avplw"><div class="avplh">%s</div><div class="avplg">%s</div></div>' % (
            heading, cards)) if cards else ""
        panels += '<div class="avpanel" data-i="%d" style="display:%s">%s%s</div>' % (
            i, "block" if i == 0 else "none", box, plw)
    js = ("<script>function avTab(b,i){var m=b.closest('.avmod');"
          "m.querySelectorAll('.avtab').forEach(function(x,j){x.classList.toggle('on',j===i);});"
          "m.querySelectorAll('.avpanel').forEach(function(p){p.style.display=(+p.getAttribute('data-i')===i)?'block':'none';});}"
          "function avScroll(b,d){b.closest('.avtabsrow').querySelector('.avtabs').scrollBy({left:d*240,behavior:'smooth'});}</script>")
    mod = ('<section class="blk"><div class="wrap"><h2>%s</h2><div class="avmod">'
           '<div class="avtabsrow"><button class="avarrow" onclick="avScroll(this,-1)">&lsaquo;</button>'
           '<div class="avtabs">%s</div><button class="avarrow" onclick="avScroll(this,1)">&rsaquo;</button></div>'
           '%s</div></div></section>%s') % (U("browse"), tabs, panels, js)
    body = CSS + overview + mod + ('<div class="wrap">%s</div>' % hp.cta2(lang, "applications"))
    crumb = [("Home" if not zh else "首页", "/"), ("Industries" if not zh else "行业", "/industries/"),
             (_t(lang, "Automotive Label Solutions", "汽车标签解决方案"), PATH)]
    write(lang, PATH, page(lang, PATH,
        _t(lang, "Automotive Label Solutions — Durable Vehicle Labels | ETIA",
                 "汽车标签解决方案 —— 耐用整车标签 | ETIA"),
        _t(lang, "Durable automotive label materials for 19 applications across the vehicle — engine bay, battery, fuel & charging, interior, exterior and rubber components.",
                 "覆盖整车 19 个应用的耐用汽车标签材料 —— 发动机舱、电池、燃油与充电、内饰、外饰与橡胶部件。"),
        _t(lang, "Automotive Label Solutions", "汽车标签解决方案"), "", body, crumb, active="", hero=hero))
    if lang == "en": hp.track(PATH, "industries")

URLS = [PATH]
def main():
    for lang in LANGS:
        build_sector(lang)

if __name__ == "__main__":
    main()
