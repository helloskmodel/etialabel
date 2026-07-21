#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Single build entrypoint. HEATPROOF builds the shared shell (home, products hub,
core/legal, nav/footer). Only the CURRENT sectors are layered on: Metals/Ceramics
(steel) and Automotive (E-Label). Legacy partner-brand sectors and the Circuit
Board & PCB / Apex product-line (to be redefined) have been retired. Finally
strips Chinese full-stops and verifies."""
import sys, os
BUILD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BUILD)
import gen_heatproof as hp
import gen_steel as steel
import gen_autoapps as autoapps
import gen_appnotes as appnotes

hp.main()        # clean + build shell: home, products hub, core/legal, nav/footer, base vercel.json
steel.main()     # Metals & Ceramics sector — Steel/Aluminum/Ceramics + HP-900 line (owns /industries/metal-ceramics/, /industries/steel/ …)
autoapps.main()  # Automotive Label Solutions — E-Label sector (owns /industries/automotive-label-materials/)
appnotes.main()  # Application Notes — one SEO article per application (Purpose/Challenge/Risk/Solution)

# sitemaps + redirects run LAST so every sector's tracked URLs are included
hp.build_sitemaps()
hp.write_redirects()

def strip_cn_fullstops():
    """Client style: Chinese copy uses no full-stop (。). Trailing 。 is dropped; a
    mid-sentence 。 (between clauses) becomes a space so sentences don't run together."""
    root_dir = os.path.dirname(BUILD)
    skip = {"_build", "_docs", ".git", "node_modules", "scratchpad"}
    n = 0
    for r, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in skip and not d.startswith(".")]
        for f in files:
            if not f.endswith(".html"):
                continue
            p = os.path.join(r, f)
            s = open(p, encoding="utf-8").read()
            if "。" not in s:
                continue
            new = s.replace("。<", "<").replace("。 ", " ").replace("。", " ")
            if new != s:
                open(p, "w", encoding="utf-8").write(new); n += 1
    print("Chinese full-stop (。) stripped from", n, "pages")

strip_cn_fullstops()
print("BUILD COMPLETE — total EN canonical URLs:", len(hp.ALL_URLS))
