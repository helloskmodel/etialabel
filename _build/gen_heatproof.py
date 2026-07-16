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

def L(lang, path):  # localize a site-relative path (vi/th have no inner pages -> English)
    return PREFIX.get(lang, "") + path

# ---------------------------------------------------------------- design system (finalized brand)
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{--ink:#141b2d;--mut:#5c6678;--faint:#8a93a3;--line:#e7ebf2;--bg:#f6f8fc;--mint:#f1f7ef;
--tint-green:#f0f5ee;--tint-blue:#edf2fb;
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
.langsw{display:inline-flex;gap:2px;margin-left:10px;border:1px solid var(--line);border-radius:9px;padding:2px}
nav .langsw a{display:inline-block;font-size:12px;color:var(--faint);padding:5px 9px;border-radius:7px;font-weight:600}
nav .langsw a.on{color:#fff;background:var(--blue)}
nav .langsw a:hover{color:var(--blue)}nav .langsw a.on:hover{color:#fff}
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
.whygrid{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}
.why{display:flex;gap:14px;align-items:flex-start;padding-top:4px}
.why .ic{flex:none;width:46px;height:46px;border-radius:12px;background:#fff;border:1px solid var(--line);color:var(--green-d);display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(16,34,58,.05)}
.why .ic svg{width:24px;height:24px}
.why .txt{flex:1;min-width:0}
.why .n{font-family:var(--serif);font-size:15px;color:var(--faint)}
.why b{display:block;font-family:var(--serif);font-size:19px;color:var(--blue-deep);margin:0 0 2px}
.why .sub{display:block;font-size:12px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--green-d);margin-bottom:8px}
.why p{font-size:14px;color:var(--mut)}
.brandwall{display:flex;flex-wrap:wrap;gap:10px;margin-top:6px}
.bchip{display:inline-block;font-size:12px;font-weight:700;padding:6px 14px;border-radius:22px;background:var(--bg);border:1px solid var(--line);color:var(--ink)}
/* split sections (image + text) */
.split{display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:center;padding:26px 0}
.split .txt .eyebrow{margin-bottom:10px}
.split .txt h2{font-family:var(--serif);font-weight:600;font-size:30px;color:var(--ink);margin-bottom:8px}
.split .txt>.sub{color:var(--mut);margin-bottom:14px;max-width:36em}
.imgframe{border:1px solid var(--line);border-radius:18px;background:linear-gradient(135deg,var(--mint),#fff);aspect-ratio:4/3;display:flex;align-items:center;justify-content:center;color:var(--faint);font-size:12.5px;letter-spacing:.04em;overflow:hidden}
.imgframe img{width:100%;height:100%;object-fit:cover;display:block}
.whyrows{display:flex;flex-direction:column}
.whyrow{display:flex;gap:14px;padding:15px 0;border-top:1px solid var(--line)}
.whyrow:first-child{border-top:none}
.whyrow .ic{flex:none;width:44px;height:44px;border-radius:11px;background:var(--mint);display:flex;align-items:center;justify-content:center;color:var(--green-d)}
.whyrow .ic svg{width:23px;height:23px}
.whyrow b{display:block;font-family:var(--serif);font-size:18px;color:var(--blue-deep)}
.whyrow p{font-size:14px;color:var(--mut);margin-top:2px}
.indcard{display:flex;gap:16px;align-items:flex-start}
.indcard .ic{flex:none;width:48px;height:48px;border-radius:12px;background:var(--mint);color:var(--green-d);display:flex;align-items:center;justify-content:center}
.indcard .ic svg{width:25px;height:25px}
.indcard .body{flex:1;min-width:0}
.indcard h3{font-family:var(--serif);font-weight:600}
.indcard .apps{display:flex;flex-wrap:wrap;gap:6px;margin-top:9px}
.indcard .apps span{font-size:12px;font-weight:600;color:var(--mut);background:#fff;border:1px solid var(--line);border-radius:16px;padding:4px 10px}
.indcard .go{color:var(--blue);font-weight:700;font-size:14px;margin-top:14px}
.focuslist{display:flex;flex-direction:column;gap:10px;margin-top:6px}
.focuslist a{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:15px 18px;border:1px solid var(--line);border-radius:12px;color:var(--ink);font-weight:700;font-size:16px}
.focuslist a:hover{border-color:var(--blue);color:var(--blue);text-decoration:none;box-shadow:0 6px 20px rgba(26,86,219,.08)}
.focuslist a small{color:var(--faint);font-size:12.5px;font-weight:500;display:block;margin-top:2px}
.selrows{display:flex;flex-direction:column;gap:10px;margin-top:6px}
.selrows a{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:13px 16px;border:1px solid var(--line);border-radius:11px;color:var(--ink)}
.selrows a:hover{border-color:var(--blue);text-decoration:none}
.selrows a .l b{color:var(--blue-deep)}.selrows a .l span{color:var(--mut);font-size:13px}
.selrows a .r{color:var(--faint);font-size:12.5px;white-space:nowrap}
/* case-studies carousel (16:9) */
.cases{position:relative}
.cwin{overflow:hidden;border-radius:18px;border:1px solid var(--line)}
.ctrack{display:flex;transition:transform .45s ease}
.cslide{min-width:100%}
.cslide .img16{aspect-ratio:16/9;background:linear-gradient(135deg,var(--mint),#eef2fb);display:flex;align-items:center;justify-content:center;color:var(--faint);font-size:13px;letter-spacing:.04em}
.cslide .img16 img{width:100%;height:100%;object-fit:cover;display:block}
.cslide .cap{padding:20px 24px;background:#fff;display:flex;justify-content:space-between;align-items:flex-end;gap:18px;flex-wrap:wrap}
.cslide .cap .eyebrow{color:var(--blue)}
.cslide .cap h3{font-family:var(--serif);font-size:24px;color:var(--blue-deep);margin:4px 0 9px}
.cslide .cap .kw{display:flex;flex-wrap:wrap;gap:6px}
.cnav{display:flex;align-items:center;justify-content:space-between;margin-top:16px}
.cdots{display:flex;gap:8px}
.cdot{width:9px;height:9px;border-radius:50%;background:var(--line);border:none;cursor:pointer;padding:0}
.cdot.on{background:var(--blue)}
.carrows{display:flex;gap:8px}
.carrow{width:42px;height:42px;border-radius:50%;border:1px solid var(--line);background:#fff;cursor:pointer;font-size:16px;color:var(--ink);line-height:1}
.carrow:hover{border-color:var(--blue);color:var(--blue)}
.whyclose{text-align:center;font-family:var(--serif);font-weight:600;color:var(--blue-deep);font-size:18px;letter-spacing:.02em;margin-top:26px}
/* explore-by-application carousel */
.acar-wrap{position:relative;margin-top:8px}
.acar{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;border-radius:20px;border:1px solid var(--line);background:#fff;scrollbar-width:none}
.acar::-webkit-scrollbar{display:none}
.aslide{flex:0 0 100%;scroll-snap-align:start;display:grid;grid-template-columns:55% 45%;min-height:430px}
.aimg{position:relative;display:flex;align-items:center;justify-content:center;overflow:hidden}
.aimg img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.aimg .aicon{color:#ffffffcc;font-size:78px;line-height:1}
.aimg .aicon svg{width:92px;height:92px}
.aimg .anum{position:absolute;left:26px;bottom:22px;color:#fff;font-family:var(--serif);font-size:18px;letter-spacing:.1em;font-weight:600;opacity:.92}
.aimg.g0{background:linear-gradient(150deg,#1A56DB,#143C96)}
.aimg.g1{background:linear-gradient(150deg,#B45309,#7c2d12)}
.aimg.g2{background:linear-gradient(150deg,#0e7490,#155e75)}
.aimg.g3{background:linear-gradient(150deg,#334155,#0f172a)}
.aimg.g4{background:linear-gradient(150deg,#41A62A,#256d18)}
.aimg.g5{background:linear-gradient(150deg,#2563eb,#0e7490)}
.acopy{padding:40px 42px;display:flex;flex-direction:column;justify-content:center}
.acopy .aeyebrow{font-size:12px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--green-d);margin-bottom:10px}
.acopy h3{font-family:var(--serif);font-weight:600;font-size:27px;color:var(--blue-deep);line-height:1.12;margin-bottom:12px}
.acopy>p{font-size:15px;color:var(--mut);max-width:34em}
.atags{display:flex;flex-wrap:wrap;gap:7px;margin:16px 0}
.atags span{font-size:12px;font-weight:700;color:var(--blue);background:#eaf1ff;border:1px solid #d6e2fb;border-radius:16px;padding:5px 12px}
.afeat{border-top:1px solid var(--line);padding-top:14px;margin-bottom:18px}
.afeat .k{display:block;font-size:11px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--faint);margin-bottom:2px}
.afeat .v{font-size:15px;font-weight:700;color:var(--ink)}
.acar-nav{position:absolute;top:50%;transform:translateY(-50%);width:46px;height:46px;border-radius:50%;border:1px solid var(--line);background:#fff;color:var(--ink);font-size:22px;line-height:1;cursor:pointer;z-index:5;box-shadow:0 6px 18px rgba(16,34,58,.14)}
.acar-nav:hover{border-color:var(--blue);color:var(--blue)}
.acar-nav.prev{left:-14px}.acar-nav.next{right:-14px}
@media(max-width:820px){.two{grid-template-columns:1fr}footer .fg{grid-template-columns:1fr}.pagehead h1{font-size:30px}
.hero h1{font-size:32px}.svcbar .wrap{grid-template-columns:1fr 1fr}.whygrid{grid-template-columns:1fr 1fr}
.split{grid-template-columns:1fr;gap:22px}.split .imgframe{order:-1}.split .txt h2{font-size:25px}
.aslide{grid-template-columns:1fr;min-height:0}.aimg{min-height:190px}.aimg .aicon svg{width:60px;height:60px}.acopy{padding:26px 24px}.acopy h3{font-size:22px}.acar-nav{display:none}
.cslide .cap h3{font-size:20px}}
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
        return """<div class="cta"><div class="ic">⚡</div><h3>始于应用。终于选对材料。</h3>
<p>告知表面、温度、化学环境与打印方式,我们推荐材料并安排样品验证。</p>
<div class="btns"><a class="btn pri" href="%s">申请样品</a><a class="btn on-dark" href="%s">咨询工程师</a></div></div>""" % (L(lang,"/contact/"), L(lang,"/contact/"))
    return """<div class="cta"><div class="ic">⚡</div><h3>Start with the Application. Finish with the Right Material.</h3>
<p>Tell us the surface, temperature, chemistry and print method — we'll recommend the material and arrange samples.</p>
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
    # Products & Solutions — three ways to find a material
    routes = [
      ("按行业" if lang=="zh" else "By Industry",
       "电子/PCB、金属陶瓷、医疗、汽车、电力线缆、户外能源 —— 从您的行业与应用出发。" if lang=="zh"
       else "Electronics/PCB, metal & ceramics, medical, automotive, wire & cable, outdoor & energy — start from your industry and application.",
       "/industries/"),
      ("按材料" if lang=="zh" else "By Material",
       "聚酰亚胺(重点)、聚酯、乙烯基等 —— 从材料结构出发选型。" if lang=="zh"
       else "Polyimide (featured), polyester, vinyl and more — start from the material construction.",
       "/materials/"),
      ("严选产品" if lang=="zh" else "Featured Solutions",
       "面向极端温度、化学、磨损与防篡改的严苛环境标签精选。" if lang=="zh"
       else "Selected harsh-environment labels for extreme temperature, chemical, abrasion and tamper-evident needs.",
       "/featured-solutions/"),
    ]
    rcards = "".join('<a class="card" href="%s"><h3>%s</h3><p>%s</p><div class="rows" style="color:var(--blue);font-weight:700;margin-top:10px">%s →</div></a>'%(
        L(lang,u), esc(t), esc(d), ("进入" if lang=="zh" else "Explore")) for t,d,u in routes)
    # secondary: ultra-high-temperature process lines
    lcards = "".join('<a class="card" href="%s"><h3>%s</h3><p>%s</p></a>'%(
        L(lang,u_line(pid)), esc(PATHS[pid]["title_zh"] if lang=="zh" else PATHS[pid]["title_en"]),
        ("%d 款产品"%len(line_products(pid)) if lang=="zh" else "%d products"%len(line_products(pid))))
        for pid in ["direct_hot_application","heat_treatment_labels","heat_treatment_tags"])
    body = ('<section class="blk"><div class="wrap"><h2>%s</h2><div class="sub">%s</div><div class="grid">%s</div></div></section>'
            '<section class="blk" style="background:var(--tint-blue)"><div class="wrap"><h2>%s</h2><div class="sub">%s</div><div class="grid">%s</div></div></section>'
            '<div class="wrap">%s</div>') % (
        ("三种查找方式" if lang=="zh" else "Three ways to find a material"),
        ("按行业、按材料,或从严选产品切入 —— 每条路径最终都指向同一款有数据表支撑的产品。" if lang=="zh"
         else "By industry, by material, or from our featured products — every path converges on the same datasheet-backed material."),
        rcards,
        ("超高温工艺产品线" if lang=="zh" else "Ultra-high-temperature process lines"),
        ("热态直贴 / 热处理标签 / 热处理吊牌 —— 面向钢铁、铝、陶瓷、混凝土等高温工艺。" if lang=="zh"
         else "Direct hot application / heat-treatment labels / heat-treatment tags — for steel, aluminum, ceramics and concrete."),
        lcards, cta(lang))
    h1 = "产品与解决方案" if lang=="zh" else "Products & Solutions"
    lede = ("按行业、按材料或从严选产品出发,找到适配您应用的耐久标签材料。" if lang=="zh"
            else "Find durable label materials matched to your application — by industry, by material, or from our featured solutions.")
    crumb = [("Home","/"),("Products & Solutions",u_products())]
    write(lang, u_products(), page(lang, u_products(),
        ("产品与解决方案 | ETIA" if lang=="zh" else "Products & Solutions | ETIA"),
        ("按行业、按材料或严选产品浏览 ETIA 耐久与特种标签材料。" if lang=="zh"
         else "Browse ETIA durable and specialty label materials by industry, by material, or by featured solution."),
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
    # cross-series card: Healthcare & Life Sciences (FLEXcon + BIO TECH) — built by gen_healthcare
    hc_card = ('<a class="card" href="%s"><h3>%s</h3><p>%s</p><div class="xlinks">'
               '<a href="%s">FLEXcon</a><a href="%s">BIO TECH</a></div></a>') % (
        L(lang,"/industries/healthcare-life-sciences/"),
        ("医疗与生命科学" if lang=="zh" else "Healthcare & Life Sciences"),
        ("FLEXcon 与 BIO TECH:可穿戴、诊断、制药、医疗器械、实验室;低温/液氮/灭菌。" if lang=="zh"
         else "FLEXcon and BIO TECH: wearables, diagnostics, pharma, devices, laboratory; cryogenic, sterilization."),
        L(lang,"/brands/flexcon/healthcare-life-sciences/"),
        L(lang,"/brands/bio-tech/healthcare-life-sciences/"))
    # cross-series card: Electronics & PCB (Polyonics) — built by gen_pcb
    pcb_card = ('<a class="card" href="%s"><h3>%s</h3><p>%s</p><div class="xlinks">'
                '<a href="%s">%s</a></div></a>') % (
        L(lang,"/industries/electronics-pcb/"),
        ("电子制造与PCB" if lang=="zh" else "Electronics & PCB"),
        ("Polyonics 聚酰亚胺:回流焊、波峰焊、严苛清洗、ESD 与激光可标记。" if lang=="zh"
         else "Polyonics polyimide: reflow, wave solder, harsh wash, ESD and laser-markable."),
        L(lang,"/materials/polyimide-pi-label-materials/"),("聚酰亚胺产品线" if lang=="zh" else "Polyimide line"))
    # cross-series card: Wire & Cable (Avery Dennison) — built by gen_wirecable
    wc_card = ('<a class="card" href="%s"><h3>%s</h3><p>%s</p><div class="xlinks">'
               '<a href="%s">%s</a></div></a>') % (
        L(lang,"/industries/wire-cable/"),
        ("电力与线缆" if lang=="zh" else "Wire & Cable"),
        ("Avery Dennison:旗型、缠绕、自覆膜、热缩、吊牌;按应用/行业/环境。" if lang=="zh"
         else "Avery Dennison: flag, wrap, self-laminating, heat-shrink, tags; by application/industry/environment."),
        L(lang,"/brands/avery-dennison/wire-cable/"),("Avery Dennison" ))
    h1 = "工业标识 — 行业与工艺应用" if lang=="zh" else "Industries & Applications"
    body = '<section class="blk"><div class="wrap"><div class="grid">%s%s%s%s%s</div></div></section><div class="wrap">%s</div>' % (auto_card, hc_card, pcb_card, wc_card, cards, cta(lang))
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

def build_outdoor_energy(lang):
    """Outdoor & Energy application landing — lists applications; materials matched on
    request (no products invented yet)."""
    path="/industries/outdoor-energy/"
    apps=[
      ("Solar Panel Identification","光伏组件标识","PV modules, junction boxes and frames","光伏组件、接线盒与边框"),
      ("Outdoor Equipment Labels","户外设备标签","Enclosures, machinery and field equipment","机柜、机械与现场设备"),
      ("Electrical & Utility Identification","电力与公用设施标识","Utility assets, meters and distribution","电力资产、电表与配电"),
      ("Battery & Energy Storage Labels","电池与储能标签","Energy-storage systems and battery packs","储能系统与电池组"),
      ("UV- and Weather-Resistant Labels","耐UV与耐候标签","Sun, rain, moisture and temperature cycling","日晒、雨淋、潮湿与温变"),
      ("Rating Plates & Asset Identification","铭牌与资产标识","Nameplates, ratings and asset tags","铭牌、参数牌与资产标签"),
    ]
    cards="".join('<a class="card" href="%s"><h3>%s</h3><p>%s</p></a>'%(
        L(lang,"/contact/"), esc(z if lang=="zh" else e), esc(dz if lang=="zh" else de)) for e,z,de,dz in apps)
    note=("户外与能源应用的具体材料按需匹配;经验证的产品与参数正在完善中。" if lang=="zh"
          else "Materials for outdoor and energy applications are matched on request; verified products and specifications are being finalized.")
    body=('<section class="blk"><div class="wrap"><h2>%s</h2><div class="grid">%s</div></div></section>'
          '<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'
          '<div class="wrap">%s</div>')%(
        ("应用" if lang=="zh" else "Applications"), cards, esc(note), cta(lang))
    crumb=[("Home","/"),("Industries & Applications",u_ind_hub()),("Outdoor & Energy",path)]
    write(lang,path,page(lang,path,
        ("户外与能源标签材料 | ETIA" if lang=="zh" else "Outdoor & Energy Label Materials | ETIA"),
        ("面向光伏、户外设备、电力设施、储能与耐候标识的标签材料。" if lang=="zh"
         else "Label materials for solar, outdoor equipment, electrical utility, energy storage and weather-resistant identification."),
        ("户外与能源标签材料" if lang=="zh" else "Outdoor & Energy Label Materials"),
        ("面向光伏、户外设备、电力设施、储能与耐UV耐候的标识方案。" if lang=="zh"
         else "Identification for solar, outdoor equipment, electrical/utility, energy storage and UV/weather exposure."),
        body,crumb,active="industries"))
    if lang=="en": track(path,"industries")

# ---------------------------------------------------------------- home
ORG_JSONLD = {"@context":"https://schema.org","@type":"Organization","name":"ETIA Label",
    "url":SITE,"slogan":"Where materials meet applications.",
    "description":"Supplier and application-support partner for durable, specialty industrial labels — from ultra-high-temperature to cryogenic, chemical and tamper-evident identification.",
    "contactPoint":[{"@type":"ContactPoint","contactType":"sales","email":"label@etia-tech.com"}]}

# four pillars: (verb, sub-label, description)
HOME_WHY = {
 "en":[("We Understand","Application First","We understand your application before recommending a material."),
       ("We Match","Material Expertise","We match materials to real surfaces, processes, and environments."),
       ("We Develop","Beyond Standard Products","We develop solutions for specialized requirements."),
       ("We Support","Long-Term Partnership","From the first sample to dependable repeat supply.")],
 "zh":[("我们理解","应用优先","在推荐材料之前,我们先理解您的真实应用。"),
       ("我们匹配","材料专业","根据表面、工艺与环境匹配合适的材料。"),
       ("我们开发","超越标准产品","针对专业需求开发更合适的材料方案。"),
       ("我们支持","长期合作","从第一份样品,到稳定的重复供应。")],
}

# refined line icons for the four "We ..." pillars (24px, round caps, stroke = currentColor)
WHY_ICONS = [
 # We Understand — magnifier (examine the application)
 '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.4 15.4 21 21"/><path d="M8 10.5h5M10.5 8v5"/></svg>',
 # We Match — target (material matched to the application)
 '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r=".6" fill="currentColor"/></svg>',
 # We Develop — flask (constructions & testing)
 '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 3.5h5M10 3.5v5.3L5.7 16.8A2 2 0 0 0 7.5 20h9a2 2 0 0 0 1.8-3.2L14 8.8V3.5"/><path d="M8.2 14.5h7.6"/></svg>',
 # We Support — headset (samples, testing, repeat supply)
 '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 13v-1a8 8 0 0 1 16 0v1"/><path d="M4 13.5h1.4A1.6 1.6 0 0 1 7 15.1v2.3A1.6 1.6 0 0 1 5.4 19H4z"/><path d="M20 13.5h-1.4a1.6 1.6 0 0 0-1.6 1.6v2.3a1.6 1.6 0 0 0 1.6 1.6H20z"/><path d="M20 19a3 3 0 0 1-3 3h-2"/></svg>',
]

# Application Center — six focus industries with their applications as tags.
# format: (name_en, name_zh, url, apps_en[], apps_zh[]) — names only, no partner brands.
HOME_FOCUS = [
 ("Medical & Laboratory","医疗与实验室","/industries/healthcare-life-sciences/",
  ["Cryogenic storage","Slides","Chemical exposure"],["深低温存储","载玻片","化学环境"]),
 ("Electronics Manufacturing","电子制造","/industries/electronics-pcb/",
  ["PCB assembly","Reflow","Chemical cleaning"],["PCB装配","回流焊","化学清洗"]),
 ("Steel & Metals","钢铁与金属","/industries/steel/",
  ["Hot-metal labeling","Heat treatment","Traceability"],["热态贴标","热处理","生产追溯"]),
 ("Ceramics & Sanitaryware","陶瓷与卫浴","/industries/ceramics/",
  ["Kiln firing","Acid washing","Process tracking"],["窑炉烧制","酸洗","工艺追踪"]),
 ("Tire & Rubber","轮胎与橡胶","/featured-solutions/e-2314-tire-vulcanization-barcode-label/",
  ["Vulcanization","Pressure","Barcode tracking"],["硫化","压力","条码追溯"]),
 ("Automotive","汽车制造","/industries/automotive-label-materials/",
  ["VIN identification","Laser marking","Weather exposure"],["VIN标识","激光打标","户外耐候"]),
]

# one line icon per Application-Center industry — SAME ORDER as home_i18n.json "focus":
# Electronics & PCB · Metal Processing & Ceramics · Medical & Pharma · Automotive · Wire & Cable · Outdoor & Energy
INDUSTRY_ICONS = [
 # Electronics & PCB — chip
 '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="6.5" y="6.5" width="11" height="11" rx="1.5"/><rect x="10" y="10" width="4" height="4" rx="1"/><path d="M9.5 3.5v3M14.5 3.5v3M9.5 17.5v3M14.5 17.5v3M3.5 9.5h3M3.5 14.5h3M17.5 9.5h3M17.5 14.5h3"/></svg>',
 # Metal Processing & Ceramics — flame over ingot
 '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.5c.8 3 3.1 4.4 3.1 7.6 0 1.9-1.4 3.4-3.1 3.4s-3.1-1.5-3.1-3.4c0-1.1.5-1.9 1.2-2.6-.1 1.1.5 1.8.9 2.1.5-1.9.2-4.4 1-7.1z"/><rect x="6" y="16.5" width="12" height="4.5" rx="1"/></svg>',
 # Medical & Pharma — cross
 '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="3.5"/><path d="M12 8.5v7M8.5 12h7"/></svg>',
 # Automotive — car
 '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 13l1.7-4.6A2 2 0 0 1 6.6 7h10.8a2 2 0 0 1 1.9 1.4L21 13v5h-2.5v-2h-13v2H3z"/><circle cx="7.5" cy="16" r="1.6"/><circle cx="16.5" cy="16" r="1.6"/></svg>',
 # Wire & Cable — plug + cable
 '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="2.5" width="6" height="7" rx="1.5"/><path d="M11 2.5V5M13 2.5V5"/><path d="M12 9.5v2.5a4 4 0 0 1-4 4 4 4 0 0 0-4 4v.5"/></svg>',
 # Outdoor & Energy — sun
 '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2.6M12 19.4V22M4.2 4.2l1.9 1.9M17.9 17.9l1.9 1.9M2 12h2.6M19.4 12H22M4.2 19.8l1.9-1.9M17.9 6.1l1.9-1.9"/></svg>',
]

def _load_featured():
    try: return json.load(open(os.path.join(BUILD_DIR, "data", "featured.json")))
    except Exception: return None

def harsh_carousel(lang):
    """ETIA Selected → Case Studies: 16:9 image + keywords, manual carousel (no autoplay)."""
    fdata = _load_featured()
    if not fdata: return ""
    prods = sorted([p for p in fdata["products"] if p.get("homepage_featured")], key=lambda x: x["featured_order"])
    if not prods: return ""
    def land(p): return "/products/%s/" % p["maps_to"] if p.get("maps_to") else "%s%s/" % (fdata["center_route"], p["slug"])
    slides = ""; dots = ""
    for i, p in enumerate(prods):
        img = ('<img src="%s" alt="%s">' % (esc(p["home_image"]), esc(p["harsh_en"]))) if p.get("home_image") else esc("16:9 image · %s" % p["model"])
        kw = "".join('<span class="pill tag">%s</span>' % esc(t) for t in (p["tags_zh"] if lang=="zh" else p["tags_en"]))
        view = "查看方案" if lang=="zh" else "View Solution"
        slides += ('<div class="cslide"><div class="img16">%s</div><div class="cap">'
                   '<div><div class="eyebrow">%s · %s</div><h3>%s</h3><div class="kw">%s</div></div>'
                   '<a class="btn pri" style="padding:9px 18px;font-size:14px" href="%s">%s →</a></div></div>') % (
            img, esc(p["industry_zh"] if lang=="zh" else p["industry_en"]), esc(p["model"]),
            esc(p["harsh_zh"] if lang=="zh" else p["harsh_en"]), kw, L(lang, land(p)), view)
        dots += '<button class="cdot%s" data-i="%d" aria-label="slide %d"></button>' % (" on" if i==0 else "", i, i+1)
    title = "重点应用案例" if lang=="zh" else "Selected Applications"
    sub = ("真实严苛工况下的重点产品与应用。" if lang=="zh" else "Key products in real harsh-environment applications.")
    viewall = "查看全部严苛环境标签" if lang=="zh" else "View All Harsh Environment Labels"
    js = ("<script>(function(){var t=document.getElementById('ctrack');if(!t)return;var n=t.children.length,i=0;"
          "function go(x){i=(x+n)%n;t.style.transform='translateX('+(-i*100)+'%')';"
          "var d=document.querySelectorAll('.cdot');for(var k=0;k<d.length;k++)d[k].className='cdot'+(k===i?' on':'');}"
          "var pv=document.getElementById('cprev'),nx=document.getElementById('cnext');"
          "if(pv)pv.onclick=function(){go(i-1)};if(nx)nx.onclick=function(){go(i+1)};"
          "document.querySelectorAll('.cdot').forEach(function(b){b.onclick=function(){go(+b.getAttribute('data-i'))}});"
          "})();</script>")
    return ('<section class="blk"><div class="wrap"><h2>%s</h2><div class="sub">%s</div>'
            '<div class="cases"><div class="cwin"><div class="ctrack" id="ctrack">%s</div></div>'
            '<div class="cnav"><div class="cdots">%s</div><div class="carrows">'
            '<button class="carrow" id="cprev" aria-label="previous">‹</button>'
            '<button class="carrow" id="cnext" aria-label="next">›</button></div></div>'
            '<div style="margin-top:16px"><a class="btn sec" href="%s">%s →</a></div></div></section>%s') % (
        esc(title), esc(sub), slides, dots, L(lang, fdata["center_route"]), esc(viewall), js)

def img_frame(label):
    return '<div class="imgframe">%s</div>' % esc(label)

def harsh_module(lang):
    """Third screen — Explore by Application: five core industries as entry points
    (layer-by-layer drill-down: industry -> application -> product). No hot-products grid."""
    cards=""
    for k,(fe,fz,u,apps_en,apps_zh) in enumerate(HOME_FOCUS):
        pills="".join('<span>%s</span>'%esc(a) for a in (apps_zh if lang=="zh" else apps_en))
        cards+=('<a class="card indcard" href="%s"><div class="ic">%s</div>'
                '<div class="body"><h3>%s</h3><div class="apps">%s</div><div class="go">%s →</div></div></a>')%(
            L(lang,u), INDUSTRY_ICONS[k%len(INDUSTRY_ICONS)], esc(fz if lang=="zh" else fe),
            pills, ("进入" if lang=="zh" else "Explore"))
    eyebrow="应用中心" if lang=="zh" else "APPLICATION CENTER"
    title="查找您的应用。" if lang=="zh" else "Find Your Application."
    sub=("根据具体工艺、环境与标识要求,探索适合的耐久标签材料。" if lang=="zh"
         else "Explore durable label materials selected for specific processes, environments, and identification requirements.")
    viewall="查看全部应用" if lang=="zh" else "View All Applications"
    return ('<section class="blk" id="applications" style="background:var(--tint-blue)"><div class="wrap">'
            '<div class="eyebrow">%s</div><h2>%s</h2><div class="sub">%s</div><div class="grid">%s</div>'
            '<div style="margin-top:18px"><a class="btn sec" href="%s">%s →</a></div></div></section>')%(
        esc(eyebrow),esc(title),esc(sub),cards,L(lang,u_ind_hub()),esc(viewall))

def build_home(lang):
    path = "/"

HOME_I18N = json.load(open(os.path.join(BUILD_DIR, "data", "home_i18n.json")))
HOME_LANGS = HOME_I18N["langs"]
HL_PREFIX = HOME_I18N["prefix"]
FOCUS_URLS = HOME_I18N["focus_urls"]

def home_hlink(lang, path):
    # home internal link: en -> path, zh -> /zh+path (inner zh exists), vi/th -> English pages
    return ("/zh"+path) if lang=="zh" else path

def home_switcher(active):
    out=""
    for lg in HOME_LANGS:
        href = "/" if lg=="en" else HL_PREFIX[lg]+"/"
        out += '<a href="%s"%s>%s</a>' % (href, ' class="on"' if lg==active else '', esc(HOME_I18N["lang_name"][lg]))
    return '<span class="langsw">%s</span>' % out

def home_nav(lang):
    T=HOME_I18N[lang]
    hrefs=["/products/","/industries/","/technical-resources/","/about/","/contact/"]
    links="".join('<a href="%s">%s</a>'%(home_hlink(lang,h),esc(lbl)) for h,lbl in zip(hrefs,T["nav"]))
    return '<nav>%s%s</nav>' % (links, home_switcher(lang))

def home_footer(lang):
    T=HOME_I18N[lang]; nh,lh,ch=T["footer_heads"]
    navl="".join('<li><a href="%s">%s</a></li>'%(home_hlink(lang,h),esc(l)) for h,l in
                 zip(["/products/","/industries/","/technical-resources/","/about/"],T["nav"][:4]))
    legal="".join('<li><a href="%s">%s</a></li>'%(home_hlink(lang,p),t) for p,t in
                  [("/privacy/","Privacy Policy"),("/cookies/","Cookie Policy"),("/terms/","Terms of Use")])
    return ('<footer><div class="wrap"><div class="flogo"><span class="ar">◄</span><span class="grn">ETIA</span><span class="blu">·LABEL</span></div>'
            '<div class="fg"><div><h5>%s</h5><ul>%s</ul></div><div><h5>%s</h5><ul>%s</ul></div>'
            '<div><h5>%s</h5><a class="email" href="mailto:label@etia-tech.com">label@etia-tech.com</a><br><br>'
            'Shanghai · Hong Kong · Bangkok · Bac Ninh</div></div>'
            '<div class="bar"><span>© 2026 ETIA-TECH (ASIA) Co., Limited. All rights reserved.</span></div></div></footer>') % (
        esc(nh),navl,esc(lh),legal,esc(ch))

def home_hreflang(path):
    t=[]
    for lg in HOME_LANGS:
        t.append('<link rel="alternate" hreflang="%s" href="%s%s%s">'%(lg,SITE,HL_PREFIX[lg],path))
    t.append('<link rel="alternate" hreflang="x-default" href="%s%s">'%(SITE,path))
    return "".join(t)

def build_home(lang):
    path="/"
    T=HOME_I18N[lang]
    # Why ETIA pillars — icon + "We…" heading + up to two short lines
    why_html="".join('<div class="why"><div class="ic">%s</div><div class="txt"><b>%s</b><p>%s</p></div></div>'%(
        WHY_ICONS[k%len(WHY_ICONS)],esc(head),esc(text)) for k,(head,text) in enumerate(T["why"]))
    why_close=('<p class="whyclose">%s</p>'%esc(T["why_close"])) if T.get("why_close") else ""
    # Explore by Application — large image + copy carousel (one industry per slide)
    n=len(T["focus"])
    slides=""
    for k,f in enumerate(T["focus"]):
        tags="".join('<span>%s</span>'%esc(t) for t in f["tags"])
        slides+=('<div class="aslide">'
                 '<div class="aimg g%d"><span class="aicon">%s</span><span class="anum">%02d / %02d</span></div>'
                 '<div class="acopy"><div class="aeyebrow">%s</div><h3>%s</h3><p>%s</p>'
                 '<div class="atags">%s</div>'
                 '<div class="afeat"><span class="k">%s</span><span class="v">%s</span></div>'
                 '<a class="btn sec" href="%s">%s →</a></div></div>')%(
            k%6, INDUSTRY_ICONS[k%len(INDUSTRY_ICONS)], k+1, n,
            esc(f["name"]), esc(f["headline"]), esc(f["desc"]), tags,
            esc(f["feat_kind"]), esc(f["feat"]),
            home_hlink(lang,FOCUS_URLS[k]), esc(T["explore"]))
    app_carousel=('<div class="acar-wrap"><button class="acar-nav prev" type="button" aria-label="Previous" onclick="etaSlide(-1)">‹</button>'
                  '<div class="acar" id="acar">%s</div>'
                  '<button class="acar-nav next" type="button" aria-label="Next" onclick="etaSlide(1)">›</button></div>')%slides
    final_cta=('<div class="wrap"><div class="cta"><div class="ic">⚡</div><h3>%s</h3><p>%s</p>'
               '<div class="btns"><a class="btn pri" href="%s">%s</a><a class="btn on-dark" href="%s">%s</a></div></div></div>')%(
        esc(T["fcta_title"]),esc(T["fcta_para"]),home_hlink(lang,"/contact/"),esc(T["fcta_b1"]),home_hlink(lang,"/contact/"),esc(T["fcta_b2"]))
    svc_html="".join('<div class="i">%s</div>'%esc(s) for s in T.get("svc",[]))
    body="""<section class="hero"><div class="wrap">
<div class="eyebrow">%s</div><h1 class="serif">%s</h1>
<p class="lede" style="color:var(--ink);font-size:20px;font-weight:600;max-width:32em">%s</p>
<p class="lede">%s</p>
<div class="btns"><a class="btn pri" href="#applications">%s</a><a class="btn sec" href="%s">%s</a></div></div></section>
<section class="svcbar"><div class="wrap">%s</div></section>
<section class="blk" style="background:var(--tint-green)"><div class="wrap"><div class="eyebrow">%s</div><h2>%s</h2><div class="sub">%s</div><div class="whygrid">%s</div>%s</div></section>
<section class="blk" id="applications" style="background:var(--tint-blue)"><div class="wrap"><div class="eyebrow">%s</div><h2>%s</h2><div class="sub">%s</div>%s
<div style="margin-top:20px"><a class="btn sec" href="%s">%s →</a></div></div></section>
%s""" % (
        esc(T["hero_eyebrow"]),esc(T["hero_h1"]),esc(T["hero_line"]),esc(T["hero_para"]),esc(T["hero_b1"]),home_hlink(lang,"/contact/"),esc(T["hero_b2"]),
        svc_html,
        esc(T["why_eyebrow"]),esc(T["why_head"]),esc(T["why_intro"]),why_html,why_close,
        esc(T["appc_eyebrow"]),esc(T["appc_title"]),esc(T["appc_sub"]),app_carousel,home_hlink(lang,"/industries/"),esc(T["appc_viewall"]),
        final_cta)
    canonical=SITE+HL_PREFIX[lang]+path
    schema_js='<script type="application/ld+json">%s</script>'%json.dumps(ORG_JSONLD,ensure_ascii=False)
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
<script>function etaSlide(d){var c=document.getElementById('acar');if(c)c.scrollBy({left:d*c.clientWidth,behavior:'smooth'});}</script>
</body></html>""" % (lang,esc(T["meta_title"]),esc(T["meta_desc"]),canonical,home_hreflang(path),esc(T["meta_title"]),CSS,schema_js,
        ("/" if lang=="en" else HL_PREFIX[lang]+"/"),home_nav(lang),body,home_footer(lang))
    outdir=os.path.join(ROOT,HL_PREFIX[lang].strip("/")) if HL_PREFIX[lang] else ROOT
    os.makedirs(outdir,exist_ok=True)
    open(os.path.join(outdir,"index.html"),"w").write(doc)
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
              "label-materials","popular","featured-solutions","vi","th"]:
        p=os.path.join(ROOT,d)
        if os.path.isdir(p): shutil.rmtree(p)
    for f in os.listdir(ROOT):
        if f.startswith("sitemap") or f=="robots.txt": os.remove(os.path.join(ROOT,f))

def build_about(lang):
    zh = (lang=="zh")
    lead = ("ETIA 是耐用与特种工业标签材料的解决方案伙伴 —— 我们从您的应用出发,匹配、开发并供应能在普通标签失效之处依然可靠的标签。" if zh
            else "ETIA is a solution partner for durable and specialty industrial label materials — we start from your application to match, develop and supply labels that perform where ordinary ones fail.")
    blocks = [
      (("应用优先" if zh else "Application first"),
       ("在推荐材料之前,我们先理解表面、温度、化学环境、打印方式与产品生命周期。" if zh
        else "Before recommending a material, we understand the surface, temperature, chemistry, print method and product lifecycle.")),
      (("材料与研发" if zh else "Materials & development"),
       ("我们整合来自选定国际专业品牌的特种材料,并针对油污、难粘基材与复杂工艺开发 ETIA 自有材料结构。" if zh
        else "We combine specialty materials from selected international brands with ETIA-developed constructions for oily, hard-to-bond and demanding processes.")),
      (("加工与供应" if zh else "Converting & supply"),
       ("自有分切与模切,支持多品种、小批量与稳定的长期供应。" if zh
        else "In-house slitting and die-cutting supporting higher-mix, small-batch runs and dependable long-term supply.")),
      (("区域布局" if zh else "Regional presence"),
       ("上海 · 香港 · 曼谷 · 北宁,持续拓展东南亚市场。" if zh
        else "Shanghai · Hong Kong · Bangkok · Bac Ninh, expanding across Southeast Asia.")),
    ]
    cards="".join('<div class="card"><h3>%s</h3><p>%s</p></div>'%(esc(t),esc(d)) for t,d in blocks)
    note=("ETIA 是材料供应与应用支持伙伴,并非所代表品牌产品的制造商;我们不将原厂的制造、研发与认证能力写作 ETIA 自有。" if zh
          else "ETIA is a materials supply and application-support partner, not the manufacturer of the represented brands' products; we do not present manufacturers' production, R&D or certifications as our own.")
    body=('<section class="blk"><div class="wrap"><div class="grid">%s</div></div></section>'
          '<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'
          '<div class="wrap">%s</div>')%(cards,esc(note),cta(lang))
    crumb=[("Home","/"),("About ETIA","/about/")]
    write(lang,"/about/",page(lang,"/about/",
        ("关于 ETIA | ETIA" if zh else "About ETIA | ETIA"),
        ("ETIA 是耐用与特种工业标签材料的解决方案伙伴,应用优先、自有加工、区域供应。" if zh
         else "ETIA is a solution partner for durable and specialty industrial label materials — application-first, in-house converting, regional supply."),
        ("关于 ETIA" if zh else "About ETIA"), lead, body, crumb, active="about"))
    if lang=="en": track("/about/","core")

def build_contact(lang):
    zh=(lang=="zh")
    offices=[
      ("Shanghai","上海","China","中国","+86 151 2119 7091 · 400 990 8448"),
      ("Hong Kong","香港","ETIA-TECH (ASIA) Co., Limited","ETIA-TECH (ASIA) Co., Limited","label@etia-tech.com"),
      ("Bangkok","曼谷","Thailand","泰国","+66 811 746 947"),
      ("Bac Ninh","北宁","Vietnam","越南","+84 344 590 091"),
    ]
    cards="".join('<div class="card"><h3>%s</h3><p>%s</p><div class="rows"><b>%s</b></div></div>'%(
        esc(z if zh else e), esc(rz if zh else r), esc(c)) for e,z,r,rz,c in offices)
    ask=("告诉我们:粘贴表面、温度(贴标时与后续最高)、化学暴露、打印方式与标签尺寸,我们推荐材料并安排样品。" if zh
         else "Tell us: the surface, temperature (at application and later peak), chemical exposure, print method and label size — we'll recommend the material and arrange samples.")
    body=('<section class="blk"><div class="wrap"><h2>%s</h2><div class="sub">%s</div>'
          '<a class="btn pri" href="mailto:label@etia-tech.com">label@etia-tech.com</a></div></section>'
          '<section class="blk" style="background:var(--tint-blue)"><div class="wrap"><h2>%s</h2><div class="grid">%s</div></div></section>'
          '<div class="wrap">%s</div>')%(
        ("告诉我们您的应用" if zh else "Tell us your application"), esc(ask),
        ("办公室" if zh else "Offices"), cards, cta(lang))
    crumb=[("Home","/"),("Contact","/contact/")]
    write(lang,"/contact/",page(lang,"/contact/",
        ("联系 ETIA | ETIA" if zh else "Contact ETIA | ETIA"),
        ("联系 ETIA:上海 · 香港 · 曼谷 · 北宁 · label@etia-tech.com。提供工况,我们匹配材料并寄样。" if zh
         else "Contact ETIA — Shanghai · Hong Kong · Bangkok · Bac Ninh · label@etia-tech.com. Share your application and we'll match the material and send samples."),
        ("联系我们" if zh else "Contact ETIA"),
        ("提供工况,我们匹配材料并寄样验证。" if zh else "Share your application — we'll match the material and validate by sample."),
        body, crumb, active="contact"))
    if lang=="en": track("/contact/","core")

def build_tech(lang):
    zh=(lang=="zh")
    items=[
      (("应用优先的选型" if zh else "Application-first selection"),
       ("我们按真实工况匹配材料,而不是默认推荐参数最高的方案。" if zh
        else "We match materials to the real process, not automatically the highest-spec option.")),
      (("技术数据表(TDS)" if zh else "Technical data sheets (TDS)"),
       ("每个型号的耐温、认证与化学数据以原厂 TDS 为准 —— 可按需索取。" if zh
        else "Temperature, certification and chemical data for each model come from the manufacturer TDS — available on request.")),
      (("温度的正确读法" if zh else "Reading temperatures correctly"),
       ("区分贴标温度、持续使用温度与短时峰值温度;峰值不等于长期耐温。" if zh
        else "Distinguish application temperature, continuous service temperature and short-term peak; a peak is not a continuous rating.")),
      (("样品与验证" if zh else "Samples & validation"),
       ("量产前请以实际材料通过您的打印、表面、化学与暴露顺序测试。" if zh
        else "Before production, test the actual material through your print, surface, chemistry and exposure sequence.")),
    ]
    cards="".join('<div class="card"><h3>%s</h3><p>%s</p></div>'%(esc(t),esc(d)) for t,d in items)
    body=('<section class="blk"><div class="wrap"><div class="grid">%s</div></div></section>'
          '<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'
          '<div class="wrap">%s</div>')%(cards,
        ("选型指南、温度分级参考与应用笔记正在陆续发布;需要具体型号资料请联系 ETIA。" if zh
         else "Selection guides, temperature-tier references and application notes are being published; contact ETIA for model-specific data."),
        cta(lang))
    crumb=[("Home","/"),("Technical Resources","/technical-resources/")]
    write(lang,"/technical-resources/",page(lang,"/technical-resources/",
        ("技术资源 | ETIA" if zh else "Technical Resources | ETIA"),
        ("选型方法、TDS 索取、温度读法与样品验证 —— ETIA 应用支持。" if zh
         else "Selection approach, TDS on request, reading temperatures and sample validation — ETIA application support."),
        ("技术资源" if zh else "Technical Resources"),
        ("选型方法、技术数据与验证建议 —— 帮助您在量产前选对材料。" if zh
         else "Selection approach, technical data and validation guidance — to choose the right material before production."),
        body, crumb, active="tech"))
    if lang=="en": track("/technical-resources/","core")

def build_all():
  for lang in HOME_LANGS:   # home is 4-language (en, zh, vi, th)
    build_home(lang)
  for lang in LANGS:        # inner site is en + zh
    build_products_hub(lang)
    for pid in PATHS: build_process_line(lang, pid)
    for pid in PRODUCTS: build_product(lang, PRODUCTS[pid])
    build_industries_hub(lang)
    for iid in INDUSTRIES: build_industry(lang, iid)
    for a in APPS: build_application(lang, a)
    build_outdoor_energy(lang)
    build_about(lang)
    build_contact(lang)
    build_tech(lang)
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
