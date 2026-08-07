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

LANGS = ["en", "zh"]                       # default inner-site languages
NAV_PILLAR_LANGS = ["en", "zh", "vi", "th"]  # Solutions / Service / Insight pillars: all 4 languages
JX = {"en": 0, "zh": 1, "vi": 2, "th": 3}
def P(lang, en, zh, vi, th):               # 4-language inline string pick
    return {"en": en, "zh": zh, "vi": vi, "th": th}.get(lang, en)
PREFIX = {"en": "", "zh": "/cn", "vi": "/vn", "th": "/th"}
HREFLANG = {"en": "en", "zh": "zh", "vi": "vi", "th": "th"}
# Paths that exist in all four languages (home only). Links to any other path from
# a vi/th page fall back to the English version (no 404). Industry hubs are EN+ZH.
FOURLANG = {"/", "/products/", "/products/find/", "/products/polyonics/", "/products/heatproof/", "/applications/", "/service/", "/insights/"}
FOURLANG_PREFIX = ("/insights/", "/industries/", "/products/item/", "/products/polyonics/")  # article, industry, product & Polyonics pages exist in all 4 langs
def Lx(lang, path):
    """Smart localized link: use the vi/th version only if that path is 4-language."""
    if lang in ("vi", "th") and path not in FOURLANG and not path.startswith(FOURLANG_PREFIX):
        return path
    return PREFIX.get(lang, "") + path

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
html{color-scheme:only light}
:root{color-scheme:only light;--ink:#141b2d;--mut:#5c6678;--faint:#8a93a3;--line:#e7ebf2;--bg:#f6f8fc;--mint:#f1f7ef;
--tint-green:#f0f5ee;--tint-blue:#edf2fb;
--blue-deep:#143C96;--blue:#1A56DB;--green:#41A62A;--green-d:#358B22;
--serif:'Inter','PingFang SC','Microsoft YaHei','Noto Sans SC','Noto Sans Thai',system-ui,-apple-system,'Segoe UI',sans-serif;
--sans:'Inter','PingFang SC','Microsoft YaHei','Noto Sans SC','Noto Sans Thai',system-ui,-apple-system,'Segoe UI',sans-serif}
html,body{background:#fff}
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
.logo img{height:40px;width:auto;display:block}
.logo .ar{color:var(--green);margin-right:2px}.logo .grn{color:var(--green)}.logo .blu{color:var(--blue-deep)}
nav{display:flex;align-items:center;gap:26px}
nav .navlinks{display:flex;align-items:center;gap:26px}
.navtog{display:none;background:none;border:none;cursor:pointer;padding:6px;margin-left:8px;color:var(--ink)}
.navtog svg{width:26px;height:26px;display:block}
nav a{font-size:14.5px;font-weight:600;color:var(--ink);white-space:nowrap}
nav a:hover{color:var(--blue)}nav a.on{color:var(--blue)}
nav .lang{font-size:13px;color:var(--faint);border:1px solid var(--line);border-radius:8px;padding:5px 10px}
.langsw{display:inline-flex;gap:2px;margin-left:10px;border:1px solid var(--line);border-radius:9px;padding:2px}
nav .langsw a{display:inline-block;font-size:12px;color:var(--faint);padding:5px 9px;border-radius:7px;font-weight:600}
nav .langsw a.on{color:#fff;background:var(--blue)}
nav .langsw a:hover{color:var(--blue)}nav .langsw a.on:hover{color:#fff}
/* Products mega-menu — left-anchored cascading columns (up to 3 levels, Delo/Panacol style) */
nav .nd{position:relative;display:inline-block}
nav .nd.ndwide{position:static}
nav .ndt{display:inline-flex;align-items:center;gap:6px;font-size:14.5px;font-weight:600;color:var(--ink);cursor:pointer}
nav .ndt .caret{font-size:10px;color:var(--faint);transition:.15s}
nav .nd:hover .ndt,nav .nd.open .ndt{color:var(--blue)}
nav .nd:hover .ndt .caret,nav .nd.open .ndt .caret{transform:rotate(180deg);color:var(--blue)}
nav .ndm.pm{position:absolute;top:70px;left:24px;right:auto;background:#fff;border:1px solid var(--line);
  border-radius:16px;box-shadow:0 26px 70px rgba(20,40,90,.20);display:grid;grid-template-columns:224px 268px 244px;
  max-width:calc(100vw - 48px);opacity:0;visibility:hidden;transform:translateY(10px);transition:.16s;z-index:60;overflow:hidden}
nav .nd.open .ndm.pm,nav .nd:hover .ndm.pm{opacity:1;visibility:visible;transform:translateY(0)}
nav .ndm.pm.pm2{grid-template-columns:224px minmax(300px,360px)}
.pm .ndrail{background:var(--bg);border-right:1px solid var(--line);padding:16px 12px}
.pm .ndrail-h{font-size:11px;font-weight:800;letter-spacing:.09em;color:var(--faint);padding:0 14px 12px}
.pm .axbtn{display:flex;align-items:center;justify-content:space-between;gap:8px;width:100%;text-align:left;background:none;border:none;font-family:inherit;
  font-size:14.5px;font-weight:700;color:var(--ink);padding:12px 14px;border-radius:10px;cursor:pointer;white-space:nowrap;transition:.12s}
.pm .axbtn .chev{color:var(--faint);font-size:17px;line-height:1}
.pm .axbtn.on,.pm .axbtn:hover{background:#fff;color:var(--blue);box-shadow:0 3px 12px rgba(16,34,58,.08)}
.pm .axbtn.on .chev,.pm .axbtn:hover .chev{color:var(--blue)}
.pm .ndmid{border-right:1px solid var(--line);padding:16px 12px}
.pm .midgroup{flex-direction:column;gap:2px}
.pm .axitem{display:flex;align-items:center;gap:12px;width:100%;text-align:left;background:none;border:none;font-family:inherit;
  font-size:14px;font-weight:600;color:var(--ink);padding:10px 12px;border-radius:10px;white-space:nowrap;cursor:pointer;transition:.12s}
.pm .axitem:hover,.pm .axitem.on{background:var(--tint-blue);color:var(--blue);text-decoration:none}
.pm .axitem .axl{flex:1}
.pm .axitem .chev{color:var(--faint);font-size:17px;line-height:1;margin-left:auto}
.pm .axitem:hover .chev,.pm .axitem.on .chev{color:var(--blue)}
.pm .axi{flex:none;width:32px;height:32px;border-radius:9px;background:var(--mint);color:var(--green-d);display:flex;align-items:center;justify-content:center}
.pm .axi:empty{display:none}
.pm .axi svg{width:19px;height:19px}
.pm .ndsub{padding:16px 12px}
.pm .subgroup{flex-direction:column;gap:2px}
.pm .subgroup a{display:block;font-size:14px;font-weight:600;color:var(--ink);padding:10px 12px;border-radius:10px;white-space:nowrap}
.pm .subgroup a:hover{background:var(--tint-green);color:var(--green-d);text-decoration:none}
.pm .subgroup a.suball{font-weight:700;color:var(--blue);border-bottom:1px solid var(--line);border-radius:0;margin-bottom:4px;padding-bottom:12px}
.pm .subgroup a.suball:hover{background:none;text-decoration:underline}
.pm .subempty{color:var(--faint);font-size:13px;font-weight:500;padding:12px;line-height:1.5}
/* simple single-level dropdown (top-level Product / Industry menus) */
nav .ndt.on{color:var(--blue)}
nav .ndm.sm{position:absolute;top:48px;left:0;background:#fff;border:1px solid var(--line);border-radius:12px;
  box-shadow:0 22px 56px rgba(20,40,90,.18);min-width:224px;padding:6px;opacity:0;visibility:hidden;
  transform:translateY(8px);transition:.16s;z-index:60}
nav .nd.open .ndm.sm,nav .nd:hover .ndm.sm{opacity:1;visibility:visible;transform:translateY(0)}
nav .ndm.sm a{display:block;font-size:14px;font-weight:600;color:var(--ink);padding:8px 14px;border-radius:9px;white-space:nowrap}
nav .ndm.sm a:hover{background:var(--tint-blue);color:var(--blue);text-decoration:none}nav .ndm.mega{position:fixed;top:76px;left:50%;background:#fff;border:1px solid var(--line);border-radius:16px;box-shadow:0 22px 56px rgba(20,40,90,.18);padding:22px 26px;display:grid;grid-template-columns:1fr 1fr;gap:10px 48px;width:min(920px,94vw);opacity:0;visibility:hidden;transform:translate(-50%,8px);transition:opacity .16s,transform .16s,visibility .16s;z-index:60}nav .ndm.mega::before{content:"";position:absolute;left:0;right:0;top:-18px;height:18px}.nd:hover .ndm.mega,nav .nd.open .ndm.mega{opacity:1;visibility:visible;transform:translate(-50%,0)}nav .ndm.mega a{display:block;min-width:0;padding:11px 14px;border-radius:10px;text-decoration:none}nav .ndm.mega a:hover{background:var(--tint-blue)}nav .ndm.mega a b{display:block;font-size:14.5px;color:var(--blue-deep);font-weight:700}nav .ndm.mega a:hover b{color:var(--blue)}nav .ndm.mega a span{display:block;font-size:12.5px;color:var(--mut);line-height:1.45;margin-top:2px}
nav .ndm.mega .findrow{grid-column:1/-1;background:#eafbe3;border:1px solid #cdeebf;margin-bottom:4px}
nav .ndm.mega .findrow b{color:var(--green-d)}
nav .ndm.mega .findrow:hover{background:#e0f6d4}
nav .ndm.mega .findrow:hover b{color:var(--green-d)}
nav .ndm.mega .megahd{grid-column:1/-1;font-size:11px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:#8a94a6;padding:8px 14px 0;margin-top:6px;border-top:1px solid var(--line)}
nav .ndm.mega a.brandrow b{color:#143C96}nav .ndm.mega a.brandrow:hover b{color:var(--blue)}
.ndmob a.ndma.find{color:var(--green-d);font-weight:700}
.ndmob{display:none}
@media(max-width:980px){nav .ndm.pm{grid-template-columns:200px 1fr;left:16px}.pm .ndsub{display:none}}
@media(max-width:900px){
.navtog{display:inline-flex}
nav .langsw,nav>a.lang{margin-left:auto}
nav .langsw{display:inline-flex}nav .langsw a{display:inline-block;padding:5px 7px;font-size:11.5px}
nav .navlinks{display:none;position:absolute;top:100%;left:0;right:0;background:#fff;border-top:1px solid var(--line);border-bottom:1px solid var(--line);box-shadow:0 22px 44px rgba(20,40,90,.16);flex-direction:column;align-items:stretch;gap:0;padding:6px 0;z-index:55}
nav.open .navlinks{display:flex}
nav .navlinks>a,nav .navlinks .ndt{padding:14px 24px;font-size:16px;border-bottom:1px solid var(--bg)}
nav .navlinks .nd,nav .navlinks .nd.ndwide{display:block;position:static}
nav .navlinks .ndm.pm,nav .navlinks .ndm.sm,nav .navlinks .ndm.mega{display:none}
nav .navlinks .ndt{display:flex;align-items:center;justify-content:space-between}
nav .navlinks .ndt .caret{display:inline-block;font-size:15px;color:var(--faint);transition:.15s}
nav .navlinks .nd.mopen .ndt,nav .navlinks .nd.mopen .ndt .caret{color:var(--blue)}
nav .navlinks .nd.mopen .ndt .caret{transform:rotate(180deg)}
nav .navlinks .ndmob{display:none;background:#fff}
nav .navlinks .nd.mopen .ndmob{display:block}
.ndmob .ndmr{display:flex;align-items:center;gap:14px;width:100%;text-align:left;background:none;border:none;font-family:inherit;font-size:16px;font-weight:600;color:var(--ink);padding:16px 24px;border-bottom:1px solid var(--line);cursor:pointer}
.ndmob .ndmi{flex:none;width:26px;height:26px;color:var(--green-d);display:flex;align-items:center;justify-content:center}
.ndmob .ndmi svg{width:24px;height:24px}
.ndmob .ndml{flex:1}
.ndmob .mchev{font-size:22px;line-height:1;color:var(--faint);transition:.15s}
.ndmob .ndmg.open .mchev{transform:rotate(90deg);color:var(--blue)}
.ndmob .ndmg.open .ndmr{color:var(--blue)}
.ndmob .ndmc{display:none;background:var(--bg)}
.ndmob .ndmg.open .ndmc{display:block}
.ndmob .ndma{display:block;font-size:15px;color:var(--ink);padding:13px 24px 13px 64px;border-bottom:1px solid var(--line)}
.ndmob .ndma.sub{padding-left:82px;font-size:14px;color:var(--mut)}}
.crumb{font-size:13px;color:var(--mut);padding:16px 0}
.crumb a{color:var(--mut)}.crumb b{color:var(--ink)}
.btn{display:inline-block;font-weight:700;font-size:15px;padding:12px 24px;border-radius:10px}
.btn.pri{background:var(--green);color:#fff}.btn.pri:hover{background:var(--green-d);text-decoration:none}
.btn.sec{border:1.5px solid var(--ink);color:var(--ink)}.btn.sec:hover{background:var(--ink);color:#fff;text-decoration:none}
.pagehead{padding:34px 0 8px}
.pagehead h1{font-family:var(--sans);font-weight:800;font-size:40px;line-height:1.12;text-align:left;text-wrap:balance;max-width:20em}
.pagehead .lede{margin-top:14px;color:var(--mut);font-size:18px;max-width:44em}
.pagehead .btns{margin-top:22px;display:flex;gap:12px;flex-wrap:wrap}
section.blk{padding:42px 0}
.blk h2{font-family:var(--serif);font-weight:600;font-size:26px;color:var(--ink);margin-bottom:6px}
.blk h2+.sub{color:var(--mut);margin-bottom:16px;max-width:46em}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}
.grid.grid3{grid-template-columns:repeat(3,1fr)}
.grid.grid2{grid-template-columns:repeat(2,1fr);max-width:760px}
@media(max-width:900px){.grid.grid3{grid-template-columns:1fr 1fr}}
@media(max-width:560px){.grid.grid3,.grid.grid2{grid-template-columns:1fr}}
/* industry landing HERO SECTION (label + slogan, banner-ready) */
.indhero{position:relative;background:var(--blue-deep);color:#fff;overflow:hidden;background-size:cover;background-position:center right;border-bottom:2px solid #fff}
.indhero.hasimg::before{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(20,60,150,.90) 16%,rgba(20,60,150,.50) 54%,rgba(20,60,150,.08));z-index:1}
.indhero .wrap{position:relative;z-index:2;padding:60px 24px}
.indhero .eyebrow{color:#8fe063}
.indhero h1{color:#fff;font-family:var(--sans);font-size:40px;line-height:1.12;letter-spacing:-.01em;margin:12px 0 16px;max-width:18em;font-weight:800;text-align:left}
.indhero .slogan{font-size:20px;line-height:1.45;color:#dbe6ff;font-weight:600;max-width:32em}
@media(max-width:820px){.indhero{min-height:280px}.indhero h1{font-size:30px}.indhero .slogan{font-size:16.5px}.indhero .wrap{padding:36px 24px}}
/* tabbed applications module (industry landing) — single scrollable row of tabs */
.appmod{margin-top:6px}
.apptabsrow{display:flex;align-items:stretch;border-bottom:2px solid var(--line);margin-bottom:30px}
.apparrow{flex:none;background:none;border:none;color:var(--faint);font-size:26px;line-height:1;cursor:pointer;padding:0 6px;align-self:center}
.apparrow:hover{color:var(--blue)}
.apptabs{display:flex;flex-wrap:nowrap;gap:2px;overflow-x:auto;scroll-behavior:smooth;flex:1;scrollbar-width:none;-ms-overflow-style:none}
.apptabs::-webkit-scrollbar{display:none}
.apptab{flex:none;max-width:210px;text-align:center;white-space:normal;background:none;border:none;font-family:inherit;font-size:15px;font-weight:700;color:var(--mut);padding:14px 16px;cursor:pointer;border-bottom:3px solid transparent;margin-bottom:-2px;line-height:1.25}
.apptab:hover{color:var(--ink)}
.apptab.on{color:var(--blue-deep);border-bottom-color:var(--blue)}
/* regional contact cards (Service page) */
.gcont{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:22px}
@media(max-width:760px){.gcont{grid-template-columns:1fr}}
.gcard{border:1px solid var(--line);border-radius:16px;padding:24px 26px;background:#fff}
.gc-region{font-size:18px;font-weight:800;color:var(--blue-deep);margin-bottom:12px}
.gc-name{font-weight:700;color:var(--ink);margin-bottom:6px}
.gc-role{font-weight:600;color:var(--mut);font-size:14px}
.gc-line{display:flex;gap:10px;align-items:flex-start;font-size:14px;color:var(--mut);line-height:1.55;margin-top:11px}
.gc-line svg{width:16px;height:16px;flex:none;margin-top:2px;color:var(--faint)}
a.gc-line{color:var(--green-d);font-weight:600;text-decoration:none}
a.gc-line:hover{text-decoration:underline}
a.gc-line svg{color:var(--green-d)}
.gc-note{color:var(--faint);font-size:13.5px;margin-top:22px}
/* service contact form + phones */
.ctwo{display:grid;grid-template-columns:1.4fr 1fr;gap:36px;align-items:start;margin-top:10px}
.cform{display:flex;flex-direction:column;gap:12px}
.cform .cfrow{display:flex;gap:12px}
.cform input,.cform textarea{width:100%;font-family:inherit;font-size:14px;padding:12px 14px;border:1px solid var(--line);border-radius:10px;background:#fff;color:var(--ink)}
.cform input:focus,.cform textarea:focus{outline:none;border-color:var(--blue)}
.cform .btn{align-self:flex-start;margin-top:4px;border:none;cursor:pointer}
.cphones{display:flex;flex-direction:column;gap:15px}
.cph{border-left:3px solid var(--blue);padding:3px 0 3px 14px}
.cph b{display:block;font-size:15px;color:var(--blue-deep)}
.cph span{font-size:13.5px;color:var(--mut)}
@media(max-width:820px){.ctwo{grid-template-columns:1fr;gap:24px}.cform .cfrow{flex-direction:column}}
.apppanel{display:grid;grid-template-columns:minmax(0,460px) 1fr;gap:40px;align-items:center}
.apppanel .apimg{position:relative;aspect-ratio:16/9;border-radius:14px;overflow:hidden;background:linear-gradient(135deg,#dfe7f3,#eef2f8);display:flex;align-items:center;justify-content:center;cursor:pointer}
.apppanel .apimg img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transition:transform .35s}
.apppanel .apimg:hover img{transform:scale(1.04)}
.apppanel .apimg .ph{font-size:42px;color:#aeb8c9}
.apppanel .apimg .apimg-cta{position:absolute;left:0;right:0;bottom:0;z-index:2;padding:30px 16px 12px;color:#fff;font-weight:700;font-size:13.5px;background:linear-gradient(0deg,rgba(9,24,58,.85),transparent);opacity:0;transition:opacity .2s}
.apppanel .apimg:hover .apimg-cta{opacity:1}
.apppanel .aptext h3{font-size:25px;color:var(--blue-deep);margin-bottom:14px;line-height:1.2}
.apppanel .aptext p{font-size:15.5px;color:var(--mut);line-height:1.65;margin-bottom:20px;max-width:40em}
.apppanel .aptext .plink{font-size:14px;font-weight:700;color:var(--blue)}
/* service commitment panel text */
.appmod.svc .apptab{max-width:none;white-space:nowrap}
.appmod.svc .apppanel{align-items:start;grid-template-columns:minmax(0,300px) 1fr;gap:32px}
.appmod.svc .apimg{aspect-ratio:4/3;max-width:300px}
.aptext .svc-num{font-size:13px;font-weight:800;letter-spacing:.12em;color:var(--green-d)}
.aptext .svc-num+h3{margin-top:6px}
.aptext .svc-tag{font-size:17px;font-weight:700;color:var(--ink);margin-bottom:16px;max-width:40em}
.aptext .svc-close{font-size:15px;font-weight:800;color:var(--blue);margin-bottom:0}
@media(max-width:820px){.apppanel{grid-template-columns:1fr;gap:20px}.apptab{font-size:13.5px;padding:10px 11px}.apppanel .aptext h3{font-size:22px}
.appmod.svc .apppanel{grid-template-columns:1fr;gap:18px}.appmod.svc .apimg{max-width:none;width:100%}}
.card{border:1px solid var(--line);border-radius:14px;padding:22px;background:#fff;transition:.15s;display:block}
.card:hover{border-color:var(--blue);box-shadow:0 12px 30px rgba(20,40,90,.12);transform:translateY(-3px);text-decoration:none}
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
.an-block{padding:18px 0;border-bottom:1px solid var(--line)}.an-block:last-of-type{border-bottom:none}
/* application-notes: filter chips + search */
.nfrow{display:flex;gap:10px;overflow-x:auto;padding:10px 0 14px;scrollbar-width:thin}
.nfchip{flex:none;border:1.5px solid var(--line);background:#fff;border-radius:22px;padding:9px 18px;font-family:inherit;font-size:14px;font-weight:700;color:var(--ink);cursor:pointer;white-space:nowrap;transition:.12s}
.nfchip:hover{border-color:var(--blue);color:var(--blue)}
.nfchip .n{color:var(--faint);font-weight:700;margin-left:7px;font-size:12.5px}
.nfchip.on{background:var(--blue);border-color:var(--blue);color:#fff}
.nfchip.on .n{color:#cfe0ff}
.nfbar{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;margin:8px 0 4px}
.nsearch{flex:1;min-width:220px;max-width:420px;font-family:inherit;font-size:15px;padding:12px 16px;border:1px solid var(--line);border-radius:10px;background:#fff;color:var(--ink)}
.nsearch:focus{outline:none;border-color:var(--blue)}
.cta{background:linear-gradient(155deg,var(--blue),var(--blue-deep));color:#fff;border-radius:18px;padding:40px;text-align:center;margin:26px 0}
.cta .ic{font-size:28px;color:#8fe063}
.cta h3{font-size:26px;font-weight:800;margin-top:4px;text-wrap:balance}
.cta p{color:#d3ddf3;margin:12px auto 20px;max-width:52em}
.cta .btns{display:grid;grid-template-columns:1fr 1fr;gap:12px;max-width:480px;margin:16px auto 0}
.cta .btns .btn{display:block;width:100%;padding:11px 16px;font-size:14px;text-align:center}
@media(max-width:520px){.cta .btns{grid-template-columns:1fr;max-width:320px}}
.btn.on-dark{border:1.5px solid #ffffff66;color:#fff}.btn.on-dark:hover{background:#fff;color:var(--blue-deep);text-decoration:none}
footer{background:#f3f5f8;color:var(--mut);padding:48px 0 26px;font-size:14px;border-top:1px solid var(--line);margin-top:20px}
footer .flogo{font-weight:800;font-size:21px;margin-bottom:22px}
footer .flogo img{height:34px;width:auto;display:block}
footer .fg{display:grid;grid-template-columns:1fr 1fr 1.3fr;gap:26px}
footer h5{color:var(--blue);font-size:14px;font-weight:700;margin-bottom:12px}
footer ul{list-style:none;display:flex;flex-direction:column;gap:8px}
footer a{color:var(--mut)}footer a:hover{color:var(--blue)}
footer .email{color:var(--green);font-weight:600}
footer .bar{border-top:1px solid var(--line);margin-top:30px;padding-top:16px;color:var(--faint);font-size:12.5px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}
/* home */
/* home section banners (dark image + green corner label) */
.hbanner{position:relative;overflow:hidden;background:var(--blue-deep);background-size:cover;background-position:center right;border-bottom:2px solid #fff;display:flex;align-items:center;min-height:320px}
.hbanner::before{content:"";position:absolute;inset:0;z-index:1;background:linear-gradient(90deg,rgba(20,60,150,.90) 16%,rgba(20,60,150,.50) 54%,rgba(20,60,150,.08))}
.hbanner .wrap{position:relative;z-index:2;width:100%;padding:60px 24px}
.hbanner .eyebrow{color:#8fe063;margin-bottom:6px}
.hbanner h1{color:#fff;font-family:var(--sans);font-weight:800;font-size:40px;line-height:1.12;letter-spacing:-.01em;text-align:left;margin:2px 0 10px;max-width:18em}
.hbanner .hsub{font-size:18px;font-weight:700;color:#eef3ff;margin-bottom:10px;max-width:40em}
.hbanner .hbody{font-size:15px;color:#c7d3ec;line-height:1.65;max-width:46em;margin-bottom:22px}
.hbanner .htab{position:absolute;top:0;right:0;z-index:3;background:var(--green);color:#fff;font-size:11px;font-weight:800;letter-spacing:.12em;padding:8px 20px;border-bottom-left-radius:12px}
.hbanner .btns{display:flex;gap:12px;flex-wrap:wrap}
.hcta{display:inline-block;background:#41A62A;color:#fff;font-family:var(--sans);font-weight:800;font-size:14.5px;padding:12px 24px;border-radius:9px;text-decoration:none;border:0;line-height:1.2}
.hcta:hover{background:#358B22;color:#fff}
.hbanner .btns .btn.sec{border-color:rgba(255,255,255,.6);color:#fff}
.hbanner .btns .btn.sec:hover{background:#fff;color:var(--blue-deep)}
@media(max-width:820px){.hbanner{min-height:250px}.hbanner h1{font-size:27px}.hbanner .hsub{font-size:15.5px}.hbanner .wrap{padding:34px 24px}}
.hero{padding:60px 0 46px}
.hero .eyebrow{margin-bottom:14px}
.hero h1{font-family:var(--sans);font-weight:800;font-size:40px;line-height:1.12;letter-spacing:-.01em;text-align:left;text-wrap:balance;max-width:18em}
.hero .lede{margin-top:18px;color:var(--mut);font-size:19px;max-width:40em}
.hero .btns{margin-top:26px;display:flex;gap:12px;flex-wrap:wrap}
.trustbar{background:linear-gradient(150deg,var(--blue),var(--blue-deep))}
.trustbar .wrap{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;padding:14px 24px}
.trustbar .ti{font-size:13.5px;font-weight:700;color:#fff;display:flex;gap:8px;align-items:center;justify-content:center;text-align:center}
.trustbar .ti::before{content:"✓";color:#8fe063;font-weight:800;flex:none}
.scgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:24px;margin-top:10px}
.sci{border-top:2px solid var(--green);padding-top:14px}
.sci-img{width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:10px;display:block;margin:0 0 12px;background:#eef3fc}
.sci:has(.sci-img){border-top:none;padding-top:0}
.sci b{display:block;font-size:15px;font-weight:700;color:var(--blue-deep);margin-bottom:6px}
.sci p{font-size:13px;color:var(--mut);line-height:1.55}
.svcbar{background:linear-gradient(155deg,var(--blue),var(--blue-deep));color:#fff}
.svcbar .wrap{display:grid;grid-template-columns:repeat(4,1fr);gap:24px;padding:26px 24px}
.svcbar .i{display:flex;gap:10px;align-items:flex-start}
.svcbar .i::before{content:"✓";color:#8fe063;font-weight:800;flex:none;margin-top:2px}
.svcbar .i b{display:block;font-size:14px;font-weight:700;color:#fff;margin-bottom:4px}
.svcbar .i span{display:block;font-size:11.5px;color:#c3d0ea;line-height:1.45}
.whygrid{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}
.why{display:flex;gap:14px;align-items:flex-start;padding-top:4px}
.why .ic{flex:none;width:46px;height:46px;border-radius:12px;background:#fff;border:1px solid var(--line);color:var(--green-d);display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(16,34,58,.05)}
.why .ic svg{width:24px;height:24px}
.why .txt{flex:1;min-width:0}
.why .n{font-family:var(--serif);font-size:15px;color:var(--faint)}
.why b{display:block;font-weight:700;font-size:17px;color:var(--blue-deep);margin:0 0 7px}
.why .wlead{font-size:14.5px;font-weight:600;color:var(--ink);line-height:1.4;margin-bottom:7px}
.why .wexp{font-size:13px;color:var(--mut);line-height:1.5}
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
/* explore-by-application: six cards (image top / copy below) */
.acgrid{display:grid;grid-template-columns:repeat(6,1fr);gap:12px}
.acgrid.acgrid5{grid-template-columns:repeat(5,1fr)}
.acgrid.acgrid6{display:flex;flex-wrap:nowrap;overflow-x:auto;scroll-snap-type:x mandatory;-webkit-overflow-scrolling:touch;gap:14px;padding:2px 2px 12px}
.acgrid.acgrid6 .acard{flex:0 0 212px;scroll-snap-align:start}
.solgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
@media(max-width:900px){.solgrid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:560px){.solgrid{grid-template-columns:1fr}}
/* Products landing — mega-menu-style category cards (heading + chevron + description) */
.pmgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:0 44px;margin-top:6px}
.pmcard{display:block;padding:20px 0;border-top:1px solid var(--line);text-decoration:none;color:inherit;transition:padding-left .15s}
.pmcard:hover{padding-left:6px}
.pmcard h3{display:flex;align-items:baseline;gap:8px;margin:0 0 6px;font-size:18px;color:var(--blue-deep)}
.pmcard:hover h3{color:var(--blue)}
.pmcard h3 .pmar{color:var(--green-d);font-weight:800}
.pmcard p{margin:0;font-size:14px;line-height:1.6;color:var(--mut)}
.pmgrid.pm4{grid-template-columns:repeat(4,1fr);gap:0 32px}
@media(max-width:820px){.pmgrid{grid-template-columns:1fr 1fr;gap:0 24px}.pmgrid.pm4{grid-template-columns:1fr 1fr;gap:0 24px}}
@media(max-width:560px){.pmgrid{grid-template-columns:1fr}.pmgrid.pm4{grid-template-columns:1fr}}
.freesample{background:linear-gradient(150deg,var(--blue),var(--blue-deep))}
.fsbox{display:grid;grid-template-columns:1fr 1fr;gap:30px;align-items:center}
.fsbox h2{color:#fff;font-size:26px}
.fsbox .fssub{color:#d3ddf3;font-size:15px;max-width:26em;margin-top:8px}
.fsbox .fsnote{color:#8fe063;font-size:12.5px;font-weight:700;margin-top:12px}
.fsform{display:grid;gap:10px}
.fsform input{width:100%;padding:13px 15px;border-radius:10px;border:1px solid #ffffff33;background:#ffffff14;color:#fff;font-size:14.5px;font-family:inherit}
.fsform input::placeholder{color:#c3d0ea}
.fsform input:focus{outline:none;border-color:#8fe063;background:#ffffff1f}
.fsform .btn.pri{width:100%;text-align:center;margin-top:4px;border:none;cursor:pointer;font-family:inherit}
.acard{display:flex;flex-direction:column;border:1px solid var(--line);border-radius:13px;overflow:hidden;background:#fff;color:var(--ink);transition:transform .18s,box-shadow .18s,border-color .18s}
.acard:hover{transform:translateY(-4px);box-shadow:0 14px 34px rgba(20,40,90,.14);border-color:var(--blue);text-decoration:none}
.acard-img{position:relative;aspect-ratio:16/11;display:flex;align-items:center;justify-content:center;overflow:hidden}
.acard-img img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transition:transform .35s}
.acard:hover .acard-img img{transform:scale(1.06)}
.sc4{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.sc4 .sccard .acard-img{background:#eef3fc;aspect-ratio:16/10}
.sc4 .sccard .acard-img img{object-fit:cover}
@media(max-width:900px){.sc4{grid-template-columns:repeat(2,1fr)}}
@media(max-width:560px){.sc4{grid-template-columns:1fr}}
.appcard .acard-img{background:#eef3fc;aspect-ratio:16/10}
.appcard .acard-body p{font-size:14px;color:var(--mut);line-height:1.55;margin-top:6px}
.appnotesgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
@media(max-width:900px){.appnotesgrid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:760px){.appnotesgrid{gap:11px}.appnotesgrid .acard-body h3{font-size:15px}.appnotesgrid .acard-body p{font-size:12.5px}}
@media(max-width:520px){.appnotesgrid{grid-template-columns:1fr}}
/* application-notes search / filter box */
.ansearch{position:relative;max-width:420px;margin:2px 0 20px}
.ansearch input{width:100%;font-family:inherit;font-size:14.5px;padding:11px 14px 11px 40px;border:1px solid var(--line);border-radius:10px;background:#fff;color:var(--ink)}
.ansearch input:focus{outline:none;border-color:var(--blue);box-shadow:0 0 0 3px rgba(26,86,219,.12)}
.ansearch .ansearch-ic{position:absolute;left:13px;top:50%;transform:translateY(-50%);color:var(--faint);pointer-events:none;display:flex}
.ansearch .ansearch-ic svg{width:18px;height:18px}
.annohit{color:var(--mut);font-size:14px;padding:6px 2px;display:none}
.indfilter{display:flex;flex-wrap:wrap;gap:9px;margin:2px 0 22px}
.indfbtn{font-size:14px;font-weight:700;color:var(--mut);background:#fff;border:1px solid var(--line);border-radius:999px;padding:8px 16px;cursor:pointer;transition:.15s}
.indfbtn:hover{border-color:var(--blue);color:var(--blue)}
.indfbtn.on{background:var(--blue);border-color:var(--blue);color:#fff}
.acard-img .aicon{color:#ffffffe6}
.acard-img .aicon svg{width:38px;height:38px}
.acard-body{padding:12px 12px 14px;display:flex;flex-direction:column;flex:1}
.acard-eyebrow{font-size:9.5px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;color:var(--green-d);margin-bottom:5px;line-height:1.25}
.acard-body h3{font-weight:700;font-size:14px;color:var(--blue-deep);line-height:1.2;margin-bottom:5px}
.acard-body h3.indname{font-size:16.5px;line-height:1.18;margin-bottom:7px}
.acard-body>p{font-size:11px;color:var(--mut);line-height:1.45;flex:1}
.acard .atags{display:flex;flex-wrap:wrap;gap:4px;margin:9px 0}
.acard .atags span{font-size:10px;font-weight:700;color:var(--blue);background:#eaf1ff;border:1px solid #d6e2fb;border-radius:11px;padding:3px 7px}
.acard-go{color:var(--blue);font-weight:700;font-size:11.5px}
.pcard h3{font-size:14px}
.pcard .pmodel{font-size:11px;font-weight:600;color:var(--mut);letter-spacing:.02em;margin-top:4px}
.pcard .pcode{display:inline-block;align-self:flex-start;font-size:11px;font-weight:800;color:var(--green-d);letter-spacing:.03em;background:var(--tint-green);border:1px solid #d5e6cf;border-radius:7px;padding:2px 8px;margin-top:9px;flex:0}
.pcard .acard-go{margin-top:auto;padding-top:12px}
@media(max-width:1180px){.acgrid{grid-template-columns:repeat(3,1fr)}}
/* Solutions by Industry — image-card carousel */
.indcar-wrap{position:relative;margin-top:20px}
.indcar{display:flex;gap:14px;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;padding:4px 2px}
.indcar::-webkit-scrollbar{display:none}
/* Key Products carousel — identical to the Industry carousel (arrows + card size) */
.prodcar{display:flex;gap:14px;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;padding:4px 2px}
.prodcar::-webkit-scrollbar{display:none}
.prodcar>.acard{flex:0 0 280px;scroll-snap-align:start}
.prodcar>.acard .acard-img{aspect-ratio:16/9}
@media(max-width:600px){.prodcar>.acard{flex:0 0 66%}.prodcar>.acard .acard-img{aspect-ratio:16/10}}
.indcar>.acard{flex:0 0 280px;scroll-snap-align:start}
.indcar>.acard .acard-img{aspect-ratio:16/9}
.acard-img.g0{background:linear-gradient(150deg,#1A56DB,#143C96)}
.acard-img.g1{background:linear-gradient(150deg,#0e7490,#155e75)}
.acard-img.g2{background:linear-gradient(150deg,#41A62A,#256d18)}
.acard-img.g3{background:linear-gradient(150deg,#B45309,#7c2d12)}
.acard-img.g4{background:linear-gradient(150deg,#334155,#0f172a)}
.acard-img.g5{background:linear-gradient(150deg,#2563eb,#0e7490)}
@media(max-width:600px){.indcar>.acard{flex:0 0 66%}.indcar>.acard .acard-img{aspect-ratio:16/10}}
/* explore-by-application carousel (legacy) */
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
/* product catalog: facets + list (Brady IA, modern skin) */
.catalog{display:grid;grid-template-columns:236px 1fr;gap:30px;align-items:start;margin-top:6px}
.facets .fgroup{border-bottom:1px solid var(--line);padding:14px 0}
.facets .fgroup:first-child{padding-top:0}
.facets h4{font-size:11.5px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--faint);margin-bottom:9px}
.facets label{display:flex;align-items:center;gap:9px;font-size:14px;color:var(--ink);padding:5px 0;cursor:pointer}
.facets input{width:16px;height:16px;accent-color:var(--blue);flex:none}
.catcount{font-size:13px;font-weight:700;color:var(--faint);margin-bottom:14px}
.plist{display:flex;flex-direction:column;gap:12px}
.prow{border:1px solid var(--line);border-radius:12px;background:#fff;padding:16px 20px;transition:.15s}
.prow:hover{border-color:var(--blue);box-shadow:0 8px 24px rgba(26,86,219,.08)}
.prow h3{font-size:16.5px;line-height:1.25;margin-bottom:4px}
.prow h3 a{color:var(--blue-deep)}.prow h3 a:hover{color:var(--blue);text-decoration:none}
.prow .pconstr{font-size:12.5px;font-weight:600;color:var(--faint);margin-bottom:7px}
.prow>p{font-size:13.5px;color:var(--mut);line-height:1.55;margin-bottom:10px}
.prow .pmeta{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:11px}
.prow .pmeta span{font-size:11.5px;font-weight:700;background:var(--bg);border:1px solid var(--line);border-radius:14px;padding:4px 10px;color:var(--mut)}
.prow .pmeta span.esd{background:#eaf1ff;color:var(--blue);border-color:#d6e2fb}
.prow .pactions{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.pbtn{display:inline-block;font-size:10.5px;font-weight:800;letter-spacing:.03em;padding:5px 11px;border-radius:15px;border:1px solid var(--line);color:var(--blue-deep);background:#fff;white-space:nowrap;line-height:1.3}
.pbtn:hover{border-color:var(--blue);color:var(--blue);text-decoration:none}
.pbtn.sample{background:var(--green);border-color:var(--green);color:#fff}
.pbtn.sample:hover{background:var(--green-d);border-color:var(--green-d);color:#fff}
.pbtn.view{background:var(--blue);border-color:var(--blue);color:#fff}
.pbtn.view:hover{background:var(--blue-deep);border-color:var(--blue-deep);color:#fff}
/* product spec table */
.ptable-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px}
.ptable{width:100%;border-collapse:collapse;font-size:13.5px}
.ptable th{text-align:left;font-size:11px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--faint);padding:12px 14px;border-bottom:2px solid var(--line);white-space:nowrap;background:var(--bg)}
.ptable td{padding:15px 14px;border-bottom:1px solid var(--line);vertical-align:top;color:var(--mut);white-space:nowrap}
.ptable tr:last-child td{border-bottom:none}
.ptable tbody tr:hover{background:#fafbfe}
.ptable .ptd-name{font-weight:800;font-size:14.5px;white-space:normal;min-width:220px}
.ptable .ptd-name a{color:var(--blue-deep)}.ptable .ptd-name a:hover{color:var(--blue);text-decoration:none}
.ptable .ptd-desc{font-weight:400;font-size:12px;color:var(--mut);margin-top:4px;line-height:1.45;max-width:34em;white-space:normal}
.ptable .esd-y{display:inline-block;font-size:11px;font-weight:800;background:#eaf1ff;color:var(--blue);border:1px solid #d6e2fb;border-radius:12px;padding:3px 9px}
.ptable .ptd-act{white-space:normal;min-width:224px;width:224px}
.ptable .ptd-act .pbtn{margin:0 5px 5px 0}
@media(max-width:820px){.catalog{grid-template-columns:1fr}}
@media(max-width:820px){.two{grid-template-columns:1fr}footer .fg{grid-template-columns:1fr}.pagehead h1{font-size:30px}
.hero h1{font-size:30px}.svcbar .wrap{grid-template-columns:1fr 1fr}.whygrid{grid-template-columns:1fr 1fr}
.split{grid-template-columns:1fr;gap:22px}.split .imgframe{order:-1}.split .txt h2{font-size:25px}
.acgrid{grid-template-columns:1fr 1fr;gap:10px}
.acgrid.acgrid5,.acgrid.acgrid6{display:flex;grid-template-columns:none;overflow-x:auto;scroll-snap-type:x mandatory;-webkit-overflow-scrolling:touch;gap:12px;padding:2px 2px 10px}
.acgrid.acgrid5::-webkit-scrollbar,.acgrid.acgrid6::-webkit-scrollbar{display:none}
.acgrid.acgrid5 .acard,.acgrid.acgrid6 .acard{flex:0 0 46%;scroll-snap-align:start}
.trustbar .wrap{grid-template-columns:1fr 1fr;gap:10px}
.scgrid{grid-template-columns:1fr 1fr;gap:16px}
.fsbox{grid-template-columns:1fr;gap:20px}
.aslide{grid-template-columns:1fr;min-height:0}.aimg{min-height:190px}.aimg .aicon svg{width:60px;height:60px}.acopy{padding:26px 24px}.acopy h3{font-size:22px}.acar-nav{display:none}
.cslide .cap h3{font-size:20px}}
@media(max-width:560px){.scgrid{grid-template-columns:1fr}.trustbar .wrap{grid-template-columns:1fr}.svcbar .wrap{grid-template-columns:1fr}.whygrid{grid-template-columns:1fr}}
"""

NAV_ITEMS = [("Home", "/", "home"),
             ("Product", "/products/", "products"),
             ("Solutions", "/applications/", "applications"),
             ("Resources", "/insights/", "insights"),
             ("Service", "/service/", "service")]
NAV_ZH = {"Home":"首页","Products":"产品","Product":"产品","Industry":"行业","Solutions":"方案","Case Studies":"案例","Application Notes":"应用笔记","Application":"应用","News":"新闻","Insights":"资讯","Insight":"资讯","Resource":"资讯","Resources":"资讯","Service":"服务",
          "Industries":"行业","About ETIA":"关于 ETIA","Contact":"联系我们"}
# 4-language nav / footer labels (keyed by the English label)
NAV_VI = {"Home":"Trang chủ","Products":"Sản phẩm","Product":"Sản phẩm","Industry":"Ngành","Solutions":"Giải pháp","Case Studies":"Nghiên cứu điển hình","Application Notes":"Ghi chú ứng dụng","Application":"Ứng dụng","News":"Tin tức","Insight":"Tài nguyên","Resource":"Tài nguyên","Resources":"Tài nguyên","Service":"Dịch vụ",
          "Industries":"Ngành","About ETIA":"Về ETIA","Contact":"Liên hệ"}
NAV_TH = {"Home":"หน้าแรก","Products":"ผลิตภัณฑ์","Product":"ผลิตภัณฑ์","Industry":"อุตสาหกรรม","Solutions":"โซลูชัน","Case Studies":"กรณีศึกษา","Application Notes":"แอปพลิเคชันโน้ต","Application":"การใช้งาน","News":"ข่าว","Insight":"แหล่งข้อมูล","Resource":"แหล่งข้อมูล","Resources":"แหล่งข้อมูล","Service":"บริการ",
          "Industries":"อุตสาหกรรม","About ETIA":"เกี่ยวกับ ETIA","Contact":"ติดต่อ"}
def navlab(lang, t):
    if lang == "zh": return NAV_ZH.get(t, t)
    if lang == "vi": return NAV_VI.get(t, t)
    if lang == "th": return NAV_TH.get(t, t)
    return t

# Products mega-menu: current sectors only (legacy partner-brand sectors retired)
def _navsvg(p): return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">%s</svg>' % p
AXIS_ICONS = {
 "env":  _navsvg('<path d="M12 2s4 4 4 8a4 4 0 0 1-8 0c0-4 4-8 4-8z"/><path d="M12 22a6 6 0 0 0 6-6"/>'),
 "app":  _navsvg('<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>'),
 "mat":  _navsvg('<rect x="3" y="4" width="18" height="5" rx="1"/><path d="M5 13h14M5 17h10M5 21h14"/>'),
}
PROD_AXES = [
 ("env","By Environment","按环境",[
   ("Heat Resistant","耐高温","/products/item/high-heat-identification/"),
   ("Low Temperature Resistant","耐低温","/products/item/cold-chain-cryogenic-labels/"),
   ("Chemical Resistant","耐化学","/products/item/chemical-resistant-labels/"),
   ("Sterilization","灭菌","/products/item/sterilization-labels/"),
 ]),
 ("app","By Industry","按行业",[
   ("PCB","PCB","/industries/pcb-electronics-labeling-solutions/"),
   ("Automotive & Tire","汽车与轮胎","/industries/automotive-labeling-solutions/"),
   ("Wire & Cable","线缆","/industries/wire-cable-labeling-solutions/"),
   ("Outdoor & Energy","户外与能源","/industries/outdoor-energy-labeling-solutions/"),
   ("Medical & Pharmacy","医疗与制药","/industries/medical-pharmaceutical-labeling-solutions/"),
   ("Steel & Ceramics","钢铁与陶瓷","/industries/steel-metal-ceramic-labeling-solutions/"),
 ]),
]

def products_dropdown(lang, linkfn):
    """Left-anchored cascading flyout: col1 axes -> col2 items -> col3 sub-items.
    Items carrying a 4th element (a list of children) render a chevron and open col3."""
    zh = (lang == "zh")
    # vi/th labels for the small set of menu strings (fall back to EN otherwise)
    MENU_VITH = {"By Environment": ("Theo môi trường", "ตามสภาพแวดล้อม"),
                 "By Industry": ("Theo ngành", "ตามอุตสาหกรรม"),
                 "By Material": ("Theo vật liệu", "ตามวัสดุ"),
                 "Heat Resistant": ("Chịu nhiệt", "ทนความร้อน"),
                 "Low Temperature Resistant": ("Chịu nhiệt độ thấp", "ทนอุณหภูมิต่ำ")}
    def lab(e, z):
        if zh: return z
        if lang == "vi" and e in MENU_VITH: return MENU_VITH[e][0]
        if lang == "th" and e in MENU_VITH: return MENU_VITH[e][1]
        return e
    def pick(en, zh_, vi, th): return {"zh": zh_, "vi": vi, "th": th}.get(lang, en)
    top = pick("Product", "产品", "Sản phẩm", "ผลิตภัณฑ์")
    rail = ""; mids = ""; subs = ""
    for i, (key, he, hz, items) in enumerate(PROD_AXES):
        on = " on" if i == 0 else ""
        rail += ('<button type="button" class="axbtn%s" data-ax="%s" onmouseover="etaAx(this,\'%s\')">'
                 '<span class="axc">%s</span><span class="chev">&rsaquo;</span></button>') % (on, key, key, esc(lab(he, hz)))
        midlinks = ""
        for j, item in enumerate(items):
            e, z, u = item[0], item[1], item[2]
            kids = item[3] if len(item) > 3 else None
            ic = INDUSTRY_ICONS[j % len(INDUSTRY_ICONS)] if key == "app" else ""
            icon = '<span class="axi">%s</span>' % ic
            if kids:
                sid = "%s-%d" % (key, j)
                midlinks += ('<button type="button" class="axitem haskid" data-sub="%s" onmouseover="etaSub(this,\'%s\')">'
                             '%s<span class="axl">%s</span><span class="chev">&rsaquo;</span></button>') % (
                    sid, sid, icon, esc(lab(e, z)))
                sublinks = '<a class="suball" href="%s">%s</a>' % (
                    linkfn(u), esc(pick("View all →", "查看全部 →", "Xem tất cả →", "ดูทั้งหมด →")))
                sublinks += "".join('<a href="%s">%s</a>' % (linkfn(cu), esc(lab(ce, cz))) for ce, cz, cu in kids)
                subs += '<div class="subgroup" data-sub="%s" style="display:none">%s</div>' % (sid, sublinks)
            else:
                midlinks += ('<a class="axitem" href="%s" onmouseover="etaSub(this,\'\')">'
                             '%s<span class="axl">%s</span></a>') % (linkfn(u), icon, esc(lab(e, z)))
        mids += '<div class="midgroup" data-mid="%s" style="display:%s">%s</div>' % (
            key, "flex" if i == 0 else "none", midlinks)
    subs += ('<div class="subgroup subph" data-sub="" style="display:flex"><div class="subempty">%s</div></div>') % (
        pick("Hover a category on the left to see its product lines.",
             "将鼠标移到左侧类别上，查看其产品系列。",
             "Di chuột vào một danh mục bên trái để xem các dòng sản phẩm.",
             "วางเมาส์บนหมวดหมู่ทางซ้ายเพื่อดูสายผลิตภัณฑ์"))
    # Mobile accordion — one collapsed row per axis (icon + label + chevron);
    # tapping an axis reveals its items. Keeps the phone menu short at a glance.
    mob = '<div class="ndmob">'
    for key, he, hz, itms in PROD_AXES:
        inner = ""
        for item in itms:
            e, z, u = item[0], item[1], item[2]
            kids = item[3] if len(item) > 3 else None
            inner += '<a class="ndma" href="%s">%s</a>' % (linkfn(u), esc(lab(e, z)))
            if kids:
                inner += "".join('<a class="ndma sub" href="%s">%s</a>' % (linkfn(cu), esc(lab(ce, cz)))
                                 for ce, cz, cu in kids)
        mob += ('<div class="ndmg"><button type="button" class="ndmr" onclick="etaMob(this)">'
                '<span class="ndmi">%s</span><span class="ndml">%s</span><span class="mchev">&rsaquo;</span></button>'
                '<div class="ndmc">%s</div></div>') % (AXIS_ICONS.get(key, ""), esc(lab(he, hz)), inner)
    mob += '</div>'
    has_kids = any(len(item) > 3 for _, _, _, itms in PROD_AXES for item in itms)
    pmcls = "ndm pm" if has_kids else "ndm pm pm2"
    sub_col = ('<div class="ndsub">%s</div>' % subs) if has_kids else ""
    return ('<div class="nd ndwide" onmouseenter="etaOpen(this)" onmouseleave="etaClose(this)">'
            '<a class="ndt" href="%s" onclick="return etaProd(this,event)">%s <span class="caret">&#9662;</span></a>'
            '<div class="%s">'
            '<div class="ndrail"><div class="ndrail-h">%s</div>%s</div>'
            '<div class="ndmid">%s</div>'
            '%s'
            '</div>%s</div>') % (linkfn("/products/"), esc(top), pmcls, ("产品方案" if zh else "LABEL SOLUTIONS"), rail, mids, sub_col, mob)

# Simple single-level dropdown (used for the top-level Product and Industry menus).
# One flat column of links — easier to find and tap than the nested cascading menu,
# especially on mobile (a single tap reveals the whole list).
_MENU_VITH = {"By Environment": ("Theo môi trường", "ตามสภาพแวดล้อม"),
              "By Industry": ("Theo ngành", "ตามอุตสาหกรรม"),
              "Heat Resistant": ("Chịu nhiệt", "ทนความร้อน"),
              "Low Temperature Resistant": ("Chịu nhiệt độ thấp", "ทนอุณหภูมิต่ำ"),
              # Product mega-menu industry names (PCB stays as-is)
              "Automotive & Tire": ("Ô tô & Lốp xe", "ยานยนต์และยาง"),
              "Wire & Cable": ("Dây & Cáp", "สายไฟและเคเบิล"),
              "Outdoor & Energy": ("Ngoài trời & Năng lượng", "กลางแจ้งและพลังงาน"),
              "Medical & Pharmacy": ("Y tế & Dược", "การแพทย์และเภสัช"),
              "Steel & Ceramics": ("Thép & Gốm sứ", "เหล็กและเซรามิก")}
INDUSTRY_MENU_DESC = {
 "/industries/pcb-electronics-labeling-solutions/":{"en":"Reflow-, wash- and ESD-safe identification for electronics.","zh":"耐回流焊、清洗与防静电的电子标识","vi":"Nhận diện chịu reflow, rửa và an toàn ESD cho điện tử.","th":"การระบุที่ทนรีโฟลว์ ล้าง และปลอดภัย ESD สำหรับอิเล็กทรอนิกส์"},
 "/industries/automotive-labeling-solutions/":{"en":"Vehicle, tire, battery and component identification.","zh":"汽车、轮胎、电池与零部件标识","vi":"Nhận diện xe, lốp, pin và linh kiện.","th":"การระบุยานพาหนะ ยาง แบตเตอรี่ และชิ้นส่วน"},
 "/industries/wire-cable-labeling-solutions/":{"en":"Durable marking for wire, cable and harness assemblies.","zh":"线缆与束线组件的耐久标识","vi":"Đánh dấu bền cho dây, cáp và bó dây.","th":"การทำเครื่องหมายทนทานสำหรับสายไฟ สายเคเบิล และชุดสายไฟ"},
 "/industries/outdoor-energy-labeling-solutions/":{"en":"Weatherable identification that survives years outdoors.","zh":"耐候标识，户外多年不失效","vi":"Nhận diện chịu thời tiết, bền nhiều năm ngoài trời.","th":"การระบุที่ทนสภาพอากาศ อยู่ได้หลายปีกลางแจ้ง"},
 "/industries/medical-pharmaceutical-labeling-solutions/":{"en":"Device, lab and cold-storage ID through sterilization.","zh":"器械、实验室与冷储标识，耐灭菌","vi":"Nhận diện thiết bị, phòng lab và bảo quản lạnh, chịu tiệt trùng.","th":"การระบุอุปกรณ์ ห้องแล็บ และการเก็บเย็น ผ่านการฆ่าเชื้อ"},
 "/industries/steel-metal-ceramic-labeling-solutions/":{"en":"High-temperature identification for metal processing.","zh":"金属加工的高温标识","vi":"Nhận diện nhiệt độ cao cho gia công kim loại.","th":"การระบุอุณหภูมิสูงสำหรับการแปรรูปโลหะ"},
}
# "By Brand" entries added to the Product mega-menu so the brand pages are findable.
BRAND_MENU = [
    ("/products/polyonics/", ("Polyonics", "Polyonics", "Polyonics", "Polyonics"),
     ("Imported polyimide labels — PCB, ESD & flame-retardant",
      "进口聚酰亚胺标签 —— PCB、防静电与阻燃",
      "Nhãn polyimide nhập khẩu — PCB, ESD & chống cháy",
      "ฉลากโพลีอิไมด์นำเข้า — PCB, ESD และหน่วงไฟ")),
    ("/products/item/e-series/", ("E-Label", "E-Label", "E-Label", "E-Label"),
     ("ETIA in-house polyimide PCB labels — general, ESD & removable",
      "ETIA 自研聚酰亚胺 PCB 标签 —— 通用、防静电与可移除",
      "Nhãn PCB polyimide tự phát triển của ETIA — phổ thông, ESD & tháo rời",
      "ฉลาก PCB โพลีอิไมด์ที่ ETIA พัฒนาเอง — ทั่วไป, ESD และถอดได้")),
    ("/products/heatproof/", ("HEATPROOF", "HEATPROOF", "HEATPROOF", "HEATPROOF"),
     ("Extreme-temperature labels & tags (to 1200 °C)",
      "极端高温标签与标牌（至 1200 °C）",
      "Nhãn & thẻ nhiệt độ cực cao (đến 1200 °C)",
      "ฉลากและแท็กอุณหภูมิสูงสุด (ถึง 1200 °C)")),
]
_LI = {"en": 0, "zh": 1, "vi": 2, "th": 3}

def simple_dropdown(lang, top_en, top_href, items, is_active, linkfn, descs=None, brands=None):
    zh = (lang == "zh")
    def lab(e, z):
        if zh: return z
        if lang == "vi" and e in _MENU_VITH: return _MENU_VITH[e][0]
        if lang == "th" and e in _MENU_VITH: return _MENU_VITH[e][1]
        return e
    top = navlab(lang, top_en)
    mob = "".join('<a class="ndma" href="%s">%s</a>' % (linkfn(u), esc(lab(e, z))) for e, z, u in items)
    if descs:  # mega-menu panel: name + short description per item
        find_lbl = P(lang,"Find a Label Material","查找标签材料","Tìm vật liệu nhãn","ค้นหาวัสดุฉลาก")
        find_sub = P(lang,"Search by part number, material or application",
                     "按料号、材料或应用搜索","Tìm theo mã, vật liệu hoặc ứng dụng","ค้นหาด้วยรหัส วัสดุ หรือการใช้งาน")
        finder = ('<a class="findrow" href="%s"><b>&#128269; %s</b><span>%s</span></a>'
                  % (linkfn("/products/find/"), esc(find_lbl), esc(find_sub)))
        desktop = finder + "".join('<a href="%s"><b>%s</b><span>%s</span></a>' % (
            linkfn(u), esc(lab(e, z)), esc(descs.get(u, {}).get(lang) or descs.get(u, {}).get("en", "")))
            for e, z, u in items)
        if brands:
            li = _LI.get(lang, 0)
            brand_lbl = P(lang, "By Brand", "按品牌", "Theo thương hiệu", "ตามแบรนด์")
            desktop += '<div class="megahd">%s</div>' % esc(brand_lbl)
            desktop += "".join('<a class="brandrow" href="%s"><b>%s</b><span>%s</span></a>' % (
                linkfn(u), esc(nm[li]), esc(ds[li])) for u, nm, ds in brands)
            mob += "".join('<a class="ndma" href="%s">%s</a>' % (linkfn(u), esc(nm[li])) for u, nm, ds in brands)
        panel = '<div class="ndm mega">%s</div>' % desktop
        mob = ('<a class="ndma find" href="%s">&#128269; %s</a>' % (linkfn("/products/find/"), esc(find_lbl))) + mob
    else:
        desktop = "".join('<a href="%s">%s</a>' % (linkfn(u), esc(lab(e, z))) for e, z, u in items)
        panel = '<div class="ndm sm">%s</div>' % desktop
    return ('<div class="nd" onmouseenter="etaOpen(this)" onmouseleave="etaClose(this)">'
            '<a class="ndt%s" href="%s" onclick="return etaProd(this,event)">%s <span class="caret">&#9662;</span></a>'
            '%s<div class="ndmob">%s</div></div>') % (
        (" on" if is_active else ""), linkfn(top_href), esc(top), panel, mob)

ALL_URLS = []   # (path, group, changefreq)  — English canonical set for sitemap
def track(path, group): ALL_URLS.append((path, group))

def hreflang_block(path, langs=None):
    t = []
    for lg in (langs or LANGS):
        t.append('<link rel="alternate" hreflang="%s" href="%s">' % (HREFLANG[lg], SITE + PREFIX[lg] + path))
    t.append('<link rel="alternate" hreflang="x-default" href="%s">' % (SITE + path))  # EN is x-default
    return "".join(t)

def breadcrumb_jsonld(items, lang):
    return {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":i+1,"name":n,"item":SITE+PREFIX[lang]+p} for i,(n,p) in enumerate(items)]}

NAV_TOGGLE = ('<button class="navtog" type="button" aria-label="Menu" onclick="etaMenu(this)">'
              '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">'
              '<path d="M4 7h16M4 12h16M4 17h16"/></svg></button>')

LANG_CODE = {"en": "EN", "zh": "CN", "vi": "VN", "th": "TH"}
def nav_html(lang, active, path="/", langs=None):
    langs = langs or ["en", "zh"]
    items = ""
    linkfn = lambda p: Lx(lang, p)
    for t, href, key in NAV_ITEMS:
        if key == "products":
            # Product dropdown lists the industry sectors directly (one level).
            items += simple_dropdown(lang, t, href, PROD_AXES[1][3], key == active, linkfn, descs=INDUSTRY_MENU_DESC, brands=BRAND_MENU)
        else:
            items += '<a href="%s"%s>%s</a>' % (Lx(lang, href), ' class="on"' if key==active else '', navlab(lang, t))
    if len(langs) > 2:
        # 4-language switcher chips (page exists in all of `langs`)
        sw = '<div class="langsw">%s</div>' % "".join(
            '<a href="%s"%s>%s</a>' % (PREFIX[lg] + path, ' class="on"' if lg == lang else '', LANG_CODE[lg])
            for lg in langs)
    else:
        other = "zh" if lang == "en" else "en"
        sw = '<a class="lang" href="%s">%s</a>' % (L(other, path), LANG_CODE[other])
    return '<nav><div class="navlinks">%s</div>%s%s</nav>' % (items, sw, NAV_TOGGLE)

FOOTER_LINKS = [("Home", "/"), ("Product", u_products()), ("Solutions", "/applications/"),
                ("Resources", "/insights/"), ("Service", "/service/"),
                ("About ETIA", "/about/"), ("Contact", "/contact/")]
FOOTER_I18N = {
 "heads": {"en": ("Navigation","Legal","Contact"), "zh": ("导航","法律","联系"),
           "vi": ("Điều hướng","Pháp lý","Liên hệ"), "th": ("เมนู","กฎหมาย","ติดต่อ")},
 "legal": {"en": ("Privacy Policy","Cookie Policy","Terms of Use"),
           "zh": ("隐私政策","Cookie 政策","使用条款"),
           "vi": ("Chính sách bảo mật","Chính sách cookie","Điều khoản sử dụng"),
           "th": ("นโยบายความเป็นส่วนตัว","นโยบายคุกกี้","ข้อกำหนดการใช้งาน")},
 "tag": {"en": "Supplier &amp; application-support partner — genuine, brand-authorized materials.",
         "zh": "特种工业标签的供应与应用支持伙伴 —— 正品、品牌授权材料。",
         "vi": "Đối tác cung ứng và hỗ trợ ứng dụng — vật liệu chính hãng, được ủy quyền thương hiệu.",
         "th": "พันธมิตรด้านการจัดหาและสนับสนุนการใช้งาน — วัสดุแท้ที่ได้รับอนุญาตจากแบรนด์"},
 "pc": {"en": ("Privacy","Cookies"), "zh": ("隐私","Cookie"),
        "vi": ("Bảo mật","Cookie"), "th": ("ความเป็นส่วนตัว","คุกกี้")},
}
def footer_html(lang):
    heads = FOOTER_I18N["heads"].get(lang, FOOTER_I18N["heads"]["en"])
    legals = FOOTER_I18N["legal"].get(lang, FOOTER_I18N["legal"]["en"])
    tag = FOOTER_I18N["tag"].get(lang, FOOTER_I18N["tag"]["en"])
    pc = FOOTER_I18N["pc"].get(lang, FOOTER_I18N["pc"]["en"])
    nav = "".join('<li><a href="%s">%s</a></li>' % (Lx(lang, p), navlab(lang, t)) for t, p in FOOTER_LINKS)
    legal = "".join('<li><a href="%s">%s</a></li>' % (Lx(lang, p), lt) for lt, p in
                    zip(legals, ["/privacy/","/cookies/","/terms/"]))
    return ("""<footer><div class="wrap">
<div class="flogo"><img src="https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com/IMAGO/LOGO/ETIA%%20LOGO.jpg" alt="ETIA Label"></div>
<div class="fg">
<div><h5>%s</h5><ul>%s</ul></div>
<div><h5>%s</h5><ul>%s</ul></div>
<div><h5>%s</h5><a class="email" href="mailto:etialabel@etia-tech.com">etialabel@etia-tech.com</a><br><br>
Shanghai · Hong Kong · Bangkok · Bac Ninh<br><span style="color:var(--faint)">%s</span></div>
</div>""" % (heads[0], nav, heads[1], legal, heads[2], tag)) + """
<div class="bar"><span>© 2026 ETIA-TECH (ASIA) Co., Limited. All rights reserved.</span><span><a href="%s">%s</a> &nbsp; <a href="%s">%s</a></span></div>
</div></footer>""" % (Lx(lang,"/privacy/"), pc[0], Lx(lang,"/cookies/"), pc[1])

TRUST_TITLES = {
 "en":["100% Quality Inspection","Application-Driven Solutions","Flexible Supply","Responsive Application Support"],
 "zh":["100% 质量检测","应用驱动方案","柔性供应","快速应用支持"],
 "vi":["Kiểm tra chất lượng 100%","Giải pháp theo ứng dụng","Cung ứng linh hoạt","Hỗ trợ ứng dụng kịp thời"],
 "th":["การตรวจสอบคุณภาพ 100%","โซลูชันที่ขับเคลื่อนด้วยการใช้งาน","การจัดหาที่ยืดหยุ่น","การสนับสนุนการใช้งานที่ตอบสนองรวดเร็ว"],
}
def trust_bar(lang):
    items="".join('<div class="ti">%s</div>'%esc(t) for t in TRUST_TITLES.get(lang, TRUST_TITLES["en"]))
    return '<section class="trustbar"><div class="wrap">%s</div></section>' % items

CTA_I18N = {
 "en": ("Start with the Application. Finish with the Right Material.",
        "Tell us the surface, temperature, chemistry and print method — we'll recommend the material and arrange samples.",
        "Talk to a Specialist", "Talk to an Engineer"),
 "zh": ("始于应用。终于选对材料。",
        "告知表面、温度、化学环境与打印方式,我们推荐材料并安排样品验证。",
        "咨询专家", "咨询工程师"),
 "vi": ("Bắt đầu từ ứng dụng. Kết thúc bằng đúng vật liệu.",
        "Hãy cho biết bề mặt, nhiệt độ, môi trường hóa chất và phương pháp in — chúng tôi sẽ đề xuất vật liệu và chuẩn bị mẫu.",
        "Trao đổi với chuyên gia", "Trao đổi với kỹ sư"),
 "th": ("เริ่มจากการใช้งาน จบด้วยวัสดุที่ถูกต้อง",
        "บอกเราถึงพื้นผิว อุณหภูมิ สภาพแวดล้อมทางเคมี และวิธีการพิมพ์ แล้วเราจะแนะนำวัสดุและจัดเตรียมตัวอย่าง",
        "ปรึกษาผู้เชี่ยวชาญ", "ปรึกษาวิศวกร"),
}
def cta(lang):
    h, p, b1, b2 = CTA_I18N.get(lang, CTA_I18N["en"])
    u = L(lang, "/contact/")
    return ('<div class="cta"><div class="ic">⚡</div><h3>%s</h3><p>%s</p>'
            '<div class="btns"><a class="btn pri" href="%s">%s</a>'
            '<a class="btn on-dark" href="%s">%s</a></div></div>') % (
        esc(h), esc(p), u, esc(b1), u, esc(b2))

# Per-page bottom CTA (question headline + <=2 sentences + primary + secondary).
CTAS = {
 "home": {"h": ("Find the Right Material for Your Application.", "为您的应用找到合适的材料。",
                "Tìm đúng vật liệu cho ứng dụng của bạn.", "ค้นหาวัสดุที่เหมาะกับการใช้งานของคุณ"),
   "body": ("Tell us about the surface, temperature, chemical exposure, printing method and expected service life. We'll help you narrow down the right material and prepare samples for evaluation.",
            "告诉我们贴附表面、温度、化学暴露、打印方式与预期使用寿命，我们将帮您缩小材料范围并准备样品供评估。",
            "Hãy cho biết bề mặt, nhiệt độ, môi trường hóa chất, phương pháp in và tuổi thọ dự kiến. Chúng tôi sẽ giúp bạn khoanh vùng vật liệu phù hợp và chuẩn bị mẫu để đánh giá.",
            "บอกเราถึงพื้นผิว อุณหภูมิ การสัมผัสสารเคมี วิธีการพิมพ์ และอายุการใช้งานที่คาดหวัง เราจะช่วยคัดกรองวัสดุที่เหมาะสมและเตรียมตัวอย่างเพื่อประเมิน"),
   "b1": ("Talk to a Material Specialist", "咨询材料专家", "Trao đổi với chuyên gia vật liệu", "ปรึกษาผู้เชี่ยวชาญด้านวัสดุ"), "b1u": "/contact/",
   "b2": ("Send Us Your Requirements", "提交您的需求", "Gửi yêu cầu của bạn", "ส่งข้อกำหนดของคุณ"), "b2u": "/contact/"},
 "products": {"h": ("Need Help Comparing Materials?", "需要帮助比较材料？",
                     "Cần trợ giúp so sánh vật liệu?", "ต้องการความช่วยเหลือในการเปรียบเทียบวัสดุ?"),
   "body": ("Share your performance requirements and preferred construction. We will help you compare suitable material options based on temperature, surface, adhesive, printing, and durability needs.",
            "告诉我们您的性能要求与倾向的材料结构，我们将根据温度、表面、胶粘剂、打印与耐久性需求，帮您比较合适的材料选项。",
            "Hãy cho biết yêu cầu hiệu suất và cấu tạo mong muốn. Chúng tôi sẽ giúp bạn so sánh các vật liệu phù hợp theo nhiệt độ, bề mặt, keo dán, in ấn và độ bền.",
            "แบ่งปันข้อกำหนดด้านประสิทธิภาพและโครงสร้างที่ต้องการ เราจะช่วยเปรียบเทียบตัวเลือกวัสดุที่เหมาะสมตามอุณหภูมิ พื้นผิว กาว การพิมพ์ และความทนทาน"),
   "b1": ("Get Material Recommendations", "获取材料推荐", "Nhận đề xuất vật liệu", "รับคำแนะนำวัสดุ"), "b1u": "/contact/",
   "b2": ("Request Technical Data", "索取技术数据", "Yêu cầu dữ liệu kỹ thuật", "ขอข้อมูลทางเทคนิค"), "b2u": "/contact/"},
 "applications": {"h": ("Have a Specific Application Challenge?", "有具体的应用难题？",
                         "Bạn có thách thức ứng dụng cụ thể?", "มีความท้าทายด้านการใช้งานเฉพาะหรือไม่?"),
   "body": ("Describe where the label will be used, what it must withstand, and how it will be printed. We will help you identify the key material requirements and recommend a practical starting point.",
            "描述标签的使用位置、需承受的工况以及打印方式，我们将帮您梳理关键材料要求，并给出可落地的选型起点。",
            "Hãy cho biết nhãn sẽ được dùng ở đâu, phải chịu những gì và sẽ được in như thế nào. Chúng tôi sẽ giúp bạn xác định các yêu cầu vật liệu then chốt và đề xuất điểm khởi đầu thực tế.",
            "บอกเราว่าจะใช้ฉลากที่ไหน ต้องทนอะไร และจะพิมพ์อย่างไร เราจะช่วยระบุข้อกำหนดวัสดุสำคัญและแนะนำจุดเริ่มต้นที่ใช้งานได้จริง"),
   "b1": ("Discuss Your Application", "沟通您的应用", "Trao đổi về ứng dụng", "ปรึกษาเรื่องการใช้งาน"), "b1u": "/contact/",
   "b2": ("Talk to a Specialist", "咨询专家", "Trao đổi với chuyên gia", "ปรึกษาผู้เชี่ยวชาญ"), "b2u": "/contact/"},
 "insights": {"h": ("Still Have Questions After Reading?", "读完仍有疑问？",
                     "Vẫn còn thắc mắc sau khi đọc?", "ยังมีคำถามหลังจากอ่านหรือไม่?"),
   "body": ("Technical articles can explain the principles, but every process is different. Send us your application details and our team will help you translate the guidance into a suitable material choice.",
            "技术文章讲的是原理，但每个工艺都不同。把您的应用细节发给我们，团队会帮您把这些指南转化为合适的材料选择。",
            "Các bài viết kỹ thuật có thể giải thích nguyên lý, nhưng mỗi quy trình đều khác nhau. Hãy gửi chi tiết ứng dụng của bạn và đội ngũ của chúng tôi sẽ giúp chuyển hướng dẫn thành lựa chọn vật liệu phù hợp.",
            "บทความทางเทคนิคอธิบายหลักการได้ แต่ทุกกระบวนการแตกต่างกัน ส่งรายละเอียดการใช้งานของคุณมาให้เรา แล้วทีมของเราจะช่วยแปลงคำแนะนำเป็นการเลือกวัสดุที่เหมาะสม"),
   "b1": ("Ask a Material Question", "提出材料问题", "Đặt câu hỏi về vật liệu", "ถามคำถามเกี่ยวกับวัสดุ"), "b1u": "/contact/",
   "b2": ("Explore Applications", "浏览应用笔记", "Khám phá ứng dụng", "สำรวจการใช้งาน"), "b2u": "/applications/"},
 "service": {"h": ("Looking for Material or Production Support?", "需要材料或生产方面的支持？",
                    "Cần hỗ trợ về vật liệu hoặc sản xuất?", "กำลังมองหาการสนับสนุนด้านวัสดุหรือการผลิต?"),
   "body": ("Whether you need help with material selection, testing, converting, quality control, or repeat supply, our team is ready to support your project with clear and practical guidance.",
            "无论是材料选型、检测、加工、质量控制还是持续供应，我们的团队都能以清晰、务实的建议支持您的项目。",
            "Dù bạn cần hỗ trợ về lựa chọn vật liệu, thử nghiệm, gia công, kiểm soát chất lượng hay cung ứng lặp lại, đội ngũ của chúng tôi luôn sẵn sàng hỗ trợ dự án của bạn với hướng dẫn rõ ràng và thiết thực.",
            "ไม่ว่าคุณต้องการความช่วยเหลือด้านการเลือกวัสดุ การทดสอบ การแปรรูป การควบคุมคุณภาพ หรือการจัดหาซ้ำ ทีมของเราพร้อมสนับสนุนโครงการของคุณด้วยคำแนะนำที่ชัดเจนและใช้งานได้จริง"),
   "b1": ("Talk to a Specialist", "咨询专家", "Trao đổi với chuyên gia", "ปรึกษาผู้เชี่ยวชาญ"), "b1u": "/contact/",
   "b2": ("Submit Your Requirements", "提交您的需求", "Gửi yêu cầu của bạn", "ส่งข้อกำหนดของคุณ"), "b2u": "/contact/"},
 "application-note": {"h": ("Need a Material Recommendation for This Application?", "需要这个应用的材料推荐？"),
   "body": ("Share your surface, temperature, chemical exposure, and printing requirements. We will help you identify suitable options for testing.",
            "告诉我们表面、温度、化学暴露与打印要求，我们将帮您筛选出可供测试的合适选项。"),
   "b1": ("Request a Recommendation", "申请选型推荐"), "b1u": "/contact/",
   "b2": ("Talk to a Specialist", "咨询专家"), "b2u": "/contact/"},
 "case-study": {"h": ("Facing a Similar Identification Challenge?", "面临类似的标识难题？"),
   "body": ("Tell us about your process and operating conditions. We will review the application and help you evaluate a suitable material construction.",
            "告诉我们您的工艺与工况，我们将评估应用并帮您选出合适的材料结构。"),
   "b1": ("Discuss a Similar Project", "沟通类似项目"), "b1u": "/contact/",
   "b2": ("Talk to a Specialist", "咨询专家"), "b2u": "/contact/"},
 "product-detail": {"h": ("Need to Confirm Whether This Material Is Suitable?", "需要确认这款材料是否适用？"),
   "body": ("Send us your application conditions and printing requirements. We will help you evaluate fit, available formats, and sample options.",
            "把您的应用工况与打印要求发给我们，我们将帮您评估适用性、可选规格与样品方案。"),
   "b1": ("Check Material Suitability", "确认材料适用性"), "b1u": "/contact/",
   "b2": ("FREE SAMPLE", "免费样品"), "b2u": "/contact/"},
}

def cta2(lang, kind, linkfn=L):
    c = CTAS.get(kind, CTAS["home"])
    li = {"en": 0, "zh": 1, "vi": 2, "th": 3}.get(lang, 0)
    pk = lambda t: t[li] if li < len(t) else t[0]
    return ('<div class="cta cta-q"><h3>%s</h3><p>%s</p>'
            '<div class="btns"><a class="btn pri" href="%s">%s</a>'
            '<a class="btn on-dark" href="%s">%s</a></div></div>') % (
        esc(pk(c["h"])), esc(pk(c["body"])), linkfn(lang, c["b1u"]), esc(pk(c["b1"])),
        linkfn(lang, c["b2u"]), esc(pk(c["b2"])))

def page(lang, path, title, desc, h1, lede, body, crumb, schema_extra=None, active="", trust=True, hero=None, langs=None, keywords=""):
    canonical = SITE + PREFIX[lang] + path
    kw_meta = ('<meta name="keywords" content="%s">' % esc(keywords)) if keywords else ""
    sch = [breadcrumb_jsonld(crumb, lang)] + (schema_extra or [])
    schema_js = "".join('<script type="application/ld+json">%s</script>' % json.dumps(s, ensure_ascii=False) for s in sch)
    cr = ' &rsaquo; '.join((('<a href="%s">%s</a>' % (Lx(lang,p), esc(n))) if p and i < len(crumb)-1 else '<b>%s</b>' % esc(n))
                           for i,(n,p) in enumerate(crumb))
    lede_html = ('<p class="lede">%s</p>' % lede) if lede else ""
    # hero (when given) replaces the plain pagehead block — used for the industry
    # landing HERO SECTION (label + slogan, banner-ready).
    head_block = hero if hero else ('<div class="wrap"><div class="pagehead"><h1>%s</h1>%s</div></div>' % (esc(h1), lede_html))
    return """<!doctype html><html lang="%s"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<link rel="icon" type="image/png" href="/favicon.png"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com" crossorigin><link rel="dns-prefetch" href="https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com">
<title>%s</title><meta name="description" content="%s">%s
<link rel="canonical" href="%s">%s
<meta property="og:title" content="%s"><meta property="og:type" content="website"><meta property="og:site_name" content="ETIA Label">
<style>%s</style>%s</head><body>
<div class="topstrip"></div>
<header><div class="wrap"><a class="logo" href="%s"><img src="https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com/IMAGO/LOGO/ETIA%%20LOGO.jpg" alt="ETIA Label"></a>%s</div></header>
<div class="wrap"><div class="crumb">%s</div></div>
%s
%s
%s
%s
<script>
function etaOpen(n){clearTimeout(n._t);n.classList.add('open');}
function etaMenu(b){var n=b.closest('nav');if(n)n.classList.toggle('open');}
function etaMob(b){var g=b.closest('.ndmg');if(g)g.classList.toggle('open');}
function etaProd(b,e){if(window.innerWidth<=900){if(e&&e.preventDefault)e.preventDefault();b.closest('.nd').classList.toggle('mopen');return false;}return true;}
function etaClose(n){n._t=setTimeout(function(){n.classList.remove('open');},180);}
function etaSub(b,s){var m=b?b.closest('.ndm'):(document.querySelector('.nd.open .ndm')||document.querySelector('.ndm'));if(!m)return;
if(b&&b.classList&&b.classList.contains('axitem'))m.querySelectorAll('.axitem').forEach(function(x){x.classList.toggle('on',x===b);});
m.querySelectorAll('.subgroup').forEach(function(p){p.style.display=(p.getAttribute('data-sub')===s)?'flex':'none';});}
function etaAx(b,a){var m=b.closest('.ndm');
m.querySelectorAll('.axbtn').forEach(function(x){x.classList.toggle('on',x===b);});
m.querySelectorAll('.midgroup').forEach(function(p){p.style.display=(p.getAttribute('data-mid')===a)?'flex':'none';});
var mg=m.querySelector('.midgroup[data-mid="'+a+'"]');var first=mg?mg.querySelector('.axitem.haskid'):null;
etaSub(first,first?first.getAttribute('data-sub'):'');}
</script>
</body></html>""" % (lang, esc(title), esc(desc), kw_meta, canonical, hreflang_block(path, langs), esc(title), CSS, schema_js,
     Lx(lang,"/"), nav_html(lang, active, path, langs), cr, head_block, (trust_bar(lang) if trust else ""), body, footer_html(lang))

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

# Introduced product landing pages, in display order (home best-sellers first).
# Add a slug here when a product's page is ready — it then appears in the /products/
# catalog and is internally linked for SEO. Missing files are skipped safely.
FEATURED_PRODUCTS = [
  # Trimmed for launch — keep only the high-temp and low-temp solutions live.
  # The rest are retained as data files (data/products/*.json) and will be
  # re-added here as their pages are finalized.
  "high-heat-identification",       # high temperature
  "cold-chain-cryogenic-labels",    # low temperature
]

def build_products_hub(lang):
    # Featured product catalog — every introduced product landing page. This is the
    # single "products entry" the home best-sellers link into, and the SEO backbone
    # (internal links to every product page). Grows as new products are introduced.
    def _plang(node):
        if not isinstance(node, dict): return node or ""
        return node.get(lang) or node.get("en") or node.get("zh") or ""
    pcat=""
    for slug in FEATURED_PRODUCTS:
        fp=os.path.join(BUILD_DIR,"data","products",slug+".json")
        if not os.path.exists(fp): continue
        p=json.load(open(fp,encoding="utf-8"))
        pcat+='<a class="card" href="%s"><h3>%s</h3><p>%s</p></a>'%(
            Lx(lang,"/products/item/%s/"%slug), esc(_plang(p.get("title",{}))), esc(_plang(p.get("tagline",{}))))
    catalog_section=('<section class="blk"><div class="wrap"><div class="eyebrow">%s</div><h2>%s</h2>'
                     '<div class="sub">%s</div><div class="grid grid2">%s</div></div></section>')%(
        ("产品目录" if lang=="zh" else "PRODUCTS"),
        ("产品精选" if lang=="zh" else "Featured Products"),
        ("按型号浏览已上线的 ETIA 特种标签产品，更多产品陆续补充。" if lang=="zh"
         else "Browse ETIA specialty label products by model — more are added over time."),
        pcat)
    # Secondary route — find by industry & application
    routes = [
      ("按行业与应用" if lang=="zh" else "By Industry & Application",
       "金属与陶瓷、汽车 —— 从您的行业与应用出发选型" if lang=="zh"
       else "Metal & ceramics and automotive — start from your industry and application.",
       "/industries/"),
    ]
    rcards = "".join('<a class="card" href="%s"><h3>%s</h3><p>%s</p><div class="rows" style="color:var(--blue);font-weight:700;margin-top:10px">%s →</div></a>'%(
        L(lang,u), esc(t), esc(d), ("进入" if lang=="zh" else "Explore")) for t,d,u in routes)
    body = (catalog_section +
        '<section class="blk" style="background:var(--tint-blue)"><div class="wrap"><h2>%s</h2><div class="sub">%s</div><div class="grid grid2">%s</div></div></section>'
            '<div class="wrap">%s</div>') % (
        ("从应用出发" if lang=="zh" else "Start from your application"),
        ("从您的行业与应用出发,匹配适配的耐久标签材料。" if lang=="zh"
         else "Start from your industry and application to match the right durable label material."),
        rcards, cta(lang))
    h1 = "产品与解决方案" if lang=="zh" else "Products & Solutions"
    lede = ("从您的行业与应用出发,找到适配的耐久标签材料。" if lang=="zh"
            else "Find durable label materials matched to your application.")
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
        cta2(lang,"product-detail"))
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
        cta2(lang,"product-detail"))
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
    # All industry sectors, mirroring the home "Solutions by Industry" carousel
    # and the nav "By Industry" menu (image-top cards).
    focus = HOME_I18N[lang]["focus"]
    explore = HOME_I18N[lang].get("explore", "View")
    cards = ""
    for k, f in enumerate(focus):
        img = f.get("img", "")
        im = ('<img src="%s" alt="%s" loading="lazy" onerror="this.remove()">' % (esc(img), esc(f["name"]))) if img else ""
        cards += ('<a class="acard" href="%s"><div class="acard-img g%d">%s</div>'
                  '<div class="acard-body"><h3 class="indname">%s</h3><p>%s</p>'
                  '<div class="acard-go">%s →</div></div></a>') % (
            L(lang, FOCUS_URLS[k]), k % 6, im, esc(f["name"]), esc(f["desc"]), esc(explore))
    h1 = "行业与应用" if lang == "zh" else "Industries & Applications"
    body = '<section class="blk"><div class="wrap"><div class="grid">%s</div></div></section><div class="wrap">%s</div>' % (cards, cta(lang))
    crumb=[("Home","/"),("Industries & Applications",u_ind_hub())]
    write(lang, u_ind_hub(), page(lang, u_ind_hub(),
        ("行业与应用 | ETIA" if lang=="zh" else "Industries & Applications | ETIA"),
        ("从您的行业与应用出发,匹配合适的标签材料。" if lang=="zh"
         else "Start from your industry and application to match the right label material."),
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
        ("推荐工艺线" if lang=="zh" else "Recommended process lines"), proclinks, cta2(lang,"applications"))
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
        cta2(lang,"applications"))
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
    "contactPoint":[{"@type":"ContactPoint","contactType":"sales","email":"etialabel@etia-tech.com"}]}

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
 ("Automotive","汽车制造","/industries/automotive-labeling-solutions/",
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
    # explicit icon per HOME_FOCUS entry: Metal&Ceramics -> flame(1), Automotive -> car(3), PCB -> chip(0)
    focus_icons=[3]  # Automotive -> car icon
    for k,(fe,fz,u,apps_en,apps_zh) in enumerate(HOME_FOCUS):
        pills="".join('<span>%s</span>'%esc(a) for a in (apps_zh if lang=="zh" else apps_en))
        cards+=('<a class="card indcard" href="%s"><div class="ic">%s</div>'
                '<div class="body"><h3>%s</h3><div class="apps">%s</div><div class="go">%s →</div></div></a>')%(
            L(lang,u), INDUSTRY_ICONS[focus_icons[k%len(focus_icons)]], esc(fz if lang=="zh" else fe),
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
    # home internal link: en -> path, zh -> /cn+path (inner zh exists),
    # vi/th -> localized only for 4-language paths (pillars, insights, industries), else English.
    if lang=="zh": return "/cn"+path
    if lang in ("vi","th") and (path in FOURLANG or path.startswith(FOURLANG_PREFIX)):
        return PREFIX[lang]+path
    return path

def home_switcher(active):
    out=""
    for lg in HOME_LANGS:
        href = "/" if lg=="en" else HL_PREFIX[lg]+"/"
        out += '<a href="%s"%s>%s</a>' % (href, ' class="on"' if lg==active else '', esc(HOME_I18N["lang_name"][lg]))
    return '<span class="langsw">%s</span>' % out

def home_nav(lang):
    lf=lambda p: home_hlink(lang,p)
    # Product dropdown lists the industry sectors directly (matches nav_html).
    prod=simple_dropdown(lang, "Product", "/products/", PROD_AXES[1][3], False, lf, descs=INDUSTRY_MENU_DESC, brands=BRAND_MENU)
    home_lbl={"en":"Home","zh":"首页","vi":"Trang chủ","th":"หน้าแรก"}.get(lang,"Home")
    home_link='<a href="%s">%s</a>'%(lf("/"),esc(home_lbl))
    # top nav after Product: Solutions, Resources, Service
    app_lbl={"en":"Solutions","zh":"方案","vi":"Giải pháp","th":"โซลูชัน"}.get(lang,"Solutions")
    ins_lbl={"en":"Resources","zh":"资讯","vi":"Tài nguyên","th":"แหล่งข้อมูล"}.get(lang,"Resources")
    sv_lbl={"en":"Service","zh":"服务","vi":"Dịch vụ","th":"บริการ"}.get(lang,"Service")
    links=('<a href="%s">%s</a><a href="%s">%s</a><a href="%s">%s</a>'%(
        lf("/applications/"),esc(app_lbl),lf("/insights/"),esc(ins_lbl),lf("/service/"),esc(sv_lbl)))
    return '<nav><div class="navlinks">%s%s%s</div>%s%s</nav>' % (
        home_link, prod, links, home_switcher(lang), NAV_TOGGLE)

def home_footer(lang):
    T=HOME_I18N[lang]; nh,lh,ch=T["footer_heads"]
    # footer nav mirrors the top nav: Product · Application · Resources · Service
    foot_nav=[("/products/",{"en":"Product","zh":"产品","vi":"Sản phẩm","th":"ผลิตภัณฑ์"}.get(lang,"Product")),
              ("/applications/",{"en":"Application","zh":"应用","vi":"Ứng dụng","th":"การใช้งาน"}.get(lang,"Application")),
              ("/insights/",{"en":"Resources","zh":"资讯","vi":"Tài nguyên","th":"แหล่งข้อมูล"}.get(lang,"Resources")),
              ("/service/",{"en":"Service","zh":"服务","vi":"Dịch vụ","th":"บริการ"}.get(lang,"Service"))]
    navl="".join('<li><a href="%s">%s</a></li>'%(home_hlink(lang,h),esc(l)) for h,l in foot_nav)
    legal="".join('<li><a href="%s">%s</a></li>'%(home_hlink(lang,p),t) for p,t in
                  [("/privacy/","Privacy Policy"),("/cookies/","Cookie Policy"),("/terms/","Terms of Use")])
    return ('<footer><div class="wrap"><div class="flogo"><img src="https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com/IMAGO/LOGO/ETIA%%20LOGO.jpg" alt="ETIA Label"></div>'
            '<div class="fg"><div><h5>%s</h5><ul>%s</ul></div><div><h5>%s</h5><ul>%s</ul></div>'
            '<div><h5>%s</h5><a class="email" href="mailto:etialabel@etia-tech.com">etialabel@etia-tech.com</a><br><br>'
            'Shanghai · Hong Kong · Bangkok · Bac Ninh</div></div>'
            '<div class="bar"><span>© 2026 ETIA-TECH (ASIA) Co., Limited. All rights reserved.</span></div></div></footer>') % (
        esc(nh),navl,esc(lh),legal,esc(ch))

def home_hreflang(path):
    t=[]
    for lg in HOME_LANGS:
        t.append('<link rel="alternate" hreflang="%s" href="%s%s%s">'%(lg,SITE,HL_PREFIX[lg],path))
    t.append('<link rel="alternate" hreflang="x-default" href="%s%s">'%(SITE,path))
    return "".join(t)

# New home structure: hero + 4 gateway sections (Products / Applications / Insights / Service).
# EN copy supplied by client; ZH translated; vi/th fall back to EN.
HOME2 = {
 "en": {
  "hero": {"eyebrow": "DURABLE IDENTIFICATION · SPECIALTY LABEL MATERIALS",
           "h1": "Where Materials Meet Applications.",
           "line": "Every demanding application starts with the right material.",
           "body": "For over 20 years, ETIA has helped manufacturers solve complex identification challenges through specialty materials, application expertise, and flexible supply.",
           "b1": "Explore Solutions", "b2": "Talk to a Specialist"},
  "sections": [
   {"eyebrow": "SPECIALTY LABEL MATERIALS · ENGINEERED CONSTRUCTIONS",
    "h2": "Materials Built for Demanding Conditions.",
    "sub": "The right construction starts with the right performance requirements.",
    "body": "Explore specialty label materials for high temperature, cryogenic storage, chemical exposure, outdoor durability, difficult surfaces, and long-term industrial identification.",
    "b1": "Explore Materials", "b1u": "/products/", "b2": "Request Material Support", "b2u": "/contact/"},
   {"eyebrow": "INDUSTRIES · PROCESSES · OPERATING CONDITIONS",
    "h2": "Applications Drive Material Selection.",
    "sub": "Every application starts with the right material.",
    "body": "Explore application notes developed around real surfaces, temperatures, chemicals, printing methods, processes, and service-life requirements.",
    "b1": "Explore Applications", "b1u": "/products/", "b2": "Discuss Your Application", "b2u": "/contact/"},
   {"eyebrow": "TECHNICAL GUIDANCE · MATERIAL KNOWLEDGE · CASE STUDIES",
    "h2": "Knowledge Drives Better Decisions.",
    "sub": "Application notes, material insights, industry news, and expert guidance.",
    "body": "Explore technical guidance, material-selection insights, performance testing, printing considerations, and real-world case studies.",
    "b1": "Read Application Notes", "b1u": "/application-notes/", "b2": "View Case Studies", "b2u": "/products/"},
   {"eyebrow": "APPLICATION SUPPORT · TESTING · FLEXIBLE SUPPLY",
    "h2": "Responsive Service Drives Success.",
    "sub": "Every project is backed by fast, reliable expert support.",
    "body": "From application review and sample evaluation to laboratory testing, converting, quality inspection, and repeat supply, ETIA helps manufacturers move confidently from selection to production.",
    "b1": "Talk to a Material Specialist", "b1u": "/contact/", "b2": "Talk to a Specialist", "b2u": "/contact/"},
  ]},
 "zh": {
  "hero": {"eyebrow": "耐久标识 · 特种标签材料",
           "h1": "让材料匹配应用。",
           "line": "每一个严苛应用，都始于选对材料。",
           "body": "20 多年来，ETIA 以特种材料、应用专业与柔性供应，帮助制造商解决复杂的标识难题。",
           "b1": "浏览方案", "b2": "咨询专家"},
  "sections": [
   {"eyebrow": "特种标签材料 · 工程化结构",
    "h2": "为严苛工况而生的材料。",
    "sub": "合适的材料结构，始于明确的性能要求。",
    "body": "探索适用于高温、深低温储存、化学暴露、户外耐久、难贴表面及长期工业标识的特种标签材料。",
    "b1": "浏览材料", "b1u": "/products/", "b2": "获取材料支持", "b2u": "/contact/"},
   {"eyebrow": "行业 · 工艺 · 工况",
    "h2": "应用驱动材料选择。",
    "sub": "每一个应用，都始于选对材料。",
    "body": "查阅围绕真实表面、温度、化学品、打印方式、工艺与使用寿命要求编写的应用笔记。",
    "b1": "浏览应用笔记", "b1u": "/products/", "b2": "沟通您的应用", "b2u": "/contact/"},
   {"eyebrow": "技术指南 · 材料知识 · 案例研究",
    "h2": "知识驱动更好的决策。",
    "sub": "应用笔记、材料洞察、行业动态与专家见解，一站获取。",
    "body": "探索技术指南、材料选型洞察、性能测试、打印要点与真实案例研究。",
    "b1": "浏览应用笔记", "b1u": "/application-notes/", "b2": "查看案例", "b2u": "/products/"},
   {"eyebrow": "应用支持 · 检测 · 柔性供应",
    "h2": "快速响应，驱动项目成功。",
    "sub": "每一个项目，都有快速、可靠的专业支持。",
    "body": "从应用评估、样品验证，到实验室检测、加工成型、质量检验与持续供应，ETIA 帮助制造商从选型稳步走向量产。",
    "b1": "咨询材料专家", "b1u": "/contact/", "b2": "咨询专家", "b2u": "/contact/"},
  ]},
 "vi": {
  "hero": {"eyebrow": "NHẬN DIỆN BỀN VỮNG · VẬT LIỆU NHÃN CHUYÊN DỤNG",
           "h1": "Nơi vật liệu đáp ứng đúng ứng dụng.",
           "line": "Mỗi ứng dụng khắt khe đều bắt đầu từ việc chọn đúng vật liệu.",
           "body": "Hơn 20 năm qua, ETIA đã giúp các nhà sản xuất giải quyết những thách thức nhận diện phức tạp bằng vật liệu chuyên dụng, chuyên môn ứng dụng và nguồn cung linh hoạt.",
           "b1": "Khám phá giải pháp", "b2": "Trao đổi với chuyên gia"},
  "sections": [
   {"eyebrow": "VẬT LIỆU NHÃN CHUYÊN DỤNG · CẤU TRÚC KỸ THUẬT",
    "h2": "Vật liệu cho những điều kiện khắt khe.",
    "sub": "Cấu trúc phù hợp bắt đầu từ yêu cầu hiệu suất rõ ràng.",
    "body": "Khám phá vật liệu nhãn chuyên dụng cho nhiệt độ cao, lưu trữ siêu lạnh, tiếp xúc hóa chất, độ bền ngoài trời, bề mặt khó dán và nhận diện công nghiệp dài hạn.",
    "b1": "Khám phá vật liệu", "b1u": "/products/", "b2": "Yêu cầu hỗ trợ vật liệu", "b2u": "/contact/"},
   {"eyebrow": "NGÀNH · QUY TRÌNH · ĐIỀU KIỆN VẬN HÀNH",
    "h2": "Ứng dụng quyết định lựa chọn vật liệu.",
    "sub": "Mọi ứng dụng đều bắt đầu từ vật liệu phù hợp.",
    "body": "Khám phá các ghi chú ứng dụng được xây dựng từ bề mặt, nhiệt độ, hóa chất, phương pháp in, quy trình và yêu cầu tuổi thọ thực tế.",
    "b1": "Khám phá ứng dụng", "b1u": "/products/", "b2": "Trao đổi về ứng dụng", "b2u": "/contact/"},
   {"eyebrow": "HƯỚNG DẪN KỸ THUẬT · KIẾN THỨC VẬT LIỆU · NGHIÊN CỨU TÌNH HUỐNG",
    "h2": "Kiến thức tạo nên quyết định tốt hơn.",
    "sub": "Ghi chú ứng dụng, hiểu biết vật liệu, tin ngành và tư vấn chuyên gia.",
    "body": "Khám phá hướng dẫn kỹ thuật, kinh nghiệm chọn vật liệu, thử nghiệm hiệu suất, lưu ý khi in và các tình huống thực tế.",
    "b1": "Đọc ghi chú ứng dụng", "b1u": "/application-notes/", "b2": "Xem nghiên cứu tình huống", "b2u": "/products/"},
   {"eyebrow": "HỖ TRỢ ỨNG DỤNG · THỬ NGHIỆM · CUNG ỨNG LINH HOẠT",
    "h2": "Dịch vụ nhanh nhạy thúc đẩy thành công.",
    "sub": "Mọi dự án đều được hỗ trợ chuyên gia nhanh chóng, đáng tin cậy.",
    "body": "Từ đánh giá ứng dụng, thử mẫu, đến thử nghiệm phòng lab, gia công, kiểm tra chất lượng và cung ứng lặp lại, ETIA giúp nhà sản xuất tự tin đi từ lựa chọn đến sản xuất.",
    "b1": "Trao đổi với chuyên gia vật liệu", "b1u": "/contact/", "b2": "Trao đổi với chuyên gia", "b2u": "/contact/"},
  ]},
 "th": {
  "hero": {"eyebrow": "ระบบระบุข้อมูลที่ทนทาน · วัสดุฉลากเฉพาะทาง",
           "h1": "จุดที่วัสดุตอบโจทย์การใช้งานจริง",
           "line": "ทุกการใช้งานที่ท้าทายเริ่มต้นจากการเลือกวัสดุที่ถูกต้อง",
           "body": "ตลอดกว่า 20 ปี ETIA ช่วยผู้ผลิตแก้ปัญหาการระบุข้อมูลที่ซับซ้อน ด้วยวัสดุเฉพาะทาง ความเชี่ยวชาญด้านการใช้งาน และการจัดหาที่ยืดหยุ่น",
           "b1": "สำรวจโซลูชัน", "b2": "ปรึกษาผู้เชี่ยวชาญ"},
  "sections": [
   {"eyebrow": "วัสดุฉลากเฉพาะทาง · โครงสร้างเชิงวิศวกรรม",
    "h2": "วัสดุที่สร้างมาเพื่อสภาวะที่ท้าทาย",
    "sub": "โครงสร้างที่เหมาะสมเริ่มจากข้อกำหนดด้านสมรรถนะที่ชัดเจน",
    "body": "สำรวจวัสดุฉลากเฉพาะทางสำหรับอุณหภูมิสูง การจัดเก็บเย็นจัด การสัมผัสสารเคมี ความทนทานกลางแจ้ง พื้นผิวที่ติดยาก และการระบุข้อมูลอุตสาหกรรมระยะยาว",
    "b1": "สำรวจวัสดุ", "b1u": "/products/", "b2": "ขอการสนับสนุนด้านวัสดุ", "b2u": "/contact/"},
   {"eyebrow": "อุตสาหกรรม · กระบวนการ · สภาวะการทำงาน",
    "h2": "การใช้งานกำหนดการเลือกวัสดุ",
    "sub": "ทุกการใช้งานเริ่มต้นด้วยวัสดุที่ถูกต้อง",
    "body": "สำรวจแอปพลิเคชันโน้ตที่พัฒนาจากพื้นผิว อุณหภูมิ สารเคมี วิธีการพิมพ์ กระบวนการ และข้อกำหนดอายุการใช้งานจริง",
    "b1": "สำรวจการใช้งาน", "b1u": "/products/", "b2": "ปรึกษาเรื่องการใช้งาน", "b2u": "/contact/"},
   {"eyebrow": "คำแนะนำทางเทคนิค · ความรู้ด้านวัสดุ · กรณีศึกษา",
    "h2": "ความรู้นำไปสู่การตัดสินใจที่ดีกว่า",
    "sub": "โน้ตการใช้งาน ข้อมูลวัสดุ ข่าวอุตสาหกรรม และคำแนะนำจากผู้เชี่ยวชาญ",
    "body": "สำรวจคำแนะนำทางเทคนิค ข้อมูลเชิงลึกในการเลือกวัสดุ การทดสอบสมรรถนะ ข้อควรพิจารณาในการพิมพ์ และกรณีศึกษาจริง",
    "b1": "อ่านแอปพลิเคชันโน้ต", "b1u": "/application-notes/", "b2": "ดูกรณีศึกษา", "b2u": "/products/"},
   {"eyebrow": "การสนับสนุนการใช้งาน · การทดสอบ · การจัดหาที่ยืดหยุ่น",
    "h2": "บริการที่ตอบสนองไวขับเคลื่อนความสำเร็จ",
    "sub": "ทุกโครงการได้รับการสนับสนุนจากผู้เชี่ยวชาญที่รวดเร็วและเชื่อถือได้",
    "body": "ตั้งแต่การประเมินการใช้งานและตัวอย่าง ไปจนถึงการทดสอบในห้องปฏิบัติการ การแปรรูป การตรวจสอบคุณภาพ และการจัดส่งซ้ำ ETIA ช่วยให้ผู้ผลิตก้าวจากการเลือกสู่การผลิตอย่างมั่นใจ",
    "b1": "ปรึกษาผู้เชี่ยวชาญด้านวัสดุ", "b1u": "/contact/", "b2": "ปรึกษาผู้เชี่ยวชาญ", "b2u": "/contact/"},
  ]},
}

# Green corner labels + banner background images (fill BG with clean COS URLs later)
HOME_TABS = [("HOME", "首页"), ("PRODUCTS", "产品"), ("APPLICATIONS", "应用"), ("RESOURCES", "资讯"), ("SERVICE", "服务")]
# Page hero banners (COS). .hbanner::before lays the brand-blue gradient over the photo.
_BN = "https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com/BANNER/"
BANNER_HOME = _BN + "HOMEPAGE-BANNER"
BANNER_APPLICATION = _BN + "SOLUTION-BANNERNEW"
# Insights & Service heroes use a PER-LANGUAGE banner (client supplies one image
# per language). File convention: <stem>-<lang> with lang in en/zh/vi/th.
# Single banner per page, all languages (kept simple).
BANNER_INSIGHT = _BN + "insightbanner-en"
BANNER_SERVICE = _BN + "SERVICE-BANNER"
BANNER_PRODUCT = _BN + "PRODUCT-BANNER"
HOME_BG = [BANNER_HOME, "", "", "", ""]
# section_hero idx: 0=Products, 1=Applications, 2=Insights, 3=Service
SECTION_BG = {0: BANNER_PRODUCT, 1: BANNER_APPLICATION, 2: BANNER_INSIGHT, 3: BANNER_SERVICE}

def section_banner(idx, lang):
    """Hero background for a section page (single image, all languages)."""
    return SECTION_BG.get(idx, "")

def hero_cta(lang):
    # ONE unified banner contact button, identical everywhere (green · Talk to us).
    return '<a class="hcta" href="%s">%s</a>' % (
        Lx(lang, "/contact/"),
        esc(P(lang, "Talk to us", "联系我们", "Liên hệ với chúng tôi", "ติดต่อเรา")))

def _banner_html(linkfn, lang, bg, eyebrow, title, sub, body, b1, b1u, b2, b2u, bg_pos=""):
    # .hbanner defaults to background-position:center right; some banners (e.g. the
    # PCB banner, whose imagery sits along the bottom) need an override so the
    # meaningful part isn't cropped out.
    if bg:
        pos = (';background-position:%s' % bg_pos) if bg_pos else ""
        st = ' style="background-image:url(%s)%s"' % (esc(bg), pos)
    else:
        st = ""
    # Every part except the headline + slogan is optional; the contact button is
    # the single unified hero CTA on every banner (b1/b2 params are ignored).
    eyebrow_html = ('<div class="eyebrow">%s</div>' % esc(eyebrow)) if eyebrow else ""
    body_html = ('<p class="hbody">%s</p>' % esc(body)) if body else ""
    btns_html = '<div class="btns">%s</div>' % hero_cta(lang)
    return ('<section class="hbanner"%s><div class="wrap">'
            '%s<h1>%s</h1>'
            '<p class="hsub">%s</p>%s%s</div></section>') % (
        st, eyebrow_html, esc(title), esc(sub), body_html, btns_html)

def home_banner(lang, bg, eyebrow, title, sub, body, b1, b1u, b2, b2u, bg_pos=""):
    return _banner_html(home_hlink, lang, bg, eyebrow, title, sub, body, b1, b1u, b2, b2u, bg_pos)

_COS = "https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com/"
# Home hero (etiatech.com house style): trust pill + navy headline + green sub +
# green/outline CTAs, with a rotating "window" showing one real label per industry
# (photos pulled from the Industry pages). New materials are swapped by editing this list.
HOME_HERO_ITEMS = [
    ("/industries/pcb-electronics-labeling-solutions/", _COS + "INDUSTRY/PCB-APEX",
     ("PCB & Electronics", "PCB 电子", "PCB & Điện tử", "PCB และอิเล็กทรอนิกส์"),
     ("Reflow-, wash- and ESD-safe", "耐回流焊、清洗与防静电", "Chịu reflow, rửa & ESD", "ทนรีโฟลว์ ล้าง และ ESD")),
    ("/industries/automotive-labeling-solutions/", _COS + "INDUSTRY/AUTO-VINCODE",
     ("Automotive", "汽车", "Ô tô", "ยานยนต์"),
     ("VIN, engine, tire & battery", "VIN、发动机、轮胎与电池", "VIN, động cơ, lốp & pin", "VIN เครื่องยนต์ ยาง แบตเตอรี่")),
    ("/industries/medical-pharmaceutical-labeling-solutions/", _COS + "INDUSTRY/MEDICAL-BANNERNEW",
     ("Medical & Pharma", "医疗医药", "Y tế & Dược", "การแพทย์และยา"),
     ("Cryogenic, blood-bag & lab", "低温冻存、血袋与实验室", "Đông lạnh, túi máu & phòng lab", "อุณหภูมิต่ำ ถุงเลือด และแล็บ"),
     "center bottom"),  # show the bottle at the bottom; crop the top
    ("/industries/wire-cable-labeling-solutions/", _COS + "INDUSTRY/CABLE-XF603",
     ("Wire & Cable", "线缆", "Cáp & Dây", "สายเคเบิล"),
     ("Durable wire & harness marking", "耐久线缆与束线标识", "Đánh dấu dây & bó dây bền", "ทำเครื่องหมายสายไฟทนทาน")),
    ("/industries/steel-metal-ceramic-labeling-solutions/", _COS + "INDUSTRY/STEEL-HP900",
     ("Steel & Metal", "钢铁金属", "Thép & Kim loại", "เหล็กและโลหะ"),
     ("Direct-apply up to 1000 °C", "高温直贴，最高 1000 °C", "Dán trực tiếp tới 1000 °C", "ติดตรงสูงสุด 1000 °C")),
    ("/industries/outdoor-energy-labeling-solutions/", _COS + "INDUSTRY/OUTDOOR-WARNING%20OILDRUM",
     ("Outdoor & Energy", "户外能源", "Ngoài trời & Năng lượng", "กลางแจ้งและพลังงาน"),
     ("Weatherable for years outdoors", "户外耐候多年", "Chịu thời tiết nhiều năm", "ทนสภาพอากาศได้หลายปี")),
]

_HOME_HERO_CSS = """<style>
.hhero{background:linear-gradient(155deg,#eef3ff 0%,#edf6ec 100%);border-bottom:1px solid var(--line)}
.hhero-in{display:grid;grid-template-columns:1.15fr .85fr;gap:44px;align-items:center;padding:44px 0 48px}
.hhero-pill{display:inline-flex;align-items:center;gap:9px;background:#fff;border:1px solid var(--line);border-radius:999px;padding:9px 15px;box-shadow:0 6px 16px rgba(16,34,58,.08);font-weight:700;color:var(--blue-deep);font-size:13px;line-height:1.3}
.hhero-pill .ck{color:var(--green);display:grid;place-items:center;flex:none}
.hhero h1{font-family:var(--sans);font-weight:800;color:var(--blue-deep);letter-spacing:-.01em;font-size:clamp(30px,4.4vw,46px);line-height:1.1;margin:18px 0 8px;max-width:18ch;text-wrap:balance}
.hhero .hsub{font-family:var(--sans);font-weight:800;color:var(--green-d);font-size:clamp(17px,2.3vw,23px);margin:0 0 26px;text-wrap:balance}
.hhero-cta{display:flex;flex-wrap:wrap;gap:12px}
.hhbtn{font-family:var(--sans);font-weight:700;font-size:15px;border-radius:11px;padding:14px 24px;text-decoration:none;border:1.5px solid transparent;display:inline-block}
.hhbtn.pri{background:var(--green);color:#fff}
.hhbtn.sample{background:var(--blue);color:#fff}
.hhbtn.sample:hover{background:var(--blue-deep)}
.hhbtn.gho{background:#fff;border-color:var(--line);color:var(--blue-deep)}
.hhwin{position:relative;aspect-ratio:16/11;max-height:300px;margin-left:auto;width:100%;max-width:440px;border-radius:18px;overflow:hidden;background:linear-gradient(150deg,#e9eefc,#e8f4e3);border:1px solid var(--line);box-shadow:0 20px 48px rgba(16,34,58,.15)}
.hhslide{position:absolute;inset:0;text-decoration:none;color:inherit;opacity:0;transition:opacity .5s ease;pointer-events:none}
.hhslide.on{opacity:1;pointer-events:auto}
.hhslide img{width:100%;height:100%;object-fit:cover;background:#e8eefb;display:block}
.hhdots{position:absolute;bottom:12px;right:14px;display:flex;gap:6px;z-index:2}
.hhdots i{width:8px;height:8px;border-radius:50%;background:rgba(255,255,255,.8);box-shadow:0 0 0 1px rgba(16,34,58,.14);cursor:pointer}
.hhdots i.on{width:22px;border-radius:5px;background:var(--green)}
@media(max-width:860px){.hhero-in{grid-template-columns:1fr;gap:22px;padding:28px 0 32px}.hhwin{max-width:100%;margin:0;max-height:260px}}
</style>"""

_HOME_TRUST = [
    (("20+ Years","20+ 年","20+ Năm","20+ ปี"),
     ("Specialty Material Expertise","特种材料专业积累","Chuyên môn vật liệu đặc biệt","ความเชี่ยวชาญวัสดุเฉพาะทาง")),
    (("Multi-Brand Portfolio","多品牌产品组合","Danh mục đa thương hiệu","พอร์ตหลายแบรนด์"),
     ("Global Brands + ETIA Materials","国际品牌 + ETIA 自研材料","Thương hiệu toàn cầu + vật liệu ETIA","แบรนด์ระดับโลก + วัสดุ ETIA")),
    (("Asia-Based Supply","亚洲本地供应","Nguồn cung tại châu Á","อุปทานในเอเชีย"),
     ("Local Stock & Application Support","本地备货与应用支持","Kho địa phương & hỗ trợ ứng dụng","สต๊อกในพื้นที่และการสนับสนุนการใช้งาน")),
]
_HOME_TRUST_CSS = """<style>
.htrust{background:linear-gradient(100deg,var(--blue-deep),var(--blue))}
.htrust-in{display:grid;grid-template-columns:repeat(3,1fr);padding:16px 0}
.htrust .ht{padding:4px 26px;text-align:center;color:#fff;border-left:1px solid rgba(255,255,255,.2)}
.htrust .ht:first-child{border-left:none}
.htrust .ht b{display:block;font-family:var(--sans);font-weight:800;font-size:clamp(17px,1.9vw,21px);letter-spacing:-.01em;line-height:1.15}
.htrust .ht span{display:block;font-size:12.5px;color:#fff;opacity:.92;margin-top:3px;line-height:1.35}
@media(max-width:760px){.htrust-in{grid-template-columns:1fr;padding:4px 0}.htrust .ht{border-left:none;border-top:1px solid rgba(255,255,255,.16);padding:12px 20px}.htrust .ht:first-child{border-top:none}}
</style>"""

def home_trustbar(lang):
    j = JX[lang]
    cells = "".join('<div class="ht"><b>%s</b><span>%s</span></div>' % (esc(top[j]), esc(sub[j]))
                    for top, sub in _HOME_TRUST)
    return _HOME_TRUST_CSS + '<section class="htrust"><div class="wrap htrust-in">' + cells + '</div></section>'

def home_hero(lang):
    j = JX[lang]
    # Restore the original homepage slogan (do not change it): from HOME2 hero.
    hh = HOME2.get(lang, HOME2["en"])["hero"]
    pill_txt = hh["eyebrow"]
    head = hh["h1"]
    sub = hh["line"]
    c1 = P(lang,"Find a label material →","查找标签材料 →","Tìm vật liệu nhãn →","ค้นหาวัสดุฉลาก →")
    c3 = P(lang,"Request a Sample","索取样品","Yêu cầu mẫu","ขอตัวอย่าง")
    c2 = P(lang,"Talk to an Engineer","咨询工程师","Trao đổi với kỹ sư","ปรึกษาวิศวกร")
    slides, dots = "", ""
    for k,item in enumerate(HOME_HERO_ITEMS):
        url,img,nm,ln = item[0],item[1],item[2],item[3]
        pos = item[4] if len(item) > 4 else ""
        on = " on" if k==0 else ""
        style = (' style="object-position:%s"' % esc(pos)) if pos else ""
        # First slide: eager + high priority so the hero paints immediately (no blank flash).
        fp = ' fetchpriority="high"' if k==0 else ''
        slides += ('<a class="hhslide%s" href="%s" aria-label="%s"><img src="%s" alt="%s" loading="%s"%s%s onerror="this.style.display=\'none\'"></a>') % (
            on, home_hlink(lang,url), esc(nm[j]), esc(img), esc(nm[j]), "eager" if k==0 else "lazy", fp, style)
        dots += '<i class="%s"></i>' % ("on" if k==0 else "")
    check = '<span class="ck"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M20 6 9 17l-5-5"/></svg></span>'
    script = ("<script>(function(){var w=document.getElementById('hhwin');if(!w)return;"
              "var s=w.querySelectorAll('.hhslide'),d=w.querySelectorAll('.hhdots i'),i=0;"
              "function go(n){i=((n%s.length)+s.length)%s.length;"
              "s.forEach(function(x,k){x.classList.toggle('on',k===i);});"
              "d.forEach(function(x,k){x.classList.toggle('on',k===i);});}"
              "d.forEach(function(x,k){x.addEventListener('click',function(){go(k);});});"
              "if(!window.matchMedia||!matchMedia('(prefers-reduced-motion:reduce)').matches)"
              "setInterval(function(){go(i+1);},3500);})();</script>")
    # (The home page shell already emits a <head> preload for the first hero image.)
    return (_HOME_HERO_CSS +
        '<section class="hhero"><div class="wrap hhero-in">'
        '<div class="hhero-copy"><span class="hhero-pill">' + check + ' ' + esc(pill_txt) + '</span>'
        '<h1>' + esc(head) + '</h1><p class="hsub">' + esc(sub) + '</p>'
        '<div class="hhero-cta"><a class="hhbtn pri" href="' + home_hlink(lang,"/products/find/") + '">' + esc(c1) + '</a>'
        '<a class="hhbtn sample" href="' + home_hlink(lang,"/products/find/") + '">' + esc(c3) + '</a>'
        '<a class="hhbtn gho" href="' + home_hlink(lang,"/contact/") + '">' + esc(c2) + '</a></div></div>'
        '<div class="hhwin" id="hhwin">' + slides + '<div class="hhdots" id="hhdots">' + dots + '</div></div>'
        '</div></section>' + script)

# Solutions hero — same Home-page look (light gradient, navy headline, green sub,
# rotating window), keeping the existing Solutions slogan. The window cycles the
# operating-condition photos: high temperature / low temperature / chemical /
# sterilization (each links to its solution page).
_SOL_HERO_ITEMS = [
    ("/products/item/high-heat-identification/", _COS + "SOLUTION%20/HEAT-1200.jpg",
     ("1200 °C High Heat", "1200 °C 高温", "1200 °C nhiệt cao", "1200 °C ความร้อนสูง")),
    ("/products/item/cold-chain-cryogenic-labels/", _COS + "SOLUTION%20/COLD-196.jpg",
     ("−196 °C Cryogenic", "−196 °C 深冷", "−196 °C siêu lạnh", "−196 °C เยือกแข็ง")),
    ("/products/item/high-heat-identification/", _COS + "SOLUTION%20/HEAT-330.jpg",
     ("330 °C High Heat", "330 °C 高温", "330 °C nhiệt cao", "330 °C ความร้อนสูง")),
    ("/products/item/cold-chain-cryogenic-labels/", _COS + "SOLUTION%20/COLD-80C.jpg",
     ("−80 °C Deep Freeze", "−80 °C 超低温", "−80 °C đông sâu", "−80 °C แช่แข็งลึก")),
    ("/products/item/chemical-resistant-labels/", _COS + "SOLUTION%20/CHEMICAL-ACID.jpg",
     ("Acid & Solvent", "强酸溶剂", "Axit & dung môi", "กรดและตัวทำละลาย")),
    ("/products/item/chemical-resistant-labels/", _COS + "SOLUTION%20/CHEMICAL-OIL.jpg",
     ("Oil & Grease", "油污油脂", "Dầu & mỡ", "น้ำมันและจาระบี")),
    ("/products/item/sterilization-labels/", _COS + "SOLUTION%20/STERLIZATION-STEAM.png",
     ("Steam Sterilization", "高温蒸汽灭菌", "Tiệt trùng hơi nước", "ฆ่าเชื้อด้วยไอน้ำ")),
    ("/products/item/sterilization-labels/", _COS + "SOLUTION%20/STERLIZATION%20-%20GAMMA.jpg",
     ("Gamma Sterilization", "伽马射线灭菌", "Tiệt trùng Gamma", "ฆ่าเชื้อด้วยรังสีแกมมา")),
]

def solutions_hero(lang):
    j = JX[lang]
    s = HOME2.get(lang, HOME2["en"])["sections"][1]   # keep existing Solutions slogan
    pill_txt = s["eyebrow"]; head = s["h2"]; sub = s["sub"]
    c1 = P(lang, "Find a label material →", "查找标签材料 →", "Tìm vật liệu nhãn →", "ค้นหาวัสดุฉลาก →")
    c2 = P(lang, "Talk to us", "联系我们", "Liên hệ với chúng tôi", "ติดต่อเรา")
    slides, dots = "", ""
    for k, (url, img, nm) in enumerate(_SOL_HERO_ITEMS):
        on = " on" if k == 0 else ""
        # First two slides load eagerly (first also high-priority) so neither the
        # opening image nor the first rotation shows a blank while COS loads.
        fp = ' fetchpriority="high"' if k == 0 else ''
        ld = "eager" if k < 2 else "lazy"
        dc = ' decoding="async"'
        slides += ('<a class="hhslide%s" href="%s" aria-label="%s"><img src="%s" alt="%s" loading="%s"%s%s onerror="this.style.display=\'none\'"></a>') % (
            on, Lx(lang, url), esc(nm[j]), esc(img), esc(nm[j]), ld, dc, fp)
        dots += '<i class="%s"></i>' % ("on" if k == 0 else "")
    check = '<span class="ck"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M20 6 9 17l-5-5"/></svg></span>'
    script = ("<script>(function(){var w=document.getElementById('hhwin');if(!w)return;"
              "var s=w.querySelectorAll('.hhslide'),d=w.querySelectorAll('.hhdots i'),i=0;"
              "function go(n){i=((n%s.length)+s.length)%s.length;"
              "s.forEach(function(x,k){x.classList.toggle('on',k===i);});"
              "d.forEach(function(x,k){x.classList.toggle('on',k===i);});}"
              "d.forEach(function(x,k){x.addEventListener('click',function(){go(k);});});"
              "if(!window.matchMedia||!matchMedia('(prefers-reduced-motion:reduce)').matches)"
              "setInterval(function(){go(i+1);},3800);})();</script>")
    preload = ('<link rel="preload" as="image" href="%s" fetchpriority="high">'
               '<link rel="preload" as="image" href="%s">') % (
        esc(_SOL_HERO_ITEMS[0][1]), esc(_SOL_HERO_ITEMS[1][1]))
    return (preload + _HOME_HERO_CSS +
        '<section class="hhero"><div class="wrap hhero-in">'
        '<div class="hhero-copy"><span class="hhero-pill">' + check + ' ' + esc(pill_txt) + '</span>'
        '<h1>' + esc(head) + '</h1><p class="hsub">' + esc(sub) + '</p>'
        '<div class="hhero-cta"><a class="hhbtn pri" href="' + Lx(lang, "/products/find/") + '">' + esc(c1) + '</a>'
        '<a class="hhbtn gho" href="' + Lx(lang, "/contact/") + '">' + esc(c2) + '</a></div></div>'
        '<div class="hhwin" id="hhwin">' + slides + '<div class="hhdots" id="hhdots">' + dots + '</div></div>'
        '</div></section>' + script)

# Page HERO banner for inner pages (uses L() for en/zh links). Same look as the home banner.
def page_hero(lang, eyebrow, title, sub, body, b1, b1u, b2, b2u, bg=""):
    return _banner_html(L, lang, bg, eyebrow, title, sub, body, b1, b1u, b2, b2u)

# Per-page hero from a HOME2 section. idx: 0=Products,1=Applications,2=Insights,3=Service.
def section_hero(lang, idx, bg=""):
    s = HOME2.get(lang, HOME2["en"])["sections"][idx]
    bg = bg or SECTION_BG.get(idx, "")
    return page_hero(lang, s["eyebrow"], s["h2"], s["sub"], s["body"], s["b1"], s["b1u"], s["b2"], s["b2u"], bg)

# ---- Animated page heroes (same .hbanner look, with a moving background layer) ----
# Two flavours: a single "Ken Burns" slow-zoom visual (Insights / Service), and a
# rotating "working-conditions" carousel that cycles through harsh-environment
# photos with a small changing caption (Solutions). Both respect reduced-motion.
_HERO_FX_CSS = """<style>
.hbx{position:relative;overflow:hidden;background:var(--blue-deep);border-bottom:2px solid #fff;display:flex;align-items:center;min-height:320px}
.hbx .hbx-bg{position:absolute;inset:0;background-size:cover;background-position:center right;z-index:0;will-change:transform,opacity}
.hbx .hbx-bg.kb{animation:hbxzoom 22s ease-in-out infinite alternate}
@keyframes hbxzoom{from{transform:scale(1.001)}to{transform:scale(1.10)}}
.hbx.car .hbx-bg{opacity:0;transition:opacity 1.1s ease}
.hbx.car .hbx-bg.on{opacity:1;animation:hbxzoom 9s ease-in-out infinite alternate}
.hbx::before{content:"";position:absolute;inset:0;z-index:1;background:linear-gradient(90deg,rgba(20,60,150,.90) 16%,rgba(20,60,150,.50) 54%,rgba(20,60,150,.08))}
.hbx .wrap{position:relative;z-index:2;width:100%;padding:60px 24px}
.hbx .eyebrow{color:#8fe063;margin-bottom:6px}
.hbx h1{color:#fff;font-family:var(--sans);font-weight:800;font-size:40px;line-height:1.12;letter-spacing:-.01em;text-align:left;margin:2px 0 10px;max-width:18em}
.hbx .hsub{font-size:18px;font-weight:700;color:#eef3ff;margin-bottom:16px;max-width:40em}
.hbx .btns{display:flex;gap:12px;flex-wrap:wrap}
.hbx .hbx-env{position:absolute;right:18px;bottom:16px;z-index:3;display:flex;gap:8px;align-items:center;flex-wrap:wrap;justify-content:flex-end;max-width:60%}
.hbx .hbx-tag{position:absolute;right:0;bottom:0;white-space:nowrap;background:rgba(9,26,66,.55);border:1px solid rgba(255,255,255,.28);color:#eaf1ff;font-size:12.5px;font-weight:700;padding:5px 12px;border-radius:999px;opacity:0;transition:opacity .5s ease}
.hbx .hbx-tag.on{opacity:1;position:relative}
.hbx .hbx-dots{position:absolute;left:24px;bottom:16px;z-index:3;display:flex;gap:6px}
.hbx .hbx-dots i{width:8px;height:8px;border-radius:50%;background:rgba(255,255,255,.55);cursor:pointer}
.hbx .hbx-dots i.on{width:22px;border-radius:5px;background:var(--green)}
@media(max-width:820px){.hbx{min-height:250px}.hbx h1{font-size:27px}.hbx .hsub{font-size:15.5px}.hbx .wrap{padding:34px 24px}.hbx .hbx-tag{font-size:11px}}
@media(prefers-reduced-motion:reduce){.hbx .hbx-bg{animation:none!important}}
</style>"""

def hero_single_anim(lang, bg, eyebrow, title, sub):
    """Single main visual with a subtle Ken Burns slow-zoom (Insights / Service)."""
    bgdiv = ('<div class="hbx-bg kb" style="background-image:url(%s)"></div>' % esc(bg)) if bg else ""
    eye = ('<div class="eyebrow">%s</div>' % esc(eyebrow)) if eyebrow else ""
    html = ('<section class="hbx">%s<div class="wrap">%s<h1>%s</h1>'
            '<p class="hsub">%s</p><div class="btns">%s</div></div></section>') % (
        bgdiv, eye, esc(title), esc(sub), hero_cta(lang))
    preload = ('<link rel="preload" as="image" href="%s" fetchpriority="high">' % esc(bg)) if bg else ""
    return preload + _HERO_FX_CSS + html

def hero_carousel(lang, slides, eyebrow, title, sub):
    """Rotating 'working-conditions' banner. slides = [(img_url, {4-lang caption})].
    Headline/slogan stay fixed; only the background photo + caption rotate."""
    j = JX[lang]
    bgs = tags = dots = ""
    for k, (img, env) in enumerate(slides):
        on = " on" if k == 0 else ""
        cap = env[j] if isinstance(env, (list, tuple)) else (env.get(lang) or env.get("en"))
        bgs += '<div class="hbx-bg%s" style="background-image:url(%s)"></div>' % (on, esc(img))
        tags += '<span class="hbx-tag%s">%s</span>' % (on, esc(cap))
        dots += '<i class="%s"></i>' % ("on" if k == 0 else "")
    eye = ('<div class="eyebrow">%s</div>' % esc(eyebrow)) if eyebrow else ""
    script = ("<script>(function(){var s=document.currentScript.previousElementSibling;"
              "var bg=s.querySelectorAll('.hbx-bg'),tg=s.querySelectorAll('.hbx-tag'),"
              "dt=s.querySelectorAll('.hbx-dots i'),i=0;"
              "function go(n){i=(n+bg.length)%bg.length;"
              "bg.forEach(function(x,k){x.classList.toggle('on',k===i);});"
              "tg.forEach(function(x,k){x.classList.toggle('on',k===i);});"
              "dt.forEach(function(x,k){x.classList.toggle('on',k===i);});}"
              "dt.forEach(function(x,k){x.addEventListener('click',function(){go(k);});});"
              "if(!window.matchMedia||!matchMedia('(prefers-reduced-motion:reduce)').matches)"
              "setInterval(function(){go(i+1);},4200);})();</script>")
    html = ('<section class="hbx car">%s<div class="wrap">%s<h1>%s</h1>'
            '<p class="hsub">%s</p><div class="btns">%s</div></div>'
            '<div class="hbx-env">%s</div><div class="hbx-dots">%s</div></section>') % (
        bgs, eye, esc(title), esc(sub), hero_cta(lang), tags, dots)
    preload = ('<link rel="preload" as="image" href="%s" fetchpriority="high">' % esc(slides[0][0])) if slides else ""
    return preload + _HERO_FX_CSS + html + script

# Solutions "operating-conditions" carousel — the four solution categories this page
# is organised around: High Temperature / Low Temperature / Chemical / Sterilization
# (reuses each solution page's own environment photo, guaranteed to resolve on COS).
_SOL_SLIDES = [
    (_COS + "APPLICATION%20/enviroment-heat",
     ("High Temperature", "高温", "Nhiệt độ cao", "อุณหภูมิสูง")),
    (_COS + "APPLICATION%20/enviroment-cold",
     ("Low Temperature", "低温", "Nhiệt độ thấp", "อุณหภูมิต่ำ")),
    (_COS + "APPLICATION%20/enviroment-chemical",
     ("Chemical Resistant", "化学", "Kháng hóa chất", "สารเคมี")),
    (_COS + "APPLICATION%20/enviroment-sterlization",
     ("Sterilization", "消毒灭菌", "Tiệt trùng", "การฆ่าเชื้อ")),
]

def build_home(lang):
    path="/"
    T=HOME_I18N[lang]
    G=HOME2.get(lang, HOME2["en"])
    # Why ETIA pillars — icon + "We…" heading + up to two short lines
    why_html="".join('<div class="why"><div class="ic">%s</div><div class="txt"><b>%s</b><p class="wexp">%s</p></div></div>'%(
        WHY_ICONS[k%len(WHY_ICONS)],esc(head),esc(text)) for k,(head,text) in enumerate(T["why"]))
    why_close=('<p class="whyclose">%s</p>'%esc(T["why_close"])) if T.get("why_close") else ""
    # Solutions by Industry — image-card carousel (photo on top, copy below), arrows scroll the row
    cards=""
    for k,f in enumerate(T["focus"]):
        # photo if supplied, else a clean gradient header with the industry icon
        top=('<img src="%s" alt="%s" loading="lazy" onerror="this.remove()">'%(esc(f["img"]),esc(f["name"]))) if f.get("img") \
            else ('<span class="aicon">%s</span>'%INDUSTRY_ICONS[k%len(INDUSTRY_ICONS)])
        cards+=('<a class="acard" href="%s"><div class="acard-img g%d">%s</div>'
                '<div class="acard-body"><h3 class="indname">%s</h3><p>%s</p>'
                '<div class="acard-go">%s →</div></div></a>')%(
            home_hlink(lang,FOCUS_URLS[k]), k%6, top,
            esc(f["name"]), esc(f["desc"]), esc(T["explore"]))
    app_grid=('<div class="indcar-wrap"><button class="acar-nav prev" onclick="etaIndSlide(-1)" aria-label="Previous">&lsaquo;</button>'
              '<div class="indcar" id="indcar">%s</div>'
              '<button class="acar-nav next" onclick="etaIndSlide(1)" aria-label="Next">&rsaquo;</button></div>')%cards
    # Most Popular Products — same card pattern (image top), application name as title, model small.
    # Cards link to the product landing page when one exists (per-index slug), else to contact.
    PROD_ICON=[1,2,0,3,2,4]
    POP_PROD_SLUGS=["hp-901","e-4812","apex","e-2813","e-2712"]  # "" -> no landing yet (falls back to contact)
    pcards=""
    for k,pr in enumerate(T.get("products",[])):
        gi=PROD_ICON[k%len(PROD_ICON)]
        slug=pr.get("slug") or (POP_PROD_SLUGS[k] if k<len(POP_PROD_SLUGS) else "")
        href=home_hlink(lang,"/products/item/%s/"%slug) if slug else home_hlink(lang,"/contact/")
        pimg=('<img src="%s" alt="%s" loading="lazy" onerror="this.remove()">'%(esc(pr["img"]),esc(pr["name"]))) if pr.get("img") else ""
        pcode_html=('<div class="pcode">%s</div>'%esc(pr["code"])) if pr.get("code") else ""  # skip empty code pill (solution cards)
        pcards+=('<a class="acard pcard" href="%s"><div class="acard-img g%d">%s<span class="aicon">%s</span></div>'
                 '<div class="acard-body"><h3>%s</h3><div class="pmodel">%s</div>%s'
                 '<div class="acard-go">%s →</div></div></a>')%(
            href, gi, pimg, INDUSTRY_ICONS[gi%len(INDUSTRY_ICONS)],
            esc(pr["name"]), esc(pr["model"]), pcode_html,
            esc(T.get("prod_cta","Talk to a Specialist") if not slug else P(lang,"View Product","查看产品","Xem sản phẩm","ดูสินค้า")))
    prod_viewall={"en":"View All Products","zh":"查看全部产品","vi":"Xem tất cả sản phẩm","th":"ดูสินค้าทั้งหมด"}.get(lang,"View All Products")
    prod_section=('<section class="blk" style="background:var(--bg)"><div class="wrap">'
                  '<div class="eyebrow">%s</div><h2>%s</h2><div class="sub">%s</div>'
                  '<div class="indcar-wrap"><button class="acar-nav prev" onclick="etaProdSlide(-1)" aria-label="Previous">&lsaquo;</button>'
                  '<div class="prodcar" id="prodcar">%s</div>'
                  '<button class="acar-nav next" onclick="etaProdSlide(1)" aria-label="Next">&rsaquo;</button></div>'
                  '</div></section>')%(
        esc(T.get("prod_eyebrow","")),esc(T.get("prod_title","")),esc(T.get("prod_sub","")),pcards) if pcards else ""
    # Free Sample — lead capture (email / phone / address) -> mailto
    fs_section=('<section class="blk freesample"><div class="wrap"><div class="fsbox">'
                '<div class="fsL"><div class="eyebrow" style="color:#8fe063">%s</div>'
                '<h2 style="color:#fff">%s</h2><p class="fssub">%s</p><div class="fsnote">%s</div></div>'
                '<form class="fsform" onsubmit="return etaSample(event)">'
                '<input id="fs-email" type="email" required placeholder="%s">'
                '<input id="fs-phone" type="tel" placeholder="%s">'
                '<input id="fs-addr" type="text" placeholder="%s">'
                '<button class="btn pri" type="submit">%s</button></form>'
                '</div></div></section>')%(
        esc(T.get("fs_eyebrow","FREE SAMPLE")),esc(T.get("fs_title","Request Free Samples")),
        esc(T.get("fs_sub","")),esc(T.get("fs_note","")),
        esc(T.get("fs_email","Email")),esc(T.get("fs_phone","Phone")),
        esc(T.get("fs_addr","Mailing address")),esc(T.get("fs_btn","Request Free Sample")))
    final_cta='<div class="wrap">%s</div>'%cta2(lang,"home",home_hlink)
    # Service Commitment — same image-top card carousel as Industries/Products (small images, one row, mobile-friendly)
    sc_items="".join('<div class="acard sccard"><div class="acard-img">%s</div>'
                     '<div class="acard-body"><h3 class="indname">%s</h3><p>%s</p></div></div>'%(
        ('<img src="%s" alt="" loading="lazy" onerror="this.remove()">'%esc(it["img"]) if it.get("img") else ''),
        esc(it["title"]),esc(it["desc"])) for it in T.get("svc",[]))
    sc_section=('<section class="blk"><div class="wrap"><div class="eyebrow">%s</div><h2>%s</h2>'
                '<div class="sc4">%s</div></div></section>')%(
        esc(T.get("sc_eyebrow","SERVICE COMMITMENT")),esc(T.get("sc_title","Our Service Commitment")),sc_items)
    hero_banner=home_hero(lang)
    why_section=('<section class="blk" style="background:var(--bg)"><div class="wrap">'
                 '<div class="eyebrow">%s</div><h2>%s</h2><div class="sub">%s</div>'
                 '<div class="whygrid">%s</div>%s</div></section>')%(
        esc(T["why_eyebrow"]),esc(T["why_head"]),esc(T["why_intro"]),why_html,why_close)
    app_section=('<section class="blk" id="applications" style="background:var(--tint-blue)"><div class="wrap">'
                 '<div class="eyebrow">%s</div><h2>%s</h2><div class="sub">%s</div>%s</div></section>')%(
        esc(T["appc_eyebrow"]),esc(T["appc_title"]),esc(T["appc_sub"]),app_grid)
    # trust strip removed from the home page: it duplicated the Service Commitment
    # section below (same four items). Keep the dedicated section only.
    body=hero_banner+home_trustbar(lang)+why_section+app_section+prod_section+sc_section+final_cta
    canonical=SITE+HL_PREFIX[lang]+path
    schema_js='<script type="application/ld+json">%s</script>'%json.dumps(ORG_JSONLD,ensure_ascii=False)
    hero_preload=('<link rel="preload" as="image" href="'+HOME_HERO_ITEMS[0][1]+'" fetchpriority="high">') if HOME_HERO_ITEMS else ""
    doc="""<!doctype html><html lang="%s"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<link rel="icon" type="image/png" href="/favicon.png"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com" crossorigin><link rel="dns-prefetch" href="https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com">
<title>%s</title><meta name="description" content="%s">
<link rel="canonical" href="%s">%s%s
<meta property="og:title" content="%s"><meta property="og:type" content="website"><meta property="og:site_name" content="ETIA Label">
<style>%s</style>%s</head><body>
<div class="topstrip"></div>
<header><div class="wrap"><a class="logo" href="%s"><img src="https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com/IMAGO/LOGO/ETIA%%20LOGO.jpg" alt="ETIA Label"></a>%s</div></header>
%s
%s
<script>
function etaOpen(n){clearTimeout(n._t);n.classList.add('open');}
function etaMenu(b){var n=b.closest('nav');if(n)n.classList.toggle('open');}
function etaMob(b){var g=b.closest('.ndmg');if(g)g.classList.toggle('open');}
function etaProd(b,e){if(window.innerWidth<=900){if(e&&e.preventDefault)e.preventDefault();b.closest('.nd').classList.toggle('mopen');return false;}return true;}
function etaClose(n){n._t=setTimeout(function(){n.classList.remove('open');},180);}
function etaSub(b,s){var m=b?b.closest('.ndm'):(document.querySelector('.nd.open .ndm')||document.querySelector('.ndm'));if(!m)return;
if(b&&b.classList&&b.classList.contains('axitem'))m.querySelectorAll('.axitem').forEach(function(x){x.classList.toggle('on',x===b);});
m.querySelectorAll('.subgroup').forEach(function(p){p.style.display=(p.getAttribute('data-sub')===s)?'flex':'none';});}
function etaAx(b,a){var m=b.closest('.ndm');
m.querySelectorAll('.axbtn').forEach(function(x){x.classList.toggle('on',x===b);});
m.querySelectorAll('.midgroup').forEach(function(p){p.style.display=(p.getAttribute('data-mid')===a)?'flex':'none';});
var mg=m.querySelector('.midgroup[data-mid="'+a+'"]');var first=mg?mg.querySelector('.axitem.haskid'):null;
etaSub(first,first?first.getAttribute('data-sub'):'');}
function etaSlide(d){var c=document.getElementById('acar');if(c)c.scrollBy({left:d*c.clientWidth,behavior:'smooth'});}
function etaIndSlide(d){var c=document.getElementById('indcar');if(c)c.scrollBy({left:d*Math.min(628,Math.max(300,c.clientWidth*0.85)),behavior:'smooth'});}
function etaProdSlide(d){var c=document.getElementById('prodcar');if(c)c.scrollBy({left:d*Math.min(628,Math.max(300,c.clientWidth*0.85)),behavior:'smooth'});}
function etaSvcSlide(d){var c=document.getElementById('svccar');if(c)c.scrollBy({left:d*Math.min(628,Math.max(300,c.clientWidth*0.85)),behavior:'smooth'});}
function etaSample(e){e.preventDefault();var g=function(i){var el=document.getElementById(i);return el?el.value:'';};
var b='Email: '+g('fs-email')+'%%0D%%0APhone: '+g('fs-phone')+'%%0D%%0AAddress: '+g('fs-addr')+'%%0D%%0A%%0D%%0APlease send free samples.';
window.location.href='mailto:etialabel@etia-tech.com?subject=Free%%20Sample%%20Request&body='+b;return false;}</script>
</body></html>""" % (lang,esc(T["meta_title"]),esc(T["meta_desc"]),canonical,home_hreflang(path),hero_preload,esc(T["meta_title"]),CSS,schema_js,
        ("/" if lang=="en" else HL_PREFIX[lang]+"/"),home_nav(lang),body,home_footer(lang))
    outdir=os.path.join(ROOT,HL_PREFIX[lang].strip("/")) if HL_PREFIX[lang] else ROOT
    os.makedirs(outdir,exist_ok=True)
    open(os.path.join(outdir,"index.html"),"w").write(doc)
    if lang=="en": track(path,"core")

# ---------------------------------------------------------------- sitemaps + redirects
LANG_ORDER = ["en", "zh", "vi", "th"]
DIR_LANG = {"cn": "zh", "vn": "vi", "th": "th"}  # locale dir -> lang code
# Product/item slugs that are environment Solution pages (own sitemap group).
ENV_SOLUTION_SLUGS = ("high-heat-identification", "cold-chain-cryogenic-labels",
                      "chemical-resistant-labels", "sterilization-labels")
# Legacy duplicate paths that 301 to their /products/item/ canonical — kept out
# of the sitemap so crawlers only see one URL per product.
SITEMAP_EXCLUDE = {"/products/apex-series/", "/products/e-2712/"}

def _sitemap_group(canon):
    if canon in SITEMAP_EXCLUDE:
        return None
    if canon == "/":
        return "core"
    if canon.startswith("/insights/"):
        return "insights"
    if canon.startswith("/application-notes/"):
        return "notes"
    if canon.startswith("/industries/"):
        return "industries"
    if canon.startswith("/products/"):
        if canon == "/products/":
            return "core"  # the Products landing hub
        if any(canon == "/products/item/%s/" % s for s in ENV_SOLUTION_SLUGS):
            return "environment-solutions"
        return "products"
    return "core"  # home, about, service, applications, contact, legal, etc.

def build_sitemaps():
    """Filesystem-based: list exactly the pages that exist, in every locale they
    exist, split into one sitemap per section, each locale URL listed in full with
    hreflang alternates. Empty sections are skipped; a stale sitemap-*.xml is removed."""
    skip_dirs = {"_build", "_docs", ".git", "node_modules", "scratchpad"}
    pages = {}  # canonical path -> set(lang)
    for r, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith(".")]
        if "index.html" not in files:
            continue
        rel = os.path.relpath(r, ROOT).replace(os.sep, "/")
        if rel == ".":
            canon, lang = "/", "en"
        else:
            parts = rel.split("/")
            if parts[0] in DIR_LANG:
                lang = DIR_LANG[parts[0]]
                rest = "/".join(parts[1:])
                canon = "/" + (rest + "/" if rest else "")
            else:
                lang, canon = "en", "/" + rel + "/"
        pages.setdefault(canon, set()).add(lang)

    groups = {}
    for canon, langs in pages.items():
        g = _sitemap_group(canon)
        if not g:
            continue
        ordered = [l for l in LANG_ORDER if l in langs]
        groups.setdefault(g, []).append((canon, ordered))

    order = [("core", "sitemap-core.xml"), ("products", "sitemap-products.xml"),
             ("industries", "sitemap-industries.xml"),
             ("environment-solutions", "sitemap-environment-solutions.xml"),
             ("notes", "sitemap-application-notes.xml"), ("insights", "sitemap-insights.xml")]
    written = []
    for g, fn in order:
        items = sorted(groups.get(g, []))
        if not items:
            continue
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        for canon, langs in items:
            for lg in langs:
                xml += '  <url><loc>%s%s%s</loc>' % (SITE, PREFIX[lg], canon)
                for al in langs:
                    xml += '<xhtml:link rel="alternate" hreflang="%s" href="%s%s%s"/>' % (HREFLANG[al], SITE, PREFIX[al], canon)
                xml += '<xhtml:link rel="alternate" hreflang="x-default" href="%s%s"/>' % (SITE, canon)
                xml += '</url>\n'
        xml += '</urlset>\n'
        open(os.path.join(ROOT, fn), "w").write(xml)
        written.append(fn)

    idx = '<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for fn in written:
        idx += '  <sitemap><loc>%s/%s</loc></sitemap>\n' % (SITE, fn)
    idx += '</sitemapindex>\n'
    open(os.path.join(ROOT, "sitemap-index.xml"), "w").write(idx)
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(idx)  # alias so /sitemap.xml also resolves
    open(os.path.join(ROOT, "robots.txt"), "w").write("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap-index.xml\n" % SITE)
    # remove stale section sitemaps that are no longer generated (e.g. old empty ones)
    keep = set(written) | {"sitemap-index.xml"}
    for f in os.listdir(ROOT):
        if f.startswith("sitemap-") and f.endswith(".xml") and f not in keep:
            os.remove(os.path.join(ROOT, f))

def write_redirects():
    # 301 migration redirects (per brief §13) + clean-url config, in vercel.json
    cfg={"cleanUrls":True,"trailingSlash":True,"redirects":[
      # /products/ is now a real landing page (build_products_landing). Only the
      # /industries/ hub paths still redirect to Home (no industries hub page);
      # exact paths only, so individual /industries/<slug>/ pages are unaffected.
      {"source":"/industries","destination":"/","permanent":False},
      {"source":"/industries/","destination":"/","permanent":False},
      {"source":"/cn/industries","destination":"/cn/","permanent":False},
      {"source":"/cn/industries/","destination":"/cn/","permanent":False},
      {"source":"/vn/industries","destination":"/vn/","permanent":False},
      {"source":"/vn/industries/","destination":"/vn/","permanent":False},
      {"source":"/th/industries","destination":"/th/","permanent":False},
      {"source":"/th/industries/","destination":"/th/","permanent":False},
      {"source":"/cases","destination":"/","permanent":True},
      {"source":"/cases/:path*","destination":"/","permanent":True},
      {"source":"/products/direct-label","destination":"/products/direct-hot-application-labels/","permanent":True},
      {"source":"/products/management-label","destination":"/products/heat-treatment-labels/","permanent":True},
      {"source":"/products/management-tag","destination":"/products/heat-treatment-tags/","permanent":True},
      {"source":"/products/hp-700t","destination":"/products/hp-900/","permanent":True},
      {"source":"/products/heatproof/hp-t42-hp-cbr-tag","destination":"/products/heatproof/hp-l90/","permanent":True},
      {"source":"/industries/esd-safe-labels","destination":"/industries/pcb-electronics-labeling-solutions/","permanent":True},
      {"source":"/application-notes/green-tire-wip-tracking","destination":"/application-notes/tire-bead-labels/","permanent":True},
      {"source":"/industries/automotive-label-materials","destination":"/industries/automotive-labeling-solutions/","permanent":True},
      {"source":"/industries/circuit-board-pcb","destination":"/industries/pcb-electronics-labeling-solutions/","permanent":True},
      {"source":"/industries/cable-labeling-solutions","destination":"/industries/wire-cable-labeling-solutions/","permanent":True},
      {"source":"/industries/outdoor-labeling-solutions","destination":"/industries/outdoor-energy-labeling-solutions/","permanent":True},
      {"source":"/industries/medical-labeling-solutions","destination":"/industries/medical-pharmaceutical-labeling-solutions/","permanent":True},
      {"source":"/industries/steel-labeling-solutions","destination":"/industries/steel-metal-ceramic-labeling-solutions/","permanent":True},
      # Legacy product pages -> canonical /products/item/ pages (avoid duplicate content)
      {"source":"/products/apex-series","destination":"/products/item/apex/","permanent":True},
      {"source":"/cn/products/apex-series","destination":"/cn/products/item/apex/","permanent":True},
      {"source":"/products/e-2712","destination":"/products/item/e-2712/","permanent":True},
      {"source":"/cn/products/e-2712","destination":"/cn/products/item/e-2712/","permanent":True},
    ]}
    # Always revalidate HTML so visitors get the latest page (the CSS is inlined in
    # each page, so a stale HTML also means stale styling). Content is regenerated
    # on every deploy, so caching HTML causes "changes not showing" reports.
    cfg["headers"]=[
      {"source":"/(.*)","headers":[
        {"key":"Cache-Control","value":"public, max-age=0, must-revalidate"}]},
    ]
    open(os.path.join(ROOT,"vercel.json"),"w").write(json.dumps(cfg,indent=2)+"\n")

# ---------------------------------------------------------------- run
def clean():
    # preserve source (generators/data/docs); regenerate the section output dirs.
    # NOTE: does NOT delete automotive-owned dirs (label-materials, brands are handled
    # by the orchestrator ordering); heatproof runs first, automotive layers on top.
    for d in ["products","industries","applications","application-notes","technical-resources","about","contact","zh","cn",
              "materials","brands","insights","news","service","support","company","privacy","cookies","terms",
              "label-materials","popular","featured-solutions","vi","vn","th"]:
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
    # offices: (name P-args, sub-line P-args, contact string)
    offices=[
      (("Shanghai","上海","Thượng Hải","เซี่ยงไฮ้"),("China","中国","Trung Quốc","จีน"),
       "+86 139 1833 9249 · 400 990 8448 · +86-21-6432-7144"),
      (("Hong Kong","香港","Hồng Kông","ฮ่องกง"),
       ("ETIA-TECH (ASIA) Co., Limited",)*4,"etialabel@etia-tech.com"),
      (("Bangkok","曼谷","Bangkok","กรุงเทพฯ"),("Thailand","泰国","Thái Lan","ไทย"),
       "+66 811 746 947"),
      (("Bac Ninh","北宁","Bắc Ninh","บั๊กนิญ"),("Vietnam","越南","Việt Nam","เวียดนาม"),
       "+84 961 530 153"),
    ]
    cards="".join('<div class="card"><h3>%s</h3><p>%s</p><div class="rows"><b>%s</b></div></div>'%(
        esc(P(lang,*nm)), esc(P(lang,*sub)), esc(c)) for nm,sub,c in offices)
    ask=P(lang,
        "Tell us: the surface, temperature (at application and later peak), chemical exposure, print method and label size — we'll recommend the material and arrange samples.",
        "告诉我们:粘贴表面、温度(贴标时与后续最高)、化学暴露、打印方式与标签尺寸,我们推荐材料并安排样品。",
        "Cho chúng tôi biết: bề mặt, nhiệt độ (khi dán và đỉnh sau đó), tiếp xúc hóa chất, phương pháp in và kích thước nhãn — chúng tôi sẽ đề xuất vật liệu và sắp xếp mẫu.",
        "บอกเรา: พื้นผิว อุณหภูมิ (ตอนติดและจุดสูงสุดภายหลัง) การสัมผัสสารเคมี วิธีพิมพ์ และขนาดฉลาก — เราจะแนะนำวัสดุและจัดเตรียมตัวอย่าง")
    def lb(en,zh_,vi="",th=""): return P(lang,en,zh_,vi or en,th or en)
    form_css=('<style>.cform{max-width:760px}'
      '.cfg{display:grid;grid-template-columns:1fr 1fr;gap:14px 16px;margin:12px 0 18px}'
      '.cform label{display:flex;flex-direction:column;font-size:13px;font-weight:700;color:var(--blue-deep);gap:6px}'
      '.cform label.full{grid-column:1/-1}'
      '.cform input,.cform textarea{font:inherit;font-weight:400;padding:11px 12px;border:1px solid var(--line);border-radius:9px;background:#fff;color:var(--ink)}'
      '.cform input:focus,.cform textarea:focus{outline:2px solid var(--blue);border-color:var(--blue)}'
      '@media(max-width:560px){.cfg{grid-template-columns:1fr}}</style>')
    form=(form_css+'<form class="cform" onsubmit="return etaContact(event)"><div class="cfg">'
      '<label>'+esc(lb("Name *","姓名 *","Tên *","ชื่อ *"))+'<input name="name" required></label>'
      '<label>'+esc(lb("Company","公司","Công ty","บริษัท"))+'<input name="company"></label>'
      '<label>'+esc(lb("Email *","邮箱 *","Email *","อีเมล *"))+'<input type="email" name="email" required></label>'
      '<label>'+esc(lb("Phone *","电话 *","Điện thoại *","โทรศัพท์ *"))+'<input name="phone" required></label>'
      '<label class="full">'+esc(lb("Product / Interest","产品 / 需求","Sản phẩm / Nhu cầu","สินค้า / ความสนใจ"))+'<input name="product" id="cf_product"></label>'
      '<label class="full">'+esc(lb("Your application — surface, temperature, chemistry, print method, label size","您的应用 —— 表面、温度、化学环境、打印方式、标签尺寸","Ứng dụng của bạn — bề mặt, nhiệt độ, hóa chất, phương pháp in, kích thước nhãn","การใช้งานของคุณ — พื้นผิว อุณหภูมิ สารเคมี วิธีพิมพ์ ขนาดฉลาก"))+'<textarea name="message" rows="4"></textarea></label>'
      '</div><button class="btn pri" type="submit">'+esc(lb("Send to ETIA","发送给 ETIA","Gửi cho ETIA","ส่งถึง ETIA"))+'</button></form>')
    form_js=('<script>(function(){var p=new URLSearchParams(location.search),pr=p.get("product"),ty=p.get("type"),f=document.getElementById("cf_product");if(f&&pr){f.value=pr+(ty?" ("+ty+")":"");}})();'
      'function etaContact(e){e.preventDefault();var f=e.target,g=function(n){var el=f.querySelector("[name="+n+"]");return el?el.value.trim():"";};'
      'var nm=g("name"),em=g("email"),ph=g("phone");'
      'if(!nm||!em||!ph){alert("'+lb("Please fill in name, email and phone.","请填写姓名、邮箱和电话。","Vui lòng điền tên, email và điện thoại.","กรุณากรอกชื่อ อีเมล และโทรศัพท์")+'");return false;}'
      'var s="ETIA enquiry"+(g("product")?" - "+g("product"):"");'
      'var b="Name: "+nm+"\\nCompany: "+g("company")+"\\nEmail: "+em+"\\nPhone: "+ph+"\\nProduct: "+g("product")+"\\n\\n"+g("message");'
      'window.location.href="mailto:etialabel@etia-tech.com?subject="+encodeURIComponent(s)+"&body="+encodeURIComponent(b);return false;}</script>')
    body=('<section class="blk"><div class="wrap"><h2>%s</h2><div class="sub">%s</div>%s%s'
          '<p class="muted" style="font-size:13px;margin-top:10px">%s <a href="mailto:etialabel@etia-tech.com">etialabel@etia-tech.com</a></p></div></section>'
          '<section class="blk" style="background:var(--tint-blue)"><div class="wrap"><h2>%s</h2><div class="grid">%s</div></div></section>')%(
        lb("Tell us your application","告诉我们您的应用","Cho chúng tôi biết ứng dụng của bạn","บอกเราเกี่ยวกับการใช้งานของคุณ"),
        esc(ask), form, form_js,
        lb("Prefer email? Write to","更习惯邮件？请联系","Thích email hơn? Viết cho","สะดวกอีเมล? เขียนถึง"),
        lb("Offices","办公室","Văn phòng","สำนักงาน"), cards)
    contact_lbl=P(lang,"Contact","联系我们","Liên hệ","ติดต่อ")
    crumb=[(P(lang,"Home","首页","Trang chủ","หน้าแรก"),"/"),(contact_lbl,"/contact/")]
    write(lang,"/contact/",page(lang,"/contact/",
        P(lang,"Contact ETIA | ETIA","联系 ETIA | ETIA","Liên hệ ETIA | ETIA","ติดต่อ ETIA | ETIA"),
        P(lang,
          "Contact ETIA — Shanghai · Hong Kong · Bangkok · Bac Ninh · etialabel@etia-tech.com. Share your application and we'll match the material and send samples.",
          "联系 ETIA:上海 · 香港 · 曼谷 · 北宁 · etialabel@etia-tech.com。提供工况,我们匹配材料并寄样。",
          "Liên hệ ETIA — Thượng Hải · Hồng Kông · Bangkok · Bắc Ninh · etialabel@etia-tech.com. Chia sẻ ứng dụng của bạn, chúng tôi sẽ ghép vật liệu và gửi mẫu.",
          "ติดต่อ ETIA — เซี่ยงไฮ้ · ฮ่องกง · กรุงเทพฯ · บั๊กนิญ · etialabel@etia-tech.com แบ่งปันการใช้งานของคุณ เราจะจับคู่วัสดุและส่งตัวอย่าง"),
        P(lang,"Contact ETIA","联系我们","Liên hệ ETIA","ติดต่อ ETIA"),
        P(lang,"Share your application — we'll match the material and validate by sample.",
          "提供工况,我们匹配材料并寄样验证。",
          "Chia sẻ ứng dụng của bạn — chúng tôi sẽ ghép vật liệu và xác thực bằng mẫu.",
          "แบ่งปันการใช้งานของคุณ — เราจะจับคู่วัสดุและตรวจสอบด้วยตัวอย่าง"),
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

SERVICE_OFFICES=[
  ("Shanghai","上海","+86 139 1833 9249 · 400 990 8448"),
  ("Hong Kong","香港","etialabel@etia-tech.com"),
  ("Bangkok","曼谷","+66 811 746 947"),
  ("Bac Ninh","北宁","+84 961 530 153"),
]
# Regional contact cards for the Service page ("Contact your regional ETIA team").
# addr = [native line, english line] (native omitted for HK). role = (en, zh).
SERVICE_REGIONS=[
  {"region":("China · Shanghai","中国 · 上海","Trung Quốc · Thượng Hải","จีน · เซี่ยงไฮ้"),"name":"Da Li","role":("","","",""),
   "addr":["上海市普陀区中江路 388 弄国盛中心 2 号楼 1903 室",
           "Rm. 1903, 2# Building, Guoson Centre, No. 388 Zhongjiang Rd, Putuo District, Shanghai, China"],
   "phone":"+86 139 1833 9249 · 400 990 8448 · +86-21-6432-7144","email":"etialabel@etia-tech.com"},
  {"region":("China · Hong Kong","中国 · 香港","Trung Quốc · Hồng Kông","จีน · ฮ่องกง"),"name":"Da Li","role":("","","",""),
   "addr":["Room 1003, 10/F, Tower 1, Lippo Centre, 89 Queensway, Admiralty, Hong Kong"],
   "phone":"+86 139 1833 9249","email":"etialabel@etia-tech.com"},
  {"region":("Thailand · Bangkok","泰国 · 曼谷","Thái Lan · Bangkok","ไทย · กรุงเทพฯ"),"name":"Mr. Sompoch Ratchakom (Job)","role":("Sales Director","销售总监","Giám đốc Kinh doanh","ผู้อำนวยการฝ่ายขาย"),
   "addr":["22/41 เอช-เคป บิซ เซ็นเตอร์ ถนนสุขาภิบาล 2 แขวงประเวศ เขตประเวศ กรุงเทพฯ 10250",
           "22/41 H-Cape Biz Center, Sukhaphiban 2 Road, Prawet Subdistrict, Prawet District, Bangkok 10250, Thailand"],
   "phone":"+66 811 746 947","email":"etialabel@etia-tech.com"},
  {"region":("Vietnam · Bac Ninh","越南 · 北宁","Việt Nam · Bắc Ninh","เวียดนาม · บั๊กนิญ"),"name":"Trần Diệu Hoa","role":("Technical Engineer","技术工程师","Kỹ sư Kỹ thuật","วิศวกรเทคนิค"),
   "addr":["Số 10 đường Thanh Niên, Khu 5, Phường Võ Cường, Tỉnh Bắc Ninh, Việt Nam",
           "No. 10 Thanh Nien Street, Area 5, Vo Cuong Ward, Bac Ninh Province, Viet Nam"],
   "phone":"+84 961 530 153","email":"etialabel@etia-tech.com"},
]
# 4 service images (one per commitment) on COS. quote() matches COS folder encoding.
import urllib.parse as _up
_SVC_B="https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com/"+_up.quote("C・Service 服务图 4 组")+"/"
SERVICE_IMGS=["https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com/SERVICE%20/QUALITY",
              "https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com/SERVICE%20/SOLUTION",
              "https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com/SERVICE%20/SUPPLY",
              "https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com/SERVICE%20/SUPPORT"]
SERVICE_INTRO=(
  "From material quality and application validation to flexible converting and ongoing support, ETIA helps customers reduce risk and achieve reliable labeling performance throughout the entire project lifecycle.",
  "从材料质量、应用验证，到柔性加工与持续支持，ETIA 在项目全流程中帮助客户降低导入风险，确保标签应用稳定可靠。",
  "Từ chất lượng vật liệu và xác nhận ứng dụng đến gia công linh hoạt và hỗ trợ liên tục, ETIA giúp khách hàng giảm rủi ro và đạt hiệu suất dán nhãn đáng tin cậy trong suốt vòng đời dự án.",
  "ตั้งแต่คุณภาพวัสดุและการตรวจสอบการใช้งาน ไปจนถึงการแปรรูปที่ยืดหยุ่นและการสนับสนุนอย่างต่อเนื่อง ETIA ช่วยลูกค้าลดความเสี่ยงและได้ประสิทธิภาพการติดฉลากที่เชื่อถือได้ตลอดวงจรชีวิตของโครงการ")
# num, title(en,zh,vi,th), tagline(...), body[(...)...], close(...)
SERVICE_COMMIT=[
 {"num":"01","title":('100% Quality Inspection', '100% 质量检验', 'Kiểm tra chất lượng 100%', 'การตรวจสอบคุณภาพ 100%'),
  "tag":('Every batch tested. Every shipment verified.', '批批检测，件件验证。', 'Kiểm tra từng lô. Xác minh từng lô hàng.', 'ทดสอบทุกล็อต ตรวจสอบทุกการจัดส่ง'),
  "body":[('Incoming materials are tested before production, verified during processing, and inspected again before shipment. Every batch is retained for full traceability.', '来料先检测，上机前验证，出厂前复检，并保留批次留样，实现全流程质量追溯。', 'Vật liệu đầu vào được kiểm tra trước sản xuất, xác minh trong quá trình gia công và kiểm tra lại trước khi giao hàng. Mỗi lô đều được lưu mẫu để truy xuất đầy đủ.', 'วัสดุขาเข้าได้รับการทดสอบก่อนการผลิต ตรวจสอบระหว่างกระบวนการ และตรวจสอบอีกครั้งก่อนจัดส่ง ทุกล็อตถูกเก็บไว้เพื่อการตรวจสอบย้อนกลับอย่างสมบูรณ์')],
  "close":('Every material. Every batch. Every delivery.', '每一种材料，每一个批次，每一次交付。', 'Mọi vật liệu. Mọi lô. Mọi lần giao hàng.', 'ทุกวัสดุ ทุกล็อต ทุกการจัดส่ง')},
 {"num":"02","title":('Application-Driven Solutions', '应用驱动方案', 'Giải pháp theo ứng dụng', 'โซลูชันที่ขับเคลื่อนด้วยการใช้งาน'),
  "tag":('The right material for every application.', '以应用为导向，匹配合适材料。', 'Vật liệu phù hợp cho mọi ứng dụng.', 'วัสดุที่เหมาะสมสำหรับทุกการใช้งาน'),
  "body":[('Our engineers work with your team to understand the application, evaluate the process, and recommend the right material through on-site or remote support.', '工程师深入了解您的应用、工艺与环境，可现场或远程协同，帮助选择更适合的材料与标识方案。', 'Kỹ sư của chúng tôi làm việc với đội ngũ của bạn để hiểu ứng dụng, đánh giá quy trình và đề xuất vật liệu phù hợp thông qua hỗ trợ tại chỗ hoặc từ xa.', 'วิศวกรของเราทำงานร่วมกับทีมของคุณเพื่อทำความเข้าใจการใช้งาน ประเมินกระบวนการ และแนะนำวัสดุที่เหมาะสมผ่านการสนับสนุนในสถานที่หรือระยะไกล')],
  "close":("We don't guess. We validate.", '我们不凭猜测，依靠验证。', 'Chúng tôi không phỏng đoán. Chúng tôi xác thực.', 'เราไม่เดา เราพิสูจน์')},
 {"num":"03","title":('Flexible Supply', '柔性供应', 'Cung ứng linh hoạt', 'การจัดหาที่ยืดหยุ่น'),
  "tag":('Flexible supply, built around your production.', '灵活供货，适配您的生产节奏。', 'Cung ứng linh hoạt, phù hợp với sản xuất của bạn.', 'การจัดหาที่ยืดหยุ่น ออกแบบตามการผลิตของคุณ'),
  "body":[('Multiple warehouses, flexible air and sea logistics, plus custom slitting, die-cutting, and pre-printed labels to support your production.', '多地仓储，海运、空运灵活配送，并提供分切、模切、预打印等配套服务，满足不同生产需求。', 'Nhiều kho hàng, logistics đường biển và hàng không linh hoạt, cùng dịch vụ cắt, bế và in sẵn theo yêu cầu để hỗ trợ sản xuất của bạn.', 'คลังสินค้าหลายแห่ง โลจิสติกส์ทางอากาศและทางทะเลที่ยืดหยุ่น พร้อมบริการสลิต ไดคัท และฉลากพิมพ์ล่วงหน้าตามความต้องการเพื่อสนับสนุนการผลิตของคุณ')],
  "close":('Flexible materials. Flexible formats. Flexible quantities.', '材料灵活、规格灵活、数量灵活。', 'Vật liệu linh hoạt. Quy cách linh hoạt. Số lượng linh hoạt.', 'วัสดุยืดหยุ่น รูปแบบยืดหยุ่น จำนวนยืดหยุ่น')},
 {"num":"04","title":('Responsive Application Support', '快速应用支持', 'Hỗ trợ ứng dụng nhanh chóng', 'การสนับสนุนการใช้งานที่รวดเร็ว'),
  "tag":('Fast support for material selection, printing, adhesion and application issues.', '快速响应材料选型、打印、粘接及实际应用中的问题', 'Hỗ trợ nhanh cho việc chọn vật liệu, in ấn, độ bám dính và các vấn đề ứng dụng.', 'การสนับสนุนที่รวดเร็วสำหรับการเลือกวัสดุ การพิมพ์ การยึดเกาะ และปัญหาการใช้งาน'),
  "body":[('A dedicated support team connects sales, engineering, logistics, and service for fast, coordinated responses throughout your project.', '专属服务团队协同销售、工程、物流与客服，快速响应项目需求，持续支持生产运行。', 'Đội ngũ hỗ trợ chuyên trách kết nối bán hàng, kỹ thuật, logistics và dịch vụ để phản hồi nhanh và phối hợp xuyên suốt dự án của bạn.', 'ทีมสนับสนุนเฉพาะทางเชื่อมโยงฝ่ายขาย วิศวกรรม โลจิสติกส์ และบริการ เพื่อการตอบสนองที่รวดเร็วและประสานงานตลอดโครงการของคุณ')],
  "close":('Before delivery, during production, and beyond.', '交付之前、生产之中，以及长期应用之后。', 'Trước khi giao hàng, trong khi sản xuất và về sau.', 'ก่อนการจัดส่ง ระหว่างการผลิต และหลังจากนั้น')},
]

def build_service(lang):
    zh=(lang=="zh")
    j=JX[lang]
    # --- Service Commitment as a tab BAR (same module as the industry landings) ---
    def panel_img(i):
        u=SERVICE_IMGS[i] if i<len(SERVICE_IMGS) else ""
        img=('<img src="%s" alt="" loading="lazy" onerror="this.remove()">'%esc(u)) if u else ""
        return '<div class="apimg">%s<span class="ph">\U0001F6E1</span></div>'%img
    tabs="".join('<button class="apptab%s" onclick="etaTab(this)">%s</button>'%((" on" if i==0 else ""),esc(it["title"][j]))
                 for i,it in enumerate(SERVICE_COMMIT))
    def panel(i,it):
        bodyp="".join('<p>%s</p>'%esc(b[j]) for b in it["body"])
        return ('<div class="apppanel"%s>%s<div class="aptext"><div class="svc-num">%s</div>'
                '<h3>%s</h3><p class="svc-tag">%s</p>%s<p class="svc-close">%s</p></div></div>')%(
            (' style="display:none"' if i>0 else ''),panel_img(i),esc(it["num"]),
            esc(it["title"][j]),esc(it["tag"][j]),bodyp,esc(it["close"][j]))
    panels="".join(panel(i,it) for i,it in enumerate(SERVICE_COMMIT))
    tabscript=("<script>function etaTab(b){var m=b.closest('.appmod');var t=[].slice.call(m.querySelectorAll('.apptab'));"
               "var i=t.indexOf(b);t.forEach(function(x,j){x.classList.toggle('on',j===i);});"
               "m.querySelectorAll('.apppanel').forEach(function(p,j){p.style.display=(j===i)?'grid':'none';});}"
               "function etaScroll(b,d){var r=b.closest('.apptabsrow').querySelector('.apptabs');r.scrollBy({left:d*260,behavior:'smooth'});}"
               "function etaMail(f){var g=function(n){var e=f.elements[n];return e?e.value:'';};"
               "var b='Name: '+g('name')+'%0D%0ACompany: '+g('company')+'%0D%0APhone: '+g('phone')+'%0D%0AEmail: '+g('email')+'%0D%0A%0D%0A'+g('msg');"
               "window.location.href='mailto:etialabel@etia-tech.com?subject='+encodeURIComponent('Website enquiry')+'&body='+encodeURIComponent(b);return false;}</script>")
    commit_sec=('<section class="blk"><div class="wrap"><h2>%s</h2>'
                '<p class="lede" style="max-width:64em;margin-bottom:26px">%s</p>'
                '<div class="appmod svc">'
                '<div class="apptabsrow"><button class="apparrow" onclick="etaScroll(this,-1)" aria-label="prev">&lsaquo;</button>'
                '<div class="apptabs">%s</div>'
                '<button class="apparrow" onclick="etaScroll(this,1)" aria-label="next">&rsaquo;</button></div>'
                '<div class="apppanels">%s</div></div></div></section>')%(
        P(lang,"Our Service Commitment","我们的服务承诺","Cam kết dịch vụ của chúng tôi","คำมั่นสัญญาด้านบริการของเรา"), esc(SERVICE_INTRO[j]), tabs, panels)
    # --- contact form with phone ---
    ph=lambda p: '<input name="%s" placeholder="%s"%s>'%p
    fields=('<div class="cfrow"><input name="name" placeholder="%s" required><input name="company" placeholder="%s"></div>'
            '<div class="cfrow"><input name="phone" placeholder="%s" required><input name="email" type="email" placeholder="%s"></div>'
            '<textarea name="msg" rows="4" placeholder="%s"></textarea>'
            '<button class="btn pri" type="submit">%s</button>')%(
        P(lang,"Name *","姓名 *","Họ tên *","ชื่อ *"),P(lang,"Company","公司","Công ty","บริษัท"),
        P(lang,"Phone *","电话 *","Điện thoại *","โทรศัพท์ *"),P(lang,"Email","邮箱","Email","อีเมล"),
        P(lang,"Describe your application: surface, temperature, chemistry, print method and label size",
             "请描述您的应用：表面、温度、化学环境、打印方式与标签尺寸",
             "Mô tả ứng dụng của bạn: bề mặt, nhiệt độ, hóa chất, phương pháp in và kích thước nhãn",
             "อธิบายการใช้งานของคุณ: พื้นผิว อุณหภูมิ สารเคมี วิธีการพิมพ์ และขนาดฉลาก"),
        P(lang,"Send Enquiry","提交","Gửi yêu cầu","ส่งคำถาม"))
    # --- Global regional contact cards ---
    IC_PIN='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-6-5.686-6-10a6 6 0 1 1 12 0c0 4.314-6 10-6 10z"/><circle cx="12" cy="11" r="2.4"/></svg>'
    IC_TEL='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6.6 10.8a13 13 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.24 11 11 0 0 0 3.5.56 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1 11 11 0 0 0 .56 3.5 1 1 0 0 1-.24 1z"/></svg>'
    IC_MAIL='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>'
    def gcard(r):
        role = r["role"][j]
        role_html = (' <span class="gc-role">· %s</span>' % esc(role)) if role else ""
        addr_html = "<br>".join(esc(a) for a in r["addr"])
        return ('<div class="gcard"><div class="gc-region">%s</div>'
                '<div class="gc-name">%s%s</div>'
                '<div class="gc-line">%s<div>%s</div></div>'
                '<div class="gc-line">%s<div>%s</div></div>'
                '<a class="gc-line" href="mailto:%s">%s<div>%s</div></a></div>') % (
            esc(r["region"][j]), esc(r["name"]), role_html,
            IC_PIN, addr_html, IC_TEL, esc(r["phone"]), esc(r["email"]), IC_MAIL, esc(r["email"]))
    global_sec=('<section class="blk"><div class="wrap"><div class="eyebrow">%s</div><h2>%s</h2>'
                '<div class="gcont">%s</div><p class="gc-note">%s</p></div></section>')%(
        P(lang,"GLOBAL CONTACT","全球联系","LIÊN HỆ TOÀN CẦU","ติดต่อทั่วโลก"),
        P(lang,"Contact Your Regional ETIA Team","联系您所在地区的 ETIA 团队","Liên hệ đội ngũ ETIA khu vực của bạn","ติดต่อทีม ETIA ในภูมิภาคของคุณ"),
        "".join(gcard(r) for r in SERVICE_REGIONS),
        P(lang,"* Email us for a fast response — our team usually replies within one business day.",
             "* 通过邮件联系我们可获得快速响应 —— 我们的团队通常在 1 个工作日内回复",
             "* Gửi email cho chúng tôi để được phản hồi nhanh — đội ngũ của chúng tôi thường trả lời trong vòng một ngày làm việc.",
             "* ส่งอีเมลถึงเราเพื่อการตอบกลับที่รวดเร็ว — ทีมของเรามักตอบกลับภายในหนึ่งวันทำการ"))
    # form's side column: a short email note (regional phones now live in the cards above)
    phones=('<div class="cph"><b>%s</b><span><a class="email" href="mailto:etialabel@etia-tech.com">etialabel@etia-tech.com</a></span></div>'
            '<div class="cph"><b>%s</b><span>%s</span></div>')%(
        P(lang,"Email","邮箱","Email","อีเมล"),
        P(lang,"Response time","响应时间","Thời gian phản hồi","เวลาตอบกลับ"),
        P(lang,"We usually reply within one business day","我们通常在 1 个工作日内回复","Chúng tôi thường trả lời trong vòng một ngày làm việc","เรามักตอบกลับภายในหนึ่งวันทำการ"))
    form_sec=('<section class="blk" style="background:var(--tint-blue)"><div class="wrap">'
              '<h2>%s</h2><div class="sub">%s</div>'
              '<div class="ctwo"><form class="cform" onsubmit="return etaMail(this)">%s</form>'
              '<div class="cphones">%s</div></div></div></section>')%(
        P(lang,"Get in Touch","联系我们","Liên hệ","ติดต่อเรา"),
        P(lang,"Leave your phone and application — we'll reply quickly and arrange samples.",
             "留下电话与应用需求，我们尽快回复并安排样品。",
             "Để lại số điện thoại và ứng dụng của bạn — chúng tôi sẽ trả lời nhanh và chuẩn bị mẫu.",
             "ทิ้งเบอร์โทรและการใช้งานของคุณไว้ — เราจะตอบกลับอย่างรวดเร็วและจัดเตรียมตัวอย่าง"),
        fields, phones)
    body=commit_sec+global_sec+form_sec+('<div class="wrap">%s</div>'%cta2(lang,"service"))+tabscript
    crumb=[(P(lang,"Home","首页","Trang chủ","หน้าแรก"),"/"),(P(lang,"Service","服务","Dịch vụ","บริการ"),"/service/")]
    # hero = single main visual with a subtle Ken Burns zoom (headline + slogan only)
    sh=HOME2.get(lang,HOME2["en"])["sections"][3]
    hero=hero_single_anim(lang, section_banner(3, lang), "", sh["h2"], sh["sub"])
    body=home_trustbar(lang)+body   # 20-year trust bar under the hero
    write(lang,"/service/",page(lang,"/service/",
        P(lang,"Service | ETIA","服务 | ETIA","Dịch vụ | ETIA","บริการ | ETIA"),
        P(lang,"100% quality inspection, application-driven selection, flexible supply and responsive support — the ETIA service commitment.",
             "100% 质量检测、应用驱动选型、柔性供应与快速响应服务 —— ETIA 服务承诺。",
             "Kiểm tra chất lượng 100%, lựa chọn theo ứng dụng, cung ứng linh hoạt và hỗ trợ nhanh chóng — cam kết dịch vụ của ETIA.",
             "การตรวจสอบคุณภาพ 100% การเลือกตามการใช้งาน การจัดหาที่ยืดหยุ่น และการสนับสนุนที่รวดเร็ว — คำมั่นสัญญาด้านบริการของ ETIA"),
        P(lang,"Service","服务","Dịch vụ","บริการ"), "",
        body, crumb, active="service", trust=False, hero=hero, langs=NAV_PILLAR_LANGS))
    if lang=="en": track("/service/","core")

def build_products_landing(lang):
    """Products landing page (/products/) — a mega-menu-style category page:
    browse by industry and by operating environment. No redirect to Home."""
    T = HOME_I18N[lang]
    def card(url, name, desc):
        return ('<a class="pmcard" href="%s"><h3><span class="pmar">›</span>%s</h3>'
                '<p>%s</p></a>') % (Lx(lang, url), esc(name), esc(desc))
    # By Industry — 6 sectors (names + descriptions already 4-language in home_i18n)
    ind_cards = "".join(card(FOCUS_URLS[k], f["name"], f["desc"]) for k, f in enumerate(T["focus"]))
    # By Environment — the 4 environment solution pages (4-language)
    ENV = [
      ("/products/item/high-heat-identification/",
       P(lang,"Heat Resistant","耐高温","Chịu nhiệt cao","ทนความร้อนสูง"),
       P(lang,"High-temperature identification that stays legible and firmly bonded through demanding thermal processing.",
            "面向高温工艺的标识方案 —— 高温下依旧清晰可读、牢固贴附",
            "Nhận diện ở nhiệt độ cao, vẫn rõ nét và bám chắc qua các quá trình xử lý nhiệt khắc nghiệt.",
            "การระบุที่อุณหภูมิสูง ยังคงอ่านได้และยึดแน่นตลอดกระบวนการทางความร้อนที่เข้มงวด")),
      ("/products/item/cold-chain-cryogenic-labels/",
       P(lang,"Low Temperature Resistant","耐低温","Chịu nhiệt độ thấp","ทนอุณหภูมิต่ำ"),
       P(lang,"Cold-chain and cryogenic labels for storage down to −196°C and repeated freeze-thaw.",
            "冷链与超低温标签 —— 适用于低至 −196°C 存储与反复冻融",
            "Nhãn chuỗi lạnh và siêu lạnh cho lưu trữ tới −196°C và chu kỳ đông-rã lặp lại.",
            "ฉลากโซ่ความเย็นและอุณหภูมิต่ำมากสำหรับการจัดเก็บถึง −196°C และการแช่แข็ง-ละลายซ้ำ")),
      ("/products/item/chemical-resistant-labels/",
       P(lang,"Chemical Resistant","耐化学","Kháng hóa chất","ทนสารเคมี"),
       P(lang,"Labels that resist solvents, disinfectants, oils, acids and alkalis without fading or lifting.",
            "耐溶剂、消毒剂、油污、酸碱等化学介质 —— 不褪色、不脱落",
            "Nhãn kháng dung môi, chất khử trùng, dầu, axit và kiềm mà không phai màu hay bong tróc.",
            "ฉลากที่ทนตัวทำละลาย น้ำยาฆ่าเชื้อ น้ำมัน กรดและด่าง โดยไม่ซีดจางหรือหลุดลอก")),
      ("/products/item/sterilization-labels/",
       P(lang,"Sterilization","灭菌","Tiệt trùng","การฆ่าเชื้อ"),
       P(lang,"Labels that survive steam, dry heat, gamma, EtO and chemical sterilization while staying readable.",
            "耐蒸汽、干热、伽马、环氧乙烷及化学灭菌 —— 全周期清晰可读",
            "Nhãn chịu được hơi nước, nhiệt khô, gamma, EtO và tiệt trùng hóa học mà vẫn đọc được.",
            "ฉลากที่ทนไอน้ำ ความร้อนแห้ง แกมมา EtO และการฆ่าเชื้อด้วยสารเคมี ขณะยังคงอ่านได้")),
    ]
    env_cards = "".join(card(u, nm, ds) for u, nm, ds in ENV)
    sec = lambda eye, h, grid, gcls="": ('<section class="blk"><div class="wrap"><div class="eyebrow">%s</div>'
        '<h2>%s</h2><div class="pmgrid%s">%s</div></div></section>') % (esc(eye), esc(h), (" " + gcls) if gcls else "", grid)
    find_url = Lx(lang, "/products/find/")
    find_band = (
      '<section class="blk" style="padding-top:26px;padding-bottom:0"><div class="wrap">'
      '<a href="%s" style="display:flex;flex-wrap:wrap;align-items:center;gap:16px 22px;justify-content:space-between;'
      'background:linear-gradient(100deg,#143C96,#1A56DB);border-radius:16px;padding:22px 26px;text-decoration:none;'
      'box-shadow:0 14px 34px rgba(20,60,150,.18)">'
      '<div style="min-width:0"><div style="color:#8fe063;font-size:12px;font-weight:800;letter-spacing:.12em;text-transform:uppercase">%s</div>'
      '<div style="color:#fff;font-family:var(--sans);font-weight:800;font-size:23px;line-height:1.15;margin:3px 0 2px">%s</div>'
      '<div style="color:#dbe6ff;font-size:14px">%s</div></div>'
      '<span style="flex:none;background:#41A62A;color:#fff;font-weight:800;font-size:14px;padding:12px 22px;border-radius:10px">%s</span>'
      '</a></div></section>') % (
        find_url,
        esc(P(lang,"Product Finder","产品查找","Tìm sản phẩm","ค้นหาสินค้า")),
        esc(P(lang,"Find a Label Material","查找标签材料","Tìm vật liệu nhãn","ค้นหาวัสดุฉลาก")),
        esc(P(lang,"Search by part number, material or application — or filter by industry, temperature and more.",
              "按料号、材料或应用搜索 —— 或按行业、温度等维度筛选。",
              "Tìm theo mã, vật liệu hoặc ứng dụng — hoặc lọc theo ngành, nhiệt độ và hơn thế.",
              "ค้นหาด้วยรหัส วัสดุ หรือการใช้งาน — หรือกรองตามอุตสาหกรรม อุณหภูมิ และอื่นๆ")),
        esc(P(lang,"Search & filter →","搜索与筛选 →","Tìm & lọc →","ค้นหาและกรอง →")))
    body = (find_band
          + sec(P(lang,"BY INDUSTRY","按行业","THEO NGÀNH","ตามอุตสาหกรรม"),
                P(lang,"Labels by Industry","按行业选择","Nhãn theo ngành","ฉลากตามอุตสาหกรรม"), ind_cards)
          + sec(P(lang,"BY ENVIRONMENT","按环境","THEO MÔI TRƯỜNG","ตามสภาพแวดล้อม"),
                P(lang,"Labels by Operating Environment","按使用环境选择","Nhãn theo môi trường vận hành","ฉลากตามสภาพแวดล้อมการใช้งาน"), env_cards, "pm4")
          + sec(P(lang,"BY BRAND","按品牌","THEO THƯƠNG HIỆU","ตามแบรนด์"),
                P(lang,"Labels by Brand","按品牌选择","Nhãn theo thương hiệu","ฉลากตามแบรนด์"),
                card("/products/polyonics/",
                     P(lang,"Polyonics","Polyonics","Polyonics","Polyonics"),
                     P(lang,"Genuine imported Polyonics polyimide labels — APEX, XF58 and ESD-XF78 series.",
                          "Polyonics 原装进口聚酰亚胺标签 —— APEX、XF58 与 ESD-XF78 系列。",
                          "Nhãn polyimide Polyonics nhập khẩu chính hãng — dòng APEX, XF58 và ESD-XF78.",
                          "ฉลากโพลีอิไมด์ Polyonics นำเข้าแท้ — ซีรีส์ APEX, XF58 และ ESD-XF78"))
                + card("/products/item/e-series/",
                     P(lang,"E-Label","E-Label","E-Label","E-Label"),
                     P(lang,"ETIA's own in-house polyimide PCB label series — general, high-adhesion, removable and ESD.",
                          "ETIA 自研聚酰亚胺 PCB 标签系列 —— 通用、超粘、可移除与防静电。",
                          "Dòng nhãn PCB polyimide tự phát triển của ETIA — phổ thông, siêu bám, tháo rời và chống tĩnh điện.",
                          "ซีรีส์ฉลาก PCB โพลีอิไมด์ที่ ETIA พัฒนาเอง — ทั่วไป กาวเหนียว ถอดได้ และป้องกันไฟฟ้าสถิต"))
                + card("/products/heatproof/",
                     P(lang,"HEATPROOF","HEATPROOF","HEATPROOF","HEATPROOF"),
                     P(lang,"Extreme-temperature labels and tags — metal-foil and ceramic, 200°C to 1200°C.",
                          "极端高温标签与吊牌 —— 金属箔与陶瓷，200°C 至 1200°C。",
                          "Nhãn và thẻ nhiệt độ cực cao — lá kim loại và gốm, 200°C đến 1200°C.",
                          "ฉลากและแท็กอุณหภูมิสูงสุดขั้ว — ฟอยล์โลหะและเซรามิก 200°C ถึง 1200°C")))
          + ('<div class="wrap">%s</div>' % cta2(lang, "products", Lx)))
    s = HOME2.get(lang, HOME2["en"])["sections"][0]
    hero = page_hero(lang, s["eyebrow"], s["h2"], s["sub"], "",
                     s["b1"], s["b1u"], s["b2"], s["b2u"], SECTION_BG.get(0, ""))
    crumb = [(P(lang,"Home","首页","Trang chủ","หน้าแรก"),"/"),
             (P(lang,"Products","产品","Sản phẩm","ผลิตภัณฑ์"),"/products/")]
    write(lang, "/products/", page(lang, "/products/",
        P(lang,"Products | ETIA","产品 | ETIA","Sản phẩm | ETIA","ผลิตภัณฑ์ | ETIA"),
        P(lang,"Browse ETIA durable and specialty label materials by industry and by operating environment.",
             "按行业与使用环境浏览 ETIA 耐久与特种标签材料。",
             "Duyệt vật liệu nhãn bền và chuyên dụng của ETIA theo ngành và theo môi trường vận hành.",
             "เรียกดูวัสดุฉลากทนทานและเฉพาะทางของ ETIA ตามอุตสาหกรรมและสภาพแวดล้อมการใช้งาน"),
        P(lang,"Products","产品","Sản phẩm","ผลิตภัณฑ์"), "",
        body, crumb, active="products", trust=False, hero=hero, langs=NAV_PILLAR_LANGS))
    if lang=="en": track("/products/","core")

def build_applications(lang):
    """Applications = Application-Notes hub. A simple picture + topic card grid,
    newest first. (Kept intentionally plain — no industry filter.)"""
    zh=(lang=="zh")
    j=JX[lang]
    def _nl(node):
        if not isinstance(node,dict): return node or ""
        return node.get(lang) or node.get("en") or node.get("zh") or ""
    notes=[]
    adir=os.path.join(BUILD_DIR,"data","appnotes")
    for fn in sorted(os.listdir(adir)):
        if fn.endswith(".json"):
            n=json.load(open(os.path.join(adir,fn),encoding="utf-8"))
            nlangs=n.get("langs",["en","zh","vi","th"])
            # show the note if it exists in this language, or fall back to English
            # (vi/th note pages default to the English article until translated).
            if lang in nlangs or "en" in nlangs: notes.append(n)
    notes.sort(key=lambda n:n.get("order",99))
    def _notecard(n):
        img=n.get("image") or n.get("banner") or ""
        im=('<img src="%s" alt="" loading="lazy" onerror="this.remove()">'%esc(img)) if img else ''
        title=_nl(n.get("title",{})); sub=_nl(n.get("subtitle",{}))
        tags=n.get("tags",{}) if isinstance(n.get("tags",{}),dict) else {}
        txt=" ".join([title,sub]+[str(x) for x in (tags.get(lang,[]) or tags.get("en",[]))]).lower()
        return ('<a class="acard appcard" data-txt="%s" href="%s"><div class="acard-img">%s</div>'
                '<div class="acard-body"><h3 class="indname">%s</h3><p>%s</p></div></a>')%(
            esc(txt), Lx(lang,"/application-notes/%s/"%n["slug"]), im, esc(title), esc(sub))
    note_cards="".join(_notecard(n) for n in notes)
    T=HOME_I18N[lang]
    # 1) Label Solutions by environment — the temperature solution landing pages
    #    (Heat Resistant / Low Temperature Resistant, room for more as they launch).
    SOL_DESC={
      "/products/item/high-heat-identification/":
        {"en":"High-temperature identification that stays legible and firmly bonded through demanding thermal processing.",
         "zh":"面向高温工艺的标识方案 —— 高温下依旧清晰可读、牢固贴附",
         "vi":"Nhận diện ở nhiệt độ cao, vẫn rõ nét và bám chắc qua các quá trình xử lý nhiệt khắc nghiệt.",
         "th":"การระบุที่อุณหภูมิสูง ยังคงอ่านได้และยึดแน่นตลอดกระบวนการทางความร้อนที่เข้มงวด"},
      "/products/item/cold-chain-cryogenic-labels/":
        {"en":"Cold-chain and cryogenic labels for storage down to −196°C and repeated freeze-thaw.",
         "zh":"冷链与超低温标签 —— 适用于低至 −196°C 存储与反复冻融",
         "vi":"Nhãn chuỗi lạnh và siêu lạnh cho lưu trữ tới −196°C và chu kỳ đông-rã lặp lại.",
         "th":"ฉลากโซ่ความเย็นและอุณหภูมิต่ำมากสำหรับการจัดเก็บถึง −196°C และการแช่แข็ง-ละลายซ้ำ"},
      "/products/item/chemical-resistant-labels/":
        {"en":"Labels that resist solvents, disinfectants, oils, acids and alkalis without fading or lifting.",
         "zh":"耐溶剂、消毒剂、油污、酸碱等化学介质 —— 不褪色、不脱落",
         "vi":"Nhãn kháng dung môi, chất khử trùng, dầu, axit và kiềm mà không phai màu hay bong tróc.",
         "th":"ฉลากที่ทนตัวทำละลาย น้ำยาฆ่าเชื้อ น้ำมัน กรดและด่าง โดยไม่ซีดจางหรือหลุดลอก"},
      "/products/item/sterilization-labels/":
        {"en":"Labels that survive steam, dry heat, gamma, EtO and chemical sterilization while staying readable.",
         "zh":"耐蒸汽、干热、伽马、环氧乙烷及化学灭菌 —— 全周期清晰可读",
         "vi":"Nhãn chịu được hơi nước, nhiệt khô, gamma, EtO và tiệt trùng hóa học mà vẫn đọc được.",
         "th":"ฉลากที่ทนไอน้ำ ความร้อนแห้ง แกมมา EtO และการฆ่าเชื้อด้วยสารเคมี ขณะยังคงอ่านได้"},
    }
    SOL_NAME={
      "/products/item/high-heat-identification/":("Heat Resistant","耐高温","Chịu nhiệt cao","ทนความร้อนสูง"),
      "/products/item/cold-chain-cryogenic-labels/":("Low Temperature Resistant","耐低温","Chịu nhiệt độ thấp","ทนอุณหภูมิต่ำ"),
      "/products/item/chemical-resistant-labels/":("Chemical Resistant","耐化学","Kháng hóa chất","ทนสารเคมี"),
      "/products/item/sterilization-labels/":("Sterilization","灭菌","Tiệt trùng","การฆ่าเชื้อ"),
    }
    SOL_ICON=[1,2,0,3]  # flame / droplet / chip / … from INDUSTRY_ICONS — fallback only
    _SOLC="https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com/SOLUTION%20/"
    SOL_IMG={
      "/products/item/high-heat-identification/":     _SOLC+"SOLUTION-HEAT.jpg",
      "/products/item/cold-chain-cryogenic-labels/":  _SOLC+"SOLUTION-COLD.jpg",
      "/products/item/chemical-resistant-labels/":    _SOLC+"SOLUTION-CHEMICAL.jpg",
      "/products/item/sterilization-labels/":         _SOLC+"SOLUTION-sterlization.jpg",
    }
    sol_cards=""
    for i,(e,z,u) in enumerate(PROD_AXES[0][3]):
        nm=SOL_NAME.get(u,(e,z,e,e))[j]
        ds=SOL_DESC.get(u,{}).get(lang) or SOL_DESC.get(u,{}).get("en","")
        img=SOL_IMG.get(u,"")
        top=('<img src="%s" alt="%s" loading="lazy" onerror="this.remove()">'%(esc(img),esc(nm))) if img \
            else ('<span class="aicon">%s</span>'%INDUSTRY_ICONS[SOL_ICON[i%len(SOL_ICON)]%len(INDUSTRY_ICONS)])
        sol_cards+=('<a class="acard" href="%s"><div class="acard-img g%d">%s</div>'
                    '<div class="acard-body"><h3 class="indname">%s</h3><p>%s</p>'
                    '<div class="acard-go">%s →</div></div></a>')%(
            Lx(lang,u), i%6, top, esc(nm), esc(ds), esc(T["explore"]))
    sol_section=('<section class="blk"><div class="wrap"><div class="eyebrow">%s</div><h2>%s</h2><div class="sub">%s</div>'
                 '<div class="solgrid">%s</div></div></section>')%(
        P(lang,"LABEL SOLUTIONS","标签方案","GIẢI PHÁP NHÃN","โซลูชันฉลาก"),
        P(lang,"Label Solutions by Environment","按环境选择方案","Giải pháp nhãn theo môi trường","โซลูชันฉลากตามสภาพแวดล้อม"),
        P(lang,"From high heat to deep cryogenic — choose a label solution by operating environment.",
             "从高温到超低温 —— 按使用环境选择合适的标签方案。",
             "Từ nhiệt độ cao đến siêu lạnh — chọn giải pháp nhãn theo môi trường vận hành.",
             "ตั้งแต่ความร้อนสูงไปจนถึงความเย็นจัด — เลือกโซลูชันฉลากตามสภาพแวดล้อมการใช้งาน"),
        sol_cards)
    # 2) Application Notes (industries now live in the Product nav dropdown, so
    #    the Solutions page carries the environment solutions + the notes only).
    #    A small search box helps visitors filter the notes as the list grows.
    search_ic=('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
               'stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/>'
               '<path d="m21 21-4.3-4.3"/></svg>')
    search_box=('<div class="ansearch"><span class="ansearch-ic">%s</span>'
                '<input id="anq" type="search" autocomplete="off" placeholder="%s" '
                'oninput="etaNoteFilter(this.value)"></div>')%(
        search_ic, P(lang,"Search application notes (industry, product, keyword)…","搜索应用笔记（行业、产品、关键词）…",
                        "Tìm ghi chú ứng dụng (ngành, sản phẩm, từ khóa)…","ค้นหาบันทึกการใช้งาน (อุตสาหกรรม ผลิตภัณฑ์ คำสำคัญ)…"))
    nohit=('<div class="annohit" id="annohit">%s</div>')%(
        P(lang,"No matching application notes.","未找到匹配的应用笔记","Không tìm thấy ghi chú ứng dụng phù hợp.","ไม่พบบันทึกการใช้งานที่ตรงกัน"))
    filter_js=('<script>function etaNoteFilter(q){q=(q||"").trim().toLowerCase();'
               'var g=document.getElementById("angrid"),n=0;'
               'g.querySelectorAll(".appcard").forEach(function(c){'
               'var m=(c.getAttribute("data-txt")||"").indexOf(q)>=0;'
               'c.style.display=m?"":"none";if(m)n++;});'
               'var nh=document.getElementById("annohit");if(nh)nh.style.display=n?"none":"block";}</script>')
    # NB: keep sol_section OUT of this %-format — its image URLs contain %20.
    body=sol_section+(
          '<section class="blk"><div class="wrap"><div class="eyebrow">%s</div><h2>%s</h2>'
          '%s<div class="appnotesgrid" id="angrid">%s</div>%s%s</div></section>'
          '<div class="wrap">%s</div>')%(
        P(lang,"APPLICATION NOTES","应用笔记","GHI CHÚ ỨNG DỤNG","บันทึกการใช้งาน"),
        P(lang,"Application Notes","应用笔记","Ghi chú ứng dụng","บันทึกการใช้งาน"),
        search_box, note_cards, nohit, filter_js, cta2(lang,"applications"))
    # hero: Home-page-style hero (same light look, existing slogan) with a rotating
    # window cycling the operating-condition photos (heat / cold / chemical / sterilization)
    hero=solutions_hero(lang)
    body=home_trustbar(lang)+body   # 20-year trust bar under the hero
    crumb=[(P(lang,"Home","首页","Trang chủ","หน้าแรก"),"/"),(P(lang,"Solutions","方案","Giải pháp","โซลูชัน"),"/applications/")]
    write(lang,"/applications/",page(lang,"/applications/",
        P(lang,"Solutions | ETIA","方案 | ETIA","Giải pháp | ETIA","โซลูชัน | ETIA"),
        P(lang,"Choose a label solution by operating environment and browse real-world application notes — heat, cold and more.",
             "按使用环境选择标签方案，并查看真实应用笔记 —— 高温、低温与更多。",
             "Chọn giải pháp nhãn theo môi trường vận hành và xem các ghi chú ứng dụng thực tế — nhiệt, lạnh và hơn thế.",
             "เลือกโซลูชันฉลากตามสภาพแวดล้อมการใช้งาน และดูบันทึกการใช้งานจริง — ร้อน เย็น และอื่นๆ"),
        P(lang,"Solutions","方案","Giải pháp","โซลูชัน"), "",
        body, crumb, active="applications", trust=False, hero=hero, langs=NAV_PILLAR_LANGS))
    if lang=="en": track("/applications/","industries")

def build_insights(lang):
    zh=(lang=="zh")
    items=[
      (("从应用出发，而非从目录出发" if zh else "Start from the application, not the catalog"),
       ("选对标签始于工艺、表面、温度、化学环境与打印方式，而不是默认参数最高的型号。" if zh
        else "The right label starts with the process, surface, temperature, chemistry and print method — not a default top-spec model.")),
      (("应用温度 vs 峰值温度" if zh else "Application temperature vs. peak temperature"),
       ("短时峰值温度不等于长期耐温；区分二者可避免现场失效。" if zh
        else "A short-term peak rating is not a continuous service rating; separating them prevents field failures.")),
      (("整体结构决定成败" if zh else "The whole construction matters"),
       ("面材、胶粘剂、涂层、碳带与被贴表面共同决定标签能否存活，而非仅看面材。" if zh
        else "Face material, adhesive, topcoat, ribbon and surface together decide whether a label survives — not the face alone.")),
      (("回流焊、清洗与化学暴露" if zh else "Reflow, wash and chemical exposure"),
       ("焊接前贴附的标签，需在高温、助焊剂、溶剂与多次清洗后仍保持清晰可读。" if zh
        else "Labels applied before soldering must stay readable through heat, flux, solvents and repeated washes.")),
    ]
    cards="".join('<div class="card"><h3>%s</h3><p>%s</p></div>'%(esc(t),esc(d)) for t,d in items)
    body=('<section class="blk"><div class="wrap"><div class="grid">%s</div></div></section>'
          '<section class="blk"><div class="wrap"><div class="verify">%s</div></div></section>'
          '<div class="wrap">%s</div>')%(cards,
        ("更多应用笔记与选型参考陆续发布；需要具体型号资料请联系 ETIA。" if zh
         else "More application notes and selection references are being published; contact ETIA for model-specific data."),
        cta2(lang,"insights"))
    crumb=[("Home","/"),("Insights","/insights/")]
    write(lang,"/insights/",page(lang,"/insights/",
        ("洞察 | ETIA" if zh else "Insights | ETIA"),
        ("应用优先选型、温度读法、构造原理与工艺暴露 —— ETIA 标签应用知识。" if zh
         else "Application-first selection, reading temperatures, construction and process exposure — ETIA label application knowledge."),
        ("洞察" if zh else "Insights"), "",
        body, crumb, active="insights", hero=section_hero(lang, 2)))
    if lang=="en": track("/insights/","core")

LEGAL_UPDATED=("2026年7月16日","16 July 2026")

def _legal_page(lang, path, title_en, title_zh, desc_en, desc_zh, secs_en, secs_zh):
    """General website legal template (to be reviewed by the client's legal counsel)."""
    zh=(lang=="zh")
    secs=secs_zh if zh else secs_en
    body_secs="".join('<section class="blk"><div class="wrap"><h2>%s</h2>%s</div></section>'
                      %(esc(h),"".join('<p style="color:var(--mut);max-width:64em;margin-bottom:12px">%s</p>'%esc(p) for p in ps))
                      for h,ps in secs)
    upd='<div class="wrap"><p style="color:var(--faint);font-size:13px;margin:6px 0 0">%s %s</p></div>'%(
        ("最后更新：" if zh else "Last updated:"), LEGAL_UPDATED[0 if zh else 1])
    body=upd+body_secs+('<div class="wrap">%s</div>'%cta(lang))
    crumb=[("Home","/"),((title_zh if zh else title_en),path)]
    write(lang,path,page(lang,path,(title_zh if zh else title_en)+" | ETIA",
        (desc_zh if zh else desc_en),(title_zh if zh else title_en),"",body,crumb,active="",trust=False))
    if lang=="en": track(path,"core")

def build_legal(lang):
    CONTACT="etialabel@etia-tech.com"
    _legal_page(lang,"/privacy/","Privacy Policy","隐私政策",
        "How ETIA collects, uses and protects information submitted through this website.",
        "ETIA 如何收集、使用并保护通过本网站提交的信息。",
        [("Introduction",["ETIA (\"we\", \"us\") respects your privacy. This Privacy Policy explains what information we collect through this website, how we use it, and the choices you have. It applies to this website only."]),
         ("Information We Collect",["Information you provide: when you submit an enquiry, request a sample or contact us, we collect the details you enter — such as your name, company, phone number, email address and the content of your message.",
                                    "Information collected automatically: like most websites, we may collect technical data such as IP address, browser type, device information and pages visited, through cookies and similar technologies."]),
         ("How We Use Information",["We use the information to respond to your enquiries, provide samples, quotations and application support, operate and improve the website, and meet legal or regulatory obligations."]),
         ("Cookies",["This website uses cookies and similar technologies. Please see our Cookie Policy for details on the cookies we use and how to manage them."]),
         ("Sharing of Information",["We do not sell your personal information. We may share it with affiliated companies and trusted service providers who help us respond to your enquiry or operate the website, and where required by law."]),
         ("Data Retention & Security",["We retain personal information only as long as necessary for the purposes described above or as required by law, and we apply reasonable technical and organisational measures to protect it."]),
         ("Your Rights",["Subject to applicable law, you may request access to, correction of, or deletion of your personal information. To make a request, contact us at "+CONTACT+"."]),
         ("International Transfers",["ETIA operates in several countries. Your information may be processed in the countries where we or our service providers operate, with appropriate safeguards."]),
         ("Changes to This Policy",["We may update this Privacy Policy from time to time. The \"Last updated\" date shows when it was last revised."]),
         ("Contact Us",["For any privacy question or request, contact us at "+CONTACT+"."])],
        [("引言",["ETIA（\"我们\"）尊重您的隐私。本隐私政策说明我们通过本网站收集哪些信息、如何使用，以及您拥有的选择。本政策仅适用于本网站。"]),
         ("我们收集的信息",["您主动提供的信息：当您提交询价、咨询专家或与我们联系时，我们会收集您填写的内容，例如姓名、公司、电话、邮箱及留言内容。",
                     "自动收集的信息：与大多数网站一样，我们可能通过 Cookie 及类似技术收集技术数据，如 IP 地址、浏览器类型、设备信息及访问页面。"]),
         ("信息的使用",["我们使用这些信息以回复您的询问、提供样品、报价与应用支持，运营并改进本网站，并履行法律或监管义务。"]),
         ("Cookie",["本网站使用 Cookie 及类似技术。有关我们使用的 Cookie 及管理方式，请参见我们的 Cookie 政策。"]),
         ("信息的共享",["我们不会出售您的个人信息。我们可能与关联公司及协助我们回复询问或运营网站的可信服务商共享信息，或在法律要求时共享。"]),
         ("信息保留与安全",["我们仅在实现上述目的所需或法律要求的期限内保留个人信息，并采取合理的技术与管理措施加以保护。"]),
         ("您的权利",["在适用法律范围内，您可以请求访问、更正或删除您的个人信息。如需提出请求，请通过 "+CONTACT+" 与我们联系。"]),
         ("跨境传输",["ETIA 在多个国家运营。您的信息可能在我们或服务商运营的国家处理，并采取适当的保护措施。"]),
         ("政策变更",["我们可能会不时更新本隐私政策。\"最后更新\"日期显示其最近修订时间。"]),
         ("联系我们",["如有任何隐私问题或请求，请通过 "+CONTACT+" 与我们联系。"])])
    _legal_page(lang,"/cookies/","Cookie Policy","Cookie 政策",
        "How this website uses cookies and how you can manage them.",
        "本网站如何使用 Cookie 以及您如何管理它们。",
        [("What Are Cookies",["Cookies are small text files placed on your device when you visit a website. They help the site function and provide information to site operators."]),
         ("How We Use Cookies",["Essential cookies: needed for the website to function correctly.",
                                "Analytics and preference cookies: help us understand how the website is used and remember your preferences, so we can improve it."]),
         ("Managing Cookies",["You can control or delete cookies through your browser settings. Blocking some cookies may affect how the website works."]),
         ("Changes & Contact",["We may update this Cookie Policy from time to time. For questions, contact "+CONTACT+"."])],
        [("什么是 Cookie",["Cookie 是您访问网站时存放在您设备上的小型文本文件，用于帮助网站运行并向网站运营者提供信息。"]),
         ("我们如何使用 Cookie",["必要 Cookie：网站正常运行所必需。",
                          "分析与偏好 Cookie：帮助我们了解网站的使用情况并记住您的偏好，以便改进网站。"]),
         ("管理 Cookie",["您可以通过浏览器设置控制或删除 Cookie。屏蔽部分 Cookie 可能影响网站的使用。"]),
         ("变更与联系",["我们可能会不时更新本 Cookie 政策。如有疑问，请联系 "+CONTACT+"。"])])
    _legal_page(lang,"/terms/","Terms of Use","使用条款",
        "The terms that govern your use of the ETIA website.",
        "约束您使用 ETIA 网站的条款。",
        [("Acceptance of Terms",["By accessing or using this website, you agree to these Terms of Use. If you do not agree, please do not use the website."]),
         ("Use of the Website",["You agree to use this website only for lawful purposes and not in any way that could damage, disable or impair the website or interfere with others' use of it."]),
         ("Intellectual Property",["Unless otherwise stated, the content on this website — including text, images, layout and trademarks — is owned by or licensed to ETIA and may not be copied or used without permission."]),
         ("Product Information",["Product descriptions, specifications and temperature figures on this website are indicative and provided for general guidance. They are not a guarantee of performance. Final material data comes from the manufacturer technical data sheet (TDS), and suitability should be confirmed by your own application testing before production."]),
         ("No Warranty & Limitation of Liability",["This website and its content are provided \"as is\" without warranties of any kind. To the extent permitted by law, ETIA is not liable for any loss arising from use of, or reliance on, this website."]),
         ("Third-Party Links",["This website may contain links to third-party sites. We are not responsible for the content or practices of those sites."]),
         ("Changes",["We may update these Terms of Use from time to time. Continued use of the website means you accept the current terms."]),
         ("Contact",["For questions about these terms, contact "+CONTACT+"."])],
        [("条款的接受",["访问或使用本网站即表示您同意本使用条款。若您不同意，请勿使用本网站。"]),
         ("网站的使用",["您同意仅将本网站用于合法目的，不以任何可能损害、瘫痪或削弱网站，或干扰他人使用的方式使用本网站。"]),
         ("知识产权",["除另有说明外，本网站的内容 —— 包括文字、图片、版式与商标 —— 归 ETIA 所有或经授权使用，未经许可不得复制或使用。"]),
         ("产品信息",["本网站的产品描述、规格与温度数据为指示性内容，仅供一般参考，并非性能保证。最终材料数据以原厂技术数据表（TDS）为准，量产前应通过您自身的应用测试确认适用性。"]),
         ("免责声明与责任限制",["本网站及其内容按\"现状\"提供，不作任何形式的保证。在法律允许的范围内，ETIA 不对因使用或依赖本网站而产生的任何损失承担责任。"]),
         ("第三方链接",["本网站可能包含指向第三方网站的链接。我们不对这些网站的内容或做法负责。"]),
         ("变更",["我们可能会不时更新本使用条款。继续使用本网站即表示您接受当前条款。"]),
         ("联系",["如对本条款有疑问，请联系 "+CONTACT+"。"])])

def build_all():
  for lang in HOME_LANGS:   # home is 4-language (en, zh, vi, th)
    build_home(lang)
  for lang in LANGS:        # inner site is en + zh
    # No products/industries hub ("集合页"): browse happens from Home + the
    # Product nav dropdown. /products/ and /industries/ redirect to Home
    # (see write_redirects). Individual product & industry pages remain.
    build_about(lang)
    # legal pages (general website template — client legal counsel should review)
    build_legal(lang)
  for lang in NAV_PILLAR_LANGS:  # Product / Solutions / Service pillars: all 4 languages
    build_contact(lang)  # linked from the hero CTA on every page → must exist in all 4 languages
    build_products_landing(lang)  # nav pillar: Product (mega-menu-style landing)
    build_applications(lang)   # nav pillar: Solutions
    build_service(lang)
    # /insights/ (nav pillar: Insight) is built by gen_news as the Insights article hub

def main():
    clean()
    build_all()
    # NOTE: build_sitemaps() + write_redirects() are called by the orchestrator
    # (build.py) AFTER every sector generator has tracked its URLs, so the sector
    # and Application-Notes pages are included in the sitemap.
    from collections import Counter
    print("HEATPROOF EN canonical URLs:", len(ALL_URLS))
    print(Counter(g for _,g in ALL_URLS))

if __name__ == "__main__":
    main()
