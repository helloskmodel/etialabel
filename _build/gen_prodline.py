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
APEX_BANNER = TDS_BASE + "APEXbanner.jpg"

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
SKUS = [  # (sku, finish-key, thickness, esd)
 ("XF-101M", "M", "1 mil", False), ("XF-101S", "S", "1 mil", False), ("XF-101G", "G", "1 mil", False),
 ("XF-101ME", "M", "1 mil", True), ("XF-101SE", "S", "1 mil", True),
 ("XF-102M", "M", "2 mil", False), ("XF-102S", "S", "2 mil", False), ("XF-102G", "G", "2 mil", False),
 ("XF-102ME", "M", "2 mil", True), ("XF-102SE", "S", "2 mil", True),
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
        H("NEW · POLYONICS PRODUCT LINE", "全新 · POLYONICS 产品线"),
        H("Introducing the NEW Apex Series – Ultra-Performance Polyimide Label Materials for PCBs",
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

URLS = []
def main():
    for lang in LANGS:
        build_apex(lang)
    URLS.append("/products/circuit-board-labels/apex-series/")

if __name__ == "__main__":
    main()
