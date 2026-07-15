#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ETIA · HEATPROOF (ultra-high-temperature labels & tags) — dual-path site generator.
Implements the approved architecture: Industry path + Process path -> one canonical product
page each. Data-driven from _build/data/heatproof.json. English + /zh/ with reciprocal hreflang.
ETIA is presented as supplier / application-support partner, NOT the manufacturer.
Temperature parameters are taken verbatim from the brief; none are invented. Items needing
datasheet verification are marked.  Build = run this script; output written to repo root."""
import json, os, re, html, shutil

BUILD_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BUILD_DIR)
DATA = json.load(open(os.path.join(BUILD_DIR, "data", "heatproof.json")))
SITE = "https://www.etialabel.com"

PATHS = {p["id"]: p for p in DATA["process_paths"]}
PRODUCTS = {p["id"]: p for p in DATA["products"]}
INDUSTRIES = {i["id"]: i for i in DATA["industries"]}
APPS = DATA["applications"]

LANGS = ["en", "zh"]
PREFIX = {"en": "", "zh": "/zh"}
HREFLANG = {"en": "en", "zh": "zh"}

def esc(s): return html.escape(str(s or ""), quote=True)

# ---------------------------------------------------------------- URLs
def u_products(): return "/products/"
def u_line(pid): return "/products/%s/" % PATHS[pid]["slug"]
def u_prod(slug): return "/products/%s/" % slug
def u_ind_hub(): return "/industries/"
def u_industry(iid):
    i = INDUSTRIES[iid]
    base = "/industries/" if i["parent_type"] == "industry" else "/applications/"
    return "%s%s/" % (base, i["slug"])
def u_app(parent, slug):
    return "%s%s/" % (u_industry(parent), slug)

def L(lang, path):  # localize a site-relative path
    return PREFIX[lang] + path

# ---------------------------------------------------------------- design system (finalized brand)
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{--ink:#141b2d;--mut:#5c6678;--faint:#8a93a3;--line:#e7ebf2;--bg:#f6f8fc;--mint:#f1f7ef;
--blue-deep:#143C96;--blue:#1A56DB;--green:#41A62A;--green-d:#358B22;
--serif:'Iowan Old Style','Palatino Linotype','Palatino','Georgia',serif;
--sans:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif}
body{font-family:var(--sans);color:var(--ink);background:#fff;line-height:1.65;-webkit-font-smoothing:antialiased}
a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}
img{max-width:100%}
.wrap{max-width:1180px;margin:0 auto;padding:0 24px}
.eyebrow{font-size:12.5px;font-weight:700;letter-spacing:.15em;text-transform:uppercase;color:var(--blue)}
.serif{font-family:var(--serif)}
.topstrip{height:3px;background:linear-gradient(90deg,var(--blue-deep),var(--blue) 60%,var(--green))}
header{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:40}
header .wrap{display:flex;align-items:center;justify-content:space-between;height:70px;gap:16px}
.logo{display:flex;align-items:center;font-weight:800;font-size:22px}
.logo .ar{color:var(--green);margin-right:2px}.logo .grn{color:var(--green)}.logo .blu{color:var(--blue-deep)}
nav{display:flex;align-items:center;gap:26px}
nav a{font-size:14.5px;font-weight:600;color:var(--ink);white-space:nowrap}
nav a:hover{color:var(--blue)}nav a.on{color:var(--blue)}
nav .lang{font-size:13px;color:var(--faint);border:1px solid var(--line);border-radius:8px;padding:5px 10px}
@media(max-width:900px){nav a:not(.lang){display:none}}
.crumb{font-size:13px;color:var(--mut);padding:16px 0}
.crumb a{color:var(--mut)}.crumb b{color:var(--ink)}
.btn{display:inline-block;font-weight:700;font-size:15px;padding:12px 24px;border-radius:10px}
.btn.pri{background:var(--green);color:#fff}.btn.pri:hover{background:var(--green-d);text-decoration:none}
.btn.sec{border:1.5px solid var(--ink);color:var(--ink)}.btn.sec:hover{background:var(--ink);color:#fff;text-decoration:none}
.pagehead{padding:34px 0 8px}
.pagehead h1{font-family:var(--serif);font-weight:600;font-size:38px;line-height:1.1;text-wrap:balance;max-width:20em}
.pagehead .lede{margin-top:14px;color:var(--mut);font-size:18px;max-width:44em}
.pagehead .btns{margin-top:22px;display:flex;gap:12px;flex-wrap:wrap}
section.blk{padding:34px 0}
.blk h2{font-family:var(--serif);font-weight:600;font-size:26px;color:var(--ink);margin-bottom:6px}
.blk h2+.sub{color:var(--mut);margin-bottom:16px;max-width:46em}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}
.card{border:1px solid var(--line);border-radius:14px;padding:22px;background:#fff;transition:.15s;display:block}
.card:hover{border-color:var(--blue);box-shadow:0 8px 26px rgba(26,86,219,.10);text-decoration:none}
.card h3{font-size:18px;color:var(--blue-deep);margin-bottom:6px}
.card p{font-size:14px;color:var(--mut)}
.card .rows{margin-top:12px;font-size:13px;color:var(--mut)}
.card .rows b{color:var(--ink)}
.pill{display:inline-block;font-size:11px;font-weight:700;padding:3px 9px;border-radius:20px;background:#eaf1ff;color:var(--blue);border:1px solid #d6e2fb;margin:2px 3px 0 0}
.pill.tag{background:#fef3e8;color:#b45309;border-color:#f4d9bd}
.tablewrap{overflow-x:auto;margin-top:8px}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{text-align:left;padding:11px 12px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:var(--bg);font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--mut)}
td.mono{font-family:ui-monospace,Menlo,monospace;font-weight:600}
.two{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.tcard{border:1px solid var(--line);border-radius:12px;padding:16px;background:var(--bg)}
.tcard .k{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--mut)}
.tcard .v{font-size:18px;font-weight:700;color:var(--blue-deep);margin-top:4px}
ul.checks{list-style:none;margin-top:8px}
ul.checks li{padding:7px 0 7px 26px;position:relative;font-size:14.5px;color:var(--mut);border-bottom:1px solid var(--line)}
ul.checks li::before{content:"→";position:absolute;left:0;color:var(--blue);font-weight:700}
.verify{background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:12px 16px;font-size:13.5px;color:#92400e;margin-top:14px}
.xlinks{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
.xlinks a{font-size:13px;background:var(--bg);border:1px solid var(--line);padding:7px 13px;border-radius:20px;color:var(--ink)}
.cta{background:linear-gradient(155deg,var(--blue),var(--blue-deep));color:#fff;border-radius:18px;padding:40px;text-align:center;margin:26px 0}
.cta .ic{font-size:28px;color:#8fe063}
.cta h3{font-size:26px;font-weight:800;margin-top:4px;text-wrap:balance}
.cta p{color:#d3ddf3;margin:12px auto 20px;max-width:40em}
.cta .btns{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.btn.on-dark{border:1.5px solid #ffffff66;color:#fff}.btn.on-dark:hover{background:#fff;color:var(--blue-deep);text-decoration:none}
footer{background:#f3f5f8;color:var(--mut);padding:48px 0 26px;font-size:14px;border-top:1px solid var(--line);margin-top:20px}
footer .flogo{font-weight:800;font-size:21px;margin-bottom:22px}
footer .fg{display:grid;grid-template-columns:1fr 1fr 1.3fr;gap:26px}
footer h5{color:var(--blue);font-size:14px;font-weight:700;margin-bottom:12px}
footer ul{list-style:none;display:flex;flex-direction:column;gap:8px}
footer a{color:var(--mut)}footer a:hover{color:var(--blue)}
footer .email{color:var(--green);font-weight:600}
footer .bar{border-top:1px solid var(--line);margin-top:30px;padding-top:16px;color:var(--faint);font-size:12.5px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}
/* home */
.hero{padding:60px 0 46px}
.hero .eyebrow{margin-bottom:14px}
.hero h1{font-family:var(--serif);font-weight:600;font-size:46px;line-height:1.08;letter-spacing:-.01em;text-wrap:balance;max-width:16em}
.hero .lede{margin-top:18px;color:var(--mut);font-size:19px;max-width:40em}
.hero .btns{margin-top:26px;display:flex;gap:12px;flex-wrap:wrap}
.svcbar{background:linear-gradient(155deg,var(--blue),var(--blue-deep));color:#fff}
.svcbar .wrap{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;padding:20px 24px}
.svcbar .i{font-size:14.5px;font-weight:600;display:flex;gap:9px;align-items:flex-start}
.svcbar .i::before{content:"✓";color:#8fe063;font-weight:800;flex:none}
.whygrid{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}
.why{border-top:2px solid var(--line);padding-top:14px}
.why .n{font-family:var(--serif);font-size:15px;color:var(--faint)}
.why b{display:block;font-family:var(--serif);font-size:20px;color:var(--blue-deep);margin:2px 0 6px}
.why p{font-size:14px;color:var(--mut)}
.brandwall{display:flex;flex-wrap:wrap;gap:10px;margin-top:6px}
.bchip{display:inline-block;font-size:12px;font-weight:700;padding:6px 14px;border-radius:22px;background:var(--bg);border:1px solid var(--line);color:var(--ink)}
@media(max-width:820px){.two{grid-template-columns:1fr}footer .fg{grid-template-columns:1fr}.pagehead h1{font-size:30px}
.hero h1{font-size:32px}.svcbar .wrap{grid-template-columns:1fr 1fr}.whygrid{grid-template-columns:1fr 1fr}}
"""

