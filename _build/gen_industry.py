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
  "banner": "https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com/A%E3%83%BBHERO%20banner%206%20%E7%BB%84/hero-automotive-tire.png",
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
  "banner": "https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com/A%E3%83%BBHERO%20banner%206%20%E7%BB%84/hero-electronics-pcb.png",
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
 # --- DRAFT copy (client to refine); structure + hero images are final ---
 "cable": {
  "slug": "cable-labeling-solutions",
  "banner": _HERO + "hero-wire-cable.png",
  "hero_alt": ("Bundled wires and cables carrying identification markers", "带标识的成束线缆"),
  "eyebrow": ("INDUSTRY LABELING SOLUTIONS", "行业标签解决方案"),
  "title": ("Cable & Wire Labeling Solutions", "线缆标签解决方案"),
  "headline": ("Durable Identification for Wire, Cable and Harness", "面向线缆与线束的耐用标识"),
  "intro": ("From wire and cable manufacturing to harness assembly and field installation, markers identify the conductors, circuits and assemblies that must stay readable for the life of the installation. ETIA helps manufacturers match self-laminating, heat-shrink and flag label materials to each conductor size and environment.",
            "从线缆制造到线束装配与现场安装,标识标签用于区分导线、回路与组件,并需在安装的整个寿命中保持可读 ETIA 帮助制造商为各种线径与环境匹配自贴合、热缩与旗形标签材料"),
  "why_title": ("Why Cable Labeling Matters", "为什么线缆标签很重要"),
  "why": ("Wire and cable identification must survive bending, abrasion, oils, sunlight and years of service — often on small conductors with little room to print. A durable, correctly matched marker keeps circuits traceable through manufacturing, installation and maintenance, and prevents the costly errors that come from mis-identified conductors.",
          "线缆标识必须经受弯折、磨损、油污、日晒与多年使用 —— 而且往往是在可打印空间很小的细导线上 一个耐用且匹配得当的标识,让回路在制造、安装与维护中保持可追溯,并避免导线标识错误带来的高昂损失"),
  "explore_title": ("Explore Cable Labeling Solutions", "探索线缆标签解决方案"),
  "categories": [
   {"name": ("Wire & Cable Marking", "线缆标识"),
    "desc": ("Durable conductor and cable identification that stays put through flexing and handling.",
             "经受弯折与搬运仍不脱落的导线与线缆标识"),
    "apps": [("Self-Laminating Labels","自贴合标签"),("Heat-Shrink Sleeves","热缩套管"),
             ("Flag Labels","旗形标签"),("Wrap-Around Labels","缠绕标签")]},
   {"name": ("Harness Assembly", "线束装配"),
    "desc": ("Identification and tracking for harness components and bundles in assembly.",
             "线束组件与线束在装配中的标识与追踪"),
    "apps": [("Component Labels","元件标签"),("Bundle Labels","线束标签"),
             ("WIP Tracking","在制品追踪"),("Circuit Identification","回路标识")]},
   {"name": ("Datacom & Network", "数据与网络"),
    "desc": ("Clear identification for network cabling, panels and faceplates.",
             "网络布线、配线架与面板的清晰标识"),
    "apps": [("Patch Panel Labels","配线架标签"),("Faceplate Labels","面板标签"),
             ("Cable Bundle Labels","线束标签")]},
   {"name": ("Field & Installation", "现场与安装"),
    "desc": ("Weatherable identification and safety marking for installed cable.",
             "已安装线缆的耐候标识与安全标记"),
    "apps": [("Voltage Markers","电压标识"),("Warning Labels","警告标签"),("Asset Labels","资产标签")]},
  ],
  "challenges": [
   ("🔁",("Bending & Flexing","弯折")),("🪨",("Abrasion","磨损")),("🛢️",("Oil & Fluids","油液")),
   ("☀️",("UV Exposure","紫外线")),("📏",("Small Diameter","细线径")),("💧",("Moisture","潮湿")),
   ("♾️",("Long-Term Durability","长期耐久")),("⚙️",("Automated Application","自动贴标")),
  ],
  "guide_desc": ("The guide gives an application overview, the key labeling challenges across wire, cable and harness, the main selection considerations, typical labeling technologies and a recommended evaluation path before you specify materials.",
                 "本指南提供应用概览、线缆与线束的主要标签挑战、核心选型考量、常用标签技术以及在确定材料前推荐的评估路径"),
  "seo_title": ("Cable & Wire Labeling Solutions | ETIA", "线缆标签解决方案 | ETIA"),
  "seo_desc": ("Durable wire, cable and harness labels — self-laminating, heat-shrink and flag markers that stay readable through flexing, abrasion and outdoor service. ETIA application support.",
               "耐用的线缆与线束标签 —— 自贴合、热缩与旗形标识,经受弯折、磨损与户外使用仍可读 由 ETIA 提供应用支持"),
  "primary_kw": "cable labeling solutions",
  "secondary_kw": ["wire labels", "cable markers", "self-laminating labels", "heat-shrink sleeves",
                   "harness labels", "wire identification", "flag labels", "datacom labels"],
 },
 "outdoor": {
  "slug": "outdoor-labeling-solutions",
  "banner": _HERO + "hero-outdoor-energy.png",
  "hero_alt": ("Outdoor energy equipment carrying a weatherable rating label", "带耐候铭牌的户外能源设备"),
  "eyebrow": ("INDUSTRY LABELING SOLUTIONS", "行业标签解决方案"),
  "title": ("Outdoor & Energy Labeling Solutions", "户外与能源标签解决方案"),
  "headline": ("Identification That Survives Years Outdoors", "经久户外的可靠标识"),
  "intro": ("From solar and energy equipment to outdoor infrastructure, labels must stay legible through years of sun, rain, temperature swings and handling. ETIA helps manufacturers match weatherable label materials to each outdoor surface, exposure and compliance requirement.",
            "从光伏与能源设备到户外基础设施,标签必须在多年日晒、雨淋、温差与搬运中保持清晰 ETIA 帮助制造商为各种户外表面、暴露条件与合规要求匹配耐候标签材料"),
  "why_title": ("Why Outdoor Labeling Matters", "为什么户外标签很重要"),
  "why": ("Outdoor labels face constant UV, moisture, temperature cycling and abrasion. When a rating plate fades or a warning peels, safety information and asset traceability are lost — and field replacement is expensive. Weatherable materials, matched to the surface and exposure, keep identification readable for the service life of the equipment.",
          "户外标签持续面对紫外线、潮湿、温度循环与磨损 一旦铭牌褪色或警示翘起,安全信息与资产追溯就会丢失 —— 而现场更换成本高昂 与表面和暴露条件匹配的耐候材料,让标识在设备整个使用寿命中保持可读"),
  "explore_title": ("Explore Outdoor & Energy Labeling Solutions", "探索户外与能源标签解决方案"),
  "categories": [
   {"name": ("Equipment Identification", "设备标识"),
    "desc": ("Permanent rating and asset identification for outdoor equipment.",
             "面向户外设备的永久铭牌与资产标识"),
    "apps": [("Rating Plates","铭牌"),("Serial Number Labels","序列号标签"),
             ("Asset Labels","资产标签"),("QR Code Labels","二维码标签")]},
   {"name": ("Safety & Warning", "安全与警示"),
    "desc": ("Durable safety communication that stays legible outdoors.",
             "在户外仍清晰可读的耐久安全信息"),
    "apps": [("High Voltage Labels","高压标签"),("Warning Labels","警告标签"),("Caution Labels","注意标签")]},
   {"name": ("Energy & Solar", "能源与光伏"),
    "desc": ("Identification and compliance marking for solar and energy assets.",
             "面向光伏与能源资产的标识与合规标记"),
    "apps": [("Module Labels","组件标签"),("Junction Box Labels","接线盒标签"),("Compliance Labels","合规标签")]},
   {"name": ("Compliance & Certification", "合规与认证"),
    "desc": ("Weatherable identification that meets regulatory requirements.",
             "满足法规要求的耐候标识"),
    "apps": [("Regulatory Labels","法规标签"),("Certification Labels","认证标签")]},
  ],
  "challenges": [
   ("☀️",("UV Exposure","紫外线")),("💧",("Moisture","潮湿")),("🌡️",("Temperature Cycling","温度循环")),
   ("🪨",("Abrasion","磨损")),("🌧️",("Weathering","风化")),("♾️",("Long-Term Durability","长期耐久")),
   ("🧴",("Low-Surface-Energy Plastics","低表面能塑料")),("🏭",("Outdoor Exposure","户外暴露")),
  ],
  "guide_desc": ("The guide gives an application overview, the key outdoor labeling challenges, the main selection considerations, typical labeling technologies and a recommended evaluation path before you specify materials.",
                 "本指南提供应用概览、户外标签的主要挑战、核心选型考量、常用标签技术以及在确定材料前推荐的评估路径"),
  "seo_title": ("Outdoor & Energy Labeling Solutions | ETIA", "户外与能源标签解决方案 | ETIA"),
  "seo_desc": ("Weatherable outdoor and energy labels — rating plates, safety and solar identification that resist UV, moisture and temperature cycling for years. ETIA application support.",
               "耐候的户外与能源标签 —— 铭牌、安全与光伏标识,多年抵御紫外线、潮湿与温度循环 由 ETIA 提供应用支持"),
  "primary_kw": "outdoor labeling solutions",
  "secondary_kw": ["weatherproof labels", "UV-resistant labels", "solar labels", "rating plates",
                   "outdoor asset labels", "energy equipment labels", "durable outdoor labels", "compliance labels"],
 },
 "medical": {
  "slug": "medical-labeling-solutions",
  "banner": _HERO + "hero-medical-laboratory.png",
  "hero_alt": ("Medical device and laboratory vials carrying identification labels", "带标识标签的医疗器械与实验室样品瓶"),
  "eyebrow": ("INDUSTRY LABELING SOLUTIONS", "行业标签解决方案"),
  "title": ("Medical & Life Sciences Labeling Solutions", "医疗与生命科学标签解决方案"),
  "headline": ("Reliable Identification for Devices, Diagnostics and Labs", "面向器械、诊断与实验室的可靠标识"),
  "intro": ("From medical device manufacturing to diagnostics and laboratory workflows, labels carry the identification and traceability that patient safety and regulatory compliance depend on. ETIA helps manufacturers match label materials to sterilization, cold storage, chemical exposure and small-part marking.",
            "从医疗器械制造到诊断与实验室流程,标签承载着患者安全与法规合规所依赖的标识与追溯 ETIA 帮助制造商为灭菌、冷藏、化学品接触与小部件标记匹配标签材料"),
  "why_title": ("Why Medical Labeling Matters", "为什么医疗标签很重要"),
  "why": ("Medical and laboratory labels must stay bonded and readable through sterilization, cold storage, solvents and handling, often on small vials, devices and instruments. When identification fails, samples are lost and traceability breaks — so the labeling choice supports both regulatory compliance and patient safety.",
          "医疗与实验室标签必须经受灭菌、冷藏、溶剂与搬运仍牢固可读,而且往往贴在小瓶、器械与仪器上 一旦标识失效,样品丢失、追溯中断 因此标签选择同时支撑法规合规与患者安全"),
  "explore_title": ("Explore Medical Labeling Solutions", "探索医疗标签解决方案"),
  "categories": [
   {"name": ("Device Identification", "器械标识"),
    "desc": ("Permanent identification for medical devices, instruments and components.",
             "面向医疗器械、仪器与部件的永久标识"),
    "apps": [("UDI Labels","UDI 标签"),("Instrument Labels","器械标签"),("Component Labels","元件标签")]},
   {"name": ("Diagnostics & Lab", "诊断与实验室"),
    "desc": ("Identification that survives cold storage and lab chemistries.",
             "经受冷藏与实验室化学环境的标识"),
    "apps": [("Vial Labels","样品瓶标签"),("Cryogenic Labels","深冷标签"),
             ("Slide Labels","载玻片标签"),("Specimen Labels","标本标签")]},
   {"name": ("Sterilization", "灭菌"),
    "desc": ("Labels that stay bonded and readable through sterilization cycles.",
             "经受灭菌循环仍牢固可读的标签"),
    "apps": [("Autoclave Labels","高压灭菌标签"),("Sterilization Indicator Labels","灭菌指示标签")]},
   {"name": ("Traceability & Compliance", "追溯与合规"),
    "desc": ("Barcode and lot identification for full-chain traceability.",
             "面向全链路追溯的条码与批次标识"),
    "apps": [("Barcode Labels","条码标签"),("Lot Labels","批次标签"),("Compliance Labels","合规标签")]},
  ],
  "challenges": [
   ("🧫",("Sterilization","灭菌")),("❄️",("Cold / Cryogenic","冷藏 / 深冷")),("🧪",("Chemicals","化学品")),
   ("🔎",("Small Labels","小标签")),("💧",("Moisture","潮湿")),("🪨",("Abrasion","磨损")),
   ("♾️",("Long-Term Durability","长期耐久")),("⚙️",("Automated Application","自动贴标")),
  ],
  "guide_desc": ("The guide gives an application overview, the key labeling challenges across devices, diagnostics and labs, the main selection considerations, typical labeling technologies and a recommended evaluation path before you specify materials.",
                 "本指南提供应用概览、器械、诊断与实验室的主要标签挑战、核心选型考量、常用标签技术以及在确定材料前推荐的评估路径"),
  "seo_title": ("Medical & Life Sciences Labeling Solutions | ETIA", "医疗与生命科学标签解决方案 | ETIA"),
  "seo_desc": ("Durable medical and lab labels — UDI, vial, cryogenic and sterilization identification that survives cold storage, solvents and autoclaving. ETIA application support.",
               "耐用的医疗与实验室标签 —— UDI、样品瓶、深冷与灭菌标识,经受冷藏、溶剂与高压灭菌 由 ETIA 提供应用支持"),
  "primary_kw": "medical labeling solutions",
  "secondary_kw": ["medical device labels", "UDI labels", "cryogenic labels", "vial labels",
                   "laboratory labels", "sterilization labels", "specimen labels", "life sciences labels"],
 },
 "steel": {
  "slug": "steel-labeling-solutions",
  "banner": _HERO + "hero-metals-ceramics.png",
  "hero_alt": ("Steel coils in storage carrying identification tags", "存放中带标识挂签的钢卷"),
  "eyebrow": ("INDUSTRY LABELING SOLUTIONS", "行业标签解决方案"),
  "title": ("Steel & Metals Labeling Solutions", "钢铁与金属标签解决方案"),
  "headline": ("Identification That Survives Heat, Handling and Storage", "经受高温、搬运与存放的可靠标识"),
  "intro": ("From steel and metal production to heat treatment and warehouse tracking, labels and tags must survive high temperature, rough handling, oils and long outdoor storage. ETIA helps manufacturers match durable label and tag materials to each stage of metal processing and logistics.",
            "从钢铁与金属生产到热处理与仓储追踪,标签与挂签必须经受高温、粗放搬运、油污与长期户外存放 ETIA 帮助制造商为金属加工与物流的各个阶段匹配耐用标签与挂签材料"),
  "why_title": ("Why Steel Labeling Matters", "为什么钢铁标签很重要"),
  "why": ("Metal processing is one of the harshest labeling environments — high heat, scale, oils, abrasion and months of outdoor storage. When a tag is lost, coils and plates lose their identity and traceability breaks. Materials matched to the temperature and handling of each stage keep identification intact from the mill through dispatch.",
          "金属加工是最严苛的标签环境之一 —— 高温、氧化皮、油污、磨损与数月户外存放 一旦挂签丢失,钢卷与钢板便失去身份、追溯中断 与各阶段温度和搬运方式匹配的材料,让标识从轧机到发运始终完好"),
  "explore_title": ("Explore Steel & Metals Labeling Solutions", "探索钢铁与金属标签解决方案"),
  "categories": [
   {"name": ("Production & Heat Treatment", "生产与热处理"),
    "desc": ("High-temperature identification through production and heat treatment.",
             "贯穿生产与热处理的耐高温标识"),
    "apps": [("High-Temperature Labels","耐高温标签"),("Heat-Treatment Tags","热处理挂签"),
             ("Billet & Coil Labels","钢坯与钢卷标签")]},
   {"name": ("Warehouse & Logistics", "仓储与物流"),
    "desc": ("Durable identification for coils, bundles and racks in storage.",
             "面向钢卷、捆料与货架存放的耐用标识"),
    "apps": [("Coil Labels","钢卷标签"),("Bundle Tags","捆料挂签"),
             ("Rack Labels","货架标签"),("Barcode Labels","条码标签")]},
   {"name": ("Identification & Grading", "标识与分级"),
    "desc": ("Grade and serial identification for traceability and inspection.",
             "面向追溯与检验的牌号与序列标识"),
    "apps": [("Grade Labels","牌号标签"),("Serial Number Tags","序列号挂签"),("Inspection Labels","检验标签")]},
   {"name": ("Outdoor Storage", "户外存放"),
    "desc": ("Weatherable tags and labels for long outdoor storage.",
             "面向长期户外存放的耐候挂签与标签"),
    "apps": [("Weatherable Tags","耐候挂签"),("Asset Labels","资产标签")]},
  ],
  "challenges": [
   ("🔥",("High Heat","高温")),("🪨",("Scale & Abrasion","氧化皮与磨损")),("🛢️",("Oil & Fluids","油液")),
   ("🏭",("Outdoor Storage","户外存放")),("💧",("Moisture","潮湿")),("💪",("Rough Handling","粗放搬运")),
   ("♾️",("Long-Term Durability","长期耐久")),("🧴",("Low-Surface-Energy","低表面能")),
  ],
  "guide_desc": ("The guide gives an application overview, the key labeling challenges across metal production, heat treatment and storage, the main selection considerations, typical labeling technologies and a recommended evaluation path before you specify materials.",
                 "本指南提供应用概览、金属生产、热处理与存放的主要标签挑战、核心选型考量、常用标签技术以及在确定材料前推荐的评估路径"),
  "seo_title": ("Steel & Metals Labeling Solutions | ETIA", "钢铁与金属标签解决方案 | ETIA"),
  "seo_desc": ("Durable steel and metals labels and tags — high-temperature, coil and heat-treatment identification that survives heat, scale and outdoor storage. ETIA application support.",
               "耐用的钢铁与金属标签及挂签 —— 耐高温、钢卷与热处理标识,经受高温、氧化皮与户外存放 由 ETIA 提供应用支持"),
  "primary_kw": "steel labeling solutions",
  "secondary_kw": ["metal labels", "coil labels", "high temperature tags", "heat treatment labels",
                   "steel tags", "billet labels", "warehouse labels", "durable metal tags"],
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

    hero = ('<section class="inhero"><div class="wrap"><div class="eyebrow">%s</div>'
            '<h1>%s</h1><div class="isub">%s</div><p>%s</p>'
            '<div class="inbtns"><a class="btn pri" href="#solutions">%s</a>'
            '<a class="btn on-dark" href="#guide">%s</a></div></div></section>') % (
        T(d["eyebrow"]), T(d["title"]), T(d["headline"]), T(d["intro"]),
        U("primary_cta"), U("secondary_cta"))

    why = ('<section class="blk"><div class="wrap"><h2>%s</h2>'
           '<div class="inwhy"><p>%s</p></div></div></section>') % (
        T(d["why_title"]), T(d["why"]))

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

    res_cards = [("r_an", "r_an_d", AN), ("r_ei", "r_ei_d", AN),
                 ("r_cs", "r_cs_d", CS), ("r_faq", "r_faq_d", CONTACT)]
    res = ('<section class="blk"><div class="wrap"><h2>%s</h2><div class="inres">%s</div>'
           '</div></section>') % (
        U("res_title"),
        "".join('<a class="inresc" href="%s"><h3>%s</h3><p>%s</p><span class="ar">→</span></a>'
                % (Lx(lang, u), U(t), U(dsc)) for t, dsc, u in res_cards))

    cta = ('<section class="blk"><div class="wrap"><div class="incta"><h2>%s</h2><p>%s</p>'
           '<div class="db"><a class="btn pri" href="%s">%s</a>'
           '<a class="btn on-dark" href="%s">%s</a></div></div></div></section>') % (
        esc(_t(lang, FINAL_Q[0], FINAL_Q[1])), esc(_t(lang, FINAL_BODY[0], FINAL_BODY[1])),
        contact, U("final_primary"), contact, U("final_secondary"))

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
