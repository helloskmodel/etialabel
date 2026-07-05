#!/usr/bin/env python3
"""从 data/labels.db 生成自包含网页版产品库(单HTML, 数据内嵌).
用法: python3 scripts/build_web_catalog.py [输出路径] [lang=zh|en]
  lang=zh(默认) 中文界面+中文数据; lang=en 英文界面+英文数据。
未来加语言: 在 UI_I18N 增加一列 + SQL 选对应 _xx 字段即可。
生成后可直接浏览器打开, 或作为静态页发布。"""
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TPL = ROOT / "scripts/web_catalog"

args = [a for a in sys.argv[1:] if not a.startswith("lang=")]
lang = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("lang=")), "zh")
out = Path(args[0]) if args else ROOT / f"data/etia-catalog{'-en' if lang=='en' else ''}.html"

db = sqlite3.connect(ROOT / "data/labels.db")
db.row_factory = sqlite3.Row

if lang == "en":
    # 英文: 用 _en 字段填进同名 key(nc/fc/ac/ap/sub/bcn), JS模板无需改
    SQL = """
    SELECT b.brand_code bc, b.brand_name_en bcn, p.model_no m, p.product_name_en nc, p.product_name_en ne,
           f.face_name_en fc, a.adh_name_en ac,
           (SELECT GROUP_CONCAT(d.app_name_en,' / ') FROM product_application pa
            JOIN application_dict d ON d.app_id=pa.app_id WHERE pa.product_id=p.product_id) ap,
           p.temp_long_min t0, p.temp_long_max t1, p.temp_peak_max tp, p.temp_tier tier,
           p.chem_grade chem, p.thickness_um th, p.color c, p.print_method pr, p.certification cert,
           p.feature ft, p.benefit bn, p.application_desc ds, p.source_url src, p.tds_url tds,
           (SELECT ap2.name_en FROM application ap2 WHERE ap2.name_cn=p.sub_application) sub
    FROM product p JOIN brand b ON b.brand_id=p.brand_id
    LEFT JOIN facestock_dict f ON f.face_id=p.face_id
    LEFT JOIN adhesive_dict a ON a.adh_id=p.adh_id
    WHERE p.status=1 ORDER BY b.sort_order, b.brand_code, p.model_no"""
else:
    SQL = """
    SELECT b.brand_code bc, b.brand_name_cn bcn, p.model_no m, p.product_name_cn nc, p.product_name_en ne,
           f.face_name_cn fc, a.adh_name_cn ac,
           (SELECT GROUP_CONCAT(d.app_name_cn,' / ') FROM product_application pa
            JOIN application_dict d ON d.app_id=pa.app_id WHERE pa.product_id=p.product_id) ap,
           p.temp_long_min t0, p.temp_long_max t1, p.temp_peak_max tp, p.temp_tier tier,
           p.chem_grade chem, p.thickness_um th, p.color c, p.print_method pr, p.certification cert,
           p.feature ft, p.benefit bn, p.application_desc ds, p.source_url src, p.tds_url tds,
           p.sub_application sub
    FROM product p JOIN brand b ON b.brand_id=p.brand_id
    LEFT JOIN facestock_dict f ON f.face_id=p.face_id
    LEFT JOIN adhesive_dict a ON a.adh_id=p.adh_id
    WHERE p.status=1 ORDER BY b.sort_order, b.brand_code, p.model_no"""

rows = db.execute(SQL).fetchall()
recs = []
for r in rows:
    d = {k: r[k] for k in r.keys() if r[k] not in (None, "")}
    for k in ("ft", "bn", "ds"):
        if k in d and len(d[k]) > 600:
            d[k] = d[k][:600] + "…"
    recs.append(d)

