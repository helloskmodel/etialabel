#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ETIA Label overseas website generator — catalog-driven (By Industry / By Solution /
By Material -> Product Detail Page). English-first, multilingual-ready. Corporate-site IA
(Home / Products & Solutions / Applications / Insights / Service & Support / Company / Contact)."""
import json, os, re, html, shutil

BUILD_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BUILD_DIR)
DATA_DIR = os.path.join(BUILD_DIR, "data")
SITE = "https://www.etialabel.com"

LANGS = ["en"]
DEFAULT_LANG = "en"
LANG_PREFIX = {"en": ""}
HREFLANG = {"en": "en"}

catalog = json.load(open(os.path.join(DATA_DIR, "catalog.json")))
INDUSTRIES = catalog["industries"]     # {L1: {L2: [rows]}}
SOLUTIONS  = catalog["solutions"]       # {L1: {L2: [rows]}}
MATERIALS  = catalog["materials"]       # {"Base — Property": [rows]}

# ------------------------------------------------------------------ helpers
def esc(s): return html.escape(str(s), quote=True)

def slugify(s):
    s = (s or "").lower().replace("&", "and").replace("+", "-plus-")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-") or "x"

def is_ys(pn):
    return bool(re.match(r"\s*(HP|GH|CX)", (pn or "").upper()))

PRIO = {"Highest": 0, "High": 1, "Medium": 2, "": 3}

# ------------------------------------------------------------------ product registry
PRODUCTS = {}       # slug -> product dict
MODEL2SLUG = {}
USED_SLUGS = set()

def uniq_slug(base):
    s, i = base, 2
    while s in USED_SLUGS:
        s = "%s-%d" % (base, i); i += 1
    USED_SLUGS.add(s)
    return s

def reg_product(model, label, seo, poly, etia, brady):
    model = (model or "").strip()
    if not model:
        return None
    slug = MODEL2SLUG.get(model)
    if not slug:
        slug = uniq_slug(slugify(model))
        MODEL2SLUG[model] = slug
        PRODUCTS[slug] = {"model": model, "label": label or model, "seo": seo or "",
                          "poly": set(), "ys": set(), "etia": set(), "brady": set(),
                          "collections": {}, "belongs": {"industry": set(), "solution": set(), "material": set()}}
    p = PRODUCTS[slug]
    if poly: p["poly"].add(poly)
    if etia:
        (p["ys"] if is_ys(etia) else p["etia"]).add(etia)
    if brady:
        for b in re.split(r"[\s/]+", brady):
            if b: p["brady"].add(b)
    return slug

# path url builders
def u_ind(l1, l2=None):
    return "/products/by-industry/%s/%s" % (slugify(l1), (slugify(l2) + "/") if l2 else "")
def u_sol(l1, l2=None):
    return "/products/by-solution/%s/%s" % (slugify(l1), (slugify(l2) + "/") if l2 else "")
def u_mat_base(base):
    return "/products/by-material/%s/" % slugify(base)
def u_mat(base, prop):
    return "/products/by-material/%s/%s/" % (slugify(base), slugify(prop))
def u_pdp(slug):
    return "/products/item/%s/" % slug

# Pass 1: register every product occurrence and its collection membership
def register_all():
    for l1, subs in INDUSTRIES.items():
        for l2, rows in subs.items():
            url, title = u_ind(l1, l2), "%s — %s" % (l1, l2)
            for r in rows:
                s = reg_product(r["model"], r.get("series"), r.get("seo"), r["poly"], r["etia"], r["brady"])
                if s:
                    PRODUCTS[s]["collections"][url] = title
                    PRODUCTS[s]["belongs"]["industry"].add(l1)
    for l1, subs in SOLUTIONS.items():
        for l2, rows in subs.items():
            url, title = u_sol(l1, l2), "%s — %s" % (l1, l2)
            for r in rows:
                s = reg_product(r["model"], r.get("series"), r.get("seo"), r["poly"], r["etia"], r["brady"])
                if s:
                    PRODUCTS[s]["collections"][url] = title
                    PRODUCTS[s]["belongs"]["solution"].add(l1)
    for combined, rows in MATERIALS.items():
        base, prop = (combined.split("—", 1) + [""])[:2]
        base, prop = base.strip(), prop.strip()
        url, title = u_mat(base, prop), combined
        for r in rows:
            s = reg_product(r["model"], r.get("detail"), r.get("seo"), r["poly"], r["etia"], r["brady"])
            if s:
                PRODUCTS[s]["collections"][url] = title
                PRODUCTS[s]["belongs"]["material"].add(base)

# ------------------------------------------------------------------ CSS (white Hönle-style header)
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{--blue-deep:#143C96;--blue:#1A56DB;--green:#41A62A;--green-d:#358B22;--amber:#b45309;--ink:#16223a;--mut:#5a6577;--line:#e2e8f2;--bg:#f5f8fd}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:#fff;line-height:1.6;-webkit-font-smoothing:antialiased}
a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}
img{max-width:100%}
.wrap{max-width:1180px;margin:0 auto;padding:0 22px}
.topstrip{height:4px;background:linear-gradient(90deg,#6d28d9 0%,var(--blue) 55%,#22a3e0 100%)}
header.site{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:40}
header.site .wrap{display:flex;align-items:center;justify-content:space-between;height:66px;gap:16px}
.logo{font-weight:800;font-size:22px;color:var(--blue-deep);letter-spacing:.2px;display:flex;align-items:center}
.logo .dot{color:var(--green)}
.logo small{font-weight:700;font-size:13px;color:var(--mut);margin-left:8px;letter-spacing:.5px;text-transform:uppercase}
nav.main{display:flex;align-items:center;gap:26px}
nav.main .item{position:relative}
nav.main .item>a{color:var(--ink);font-weight:600;font-size:15px;line-height:66px;display:inline-block;white-space:nowrap}
nav.main .item:hover>a,nav.main .item>a.on{color:var(--blue)}
nav.main .item.has>a::after{content:"▾";font-size:10px;margin-left:5px;color:var(--mut)}
.mega{position:absolute;top:60px;left:0;background:#fff;border:1px solid var(--line);border-radius:12px;box-shadow:0 14px 40px rgba(16,34,58,.14);min-width:250px;padding:8px;display:none}
nav.main .item:hover .mega{display:block}
.mega a{display:block;padding:10px 12px;border-radius:8px;color:var(--ink);font-size:14px;font-weight:600}
.mega a small{display:block;font-weight:500;color:var(--mut);font-size:12px}
.mega a:hover{background:var(--bg);color:var(--blue);text-decoration:none}
.navcta{background:var(--green);color:#fff!important;padding:9px 18px;border-radius:9px;font-weight:700;line-height:1!important}
.navcta:hover{background:var(--green-d);text-decoration:none}
.crumb{font-size:13px;color:var(--mut);padding:14px 0}
.crumb a{color:var(--mut)}.crumb b{color:var(--ink)}
.hero{background:linear-gradient(155deg,#0f2f7a 0%,var(--blue-deep) 55%,#1c4bc4 100%);color:#fff;padding:64px 0 56px}
.hero h1{font-size:38px;line-height:1.15;font-weight:800;max-width:880px;text-wrap:balance}
.hero p{color:#cfdcf5;margin-top:16px;max-width:740px;font-size:18px}
.hero .btns{margin-top:26px;display:flex;flex-wrap:wrap;gap:12px}
.pagehead{background:linear-gradient(155deg,#0f2f7a,var(--blue-deep));color:#fff;padding:40px 0}
.pagehead h1{font-size:30px;font-weight:800;text-wrap:balance;max-width:900px}
.pagehead p{color:#cfdcf5;margin-top:10px;max-width:760px}
.btn{display:inline-block;background:var(--green);color:#fff;font-weight:700;padding:12px 26px;border-radius:10px;transition:.15s}
.btn:hover{text-decoration:none;background:var(--green-d)}
.btn.ghost{background:transparent;border:1.5px solid #5c7fd6;color:#e3ebfb}
.btn.ghost:hover{background:rgba(255,255,255,.08);border-color:#8aa6e8}
.btn.blue{background:var(--blue)}.btn.blue:hover{background:var(--blue-deep)}
.sec{padding:44px 0}
.sec h2{font-size:25px;margin-bottom:6px;color:var(--blue-deep);text-wrap:balance}
.sec .lede{color:var(--mut);margin-bottom:20px;max-width:820px}
.paths{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.pcard{border:1px solid var(--line);border-radius:14px;padding:24px;background:var(--bg);transition:.15s;display:block}
.pcard:hover{border-color:var(--blue);box-shadow:0 8px 26px rgba(26,86,219,.10);text-decoration:none}
.pcard .tag{font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.7px;color:var(--blue)}
.pcard h3{font-size:19px;margin:6px 0 6px;color:var(--blue-deep)}
.pcard p{color:var(--mut);font-size:14px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}
.card{border:1px solid var(--line);border-radius:12px;padding:18px;background:#fff;transition:.15s;display:block}
.card:hover{border-color:var(--blue);box-shadow:0 4px 18px rgba(26,86,219,.10);text-decoration:none}
.card h4{font-size:15px;margin-bottom:5px;color:var(--blue-deep)}
.card p{font-size:13px;color:var(--mut)}
.card .meta{margin-top:9px;display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.trust{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.trust .t{background:var(--bg);border:1px solid var(--line);border-top:3px solid var(--blue);border-radius:10px;padding:20px}
.trust .t b{display:block;color:var(--blue-deep);font-size:16px;margin-bottom:4px}
.trust .t p{color:var(--mut);font-size:14px}
.bchip{display:inline-block;font-size:11px;font-weight:700;padding:2px 9px;border-radius:20px;color:#fff}
.bchip.poly{background:var(--blue)}.bchip.ys{background:var(--amber)}.bchip.etia{background:var(--green)}
.bchip.flexcon{background:#0f766e}.bchip.computype{background:#6d28d9}.bchip.brady{background:#64748b}
.prio{font-size:11px;font-weight:700;padding:2px 8px;border-radius:6px;background:#eaf1ff;color:var(--blue);border:1px solid #d6e2fb}
.tablewrap{overflow-x:auto}
table.matrix{width:100%;border-collapse:collapse;font-size:14px;margin-top:8px}
table.matrix th,table.matrix td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line)}
table.matrix th{background:var(--bg);font-size:12px;text-transform:uppercase;letter-spacing:.4px;color:var(--mut)}
table.matrix td.mono{font-family:ui-monospace,Menlo,monospace;font-weight:600}
.specs{list-style:none}.specs li{display:flex;justify-content:space-between;gap:16px;padding:12px 0;border-bottom:1px solid var(--line);font-size:14px}
.specs li span:first-child{color:var(--mut)}.specs li span:last-child{font-weight:700;text-align:right}
.certs{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
.cert{font-size:12px;font-weight:700;background:#eaf1ff;color:var(--blue);padding:6px 12px;border-radius:8px;border:1px solid #d6e2fb}
.xlinks{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
.xlinks a{font-size:13px;background:var(--bg);border:1px solid var(--line);padding:7px 13px;border-radius:20px;color:var(--ink)}
.xlinks a:hover{border-color:var(--blue);text-decoration:none}
.faq details{border:1px solid var(--line);border-radius:10px;padding:4px 16px;margin-bottom:10px}
.faq summary{font-weight:700;padding:12px 0;cursor:pointer;font-size:15px}
.faq p{padding:0 0 14px;color:var(--mut);font-size:14px}
.note{background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:16px 18px;font-size:14px;color:#92400e}
.offices{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
.office{border:1px solid var(--line);border-top:3px solid var(--green);border-radius:12px;padding:20px}
.office h3{font-size:17px;color:var(--blue-deep);margin-bottom:4px}
.office .role{font-weight:700;font-size:14px;margin-bottom:8px}.office .role span{color:var(--mut);font-weight:600}
.office .addr{color:var(--mut);font-size:14px;margin-bottom:12px}
.office .crows{list-style:none;display:flex;flex-direction:column;gap:7px}
.office .crows li{font-size:14px;display:flex;gap:8px}.office .crows .ic{color:var(--blue);font-weight:700;width:16px;flex:none;text-align:center}
.cta{background:linear-gradient(150deg,var(--blue-deep),#0f2f7a);color:#fff;border-radius:16px;padding:38px;text-align:center;margin:12px 0}
.cta h3{font-size:23px;text-wrap:balance}.cta p{color:#cfdcf5;margin:10px auto 18px;max-width:660px}
.cta .btns{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
footer.site{background:var(--blue-deep);color:#aebfe0;padding:40px 0;margin-top:12px;font-size:13px}
footer.site .fgrid{display:grid;grid-template-columns:2fr 1fr 1fr;gap:24px}
footer.site strong{color:#fff}footer.site a{color:#cdd9f2}
footer.site h5{color:#fff;font-size:13px;text-transform:uppercase;letter-spacing:.5px;margin-bottom:10px}
footer.site ul{list-style:none;display:flex;flex-direction:column;gap:6px}
.fbar{border-top:1px solid #2a4a86;margin-top:24px;padding-top:16px;color:#8fb0e6}
@media(max-width:820px){.paths{grid-template-columns:1fr}.trust{grid-template-columns:1fr}.offices{grid-template-columns:1fr}
.hero h1{font-size:28px}footer.site .fgrid{grid-template-columns:1fr}nav.main{display:none}}
"""

