#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E-2712 — dual anti-static polyester label landing page. The E-Label ESD-safe
recommendation. EN + ZH. (Brady comparison and China hotline kept out — internal
/ not for the overseas site.)"""
import os
import gen_heatproof as hp
from gen_heatproof import esc, L, page, write, LANGS

PATH = "/products/e-2712/"

def _t(lang, en, zh): return zh if lang == "zh" else en

def _svg(p): return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">%s</svg>' % p)
IC_TOP   = _svg('<rect x="3" y="4" width="18" height="4" rx="1"/><path d="M3 12h18M3 16h18M3 20h18"/>')
IC_ADH   = _svg('<rect x="3" y="10" width="18" height="4" rx="1"/><path d="M5 14v2M9 14v3M13 14v2M17 14v3M21 14v2"/>')
IC_LINER = _svg('<path d="M4 4h16v16H4z"/><path d="M8 4 4 8M14 4 4 14M20 4 4 20M20 10 10 20M20 16l-4 4"/>')
IC_BOLT  = _svg('<path d="M13 2 3 14h7l-1 8 10-12h-7l1-8z"/>')
IC_SHIELD= _svg('<path d="M12 3 4 6.5v5c0 4.6 3.2 7.7 8 9.5 4.8-1.8 8-4.9 8-9.5v-5L12 3z"/><path d="m9 12 2 2 4-4"/>')
IC_INF   = _svg('<circle cx="12" cy="12" r="9"/><path d="M12 8v8M8 12h8"/>')
IC_HEAT  = _svg('<path d="M12 2s4 4 4 8a4 4 0 0 1-8 0c0-4 4-8 4-8z"/>')
IC_PRINT = _svg('<rect x="6" y="3" width="12" height="7" rx="1"/><path d="M6 18H4a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="7" rx="1"/>')
IC_CHEM  = _svg('<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-9V3"/>')
IC_LEAF  = _svg('<path d="M11 20A7 7 0 0 1 4 13c0-6 8-9 16-9 0 8-3 16-9 16z"/><path d="M11 20c0-5 2-9 6-11"/>')

# three-layer anti-static (Why)
LAYERS = [
 (IC_TOP, "Anti-static face", "涂层面防静电",
  "Surface resistivity 10⁸–10¹¹ Ω/sq — no static from surface friction, protected right through stacking and handling.",
  "表面电阻率 10⁸~10¹¹ Ω/sq,外表面摩擦不产生静电,堆叠全程防护"),
 (IC_ADH, "Anti-static adhesive", "粘胶面防静电",
  "Adhesive resistivity 10⁷–10¹¹ Ω/sq — no static build-up once applied to boards and components.",
  "胶层电阻率 10⁷~10¹¹ Ω/sq,贴合电路板、元器件后不产生静电积聚"),
 (IC_LINER, "Anti-static liner", "离型底纸防静电",
  "The liner is anti-static too — peel voltage under 100 V, no high-voltage shock to precision parts on removal.",
  "底纸同步防静电,撕标剥离电压 <100V,撕取时无高压静电冲击精密电子件"),
]

# core advantages
ADV = [
 (IC_BOLT, "Peel voltage < 100 V", "低剥离电压 < 100V",
  "Ordinary anti-static labels can peel at hundreds of volts; E-2712 holds peel voltage under 100 V — zero static shock on removal.",
  "普通防静电标签剥离电压可达数百伏;E-2712 剥离电压严格控制在 100V 以内,撕标零静电冲击"),
 (IC_SHIELD, "Full-process ESD compliance", "全流程 ESD 合规",
  "Meets EOS/ESD STM 11.11 — ready for anti-static cleanroom use and Class I precision-electronics control.",
  "完全遵循 EOS/ESD STM 11.11 标准,无尘防静电车间直接使用,满足 I 类精密电子生产管控"),
 (IC_INF, "Permanent, non-decaying", "永久防静电不衰减",
  "Anti-static particles are built into the substrate — performance stays stable under heat and humidity and does not wash off or fade.",
  "防静电粒子内置于基材,高温、潮湿环境下性能长期稳定,不随清洗、高温加工失效"),
]

# supporting performance
PERF = [
 (IC_HEAT, "Heat & environment", "耐高温耐环境",
  "2 mil heavy PET, −40 to 180 °C — no deformation or lifting through high-temp bake or hot-humid storage.",
  "2mil 加厚 PET 基材,−40℃~180℃ 宽温区,高温烘烤、湿热仓储不变形、不翘边"),
 (IC_PRINT, "Print & traceability", "打印与追溯",
  "High-precision thermal-transfer printing with the right ribbon; crisp, abrasion-resistant barcodes for full-lifecycle PCB traceability; solvent/water-based ink compatible.",
  "配合合适色带高精度打印,条码清晰耐摩擦,满足 PCB 全生命周期追溯;支持溶剂/水性油墨印刷"),
 (IC_CHEM, "Chemical resistance", "耐化学腐蚀",
  "Resists IPA, industrial cleaners, acids/alkalis and cutting oil; passes salt spray, UV and 95% RH — barcode stays clear after PCB wash.",
  "耐异丙醇、工业清洗剂、酸碱溶液、切削油;通过盐雾、UV、95%RH 长期测试,水洗后条码字迹完整清晰"),
 (IC_LEAF, "Environmental compliance", "环保合规",
  "EU RoHS compliant, no harmful heavy metals — suitable for medical, semiconductor and industrial-control use.",
  "符合欧盟 RoHS,无有害重金属,适用于医疗、半导体、工控行业"),
]

STATS = [
 ("", "< 100 V", "Peel voltage — no static shock on removal", "剥离电压 —— 撕取无静电冲击"),
 ("", "10⁸–10¹¹", "Ω/sq surface resistivity", "Ω/sq 表面电阻率"),
 ("", "−40~180°C", "2 mil PET operating range", "2mil PET 工作温区"),
]

APPS = [
 ("PCB post-process ID", "PCB 后制程标识",
  "SMT motherboards, rigid-flex, control and power boards — batch, serial and QR permanent marking.",
  "SMT 贴片后主板、软硬结合板、工控板、电源板的批次、序列号、二维码永久标识"),
 ("Precision component ID", "精密元器件标识",
  "Chips, CPUs, memory, diodes, capacitors, connectors; semiconductor packaging, wafer carriers and trays; long-life labels for ESD-sensitive parts in storage and turnover.",
  "芯片、CPU、存储颗粒、二极管、电容电阻、连接器;半导体封装、晶圆载具、元器件托盘;静电敏感元器件入库、周转长效标签"),
 ("Cleanroom process ID", "无尘车间标识",
  "Tooling, jigs, carriers and trays as ESD assets; batch-control barcodes for anti-static zones.",
  "产线工装、治具、载具、料盘 ESD 资产标识;防静电区域物料批次管控条码"),
 ("Finished-product nameplates", "成品铭牌与追溯",
  "New-energy BMS and battery control boards, inverter boards; industrial servo drives, PLC and industrial-motherboard PCB marking.",
  "新能源储能 BMS、锂电控制板、逆变器板;工控伺服驱动、PLC、工业主板 PCB 标识"),
]

CSS = """<style>
.e2hero{background:linear-gradient(120deg,#08331f 0%,#0d5a34 48%,#0f7a45 100%);color:#fff}
.e2hero .wrap{padding:60px 24px}.e2hero .eyebrow{color:#9be6c2;letter-spacing:.08em}
.e2hero h1{color:#fff;font-size:40px;font-weight:800;line-height:1.12;margin:8px 0 4px;max-width:16em}
.e2hero .ser{font-size:20px;font-weight:800;color:#dff3ea;letter-spacing:.03em;margin-bottom:14px}
.e2hero p{color:#eafff4;font-size:16.5px;line-height:1.6;max-width:52em}
.e2hero .btns{margin-top:24px;display:flex;gap:12px;flex-wrap:wrap}
.e2sec{max-width:70em}.e2sec h2{margin-bottom:6px}.e2sec p{font-size:16px;line-height:1.7;color:var(--ink)}
.e2sec p+p{margin-top:12px}
.e2g3{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:8px}
.e2g4{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:8px}
.e2c{border:1px solid var(--line);border-radius:12px;padding:20px 18px;background:#fff}
.e2c.acc{border-top:3px solid var(--green-d)}
.e2c .i{width:32px;height:32px;color:var(--green-d)}.e2c .i svg{width:32px;height:32px}
.e2c h3{font-size:15.5px;font-weight:800;color:var(--blue-deep);margin:11px 0 7px}
.e2c p{font-size:13.5px;color:var(--ink);line-height:1.55;margin:0}
.e2stats{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.e2st{background:var(--mint);border:1px solid #cfe6c5;border-radius:14px;padding:26px 20px;text-align:center}
.e2st .big{font-size:38px;font-weight:800;color:var(--green-d);line-height:1.05}
.e2st .lab{font-size:13.5px;color:var(--ink);margin-top:10px;line-height:1.45;font-weight:600}
.e2apps{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
.e2ap{border:1px solid var(--line);border-radius:12px;padding:18px 20px;background:#fff;border-left:3px solid var(--green-d)}
.e2ap h3{font-size:15.5px;font-weight:800;color:var(--blue-deep);margin:0 0 6px}
.e2ap p{font-size:13.5px;color:var(--mut);line-height:1.55;margin:0}
.e2note{font-size:13px;color:var(--mut);line-height:1.6;margin-top:14px;max-width:64em}
@media(max-width:900px){.e2g3{grid-template-columns:1fr}.e2g4{grid-template-columns:1fr 1fr}.e2stats{grid-template-columns:1fr}.e2apps{grid-template-columns:1fr}}
@media(max-width:560px){.e2g4{grid-template-columns:1fr}.e2hero h1{font-size:31px}}
</style>"""


def build(lang):
    def T(en, zh): return esc(_t(lang, en, zh))
    contact = L(lang, "/contact/")
    btn = lambda cls, label: '<a class="btn %s" href="%s">%s</a>' % (cls, contact, label)

    hero = ('<section class="e2hero"><div class="wrap"><div class="eyebrow">%s</div>'
            '<h1>%s</h1><div class="ser">%s</div><p>%s</p>'
            '<div class="btns">%s%s</div></div></section>') % (
        T("ESD-SAFE PCB LABEL MATERIALS", "防静电 PCB 标签材料"),
        T("Dual Anti-Static Polyester Labels", "双抗静电聚酯标签"),
        T("E-2712", "E-2712"),
        T("A triple-layer anti-static polyester label — face, adhesive and liner — that blocks static across printing, application and peel. E-2712 removes the ESD-breakdown risk that surface-only anti-static labels leave behind.",
          "面层、胶面、底纸三层全防静电的聚酯标签,从打印、贴标到剥离全流程阻断静电 E-2712 消除普通仅面层防静电标签遗留的静电击穿风险"),
        btn("pri", T("Request Samples", "索取样品")),
        btn("on-dark", T("Ask an Expert", "咨询专家")))

    problem = ('<section class="blk"><div class="wrap"><div class="e2sec"><h2>%s</h2><p>%s</p><p>%s</p></div></div></section>') % (
        T("The hidden cost of static", "看不见的静电成本"),
        T("In PCB, semiconductor and precision-electronics production, an ESD-sensitive label can let static punch through chips and capacitors — scrapping entire lots. Ordinary anti-static labels protect the top surface only; the moment the liner is peeled, a high peel voltage can still damage the board.",
          "在 PCB、半导体、精密电子加工的生产流转与仓储追溯中,静电敏感标签可能让静电击穿芯片、电容,导致整批元器件报废 普通防静电标签仅面层防静电,撕标剥离瞬间产生高压剥离电压,依旧损伤精密电路板"),
        T("E-2712 uses a full three-layer anti-static construction — face, adhesive and liner — so static is blocked from print to peel, delivering true dual anti-static protection.",
          "E-2712 采用面层+胶面+底纸三层全防静电结构,从打印、贴标到剥离全程阻断静电,真正实现双抗静电防护"))

    layers = "".join('<div class="e2c acc"><span class="i">%s</span><h3>%s</h3><p>%s</p></div>' % (
        ic, T(te, tz), T(de, dz)) for ic, te, tz, de, dz in LAYERS)
    layerblk = ('<section class="blk alt"><div class="wrap"><h2>%s</h2>'
                '<p style="color:var(--mut);max-width:60em;margin-bottom:4px">%s</p>'
                '<div class="e2g3">%s</div></div></section>') % (
        T("Triple-layer anti-static", "三层全域防静电"),
        T("Most anti-static labels treat the print coating only. E-2712 makes every layer anti-static:",
          "市面上多数防静电标签仅做面层防静电 E-2712 让每一层都防静电:"), layers)

    adv = "".join('<div class="e2c"><span class="i">%s</span><h3>%s</h3><p>%s</p></div>' % (
        ic, T(te, tz), T(de, dz)) for ic, te, tz, de, dz in ADV)
    advblk = '<section class="blk"><div class="wrap"><h2>%s</h2><div class="e2g3">%s</div></div></section>' % (
        T("Core advantages", "核心优势"), adv)

    stats = "".join('<div class="e2st"><div class="big">%s</div><div class="lab">%s</div></div>' % (
        esc(big), T(le, lz)) for pre, big, le, lz in STATS)
    statblk = '<section class="blk alt"><div class="wrap"><h2>%s</h2><div class="e2stats">%s</div></div></section>' % (
        T("At a glance", "关键指标"), stats)

    perf = "".join('<div class="e2c"><span class="i">%s</span><h3>%s</h3><p>%s</p></div>' % (
        ic, T(te, tz), T(de, dz)) for ic, te, tz, de, dz in PERF)
    perfblk = '<section class="blk"><div class="wrap"><h2>%s</h2><div class="e2g4">%s</div></div></section>' % (
        T("Built for the whole electronics process", "适配电子全制程"), perf)

    apps = "".join('<div class="e2ap"><h3>%s</h3><p>%s</p></div>' % (T(te, tz), T(de, dz))
                   for te, tz, de, dz in APPS)
    appblk = '<section class="blk alt"><div class="wrap"><h2>%s</h2><div class="e2apps">%s</div></div></section>' % (
        T("Applications", "主要应用"), apps)

    finalcta = ('<section class="blk"><div class="wrap"><div class="cta cta-q"><h3>%s</h3><p>%s</p>'
                '<div class="btns"><a class="btn pri" href="%s">%s</a>'
                '<a class="btn on-dark" href="%s">%s</a></div></div></div></section>') % (
        T("Test E-2712 on your process", "在你的工序上测试 E-2712"),
        T("ETIA supplies E-2712 with sample evaluation, spec customisation and application support for ESD-controlled electronics manufacturing.",
          "ETIA 供应 E-2712,并为 ESD 受控电子制造提供样品评估、规格定制与应用支持"),
        contact, T("Request E-2712 Samples", "索取 E-2712 样品"),
        contact, T("Talk to an Application Expert", "咨询应用专家"))

    body = CSS + problem + layerblk + advblk + statblk + perfblk + appblk + finalcta
    sname = _t(lang, "E-2712", "E-2712")
    crumb = [(_t(lang, "Home", "首页"), "/"), (_t(lang, "Products", "产品"), "/products/"), (sname, PATH)]
    write(lang, PATH, page(lang, PATH,
        _t(lang, "E-2712 — Dual Anti-Static Polyester ESD Label | ETIA",
                 "E-2712 —— 双抗静电聚酯防静电标签 | ETIA"),
        _t(lang, "E-2712 dual anti-static polyester label — anti-static face, adhesive and liner, peel voltage under 100 V, EOS/ESD STM 11.11, −40 to 180 °C, RoHS.",
                 "E-2712 双抗静电聚酯标签 —— 面层、胶面、底纸全防静电,剥离电压 <100V,EOS/ESD STM 11.11,−40~180°C,RoHS"),
        sname, "", body, crumb, active="", hero=hero))
    if lang == "en": hp.track(PATH, "core")

URLS = [PATH]
def main():
    for lang in LANGS:
        build(lang)

if __name__ == "__main__":
    main()
