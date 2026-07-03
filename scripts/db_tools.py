#!/usr/bin/env python3
"""Tools for label_materials_db.json: validate, merge crawl fragments, regenerate CSV.

Usage:
  python3 scripts/db_tools.py validate
  python3 scripts/db_tools.py merge crawl/polyonics/records.json
  python3 scripts/db_tools.py csv
  python3 scripts/db_tools.py stats
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "label_materials_db.json"
CSV_PATH = ROOT / "label_materials_db.csv"

LIST_FIELDS = {"industries", "features_en", "features_zh", "benefits_en",
               "benefits_zh", "certifications", "sources"}
REQUIRED_NONEMPTY = {"manufacturer", "product_code", "name_en", "name_zh",
                     "tds_url", "data_status"}


def load_db():
    with open(DB_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_db(db):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
        f.write("\n")


def validate_record(rec, fields, errors, ctx):
    extra = set(rec) - set(fields)
    missing = set(fields) - set(rec)
    # tds_local_path is an allowed optional extension per task spec
    extra -= {"tds_local_path"}
    if extra:
        errors.append(f"{ctx}: unexpected fields {sorted(extra)}")
    if missing:
        errors.append(f"{ctx}: missing fields {sorted(missing)}")
    for f in REQUIRED_NONEMPTY & set(rec):
        if not rec[f]:
            errors.append(f"{ctx}: empty required field '{f}'")
    for f in LIST_FIELDS & set(rec):
        if not isinstance(rec[f], list):
            errors.append(f"{ctx}: field '{f}' must be a list")
    for f in set(rec) - LIST_FIELDS:
        if not isinstance(rec[f], str):
            errors.append(f"{ctx}: field '{f}' must be a string")
    if rec.get("tds_url") and not str(rec["tds_url"]).startswith("http"):
        errors.append(f"{ctx}: tds_url is not a URL")


def cmd_validate():
    db = load_db()
    fields = db["meta"]["record_fields"]
    errors = []
    seen = {}
    for i, rec in enumerate(db["records"]):
        key = (rec.get("manufacturer", "").lower(), rec.get("product_code", "").lower())
        ctx = f"records[{i}] {key[0]}/{key[1]}"
        if key in seen:
            errors.append(f"{ctx}: duplicate of records[{seen[key]}]")
        seen[key] = i
        validate_record(rec, fields, errors, ctx)
    if errors:
        print(f"INVALID: {len(errors)} error(s)")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    print(f"OK: {len(db['records'])} records valid, no duplicates")


def cmd_merge(fragment_path):
    db = load_db()
    fields = db["meta"]["record_fields"]
    with open(fragment_path, encoding="utf-8") as f:
        frag = json.load(f)
    new_recs = frag["records"] if isinstance(frag, dict) else frag
    errors = []
    for i, rec in enumerate(new_recs):
        validate_record(rec, fields, errors, f"fragment[{i}] {rec.get('product_code')}")
    if errors:
        print(f"REJECTED: fragment has {len(errors)} error(s)")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    index = {(r["manufacturer"].lower(), r["product_code"].lower()): i
             for i, r in enumerate(db["records"])}
    added, updated = 0, 0
    for rec in new_recs:
        key = (rec["manufacturer"].lower(), rec["product_code"].lower())
        if key in index:
            existing = db["records"][index[key]]
            for f, v in rec.items():
                if v and (not existing.get(f)):
                    existing[f] = v
            if rec.get("data_status") == "verified":
                existing["data_status"] = "verified"
                existing["last_verified"] = rec.get("last_verified", existing.get("last_verified", ""))
            for lf in ("sources", "industries", "certifications"):
                if rec.get(lf):
                    merged = list(dict.fromkeys(existing.get(lf, []) + rec[lf]))
                    existing[lf] = merged
            updated += 1
        else:
            index[key] = len(db["records"])
            db["records"].append(rec)
            added += 1
    save_db(db)
    print(f"merged {fragment_path}: added={added} updated={updated} total={len(db['records'])}")


def cmd_csv():
    db = load_db()
    fields = db["meta"]["record_fields"] + ["tds_local_path"]
    with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(fields)
        for rec in db["records"]:
            row = []
            for fld in fields:
                v = rec.get(fld, "")
                if isinstance(v, list):
                    v = " | ".join(v)
                row.append(v)
            w.writerow(row)
    print(f"wrote {CSV_PATH.name}: {len(db['records'])} rows")


def cmd_stats():
    db = load_db()
    by_mfr = {}
    for rec in db["records"]:
        m = rec["manufacturer"]
        by_mfr.setdefault(m, {"total": 0, "verified": 0})
        by_mfr[m]["total"] += 1
        if rec.get("data_status") == "verified":
            by_mfr[m]["verified"] += 1
    for m, s in sorted(by_mfr.items()):
        print(f"{m:16s} total={s['total']:4d} verified={s['verified']:4d}")
    print(f"{'ALL':16s} total={len(db['records']):4d}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "validate"
    if cmd == "validate":
        cmd_validate()
    elif cmd == "merge":
        cmd_merge(sys.argv[2])
    elif cmd == "csv":
        cmd_csv()
    elif cmd == "stats":
        cmd_stats()
    else:
        print(__doc__)
        sys.exit(1)
