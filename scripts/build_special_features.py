#!/usr/bin/env python3
"""给产品打"特色功能"标(跨行业维度): REMOVABLE / TAMPER / AUTOMATION / RFID.
规则精准, 只标品牌原文真实支撑的; 逗号分隔存 product.special_features. 幂等可重跑。
"""
import sqlite3
from pathlib import Path
DB = Path(__file__).resolve().parent.parent / "data/labels.db"
# (标签中文, 标签英文, 精准SQL条件)
RULES = [
    ("可移除", "Removable",
     "a.adh_code='REMOVABLE' OR p.feature LIKE '%removable%' OR p.feature LIKE '%repositionable%'"
     " OR p.product_name_en LIKE '%removable%' OR p.product_name_en LIKE '%repositionable%'"),
    ("防伪防拆", "Tamper-Evident",
     "f.face_code='TAMPER_EVIDENT' OR p.feature LIKE '%tamper%' OR p.feature LIKE '%destructible%'"
     " OR p.product_name_en LIKE '%tamper%' OR p.product_name_en LIKE '%destructible%'"),
    ("自动化贴标", "Automation-Ready",
     "p.feature LIKE '%structured adhesive%' OR p.feature LIKE '%air egress%' OR p.feature LIKE '%air-egress%'"
     " OR p.feature LIKE '%bubble-free%' OR p.feature LIKE '%go on smoothly%'"
     " OR (b.brand_code='3M' AND p.model_no GLOB '*SA')"),
    ("RFID", "RFID",
     "p.feature LIKE '%RFID%' OR p.product_name_en LIKE '%RFID%' OR p.product_name_en LIKE '%inlay%'"
     " OR p.application_desc LIKE '%RFID%' OR p.application_desc LIKE '%inlay%'"),
]


def main():
    db = sqlite3.connect(DB)
    try:
        db.execute("ALTER TABLE product ADD COLUMN special_features TEXT")
    except sqlite3.OperationalError:
        pass
    db.execute("UPDATE product SET special_features=''")
    tags = {}
    for cn, en, cond in RULES:
        ids = [r[0] for r in db.execute(
            f"""SELECT p.product_id FROM product p JOIN brand b ON b.brand_id=p.brand_id
               LEFT JOIN adhesive_dict a ON a.adh_id=p.adh_id
               LEFT JOIN facestock_dict f ON f.face_id=p.face_id
               WHERE p.status=1 AND ({cond})""").fetchall()]
        for pid in ids:
            tags.setdefault(pid, []).append(f"{cn}|{en}")
        print(f"  {cn} ({en}): {len(ids)} 款")
    for pid, tg in tags.items():
        db.execute("UPDATE product SET special_features=? WHERE product_id=?", ("; ".join(tg), pid))
    db.commit()
    print("已打标产品:", len(tags))
    db.close()


if __name__ == "__main__":
    main()
