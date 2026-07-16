#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Industry LANDING pages (first layer). Data-driven brochure layout, EN + /cn.
Runs after the section generators so it owns /industries/<slug>/index.html.
Add more industries by adding entries to LANDINGS."""
import os, json
import gen_heatproof as hp
from gen_heatproof import esc, L, page, write, cta, LANGS

_PCBD = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "pcb.json"), encoding="utf-8"))
PCB_CATS = {c["slug"]: c for c in _PCBD["categories"]}
PCB_PROD = _PCBD["products"]
PCB_MKT = _PCBD.get("category_market", {})

def build_pcb_category(lang, cat_slug):
    """Application page (layer 2): short intro + compact facets + product list.
    Labels all look alike, so NO product images — hoenle style: name + material
    construction + use description + spec chips."""
    zh = (lang == "zh")
    cat = PCB_CATS[cat_slug]
    prods = [p for p in PCB_PROD if cat_slug in p.get("application_categories", [])]
    contact = L(lang, "/contact/")
    cards = ""
    if prods:
        colors = sorted({p["film_color"] for p in prods if p.get("film_color") and p["film_color"] != "—"})
        finishes = sorted({p["finish"] for p in prods if p.get("finish") and p["finish"] != "—"})
        has_esd = any(p.get("esd") for p in prods)
        def fg(title, name, values):
            if not values: return ""
            boxes = "".join('<label><input type="checkbox" onchange="etaFilter(this)" data-fg="%s" data-fv="%s">%s</label>' % (name, esc(v), esc(v)) for v in values)
            return '<div class="fgroup"><h4>%s</h4>%s</div>' % (esc(title), boxes)
        facets = fg(("颜色" if zh else "Color"), "color", colors) + fg(("表面" if zh else "Finish"), "finish", finishes)
        if has_esd:
            facets += '<div class="fgroup"><h4>ESD</h4><label><input type="checkbox" onchange="etaFilter(this)" data-fg="esd" data-fv="1">%s</label></div>' % ("抗静电" if zh else "ESD-Safe")
        for p in prods:
            c = p.get("film_color", ""); fin = p.get("finish", "")
            meta = ""
            if c and c != "—": meta += '<span>%s</span>' % esc(c)
            if fin and fin != "—": meta += '<span>%s</span>' % esc(fin)
            if p.get("heat_tier"): meta += '<span>%s</span>' % esc(p["heat_tier"])
            if p.get("esd"): meta += '<span class="esd">ESD-Safe</span>'
            constr = p.get("construction", "") or ""
            desc = p.get("brochure_direction_zh" if zh else "brochure_direction_en", "") or ""
            url = L(lang, "/products/%s/" % p["slug"])
            cards += ('<div class="prow" data-color="%s" data-finish="%s" data-esd="%s">'
                      '<h3><a href="%s">%s</a></h3>'
                      '%s<p>%s</p><div class="pmeta">%s</div>'
                      '<a class="plink" href="%s">%s →</a></div>') % (
                esc(c if c != "—" else ""), esc(fin if fin != "—" else ""), ("1" if p.get("esd") else ""),
                url, esc(p["product_name"]),
                ('<div class="pconstr">%s</div>' % esc(constr)) if constr else "",
                esc(desc), meta,
                url, ("查看产品 / 申请样品" if zh else "View Product / Request Sample"))
        n = len(prods)
    else:
        # No individual product entries yet — render the market-equivalent categories as rows.
        facets = ""
        rows = PCB_MKT.get(cat_slug, [])
        for r in rows:
            eqs = [("Polyonics", r.get("polyonics")), ("ETIA", r.get("etia")),
                   ("Brady", r.get("brady")), ("3M", r.get("3m"))]
            meta = "".join('<span>%s %s</span>' % (esc(b), esc(v)) for b, v in eqs if v and v not in ("—", "on request", None))
            title = r.get("cat_zh" if zh else "cat_en", "")
            desc = ("根据实际工艺与可移除/残胶要求匹配具体型号，最终由样品确认；请联系 ETIA 索取规格。" if zh
                    else "Specific construction is matched to your process and removability/residue requirements, to be confirmed by sample; contact ETIA for the specification.")
            cards += ('<div class="prow"><h3>%s</h3><p>%s</p><div class="pmeta">%s</div>'
                      '<a class="plink" href="%s">%s →</a></div>') % (
                esc(title), desc, meta,
                contact, ("联系 ETIA 选型" if zh else "Contact ETIA for Selection"))
        n = len(rows)
    count = '<div class="catcount">%s</div>' % ((("共 %d 项" % n) if zh else ("%d results" % n)) if n else "")
    filt = ("<script>function etaFilter(x){var r=x.closest('.catalog')||document;var g={};"
            "r.querySelectorAll('.fgroup input:checked').forEach(function(c){(g[c.dataset.fg]=g[c.dataset.fg]||[]).push(c.dataset.fv);});"
            "r.querySelectorAll('.prow').forEach(function(k){var s=true;for(var f in g){if(g[f].indexOf(k.getAttribute('data-'+f)||'')<0){s=false;break;}}k.style.display=s?'':'none';});}</script>")
    if facets:
        catalog = ('<div class="catalog"><aside class="facets">%s</aside>'
                   '<div>%s<div class="plist">%s</div></div></div>') % (facets, count, cards)
    else:
        catalog = '<div>%s<div class="plist">%s</div></div>' % (count, cards)
    body = ('<section class="blk"><div class="wrap">%s</div></section>'
            '<div class="wrap">%s</div>%s') % (catalog, cta(lang), filt)
    path = "/industries/electronics-pcb/%s/" % cat_slug
    crumb = [(("首页" if zh else "Home"), "/"), (("行业" if zh else "Industries"), "/industries/"),
             (("电子与PCB" if zh else "Electronics & PCB"), "/industries/electronics-pcb/"),
             ((cat["title_zh"] if zh else cat["title_en"]), path)]
    lede = cat["lede_zh"] if zh else cat["lede_en"]
    write(lang, path, page(lang, path,
        ((cat["title_zh"] if zh else cat["title_en"]) + " | ETIA"),
        lede[:160], (cat["title_zh"] if zh else cat["title_en"]), lede, body, crumb, active="products", trust=False))
    if lang == "en":
        URLS.append(path)

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
  # Application thumbnails (image + text cards). Fill with clean COS URLs when ready.
  "app_imgs": ["", "", "", "", "", ""],
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

 # ---- Metals & Ceramics ----
 "steel": {
  "path": "/industries/steel/",
  "app_urls": [
    "/industries/steel/hot-steel-billet-identification/",
    "/industries/steel/forged-steel-heat-treatment-tracking/",
    "/industries/steel/steel-coil-annealing-traceability/",
    "/industries/steel/ultra-high-temperature-steel-identification/",
    "/industries/ceramics/ceramic-kiln-traceability/",
    "/industries/ceramics/crucible-identification/",
  ],
  "app_imgs": ["", "", "", "", "", ""],
  "en": {
    "eyebrow": "Metals & Ceramics",
    "h1": "Label Materials for Metals and Ceramics",
    "hero": "Steel, aluminium and ceramic processes expose identification to extreme heat, direct flame, oxidation, abrasion and repeated firing. ETIA supplies high-temperature label and tag materials and matches each construction to the real process — surface, peak temperature, dwell time and handling.",
    "apps_h": "Applications We Support",
    "apps": [
      ("Hot Steel Billet Identification", "Identification applied to hot billets that must survive high surface temperature, scale and downstream handling.", "Explore"),
      ("Forged-Steel Heat-Treatment Tracking", "Traceability through forging and heat-treatment where labels face heat, oil quench and mechanical handling.", "Explore"),
      ("Steel Coil Annealing", "Coil identification that must remain readable through annealing heat and the coil process line.", "Explore"),
      ("Ultra-High-Temperature Steel Identification", "Materials for the most extreme steel process temperatures, selected by the actual thermal profile.", "Explore"),
      ("Ceramic Kiln Process Tracking", "Identification that survives kiln firing cycles and repeated high-temperature exposure.", "Explore"),
      ("Crucible Identification", "Marking for crucibles and refractory ware exposed to extreme, repeated heat.", "Explore"),
    ],
    "fcta_h": "Match the Right Material to Your Thermal Process",
    "fcta_body": "Share your surface, peak temperature, dwell time and handling with ETIA, and request materials for testing.",
    "fcta1": "Talk to an Application Specialist", "fcta2": "Request Samples",
    "meta_title": "Metals & Ceramics Label Materials — High-Temperature Steel & Kiln Identification | ETIA",
    "meta_desc": "High-temperature label and tag materials for steel, aluminium and ceramics: hot billet/coil ID, forged-steel heat-treatment, annealing, kiln firing and crucible marking. ETIA supports selection, samples and supply.",
  },
  "zh": {
    "eyebrow": "金属与陶瓷",
    "h1": "面向金属与陶瓷的标签材料",
    "hero": "钢铁、铝及陶瓷工艺会让标识经受极端高温、直接火焰、氧化、磨损与多次烧成。ETIA 供应耐高温标签与标牌材料，并根据真实工艺——表面、峰值温度、持续时间与搬运方式——匹配合适的材料结构。",
    "apps_h": "我们支持的应用",
    "apps": [
      ("热钢坯标识", "贴附于高温钢坯的标识，需要经受高表面温度、氧化皮及后续搬运。", "查看"),
      ("锻钢热处理追溯", "贯穿锻造与热处理的追溯，标签需应对高温、油淬及机械搬运。", "查看"),
      ("钢卷退火标识", "钢卷标识需在退火高温及卷材产线过程中保持可读。", "查看"),
      ("超高温钢材标识", "面向最极端钢铁工艺温度的材料，按实际热曲线选型。", "查看"),
      ("陶瓷窑炉过程追踪", "可经受窑炉烧成循环及多次高温暴露的标识。", "查看"),
      ("坩埚标识", "用于经受极端、反复高温的坩埚与耐火制品标记。", "查看"),
    ],
    "fcta_h": "为您的热工艺匹配合适材料",
    "fcta_body": "向 ETIA 提供表面、峰值温度、持续时间与搬运方式，并申请材料进行测试。",
    "fcta1": "联系应用选型人员", "fcta2": "申请样品",
    "meta_title": "金属与陶瓷标签材料｜耐高温钢铁与窑炉标识｜ETIA",
    "meta_desc": "面向钢铁、铝及陶瓷的耐高温标签与标牌材料：热钢坯/钢卷标识、锻钢热处理、退火、窑炉烧成与坩埚标记。ETIA 提供选型、样品与供应支持。",
  },
 },

 # ---- Medical & Laboratory ----
 "healthcare-life-sciences": {
  "path": "/industries/healthcare-life-sciences/",
  "app_urls": [
    "/industries/healthcare-life-sciences/diagnostics-testing/",
    "/industries/healthcare-life-sciences/laboratory/",
    "/industries/healthcare-life-sciences/medical-devices/",
    "/industries/healthcare-life-sciences/pharmaceutical/",
    "/industries/healthcare-life-sciences/wearable-devices/",
  ],
  "app_imgs": ["", "", "", "", ""],
  "en": {
    "eyebrow": "Medical & Laboratory",
    "h1": "Label Materials for Medical and Laboratory",
    "hero": "Medical and laboratory identification must stay readable through cold storage, solvents, disinfection, sterilization and skin contact. ETIA supplies specialty label materials and helps match each construction to the surface, chemistry and process.",
    "apps_h": "Applications We Support",
    "apps": [
      ("Diagnostics & Testing", "Labels for diagnostic consumables and test devices that face solvents, moisture and cold storage.", "Explore"),
      ("Laboratory", "Identification for tubes, vials and slides through cryogenic storage, chemicals and autoclaving.", "Explore"),
      ("Medical Devices", "Durable device identification and UDI marking that must survive cleaning and the product lifecycle.", "Explore"),
      ("Pharmaceutical", "Materials for pharmaceutical containers and packaging with clean, reliable adhesion.", "Explore"),
      ("Wearable Devices", "Skin-contact and device labels balancing adhesion, comfort and durability.", "Explore"),
    ],
    "fcta_h": "Match the Right Material to Your Application",
    "fcta_body": "Tell ETIA the surface, chemistry, temperature and process, and request materials for testing.",
    "fcta1": "Talk to an Application Specialist", "fcta2": "Request Samples",
    "meta_title": "Medical & Laboratory Label Materials — Cryogenic, Chemical & Sterilization Resistant | ETIA",
    "meta_desc": "Specialty label materials for medical and laboratory identification: diagnostics, laboratory cryo/autoclave, medical devices, pharmaceutical and wearables. ETIA supports selection, samples and supply.",
  },
  "zh": {
    "eyebrow": "医疗与实验室",
    "h1": "面向医疗与实验室的标签材料",
    "hero": "医疗与实验室标识需要在冷藏、溶剂、消毒、灭菌及皮肤接触环境下保持可读。ETIA 供应特种标签材料，并根据表面、化学环境与工艺匹配合适的材料结构。",
    "apps_h": "我们支持的应用",
    "apps": [
      ("诊断与检测", "用于诊断耗材与检测器件的标签，需应对溶剂、潮湿与冷藏。", "查看"),
      ("实验室", "试管、样品瓶及载玻片标识，需经受深低温储存、化学品与高压灭菌。", "查看"),
      ("医疗器械", "耐久的器械标识与 UDI 标记，需经受清洗及产品生命周期。", "查看"),
      ("制药", "用于药品容器与包装的材料，粘接洁净可靠。", "查看"),
      ("可穿戴设备", "兼顾粘接、舒适与耐久的皮肤接触及设备标签。", "查看"),
    ],
    "fcta_h": "为您的应用匹配合适材料",
    "fcta_body": "向 ETIA 提供表面、化学环境、温度与工艺，并申请材料进行测试。",
    "fcta1": "联系应用选型人员", "fcta2": "申请样品",
    "meta_title": "医疗与实验室标签材料｜耐深低温、耐化学与耐灭菌｜ETIA",
    "meta_desc": "面向医疗与实验室标识的特种标签材料：诊断检测、实验室深低温/高压灭菌、医疗器械、制药与可穿戴。ETIA 提供选型、样品与供应支持。",
  },
 },

 # ---- Automotive & Tire (landing route matches mega-menu; cards link to /industries/automotive/*) ----
 "automotive-label-materials": {
  "path": "/industries/automotive-label-materials/",
  "app_urls": [
    "/industries/automotive/underhood-powertrain-labels/",
    "/industries/automotive/parts-marking-nameplate-labels/",
    "/industries/automotive/vin-security-compliance-labels/",
    "/industries/automotive/cable-wire-harness-labels/",
    "/industries/automotive/ev-battery-charging-labels/",
    "/industries/automotive/paint-masking-overlaminate/",
  ],
  "app_imgs": ["", "", "", "", "", ""],
  "en": {
    "eyebrow": "Automotive & Tire",
    "h1": "Label Materials for Automotive and Tire",
    "hero": "Automotive identification must survive heat, oil, fuel, abrasion and years of service. ETIA supplies specialty label materials for underhood, parts marking, compliance, wiring and EV applications — matched to the real surface and environment.",
    "apps_h": "Applications We Support",
    "apps": [
      ("Underhood & Powertrain Labels", "Identification for high-heat, oil- and chemical-exposed underhood and powertrain areas.", "Explore"),
      ("Parts Marking & Nameplates", "Durable component identification and nameplates for the product lifecycle.", "Explore"),
      ("VIN, Security & Compliance", "VIN, security and regulatory-compliance labels with tamper and durability requirements.", "Explore"),
      ("Cable & Wire Harness Labels", "Wire and harness identification that resists heat, abrasion and handling.", "Explore"),
      ("EV Battery & Charging Labels", "Identification and warning labels for EV battery, charging and high-voltage areas.", "Explore"),
      ("Paint Masking & Overlaminate", "Masking and overlaminate materials matched to temperature and removability.", "Explore"),
    ],
    "fcta_h": "Match the Right Material to Your Application",
    "fcta_body": "Tell ETIA the surface, temperature, chemistry and durability need, and request materials for testing.",
    "fcta1": "Talk to an Application Specialist", "fcta2": "Request Samples",
    "meta_title": "Automotive & Tire Label Materials — Underhood, VIN, Harness & EV | ETIA",
    "meta_desc": "Specialty automotive label materials for underhood/powertrain, parts marking, VIN and compliance, wire harness, EV battery and paint masking. ETIA supports selection, samples and supply.",
  },
  "zh": {
    "eyebrow": "汽车与轮胎",
    "h1": "面向汽车与轮胎的标签材料",
    "hero": "汽车标识需要经受高温、油污、燃油、磨损及多年使用。ETIA 供应用于发动机舱、零件标记、法规合规、线束及电动车应用的特种标签材料——按真实表面与环境匹配。",
    "apps_h": "我们支持的应用",
    "apps": [
      ("发动机舱与动力总成标签", "用于高温、接触油污及化学品的发动机舱与动力总成区域标识。", "查看"),
      ("零件标记与铭牌", "面向产品生命周期的耐久零部件标识与铭牌。", "查看"),
      ("VIN、安全与合规", "满足防拆与耐久要求的 VIN、安全及法规合规标签。", "查看"),
      ("线缆与线束标签", "耐高温、耐磨、耐搬运的导线与线束标识。", "查看"),
      ("电池与充电标签", "用于电动车电池、充电及高压区域的标识与警示标签。", "查看"),
      ("喷漆遮蔽与覆膜", "按温度与可移除性匹配的遮蔽与覆膜材料。", "查看"),
    ],
    "fcta_h": "为您的应用匹配合适材料",
    "fcta_body": "向 ETIA 提供表面、温度、化学环境与耐久需求，并申请材料进行测试。",
    "fcta1": "联系应用选型人员", "fcta2": "申请样品",
    "meta_title": "汽车与轮胎标签材料｜发动机舱、VIN、线束与电动车｜ETIA",
    "meta_desc": "面向发动机舱/动力总成、零件标记、VIN 与合规、线束、电动车电池及喷漆遮蔽的汽车特种标签材料。ETIA 提供选型、样品与供应支持。",
  },
 },

 # ---- Wire & Cable ----
 "wire-cable": {
  "path": "/industries/wire-cable/",
  "app_urls": [
    "/industries/wire-cable/flag-cable-labels/",
    "/industries/wire-cable/wrap-around-cable-labels/",
    "/industries/wire-cable/heat-shrink-wire-markers/",
    "/industries/wire-cable/self-laminating-wire-labels/",
    "/industries/wire-cable/wire-harness-cable-assemblies/",
    "/industries/wire-cable/datacom-network-cabling/",
  ],
  "app_imgs": ["", "", "", "", "", ""],
  "en": {
    "eyebrow": "Wire & Cable",
    "h1": "Label Materials for Wire and Cable",
    "hero": "Wire and cable identification must wrap, self-laminate or shrink onto the conductor and stay readable through handling, heat and the installed environment. ETIA supplies specialty label materials matched to the cable diameter, method and environment.",
    "apps_h": "Applications We Support",
    "apps": [
      ("Flag Cable Labels", "Flag-style labels for thin wires where a wrap-around print area is not enough.", "Explore"),
      ("Wrap-Around Cable Labels", "Self-wrapping labels with a clear over-laminate that protects the printed area.", "Explore"),
      ("Heat-Shrink Wire Markers", "Heat-shrink markers for permanent, durable conductor identification.", "Explore"),
      ("Self-Laminating Wire Labels", "Self-laminating labels that seal the print under a protective clear tail.", "Explore"),
      ("Wire Harness & Cable Assemblies", "Identification for harness and assembly production and downstream service.", "Explore"),
      ("DataCom & Network Cabling", "Labels for structured cabling, patch and network identification.", "Explore"),
    ],
    "fcta_h": "Match the Right Material to Your Cable",
    "fcta_body": "Tell ETIA the cable diameter, method and environment, and request materials for testing.",
    "fcta1": "Talk to an Application Specialist", "fcta2": "Request Samples",
    "meta_title": "Wire & Cable Label Materials — Flag, Wrap-Around, Heat-Shrink & Self-Laminating | ETIA",
    "meta_desc": "Specialty wire and cable label materials: flag labels, wrap-around, heat-shrink markers, self-laminating, wire harness and datacom cabling. ETIA supports selection, samples and supply.",
  },
  "zh": {
    "eyebrow": "电线与电缆",
    "h1": "面向电线与电缆的标签材料",
    "hero": "电线电缆标识需要以缠绕、自覆膜或热缩方式固定在导体上，并在搬运、高温及安装环境中保持可读。ETIA 供应按线径、方式与环境匹配的特种标签材料。",
    "apps_h": "我们支持的应用",
    "apps": [
      ("旗形电缆标签", "用于细线的旗形标签，适合缠绕打印面积不足的场景。", "查看"),
      ("缠绕式电缆标签", "自缠绕标签，带透明覆膜保护打印区域。", "查看"),
      ("热缩线标", "热缩标记，实现永久、耐久的导体标识。", "查看"),
      ("自覆膜线标", "自覆膜标签，用透明保护尾将打印内容封在膜下。", "查看"),
      ("线束与线缆组件", "面向线束与组件生产及后续维护的标识。", "查看"),
      ("数据与网络布线", "用于综合布线、跳线及网络标识的标签。", "查看"),
    ],
    "fcta_h": "为您的线缆匹配合适材料",
    "fcta_body": "向 ETIA 提供线径、方式与环境，并申请材料进行测试。",
    "fcta1": "联系应用选型人员", "fcta2": "申请样品",
    "meta_title": "电线与电缆标签材料｜旗形、缠绕、热缩与自覆膜｜ETIA",
    "meta_desc": "特种电线电缆标签材料：旗形标签、缠绕式、热缩标记、自覆膜、线束与数据网络布线。ETIA 提供选型、样品与供应支持。",
  },
 },

 # ---- Outdoor & Energy (no layer-2 pages yet — cards route to contact) ----
 "outdoor-energy": {
  "path": "/industries/outdoor-energy/",
  "app_urls": [],
  "app_imgs": ["", "", "", "", ""],
  "en": {
    "eyebrow": "Outdoor & Energy",
    "h1": "Label Materials for Outdoor and Energy",
    "hero": "Outdoor and energy identification must survive UV, weather, temperature cycling and years of exposure. ETIA supplies durable, weather-resistant label materials matched to the surface, environment and required service life.",
    "apps_h": "Applications We Support",
    "apps": [
      ("Solar Panel Identification", "Durable labels for solar modules exposed to UV, heat and long outdoor service.", "Contact ETIA"),
      ("Outdoor Equipment Labels", "Weather-resistant identification for outdoor equipment and enclosures.", "Contact ETIA"),
      ("Energy Storage Labels", "Identification and warning labels for energy-storage and battery systems.", "Contact ETIA"),
      ("UV & Weather-Resistant Labels", "Materials selected for long-term UV, moisture and temperature exposure.", "Contact ETIA"),
      ("Rating & Nameplate Labels", "Durable rating plates and nameplates for outdoor and energy assets.", "Contact ETIA"),
    ],
    "fcta_h": "Match the Right Material to Your Environment",
    "fcta_body": "Tell ETIA the surface, exposure and service-life need, and request materials for testing.",
    "fcta1": "Talk to an Application Specialist", "fcta2": "Request Samples",
    "meta_title": "Outdoor & Energy Label Materials — UV, Weather & Long-Life Identification | ETIA",
    "meta_desc": "Durable, weather-resistant label materials for outdoor and energy: solar module ID, outdoor equipment, energy storage, UV/weather and rating plates. ETIA supports selection, samples and supply.",
  },
  "zh": {
    "eyebrow": "户外与能源",
    "h1": "面向户外与能源的标签材料",
    "hero": "户外与能源标识需要经受紫外线、气候、温度循环及多年暴露。ETIA 供应耐久、耐候的标签材料，并按表面、环境与所需使用寿命匹配。",
    "apps_h": "我们支持的应用",
    "apps": [
      ("太阳能组件标识", "用于经受紫外线、高温及长期户外使用的光伏组件耐久标签。", "联系 ETIA"),
      ("户外设备标签", "用于户外设备与机箱的耐候标识。", "联系 ETIA"),
      ("储能标签", "用于储能与电池系统的标识与警示标签。", "联系 ETIA"),
      ("耐紫外与耐候标签", "针对长期紫外线、潮湿与温度暴露选型的材料。", "联系 ETIA"),
      ("铭牌与规格标签", "用于户外与能源资产的耐久规格牌与铭牌。", "联系 ETIA"),
    ],
    "fcta_h": "为您的环境匹配合适材料",
    "fcta_body": "向 ETIA 提供表面、暴露条件与使用寿命需求，并申请材料进行测试。",
    "fcta1": "联系应用选型人员", "fcta2": "申请样品",
    "meta_title": "户外与能源标签材料｜耐紫外、耐候与长寿命标识｜ETIA",
    "meta_desc": "面向户外与能源的耐久耐候标签材料：光伏组件标识、户外设备、储能、耐紫外/耐候与规格铭牌。ETIA 提供选型、样品与供应支持。",
  },
 },
}


# Hero slogan per industry (bilingual). Sits under the industry label in the HERO SECTION.
SLOGANS = {
    "electronics-pcb": ("Identification that survives the entire manufacturing process.",
                        "贯穿整个制造流程，始终可靠可读的标识。"),
    "steel": ("Built for extreme heat, direct flame and repeated firing.",
              "为极端高温、直接火焰与反复烧成而生。"),
    "healthcare-life-sciences": ("Readable through cold storage, chemicals and sterilization.",
                                 "历经冷藏、化学与灭菌，依然清晰可读。"),
    "automotive-label-materials": ("Durable through heat, oil and a lifetime of service.",
                                   "耐高温、耐油污，伴随整车全生命周期。"),
    "wire-cable": ("The right marker for every wire and cable.",
                   "为每一根电线与电缆匹配合适的标识。"),
    "outdoor-energy": ("Weatherproof identification that lasts for years outdoors.",
                       "耐候标识，户外经年不褪色。"),
}

# Brochure / product-list cards shown below the tab module (FLEXcon-style resource row).
# Only real, existing destinations — swap in real brochure PDFs later.
def _resources(lang, slug):
    zh = (lang == "zh")
    cards = [((("浏览产品与方案" if zh else "Browse Products & Solutions"),
               ("按应用、环境、特性与材料浏览" if zh else "Browse by application, environment, feature and material"),
               "/products/")),
             ((("申请样品" if zh else "Request Samples"),
               ("提供工况，我们安排材料测试" if zh else "Share your conditions — we arrange material testing"),
               "/contact/"))]
    return cards

def build_landing(lang, slug):
    """Layer-1 industry landing. HERO SECTION (industry label + slogan, banner-ready) →
    intro paragraph → applications tab module (single scrollable row of tabs + active
    panel with image + text) → brochure/resource cards → CTA."""
    d = LANDINGS[slug][lang]
    path = LANDINGS[slug]["path"]
    zh = (lang == "zh")
    contact = L(lang, "/contact/")
    def sec(bg, inner):
        st = ' style="background:%s"' % bg if bg else ""
        return '<section class="blk"%s><div class="wrap">%s</div></section>' % (st, inner)

    # --- HERO SECTION (banner-ready) ---
    hero_img = LANDINGS[slug].get("hero_img", "")
    slogan = SLOGANS.get(slug, ("", ""))[1 if zh else 0]
    if hero_img:
        hero_open = '<section class="indhero hasimg" style="background-image:url(%s)">' % esc(hero_img)
    else:
        hero_open = '<section class="indhero">'
    hero_html = ('%s<div class="wrap"><div class="eyebrow">%s</div><h1>%s</h1>'
                 '<p class="slogan">%s</p></div></section>') % (
        hero_open, esc(d["eyebrow"]), esc(d["h1"]), esc(slogan))

    # --- intro paragraph (below hero) ---
    intro = sec("", '<p class="lede" style="max-width:62em">%s</p>' % esc(d["hero"]))

    # --- applications tab module: single scrollable row of tabs + active panel ---
    app_urls = LANDINGS[slug].get("app_urls", [])
    app_imgs = LANDINGS[slug].get("app_imgs", [])
    def panel_img(i, t):
        url = app_imgs[i] if i < len(app_imgs) else ""
        img = ('<img src="%s" alt="%s" loading="lazy" onerror="this.remove()">' % (esc(url), esc(t))) if url else ""
        return '<div class="apimg">%s<span class="ph">\U0001F3F7</span></div>' % img
    tabs = "".join(
        '<button class="apptab%s" onclick="etaTab(this)">%s</button>' % ((" on" if i == 0 else ""), esc(t))
        for i, (t, dsc, cta_) in enumerate(d["apps"]))
    panels = "".join(
        '<div class="apppanel"%s>%s<div class="aptext"><h3>%s</h3><p>%s</p>'
        '<a class="plink" href="%s">%s →</a></div></div>'
        % ((' style="display:none"' if i > 0 else ''), panel_img(i, t), esc(t), esc(dsc),
           (L(lang, app_urls[i]) if i < len(app_urls) else contact), esc(cta_))
        for i, (t, dsc, cta_) in enumerate(d["apps"]))
    tabscript = ("<script>function etaTab(b){var m=b.closest('.appmod');"
                 "var t=[].slice.call(m.querySelectorAll('.apptab'));var i=t.indexOf(b);"
                 "t.forEach(function(x,j){x.classList.toggle('on',j===i);});"
                 "m.querySelectorAll('.apppanel').forEach(function(p,j){p.style.display=(j===i)?'grid':'none';});}"
                 "function etaScroll(b,dir){var r=b.closest('.apptabsrow').querySelector('.apptabs');"
                 "r.scrollBy({left:dir*260,behavior:'smooth'});}</script>")
    apps_html = ('<h2>%s</h2><div class="appmod">'
                 '<div class="apptabsrow"><button class="apparrow" onclick="etaScroll(this,-1)" aria-label="prev">&lsaquo;</button>'
                 '<div class="apptabs">%s</div>'
                 '<button class="apparrow" onclick="etaScroll(this,1)" aria-label="next">&rsaquo;</button></div>'
                 '<div class="apppanels">%s</div></div>%s') % (esc(d["apps_h"]), tabs, panels, tabscript)

    # --- brochure / resource cards ---
    bcards = "".join(
        '<a class="bcard" href="%s"><div class="bct"><h3>%s</h3><p>%s</p></div><span class="barr">&rarr;</span></a>'
        % (L(lang, url), esc(t), esc(s)) for t, s, url in _resources(lang, slug))
    brochures = sec("", '<div class="brochures">%s</div>' % bcards)

    final = ('<div class="wrap"><div class="cta"><div class="ic">⚡</div><h3>%s</h3><p>%s</p>'
             '<div class="btns"><a class="btn pri" href="%s">%s</a>'
             '<a class="btn on-dark" href="%s">%s</a></div></div></div>') % (
        esc(d["fcta_h"]), esc(d["fcta_body"]), contact, esc(d["fcta1"]), contact, esc(d["fcta2"]))

    body = intro + sec("", apps_html) + brochures + final

    crumb = [(("首页" if zh else "Home"), "/"),
             (("行业" if zh else "Industries"), "/industries/"),
             (d["eyebrow"], path)]
    write(lang, path, page(lang, path, d["meta_title"], d["meta_desc"],
                           d["h1"], d["hero"], body, crumb, active="industries", trust=False, hero=hero_html))
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
        for cat_slug in PCB_CATS:
            build_pcb_category(lang, cat_slug)
        build_by_environment(lang)
        build_by_feature(lang)
        build_products_overview(lang)
        build_application_notes(lang)


if __name__ == "__main__":
    main()
