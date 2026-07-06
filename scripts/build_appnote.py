#!/usr/bin/env python3
"""Application Note 生成器 —— 按 etiatech.com 模板:
标题+⭐HOT / 类别·主推产品 / 引言 / THE CHALLENGE·SOLUTION·BENEFIT /
TECHNOLOGY HIGHLIGHTS / 产品详情落地页 / Recommended Products。内置SEO+结构化数据。
技术正文为成熟工程事实; 主推与推荐产品全部取自真实数据库, 不编造参数。
用法: python3 scripts/build_appnote.py <note_key|all> [输出目录]
"""
import html
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data/labels.db"
SITE = "https://label.etiatech.com"


def esc(s):
    return html.escape(str(s or ""))


# ==================== 聚酰亚胺全部应用方案(内容为成熟工程事实) ====================
NOTES = {
    "pcb-reflow": {
        "code": "AN-ELEC-001", "hot": True,
        "industry": "Electronics Manufacturing", "category": "PCB Traceability & Reflow Soldering",
        "title": "Polyimide Labels for PCB Reflow Traceability",
        "filter": "f.face_code='POLYIMIDE' AND p.sub_application='电路板PCB'",
        "intro": ("PCB traceability requires a serial or 2D barcode applied to the bare board or panel before "
                  "assembly, so every board is tracked through the whole SMT line. The label must survive the "
                  "full thermal and chemical process with a scannable barcode."),
        "challenge": "Keep a barcode scannable through 245–260°C lead-free reflow (often multiple passes), "
                     "wave soldering and aqueous/solvent cleaning — without curl, char or delamination.",
        "solution": "Polyimide (PI) film facestock with a high-temperature acrylic or silicone adhesive, "
                    "thermal-transfer or laser marked, holding to the board through repeated thermal cycles.",
        "benefit": "Uninterrupted board-level traceability with zero re-labelling or scrap, plus halogen-free / "
                   "UL 94 V-0 options for electronics compliance.",
        "highlights": [
            "PI film is dimensionally stable and non-charring to 260°C continuous, 300°C+ short-term",
            "High-holding acrylic (e.g. 3M 350) or silicone adhesives survive repeated reflow cycles",
            "Thermal-transfer or laser marking keeps high scan contrast after reflow and cleaning",
            "Halogen-free, UL 94 V-0 and UL 969 recognised options for electronics compliance"],
        "faq": [("What reflow temperature must PCB labels survive?",
                 "Lead-free SMT reflow peaks at 245–260°C (IPC/JEDEC J-STD-020) and boards may reflow more than once; "
                 "polyimide rated 260°C continuous / 300°C+ short-term covers this with margin."),
                ("Polyimide vs high-temp PET for PCB labels?",
                 "High-temp PET tops out near 150–180°C — fine for post-assembly asset labels but not reflow. Labels "
                 "applied before/during assembly need polyimide.")],
    },
    "esd-safe": {
        "code": "AN-ELEC-002", "hot": False,
        "industry": "Electronics Manufacturing", "category": "ESD-Safe Labeling",
        "title": "Static-Dissipative Polyimide Labels for ESD-Controlled Assembly",
        "filter": "f.face_code='POLYIMIDE' AND p.sub_application='防静电ESD'",
        "intro": ("Inside an ESD-protected area (EPA), every consumable — including labels — must not generate or "
                  "hold a static charge that could damage sensitive semiconductors and assemblies."),
        "challenge": "Ordinary label facestocks and adhesives can tribo-charge on peel and application, risking "
                     "ESD damage to components in an EPA while still needing to survive downstream high-temp process.",
        "solution": "Static-dissipative polyimide labels with a low-charging topcoat and adhesive, keeping surface "
                    "resistivity in the dissipative range while retaining polyimide's high-temperature performance.",
        "benefit": "Protects ESD-sensitive devices and keeps the line ANSI/ESD S20.20 compliant, without giving up "
                   "reflow-grade heat resistance.",
        "highlights": [
            "Static-dissipative topcoat keeps surface resistivity in the ESD-safe range",
            "Low-charging pressure-sensitive adhesive minimises tribo-charging on peel and placement",
            "Polyimide base still withstands SMT reflow temperatures",
            "Tested to ANSI/ESD S20.20 and ESD STM 54 (per product TDS)"],
        "faq": [("Why do labels need to be ESD-safe?",
                 "In an EPA, a charged label can discharge into a sensitive component and cause latent or immediate "
                 "failure. Static-dissipative labels keep charge generation and retention within safe limits.")],
    },
    "ev-battery": {
        "code": "AN-ENGY-001", "hot": True,
        "industry": "New Energy / EV", "category": "EV Battery & Energy Storage",
        "title": "Flame-Retardant Polyimide Labels for EV Battery Cells & Packs",
        "filter": "f.face_code='POLYIMIDE' AND p.sub_application='动力电池'",
        "intro": ("Lithium-ion cells, modules and packs — in EVs and in grid/data-centre energy storage — need "
                  "permanent identification that meets battery flammability and traceability requirements."),
        "challenge": "Battery-pack labels must resist heat, electrolyte and abrasion, stay permanently bonded through "
                     "the pack's life, and meet flame-retardancy standards for cell and module marking.",
        "solution": "Polyimide film labels with flame-retardant (UL 94 VTM-0) constructions and durable adhesives, "
                    "thermal-transfer printable for serial/2D traceability on cells, modules and packs.",
        "benefit": "Compliant, permanent battery marking that survives assembly and service, supporting recall "
                   "traceability and safety certification across EV and stationary-storage applications.",
        "highlights": [
            "UL 94 VTM-0 flame-retardant polyimide constructions for battery marking",
            "Resistant to electrolyte, heat and abrasion for pack-life permanence",
            "Thermal-transfer printable for serial / 2D-code cell and module traceability",
            "Thin, conformable film suits curved cell cans and module surfaces"],
        "faq": [("Do battery labels need to be flame-retardant?",
                 "Cell and module marking commonly specifies flame-retardant (UL 94 VTM-0) label constructions; "
                 "check each product's certification and TDS against your battery spec.")],
    },
    "under-hood": {
        "code": "AN-AUTO-001", "hot": False,
        "industry": "Automotive", "category": "Under-Hood & Powertrain",
        "title": "High-Temperature Polyimide Labels for Under-Hood & Powertrain",
        "filter": "f.face_code='POLYIMIDE' AND p.sub_application='发动机舱/车厢底'",
        "intro": ("Under-hood and powertrain components run hot and are exposed to fuels, oils and solvents. "
                  "Rating plates, warning and traceability labels there must stay legible for the vehicle's life."),
        "challenge": "Sustained under-hood heat, thermal cycling, plus fuel/oil/solvent exposure and abrasion "
                     "degrade ordinary labels, causing illegible markings and warning/compliance failures.",
        "solution": "Polyimide film labels with high-temperature acrylic or silicone adhesives — some rated to "
                    "300°C+ short-term — thermal-transfer or laser marked for durable under-hood identification.",
        "benefit": "Warning, rating and traceability marks that stay legible and bonded through years of under-hood "
                   "heat, chemicals and vibration, supporting automotive compliance.",
        "highlights": [
            "Polyimide facestocks rated from ~210°C continuous up to 376°C with silicone adhesive",
            "Short-term peak survival to 300–537°C for the most extreme powertrain zones",
            "Resistant to fuels, oils and cleaning solvents common under the hood",
            "UL 94 and FAR 25.853 tested constructions available (per product TDS)"],
        "faq": [("Acrylic or silicone adhesive for under-hood?",
                 "High-temperature acrylic covers most under-hood zones; silicone adhesives extend continuous service "
                 "temperature further (e.g. 376°C facestocks) for the hottest powertrain areas.")],
    },
    "wire-cable": {
        "code": "AN-DATA-001", "hot": False,
        "industry": "Electronics / Data & Telecom", "category": "Wire & Cable Identification",
        "title": "Polyimide Labels for High-Temperature Wire & Cable Marking",
        "filter": "f.face_code='POLYIMIDE' AND p.sub_application='线缆标识'",
        "intro": ("Wire and cable in high-temperature or safety-critical harnesses need permanent, self-wrapping "
                  "identification that survives heat, flame and mechanical stress."),
        "challenge": "Harness labels must wrap small-diameter wire, stay bonded through heat and vibration, and meet "
                     "flammability / low-smoke requirements in aerospace, rail and automotive harnesses.",
        "solution": "Thin polyimide film labels with aggressive high-temperature adhesive, thermal-transfer "
                    "printable and flame-retardant (UL 94 VTM-0), for durable self-wrap or flag wire marking.",
        "benefit": "Legible, permanent wire identification that meets flame and smoke standards and survives the "
                   "harsh thermal and mechanical environment of high-reliability harnesses.",
        "highlights": [
            "Thin, conformable polyimide wraps small-diameter wire without lifting",
            "Aggressive high-temperature adhesive holds through heat and vibration",
            "UL 94 VTM-0, UL 969 and FMVSS / FAR-tested flame-retardant constructions",
            "Thermal-transfer printable for barcodes and legends on the harness"],
        "faq": [("Why polyimide for wire marking?",
                 "Polyimide combines thin conformability, high-temperature resistance and inherent flame retardancy — "
                 "ideal for self-wrap wire labels in aerospace, rail and automotive harnesses.")],
    },
    "overlaminate": {
        "code": "AN-ELEC-003", "hot": False,
        "industry": "Electronics Manufacturing", "category": "High-Temperature Overlaminate",
        "title": "Polyimide Overlaminates for High-Temperature Barcode Protection",
        "filter": "f.face_code='POLYIMIDE' AND p.sub_application='覆膜保护'",
        "intro": ("A clear high-temperature overlaminate protects a printed barcode or legend from abrasion, "
                  "solvents and handling — critical where the code must stay scannable through a harsh process."),
        "challenge": "Printed images can abrade or dissolve during handling, cleaning and high-temperature process, "
                     "degrading scan contrast and breaking traceability.",
        "solution": "Clear polyimide overlaminate films — rated to 350°C continuous / 500°C peak — laminated over "
                    "the printed label to shield the image while withstanding the same thermal exposure.",
        "benefit": "The barcode stays high-contrast and scannable through abrasion, solvents and extreme heat, "
                   "extending traceability reliability with no re-work.",
        "highlights": [
            "Clear polyimide overlaminate rated to 350°C continuous / 500°C short-term",
            "Protects the printed image from abrasion, solvents and flux",
            "High-temperature acrylic adhesive for permanent lamination",
            "REACH / RoHS compliant constructions (per product TDS)"],
        "faq": [("When do I need an overlaminate?",
                 "Use an overlaminate when the printed barcode faces abrasion, aggressive cleaning or extreme heat "
                 "that could otherwise erode scan contrast before end of life.")],
    },
}

