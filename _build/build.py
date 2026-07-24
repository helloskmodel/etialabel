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
import gen_casestudies as casestudies
import gen_appnote_full as appnote_full
import gen_appnotes as appnotes

hp.main()        # clean + build shell: home, products hub, core/legal, nav/footer, base vercel.json
# NB: gen_autoapps is imported (its PROP/PROP_ZH vocab is reused by gen_appnotes) but no
# longer builds a landing — the industry hubs below own the automotive + PCB pages.
industry.main()  # Industry landing hubs — shared layout (owns automotive + PCB landing pages, EN+ZH)
import render_industry  # v2 data-driven override: rebuilds Wire & Cable with the new design + real content
render_industry.main()
apex.main()      # Apex Series — next-gen PCB polyimide (owns /products/apex-series/)
e2712.main()     # E-2712 — dual anti-static polyester, the E-Label ESD pick (owns /products/e-2712/)
polyimide.main() # Polyimide Label Materials — technical page + full product line (owns /products/polyimide-label-materials/)
environments.main() # Labels by Environment — heat / cold / chemical / abrasion hub (owns /environments/)
casestudies.main()  # Case Studies — hub + one big landing page per case (owns /case-studies/)
appnote_full.main() # Full engineering Application Notes per Standard V1.0 (hero + 7 sections)
appnotes.main()  # Application Notes — simple 4-section notes + hub (lists featured full notes too)

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
