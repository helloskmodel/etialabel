#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build _build/data/pi_center.json — Polyimide (PI) Material & Application Center.

Phase 1 per CODEX BUILD SPEC: three pathways (Process 8 / Performance 9 / Industry 7),
8 Featured Solution families, POLYONICS + ETIA featured, Avery/Brady/LINTEC related.
Hidden in PI center: 3M, FLEXcon, Computype, YS-Tech, MiLabels.
No temperatures or certifications invented — unlisted specs stay pending verification.
"""
import json, os
BUILD=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(BUILD,"data","pi_center.json")

PROCESS=[
 ("high-temperature-pcb-labels","High-Temperature PCB Identification & Tracking","PCB耐高温识别与追踪"),
 ("smt-process-tracking-labels","SMT Process Tracking","SMT制程追踪"),
 ("reflow-soldering-labels","Reflow Soldering","回流焊"),
 ("wave-soldering-labels","Wave Soldering","波峰焊与过锡炉"),
 ("pcb-wash-process-labels","PCB Wash Process","PCB清洗"),
 ("high-temperature-barcode-labels","High-Temperature Barcode Tracking","高温条码追踪"),
 ("high-temperature-masking-tapes","High-Temperature Masking","高温遮蔽"),
 ("heat-treatment-process-labels","Industrial Heat Treatment","工业热处理"),
]
PERFORMANCE=[
 ("300c-high-temperature-labels","300°C Process Exposure","300℃高温制程"),
 ("esd-safe-polyimide-labels","ESD-Safe & Static-Dissipative","ESD防静电"),
 ("chemical-resistant-polyimide-labels","Chemical & Flux Resistant","耐化学品与助焊剂"),
 ("abrasion-resistant-polyimide-labels","Abrasion-Resistant Topcoat","耐磨打印表面"),
 ("flame-retardant-polyimide-labels","Flame-Retardant","阻燃"),
 ("halogen-free-polyimide-labels","Halogen-Free","无卤"),
 ("low-outgassing-polyimide-labels","Low-Outgassing","低释气"),
 ("removable-high-temperature-labels","Removable & Residue-Free","可移除与无残胶"),
 ("polyimide-overlaminates","High-Temperature Print Protection","高温打印保护"),
]
INDUSTRY=[
 ("electronics-pcb","Electronics & PCB Manufacturing","电子与PCB制造"),
 ("semiconductor-advanced-packaging","Semiconductor & Advanced Packaging","半导体与先进封装"),
 ("automotive-new-energy","Automotive & New Energy Vehicles","汽车与新能源车"),
 ("wire-cable-fiber-optics","Wire, Cable & Fiber Optics","电线、电缆与光纤"),
 ("aerospace-transportation","Aerospace & Transportation","航空航天与交通运输"),
 ("medical-laboratory","Medical Devices & Laboratories","医疗设备与实验室"),
 ("industrial-heat-treatment","Industrial Manufacturing & Heat Treatment","工业制造与热处理"),
]

# member model = {brand, model, slug(optional existing product page)}
def M(brand,model,slug=None): return {"brand":brand,"model":model,"slug":slug}

FAMILIES=[
 {"id":"PI-F01","en":"PCB High-Temperature Tracking Labels","zh":"PCB高温追踪标签","brands":["POLYONICS","ETIA"],
  "process":["high-temperature-pcb-labels","reflow-soldering-labels","wave-soldering-labels","pcb-wash-process-labels","high-temperature-barcode-labels","smt-process-tracking-labels"],
  "performance":["300c-high-temperature-labels"],"industry":["electronics-pcb","semiconductor-advanced-packaging","industrial-heat-treatment"],
  "members":[M("POLYONICS","XF-533","polyonics-xf-533"),M("POLYONICS","XF-542","polyonics-xf-542"),M("POLYONICS","XF-505","polyonics-xf-505"),
             M("ETIA","E-8532TT"),M("ETIA","E-8531")],
  "note_en":"Low-profile and colour-coded polyimide for reflow, wave solder and repeated harsh washes.",
  "note_zh":"低厚度与颜色区分聚酰亚胺,适用于回流焊、波峰焊与多轮严苛清洗。"},
 {"id":"PI-F02","en":"ESD-Safe Polyimide Labels","zh":"ESD安全PI标签","brands":["POLYONICS","ETIA"],
  "process":["reflow-soldering-labels","wave-soldering-labels","smt-process-tracking-labels","pcb-wash-process-labels"],
  "performance":["esd-safe-polyimide-labels"],"industry":["electronics-pcb","semiconductor-advanced-packaging"],
  "members":[M("POLYONICS","XF-781"),M("POLYONICS","XF-782"),M("POLYONICS","XF-784"),
             M("POLYONICS","XF-101SE","polyonics-xf-101se"),M("POLYONICS","XF-101ME","polyonics-xf-101me"),
             M("POLYONICS","XF-101M","polyonics-xf-101m"),M("POLYONICS","XF-102SE","polyonics-xf-102se"),
             M("ETIA","E-8731"),M("ETIA","E-8732")],
  "note_en":"Static-dissipative polyimide for ESD-controlled electronics and semiconductor production.",
  "note_zh":"静电耗散聚酰亚胺,用于 ESD 管控的电子与半导体生产。"},
 {"id":"PI-F03","en":"Chemical-Resistant Polyimide Labels","zh":"耐化学PI标签","brands":["POLYONICS","ETIA"],
  "process":["pcb-wash-process-labels","reflow-soldering-labels"],
  "performance":["chemical-resistant-polyimide-labels"],"industry":["electronics-pcb"],
  "members":[M("POLYONICS","XF-102G","polyonics-xf-102g"),M("POLYONICS","XF-446","polyonics-xf-446"),
             M("ETIA","E-8512"),M("ETIA","E-2712")],
  "note_en":"Polyimide and PET for flux, solvents and aggressive cleaning chemistry.",
  "note_zh":"聚酰亚胺与 PET,耐助焊剂、溶剂与强力清洗化学品。"},
 {"id":"PI-F04","en":"Abrasion-Resistant Polyimide Labels","zh":"耐磨PI标签","brands":["POLYONICS","ETIA"],
  "process":["high-temperature-barcode-labels"],"performance":["abrasion-resistant-polyimide-labels"],
  "industry":["electronics-pcb","automotive-new-energy"],
  "members":[M("POLYONICS","XF-731"),M("POLYONICS","XF-732")],
  "note_en":"Abrasion-resistant topcoat for barcode and small-text durability. Specs pending verification.",
  "note_zh":"耐磨打印涂层,提升条码与小字耐久性。参数待核验。"},
 {"id":"PI-F05","en":"Flame-Retardant Polyimide Labels","zh":"阻燃PI标签","brands":["POLYONICS","ETIA"],
  "process":["high-temperature-pcb-labels"],"performance":["flame-retardant-polyimide-labels"],
  "industry":["electronics-pcb","automotive-new-energy","aerospace-transportation"],
  "members":[M("POLYONICS","XF-603"),M("POLYONICS","XF-603FR")],
  "note_en":"Flame-retardant polyimide. UL / flammability status bound to the specific model — pending verification.",
  "note_zh":"阻燃聚酰亚胺。UL/阻燃状态须绑定具体型号 —— 待核验。"},
 {"id":"PI-F06","en":"High-Temperature Polyimide Overlaminates","zh":"高温PI覆膜","brands":["POLYONICS","ETIA"],
  "process":["high-temperature-barcode-labels"],"performance":["polyimide-overlaminates"],"industry":["electronics-pcb"],
  "members":[M("POLYONICS","XL-1501"),M("POLYONICS","XL-1502"),M("POLYONICS","XL-1561")],
  "note_en":"Clear high-temperature overlaminates protecting printed identification. Specs pending verification.",
  "note_zh":"透明高温覆膜,保护印刷标识。参数待核验。"},
 {"id":"PI-F07","en":"Polyimide Engineering Tapes","zh":"PI工程胶带","brands":["POLYONICS","ETIA"],
  "process":["high-temperature-masking-tapes"],"performance":["300c-high-temperature-labels"],
  "industry":["electronics-pcb","semiconductor-advanced-packaging"],
  "members":[M("POLYONICS","XT series")],
  "note_en":"Polyimide engineering tapes for high-temperature masking. Specific grades on request.",
  "note_zh":"聚酰亚胺工程胶带,用于高温遮蔽。具体规格按需提供。"},
 {"id":"PI-F08","en":"Industrial Heat-Treatment Labels","zh":"工业热处理标签","brands":["ETIA"],
  "process":["heat-treatment-process-labels"],"performance":["300c-high-temperature-labels"],
  "industry":["industrial-heat-treatment"],
  "members":[M("ETIA","HEATPROOF series")],
  "note_en":"ETIA ultra-high-temperature labels and tags for heat-treatment tracking (see HEATPROOF program).",
  "note_zh":"ETIA 超高温标签与吊牌,用于热处理追溯(见 HEATPROOF 系列)。"},
]

# related products (only Avery Dennison, Brady, LINTEC per spec) — equivalence-by-construction
RELATED=[
 {"cat_en":"Standard matte white PI","cat_zh":"标准哑白PI","avery":"ADS1622","brady":"B-729","lintec":"on request"},
 {"cat_en":"Ultra-thin ESD PI","cat_zh":"超薄ESD PI","avery":"AAG996 / AAH477","brady":"B-718 / B-719","lintec":"on request"},
 {"cat_en":"Amber ultra-heat PI","cat_zh":"琥珀超耐高温PI","avery":"MZS1412","brady":"B-724","lintec":"on request"},
 {"cat_en":"Chemical-resistant","cat_zh":"耐化学","avery":"ADS1685","brady":"B-777 / B-797","lintec":"on request"},
 {"cat_en":"High-temp overlaminate","cat_zh":"高温覆膜","avery":"—","brady":"—","lintec":"on request"},
]

HIDDEN_BRANDS=["3M","FLEXcon","Computype","YS-Tech","MiLabels"]

data={"route":"/materials/polyimide-pi-label-materials/",
 "process":[{"slug":s,"en":e,"zh":z} for s,e,z in PROCESS],
 "performance":[{"slug":s,"en":e,"zh":z} for s,e,z in PERFORMANCE],
 "industry":[{"slug":s,"en":e,"zh":z} for s,e,z in INDUSTRY],
 "families":FAMILIES,"related":RELATED,"hidden_brands":HIDDEN_BRANDS,
 "featured_brands":["POLYONICS","ETIA"]}

# integrity: family taxonomy refs valid
ps={s for s,_,_ in PROCESS}; rs={s for s,_,_ in PERFORMANCE}; isx={s for s,_,_ in INDUSTRY}
errs=[]
for f in FAMILIES:
    for x in f["process"]:
        if x not in ps: errs.append("%s bad process %s"%(f["id"],x))
    for x in f["performance"]:
        if x not in rs: errs.append("%s bad perf %s"%(f["id"],x))
    for x in f["industry"]:
        if x not in isx: errs.append("%s bad industry %s"%(f["id"],x))
if errs: raise SystemExit("DATA ERRORS:\n"+"\n".join(errs))
os.makedirs(os.path.dirname(OUT),exist_ok=True)
json.dump(data,open(OUT,"w"),ensure_ascii=False,indent=1)
print("process:",len(PROCESS),"performance:",len(PERFORMANCE),"industry:",len(INDUSTRY))
print("families:",len(FAMILIES),"| members:",sum(len(f["members"]) for f in FAMILIES))
print("featured brands:",data["featured_brands"],"| hidden:",HIDDEN_BRANDS)
# guard: no hidden brand appears as a family member
for f in FAMILIES:
    for m in f["members"]:
        if m["brand"] in HIDDEN_BRANDS: print("  WARNING hidden brand member:",f["id"],m)
