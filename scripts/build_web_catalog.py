#!/usr/bin/env python3
"""从 data/labels.db 生成自包含网页版产品库(单HTML, 数据内嵌).
用法: python3 scripts/build_web_catalog.py [输出路径, 默认 data/etia-catalog.html]
生成后可直接浏览器打开, 或作为Artifact/静态页发布。"""
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TPL = ROOT / "scripts/web_catalog"
out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data/etia-catalog.html"

db = sqlite3.connect(ROOT / "data/labels.db")
db.row_factory = sqlite3.Row
rows = db.execute("""
SELECT b.brand_code bc, b.brand_name_cn bcn, p.model_no m, p.product_name_cn nc, p.product_name_en ne,
       f.face_name_cn fc, a.adh_name_cn ac,
       (SELECT GROUP_CONCAT(d.app_name_cn,' / ') FROM product_application pa
        JOIN application_dict d ON d.app_id=pa.app_id WHERE pa.product_id=p.product_id) ap,
       p.temp_long_min t0, p.temp_long_max t1, p.temp_peak_max tp, p.temp_tier tier,
       p.chem_grade chem, p.thickness_um th, p.color c, p.print_method pr, p.certification cert,
       p.feature ft, p.benefit bn, p.application_desc ds, p.source_url src, p.tds_url tds
FROM product p JOIN brand b ON b.brand_id=p.brand_id
LEFT JOIN facestock_dict f ON f.face_id=p.face_id
LEFT JOIN adhesive_dict a ON a.adh_id=p.adh_id
WHERE p.status=1 ORDER BY b.sort_order, b.brand_code, p.model_no""").fetchall()
recs = []
for r in rows:
    d = {k: r[k] for k in r.keys() if r[k] not in (None, "")}
    for k in ("ft", "bn", "ds"):
        if k in d and len(d[k]) > 600:
            d[k] = d[k][:600] + "…"
    recs.append(d)
data = json.dumps(recs, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
body_html = (TPL / "head.html").read_text() + (TPL / "body.html").read_text().replace("__DATA__", data)
html = ('<!doctype html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        + body_html + "\n</body>\n</html>\n")
out.write_text(html)
print(f"{out}: {len(recs)} 款, {round(len(html)/1024)} KB")
