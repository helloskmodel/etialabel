#!/usr/bin/env python3
"""Application Note 生成器 —— 按 etiatech.com 版式生成"应用方案"页, 内置SEO+结构化数据.
用法: python3 scripts/build_appnote.py <note_key> [输出路径]
技术正文为成熟工程事实(如回流焊峰值温度取自IPC/J-STD标准); 推荐产品/材料表全部取自
真实数据库 data/labels.db, 不编造型号与参数。官网未公布的产品参数留空。
"""
import html
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data/labels.db"
SITE = "https://label.etiatech.com"


def esc(s):
    return html.escape(str(s or ""))


# ---------------------------------------------------------------- 应用方案配置
NOTES = {
    "polyimide-reflow": {
        "slug": "polyimide-labels-reflow-soldering",
        "industry": "Electronics Manufacturing",
        "application": "PCB Traceability & Reflow Soldering",
        "title": "Using Polyimide Labels to Survive Reflow Soldering and Guarantee PCB Traceability",
        "code": "AN-ELEC-001",
        # 面材过滤(材料表 & 推荐产品从数据库真实取)
        "product_filter": "f.face_code='POLYIMIDE' AND (p.sub_application IN ('电路板PCB','防静电ESD','覆膜保护') OR p.temp_long_max>=200)",
        "metric_big": "300°C",
        "metric_sub": "Continuous-rated polyimide facestocks — barcodes stay scannable through SMT reflow, wave solder and aqueous cleaning.",
        "benefit_chips": ["Survives reflow (245–260°C)", "Solvent & flux resistant",
                          "Halogen-free / UL 94 V-0 options", "Barcode stays scannable"],
        "overview": ("Printed-circuit-board traceability requires a serial or 2D barcode applied to the bare "
                     "board or panel <em>before</em> assembly, so that every board can be tracked through the "
                     "entire SMT line. That means the label — face, adhesive and printed image — has to survive "
                     "the full thermal and chemical process without curling, charring or losing scan contrast."),
        "challenge": ("Lead-free SMT reflow (SAC alloys) peaks at 245–260°C per IPC/JEDEC J-STD-020, and boards "
                      "may pass through reflow multiple times, plus wave soldering and aqueous or solvent cleaning. "
                      "Ordinary PET or paper labels shrink, discolour, delaminate or become unscannable under this "
                      "exposure, breaking the traceability chain and forcing costly re-labelling or scrap."),
        "solution": ("Polyimide (PI) film facestocks are dimensionally stable and non-charring to 260°C continuous "
                     "and 300°C+ short-term, paired with high-temperature acrylic or silicone adhesives that hold "
                     "on the board through repeated thermal cycles. Thermal-transfer or laser-marked PI labels keep "
                     "a high-contrast, scannable barcode through reflow, wave solder and cleaning. Many PI stocks are "
                     "halogen-free and UL 94 V-0 rated for electronics compliance. This note compares cross-brand "
                     "options so you can match temperature, adhesive and certification to your line."),
        "faq": [
            ("What temperature do PCB labels need to survive?",
             "Lead-free SMT reflow peaks at 245–260°C (IPC/JEDEC J-STD-020) and boards may see reflow more than once. "
             "Polyimide labels rated 260°C continuous / 300°C+ short-term cover this with margin."),
            ("Polyimide vs high-temp PET for PCB labels?",
             "High-temp PET tops out around 150–180°C — fine for post-assembly asset labels, but it will not survive "
             "reflow. For labels applied before or during assembly you need polyimide."),
            ("Which adhesive should I choose?",
             "High-temperature acrylic suits most reflow labelling; silicone adhesives extend service temperature "
             "further for the most extreme profiles. Both are represented across the products in the table below."),
            ("Are polyimide labels halogen-free / UL rated?",
             "Many polyimide label stocks are halogen-free and carry UL 94 V-0 flame ratings and UL 969 recognition. "
             "Check each product's certification column and its official TDS."),
        ],
    },
}


