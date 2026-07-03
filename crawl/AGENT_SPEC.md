# Crawl Agent Specification — Label Material Database

You are extracting label material records from ONE manufacturer's website.

## Hard rules (violations make your output unusable)
1. **NEVER invent product codes, specs, temperatures, or certifications.** A value goes
   into a record ONLY if you actually saw it in content you fetched during this run
   (product page HTML, TDS PDF, category listing). If a spec is not on the page, leave
   the field as an empty string `""` (or empty list for list fields). Do NOT fill gaps
   from memory/training data.
2. `data_status` = `"verified"` only when you fetched the product page or TDS and it
   confirms the product code. Anything you could not confirm goes in the unverified
   list, NOT in records.
3. `tds_url` must be the actual TDS PDF URL, or the exact product page URL that
   contains/links the TDS. It must be a URL you saw in fetched content — never guessed.
4. Rate-limit: sleep 1 second between HTTP requests. Use curl with
   `-A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36" --compressed -L --max-time 30`.
   If a URL returns 403/429 or a bot-block page, log it and skip — do not hammer.
5. Dedupe within your own output on `product_code`. One product appearing in multiple
   categories = ONE record whose `application_en`/`industries` cover all of them.

## Record schema — every record must have EXACTLY these 22 fields
```json
{
  "manufacturer": "",             // exact brand name, e.g. "Polyonics"
  "product_code": "",             // e.g. "XF-781" — as printed on site
  "name_en": "",                  // product title from page
  "name_zh": "",                  // your Chinese translation of name_en
  "facestock_en": "",             // material/facestock spec + thickness as printed (e.g. "2.0 mil white polyimide")
  "facestock_zh": "",
  "adhesive_en": "",              // adhesive spec as printed (e.g. "high-temperature silicone"); "None (tie-on tag)" for tags
  "adhesive_zh": "",
  "application_en": "",           // what it is used for (from application/industry text)
  "application_zh": "",
  "industries": [],               // list of industry tags, e.g. ["Electronics", "Automotive"]
  "features_en": [],              // what the product IS (marketing bullets about properties)
  "features_zh": [],
  "benefits_en": [],              // what the user GAINS (split from features)
  "benefits_zh": [],
  "temperature_performance": "",  // temp specs, units exactly as printed (e.g. "up to 500°F (260°C) for 30 min")
  "certifications": [],           // e.g. ["UL 969", "cUL", "RoHS", "BS5609", "ASTM E595"]
  "tds_url": "",
  "catalog_url": "",              // category/application page you found it on
  "data_status": "verified",
  "sources": [],                  // every URL you used to build this record
  "last_verified": "2026-07-03"
}
```
All non-list fields are strings. All list fields are JSON arrays of strings.

## Taxonomy — map free-text specs to these terms where possible (keep the printed
detail too, e.g. "2 mil gloss white Polyester (PET)")
- Facestock: Polyimide; Polyester (PET); Polyethylene naphthalate (PEN); Polypropylene (PP);
  Polyethylene (PE); Polyolefin; Vinyl (PVC); Polyvinyl fluoride (PVF); Polycarbonate;
  Paper; Thermal paper; Aluminum foil; Metalized polyester; Ceramic; Glass cloth;
  Nylon cloth; Polyester cloth; Vinyl cloth; Tamper-evident / destructible film;
  Tag stock (no adhesive); Static-dissipative film
- Adhesive: Permanent acrylic; High-tack permanent acrylic; Aggressive acrylic;
  Removable acrylic; Repositionable acrylic; Modified acrylic; Silicone; Rubber-based;
  Emulsion acrylic; Solvent acrylic; Low-temperature acrylic; High-temperature acrylic;
  Low-outgassing acrylic; None (tie-on tag); None (overlaminate)

## Chinese translations
Translate name/facestock/adhesive/application/features/benefits into natural
simplified Chinese for the `_zh` fields. Keep product codes, polymer abbreviations
(PET/PP/PI), and certification names untranslated inside the Chinese text.

## Features vs benefits split
- features_en: intrinsic properties — "halogen-free", "1-mil polyimide film", "matte white topcoat"
- benefits_en: user outcomes — "survives wave soldering without discoloration", "reduces relabeling cost"

## Output files (write with the Write tool)
1. `crawl/<mfr_slug>/records.json` — `{"records": [ ... ]}`
2. `crawl/<mfr_slug>/unverified.json` — `{"unverified": [{"product_code_or_name": "", "reason": "", "url": ""}], "blocked_urls": ["..."]}`

## Final response format (plain text, no file dumps)
- counts: records written, unverified, blocked URLs
- how you enumerated products (which listing pages/APIs)
- any gap between site's stated total and your count, with explanation
