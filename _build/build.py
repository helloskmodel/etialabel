#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Single build entrypoint. HEATPROOF builds the shared shell (home, products hub,
core/legal, nav/footer). Today only ONE sector is live — Automotive (unified
format) — plus its Application Notes. All other sectors (Metal & Ceramics /
steel and the HEATPROOF heat-content, PCB/Apex) are retired pending re-supply in
the unified sector format. Finally strips Chinese full-stops and verifies."""
import sys, os
BUILD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BUILD)
import gen_heatproof as hp
import gen_autoapps as autoapps
import gen_pcb as pcb
import gen_industry as industry
import gen_apex as apex
import gen_e2712 as e2712
import gen_polyimide as polyimide
import gen_environments as environments
import gen_appnote_full as appnote_full
import gen_appnotes as appnotes

hp.main()        # clean + build shell: home, products hub, core/legal, nav/footer, base vercel.json
# NB: gen_autoapps is imported (its PROP/PROP_ZH vocab is reused by gen_appnotes) but no
# longer builds a landing — the industry hubs below own the automotive + PCB pages.
industry.main()  # Industry landing hubs — shared layout (owns automotive + PCB landing pages, EN+ZH)
import gen_product  # product Landing pages (part 4)
gen_product.main()
import render_industry  # v2 data-driven override: rebuilds Wire & Cable with the new design + real content
render_industry.main()
apex.main()      # Apex Series — next-gen PCB polyimide (owns /products/apex-series/)
e2712.main()     # E-2712 — dual anti-static polyester, the E-Label ESD pick (owns /products/e-2712/)
polyimide.main() # Polyimide Label Materials — technical page + full product line (owns /products/polyimide-label-materials/)
environments.main() # Labels by Environment — heat / cold / chemical / abrasion hub (owns /environments/)
appnote_full.main() # Full engineering Application Notes per Standard V1.0 (hero + 7 sections)
import gen_news
gen_news.main()  # News / Insights hub + article pages
appnotes.main()  # Application Notes — simple 4-section notes + hub (lists featured full notes too)
import gen_appnote_v2  # data-driven 4-language Application Notes + hub override (owns /application-notes/)
gen_appnote_v2.main()

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

def optimize_cos_images():
    """Append COS image-processing (数据万象/imageMogr2) params to every COS image
    URL so images are served as compressed WebP. WebP + quality only — no resize —
    so dimensions never change and small images are never upscaled. Requires image
    processing enabled on the bucket."""
    import re
    root_dir = os.path.dirname(BUILD)
    skip = {"_build", "_docs", ".git", "node_modules", "scratchpad"}
    HOST = "eitalabel-1303055923.cos.ap-singapore.myqcloud.com"
    PARAM = "?imageMogr2/format/webp/quality/80"
    # match a COS URL WITH a path (so the bare preconnect host is left untouched)
    pat = re.compile(r"https://" + re.escape(HOST) + r"/[^\s\"'()<>]+")
    def repl(m):
        u = m.group(0)
        # leave the logo untouched (tiny, and it has no onerror fallback)
        if "?" in u or "/LOGO/" in u.upper():
            return u
        return u + PARAM
    n = 0
    for r, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in skip and not d.startswith(".")]
        for f in files:
            if not f.endswith(".html"):
                continue
            p = os.path.join(r, f)
            s = open(p, encoding="utf-8").read()
            new = pat.sub(repl, s)
            if new != s:
                open(p, "w", encoding="utf-8").write(new); n += 1
    print("COS image optimize (webp/q80): processed", n, "pages")

strip_cn_fullstops()
# optimize_cos_images() DISABLED: appending ?imageMogr2/... broke images when the
# bucket's image processing wasn't active. Re-enable only once WebP output is
# confirmed working on the COS bucket.
print("BUILD COMPLETE — total EN canonical URLs:", len(hp.ALL_URLS))
