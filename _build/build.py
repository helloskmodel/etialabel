#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Single build entrypoint. Runs HEATPROOF first (it does the wholesale clean and builds
the shared shell: home, industries, products hub, core/legal stubs), then layers the
Automotive (3M + FLEXcon) section on top without clobbering. Finally verifies."""
import sys, os
BUILD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BUILD)
import gen_heatproof as hp
import gen_automotive as auto
import gen_healthcare as hc
import gen_pcb as pcb
import gen_wirecable as wc
import gen_pi as pi
import gen_featured as fs
import gen_ind_landing as land
import gen_notes as notes
import gen_prodline as prodline
import gen_steel as steel

hp.main()      # clean + build heatproof + home (with harsh-env module) + base vercel.json
auto.main()    # build automotive + automotive sitemap + merge redirects
hc.main()      # build healthcare + healthcare sitemap + merge redirects
pcb.main()     # build electronics & pcb / polyimide categories + sitemap
wc.main()      # build wire & cable + sitemap
pi.main()      # build Polyimide (PI) Material & Application Center + By-Material hub
fs.main()      # build Featured Solutions center + harsh-environment landing pages
land.main()    # industry LANDING pages (brochure layer) — owns /industries/<slug>/ index
notes.main()   # Application Notes (SEO articles) + Electronic Component Labels product landing
prodline.main()  # Reusable product-line landings (Polyonics Apex Series, first instance)
steel.main()     # Metals/Steel sector — application landing + HP-700T product line (owns /industries/steel/)
print("BUILD COMPLETE — total EN canonical URLs:",
      len(hp.ALL_URLS)+len(auto.AUTO_URLS)+len(hc.HC_URLS)+len(pcb.URLS)+len(wc.URLS)+len(pi.URLS)+len(fs.URLS)+len(land.URLS)+len(notes.URLS)+len(prodline.URLS)+len(steel.URLS))
