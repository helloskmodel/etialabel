#!/usr/bin/env python3
"""把已抓取的原始数据(data/raw/)清洗成 /admin/import 可导入的Excel(data/import/).

清洗规则依据 docs/label-pim-database-design.md 模块3:
- 五维对齐: face/adh 映射到标准字典code; apps 多对多; 耐温取长期上限(tmax);
  只有峰值时按 峰值x0.7 折算长期值并在 source_raw 标"待复核"(Polyonics/LINTEC);
  YS-Tech 温度带上限直接归档(设计文档3.4)。
- 耐化学 A/B/C/D: 耐强溶剂浸泡→A; 耐IPA/汽油/机油→B; 仅耐水油→C; 无声明→D。
- 官网没写的参数留空,绝不编造; 原始分类原文存 source_raw, 源页URL存 url。
"""
import glob
import json
import re
from collections import OrderedDict
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw"
OUT = ROOT / "data/import"
OUT.mkdir(parents=True, exist_ok=True)

HEADERS = ["brand", "model", "name_cn", "name_en", "face", "adh", "apps",
           "tmin", "tmax", "tpeak", "chem", "thick", "color", "print", "cert",
           "feature", "benefit", "app_desc", "source_raw", "url", "pub", "tds", "sub"]

# ---------------------------------------------------------------- face / adh
FACE_MAP = [  # (关键词正则, code) 顺序敏感: 具体的在前
    (r"polyimide|\bPI\b", "POLYIMIDE"),
    (r"metali?zed polyester|metallized", "POLYESTER"),
    (r"polyester|\bPET\b|Yupo.*PET", "POLYESTER"),
    (r"\bPEN\b", "PEN"),
    (r"\bPPS\b", "PPS"),
    (r"aluminum foil|aluminium foil|\bAL foil|铝箔", "ALU_FOIL"),
    (r"polypropylene|\bPP\b(?!S)", "PP"),
    (r"polyethylene naphthalate", "PEN"),
    (r"polyethylene|\bPE\b(?!N|T)", "PE"),
    (r"vinyl|\bPVC\b", "VINYL"),
    (r"polyolefin", "POLYOLEFIN"),
    (r"nylon cloth", "NYLON_CLOTH"),
    (r"glass cloth|acetate cloth|polyester cloth|cloth", "CLOTH"),
    (r"tyvek", "TYVEK"),
    (r"synthetic paper|yupo", "SYNTHETIC_PAPER"),
    (r"thermal paper|paper", "PAPER"),
    (r"ceramic|coated steel|metal (base|tag)|stainless", "CERAMIC_METAL"),
    (r"tamper|destructible|易碎|frangible|acrylate", "TAMPER_EVIDENT"),
    (r"polycarbonate", "POLYCARBONATE"),      # 以下字典自动新建
    (r"polyurethane", "POLYURETHANE"),
    (r"polystyrene|\bPS\b film", "POLYSTYRENE"),
    (r"nonwoven", "NONWOVEN"),
    (r"foam base|foam", "FOAM"),
    (r"tedlar|\bPVF\b", "PVF"),
    (r"tissue", "TISSUE"),
    (r"thermal top", "PAPER"),
    (r"aluminum|aluminium|\bAL\b core", "ALU_FOIL"),
]
ADH_MAP = [
    (r"tie-on|no adhesive|none|机械固定|无胶", "NONE"),
    (r"heat[- ]?activated|heat seal", "HEAT_ACTIVATED"),  # 自动新建(YS-Tech贴热面)
    (r"repositionable|removable|low adhesion", "REMOVABLE"),
    (r"aggressive|high[- ]?tack|super[- ]?bond|high adhesion", "AGGRESSIVE_PERM"),
    (r"pressure[- ]?sensitive|2 layer adhesive", "PSA"),  # 自动新建: 压敏胶(化学系未标注)
    (r"silicone", "SILICONE"),
    (r"rubber", "RUBBER"),
    (r"medical|low[- ]?trauma", "MEDICAL_GRADE"),
    (r"(high[- ]?temp|HT).{0,12}acrylic|acrylic.{0,12}(high[- ]?temp|350|100MP)", "HT_ACRYLIC"),
    (r"low[- ]?temp|cold[- ]?temp|freezer|cryo", "COLD_TEMP"),
    (r"acrylic", "ACRYLIC"),
]


