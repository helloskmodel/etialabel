# ETIA Label — Overseas (Google SEO) Site

Static, multi-page industrial specialty-label site for the **overseas English** market
(Google SEO). This is **separate from the domestic Baidu/Chinese site** — do not mix them.

## Three navigation paths (all converge on a Product Detail Page)

| Path | Root | Levels |
|---|---|---|
| **By Industry** | `/industries/` | Industry hub → application leaf → products |
| **By Application** | `/applications/` | Process hub → products |
| **By Base Material** | `/materials/` | Substrate hub → products |

Plus `/products/` (detail pages), `/brands/` (Brady cross-reference), `/technical-resources/`.

## SEO

- English slugs, one flat level per path (≤3 deep), independent `<title>`/meta per page.
- **BreadcrumbList** + **FAQPage** JSON-LD on every hub/leaf/product page.
- `sitemap-index.xml` grouped into core / industries / applications / materials / products / tech-resources.
- `robots.txt` points at the sitemap index. Trailing-slash canonical URLs.

## Catalog (V1.0)

122 parts across **5 brands** — Polyonics (PI electronics), YS Tech (metal/ceramic high-temp),
ETIA (PET/PP/specialty), plus distributed Flexcon and Avery cryo/medical stock.
8 industries × process leaves, 8 applications, 5 materials.

> **Coverage note:** EV & Battery and Outdoor Equipment leaves have no V1.0 parts yet; those
> pages ship with "engineered-to-spec / request sourcing" content to keep the internal-link mesh
> complete. Populate with real part numbers in V2.

### Rich product landing pages

39 spec-sheet parts (ETIA Feature + Benefit sheet, 8 product series) render **full landing
pages** — Overview, Specifications, Features & Benefits, Applications and FAQ — instead of the
thin spec/FAQ stub. English copy lives in `_build/data/product_details.json`, keyed by model;
regenerate it from source with `python3 _build/build_details_data.py`. Any model that also
appears in the catalog tree keeps its industry / application / material cross-links and Brady
cross-reference.

## Build

```
python3 _build/build_details_data.py   # (re)builds the EN product-detail data
python3 _build/gen_en.py               # regenerates all HTML + sitemaps from _build/data/*.json
```

ETIA is an authorized distributor / converter — specs cite the original manufacturers; the role is supply + service.
