#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Labels by Environment — hub page with one anchored section per environment
challenge (heat, cold, chemical, abrasion). Nav "By Environment" items deep-link
to the anchors. EN + ZH."""
import os
import gen_heatproof as hp
from gen_heatproof import esc, L, page, write, LANGS

PATH = "/environments/"

def _t(lang, en, zh): return zh if lang == "zh" else en

def _svg(p): return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">%s</svg>' % p)
IC_HEAT = _svg('<path d="M12 2s4 4 4 8a4 4 0 0 1-8 0c0-4 4-8 4-8z"/><path d="M12 22a6 6 0 0 0 6-6"/>')
IC_COLD = _svg('<path d="M12 2v20M4 6l16 12M20 6 4 18"/><path d="M12 5 9 8m3-3 3 3M12 19l-3-3m3 3 3-3"/>')
IC_CHEM = _svg('<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-9V3"/><path d="M6.5 14h11"/>')
IC_ABR  = _svg('<path d="M3 17l6-6 4 4 8-8"/><path d="M14 7h7v7"/>')

ENVIRONMENTS = [
 ("heat-resistant", IC_HEAT, "Heat Resistant", "耐高温",
  "Labels that survive multi-pass reflow, wave solder and sustained high-temperature operation without smearing, lifting or losing barcode contrast. Polyimide constructions are rated to 300 °C short-term.",
  "在多次回流、波峰焊与持续高温工况下不糊、不翘、不失条码对比度的标签 聚酰亚胺构造短时耐 300 °C",
  [("/products/polyimide-label-materials/", "Polyimide label materials", "聚酰亚胺标签材料"),
   ("/industries/circuit-board-pcb/", "PCB labeling solutions", "PCB 标签解决方案")]),
 ("cold-temperatures", IC_COLD, "Cold Temperatures", "低温",
  "Adhesion and legibility that hold through cold-chain, freezer and cryogenic exposure, and through the thermal shock of moving between temperature extremes.",
  "在冷链、冷冻与深冷环境,以及温度骤变的热冲击下保持粘接与可读",
  [("/industries/automotive-label-materials/", "Automotive labeling solutions", "汽车标签解决方案"),
   ("/contact/", "Talk to a specialist", "咨询专家")]),
 ("chemical", IC_CHEM, "Chemical", "耐化学",
  "Resistance to aggressive fluxes, solvents, cleaners and process chemistries — from ORH1 highly active fluxes and Zestron/Kyzen washes to fuels, oils and cleaning agents.",
  "耐强活性助焊剂、溶剂、清洗剂与工艺化学品 —— 从 ORH1 高活性助焊剂、Zestron/Kyzen 清洗到燃油、油类与清洁剂",
  [("/industries/circuit-board-pcb/", "PCB labeling solutions", "PCB 标签解决方案"),
   ("/products/polyimide-label-materials/", "Polyimide label materials", "聚酰亚胺标签材料")]),
 ("abrasion", IC_ABR, "Abrasion", "耐磨",
  "Durable marking that stays legible through handling, rubbing, cleaning and mechanical wear across the product lifecycle.",
  "在整个生命周期的操作、摩擦、清洗与机械磨损中保持清晰的耐久标识",
  [("/industries/automotive-label-materials/", "Automotive labeling solutions", "汽车标签解决方案"),
   ("/industries/circuit-board-pcb/", "PCB labeling solutions", "PCB 标签解决方案")]),
]

CSS = """<style>
.envhero{background:linear-gradient(120deg,#0c2555 0%,#16357d 52%,#1e50c7 100%);color:#fff}
.envhero .wrap{padding:56px 24px}
.envhero h1{color:#fff;font-size:38px;font-weight:800;line-height:1.14;margin:0 0 12px;max-width:16em}
.envov{max-width:70em}.envov p{font-size:17px;line-height:1.7;color:var(--ink)}
.envgrid{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}
.envc{border:1px solid var(--line);border-radius:14px;padding:24px;background:#fff;border-top:3px solid var(--blue);scroll-margin-top:90px}
.envc .h{display:flex;align-items:center;gap:12px;margin-bottom:10px}
.envc .i{width:34px;height:34px;color:var(--blue);flex:none}.envc .i svg{width:34px;height:34px}
.envc h2{font-size:20px;font-weight:800;color:var(--blue-deep);margin:0}
.envc p{font-size:14.5px;color:var(--ink);line-height:1.6;margin:0}
.envc .lk{margin-top:14px;display:flex;flex-direction:column;gap:7px}
.envc .lk a{font-size:14px;font-weight:700;color:var(--blue-deep)}
@media(max-width:820px){.envgrid{grid-template-columns:1fr}}
</style>"""


def build(lang):
    def T(en, zh): return esc(_t(lang, en, zh))
    contact = L(lang, "/contact/")
    hero = ('<section class="envhero"><div class="wrap"><h1>%s</h1>'
            '<div style="margin-top:20px"><a class="btn pri" href="%s">%s</a></div></div></section>') % (
        T("Labels by Environment", "按环境选择标签"), contact, T("Talk to a Specialist", "咨询专家"))
    overview = ('<section class="blk"><div class="wrap"><div class="envov"><p>%s</p></div></div></section>') % T(
        "Start from the condition the label has to survive. Each environment below maps to the materials and solutions built for it — heat, cold, chemical attack and abrasion.",
        "从标签必须承受的工况出发 下面每种环境都对应为其打造的材料与方案 —— 高温、低温、化学腐蚀与磨损")
    cards = ""
    for slug, ic, te, tz, de, dz, links in ENVIRONMENTS:
        lk = "".join('<a href="%s">%s →</a>' % (L(lang, u), T(le, lz)) for u, le, lz in links)
        cards += ('<div class="envc" id="%s"><div class="h"><span class="i">%s</span><h2>%s</h2></div>'
                  '<p>%s</p><div class="lk">%s</div></div>') % (slug, ic, T(te, tz), T(de, dz), lk)
    body = CSS + overview + ('<section class="blk alt"><div class="wrap"><div class="envgrid">%s</div></div></section>' % cards) \
           + ('<div class="wrap">%s</div>' % hp.cta2(lang, "applications"))
    sname = _t(lang, "By Environment", "按环境")
    crumb = [(_t(lang, "Home", "首页"), "/"), (_t(lang, "Products", "产品"), "/products/"), (sname, PATH)]
    write(lang, PATH, page(lang, PATH,
        _t(lang, "Labels by Environment — Heat, Cold, Chemical, Abrasion | ETIA",
                 "按环境选择标签 —— 高温、低温、化学、磨损 | ETIA"),
        _t(lang, "Specialty labels chosen by the environment they must survive — heat-resistant, cold-temperature, chemical-resistant and abrasion-resistant materials and solutions.",
                 "按必须承受的环境选择特种标签 —— 耐高温、耐低温、耐化学与耐磨的材料与方案"),
        sname, "", body, crumb, active="", hero=hero))
    if lang == "en": hp.track(PATH, "core")

URLS = [PATH]
def main():
    for lang in LANGS:
        build(lang)

if __name__ == "__main__":
    main()