def map_code(table, text):
    if not text:
        return ""
    for pat, code in table:
        if re.search(pat, text, re.I):
            return code
    return ""


# ---------------------------------------------------------------- 中文名模板
CN_COLOR = [("white", "白色"), ("clear", "透明"), ("silver", "银色"),
            ("black", "黑色"), ("yellow", "黄色"), ("green", "绿色"),
            ("red", "红色"), ("blue", "蓝色"), ("amber", "琥珀色")]
CN_FINISH = [("glossy", "光面"), ("gloss", "光面"), ("matte", "哑面"),
             ("matt", "哑面"), ("satin", "缎面")]
CN_MATERIAL = [("polyimide", "聚酰亚胺"), ("metallized polyester", "金属化聚酯"),
               ("polyester", "聚酯"), ("polypropylene", "聚丙烯"),
               ("polyethylene", "聚乙烯"), ("polyolefin", "聚烯烃"),
               ("vinyl", "乙烯基"), ("paper", "纸质"), ("tyvek", "Tyvek"),
               ("nylon cloth", "尼龙布"), ("polycarbonate", "聚碳酸酯"),
               ("aluminum foil", "铝箔"), ("acrylate", "丙烯酸酯")]
CN_TRAIT = [("thermal transfer", "热转印"), ("laser markable", "激光打标"),
            ("acetone resistant", "耐丙酮"), ("chemical resistant", "耐化学"),
            ("high temperature", "耐高温"), ("tamper evident", "防拆"),
            ("tamper indicating", "防拆"), ("destructible", "易碎"),
            ("removable", "可移除"), ("repositionable", "可重贴"),
            ("dissolvable", "可溶解"), ("self-laminating", "自覆膜"),
            ("heat-shrink", "热缩"), ("reflective", "反光"),
            ("static dissipative", "防静电"), ("低温", "低温")]
CN_TYPE = [("overlaminating tape", "覆膜带"), ("overlaminate", "覆膜"),
           ("label material", "标签材料"), ("label stock", "标签材料"),
           ("labelstock", "标签材料"), ("sleeve", "套管"), ("tag", "挂牌"),
           ("tape", "胶带"), ("label", "标签")]


def cn_name(name_en, brand_prefix, model):
    low = name_en.lower()
    parts = []
    for pairs in (CN_TRAIT, CN_FINISH, CN_COLOR, CN_MATERIAL):
        for k, cn in pairs:
            if k in low:
                parts.append(cn)
                break
    typ = ""
    for k, cn in CN_TYPE:
        if k in low:
            typ = cn
            break
    if not parts and not typ:
        return ""
    return f"{brand_prefix}{''.join(parts)}{typ or '标签材料'} {model}".strip()


# ---------------------------------------------------------------- 通用工具
def c_int(s):
    """'130 °C' / '150℃' / '-70 °C' -> int"""
    if not s:
        return None
    m = re.search(r"(-?\d+)\s*(?:°\s*C|℃|C\b)", str(s))
    return int(m.group(1)) if m else None


def um_from(s):
    """'0.064 mm'/'50 micron'/'2 mil' -> um int"""
    if not s:
        return None
    s = str(s)
    m = re.search(r"([\d.]+)\s*mm", s)
    if m:
        return round(float(m.group(1)) * 1000)
    m = re.search(r"([\d.]+)\s*(?:micron|um|µm|μm)", s, re.I)
    if m:
        return round(float(m.group(1)))
    m = re.search(r"([\d.]+)\s*mil\b", s, re.I)
    if m:
        return round(float(m.group(1)) * 25.4)
    return None


