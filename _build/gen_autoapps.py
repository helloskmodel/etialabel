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

def _svg(p): return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">%s</svg>' % p)
IC_INTRO = _svg('<circle cx="12" cy="12" r="9"/><path d="M12 16v-5M12 8h.01"/>')

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
.avbox{border:1px solid var(--line);border-radius:12px;padding:20px 22px;background:#fff;max-width:none}
.avbox .h{display:flex;align-items:center;gap:12px;margin-bottom:10px}
.avbox .h .i{width:28px;height:28px;flex:0 0 auto;color:var(--blue)}.avbox .h .i svg{width:28px;height:28px}
.avbox .h .e{font-size:12px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;color:var(--blue)}
.avbox .area{display:inline-block;background:var(--tint-blue);color:var(--blue-deep);font-size:11.5px;font-weight:700;border-radius:20px;padding:4px 12px;margin-bottom:12px}
.avbox p{font-size:15px;color:var(--ink);line-height:1.65}
.avbox .avmeta{margin-top:14px;padding-top:14px;border-top:1px solid var(--line);font-size:14px;color:var(--ink);line-height:1.6}
.avbox .avmeta span{display:block;font-size:10.5px;font-weight:800;text-transform:uppercase;letter-spacing:.04em;color:var(--faint);margin-bottom:3px}
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
@media(max-width:820px){.avplg{grid-template-columns:1fr}}
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
        # single Introduction box — summarizes intro (purpose) + challenge + recommended solution
        lead = esc(a.get("overview") or a["purpose"])
        metas = ""
        if a.get("challenges"):
            metas += '<div class="avmeta"><span>%s</span>%s</div>' % (H("Challenge", "挑战"), esc(a["challenges"]))
        if a.get("solution"):
            metas += '<div class="avmeta"><span>%s</span>%s</div>' % (H("Recommended Solution", "推荐方案"), esc(a["solution"]))
        area = ('<span class="area">%s</span>' % esc(a["area"])) if a.get("area") else ""
        box = ('<div class="avbox"><div class="h"><span class="i">%s</span><span class="e">%s</span></div>'
               '%s<p>%s</p>%s</div>') % (IC_INTRO, U("intro"), area, lead, metas)
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
