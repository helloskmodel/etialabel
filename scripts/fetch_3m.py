#!/usr/bin/env python3
"""Fetch all 3M PDP pages from crawl/3m/discovery.json (rate-limited, 1 req/~1.5s),
extract window.__INITIAL_DATA, and save a compact per-product JSON into
crawl/3m/pages/<stock_number>.json for downstream record composition."""
import json
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "crawl/3m/pages"
PAGES.mkdir(parents=True, exist_ok=True)
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")


def fetch(url):
    r = subprocess.run(
        ["curl", "-s", "--compressed", "-A", UA, "-L", "--max-time", "40", url],
        capture_output=True, text=True)
    return r.stdout


def extract_initial_data(html):
    s = html.find("window.__INITIAL_DATA")
    if s < 0:
        return None
    start = html.index("{", s)
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(html)):
        ch = html[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return json.loads(html[start:i + 1])
    return None


def compact(d, url):
    pd = d.get("productDetails", {})
    out = {
        "url": url,
        "canonical": pd.get("canonical", ""),
        "name": pd.get("name", ""),
        "product_number": pd.get("productNumber", ""),
        "stock_number": pd.get("stockNumber", ""),
        "short_description": pd.get("shortDescription", ""),
        "division": pd.get("divisionName", ""),
        "discontinued": pd.get("discontinued", False),
        "benefits": d.get("benefits", []),
        "attributes": {},
        "tds_pdfs": [],
        "resources": [],
        "breadcrumb": [b.get("name", "") for b in d.get("breadCrumb", [])
                       if isinstance(b, dict)],
    }
    for a in d.get("classificationAttributes", []):
        label = a.get("label", "")
        vals = a.get("values", [])
        if label and vals:
            out["attributes"][label] = vals
    for t in d.get("tds", []) or []:
        u = t.get("originalUrl") or t.get("url") or ""
        if u:
            out["tds_pdfs"].append(u)
    for r in d.get("resources", []) or []:
        out["resources"].append({
            "title": r.get("title", ""),
            "url": r.get("originalUrl") or r.get("url", ""),
            "contentType": r.get("contentType", ""),
        })
    # fallback: any multimedia pdf in raw html handled by caller
    return out


def main():
    disc = json.loads((ROOT / "crawl/3m/discovery.json").read_text())
    products = disc["products"]
    log = open(ROOT / "crawl/3m/fetch_log.txt", "w")
    done = fail = 0
    for i, p in enumerate(products):
        url = p["url"]
        key = p.get("stock_number") or re.sub(r"\W+", "_", url[-24:])
        outfile = PAGES / f"{key}.json"
        if outfile.exists():
            done += 1
            continue
        html = fetch(url)
        try:
            d = extract_initial_data(html)
        except Exception as e:
            d = None
            log.write(f"PARSE_ERR {url} {e}\n")
        if not d:
            fail += 1
            log.write(f"FAIL {url} len={len(html)}\n")
            log.flush()
            time.sleep(1.5)
            continue
        c = compact(d, url)
        c["discovery"] = {"material_number": p.get("material_number", ""),
                          "title": p.get("title", ""),
                          "industries": p.get("industries", [])}
        if not c["tds_pdfs"]:
            for m in re.finditer(r'https://multimedia\.3m\.com/mws/media/[^"\\]+?\.pdf[^"\\]*', html):
                u = m.group(0).replace("&amp;", "&")
                if u not in c["tds_pdfs"]:
                    c["tds_pdfs"].append(u)
        outfile.write_text(json.dumps(c, ensure_ascii=False, indent=1))
        done += 1
        log.write(f"OK {key} {c['product_number']} tds={len(c['tds_pdfs'])}\n")
        log.flush()
        time.sleep(1.5)
    log.write(f"DONE ok={done} fail={fail}\n")
    log.close()
    print(f"done ok={done} fail={fail}")


if __name__ == "__main__":
    main()
