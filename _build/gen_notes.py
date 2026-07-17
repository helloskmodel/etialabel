#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Application Notes (SEO articles) + the Electronic Component Labels product landing page.
Bilingual (EN + /cn). Content supplied by the client (Polyonics Apex electronics line).
Brand claims (Apex +72% flux, 300°C, UL94, ANSI/ESD) belong to Polyonics® / are supplied
by ETIA; market cross-references are construction-equivalence, verify by TDS + sample. These
disclaimers are preserved in the copy."""
import gen_heatproof as hp
from gen_heatproof import esc, L, page, write, cta, LANGS, track

URLS = []

# ---------- render helpers (a value may be a plain str or an (en, zh) tuple) ----------
def _t(v, zh): return (v[1] if zh else v[0]) if isinstance(v, tuple) else v
def _p(items, zh):
    return "".join('<p style="color:var(--mut);max-width:64em;line-height:1.7;margin-bottom:12px">%s</p>' % esc(_t(x, zh)) for x in items)
def _ul(items, zh):
    return '<ul class="checks">%s</ul>' % "".join('<li>%s</li>' % esc(_t(x, zh)) for x in items)
def _tbl(head, rows, zh):
    th = "".join('<th>%s</th>' % esc(_t(h, zh)) for h in head)
    body = "".join('<tr>%s</tr>' % "".join('<td>%s</td>' % esc(_t(c, zh)) for c in r) for r in rows)
    return ('<div class="ptable-wrap"><table class="ptable"><thead><tr>%s</tr></thead>'
            '<tbody>%s</tbody></table></div>') % (th, body)
def _sec(title, inner, bg=""):
    st = ' style="background:%s"' % bg if bg else ""
    return '<section class="blk"%s><div class="wrap"><h2>%s</h2>%s</div></section>' % (st, esc(title), inner)
def _note(text):
    return '<div class="verify" style="margin-top:8px">%s</div>' % esc(text)

MKT_DISCLAIMER = ("Cross-references are based on material-construction equivalence (facestock / adhesive / temperature / finish / ESD), not one-to-one official certification. Verify ribbon, printing and cleaning chemistry by sample before production.",
                  "对应型号表基于材料构造等效（面材 / 胶系 / 耐温 / 表面 / ESD），非逐一官方认证；量产前请以样品验证碳带、打印与清洗化学品。")

# ==================================================================== PRODUCT LANDING
def build_ecl(lang):
    zh = (lang == "zh")
    path = "/industries/electronic-component-labels/"
    h1 = ("Electronic Component Labels Built for Extreme Environments", "为极端环境而生的电子元器件标签")
    lede = ("Polyonics® is a specialty coating manufacturer — not a label printer. We engineer the materials that let electronic-component labels survive 300°C (572°F) reflow, wave solder, aggressive flux and the entire PCB assembly process. The Apex series improves flux and solder resistance by 72% over the previous generation. ETIA supplies these Polyonics materials — as converted roll stock (for your own printing) or full-spec OEM material.",
            "Polyonics® 是一家特种涂层制造商 —— 而非标签印刷厂。我们研发的是让电子元器件标签能挺过 300°C（572°F）回流焊、波峰焊、强活性助焊剂以及整个 PCB 组装工艺的材料。Apex 系列的助焊剂/焊接耐受性比上一代提升 72%。ETIA 以转换卷材或完整规格 OEM 材料形式供应这些 Polyonics 材料。")

    s1 = _sec(_t(("Engineered for the PCB Assembly Process", "为 PCB 组装工艺而生"), zh),
        _p([("Electronic-component and PCB labels carry a traceable identity through the harshest steps of the board's life — before it even enters service. A single label may face:",
             "电子元器件与 PCB 标签在电路板投入使用之前，就要在其一生中最严苛的工序里承载追溯身份。一张标签可能面对：")], zh)
        + _ul([("Multiple reflow and wave-solder passes up to 300°C", "最高 300°C 的多次回流焊与波峰焊"),
               ("Strong active fluxes — no-clean, water-soluble and rosin", "强活性助焊剂 —— 免洗、水溶性与松香型"),
               ("High-pressure chemical cleaning — IPA, MEK and aqueous cleaners", "高压化学清洗 —— IPA、MEK 与水基清洗剂"),
               ("Abrasion during handling, assembly and field exposure", "搬运、组装与现场暴露中的磨损")], zh)
        + _p([("Facestock, topcoat, adhesive and release liner work as one system that decides whether the barcode is still readable at the end. This is a coating problem — exactly the engineering Polyonics specializes in.",
               "面材、涂层、胶粘剂与离型层作为一个整体，决定了条码在最后是否仍可读。这是一个涂层问题 —— 也正是 Polyonics 所专注的工程。")], zh))

    s2 = _sec(_t(("Measured Performance, Not Slogans (Apex Series)", "实测性能，而非口号（Apex 系列）"), zh),
        _tbl([("Property", "性能"), ("Result", "结果")],
             [[("Flux / solder resistance", "助焊剂 / 焊接耐受"), ("+72% vs. previous generation", "对比上一代 +72%")],
              [("Cleaner resistance", "清洗剂耐受"), ("+15% vs. previous generation", "对比上一代 +15%")],
              [("Temperature", "耐温"), ("Reliable adhesion & readable barcode up to 300°C (572°F)", "最高 300°C（572°F）下可靠粘接与条码可读")],
              [("Chemical", "耐化学"), ("IPA, MEK, no-clean / water-soluble / rosin flux, aqueous cleaners", "IPA、MEK、免洗 / 水溶性 / 松香助焊剂、水基清洗剂")],
              [("Abrasion", "耐磨"), ("Proprietary topcoat keeps print legible through handling, assembly and field exposure", "专有涂层在搬运、组装与现场暴露中保持印字清晰")]], zh), "var(--tint-green)")

    s3 = _sec(_t(("Polyonics® vs. Catalog Suppliers", "Polyonics® 对比目录型供应商"), zh),
        _tbl([("", ""), ("Polyonics® (supplied by ETIA)", "Polyonics®（ETIA 供货）"), ("Catalog supplier", "目录型供应商")],
             [[("Coating technology", "涂层技术"), ("In-house proprietary", "自研专有"), ("Generic or none", "通用或无")],
              [("Custom formulation", "定制配方"), ("Matched to your process", "按你的工艺匹配"), ("Limited or unavailable", "有限或不可")],
              [("Engineering support", "工程支持"), ("Direct access to coating specialists", "直接对接涂层专家"), ("Sales rep with a catalog", "拿着目录的销售")],
              [("ESD options", "ESD 选项"), ("Available in selected constructions", "部分结构可提供"), ("Isolated SKUs only", "仅个别 SKU")],
              [("Apex flux resistance", "Apex 系列助焊剂耐受"), ("+72% vs. previous generation", "对比上一代 +72%"), ("No equivalent", "无对应")]], zh))

    s4 = _sec(_t(("Electronic Label Product Family (Supplied by ETIA)", "电子标签产品族（ETIA 供货）"), zh),
        _tbl([("Model", "型号"), ("Face / Type", "表面 / 类型"), ("Thickness", "厚度"), ("Temperature", "耐温"), ("Use", "适用")],
             [["XF-101M / XF-102M", ("Matte white", "哑白"), "1 / 2 mil", ("Up to 300°C", "最高 300°C"), ("General low-profile PCB ID", "通用低厚度 PCB 标识")],
              ["XF-101S / XF-102S", ("Semi-gloss white", "半光白"), "1 / 2 mil", ("Up to 300°C", "最高 300°C"), ("Balance of scanning & handling", "扫码与操作平衡")],
              ["XF-101G / XF-102G (APEX)", ("Gloss white", "亮光白"), "1 / 2 mil", ("Up to 300°C", "最高 300°C"), ("Sharpest for high-density 2D codes", "高密度二维码最锐利")],
              ["XF-101SE / XF-102SE / XF-101ME", ("ESD semi-gloss / matte white", "ESD 半光 / 哑白"), "1 / 2 / 3 mil", ("Up to 300°C", "最高 300°C"), ("ESD-controlled assembly", "ESD 管控组装")],
              ["XF-616", ("Matte white, ultra-thin", "哑白，超薄"), "0.5 mil", ("Up to 300°C", "最高 300°C"), ("BGA / fine-pitch / tight clearance", "BGA / 细间距 / 有限间隙")],
              ["XF-603", ("White, UL94 flame-retardant", "白色，UL94 阻燃"), "1 mil", ("Up to 300°C", "最高 300°C"), ("Flame-retardant PCB ID", "阻燃 PCB 标识")],
              ["XF-505", ("Light green", "浅绿"), "1 mil", ("Up to 287°C", "最高 287°C"), ("Colour-coding by process", "颜色区分工序")]], zh)
        + _note(_t(("1 and 2 mil · matte / semi-gloss / gloss · ESD options · strong PSA · REACH & RoHS compliant · Made in USA.",
                    "1 与 2 mil · 哑 / 半光 / 亮 · ESD 选项 · 强力压敏胶 · 符合 REACH 与 RoHS · 美国制造。"), zh)), "var(--tint-blue)")

    s5 = _sec(_t(("Trusted Applications", "可信赖的应用"), zh),
        _ul([("Printed circuit board identification and tracking", "印制电路板标识与追踪"),
             ("Electronic component tracking", "电子元器件追踪"),
             ("Asset tracking", "资产追踪"),
             ("Warranty labels", "保修标签")], zh))

    s6 = _sec(_t(("Market Cross-Reference", "市场对应型号"), zh),
        _tbl([("Brand", "品牌"), ("Corresponding line", "对应产品线"), ("Notes", "说明")],
             [[("Polyonics® (featured here)", "Polyonics®（本页主推）"), "XF-101/102, XF-616, XF-603, XF-505", ("Apex ultra-high-performance polyimide", "Apex 超高性能聚酰亚胺")],
              ["Brady", "B-729 / B-768 / B-718 / B-719 / B-730 / B-731", ("Polyimide PCB label materials", "聚酰亚胺 PCB 标签材料")],
              ["ETIA", "E-8511 / E-8531 / E-8532TT / E-8731 (ESD)", ("Polyimide equivalents", "聚酰亚胺对应型号")],
              ["3M", "7811 / 7812", ("Matte white polyimide", "哑白聚酰亚胺")],
              ["Avery Dennison", "ADS1622/1684 · MZ2001W · AAG996 (ESD)", ("25–50 µm matte / gloss / ESD polyimide", "25–50 µm 哑 / 亮 / ESD 聚酰亚胺")]], zh)
        + _note(_t(("Cross-references are based on material-construction equivalence, not one-to-one official certification; the Apex series exceeds standard catalog polyimide in flux/cleaner resistance and process-temperature range. Verify ribbon, printing and cleaning chemistry by sample before production.",
                    "对应关系基于材料构造等效，非逐一官方认证；Apex 系列在助焊剂/清洗剂耐受与工艺温区上优于标准目录聚酰亚胺。量产前请以样品验证碳带、打印与清洗化学品。"), zh)))

    talk = _sec(_t(("Talk to a Specialist", "咨询专家"), zh),
        _p([("Tell us your reflow / wave profile, flux and cleaning chemistry, ESD requirements, application surface and barcode density, and ETIA will lock in the right Polyonics® construction and arrange free samples for process validation.",
             "告诉我们你的回流 / 波峰曲线、助焊剂与清洗化学品、ESD 要求、粘贴表面与条码密度，ETIA 将为你锁定合适的 Polyonics® 结构，并安排免费打样用于工艺验证。")], zh))

    body = s1 + s2 + s3 + s4 + s5 + s6 + talk + ('<div class="wrap">%s</div>' % cta(lang))
    crumb = [(("首页" if zh else "Home"), "/"), (("行业" if zh else "Industries"), "/industries/"),
             (("电子元器件标签" if zh else "Electronic Component Labels"), path)]
    meta_t = ("电子元器件标签｜耐 300°C 回流焊·波峰焊·强助焊剂 — Apex 系列｜ETIA（Polyonics®）" if zh
              else "Electronic Component Labels — 300°C Reflow, Wave-Solder & Strong-Flux Resistant | Apex Series | ETIA (Polyonics®)")
    meta_d = ("电子元器件标签材料，专为耐受 300°C 回流焊、波峰焊与强活性助焊剂、贯穿整个 PCB 组装工艺而设计。Polyonics® Apex 系列助焊剂耐受较上一代提升 72%，由 ETIA 以转换卷材或 OEM 材料供应。" if zh
              else "Electronic component label materials engineered to survive 300°C reflow, wave solder and aggressive flux across the entire PCB assembly process. The Polyonics® Apex series improves flux resistance 72% over the previous generation, supplied by ETIA as converted roll stock or OEM material.")
    write(lang, path, page(lang, path, meta_t, meta_d, _t(h1, zh), _t(lede, zh), body, crumb, active="products", trust=False))
    if lang == "en":
        URLS.append(path); track(path, "core")

# ==================================================================== APPLICATION NOTES
NOTES = [
 {"slug": "smt-reflow-wave-solder",
  "title": ("SMT Reflow & Wave-Solder High-Temperature Labels", "SMT 回流焊 / 波峰焊 高温标签"),
  "meta_t": ("SMT Reflow & Wave-Solder High-Temperature PCB Labels | Application Note | ETIA",
             "SMT 回流焊 / 波峰焊 高温 PCB 标签｜应用笔记｜ETIA"),
  "meta_d": ("Labels that survive 300°C reflow, wave solder, aggressive flux and harsh cleaning with a readable barcode. Polyonics® Apex polyimide, supplied by ETIA.",
             "耐 300°C 回流焊、波峰焊、强助焊剂与严苛清洗且条码可读的标签。Polyonics® Apex 聚酰亚胺，ETIA 供货。"),
  "overview": ("Through PCB assembly, test and later repair, the label must carry a traceable identity. Lead-free reflow, wave solder, aggressive active flux and high-pressure chemical cleaning act in turn — and the barcode must stay clear and scannable through all of it.",
               "PCB 在组装、测试到后期维修的全过程中，标签必须承载追溯身份。无铅回流焊、波峰焊、强活性助焊剂与高压化学清洗轮番作用，标签要在这一切之后仍保持条码清晰可扫。"),
  "challenge": ("Ordinary labels shrink, lift or yellow after reflow; the barcode becomes unreadable and traceability breaks — right at the most critical process step.",
                "普通标签在回流焊后收缩、翘起或变黄，条码无法识别，追溯就此中断 —— 而这恰恰发生在最关键的制程节点。"),
  "req": [("Withstand multiple passes at peak 300°C (572°F)", "耐峰值 300°C（572°F）多次过炉"),
          ("Resist no-clean / water-soluble / rosin flux and wave-solder attack", "耐免洗 / 水溶性 / 松香型助焊剂与波峰锡蚀"),
          ("Resist high-pressure water and chemical cleaning (IPA, MEK, aqueous cleaners)", "耐高压水洗 / 化学清洗（IPA、MEK、水基清洗剂）"),
          ("Support fine text and high-density Data Matrix / 2D codes", "面向细字与高密度 Data Matrix / 二维码"),
          ("Permanent adhesion to high-surface-energy PCB substrates", "对高表面能 PCB 基材永久粘接")],
  "solution": ("Polyonics® Apex-series polyimide (matte / semi-gloss / gloss) with a new-generation proprietary topcoat — no yellowing, no softening, abrasion-resistant; +72% flux resistance and +15% cleaner resistance over the previous generation. Gloss XF-101G suits high-density 2D codes; ultra-thin XF-616 suits BGA / fine-pitch.",
               "采用 Polyonics® Apex 系列聚酰亚胺（哑面 / 半光 / 亮面可选），配新一代专有涂层 —— 不泛黄、不软化、耐磨，助焊剂耐受较上一代 +72%、清洗剂耐受 +15%。亮面 XF-101G 适合高密度二维码，超薄 XF-616 适合 BGA / 细间距。"),
  "rec_head": [("Model", "型号"), ("Face", "表面"), ("Thickness", "厚度"), ("Temperature", "耐温"), ("Notes", "说明")],
  "rec_rows": [["XF-101M / XF-102M", ("Matte white", "哑白"), "1 / 2 mil", ("Up to 300°C", "最高 300°C"), ("General low-profile PCB ID", "通用低厚度 PCB 标识")],
               ["XF-101S / XF-102S", ("Semi-gloss white", "半光白"), "1 / 2 mil", ("Up to 300°C", "最高 300°C"), ("Balance of scanning & handling", "扫码与操作平衡")],
               ["XF-101G / XF-102G (APEX)", ("Gloss white", "亮光白"), "1 / 2 mil", ("Up to 300°C", "最高 300°C"), ("Sharpest for high-density 2D codes", "高密度二维码最锐利")],
               ["XF-616", ("Matte white, ultra-thin", "哑白，超薄"), "0.5 mil", ("Up to 300°C", "最高 300°C"), ("BGA / fine-pitch / tight clearance", "BGA / 细间距 / 有限间隙")]],
  "benefit": [("Barcode survives the whole line — reliable adhesion and scannability after multiple 300°C passes; traceability unbroken", "条码挺过整条产线 —— 300°C 多次过炉后仍可靠粘接、可扫，追溯不断链"),
              ("Harsher cleaning without smearing — +72% flux / +15% cleaner resistance, image fidelity preserved", "清洗更狠也不糊印 —— +72% 助焊剂 / +15% 清洗剂耐受，图像保真"),
              ("Fits dense boards — ultra-thin low profile clears low components and tight layouts", "贴得进密板 —— 超薄低厚度避开低矮元件与密集布局"),
              ("Right finish — gloss for fixed scanners, matte for anti-glare, semi-gloss for a balance", "选对表面 —— 固定扫码选亮面，防眩选哑面，操作平衡选半光")],
  "mkt_rows": [[("Polyonics® (featured here)", "Polyonics®（本页主推）"), "XF-101/102, XF-616", ("Apex ultra-high-performance PI", "Apex 超高性能 PI")],
               ["Brady", "B-729 / B-730 / B-768", ("Polyimide PCB labels", "聚酰亚胺 PCB 标签")],
               ["ETIA", "E-8511 / E-8531 / E-8532TT", ("Polyimide equivalents", "聚酰亚胺对应")],
               ["3M", "7811 / 7812", ("Matte white polyimide", "哑白聚酰亚胺")],
               ["Avery Dennison", "ADS1622 / ADS1684", ("25–50 µm matte / gloss PI", "25–50µm 哑 / 亮 PI")]]},
 {"slug": "esd-static-dissipative",
  "title": ("ESD Static-Dissipative PCB / Component Labels", "ESD 防静电 PCB / 元器件标签"),
  "meta_t": ("ESD Static-Dissipative Labels — ANSI/ESD S20.20 | Application Note | ETIA",
             "ESD 静电耗散标签｜ANSI/ESD S20.20｜应用笔记｜ETIA"),
  "meta_d": ("Static-dissipative, low-charging, halogen-free polyimide labels compliant with ANSI/ESD S20.20 and reflow-capable to 300°C. Polyonics® Apex ESD, supplied by ETIA.",
             "静电耗散、低起电、无卤聚酰亚胺标签，符合 ANSI/ESD S20.20，耐 300°C 回流。Polyonics® Apex ESD，ETIA 供货。"),
  "overview": ("Inside an ESD-protected area (EPA), anything that touches or comes near sensitive electronics must be static-safe — labels included. A label must both manage charge and be a durable, printable, high-temperature identifier.",
               "在 ESD 防护区（EPA）内，凡接触或靠近敏感电子的物品都必须静电安全 —— 标签也不例外。它既要管理电荷，又要是耐用、可打印的耐高温标识。"),
  "challenge": ("Ordinary labels accumulate and then discharge static, damaging sensitive semiconductors and ICs — becoming the very hazard the EPA exists to eliminate.",
                "普通标签会积累又释放静电，损坏敏感半导体与 IC，反而成为 EPA 要消除的隐患。"),
  "req": [("Surface resistance in the dissipative range (10⁶–10¹¹ Ω; XF-781 family 10⁹–10¹¹ Ω)", "表面电阻处于耗散范围（10⁶–10¹¹ Ω；XF-781 族 10⁹–10¹¹ Ω）"),
          ("Compliant with ANSI/ESD S20.20 (and ESD S541 / IEC 61340 / JEDEC JESD 625B systems)", "符合 ANSI/ESD S20.20（及 ESD S541 / IEC 61340 / JEDEC JESD 625B 体系）"),
          ("Low charge generation (peel / re-apply < 125 V)", "低起电（离型剥离 / 重贴 < 125 V）"),
          ("Withstand 260–300°C reflow, halogen-free", "耐 260–300°C 回流焊、无卤"),
          ("Static-dissipative adhesive and release liner (full-path charge management)", "静电耗散胶层与离型层（全链路电荷管理）")],
  "solution": ("Polyonics® Apex ESD polyimide — static-dissipative adhesive plus static-dissipative liner, low-charging PSA (<125 V), halogen-free, ANSI/ESD S20.20 compliant. Semi-gloss XF-101SE / matte XF-101ME for different scanning and anti-glare needs; XF-781/782 is the best-documented ESD semi-gloss.",
               "采用 Polyonics® Apex ESD 聚酰亚胺 —— 静电耗散胶 + 静电耗散离型层，低起电 PSA（<125 V）、无卤，符合 ANSI/ESD S20.20。半光 XF-101SE / 哑面 XF-101ME 满足不同扫码与防眩需求；XF-781/782 为文档最完整的 ESD 半光款。"),
  "rec_head": [("Model", "型号"), ("Face / Type", "表面 / 类型"), ("Thickness", "厚度"), ("Temperature", "耐温"), ("Notes", "说明")],
  "rec_rows": [["XF-101SE / XF-102SE", ("ESD semi-gloss white", "ESD 半光白"), "1 / 2 mil", ("Up to 300°C", "最高 300°C"), ("Apex ESD mainstay", "Apex ESD 主力")],
               ["XF-101ME", ("ESD matte white", "ESD 哑白"), "3 mil", ("Up to 300°C", "最高 300°C"), ("Anti-glare, thicker construction", "防眩、较厚结构")],
               ["XF-781 / XF-782", ("ESD semi-gloss white", "ESD 半光白"), "1 / 2 mil", ("−40 to 300°C", "−40~300°C"), ("10⁹–10¹¹ Ω, UL969, halogen-free", "10⁹–10¹¹ Ω，UL969、无卤")]],
  "benefit": [("Protects sensitive devices — the label manages charge instead of becoming a discharge source in the EPA", "保护敏感器件 —— 标签管理电荷，不在 EPA 内成为放电源"),
              ("Passes the ESD audit — dissipative facestock plus adhesive, compliant with the ANSI/ESD S20.20 system", "通过 ESD 审核 —— 耗散面材 + 胶层，符合 ANSI/ESD S20.20 体系"),
              ("Survives reflow — 300°C rated, ESD and heat resistance together", "过得了回流 —— 耐 300°C，ESD 与耐高温兼得"),
              ("Low-charging, halogen-free — peel / re-apply <125 V, meets sensitive-device cleanliness needs", "低起电、无卤 —— 剥离 / 重贴 <125 V，满足敏感器件洁净要求")],
  "mkt_rows": [[("Polyonics® (featured here)", "Polyonics®（本页主推）"), "XF-101SE / XF-102SE / XF-101ME / XF-781", ("Apex ESD polyimide", "Apex ESD 聚酰亚胺")],
               ["Brady", "B-718 / B-719 / B-722SE", ("Static-dissipative polyimide", "静电耗散聚酰亚胺")],
               ["ETIA", "E-8731 / E-8732", ("ESD polyimide equivalents", "ESD 聚酰亚胺对应")],
               ["Avery Dennison", "AAG996 (ADS1403)", ("ESD polyimide", "ESD 聚酰亚胺")],
               ["3M", "—", ("No direct ESD polyimide", "无直接 ESD 聚酰亚胺")]]},
 {"slug": "ul94-v0-flame-retardant",
  "title": ("UL94 V-0 Flame-Retardant Labels", "UL94 V-0 阻燃标签"),
  "meta_t": ("UL94 V-0 / VTM-0 Flame-Retardant Labels | Application Note | ETIA",
             "UL94 V-0 / VTM-0 阻燃标签｜应用笔记｜ETIA"),
  "meta_d": ("Flame-retardant labels rated UL94 V-0 / VTM-0 for electronics, batteries, harnesses and electrical components. Polyonics® XF-603 PI and XF-611 PET, supplied by ETIA.",
             "面向电子、电池、线束与电气元件的 UL94 V-0 / VTM-0 阻燃标签。Polyonics® XF-603 PI 与 XF-611 PET，ETIA 供货。"),
  "overview": ("Electronic equipment, batteries, wire harnesses and electrical components often require flame-retardant identification to meet product-safety and fire codes. A label must not fuel a fire or help it spread.",
               "电子设备、电池、线束与电气元件常要求阻燃标识，以满足产品安规与消防要求。标签在起火时不能助燃或助长火势蔓延。"),
  "challenge": ("Non-flame-retardant labels help spread fire and generate smoke, so the product fails UL / safety certification.",
                "非阻燃标签会助长火势蔓延、产生烟气，导致产品无法通过 UL / 安规认证。"),
  "req": [("UL94 V-0 / VTM-0 flame rating", "UL94 V-0 / VTM-0 阻燃等级"),
          ("Temperature resistance, electrical insulation, low smoke", "耐温、电气绝缘、低烟"),
          ("Compatible with electronic processing (reflow / cleaning)", "兼容电子制程（回流 / 清洗）"),
          ("Printable and traceable", "可打印、可追溯")],
  "solution": ("Polyonics® XF-603 flame-retardant polyimide (UL94 VTM-0, 300°C, cross-references Brady B-8088A); for lower-temperature / PET needs, XF-611 flame-retardant PET (UL94 VTM-0, cross-references Brady B-5109FR).",
               "采用 Polyonics® XF-603 阻燃聚酰亚胺（符合 UL94 VTM-0，耐 300°C，对标 Brady B-8088A）；较低温 / PET 需求可选 XF-611 阻燃 PET（UL94 VTM-0，对标 Brady B-5109FR）。"),
  "rec_head": [("Model", "型号"), ("Material", "材料"), ("Thickness", "厚度"), ("Temperature", "耐温"), ("Flame", "阻燃"), ("Notes", "说明")],
  "rec_rows": [["XF-603", ("Polyimide (PI)", "聚酰亚胺 PI"), "1 mil", ("Up to 300°C", "最高 300°C"), "UL94 VTM-0", ("Electronic flame-retardant PCB ID", "电子阻燃 PCB 标识")],
               ["XF-611", ("Polyester (PET)", "聚酯 PET"), "1.5 mil", ("Up to 150°C", "最高 150°C"), "UL94 VTM-0", ("Lower-temp / cable flame-retardant", "较低温 / 线缆阻燃")]],
  "benefit": [("Passes safety codes — UL94 V-0/VTM-0 flame rating supports product certification", "过安规 —— UL94 V-0/VTM-0 阻燃，助力产品认证"),
              ("Won't fuel fire, low smoke — reduces fire-spread and smoke risk", "不助燃、低烟 —— 降低火势蔓延与烟气风险"),
              ("Temperature too — the PI grade is rated 300°C, usable in reflow", "兼顾耐温 —— PI 款耐 300°C，回流制程可用"),
              ("Traceable — flame-retardant while keeping the barcode / ID clear", "可追溯 —— 阻燃同时保持条码 / 标识清晰")],
  "mkt_rows": [[("Polyonics® (featured here)", "Polyonics®（本页主推）"), "XF-603 (PI) · XF-611 (PET)", ("UL94 VTM-0 flame-retardant", "UL94 VTM-0 阻燃")],
               ["Brady", "B-8088A (PI) · B-5109FR (PET)", ("Flame-retardant label materials", "阻燃标签材料")],
               ["ETIA", "E-2931 / E-2932", ("UL94 VTM-0 cable flame-retardant", "UL94 VTM-0 线缆阻燃")],
               ["3M / Avery", "—", ("No direct UL94 flame-retardant label", "无直接 UL94 阻燃标签款")]]},
]
NOTE_IND = ("Electronics & PCB", "电子与PCB")

def build_note(lang, n):
    zh = (lang == "zh")
    path = "/application-notes/%s/" % n["slug"]
    body = (
        _sec(_t(("The Challenge", "应用挑战"), zh), _p([n["challenge"]], zh), "var(--tint-green)")
        + _sec(_t(("Performance Requirements", "性能要求"), zh), _ul(n["req"], zh))
        + _sec(_t(("The ETIA Solution", "ETIA 方案"), zh), _p([n["solution"]], zh), "var(--tint-blue)")
        + _sec(_t(("Recommended Products", "推荐产品"), zh), _tbl(n["rec_head"], n["rec_rows"], zh))
        + _sec(_t(("Customer Benefits", "客户收益"), zh), _ul(n["benefit"], zh))
        + _sec(_t(("Market Cross-Reference", "市场对应型号"), zh),
               _tbl([("Brand", "品牌"), ("Corresponding model", "对应型号"), ("Notes", "说明")], n["mkt_rows"], zh)
               + _note(_t(MKT_DISCLAIMER, zh)))
        + ('<div class="wrap">%s</div>' % cta(lang)))
    crumb = [(("首页" if zh else "Home"), "/"),
             (("应用笔记" if zh else "Application Notes"), "/application-notes/"),
             (_t(n["title"], zh), path)]
    write(lang, path, page(lang, path, _t(n["meta_t"], zh), _t(n["meta_d"], zh),
                           _t(n["title"], zh), _t(n["overview"], zh), body, crumb, active="notes", trust=False))
    if lang == "en":
        URLS.append(path); track(path, "core")

# Published notes for the Application Notes index (slug, title en/zh, industry label en/zh)
PUBLISHED = [(n["slug"], n["title"][0], n["title"][1], NOTE_IND[0], NOTE_IND[1]) for n in NOTES]

def main():
    for lang in LANGS:
        build_ecl(lang)
        for n in NOTES:
            build_note(lang, n)

if __name__ == "__main__":
    main()
