#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build _build/data/automotive.json from the 3M + FLEXcon automotive brief.

Rules honored (brief §10, §7):
 - 3M and FLEXcon are SEPARATE brands; never merged.
 - ETIA supplies/supports selection; NOT the manufacturer.
 - Only brochure-verified facts are recorded. Missing TDS-level values are null with
   verification_status = "needs_verification". No parameters are invented.
 - Temperatures distinguish service range vs short-term peak (+ duration).
 - The 3M brochure lists NO temperatures -> all 3M temp fields stay null / needs_verification.
"""
import json, os

BUILD = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BUILD, "data", "automotive.json")

SOURCE_3M = "3M-IATD-Automotive-Portfolio-Labels-Brochure (2022-04)"
SOURCE_FX = "FLEXcon-Automotive-Brochure (product data stated 2025-01)"

# -------- application categories (Path A) --------
APPLICATIONS = [
 ("underhood-powertrain-labels","Underhood & Powertrain Labels","发动机舱与动力系统标签"),
 ("ev-battery-charging-labels","EV Battery & Charging Labels","EV电池与充电系统标签"),
 ("cable-wire-harness-labels","Cable & Wire Harness Labels","汽车线束与电缆标签"),
 ("vin-security-compliance-labels","VIN, Security & Compliance Labels","VIN、防拆与法规追溯标签"),
 ("door-jamb-information-labels","Door-Jamb & Vehicle Information Labels","门框与车辆信息标签"),
 ("warning-instruction-labels","Warning & Instructional Labels","警示与操作说明标签"),
 ("parts-marking-nameplate-labels","Parts Marking & Nameplates","零部件标识与铭牌标签"),
 ("paint-masking-overlaminate","Paint Masking & Overlaminate","汽车涂装遮蔽与覆膜"),
 ("removable-surface-protection","Removable Surface Protection","可移除汽车表面保护"),
]

# -------- performance paths (Path B) --------
PERFORMANCE = [
 ("high-temperature-automotive-labels","High-Temperature Automotive Labels","耐高温汽车标签"),
 ("chemical-fuel-oil-resistant-labels","Chemical, Fuel & Oil Resistance","耐化学、燃油与油污"),
 ("labels-for-difficult-automotive-surfaces","Difficult & Low-Surface-Energy Surfaces","难粘与低表面能表面"),
 ("automotive-tamper-evident-labels","Tamper-Evident & Destructible","防拆与易碎"),
 ("automotive-laser-markable-labels","Laser-Markable","激光可标记"),
 ("weather-resistant-automotive-labels","Weather, UV & Moisture Resistance","耐候、耐UV与耐潮湿"),
 ("removable-automotive-labels","Removable & Residue-Controlled","可移除与残胶控制"),
 ("flexible-conformable-automotive-labels","Flexible & Conformable Materials","柔性与曲面贴合"),
 ("automotive-masking-overlaminate","Masking & Overlamination","遮蔽与覆膜"),
]

# -------- products --------
# helper to build a product dict with sane defaults
def P(pid, brand, name, slug, ptype, family, apps, perf, direction,
      construction_id=None, regional=None, film_color=None, finish=None,
      min_c=None, max_c=None, peak_c=None, peak_dur=None,
      tamper=None, removability=None, status="needs_verification", zh_direction=None):
    return {
        "id": pid, "brand": brand, "product_name": name, "slug": slug,
        "product_type": ptype, "product_family": family,
        "construction_id": construction_id, "regional_equivalent_ids": regional or [],
        "application_categories": apps, "performance_paths": perf,
        "film_color": film_color, "finish": finish,
        "min_service_temperature_c": min_c, "max_service_temperature_c": max_c,
        "short_term_peak_temperature_c": peak_c, "short_term_peak_duration": peak_dur,
        "application_temperature_c": None,
        "tamper_evidence_type": tamper, "removability": removability,
        "brochure_direction_en": direction,
        "brochure_direction_zh": zh_direction or "",
        "verification_status": status,
        "source_document": SOURCE_3M if brand == "3M" else SOURCE_FX,
    }

PRODUCTS = [
 # ---- 3M (brochure lists NO temperatures -> temps null, needs_verification) ----
 P("3m-3921","3M","3M High Temperature Resistant Label Material 3921","3m-3921-high-temperature-label-material",
   "label_material","3M High Temperature Resistant",
   ["cable-wire-harness-labels"],["high-temperature-automotive-labels"],
   "Identification of different automotive wire harnesses; high-temperature resistant construction.",
   zh_direction="用于不同汽车线束的标识,耐高温结构。"),
 P("3m-7871","3M","3M Polyester Label Material 7871 / 7871V","3m-7871-polyester-label-material",
   "label_material","3M Polyester 78xx",
   ["warning-instruction-labels","underhood-powertrain-labels","ev-battery-charging-labels"],
   ["high-temperature-automotive-labels"],
   "Radiator warning labels and long-lasting operating instructions; charger operating instructions.",
   regional=["7871V"], zh_direction="散热器警示标签与耐久操作说明;充电器操作说明。"),
 P("3m-7868","3M","3M Polyester Label Material 7868 / 7868V","3m-7868-polyester-label-material",
   "label_material","3M Polyester 78xx",
   ["ev-battery-charging-labels","door-jamb-information-labels","warning-instruction-labels","underhood-powertrain-labels"],
   [],
   "Battery, jump-start and tire-pressure information; branding, instructions and warning labels.",
   regional=["7868V"], zh_direction="电池、跨接启动与胎压信息;品牌、说明与警示标签。"),
 P("3m-7879","3M","3M Polyester Label Material 7879","3m-7879-polyester-label-material",
   "label_material","3M Polyester 78xx",
   ["underhood-powertrain-labels","parts-marking-nameplate-labels"],
   ["chemical-fuel-oil-resistant-labels"],
   "Adhesion to slightly oily surfaces, including power-steering pump examples.",
   zh_direction="可粘附于轻微油污表面,包括动力转向泵等示例。"),
 P("3m-ofm03402","3M","3M Polyester Label Material OFM03402","3m-ofm03402-automotive-label-material",
   "label_material","3M Polyester",
   ["parts-marking-nameplate-labels"],["labels-for-difficult-automotive-surfaces"],
   "Structured and hard-to-bond plastic surfaces.",
   zh_direction="用于结构化及难粘塑料表面。"),
 P("3m-7847","3M","3M Laser Markable Label Material 7847","3m-7847-laser-markable-label-material",
   "label_material","3M Laser Markable",
   ["vin-security-compliance-labels","door-jamb-information-labels","warning-instruction-labels"],
   ["automotive-laser-markable-labels","chemical-fuel-oil-resistant-labels","automotive-tamper-evident-labels"],
   "VIN labels inside door jambs; laser-marked service and loading instructions; resistance to chemical and mechanical influences.",
   zh_direction="门框内VIN标签;激光打标的维修与装载说明;耐化学与机械影响。"),
 P("3m-7247","3M","3M Polyester Label Material 7247","3m-7247-polyester-label-material",
   "label_material","3M Polyester 78xx",
   ["ev-battery-charging-labels","warning-instruction-labels","parts-marking-nameplate-labels"],
   ["flexible-conformable-automotive-labels","labels-for-difficult-automotive-surfaces"],
   "Operating instructions on differently shaped surfaces, including fuel/charging-area type applications.",
   zh_direction="用于不同形状表面的操作说明,包括加油/充电区域类应用。"),
 P("3m-76716na","3M","3M Polyolefin Label Material 76716NA","3m-76716na-polyolefin-label-material",
   "label_material","3M Polyolefin",
   ["ev-battery-charging-labels"],["flexible-conformable-automotive-labels"],
   "Product labeling on flexible materials.",
   zh_direction="用于柔性材料上的产品标识。"),
 P("3m-92904","3M","3M Durable Resin Ribbon 92904","3m-92904-durable-resin-ribbon",
   "ribbon","3M Ribbon",
   [],["chemical-fuel-oil-resistant-labels"],
   "Printing consumable — NOT a label face material. High solvent and chemical resistance when printed on compatible 3M PP and PET label materials.",
   zh_direction="打印耗材,非面材。在兼容的3M PP与PET面材上打印时具备高耐溶剂与耐化学性。"),

 # ---- FLEXcon (temps per brochure list where stated) ----
 P("flexcon-thermlfilm-advantage-extreme-white","FLEXcon","FLEXcon ThermlFilm Advantage Extreme White","flexcon-thermlfilm-advantage-extreme-white",
   "label_material","ThermlFilm Advantage",
   ["underhood-powertrain-labels"],["high-temperature-automotive-labels"],
   "Underhood durable white identification (Advantage family).",
   film_color="White", min_c=-40, max_c=150, status="verified_brochure",
   zh_direction="发动机舱耐久白色标识(Advantage 系列)。"),
 P("flexcon-thermlfilm-advantage-value-satin-white","FLEXcon","FLEXcon ThermlFilm Advantage Value Satin White","flexcon-thermlfilm-advantage-value-satin-white",
   "label_material","ThermlFilm Advantage",
   ["parts-marking-nameplate-labels"],[],
   "General parts marking; satin white durable identification.",
   film_color="White", finish="Satin", min_c=-40, max_c=150, status="verified_brochure",
   zh_direction="通用零部件标识;缎面白色耐久标识。"),
 P("flexcon-thermlfilm-nexgen-underhood","FLEXcon","FLEXcon ThermlFilm NexGen (20120 / 21120 / 24120 equivalents)","flexcon-thermlfilm-nexgen-underhood",
   "label_material","ThermlFilm NexGen",
   ["underhood-powertrain-labels"],[],
   "High-performance permanent underhood label constructions. Specific temperature not stated for these equivalents — verify TDS.",
   zh_direction="高性能永久性发动机舱标签结构。该等效型号未标注具体温度,需核对TDS。"),
 P("flexcon-compucal-excel-21440","FLEXcon","FLEXcon CompuCal Excel 21440","flexcon-compucal-excel-21440",
   "label_material","CompuCal Excel",
   ["underhood-powertrain-labels"],[],
   "White matte underhood identification. Temperature not stated in brochure list — verify TDS.",
   film_color="White", finish="Matte",
   zh_direction="白色哑光发动机舱标识。手册未列温度,需核对TDS。"),
 P("flexcon-chemgard-ii-pet-dsj9-6c09hr","FLEXcon","FLEXcon ChemGard II PET DSJ9-6C09HR","flexcon-chemgard-ii-pet-dsj9-6c09hr",
   "label_material","ChemGard II",
   ["ev-battery-charging-labels","parts-marking-nameplate-labels"],["chemical-fuel-oil-resistant-labels"],
   "Chemical-resistant permanent battery/component identification (ChemGard II family, adhesive L-606/L-778 class). Verify exact chemical-resistance data per TDS.",
   construction_id="DSJ9-6C09HR",
   zh_direction="耐化学永久性电池/部件标识(ChemGard II 系列)。请按TDS核对具体耐化学数据。"),
 P("flexcon-chemgard-ii-pet-dwj9-6c09hr","FLEXcon","FLEXcon ChemGard II PET DWJ9-6C09HR","flexcon-chemgard-ii-pet-dwj9-6c09hr",
   "label_material","ChemGard II",
   ["ev-battery-charging-labels","parts-marking-nameplate-labels"],["chemical-fuel-oil-resistant-labels"],
   "Chemical-resistant permanent identification (ChemGard II family). Verify exact chemical-resistance data per TDS.",
   construction_id="DWJ9-6C09HR",
   zh_direction="耐化学永久性标识(ChemGard II 系列)。请按TDS核对具体耐化学数据。"),
 P("flexcon-tampermark-mm-150-silver-void","FLEXcon","FLEXcon TamperMark MM 150 Silver Void","flexcon-tampermark-mm-150-silver-void",
   "label_material","TamperMark",
   ["vin-security-compliance-labels"],["automotive-tamper-evident-labels"],
   "Silver VOID security label leaving evidence of attempted removal.",
   film_color="Silver", min_c=-40, max_c=150, tamper="VOID transfer", status="verified_brochure",
   zh_direction="银色VOID防拆标签,揭起后留下拆除痕迹。"),
 P("flexcon-tampermark-pm-200-white-void-ii","FLEXcon","FLEXcon ThermlFilm TamperMark PM 200 White Void II","flexcon-tampermark-pm-200-white-void-ii",
   "label_material","TamperMark",
   ["vin-security-compliance-labels"],["automotive-tamper-evident-labels"],
   "White VOID security label leaving evidence of attempted removal.",
   film_color="White", min_c=-40, max_c=150, tamper="VOID transfer", status="verified_brochure",
   zh_direction="白色VOID防拆标签,揭起后留下拆除痕迹。"),
 P("flexcon-thermlfilm-pe-200-white-destruct","FLEXcon","FLEXcon ThermlFilm PE 200 White Destruct","flexcon-thermlfilm-pe-200-white-destruct",
   "label_material","TamperMark / Destructible",
   ["vin-security-compliance-labels"],["automotive-tamper-evident-labels"],
   "Destructible white face that fragments on removal. Temperature not stated — verify TDS.",
   film_color="White", tamper="Destructible face",
   zh_direction="易碎白色面材,揭起时破碎。手册未列温度,需核对TDS。"),
 P("flexcon-thermlfilm-pm-100-clear-tc-387-l-29","FLEXcon","FLEXcon ThermlFilm PM 100 Clear TC-387 L-29","flexcon-thermlfilm-pm-100-clear-tc-387-l-29",
   "label_material","ThermlFilm PM 100",
   ["cable-wire-harness-labels"],[],
   "Clear PET cable/wire-harness construction.",
   construction_id="TC-387 L-29", film_color="Clear", min_c=-40, max_c=150, status="verified_brochure",
   zh_direction="透明PET线束/电缆结构。"),
 P("flexcon-thermlfilm-pm-100-clear-tc-716-l-344","FLEXcon","FLEXcon ThermlFilm PM 100 Clear TC-716 L-344","flexcon-thermlfilm-pm-100-clear-tc-716-l-344",
   "label_material","ThermlFilm PM 100",
   ["cable-wire-harness-labels"],[],
   "Clear PET cable/wire-harness construction.",
   construction_id="TC-716 L-344", film_color="Clear", min_c=-40, max_c=150, status="verified_brochure",
   zh_direction="透明PET线束/电缆结构。"),
 P("flexcon-thermlfilm-pm-100-white-tc-716-v-344hs","FLEXcon","FLEXcon ThermlFilm PM 100 White TC-716 V-344HS","flexcon-thermlfilm-pm-100-white-tc-716-v-344hs",
   "label_material","ThermlFilm PM 100",
   ["cable-wire-harness-labels"],[],
   "White PET cable/wire-harness construction.",
   construction_id="TC-716 V-344HS", film_color="White", min_c=-40, max_c=150, status="verified_brochure",
   zh_direction="白色PET线束/电缆结构。"),
 P("flexcon-thermlfilm-colormark-pm-200-sun-yellow","FLEXcon","FLEXcon ThermlFilm ColorMark PM 200 Sun Yellow","flexcon-thermlfilm-colormark-pm-200-sun-yellow",
   "label_material","ThermlFilm ColorMark",
   ["warning-instruction-labels"],[],
   "Yellow warning/instruction PET.",
   film_color="Yellow", min_c=-40, max_c=150, status="verified_brochure",
   zh_direction="黄色警示/说明PET。"),
 P("flexcon-thermlfilm-v-200-cast-conformable","FLEXcon","FLEXcon ThermlFilm V 200 Cast (Silver / White / Yellow)","flexcon-thermlfilm-v-200-cast-conformable",
   "label_material","ThermlFilm V 200 Cast",
   ["warning-instruction-labels","door-jamb-information-labels"],["flexible-conformable-automotive-labels"],
   "Conformable cast warning/instruction films for shaped surfaces.",
   min_c=-40, max_c=90, status="verified_brochure",
   zh_direction="可贴合的浇铸警示/说明薄膜,适用于曲面。"),
 P("flexcon-thermlfilm-mm-500-bbstainless","FLEXcon","FLEXcon ThermlFilm MM 500 BBStainless","flexcon-thermlfilm-mm-500-bbstainless",
   "label_material","ThermlFilm MM 500",
   ["parts-marking-nameplate-labels"],[],
   "Brushed-silver nameplate / decorative construction.",
   film_color="Brushed silver", finish="Brushed", min_c=-40, max_c=150, status="verified_brochure",
   zh_direction="拉丝银色铭牌/装饰结构。"),
 P("flexcon-dpm-uvcg-clear-uv-polyester","FLEXcon","FLEXcon DPM UVCG 1 Mil Clear UV Polyester","flexcon-dpm-uvcg-clear-uv-polyester",
   "overlaminate","DPM Overlaminate",
   ["paint-masking-overlaminate"],["automotive-masking-overlaminate","weather-resistant-automotive-labels"],
   "Clear UV polyester overlaminate protecting printed information. Outdoor duration to be confirmed by TDS.",
   film_color="Clear", min_c=-40, max_c=150, status="verified_brochure",
   zh_direction="透明UV聚酯覆膜,保护印刷信息。"),
 P("flexcon-dpm-cg-clear-polyester-overlaminate","FLEXcon","FLEXcon DPM CG Clear Polyester Overlaminating","flexcon-dpm-cg-clear-polyester-overlaminate",
   "overlaminate","DPM Overlaminate",
   ["paint-masking-overlaminate"],["automotive-masking-overlaminate"],
   "High-performance clear polyester overlaminate.",
   film_color="Clear", min_c=-40, max_c=150, status="verified_brochure",
   zh_direction="高性能透明聚酯覆膜。"),
 P("flexcon-flexmark-om-200-clear-v866lp","FLEXcon","FLEXcon FlexMark OM 200 Clear HS V-866LP","flexcon-flexmark-om-200-clear-v866lp",
   "masking_material","FlexMark OM 200",
   ["paint-masking-overlaminate"],["automotive-masking-overlaminate","high-temperature-automotive-labels"],
   "Clear high-temperature paint-masking construction.",
   construction_id="V-866LP", film_color="Clear", min_c=-40, max_c=180, peak_c=220,
   peak_dur="short term, 30 minutes", status="verified_brochure",
   zh_direction="透明耐高温涂装遮蔽结构。"),
 P("flexcon-flexmark-om-200-clear-v866ulp","FLEXcon","FLEXcon FlexMark OM 200 Clear HS V-866ULP","flexcon-flexmark-om-200-clear-v866ulp",
   "masking_material","FlexMark OM 200",
   ["paint-masking-overlaminate"],["automotive-masking-overlaminate","high-temperature-automotive-labels"],
   "Clear high-temperature paint-masking construction.",
   construction_id="V-866ULP", film_color="Clear", min_c=-40, max_c=180, peak_c=220,
   peak_dur="short term, 30 minutes", status="verified_brochure",
   zh_direction="透明耐高温涂装遮蔽结构。"),
 P("flexcon-thermlfilm-pm-200-white-hs-tc-390-v-305","FLEXcon","FLEXcon ThermlFilm PM 200 White HS TC-390 V-305","flexcon-thermlfilm-pm-200-white-hs-tc-390-v-305",
   "masking_material","ThermlFilm PM 200",
   ["paint-masking-overlaminate"],["automotive-masking-overlaminate","high-temperature-automotive-labels"],
   "White high-temperature masking construction.",
   construction_id="TC-390 V-305", film_color="White", peak_c=220,
   peak_dur="short term, 30 minutes", status="verified_brochure",
   zh_direction="白色耐高温遮蔽结构。"),
 P("flexcon-flex-vu-om-200-clear-a-324","FLEXcon","FLEXcon Flex-Vu OM 200 Clear A-324","flexcon-flex-vu-om-200-clear-a-324",
   "protection_film","Flex-Vu OM 200",
   ["removable-surface-protection"],["removable-automotive-labels"],
   "Clear removable surface-protection film.",
   construction_id="A-324", film_color="Clear", min_c=-40, max_c=150,
   removability="Removable", status="verified_brochure",
   zh_direction="透明可移除表面保护膜。"),
 P("flexcon-flexmark-pe-380-f-clear-matte-v-133","FLEXcon","FLEXcon FlexMark PE 380 F Clear Matte V-133","flexcon-flexmark-pe-380-f-clear-matte-v-133",
   "protection_film","FlexMark PE 380",
   ["removable-surface-protection"],["removable-automotive-labels"],
   "Clear matte removable surface-protection film.",
   construction_id="V-133", film_color="Clear", finish="Matte", min_c=-29, max_c=80,
   removability="Removable", status="verified_brochure",
   zh_direction="透明哑光可移除表面保护膜。"),
]

data = {
 "series": "automotive",
 "brands": {
   "3m": {"name":"3M","h1_en":"3M Automotive Label Materials for Durable Vehicle Identification",
          "h1_zh":"3M汽车耐久标识标签材料","source":SOURCE_3M},
   "flexcon": {"name":"FLEXcon","h1_en":"FLEXcon Automotive Label Materials for Identification, Protection and Security",
          "h1_zh":"FLEXcon汽车标识、保护与安全标签材料","source":SOURCE_FX},
 },
 "applications": [{"slug":s,"title_en":e,"title_zh":z} for s,e,z in APPLICATIONS],
 "performance":  [{"slug":s,"title_en":e,"title_zh":z} for s,e,z in PERFORMANCE],
 "products": PRODUCTS,
}

# ---- integrity checks ----
app_slugs={a["slug"] for a in data["applications"]}
perf_slugs={p["slug"] for p in data["performance"]}
errs=[]
seen=set()
for p in PRODUCTS:
    if p["slug"] in seen: errs.append("dup slug "+p["slug"])
    seen.add(p["slug"])
    for a in p["application_categories"]:
        if a not in app_slugs: errs.append("%s bad app %s"%(p["id"],a))
    for pf in p["performance_paths"]:
        if pf not in perf_slugs: errs.append("%s bad perf %s"%(p["id"],pf))
if errs:
    raise SystemExit("DATA ERRORS:\n"+"\n".join(errs))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(data, open(OUT,"w"), ensure_ascii=False, indent=1)

# ---- report ----
from collections import Counter
bybrand=Counter(p["brand"] for p in PRODUCTS)
byver=Counter(p["verification_status"] for p in PRODUCTS)
print("products:",len(PRODUCTS),dict(bybrand))
print("verification:",dict(byver))
print("applications:",len(APPLICATIONS),"performance:",len(PERFORMANCE))
# coverage: apps/perf with no product
for a in app_slugs:
    if not any(a in p["application_categories"] for p in PRODUCTS): print("  app no product:",a)
for pf in perf_slugs:
    if not any(pf in p["performance_paths"] for p in PRODUCTS): print("  perf no product:",pf)
