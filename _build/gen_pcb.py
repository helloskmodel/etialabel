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
.pclist{border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#fff;max-width:920px}
.pcpr{display:grid;grid-template-columns:280px 1fr;gap:18px;padding:15px 18px;border-bottom:1px solid var(--line);align-items:start}
.pcpr:last-child{border-bottom:none}
.pcpr .var{display:flex;align-items:center;gap:8px;margin-bottom:9px}
.pcpr .vt{font-size:11px;font-weight:800;letter-spacing:.03em;text-transform:uppercase;color:var(--blue-deep)}
.pcesd{font-size:9.5px;font-weight:800;letter-spacing:.02em;border-radius:5px;padding:2px 7px;white-space:nowrap}
.pcesd.on{color:var(--green-d);background:var(--mint);border:1px solid #cfe6c5}
.pcesd.off{color:var(--mut);background:#f1f3f6;border:1px solid var(--line)}
.pcpn{display:flex;align-items:center;gap:7px;padding:2px 0;font-size:13.5px}
.pcpn b{font-weight:800;color:var(--blue-deep)}
.pcbadge{font-size:9px;font-weight:800;letter-spacing:.03em;text-transform:uppercase;border-radius:5px;padding:2px 6px;flex:0 0 auto;width:64px;text-align:center}
.pcbadge.el{color:var(--green-d);background:var(--mint);border:1px solid #cfe6c5}
.pcbadge.apex{color:#2f7ad1;background:#eaf3fc;border:1px solid #cfe4f8}
.pcbadge.xf{color:#0b2a6b;background:#dbe6fa;border:1px solid #b6cdf3}
.pcpr .spec{font-size:13px;color:var(--mut);line-height:1.55;align-self:center}
@media(max-width:820px){.pc2{grid-template-columns:1fr 1fr;gap:9px}
 .pcpr{grid-template-columns:1fr;gap:9px}.pcbox{padding:11px 12px}.pcchip{font-size:11px;padding:3px 8px}}
</style>"""


def build_sector(lang):
    zh = (lang == "zh")
    def U(k): return esc(_t(lang, *UI[k]))
    def T(en, zh_): return esc(_t(lang, en, zh_))
    contact = L(lang, "/contact/")
    hero = ('<section class="pchero"><div class="wrap"><div class="eyebrow">%s</div>'
            '<h1>%s</h1><p>%s</p><div style="margin-top:20px"><a class="btn pri" href="%s">%s</a></div>'
            '</div></section>') % (
        T(SEC["eyebrow_en"], SEC["eyebrow_zh"]), T(SEC["name_en"], SEC["name_zh"]),
        T(SEC["subhead_en"], SEC["subhead_zh"]), contact, U("talk"))
    overview = '<section class="blk"><div class="wrap"><div class="pcov"><p>%s</p></div></div></section>' % T(SEC["intro_en"], SEC["intro_zh"])
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
        more = ""
        if pr["key"] == "esd-safe":
            more = ('<p style="margin-top:10px"><a href="%s" style="font-weight:700;color:var(--blue-deep)">%s</a></p>') % (
                L(lang, "/industries/esd-safe-labels/"), _t(lang, "Full ESD-Safe specs & compliance →", "ESD 完整规格与合规 →"))
        rec = ('<div class="pcbox rec"><div class="h"><span class="i" style="color:var(--green-d)">%s</span>'
               '<span class="e" style="color:var(--green-d)">%s</span></div>'
               '<div class="pcmat">%s</div><p style="margin-top:6px">%s</p>%s</div>') % (
            IC_SOL, U("recommend"), T(pr["material_en"], pr["material_zh"]), T(pr["overview_en"], pr["overview_zh"]), more)
        box = '<div class="pc2">%s%s</div>' % (chal, rec)
        # compact list — one row per variant; E-Label primary + APEX/XF reference chips
        rows = ""
        for p in pr["products"]:
            var = _t(lang, p.get("variant_en", ""), p.get("variant_zh", ""))
            esd_tag = ('<span class="pcesd on">ESD ✓</span>' if p.get("esd")
                       else '<span class="pcesd off">%s</span>' % _t(lang, "no ESD", "无 ESD"))
            pns = ""
            for label, cls, key in (("E-Label", "el", "elabel"),
                                    ("APEX", "apex", "apex"),
                                    ("XF", "xf", "xf")):
                val = p.get(key)
                if val:
                    pns += '<div class="pcpn"><span class="pcbadge %s">%s</span><b>%s</b></div>' % (cls, label, esc(val))
            spec = _t(lang, p.get("spec_en", ""), p.get("spec_zh", ""))
            rows += ('<div class="pcpr"><div><div class="var"><span class="vt">%s</span>%s</div>%s</div>'
                     '<div class="spec">%s</div></div>') % (esc(var), esd_tag, pns, esc(spec))
        plw = '<div class="pcplw"><div class="pcplh">%s</div><div class="pclist">%s</div></div>' % (U("products"), rows)
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
        _t(lang, "Circuit Board & PCB Labels by Category | ETIA", "按类别划分的电路板与 PCB 标签 | ETIA"),
        _t(lang, SEC["subhead_en"], SEC["subhead_zh"]), sname, "", body, crumb, active="", hero=hero))
    if lang == "en": hp.track(PATH, "industries")

URLS = [PATH]
def main():
    for lang in LANGS:
        build_sector(lang)

if __name__ == "__main__":
    main()
