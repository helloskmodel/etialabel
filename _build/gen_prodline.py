#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reusable PRODUCT-LINE landing pages (Polyonics-order, one consistent style per section).
Data-driven: add a line to LINES. First instance: Polyonics Apex Series (PCB).
Section order follows the Polyonics page: Hero -> Value Pillars -> Why -> Features ->
Specifications -> SKUs (+thermal) -> Applications -> Print Performance -> Documents -> CTA."""
import gen_heatproof as hp
from gen_heatproof import esc, L, page, write, LANGS

COS = "https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com/"
TDS_BASE = COS + "TDS/POLIOLICS/"
APEX_BANNER = "https://etiatech-1303055923.cos.ap-singapore.myqcloud.com/IMAGE/logo/BANNER-OMNICURE.jpg"

def _svg(p): return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
                     'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">%s</svg>' % p)
IC = [
 _svg('<path d="M12 2s4 4 4 8a4 4 0 0 1-8 0c0-1.5.7-3 2-4.5"/>'),                         # heat
 _svg('<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-9V3"/>'),            # chemical
 _svg('<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>'),                        # readability
 _svg('<rect x="6" y="3" width="12" height="6"/><path d="M6 18H4a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="7"/>'),  # print
 _svg('<path d="M12 2 4 6.5v5c0 4.6 3.2 7.7 8 9.5 4.8-1.8 8-4.9 8-9.5v-5L12 2z"/><path d="m9 12 2 2 4-4"/>'),  # usa/shield
]
CHK = _svg('<path d="m5 12 4 4L19 7"/>')
DOC = _svg('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/>')

PL_CSS = """<style>
.aphero{background:linear-gradient(115deg,rgba(10,30,80,.90),rgba(20,60,150,.66) 55%,rgba(26,86,219,.42)),url('__BANNER__') center/cover no-repeat #0e2a63;color:#fff}
.aphero .wrap{padding:56px 24px}.aphero .eyebrow{color:#9dbcff}
.aphero h1{color:#fff;font-size:38px;font-weight:800;line-height:1.14;margin:6px 0 12px;max-width:20em}
.aphero p{color:#eef3ff;font-size:16px;line-height:1.6;max-width:56em}
.plsub{color:var(--mut);font-size:15px;margin:-6px 0 16px;max-width:64em}
.pillg{display:grid;grid-template-columns:1fr 1fr;gap:2px 48px}
.pillr{display:flex;gap:16px;align-items:flex-start;padding:18px 0;border-bottom:1px solid var(--line)}
.pilli{flex:0 0 auto;width:38px;height:38px;color:var(--blue)}.pilli svg{width:38px;height:38px}
.pillt h3{font-size:18px;color:var(--blue-deep);margin-bottom:5px;line-height:1.25}
.pillt p{font-size:15px;color:var(--ink);line-height:1.6}
.plul{list-style:none;padding:0;margin:6px 0 0;display:grid;grid-template-columns:1fr 1fr;gap:0 44px}
.plul li{display:flex;gap:12px;align-items:flex-start;font-size:15.5px;color:var(--ink);line-height:1.55;padding:13px 0;border-bottom:1px solid var(--line)}
.plul .bt{flex:0 0 auto;width:22px;height:22px;color:var(--green-d)}.plul .bt svg{width:22px;height:22px}
.spectbl{width:100%;border-collapse:collapse;font-size:15px;max-width:940px}
.spectbl th{text-align:left;width:230px;background:#f4f7fd;color:var(--blue-deep);font-weight:800;padding:14px 16px;vertical-align:top}
.spectbl td{padding:14px 16px;border-bottom:1px solid var(--line);color:var(--ink)}
.skutbl{width:100%;border-collapse:collapse;font-size:14.5px}
.skutbl th{text-align:left;background:#f4f7fd;color:var(--blue-deep);font-weight:800;font-size:12px;letter-spacing:.03em;text-transform:uppercase;padding:12px;border-bottom:2px solid var(--line)}
.skutbl td{padding:12px;border-bottom:1px solid var(--line);color:var(--ink)}.skutbl td.sku{font-weight:800;color:var(--blue-deep);font-size:15px}
.esdp{background:#eaf1ff;color:var(--blue);border-radius:9px;padding:2px 9px;font-size:11.5px;font-weight:800}
.ract{display:flex;gap:7px;flex-wrap:wrap}
.plb{font-size:11px;font-weight:800;padding:6px 12px;border-radius:14px;text-decoration:none;border:1.5px solid var(--blue);color:var(--blue)}
.plb.s{background:var(--green);border-color:var(--green);color:#fff}.plb.t{border-color:var(--line);color:var(--mut)}
.tgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;max-width:660px;margin-top:6px}
.tcell{border:1px solid var(--line);border-radius:12px;padding:18px;text-align:center;background:#fff}
.tv{font-size:26px;font-weight:800;color:var(--blue)}.tl{font-size:13px;color:var(--mut);margin-top:6px}
.achip{display:inline-block;padding:9px 16px;border:1px solid var(--line);border-radius:22px;font-size:14px;color:var(--ink);background:#fff;margin:0 8px 9px 0}
.doclist{display:flex;flex-direction:column;gap:10px;max-width:820px}
.docr{display:flex;align-items:center;gap:14px;padding:13px 18px;border:1px solid var(--line);border-radius:10px;background:#fff;text-decoration:none;transition:.15s}
.docr:hover{border-color:var(--blue);background:#f8faff}
.doci{flex:0 0 auto;width:24px;height:24px;color:var(--blue)}.doci svg{width:24px;height:24px}
.docn{flex:1;font-size:15px;font-weight:700;color:var(--ink)}.docg{font-size:11px;font-weight:800;color:var(--mut);border:1px solid var(--line);border-radius:6px;padding:2px 7px}
.docd{font-size:13px;font-weight:800;color:var(--blue)}
@media(max-width:820px){.pillg,.plul{grid-template-columns:1fr}.tgrid{grid-template-columns:1fr}}
</style>""".replace("__BANNER__", APEX_BANNER)

def _t(lang, en, zh): return zh if lang == "zh" else en

# --------------------------------------------------------------- Apex data
PILLARS = [  # (icon idx, (en title, zh title), (en desc, zh desc))  -- VERBATIM copy
 (0, ("Improved Heat Resistance", "耐热性提升"),
     ("Engineered for extreme thermal cycles, ensuring your labels remain secure and readable.",
      "专为极端热循环设计，确保标签牢固附着、清晰可读。")),
 (1, ("Improved Chemical and Flux Resistance", "化学与助焊剂耐受性提升"),
     ("Withstands the harshest PCB processes, including high-pressure washes and aggressive fluxes.",
      "可承受最严苛的 PCB 工艺，包括高压清洗与强助焊剂。")),
 (2, ("Precision Readability", "精准可读性"),
     ("Maintains small-font and barcode readability through reflow and cleaning.",
      "在回流焊与清洗后仍保持小字号与条码的可读性。")),
 (3, ("Superior Print Performance", "卓越打印性能"),
     ("Optimized for crisp, high-contrast TTR printability.",
      "针对清晰、高对比度的热转印（TTR）打印进行优化。")),
 (4, ("Made in the USA, Trusted Global Supplier", "美国制造，值得信赖的全球供应商"),
     ("The quality you expect from a leader in performance label materials.",
      "源自高性能标签材料领导者的品质保证。")),
]
WHY = [  # VERBATIM
 ("72% improvement in flux solder performance vs. our legacy line, validated in testing.",
  "助焊剂焊接性能提升 72%（相较上一代材料，经测试验证）。"),
 ("15% improvement in cleaner resistance vs. our legacy line, helping labels survive high-pressure washes.",
  "清洗剂耐受性提升 15%（相较上一代材料），助力标签经受高压清洗。"),
 ("Enhanced ink transfer for more defined images, even at smaller font sizes. Designed to extend printhead life and maintain readability through exposure to highly caustic solutions.",
  "油墨转移增强，即使在更小字号下也能获得更清晰的图像；延长打印头寿命，并在强腐蚀性溶液暴露后保持可读性。"),
 ("Coating and adhesive system engineered for elevated temperatures, ensuring labels stay put and remain readable.",
  "涂层与胶粘系统专为高温设计，确保标签牢固附着、保持可读。"),
]
FEATURES = [  # from TDS "Features" (verbatim)
 ("Thermal transfer printable top surface", "热转印可打印表面"),
 ("UL 969 pending approval label and ribbon combinations", "UL 969 认证审批中（标签与碳带组合）"),
 ("Dimensionally stable at high temperatures", "高温尺寸稳定"),
 ("Chemical and abrasion resistant", "耐化学与耐磨"),
 ("Heat, cold and solvent resistant", "耐热、耐冷、耐溶剂"),
 ("Low out-gassing", "低放气"),
 ("Passes the requirements of MIL-STD-202G and Method 215K", "通过 MIL-STD-202G Method 215K 要求"),
 ("Resists smearing even in absence of preheat prior to chemical wash", "即使化学清洗前未预热也不易涂抹"),
 ("REACH and RoHS compliant", "符合 REACH 与 RoHS"),
]
SPECS = [  # only TDS-stated info
 (("Film", "面材"), ("Polyimide — 1 mil (25 µm) / 2 mil", "聚酰亚胺 — 1 mil (25 µm) / 2 mil")),
 (("Adhesive", "胶粘剂"), ("High-temperature acrylic, pressure-sensitive", "高温丙烯酸压敏胶")),
 (("Topcoat / finish", "面涂 / 表面"), ("High-opacity white — matte / semi-gloss / gloss", "高遮盖白 — 哑面 / 半光 / 亮光")),
 (("Print method", "打印方式"), ("Thermal transfer (full-resin ribbon recommended)", "热转印（建议使用全树脂碳带）")),
 (("Thermal exposure (typical)", "热暴露（典型）"),
  ("Up to 100 hrs @ 302°F (150°C) · 5 min @ 500°F (260°C) · 90 sec @ 572°F (300°C)",
   "最高 100 小时 @150°C · 5 分钟 @260°C · 90 秒 @300°C")),
 (("Standards", "标准"), ("MIL-STD-202G Method 215K · UL 969 (pending) · REACH · RoHS",
                          "MIL-STD-202G Method 215K · UL 969（审批中）· REACH · RoHS")),
]
FIN = {"M": ("Matte white", "哑面白"), "S": ("Semi-gloss white", "半光白"), "G": ("Gloss white", "亮光白")}
SKUS = [  # (sku, finish-key, thickness, esd) -- exactly the 8 TDS files on COS
 ("XF-101M", "M", "1 mil", False), ("XF-101S", "S", "1 mil", False), ("XF-101G", "G", "1 mil", False),
 ("XF-101ME", "M", "1 mil", True),
 ("XF-102M", "M", "2 mil", False), ("XF-102S", "S", "2 mil", False), ("XF-102G", "G", "2 mil", False),
 ("XF-102SE", "S", "2 mil", True),
]
THERMAL = [("100 hrs", "302°F / 150°C"), ("5 min", "500°F / 260°C"), ("90 sec", "572°F / 300°C")]
APPS = [("PCB identification & WIP labeling", "PCB 标识与在制品(WIP)标签"),
        ("Electronic component tracking", "电子元件追溯"),
        ("Asset & warranty labeling", "资产与保修标签"),
        ("Aerospace / automotive / electronics / laboratory", "航空航天 / 汽车 / 电子 / 实验室")]

def build_apex(lang):
    zh = (lang == "zh")
    def H(en, z): return esc(_t(lang, en, z))
    # HERO
    hero = ('<section class="aphero"><div class="wrap"><div class="eyebrow">%s</div>'
            '<h1>%s</h1><p>%s</p><div style="margin-top:20px"><a class="btn pri" href="%s">%s</a></div>'
            '</div></section>') % (
        H("Ultra Heat Resistant Label", "超耐高温标签"),
        H("New Apex Series – Ultra-Performance Polyimide Label Materials for PCBs",
          "全新 Apex 系列 —— 面向 PCB 的超高性能聚酰亚胺标签材料"),
        H("Next-gen coating for modern PCB lines. Proven gains in flux and cleaner resistance with excellent print quality and adhesion at high temperatures.",
          "面向现代 PCB 产线的新一代涂层。助焊剂与清洗剂耐受性显著提升，兼具优异的打印质量与高温附着力。"),
        L(lang, "/contact/"), H("Ask the Experts", "咨询专家"))
    # VALUE PILLARS (one consistent style: icon list)
    pill = "".join('<div class="pillr"><div class="pilli">%s</div><div class="pillt"><h3>%s</h3><p>%s</p></div></div>'
                   % (IC[i], H(te, tz), H(de, dz)) for i, (te, tz), (de, dz) in PILLARS)
    s_pillars = ('<section class="blk"><div class="wrap"><h2>%s</h2><div class="pillg">%s</div></div></section>'
                 % (H("Value Pillars", "产品优势"), pill))
    # WHY APEX (one consistent style: bullet list)
    why = "".join('<li><span class="bt">%s</span>%s</li>' % (CHK, H(e, z)) for e, z in WHY)
    s_why = ('<section class="blk" style="background:#f4f7fd"><div class="wrap"><h2>%s</h2>'
             '<p class="plsub">%s</p><ul class="plul">%s</ul></div></section>') % (
        H("Why Apex for PCB Manufacturing", "为什么选择 Apex"),
        H("Built for today's fluxes, cleaners, and multi-cycle reflow.", "专为当今的助焊剂、清洗剂与多次回流焊工艺打造。"), why)
    # FEATURES (bullet list, from TDS)
    feat = "".join('<li><span class="bt">%s</span>%s</li>' % (CHK, H(e, z)) for e, z in FEATURES)
    s_feat = ('<section class="blk"><div class="wrap"><h2>%s</h2><p class="plsub">%s</p><ul class="plul">%s</ul></div></section>'
              % (H("Features", "特性"), H("From the product Technical Data Sheets.", "摘自产品技术数据表（TDS）。"), feat))
    # SPECIFICATIONS (table)
    spec = "".join('<tr><th>%s</th><td>%s</td></tr>' % (H(ke, kz), H(ve, vz)) for (ke, kz), (ve, vz) in SPECS)
    s_spec = ('<section class="blk" style="background:#f4f7fd"><div class="wrap"><h2>%s</h2>'
              '<p class="plsub">%s</p><table class="spectbl"><tbody>%s</tbody></table></div></section>') % (
        H("Specifications", "规格参数"),
        H("Per the TDS. Exact per-SKU values are in each Technical Data Sheet below.",
          "依据 TDS。各型号精确参数请见下方对应技术数据表。"), spec)
    # SKUs (+ thermal)
    def acts(sku):
        return ('<div class="ract"><a class="plb t" href="%s%s.pdf" target="_blank">TDS</a>'
                '<a class="plb s" href="%s">%s</a><a class="plb" href="%s">%s</a></div>') % (
            TDS_BASE, sku,
            L(lang, "/contact/?product=%s&type=sample" % sku), H("FREE SAMPLE", "免费样品"),
            L(lang, "/contact/?product=%s&type=inquiry" % sku), H("INQUIRY", "询价"))
    rows = "".join('<tr><td class="sku">%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
        esc(sku), H(*FIN[fk]), esc(th), ('<span class="esdp">ESD</span>' if e else "—"), acts(sku))
        for sku, fk, th, e in SKUS)
    heads = "".join('<th>%s</th>' % H(*h) for h in [("Apex SKU","型号"),("Finish","表面"),("Thickness","厚度"),("ESD","ESD"),("Get it","获取")])
    therm = "".join('<div class="tcell"><div class="tv">%s</div><div class="tl">%s</div></div>' % (esc(v), esc(l)) for v, l in THERMAL)
    s_sku = ('<section class="blk"><div class="wrap"><h2>%s</h2><p class="plsub">%s</p>'
             '<div class="ptable-wrap" style="overflow-x:auto"><table class="skutbl"><thead><tr>%s</tr></thead>'
             '<tbody>%s</tbody></table></div>'
             '<h3 style="margin:26px 0 10px;color:var(--blue-deep)">%s</h3><div class="tgrid">%s</div>'
             '</div></section>') % (
        H("Product Line at a Glance — Apex Series SKUs", "Apex 系列型号一览"),
        H("All SKUs: polyimide film · acrylic adhesive · REACH/RoHS. ANSI/ESD S20.20 options available. FREE SAMPLE is per SKU.",
          "所有型号：聚酰亚胺面材 · 丙烯酸胶 · 符合 REACH/RoHS。提供 ANSI/ESD S20.20 选项。免费样品按单个型号提供。"),
        heads, rows, H("Thermal Exposure Guide (typical — see TDS for exact limits)", "热暴露参考（典型值 —— 精确上限见 TDS）"), therm)
    # APPLICATIONS
    chips = "".join('<span class="achip">%s</span>' % H(e, z) for e, z in APPS)
    s_app = ('<section class="blk" style="background:#f4f7fd"><div class="wrap"><h2>%s</h2>'
             '<p class="plsub">%s</p><div>%s</div></div></section>') % (
        H("Applications", "应用"),
        H("Compatible with common PCB process chemistries and fluxes.", "兼容常见的 PCB 工艺化学品与助焊剂。"), chips)
    # PRINT PERFORMANCE
    s_print = ('<section class="blk"><div class="wrap"><h2>%s</h2>'
               '<p style="max-width:60em;font-size:15.5px;line-height:1.7;color:var(--ink)">%s</p></div></section>') % (
        H("Print Performance", "打印性能"),
        H("Thermal-transfer printability that holds through reflow. Optimized for crisp, high-contrast TTR images — protecting the readability of small type and dense barcodes after heat and wash cycles.",
          "可经受回流焊的热转印打印性能。针对清晰、高对比度的 TTR 图像进行优化 —— 在高温与清洗循环后仍保护小字号与密集条码的可读性。"))
    # DOCUMENT DOWNLOADS (real TDS files)
    docs = "".join('<a class="docr" href="%s%s.pdf" target="_blank"><span class="doci">%s</span>'
                   '<span class="docn">%s — %s (%s)</span><span class="docg">PDF</span><span class="docd">%s</span></a>' % (
        TDS_BASE, sku, DOC, esc(sku), H(*FIN[fk]), esc(th), H("Download", "下载"))
        for sku, fk, th, e in SKUS)
    s_doc = ('<section class="blk" style="background:#f4f7fd"><div class="wrap"><h2>%s</h2>'
             '<p class="plsub">%s</p><div class="doclist">%s</div>'
             '<p class="plsub" style="margin-top:14px">%s</p></div></section>') % (
        H("Document Downloads", "资料下载"),
        H("Technical Data Sheets for each Apex SKU.", "各 Apex 型号的技术数据表（TDS）。"), docs,
        H("REACH / RoHS / UL declarations available on request.", "REACH / RoHS / UL 声明可应要求提供。"))
    # CTA
    s_cta = ('<section class="blk"><div class="wrap"><div class="cta" style="text-align:left"><h3>%s</h3><p>%s</p>'
             '<div class="btns"><a class="btn pri" href="%s">%s</a><a class="btn on-dark" href="%s">%s</a></div>'
             '</div></div></section>') % (
        H("Request guidance on SKU selection", "需要选型建议？"),
        H("Tell us your board design, line conditions and print specs — ETIA will confirm the right Apex construction and arrange samples.",
          "告诉我们您的板型设计、产线条件与打印规格 —— ETIA 将确认合适的 Apex 结构并安排样品。"),
        L(lang, "/contact/"), H("Ask the Experts", "咨询专家"),
        L(lang, "/contact/"), H("Request Apex Samples", "申请 Apex 样品"))

    body = PL_CSS + s_pillars + s_why + s_feat + s_spec + s_sku + s_app + s_print + s_doc + s_cta
    path = "/products/circuit-board-labels/apex-series/"
    crumb = [("Home" if not zh else "首页", "/"),
             ("Products" if not zh else "产品", "/products/"),
             ("Circuit Board & PCB Labels" if not zh else "电路板与 PCB 标签", ""),
             ("Apex Series" if not zh else "Apex 系列", path)]
    write(lang, path, page(lang, path,
        _t(lang, "Polyonics Apex Series — Ultra-Performance PCB Polyimide Labels | ETIA",
                 "Polyonics Apex 系列 —— 超高性能 PCB 聚酰亚胺标签 | ETIA"),
        _t(lang, "The new Polyonics Apex Series: ultra-performance polyimide PCB labels with improved flux and cleaner resistance, 300°C heat resistance, ESD-safe and UL options.",
                 "全新 Polyonics Apex 系列：超高性能 PCB 聚酰亚胺标签，助焊剂与清洗剂耐受性提升，耐温 300°C，提供 ESD 与 UL 选项。"),
        _t(lang, "Apex Series", "Apex 系列"), "",
        body, crumb, active="products", hero=hero))
    if lang == "en":
        hp.track(path, "products")

# =================================================================== PCB SECTOR
SECTOR_INTRO = (
 "PCB labels — also called printed circuit board markers — provide track-and-trace identification "
 "through assembly, testing, repair and maintenance. Manufacturers use multi-pass, high-temperature "
 "reflow and wave-soldering with pre-heat and thermal soaks, highly active (ORH1) fluxes and "
 "high-pressure chemical washes. Polyonics® polyimide PCB label materials withstand the severity of "
 "these processes, keeping printed barcodes and images readable through the harshest, multi-cycle "
 "manufacturing — for accurate inventory control and traceability from production to delivery. "
 "All materials are REACH &amp; RoHS compliant.",
 "PCB 标签 —— 又称印制电路板标识 —— 贯穿装配、测试、维修与维护，实现全流程追溯。制造过程采用多次高温回流焊与波峰焊，"
 "包含预热与热浸、强活性（ORH1）助焊剂及高压化学清洗。Polyonics® 聚酰亚胺 PCB 标签材料可承受这些严苛工艺，"
 "在最严苛的多循环制造中保持条码与图像清晰可读 —— 从生产到交付实现精确的库存控制与可追溯性。所有材料均符合 REACH 与 RoHS。")

# (name_en, name_zh, (proc), (challenge), (recommended), draft)
PROC = [
 ("Wash and Reflow", "清洗与回流",
  ("The label is applied before soldering and remains on the PCB through reflow or wave soldering, flux exposure, chemical cleaning, and high-pressure washing.",
   "标签在焊接前贴附，并在回流焊或波峰焊、助焊剂暴露、化学清洗与高压清洗全过程中留存于 PCB 上。"),
  ("Extreme heat, active fluxes, and aggressive cleaners can cause ordinary labels to shrink, lift, discolor, or lose barcode readability.",
   "极端高温、活性助焊剂与强清洗剂会使普通标签收缩、翘边、变色或丧失条码可读性。"),
  ("High-temperature polyimide materials with heat-resistant coatings and aggressive adhesives. Standard and ESD-safe constructions are available.",
   "采用耐高温聚酰亚胺材料，配以耐热涂层与强力胶粘剂。提供标准型与 ESD 抗静电结构。"), False),
 ("Wash and Non-Reflow", "清洗（非回流）",
  ("The label is applied after reflow but before chemical cleaning or high-pressure washing. It encounters aggressive cleaners and moderate heat without passing through the full reflow profile.",
   "标签在回流焊之后、化学清洗或高压清洗之前贴附，会经受强清洗剂与中等温度，但不经历完整回流焊曲线。"),
  ("Cleaning chemicals and wash pressure can damage printed images, soften the label coating, or cause edge lifting.",
   "清洗化学品与清洗压力可能损坏打印图像、软化标签涂层或导致边缘翘起。"),
  ("Chemical-resistant polyimide or polyester materials selected according to the cleaner, wash pressure, and temperature exposure. ESD-safe options are available.",
   "根据清洗剂、清洗压力与温度暴露选用耐化学聚酰亚胺或聚酯材料。提供 ESD 抗静电选项。"), False),
 ("Post-Process", "后道工序",
  ("The label is applied after soldering, reflow, and cleaning have been completed. It carries final serial numbers, barcodes, inspection data, or warranty information.",
   "标签在焊接、回流与清洗完成后贴附，承载最终序列号、条码、检验数据或保修信息。"),
  ("Limited space, uneven surfaces, repeated handling, and long service life require reliable adhesion and clearly readable small-format identification.",
   "空间有限、表面不平、反复搬运与长使用寿命，要求可靠附着与清晰可读的小尺寸标识。"),
  ("Durable polyester materials provide a practical and cost-effective solution. ESD-safe polyester options are available for sensitive assemblies.",
   "耐用聚酯材料提供实用且高性价比的方案。对敏感组件提供 ESD 抗静电聚酯选项。"), False),
 ("Laser Markable", "激光打标",
  ("Serial numbers, text, barcodes, and 2D codes are created directly on a laser-sensitive label surface. Depending on the construction, the label can remain on the PCB through wash and reflow processes.",
   "序列号、文字、条码与二维码直接在激光敏感的标签表面生成。视结构不同，标签可在清洗与回流工艺中留存于 PCB 上。"),
  ("The marked image must maintain high contrast and precise code definition despite heat, chemicals, cleaning, and abrasion.",
   "在高温、化学品、清洗与磨损下，打标图像须保持高对比度与精确的码型清晰度。"),
  ("Laser-markable polyimide materials for permanent, high-resolution PCB identification. Standard and ESD-safe constructions are available.",
   "激光可打标聚酰亚胺材料，实现永久、高分辨率的 PCB 标识。提供标准型与 ESD 抗静电结构。"), False),
 ("Auto Dispense", "自动贴标",
  ("Labels are applied by automatic dispensers and applicators during high-throughput PCB assembly, without manual placement.",
   "在高节拍 PCB 装配中，标签由自动贴标机与施标器贴附，无需人工放置。"),
  ("Successful automatic placement depends on liner release, stiffness, curl, roll direction and die-cut quality — not only durability.",
   "自动贴标的成功不仅取决于耐久性，还取决于离型、挺度、卷曲、卷向与模切质量。"),
  ("Polyimide and polyester constructions validated for dispensing performance and dimensional stability. (Draft — awaiting client copy.)",
   "经验证具备贴标性能与尺寸稳定性的聚酰亚胺与聚酯结构。（草拟 —— 待客户文案确认。）"), True),
 ("Masks, Dots and Arrows", "遮蔽点与箭头",
  ("Removable masking dots, solder-mask circles and inspection arrows applied during PCB processing, then removed after the step.",
   "在 PCB 加工过程中贴附、并在该工序后移除的可移除遮蔽圆点、阻焊圆点与检验箭头。"),
  ("Materials must withstand process heat yet remove cleanly without residue, and stay stable as small die-cut shapes.",
   "材料须承受工艺高温，同时可洁净无残胶地移除，并在小尺寸模切形状下保持稳定。"),
  ("Removable high-temperature polyimide masking dots and film shapes for PCB processing. (Draft — awaiting client copy.)",
   "用于 PCB 加工的可移除耐高温聚酰亚胺遮蔽圆点与薄膜形状。（草拟 —— 待客户文案确认。）"), True),
]
# product-line cards (name, (desc en,zh), url, gradient, image)
PLINES = [
 ("NEW Apex Series – Ultra-Performance Polyimide Label Materials for PCBs",
  ("Premium polyimide platform — proven flux/cleaner gains, 300°C, ESD & UL options.",
   "高端聚酰亚胺平台 —— 助焊剂/清洗剂性能提升，耐温 300°C，提供 ESD 与 UL 选项。"),
  "/products/circuit-board-labels/apex-series/", "linear-gradient(135deg,#0e2a63,#1A56DB)", APEX_BANNER),
 ("POLYONICS XF", ("Core XF polyimide family for reflow, wash and general PCB identification.",
                   "面向回流、清洗与通用 PCB 标识的核心 XF 聚酰亚胺系列。"),
  "/contact/", "linear-gradient(135deg,#1A56DB,#3f7be0)", ""),
 ("ETIA E85 SERIES", ("ETIA-branded durable PET/PI series — cost-effective, in-stock.",
                      "ETIA 自有耐用 PET/PI 系列 —— 高性价比、现货供应。"),
  "/contact/", "linear-gradient(135deg,#358B22,#41A62A)", ""),
]

SECTOR_CSS = """<style>
.pcmod{margin-top:8px}
.pctabsrow{display:flex;align-items:center;gap:6px;border-bottom:1px solid var(--line)}
.pctabs{display:flex;gap:26px;overflow-x:auto;scrollbar-width:none;flex:1}.pctabs::-webkit-scrollbar{display:none}
.pctab{white-space:nowrap;background:none;border:none;padding:12px 0;font-size:15px;font-weight:700;color:var(--mut);cursor:pointer;border-bottom:3px solid transparent;margin-bottom:-1px}
.pctab.on{color:var(--blue-deep);border-bottom-color:var(--blue)}
.pcarrow{background:none;border:none;font-size:20px;color:var(--mut);cursor:pointer;padding:4px 6px}
.pcpanel{padding-top:24px}
.pc3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}
.pcbox{border:1px solid var(--line);border-radius:12px;padding:20px 20px 22px;background:#fff}
.pchead{display:flex;align-items:center;gap:12px;margin-bottom:12px}
.pcbi{flex:0 0 auto;width:34px;height:34px}.pcbi svg{width:34px;height:34px}
.pce{font-size:15px;font-weight:800;letter-spacing:.03em;text-transform:uppercase;line-height:1.15}
.pcbox p{font-size:15px;color:var(--ink);line-height:1.6}
.pcdraft{font-size:11px;color:var(--mut);font-style:italic;margin-top:8px}
.plw{margin-top:30px}
.plh{font-size:12px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--mut);margin-bottom:14px}
.plg{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.plc{display:flex;flex-direction:column;border:1px solid var(--line);border-radius:13px;overflow:hidden;background:#fff;text-decoration:none;transition:transform .18s,box-shadow .18s,border-color .18s}
.plc:hover{transform:translateY(-4px);box-shadow:0 14px 34px rgba(20,40,90,.14);border-color:var(--blue)}
.plimg{position:relative;aspect-ratio:16/9;background-size:cover;background-position:center;display:flex;align-items:flex-end}
.plgo{color:#fff;font-weight:800;font-size:12px;padding:10px 12px;background:linear-gradient(transparent,rgba(0,0,0,.35))}
.plb2{padding:14px 15px 16px}.pln{font-weight:800;font-size:15.5px;color:var(--blue-deep)}.plb2 p{font-size:12px;color:var(--mut);line-height:1.5;margin-top:7px}
@media(max-width:820px){.pc3{grid-template-columns:1fr}.plg{grid-template-columns:1fr}}
</style>"""
PROC_ICONS = (
 _svg('<path d="M3 12h4l2-7 4 14 2-7h6"/>'),                 # process
 _svg('<path d="M12 3 2 20h20L12 3z"/><path d="M12 10v5M12 18h.01"/>'),  # challenge
 _svg('<path d="M12 3 4 6.5v5c0 4.6 3.2 7.7 8 9.5 4.8-1.8 8-4.9 8-9.5v-5L12 3z"/><path d="m9 12 2 2 4-4"/>'),  # recommended
)

def build_pcb_sector(lang):
    zh = (lang == "zh")
    def H(en, z): return esc(_t(lang, en, z))
    tabs = ""; panels = ""
    for i, (ne, nz, pr, ch, rc, draft) in enumerate(PROC):
        tabs += '<button class="pctab%s" onclick="pcTab(this,%d)">%s</button>' % (" on" if i == 0 else "", i, H(ne, nz))
        cols = ('<div class="pc3">'
                '<div class="pcbox"><div class="pchead"><div class="pcbi" style="color:var(--blue)">%s</div><div class="pce" style="color:var(--blue)">%s</div></div><p>%s</p></div>'
                '<div class="pcbox"><div class="pchead"><div class="pcbi" style="color:#c2621f">%s</div><div class="pce" style="color:#b4531a">%s</div></div><p>%s</p></div>'
                '<div class="pcbox" style="background:#f4f9f2"><div class="pchead"><div class="pcbi" style="color:var(--green-d)">%s</div><div class="pce" style="color:var(--green-d)">%s</div></div><p>%s</p>%s</div>'
                '</div>') % (
            PROC_ICONS[0], H("Process", "工艺"), H(*pr),
            PROC_ICONS[1], H("Challenge", "挑战"), H(*ch),
            PROC_ICONS[2], H("Recommended Material", "推荐材料"), H(*rc),
            ('<p class="pcdraft">%s</p>' % H("Draft — awaiting final copy.", "草拟 —— 待最终文案。") if draft else ""))
        cards = ""
        for name, (de, dz), url, grad, img in PLINES:
            style = (('background:%s;background-image:url(%s);background-size:cover;background-position:center' % (grad, esc(img)))
                     if img else ('background:%s' % grad))
            cards += ('<a class="plc" href="%s"><div class="plimg" style="%s"><span class="plgo">%s</span></div>'
                      '<div class="plb2"><div class="pln">%s</div><p>%s</p></div></a>') % (
                L(lang, url), style, H("Open series →", "查看系列 →"), esc(name), H(de, dz))
        panels += ('<div class="pcpanel" data-i="%d" style="display:%s">%s'
                   '<div class="plw"><div class="plh">%s</div><div class="plg">%s</div></div></div>') % (
            i, "block" if i == 0 else "none", cols, H("Product Lines", "产品系列"), cards)
    js = ("<script>function pcTab(b,i){var m=b.closest('.pcmod');"
          "m.querySelectorAll('.pctab').forEach(function(x,j){x.classList.toggle('on',j===i);});"
          "m.querySelectorAll('.pcpanel').forEach(function(p){p.style.display=(+p.getAttribute('data-i')===i)?'block':'none';});}"
          "function pcScroll(b,d){b.closest('.pctabsrow').querySelector('.pctabs').scrollBy({left:d*240,behavior:'smooth'});}</script>")
    intro = '<section class="blk" style="padding-bottom:0"><div class="wrap"><p style="max-width:70em;font-size:15px;line-height:1.7;color:var(--ink)">%s</p></div></section>' % _t(lang, *SECTOR_INTRO)
    module = ('<section class="blk"><div class="wrap"><h2>%s</h2><div class="pcmod">'
              '<div class="pctabsrow"><button class="pcarrow" onclick="pcScroll(this,-1)">&lsaquo;</button>'
              '<div class="pctabs">%s</div><button class="pcarrow" onclick="pcScroll(this,1)">&rsaquo;</button></div>'
              '%s</div></div></section>%s') % (H("Browse by Process", "按工艺浏览"), tabs, panels, js)
    body = SECTOR_CSS + intro + module + ('<div class="wrap">%s</div>' % hp.cta2(lang, "products"))
    path = "/products/circuit-board-labels/"
    crumb = [("Home" if not zh else "首页", "/"), ("Products" if not zh else "产品", "/products/"),
             ("Circuit Board & PCB Labels" if not zh else "电路板与 PCB 标签", path)]
    hero = ('<section class="indhero hasimg" style="background-image:url(%s)"><div class="wrap"><div class="eyebrow">%s</div>'
            '<h1>%s</h1><p class="slogan">%s</p></div></section>') % (
        esc(APEX_BANNER),
        H("PRODUCTS · ELECTRONICS & PCB", "产品 · 电子与 PCB"),
        H("Circuit Board & PCB Labels", "电路板与 PCB 标签"),
        H("Select a process to see the challenge, the recommended material, and the product lines that fit.",
          "选择一种工艺，查看对应的挑战、推荐材料与适配的产品系列。"))
    write(lang, path, page(lang, path,
        _t(lang, "Circuit Board & PCB Labels | ETIA", "电路板与 PCB 标签 | ETIA"),
        _t(lang, "Ultra-durable circuit-board and PCB labels for reflow, wash, post-process, laser marking, auto-dispense and masking — Polyonics Apex, XF and ETIA E85 lines.",
                 "面向回流、清洗、后道、激光打标、自动贴标与遮蔽的超耐用电路板 / PCB 标签 —— Polyonics Apex、XF 与 ETIA E85 系列。"),
        _t(lang, "Circuit Board & PCB Labels", "电路板与 PCB 标签"), "",
        body, crumb, active="products", hero=hero))
    if lang == "en":
        hp.track(path, "products")

URLS = []
def main():
    for lang in LANGS:
        build_pcb_sector(lang)
        build_apex(lang)
    URLS.append("/products/circuit-board-labels/")
    URLS.append("/products/circuit-board-labels/apex-series/")

if __name__ == "__main__":
    main()
