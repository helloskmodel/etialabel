#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Industry LANDING pages (first layer). Data-driven brochure layout, EN + /cn.
Runs after the section generators so it owns /industries/<slug>/index.html.
Add more industries by adding entries to LANDINGS."""
import gen_heatproof as hp
from gen_heatproof import esc, L, page, write, cta, LANGS

URLS = []

LANDINGS = {
 "electronics-pcb": {
  "path": "/industries/electronics-pcb/",
  "app_urls": [
    "/industries/electronics-pcb/reflow-polyimide-labels/",
    "/industries/electronics-pcb/non-reflow-polyimide-labels/",
    "/industries/electronics-pcb/post-process-labels/",
    "/industries/electronics-pcb/auto-dispense-labels/",
    "/industries/electronics-pcb/masking-dots-inspection-arrows/",
    "/industries/electronics-pcb/laser-markable-labels/",
  ],
  "en": {
    "eyebrow": "Electronics & PCB",
    "h1": "Label Materials for Electronics and PCB Manufacturing",
    "hero": "Reliable identification must survive more than the finished product environment. It may need to remain readable through soldering, flux, aggressive cleaning, static-controlled handling and automated assembly. ETIA supplies specialty label materials and helps match each construction to the actual manufacturing process.",
    "cta1": "Discuss Your Application", "cta2": "Request Samples",
    "intro_h": "Identification Through the Manufacturing Process",
    "intro": [
      "PCB and electronics labels may be applied before, during or after manufacturing. Their exposure changes according to the point of application. A pre-process label may encounter reflow or wave solder, rapid temperature change, flux and repeated cleaning. A post-process label may require chemical resistance, strong adhesion and durable traceability throughout assembly and service life. Labels used in ESD-controlled areas may also require static-dissipative constructions, while automated placement introduces additional requirements for release consistency, stiffness, curl and liner performance.",
      "For this reason, material selection should begin with the process — not only with the highest stated temperature. Facestock, adhesive, print topcoat, ribbon, release liner, PCB surface and exposure sequence must work as a complete identification system.",
    ],
    "challenges_h": "Manufacturing Challenges",
    "challenges": [
      ("High-Temperature Processing", "Labels applied before reflow or wave solder must remain attached, dimensionally stable and readable through rapid heating and cooling. Peak temperature, dwell time, solder contact and label position all influence the required construction."),
      ("Flux, Solvents and Harsh Wash", "Cleaning chemistry can affect the facestock, adhesive and printed image differently. The number of wash cycles, cleaner concentration, spray pressure and drying process should be considered together."),
      ("ESD-Controlled Manufacturing", "Sensitive electronic assemblies may require static-dissipative facestocks, adhesives or release liners. ESD performance must be confirmed for the complete construction and intended handling process."),
      ("Small Components and Dense Codes", "Compact assemblies require thin materials and reliable high-contrast printing. Barcode density, available marking area, surface finish and scanner performance should be verified before production."),
      ("Automated Dispensing", "Successful automatic placement depends on more than label durability. Label stiffness, die-cut quality, liner release, curl, roll direction and applicator settings can determine whether a material dispenses consistently."),
      ("Long-Term Traceability", "Serial numbers, lot codes and process data must remain readable through downstream assembly, inspection and the required product lifecycle."),
    ],
    "offers_h": "What ETIA Offers",
    "offers": [
      ("High-Temperature Polyimide Materials", "Polyimide constructions for PCB identification through reflow, wave solder, high heat and demanding manufacturing processes."),
      ("Harsh-Wash-Resistant Materials", "Constructions selected for exposure to flux, solvents, aqueous cleaning and repeated wash cycles."),
      ("Static-Dissipative Constructions", "ESD-aware options for sensitive electronics and controlled manufacturing environments."),
      ("Automated-Application Materials", "Materials evaluated for dispensing performance, liner release, dimensional stability and conversion requirements."),
      ("Post-Process Identification", "Polyester, polyimide and other durable constructions for labels applied after soldering or major thermal processing."),
      ("Laser-Markable Materials", "Specialty materials designed to create durable variable information through a compatible laser-marking process."),
      ("Masking and Inspection Materials", "Temporary masking, process-control dots and visual inspection indicators selected according to temperature, chemistry and removability requirements."),
    ],
    "apps_h": "Applications We Support",
    "apps": [
      ("Reflow and Wave-Solder PCB Labels", "Polyimide materials for identification applied before soldering and cleaning. Selection depends on peak temperature, dwell time, solder exposure, wash chemistry, label profile and ESD requirements.", "Explore Reflow and Wave-Solder Labels"),
      ("Non-Reflow PCB Labels", "Materials for applications involving cleaning, solvents and moderate heat where the label does not travel through a full reflow profile.", "Explore Non-Reflow PCB Labels"),
      ("Post-Process Circuit Board Labels", "Durable identification applied after the most severe manufacturing stages, with selection focused on the finished surface, chemical exposure and required lifecycle.", "Explore Post-Process Labels"),
      ("Auto-Dispense PCB Labels", "Label constructions and converting formats evaluated for reliable automated dispensing and placement.", "Explore Auto-Dispense Labels"),
      ("PCB Masking and Inspection Materials", "Temporary masking dots and inspection indicators for process control, protection and visual workflow management.", "Explore Masking and Inspection Materials"),
      ("Laser-Markable Label Materials", "Materials designed for permanent, high-contrast variable information generated through a qualified laser and material combination.", "Explore Laser-Markable Materials"),
    ],
    "dir_h": "Two Product Directions",
    "dir": [
      ("Polyonics — Performance for Demanding Processes", "Polyonics materials provide specialized constructions for high heat, harsh wash, low-profile identification and ESD-controlled electronics manufacturing. ETIA supplies selected Polyonics products and supports application review, sample qualification and format conversion.", "Explore Polyonics PCB Materials"),
      ("ETIA — Application-Matched Practical Value", "ETIA materials provide practical options for customers balancing process requirements, format flexibility, supply planning and total material cost. Final selection is based on the actual manufacturing sequence and customer testing.", "Explore ETIA PCB Materials"),
    ],
    "steps_h": "How We Support Selection",
    "steps": [
      ("01", "Understand the Process", "We review the application point, PCB surface, peak and continuous temperature, dwell time, solder contact, cleaning chemistry, ESD requirements, print method, barcode density and lifecycle."),
      ("02", "Match the Construction", "We compare facestock, adhesive, topcoat, liner and print-system compatibility against the required process."),
      ("03", "Arrange Samples", "Candidate materials are prepared in a suitable format for print, adhesion and process testing."),
      ("04", "Confirm Before Production", "The selected construction should be tested through the customer's complete manufacturing sequence before production approval."),
    ],
    "why_h": "Why ETIA",
    "why": [
      "Application-based material selection",
      "Access to specialized label constructions",
      "Polyonics and ETIA product options",
      "Sample and qualification support",
      "Flexible sizes, formats and converting",
      "Quality inspection and traceability",
      "Supply planning and long-term application support",
    ],
    "close_h": "Select by the Real Process",
    "close": "The most heat-resistant material is not automatically the best material. Reliable identification depends on matching the complete construction to the real process. Share your temperature profile, chemistry, surface, print method and application timing with ETIA so that the selection can begin from the conditions that matter.",
    "fcta_h": "Find the Right Material for Your PCB Process",
    "fcta_body": "Discuss your manufacturing conditions with ETIA and request materials for application testing.",
    "fcta1": "Talk to an Application Specialist", "fcta2": "Request Samples",
    "meta_title": "Electronics & PCB Label Materials for Manufacturing Processes | ETIA",
    "meta_desc": "Durable label materials for PCB manufacturing, reflow, wave solder, harsh wash, ESD control, automated dispensing and post-process traceability. ETIA supports selection, samples, converting and supply.",
  },
  "zh": {
    "eyebrow": "电子与PCB",
    "h1": "面向电子与PCB制造的标签材料",
    "hero": "可靠标识不仅需要适应成品的使用环境，还可能需要经历焊接、助焊剂、严苛清洗、静电控制及自动化装配。ETIA供应特种标签材料，并根据客户的实际制造流程匹配合适的材料结构。",
    "cta1": "沟通应用需求", "cta2": "申请样品",
    "intro_h": "贯穿制造流程的可靠标识",
    "intro": [
      "电子与PCB标签可能在制造前、制造过程中或制造完成后贴附，不同贴标阶段对应的工况并不相同。制程前标签可能需要经历回流焊或波峰焊、快速温度变化、助焊剂及多次清洗；后制程标签则更关注耐化学性、粘接可靠性以及装配和使用周期内的持续追溯。ESD控制区域还可能需要静电耗散结构；自动贴标则会增加对离型稳定性、挺度、翘曲和底纸性能的要求。",
      "因此，材料选型应从真实工艺开始，而不能只比较标称最高耐温。面材、胶黏剂、打印涂层、碳带、离型底纸、PCB表面及完整的暴露顺序需要作为一个标识系统共同验证。",
    ],
    "challenges_h": "制造工艺中的标识挑战",
    "challenges": [
      ("高温制程", "在回流焊或波峰焊之前贴附的标签，需要经历快速升温和降温后仍保持粘接、尺寸稳定及信息可读。峰值温度、持续时间、焊料接触情况及贴标位置都会影响材料选择。"),
      ("助焊剂、溶剂与严苛清洗", "清洗介质可能分别影响面材、胶黏剂和打印图像。清洗次数、介质浓度、喷淋压力及干燥流程需要综合评估。"),
      ("ESD控制制造", "敏感电子组件可能要求面材、胶黏剂或离型底纸具备静电耗散性能。ESD表现需要结合完整材料结构和实际操作流程确认。"),
      ("小型组件与高密度条码", "紧凑型组件需要薄型材料和稳定的高对比度打印。量产前应确认条码密度、可用贴标面积、表面光泽及扫描设备的适配性。"),
      ("自动贴标", "自动贴标是否稳定不仅取决于材料耐久性。材料挺度、模切质量、离型力、翘曲、出标方向及设备参数都会影响连续出标效果。"),
      ("长期追溯", "序列号、批次信息及制程数据需要在后续装配、检测及规定的产品生命周期内保持清晰可读。"),
    ],
    "offers_h": "ETIA可以提供",
    "offers": [
      ("耐高温聚酰亚胺材料", "适用于PCB回流焊、波峰焊、高温及严苛制造流程的聚酰亚胺标签结构。"),
      ("耐严苛清洗材料", "针对助焊剂、溶剂、水基清洗及多次清洗工艺进行选型的材料结构。"),
      ("静电耗散材料结构", "适用于敏感电子组件和ESD控制制造环境的材料选择。"),
      ("自动贴标材料", "根据出标性能、离型稳定性、尺寸稳定性及模切加工要求进行评估的材料结构。"),
      ("后制程产品标识", "适用于焊接或主要热制程完成后贴附的聚酯、聚酰亚胺及其他耐久材料。"),
      ("激光打标材料", "通过适配的激光工艺生成耐久可变信息的特种标签材料。"),
      ("遮蔽与检验材料", "根据温度、化学介质及可移除要求选用的临时遮蔽圆点、制程控制标签和目视检验标识。"),
    ],
    "apps_h": "我们支持的应用",
    "apps": [
      ("回流焊与波峰焊PCB标签", "适用于焊接和清洗前贴附的聚酰亚胺材料。选型需要考虑峰值温度、持续时间、焊料暴露、清洗介质、标签厚度及ESD要求。", "查看回流焊与波峰焊标签"),
      ("非回流焊PCB标签", "适用于严苛清洗、溶剂和中等温度，但不需要经历完整回流焊温度曲线的材料。", "查看非回流焊PCB标签"),
      ("PCB后制程标签", "在主要严苛制造工序完成后贴附的耐久标识，重点考虑成品表面、化学暴露及生命周期要求。", "查看PCB后制程标签"),
      ("PCB自动贴标材料", "针对自动出标和贴附稳定性进行评估的标签结构与模切形式。", "查看自动贴标材料"),
      ("PCB遮蔽与检验材料", "用于制程保护、流程控制及目视检验的临时遮蔽圆点和检验指示标签。", "查看遮蔽与检验材料"),
      ("激光打标标签材料", "通过经过匹配验证的激光与材料组合生成高对比度、耐久可变信息的材料。", "查看激光打标材料"),
    ],
    "dir_h": "两种产品方向",
    "dir": [
      ("Polyonics —— 面向严苛制程的性能方案", "Polyonics针对高温、严苛清洗、薄型标识及ESD控制电子制造提供专业材料结构。ETIA供应相关Polyonics产品，并支持应用评估、样品验证及规格转换。", "查看Polyonics PCB材料"),
      ("ETIA —— 兼顾应用要求与综合成本", "ETIA材料面向需要综合考虑工艺要求、规格灵活性、供应安排及材料成本的客户。最终选型以真实制造流程及客户测试结果为依据。", "查看ETIA PCB材料"),
    ],
    "steps_h": "ETIA选型支持流程",
    "steps": [
      ("01", "了解实际工艺", "确认贴标阶段、PCB表面、峰值及持续温度、持续时间、焊料接触、清洗介质、ESD要求、打印方式、条码密度和使用周期。"),
      ("02", "匹配材料结构", "根据工艺要求比较面材、胶黏剂、打印涂层、底纸及打印系统兼容性。"),
      ("03", "安排样品", "将候选材料加工成合适形式，用于打印、粘接及完整制程测试。"),
      ("04", "量产前确认", "所选材料应在客户完整制造流程中完成测试后，再进行量产确认。"),
    ],
    "why_h": "为什么选择ETIA",
    "why": [
      "从实际应用出发进行材料选型",
      "提供多种特种标签材料结构",
      "提供Polyonics及ETIA产品方向",
      "支持样品与应用验证",
      "支持灵活尺寸、规格和模切加工",
      "质量检测与全过程追溯",
      "供应规划与长期应用支持",
    ],
    "close_h": "根据真实工艺选材",
    "close": "最高耐温的材料不一定是最合适的材料。可靠标识来自完整材料结构与实际工艺的正确匹配。向ETIA提供温度曲线、化学介质、贴附表面、打印方式及贴标阶段，我们将从真正影响应用的条件开始选型。",
    "fcta_h": "为您的PCB制造流程匹配合适材料",
    "fcta_body": "与ETIA沟通实际制造工况，并申请材料进行应用测试。",
    "fcta1": "联系应用选型人员", "fcta2": "申请样品",
    "meta_title": "电子与PCB制造标签材料｜回流焊、波峰焊、耐清洗与ESD应用｜ETIA",
    "meta_desc": "面向PCB制造、回流焊、波峰焊、严苛清洗、ESD控制、自动贴标及后制程追溯的耐久标签材料。ETIA提供材料选型、样品测试、模切加工与供应支持。",
  },
 },
}


def cards_grid(items):
    return '<div class="grid">%s</div>' % "".join(
        '<div class="card"><h3>%s</h3><p>%s</p></div>' % (esc(t), esc(dsc)) for t, dsc in items)

def build_landing(lang, slug):
    d = LANDINGS[slug][lang]
    path = LANDINGS[slug]["path"]
    contact = L(lang, "/contact/")
    def sec(bg, inner):
        st = ' style="background:%s"' % bg if bg else ""
        return '<section class="blk"%s><div class="wrap">%s</div></section>' % (st, inner)

    top = ('<div class="btns" style="margin-bottom:22px"><a class="btn pri" href="%s">%s</a>'
           '<a class="btn sec" href="%s">%s</a></div>'
           '<h2>%s</h2>%s') % (
        contact, esc(d["cta1"]), contact, esc(d["cta2"]),
        esc(d["intro_h"]), "".join('<p style="color:var(--mut);max-width:60em;margin-bottom:12px">%s</p>' % esc(p) for p in d["intro"]))

    challenges = '<h2>%s</h2>%s' % (esc(d["challenges_h"]), cards_grid(d["challenges"]))
    offers = '<h2>%s</h2>%s' % (esc(d["offers_h"]), cards_grid(d["offers"]))

    app_urls = LANDINGS[slug].get("app_urls", [])
    app_cards = "".join(
        '<a class="card" href="%s"><h3>%s</h3><p>%s</p><div class="go" style="color:var(--blue);font-weight:700;font-size:13.5px;margin-top:12px">%s →</div></a>'
        % (L(lang, app_urls[i]) if i < len(app_urls) else contact, esc(t), esc(dsc), esc(cta_))
        for i, (t, dsc, cta_) in enumerate(d["apps"]))
    apps = '<h2>%s</h2><div class="grid">%s</div>' % (esc(d["apps_h"]), app_cards)

    dir_cards = "".join(
        '<div class="card"><h3>%s</h3><p>%s</p><div style="margin-top:14px"><a class="btn sec" href="%s">%s →</a></div></div>'
        % (esc(t), esc(dsc), contact, esc(cta_)) for t, dsc, cta_ in d["dir"])
    directions = '<h2>%s</h2><div class="two">%s</div>' % (esc(d["dir_h"]), dir_cards)

    step_cards = "".join(
        '<div class="card"><h3><span style="color:var(--green-d)">%s</span> &nbsp;%s</h3><p>%s</p></div>'
        % (esc(n), esc(t), esc(dsc)) for n, t, dsc in d["steps"])
    steps = '<h2>%s</h2><div class="grid">%s</div>' % (esc(d["steps_h"]), step_cards)

    why = '<h2>%s</h2><ul class="checks">%s</ul>' % (
        esc(d["why_h"]), "".join('<li>%s</li>' % esc(x) for x in d["why"]))
    close = '<h2>%s</h2><p style="color:var(--mut);max-width:60em">%s</p>' % (esc(d["close_h"]), esc(d["close"]))

    final = ('<div class="wrap"><div class="cta"><div class="ic">⚡</div><h3>%s</h3><p>%s</p>'
             '<div class="btns"><a class="btn pri" href="%s">%s</a>'
             '<a class="btn on-dark" href="%s">%s</a></div></div></div>') % (
        esc(d["fcta_h"]), esc(d["fcta_body"]), contact, esc(d["fcta1"]), contact, esc(d["fcta2"]))

    body = (sec("", top)
            + sec("var(--tint-green)", challenges)
            + sec("", offers)
            + sec("var(--tint-blue)", apps)
            + sec("", directions)
            + sec("var(--tint-green)", steps)
            + sec("", why)
            + sec("", close)
            + final)

    crumb = [("Home", "/"), ("Applications", "/industries/"), (d["eyebrow"], path)]
    write(lang, path, page(lang, path, d["meta_title"], d["meta_desc"],
                           d["h1"], d["hero"], body, crumb, active="industries"))
    if lang == "en":
        URLS.append(path)


# ---- Browse: By Environment (Products axis) ----
BY_ENV = [
    ("Oil-Resistant Labels", "耐油污标签"),
    ("ESD-Safe Labels", "抗静电标签"),
    ("Laser-Markable Labels", "激光打标标签"),
    ("Abrasion-Resistant Labels", "耐磨标签"),
    ("Cryogenic Labels", "深低温标签"),
    ("Moisture-Resistant Labels", "耐潮湿标签"),
    ("Chemical-Resistant Labels", "耐化学标签"),
    ("Heat-Resistant Labels", "耐高温标签"),
    ("Sterilization-Resistant Labels", "耐灭菌标签"),
]

def build_by_environment(lang):
    zh = (lang == "zh")
    contact = L(lang, "/contact/")
    cards = "".join(
        '<a class="card" href="%s"><h3>%s</h3><div class="go" style="color:var(--blue);font-weight:700;font-size:13.5px;margin-top:10px">%s →</div></a>'
        % (contact, esc(z if zh else e), ("申请样品" if zh else "Request Samples")) for e, z in BY_ENV)
    body = ('<section class="blk"><div class="wrap"><div class="grid">%s</div></div></section>'
            '<div class="wrap">%s</div>') % (cards, cta(lang))
    path = "/products/by-environment/"
    crumb = [("Home", "/"), ("Products", "/products/"), ("By Environment" if not zh else "按环境", path)]
    write(lang, path, page(lang, path,
          ("按环境选择标签材料 | ETIA" if zh else "Label Materials by Environment | ETIA"),
          ("按使用环境选择标签材料：耐油污、抗静电、激光打标、耐磨、深低温、耐潮湿、耐化学、耐高温、耐灭菌。" if zh
           else "Select label materials by environment: oil, ESD, laser-marking, abrasion, cryogenic, moisture, chemical, heat and sterilization."),
          ("按环境" if zh else "By Environment"),
          ("按使用环境快速定位合适的标签材料 —— 具体型号由 ETIA 依据真实工况匹配。" if zh
           else "Find the right label material by the environment it must survive — matched to your real conditions by ETIA."),
          body, crumb, active="products"))
    if lang == "en":
        URLS.append(path)


BY_FEATURE = [
    ("Tamper-Evident Labels", "防拆标签"),
    ("Removable Labels", "可移除标签"),
]

BY_MATERIAL = [
    ("Polyimide — Heat-Resistant", "聚酰亚胺 · 耐高温", "/materials/polyimide-pi-label-materials/"),
]

# By Application axis = the six industries (landing pages)
APPS_AXIS = [
    ("Electronics & PCB", "电子与PCB", "/industries/electronics-pcb/"),
    ("Metals & Ceramics", "金属与陶瓷", "/industries/steel/"),
    ("Medical & Laboratory", "医疗与实验室", "/industries/healthcare-life-sciences/"),
    ("Automotive & Tire", "汽车与轮胎", "/industries/automotive-label-materials/"),
    ("Wire & Cable", "电线与电缆", "/industries/wire-cable/"),
    ("Outdoor & Energy", "户外与能源", "/industries/outdoor-energy/"),
]

def build_by_feature(lang):
    zh = (lang == "zh")
    contact = L(lang, "/contact/")
    cards = "".join(
        '<a class="card" href="%s"><h3>%s</h3><div class="go" style="color:var(--blue);font-weight:700;font-size:13.5px;margin-top:10px">%s →</div></a>'
        % (contact, esc(z if zh else e), ("申请样品" if zh else "Request Samples")) for e, z in BY_FEATURE)
    body = ('<section class="blk"><div class="wrap"><div class="grid">%s</div></div></section>'
            '<div class="wrap">%s</div>') % (cards, cta(lang))
    path = "/products/by-feature/"
    crumb = [("Home", "/"), ("Products", "/products/"), ("By Feature" if not zh else "按特性", path)]
    write(lang, path, page(lang, path,
          ("按特性选择标签材料 | ETIA" if zh else "Label Materials by Feature | ETIA"),
          ("按功能特性选择标签:防拆、可移除等 —— 具体型号由 ETIA 依据真实应用匹配。" if zh
           else "Select labels by feature: tamper-evident, removable and more — matched to your application by ETIA."),
          ("按特性" if zh else "By Feature"),
          ("按功能特性快速定位合适的标签材料。" if zh
           else "Find the right label material by the feature you need."),
          body, crumb, active="products"))
    if lang == "en":
        URLS.append(path)

def build_products_overview(lang):
    zh = (lang == "zh")
    def axis(head_e, head_z, sub_e, sub_z, items, bg):
        cards = "".join(
            '<a class="card" href="%s"><h3>%s</h3></a>' % (L(lang, url), esc(z if zh else e))
            for e, z, url in items)
        st = ' style="background:%s"' % bg if bg else ""
        return ('<section class="blk"%s><div class="wrap"><div class="eyebrow">%s</div><h2>%s</h2>'
                '<div class="sub">%s</div><div class="grid">%s</div></div></section>') % (
            st, esc(head_z if zh else head_e).upper() if not zh else esc(head_z),
            esc((head_z if zh else head_e)), esc(sub_z if zh else sub_e), cards)
    env_items = [(e, z, "/products/by-environment/") for e, z in BY_ENV]
    feat_items = [(e, z, "/products/by-feature/") for e, z in BY_FEATURE]
    body = (
        axis("By Application", "按应用", "Start from your industry and process.", "从您的行业与工艺出发。", APPS_AXIS, "") +
        axis("By Environment", "按环境", "Start from the condition the label must survive.", "从标签需要承受的环境出发。", env_items, "var(--tint-green)") +
        axis("By Feature", "按特性", "Start from the functional property you need.", "从您需要的功能特性出发。", feat_items, "") +
        axis("By Material", "按材料", "Start from the substrate.", "从基材出发。", BY_MATERIAL, "var(--tint-blue)") +
        '<div class="wrap">%s</div>' % cta(lang))
    path = "/products/"
    crumb = [("Home", "/"), ("Products", path)]
    write(lang, path, page(lang, path,
          ("产品与方案 | ETIA" if zh else "Products & Solutions | ETIA"),
          ("按应用、环境、特性与材料四种方式浏览 ETIA 特种标签材料。" if zh
           else "Browse ETIA specialty label materials four ways — by application, environment, feature and material."),
          ("产品与方案" if zh else "Products & Solutions"),
          ("四种浏览方式,快速找到适合您应用的标签材料。" if zh
           else "Four ways to browse — find the label material that fits your application."),
          body, crumb, active="products"))
    if lang == "en":
        URLS.append(path)

def build_application_notes(lang):
    zh = (lang == "zh")
    # Browse chips: by industry (6) + by environment (9) — articles get tagged into these.
    # Application Notes is an independent SEO article library — tags organize notes, they do NOT link to products.
    ind_chips = "".join('<span class="pill">%s</span>' % esc(z if zh else e) for e, z, u in APPS_AXIS)
    env_chips = "".join('<span class="pill tag">%s</span>' % esc(z if zh else e) for e, z in BY_ENV)
    body = (
        '<section class="blk"><div class="wrap">'
        '<h2>%s</h2><div class="xlinks">%s</div>'
        '<h2 style="margin-top:26px">%s</h2><div class="xlinks">%s</div>'
        '<div class="verify" style="margin-top:22px">%s</div></div></section>'
        '<div class="wrap">%s</div>') % (
        ("按行业浏览" if zh else "Browse by Industry"), ind_chips,
        ("按环境浏览" if zh else "Browse by Environment"), env_chips,
        ("应用笔记正在陆续发布（约 40 篇，按行业 / 应用 / 环境标记）。需要特定主题资料请联系 ETIA。" if zh
         else "Application notes are being published (around 40, tagged by industry / application / environment). Contact ETIA for a specific topic."),
        cta(lang))
    path = "/application-notes/"
    crumb = [("Home", "/"), ("Application Notes" if not zh else "应用笔记", path)]
    write(lang, path, page(lang, path,
          ("应用笔记 | ETIA" if zh else "Application Notes | ETIA"),
          ("面向严苛标识应用的技术笔记与选型参考，按行业、应用与环境组织。" if zh
           else "Technical application notes and selection references for demanding identification, organized by industry, application and environment."),
          ("应用笔记" if zh else "Application Notes"),
          ("按行业、应用与环境组织的标签应用知识库 —— 帮助您在量产前选对材料。" if zh
           else "A library of label application knowledge — organized by industry, application and environment."),
          body, crumb, active="notes"))
    if lang == "en":
        URLS.append(path)

def main():
    for slug in LANDINGS:
        for lang in LANGS:
            build_landing(lang, slug)
    for lang in LANGS:
        build_by_environment(lang)
        build_by_feature(lang)
        build_products_overview(lang)
        build_application_notes(lang)


if __name__ == "__main__":
    main()