# ------------------------------------------------------------------ page shell
def nav_html(active=""):
    def item(label, href, key, mega=None):
        cls = "item has" if mega else "item"
        on = ' class="on"' if key == active else ''
        h = '<div class="%s"><a href="%s"%s>%s</a>' % (cls, href, on, label)
        if mega:
            h += '<div class="mega">' + "".join(
                '<a href="%s">%s%s</a>' % (hu, esc(t), ('<small>%s</small>' % esc(sub)) if sub else '')
                for t, hu, sub in mega) + '</div>'
        return h + '</div>'
    items = [
        item("Home", "/", "home"),
        item("Products &amp; Solutions", "/products/", "products", [
            ("By Industry", "/products/by-industry/", "Start from your sector"),
            ("By Solution", "/products/by-solution/", "Start from your process"),
            ("By Material", "/products/by-material/", "Start from the substrate")]),
        item("Applications", "/applications/", "applications"),
        item("Insights", "/insights/", "insights", [
            ("Case Studies", "/insights/case-studies/", "Real deployments"),
            ("Blog", "/insights/blog/", "Articles &amp; know-how"),
            ("Resources", "/insights/resources/", "Guides &amp; downloads")]),
        item("Service &amp; Support", "/support/", "support"),
        item("Company", "/company/", "company"),
        item("Contact", "/contact/", "contact"),
    ]
    return '<nav class="main">' + "".join(items) + '</nav>'

