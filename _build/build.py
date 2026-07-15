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

hp.main()      # clean + build heatproof + heatproof sitemaps + base vercel.json
auto.main()    # build automotive + automotive sitemap + merge redirects
hc.main()      # build healthcare + healthcare sitemap + merge redirects
print("BUILD COMPLETE — total EN canonical URLs:",
      len(hp.ALL_URLS) + len(auto.AUTO_URLS) + len(hc.HC_URLS))