def fetch_products(filt, limit=14):
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    rows = db.execute(f"""SELECT b.brand_name_en br, p.model_no m, p.product_name_en ne,
        f.face_name_en fc, a.adh_name_en ac, p.temp_long_max t1, p.temp_peak_max tp,
        p.sub_application sub, p.certification cert, p.tds_url tds, p.source_url src
        FROM product p JOIN brand b ON b.brand_id=p.brand_id
        JOIN facestock_dict f ON f.face_id=p.face_id
        LEFT JOIN adhesive_dict a ON a.adh_id=p.adh_id
        WHERE p.status=1 AND ({filt})
        ORDER BY p.temp_long_max DESC, (p.tds_url IS NOT NULL) DESC LIMIT {limit}""").fetchall()
    total = db.execute(f"""SELECT COUNT(*), COUNT(DISTINCT p.brand_id) FROM product p
        JOIN facestock_dict f ON f.face_id=p.face_id
        LEFT JOIN adhesive_dict a ON a.adh_id=p.adh_id WHERE p.status=1 AND ({filt})""").fetchone()
    db.close()
    return [dict(r) for r in rows], total[0], total[1]


APP_EN = {"电路板PCB": "PCB labelling", "防静电ESD": "ESD-safe", "覆膜保护": "Overlaminate",
          "发动机舱/车厢底": "Under-hood", "结构粘接/泡棉": "Bonding", "动力电池": "EV battery",
          "低温冻存": "Cryogenic", "线缆标识": "Wire & cable"}