def hreflang_tags(canonical):
    path = canonical[len(SITE):] if canonical.startswith(SITE) else canonical
    t = ['<link rel="alternate" hreflang="%s" href="%s">' % (HREFLANG[l], SITE + LANG_PREFIX[l] + path) for l in LANGS]
    t.append('<link rel="alternate" hreflang="x-default" href="%s">' % (SITE + LANG_PREFIX[DEFAULT_LANG] + path))
    return "".join(t)

def crumbs(items):
    parts = []
    for i, (t, uu) in enumerate(items):
        if uu and i < len(items) - 1:
            parts.append('<a href="%s">%s</a>' % (uu, esc(t)))
        else:
            parts.append('<b>%s</b>' % esc(t))
    return '<div class="wrap crumb">%s</div>' % ' &rsaquo; '.join(parts)

def page(title, desc, canonical, body, schema=None, active="", crumb=None):
    sj = ('<script type="application/ld+json">%s</script>' % json.dumps(schema, ensure_ascii=False)) if schema else ""
    cr = crumbs(crumb) if crumb else ""
    return """<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="%s">%s
<meta property="og:title" content="%s"><meta property="og:type" content="website"><meta property="og:site_name" content="ETIA Label">
<style>%s</style>%s</head><body>
<div class="topstrip"></div>
<header class="site"><div class="wrap"><a class="logo" href="/">ETIA<span class="dot">.</span>LABEL <small>Solution Partner</small></a>%s</div></header>
%s
%s
%s
</body></html>""" % (esc(title), esc(desc), canonical, hreflang_tags(canonical), esc(title), CSS, sj, nav_html(active), cr, body, FOOTER)

FOOTER = """<footer class="site"><div class="wrap">
<div class="fgrid">
<div><strong>ETIA Label</strong> — Your Solution Partner for labels that perform where ordinary ones fail.<br>
Sole agent: Polyonics (USA) &amp; YS&nbsp;Tech (Japan) · FlexCon · Computype · Own die-cutting &amp; slitting factory.<br>
<em style="color:#8fb0e6">Engineering Success.</em></div>
<div><h5>Products &amp; Solutions</h5><ul>
<li><a href="/products/by-industry/">By Industry</a></li><li><a href="/products/by-solution/">By Solution</a></li>
<li><a href="/products/by-material/">By Material</a></li><li><a href="/products/">All Products</a></li></ul></div>
<div><h5>Company</h5><ul>
<li><a href="/company/">About ETIA</a></li><li><a href="/applications/">Applications</a></li>
<li><a href="/insights/">Insights</a></li><li><a href="/support/">Service &amp; Support</a></li>
<li><a href="/contact/">Contact</a></li></ul></div>
</div>
<div class="fbar">© ETIA Label · Genuine brand-authorized materials — never grey-market. label@etia-tech.com</div>
</div></footer>"""

def write(path, content):
    full = os.path.join(ROOT, path.strip("/"), "index.html") if not path.endswith((".xml", ".txt")) else os.path.join(ROOT, path.strip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(content)

ALL_URLS = []
def track(u, g): ALL_URLS.append((u, g))

def bc_schema(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement":
            [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + uu} for i, (n, uu) in enumerate(items)]}
def faq_schema(qas):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity":
            [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qas]}
def faq_html(qas):
    return '<div class="faq">' + "".join('<details><summary>%s</summary><p>%s</p></details>' % (esc(q), esc(a)) for q, a in qas) + '</div>'

def cta():
    return """<div class="cta"><h3>Tell us the application — we'll engineer the label.</h3>
<p>Send your temperature range, surface, chemical exposure and print method. We'll return the matched Polyonics, YS&nbsp;Tech or ETIA part with a datasheet and free qualification samples — often within one working day.</p>
<div class="btns"><a class="btn" href="/contact/">Request Samples &amp; Datasheet</a>
<a class="btn ghost" href="/products/">Explore Products &amp; Solutions</a></div></div>"""

# ------------------------------------------------------------------ shared content blocks
TRUST = """<div class="sec"><h2>Why buyers choose ETIA</h2><div class="trust">
<div class="t"><b>20 years, two sole agencies</b><p>Sole agent for Polyonics (USA) and YS&nbsp;Tech (Japan) — genuine, brand-authorized material, never grey-market.</p></div>
<div class="t"><b>Our own factory</b><p>In-house die-cutting and slitting plus local stock means faster delivery to printers, converters and end users alike.</p></div>
<div class="t"><b>Application-first partnership</b><p>We start from your environment — surface, heat, chemistry, print method, lifecycle — then engineer the label, from sample to production.</p></div>
</div></div>"""

BRANDS_MATRIX = """<div class="sec"><h2>Authorized brands we represent</h2>
<p class="lede">Genuine, brand-authorized materials — never grey-market substitutes.</p><div class="grid">
<div class="card"><h4><span class="bchip poly">Polyonics</span> &nbsp;USA</h4><p>Ultra-thin polyimide &amp; PET for PCB reflow, ESD, flame-retardant and laser-marking electronics labels. <b>Sole agent — 20 years.</b></p></div>
<div class="card"><h4><span class="bchip ys">YS&nbsp;Tech</span> &nbsp;Japan</h4><p>Metal, aluminum-foil and inorganic ceramic tags for 300–1300&nbsp;°C metallurgy, heat-treatment and kilns. <b>Sole agent, Asia-Pacific.</b></p></div>
<div class="card"><h4><span class="bchip flexcon">FlexCon</span> &nbsp;USA</h4><p>Pressure-sensitive films, adhesives and specialty face-stocks — the material base for demanding converted labels.</p></div>
<div class="card"><h4><span class="bchip computype">Computype</span> &nbsp;USA</h4><p>Barcode, traceability and identification systems for regulated, high-mix production.</p></div>
<div class="card"><h4><span class="bchip etia">ETIA</span> &nbsp;Own brand</h4><p>Full-range PET, PP and specialty converter stock — cut in our own die-cutting &amp; slitting factory.</p></div>
</div></div>"""

