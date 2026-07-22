#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Circuit Board & PCB Labels — organised by process (Wash & Reflow / Wash &
Non-Reflow / Post-Process). Each product is offered under three series, shown as
colour-coded badges: Polyonics APEX, Polyonics XF, E-Label. EN + ZH.
Data: _build/data/pcb_processes.json. (Brady competitive data stays internal.)"""
import os, json
import gen_heatproof as hp
from gen_heatproof import esc, L, page, write, LANGS

_D = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "pcb_processes.json"), encoding="utf-8"))
SEC = _D["sector"]
PROCESSES = _D["processes"]
PATH = SEC["path"]

def _t(lang, en, zh): return zh if lang == "zh" else en

def _svg(p): return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">%s</svg>' % p)
IC_CHAL = _svg('<path d="M12 3 2 20h20L12 3z"/><path d="M12 10v5M12 18h.01"/>')
IC_SOL  = _svg('<path d="M12 3 4 6.5v5c0 4.6 3.2 7.7 8 9.5 4.8-1.8 8-4.9 8-9.5v-5L12 3z"/><path d="m9 12 2 2 4-4"/>')

UI = {
 "browse": ("Browse by Process", "按工序浏览"),
 "challenge": ("Challenge", "工序挑战"),
 "recommend": ("Recommended Material", "推荐材料"),
 "products": ("Products", "产品"),
 "talk": ("Talk to a Specialist", "咨询专家"),
}

CSS = """<style>
.pchero{background:linear-gradient(120deg,#0c2555 0%,#16357d 52%,#1e50c7 100%);color:#fff}
.pchero .wrap{padding:56px 24px}.pchero .eyebrow{color:#9dbcff}
.pchero h1{color:#fff;font-size:38px;font-weight:800;line-height:1.14;margin:6px 0 12px;max-width:20em}
.pchero p{color:#eef3ff;font-size:16px;line-height:1.6;max-width:56em}
.pcov{max-width:70em}.pcov p{font-size:17px;line-height:1.7;color:var(--ink)}
.pctabsrow{display:flex;align-items:center;gap:6px;border-bottom:1px solid var(--line)}
.pctabs{display:flex;gap:24px;overflow-x:auto;scrollbar-width:none;flex:1}.pctabs::-webkit-scrollbar{display:none}
.pctab{white-space:nowrap;background:none;border:none;padding:12px 0;font-size:15px;font-weight:700;color:var(--mut);cursor:pointer;border-bottom:3px solid transparent;margin-bottom:-1px}
.pctab.on{color:var(--blue-deep);border-bottom-color:var(--blue)}
.pcpanel{padding-top:24px}
.pclead{font-size:17px;line-height:1.6;color:var(--ink);max-width:60em;margin:0 0 20px;font-weight:500}
.pc2{display:grid;grid-template-columns:1fr 1fr;gap:14px;align-items:start;max-width:760px}
.pcbox{border:1px solid var(--line);border-radius:12px;padding:16px 18px;background:#fff}
.pcbox.rec{background:#f4f9f2}
.pcbox .h{display:flex;align-items:center;gap:10px;margin-bottom:9px}
.pcbox .h .i{width:24px;height:24px;flex:0 0 auto}.pcbox .h .i svg{width:24px;height:24px}
.pcbox .h .e{font-size:12px;font-weight:800;letter-spacing:.04em;text-transform:uppercase}
.pcbox p{font-size:14px;color:var(--ink);line-height:1.55}
.pcchips{display:flex;flex-wrap:wrap;gap:7px}
.pcchip{font-size:12px;font-weight:700;border-radius:20px;padding:5px 12px;line-height:1.25}
.pcchip.ch{background:#fff1e8;color:#b4531a;border:1px solid #f4cdb0}
.pcmat{font-size:14px;font-weight:800;color:var(--green-d)}
.pcplw{margin-top:24px}.pcplh{font-size:12px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--mut);margin-bottom:12px}
.pcseries{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px;align-items:start}
.pcscard{border:1px solid var(--line);border-radius:12px;background:#fff;overflow:hidden}
.pcscard.apex{border-top:3px solid #2f7ad1}
.pcscard.xf{border-top:3px solid #0b2a6b}
.pcscard.el{border-top:3px solid var(--green-d)}
.pcshead{font-size:12px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;padding:11px 16px;border-bottom:1px solid var(--line)}
.pcshead.apex{color:#2f7ad1;background:#eaf3fc}
.pcshead.xf{color:#0b2a6b;background:#dbe6fa}
.pcshead.el{color:var(--green-d);background:var(--mint)}
.pcsitem{padding:12px 16px;border-bottom:1px solid var(--line)}
.pcsitem:last-child{border-bottom:none}
.pcsitem b{display:block;font-size:15px;font-weight:800;color:var(--blue-deep);margin-bottom:4px}
.pcsitem span{font-size:12.5px;color:var(--mut);line-height:1.5}
@media(max-width:820px){.pc2{grid-template-columns:1fr 1fr;gap:9px}.pcseries{grid-template-columns:1fr}
 .pcbox{padding:11px 12px}.pcchip{font-size:11px;padding:3px 8px}}
</style>"""


def build_sector(lang):
    zh = (lang == "zh")
    def U(k): return esc(_t(lang, *UI[k]))
    def T(en, zh_): return esc(_t(lang, en, zh_))
    contact = L(lang, "/contact/")
    hero = ('<section class="pchero"><div class="wrap">'
            '<h1>%s</h1><div style="margin-top:20px"><a class="btn pri" href="%s">%s</a></div>'
            '</div></section>') % (T(SEC["name_en"], SEC["name_zh"]), contact, U("talk"))
    apex_link = ('<p style="margin-top:14px"><a href="%s" style="font-weight:700;color:var(--blue-deep)">%s</a></p>') % (
        L(lang, "/products/apex-series/"),
        _t(lang, "Explore the Apex Series — next-generation PCB polyimide →", "了解 Apex 系列 —— 新一代 PCB 聚酰亚胺 →"))
    overview = '<section class="blk"><div class="wrap"><div class="pcov"><p>%s</p>%s</div></div></section>' % (
        T(SEC["subhead_en"], SEC["subhead_zh"]), apex_link)
    tabs = ""; panels = ""
    for i, pr in enumerate(PROCESSES):
        tabs += '<button class="pctab%s" data-key="%s" onclick="pcTab(this,%d)">%s</button>' % (
            " on" if i == 0 else "", esc(pr["key"]), i, T(pr["name_en"], pr["name_zh"]))
        chips = "".join('<span class="pcchip ch">%s</span>' % esc(c)
                        for c in (pr["chips_zh"] if zh else pr["chips_en"]))
        chal = ('<div class="pcbox"><div class="h"><span class="i" style="color:#c2621f">%s</span>'
                '<span class="e" style="color:#c2621f">%s</span></div><p>%s</p>'
                '<div class="pcchips" style="margin-top:8px">%s</div></div>') % (
            IC_CHAL, U("challenge"), T(pr["challenge_en"], pr["challenge_zh"]), chips)
        rec = ('<div class="pcbox rec"><div class="h"><span class="i" style="color:var(--green-d)">%s</span>'
               '<span class="e" style="color:var(--green-d)">%s</span></div>'
               '<div class="pcmat">%s</div><p style="margin-top:6px">%s</p></div>') % (
            IC_SOL, U("recommend"), T(pr["material_en"], pr["material_zh"]), T(pr["overview_en"], pr["overview_zh"]))
        lead = ('<p class="pclead">%s</p>' % T(pr.get("lead_en", ""), pr.get("lead_zh", ""))) if pr.get("lead_en") else ""
        box = lead + '<div class="pc2">%s%s</div>' % (chal, rec)
        # three series cards side by side — Polyonics APEX, Polyonics XF, E-Label
        cards = ""
        for label, cls, key in (("Polyonics APEX", "apex", "apex"),
                                ("Polyonics XF", "xf", "xf"),
                                ("E-Label", "el", "elabel")):
            items = ""
            for p in pr["products"]:
                val = p.get(key)
                if not val:
                    continue
                spec = _t(lang, p.get("spec_en", ""), p.get("spec_zh", ""))
                items += '<div class="pcsitem"><b>%s</b><span>%s</span></div>' % (esc(val), esc(spec))
            if not items:
                continue
            cards += '<div class="pcscard %s"><div class="pcshead %s">%s</div>%s</div>' % (
                cls, cls, esc(label), items)
        plw = '<div class="pcplw"><div class="pcplh">%s</div><div class="pcseries">%s</div></div>' % (U("products"), cards)
        panels += '<div class="pcpanel" data-i="%d" style="display:%s">%s%s</div>' % (
            i, "block" if i == 0 else "none", box, plw)
    js = ("<script>function pcTab(b,i){var m=b.closest('.pcmod');"
          "m.querySelectorAll('.pctab').forEach(function(x,j){x.classList.toggle('on',j===i);});"
          "m.querySelectorAll('.pcpanel').forEach(function(p){p.style.display=(+p.getAttribute('data-i')===i)?'block':'none';});}"
          "function pcScroll(b,d){b.closest('.pctabsrow').querySelector('.pctabs').scrollBy({left:d*240,behavior:'smooth'});}"
          "function pcHash(){var h=(location.hash||'').replace('#','');if(!h)return;"
          "var t=document.querySelector('.pctab[data-key=\"'+h+'\"]');if(t){pcTab(t,+t.getAttribute('onclick').replace(/[^0-9]/g,''));"
          "t.scrollIntoView({block:'nearest',inline:'center'});t.closest('.pcmod').scrollIntoView({behavior:'smooth',block:'start'});}}"
          "window.addEventListener('hashchange',pcHash);pcHash();</script>")
    mod = ('<section class="blk"><div class="wrap"><h2>%s</h2><div class="pcmod">'
           '<div class="pctabsrow"><button class="avarrow" onclick="pcScroll(this,-1)">&lsaquo;</button>'
           '<div class="pctabs">%s</div><button class="avarrow" onclick="pcScroll(this,1)">&rsaquo;</button></div>'
           '%s</div></div></section>%s') % (U("browse"), tabs, panels, js)
    body = CSS + overview + mod + ('<div class="wrap">%s</div>' % hp.cta2(lang, "applications"))
    sname = _t(lang, SEC["name_en"], SEC["name_zh"])
    crumb = [(_t(lang, "Home", "首页"), "/"), (_t(lang, "Industries", "行业"), "/industries/"), (sname, PATH)]
    write(lang, PATH, page(lang, PATH,
        _t(lang, "PCB Labeling Solutions — Circuit Board Labels by Process | ETIA", "PCB 标签解决方案 —— 按工序划分的电路板标签 | ETIA"),
        _t(lang, SEC["subhead_en"], SEC["subhead_zh"]), sname, "", body, crumb, active="", hero=hero))
    if lang == "en": hp.track(PATH, "industries")

URLS = [PATH]
def main():
    for lang in LANGS:
        build_sector(lang)

if __name__ == "__main__":
    main()