ORDER = ["pcb-reflow", "esd-safe", "ev-battery", "under-hood", "wire-cable", "overlaminate"]

APP_EN = {"电路板PCB": "PCB labelling", "防静电ESD": "ESD-safe", "覆膜保护": "Overlaminate",
          "发动机舱/车厢底": "Under-hood", "动力电池": "EV battery", "线缆标识": "Wire & cable"}


def products(filt, limit=12):
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    rows = db.execute(f"""SELECT b.brand_name_en br, p.model_no m, p.product_name_en ne,
        f.face_name_en fc, a.adh_name_en ac, p.temp_long_min t0, p.temp_long_max t1, p.temp_peak_max tp,
        p.thickness_um th, p.color c, p.sub_application sub, p.certification cert,
        p.application_desc ds, p.benefit bn, p.tds_url tds, p.source_url src
        FROM product p JOIN brand b ON b.brand_id=p.brand_id
        JOIN facestock_dict f ON f.face_id=p.face_id
        LEFT JOIN adhesive_dict a ON a.adh_id=p.adh_id
        WHERE p.status=1 AND ({filt})
        ORDER BY (p.tds_url!='') DESC, (p.certification!='') DESC, p.temp_long_max DESC LIMIT {limit}""").fetchall()
    db.close()
    return [dict(r) for r in rows]


