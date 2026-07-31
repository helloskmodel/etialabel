# ETIA Label website — project brain (read this first)

Static, 4-language marketing site for **ETIA-TECH** industrial specialty labels.
Live at **www.etialabel.com** (Vercel serves the committed HTML). Python generators
in `_build/` produce the HTML that is committed to the repo root.

## Languages
Four languages, URL-prefixed: EN `/`, ZH `/cn/`, VN `/vn/`, TH `/th/`.
Every user-facing string must exist in all four (translation is allowed; **never
invent product facts** — content comes only from client-supplied briefs/TDS).

## Build
```
cd /home/user/etialabel/_build && python3 build.py
```
- Generators auto-discover data files, so **adding a `data/products/<slug>.json`
  auto-creates** `/products/item/<slug>/` in every language in its `langs` list.
- `build.py` prints a **BANNER AUDIT** — every product must resolve to a banner.
- Never run `build.py` from the repo root; always `cd _build` first.

## Deploy workflow (IMPORTANT — squash-merge conflicts otherwise)
The dev branch is `claude/hello-it32g6`. Because PRs are **squash-merged**, the
branch diverges from `main` after each merge. Deploy each change like this:
1. Save changed source files to a scratch dir.
2. `git checkout -- . && git fetch origin main && git checkout -B claude/hello-it32g6 origin/main`
3. Restore the saved files, then `cd _build && python3 build.py`.
4. `git add -A && git commit` (footer: `Co-Authored-By: Claude ...`), then
   `git push -u origin claude/hello-it32g6 --force-with-lease`.
5. Open a PR to `main`, then **squash-merge** it.

## Key generators (all under `_build/`)
- `gen_heatproof.py` — site shell: `<head>`, nav (`nav_html`, `home_nav`,
  `simple_dropdown` mega-menu), footer, home page (`build_home`), Solutions
  (`build_applications`), Service (`build_service`), Products landing
  (`build_products_landing`), CSS, `write_redirects()` → `vercel.json`.
  Helpers: `P(lang,en,zh,vi,th)` inline 4-lang string; `Lx(lang,path)` localized
  link; `hero_cta(lang)` the single green "Talk to us" banner button.
- `gen_product.py` — **product landing pages** from `data/products/*.json`.
- `render_industry.py` — industry pages from `data/industries/*.json` (`.wchero`).
- `gen_appnote_v2.py` — Application Notes from `data/appnotes/*.json` + hub.
- `gen_news.py` — Insights hub + articles from `data/news.json`.

## Product landing page = one JSON file (`data/products/<slug>.json`)
Schema (every text field is `{"en","zh","vi","th"}`; lists are `{"en":[...],...}`):
```json
{
  "slug": "xxx",
  "source": "client TDS ...",
  "langs": ["en","zh","vi","th"],
  "banner": "",                      // leave "" → uses the industry banner
  "product_img": "https://.../INDUSTRY/....",   // optional feature photo ("" = none)
  "diagram": {                       // optional construction/structure image
    "img": "https://.../....",
    "title": {"en":"Construction", ...},
    "caption": {"en":"", ...},
    "legend": {"en":["D — ...","C — ...","B — ...","A — ..."], ...}
  },
  "title": {...}, "tagline": {...}, "positioning": {...},
  "features": {"en":[...], ...},
  "spec_table": { "headers": {"en":[...], ...},
                  "rows": [ {"cells": ["PLAIN", {"en":"...", ...}]} ],
                  "notes": {"en":[...], ...} },
  "applications": {"en":[...], ...},
  "certifications": {"en":[...], ...}
}
```
Render order: hero → Overview(positioning) → Construction(diagram) → Features →
Specifications(spec_table) → Applications → Certifications → email CTA.
Spec-table cells may be plain strings (numbers/units/model codes) or `{lang}` dicts.
Missing vi/th fields fall back to English (not Chinese).

### TDS → landing page recipe
1. Read the TDS; extract title, tagline, overview, features, spec table,
   applications, certifications. **Only what the TDS states** — no invented specs.
2. Write EN, then translate to ZH/VN/TH (keep model codes, standards, units as-is).
3. Pick the industry (see banner rule) and add the slug to `PRODUCT_INDUSTRY` in
   `gen_product.py` if not present, so the banner audit passes.
4. Optionally link it from the relevant industry page (`data/industries/*.json`
   → a tier's `products[]`, set `"slug"` + `"landing": true`) and/or feature it
   on the homepage (`data/home_i18n.json` → each lang's `products[]`).
5. Build, verify all 4 languages, deploy.

## Uniform banner rule (no exceptions)
Every product landing page shows its **industry's** banner. In `gen_product.py`:
- `INDUSTRY_BANNERS` maps industry → COS image (pcb/auto/cable/steel/medical/outdoor).
- `PRODUCT_INDUSTRY` maps each product slug → industry.
- `product_industry(d, slug)` resolves it; the build's BANNER AUDIT flags any
  product with no banner. Solution pages in `SOLUTION_SLUGS` keep their own banner.
Current PCB banner: `INDUSTRY/PCB-BANNERNEW.jpg`.

## Conventions / decisions already made
- **Banners** are unified to the home-banner style (`.hbanner`): 320px min-height,
  centered, 40px `var(--sans)` headline, blue gradient overlay, ONE green
  **"Talk to us / 联系我们"** button (`hero_cta`) → `/contact/`.
- **Enquiry email:** `etialabel@etia-tech.com` (regional office emails differ).
- **Nav pillars** (Product / Solutions / Service / Insight) build in all 4 langs.
  The Product nav is a **mega-menu** (industry name + description) and its top
  link goes to `/products/` (a real landing page, no Home redirect).
- **Homepage** Key Products = a single horizontal-scroll row (`acgrid6`); Service
  Commitment = a static 4-card grid (`sc4`), no carousel.
- Favicon: `favicon.ico` / `favicon.png` / `apple-touch-icon.png` at repo root.
- COS image host: `https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com/`.
  Images can't be fetched/verified from the sandbox — trust client-supplied URLs;
  if an image was re-uploaded to the same path, it should just work (avoid `?v=`
  cache-busters — COS returned blank for query-string variants).

## More docs
See `_build/docs/` — `SITE_ARCHITECTURE.md`, `DEPLOY.md`, `PAGES.md`,
`CONTENT.md`, `CONTENT_TEMPLATES.md`.