OFFICES = [
 {"loc": "China · Shanghai", "name": "Mark Tang", "role": "",
  "addr": "Rm. 1903, 2# Building, Guoson Centre, No. 388 Zhongjiang Rd, Putuo District, Shanghai, China",
  "phones": [("400 990 8448", "tel:4009908448"), ("+86-21-6432-7144 ext. 106", "tel:+862164327144")], "email": "label@etia-tech.com"},
 {"loc": "Hong Kong", "name": "Mark Tang", "role": "",
  "addr": "Room 1003, 10/F, Tower 1, Lippo Centre, 89 Queensway, Admiralty, Hong Kong",
  "phones": [("+86 151 2119 7091", "tel:+8615121197091")], "email": "label@etia-tech.com"},
 {"loc": "Thailand · Bangkok", "name": "Mr. Sompoch Ratchakom (Job)", "role": "Sales Director",
  "addr": "22/41 H-Cape Biz Center, Sukhaphiban 2 Road, Prawet Subdistrict, Prawet District, Bangkok 10250, Thailand",
  "phones": [("+66 811 746 947", "tel:+66811746947")], "email": "label@etia-tech.com"},
 {"loc": "Vietnam · Bac Ninh", "name": "Tien Nguyen", "role": "Technical Engineer",
  "addr": "No. 10 Thanh Nien Street, Area 5, Vo Cuong Ward, Bac Ninh Province, Viet Nam",
  "phones": [("+84 344 590 091", "tel:+84344590091")], "email": "label@etia-tech.com"}]

def office_cards():
    out = []
    for o in OFFICES:
        role = esc(o["name"]) + ((" · <span>%s</span>" % esc(o["role"])) if o["role"] else "")
        phones = "".join('<li><span class="ic">☎</span><a href="%s">%s</a></li>' % (uu, esc(p)) for p, uu in o["phones"])
        out.append('<div class="office"><h3>%s</h3><div class="role">%s</div><p class="addr">%s</p>'
                   '<ul class="crows"><li><span class="ic">✉</span><a href="mailto:%s">%s</a></li>%s</ul></div>'
                   % (esc(o["loc"]), role, esc(o["addr"]), o["email"], esc(o["email"]), phones))
    return '<div class="offices">%s</div>' % "".join(out)

def contact_points():
    return [{"@type": "ContactPoint", "contactType": "sales", "telephone": o["phones"][0][0], "email": o["email"]} for o in OFFICES]

# ------------------------------------------------------------------ product cards / matrix
def brand_chips(p):
    c = []
    if p["poly"]: c.append('<span class="bchip poly">Polyonics</span>')
    if p["ys"]: c.append('<span class="bchip ys">YS Tech</span>')
    if p["etia"]: c.append('<span class="bchip etia">ETIA</span>')
    return "".join(c)

def product_cards(rows):
    """rows: list of (model, seo_priority)."""
    seen, cards = set(), []
    ordered = sorted(rows, key=lambda r: (PRIO.get(r[1], 3), r[0]))
    for model, prio in ordered:
        slug = MODEL2SLUG.get(model.strip())
        if not slug or slug in seen:
            continue
        seen.add(slug)
        p = PRODUCTS[slug]
        badge = ('<span class="prio">%s priority</span>' % esc(prio)) if prio in ("Highest", "High") else ""
        cards.append('<a class="card" href="%s"><h4>%s</h4><div class="meta">%s %s</div></a>'
                     % (u_pdp(slug), esc(p["label"] or model), brand_chips(p), badge))
    return '<div class="grid">%s</div>' % "".join(cards)

# ------------------------------------------------------------------ builders
def build_home():
    ind_cards = "".join('<a class="card" href="%s"><h4>%s</h4><p>%d process areas</p></a>'
                        % (u_ind(l1), esc(l1), len(subs)) for l1, subs in INDUSTRIES.items())
    brand_row = ('<div class="certs">'
                 '<span class="bchip poly">Polyonics · USA</span><span class="bchip ys">YS Tech · Japan</span>'
                 '<span class="bchip etia">ETIA · Own brand</span><span class="bchip flexcon">FlexCon</span>'
                 '<span class="bchip computype">Computype</span></div>')
    body = """<section class="hero"><div class="wrap">
<h1>Your solution partner for labels that perform where ordinary ones fail.</h1>
<p>For over 20 years we've engineered durable and specialty labels for the toughest conditions — extreme heat to 1300&nbsp;°C, cryogenic cold to −196&nbsp;°C, harsh chemicals, oily surfaces and lead-free PCB assembly. We start from your application, not a catalog.</p>
<div class="btns"><a class="btn" href="/contact/">Request Samples &amp; Datasheet</a>
<a class="btn ghost" href="/products/">Explore Products &amp; Solutions</a></div></div></section>
<div class="wrap">
<div class="sec"><h2>Find your label three ways</h2><p class="lede">Every path converges on the same datasheet-backed product — genuine Polyonics, YS&nbsp;Tech and ETIA material.</p>
<div class="paths">
<a class="pcard" href="/products/by-industry/"><div class="tag">Path 1</div><h3>By Industry</h3><p>Electronics, automotive, steel, medical, pharma, outdoor/PV, telecom, ceramics.</p></a>
<a class="pcard" href="/products/by-solution/"><div class="tag">Path 2</div><h3>By Solution</h3><p>SMT reflow, heat-treatment, cold-chain, ESD, weatherproofing and compliance.</p></a>
<a class="pcard" href="/products/by-material/"><div class="tag">Path 3</div><h3>By Material</h3><p>Polyimide, PET, ceramic &amp; metal high-temp, low-temp specialty, synthetic paper.</p></a>
</div></div>
<div class="sec"><h2>Industries we serve</h2><div class="grid">%s</div></div>
<div class="sec"><h2>Why buyers choose ETIA</h2><div class="trust">
<div class="t"><b>20 years, two sole agencies</b><p>Sole agent for Polyonics (USA) and YS&nbsp;Tech (Japan) — genuine, brand-authorized material, never grey-market.</p></div>
<div class="t"><b>Our own factory</b><p>In-house die-cutting and slitting plus local stock means faster delivery to printers, converters and end users alike.</p></div>
<div class="t"><b>Application-first partnership</b><p>We start from your environment — surface, heat, chemistry, print method, lifecycle — then engineer the label, from sample to production.</p></div></div>
<p class="lede" style="margin-top:24px">Authorized brands we represent</p>%s</div>
%s
</div>""" % (ind_cards, brand_row, cta())
    sch = {"@context": "https://schema.org", "@type": "Organization", "name": "ETIA Label", "url": SITE,
           "slogan": "Your Solution Partner. Engineering Success.",
           "description": "Solution partner for durable, specialty industrial labels. Sole agent for Polyonics (USA) and YS Tech (Japan), with in-house die-cutting and slitting.",
           "brand": ["Polyonics", "YS Tech", "FlexCon", "Computype", "ETIA"], "contactPoint": contact_points()}
    write("/", page("ETIA Label — Your Solution Partner for Industrial Specialty Labels",
        "Durable, high-performance industrial labels for extreme heat to 1300°C, cryogenic cold, chemicals and lead-free PCB assembly. Polyonics, YS Tech & ETIA — browse by industry, solution or material. Free samples.",
        SITE + "/", body, sch, active="home"))
    track("/", "core")