NAV_ITEMS = [("Products", u_products(), "products"),
             ("Industries &amp; Applications", u_ind_hub(), "industries"),
             ("Technical Resources", "/technical-resources/", "tech"),
             ("About ETIA", "/about/", "about"),
             ("Contact", "/contact/", "contact")]
NAV_ZH = {"Products":"产品中心","Industries &amp; Applications":"行业与应用",
          "Technical Resources":"技术资源","About ETIA":"关于ETIA","Contact":"联系我们"}

ALL_URLS = []   # (path, group, changefreq)  — English canonical set for sitemap
def track(path, group): ALL_URLS.append((path, group))

def hreflang_block(path):
    t = []
    for lg in LANGS:
        t.append('<link rel="alternate" hreflang="%s" href="%s">' % (HREFLANG[lg], SITE + PREFIX[lg] + path))
    t.append('<link rel="alternate" hreflang="x-default" href="%s">' % (SITE + path))  # EN is x-default
    return "".join(t)

def breadcrumb_jsonld(items, lang):
    return {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":i+1,"name":n,"item":SITE+PREFIX[lang]+p} for i,(n,p) in enumerate(items)]}

def nav_html(lang, active, path="/"):
    def lab(t): return NAV_ZH[t] if lang == "zh" else t
    items = "".join('<a href="%s"%s>%s</a>' % (L(lang, href), ' class="on"' if key==active else '', lab(t))
                    for t, href, key in NAV_ITEMS)
    other = "zh" if lang == "en" else "en"
    other_label = "中文" if lang == "en" else "EN"   # label = the language you switch TO
    return '<nav>%s<a class="lang" href="%s">%s</a></nav>' % (items, L(other, path), other_label)

FOOTER_LINKS = [("Products", u_products()), ("Industries & Applications", u_ind_hub()),
                ("Technical Resources", "/technical-resources/"), ("About ETIA", "/about/")]
def footer_html(lang):
    nav = "".join('<li><a href="%s">%s</a></li>' % (L(lang, p), t) for t, p in FOOTER_LINKS)
    legal = "".join('<li><a href="%s">%s</a></li>' % (L(lang, p), t) for t, p in
                    [("Privacy Policy","/privacy/"),("Cookie Policy","/cookies/"),("Terms of Use","/terms/")])
    return """<footer><div class="wrap">
<div class="flogo"><span class="ar">◄</span><span class="grn">ETIA</span><span class="blu">·LABEL</span></div>
<div class="fg">
<div><h5>Navigation</h5><ul>%s</ul></div>
<div><h5>Legal</h5><ul>%s</ul></div>
<div><h5>Contact</h5><a class="email" href="mailto:label@etia-tech.com">label@etia-tech.com</a><br><br>
Shanghai · Hong Kong · Bangkok · Bac Ninh<br><span style="color:var(--faint)">Supplier &amp; application-support partner — genuine, brand-authorized materials.</span></div>
</div>
<div class="bar"><span>© 2026 ETIA-TECH (ASIA) Co., Limited. All rights reserved.</span><span><a href="%s">Privacy</a> &nbsp; <a href="%s">Cookies</a></span></div>
</div></footer>""" % (nav, legal, L(lang,"/privacy/"), L(lang,"/cookies/"))

def cta(lang):
    if lang == "zh":
        return """<div class="cta"><div class="ic">⚡</div><h3>提供工况，我们匹配材料并寄样验证。</h3>
<p>告知贴标时的物件温度、后续最高工艺温度、表面与附着方式,我们推荐方案并安排样品。</p>
<div class="btns"><a class="btn pri" href="%s">申请样品</a><a class="btn on-dark" href="%s">咨询工程师</a></div></div>""" % (L(lang,"/contact/"), L(lang,"/contact/"))
    return """<div class="cta"><div class="ic">⚡</div><h3>Tell us the process. We'll match the material and validate by sample.</h3>
<p>Share the object temperature at application, the maximum later process temperature, the surface and the attachment method — we'll recommend an approach and arrange samples.</p>
<div class="btns"><a class="btn pri" href="%s">Request a Sample</a><a class="btn on-dark" href="%s">Talk to an Engineer</a></div></div>""" % (L(lang,"/contact/"), L(lang,"/contact/"))

def page(lang, path, title, desc, h1, lede, body, crumb, schema_extra=None, active=""):
    canonical = SITE + PREFIX[lang] + path
    sch = [breadcrumb_jsonld(crumb, lang)] + (schema_extra or [])
    schema_js = "".join('<script type="application/ld+json">%s</script>' % json.dumps(s, ensure_ascii=False) for s in sch)
    cr = ' &rsaquo; '.join((('<a href="%s">%s</a>' % (L(lang,p), esc(n))) if p and i < len(crumb)-1 else '<b>%s</b>' % esc(n))
                           for i,(n,p) in enumerate(crumb))
    lede_html = ('<p class="lede">%s</p>' % lede) if lede else ""
    return """<!doctype html><html lang="%s"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title><meta name="description" content="%s">
<link rel="canonical" href="%s">%s
<meta property="og:title" content="%s"><meta property="og:type" content="website"><meta property="og:site_name" content="ETIA Label">
<style>%s</style>%s</head><body>
<div class="topstrip"></div>
<header><div class="wrap"><a class="logo" href="%s"><span class="ar">◄</span><span class="grn">ETIA</span><span class="blu">·LABEL</span></a>%s</div></header>
<div class="wrap"><div class="crumb">%s</div></div>
<div class="wrap"><div class="pagehead"><h1>%s</h1>%s</div></div>
%s
%s
</body></html>""" % (lang, esc(title), esc(desc), canonical, hreflang_block(path), esc(title), CSS, schema_js,
     L(lang,"/"), nav_html(lang, active, path), cr, esc(h1), lede_html, body, footer_html(lang))

def write(lang, path, content):
    full = os.path.join(ROOT, (PREFIX[lang] + path).strip("/"), "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(content)

VERIFY_EN = "Temperature figures are indicative and taken from product-line references; verify against the current technical datasheet and by application testing before production."
VERIFY_ZH = "温度数值为参考值,源自产品线资料;量产前请以最新技术数据表为准并经应用测试确认。"

# ---------------------------------------------------------------- builders
def prod_type_pill(p):
    return '<span class="pill tag">Tag</span>' if p["type"]=="tag" else '<span class="pill">Label</span>'

def line_products(pid):
    return [PRODUCTS[x] for x in PRODUCTS if pid in PRODUCTS[x]["process_paths"]]

def build_products_hub(lang):
    cards = ""
    for pid in ["direct_hot_application","heat_treatment_labels","heat_treatment_tags"]:
        pp = PATHS[pid]; prods = line_products(pid)
        title = pp["title_zh"] if lang=="zh" else pp["title_en"]
        temps = [PRODUCTS[x]["max_proc"] for x in PRODUCTS if pid in PRODUCTS[x]["process_paths"]]
        cards += ('<a class="card" href="%s"><h3>%s</h3><p>%s</p>'
                  '<div class="rows"><b>%d</b> products · format: %s</div></a>') % (
            L(lang,u_line(pid)), esc(title),
            ("面向该工艺的材料选择。" if lang=="zh" else "Material selection focused on this process."),
            len(prods), ("吊牌" if pp["type"]=="tag" else "标签") if lang=="zh" else pp["type"])
    body = ('<section class="blk"><div class="wrap"><h2>%s</h2><div class="sub">%s</div><div class="grid">%s</div></div></section>'
            '<div class="wrap">%s</div>') % (
        ("三条工艺产品线" if lang=="zh" else "Three process product lines"),
        ("按贴标方式与工艺温度选择。不把所有单品直接堆在总览页。" if lang=="zh" else "Choose by how the label or tag is applied and the process it must survive."),
        cards, cta(lang))
    h1 = "工业追溯用超高温标签与吊牌" if lang=="zh" else "Ultra-High-Temperature Labels and Tags for Industrial Traceability"
    lede = ("面向钢铁、铝业、陶瓷、混凝土等高温工艺的标识方案。ETIA 供应 YS-Tech HEATPROOF 材料并提供应用支持。" if lang=="zh"
            else "Identification that survives casting, rolling, annealing, firing and repeated heat cycles. ETIA supplies YS-Tech HEATPROOF materials with application support.")
    crumb = [("Home","/"),("Products",u_products())]
    write(lang, u_products(), page(lang, u_products(),
        ("超高温标签与吊牌 | ETIA" if lang=="zh" else "Ultra-High-Temperature Labels & Tags | ETIA"),
        ("面向高温工艺的直贴标签、热处理标签与吊牌 — 钢铁/铝/陶瓷/混凝土。" if lang=="zh"
         else "Ultra-high-temperature labels and tags for direct hot application, heat-treatment and tagging across steel, aluminum, ceramics and concrete."),
        h1, lede, body, crumb, active="products"))
    if lang=="en": track(u_products(),"core")

LINE_SECTIONS = {
 "direct_hot_application":{
   "def_en":"Labels are applied directly to steel, aluminum or other metal while the surface is still hot. Identification begins early in casting, rolling or hot-forming and can continue through downstream production.",
   "def_zh":"标签在金属表面仍处于高温时直接贴附于钢、铝或其他金属制品。标识在铸造、轧制或热成形早期即开始,并可延续至下游工序。",
   "sections_en":["What direct hot application means","Why conventional pressure-sensitive labels fail","Heat-activated adhesion","Manual and robotic application","Variable thermal-transfer printing and barcodes","Application-temperature versus maximum-process-temperature"],
 },
 "heat_treatment_labels":{
   "def_en":"Labels are normally applied at room temperature or lower, then remain with the product through annealing, homogenizing, firing, reflow, autoclave or repeated heat cycles.",
   "def_zh":"标签通常在常温或较低温度下贴附,随后随产品经历退火、均质、烧成、回流、高压灭菌或反复热循环。",
   "sections_en":["Applied before heating","Annealing, homogenizing, firing, reflow and autoclave","Temperature, atmosphere and dwell-time selection","Adhesion on smooth versus rough surfaces","Chemical, pickling and multiple-cycle exposure","Printing and barcode readability"],
 },
 "heat_treatment_tags":{
   "def_en":"Tags are used where pressure-sensitive labels are not suitable, or where products must survive long heat exposure, pickling, galvanizing, multiple heat cycles or mechanical impact. Tags attach by nail, screw, spot/stud welding or other mechanical methods.",
   "def_zh":"当压敏标签不适用,或产品需经受长时间高温、酸洗、镀锌、多次热循环或机械冲击时,采用吊牌。吊牌可通过钉、螺钉、点焊/植焊等机械方式附着。",
   "sections_en":["When to use a tag instead of an adhesive label","Nail, screw and welding attachment","Long-duration heat-treatment tracking","Pickling, acid bath, galvanizing and coating exposure","Printing, cutting and barcode scanning","Attachment-method validation"],
 },
}

def build_process_line(lang, pid):
    pp = PATHS[pid]; meta = LINE_SECTIONS[pid]
    prods = line_products(pid)
    # comparison table
    if pid == "direct_hot_application":
        head = ["Product","Application temperature","Maximum process resistance","Main direction"] if lang=="en" else ["型号","贴标温度","最高工艺耐温","主要方向"]
        rows = "".join('<tr><td class="mono"><a href="%s">%s</a></td><td>%s</td><td>%s</td><td>%s</td></tr>'
                       % (L(lang,u_prod(p["slug"])), esc(p["name"]), esc(p["app_temp"] or "—"), esc(p["max_proc"]), esc(p["note"]))
                       for p in prods)
    else:
        head = ["Product","Maximum heat resistance","Key direction"] if lang=="en" else ["型号","最高耐温","关键方向"]
        rows = "".join('<tr><td class="mono"><a href="%s">%s</a></td><td>%s</td><td>%s</td></tr>'
                       % (L(lang,u_prod(p["slug"])), esc(p["name"]), esc(p["max_proc"]), esc(p["note"]))
                       for p in prods)
    table = '<div class="tablewrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (
        "".join("<th>%s</th>"%h for h in head), rows)
    seclist = "".join("<li>%s</li>" % esc(s) for s in meta["sections_en"]) if lang=="en" else ""
    sec_en = ('<section class="blk"><div class="wrap"><h2>What this line covers</h2><ul class="checks">%s</ul></div></section>' % seclist) if lang=="en" else ""
    industries_here = sorted({i for p in prods for i in p["industries"]})
    ind_links = "".join('<a href="%s">%s</a>' % (L(lang,u_industry(i)), esc(INDUSTRIES[i]["title_zh"] if lang=="zh" else INDUSTRIES[i]["title_en"])) for i in industries_here)
    others = "".join('<a href="%s">%s</a>' % (L(lang,u_line(o)), esc(PATHS[o]["title_zh"] if lang=="zh" else PATHS[o]["title_en"])) for o in PATHS if o!=pid)
    body = ('<section class="blk"><div class="wrap"><h2>%s</h2><div class="sub">%s</div></div></section>'
            '<section class="blk"><div class="wrap"><h2>%s</h2>%s<div class="verify">%s</div></div></section>'
            '%s'
            '<section class="blk"><div class="wrap"><h2>%s</h2><div class="xlinks">%s</div></div></section>'
            '<section class="blk"><div class="wrap"><h2>%s</h2><div class="xlinks">%s</div></div></section>'
            '<div class="wrap">%s</div>') % (
        ("工艺定义" if lang=="zh" else "Process definition"), esc(meta["def_zh"] if lang=="zh" else meta["def_en"]),
        ("产品对比" if lang=="zh" else "Product comparison"), table, (VERIFY_ZH if lang=="zh" else VERIFY_EN),
        sec_en,
        ("行业应用" if lang=="zh" else "Industry applications"), ind_links or "—",
        ("其他工艺线" if lang=="zh" else "Related process lines"), others,
        cta(lang))
    # ItemList structured data (visible product list matches markup)
    itemlist = {"@context":"https://schema.org","@type":"ItemList","itemListElement":[
        {"@type":"ListItem","position":i+1,"name":p["name"],"url":SITE+PREFIX[lang]+u_prod(p["slug"])} for i,p in enumerate(prods)]}
    h1 = pp["h1_zh"] if lang=="zh" else pp["h1_en"]
    crumb = [("Home","/"),("Products",u_products()),(pp["title_zh"] if lang=="zh" else pp["title_en"], u_line(pid))]
    write(lang, u_line(pid), page(lang, u_line(pid),
        "%s | ETIA" % (pp["title_zh"] if lang=="zh" else pp["title_en"]),
        esc(meta["def_zh"] if lang=="zh" else meta["def_en"])[:157],
        h1, "", body, crumb, schema_extra=[itemlist], active="products"))
    if lang=="en": track(u_line(pid),"products")

def build_product(lang, p):
    slug = p["slug"]; url = u_prod(slug)
    paths = [PATHS[x] for x in p["process_paths"]]
    path_badges = "".join('<a class="pill" href="%s">%s</a>' % (L(lang,u_line(x)), esc(PATHS[x]["title_zh"] if lang=="zh" else PATHS[x]["title_en"])) for x in p["process_paths"])
    # separated temperature cards (critical rule)
    tcards = ""
    if p["app_temp"]:
        tcards += '<div class="tcard"><div class="k">%s</div><div class="v">%s</div></div>' % (("贴标时物件温度" if lang=="zh" else "Application temperature"), esc(p["app_temp"]))
    tcards += '<div class="tcard"><div class="k">%s</div><div class="v">%s</div></div>' % (("最高工艺耐温" if lang=="zh" else "Maximum process resistance"), esc(p["max_proc"]))
    # applications using this product (reverse links)
    applinks = ""
    for a in APPS:
        if slug in a["recommended"]:
            applinks += '<a href="%s">%s</a>' % (L(lang,u_app(a["parent"],a["slug"])), esc(a["title_en"]))
    # alternatives = same process path, nearest
    alts = [q for q in line_products(p["process_paths"][0]) if q["id"]!=slug][:4]
    altlinks = "".join('<a href="%s">%s — %s</a>' % (L(lang,u_prod(q["slug"])), esc(q["name"]), esc(q["max_proc"])) for q in alts)
    body = ('<section class="blk"><div class="wrap"><div class="two">%s</div>'
            '<div class="verify">%s</div></div></section>'
            '<section class="blk"><div class="wrap"><h2>%s</h2><p style="color:var(--mut);max-width:46em">%s</p>'
            '<div class="xlinks" style="margin-top:12px">%s</div></div></section>'
            '<section class="blk"><div class="wrap"><h2>%s</h2><div class="xlinks">%s</div></div></section>'
            '<section class="blk"><div class="wrap"><h2>%s</h2><div class="xlinks">%s</div></div></section>'
            '<div class="wrap">%s</div>') % (
        tcards, (VERIFY_ZH if lang=="zh" else VERIFY_EN),
        ("定位与方向" if lang=="zh" else "Positioning"), esc(p["note"]),
        path_badges,
        ("推荐行业应用" if lang=="zh" else "Recommended applications"), applinks or ("—"),
        ("相关与替代产品" if lang=="zh" else "Related & alternative products"), altlinks or "—",
        cta(lang))
    name = p["name"]
    ptype = ("吊牌" if p["type"]=="tag" else "标签") if lang=="zh" else p["type"]
    h1 = "%s %s" % (name, ("耐高温"+ptype if lang=="zh" else "High-Temperature "+p["type"].title()))
    crumb = [("Home","/"),("Products",u_products()),(name, url)]
    # NOTE: no Product structured data — no real offer/availability data (per SEO rule 6).
    write(lang, url, page(lang, url,
        "%s %s | ETIA" % (name, ("耐高温标识" if lang=="zh" else "Ultra-High-Temperature Identification")),
        ("%s — %s。%s" % (name, p["note"], p["max_proc"]))[:157] if lang=="zh" else ("%s — %s. Maximum process resistance %s." % (name, p["note"], p["max_proc"]))[:157],
        h1, "", body, crumb, active="products"))
    if lang=="en": track(url,"products")

def build_industries_hub(lang):
    cards = ""
    order = ["steel","aluminum","heat-resistant-asset-management","coating-process-identification","ceramics","concrete"]
    for iid in order:
        i = INDUSTRIES[iid]
        apps = [a for a in APPS if a["parent"]==iid]
        title = i["title_zh"] if lang=="zh" else i["title_en"]
        alink = "".join('<a href="%s">%s</a>' % (L(lang,u_app(iid,a["slug"])), esc(a["title_en"])) for a in apps[:4])
        cards += ('<a class="card" href="%s"><h3>%s</h3><p>%s</p><div class="xlinks">%s</div></a>') % (
            L(lang,u_industry(iid)), esc(title),
            ("跨行业应用" if (lang=="zh" and i["parent_type"]!="industry") else ("%d applications" % len(apps)) if lang=="en" else "%d 个应用"%len(apps)),
            alink)
    # cross-series card: Automotive label materials (3M + FLEXcon) — built by gen_automotive
    auto_card = ('<a class="card" href="%s"><h3>%s</h3><p>%s</p><div class="xlinks">'
                 '<a href="%s">3M</a><a href="%s">FLEXcon</a></div></a>') % (
        L(lang,"/industries/automotive-label-materials/"),
        ("汽车标签材料" if lang=="zh" else "Automotive Label Materials"),
        ("3M 与 FLEXcon 汽车标识材料:发动机舱、EV电池、线束、VIN 与警示。" if lang=="zh"
         else "3M and FLEXcon materials: underhood, EV battery, wire harness, VIN and warning identification."),
        L(lang,"/brands/3m/automotive-label-materials/"),
        L(lang,"/brands/flexcon/automotive-label-materials/"))
    h1 = "工业标识 — 行业与工艺应用" if lang=="zh" else "Industries & Applications"
    body = '<section class="blk"><div class="wrap"><div class="grid">%s%s</div></div></section><div class="wrap">%s</div>' % (auto_card, cards, cta(lang))
    crumb=[("Home","/"),("Industries & Applications",u_ind_hub())]
    write(lang, u_ind_hub(), page(lang, u_ind_hub(),
        ("行业与应用 — 超高温标识 | ETIA" if lang=="zh" else "Industries & Applications — Ultra-High-Temp Identification | ETIA"),
        ("按行业与工艺选择超高温标签与吊牌:钢铁、铝、陶瓷、混凝土及资产管理、产品涂装。" if lang=="zh"
         else "Ultra-high-temperature identification by industry and process: steel, aluminum, ceramics, concrete, asset management and product coating."),
        h1, "", body, crumb, active="industries"))
    if lang=="en": track(u_ind_hub(),"industries")

def build_industry(lang, iid):
    i = INDUSTRIES[iid]; apps=[a for a in APPS if a["parent"]==iid]
    appcards = "".join('<a class="card" href="%s"><h3>%s</h3><div class="rows">%s → <b>%s</b></div></a>' % (
        L(lang,u_app(iid,a["slug"])), esc(a["title_en"]),
        esc(PATHS[a["process_path"]]["title_en"]), esc(" / ".join(x.upper() for x in a["recommended"]) or "select by process"))
        for a in apps)
    procs = sorted({a["process_path"] for a in apps})
    proclinks = "".join('<a href="%s">%s</a>' % (L(lang,u_line(x)), esc(PATHS[x]["title_zh"] if lang=="zh" else PATHS[x]["title_en"])) for x in procs)
    title = i["title_zh"] if lang=="zh" else i["title_en"]
    body = ('<section class="blk"><div class="wrap"><h2>%s</h2><div class="grid">%s</div></div></section>'
            '<section class="blk"><div class="wrap"><h2>%s</h2><div class="xlinks">%s</div></div></section>'
            '<div class="wrap">%s</div>') % (
        ("应用" if lang=="zh" else "Applications"), appcards,
        ("推荐工艺线" if lang=="zh" else "Recommended process lines"), proclinks, cta(lang))
    parentlabel = "Industries & Applications"
    crumb=[("Home","/"),(parentlabel,u_ind_hub()),(title,u_industry(iid))]
    write(lang, u_industry(iid), page(lang, u_industry(iid),
        "%s — %s | ETIA" % (title, ("超高温标识" if lang=="zh" else "Ultra-High-Temp Identification")),
        ("%s超高温标识的应用与推荐产品。" % title) if lang=="zh" else ("Ultra-high-temperature identification for %s — applications and recommended products." % i["title_en"].lower()),
        ("%s%s" % (title, ("标识方案" if lang=="zh" else " Identification"))), "", body, crumb, active="industries"))
    if lang=="en": track(u_industry(iid), "industries")

def build_application(lang, a):
    iid=a["parent"]; i=INDUSTRIES[iid]; pp=PATHS[a["process_path"]]
    recs = [PRODUCTS[r] for r in a["recommended"] if r in PRODUCTS]
    reccards = "".join('<a class="card" href="%s"><h3>%s</h3><div class="rows"><b>%s</b> · %s</div><p>%s</p></a>' % (
        L(lang,u_prod(r["slug"])), esc(r["name"]), esc(r["max_proc"]), prod_type_pill(r).replace('<span class="pill','<span class="pill'), esc(r["note"]))
        for r in recs) or ('<div class="verify">%s</div>' % ("按表面与可移除性选择,需打样确认。" if lang=="zh" else "Product selected by surface and removability — to be confirmed by sample."))
    body = ('<section class="blk"><div class="wrap"><h2>%s</h2><div class="sub">%s</div></div></section>'
            '<section class="blk"><div class="wrap"><h2>%s</h2><div class="grid">%s</div>'
            '<div class="xlinks" style="margin-top:12px"><a href="%s">%s</a><a href="%s">%s</a></div></div></section>'
            '<div class="wrap">%s</div>') % (
        ("识别要求" if lang=="zh" else "Identification requirement"),
        (("%s in %s. Process path: %s." % (a["title_en"], i["title_en"], pp["title_en"])) if lang=="en"
         else ("%s / %s 的标识需求。工艺路径:%s。" % (i["title_zh"], a["title_en"], pp["title_zh"]))),
        ("推荐产品" if lang=="zh" else "Recommended products"), reccards,
        L(lang,u_line(a["process_path"])), esc(pp["title_zh"] if lang=="zh" else pp["title_en"]),
        L(lang,u_industry(iid)), esc(i["title_zh"] if lang=="zh" else i["title_en"]),
        cta(lang))
    title=i["title_zh"] if lang=="zh" else i["title_en"]
    crumb=[("Home","/"),("Industries & Applications",u_ind_hub()),(title,u_industry(iid)),(a["title_en"],u_app(iid,a["slug"]))]
    write(lang, u_app(iid,a["slug"]), page(lang, u_app(iid,a["slug"]),
        "%s | ETIA" % a["title_en"],
        ("%s — recommended ultra-high-temperature products and process path." % a["title_en"]) if lang=="en" else ("%s — 推荐的超高温产品与工艺路径。" % a["title_en"]),
        a["title_en"], "", body, crumb, active="industries"))
    if lang=="en": track(u_app(iid,a["slug"]), "applications")

def build_stub(lang, path, title_en, title_zh, body_en, body_zh, active=""):
    title = title_zh if lang=="zh" else title_en
    body = '<section class="blk"><div class="wrap"><p style="color:var(--mut);max-width:46em">%s</p></div></section><div class="wrap">%s</div>' % (
        esc(body_zh if lang=="zh" else body_en), cta(lang))
    crumb=[("Home","/"),(title,path)]
    write(lang, path, page(lang, path, "%s | ETIA"%title, esc(body_en)[:150], title, "", body, crumb, active=active))
    if lang=="en": track(path,"core")

# ---------------------------------------------------------------- home
ORG_JSONLD = {"@context":"https://schema.org","@type":"Organization","name":"ETIA Label",
    "url":SITE,"slogan":"Where materials meet applications.",
    "description":"Supplier and application-support partner for durable, specialty industrial labels — including YS-Tech HEATPROOF ultra-high-temperature labels and tags.",
    "brand":["Polyonics","YS-Tech","FlexCon","Computype","ETIA"],
    "contactPoint":[{"@type":"ContactPoint","contactType":"sales","email":"label@etia-tech.com"}]}

HOME_WHY = {
 "en":[("01","We Understand","We start with your application and operating conditions — surface, temperature, chemistry, print method and lifecycle — before recommending a material."),
       ("02","We Source","We provide access to specialty materials from trusted global material brands, including YS-Tech HEATPROOF for ultra-high-temperature work."),
       ("03","We Develop","With flexible material constructions we support specialized, higher-mix and smaller-batch requirements that mass supply overlooks."),
       ("04","We Support","From samples and application testing to in-house slitting, die-cutting and dependable repeat supply across the region.")],
 "zh":[("01","深入理解","在推荐材料之前,我们先了解应用与工况 —— 表面、温度、化学环境、打印方式与产品生命周期。"),
       ("02","全球采购","我们整合全球专业品牌的特种材料,包括面向超高温场景的 YS-Tech HEATPROOF。"),
       ("03","自主研发","以柔性材料结构支持传统大批量供应难以覆盖的复杂、多品种、小批量需求。"),
       ("04","持续支持","从样品与应用测试,到自有分切、模切与稳定的长期供应,覆盖区域交付。")],
}

def build_home(lang):
    path = "/"
    if lang == "en":
        eyebrow="Durable Identification · Specialty Label Materials"
        h1="Where materials meet applications."
        lede="Specialty label materials and application support for demanding manufacturing environments — from ultra-high-temperature steel and ceramics to heat-treatment tracking. We start from your application, not a catalog."
        b1,b2="Explore Products","Request Samples"
        svc=["100% Quality Testing","Application-Driven Solutions","Flexible Supply","Long-Term Support"]
        paths_title="Two ways to find your label"
        paths_sub="Every path converges on the same datasheet-backed product."
        pcards=[("Products","By process line — direct hot application, heat-treatment labels and tags.",u_products()),
                ("Industries & Applications","By industry and process — steel, aluminum, ceramics, concrete and cross-industry uses.",u_ind_hub())]
        prog_title="Ultra-high-temperature program"
        prog_sub="YS-Tech HEATPROOF materials for identification that survives casting, rolling, annealing and firing."
        why_head="Built around your application."
        brands_head="Global brands we work with"
        brands_sub="We combine specialty materials from selected international brands with ETIA's own developed constructions."
    else:
        eyebrow="耐久标识 · 特种标签材料"
        h1="让材料,真正适配应用。"
        lede="面向高要求制造环境的特种标签材料与应用支持 —— 从超高温钢铁、陶瓷到热处理追溯。我们从您的应用出发,而非从目录出发。"
        b1,b2="浏览产品","申请样品"
        svc=["100% 出货检测","应用驱动的方案","柔性供应","长期支持"]
        paths_title="两种查找方式"
        paths_sub="每一条路径,最终都指向同一款有数据表支撑的产品。"
        pcards=[("产品中心","按工艺线查找 —— 超高温直贴标签、热处理标签与吊牌。",u_products()),
                ("行业与应用","按行业与工艺查找 —— 钢铁、铝、陶瓷、混凝土及跨行业应用。",u_ind_hub())]
        prog_title="超高温标识方案"
        prog_sub="采用 YS-Tech HEATPROOF 材料,标识可经受铸造、轧制、退火与烧成。"
        why_head="始于对应用的理解。"
        brands_head="我们合作的全球品牌"
        brands_sub="我们整合来自全球专业品牌的特种材料,并结合 ETIA 自有研发的材料结构。"
    # sections
    svcbar='<div class="svcbar"><div class="wrap">%s</div></div>' % "".join('<div class="i">%s</div>'%esc(s) for s in svc)
    pcards_html="".join('<a class="card" href="%s"><h3>%s</h3><p>%s</p></a>'%(L(lang,u),esc(t),esc(d)) for t,d,u in pcards)
    lines_html="".join('<a class="card" href="%s"><h3>%s</h3><p>%s</p><div class="rows"><b>%d</b> %s</div></a>'%(
        L(lang,u_line(pid)),esc(PATHS[pid]["title_zh"] if lang=="zh" else PATHS[pid]["title_en"]),
        ("面向该工艺的材料选择。" if lang=="zh" else "Material selection focused on this process."),
        len(line_products(pid)),("款产品" if lang=="zh" else "products")) for pid in ["direct_hot_application","heat_treatment_labels","heat_treatment_tags"])
    ind_order=["steel","aluminum","ceramics","concrete","heat-resistant-asset-management","coating-process-identification"]
    ind_html="".join('<a class="card" href="%s"><h3>%s</h3><p>%s</p></a>'%(
        L(lang,u_industry(iid)),esc(INDUSTRIES[iid]["title_zh"] if lang=="zh" else INDUSTRIES[iid]["title_en"]),
        ("%d applications"%len([a for a in APPS if a["parent"]==iid]) if lang=="en" else "%d 个应用"%len([a for a in APPS if a["parent"]==iid])))
        for iid in ind_order)
    why_html="".join('<div class="why"><div class="n">%s</div><b>%s</b><p>%s</p></div>'%(n,esc(t),esc(d)) for n,t,d in HOME_WHY[lang])
    brands=["Polyonics","YS-Tech","FlexCon","Computype","ETIA"]
    brand_html="".join('<span class="bchip">%s</span>'%esc(b) for b in brands)

    body="""<section class="hero"><div class="wrap">
<div class="eyebrow">%s</div><h1 class="serif">%s</h1><p class="lede">%s</p>
<div class="btns"><a class="btn pri" href="%s">%s</a><a class="btn sec" href="%s">%s</a></div></div></section>
%s
<section class="blk"><div class="wrap"><h2>%s</h2><div class="sub">%s</div><div class="grid">%s</div></div></section>
<section class="blk" style="background:var(--bg)"><div class="wrap"><h2>%s</h2><div class="sub">%s</div><div class="grid">%s</div></div></section>
<section class="blk"><div class="wrap"><h2>%s</h2><div class="grid">%s</div></div></section>
<section class="blk"><div class="wrap"><h2>%s</h2><div class="whygrid">%s</div></div></section>
<section class="blk"><div class="wrap"><h2>%s</h2><div class="sub">%s</div><div class="brandwall">%s</div></div></section>
<div class="wrap">%s</div>""" % (
        esc(eyebrow),esc(h1),esc(lede),L(lang,u_products()),esc(b1),L(lang,"/contact/"),esc(b2),
        svcbar,
        esc(paths_title),esc(paths_sub),pcards_html,
        esc(prog_title),esc(prog_sub),lines_html,
        ("行业覆盖" if lang=="zh" else "Industries we serve"),ind_html,
        esc(why_head),why_html,
        esc(brands_head),esc(brands_sub),brand_html,
        cta(lang))

    canonical=SITE+PREFIX[lang]+path
    schema_js="".join('<script type="application/ld+json">%s</script>'%json.dumps(s,ensure_ascii=False) for s in [ORG_JSONLD])
    title=("ETIA Label — Specialty & Ultra-High-Temperature Industrial Labels" if lang=="en"
           else "ETIA Label — 特种与超高温工业标签")
    desc=("Specialty label materials and application support for demanding environments — ultra-high-temperature labels and tags for steel, aluminum, ceramics and heat-treatment tracking." if lang=="en"
          else "面向严苛环境的特种标签材料与应用支持 —— 用于钢铁、铝、陶瓷及热处理追溯的超高温标签与吊牌。")
    doc="""<!doctype html><html lang="%s"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title><meta name="description" content="%s">
<link rel="canonical" href="%s">%s
<meta property="og:title" content="%s"><meta property="og:type" content="website"><meta property="og:site_name" content="ETIA Label">
<style>%s</style>%s</head><body>
<div class="topstrip"></div>
<header><div class="wrap"><a class="logo" href="%s"><span class="ar">◄</span><span class="grn">ETIA</span><span class="blu">·LABEL</span></a>%s</div></header>
%s
%s
</body></html>""" % (lang,esc(title),esc(desc),canonical,hreflang_block(path),esc(title),CSS,schema_js,
        L(lang,"/"),nav_html(lang,"home"),body,footer_html(lang))
    full=os.path.join(ROOT,(PREFIX[lang]).strip("/"),"index.html")
    os.makedirs(os.path.dirname(full) if os.path.dirname(full) else ROOT,exist_ok=True)
    open(full if lang=="en" else os.path.join(ROOT,"zh","index.html"),"w").write(doc)
    if lang=="en": track(path,"core")

# ---------------------------------------------------------------- sitemaps + redirects
def build_sitemaps():
    groups={}
    for p,g in ALL_URLS: groups.setdefault(g,[]).append(p)
    files={}
    for g,fn in [("core","sitemap-core.xml"),("products","sitemap-products.xml"),
                 ("industries","sitemap-industries.xml"),("applications","sitemap-applications.xml")]:
        xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        for p in groups.get(g,[]):
            xml+='  <url><loc>%s%s</loc>' % (SITE,p)
            for lg in LANGS: xml+='<xhtml:link rel="alternate" hreflang="%s" href="%s%s%s"/>'%(HREFLANG[lg],SITE,PREFIX[lg],p)
            xml+='</url>\n'
        xml+='</urlset>\n'; open(os.path.join(ROOT,fn),"w").write(xml); files[g]=fn
    idx='<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for fn in files.values(): idx+='  <sitemap><loc>%s/%s</loc></sitemap>\n'%(SITE,fn)
    idx+='</sitemapindex>\n'; open(os.path.join(ROOT,"sitemap-index.xml"),"w").write(idx)
    open(os.path.join(ROOT,"robots.txt"),"w").write("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap-index.xml\n"%SITE)

def write_redirects():
    # 301 migration redirects (per brief §13) + clean-url config, in vercel.json
    cfg={"cleanUrls":True,"trailingSlash":True,"redirects":[
      {"source":"/cases","destination":"/industries/","permanent":True},
      {"source":"/cases/:path*","destination":"/industries/","permanent":True},
      {"source":"/products/direct-label","destination":"/products/direct-hot-application-labels/","permanent":True},
      {"source":"/products/management-label","destination":"/products/heat-treatment-labels/","permanent":True},
      {"source":"/products/management-tag","destination":"/products/heat-treatment-tags/","permanent":True},
    ]}
    open(os.path.join(ROOT,"vercel.json"),"w").write(json.dumps(cfg,indent=2)+"\n")

# ---------------------------------------------------------------- run
def clean():
    # preserve source (generators/data/docs); regenerate the section output dirs.
    # NOTE: does NOT delete automotive-owned dirs (label-materials, brands are handled
    # by the orchestrator ordering); heatproof runs first, automotive layers on top.
    for d in ["products","industries","applications","technical-resources","about","contact","zh",
              "materials","brands","insights","support","company","privacy","cookies","terms",
              "label-materials","popular"]:
        p=os.path.join(ROOT,d)
        if os.path.isdir(p): shutil.rmtree(p)
    for f in os.listdir(ROOT):
        if f.startswith("sitemap") or f=="robots.txt": os.remove(os.path.join(ROOT,f))

def build_all():
  for lang in LANGS:
    build_home(lang)
    build_products_hub(lang)
    for pid in PATHS: build_process_line(lang, pid)
    for pid in PRODUCTS: build_product(lang, PRODUCTS[pid])
    build_industries_hub(lang)
    for iid in INDUSTRIES: build_industry(lang, iid)
    for a in APPS: build_application(lang, a)
    # supporting nav stubs (marked pending where content not yet supplied)
    build_stub(lang,"/technical-resources/","Technical Resources","技术资源",
        "Selection guides, temperature-tier reference and datasheets for ultra-high-temperature identification. Full resource library is being populated.",
        "超高温标识的选型指南、温度分级参考与技术数据表。资源库正在完善中。", active="tech")
    build_stub(lang,"/about/","About ETIA","关于ETIA",
        "ETIA is a supplier and application-support partner for durable, specialty industrial labels — not the manufacturer of HEATPROOF products. Full company profile is being finalized.",
        "ETIA 是耐用型特种工业标签的供应与应用支持伙伴,并非 HEATPROOF 产品的制造商。公司完整介绍整理中。", active="about")
    build_stub(lang,"/contact/","Contact ETIA","联系我们",
        "Tell us the object temperature at application, the maximum later process temperature, the surface and the attachment method — Shanghai · Hong Kong · Bangkok · Bac Ninh · label@etia-tech.com",
        "请告知贴标时物件温度、后续最高工艺温度、表面及附着方式 — 上海 · 香港 · 曼谷 · 北宁 · label@etia-tech.com", active="contact")
    # legal stubs (placeholder copy — to be replaced with reviewed legal text)
    build_stub(lang,"/privacy/","Privacy Policy","隐私政策",
        "This Privacy Policy explains how ETIA handles information collected through this website. Full reviewed policy text is being finalized.",
        "本隐私政策说明 ETIA 如何处理通过本网站收集的信息。经审阅的完整条款正在整理中。")
    build_stub(lang,"/cookies/","Cookie Policy","Cookie 政策",
        "This Cookie Policy describes how this website uses cookies and similar technologies. Full reviewed policy text is being finalized.",
        "本 Cookie 政策说明本网站如何使用 Cookie 及类似技术。经审阅的完整条款正在整理中。")
    build_stub(lang,"/terms/","Terms of Use","使用条款",
        "These Terms of Use govern your use of this website. Full reviewed terms are being finalized.",
        "本使用条款约束您对本网站的使用。经审阅的完整条款正在整理中。")

def main():
    clean()
    build_all()
    build_sitemaps()
    write_redirects()
    from collections import Counter
    print("HEATPROOF EN canonical URLs:", len(ALL_URLS))
    print(Counter(g for _,g in ALL_URLS))

if __name__ == "__main__":
    main()
