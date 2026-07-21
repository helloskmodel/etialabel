# Sector data format (one format for every sector)

Every industry sector is **one JSON file** in `_build/data/` that follows the shape
below. To publish a new sector:

1. Copy `_sector_template.json`, rename it (e.g. `metal_ceramics_apps.json`).
2. Fill it in (English + Chinese for every text field).
3. Add the filename to `SECTOR_FILES` in `_build/gen_autoapps.py`.
4. Run `python3 _build/build.py && python3 _build/validate.py`.

That one file produces **both**:

- the **sector page** (`sector.path`) — each application shown as **2 keyword cards**:
  **Challenge → Recommendation** (derived automatically from `props`), and
- one **Application Notes article** per application at
  `/application-notes/<application-name>/` — the full write-up
  (Label Purpose · Challenge · Risk of the Wrong Label · Recommended Solution ·
  Material Properties), listed in the sitemap for SEO.

You only write the content once; the keyword cards, the article, the index and the
sitemap entry are all generated.

---

## File shape

```jsonc
{
  "sector": {
    "name_en": "Automotive Label Solutions",
    "name_zh": "汽车标签解决方案",
    "path": "/industries/automotive-label-materials/",   // page URL, must end with /
    "eyebrow_en": "AUTOMOTIVE · LABEL SOLUTIONS",
    "eyebrow_zh": "汽车 · 标签解决方案",
    "subhead_en": "One sentence under the H1 …",
    "subhead_zh": "标题下的一句话 …",
    "intro_en": "One short paragraph above the application tabs …",
    "intro_zh": "应用标签上方的一段话 …",
    "banner": "https://…/hero.png"                        // hero background image (optional)
  },
  "apps": [
    {
      "area_en": "Engine Compartment",                    // grouping label (area/zone)
      "area_zh": "发动机舱",
      "name_en": "Radiator Warning Labels",               // becomes the article slug + tab
      "name_zh": "散热器警示标签",
      "purpose_en": "What this label is for …",           // → article lede (Label Purpose)
      "purpose_zh": "标签用途 …",
      "challenge_en": "Continuous high heat, coolant corrosion, humidity …",  // prose, article
      "challenge_zh": "持续高温环境、冷却液腐蚀、潮湿 …",
      "risk_en": "What goes wrong with the wrong label …",// → Risk of the Wrong Label (article)
      "risk_zh": "用错标签的风险 …",
      "props": ["Heat-Resistant", "Chemical-Resistant", "Humidity-Resistant"],  // SEE VOCAB
      "products": [
        {
          "model": "E-2813",
          "brand": "E-Label",                             // own brand shown on the badge; "Computype" = held/hidden
          "feature_en": "…", "feature_zh": "…",
          "benefit_en": "…", "benefit_zh": "…",
          "spec_en": "…",    "spec_zh": "…"
        }
      ]
    }
  ]
}
```

### Notes
- **Every text field is bilingual** (`_en` + `_zh`). Chinese uses **no full stop (。)** —
  the build strips them automatically, so don't worry about trailing 。.
- The **sector page shows only** the Challenge → Recommendation keyword cards.
  Purpose / Risk / full product specs appear **only** in the Application Notes article.
- `props` drives both cards: each keyword renders as a green **Recommendation** chip and
  auto-pairs to its orange **Challenge** chip. Order matters (shown left-to-right).

---

## `props` — the controlled vocabulary (use these exact keywords)

Pick from this list so the Challenge ↔ Recommendation chips always pair correctly and the
Chinese is translated once, site-wide. (Left = what you put in `props`; right = the
Challenge chip it auto-generates.)

| `props` keyword (Recommendation) | 中文 | auto Challenge chip | 中文 |
|---|---|---|---|
| `Heat-Resistant` | 耐热 | High Temperature | 高温 |
| `High-Temperature-Resistant` | 耐高温 | High Temperature | 高温 |
| `Chemical-Resistant` | 耐化学 | Chemicals | 化学品 |
| `Oil-Resistant` | 耐油污 | Oil / Fluids | 油污 |
| `Corrosion-Resistant` | 耐腐蚀 | Corrosion | 腐蚀 |
| `Humidity-Resistant` | 耐潮湿 | Moisture | 潮湿 |
| `Water-Resistant` | 耐水 | Water | 水 |
| `Waterproof` | 防水 | Water / Rain Exposure | 淋雨/浸水 |
| `UV-Resistant` | 耐紫外 | UV Exposure | 紫外线 |
| `Weather-Resistant` | 耐候 | Weather / Outdoor | 户外候变 |
| `Temperature-Resistant` | 耐温变 | Temperature Cycling | 温度变化 |
| `Abrasion-Resistant` | 耐磨 | Abrasion | 磨损 |
| `Tamper-Evident` | 防拆 | Tamper Risk | 防拆需求 |
| `Laser-Markable` | 激光打标 | Permanent Marking | 永久标识 |
| `Flexible` | 柔性 | Flexing / Bending | 弯曲变形 |

Need a keyword that isn't here? Add it once to `PROP_ZH` and `PROP_CHALLENGE` in
`_build/gen_autoapps.py` and it's available to every sector.