def build_products_landing():
    body = """<div class="pagehead"><div class="wrap"><h1>Products &amp; Solutions</h1>
<p>Browse the catalog three ways — every path converges on the same product, genuine Polyonics, YS&nbsp;Tech and ETIA material.</p></div></div>
<div class="wrap"><div class="sec"><div class="paths">
<a class="pcard" href="/products/by-industry/"><div class="tag">Path 1</div><h3>By Industry</h3><p>Start from your sector and drill to the process that stresses the label.</p></a>
<a class="pcard" href="/products/by-solution/"><div class="tag">Path 2</div><h3>By Solution</h3><p>Start from the production process or the problem you need solved.</p></a>
<a class="pcard" href="/products/by-material/"><div class="tag">Path 3</div><h3>By Material</h3><p>Start from the substrate — the film or metal that sets the performance envelope.</p></a>
</div></div>%s</div>""" % cta()
    crumb = [("Home", "/"), ("Products & Solutions", "/products/")]
    write("/products/", page("Products & Solutions — Industrial Specialty Labels | ETIA Label",
        "Browse ETIA industrial labels by industry, solution or material. Polyonics, YS Tech and ETIA products with free qualification samples.",
        SITE + "/products/", body, [bc_schema(crumb)], active="products", crumb=crumb))
    track("/products/", "core")

def build_industry_path():
    crumb0 = [("Home", "/"), ("Products & Solutions", "/products/"), ("By Industry", "/products/by-industry/")]
    cards = "".join('<a class="card" href="%s"><h4>%s</h4><p>%d process areas · %d products</p></a>'
                    % (u_ind(l1), esc(l1), len(subs), sum(len(r) for r in subs.values())) for l1, subs in INDUSTRIES.items())
    body = ('<div class="pagehead"><div class="wrap"><h1>Labels by Industry</h1><p>Eight industries, each broken down by the processes that stress the label.</p></div></div>'
            '<div class="wrap"><div class="sec"><div class="grid">%s</div></div>%s</div>' % (cards, cta()))
    write("/products/by-industry/", page("Industrial Labels by Industry | ETIA Label",
        "Browse specialty labels by industry: electronics & PCB, automotive, steel, medical, pharma, outdoor & PV, telecom, ceramics.",
        SITE + "/products/by-industry/", body, [bc_schema(crumb0)], active="products", crumb=crumb0))
    track("/products/by-industry/", "industries")
    for l1, subs in INDUSTRIES.items():
        url = u_ind(l1); crumb = crumb0 + [(l1, url)]
        subcards = "".join('<a class="card" href="%s"><h4>%s</h4><p>%d products</p></a>' % (u_ind(l1, l2), esc(l2), len(rows)) for l2, rows in subs.items())
        body = ('<div class="pagehead"><div class="wrap"><h1>%s</h1><p>Process-specific labels for %s, matched to temperature, chemistry and print method.</p></div></div>'
                '<div class="wrap"><div class="sec"><h2>Process areas</h2><div class="grid">%s</div></div>%s</div>' % (esc(l1), esc(l1.lower()), subcards, cta()))
        write(url, page("%s Labels | ETIA Label" % l1, "Specialty industrial labels for %s — matched by process, with free qualification samples." % l1.lower(),
            SITE + url, body, [bc_schema(crumb)], active="products", crumb=crumb))
        track(url, "industries")
        for l2, rows in subs.items():
            lurl = u_ind(l1, l2); lcrumb = crumb + [(l2, lurl)]
            prod = product_cards([(r["model"], r.get("seo")) for r in rows])
            faqs = [("What labels suit %s?" % l2.lower(), "The products below are matched to this process, supplied as genuine Polyonics, YS Tech or ETIA material with free qualification samples."),
                    ("Do you provide datasheets and samples?", "Yes — every listed part ships with the full datasheet and free samples so you can validate before ordering.")]
            body = ('<div class="pagehead"><div class="wrap"><h1>%s</h1><p>%s — recommended products, matched to this process.</p></div></div>'
                    '<div class="wrap"><div class="sec"><h2>Recommended products</h2>%s</div>'
                    '<div class="sec"><h2>FAQ</h2>%s</div>%s</div>' % (esc(l2), esc(l1), prod, faq_html(faqs), cta()))
            write(lurl, page("%s — %s Labels | ETIA Label" % (l2, l1), "%s labels for %s: matched products with Polyonics / YS Tech / ETIA and free samples." % (l2, l1.lower()),
                SITE + lurl, body, [bc_schema(lcrumb), faq_schema(faqs)], active="products", crumb=lcrumb))
            track(lurl, "industries")

