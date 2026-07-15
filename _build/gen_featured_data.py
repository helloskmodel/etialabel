#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build _build/data/featured.json — ETIA Selected Harsh Environment Labels.

Homepage shows 6; /featured-solutions/ center shows all 8. Claim-gating per spec §8:
only claim_status == verified numbers/claims are public (HP900 900°C, HP CX 1300°C,
APEX +72% flux). Unsupported claims (E-4812 FDA adhesive, E-2813 "3x", APEX 15%/UL,
absolute wording) are NOT rendered. E-2813RF is excluded entirely. No values invented.
"""
import json, os
BUILD=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(BUILD,"data","featured.json")

# harsh-condition filter categories (spec §10)
CONDITIONS=[
 ("extreme-cold","Extreme Cold","超低温"),
 ("extreme-heat","Extreme Heat","超高温"),
 ("chemical-exposure","Chemical Exposure","化学暴露"),
 ("abrasion-rough","Abrasion & Rough Surfaces","磨损与粗糙表面"),
 ("tamper-evidence","Tamper Evidence","防篡改"),
 ("pcb-process","PCB Process","PCB制程"),
]

def F(pid,model,slug,ind_en,ind_zh,harsh_en,harsh_zh,one_en,one_zh,tags_en,tags_zh,
      conditions,home,order,maps_to=None,verified_en=None,verified_zh=None,
      challenge_en=None,challenge_zh=None,apps_en=None,apps_zh=None):
    return {"id":pid,"model":model,"slug":slug,"industry_en":ind_en,"industry_zh":ind_zh,
        "harsh_en":harsh_en,"harsh_zh":harsh_zh,"one_liner_en":one_en,"one_liner_zh":one_zh,
        "tags_en":tags_en,"tags_zh":tags_zh,"harsh_conditions":conditions,
        "homepage_featured":home,"featured_order":order,"maps_to":maps_to,
        "verified_claim_en":verified_en,"verified_claim_zh":verified_zh,
        "challenge_en":challenge_en,"challenge_zh":challenge_zh,
        "applications_en":apps_en or [],"applications_zh":apps_zh or [],
        "tds_url":None,"tds_available":False}  # fill tds_url with the COS link when supplied

PRODUCTS=[
 F("fps-e-4812","E-4812","e-4812-cryogenic-direct-apply-label",
   "Medical & Laboratory","医疗与实验室",
   "-196°C Cryogenic Identification","-196℃液氮存储标签",
   "Apply directly at ultra-low temperature without thawing stored samples.",
   "在超低温下直接贴标,无需解冻已存样本。",
   ["Cryogenic","Freeze-Thaw","Chemical Resistant"],["超低温","冻融循环","耐化学"],
   ["extreme-cold","chemical-exposure"],True,1,
   challenge_en="Ultra-low-temperature direct application, liquid-nitrogen storage, freeze-thaw cycling and exposure to media such as DMSO, methanol, IPA and ethanol.",
   challenge_zh="超低温直接贴标、液氮存储、冻融循环,以及 DMSO、甲醇、IPA、乙醇等介质暴露。",
   apps_en=["Cryovial and sample identification","Liquid-nitrogen (vapor / liquid phase) storage","Biobank and freezer inventory","Freeze-thaw sample tracking"],
   apps_zh=["冻存管与样本识别","液氮(气相/液相)存储","生物样本库与冰箱库存","冻融样本追踪"]),
 F("fps-hp900","HP900","hp900-hot-metal-direct-apply-label",
   "Steel & Metal","钢铁与金属",
   "900°C Hot-Metal Direct Apply","900℃热态金属直贴标签",
   "Apply identification directly onto hot metal surfaces up to 900°C.",
   "在最高 900℃ 的热态金属表面直接贴标。",
   ["900°C (verified)","Direct-Apply","Heat-Treatment"],["900℃(已验证)","热态直贴","热处理"],
   ["extreme-heat"],True,2,maps_to="hp-900",
   verified_en="Direct application to hot metal surfaces up to 900°C is demonstrated (verified).",
   verified_zh="最高 900℃ 热态金属表面直接贴标具有证明(已验证)。"),
 F("fps-hp-cx","HP CX11/CX2","hp-cx11-cx2-ceramic-kiln-label",
   "Ceramics & Sanitaryware","陶瓷与卫浴",
   "1300°C Kiln Firing","1300℃陶瓷烧制标签",
   "Track ceramic ware through kiln firing up to 1300°C.",
   "在最高 1300℃ 的窑炉烧制中追踪陶瓷制品。",
   ["1300°C (verified)","Kiln Firing","Acid-Wash"],["1300℃(已验证)","窑炉烧制","酸洗"],
   ["extreme-heat","chemical-exposure"],True,3,maps_to="hp-cbr-cx2",
   verified_en="1300°C ceramic kiln firing is demonstrated (verified).",
   verified_zh="1300℃ 陶瓷窑炉烧制性能具有证明(已验证)。"),
 F("fps-e-2314","E-2314","e-2314-tire-vulcanization-barcode-label",
   "Tire & Rubber","轮胎与橡胶",
   "Tire Vulcanization Barcode","轮胎硫化条码标签",
   "Keep barcodes readable through ~200°C vulcanization, pressure and chemicals.",
   "在约 200℃ 硫化、压力与化学品中保持条码可读。",
   ["~200°C Process","Pressure","Chemical Resistant"],["约200℃制程","耐压","耐化学"],
   ["extreme-heat","chemical-exposure"],True,4,
   challenge_en="Tire vulcanization at ~200°C with pressure, acids/alkalis, oils and cleaning agents, followed by outdoor, ozone and UV exposure.",
   challenge_zh="约 200℃ 轮胎硫化,伴随压力、酸碱、油污与清洗剂,随后经历户外、臭氧与紫外线暴露。",
   apps_en=["Green-tire barcode tracking","Vulcanization process traceability","Cured-tire identification"],
   apps_zh=["生胎条码追踪","硫化过程追溯","成品轮胎识别"]),
 F("fps-e-2532bl","E-2532BL","e-2532bl-laser-tamper-evident-vin-label",
   "Automotive","汽车",
   "Laser Tamper-Evident VIN","激光防篡改VIN标签",
   "Laser-markable VIN identification with tamper-evident, weatherable construction.",
   "可激光打标的 VIN 标识,具备防篡改、耐候结构。",
   ["Tamper-Evident","Laser-Markable","Weatherable"],["防篡改","激光可标记","耐候"],
   ["tamper-evidence"],True,5,
   challenge_en="Vehicle identification (VIN) requiring laser marking, tamper and transfer resistance, and durability against weather, abrasion and automotive chemicals.",
   challenge_zh="车辆身份识别(VIN)需激光加工,并具备防篡改、防转移,以及耐候、耐磨与耐汽车化学品的耐久性。",
   apps_en=["VIN plates and labels","Anti-transfer security identification","Vehicle compliance marking"],
   apps_zh=["VIN 铭牌与标签","防转移安全识别","车辆合规标识"]),
 F("fps-xf-581","XF-581","xf-581-polyimide-pcb-label-material",
   "Electronics Manufacturing","电子制造",
   "High-Temp PCB Polyimide","PCB耐高温PI标签",
   "Polyimide identification through reflow soldering, high heat and chemical cleaning.",
   "聚酰亚胺标识,可经受回流焊、高温与化学清洗。",
   ["PCB","Reflow","Wash-Resistant"],["PCB","回流焊","耐清洗"],
   ["extreme-heat","pcb-process","chemical-exposure"],True,6,
   challenge_en="PCB and electronic-component tracking through reflow soldering and high-temperature processing with chemical cleaning, across automotive, medical and avionics electronics.",
   challenge_zh="PCB 与电子元件在回流焊及高温处理、化学清洗中的追踪,覆盖汽车、医疗与航空电子。",
   apps_en=["PCB traceability barcodes","Component pre-process identification","Work-in-process tracking"],
   apps_zh=["PCB 追溯条码","元件制程前标识","在制品追踪"]),
 F("fps-e-2813","E-2813","e-2813-aggressive-adhesive-label-material",
   "Automotive Parts","汽车零部件",
   "Aggressive Adhesive for Rough & Oily Surfaces","粗糙油污表面强粘标签",
   "Bonds to powder-coated, rough and oily surfaces where standard labels lift.",
   "可粘附于普通标签易翘的粉末涂层、粗糙及油污表面。",
   ["Rough Surface","Oily Surface","Powder-Coat"],["粗糙表面","油污表面","粉末涂层"],
   ["abrasion-rough"],False,7,
   challenge_en="Powder-coated, rough and oily surfaces on automotive parts, molds and large equipment where standard adhesives lift or fail.",
   challenge_zh="汽车零件、模具与大型设备的粉末涂层、粗糙及油污表面,普通胶黏剂易翘边或失效。",
   apps_en=["Automotive parts marking","Mold and tooling identification","Large-equipment nameplates"],
   apps_zh=["汽车零件标识","模具与工装识别","大型设备铭牌"]),
 F("fps-apex","APEX","apex-high-performance-polyimide-pcb-labels",
   "Electronics Manufacturing","电子制造",
   "High-Performance PI for Modern PCB","现代PCB高性能PI标签",
   "Engineered for modern PCB fluxes and cleaners with multi-reflow durability.",
   "面向现代 PCB 助焊剂与清洗剂,具备多次回流焊耐久性。",
   ["+72% Flux (verified)","Multi-Reflow","ESD Option"],["助焊+72%(已验证)","多次回流","ESD可选"],
   ["extreme-heat","pcb-process","chemical-exposure"],False,8,
   verified_en="72% flux-resistance improvement versus the previous product line (tested).",
   verified_zh="助焊剂性能较上一代产品线提升 72%(有试验佐证)。",
   challenge_en="Modern PCB fluxes and cleaners, multiple reflow cycles, and small-font barcode legibility with optional ESD control.",
   challenge_zh="现代 PCB 助焊剂与清洗剂、多次回流焊,以及小字体条码可读性,并可选 ESD 控制。",
   apps_en=["High-density PCB traceability","Multi-reflow assembly tracking","ESD-controlled electronics"],
   apps_zh=["高密度 PCB 追溯","多次回流装配追踪","ESD 管控电子"]),
]
# NOTE: E-2813RF intentionally excluded — no card, route or landing page (spec §3, §13.10).

data={"center_route":"/featured-solutions/","conditions":[{"slug":s,"en":e,"zh":z} for s,e,z in CONDITIONS],
      "products":PRODUCTS}

home=[p for p in PRODUCTS if p["homepage_featured"]]
assert len(home)==6, "homepage must feature exactly 6"
cond_slugs={s for s,_,_ in CONDITIONS}
for p in PRODUCTS:
    for c in p["harsh_conditions"]:
        assert c in cond_slugs, "bad condition %s"%c
os.makedirs(os.path.dirname(OUT),exist_ok=True)
json.dump(data,open(OUT,"w"),ensure_ascii=False,indent=1)
print("products:",len(PRODUCTS),"| homepage:",len(home),"| landings(new):",sum(1 for p in PRODUCTS if not p["maps_to"]))
print("verified claims:",[p["model"] for p in PRODUCTS if p["verified_claim_en"]])
print("maps to existing:",[(p["model"],p["maps_to"]) for p in PRODUCTS if p["maps_to"]])