def chem_from_text(text):
    t = (text or "").lower()
    if re.search(r"mek|xylene|toluene|acetone|solvent[s]? (resist|immersion)|"
                 r"resistan\w+ to (organic )?solvents|bs\s*5609|二甲苯", t):
        return "A"
    if re.search(r"\bipa\b|isopropyl|alcohol|gasoline|fuel|oil resist|"
                 r"resistan\w+ to oils|petrol|机油|汽油|酒精", t):
        return "B"
    if re.search(r"water resist|oil|moisture|防水|耐水", t):
        return "C"
    return "D"


def row_dict(**kw):
    d = OrderedDict((h, "") for h in HEADERS)
    d.update({k: v for k, v in kw.items() if v is not None})
    return d


def write_xlsx(rows, fname):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(HEADERS)
    for r in rows:
        ws.append([r[h] if r[h] != "" else None for h in HEADERS])
    wb.save(OUT / fname)
    return len(rows)


def finish_pub(r):
    r["pub"] = 1 if (r["face"] and r["adh"] and r["tmax"] != "" and r["apps"]) else 0
    return r


# ================================================================ Brady
BRADY_APP = {"General Identification": "MANUFACTURING", "Wire & Cable": "DATACOM",
             "Inspection Repair": "MANUFACTURING", "Rating & Name Plates": "MANUFACTURING",
             "Circuit Board": "ELECTRONICS", "Laboratory": "LAB_BIO",
             "Electrical": "ELECTRONICS", "DataCom": "DATACOM", "Safety": "SAFETY"}


def conv_brady():
    data = json.load(open(RAW / "brady/MSApp.json"))["Bnums"]
    rows = []
    for x in data:
        num = x["num"]
        adh_raw = x.get("adhesive") or ""
        adh = map_code(ADH_MAP, adh_raw) or ("NONE" if not adh_raw else "")
        face = map_code(FACE_MAP, x.get("baseMaterial") or "")
        # 耐化学: 1~5评分(5优)。溶剂≥4→A; 醇/油/燃料≥4→B; 清洁剂/油≥3→C; 全无→D
        def sc(k):
            v = x.get(k)
            return int(v) if v not in (None, "") else 0
        if sc("chemResistanceSolvents") >= 4:
            chem = "A"
        elif max(sc("chemResistanceAlcohols"), sc("chemResistanceOils"),
                 sc("chemResistanceFuels")) >= 4:
            chem = "B"
        elif max(sc("chemResistanceCleaners"), sc("chemResistanceOils")) >= 3:
            chem = "C"
        else:
            chem = "D"
        apps = ",".join(dict.fromkeys(
            BRADY_APP.get(a, "MANUFACTURING") for a in x.get("printerLabelApplications", [])))
        feats = []
        if x.get("materialType"):
            feats.append({"Label": "标签", "Sleeve": "线缆套管", "Tag": "挂牌",
                          "Self-Lam": "自覆膜"}.get(x["materialType"], x["materialType"]))
        if x.get("finish"):
            feats.append(f"表面: {x['finish']}")
        feats += x.get("specialProperties", [])
        name_en = x.get("name") or ""
        rows.append(finish_pub(row_dict(
            brand="BRADY", model=num,
            name_cn=cn_name(name_en, "Brady", num), name_en=name_en,
            face=face, adh=adh, apps=apps,
            tmin=c_int(x.get("minServiceTemperatureC")) if c_int(x.get("minServiceTemperatureC")) is not None else "",
            tmax=c_int(x.get("maxServiceTemperatureC")) if c_int(x.get("maxServiceTemperatureC")) is not None else "",
            tpeak="",
            chem=chem, thick=um_from(x.get("thicknessMm")) or "",
            color=", ".join(x.get("colors", [])),
            print="", cert=", ".join(x.get("compliance", [])),
            feature="; ".join(feats), benefit="",
            app_desc=x.get("description") or "",
            source_raw=f"Brady材料选型器 MSApp.json | materialType={x.get('materialType')} | 原胶水: {adh_raw} | 原面材: {x.get('baseMaterial')}",
            sub=(x.get("printerLabelApplications") or [""])[0],
            url="https://d37iyw84027v1q.cloudfront.net/Common/msapp/index.html",
            tds=f"https://tds.bradyid.com/TDSdocs/{num}.pdf",
        )))
    return rows