def temp_str(p):
    s = ""
    if p["t0"] is not None:
        s += f'{p["t0"]} ~ '
    s += (f'{p["t1"]}°C' if p["t1"] is not None else "—")
    if p["tp"] is not None:
        s += f' ({p["tp"]}°C peak)'
    return s


def render(key):
    n = NOTES[key]
    prods = products(n["filter"])
    lead = prods[0] if prods else None
    rest = prods[1:]
    canonical = f"{SITE}/application-notes/{key}"
    nbrand = len({p["br"] for p in prods})

    prod_chips = "".join(f'<span class="chip prod">{esc(p["br"])} {esc(p["m"])}</span>' for p in prods[:6])
    hl = "".join(f"<li>{esc(x)}</li>" for x in n["highlights"])
    lead_temp = temp_str(lead) if lead else "—"
    lead_link = (lead["tds"] or lead["src"] or "") if lead else ""
    rec_cards = "".join(
        f'''<a class="rec" href="{esc(p["tds"] or p["src"] or "#")}" target="_blank" rel="noopener">
          <div class="rec-top"><b>{esc(p["br"])} {esc(p["m"])}</b></div>
          <div class="rec-meta">{esc(p["ac"] or "—")} · {temp_str(p)}</div>
          {f'<div class="rec-cert">{esc((p["cert"] or "")[:44])}</div>' if p["cert"] else ""}
          <div class="rec-tds">{"✓ Official TDS" if p["tds"] else "Brand page"} →</div>
        </a>''' for p in rest)
    faq_html = "".join(f'<details class="faq"><summary>{esc(q)}</summary><p>{esc(a)}</p></details>'
                       for q, a in n.get("faq", []))

    seo_desc = (f'{n["category"]}: {n["solution"][:110]} Compare {len(prods)} polyimide products across '
                f'{nbrand} brands, each linked to its official TDS. {n["code"]}.')
    ld = [
        {"@context": "https://schema.org", "@type": "TechArticle", "headline": n["title"],
         "articleSection": n["category"], "author": {"@type": "Organization", "name": "ETIA"},
         "publisher": {"@type": "Organization", "name": "ETIA"}, "mainEntityOfPage": canonical},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
            {"@type": "ListItem", "position": 2, "name": "Application Notes", "item": SITE + "/application-notes"},
            {"@type": "ListItem", "position": 3, "name": n["category"], "item": canonical}]},
    ]
    if lead:
        ld.append({"@context": "https://schema.org", "@type": "Product",
                   "name": f'{lead["br"]} {lead["m"]}', "brand": lead["br"], "material": "Polyimide",
                   "url": lead_link})
    if n.get("faq"):
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in n["faq"]]})
    ld_json = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    hot = '<span class="hot">★ HOT</span>' if n["hot"] else ""

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
  --bg:#fff;--soft:#f5f7fa;--red:#c0392b;--redbg:#fdecec;--bluebg:#eaf1fb;--grn:#2e7d4f;--grnbg:#eaf6ee;}}
