#!/usr/bin/env python3
"""重建 data/labels.db 并把 data/import/*.xlsx 全部导入(进程内, 不起HTTP服务)."""
import io
import os
import sqlite3
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))
import app as A  # noqa: E402

A.init_db()
A.migrate_db()
client = A.app.test_client()
ORDER = ["brady", "3m", "lintec", "polyonics", "ystech", "avery", "flexcon", "computype"]
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for f in ORDER:
    path = os.path.join(root, "data/import", f + ".xlsx")
    if not os.path.exists(path):
        print(f, "SKIP(缺文件)")
        continue
    data = open(path, "rb").read()
    r = client.post("/admin/import",
                    data={"file": (io.BytesIO(data), f + ".xlsx")},
                    content_type="multipart/form-data")
    print(f, r.status_code)
db = sqlite3.connect(os.path.join(root, "data/labels.db"))
print("总数:", db.execute("SELECT COUNT(*) FROM product").fetchone()[0])
print("带原始sub:", db.execute("SELECT COUNT(*) FROM product WHERE sub_application!=''").fetchone()[0])