# ================================================================ 3M
def conv_3m():
    rows = {}
    for f in sorted(glob.glob(str(RAW / "3m_pages/*.json"))):
        p = json.load(open(f))
        model = p.get("product_number") or p.get("discovery", {}).get("material_number", "")
        if not model:
            continue
        at = p["attributes"]
        first = lambda k: (at.get(k) or [""])[0]
        name_en = re.split(r",\s*\d", p["name"])[0].strip()  # 去尺寸后缀
        text_all = " ".join([p.get("short_description", "")] + p.get("benefits", []))
        face_raw = first("Facestock Material")
        adh_raw = first("Face Side Adhesive Type") or first("Adhesive Type")
        m_adhnum = re.search(r"adhesive\s+(\d{3}[A-Z]{0,2})", text_all, re.I)
        adh = map_code(ADH_MAP, adh_raw + " " + (m_adhnum.group(0) if m_adhnum else ""))
        tmax = c_int(first("Maximum Operating Temperature (Celsius)"))
        tmin = c_int(first("Minimum Operating Temperature (Celsius)"))
        certs = sorted(set(re.findall(r"UL\s?\d*|cUL|CSA|RoHS|REACH|BS\s?5609|MIL-STD-\d+", text_all)))
        tds = next((u for u in p.get("tds_pdfs", []) if ".pdf" in u.lower()), "")
        r = row_dict(
            brand="3M", model=str(model),
            name_cn=cn_name(name_en, "3M", model), name_en=name_en,
            face=map_code(FACE_MAP, face_raw), adh=adh,
            apps=",".join(dict.fromkeys(
                i.upper() for i in p.get("discovery", {}).get("industries", []))),
            tmin=tmin if tmin is not None else "", tmax=tmax if tmax is not None else "",
            tpeak="", chem=chem_from_text(text_all),
            thick=um_from(first("Facestock Thickness (Metric)")) or "",
            color=first("Product Color") or first("Facestock Color"),
            print=first("Printing Method"), cert=", ".join(certs),
            feature="; ".join(f"{k}: {', '.join(v)}" for k, v in at.items()
                              if k in ("Facestock Material", "Surface Finish", "Topcoat",
                                       "Adhesive Type", "Face Side Adhesive Type"))[:500],
            benefit="; ".join(p.get("benefits", []))[:800],
            app_desc=p.get("short_description", "")[:500],
            source_raw="3M官网Labels目录 breadcrumb: " + " > ".join(p.get("breadcrumb", []))
                       + f" | 原面材: {face_raw} | 原胶水: {adh_raw}",
            url=p.get("canonical") or p.get("url", ""),
        )
        if tds:
            r["source_raw"] += f" | TDS: {tds}"
            r["tds"] = tds
        if str(model) in rows:  # 同型号双页面(卷装/定制)合并: 补空字段
            old = rows[str(model)]
            for k, v in r.items():
                if old[k] in ("", None) and v not in ("", None):
                    old[k] = v
        else:
            rows[str(model)] = r
    return [finish_pub(r) for r in rows.values()]


# ================================================================ 旧220条(LINTEC/Polyonics/YS-Tech)
def parse_temp_old(mfr, tp):
    """返回 (tmin,tmax,tpeak,待复核标记)"""
    if not tp:
        return "", "", "", False
    nums = [int(m) for m in re.findall(r"(-?\d{2,4})\s*(?:℃|°\s*C)", tp)]
    if not nums:
        return "", "", "", False
    tmin = min(nums) if min(nums) < 0 else ""
    peak = max(nums)
    if mfr == "Polyonics":
        m = re.search(r"(\d+)\s*hrs?\s*at\s*\d+\s*°?F?\s*\((\d+)\s*°?C\)", tp)
        if m:  # "100 hrs at 302°F (150°C)" -> 长期150
            return tmin, int(m.group(2)), peak, False
        return tmin, round(peak * 0.7), peak, True   # 只有峰值 -> x0.7 待复核
    if mfr == "LINTEC":
        if re.search(r"10 mins? to 1 hr|not intended for guarantee", tp):
            return tmin, round(peak * 0.7), peak, True
        return tmin, peak, "", False
    # YS-Tech: 温度带上限直接归档(设计文档3.4), 保留峰值
    return tmin, peak, peak, False