@media(prefers-color-scheme:dark){{:root{{--ink:#e6edf4;--mut:#93a3b4;--line:#26313d;--bg:#0f151c;--soft:#161f28;
  --redbg:#2a1815;--bluebg:#15202f;--grnbg:#132119;--red:#e0796b;--blue:#6ea6e8;--grn:#5cb585;}}}}
:root[data-theme="dark"]{{--ink:#e6edf4;--mut:#93a3b4;--line:#26313d;--bg:#0f151c;--soft:#161f28;--redbg:#2a1815;--bluebg:#15202f;--grnbg:#132119;--red:#e0796b;--blue:#6ea6e8;--grn:#5cb585;}}
:root[data-theme="light"]{{--ink:#1b2430;--mut:#5c6b7a;--line:#e3e8ee;--bg:#fff;--soft:#f5f7fa;--red:#c0392b;--redbg:#fdecec;--bluebg:#eaf1fb;--grnbg:#eaf6ee;--blue:#1c53a8;--grn:#2e7d4f;}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.7 -apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",system-ui,sans-serif}}
a{{color:var(--blue)}}
.wrap{{max-width:860px;margin:0 auto;padding:0 20px}}
header{{border-bottom:1px solid var(--line);padding:14px 0}}
.logo{{font-weight:800;font-size:22px}} .logo b{{color:var(--brand)}} .logo span{{color:var(--blue)}}
.hero{{background:linear-gradient(120deg,#11202b,#1c3346);color:#fff;padding:28px 0 30px;position:relative;overflow:hidden}}
.hero::after{{content:"";position:absolute;inset:0;background:radial-gradient(circle at 84% 26%,rgba(94,175,30,.3),transparent 55%)}}
.hero .wrap{{position:relative;z-index:1}}
.tagrow{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;align-items:center}}
.pill{{background:var(--brand);color:#0d1a05;font-weight:700;font-size:12px;padding:4px 11px;border-radius:15px}}
.pill.ghost{{background:rgba(255,255,255,.14);color:#fff;border:1px solid rgba(255,255,255,.3)}}
.hot{{background:#ffcf33;color:#3a2a00;font-weight:800;font-size:12px;padding:3px 9px;border-radius:12px}}
.code{{color:#9fb4c4;font-size:12.5px;letter-spacing:.06em;font-weight:700;margin-bottom:8px}}
.hero h1{{font-size:clamp(24px,4.4vw,34px);line-height:1.15;margin:0 0 8px;font-weight:800;text-wrap:balance}}
.lead-line{{color:#cfe0d3;font-size:14.5px}} .lead-line b{{color:#fff}}
.chips{{display:flex;gap:8px;flex-wrap:wrap;margin:20px 0 4px}}
.chip{{border:1px solid var(--line);background:var(--soft);border-radius:16px;padding:5px 13px;font-size:13px;color:var(--ink)}}
.chip.prod{{border-color:var(--brand);color:var(--brand);font-weight:600}}
.intro{{font-size:17px;margin:20px 0}}
.csb{{display:grid;gap:12px;margin:20px 0}}
.csb .row{{display:grid;grid-template-columns:132px 1fr;gap:14px;border-radius:12px;padding:14px 16px}}
.csb .row .lab{{font-weight:800;font-size:12.5px;letter-spacing:.06em;padding-top:2px}}
.row.c{{background:var(--redbg)}} .row.c .lab{{color:var(--red)}}
.row.s{{background:var(--bluebg)}} .row.s .lab{{color:var(--blue)}}
.row.b{{background:var(--grnbg)}} .row.b .lab{{color:var(--grn)}}
h2{{font-size:20px;margin:32px 0 10px}}
.eyebrow{{font-size:12.5px;font-weight:800;letter-spacing:.09em;color:var(--mut);margin:30px 0 8px}}
ul.hl{{margin:0;padding-left:22px}} ul.hl li{{margin:7px 0}}
.pdp{{border:1px solid var(--line);border-radius:14px;overflow:hidden;margin:12px 0}}
.pdp-head{{background:var(--soft);padding:16px 18px;border-bottom:1px solid var(--line)}}
.pdp-head .b{{font-size:12px;color:var(--brand);font-weight:700}}
.pdp-head h3{{margin:2px 0 0;font-size:20px}}
.pdp-body{{padding:6px 18px 16px}}
.spec{{width:100%;border-collapse:collapse}}
.spec th{{text-align:left;color:var(--mut);font-weight:600;font-size:12.5px;padding:8px 10px 8px 0;white-space:nowrap;width:130px;vertical-align:top;border-bottom:1px solid var(--line)}}
.spec td{{padding:8px 0;border-bottom:1px solid var(--line);font-size:14px}}
.spec tr:last-child th,.spec tr:last-child td{{border-bottom:none}}
.cta{{display:inline-block;background:var(--brand);color:#0d1a05;font-weight:800;padding:11px 22px;border-radius:9px;text-decoration:none;margin:12px 0 2px}}
.recs{{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px;margin-top:8px}}
.rec{{border:1px solid var(--line);border-radius:11px;padding:13px 15px;text-decoration:none;color:var(--ink);display:block;transition:border-color .15s}}
.rec:hover{{border-color:var(--brand)}}
.rec-top b{{font-size:14.5px}} .rec-meta{{color:var(--mut);font-size:12.5px;margin-top:3px}}
.rec-cert{{color:var(--mut);font-size:11.5px;margin-top:3px}} .rec-tds{{color:var(--brand);font-size:12px;font-weight:600;margin-top:7px}}
.faq{{border:1px solid var(--line);border-radius:10px;padding:0 16px;margin-bottom:10px;background:var(--soft)}}
.faq summary{{padding:14px 0;font-weight:600;cursor:pointer;list-style:none}}
.faq summary::-webkit-details-marker{{display:none}}
.faq summary::before{{content:"+ ";color:var(--brand);font-weight:800}} .faq[open] summary::before{{content:"− "}}
.faq p{{margin:0 0 14px;color:var(--mut);font-size:14.5px}}
.disc{{color:var(--mut);font-size:12.5px}}
footer{{border-top:1px solid var(--line);margin-top:36px;padding:24px 0;color:var(--mut);font-size:13px}}
</style>
</head>
<body>
<header><div class="wrap"><span class="logo"><b>&#9654;TIA</b>·<span>TECH</span></span></div></header>

<div class="hero"><div class="wrap">
  <div class="code">{n['code']}</div>
  <div class="tagrow"><span class="pill">{esc(n['industry'])}</span><span class="pill ghost">{esc(n['category'])}</span>{hot}</div>
  <h1>{esc(n['title'])}</h1>
  <div class="lead-line">{esc(n['category'])}{f' · <b>{esc(lead["br"])} {esc(lead["m"])}</b>' if lead else ''}</div>
</div></div>

<div class="wrap">
  <div class="chips">{prod_chips}</div>
  <p class="intro">{esc(n['intro'])}</p>

  <div class="csb">
    <div class="row c"><div class="lab">THE CHALLENGE</div><div>{esc(n['challenge'])}</div></div>
    <div class="row s"><div class="lab">THE SOLUTION</div><div>{esc(n['solution'])}</div></div>
    <div class="row b"><div class="lab">THE BENEFIT</div><div>{esc(n['benefit'])}</div></div>
  </div>

  <div class="eyebrow">TECHNOLOGY HIGHLIGHTS</div>
  <ul class="hl">{hl}</ul>

  {"" if not lead else f'''
  <h2>Recommended Product</h2>
  <div class="pdp">
    <div class="pdp-head"><div class="b">{esc(lead["br"])}</div><h3>{esc(lead["m"])} — {esc(lead["ne"] or "")}</h3></div>
    <div class="pdp-body">
      <table class="spec">
        <tr><th>Facestock</th><td>{esc(lead["fc"] or "Polyimide")}</td></tr>
        <tr><th>Adhesive</th><td>{esc(lead["ac"] or "—")}</td></tr>
        <tr><th>Temperature</th><td>{lead_temp}</td></tr>
        <tr><th>Thickness</th><td>{(str(lead["th"])+" µm") if lead["th"] is not None else "—"}</td></tr>
        <tr><th>Certifications</th><td>{esc(lead["cert"] or "—")}</td></tr>
        <tr><th>Application</th><td>{esc(lead["ds"] or "")[:260]}</td></tr>
      </table>
      {f'<a class="cta" href="{esc(lead_link)}" target="_blank" rel="noopener">⬇ Download official TDS</a>' if lead_link else ''}
    </div>
  </div>'''}

  {"" if not rest else f'<h2>Recommended Products <span class="disc">— {len(prods)} polyimide options across {nbrand} brands</span></h2><div class="recs">{rec_cards}</div>'}

  {f'<h2>FAQ</h2>{faq_html}' if faq_html else ''}

  <p class="disc" style="margin-top:26px">Technical guidance reflects established industry practice (e.g. reflow peaks per IPC/JEDEC J-STD-020). Product specs are drawn from each brand's official page / TDS; fields not published are left blank — never fabricated. For reference only; specify against the official TDS.</p>
  <p style="margin:14px 0"><a class="cta" href="{SITE}/polyimide-labels">Browse all polyimide labels →</a></p>
</div>

<footer><div class="wrap"><b>ETIA</b> · Specialty industrial labels · 20 years of selection expertise · {n['code']}</div></footer>
</body>
</html>
"""


def main():
    key = sys.argv[1] if len(sys.argv) > 1 else "all"
    outdir = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "data/appnotes"
    outdir.mkdir(parents=True, exist_ok=True)
    keys = ORDER if key == "all" else [key]
    for k in keys:
        (outdir / f"{k}.html").write_text(render(k), encoding="utf-8")
        print(f"  {NOTES[k]['code']:12s} {k}.html — {NOTES[k]['title']}")
    print(f"done: {len(keys)} notes in {outdir}")


if __name__ == "__main__":
    main()