def build_solution_path():
    crumb0 = [("Home", "/"), ("Products & Solutions", "/products/"), ("By Solution", "/products/by-solution/")]
    cards = "".join('<a class="card" href="%s"><h4>%s</h4><p>%d sub-processes · %d products</p></a>'
                    % (u_sol(l1), esc(l1), len(subs), sum(len(r) for r in subs.values())) for l1, subs in SOLUTIONS.items())
    body = ('<div class="pagehead"><div class="wrap"><h1>Labels by Solution</h1><p>Start from the production process or the problem — heat, chemistry, static, weather or compliance.</p></div></div>'
            '<div class="wrap"><div class="sec"><div class="grid">%s</div></div>%s</div>' % (cards, cta()))
    write("/products/by-solution/", page("Industrial Labels by Solution | ETIA Label",
        "Browse labels by process and problem: SMT reflow, heat-treatment, cold-chain, ESD, weatherproofing and compliance marking.",
        SITE + "/products/by-solution/", body, [bc_schema(crumb0)], active="products", crumb=crumb0))
    track("/products/by-solution/", "solutions")
    for l1, subs in SOLUTIONS.items():
        url = u_sol(l1); crumb = crumb0 + [(l1, url)]
        subcards = "".join('<a class="card" href="%s"><h4>%s</h4><p>%d products</p></a>' % (u_sol(l1, l2), esc(l2), len(rows)) for l2, rows in subs.items())
        body = ('<div class="pagehead"><div class="wrap"><h1>%s</h1><p>End-to-end labelling for this scenario, broken down by operation.</p></div></div>'
                '<div class="wrap"><div class="sec"><h2>Sub-scenarios</h2><div class="grid">%s</div></div>%s</div>' % (esc(l1), subcards, cta()))
        write(url, page("%s | ETIA Label" % l1, "%s — matched specialty labels by operation, with free qualification samples." % l1,
            SITE + url, body, [bc_schema(crumb)], active="products", crumb=crumb))
        track(url, "solutions")
        for l2, rows in subs.items():
            lurl = u_sol(l1, l2); lcrumb = crumb + [(l2, lurl)]
            prod = product_cards([(r["model"], r.get("seo")) for r in rows])
            faqs = [("Which products fit %s?" % l2.lower(), "The matched products are listed below, supplied as genuine Polyonics, YS Tech or ETIA material with free qualification samples."),
                    ("Do you provide datasheets and samples?", "Yes — every listed part ships with the datasheet and free samples so you can validate before ordering.")]
            body = ('<div class="pagehead"><div class="wrap"><h1>%s</h1><p>%s — recommended products for this operation.</p></div></div>'
                    '<div class="wrap"><div class="sec"><h2>Recommended products</h2>%s</div>'
                    '<div class="sec"><h2>FAQ</h2>%s</div>%s</div>' % (esc(l2), esc(l1), prod, faq_html(faqs), cta()))
            write(lurl, page("%s — %s | ETIA Label" % (l2, l1), "%s labels: matched products with Polyonics / YS Tech / ETIA." % l2,
                SITE + lurl, body, [bc_schema(lcrumb), faq_schema(faqs)], active="products", crumb=lcrumb))
            track(lurl, "solutions")

def material_tree():
    tree = {}
    for combined, rows in MATERIALS.items():
        base, prop = (combined.split("—", 1) + [""])[:2]
        tree.setdefault(base.strip(), {})[prop.strip()] = rows
    return tree

def build_material_path():
    crumb0 = [("Home", "/"), ("Products & Solutions", "/products/"), ("By Material", "/products/by-material/")]
    tree = material_tree()
    cards = "".join('<a class="card" href="%s"><h4>%s</h4><p>%d property groups · %d products</p></a>'
                    % (u_mat_base(base), esc(base), len(props), sum(len(r) for r in props.values())) for base, props in tree.items())
    body = ('<div class="pagehead"><div class="wrap"><h1>Labels by Base Material</h1><p>The film or metal sets the temperature ceiling, chemical resistance and print method.</p></div></div>'
            '<div class="wrap"><div class="sec"><div class="grid">%s</div></div>%s</div>' % (cards, cta()))
    write("/products/by-material/", page("Industrial Labels by Base Material | ETIA Label",
        "Browse by substrate: polyimide (PI), polyester (PET), ceramic & metal high-temp, low-temp specialty, flame-retardant & ESD, synthetic paper.",
        SITE + "/products/by-material/", body, [bc_schema(crumb0)], active="products", crumb=crumb0))
    track("/products/by-material/", "materials")
    for base, props in tree.items():
        url = u_mat_base(base); crumb = crumb0 + [(base, url)]
        subcards = "".join('<a class="card" href="%s"><h4>%s</h4><p>%d products</p></a>' % (u_mat(base, prop), esc(prop), len(rows)) for prop, rows in props.items())
        body = ('<div class="pagehead"><div class="wrap"><h1>%s</h1><p>%s label stock, grouped by performance property.</p></div></div>'
                '<div class="wrap"><div class="sec"><h2>Property groups</h2><div class="grid">%s</div></div>%s</div>' % (esc(base), esc(base), subcards, cta()))
        write(url, page("%s Labels | ETIA Label" % base, "%s label stock — by property, with Polyonics / YS Tech / ETIA options." % base,
            SITE + url, body, [bc_schema(crumb)], active="products", crumb=crumb))
        track(url, "materials")
        for prop, rows in props.items():
            lurl = u_mat(base, prop); lcrumb = crumb + [(prop, lurl)]
            prod = product_cards([(r["model"], r.get("seo")) for r in rows])
            body = ('<div class="pagehead"><div class="wrap"><h1>%s — %s</h1><p>Products on this substrate/property, matched to your process.</p></div></div>'
                    '<div class="wrap"><div class="sec"><h2>Products</h2>%s</div>%s</div>' % (esc(base), esc(prop), prod, cta()))
            write(lurl, page("%s — %s | ETIA Label" % (base, prop), "%s %s labels with Polyonics / YS Tech / ETIA options." % (base, prop),
                SITE + lurl, body, [bc_schema(lcrumb)], active="products", crumb=lcrumb))
            track(lurl, "materials")

def build_products():
    for slug, p in PRODUCTS.items():
        url = u_pdp(slug); name = p["label"] or p["model"]
        crumb = [("Home", "/"), ("Products & Solutions", "/products/"), (name, url)]
        specs = '<ul class="specs">'
        if p["poly"]: specs += '<li><span>Polyonics P/N</span><span>%s</span></li>' % esc(" · ".join(sorted(p["poly"])))
        if p["ys"]:   specs += '<li><span>YS&nbsp;Tech P/N</span><span>%s</span></li>' % esc(" · ".join(sorted(p["ys"])))
        if p["etia"]: specs += '<li><span>ETIA P/N</span><span>%s</span></li>' % esc(" · ".join(sorted(p["etia"])))
        if p["brady"]: specs += '<li><span>Brady equivalent (cross-ref)</span><span>%s</span></li>' % esc(" · ".join(sorted(p["brady"])))
        specs += '</ul>'
        xl = ""
        if p["collections"]:
            xl = '<div class="sec"><h2>Where this is used</h2><div class="xlinks">%s</div></div>' % "".join(
                '<a href="%s">%s</a>' % (cu, esc(ct)) for cu, ct in sorted(p["collections"].items(), key=lambda x: x[1]))
        brady_txt = (" It cross-references to Brady %s." % " / ".join(sorted(p["brady"]))) if p["brady"] else ""
        faqs = [("What is %s?" % name, "%s is a specialty industrial label supplied by ETIA as genuine, brand-authorized material.%s Send your temperature, surface and print method for an exact spec." % (name, brady_txt)),
                ("Which brand does this come from?", "Depending on availability we supply it as Polyonics, YS Tech or ETIA stock — all listed above. Brady numbers are provided only as a cross-reference."),
                ("Can I get samples?", "Yes — every part ships with free qualification samples and the full datasheet.")]
        chips = brand_chips(p) or '<span class="bchip etia">ETIA</span>'
        body = ('<div class="pagehead"><div class="wrap"><h1>%s</h1><p>%s</p><div class="certs" style="margin-top:12px">%s</div></div></div>'
                '<div class="wrap"><div class="sec"><h2>Part numbers &amp; equivalents</h2>%s<p class="lede" style="margin-top:10px">Genuine brand-authorized material — never grey-market. Brady numbers are cross-references only.</p></div>'
                '%s<div class="sec"><h2>FAQ</h2>%s</div>%s</div>'
                % (esc(name), esc(p["seo"] or "Specialty industrial label engineered for demanding environments."), chips, specs, xl, faq_html(faqs), cta()))
        sch = [bc_schema(crumb), faq_schema(faqs),
               {"@context": "https://schema.org", "@type": "Product", "name": name,
                "description": (p["seo"] or name), "brand": {"@type": "Brand", "name": "ETIA / Polyonics / YS Tech"}}]
        write(url, page("%s | ETIA Label" % name, ("%s — industrial specialty label. Polyonics / YS Tech / ETIA options%s Datasheet and free samples from ETIA." % (name, brady_txt))[:157],
            SITE + url, body, sch, active="products", crumb=crumb))
        track(url, "products")