# ---- UI 文案 i18n: 中文原文 -> 英文 (按长度降序替换, 避免子串冲突) ----
UI_I18N = {
    "特种标签选型商城": "Specialty Label Selector",
    "输入工况或型号,快速找到能用的标签材料": "Find the right label material by application or part number",
    "试试:聚酰亚胺 / 回流焊 / B-423 / 耐酒精 / 冻存…": "Try: polyimide / reflow / B-423 / alcohol-resistant / cryo…",
    "耐化学分级:A 耐强溶剂浸泡 / B 耐酒精·汽油·机油 / C 耐水油 / D 官网未声明 · 空白字段=品牌官网未公布(不编造)":
        "Chemical grade: A strong-solvent immersion / B alcohol·fuel·oil / C water & oil / D not stated · blank = not published by brand (never fabricated)",
    "ETIA 特种标签统一产品库 · 数据来自各品牌官网/官方TDS/官方选型器,均带溯源链接 · 官网未公布的参数留空不编造 · 2026-07":
        "ETIA Unified Label Database · Data from official brand pages / TDS / selectors, each source-linked · Unpublished specs left blank, never fabricated · 2026-07",
    "没有匹配的产品——换个关键词,或清空部分筛选条件试试。": "No matching products — try another keyword or clear some filters.",
    "＋ 更多筛选(面材/胶水/耐化学)": "＋ More filters (facestock / adhesive / chemical)",
    "产品介绍 / 适用工况": "Product Overview / Application",
    "品牌官网源页 ↗": "Brand source page ↗",
    "⬇ 下载官方 TDS": "⬇ Download official TDS",
    "查看详情 →": "View details →",
    "耐温 高→低": "Temp high→low",
    "综合排序": "Best match",
    "按品牌": "By brand",
    "特性 Feature": "Features",
    "优势 Benefit": "Benefits",
    "长期耐温": "Long-term temp",
    "厚度 / 颜色": "Thickness / Color",
    "打印方式": "Print method",
    "数据溯源:": "Source: ",
    "数据溯源": "Data source",
    "耐温 ≥ ": "Temp ≥ ",
    "耐高温": "Max temp",
    "耐低温": "Min temp",
    "耐化学": "Chemical",
    "聚酰亚胺": "Polyimide", "回流焊": "Reflow", "灭菌": "Steriliz.", "液氮": "LN₂",
    "可达": "≥", "以上": "+",
    "大品牌": " Brands", "款": "", "共": "of", "命中": "Showing", "全部": "All",
    "✓ 官方TDS": "✓ Official TDS",
    "加载更多 ▾": "Load more ▾",
    "导出CSV": "Export CSV",
    "清空": "Reset",
    "搜 索": "Search",
    "品牌": "Brand", "行业": "Industry", "应用": "Application",
    "面材": "Facestock", "胶水": "Adhesive", "资料": "Docs", "认证": "Cert",
    "关闭": "Close", "峰值": "peak", "颜色": "Color",
    "中文品名": "Name", "英文品名": "Name (EN)", "型号": "Model", "品名": "Product",
    "低温冻存": "Cryogenic", "线缆": "Cable", "铭牌": "Nameplate", "防拆": "Tamper",
    "热门": "Popular", "档": "",
    "仅看有TDS": "With TDS", "厚度um": "Thickness_um", "档位": "Tier",
    "打印": "Print", "来源": "Source", "适用": "Application",
    "－ 收起筛选": "－ Fewer filters", "ETIA产品筛选导出": "ETIA-products-export",
    "款材料": " products", "份官方TDS": " Official TDS", "材料": " products",
    "耐温": "Temp ",
    "品牌 Brand": "Brand",
}


def apply_i18n(text):
    for zh in sorted(UI_I18N, key=len, reverse=True):
        text = text.replace(zh, UI_I18N[zh])
    return text


data = json.dumps(recs, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
body_html = (TPL / "head.html").read_text() + (TPL / "body.html").read_text().replace("__DATA__", data)
if lang == "en":
    # 替换 SUB_IND 联动映射为英文版
    import re as _re
    en_map = (TPL / "sub_ind_en.js").read_text()
    body_html = _re.sub(r"const SUB_IND=\{.*?\};", en_map, body_html, count=1)
    head_body, sep, datapart = body_html.partition('<script id="data"')
    body_html = apply_i18n(head_body) + sep + apply_i18n(datapart)

html_lang = "en" if lang == "en" else "zh-CN"
html = (f'<!doctype html>\n<html lang="{html_lang}">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        + body_html + "\n</body>\n</html>\n")
out.write_text(html)
print(f"{out}: {len(recs)} products, lang={lang}, {round(len(html)/1024)} KB")
