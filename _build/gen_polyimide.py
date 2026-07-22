#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Polyimide Label Materials — technical landing page. Material properties →
three-layer system → ORH1 / ESD / Apex → full product line → applications →
print → FAQ. EN + ZH. Image slots are placeholders for a later unified pass.
CTAs route to ETIA contact; vendor corporate contact is not published."""
import os, json
import gen_heatproof as hp
from gen_heatproof import esc, L, page, write, LANGS

PATH = "/products/polyimide-label-materials/"

def _t(lang, en, zh): return zh if lang == "zh" else en

def _svg(p): return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">%s</svg>' % p)
IC_HEAT = _svg('<path d="M12 2s4 4 4 8a4 4 0 0 1-8 0c0-4 4-8 4-8z"/>')
IC_DIM  = _svg('<path d="M3 8h18M3 16h18"/><path d="M7 4v16M17 4v16"/>')
IC_CHEM = _svg('<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-9V3"/>')
IC_FLAME= _svg('<path d="M12 3s5 5 5 9a5 5 0 0 1-10 0c0-2 1-3 2-4 0 2 1 3 2 3 0-3 1-6 -1-8z"/>')
IC_DIEL = _svg('<path d="M13 2 3 14h7l-1 8 10-12h-7l1-8z"/>')
IC_STIFF= _svg('<rect x="3" y="9" width="18" height="6" rx="1"/><path d="M7 9V6M12 9V6M17 9V6"/>')

WHY = [
 (IC_HEAT, "Extremely high heat tolerance", "极高耐热",
  "Glass transition above 250 °C and thermal decomposition above 500 °C — the headroom that lets it survive lead-free reflow where polyester and paper cannot.",
  "玻璃化温度高于 250 °C,热分解高于 500 °C —— 正是这份余量让它在无铅回流中存活,而聚酯与纸张做不到"),
 (IC_DIM, "Dimensional stability", "尺寸稳定",
  "A label that shrinks or curls takes its barcode with it — a distorted code fails verification even with the print intact. Our polyimide stays dimensionally stable through advanced reflow and wave solder.",
  "会收缩或卷曲的标签会带走条码 —— 即使印字完好,变形的码也无法通过校验 我们的聚酰亚胺在先进回流与波峰焊中保持尺寸稳定"),
 (IC_CHEM, "Chemical resistance", "耐化学",
  "The film resists solvents and cleaners — but the exposed surface is the topcoat. Our non-yellowing, non-softening coatings resist abrasion at temperature and withstand highly corrosive, highly active fluxes.",
  "薄膜本身耐溶剂与清洗剂 —— 但真正暴露的是面涂层 我们不黄变、不软化的涂层在高温下耐磨,并承受强腐蚀、高活性助焊剂"),
 (IC_FLAME, "Naturally flame retardant", "天然阻燃",
  "Polyimide is inherently flame retardant. Selected constructions carry UL94 VTM-0: XF-603, XF-731, XF-781.",
  "聚酰亚胺本身具阻燃性 部分构造通过 UL94 VTM-0:XF-603、XF-731、XF-781"),
 (IC_DIEL, "Intrinsic dielectric strength", "本征介电强度",
  "Polyimide is an electrical insulator — the reason it can sit on a populated board without creating a conductive path.",
  "聚酰亚胺是电绝缘体 —— 因此可贴在已贴装的板上而不形成导电通路"),
 (IC_STIFF, "Stiffness and handling", "挺度与操作",
  "Its stiffness supports small die-cut formats and automated application without distortion, and enables 1 mil constructions that stay stable where a softer film would not.",
  "其挺度支持小尺寸模切与自动贴标而不变形,并让 1 mil 构造保持稳定,而更软的薄膜则做不到"),
]

LAYERS = [
 ("The film", "薄膜",
  "1 mil (25 µm) or 2 mil (50 µm) polyimide. Thickness is not only durability — 1 mil is a low-profile construction for tight component clearance, and its thermal envelope is identical to 2 mil. Thinner does not mean less heat resistance.",
  "1 mil(25 µm)或 2 mil(50 µm)聚酰亚胺 厚度不只关乎耐久 —— 1 mil 是面向紧凑元件间距的低厚构造,其热性能与 2 mil 完全相同 更薄不代表更不耐热"),
 ("The adhesive", "胶粘剂",
  "Aggressive acrylic PSAs that hold through multiple passes at extreme temperature and resist the most concentrated cleaning chemistries. Adhesive thickness is an independent design variable — it runs 1 to 2.4 mil and does not track film thickness. ESD constructions use low-charging adhesives.",
  "高粘接力丙烯酸压敏胶,在极端高温多次经历中保持粘接,并耐最浓的清洗化学品 胶厚是独立设计变量 —— 从 1 到 2.4 mil,不随薄膜厚度联动 ESD 构造采用低电荷胶"),
 ("The coating", "涂层",
  "The topcoat carries the printed image and takes the direct chemical and mechanical attack — the layer that most often decides pass or fail, and the hardest to reproduce. Three finishes: matte (resists solder-ball pickup), semi-gloss (balanced), high gloss (maximum contrast for the smallest fonts).",
  "面涂层承载印刷图像,直接承受化学与机械攻击 —— 最常决定成败、也最难复制的一层 三种表面:哑光(抗锡球附着)、半光(均衡)、高光(为最小字体提供最高对比度)"),
]

ORH1 = [("1 mil polyimide", "1 mil 聚酰亚胺", "XF-603 · XF-731 · XF-781"),
        ("2 mil polyimide", "2 mil 聚酰亚胺", "XF-732 · XF-782")]

ESD_SPEC = [
 ("Surface resistance", "表面电阻", "≥10⁹ and ≤10¹¹ ohms"),
 ("Low charging — PSA & liner", "低电荷 —— 胶与离型纸", "< 125 V"),
 ("Static decay", "静电衰减", "0.02 sec to 1% (EIA 541, XF-101ME)"),
 ("ESD surface durability", "ESD 表面耐久", ">500 IPA double rubs (ASTM D4752-10)"),
]

APEX = [
 ("XF-101M / XF-102M", "Matte white", "哑光白", "1 mil / 2 mil"),
 ("XF-101S / XF-102S", "Semi-gloss white", "半光白", "1 mil / 2 mil"),
 ("XF-101G / XF-102G", "High gloss white", "高光白", "1 mil / 2 mil"),
 ("XF-101ME", "Matte white, ESD-safe", "哑光白,ESD 防静电", "1 mil"),
 ("XF-101SE / XF-102SE", "Semi-gloss white, ESD-safe", "半光白,ESD 防静电", "1 mil / 2 mil"),
]

# product, finish_en, finish_zh, adhesive, orh1, esd, vtm0, reach, ul969
PI_1MIL = [
 ("XF-504", "Semi-gloss blue", "半光蓝", "1 mil acrylic", 0,0,0,1,1),
 ("XF-505", "Semi-gloss green", "半光绿", "1 mil acrylic", 0,0,0,1,1),
 ("XF-518", "Matte white", "哑光白", "1 mil acrylic", 0,0,0,1,1),
 ("XF-528", "High gloss white", "高光白", "1 mil acrylic", 0,0,0,1,1),
 ("XF-581", "Semi-gloss white", "半光白", "1 mil acrylic", 0,0,0,1,1),
 ("XF-583", "Matte white", "哑光白", "1 mil acrylic", 0,0,0,1,1),
 ("XF-603", "Semi-gloss white", "半光白", "1.1 mil acrylic", 1,0,1,1,0),
 ("XF-731", "Semi-gloss white", "半光白", "1 mil acrylic", 1,0,1,1,0),
 ("XF-781", "Semi-gloss white", "半光白", "1 mil acrylic", 1,1,1,1,0),
]
PI_2MIL = [
 ("XF-519", "Matte white", "哑光白", "1.5 mil acrylic", 0,0,0,1,1),
 ("XF-520", "Semi-gloss yellow", "半光黄", "2 mil acrylic", 0,0,0,1,1),
 ("XF-525", "Semi-gloss green", "半光绿", "2 mil acrylic", 0,0,0,1,1),
 ("XF-529", "High gloss white", "高光白", "1.5 mil acrylic", 0,0,0,1,1),
 ("XF-541", "Matte buff", "哑光米黄", "2 mil acrylic", 0,0,0,1,1),
 ("XF-552", "High gloss yellow", "高光黄", "2.4 mil acrylic", 0,0,0,1,0),
 ("XF-555", "High gloss white", "高光白", "2 mil acrylic", 0,0,0,1,1),
 ("XF-582", "Semi-gloss white", "半光白", "2 mil acrylic", 0,0,0,1,1),
 ("XF-584", "Matte white", "哑光白", "2 mil acrylic", 0,0,0,1,1),
 ("XF-592", "Semi-gloss white", "半光白", "2.4 mil acrylic", 0,0,0,1,1),
 ("XF-732", "Semi-gloss white", "半光白", "2 mil acrylic", 1,0,0,1,1),
 ("XF-782", "Semi-gloss white", "半光白", "2 mil acrylic", 1,1,0,1,1),
]
PI_PET = [
 ("XF-611", "1.5 mil polyester", "1.5 mil 聚酯", "Semi-gloss white", "半光白", "1.1 mil acrylic", 0,
  "−40 to 150 °C", "−40 至 150 °C", 1,1),
 ("XF-446", "2 mil polyester", "2 mil 聚酯", "Gloss white", "光面白", "1 mil acrylic", 1,
  "100 hrs @ 150 °C; −40 to 204 °C", "150 °C 100 小时;−40 至 204 °C", 1,1),
]

FAQ = [
 ("What temperature can polyimide labels withstand?", "聚酰亚胺标签能承受多高温度?",
  "Typically 100 hours at 150 °C, 5 minutes at 260 °C and 90 seconds at 300 °C — covering standard and lead-free reflow as well as wave solder exposure.",
  "通常 150 °C 100 小时、260 °C 5 分钟、300 °C 90 秒 —— 覆盖标准与无铅回流以及波峰焊"),
 ("If the film is a commodity, what makes one label different?", "薄膜是通用品,那标签之间的差别在哪?",
  "The film rarely fails. The topcoat carrying the printed image and the adhesive at the bond line decide whether a label survives — both are formulated and coated, and that is where the engineering sits.",
  "失效的很少是薄膜 承载印刷图像的面涂层与粘接界面的胶,才决定标签能否存活 —— 这两层都是配方与涂布的成果,工程含量在此"),
 ("What is ORH1 flux and why does it matter?", "ORH1 助焊剂是什么,为什么重要?",
  "ORH1 designates a highly active rosin flux — better wetting during soldering, and more aggressive attack on everything else it contacts, including the topcoat. Validated: XF-603, XF-731, XF-781, XF-732, XF-782.",
  "ORH1 指高活性松香助焊剂 —— 焊接润湿更好,对接触到的一切(包括面涂层)攻击也更强 已验证:XF-603、XF-731、XF-781、XF-732、XF-782"),
 ("1 mil or 2 mil?", "选 1 mil 还是 2 mil?",
  "2 mil for general use and maximum durability; 1 mil is a low-profile construction for tight component clearance. Thermal performance is identical — thinner does not mean less heat resistance.",
  "通用与最大耐久选 2 mil;1 mil 是面向紧凑元件间距的低厚构造 热性能相同 —— 更薄不代表更不耐热"),
 ("Matte, semi-gloss or high gloss?", "哑光、半光还是高光?",
  "Matte resists solder-ball pickup after molten wave solder; high gloss gives maximum brightness and contrast for the smallest fonts and densest barcodes; semi-gloss balances both.",
  "哑光抗波峰焊后的锡球附着;高光为最小字体与最密条码提供最高亮度与对比度;半光兼顾两者"),
 ("Polyimide or polyester?", "聚酰亚胺还是聚酯?",
  "Polyimide handles reflow and wave-solder temperatures; polyester does not. Polyester (XF-611, XF-446) suits post-process labeling applied after all soldering and cleaning, where it costs less.",
  "聚酰亚胺可承受回流与波峰焊温度,聚酯不行 聚酯(XF-611、XF-446)适合所有焊接清洗之后的后处理标识,成本更低"),
 ("Are polyimide labels the same as Kapton labels?", "聚酰亚胺标签和 Kapton 标签一样吗?",
  "Kapton® is DuPont's trademark for its polyimide film, often used generically. These are coated polyimide label materials.",
  "Kapton® 是杜邦聚酰亚胺薄膜的商标,常被泛用 这些是涂布型聚酰亚胺标签材料"),
]

CSS = """<style>
.pihero{background:linear-gradient(120deg,#2a1a52 0%,#3a2472 48%,#5a34b0 100%);color:#fff}
.pihero .wrap{padding:58px 24px}
.pihero h1{color:#fff;font-size:40px;font-weight:800;line-height:1.12;margin:0 0 12px;max-width:15em}
.pihero .tag{font-size:18px;font-weight:700;color:#d9ccff;line-height:1.4;max-width:30em;margin-bottom:10px}
.pihero p{color:#efe9ff;font-size:15.5px;line-height:1.6;max-width:52em}
.pihero .btns{margin-top:22px;display:flex;gap:12px;flex-wrap:wrap}
.pisec{max-width:72em}.pisec h2{margin-bottom:6px}.pisec p{font-size:16px;line-height:1.7;color:var(--ink)}
.pisec p+p{margin-top:12px}
.pifig{border:1px dashed #c9b8ee;background:#f7f3fe;border-radius:14px;padding:26px;text-align:center;color:#6b5aa0;max-width:60em}
.pifig .ph{font-size:12px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:#9b86d6}
.pifig .cap{font-size:14px;line-height:1.55;margin-top:10px;color:var(--ink)}
.pikick{font-size:19px;font-weight:800;color:var(--blue-deep);line-height:1.4;max-width:24em;margin:18px 0 0}
.piwhy{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:8px}
.piwc{border:1px solid var(--line);border-radius:12px;padding:20px 18px;background:#fff}
.piwc .i{width:30px;height:30px;color:#5a34b0}.piwc .i svg{width:30px;height:30px}
.piwc h3{font-size:15px;font-weight:800;color:var(--blue-deep);margin:11px 0 7px}
.piwc p{font-size:13.5px;color:var(--ink);line-height:1.55;margin:0}
.pilayers{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.pilc{border:1px solid var(--line);border-radius:12px;padding:20px;background:#fff;border-top:3px solid #5a34b0}
.pilc h3{font-size:16px;font-weight:800;color:var(--blue-deep);margin:0 0 8px}
.pilc p{font-size:13.5px;color:var(--ink);line-height:1.6;margin:0}
.pitbl{width:100%;border-collapse:collapse;font-size:13.5px;background:#fff;border:1px solid var(--line);border-radius:12px;overflow:hidden}
.pitbl th,.pitbl td{padding:9px 12px;text-align:left;border-bottom:1px solid var(--line);white-space:nowrap}
.pitbl th{background:var(--tint-blue);color:var(--blue-deep);font-weight:800;font-size:12px;letter-spacing:.02em}
.pitbl td:first-child{font-weight:800;color:var(--blue-deep)}
.pitbl tr:last-child td{border-bottom:none}
.pitbl .ck{color:var(--green-d);font-weight:800;text-align:center}
.pitwrap{overflow-x:auto;max-width:100%;margin-top:6px}
.pispec{width:100%;border-collapse:collapse;font-size:14px;background:#fff;border:1px solid var(--line);border-radius:12px;overflow:hidden;max-width:44em}
.pispec td{padding:10px 14px;border-bottom:1px solid var(--line)}.pispec tr:last-child td{border-bottom:none}
.pispec td:first-child{color:var(--mut);font-weight:600}.pispec td:last-child{font-weight:700;color:var(--blue-deep)}
.pichips{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.pichip{font-size:12.5px;font-weight:700;border-radius:20px;padding:6px 13px;background:var(--mint);color:var(--green-d);border:1px solid #cfe6c5}
.piapps{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.piap{border:1px solid var(--line);border-radius:12px;padding:18px 20px;background:#fff}
.piap h3{font-size:14px;font-weight:800;color:var(--blue-deep);margin:0 0 8px}
.piap p{font-size:13.5px;color:var(--mut);line-height:1.6;margin:0}
.pifaq{max-width:60em}.pifaqi{border-bottom:1px solid var(--line);padding:16px 0}
.pifaqi h3{font-size:15.5px;font-weight:800;color:var(--blue-deep);margin:0 0 6px}
.pifaqi p{font-size:14px;color:var(--ink);line-height:1.6;margin:0}
.piverify{font-size:12.5px;color:var(--mut);line-height:1.55;margin-top:12px;max-width:64em}
@media(max-width:900px){.piwhy{grid-template-columns:1fr 1fr}.pilayers{grid-template-columns:1fr}.piapps{grid-template-columns:1fr}}
@media(max-width:560px){.piwhy{grid-template-columns:1fr}.pihero h1{font-size:31px}}
</style>"""


def build(lang):
    def T(en, zh): return esc(_t(lang, en, zh))
    contact = L(lang, "/contact/")
    ck = lambda v: '<td class="ck">%s</td>' % ("✓" if v else "")

    hero = ('<section class="pihero"><div class="wrap">'
            '<h1>%s</h1><div class="tag">%s</div><p>%s</p>'
            '<div class="btns"><a class="btn pri" href="%s">%s</a>'
            '<a class="btn on-dark" href="%s">%s</a></div></div></section>') % (
        T("Polyimide Label Materials", "聚酰亚胺标签材料"),
        T("Coated polyimide for PCB and electronics manufacturing. Rated to 300 °C (572 °F).",
          "面向 PCB 与电子制造的涂布型聚酰亚胺 耐温至 300 °C(572 °F)"),
        T("The film, adhesive and coating are engineered as one system — for multi-pass reflow, ORH1 highly active fluxes and high-pressure chemical washes.",
          "薄膜、胶粘剂与涂层作为一个系统协同设计 —— 面向多次回流、ORH1 高活性助焊剂与高压化学清洗"),
        contact, T("Request Free Samples", "索取免费样品"),
        contact, T("Talk to an Expert", "咨询专家"))

    # proof
    proof = ('<section class="blk"><div class="wrap"><div class="pisec">'
             '<div class="pifig"><div class="ph">%s</div><div class="cap">%s</div></div>'
             '<p class="pikick">%s</p>'
             '<p style="margin-top:14px">%s</p></div></div></section>') % (
        T("Image — coated polyimide label retains barcode contrast after wave solder and ORH1 flux vs competitor",
          "配图 —— 涂布聚酰亚胺标签在波峰焊与 ORH1 助焊剂后仍保持条码对比度(对比竞品)"),
        T("Both labels are polyimide. Both are still attached. Only one is still readable.",
          "两张标签都是聚酰亚胺 都还贴着 只有一张仍可读"),
        T("The film is not what separates them.", "区别不在薄膜"),
        T("Polyimide film is a commodity — anyone can buy it. What determines whether a barcode survives ORH1 flux and a high-pressure wash is the coating on top of the film and the adhesive underneath it.",
          "聚酰亚胺薄膜是通用品 —— 谁都能买 决定条码能否挺过 ORH1 助焊剂与高压清洗的,是薄膜之上的涂层与之下的胶"))

    # why
    why = "".join('<div class="piwc"><span class="i">%s</span><h3>%s</h3><p>%s</p></div>' % (
        ic, T(te, tz), T(de, dz)) for ic, te, tz, de, dz in WHY)
    temp = ('<table class="pispec" style="margin-top:18px"><tr><td>%s</td><td>100 hrs @ 150 °C (302 °F)</td></tr>'
            '<tr><td>%s</td><td>5 min @ 260 °C (500 °F)</td></tr>'
            '<tr><td>%s</td><td>90 sec @ 300 °C (572 °F)</td></tr></table>') % (
        T("Long term", "长期"), T("Operating", "工作"), T("Short term", "短期"))
    whyblk = '<section class="blk alt"><div class="wrap"><h2>%s</h2><div class="piwhy">%s</div>%s</div></section>' % (
        T("Why polyimide", "为何选聚酰亚胺"), why, temp)

    # three layers
    layers = "".join('<div class="pilc"><h3>%s</h3><p>%s</p></div>' % (T(te, tz), T(de, dz))
                     for te, tz, de, dz in LAYERS)
    layerblk = ('<section class="blk"><div class="wrap"><h2>%s</h2>'
                '<p class="pisec" style="margin:0 0 14px">%s</p><div class="pilayers">%s</div></div></section>') % (
        T("The three layers", "三层结构"),
        T("A polyimide label is three engineered layers, each designed independently then matched as a system. Change one and the other two must be re-evaluated.",
          "一张聚酰亚胺标签是三层工程结构,各自独立设计再作为系统匹配 改动其一,另两层都须重新评估"), layers)

    # ORH1
    orh1_rows = "".join('<tr><td>%s</td><td>%s</td></tr>' % (T(fe, fz), esc(v)) for fe, fz, v in ORH1)
    orh1blk = ('<section class="blk alt"><div class="wrap"><h2>%s</h2>'
               '<p class="pisec">%s</p>'
               '<div class="pitwrap"><table class="pispec" style="margin-top:14px"><tr><th style="text-align:left;background:var(--tint-blue);color:var(--blue-deep);padding:9px 14px">%s</th>'
               '<th style="text-align:left;background:var(--tint-blue);color:var(--blue-deep);padding:9px 14px">%s</th></tr>%s</table></div></div></section>') % (
        T("ORH1 highly active flux resistance", "ORH1 高活性助焊剂耐受"),
        T("ORH1 designates a highly active rosin flux: better wetting during soldering, and more aggressive chemical attack on everything else — including the label topcoat. We name the class and identify exactly which materials are validated against it.",
          "ORH1 指高活性松香助焊剂:焊接润湿更好,对其它一切(含标签面涂层)的化学攻击也更强 我们点明这一类别,并明确哪些材料已通过验证"),
        T("Film", "薄膜"), T("ORH1 flux resistant", "耐 ORH1 助焊剂"), orh1_rows)

    # ESD
    esd_rows = "".join('<tr><td>%s</td><td>%s</td></tr>' % (T(le, lz), esc(v)) for le, lz, v in ESD_SPEC)
    esdblk = ('<section class="blk"><div class="wrap"><h2>%s</h2>'
              '<p class="pisec">%s</p>'
              '<table class="pispec" style="margin-top:14px">%s</table>'
              '<div class="pichips"><span class="pichip">ANSI/ESD S20.20</span><span class="pichip">ESD S541</span>'
              '<span class="pichip">IEC 61340</span><span class="pichip">JEDEC JESD 625B</span></div>'
              '<p class="pisec" style="margin-top:14px"><b>%s</b> XF-781 · XF-784 · XF-782 · XF-446 · Apex XF-101ME · XF-101SE · XF-102SE</p>'
              '</div></section>') % (
        T("ESD-safe constructions", "ESD 防静电构造"),
        T("For static-sensitive assemblies, static-dissipative through the whole stack — topcoat, adhesive and release liner — protecting against charge from human contact (HBM) and charged devices (CDM). The < 125 V low-charging spec holds on liner removal and again when the label is removed and repositioned.",
          "面向静电敏感组件,整叠(面涂层、胶、离型纸)静电耗散,防护来自人体接触(HBM)与带电器件(CDM)的静电 <125 V 低电荷指标在揭离离型纸时成立,取下再贴时同样成立"),
        esd_rows, T("ESD materials:", "ESD 材料:"))

    # Apex
    apex_rows = "".join('<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (esc(sku), T(fe, fz), esc(th))
                        for sku, fe, fz, th in APEX)
    apexblk = ('<section class="blk alt"><div class="wrap"><h2>%s</h2>'
               '<p class="pisec">%s</p>'
               '<div class="pitwrap"><table class="pitbl" style="margin-top:14px"><tr><th>SKU</th><th>%s</th><th>%s</th></tr>%s</table></div>'
               '<p class="pisec" style="margin-top:12px"><a href="%s" style="font-weight:700;color:var(--blue-deep)">%s</a></p>'
               '</div></section>') % (
        T("Apex Series", "Apex 系列"),
        T("Apex shares the polyimide film and thermal envelope of the established range; the coating and adhesive system is reformulated for where PCB processes have moved — more aggressive cleaning, more active fluxes and smaller barcodes. For a new qualification on an aggressive line, start with Apex; where a material is already qualified, there is no reason to requalify.",
          "Apex 沿用成熟系列的聚酰亚胺薄膜与热性能;涂层与胶系统则针对 PCB 工艺的演进重新配方 —— 更强的清洗、更活的助焊剂与更小的条码 产线苛刻的新选型从 Apex 起步;已选型验证过的则无需重新验证"),
        T("Finish", "表面"), T("Thickness", "厚度"), apex_rows,
        L(lang, "/products/apex-series/"), T("Full Apex Series page →", "查看 Apex 系列完整页 →"))

    # product line tables
    def pi_table(rows):
        head = ('<tr><th>%s</th><th>%s</th><th>%s</th><th>ORH1</th><th>ESD</th><th>UL94 VTM-0</th><th>REACH/RoHS</th><th>UL 969</th></tr>') % (
            T("Product", "产品"), T("Finish", "表面"), T("Adhesive", "胶粘剂"))
        body = ""
        for p, fe, fz, adh, o, e, v, r, u in rows:
            adh_disp = _t(lang, adh, adh.replace("acrylic", "丙烯酸"))
            body += '<tr><td>%s</td><td>%s</td><td>%s</td>%s%s%s%s%s</tr>' % (
                esc(p), T(fe, fz), esc(adh_disp), ck(o), ck(e), ck(v), ck(r), ck(u))
        return '<div class="pitwrap"><table class="pitbl">%s%s</table></div>' % (head, body)

    pet_head = ('<tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>ESD</th><th>%s</th><th>REACH/RoHS</th><th>UL 969</th></tr>') % (
        T("Product", "产品"), T("Film", "薄膜"), T("Finish", "表面"), T("Adhesive", "胶粘剂"), T("Temperature", "温度"))
    pet_body = ""
    for p, fie, fiz, fe, fz, adh, e, te, tz, r, u in PI_PET:
        adh_disp = _t(lang, adh, adh.replace("acrylic", "丙烯酸"))
        pet_body += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td>%s<td>%s</td>%s%s</tr>' % (
            esc(p), T(fie, fiz), T(fe, fz), esc(adh_disp), ck(e), T(te, tz), ck(r), ck(u))
    pet_table = '<div class="pitwrap"><table class="pitbl">%s%s</table></div>' % (pet_head, pet_body)

    lineblk = ('<section class="blk"><div class="wrap"><h2>%s</h2>'
               '<p class="pisec">%s</p>'
               '<h3 style="margin:20px 0 4px">%s</h3>%s'
               '<h3 style="margin:22px 0 4px">%s</h3>%s'
               '<h3 style="margin:22px 0 4px">%s</h3>%s'
               '<p class="piverify">%s</p></div></section>') % (
        T("PCB label product line", "PCB 标签产品线"),
        T("All polyimide materials rated 100 hrs @ 150 °C · 5 min @ 260 °C · 90 sec @ 300 °C unless noted.",
          "除注明外,所有聚酰亚胺材料额定 150 °C 100 小时 · 260 °C 5 分钟 · 300 °C 90 秒"),
        T("1 mil (25 µm) polyimide", "1 mil(25 µm)聚酰亚胺"), pi_table(PI_1MIL),
        T("2 mil (50 µm) polyimide", "2 mil(50 µm)聚酰亚胺"), pi_table(PI_2MIL),
        T("Polyester (post-process, lower temperature)", "聚酯(后处理,较低温)"), pet_table,
        T("Specifications transcribed from product literature; ESD = static-dissipative and low-charging. Verify against the current technical data sheet before production.",
          "规格转录自产品资料;ESD = 静电耗散且低电荷 量产前请以最新技术数据表为准"))

    # applications
    apps = [("PCB & electronics", "PCB 与电子", "PCB identification · WIP labeling · component tracking · IC permanent ID", "PCB 标识 · 在制品标签 · 元件追踪 · IC 永久标识"),
            ("Asset & warranty", "资产与保修", "Asset tracking · warranty labeling · ESD-safe packaging · stacked-product labels", "资产追踪 · 保修标签 · ESD 防静电包装 · 堆叠产品标签"),
            ("Industries", "行业", "Aerospace · Automotive · Electronics · Laboratory", "航空航天 · 汽车 · 电子 · 实验室")]
    appblk = '<section class="blk alt"><div class="wrap"><h2>%s</h2><div class="piapps">%s</div></div></section>' % (
        T("Applications", "应用"),
        "".join('<div class="piap"><h3>%s</h3><p>%s</p></div>' % (T(te, tz), T(de, dz)) for te, tz, de, dz in apps))

    # print performance
    printblk = ('<section class="blk"><div class="wrap"><div class="pisec"><h2>%s</h2>'
                '<p>%s</p><p>%s</p></div></div></section>') % (
        T("Print performance", "打印性能"),
        T("Optimized for crisp, high-contrast thermal-transfer imaging that holds small-font and dense-barcode readability through heat and wash cycles. Full-resin ribbons give the best print quality at elevated temperature and extended dwell.",
          "面向清晰、高对比度热转印,在热与清洗循环中保持小字与密集条码可读 全树脂碳带在高温与长驻留下打印质量最佳"),
        T("Testing with your specific printer and ribbon is mandatory — film, adhesive, coating and ribbon behave as one system. We supply samples matched to your printer for qualification on your own line.",
          "必须用你自己的打印机与碳带测试 —— 薄膜、胶、涂层与碳带作为一个系统 我们提供与你打印机匹配的样品,便于在你的产线上选型验证"))

    # faq
    faq = "".join('<div class="pifaqi"><h3>%s</h3><p>%s</p></div>' % (T(qe, qz), T(ae, az))
                  for qe, qz, ae, az in FAQ)
    faqblk = '<section class="blk alt"><div class="wrap"><h2>%s</h2><div class="pifaq">%s</div></div></section>' % (
        T("FAQ", "常见问题"), faq)

    # final cta
    finalcta = ('<section class="blk"><div class="wrap"><div class="cta cta-q"><h3>%s</h3><p>%s</p>'
                '<div class="btns"><a class="btn pri" href="%s">%s</a>'
                '<a class="btn on-dark" href="%s">%s</a></div></div></div></section>') % (
        T("Qualify it on your own line", "在你的产线上完成选型"),
        T("Tell us your process conditions, printer and ribbon — we will match a material and send samples.",
          "告诉我们你的工艺条件、打印机与碳带 —— 我们匹配材料并寄送样品"),
        contact, T("Request Free Samples", "索取免费样品"),
        contact, T("Talk to an Application Engineer", "咨询应用工程师"))

    body = (CSS + proof + whyblk + layerblk + orh1blk + esdblk + apexblk + lineblk
            + appblk + printblk + faqblk + finalcta)
    sname = _t(lang, "Polyimide Label Materials", "聚酰亚胺标签材料")
    crumb = [(_t(lang, "Home", "首页"), "/"), (_t(lang, "Products", "产品"), "/products/"), (sname, PATH)]
    faq_schema = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": _t(lang, qe, qz),
         "acceptedAnswer": {"@type": "Answer", "text": _t(lang, ae, az)}} for qe, qz, ae, az in FAQ]}
    write(lang, PATH, page(lang, PATH,
        _t(lang, "Polyimide Label Materials for PCB & Electronics | ETIA",
                 "PCB 与电子用聚酰亚胺标签材料 | ETIA"),
        _t(lang, "Coated polyimide label materials rated to 300 °C — ORH1 flux-resistant, ESD-safe and UL94 VTM-0 options, plus the Apex Series. Request free samples.",
                 "耐温至 300 °C 的涂布聚酰亚胺标签材料 —— 耐 ORH1 助焊剂、ESD 防静电与 UL94 VTM-0 选项,另有 Apex 系列 索取免费样品"),
        sname, "", body, crumb, schema_extra=[faq_schema], active="", hero=hero))
    if lang == "en": hp.track(PATH, "core")

URLS = [PATH]
def main():
    for lang in LANGS:
        build(lang)

if __name__ == "__main__":
    main()
