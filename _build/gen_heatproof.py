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
PREFIX = {"en": "", "zh": "/cn"}
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
--serif:'Inter','PingFang SC','Microsoft YaHei','Noto Sans SC','Noto Sans Thai',system-ui,-apple-system,'Segoe UI',sans-serif;
--sans:'Inter','PingFang SC','Microsoft YaHei','Noto Sans SC','Noto Sans Thai',system-ui,-apple-system,'Segoe UI',sans-serif}
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
nav a{font-size:14.5px;font-weight:600;color:var(--ink);white-space:nowrap}
nav a:hover{color:var(--blue)}nav a.on{color:var(--blue)}
nav .lang{font-size:13px;color:var(--faint);border:1px solid var(--line);border-radius:8px;padding:5px 10px}
.langsw{display:inline-flex;gap:2px;margin-left:10px;border:1px solid var(--line);border-radius:9px;padding:2px}
nav .langsw a{display:inline-block;font-size:12px;color:var(--faint);padding:5px 9px;border-radius:7px;font-weight:600}
nav .langsw a.on{color:#fff;background:var(--blue)}
nav .langsw a:hover{color:var(--blue)}nav .langsw a.on:hover{color:#fff}
/* Products mega-menu dropdown (spacious, icon rows, opens leftward to stay on screen) */
nav .nd{position:relative;display:inline-block}
nav .nd::after{content:"";position:absolute;top:100%;left:0;right:0;height:18px}
nav .ndt{display:inline-flex;align-items:center;gap:6px;font-size:14.5px;font-weight:600;color:var(--ink);cursor:pointer}
nav .ndt .caret{font-size:10px;color:var(--faint);transition:.15s}
nav .nd:hover .ndt{color:var(--blue)}nav .nd:hover .ndt .caret{transform:rotate(180deg);color:var(--blue)}
nav .ndm.pm{position:absolute;top:100%;right:0;margin-top:16px;background:#fff;border:1px solid var(--line);
  border-radius:18px;box-shadow:0 26px 70px rgba(20,40,90,.20);display:grid;grid-template-columns:236px 1fr;
  width:760px;max-width:92vw;opacity:0;visibility:hidden;transform:translateY(10px);transition:.16s;z-index:60;overflow:hidden}
nav .nd:hover .ndm.pm{opacity:1;visibility:visible;transform:translateY(0)}
.pm .ndrail{background:var(--bg);border-right:1px solid var(--line);padding:22px 14px}
.pm .ndrail-h{font-size:11px;font-weight:800;letter-spacing:.09em;color:var(--faint);padding:0 14px 14px}
.pm .axbtn{display:block;width:100%;text-align:left;background:none;border:none;font-family:inherit;
  font-size:15px;font-weight:700;color:var(--ink);padding:14px 16px;border-radius:11px;cursor:pointer;white-space:nowrap;transition:.12s}
.pm .axbtn.on,.pm .axbtn:hover{background:#fff;color:var(--blue);box-shadow:0 3px 12px rgba(16,34,58,.08)}
.pm .ndpanels{padding:22px 24px}
.pm .axpanel{grid-template-columns:1fr 1fr;gap:6px 18px;align-content:start}
.pm .axpanel a{display:flex;align-items:center;gap:13px;font-size:14.5px;font-weight:600;color:var(--ink);padding:11px 12px;border-radius:11px;white-space:nowrap}
.pm .axpanel a:hover{background:var(--tint-blue);color:var(--blue);text-decoration:none}
.pm .axi{flex:none;width:38px;height:38px;border-radius:10px;background:var(--mint);color:var(--green-d);display:flex;align-items:center;justify-content:center}
.pm .axi:empty{background:#eaf1ff}
.pm .axi:empty::before{content:"";width:8px;height:8px;border-radius:50%;background:var(--blue)}
.pm .axi svg{width:21px;height:21px}
@media(max-width:900px){nav a:not(.lang){display:none}nav .nd{display:none}}
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
.grid.grid3{grid-template-columns:repeat(3,1fr)}
@media(max-width:900px){.grid.grid3{grid-template-columns:1fr 1fr}}
@media(max-width:560px){.grid.grid3{grid-template-columns:1fr}}
/* industry landing HERO SECTION (label + slogan, banner-ready) */
.indhero{position:relative;background:linear-gradient(120deg,#0c2a63,var(--blue-deep) 55%,#0a1f4a);color:#fff;overflow:hidden;background-size:cover;background-position:center;min-height:380px;display:grid;align-items:center}
.indhero.hasimg::before{content:"";position:absolute;inset:0;background:linear-gradient(115deg,rgba(9,24,58,.90),rgba(9,24,58,.45));z-index:1}
.indhero .wrap{position:relative;z-index:2;padding:44px 24px}
.indhero .eyebrow{color:#9fc0ff}
.indhero h1{color:#fff;font-size:40px;line-height:1.1;margin:12px 0 16px;max-width:16em;font-weight:800}
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
/* brochure / resource cards below the tab module */
.brochures{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.bcard{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:24px 26px;border-radius:14px;color:#fff;background:linear-gradient(120deg,var(--blue-deep),var(--blue));transition:transform .15s,box-shadow .15s}
.bcard:nth-child(2){background:linear-gradient(120deg,#0f3d1f,var(--green-d))}
.bcard:hover{transform:translateY(-3px);box-shadow:0 14px 34px rgba(20,40,90,.18);text-decoration:none}
.bcard .bct h3{font-size:19px;color:#fff;margin-bottom:5px;line-height:1.2}
.bcard .bct p{font-size:13px;color:#e6eefc;line-height:1.45}
.bcard .barr{font-size:26px;color:#fff;flex:none;line-height:1}
@media(max-width:700px){.brochures{grid-template-columns:1fr}}
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
.appmod.svc .apppanel{align-items:start}
.aptext .svc-num{font-size:13px;font-weight:800;letter-spacing:.12em;color:var(--green-d)}
.aptext .svc-num+h3{margin-top:6px}
.aptext .svc-tag{font-size:17px;font-weight:700;color:var(--ink);margin-bottom:16px;max-width:40em}
.aptext .svc-close{font-size:15px;font-weight:800;color:var(--blue);margin-bottom:0}
@media(max-width:820px){.apppanel{grid-template-columns:1fr;gap:20px}.apptab{font-size:13.5px;padding:10px 11px}.apppanel .aptext h3{font-size:22px}}
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
.cta p{color:#d3ddf3;margin:12px auto 20px;max-width:40em}
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
.hero{padding:60px 0 46px}
.hero .eyebrow{margin-bottom:14px}
.hero h1{font-family:var(--serif);font-weight:600;font-size:46px;line-height:1.08;letter-spacing:-.01em;text-wrap:balance;max-width:16em}
.hero .lede{margin-top:18px;color:var(--mut);font-size:19px;max-width:40em}
.hero .btns{margin-top:26px;display:flex;gap:12px;flex-wrap:wrap}
.trustbar{background:linear-gradient(150deg,var(--blue),var(--blue-deep))}
.trustbar .wrap{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;padding:14px 24px}
.trustbar .ti{font-size:13.5px;font-weight:700;color:#fff;display:flex;gap:8px;align-items:center;justify-content:center;text-align:center}
.trustbar .ti::before{content:"✓";color:#8fe063;font-weight:800;flex:none}
.scgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:24px;margin-top:10px}
.sci{border-top:2px solid var(--green);padding-top:14px}
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
.prow .pactions{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.pbtn{display:inline-block;font-size:12px;font-weight:800;letter-spacing:.04em;padding:7px 15px;border-radius:20px;border:1.5px solid var(--line);color:var(--blue-deep);background:#fff}
.pbtn:hover{border-color:var(--blue);color:var(--blue);text-decoration:none}
.pbtn.sample{background:var(--green);border-color:var(--green);color:#fff}
.pbtn.sample:hover{background:var(--green-d);border-color:var(--green-d);color:#fff}
/* product spec table (FLEXcon-style) */
.ptable-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px}
.ptable{width:100%;border-collapse:collapse;font-size:13.5px}
.ptable th{text-align:left;font-size:11px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--faint);padding:12px 14px;border-bottom:2px solid var(--line);white-space:nowrap;background:var(--bg)}
.ptable td{padding:15px 14px;border-bottom:1px solid var(--line);vertical-align:top;color:var(--mut);white-space:nowrap}
.ptable tr:last-child td{border-bottom:none}
.ptable tbody tr:hover{background:#fafbfe}
.ptable .ptd-name{color:var(--blue-deep);font-weight:800;font-size:14.5px;white-space:normal;min-width:220px}
.ptable .ptd-desc{font-weight:400;font-size:12px;color:var(--mut);margin-top:4px;line-height:1.45;max-width:34em;white-space:normal}
.ptable .esd-y{display:inline-block;font-size:11px;font-weight:800;background:#eaf1ff;color:var(--blue);border:1px solid #d6e2fb;border-radius:12px;padding:3px 9px}
.ptable .ptd-act{white-space:normal;min-width:150px}
.ptable .ptd-act .pbtn{margin:0 6px 6px 0}
@media(max-width:820px){.catalog{grid-template-columns:1fr}}
@media(max-width:820px){.two{grid-template-columns:1fr}footer .fg{grid-template-columns:1fr}.pagehead h1{font-size:30px}
.hero h1{font-size:32px}.svcbar .wrap{grid-template-columns:1fr 1fr}.whygrid{grid-template-columns:1fr 1fr}
.split{grid-template-columns:1fr;gap:22px}.split .imgframe{order:-1}.split .txt h2{font-size:25px}
.acgrid{grid-template-columns:1fr 1fr;gap:10px}
.trustbar .wrap{grid-template-columns:1fr 1fr;gap:10px}
.scgrid{grid-template-columns:1fr 1fr;gap:16px}
.fsbox{grid-template-columns:1fr;gap:20px}
.aslide{grid-template-columns:1fr;min-height:0}.aimg{min-height:190px}.aimg .aicon svg{width:60px;height:60px}.acopy{padding:26px 24px}.acopy h3{font-size:22px}.acar-nav{display:none}
.cslide .cap h3{font-size:20px}}
"""

NAV_ITEMS = [("Products", u_products(), "products"),
             ("Application Notes", "/application-notes/", "notes"),
             ("Insights", "/insights/", "insights"),
             ("Service", "/service/", "service")]
NAV_ZH = {"Products":"产品","Application Notes":"应用笔记","Insights":"洞察","Service":"服务"}

# Products mega-menu: 4 axes (Computype-style left rail + right list)
PROD_AXES = [
 ("app","By Industry","按行业",[
   ("Electronics & PCB","电子与PCB","/industries/electronics-pcb/"),
   ("Metals & Ceramics","金属与陶瓷","/industries/steel/"),
   ("Medical & Laboratory","医疗与实验室","/industries/healthcare-life-sciences/"),
   ("Automotive & Tire","汽车与轮胎","/industries/automotive-label-materials/"),
   ("Wire & Cable","电线与电缆","/industries/wire-cable/"),
   ("Outdoor & Energy","户外与能源","/industries/outdoor-energy/"),
 ]),
 ("env","By Environment","按环境",[
   ("Abrasion-Resistant","耐磨","/products/by-environment/"),
   ("Chemical-Resistant","耐化学","/products/by-environment/"),
   ("Corrosion-Resistant","耐腐蚀","/products/by-environment/"),
   ("Dirt-Resistant","抗污","/products/by-environment/"),
   ("Fluid-Resistant","耐液体","/products/by-environment/"),
   ("Heat-Resistant","耐热","/products/by-environment/"),
   ("High-Temperature-Resistant","耐高温","/products/by-environment/"),
   ("Humidity-Resistant","耐潮湿","/products/by-environment/"),
   ("Low-Temperature-Resistant","耐低温","/products/by-environment/"),
   ("Oil-Resistant","耐油污","/products/by-environment/"),
   ("Temperature-Resistant","耐温变","/products/by-environment/"),
   ("UV-Resistant","耐紫外","/products/by-environment/"),
   ("Water-Resistant","耐水","/products/by-environment/"),
   ("Wave-Solder-Resistant","耐波峰焊","/products/by-environment/"),
   ("Weather-Resistant","耐候","/products/by-environment/"),
   ("ESD-Safe","抗静电","/products/by-environment/"),
   ("Laser-Markable","激光打标","/products/by-environment/"),
   ("Sterilization-Resistant","耐灭菌","/products/by-environment/"),
 ]),
 ("feat","By Feature","按特性",[
   ("Tamper-Evident","防拆","/products/by-feature/"),
   ("Removable","可移除","/products/by-feature/"),
 ]),
 ("mat","By Material","按材料",[
   ("Polyimide — Heat-Resistant","聚酰亚胺 · 耐高温","/materials/polyimide-pi-label-materials/"),
 ]),
]

def products_dropdown(lang, linkfn):
    zh = (lang == "zh")
    lab = lambda e, z: z if zh else e
    top = "产品" if zh else "Products"
    rail = ""; panels = ""
    for i, (key, he, hz, items) in enumerate(PROD_AXES):
        on = " on" if i == 0 else ""
        rail += '<button type="button" class="axbtn%s" onmouseover="etaAx(this,\'%s\')"><span class="axc">%s</span></button>' % (
            on, key, esc(lab(he, hz)))
        link_list = ""
        for j, (e, z, u) in enumerate(items):
            ic = INDUSTRY_ICONS[j % len(INDUSTRY_ICONS)] if key == "app" else ""
            link_list += '<a href="%s"><span class="axi">%s</span><span class="axl">%s</span></a>' % (linkfn(u), ic, esc(lab(e, z)))
        panels += '<div class="axpanel" data-ax="%s" style="display:%s">%s</div>' % (key, ("grid" if i == 0 else "none"), link_list)
    return ('<div class="nd"><a class="ndt" href="%s">%s <span class="caret">&#9662;</span></a>'
            '<div class="ndm pm"><div class="ndrail"><div class="ndrail-h">%s</div>%s</div><div class="ndpanels">%s</div></div></div>') % (
        linkfn("/products/"), esc(top), ("产品方案" if zh else "LABEL SOLUTIONS"), rail, panels)

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
    items = ""
    for t, href, key in NAV_ITEMS:
        if key == "products":
            items += products_dropdown(lang, lambda p: L(lang, p))
        else:
            items += '<a href="%s"%s>%s</a>' % (L(lang, href), ' class="on"' if key==active else '', lab(t))
    other = "zh" if lang == "en" else "en"
    other_label = "CN" if lang == "en" else "EN"   # label = the language you switch TO
    return '<nav>%s<a class="lang" href="%s">%s</a></nav>' % (items, L(other, path), other_label)

FOOTER_LINKS = [("Products", u_products()), ("Industries", u_ind_hub()),
                ("Application Notes", "/application-notes/"), ("Service", "/service/"),
                ("About ETIA", "/about/"), ("Contact", "/contact/")]
def footer_html(lang):
    nav = "".join('<li><a href="%s">%s</a></li>' % (L(lang, p), t) for t, p in FOOTER_LINKS)
    legal = "".join('<li><a href="%s">%s</a></li>' % (L(lang, p), t) for t, p in
                    [("Privacy Policy","/privacy/"),("Cookie Policy","/cookies/"),("Terms of Use","/terms/")])
    return """<footer><div class="wrap">
<div class="flogo"><img src="https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com/IMAGO/LOGO/ETIA%%20LOGO.jpg" alt="ETIA Label"></div>
<div class="fg">
<div><h5>Navigation</h5><ul>%s</ul></div>
<div><h5>Legal</h5><ul>%s</ul></div>
<div><h5>Contact</h5><a class="email" href="mailto:label@etia-tech.com">label@etia-tech.com</a><br><br>
Shanghai · Hong Kong · Bangkok · Bac Ninh<br><span style="color:var(--faint)">Supplier &amp; application-support partner — genuine, brand-authorized materials.</span></div>
</div>
<div class="bar"><span>© 2026 ETIA-TECH (ASIA) Co., Limited. All rights reserved.</span><span><a href="%s">Privacy</a> &nbsp; <a href="%s">Cookies</a></span></div>
</div></footer>""" % (nav, legal, L(lang,"/privacy/"), L(lang,"/cookies/"))

TRUST_TITLES = {
 "en":["100% Quality Inspection","Application-Driven Solutions","Flexible Supply","Responsive Application Support"],
 "zh":["100% 质量检测","应用驱动方案","柔性供应","及时应用支持"],
}
def trust_bar(lang):
    items="".join('<div class="ti">%s</div>'%esc(t) for t in TRUST_TITLES.get(lang, TRUST_TITLES["en"]))
    return '<section class="trustbar"><div class="wrap">%s</div></section>' % items

def cta(lang):
    if lang == "zh":
        return """<div class="cta"><div class="ic">⚡</div><h3>始于应用。终于选对材料。</h3>
<p>告知表面、温度、化学环境与打印方式,我们推荐材料并安排样品验证。</p>
<div class="btns"><a class="btn pri" href="%s">申请样品</a><a class="btn on-dark" href="%s">咨询工程师</a></div></div>""" % (L(lang,"/contact/"), L(lang,"/contact/"))
    return """<div class="cta"><div class="ic">⚡</div><h3>Start with the Application. Finish with the Right Material.</h3>
<p>Tell us the surface, temperature, chemistry and print method — we'll recommend the material and arrange samples.</p>
<div class="btns"><a class="btn pri" href="%s">Request a Sample</a><a class="btn on-dark" href="%s">Talk to an Engineer</a></div></div>""" % (L(lang,"/contact/"), L(lang,"/contact/"))

def page(lang, path, title, desc, h1, lede, body, crumb, schema_extra=None, active="", trust=True, hero=None):
    canonical = SITE + PREFIX[lang] + path
    sch = [breadcrumb_jsonld(crumb, lang)] + (schema_extra or [])
    schema_js = "".join('<script type="application/ld+json">%s</script>' % json.dumps(s, ensure_ascii=False) for s in sch)
    cr = ' &rsaquo; '.join((('<a href="%s">%s</a>' % (L(lang,p), esc(n))) if p and i < len(crumb)-1 else '<b>%s</b>' % esc(n))
                           for i,(n,p) in enumerate(crumb))
    lede_html = ('<p class="lede">%s</p>' % lede) if lede else ""
    # hero (when given) replaces the plain pagehead block — used for the industry
    # landing HERO SECTION (label + slogan, banner-ready).
    head_block = hero if hero else ('<div class="wrap"><div class="pagehead"><h1>%s</h1>%s</div></div>' % (esc(h1), lede_html))
    return """<!doctype html><html lang="%s"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title><meta name="description" content="%s">
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
<script>function etaAx(b,a){var m=b.closest('.ndm');m.querySelectorAll('.axbtn').forEach(function(x){x.classList.toggle('on',x===b);});m.querySelectorAll('.axpanel').forEach(function(p){p.style.display=(p.getAttribute('data-ax')===a)?'grid':'none';});}</script>
</body></html>""" % (lang, esc(title), esc(desc), canonical, hreflang_block(path), esc(title), CSS, schema_js,
     L(lang,"/"), nav_html(lang, active, path), cr, head_block, (trust_bar(lang) if trust else ""), body, footer_html(lang))

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
    return ("/cn"+path) if lang=="zh" else path

def home_switcher(active):
    out=""
    for lg in HOME_LANGS:
        href = "/" if lg=="en" else HL_PREFIX[lg]+"/"
        out += '<a href="%s"%s>%s</a>' % (href, ' class="on"' if lg==active else '', esc(HOME_I18N["lang_name"][lg]))
    return '<span class="langsw">%s</span>' % out

def home_nav(lang):
    T=HOME_I18N[lang]
    lf=lambda p: home_hlink(lang,p)
    hrefs=["/application-notes/","/insights/","/service/"]
    prod=products_dropdown(lang, lf)
    links="".join('<a href="%s">%s</a>'%(lf(h),esc(lbl)) for h,lbl in zip(hrefs,T["nav"][1:]))
    return '<nav>%s%s%s</nav>' % (prod, links, home_switcher(lang))

def home_footer(lang):
    T=HOME_I18N[lang]; nh,lh,ch=T["footer_heads"]
    navl="".join('<li><a href="%s">%s</a></li>'%(home_hlink(lang,h),esc(l)) for h,l in
                 zip(["/products/","/industries/","/insights/","/service/"],T["nav"][:4]))
    legal="".join('<li><a href="%s">%s</a></li>'%(home_hlink(lang,p),t) for p,t in
                  [("/privacy/","Privacy Policy"),("/cookies/","Cookie Policy"),("/terms/","Terms of Use")])
    return ('<footer><div class="wrap"><div class="flogo"><img src="https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com/IMAGO/LOGO/ETIA%%20LOGO.jpg" alt="ETIA Label"></div>'
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
    why_html="".join('<div class="why"><div class="ic">%s</div><div class="txt"><b>%s</b><p class="wexp">%s</p></div></div>'%(
        WHY_ICONS[k%len(WHY_ICONS)],esc(head),esc(text)) for k,(head,text) in enumerate(T["why"]))
    why_close=('<p class="whyclose">%s</p>'%esc(T["why_close"])) if T.get("why_close") else ""
    # Explore by Application — six cards (image on top, copy below; all six visible, animate on hover)
    cards=""
    for k,f in enumerate(T["focus"]):
        img_html=('<img src="%s" alt="%s" loading="lazy" onerror="this.remove()">'%(esc(f["img"]),esc(f["name"]))) if f.get("img") else ""
        cards+=('<a class="acard" href="%s"><div class="acard-img g%d">%s<span class="aicon">%s</span></div>'
                '<div class="acard-body"><h3 class="indname">%s</h3><p>%s</p>'
                '<div class="acard-go">%s →</div></div></a>')%(
            home_hlink(lang,FOCUS_URLS[k]), k%6, img_html, INDUSTRY_ICONS[k%len(INDUSTRY_ICONS)],
            esc(f["name"]), esc(f["desc"]), esc(T["explore"]))
    app_grid='<div class="acgrid">%s</div>'%cards
    # Most Popular Products — same card pattern (image top), application name as title, model small
    PROD_ICON=[1,2,0,3,2,4]
    pcards=""
    for k,pr in enumerate(T.get("products",[])):
        gi=PROD_ICON[k%len(PROD_ICON)]
        pimg=('<img src="%s" alt="%s" loading="lazy" onerror="this.remove()">'%(esc(pr["img"]),esc(pr["name"]))) if pr.get("img") else ""
        pcards+=('<a class="acard pcard" href="%s"><div class="acard-img g%d">%s<span class="aicon">%s</span></div>'
                 '<div class="acard-body"><h3>%s</h3><div class="pmodel">%s</div><div class="pcode">%s</div>'
                 '<div class="acard-go">%s →</div></div></a>')%(
            home_hlink(lang,"/contact/"), gi, pimg, INDUSTRY_ICONS[gi%len(INDUSTRY_ICONS)],
            esc(pr["name"]), esc(pr["model"]), esc(pr.get("code","")), esc(T.get("prod_cta","Request Sample")))
    prod_section=('<section class="blk" style="background:var(--tint-green)"><div class="wrap">'
                  '<div class="eyebrow">%s</div><h2>%s</h2><div class="sub">%s</div>'
                  '<div class="acgrid acgrid5">%s</div></div></section>')%(
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
    final_cta=('<div class="wrap"><div class="cta"><div class="ic">⚡</div><h3>%s</h3><p>%s</p>'
               '<div class="btns"><a class="btn pri" href="%s">%s</a><a class="btn on-dark" href="%s">%s</a></div></div></div>')%(
        esc(T["fcta_title"]),esc(T["fcta_para"]),home_hlink(lang,"/contact/"),esc(T["fcta_b1"]),home_hlink(lang,"/contact/"),esc(T["fcta_b2"]))
    trust_html=trust_bar(lang)
    sc_items="".join('<div class="sci"><b>%s</b><p>%s</p></div>'%(esc(it["title"]),esc(it["desc"])) for it in T.get("svc",[]))
    sc_section=('<section class="blk"><div class="wrap"><div class="eyebrow">%s</div><h2>%s</h2>'
                '<div class="scgrid">%s</div></div></section>')%(
        esc(T.get("sc_eyebrow","SERVICE COMMITMENT")),esc(T.get("sc_title","Our Service Commitment")),sc_items)
    body="""<section class="hero"><div class="wrap">
<div class="eyebrow">%s</div><h1 class="serif">%s</h1>
<p class="lede" style="color:var(--ink);font-size:20px;font-weight:600;max-width:32em">%s</p>
<p class="lede">%s</p>
<div class="btns"><a class="btn pri" href="#applications">%s</a><a class="btn sec" href="%s">%s</a></div></div></section>
%s
<section class="blk" style="background:var(--tint-green)"><div class="wrap"><div class="eyebrow">%s</div><h2>%s</h2><div class="sub">%s</div><div class="whygrid">%s</div>%s</div></section>
<section class="blk" id="applications" style="background:var(--tint-blue)"><div class="wrap"><div class="eyebrow">%s</div><h2>%s</h2><div class="sub">%s</div>%s
<div style="margin-top:20px"><a class="btn sec" href="%s">%s →</a></div></div></section>
%s
%s
%s""" % (
        esc(T["hero_eyebrow"]),esc(T["hero_h1"]),esc(T["hero_line"]),esc(T["hero_para"]),esc(T["hero_b1"]),home_hlink(lang,"/contact/"),esc(T["hero_b2"]),
        trust_html,
        esc(T["why_eyebrow"]),esc(T["why_head"]),esc(T["why_intro"]),why_html,why_close,
        esc(T["appc_eyebrow"]),esc(T["appc_title"]),esc(T["appc_sub"]),app_grid,home_hlink(lang,"/industries/"),esc(T["appc_viewall"]),
        prod_section,
        sc_section,
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
<header><div class="wrap"><a class="logo" href="%s"><img src="https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com/IMAGO/LOGO/ETIA%%20LOGO.jpg" alt="ETIA Label"></a>%s</div></header>
%s
%s
<script>function etaAx(b,a){var m=b.closest('.ndm');m.querySelectorAll('.axbtn').forEach(function(x){x.classList.toggle('on',x===b);});m.querySelectorAll('.axpanel').forEach(function(p){p.style.display=(p.getAttribute('data-ax')===a)?'grid':'none';});}
function etaSlide(d){var c=document.getElementById('acar');if(c)c.scrollBy({left:d*c.clientWidth,behavior:'smooth'});}
function etaSample(e){e.preventDefault();var g=function(i){var el=document.getElementById(i);return el?el.value:'';};
var b='Email: '+g('fs-email')+'%%0D%%0APhone: '+g('fs-phone')+'%%0D%%0AAddress: '+g('fs-addr')+'%%0D%%0A%%0D%%0APlease send free samples.';
window.location.href='mailto:label@etia-tech.com?subject=Free%%20Sample%%20Request&body='+b;return false;}</script>
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
    for d in ["products","industries","applications","application-notes","technical-resources","about","contact","zh","cn",
              "materials","brands","insights","service","support","company","privacy","cookies","terms",
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

SERVICE_OFFICES=[
  ("Shanghai","上海","+86 151 2119 7091 · 400 990 8448"),
  ("Hong Kong","香港","label@etia-tech.com"),
  ("Bangkok","曼谷","+66 811 746 947"),
  ("Bac Ninh","北宁","+84 344 590 091"),
]
# Future: 4 service images (one per commitment). Fill with clean COS URLs when ready.
SERVICE_IMGS=["","","",""]
SERVICE_INTRO=(
  "From material quality and application validation to flexible converting and ongoing support, ETIA helps customers reduce risk and achieve reliable labeling performance throughout the entire project lifecycle.",
  "从材料质量、应用验证，到柔性加工与持续支持，ETIA 在项目全流程中帮助客户降低导入风险，确保标签应用稳定可靠。")
# num, title(en,zh), tagline(en,zh), body[(en,zh)...], close(en,zh)
SERVICE_COMMIT=[
 {"num":"01","title":("100% Quality Inspection","100% 质量检验"),
  "tag":("Quality is verified at every stage.","每一个环节，都经过质量验证。"),
  "body":[("Reliable label performance begins with consistent material quality. Every incoming material is inspected before entering production, and finished products are checked before shipment.",
           "稳定的标签表现，始于稳定的材料质量。所有来料在进入生产前均经过检验，成品在出库前再次进行质量确认。"),
          ("Supported by our in-house laboratory, production verification, retained samples, and traceability procedures, we help ensure that every batch meets the required quality and application standards.",
           "依托自有实验室、生产过程验证、出库留样及追溯机制，我们确保每一批材料符合相应的质量和应用要求。")],
  "close":("Every material. Every batch. Every delivery.","每一种材料，每一个批次，每一次交付。")},
 {"num":"02","title":("Application-Driven Solutions","应用驱动方案"),
  "tag":("Every application is unique.","每一种应用都不一样。"),
  "body":[("Before recommending a material, we evaluate your surface, process, environment, printing method, and performance requirements.",
           "在推荐材料之前，我们会充分评估粘贴表面、生产工艺、使用环境、打印方式及性能要求。"),
          ("Whenever possible, materials are validated in our laboratory under simulated production conditions, helping reduce implementation risk before full-scale production.",
           "在条件允许的情况下，我们会在模拟实际生产工况下进行实验室验证，帮助客户在正式量产导入前降低应用风险。")],
  "close":("We don't guess. We validate.","我们不凭猜测，依靠验证。")},
 {"num":"03","title":("Flexible Supply","柔性供应"),
  "tag":("Materials supplied in the format your production needs.","按照您的生产需求，提供合适的材料规格。"),
  "body":[("Specialized applications often require more than standard material sizes and fixed order quantities. With in-house slitting, die-cutting, and converting equipment, we can adapt materials to different production and processing requirements.",
           "专业应用往往需要不同于标准产品的尺寸、规格和采购数量。依托自有分切、模切及加工设备，我们能够根据客户的生产与加工需求调整材料交付形式。"),
          ("We support multiple materials, custom widths and sizes, varied specifications, samples, small-batch orders, and volume production.",
           "我们支持多种材料、定制宽度与尺寸、多种规格、样品、小批量订单及批量生产。")],
  "close":("Flexible materials. Flexible formats. Flexible quantities.","材料灵活、规格灵活、数量灵活。")},
 {"num":"04","title":("Responsive Application Support","快速应用支持"),
  "tag":("Supporting your application at every stage.","在应用的每一个阶段，为您提供支持。"),
  "body":[("Our support continues from initial material selection and sample evaluation through printing, converting, implementation, and full-scale production.",
           "我们的支持贯穿材料选型、样品评估、打印、加工、导入及正式量产的全过程。"),
          ("When process conditions change or unexpected application issues arise, our team responds quickly with practical support to help minimize disruption and maintain consistent labeling performance.",
           "当工艺条件发生变化，或生产过程中出现新的应用问题时，我们会快速响应，提供切实可行的支持，帮助减少生产中断并保持标签性能稳定。")],
  "close":("Before delivery, during production, and beyond.","交付之前、生产之中，以及长期应用之后。")},
]

def build_service(lang):
    zh=(lang=="zh")
    j=1 if zh else 0
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
               "window.location.href='mailto:label@etia-tech.com?subject='+encodeURIComponent('Website enquiry')+'&body='+encodeURIComponent(b);return false;}</script>")
    commit_sec=('<section class="blk"><div class="wrap"><h2>%s</h2>'
                '<p class="lede" style="max-width:64em;margin-bottom:26px">%s</p>'
                '<div class="appmod svc">'
                '<div class="apptabsrow"><button class="apparrow" onclick="etaScroll(this,-1)" aria-label="prev">&lsaquo;</button>'
                '<div class="apptabs">%s</div>'
                '<button class="apparrow" onclick="etaScroll(this,1)" aria-label="next">&rsaquo;</button></div>'
                '<div class="apppanels">%s</div></div></div></section>')%(
        ("我们的服务承诺" if zh else "Our Service Commitment"), esc(SERVICE_INTRO[j]), tabs, panels)
    # --- contact form with phone ---
    ph=lambda p: '<input name="%s" placeholder="%s"%s>'%p
    fields=('<div class="cfrow"><input name="name" placeholder="%s" required><input name="company" placeholder="%s"></div>'
            '<div class="cfrow"><input name="phone" placeholder="%s" required><input name="email" type="email" placeholder="%s"></div>'
            '<textarea name="msg" rows="4" placeholder="%s"></textarea>'
            '<button class="btn pri" type="submit">%s</button>')%(
        ("姓名 *" if zh else "Name *"),("公司" if zh else "Company"),
        ("电话 *" if zh else "Phone *"),("邮箱" if zh else "Email"),
        ("请描述您的应用：表面、温度、化学环境、打印方式与标签尺寸" if zh
         else "Describe your application: surface, temperature, chemistry, print method and label size"),
        ("提交" if zh else "Send Enquiry"))
    phones="".join('<div class="cph"><b>%s</b><span>%s</span></div>'%(esc(z if zh else e),esc(c)) for e,z,c in SERVICE_OFFICES)
    form_sec=('<section class="blk" style="background:var(--tint-blue)"><div class="wrap">'
              '<h2>%s</h2><div class="sub">%s</div>'
              '<div class="ctwo"><form class="cform" onsubmit="return etaMail(this)">%s</form>'
              '<div class="cphones">%s</div></div></div></section>')%(
        ("联系我们" if zh else "Get in Touch"),
        ("留下电话与应用需求，我们尽快回复并安排样品。" if zh
         else "Leave your phone and application — we'll reply quickly and arrange samples."),
        fields, phones)
    body=commit_sec+form_sec+('<div class="wrap">%s</div>'%cta(lang))+tabscript
    crumb=[("Home","/"),("Service","/service/")]
    write(lang,"/service/",page(lang,"/service/",
        ("服务 | ETIA" if zh else "Service | ETIA"),
        ("100% 质量检测、应用驱动选型、柔性供应与及时应用支持 —— ETIA 服务承诺。" if zh
         else "100% quality inspection, application-driven selection, flexible supply and responsive support — the ETIA service commitment."),
        ("服务" if zh else "Service"),
        ("从选型、样品与检测，到柔性供应与长期应用支持，我们贯穿应用全过程。" if zh
         else "From selection, samples and testing to flexible supply and long-term support — across the full application."),
        body, crumb, active="service", trust=False))
    if lang=="en": track("/service/","core")

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
        cta(lang))
    crumb=[("Home","/"),("Insights","/insights/")]
    write(lang,"/insights/",page(lang,"/insights/",
        ("洞察 | ETIA" if zh else "Insights | ETIA"),
        ("应用优先选型、温度读法、构造原理与工艺暴露 —— ETIA 标签应用知识。" if zh
         else "Application-first selection, reading temperatures, construction and process exposure — ETIA label application knowledge."),
        ("洞察" if zh else "Insights"),
        ("关于严苛工业标签的应用知识 —— 帮助您在量产前选对材料。" if zh
         else "Application knowledge for demanding industrial labels — to choose the right material before production."),
        body, crumb, active="insights"))
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
    CONTACT="label@etia-tech.com"
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
         ("我们收集的信息",["您主动提供的信息：当您提交询价、申请样品或与我们联系时，我们会收集您填写的内容，例如姓名、公司、电话、邮箱及留言内容。",
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
    build_products_hub(lang)
    for pid in PATHS: build_process_line(lang, pid)
    for pid in PRODUCTS: build_product(lang, PRODUCTS[pid])
    build_industries_hub(lang)
    for iid in INDUSTRIES: build_industry(lang, iid)
    for a in APPS: build_application(lang, a)
    build_outdoor_energy(lang)
    build_about(lang)
    build_contact(lang)
    build_insights(lang)
    build_service(lang)
    # legal pages (general website template — client legal counsel should review)
    build_legal(lang)

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
