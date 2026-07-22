#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ESD-Safe Labels — dedicated landing page for the Polyonics ESD-Safe
polyimide/polyester product line (static-dissipative, low-charging < 125 V,
ANSI/ESD S20.20 etc.). EN + ZH. Data: _build/data/esd_labels.json."""
import os, json
import gen_heatproof as hp
from gen_heatproof import esc, L, page, write, LANGS

_D = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "esd_labels.json"), encoding="utf-8"))
SEC = _D["sector"]
PATH = SEC["path"]

def _t(lang, en, zh): return zh if lang == "zh" else en

UI = {
 "why": ("Why ESD-Safe", "为何选择防静电"),
 "compliance": ("Standards & compliance", "标准与合规"),
 "apps": ("Applications", "应用"),
 "line": ("ESD-Safe product line", "防静电产品线"),
 "film": ("Film", "基材"),
 "finish": ("Finish", "表面"),
 "adhesive": ("Adhesive", "胶粘剂"),
 "temp": ("Temperature", "温度"),
 "series": ("Polyonics XF", "Polyonics XF"),
 "talk": ("Talk to a Specialist", "咨询专家"),
}

CSS = """<style>
.eshero{background:linear-gradient(120deg,#0c2555 0%,#16357d 52%,#1e50c7 100%);color:#fff}
.eshero .wrap{padding:56px 24px}.eshero .eyebrow{color:#9dbcff}
.eshero h1{color:#fff;font-size:38px;font-weight:800;line-height:1.14;margin:6px 0 12px;max-width:18em}
.eshero p{color:#eef3ff;font-size:16px;line-height:1.6;max-width:56em}
.esov{max-width:70em}.esov p{font-size:17px;line-height:1.7;color:var(--ink)}
.eswhy{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:8px}
.eswcard{border:1px solid var(--line);border-radius:12px;padding:20px;background:#fff;border-top:3px solid var(--blue)}
.eswcard h3{font-size:16px;font-weight:800;color:var(--blue-deep);margin:0 0 8px}
.eswcard p{font-size:14px;color:var(--ink);line-height:1.6;margin:0}
.eschips{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}
.eschip{font-size:12.5px;font-weight:700;border-radius:20px;padding:6px 13px;background:var(--tint-blue);color:var(--blue-deep);border:1px solid #d7e3fb;line-height:1.25}
.esapps{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:1fr 1fr;gap:10px 28px;max-width:900px}
.esapps li{position:relative;padding-left:26px;font-size:15px;color:var(--ink);line-height:1.5}
.esapps li:before{content:"";position:absolute;left:0;top:7px;width:14px;height:14px;border-radius:4px;background:var(--mint);border:1px solid #bfe0b2}
.esplg{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}
.esprod{border:1px solid var(--line);border-radius:12px;background:#fff;overflow:hidden;border-top:3px solid #0b2a6b}
.esphd{display:flex;align-items:center;gap:10px;padding:14px 18px;border-bottom:1px solid var(--line)}
.esbadge{font-size:10px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;border-radius:6px;padding:3px 8px;color:#0b2a6b;background:#dbe6fa;border:1px solid #b6cdf3}
.esphd b{font-size:17px;font-weight:800;color:var(--blue-deep)}
.esrow{display:flex;gap:12px;padding:9px 18px;font-size:13.5px;border-bottom:1px solid #f0f2f6}
.esrow:last-child{border-bottom:none}
.esrow .k{flex:0 0 78px;color:var(--mut);font-weight:700}.esrow .v{color:var(--ink);line-height:1.5}
@media(max-width:820px){.eswhy{grid-template-columns:1fr}.esapps{grid-template-columns:1fr}}
</style>"""


def build_sector(lang):
    def U(k): return esc(_t(lang, *UI[k]))
    def T(en, zh_): return esc(_t(lang, en, zh_))
    contact = L(lang, "/contact/")
    hero = ('<section class="eshero"><div class="wrap"><div class="eyebrow">%s</div>'
            '<h1>%s</h1><p>%s</p><div style="margin-top:20px"><a class="btn pri" href="%s">%s</a></div>'
            '</div></section>') % (
        T(SEC["eyebrow_en"], SEC["eyebrow_zh"]), T(SEC["name_en"], SEC["name_zh"]),
        T(SEC["subhead_en"], SEC["subhead_zh"]), contact, U("talk"))
    overview = '<section class="blk"><div class="wrap"><div class="esov"><p>%s</p></div></div></section>' % T(SEC["intro_en"], SEC["intro_zh"])
    # why + compliance
    why = "".join('<div class="eswcard"><h3>%s</h3><p>%s</p></div>' % (
        T(w["title_en"], w["title_zh"]), T(w["text_en"], w["text_zh"])) for w in _D["why"])
    chips = "".join('<span class="eschip">%s</span>' % esc(c)
                    for c in (_D["compliance_zh"] if lang == "zh" else _D["compliance_en"]))
    whyblk = ('<section class="blk alt"><div class="wrap"><h2>%s</h2><div class="eswhy">%s</div>'
              '<div class="pcplh" style="margin-top:26px;font-size:12px;font-weight:800;letter-spacing:.05em;'
              'text-transform:uppercase;color:var(--mut)">%s</div><div class="eschips">%s</div>'
              '</div></section>') % (U("why"), why, U("compliance"), chips)
    # applications
    apps = "".join('<li>%s</li>' % esc(a) for a in (_D["applications_zh"] if lang == "zh" else _D["applications_en"]))
    appsblk = '<section class="blk"><div class="wrap"><h2>%s</h2><ul class="esapps">%s</ul></div></section>' % (U("apps"), apps)
    # product line
    cards = ""
    for p in _D["products"]:
        rows = ""
        for kk, en, zh in (("film", "film_en", "film_zh"), ("finish", "finish_en", "finish_zh"),
                           ("adhesive", "adhesive_en", "adhesive_zh"), ("temp", "temp_en", "temp_zh")):
            rows += '<div class="esrow"><span class="k">%s</span><span class="v">%s</span></div>' % (
                U(kk), T(p[en], p[zh]))
        cards += ('<div class="esprod"><div class="esphd"><span class="esbadge">%s</span><b>%s</b></div>%s</div>') % (
            U("series"), esc(p["product"]), rows)
    lineblk = '<section class="blk"><div class="wrap"><h2>%s</h2><div class="esplg">%s</div></div></section>' % (U("line"), cards)
    body = CSS + overview + whyblk + appsblk + lineblk + ('<div class="wrap">%s</div>' % hp.cta2(lang, "applications"))
    sname = _t(lang, SEC["name_en"], SEC["name_zh"])
    crumb = [(_t(lang, "Home", "首页"), "/"), (_t(lang, "Industries", "行业"), "/industries/"), (sname, PATH)]
    write(lang, PATH, page(lang, PATH,
        _t(lang, "ESD-Safe Labels — Static-Dissipative Polyimide & Polyester | ETIA",
                 "防静电（ESD）标签 —— 静电耗散聚酰亚胺与聚酯 | ETIA"),
        _t(lang, SEC["subhead_en"], SEC["subhead_zh"]), sname, "", body, crumb, active="", hero=hero))
    if lang == "en": hp.track(PATH, "industries")

URLS = [PATH]
def main():
    for lang in LANGS:
        build_sector(lang)

if __name__ == "__main__":
    main()