# -------- content sections (frameworks; content to be filled later) --------
def placeholder_hub(url, title, lede, cards, active, group, extra=""):
    crumb = [("Home", "/"), (title, url)]
    cardhtml = "".join('<a class="card" href="%s"><h4>%s</h4><p>%s</p></a>' % (cu, esc(ct), esc(cd)) for ct, cu, cd in cards)
    body = ('<div class="pagehead"><div class="wrap"><h1>%s</h1><p>%s</p></div></div>'
            '<div class="wrap"><div class="sec"><div class="grid">%s</div></div>%s%s</div>' % (esc(title), esc(lede), cardhtml, extra, cta()))
    write(url, page("%s | ETIA Label" % title, lede[:157], SITE + url, body, [bc_schema(crumb)], active=active, crumb=crumb))
    track(url, group)

def build_applications():
    placeholder_hub("/applications/", "Applications", "Application notes — how to specify labels by heat, chemistry, static, weather and process. Detailed notes are being added.",
        [("SMT & PCB Assembly", "/products/by-solution/", "Reflow, wave-solder, ESD, wash."),
         ("High-Temp Heat-Treatment", "/products/by-industry/", "300–1300 °C metal & ceramic."),
         ("Cold-Chain & Cryogenic", "/products/by-material/", "−20 to −196 °C storage."),
         ("Outdoor & Weatherproofing", "/products/by-solution/", "UV, moisture, oil, 25-year.")], "applications", "core",
        extra='<div class="sec"><div class="note"><b>More application notes coming.</b> In the meantime, tell us your process and we\'ll send the matched specification and samples.</div></div>')

def build_insights():
    placeholder_hub("/insights/", "Insights", "Case studies, articles and technical know-how from the ETIA engineering team.",
        [("Case Studies", "/insights/case-studies/", "Real deployments in tough environments."),
         ("Blog", "/insights/blog/", "Selection guides and label engineering."),
         ("Resources", "/insights/resources/", "Datasheets, guides and downloads.")], "insights", "insights")
    for slug, t, lede in [("case-studies", "Case Studies", "Real-world label deployments in extreme heat, cold, chemical and outdoor environments. Case studies are being added."),
                          ("blog", "Blog", "Articles, selection guides and label-engineering know-how. New posts are on the way."),
                          ("resources", "Resources", "Datasheets, selection guides and downloads. The resource library is being populated.")]:
        url = "/insights/%s/" % slug; crumb = [("Home", "/"), ("Insights", "/insights/"), (t, url)]
        body = ('<div class="pagehead"><div class="wrap"><h1>%s</h1><p>%s</p></div></div>'
                '<div class="wrap"><div class="sec"><div class="note"><b>Content coming soon.</b> Want a specific %s? Contact us and we\'ll share what\'s relevant to your application.</div></div>%s</div>'
                % (esc(t), esc(lede), esc(t.lower().rstrip("s")), cta()))
        write(url, page("%s | ETIA Label" % t, lede[:157], SITE + url, body, [bc_schema(crumb)], active="insights", crumb=crumb))
        track(url, "insights")

def build_support():
    crumb = [("Home", "/"), ("Service & Support", "/support/")]
    guide = "".join('<div class="card"><h4>%s</h4><p>%s</p></div>' % (esc(t), esc(d)) for t, d in [
        ("By temperature", "Under 150 °C: PET/PP. 150–300 °C: polyimide. 300–600 °C: aluminium/nickel foil. Above 600 °C: inorganic ceramic to 1300 °C."),
        ("By environment", "Cryo/LN2 → PP or specialty to −196 °C. Chemical/oil → top-coated PET or PI. Outdoor → UV-stable PET/PVC."),
        ("By print method", "Thermal transfer, laser or pre-print — each needs a compatible top-coat. Tell us your printer and ribbon."),
        ("By compliance", "UL94 V-0, ESD, FMVSS-302, autoclave, IATF 16949, ISO 13485 — filterable across the catalog.")])
    body = ('<div class="pagehead"><div class="wrap"><h1>Service &amp; Support</h1><p>Selection guidance, Brady cross-reference, samples and technical FAQ.</p></div></div>'
            '<div class="wrap"><div class="sec"><h2>Selection guide</h2><div class="grid">%s</div></div>'
            '<div class="sec"><h2>Brady cross-reference</h2><p class="lede">Searching a Brady part number? Find the equivalent Polyonics, YS&nbsp;Tech or ETIA product.</p>'
            '<a class="btn blue" href="/support/brady-cross-reference/">Open the Brady cross-reference →</a></div>'
            '<div class="sec"><h2>Samples &amp; datasheets</h2><p class="lede">Every product ships with free qualification samples and the full datasheet.</p>'
            '<a class="btn" href="/contact/">Request samples</a></div>%s</div>' % (guide, cta()))
    write("/support/", page("Service & Support — Label Selection & Brady Cross-Reference | ETIA Label",
        "Choose industrial labels by temperature, environment, print method and compliance. Brady cross-reference, datasheets and free samples.",
        SITE + "/support/", body, [bc_schema(crumb)], active="support", crumb=crumb))
    track("/support/", "core")
    # Brady cross-reference table
    rows = []
    for slug, p in sorted(PRODUCTS.items(), key=lambda kv: kv[1]["label"]):
        for b in sorted(p["brady"]):
            rows.append('<tr><td class="mono">%s</td><td><a href="%s">%s</a></td><td>%s</td></tr>'
                        % (esc(b), u_pdp(slug), esc(p["label"] or p["model"]), brand_chips(p) or '<span class="bchip etia">ETIA</span>'))
    bcrumb = [("Home", "/"), ("Service & Support", "/support/"), ("Brady Cross-Reference", "/support/brady-cross-reference/")]
    body = ('<div class="pagehead"><div class="wrap"><h1>Brady Cross-Reference</h1><p>Find the Polyonics, YS&nbsp;Tech or ETIA equivalent for a Brady part number. Brady numbers are references only — the products we supply are Polyonics, YS&nbsp;Tech and ETIA.</p></div></div>'
            '<div class="wrap"><div class="sec"><p class="lede">%d cross-referenced entries. Send any number not listed and we\'ll match it.</p>'
            '<div class="tablewrap"><table class="matrix"><thead><tr><th>Brady Part</th><th>ETIA Equivalent</th><th>Available brands</th></tr></thead><tbody>%s</tbody></table></div></div>%s</div>'
            % (len(rows), "".join(rows), cta()))
    write("/support/brady-cross-reference/", page("Brady Label Cross-Reference | ETIA Label",
        "Find Polyonics, YS Tech and ETIA equivalents for Brady industrial label part numbers, with free qualification samples.",
        SITE + "/support/brady-cross-reference/", body, [bc_schema(bcrumb)], active="support", crumb=bcrumb))
    track("/support/brady-cross-reference/", "core")

