#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apex Series — next-generation PCB polyimide label materials landing page.
Marketing page under Circuit Board & PCB. EN + ZH."""
import os
import gen_heatproof as hp
from gen_heatproof import esc, L, page, write, LANGS

PATH = "/products/apex-series/"

def _t(lang, en, zh): return zh if lang == "zh" else en

def _svg(p): return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">%s</svg>' % p)
IC_HEAT = _svg('<path d="M12 2s4 4 4 8a4 4 0 0 1-8 0c0-4 4-8 4-8z"/><path d="M12 22a6 6 0 0 0 6-6"/>')
IC_FLUX = _svg('<path d="M6 3h12M8 3v5l-4 9a3 3 0 0 0 3 4h10a3 3 0 0 0 3-4l-4-9V3"/><path d="M6.5 14h11"/>')
IC_READ = _svg('<path d="M4 5v14M8 5v14M11 5v14M14 5v14M18 5v14M21 5v14"/>')
IC_PRINT = _svg('<rect x="6" y="3" width="12" height="7" rx="1"/><path d="M6 18H4a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="7" rx="1"/>')

WHY = [
 (IC_HEAT, "Heat Resistance", "耐高温",
  "Maintains label integrity through demanding reflow processes and repeated thermal cycles.",
  "在苛刻的回流工艺与反复热循环中保持标签完整"),
 (IC_FLUX, "Flux & Cleaner Resistance", "耐助焊剂与清洗剂",
  "Withstands aggressive fluxes and common PCB cleaning chemistries.",
  "耐受强活性助焊剂与常见 PCB 清洗化学品"),
 (IC_READ, "Precision Readability", "精准可读",
  "Preserves small text and dense barcode readability after processing.",
  "加工后仍保持小字与密集条码的可读性"),
 (IC_PRINT, "Superior Print Performance", "卓越打印表现",
  "Supports crisp, high-contrast thermal-transfer printing.",
  "支持清晰、高对比度的热转印打印"),
]

STATS = [
 ("", "72%", "Improved Flux-Solder Performance", "助焊剂-焊接性能提升"),
 ("", "15%", "Improved Cleaner Resistance", "耐清洗剂提升"),
 ("Up to", "300°C", "Typical short-term thermal exposure", "短时热暴露典型值"),
]

RANGE = [
 ("XF-101M / XF-102MM", "Matte white polyimide · 1 mil / 2 mil", "哑光白聚酰亚胺 · 1 mil / 2 mil", False),
 ("XF-101S / XF-102S", "Semi-gloss white polyimide · 1 mil / 2 mil", "半光白聚酰亚胺 · 1 mil / 2 mil", False),
 ("XF-101G / XF-102G", "Gloss white polyimide · 1 mil / 2 mil", "光面白聚酰亚胺 · 1 mil / 2 mil", False),
 ("XF-101SE / XF-102SE / XF-101ME", "ESD-safe polyimide · matte and semi-gloss options", "ESD 防静电聚酰亚胺 · 哑光与半光可选", True),
]

CSS = """<style>
.axhero{background:linear-gradient(120deg,#0a1f4d 0%,#123072 50%,#1c4bbf 100%);color:#fff}
.axhero .wrap{padding:60px 24px}.axhero .eyebrow{color:#9dbcff;letter-spacing:.08em}
.axhero h1{color:#fff;font-size:40px;font-weight:800;line-height:1.12;margin:8px 0 4px;max-width:16em}
.axhero .ser{font-size:19px;font-weight:800;color:#7fe3c0;letter-spacing:.02em;margin-bottom:14px}
.axhero p{color:#eef3ff;font-size:16.5px;line-height:1.6;max-width:52em}
.axhero .btns{margin-top:24px;display:flex;gap:12px;flex-wrap:wrap}
.axsec{max-width:70em}.axsec h2{margin-bottom:6px}.axsec p{font-size:16px;line-height:1.7;color:var(--ink)}
.axsec p+p{margin-top:12px}
.axwhy{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:8px}
.axwc{border:1px solid var(--line);border-radius:12px;padding:20px 18px;background:#fff}
.axwc .i{width:34px;height:34px;color:var(--blue)}.axwc .i svg{width:34px;height:34px}
.axwc h3{font-size:15.5px;font-weight:800;color:var(--blue-deep);margin:12px 0 7px}
.axwc p{font-size:13.5px;color:var(--ink);line-height:1.55;margin:0}
.axstats{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.axst{background:var(--tint-blue);border:1px solid #d7e3fb;border-radius:14px;padding:26px 22px;text-align:center}
.axst .pre{font-size:12px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;color:var(--blue);margin-bottom:6px}
.axst .big{font-size:42px;font-weight:800;color:var(--blue-deep);line-height:1}
.axst .lab{font-size:14px;color:var(--ink);margin-top:10px;line-height:1.45;font-weight:600}
.axdis{font-size:12.5px;color:var(--mut);line-height:1.55;margin-top:16px;max-width:64em}
.axrange{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
.axrc{border:1px solid var(--line);border-radius:12px;padding:18px 20px;background:#fff;border-left:3px solid var(--blue)}
.axrc.esd{border-left-color:var(--green-d)}
.axrc .pn{font-size:16px;font-weight:800;color:var(--blue-deep)}
.axrc .ds{font-size:14px;color:var(--mut);margin-top:5px;line-height:1.5}
.axrc .esdtag{display:inline-block;margin-top:9px;font-size:10px;font-weight:800;letter-spacing:.03em;text-transform:uppercase;color:var(--green-d);background:var(--mint);border:1px solid #cfe6c5;border-radius:5px;padding:2px 8px}
.axnote{font-size:13px;color:var(--mut);line-height:1.6;margin-top:14px;max-width:64em}
.axesd{background:#f4f9f2;border:1px solid #cfe6c5;border-radius:14px;padding:22px 24px;max-width:70em}
.axesd h3{font-size:17px;font-weight:800;color:var(--green-d);margin:0 0 8px}
.axesd p{font-size:15px;color:var(--ink);line-height:1.65;margin:0}
@media(max-width:900px){.axwhy{grid-template-columns:1fr 1fr}.axstats{grid-template-columns:1fr}.axrange{grid-template-columns:1fr}}
@media(max-width:560px){.axwhy{grid-template-columns:1fr}.axhero h1{font-size:31px}}
</style>"""


def build(lang):
    def T(en, zh): return esc(_t(lang, en, zh))
    contact = L(lang, "/contact/")
    btn = lambda cls, label: '<a class="btn %s" href="%s">%s</a>' % (cls, contact, label)

    hero = ('<section class="axhero"><div class="wrap">'
            '<div class="eyebrow">%s</div>'
            '<h1>%s</h1><div class="ser">%s</div><p>%s</p>'
            '<div class="btns">%s%s</div></div></section>') % (
        T("NEXT-GENERATION PCB LABEL MATERIALS", "新一代 PCB 标签材料"),
        T("Next-Generation PCB Polyimide Labels", "新一代 PCB 聚酰亚胺标签"),
        T("Apex Series", "Apex 系列"),
        T("Designed for modern PCB manufacturing, Apex Series polyimide label materials maintain adhesion and barcode readability through high-temperature reflow, aggressive fluxes and chemical cleaning.",
          "专为现代 PCB 制造而设计,Apex 系列聚酰亚胺标签材料在高温回流、强活性助焊剂与化学清洗中保持粘接与条码可读"),
        btn("pri", T("Request Samples", "索取样品")),
        btn("on-dark", T("Ask an Expert", "咨询专家")))

    built = ('<section class="blk"><div class="wrap"><div class="axsec">'
             '<h2>%s</h2><p>%s</p><p>%s</p></div></div></section>') % (
        T("Built for Today’s PCB Processes", "为当今 PCB 工艺而生"),
        T("Multi-cycle reflow, active fluxes and high-pressure cleaning can cause conventional labels to lift, discolor or become unreadable.",
          "多次回流、活性助焊剂与高压清洗会使普通标签翘边、变色或失去可读性"),
        T("Apex Series combines high-performance polyimide films, advanced coatings and durable adhesives to support reliable PCB traceability throughout production.",
          "Apex 系列结合高性能聚酰亚胺薄膜、先进涂层与耐久胶粘剂,在整个生产过程中支撑可靠的 PCB 追溯"))

    why = "".join('<div class="axwc"><span class="i">%s</span><h3>%s</h3><p>%s</p></div>' % (
        ic, T(te, tz), T(de, dz)) for ic, te, tz, de, dz in WHY)
    whyblk = ('<section class="blk alt"><div class="wrap"><h2>%s</h2><div class="axwhy">%s</div></div></section>') % (
        T("Why Apex?", "为何选择 Apex"), why)

    stats = "".join('<div class="axst">%s<div class="big">%s</div><div class="lab">%s</div></div>' % (
        ('<div class="pre">%s</div>' % T(pre, "最高") if pre else ""), esc(big), T(le, lz))
        for pre, big, le, lz in STATS)
    statblk = ('<section class="blk"><div class="wrap"><h2>%s</h2><div class="axstats">%s</div>'
               '<p class="axdis">%s</p></div></section>') % (
        T("Proven Performance", "经验证的性能"), stats,
        T("Compared with previous-generation materials under controlled testing. Actual performance depends on the product construction and application conditions.",
          "与上一代材料在受控测试下的对比 实际性能取决于产品构造与应用条件"))

    cards = "".join('<div class="axrc%s"><div class="pn">%s</div><div class="ds">%s</div>%s</div>' % (
        " esd" if is_esd else "", esc(pn), T(de, dz),
        ('<span class="esdtag">ESD-safe</span>' if is_esd else "")) for pn, de, dz, is_esd in RANGE)
    rangeblk = ('<section class="blk alt"><div class="wrap"><h2>%s</h2><div class="axrange">%s</div>'
                '<p class="axnote">%s</p></div></section>') % (
        T("Apex Product Range", "Apex 产品系列"), cards,
        T("REACH and RoHS compliant options are available. ESD-safe and UL Recognized constructions vary by product.",
          "提供符合 REACH 与 RoHS 的选项 ESD 防静电与 UL 认证构造因产品而异"))

    esdblk = ('<section class="blk"><div class="wrap"><div class="axesd"><h3>%s</h3><p>%s</p></div></div></section>') % (
        T("ESD-Safe Options", "ESD 防静电选项"),
        T("For electrostatic-sensitive PCBs and components, selected Apex constructions provide static-dissipative surfaces and low-charging label systems to support ESD-controlled manufacturing workflows.",
          "针对静电敏感的 PCB 与元件,选定的 Apex 构造提供静电耗散表面与低电荷标签系统,支持 ESD 受控制造流程"))

    finalcta = ('<section class="blk alt"><div class="wrap"><div class="cta cta-q"><h3>%s</h3><p>%s</p>'
                '<div class="btns"><a class="btn pri" href="%s">%s</a>'
                '<a class="btn on-dark" href="%s">%s</a></div></div></div></section>') % (
        T("Find the Right Apex Material", "找到合适的 Apex 材料"),
        T("ETIA supplies Apex Series materials with sample evaluation, application support and flexible converting options.",
          "ETIA 供应 Apex 系列材料,并提供样品评估、应用支持与灵活的加工选项"),
        contact, T("Request Apex Samples", "索取 Apex 样品"),
        contact, T("Talk to an Application Expert", "咨询应用专家"))

    body = CSS + built + whyblk + statblk + rangeblk + esdblk + finalcta
    sname = _t(lang, "Apex Series", "Apex 系列")
    crumb = [(_t(lang, "Home", "首页"), "/"), (_t(lang, "Products", "产品"), "/products/"),
             (sname, PATH)]
    write(lang, PATH, page(lang, PATH,
        _t(lang, "Apex Series — Next-Generation PCB Polyimide Labels | ETIA",
                 "Apex 系列 —— 新一代 PCB 聚酰亚胺标签 | ETIA"),
        _t(lang, "Apex Series polyimide PCB label materials — heat, flux and cleaner resistant, with precision barcode readability and ESD-safe options.",
                 "Apex 系列聚酰亚胺 PCB 标签材料 —— 耐高温、耐助焊剂与清洗剂,条码精准可读,并提供 ESD 防静电选项"),
        sname, "", body, crumb, active="", hero=hero))
    if lang == "en": hp.track(PATH, "core")

URLS = [PATH]
def main():
    for lang in LANGS:
        build(lang)

if __name__ == "__main__":
    main()