def conv_old(target_mfr, brand_code, brand_cn_prefix):
    data = json.load(open(RAW / "label_materials_db_220.json"))["records"]
    rows = []
    for r in data:
        if r["manufacturer"] != target_mfr:
            continue
        text_all = " ".join([r.get("application_en", "")] + r.get("features_en", [])
                            + r.get("benefits_en", []) + [r.get("adhesive_en", "")])
        tmin, tmax, tpeak, review = parse_temp_old(target_mfr, r.get("temperature_performance", ""))
        src = f"来源分类页: {r.get('catalog_url', '')}"
        if review:
            src += " | 待复核: 官网只给短时耐温, 长期值按峰值x0.7折算(设计文档3.3规则①)"
        adh_code = map_code(ADH_MAP, r.get("adhesive_en", ""))
        if adh_code in ("AGGRESSIVE_PERM", "REMOVABLE", "PSA") and \
                re.search(r"adhesion|pressure-sensitive|2 layer", r.get("adhesive_en", ""), re.I):
            src += " | 待复核: 胶系化学类型官网未标注, 按粘性等级/压敏描述推断归类(confidence=2)"
        if r.get("temperature_performance"):
            src += f" | 原文耐温: {r['temperature_performance'][:150]}"
        apps = ",".join(dict.fromkeys(filter(None, (
            {"electronics": "ELECTRONICS", "steel": "METALLURGY", "aluminum": "METALLURGY",
             "aluminium": "METALLURGY", "galvanizing": "METALLURGY", "metallurgy": "METALLURGY",
             "ceramic": "MANUFACTURING", "ceramics": "MANUFACTURING",
             "casting": "METALLURGY", "automotive": "AUTOMOTIVE", "aerospace": "AEROSPACE",
             "medical": "MEDICAL", "pharmacy": "PHARMACY", "pharmaceutical": "PHARMACY",
             "laboratory": "LAB_BIO", "healthcare": "MEDICAL", "coating": "MANUFACTURING",
             "manufacturing": "MANUFACTURING", "industrial": "MANUFACTURING",
             "logistics": "TRANSPORTATION", "transportation": "TRANSPORTATION",
             "pcb": "ELECTRONICS", "concrete": "MANUFACTURING", "wire": "DATACOM"}
            .get(i.strip().lower(), "") for i in r.get("industries", [])))))
        rows.append(finish_pub(row_dict(
            brand=brand_code, model=r["product_code"],
            name_cn=r.get("name_zh", ""), name_en=r.get("name_en", ""),
            face=map_code(FACE_MAP, r.get("facestock_en", "")),
            adh=map_code(ADH_MAP, r.get("adhesive_en", "")),
            apps=apps, tmin=tmin, tmax=tmax, tpeak=tpeak,
            chem=chem_from_text(text_all),
            thick=um_from(r.get("facestock_en", "")) or "",
            color="", print="", cert=", ".join(r.get("certifications", [])),
            feature="; ".join(r.get("features_en", []))[:800],
            benefit="; ".join(r.get("benefits_en", []))[:800],
            app_desc=r.get("application_en", "")[:500],
            source_raw=src[:500], url=r.get("tds_url", ""),
            tds=r.get("tds_url", ""),
        )))
    return rows


