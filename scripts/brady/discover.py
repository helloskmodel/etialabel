#!/usr/bin/env python3
"""Discovery crawl for Brady label materials (B-numbers).

Fetches /labels category pages (application + property trees) with Playwright,
extracts the "Material Number" facet values, /tdsdetails links, and any
description phrases naming a B-number. Writes raw HTML per page to SCRATCH and
an intermediate JSON with per-page results. Discovery only — no records.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch import fetch_many

SCRATCH = "/tmp/claude-0/-home-user-etialabel/cf7292ce-51a7-5873-a634-9c83070304cf/scratchpad/brady"
BASE = "https://www.bradyid.com"

# slug -> (url_path, kind) ; kind: application | property | guide | hub
CATEGORIES = {
    # by application (paths as actually linked from /labels page)
    "barcode-labels":       ("/barcode-labels", "application"),
    "circuit-board":        ("/labels/circuit-board", "application"),
    "datacom":              ("/labels/datacom", "application"),
    "electrical":           ("/labels/electrical", "application"),
    "hazmat-labels":        ("/hazmat-labels", "application"),
    "inspection-inventory": ("/labels/inspection-inventory", "application"),
    "laboratory":           ("/labels/laboratory", "application"),
    "numbers-letters":      ("/labels/numbers-letters", "application"),
    "pipe-markers":         ("/pipe-markers", "application"),
    "rating-name-plate":    ("/labels/rating-name-plate", "application"),
    "safety-labels":        ("/safety-labels", "application"),
    "wire-cable-labels":    ("/wire-cable-labels", "application"),
    # by property
    "aggressive-adhesive":  ("/labels/aggressive-adhesive", "property"),
    "harsh-environment":    ("/labels/harsh-environment", "property"),
    "heat-resistant":       ("/labels/heat-resistant", "property"),
    "laser-markable":       ("/labels/laser/markable", "property"),
    "low-temperature":      ("/labels/low-temperature", "property"),
    "magnetic":             ("/labels/magnetic", "property"),
    "metallic":             ("/labels/metallic", "property"),
    "permanent-adhesive":   ("/labels/permanent-adhesive", "property"),
    "removable":            ("/labels/removable", "property"),
    "repositionable":       ("/labels/repositionable", "property"),
    "self-laminating":      ("/labels/self-laminating", "property"),
    "washdown-resistant":   ("/labels/washdown-resistant", "property"),
    # hubs / guide (enumeration sources, not category tags)
    "by-application":       ("/labels/by-application", "hub"),
    "by-property":          ("/labels/by-property", "hub"),
    "label-material-guide": ("/labels/label-material-guide", "guide"),
}

B_RE = re.compile(r"\bB-\d{2,4}[A-Z]?\b")
# facet checkbox: id="MaterialNumberB-423"
FACET_RE = re.compile(r'id="MaterialNumber(B-[0-9A-Z/-]+?)(?:ClickTarget)?"')
TDS_RE = re.compile(r'href="(/tdsdetails\?id=[^"]+)"')
# description phrase ending in (B-xxx): keep up to 140 chars before it
DESC_RE = re.compile(r'>([^<>]{15,180}?\((B-\d{2,4}[A-Z]?)\)[^<>]{0,40})<')


def parse_page(html):
    facet = set()
    for m in FACET_RE.finditer(html):
        for code in m.group(1).split("/"):
            code = code.strip()
            if B_RE.fullmatch(code):
                facet.add(code)
    tds = sorted(set(TDS_RE.findall(html)))
    descs = {}
    for m in DESC_RE.finditer(html):
        text, code = m.group(1).strip(), m.group(2)
        text = re.sub(r"\s+", " ", text)
        descs.setdefault(code, set()).add(text)
    all_b = sorted(set(B_RE.findall(html)))
    return {
        "facet_codes": sorted(facet),
        "tds_links": tds,
        "descriptions": {k: sorted(v) for k, v in descs.items()},
        "all_b_mentions": all_b,
    }


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    jobs = []
    for slug, (path, kind) in CATEGORIES.items():
        out = os.path.join(SCRATCH, f"cat-{slug}.html")
        if os.path.exists(out) and os.path.getsize(out) > 100000:
            continue  # already fetched this run
        jobs.append((BASE + path, out))
    if jobs:
        fetch_many(jobs, delay=2.0)  # 2s politeness delay between page loads

    results = {}
    for slug, (path, kind) in CATEGORIES.items():
        out = os.path.join(SCRATCH, f"cat-{slug}.html")
        entry = {"url": BASE + path, "kind": kind, "fetched": False}
        if os.path.exists(out):
            html = open(out).read()
            if len(html) < 5000 or "captcha-delivery.com" in html:
                entry["blocked"] = True
            else:
                entry["fetched"] = True
                entry.update(parse_page(html))
        results[slug] = entry
        n = len(entry.get("facet_codes", []))
        sys.stderr.write(f"{slug}: fetched={entry['fetched']} facet={n}\n")

    with open(os.path.join(SCRATCH, "pages.json"), "w") as f:
        json.dump(results, f, indent=1)
    print("wrote", os.path.join(SCRATCH, "pages.json"))


if __name__ == "__main__":
    main()
