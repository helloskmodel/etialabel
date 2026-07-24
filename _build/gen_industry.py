#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Industry landing pages — ETIALABEL Industry Landing Page Standard V1.0.

An industry page is a NAVIGATION HUB, not a product page. Flow: Hero ->
Why Labeling Matters -> Explore Labeling Solutions (4-6 cards) -> Industry
Challenges (icon items) -> Download Solution Guide -> Engineering Resources
-> Final CTA. Target 500-700 visible words. ETIA is positioned as an
application-driven supplier / solution provider (helps select, supplies,
supports) — never "we manufacture". No invented specifications.

EN + ZH. One shared layout fed by per-industry data. Placeholders routed to
/contact/ until the asset/page exists: Download PDF, Preview Guide,
Engineering Insights, FAQ (no filtered archives yet)."""
import os
import gen_heatproof as hp
from gen_heatproof import esc, L, Lx, page, write, LANGS

AN = "/application-notes/"
CS = "/case-studies/"
CONTACT = "/contact/"
# Shared 6-industry hero image set.
_HERO = "https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com/A%E3%83%BBHERO%20banner%206%20%E7%BB%84/"

def _t(lang, en, zh): return zh if lang == "zh" else en

# Shared UI vocabulary (en, zh).
UI = {
 "primary_cta":  ("Explore Applications", "查看应用"),
 "secondary_cta":("Download Solution Guide", "下载方案指南"),
 "typical":      ("Typical Applications", "典型应用"),
 "explore_an":   ("Explore Application Notes", "查看应用笔记"),
 "chal_title":   ("Built for Demanding Industry Conditions", "为严苛工况而生"),
 "guide_pdf":    ("Download PDF", "下载 PDF"),
 "guide_preview":("Preview Guide", "预览指南"),
 "res_title":    ("Explore Engineering Resources", "探索工程资源"),
 "r_an":   ("Application Notes", "应用笔记"),
 "r_an_d": ("Practical guidance for individual labeling applications.", "针对具体标签应用的实用指南"),
 "r_ei":   ("Engineering Insights", "工程洞察"),
 "r_ei_d": ("Technical articles on material selection, printing and durability.", "关于材料选型、打印与耐久性的技术文章"),
 "r_cs":   ("Case Studies", "案例研究"),
 "r_cs_d": ("Real-world labeling challenges and evaluation approaches.", "真实标签挑战与评估方法"),
 "r_faq":  ("FAQ", "常见问题"),
 "r_faq_d":("Answers to common industry labeling questions.", "常见行业标签问题解答"),
 "final_primary":   ("Talk to an Application Specialist", "咨询应用专家"),
 "final_secondary": ("Request Samples", "索取样品"),
}

DATA = {
 "automotive": {
  "slug": "automotive-labeling-solutions",
  "banner": "",
  "hero_alt": ("Automotive component on the assembly line carrying a barcode identification label",
               "汽车装配线上带条码标识标签的零部件"),
  "eyebrow": ("INDUSTRY LABELING SOLUTIONS", "行业标签解决方案"),
  "title": ("Automotive Labeling Solutions", "汽车标签解决方案"),
  "headline": ("Reliable Identification Across the Automotive Lifecycle",
               "覆盖汽车全生命周期的可靠标识"),
  "intro": ("From component manufacturing and vehicle assembly to aftermarket service, labels carry the identification, traceability and safety information that follows every part through its working life. ETIA helps automotive manufacturers match durable label materials to the heat, chemicals and outdoor exposure of each production and service environment.",
            "从零部件制造、整车装配到售后服务,标签承载着伴随每个零件整个使用寿命的标识、追溯与安全信息 ETIA 帮助汽车制造商为各生产与服务环境的高温、化学品与户外暴露匹配耐用标签材料"),
  "why_title": ("Why Automotive Labeling Matters", "为什么汽车标签很重要"),
  "why": ("A modern vehicle is built from thousands of parts made by many suppliers. Labels connect those components to the operators, machines and quality systems that build and service them, and carry the barcodes that link parts to traceability data. That information must survive heat, oil, chemicals, abrasion and years outdoors — when a label fails, traceability, warranty records and safety warnings go with it.",
          "一辆现代汽车由多家供应商制造的数千个零件组成 标签把这些零部件与制造和维修它们的操作人员、机器与质量体系连接起来,并承载把零件与追溯数据关联的条码 这些信息必须经受高温、油污、化学品、磨损与多年户外暴露 —— 一旦标签失效,追溯、保修记录与安全警示都随之丢失"),
  "explore_title": ("Explore Automotive Labeling Solutions", "探索汽车标签解决方案"),
  "categories": [
   {"name": ("Production Tracking", "生产追踪"),
    "desc": ("Maintain reliable identification for parts, assemblies, tires and work-in-process throughout manufacturing.",
             "在制造全过程中为零件、总成、轮胎与在制品保持可靠标识"),
    "apps": [("Tire Bead Labels","胎圈标签"),("WIP Tracking","在制品追踪"),
             ("Battery Cell Identification","电芯标识"),("Component Traceability","零部件追溯")]},
   {"name": ("Vehicle Identification", "车辆标识"),
    "desc": ("Permanent identification for vehicles, engines, batteries and critical components across their service life.",
             "面向车辆、发动机、电池及关键部件的永久标识,贯穿整个使用寿命"),
    "apps": [("VIN Labels","VIN 标签"),("Rating Plates","铭牌"),
             ("Serial Number Labels","序列号标签"),("Component Identification","零部件标识")]},
   {"name": ("Safety & Warning", "安全与警示"),
    "desc": ("Clear, durable safety communication for operators, technicians and end users.",
             "为操作人员、技师与终端用户提供清晰耐久的安全信息"),
    "apps": [("High Voltage Labels","高压标签"),("Warning Labels","警告标签"),
             ("Caution Labels","注意标签"),("Tire Pressure Labels","胎压标签")]},
   {"name": ("Compliance & Certification", "合规与认证"),
    "desc": ("Durable identification that meets OEM specifications and international regulatory requirements.",
             "满足 OEM 规范与国际法规要求的耐用标识"),
    "apps": [("Regulatory Labels","法规标签"),("Certification Labels","认证标签"),
             ("Compliance Identification","合规标识")]},
   {"name": ("Security & Brand Protection", "防伪与品牌保护"),
    "desc": ("Protect products against tampering, relabeling and counterfeiting.",
             "保护产品免受篡改、重贴标与假冒"),
    "apps": [("Tamper-Evident Labels","防拆标签"),("Security Labels","安全标签"),
             ("Laser Markable Identification","激光打标标识")]},
  ],
  "challenges": [
   ("🔥",("High Heat","高温")),("🛢️",("Oil & Fluids","油液")),("🧪",("Chemicals","化学品")),
   ("☀️",("UV Exposure","紫外线")),("🪨",("Abrasion","磨损")),("💧",("Moisture","潮湿")),
   ("♾️",("Long-Term Durability","长期耐久")),("⚙️",("Automated Application","自动贴标")),
  ],
  "guide_desc": ("The guide gives an application overview, the key labeling challenges across the vehicle, the main selection considerations, typical labeling technologies and a recommended evaluation path — a practical starting point before you specify materials.",
                 "本指南提供应用概览、整车主要标签挑战、核心选型考量、常用标签技术以及推荐的评估路径 —— 在你确定材料前的实用起点"),
  "seo_title": ("Automotive Labeling Solutions | ETIA", "汽车标签解决方案 | ETIA"),
  "seo_desc": ("Durable automotive labels for VIN, tire, battery and component identification — traceability, safety and compliance across the vehicle lifecycle, with ETIA application support.",
               "面向 VIN、轮胎、电池与零部件标识的耐用汽车标签 —— 覆盖整车生命周期的追溯、安全与合规,由 ETIA 提供应用支持"),
  "primary_kw": "automotive labeling solutions",
  "secondary_kw": ["vehicle identification labels", "VIN labels", "tire labels",
                   "automotive barcode labels", "under-hood labels", "automotive traceability",
                   "tamper-evident labels", "automotive battery labels"],
 },
 "pcb": {
  "slug": "pcb-electronics-labeling-solutions",
  "banner": "",
  "hero_alt": ("Printed circuit board carrying a barcode identification label during assembly",
               "贴装过程中带条码标识标签的印刷电路板"),
  "eyebrow": ("INDUSTRY LABELING SOLUTIONS", "行业标签解决方案"),
  "title": ("PCB & Electronics Labeling Solutions", "PCB 与电子标签解决方案"),
  "headline": ("Reliable Identification Throughout Electronics Manufacturing",
               "贯穿电子制造全过程的可靠标识"),
  "intro": ("From bare boards and SMT assembly to test and finished-product identification, labels keep every board and component traceable through modern electronics manufacturing. ETIA helps electronics manufacturers match label materials to reflow, cleaning and ESD-controlled processes.",
            "从裸板、SMT 贴装到测试与成品标识,标签让每块板与元件在现代电子制造中保持可追溯 ETIA 帮助电子制造商为回流、清洗与防静电工艺匹配标签材料"),
  "why_title": ("Why PCB Labeling Matters", "为什么 PCB 标签很重要"),
  "why": ("Electronics manufacturing depends on accurate identification for quality control and traceability. A label applied to a bare board may pass through reflow above 250 °C, aggressive cleaning, handling, testing and long production cycles — and must still scan cleanly at the end. Barcodes are small and densely printed, so print quality and durability matter as much as adhesion. Lost identification means scrapped boards and broken traceability records.",
          "电子制造依赖准确标识来做质量控制与追溯 贴在裸板上的标签可能要经历 250 °C 以上回流焊、强力清洗、搬运、测试与长生产周期 —— 最终仍必须清晰可扫 条码小且高密度打印,因此打印质量与耐久性与粘接同样重要 标识一旦丢失,意味着板子报废与追溯记录中断"),
  "explore_title": ("Explore PCB Labeling Solutions", "探索 PCB 标签解决方案"),
  "categories": [
   {"name": ("PCB Manufacturing", "PCB 制造"),
    "desc": ("Reliable identification throughout PCB fabrication and assembly.",
             "贯穿 PCB 制造与贴装的可靠标识"),
    "apps": [("Wash & Reflow Labels","水洗回流标签"),("Wash & Non-Reflow Labels","水洗非回流标签"),
             ("Post-Process Labels","后工序标签")]},
   {"name": ("SMT & Electronics Assembly", "SMT 与电子贴装"),
    "desc": ("Support component identification and process control throughout assembly.",
             "在贴装全过程中支持元件标识与流程控制"),
    "apps": [("Component Labels","元件标签"),("WIP Labels","在制品标签"),
             ("ESD-Safe Labels","防静电标签"),("Inspection Labels","检验标签")]},
   {"name": ("Product Identification", "产品标识"),
    "desc": ("Permanent identification for finished electronic products and assemblies.",
             "面向电子成品与总成的永久标识"),
    "apps": [("Rating Labels","铭牌标签"),("Product Labels","产品标签"),
             ("Asset Labels","资产标签"),("Serial Number Labels","序列号标签")]},
   {"name": ("Quality & Compliance", "质量与合规"),
    "desc": ("Maintain traceability and support manufacturing quality systems.",
             "保持可追溯并支撑制造质量体系"),
    "apps": [("Barcode Labels","条码标签"),("QR Code Labels","二维码标签"),
             ("Compliance Labels","合规标签"),("Calibration Labels","校准标签")]},
   {"name": ("Specialty Electronics", "特种电子"),
    "desc": ("Engineered labeling solutions for demanding electronics applications.",
             "面向严苛电子应用的工程化标签方案"),
    "apps": [("Laser Markable Labels","激光打标标签"),("Polyimide Labels","聚酰亚胺标签"),
             ("High Temperature Labels","耐高温标签")]},
  ],
  "challenges": [
   ("🔥",("Solder Reflow Heat","回流焊高温")),("🧪",("Cleaning Chemicals","清洗化学品")),
   ("⚡",("ESD Control","防静电")),("🔎",("Small Barcodes","小条码")),
   ("🧯",("Solder Flux","助焊剂")),("🪨",("Handling & Abrasion","搬运磨损")),
   ("⚙️",("Automated Application","自动贴标")),("♾️",("Long-Term Durability","长期耐久")),
  ],
  "guide_desc": ("The guide covers an application overview, the key labeling challenges in PCB and electronics assembly, the main selection considerations, typical labeling technologies and a recommended evaluation path before you specify materials.",
                 "本指南涵盖应用概览、PCB 与电子贴装的主要标签挑战、核心选型考量、常用标签技术以及在确定材料前推荐的评估路径"),
  "seo_title": ("PCB & Electronics Labeling Solutions | ETIA", "PCB 与电子标签解决方案 | ETIA"),
  "seo_desc": ("Durable PCB and electronics labels for reflow, cleaning and ESD-safe traceability — from bare board to finished product, with ETIA application support.",
               "面向回流、清洗与防静电追溯的耐用 PCB 与电子标签 —— 从裸板到成品,由 ETIA 提供应用支持"),
  "primary_kw": "pcb labeling solutions",
  "secondary_kw": ["electronics labeling", "ESD-safe labels", "reflow labels",
                   "polyimide labels", "PCB barcode labels", "component traceability labels",
                   "high temperature labels", "SMT labels"],
 },
 "cable": {
  "slug": "wire-cable-labeling-solutions",
  "banner": "",
  "hero_alt": ("Bundled wires and cables carrying identification markers", "带标识的成束线缆"),
  "eyebrow": ("INDUSTRY LABELING SOLUTIONS", "行业标签解决方案"),
  "title": ("Wire & Cable Labeling Solutions", "线缆标签解决方案"),
  "headline": ("Reliable identification that keeps systems running safely", "可靠标识，保障系统安全运行"),
  "intro": ("Clear wire and cable identification supports correct installation, faster maintenance and reliable troubleshooting across industrial equipment, electrical systems, telecommunications, transportation and infrastructure. ETIA helps manufacturers and system integrators select labeling solutions that remain attached and readable throughout production, installation and long-term service.",
            "清晰的线缆标识,支撑工业设备、电气系统、通信、交通与基础设施中的正确安装、更快维护与可靠排障 ETIA 帮助制造商与系统集成商选择在生产、安装与长期使用中始终不脱落、可读的标签方案"),
  "why_title": ("Why Wire & Cable Labeling Matters", "为什么线缆标签很重要"),
  "why": [
   ("A cable may look simple, but it connects equipment, power, signals and control systems. When identification is missing or unclear, technicians spend more time tracing connections, installation errors become more likely and maintenance becomes more difficult.",
    "线缆看似简单,却连接着设备、电力、信号与控制系统 一旦标识缺失或不清晰,技师需要花更多时间追查连接、安装出错的概率上升、维护也更困难"),
   ("Wire and cable labels create a reliable link between the physical cable and its related drawings, terminals, control panels and digital records. Depending on the application, identification may need to carry text, serial numbers, barcodes or circuit information.",
    "线缆标签在实物线缆与其对应的图纸、端子、控制柜与数字记录之间建立可靠关联 视应用不同,标识可能需要承载文字、序列号、条码或回路信息"),
   ("Smaller-diameter cables require flexible label constructions and reliable adhesives to reduce edge lifting or 'butterflying.' Common solutions include flag labels for larger amounts of printed information and wrap-around labels for a cleaner, lower-profile appearance.",
    "细线径线缆需要柔性标签结构与可靠胶粘,以减少边缘翘起或'蝶形翘边' 常见方案包括:承载较多打印信息的旗形标签,以及外观更简洁、更贴合的缠绕标签"),
  ],
  "explore_title": ("Explore Wire & Cable Labeling Solutions", "探索线缆标签解决方案"),
  "categories": [
   {"name": ("Wire Identification", "导线标识"),
    "desc": ("Maintain clear identification on individual wires in control cabinets, machinery and electrical installations.",
             "在控制柜、机械与电气装置中,为单根导线保持清晰标识"),
    "apps": [("Wire Number Labels","线号标签"),("Terminal Wire Identification","端子导线标识"),
             ("Control Cabinet Wiring","控制柜布线"),("Electrical Assembly Labels","电气装配标签")]},
   {"name": ("Flag Labels", "旗形标签"),
    "desc": ("Create a larger printable area for text, barcodes and detailed identification on small-diameter cables.",
             "在细线径线缆上,提供更大的可打印区域用于文字、条码与详细标识"),
    "apps": [("Data and Telecom Cables","数据与通信线缆"),("Industrial Control Wiring","工业控制布线"),
             ("Equipment Harnesses","设备线束"),("Service Identification","维护标识")]},
   {"name": ("Wrap-Around Labels", "缠绕标签"),
    "desc": ("Provide compact cable identification while protecting printed information beneath the transparent wrap.",
             "在透明覆盖层下保护打印信息,提供紧凑的线缆标识"),
    "apps": [("Cable Bundles","线束"),("Network Cabling","网络布线"),
             ("Industrial Equipment","工业设备"),("Electrical Panels","配电柜")]},
   {"name": ("Cable Harness Identification", "线束标识"),
    "desc": ("Track harnesses and cable assemblies throughout production, installation and maintenance.",
             "在生产、安装与维护全过程追踪线束与线缆组件"),
    "apps": [("Automotive Harnesses","汽车线束"),("Industrial Equipment Harnesses","工业设备线束"),
             ("Appliance Wiring","家电布线"),("Transportation Systems","交通系统")]},
   {"name": ("Heat-Shrink Identification", "热缩标识"),
    "desc": ("Create durable identification for cables exposed to demanding installation and service conditions.",
             "为面临严苛安装与使用条件的线缆提供耐久标识"),
    "apps": [("Power Cables","电力电缆"),("Railway Wiring","铁路布线"),
             ("Industrial Machinery","工业机械"),("Electrical Maintenance","电气维护")]},
  ],
  "challenges": [
   ("🔁",("Flexible Surfaces","柔性表面")),("📏",("Small Cable Diameters","细线径")),("📳",("Vibration","振动")),
   ("🪨",("Abrasion","磨损")),("🔥",("Heat","高温")),("🧪",("Chemicals","化学品")),
   ("☀️",("UV Exposure","紫外线")),("🔗",("Long-Term Adhesion","长期粘接")),
  ],
  "guide_desc": ("Explore common cable identification formats, application considerations, printing methods and material-selection questions for industrial wire and cable projects.",
                 "了解工业线缆项目常见的标识形式、应用考量、打印方式与选材要点"),
  "res_desc": [
   ("Practical guidance for flag, wrap-around, harness and heat-shrink identification.","旗形、缠绕、线束与热缩标识的实用指南"),
   ("Technical articles covering adhesion, flexibility, printing and long-term readability.","关于粘接、柔性、打印与长期可读性的技术文章"),
   ("Examples of cable identification and troubleshooting challenges.","线缆标识与排障挑战的案例"),
  ],
  "cta_q": ("Need Help Selecting a Wire or Cable Labeling Solution?","需要帮助选择线缆标签方案吗"),
  "cta_body": ("ETIA helps evaluate cable diameter, surface flexibility, print area, installation method and environmental exposure before arranging materials for application testing.",
               "ETIA 帮助评估线径、表面柔性、打印区域、安装方式与环境暴露,并安排材料进行应用测试"),
  "seo_title": ("Wire & Cable Labeling Solutions | ETIA", "线缆标签解决方案 | ETIA"),
  "seo_desc": ("Explore wire and cable labeling solutions for flag labels, wrap-around labels, harness identification, electrical panels and industrial wiring.",
               "线缆标签解决方案 —— 旗形、缠绕、线束标识,面向配电柜与工业布线 由 ETIA 提供应用支持"),
  "primary_kw": "wire cable labeling solutions",
  "secondary_kw": ["wire labels", "cable labels", "flag labels", "wrap-around labels",
                   "heat-shrink labels", "harness identification", "wire number labels", "electrical panel labels"],
 },
 "outdoor": {
  "slug": "outdoor-energy-labeling-solutions",
  "banner": "",
  "hero_alt": ("Outdoor energy equipment carrying a weatherable rating label", "带耐候铭牌的户外能源设备"),
  "eyebrow": ("INDUSTRY LABELING SOLUTIONS", "行业标签解决方案"),
  "title": ("Outdoor & Energy Labeling Solutions", "户外与能源标签解决方案"),
  "headline": ("Durable Identification for Energy Systems and Outdoor Assets", "面向能源系统与户外资产的耐用标识"),
  "intro": ("Outdoor and energy labels carry critical information across solar installations, battery systems, substations, electrical equipment, utilities and infrastructure. ETIA helps manufacturers, installers and asset operators select durable labeling solutions for environments affected by sunlight, rain, temperature change, chemicals, abrasion and long service life.",
            "户外与能源标签在光伏电站、电池系统、变电站、电气设备、公用事业与基础设施中承载关键信息 ETIA 帮助制造商、安装商与资产运营方,为受日晒、雨淋、温变、化学品、磨损与长使用寿命影响的环境选择耐用标签方案"),
  "why_title": ("Why Outdoor and Energy Labeling Matters", "为什么户外与能源标签很重要"),
  "why": [
   ("Energy and infrastructure assets often operate far from controlled factory environments. Labels may be exposed continuously to UV radiation, moisture, dust, heat, cold, cleaning, oils and mechanical contact.",
    "能源与基础设施资产往往远离受控的工厂环境运行 标签可能持续暴露于紫外线、潮湿、粉尘、高温、低温、清洗、油污与机械接触"),
   ("At the same time, the information they carry remains essential. Technicians rely on labels to identify equipment, understand electrical hazards, locate circuits, follow operating instructions and maintain asset records. Machine-readable codes may also connect outdoor equipment with inspection, maintenance and asset-management systems.",
    "与此同时,它们承载的信息始终至关重要 技师依靠标签识别设备、了解电气危险、定位回路、遵循操作说明并维护资产记录 机器可读码还能把户外设备与巡检、维护及资产管理系统连接起来"),
   ("A reliable outdoor labeling solution must therefore do more than look clear when first applied. It must preserve adhesion, contrast and readability throughout the intended service period.",
    "因此,可靠的户外标签方案不能只是刚贴上时清晰 它必须在整个预期使用期内保持粘接、对比度与可读性"),
  ],
  "explore_title": ("Explore Outdoor & Energy Labeling Solutions", "探索户外与能源标签解决方案"),
  "categories": [
   {"name": ("Solar Energy Identification", "光伏标识"),
    "desc": ("Support installation, maintenance and safety communication across photovoltaic systems.",
             "支撑光伏系统的安装、维护与安全信息传达"),
    "apps": [("Solar Panel Identification","光伏组件标识"),("Inverter Labels","逆变器标签"),
             ("Combiner Box Labels","汇流箱标签"),("Cable and Circuit Identification","线缆与回路标识"),
             ("Electrical Warning Labels","电气警示标签")]},
   {"name": ("Battery Energy Storage", "电池储能"),
    "desc": ("Provide durable information for battery racks, modules, enclosures and energy-storage systems.",
             "为电池架、模组、机柜与储能系统提供耐久信息"),
    "apps": [("BESS Equipment Labels","储能设备标签"),("Battery Module Identification","电池模组标识"),
             ("High-Voltage Warnings","高压警示"),("Service and Maintenance Labels","维护标签"),
             ("Serialized Asset Tracking","序列化资产追踪")]},
   {"name": ("Electrical Safety & Compliance", "电气安全与合规"),
    "desc": ("Communicate electrical hazards and operating information clearly.",
             "清晰传达电气危险与操作信息"),
    "apps": [("Arc-Flash Labels","电弧闪络标签"),("High-Voltage Labels","高压标签"),
             ("Electrical Panel Labels","配电柜标签"),("Disconnect Identification","隔离开关标识"),
             ("Operating Instructions","操作说明")]},
   {"name": ("Utilities & Infrastructure", "公用事业与基础设施"),
    "desc": ("Maintain identification across distributed equipment and long-term outdoor assets.",
             "在分布式设备与长期户外资产上保持标识"),
    "apps": [("Pole and Cabinet Identification","杆塔与机柜标识"),("Substation Labels","变电站标签"),
             ("Meter and Transformer Labels","电表与变压器标签"),("Utility Asset Tracking","公用资产追踪"),
             ("Pipeline and Valve Identification","管道与阀门标识")]},
   {"name": ("Outdoor Equipment & Assets", "户外设备与资产"),
    "desc": ("Connect physical equipment with maintenance, inspection and digital asset records.",
             "把实物设备与维护、巡检及数字资产记录连接起来"),
    "apps": [("Equipment Nameplates","设备铭牌"),("Asset Barcode Labels","资产条码标签"),
             ("QR-Code Service Labels","二维码维护标签"),("Fleet and Machinery Identification","车队与机械标识"),
             ("Inspection Status Labels","巡检状态标签")]},
  ],
  "challenges": [
   ("☀️",("UV Exposure","紫外线")),("🌧️",("Rain and Humidity","雨水与潮湿")),("🌡️",("Heat and Cold","高低温")),
   ("🪨",("Abrasion","磨损")),("🛢️",("Chemicals and Oils","化学品与油污")),("🧱",("Textured Surfaces","纹理表面")),
   ("♾️",("Long Service Life","长使用寿命")),("📊",("Barcode Readability","条码可读")),
  ],
  "guide_desc": ("A practical overview of outdoor labeling applications, durability considerations, safety communication and evaluation methods for energy and infrastructure projects.",
                 "面向能源与基础设施项目的户外标签应用、耐久性考量、安全信息传达与评估方法的实用概览"),
  "res_desc": [
   ("Guidance for solar, battery storage, utilities and outdoor asset applications.","光伏、储能、公用事业与户外资产应用的指南"),
   ("Technical articles covering UV resistance, weatherability and surface adhesion.","关于耐紫外、耐候性与表面粘接的技术文章"),
   ("Examples of labels used in demanding outdoor and energy environments.","严苛户外与能源环境中标签应用的案例"),
  ],
  "cta_q": ("Need Help Selecting an Outdoor Labeling Solution?","需要帮助选择户外标签方案吗"),
  "cta_body": ("ETIA helps compare surface type, environmental exposure, expected lifetime, printing method and required safety or asset information.",
               "ETIA 帮助比较表面类型、环境暴露、预期寿命、打印方式以及所需的安全或资产信息"),
  "seo_title": ("Outdoor & Energy Labeling Solutions | ETIA", "户外与能源标签解决方案 | ETIA"),
  "seo_desc": ("Durable labeling solutions for solar, BESS, utilities, electrical safety, infrastructure and outdoor industrial assets.",
               "面向光伏、储能、公用事业、电气安全、基础设施与户外工业资产的耐用标签方案"),
  "primary_kw": "outdoor energy labeling solutions",
  "secondary_kw": ["solar labels", "BESS labels", "arc-flash labels", "high-voltage labels",
                   "utility labels", "outdoor asset labels", "weatherproof labels", "infrastructure labels"],
 },
 "steel": {
  "slug": "steel-metal-ceramic-labeling-solutions",
  "banner": "",
  "hero_alt": ("Steel coils in storage carrying identification tags", "存放中带标识挂签的钢卷"),
  "eyebrow": ("INDUSTRY LABELING SOLUTIONS", "行业标签解决方案"),
  "title": ("Steel, Metal & Ceramic Labeling Solutions", "钢铁、金属与陶瓷标签解决方案"),
  "headline": ("Reliable Identification Through Heat, Processing and Heavy Industry", "穿越高温、加工与重工业的可靠标识"),
  "intro": ("Steel, metal and ceramic manufacturing require identification that can survive conditions far beyond ordinary industrial labeling. From raw-material tracking and heat treatment to finishing, inventory and shipment, ETIA helps manufacturers select labeling solutions for high temperatures, rough surfaces, chemicals, abrasion and demanding production environments.",
            "钢铁、金属与陶瓷制造需要能够承受远超普通工业标签条件的标识 从原料追踪、热处理到精整、库存与发运,ETIA 帮助制造商为高温、粗糙表面、化学品、磨损与严苛生产环境选择标签方案"),
  "why_title": ("Why Labeling Matters in Heavy Manufacturing", "为什么重工业标签很重要"),
  "why": [
   ("Steel, aluminum, metal and ceramic products often move through multiple production stages before reaching the customer. Throughout this journey, manufacturers need to maintain the connection between the physical item and its heat number, batch, grade, production status, inspection result and destination.",
    "钢材、铝材、金属与陶瓷产品在到达客户前往往要经过多个生产阶段 在整个过程中,制造商需要把实物与其炉号、批次、牌号、生产状态、检验结果与去向保持关联"),
   ("The challenge is that identification may need to survive direct heat, rapid temperature change, scale, dust, impact, oil, chemical treatment or outdoor storage. In some applications, the label is applied at ambient temperature and must remain readable after a later thermal process. In others, identification must be attached directly to a hot product or suspended as a tag. The correct solution depends on when the information is applied, how it is attached and which stages it must survive.",
    "难点在于,标识可能需要承受直接高温、急剧温变、氧化皮、粉尘、冲击、油污、化学处理或户外存放 在有些应用中,标签在常温下贴附,并需在随后的热工序后仍可读;在另一些应用中,标识必须直接贴在高温产品上,或以挂签形式悬挂 正确的方案取决于信息在何时施加、如何附着,以及必须经受哪些阶段"),
  ],
  "explore_title": ("Explore Steel, Metal & Ceramic Labeling Solutions", "探索钢铁、金属与陶瓷标签解决方案"),
  "categories": [
   {"name": ("Hot-Material Identification", "高温产品标识"),
    "desc": ("Maintain identification on products that are already hot during labeling.",
             "在贴标时已处于高温状态的产品上保持标识"),
    "apps": [("Steel Billet Identification","钢坯标识"),("Slab and Bloom Tracking","板坯与初轧坯追踪"),
             ("Hot Coil Identification","热轧卷标识"),("Foundry Product Tracking","铸造产品追踪")]},
   {"name": ("Heat-Treatment Identification", "热处理标识"),
    "desc": ("Preserve batch and process information through furnaces, ovens and thermal cycles.",
             "在炉窑与热循环中保留批次与工艺信息"),
    "apps": [("Annealing Labels","退火标签"),("Heat-Treatment Batch Labels","热处理批次标签"),
             ("Powder-Coating Process Labels","粉末涂装工序标签"),("Furnace Tracking","炉内追踪"),
             ("Thermal Process Tags","热工序挂签")]},
   {"name": ("Coil, Sheet & Plate Tracking", "卷材、薄板与厚板追踪"),
    "desc": ("Track metal products throughout processing, storage and delivery.",
             "在加工、存储与交付全过程追踪金属产品"),
    "apps": [("Steel Coil Labels","钢卷标签"),("Aluminum Coil Identification","铝卷标识"),
             ("Sheet and Plate Labels","薄板与厚板标签"),("Cut-Length Product Tracking","定尺产品追踪"),
             ("Inventory Labels","库存标签")]},
   {"name": ("Ceramic & High-Temperature Processing", "陶瓷与高温加工"),
    "desc": ("Maintain identification through firing, glazing, coating and other thermal processes.",
             "在烧成、施釉、涂层等热工序中保持标识"),
    "apps": [("Ceramic Firing Labels","陶瓷烧成标签"),("Kiln Identification","窑炉标识"),
             ("Refractory Product Tracking","耐火材料追踪"),("Technical Ceramics","技术陶瓷"),
             ("Process Batch Labels","工序批次标签")]},
   {"name": ("Inventory, Quality & Shipping", "库存、质量与发运"),
    "desc": ("Connect finished products with inspection, warehouse and customer information.",
             "把成品与检验、仓储及客户信息连接起来"),
    "apps": [("Quality Status Labels","质量状态标签"),("Grade and Batch Identification","牌号与批次标识"),
             ("Warehouse Tracking","仓储追踪"),("Shipping Labels","发运标签"),
             ("Customer-Specific Barcodes","客户专属条码")]},
  ],
  "challenges": [
   ("🔥",("Extreme Heat","极端高温")),("🌡️",("Thermal Cycling","热循环")),("🧱",("Rough and Oxidized Surfaces","粗糙氧化表面")),
   ("🌫️",("Scale and Dust","氧化皮与粉尘")),("🛢️",("Oil and Chemicals","油污与化学品")),("🪨",("Abrasion","磨损")),
   ("💪",("Heavy Handling","重载搬运")),("🏭",("Outdoor Storage","户外存放")),
  ],
  "guide_desc": ("Explore high-temperature identification methods, process-labeling options, attachment considerations and evaluation steps for heavy manufacturing applications.",
                 "了解面向重工业应用的高温标识方法、工序标签选项、附着方式考量与评估步骤"),
  "res_desc": [
   ("Practical guidance for billets, coils, heat treatment and ceramic processing.","钢坯、卷材、热处理与陶瓷加工的实用指南"),
   ("Technical articles explaining direct-hot application, post-applied heat exposure and tag-based identification.","解读直接高温贴附、贴后受热与挂签标识的技术文章"),
   ("Examples of traceability challenges in demanding industrial processes.","严苛工业工艺中可追溯挑战的案例"),
  ],
  "cta_q": ("Need Help Selecting a High-Temperature Labeling Solution?","需要帮助选择高温标签方案吗"),
  "cta_body": ("ETIA helps define the application temperature, exposure time, surface condition, attachment method, printing process and required point of readability.",
               "ETIA 帮助明确施加温度、受热时长、表面状态、附着方式、打印工艺与所需的可读节点"),
  "seo_title": ("Steel, Metal & Ceramic Labeling Solutions | ETIA", "钢铁、金属与陶瓷标签解决方案 | ETIA"),
  "seo_desc": ("High-temperature labeling solutions for steel, aluminum, coils, billets, heat treatment, foundries and ceramic manufacturing.",
               "面向钢铁、铝材、卷材、钢坯、热处理、铸造与陶瓷制造的高温标签方案"),
  "primary_kw": "steel metal ceramic labeling solutions",
  "secondary_kw": ["steel coil labels", "billet labels", "heat treatment labels", "high temperature labels",
                   "foundry labels", "ceramic labels", "metal tags", "hot-material labels"],
 },
 "medical": {
  "slug": "medical-pharmaceutical-labeling-solutions",
  "banner": "",
  "hero_alt": ("Medical device and laboratory vials carrying identification labels", "带标识标签的医疗器械与实验室样品瓶"),
  "eyebrow": ("INDUSTRY LABELING SOLUTIONS", "行业标签解决方案"),
  "title": ("Medical, Pharmaceutical & Life Science Labeling Solutions", "医疗、制药与生命科学标签解决方案"),
  "headline": ("Reliable Identification from Manufacturing to Patient and Sample Use", "从生产到患者与样本使用的可靠标识"),
  "intro": ("Medical devices, pharmaceutical products, IVD workflows and life-science samples depend on accurate information at every stage. ETIA helps manufacturers and laboratories select labeling solutions for device identification, sample tracking, sterilization, cold storage, chemical exposure and long-term traceability.",
            "医疗器械、药品、体外诊断（IVD）流程与生命科学样本在每个阶段都依赖准确信息 ETIA 帮助制造商与实验室选择用于器械标识、样本追踪、灭菌、冷藏、化学品接触与长期追溯的标签方案"),
  "why_title": ("Why Medical and Life Science Labeling Matters", "为什么医疗与生命科学标签很重要"),
  "why": [
   ("In medical, pharmaceutical and laboratory environments, identification errors can disrupt manufacturing, quality control, testing, storage and clinical workflows.",
    "在医疗、制药与实验室环境中,标识错误可能扰乱生产、质量控制、检测、存储与临床流程"),
   ("Labels may need to connect devices, components, containers or samples with lot numbers, patient or study information, production records, expiration data and digital systems. Some information is read by operators and patients. Other information is captured through barcodes, QR codes or laboratory automation.",
    "标签可能需要把器械、组件、容器或样本与批号、患者或研究信息、生产记录、有效期数据及数字系统关联起来 有些信息由操作者与患者阅读,另一些则通过条码、二维码或实验室自动化采集"),
   ("The environment can also be demanding. Labels may encounter sterilization, disinfectants, alcohol, moisture, refrigeration, deep freezing, liquid nitrogen, centrifugation or repeated handling. The labeling solution must be selected for the complete workflow rather than a single temperature or chemical exposure.",
    "环境同样严苛 标签可能会遇到灭菌、消毒剂、酒精、潮湿、冷藏、深冷、液氮、离心或反复搬运 标签方案必须针对完整流程来选择,而非仅针对单一温度或化学品暴露"),
  ],
  "explore_title": ("Explore Medical, Pharmaceutical & Life Science Solutions", "探索医疗、制药与生命科学标签解决方案"),
  "categories": [
   {"name": ("Medical Device Identification", "医疗器械标识"),
    "desc": ("Maintain clear information throughout manufacturing, packaging, use and service.",
             "在生产、包装、使用与维护全过程保持清晰信息"),
    "apps": [("Medical Device Labels","医疗器械标签"),("Equipment Identification","设备标识"),
             ("Catheter and Tubing Labels","导管与管路标签"),("Component Traceability","组件追溯"),
             ("Durable Rating Labels","耐久铭牌标签")]},
   {"name": ("Pharmaceutical & Biopharmaceutical Labeling", "制药与生物制药标签"),
    "desc": ("Support product, batch and process identification across regulated production environments.",
             "在受监管的生产环境中支撑产品、批次与工艺标识"),
    "apps": [("Pharmaceutical Container Labels","药品容器标签"),("Clinical Trial Labels","临床试验标签"),
             ("Bioprocess Identification","生物工艺标识"),("Batch and Lot Tracking","批次追踪"),
             ("Small-Container Labels","小容器标签")]},
   {"name": ("IVD & Diagnostic Applications", "体外诊断与诊断应用"),
    "desc": ("Connect specimens, reagents, cartridges and diagnostic devices with accurate test information.",
             "把标本、试剂、卡盒与诊断器械与准确的检测信息关联起来"),
    "apps": [("IVD Cartridge Labels","IVD 卡盒标签"),("Reagent Labels","试剂标签"),
             ("Diagnostic Kit Identification","诊断试剂盒标识"),("Tube and Vial Labels","试管与样品瓶标签"),
             ("Barcode Sample Tracking","条码样本追踪")]},
   {"name": ("Laboratory & Cryogenic Identification", "实验室与深冷标识"),
    "desc": ("Protect sample identity from collection through long-term storage.",
             "从采集到长期存储保护样本身份"),
    "apps": [("Cryogenic Vial Labels","深冷样品瓶标签"),("Freezer Labels","冷冻标签"),
             ("Microscope Slide Labels","载玻片标签"),("Biobank Identification","生物样本库标识"),
             ("Tube and Plate Labels","试管与微孔板标签")]},
   {"name": ("Sterilization & Disinfection", "灭菌与消毒"),
    "desc": ("Maintain readable identification through validated cleaning and sterilization processes.",
             "在经验证的清洗与灭菌流程中保持可读标识"),
    "apps": [("Autoclave-Resistant Labels","耐高压灭菌标签"),("Gamma-Irradiation Labels","伽马辐照标签"),
             ("Ethylene Oxide Process Labels","环氧乙烷工序标签"),("IPA-Resistant Labels","耐 IPA 标签"),
             ("Chemical Disinfection Labels","化学消毒标签")]},
   {"name": ("Wearable & Skin-Contact Applications", "可穿戴与皮肤接触应用"),
    "desc": ("Support temporary or extended attachment to the body and wearable medical devices.",
             "支持在人体与可穿戴医疗器械上的临时或长时间贴附"),
    "apps": [("Wearable Sensor Labels","可穿戴传感器标签"),("Patch Device Constructions","贴片器械结构"),
             ("Patient-Monitoring Devices","患者监护设备"),("Skin-Contact Components","皮肤接触组件")]},
  ],
  "challenges": [
   ("🧫",("Sterilization","灭菌")),("🧪",("Disinfectants and IPA","消毒剂与 IPA")),("❄️",("Cryogenic Storage","深冷存储")),
   ("💧",("Moisture and Condensation","潮湿与冷凝")),("🔬",("Small Containers","小容器")),("🔎",("Fine Barcodes","精细条码")),
   ("🔢",("Variable Data","可变数据")),("♾️",("Long-Term Traceability","长期追溯")),
  ],
  "guide_desc": ("A practical guide covering device identification, IVD, laboratory tracking, sterilization, cryogenic storage and key material-selection considerations.",
                 "涵盖器械标识、IVD、实验室追踪、灭菌、深冷存储与关键选材考量的实用指南"),
  "res_desc": [
   ("Guidance for medical devices, pharmaceuticals, IVD, sterilization and laboratory identification.","医疗器械、制药、IVD、灭菌与实验室标识的指南"),
   ("Technical articles covering cryogenic adhesion, chemical resistance, small barcodes and workflow validation.","关于深冷粘接、耐化学、小条码与流程验证的技术文章"),
   ("Examples of identification challenges across manufacturing and laboratory environments.","生产与实验室环境中标识挑战的案例"),
  ],
  "cta_q": ("Need Help Selecting the Right Labeling Solution?","需要帮助选择合适的标签方案吗"),
  "cta_body": ("ETIA helps evaluate the container or device surface, workflow, storage temperature, sterilization method, chemical exposure, barcode format and required service life.",
               "ETIA 帮助评估容器或器械表面、流程、存储温度、灭菌方式、化学品暴露、条码格式与所需使用寿命"),
  "seo_title": ("Medical & Pharmaceutical Labeling Solutions | ETIA", "医疗与制药标签解决方案 | ETIA"),
  "seo_desc": ("Labeling solutions for medical devices, pharmaceuticals, IVD, sterilization, laboratories, cryogenic storage and life sciences.",
               "面向医疗器械、药品、IVD、灭菌、实验室、深冷存储与生命科学的标签方案"),
  "primary_kw": "medical labeling solutions",
  "secondary_kw": ["medical device labels", "pharmaceutical labels", "IVD labels", "cryogenic labels",
                   "sterilization labels", "laboratory labels", "life science labels", "wearable device labels"],
 },
}

# Final CTA is shared (industry-neutral wording per the standard).
FINAL_Q = ("Need Help Selecting the Right Labeling Solution?", "需要帮助选择合适的标签方案吗")
FINAL_BODY = ("Every production environment is different. ETIA helps manufacturers compare application conditions, evaluate materials and arrange samples for process testing on your own line. Tell us your surface, temperatures, chemistries and print method and we will recommend a practical starting point.",
              "每条产线的环境都不一样 ETIA 帮助制造商比较应用条件、评估材料,并安排样品在你自己的产线上做工艺测试 把你的贴附表面、温度、化学环境与打印方式告诉我们,我们会给出实用的起点")

CSS = """<style>
/* industry pages run tighter than the global rhythm to keep the hub scannable */
.blk{padding:26px 0}
.inhero{background:linear-gradient(115deg,rgba(9,24,64,.94),rgba(16,44,120,.72) 55%,rgba(26,86,219,.42)),__BG__ #0c2555;color:#fff}
.inhero .wrap{padding:46px 24px}.inhero .eyebrow{color:#9dbcff;font-size:12px;font-weight:800;letter-spacing:.08em}
.inhero h1{color:#fff;font-size:38px;font-weight:800;line-height:1.14;margin:8px 0 6px;max-width:20em}
.inhero .isub{color:#cfe0ff;font-size:19px;font-weight:700;line-height:1.35;margin:0 0 14px;max-width:26em}
.inhero p{color:#eef3ff;font-size:16px;line-height:1.66;max-width:52em}
.inbtns{margin-top:22px;display:flex;gap:12px;flex-wrap:wrap}
.inwhy{max-width:60em}.inwhy p{font-size:16px;line-height:1.75;color:var(--ink)}
.incat{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:16px}
.incard{border:1px solid var(--line);border-radius:14px;padding:18px 20px;background:#fff}
.incard h3{font-size:18px;font-weight:800;color:var(--blue-deep);margin:0 0 8px}
.incard .cd{font-size:14.5px;line-height:1.6;color:var(--mut)}
.incard .tl{font-size:11px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--faint);margin:16px 0 8px}
.incard ul{list-style:none;padding:0;margin:0}
.incard li{position:relative;padding-left:18px;font-size:14.5px;line-height:1.7;color:var(--ink)}
.incard li:before{content:"";position:absolute;left:2px;top:11px;width:5px;height:5px;border-radius:50%;background:var(--blue)}
.incard .go{display:inline-block;margin-top:14px;font-size:13px;font-weight:700;color:var(--green-d)}
.inchal{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:20px}
.inchi{border:1px solid var(--line);border-radius:12px;padding:18px 16px;background:#fff;text-align:center}
.inchi .ic{font-size:26px;line-height:1}.inchi .ct{font-size:14px;font-weight:800;color:var(--blue-deep);margin-top:9px}
.indl{border:1px solid var(--line);border-left:4px solid var(--blue);border-radius:12px;background:var(--tint-blue);padding:24px 26px;margin-top:8px}
.indl .dd{font-size:14.5px;color:var(--ink);line-height:1.65;max-width:52em}
.indl .db{margin-top:16px;display:flex;gap:12px;flex-wrap:wrap}
.inres{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:20px}
.inres.inres3{grid-template-columns:repeat(3,1fr)}
.inresc{border:1px solid var(--line);border-radius:14px;padding:22px;background:#fff;text-decoration:none;transition:.16s;display:block}
.inresc:hover{border-color:var(--blue);box-shadow:0 10px 26px rgba(20,40,90,.10);transform:translateY(-2px)}
.inresc h3{font-size:15.5px;font-weight:800;color:var(--blue-deep);margin:0 0 7px}
.inresc p{font-size:13px;color:var(--mut);line-height:1.55;margin:0}
.inresc .ar{color:var(--green-d);font-weight:700;font-size:13px;margin-top:10px;display:inline-block}
.incta{background:linear-gradient(120deg,#123a86,#1e50c7);border-radius:18px;padding:42px 28px;text-align:center;color:#fff;margin-top:8px}
.incta h2{color:#fff;font-size:24px;font-weight:800;margin:0 0 12px;line-height:1.3}
.incta p{color:#dbe6ff;font-size:15px;line-height:1.7;max-width:44em;margin:0 auto 20px}
.incta .db{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
@media(max-width:820px){.incat{grid-template-columns:1fr}.inchal{grid-template-columns:1fr 1fr}.inres{grid-template-columns:1fr 1fr}.inhero h1{font-size:29px}}
@media(max-width:520px){.inres{grid-template-columns:1fr}}
</style>"""


def build(lang, key):
    d = DATA[key]
    def T(pair): return esc(_t(lang, pair[0], pair[1]))
    def U(k): return esc(_t(lang, UI[k][0], UI[k][1]))
    path = "/industries/%s/" % d["slug"]
    contact = Lx(lang, CONTACT)
    bg = ("url('%s') center/cover no-repeat," % d["banner"]) if d["banner"] else ""
    css = CSS.replace("__BG__", bg)

    # Hero = two lines only: title + one-line slogan (no long paragraph).
    hero = ('<section class="inhero"><div class="wrap"><div class="eyebrow">%s</div>'
            '<h1>%s</h1><div class="isub">%s</div>'
            '<div class="inbtns"><a class="btn pri" href="#solutions">%s</a>'
            '<a class="btn on-dark" href="#guide">%s</a></div></div></section>') % (
        T(d["eyebrow"]), T(d["title"]), T(d["headline"]),
        U("primary_cta"), U("secondary_cta"))

    # "why" may be a single (en,zh) pair or a list of paragraph pairs
    whys = [d["why"]] if isinstance(d["why"][0], str) else d["why"]
    why = ('<section class="blk"><div class="wrap"><h2>%s</h2>'
           '<div class="inwhy">%s</div></div></section>') % (
        T(d["why_title"]), "".join("<p>%s</p>" % T(p) for p in whys))

    cards = ""
    for c in d["categories"]:
        lis = "".join("<li>%s</li>" % T(a) for a in c["apps"])
        cards += ('<div class="incard"><h3>%s</h3><div class="cd">%s</div>'
                  '<div class="tl">%s</div><ul>%s</ul>'
                  '<a class="go" href="%s">%s →</a></div>') % (
            T(c["name"]), T(c["desc"]), U("typical"), lis, Lx(lang, AN), U("explore_an"))
    explore = ('<section class="blk" id="solutions" style="background:var(--tint-blue)">'
               '<div class="wrap"><h2>%s</h2><div class="incat">%s</div></div></section>') % (
        T(d["explore_title"]), cards)

    chal_items = "".join('<div class="inchi"><div class="ic">%s</div><div class="ct">%s</div></div>'
                         % (ic, T(t)) for ic, t in d["challenges"])
    challenges = ('<section class="blk"><div class="wrap"><h2>%s</h2>'
                  '<div class="inchal">%s</div></div></section>') % (U("chal_title"), chal_items)

    guide_title = _t(lang, "Download the %s Guide" % d["title"][0],
                     "下载%s指南" % d["title"][1])
    guide = ('<section class="blk" id="guide" style="background:var(--tint-green)"><div class="wrap">'
             '<h2>%s</h2><div class="indl"><div class="dd">%s</div><div class="db">'
             '<a class="btn pri" href="%s">%s →</a><a class="btn sec" href="%s">%s</a>'
             '</div></div></div></section>') % (
        esc(guide_title), T(d["guide_desc"]), contact, U("guide_pdf"), contact, U("guide_preview"))

    # Three engineering-resource cards (Application Notes / Engineering Insights / Case
    # Studies). Descriptions come from per-industry "res_desc" (an, ei, cs), else UI defaults.
    rd = d.get("res_desc")
    res_titles = [("r_an", AN), ("r_ei", AN), ("r_cs", CS)]
    res_defaults = ["r_an_d", "r_ei_d", "r_cs_d"]
    res_cards = ""
    for i, (tk, u) in enumerate(res_titles):
        dsc = T(rd[i]) if rd else U(res_defaults[i])
        res_cards += ('<a class="inresc" href="%s"><h3>%s</h3><p>%s</p>'
                      '<span class="ar">→</span></a>') % (Lx(lang, u), U(tk), dsc)
    res = ('<section class="blk"><div class="wrap"><h2>%s</h2><div class="inres inres3">%s</div>'
           '</div></section>') % (U("res_title"), res_cards)

    cta_q = d.get("cta_q", FINAL_Q)
    cta_body = d.get("cta_body", FINAL_BODY)
    cta = ('<section class="blk"><div class="wrap"><div class="incta"><h2>%s</h2><p>%s</p>'
           '<div class="db"><a class="btn pri" href="%s">%s</a>'
           '<a class="btn on-dark" href="%s">%s</a></div></div></div></section>') % (
        T(cta_q), T(cta_body), contact, U("final_primary"), contact, U("final_secondary"))

    body = css + why + explore + challenges + guide + res + cta
    home = _t(lang, "Home", "首页")
    inds = _t(lang, "Industries", "行业")
    crumb = [(home, "/"), (inds, "/industries/"), (_t(lang, d["title"][0], d["title"][1]), path)]
    write(lang, path, page(lang, path,
        _t(lang, d["seo_title"][0], d["seo_title"][1]),
        _t(lang, d["seo_desc"][0], d["seo_desc"][1]),
        _t(lang, d["title"][0], d["title"][1]), "", body, crumb, active="", hero=hero))
    if lang == "en":
        hp.track(path, "industries")


URLS = ["/industries/%s/" % d["slug"] for d in DATA.values()]
# Old -> new URL redirects (the industry pages were renamed to the standard slug).
REDIRECTS = [
 ("/industries/automotive-label-materials", "/industries/automotive-labeling-solutions/"),
 ("/industries/circuit-board-pcb", "/industries/pcb-electronics-labeling-solutions/"),
]

def main():
    for lang in LANGS:
        for key in DATA:
            build(lang, key)

if __name__ == "__main__":
    main()