def build_company():
    crumb = [("Home", "/"), ("Company", "/company/")]
    body = ("""<div class="pagehead"><div class="wrap"><h1>Your solution partner for labels that perform where ordinary ones fail.</h1>
<p>For over 20 years, ETIA has been a trusted partner for the labeling challenges most suppliers avoid.</p></div></div>
<div class="wrap">
<div class="sec"><h2>High-complexity is our specialty</h2>
<p class="lede">While others chase high-volume, standardized runs, we specialize in high-complexity requirements — durable and specialty labels engineered for the toughest conditions. As your solution partner, we start from your application, not a product catalog.</p>
<p style="color:var(--mut);max-width:820px">We study the full environment — surface, temperature, chemical exposure, printing method, barcode requirement and product lifecycle — then engineer labels that stay bonded, readable and reliable where ordinary labels fail: through extreme heat up to <b>1300&nbsp;°C</b>, cryogenic cold down to <b>−196&nbsp;°C</b>, harsh chemicals, oily surfaces and modern lead-free PCB assembly.</p></div>
%s
%s
<div class="sec"><h2>The details behind every solution</h2>
<p style="color:var(--mut);max-width:820px">We supply genuine, brand-authorized materials — never grey-market substitutes. With full in-house slitting and die-cutting capability plus local stock, we deliver faster to printers, converters and end users alike. From material selection and sample testing to ongoing technical support, we stay with you for the long term.</p>
<p style="max-width:820px;font-size:17px;color:var(--blue-deep);font-weight:700;margin-top:14px">We don't just supply labels. We partner with you to solve identification problems where failure is not an option.</p>
<p style="color:var(--mut);margin-top:8px">ETIA — Your Solution Partner. Engineering Success.</p></div>
%s</div>""" % (TRUST, BRANDS_MATRIX, cta()))
    sch = [bc_schema(crumb), {"@context": "https://schema.org", "@type": "AboutPage", "name": "About ETIA Label",
           "description": "ETIA is a solution partner for durable and specialty industrial labels, with 20 years' experience, sole agencies for Polyonics and YS Tech, and in-house die-cutting and slitting."}]
    write("/company/", page("Company — Your Solution Partner | ETIA Label",
        "For over 20 years ETIA has engineered durable, specialty labels for the toughest conditions. Sole agent for Polyonics (USA) & YS Tech (Japan), with in-house die-cutting and slitting.",
        SITE + "/company/", body, sch, active="company", crumb=crumb))
    track("/company/", "core")

def build_contact():
    crumb = [("Home", "/"), ("Contact", "/contact/")]
    body = ("""<div class="pagehead"><div class="wrap"><h1>Talk to your local ETIA team.</h1>
<p>Tell us your application — surface, temperature, chemical exposure and print method — and we'll return the matched part with a datasheet and free samples, often within one working day.</p></div></div>
<div class="wrap"><div class="sec"><h2>Global contacts</h2><p class="lede">Local sales and technical support across Greater China and Southeast Asia.</p>%s</div>
<div class="cta"><h3>Prefer to send your spec now?</h3><p>Email your temperature range, substrate and a competitor part number if you have one — we'll match it and ship samples.</p>
<div class="btns"><a class="btn" href="mailto:label@etia-tech.com">Email ETIA</a><a class="btn ghost" href="/products/">Explore Products</a></div></div></div>""" % office_cards())
    sch = [bc_schema(crumb), {"@context": "https://schema.org", "@type": "ContactPage", "name": "Contact ETIA Label",
           "mainEntity": {"@type": "Organization", "name": "ETIA Label", "url": SITE, "contactPoint": contact_points()}}]
    write("/contact/", page("Contact ETIA — Global Offices (China, HK, Thailand, Vietnam) | ETIA Label",
        "Contact your local ETIA team in Shanghai, Hong Kong, Bangkok or Bac Ninh for industrial specialty labels, spec matching and free samples.",
        SITE + "/contact/", body, sch, active="contact", crumb=crumb))
    track("/contact/", "core")

# ------------------------------------------------------------------ sitemaps
def build_sitemaps():
    groups = {}
    for uu, g in ALL_URLS:
        groups.setdefault(g, []).append(uu)
    smap = {"core": "sitemap-core.xml", "industries": "sitemap-industries.xml", "solutions": "sitemap-solutions.xml",
            "materials": "sitemap-materials.xml", "products": "sitemap-products.xml", "insights": "sitemap-insights.xml"}
    for g, fn in smap.items():
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for uu in groups.get(g, []):
            xml += '  <url><loc>%s%s</loc><changefreq>weekly</changefreq></url>\n' % (SITE, uu)
        xml += '</urlset>\n'
        open(os.path.join(ROOT, fn), "w").write(xml)
    idx = '<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for fn in smap.values():
        idx += '  <sitemap><loc>%s/%s</loc></sitemap>\n' % (SITE, fn)
    idx += '</sitemapindex>\n'
    open(os.path.join(ROOT, "sitemap-index.xml"), "w").write(idx)
    open(os.path.join(ROOT, "robots.txt"), "w").write("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap-index.xml\n" % SITE)

# ------------------------------------------------------------------ run
for d in ["products", "applications", "insights", "support", "company", "contact",
          "industries", "materials", "brands", "technical-resources", "about"]:
    p = os.path.join(ROOT, d)
    if os.path.isdir(p):
        shutil.rmtree(p)
for f in os.listdir(ROOT):
    if f.startswith("sitemap") or f == "robots.txt":
        os.remove(os.path.join(ROOT, f))

register_all()
build_home()
build_products_landing()
build_industry_path()
build_solution_path()
build_material_path()
build_products()
build_applications()
build_insights()
build_support()
build_company()
build_contact()
build_sitemaps()

from collections import Counter
print("Unique products:", len(PRODUCTS))
print("Pages tracked:", len(ALL_URLS))
print(Counter(g for _, g in ALL_URLS))