# ================================================================ Avery (records_raw.json 通用格式, FLEXcon同构)
def conv_raw_generic(raw_path, brand_code, shorten_model=False):
    data = json.load(open(raw_path))["records"]
    rows = {}
    for r in data:
        model = str(r.get("model", "")).strip()
        if not model:
            continue
        if shorten_model:  # FLEXcon: 全名截短为"产品家族+编号"(如 THERMLfilm SELECT 10852)
            m = re.match(r"^(.*?\d{4,6}[A-Z]{0,2})\b", model)
            if m and len(m.group(1)) < len(model):
                model = m.group(1).strip()
        temp_raw = r.get("temp_raw", "")
        tmax = c_int(temp_raw)
        if tmax is None and temp_raw:  # 只有华氏度时换算(设计文档3.3规则②)
            m = re.search(r"(-?\d+)\s*°?\s*F\b", temp_raw)
            if m:
                tmax = round((int(m.group(1)) - 32) * 5 / 9)
        neg = re.findall(r"(-\d+)\s*(?:°\s*C|℃)", temp_raw)
        tmin = min(int(n) for n in neg) if neg else ""
        text_all = " ".join([r.get("chem_raw", ""), r.get("app_desc", "")]
                            + r.get("features", []) + r.get("benefits", []))
        src = r.get("source_category_raw", "")
        for k, lab in (("facestock_raw", "原面材"), ("adhesive_raw", "原胶水"), ("liner", "底纸")):
            if r.get(k):
                src += f" | {lab}: {r[k]}"
        if temp_raw:
            src += f" | 原文耐温: {temp_raw[:120]}"
        url = r.get("url", "")
        tds = r.get("tds", "") or (url if ".pdf" in url.lower() else "")
        row = finish_pub(row_dict(
            brand=brand_code, model=model,
            name_cn=r.get("name_cn", ""), name_en=r.get("name_en", ""),
            face=map_code(FACE_MAP, r.get("facestock_raw", "")),
            adh=map_code(ADH_MAP, r.get("adhesive_raw", "")),
            apps=",".join(dict.fromkeys(r.get("sectors", []))),
            tmin=tmin, tmax=tmax if tmax is not None else "", tpeak="",
            chem=chem_from_text(text_all),
            thick=um_from(r.get("thickness_raw", "")) or "",
            color="", print="", cert=r.get("cert", ""),
            feature="; ".join(r.get("features", []))[:800],
            benefit="; ".join(r.get("benefits", []))[:800],
            app_desc=r.get("app_desc", "")[:500],
            source_raw=src[:500], url=url, tds=tds,
            sub=r.get("sub_application", ""),
        ))
        if model in rows:  # 双板块同型号合并
            old = rows[model]
            merged_apps = ",".join(dict.fromkeys(
                filter(None, old["apps"].split(",") + row["apps"].split(","))))
            for k, v in row.items():
                if old[k] in ("", None) and v not in ("", None):
                    old[k] = v
            old["apps"] = merged_apps
        else:
            rows[model] = row
    return list(rows.values())


def main():
    stats = {}
    stats["brady.xlsx"] = write_xlsx(conv_brady(), "brady.xlsx")
    if (RAW / "avery/records_raw.json").exists():
        stats["avery.xlsx"] = write_xlsx(
            conv_raw_generic(RAW / "avery/records_raw.json", "AVERY"), "avery.xlsx")
    if (RAW / "flexcon/records_raw.json").exists():
        stats["flexcon.xlsx"] = write_xlsx(
            conv_raw_generic(RAW / "flexcon/records_raw.json", "FLEXCON", shorten_model=True), "flexcon.xlsx")
    if (RAW / "computype/records_raw.json").exists():
        stats["computype.xlsx"] = write_xlsx(
            conv_raw_generic(RAW / "computype/records_raw.json", "COMPUTYPE"), "computype.xlsx")
    stats["3m.xlsx"] = write_xlsx(conv_3m(), "3m.xlsx")
    stats["lintec.xlsx"] = write_xlsx(conv_old("LINTEC", "LINTEC", "琳得科"), "lintec.xlsx")
    stats["polyonics.xlsx"] = write_xlsx(conv_old("Polyonics", "POLYONICS", ""), "polyonics.xlsx")
    stats["ystech.xlsx"] = write_xlsx(conv_old("YS-Tech", "YSTECH", ""), "ystech.xlsx")
    for k, v in stats.items():
        print(f"{k}: {v} 行")
    print("合计:", sum(stats.values()))


if __name__ == "__main__":
    main()
