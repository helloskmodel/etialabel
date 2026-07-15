#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build _build/data/healthcare.json from the Healthcare & Life Sciences brief.

Dual path (brief §1): Find by Application (5) + Find by Requirement / 工况 (9).
Same product data feeds both; one canonical product record/page each.

Compliance (brief §6):
 - ETIA = supplier / solution provider, NOT the manufacturer; FLEXcon / BIO TECH
   manufacturing, R&D and certification are not written as ETIA's own.
 - Biocompatibility, UL/IEC/FDA, temperature and regulatory info bind to the named
   series / part number only — never generalized to all materials.
 - Omni-Wave is a conductive transfer material, described separately from print labels.
 - Blood bags: application = Pharmaceutical; requirement = Low-Temperature & Frozen;
   NOT placed under Pharmaceutical Packaging & Security.
 - Only brochure-listed facts recorded; missing values -> needs_verification, not invented.
"""
import json, os
BUILD = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BUILD, "data", "healthcare.json")
SRC = "FLEXcon Healthcare (DermaFlex / Omni-Wave / PharmCal / MedFlex) + CN BIO TECH brochures (2024)"

APPLICATIONS = [
 ("wearable-devices","Wearable Devices","可穿戴设备"),
 ("diagnostics-testing","Diagnostics & Testing","诊断与检测"),
 ("pharmaceutical","Pharmaceutical","医药与制药"),
 ("medical-devices","Medical Devices","医疗器械"),
 ("laboratory","Laboratory","实验室"),
]
REQUIREMENTS = [  # 工况 / Find by Requirement
 ("low-temperature-frozen-storage","Low-Temperature & Frozen Storage","低温与冷冻存储"),
 ("cryogenic-liquid-nitrogen-storage","Cryogenic & Liquid Nitrogen Storage","液氮与超低温存储"),
 ("chemical-resistant-identification","Chemical-Resistant Identification","耐化学腐蚀"),
 ("sterilization-resistant-identification","Sterilization-Resistant Identification","耐灭菌处理"),
 ("skin-contact-biocompatible-materials","Skin-Contact & Biocompatible Materials","贴肤与生物相容"),
 ("conductive-biosensing-materials","Conductive & Biosensing Materials","导电与生物传感"),
 ("abrasion-cleaning-resistant-labels","Abrasion & Cleaning Resistance","耐磨与耐清洁"),
 ("pharmaceutical-packaging-security","Pharmaceutical Packaging & Security","药品包装与安全"),
 ("removable-dissolvable-labels","Removable & Dissolvable Labels","可移除与水溶性"),
]

def P(pid, brand, name, slug, ptype, family, apps, reqs, direction, zh_direction,
      part=None, film_color=None, finish=None, min_c=None, max_c=None,
      status="verified_brochure", note_en=None, note_zh=None):
    return {
        "id":pid,"brand":brand,"product_name":name,"slug":slug,"product_type":ptype,
        "product_family":family,"part_number":part,"application_categories":apps,
        "requirement_paths":reqs,"film_color":film_color,"finish":finish,
        "min_service_temperature_c":min_c,"max_service_temperature_c":max_c,
        "brochure_direction_en":direction,"brochure_direction_zh":zh_direction,
        "compliance_note_en":note_en,"compliance_note_zh":note_zh,
        "verification_status":status,"source_document":SRC,
    }

BIO_NOTE_EN="Temperature and chemical directions are from the BIO TECH brochure; verify the current data sheet before production."
BIO_NOTE_ZH="温度与化学方向取自 BIO TECH 手册;量产前请核对最新数据表。"
DERMA_NOTE_EN="Biocompatibility information comes from the adhesive supplier's ISO 10993 (or similar) testing, some using a similar source adhesive. Suggested wear time is not a guarantee for every product or user."
DERMA_NOTE_ZH="生物相容性信息来自胶黏剂供应商依 ISO 10993 或类似方法的测试,部分使用相似源胶黏剂;建议佩戴时间不构成对所有产品与使用者的保证。"
MEDFLEX_NOTE_EN="UL, IEC and FDA-related statements apply only to the specific series and part numbers listed by the manufacturer — not to all medical materials."
MEDFLEX_NOTE_ZH="UL、IEC 与 FDA 相关表述仅适用于原厂列明的具体系列与料号,不扩大到全部医疗材料。"
OMNI_NOTE_EN="Omni-Wave is a conductive transfer adhesive material, described separately from ordinary printable label materials."
OMNI_NOTE_ZH="Omni-Wave 为导电胶转移材料,与普通可印刷标签材料分开说明。"

PRODUCTS = [
 # ---- FLEXcon DermaFlex (wearables / skin-contact) ----
 P("dermaflex-h-506","FLEXcon","FLEXcon DermaFlex H-506 (Gentle Release)","flexcon-dermaflex-h-506",
   "skin_contact_adhesive","DermaFlex",["wearable-devices"],["skin-contact-biocompatible-materials"],
   "Gentle-release adhesive for gentle removal and fragile-skin wear.",
   "温和移除胶黏剂,适合温和揭除与脆弱皮肤佩戴。",part="H-506",status="verified_brochure",
   note_en=DERMA_NOTE_EN,note_zh=DERMA_NOTE_ZH),
 P("dermaflex-h-520","FLEXcon","FLEXcon DermaFlex H-520 (General Use)","flexcon-dermaflex-h-520",
   "skin_contact_adhesive","DermaFlex",["wearable-devices","diagnostics-testing"],["skin-contact-biocompatible-materials"],
   "General-use skin adhesive, medium bond strength.","通用贴肤胶黏剂,中等粘接强度。",part="H-520",
   note_en=DERMA_NOTE_EN,note_zh=DERMA_NOTE_ZH),
 P("dermaflex-h-529","FLEXcon","FLEXcon DermaFlex H-529 (General Use)","flexcon-dermaflex-h-529",
   "skin_contact_adhesive","DermaFlex",["wearable-devices","diagnostics-testing"],["skin-contact-biocompatible-materials"],
   "General-use skin adhesive, medium bond strength.","通用贴肤胶黏剂,中等粘接强度。",part="H-529",
   note_en=DERMA_NOTE_EN,note_zh=DERMA_NOTE_ZH),
 P("dermaflex-h-566","FLEXcon","FLEXcon DermaFlex H-566 (Long-Term Wear)","flexcon-dermaflex-h-566",
   "skin_contact_adhesive","DermaFlex",["wearable-devices"],["skin-contact-biocompatible-materials"],
   "Long-term-wear adhesive for more durable device attachment.","长期佩戴胶黏剂,适合更耐久的设备固定。",part="H-566",
   note_en=DERMA_NOTE_EN,note_zh=DERMA_NOTE_ZH),
 P("dermaflex-h-778","FLEXcon","FLEXcon DermaFlex H-778 (Long-Term Wear)","flexcon-dermaflex-h-778",
   "skin_contact_adhesive","DermaFlex",["wearable-devices"],["skin-contact-biocompatible-materials"],
   "Long-term-wear adhesive for more durable device attachment.","长期佩戴胶黏剂,适合更耐久的设备固定。",part="H-778",
   note_en=DERMA_NOTE_EN,note_zh=DERMA_NOTE_ZH),

 # ---- FLEXcon Omni-Wave (conductive / biosensing) ----
 P("omni-wave","FLEXcon","FLEXcon Omni-Wave Conductive Transfer Adhesive","flexcon-omni-wave-conductive-transfer",
   "conductive_transfer","Omni-Wave",["diagnostics-testing"],["conductive-biosensing-materials"],
   "Conductive transfer adhesive for ECG, sEMG, EDA electrodes, biosensing and TENS stimulation. Specific constructions to be confirmed.",
   "导电胶转移材料,用于 ECG、sEMG、EDA 电极、生物传感与 TENS 刺激。具体结构待确认。",
   status="needs_verification",note_en=OMNI_NOTE_EN,note_zh=OMNI_NOTE_ZH),

 # ---- FLEXcon PharmCal (pharmaceutical / cold-chain / blood bags) ----
 P("pharmcal-pharma","FLEXcon","FLEXcon PharmCal Pharmaceutical Label Material","flexcon-pharmcal-pharmaceutical",
   "label_material","PharmCal",["pharmaceutical"],["pharmaceutical-packaging-security"],
   "Pharmaceutical container labelling — small/large-diameter vials, cover labels, tamper-evident and security identification. Specific constructions to be confirmed.",
   "药品容器标识 —— 大小直径药瓶、遮盖标签、防拆与安全识别。具体结构待确认。",
   status="needs_verification"),
 P("pharmcal-blood-bag","FLEXcon","FLEXcon PharmCal Blood-Bag & Cold-Chain Label Material","flexcon-pharmcal-blood-bag-cold-chain",
   "label_material","PharmCal",["pharmaceutical"],["low-temperature-frozen-storage"],
   "Blood-bag, plasma-bag and cold-chain pharmaceutical labelling. (Blood bags: Pharmaceutical application, Low-Temperature requirement — not Packaging & Security.)",
   "血袋、血浆袋及冷链药品标识。(血袋:归“医药与制药”应用、“低温与冷冻存储”工况,不入“药品包装与安全”。)",
   status="needs_verification"),

 # ---- FLEXcon MedFlex (medical devices) ----
 P("medflex-flx069870","FLEXcon","FLEXcon MedFlex Plus MMSMGS50K","flexcon-medflex-plus-flx069870",
   "label_material","MedFlex",["medical-devices"],["abrasion-cleaning-resistant-labels","chemical-resistant-identification"],
   "Silver matte printable film for durable medical-device identification.","银色哑面可印刷膜,用于耐久医疗器械标识。",
   part="FLX069870",film_color="Silver",finish="Matte",note_en=MEDFLEX_NOTE_EN,note_zh=MEDFLEX_NOTE_ZH),
 P("medflex-flx069873","FLEXcon","FLEXcon MedFlex Plus MMSMMS50K","flexcon-medflex-plus-flx069873",
   "label_material","MedFlex",["medical-devices"],["abrasion-cleaning-resistant-labels","chemical-resistant-identification"],
   "Silver matte printable film for durable medical-device identification.","银色哑面可印刷膜,用于耐久医疗器械标识。",
   part="FLX069873",film_color="Silver",finish="Matte",note_en=MEDFLEX_NOTE_EN,note_zh=MEDFLEX_NOTE_ZH),
 P("medflex-flx069868","FLEXcon","FLEXcon MedFlex Plus PMCGS50K","flexcon-medflex-plus-flx069868",
   "label_material","MedFlex",["medical-devices"],["abrasion-cleaning-resistant-labels","chemical-resistant-identification"],
   "Clear gloss printable film for medical-device identification.","透明光面可印刷膜,用于医疗器械标识。",
   part="FLX069868",film_color="Clear",finish="Gloss",note_en=MEDFLEX_NOTE_EN,note_zh=MEDFLEX_NOTE_ZH),
 P("medflex-flx069871","FLEXcon","FLEXcon MedFlex Plus PMCMMS50K","flexcon-medflex-plus-flx069871",
   "label_material","MedFlex",["medical-devices"],["abrasion-cleaning-resistant-labels","chemical-resistant-identification"],
   "Clear matte printable film for medical-device identification.","透明哑面可印刷膜,用于医疗器械标识。",
   part="FLX069871",film_color="Clear",finish="Matte",note_en=MEDFLEX_NOTE_EN,note_zh=MEDFLEX_NOTE_ZH),
 P("medflex-flx069869","FLEXcon","FLEXcon MedFlex Plus PMWGS50K","flexcon-medflex-plus-flx069869",
   "label_material","MedFlex",["medical-devices"],["abrasion-cleaning-resistant-labels","chemical-resistant-identification"],
   "White gloss printable film for medical-device identification.","白色光面可印刷膜,用于医疗器械标识。",
   part="FLX069869",film_color="White",finish="Gloss",note_en=MEDFLEX_NOTE_EN,note_zh=MEDFLEX_NOTE_ZH),
 P("medflex-flx069872","FLEXcon","FLEXcon MedFlex Plus PMWMS50K","flexcon-medflex-plus-flx069872",
   "label_material","MedFlex",["medical-devices"],["abrasion-cleaning-resistant-labels","chemical-resistant-identification"],
   "White matte printable film for medical-device identification.","白色哑面可印刷膜,用于医疗器械标识。",
   part="FLX069872",film_color="White",finish="Matte",note_en=MEDFLEX_NOTE_EN,note_zh=MEDFLEX_NOTE_ZH),
 P("medflex-flx056662","FLEXcon","FLEXcon MedFlex Overlam OMMCS100P","flexcon-medflex-overlam-flx056662",
   "overlaminate","MedFlex Overlam",["medical-devices"],["abrasion-cleaning-resistant-labels"],
   "Clear matte protective overlaminate for printed medical-device labels.","透明哑面保护膜,用于医疗器械印刷标签。",
   part="FLX056662",film_color="Clear",finish="Matte",note_en=MEDFLEX_NOTE_EN,note_zh=MEDFLEX_NOTE_ZH),
 P("medflex-flx056663","FLEXcon","FLEXcon MedFlex Overlam OMGCS100P","flexcon-medflex-overlam-flx056663",
   "overlaminate","MedFlex Overlam",["medical-devices"],["abrasion-cleaning-resistant-labels"],
   "Clear gloss protective overlaminate for printed medical-device labels.","透明光面保护膜,用于医疗器械印刷标签。",
   part="FLX056663",film_color="Clear",finish="Gloss",note_en=MEDFLEX_NOTE_EN,note_zh=MEDFLEX_NOTE_ZH),

 # ---- BIO TECH laboratory labels ----
 P("biotech-el855","BIO TECH","BIO TECH EL855 Deep-Freeze Label","biotech-el855",
   "label_material","BIO TECH",["laboratory"],["low-temperature-frozen-storage"],
   "Applies directly to vials or tubes already frozen to -80°C, for subsequent low-temperature storage.",
   "可直接粘贴于已冷冻至 -80°C 的小瓶或试管表面,用于后续低温存储。",part="EL855",min_c=-80,
   note_en=BIO_NOTE_EN,note_zh=BIO_NOTE_ZH),
 P("biotech-el865","BIO TECH","BIO TECH EL865 Cryogenic Label","biotech-el865",
   "label_material","BIO TECH",["laboratory"],["cryogenic-liquid-nitrogen-storage"],
   "Polypropylene liquid-nitrogen storage label for tubes and vials.","聚丙烯液氮存储标签,用于试管与小瓶。",
   part="EL865",min_c=-196,note_en=BIO_NOTE_EN,note_zh=BIO_NOTE_ZH),
 P("biotech-el973","BIO TECH","BIO TECH EL973 Wrap Self-Laminating Cryo Label","biotech-el973",
   "label_material","BIO TECH",["laboratory"],["cryogenic-liquid-nitrogen-storage"],
   "Wrap-around self-laminating polypropylene label for tubes and vials.","环绕自覆膜聚丙烯标签,用于试管与小瓶。",
   part="EL973",min_c=-196,note_en=BIO_NOTE_EN,note_zh=BIO_NOTE_ZH),
 P("biotech-el855m","BIO TECH","BIO TECH EL855M Metal-Rack Cryo Label","biotech-el855m",
   "label_material","BIO TECH",["laboratory"],["cryogenic-liquid-nitrogen-storage"],
   "Vinyl liquid-nitrogen storage label for metal racks.","金属架用乙烯类液氮存储标签。",
   part="EL855M",min_c=-196,note_en=BIO_NOTE_EN,note_zh=BIO_NOTE_ZH),
 P("biotech-el844","BIO TECH","BIO TECH EL844 Glass-Capillary Cryo Label","biotech-el844",
   "label_material","BIO TECH",["laboratory"],["cryogenic-liquid-nitrogen-storage"],
   "Liquid-nitrogen storage label for glass capillary tubes.","玻璃细管液氮存储标签。",
   part="EL844",min_c=-196,note_en=BIO_NOTE_EN,note_zh=BIO_NOTE_ZH),
 P("biotech-el583","BIO TECH","BIO TECH EL583 Histology Slide Label","biotech-el583",
   "label_material","BIO TECH",["laboratory"],["chemical-resistant-identification"],
   "Histology microscope-slide label for xylene, alcohol and stain exposure.","组织学载玻片标签,耐二甲苯、乙醇与染色剂。",
   part="EL583",note_en=BIO_NOTE_EN,note_zh=BIO_NOTE_ZH),
 P("biotech-el585","BIO TECH","BIO TECH EL585 Self-Laminating Slide Label","biotech-el585",
   "label_material","BIO TECH",["laboratory"],["chemical-resistant-identification"],
   "Slide label with clear self-laminate protecting the printed information.","带透明自覆膜的载玻片标签,保护打印信息。",
   part="EL585",note_en=BIO_NOTE_EN,note_zh=BIO_NOTE_ZH),
 P("biotech-el772","BIO TECH","BIO TECH EL772 Deep-Freeze Chemical-Resistant Label","biotech-el772",
   "label_material","BIO TECH",["laboratory"],["low-temperature-frozen-storage","sterilization-resistant-identification","cryogenic-liquid-nitrogen-storage"],
   "Deep-freeze chemical-resistant polypropylene label; brochure also lists autoclave/high-temperature and ultra-low-temperature use.",
   "深冷冻耐化学聚丙烯标签;手册同时列为耐高压高温与超低温标签。",part="EL772",min_c=-196,
   note_en=BIO_NOTE_EN,note_zh=BIO_NOTE_ZH),
 P("biotech-el773","BIO TECH","BIO TECH EL773 Microplate Label","biotech-el773",
   "label_material","BIO TECH",["laboratory"],["low-temperature-frozen-storage"],
   "Microplate polypropylene label for low-temperature storage.","微孔板聚丙烯标签,用于低温存储。",
   part="EL773",note_en=BIO_NOTE_EN,note_zh=BIO_NOTE_ZH),
 P("biotech-el833","BIO TECH","BIO TECH EL833 Deep-Freeze Cloth Label","biotech-el833",
   "label_material","BIO TECH",["laboratory"],["low-temperature-frozen-storage"],
   "Deep-freeze multi-purpose nylon-cloth label for larger-diameter tubes and vials.","深冷冻多用途尼龙布标签,用于较大直径试管与小瓶。",
   part="EL833",note_en=BIO_NOTE_EN,note_zh=BIO_NOTE_ZH),
 P("biotech-el-115","BIO TECH","BIO TECH EL-115 Water-Dissolvable Label","biotech-el-115",
   "label_material","BIO TECH",["laboratory"],["removable-dissolvable-labels"],
   "Dissolves in hot water in about 30 seconds — for temporary identification and washable, reusable containers.",
   "约 30 秒溶于热水 —— 用于临时识别与可清洗、可重复使用的容器。",part="EL-115",
   note_en=BIO_NOTE_EN,note_zh=BIO_NOTE_ZH),
]

data = {
 "series":"healthcare",
 "hub_route":"/industries/healthcare-life-sciences/",
 "brands":{
   "flexcon":{"name":"FLEXcon","families":["DermaFlex","Omni-Wave","PharmCal","MedFlex"]},
   "bio-tech":{"name":"BIO TECH","families":["BIO TECH"]},
 },
 "applications":[{"slug":s,"title_en":e,"title_zh":z} for s,e,z in APPLICATIONS],
 "requirements":[{"slug":s,"title_en":e,"title_zh":z} for s,e,z in REQUIREMENTS],
 "products":PRODUCTS,
}

# integrity
app_slugs={a["slug"] for a in data["applications"]}
req_slugs={r["slug"] for r in data["requirements"]}
errs=[];seen=set()
for p in PRODUCTS:
    if p["slug"] in seen: errs.append("dup "+p["slug"])
    seen.add(p["slug"])
    for a in p["application_categories"]:
        if a not in app_slugs: errs.append("%s bad app %s"%(p["id"],a))
    for r in p["requirement_paths"]:
        if r not in req_slugs: errs.append("%s bad req %s"%(p["id"],r))
if errs: raise SystemExit("DATA ERRORS:\n"+"\n".join(errs))

os.makedirs(os.path.dirname(OUT),exist_ok=True)
json.dump(data,open(OUT,"w"),ensure_ascii=False,indent=1)

from collections import Counter
print("products:",len(PRODUCTS),dict(Counter(p["brand"] for p in PRODUCTS)))
print("verification:",dict(Counter(p["verification_status"] for p in PRODUCTS)))
print("applications:",len(APPLICATIONS),"requirements:",len(REQUIREMENTS))
for a in app_slugs:
    if not any(a in p["application_categories"] for p in PRODUCTS): print("  app no product:",a)
for r in req_slugs:
    if not any(r in p["requirement_paths"] for p in PRODUCTS): print("  req no product:",r)
