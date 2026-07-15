#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build _build/data/pcb.json — Electronics & PCB / Polyimide (Polyonics-led).

From the two Polyonics landing-page briefs. ETIA supplies Polyonics; ETIA is not the
manufacturer. Source temperatures are qualitative in the brief (reflow / ultra-high-heat) —
NO numeric temperatures are invented. Each product carries a market cross-reference
(Polyonics / Brady / ETIA-own / 3M / Avery) = equivalence-by-construction, not certified 1:1.
"""
import json, os
BUILD=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(BUILD,"data","pcb.json")
SRC="Polyonics PCB / Polyimide landing-page briefs (ETIA)"

# process/application category pages
CATEGORIES=[
 ("reflow-polyimide-labels","Reflow & Wave-Solder Polyimide PCB Labels","回流焊与波峰焊聚酰亚胺PCB标签",
  "Labels applied before soldering and cleaning that must stay attached and readable after reflow, wave solder, flux, solvents and repeated harsh washes.",
  "焊接与清洗前粘贴、且必须在回流焊、波峰焊、助焊剂、溶剂及多轮严苛清洗后保持粘接与可读的标签。"),
 ("non-reflow-polyimide-labels","Non-Reflow Polyimide PCB Labels","非回流焊聚酰亚胺PCB标签",
  "Durable PCB identification for harsh cleaning and moderate heat where the label does not pass a full reflow profile — choose by the actual process, not the highest possible temperature.",
  "面向严苛清洗与中等热暴露、无需经历完整回流焊曲线的耐久PCB标识 —— 按实际工艺选材,而非一味追求最高耐温。"),
 ("post-process-labels","Post-Process Circuit Board Labels","成品PCB后制程标签",
  "Applied after manufacturing for serial numbers, barcodes, component tracking and finished-board identification — selected for the finished surface and service environment.",
  "制造完成后添加序列号、条码、元件追踪与成品线路板信息 —— 根据成品表面与使用环境选材。"),
 ("auto-dispense-labels","Auto-Dispense PCB Labels","PCB自动剥离标签",
  "A conversion / application-format page. The base material is chosen from the reflow, non-reflow or post-process pages, then converted for reliable automatic dispensing.",
  "转换/贴标形式页面。基材从回流、非回流或后制程页选定后,再转换为可稳定自动剥离的卷材。"),
 ("masking-dots-inspection-arrows","PCB Masking Dots & Inspection Arrows","PCB遮蔽圆点与检验标记",
  "Temporary masking dots and inspection markers — removable, low-residue constructions. 'Removable' is process-dependent; residue changes after heat/chemistry.",
  "临时遮蔽圆点与检验标记 —— 可移除、低残胶结构。'可移除'随工艺变化,残胶在热/化学后可能改变。"),
 ("laser-markable-labels","Laser-Markable Label Materials","激光可标记标签材料",
  "Permanent, high-contrast marking without thermal-transfer ribbon. The material and laser system must be qualified together; not the same as direct part marking.",
  "无需热转印碳带的永久高对比标识。材料与激光系统必须共同验证;不等同于直接零件打标。"),
]

def eq(brady=None,etia=None,threeM=None,avery=None):
    return {"brady":brady,"etia":etia,"3m":threeM,"avery":avery}

def P(pid,name,slug,apps,construction,heat_tier,esd,color,finish,direction,zh_direction,
      equivalents,status="verified_brochure",on_request=False):
    return {"id":pid,"brand":"Polyonics","product_name":name,"slug":slug,
        "application_categories":apps,"construction":construction,"heat_tier":heat_tier,
        "esd":esd,"film_color":color,"finish":finish,
        "brochure_direction_en":direction,"brochure_direction_zh":zh_direction,
        "market_equivalents":equivalents,"on_request":on_request,
        "verification_status":status,"source_document":SRC}

PRODUCTS=[
 P("polyonics-xf-533","Polyonics XF-533 Low-Profile Polyimide","polyonics-xf-533",
   ["reflow-polyimide-labels","non-reflow-polyimide-labels","auto-dispense-labels"],
   "1 mil matte white polyimide, permanent acrylic adhesive for high-surface-energy substrates","reflow / wave-solder",
   False,"White","Matte",
   "Low-profile matte white polyimide for compact assemblies through high-heat wave solder and repeated harsh PCB washes; no static-dissipative performance.",
   "低厚度哑白色聚酰亚胺,适合紧凑组件,可经受高温波峰焊与多轮严苛清洗;不具静电耗散性能。",
   eq(brady="B-729",etia="E-8532TT",threeM="7812",avery="ADS1622")),
 P("polyonics-xf-542","Polyonics XF-542 Ultra-Heat-Resistant Amber Polyimide","polyonics-xf-542",
   ["reflow-polyimide-labels"],
   "Amber polyimide for the most demanding high-heat processing","ultra-high-heat",
   False,"Amber","—",
   "Amber polyimide material for demanding ultra-high-temperature PCB processing.","琥珀色聚酰亚胺,面向最严苛的超高温PCB工艺。",
   eq(brady="B-724",etia="E-8531 (color)",avery="MZS1412"),on_request=True),
 P("polyonics-xf-101m","Polyonics XF-101M Ultra-Thin ESD Polyimide","polyonics-xf-101m",
   ["reflow-polyimide-labels","non-reflow-polyimide-labels"],
   "Ultra-thin static-dissipative polyimide","reflow / wave-solder",True,"Amber/translucent","—",
   "Ultra-thin static-dissipative polyimide for ESD-sensitive components and controlled production areas.",
   "超薄静电耗散聚酰亚胺,用于ESD敏感器件与管控生产区。",
   eq(brady="B-768",etia="E-8731",avery="AAH892")),
 P("polyonics-xf-101se","Polyonics XF-101SE Ultra-Thin Gloss ESD Polyimide","polyonics-xf-101se",
   ["reflow-polyimide-labels","non-reflow-polyimide-labels","auto-dispense-labels"],
   "Ultra-thin gloss static-dissipative polyimide","reflow / wave-solder",True,"Amber/translucent","Gloss",
   "Ultra-thin gloss static-dissipative polyimide for ESD control through reflow and harsh wash.",
   "超薄亮面静电耗散聚酰亚胺,用于回流焊与严苛清洗中的ESD控制。",
   eq(brady="B-718",etia="E-8731",avery="AAG996")),
 P("polyonics-xf-101me","Polyonics XF-101ME Ultra-Thin Matte ESD Polyimide","polyonics-xf-101me",
   ["reflow-polyimide-labels"],
   "Ultra-thin matte static-dissipative polyimide","reflow / wave-solder",True,"Amber/translucent","Matte",
   "Ultra-thin matte static-dissipative polyimide; matte face supports high-contrast barcode imaging.",
   "超薄哑面静电耗散聚酰亚胺;哑面有利于高对比条码成像。",
   eq(brady="B-719",etia="E-8732",avery="AAH477")),
 P("polyonics-xf-102se","Polyonics XF-102SE Gloss ESD Polyimide","polyonics-xf-102se",
   ["reflow-polyimide-labels"],
   "Standard-profile gloss static-dissipative polyimide","reflow / wave-solder",True,"Amber/translucent","Gloss",
   "Standard-profile gloss static-dissipative polyimide for ESD identification with a more substantial construction.",
   "标准厚度亮面静电耗散聚酰亚胺,提供较厚结构的ESD识别。",
   eq(brady="B-717",etia="E-8732",avery="AAG996"),on_request=True),
 P("polyonics-xf-102g","Polyonics XF-102G Harsh-Wash Polyimide","polyonics-xf-102g",
   ["reflow-polyimide-labels"],
   "Gloss polyimide engineered for harsh-wash print durability without a preheat step","reflow / wave-solder",False,"White","Gloss",
   "Gloss polyimide for harsh-wash print performance without relying on preheating.","亮面聚酰亚胺,不依赖预热即可提升印字耐清洗性。",
   eq(brady="B-777",etia="E-8512",avery="ADS1685"),on_request=True),
 P("polyonics-xf-505","Polyonics XF-505 Light-Green Polyimide","polyonics-xf-505",
   ["reflow-polyimide-labels"],
   "Light-green polyimide for high-temperature process differentiation","reflow / wave-solder",False,"Light green","—",
   "Light-green colour-coded high-temperature polyimide for process differentiation.","浅绿色耐高温聚酰亚胺,用于工艺区分。",
   eq(brady="B-776",etia="E-8531 (color)",avery="MZ2000G")),
 P("polyonics-xf-446","Polyonics XF-446 Chemical-Resistant ESD PET","polyonics-xf-446",
   ["non-reflow-polyimide-labels","post-process-labels"],
   "Static-dissipative polyester (PET) for chemical/solvent resistance at moderate heat","moderate heat",True,"White","—",
   "Static-dissipative PET for combined chemical/solvent resistance where full reflow heat is not required.",
   "静电耗散PET,用于无需完整回流焊高温、但需耐化学/溶剂的场景。",
   eq(brady="B-473",etia="E-2712",threeM="76962 (acetone)")),
]

# category-level market cross-reference tables (where the brief lists rows beyond a single product)
CATEGORY_MARKET={
 "masking-dots-inspection-arrows":[
   {"cat_en":"Removable high-temp PI","cat_zh":"可移除耐高温PI","polyonics":"on request","brady":"B-104","etia":"E-8632 / E-8631","3m":"FM1732R","avery":"—"},
   {"cat_en":"Removable film dot","cat_zh":"可移除薄膜圆点","polyonics":"on request","brady":"B-449","etia":"E-4633","3m":"FM1542","avery":"—"},
 ],
 "laser-markable-labels":[
   {"cat_en":"Laser PI (high-temp)","cat_zh":"激光PI耐高温","polyonics":"on request","brady":"B-8423","etia":"E-2512BL","3m":"7840HL / 7850HL","avery":"MZS1039"},
   {"cat_en":"Laser PET black","cat_zh":"激光黑PET","polyonics":"on request","brady":"B-421","etia":"E-2512BL","3m":"7840HL","avery":"MZ2903"},
 ],
 "post-process-labels":[
   {"cat_en":"Durable white PET asset","cat_zh":"耐久白PET资产标","polyonics":"on request","brady":"B-423","etia":"E-2512","3m":"7815 / 7818","avery":"durable PET"},
   {"cat_en":"Metallized silver PET","cat_zh":"金属化亚银PET","polyonics":"on request","brady":"B-428","etia":"E-2522","3m":"7818","avery":"MZ series"},
   {"cat_en":"Tamper-evident / security","cat_zh":"防拆/安全","polyonics":"on request","brady":"B-7546 / B-7576","etia":"on request","3m":"7380 / 7935","avery":"—"},
 ],
}

data={"series":"pcb","hub_route":"/industries/electronics-pcb/","material_route":"/materials/polyimide/",
 "brand":{"name":"Polyonics","note_en":"ETIA supplies Polyonics; ETIA is not the manufacturer.","note_zh":"ETIA 供应 Polyonics;ETIA 并非制造商。"},
 "categories":[{"slug":s,"title_en":e,"title_zh":z,"lede_en":le,"lede_zh":lz} for s,e,z,le,lz in CATEGORIES],
 "category_market":CATEGORY_MARKET,
 "products":PRODUCTS}

# integrity
cat_slugs={c["slug"] for c in data["categories"]}
errs=[];seen=set()
for p in PRODUCTS:
    if p["slug"] in seen: errs.append("dup "+p["slug"])
    seen.add(p["slug"])
    for a in p["application_categories"]:
        if a not in cat_slugs: errs.append("%s bad cat %s"%(p["id"],a))
if errs: raise SystemExit("DATA ERRORS:\n"+"\n".join(errs))
os.makedirs(os.path.dirname(OUT),exist_ok=True)
json.dump(data,open(OUT,"w"),ensure_ascii=False,indent=1)
from collections import Counter
print("products:",len(PRODUCTS),"| categories:",len(CATEGORIES))
print("esd products:",sum(1 for p in PRODUCTS if p["esd"]),"| on_request:",sum(1 for p in PRODUCTS if p["on_request"]))
for c in cat_slugs:
    n=sum(1 for p in PRODUCTS if c in p["application_categories"])
    extra=" (+market table)" if c in CATEGORY_MARKET else ""
    print("  cat %s: %d products%s"%(c,n,extra))