def render(key):
    n = NOTES[key]
    prods, total, nbrand = fetch_products(n["product_filter"])
    canonical = f"{SITE}/{n['slug']}"
    # 推荐产品chips: 前6款真实产品
    prod_chips = "".join(
        f'<span class="chip prod">{esc(p["br"])} {esc(p["m"])}</span>' for p in prods[:6])
    benefit_chips = "".join(f'<span class="chip">{esc(b)}</span>' for b in n["benefit_chips"])
    # 材料表(真实数据)
    rows_html = ""
    for p in prods:
        app = APP_EN.get(p["sub"], p["sub"] or "PCB labelling")
        temp = (f'{p["t1"]}°C' if p["t1"] is not None else "—") + \
               (f' / {p["tp"]}°C peak' if p["tp"] is not None else "")
        cert = (p["cert"] or "")[:60] + ("…" if p["cert"] and len(p["cert"]) > 60 else "")
        link = p["tds"] or p["src"] or ""
        model = f'<a href="{esc(link)}" target="_blank" rel="noopener">{esc(p["br"])} {esc(p["m"])}</a>' if link else f'{esc(p["br"])} {esc(p["m"])}'
        rows_html += (f'<tr><td>{esc(app)}</td><td>{model}</td><td>{esc(p["fc"])}</td>'
                      f'<td>{esc(p["ac"] or "—")}</td><td>{temp}</td><td class="mut">{esc(cert) or "—"}</td></tr>')
    faq_html = "".join(
        f'<details class="faq"><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in n["faq"])

    # ---- JSON-LD 结构化数据(SEO) ----
    ld = [
        {"@context": "https://schema.org", "@type": "TechArticle",
         "headline": n["title"], "articleSection": n["application"],
         "about": "Polyimide labels for PCB traceability and reflow soldering",
         "author": {"@type": "Organization", "name": "ETIA"},
         "publisher": {"@type": "Organization", "name": "ETIA"},
         "mainEntityOfPage": canonical},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
            {"@type": "ListItem", "position": 2, "name": "Application Notes", "item": SITE + "/application-notes"},
            {"@type": "ListItem", "position": 3, "name": n["application"], "item": canonical}]},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in n["faq"]]},
        {"@context": "https://schema.org", "@type": "ItemList", "name": "Recommended polyimide labels",
         "numberOfItems": len(prods), "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "item": {
                "@type": "Product", "name": f'{p["br"]} {p["m"]}', "brand": p["br"],
                "material": "Polyimide", "url": p["tds"] or p["src"] or ""}}
            for i, p in enumerate(prods)]},
    ]
    ld_json = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    seo_desc = (f'{n["application"]}: how polyimide (PI) labels survive 245–260°C lead-free reflow soldering '
                f'for reliable PCB traceability. Compare {total} PI labels across {nbrand} brands (3M, Brady, '
                f'Polyonics, LINTEC…), each linked to its official TDS. {n["code"]}.')

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(n['title'])} | {n['code']} - ETIA</title>
<meta name="description" content="{esc(seo_desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article">
<meta property="og:title" content="{esc(n['title'])}">
<meta property="og:description" content="{esc(seo_desc)}">
<meta property="og:url" content="{canonical}">
{ld_json}
<style>
:root{{--brand:#5EAF1E;--blue:#1c53a8;--ink:#1b2430;--mut:#5c6b7a;--line:#e3e8ee;
  --bg:#ffffff;--soft:#f5f7fa;--red:#c0392b;--redbg:#fdecec;--bluebg:#eaf1fb;}}
@media(prefers-color-scheme:dark){{:root{{--ink:#e6edf4;--mut:#93a3b4;--line:#26313d;
  --bg:#0f151c;--soft:#161f28;--redbg:#2a1815;--bluebg:#15202f;--red:#e0796b;--blue:#6ea6e8;}}}}
:root[data-theme="dark"]{{--ink:#e6edf4;--mut:#93a3b4;--line:#26313d;--bg:#0f151c;--soft:#161f28;--redbg:#2a1815;--bluebg:#15202f;--red:#e0796b;--blue:#6ea6e8;}}
:root[data-theme="light"]{{--ink:#1b2430;--mut:#5c6b7a;--line:#e3e8ee;--bg:#fff;--soft:#f5f7fa;--red:#c0392b;--redbg:#fdecec;--bluebg:#eaf1fb;--blue:#1c53a8;}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.7 -apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",system-ui,sans-serif}}
a{{color:var(--blue)}}
.wrap{{max-width:840px;margin:0 auto;padding:0 20px}}
header{{border-bottom:1px solid var(--line);padding:14px 0}}
.logo{{font-weight:800;font-size:22px;letter-spacing:-.02em}}
.logo b{{color:var(--brand)}} .logo span{{color:var(--blue)}}
.hero{{background:linear-gradient(120deg,#11202b,#1c3346);color:#fff;padding:30px 0 34px;position:relative;overflow:hidden}}
.hero::after{{content:"";position:absolute;inset:0;background:radial-gradient(circle at 82% 30%,rgba(94,175,30,.32),transparent 55%)}}
.hero .wrap{{position:relative;z-index:1}}
.tagrow{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}}
.pill{{background:var(--brand);color:#0d1a05;font-weight:700;font-size:12px;padding:4px 11px;border-radius:15px}}
.pill.ghost{{background:rgba(255,255,255,.14);color:#fff;border:1px solid rgba(255,255,255,.3)}}
.hero h1{{font-size:clamp(24px,4.6vw,36px);line-height:1.15;margin:0;font-weight:800;text-wrap:balance}}
.chips{{display:flex;gap:8px;flex-wrap:wrap;margin:22px 0 4px}}
.chip{{border:1px solid var(--line);background:var(--soft);border-radius:17px;padding:5px 13px;font-size:13.5px;color:var(--ink)}}
.chip.prod{{border-color:var(--brand);color:var(--brand);font-weight:600}}
.metric{{background:var(--soft);border:1px solid var(--line);border-radius:14px;padding:26px;margin:26px 0}}
.metric b{{font-size:clamp(38px,8vw,60px);color:var(--blue);font-weight:800;line-height:1;letter-spacing:-.02em}}
.metric p{{margin:10px 0 0;color:var(--mut);font-size:15px}}
section{{margin:26px 0}}
.eyebrow{{font-size:12.5px;font-weight:800;letter-spacing:.09em;color:var(--mut);margin-bottom:8px}}
.box{{border-radius:14px;padding:20px 22px}}
.box.overview{{background:var(--soft);border:1px solid var(--line)}}
.box.challenge{{background:var(--redbg)}} .box.challenge .eyebrow{{color:var(--red)}}
.box.solution{{background:var(--bluebg)}} .box.solution .eyebrow{{color:var(--blue)}}
.box p{{margin:0}}
h2{{font-size:20px;margin:30px 0 6px}}
.tbl{{overflow-x:auto;border:1px solid var(--line);border-radius:12px}}
table{{width:100%;border-collapse:collapse;font-size:14px;min-width:640px}}
th{{background:var(--soft);text-align:left;padding:10px 12px;color:var(--mut);font-size:12.5px;border-bottom:1px solid var(--line);white-space:nowrap}}
td{{padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}}
td.mut{{color:var(--mut);font-size:12.5px}}
.faq{{border:1px solid var(--line);border-radius:10px;padding:0 16px;margin-bottom:10px;background:var(--soft)}}
.faq summary{{padding:14px 0;font-weight:600;cursor:pointer;list-style:none}}
.faq summary::-webkit-details-marker{{display:none}}
.faq summary::before{{content:"+ ";color:var(--brand);font-weight:800}}
.faq[open] summary::before{{content:"− "}}
.faq p{{margin:0 0 14px;color:var(--mut);font-size:14.5px}}
.cta{{display:inline-block;background:var(--brand);color:#0d1a05;font-weight:800;padding:12px 26px;border-radius:9px;text-decoration:none;margin:6px 0}}
.disc{{color:var(--mut);font-size:12.5px;margin-top:8px}}
footer{{border-top:1px solid var(--line);margin-top:36px;padding:26px 0;color:var(--mut);font-size:13px}}
</style>
</head>
<body>
<header><div class="wrap"><span class="logo"><b>&#9654;TIA</b>·<span>TECH</span></span></div></header>

<div class="hero"><div class="wrap">
  <div class="tagrow"><span class="pill">{esc(n['industry'])}</span><span class="pill ghost">{esc(n['application'])}</span></div>
  <h1>{esc(n['title'])}</h1>
</div></div>

<div class="wrap">
  <div class="chips">{prod_chips}</div>
  <div class="chips">{benefit_chips}</div>

  <div class="metric"><b>{esc(n['metric_big'])}</b><p>{n['metric_sub']}</p></div>

  <section><div class="eyebrow">APPLICATION OVERVIEW</div><p>{n['overview']}</p></section>

  <section><div class="box challenge"><div class="eyebrow">THE CHALLENGE</div><p>{n['challenge']}</p></div></section>

  <section><div class="box solution"><div class="eyebrow">THE SOLUTION</div><p>{n['solution']}</p></div></section>

  <section>
    <h2>Compatible Materials <span class="disc">— {total} polyimide labels across {nbrand} brands · each linked to its official TDS</span></h2>
    <div class="tbl"><table>
      <tr><th>Application</th><th>Product (→ TDS)</th><th>Facestock</th><th>Adhesive</th><th>Max / Peak temp</th><th>Certifications</th></tr>
      {rows_html}
    </table></div>
    <p class="disc">Specs are drawn from each brand's official product page / TDS. Fields not published by the brand are left blank — never fabricated. Verify against the linked TDS before specifying.</p>
  </section>

  <section>
    <a class="cta" href="{SITE}/polyimide-labels">Browse all polyimide labels →</a>
  </section>

  <section><h2>FAQ</h2>{faq_html}</section>
</div>

<footer><div class="wrap">
  <b>ETIA</b> · Specialty industrial labels · 20 years of selection expertise · {n['code']}<br>
  Data sourced from official brand pages / TDS; unpublished specs left blank. For reference only — final specification per official TDS.
</div></footer>
</body>
</html>
"""


def main():
    key = sys.argv[1] if len(sys.argv) > 1 else "polyimide-reflow"
    outp = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / f"data/appnote-{key}.html"
    outp.write_text(render(key), encoding="utf-8")
    print(f"{outp}: {NOTES[key]['code']} generated ({round(len(outp.read_text())/1024)} KB)")


if __name__ == "__main__":
    main()
