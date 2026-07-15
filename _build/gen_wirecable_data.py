#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build _build/data/wirecable.json — Wire & Cable (three pathways).

Explore by Application (8) + Explore by Industry (8) + Explore by Environment (6, the
site-wide set). Products = Avery Dennison flag & wrap-around (Brady methods referenced but
no Brady SKUs supplied). Per brief: product-level environment performance is bound to each
TDS — so product environment specs are marked needs_verification, NOT invented. Environment
association is carried at the application level (brief §6 cross table).
"""
import json, os
BUILD=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(BUILD,"data","wirecable.json")
SRC="Avery Dennison Wire Marking & Cable Label Portfolio (NA, 10/2025) + Brady DataCom references"

# site-wide 6 environments
ENVIRONMENTS=[
 ("abrasion-resistant-labels","Abrasion Resistant Labels","耐磨标签"),
 ("moisture-resistant-labels","Moisture Resistant Labels","耐潮湿标签"),
 ("chemical-resistant-labels","Chemical Resistant Labels","耐化学标签"),
 ("high-heat-labels","High Heat Labels","耐高温标签"),
 ("cryogenic-labels","Cryogenic Labels","超低温标签"),
 ("sterilization-resistant-labels","Sterilization Resistant Labels","耐灭菌标签"),
]
PRIORITY_ENV=["abrasion-resistant-labels","moisture-resistant-labels","chemical-resistant-labels","high-heat-labels"]
CONDITIONAL_ENV=["cryogenic-labels","sterilization-resistant-labels"]

# applications; env = generally-related environments, env_cond = conditional
def A(slug,en,zh,desc_en,desc_zh,env,env_cond):
    return {"slug":slug,"title_en":en,"title_zh":zh,"desc_en":desc_en,"desc_zh":desc_zh,
            "environments":env,"environments_conditional":env_cond}
FULL_ENV=["abrasion-resistant-labels","moisture-resistant-labels","chemical-resistant-labels","high-heat-labels"]
APPLICATIONS=[
 A("flag-cable-labels","Flag Cable Labels","旗型电缆标签",
   "A larger double-sided printable flag for more text, barcodes, 2D codes, port and brand information.",
   "较大的双面打印区域,适合较多文字、条码、二维码、端口及品牌信息。",FULL_ENV,CONDITIONAL_ENV),
 A("wrap-around-cable-labels","Wrap-Around Cable Labels","缠绕式电缆标签",
   "Wraps around the cable in a compact format; a clear tail can cover the printed area for dense wiring.",
   "环绕线缆、结构紧凑;透明部分可覆盖打印区,适合密集布线。",FULL_ENV,CONDITIONAL_ENV),
 A("self-laminating-wire-labels","Self-Laminating Wire Labels","自覆膜线缆标签",
   "A clear tail laminates over the printed area to help protect text and barcodes; confirm by product data.",
   "透明尾部覆盖打印区,帮助保护文字与条码;须按具体产品资料确认。",FULL_ENV,CONDITIONAL_ENV),
 A("heat-shrink-wire-markers","Heat-Shrink Wire Markers","热缩套管标识",
   "Permanent identification of wires, cables and terminals; matched to Brady or other verified products.",
   "用于导线、电缆和端子的永久识别;后续匹配 Brady 或其他已验证产品。",FULL_ENV,CONDITIONAL_ENV),
 A("cable-tags","Cable Tags","电缆吊牌与标签牌",
   "For thicker cables, cable bundles and identification that does not require an adhesive.",
   "适用于较粗电缆、电缆束及无需胶粘的识别场景。",FULL_ENV,CONDITIONAL_ENV),
 A("datacom-network-cabling","DataCom & Network Cabling","数据通信与网络布线",
   "Data centers, cabinets, workstations, ports, fiber and network-cabling identification.",
   "数据中心、机柜、工作站、端口、光纤和网络布线识别。",
   ["abrasion-resistant-labels","moisture-resistant-labels"],[]),
 A("electrical-control-panel-wiring","Electrical & Control Panel Wiring","电气与控制柜布线",
   "Control panels, terminals, conductors, electrical installation, service and troubleshooting.",
   "控制柜、端子、导线、电气安装、维修和故障排查。",
   ["abrasion-resistant-labels","moisture-resistant-labels","chemical-resistant-labels","high-heat-labels"],[]),
 A("wire-harness-cable-assemblies","Wire Harness & Cable Assemblies","线束与电缆组件",
   "Harness production, assembly tracking, build location, serial-number and barcode identification.",
   "线束生产、组件追踪、装配定位、序列号及条码识别。",FULL_ENV,CONDITIONAL_ENV),
]

def I(slug,en,zh,obj_en,obj_zh,apps,envs,show_products):
    return {"slug":slug,"title_en":en,"title_zh":zh,"objects_en":obj_en,"objects_zh":obj_zh,
            "applications":apps,"priority_environments":envs,"show_products":show_products}
INDUSTRIES=[
 I("industrial-manufacturing","Industrial Manufacturing","工业制造",
   "Industrial equipment, automated lines, robots, cabinets, in-machine wiring and service identification.",
   "工业设备、自动化产线、机器人、机柜、机器内部布线及维修识别。",
   ["flag-cable-labels","wrap-around-cable-labels","heat-shrink-wire-markers","cable-tags"],
   ["abrasion-resistant-labels","chemical-resistant-labels","high-heat-labels"],True),
 I("automotive-transportation","Automotive & Transportation","汽车与交通运输",
   "Automotive harnesses, underhood, body electronics, powertrain and transportation-equipment cabling.",
   "汽车线束、发动机舱、车身电子、动力系统及交通设备线缆。",
   ["wrap-around-cable-labels","heat-shrink-wire-markers","self-laminating-wire-labels"],
   ["abrasion-resistant-labels","moisture-resistant-labels","chemical-resistant-labels","high-heat-labels"],True),
 I("datacom-telecom","Data Communications & Telecom","数据通信与电信",
   "Data centers, server cabinets, network ports, communication equipment, copper and fiber identification.",
   "数据中心、服务器机柜、网络端口、通信设备、铜缆及光纤识别。",
   ["flag-cable-labels","wrap-around-cable-labels","self-laminating-wire-labels","datacom-network-cabling"],
   ["abrasion-resistant-labels","moisture-resistant-labels"],True),
 I("electrical-control-systems","Electrical Equipment & Control Systems","电气设备与控制系统",
   "Distribution and control cabinets, terminal blocks, PLC, field devices and electrical installation.",
   "配电柜、控制柜、端子排、PLC、现场设备及电气安装。",
   ["flag-cable-labels","wrap-around-cable-labels","heat-shrink-wire-markers","electrical-control-panel-wiring"],
   ["abrasion-resistant-labels","chemical-resistant-labels","high-heat-labels"],True),
 I("aerospace-defense","Aerospace & Defense","航空航天与国防",
   "Aircraft, avionics, harness assemblies and high-reliability cable identification.",
   "飞机、航电设备、线束组件和高可靠性线缆识别。",
   ["heat-shrink-wire-markers","wrap-around-cable-labels","cable-tags"],
   ["abrasion-resistant-labels"],False),
 I("rail-transit","Rail & Transit","轨道交通",
   "Vehicle harnesses, signaling systems, car equipment, wayside control and power cables.",
   "车辆线束、信号系统、车厢设备、轨旁控制及电力电缆。",
   ["heat-shrink-wire-markers","cable-tags","wrap-around-cable-labels"],
   ["abrasion-resistant-labels","moisture-resistant-labels","chemical-resistant-labels","high-heat-labels"],False),
 I("energy-new-energy","Energy & New Energy","能源与新能源",
   "Photovoltaic, wind, energy storage, battery systems, charging equipment and power-facility cabling.",
   "光伏、风电、储能、电池系统、充电设备及电力设施线缆。",
   ["heat-shrink-wire-markers","cable-tags","wrap-around-cable-labels"],
   ["moisture-resistant-labels","chemical-resistant-labels","high-heat-labels"],False),
 I("medical-equipment","Medical Equipment","医疗设备",
   "In-device harnesses, diagnostic-equipment cabling and sterilizable equipment connections.",
   "医疗设备内部线束、诊断设备线缆及可灭菌设备连接线。",
   ["flag-cable-labels","wrap-around-cable-labels","self-laminating-wire-labels"],
   ["chemical-resistant-labels","abrasion-resistant-labels"],False),
]

def P(pid,name,slug,part,desc,apps,face):
    # environment specs bound to TDS -> needs_verification (not invented)
    return {"id":pid,"brand":"Avery Dennison","product_name":name,"slug":slug,"part_number":part,
            "face_material":face,"application_categories":apps,"environment_paths":[],
            "environment_status":"needs_verification","product_description":desc,
            "verification_status":"needs_verification","source_document":SRC}
PRODUCTS=[
 P("avery-77920","Avery Dennison 77920 White PET Flag","avery-dennison-77920","77920","2M WH PET TC/S8025/50#",
   ["flag-cable-labels","datacom-network-cabling","electrical-control-panel-wiring"],"White PET"),
 P("avery-78385","Avery Dennison 78385 White PET Flag","avery-dennison-78385","78385","2M WH PET TC/S8001/50#SCK",
   ["flag-cable-labels","datacom-network-cabling","electrical-control-panel-wiring"],"White PET"),
 P("avery-79732","Avery Dennison 79732 White PET Flag","avery-dennison-79732","79732","2M WH PET TC/S8029/50#SCK ABC",
   ["flag-cable-labels","datacom-network-cabling","electrical-control-panel-wiring"],"White PET"),
 P("avery-40087","Avery Dennison 40087 White Vinyl Flag","avery-dennison-40087","40087","4M WH F VNL TCD/S730/50# ABC",
   ["flag-cable-labels"],"White flexible vinyl"),
 P("avery-79875","Avery Dennison 79875 Clear Vinyl Wrap","avery-dennison-79875","79875","3.5M CL VINYL NTC/S730/50",
   ["wrap-around-cable-labels","self-laminating-wire-labels"],"Clear vinyl"),
 P("avery-c0734","Avery Dennison C0734 White BOPP Wrap","avery-dennison-c0734","C0734","2.3M WH BOPP TC2000/I406KB/40#BG",
   ["wrap-around-cable-labels"],"White BOPP"),
 P("avery-77855","Avery Dennison 77855 Clear PET Wrap","avery-dennison-77855","77855","1M CL PET TC/S730/1M PET",
   ["wrap-around-cable-labels","self-laminating-wire-labels"],"Clear PET"),
 P("avery-77311","Avery Dennison 77311 PRIMAX PET Wrap","avery-dennison-77311","77311","PRIMAX 250/S730/1.2M PET",
   ["wrap-around-cable-labels"],"PET"),
]

data={"series":"wirecable","hub_route":"/industries/wire-cable/",
 "brand":{"name":"Avery Dennison","note_en":"ETIA supplies material selection; ETIA is not the manufacturer. Brady application methods and Avery Dennison materials may appear on the same page without confusing brand or product source.","note_zh":"ETIA 提供选型支持,并非制造商。Brady 的应用方法与 Avery Dennison 的材料可在同一页面呈现,但不混淆品牌与产品来源。"},
 "environments":[{"slug":s,"title_en":e,"title_zh":z} for s,e,z in ENVIRONMENTS],
 "priority_environments":PRIORITY_ENV,"conditional_environments":CONDITIONAL_ENV,
 "applications":APPLICATIONS,"industries":INDUSTRIES,"products":PRODUCTS}

# integrity
app_slugs={a["slug"] for a in APPLICATIONS}; env_slugs={e["slug"] for e in data["environments"]}
errs=[]
for p in PRODUCTS:
    for a in p["application_categories"]:
        if a not in app_slugs: errs.append("%s bad app %s"%(p["id"],a))
for a in APPLICATIONS:
    for e in a["environments"]+a["environments_conditional"]:
        if e not in env_slugs: errs.append("%s bad env %s"%(a["slug"],e))
for i in INDUSTRIES:
    for a in i["applications"]:
        if a not in app_slugs: errs.append("%s bad app %s"%(i["slug"],a))
if errs: raise SystemExit("DATA ERRORS:\n"+"\n".join(errs))
os.makedirs(os.path.dirname(OUT),exist_ok=True)
json.dump(data,open(OUT,"w"),ensure_ascii=False,indent=1)
print("products:",len(PRODUCTS),"| applications:",len(APPLICATIONS),"| industries:",len(INDUSTRIES),"| environments:",len(ENVIRONMENTS))
for a in app_slugs:
    n=sum(1 for p in PRODUCTS if a in p["application_categories"]); print("  app %s: %d products"%(a,n))
