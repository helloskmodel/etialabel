# ETIA Label — Overseas Site (English, SEA-focused)

Static, multi-page industrial specialty-label site for overseas markets (Google SEO),
built English-first with a **multilingual-ready** generator (Chinese / Thai / Vietnamese
layer in later). Fully English output — no Chinese leaks into the rendered pages.

## Positioning

**Your Solution Partner for labels that perform where ordinary ones fail.** ETIA is an
application-first solution partner (not a catalog supplier): sole agent for **Polyonics**
(USA) and **YS Tech** (Japan), plus **FlexCon** and **Computype**, with its own **ETIA**
brand and in-house **die-cutting & slitting** factory. 20 years of experience; performance
envelope from **1300 °C** heat to **−196 °C** cryogenic.

## Three navigation paths (all converge on a Product Detail Page)

| Path | Root | Levels |
|---|---|---|
| **By Industry** | `/industries/` | Industry hub → application leaf → products |
| **By Application** | `/applications/` | Process hub → products |
| **By Base Material** | `/materials/` | Substrate hub → products |

Plus `/products/` (detail pages), `/brands/` (agency matrix + Brady cross-reference),
`/technical-resources/`, and `/about/`.

## SEO / search architecture

- English slugs, flat (≤3 deep), independent `<title>`/meta/canonical per page.
- **BreadcrumbList** + **FAQPage** JSON-LD everywhere; **Product** on detail pages; **Organization** on home.
- **hreflang** (`en` + `x-default`) on every page — extends to zh/th/vi automatically.
- `sitemap-index.xml` grouped into core / industries / applications / materials / products / tech-resources.
- `robots.txt` points at the sitemap index. Trailing-slash canonical URLs.

## Brand & design

- Blue-led palette: deep blue `#143C96` (hero/header/headings), blue `#1A56DB`
  (links/borders/icons); green `#41A62A` reserved for CTA buttons (hover `#358B22`).

## Catalog

101 parts (105 records) — Polyonics (PI electronics), YS Tech (metal/ceramic high-temp),
ETIA (PET/PP/specialty). 8 industries × process leaves, 8 applications, 5 materials.
Chinese `seo` positioning strings are kept in the data as the future `zh` source but never
rendered in English — product copy is derived from material/temperature/application fields.

> **Coverage note:** EV & Battery and Outdoor Equipment leaves have no parts yet; those pages
> ship with "engineered-to-spec / request sourcing" content to keep the internal-link mesh
> complete. Populate with real part numbers later.

## Build

```
python3 _build/gen_en.py   # regenerates all HTML + sitemaps from _build/data/*.json
```

The generator reads `_build/data/{site_tree,cn_products}.json` and writes the site to the
repo root. It is destructive (clears the built dirs first), so edit the JSON or the
generator — never the generated HTML directly.

## Roadmap

- **Contact/inquiry destination** — CTA buttons currently point at `/technical-resources/`;
  add a real contact page (email / phone / WhatsApp) when provided.
- **Languages** — add `zh` / `th` / `vi` under `/<lang>/` (translations to be supplied);
  the generator's `LANGS` / `LANG_PREFIX` / hreflang scaffolding is already in place.
