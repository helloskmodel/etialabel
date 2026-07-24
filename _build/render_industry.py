#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Data-driven industry landing-page generator (v2 architecture).

Reads _build/data/industries/<slug>.json and renders the confirmed industry
page structure:  Hero -> Overview -> FlexCon Bar (performance tiers) ->
tier intro -> small product cards -> (important products) product Landing.

Content lives in the JSON (per-language fields); this file holds only template
+ logic. Never invents copy — missing language falls back to the source (zh).
"""
import json, os, html

BUILD = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BUILD)
IND_DIR = os.path.join(BUILD, "data", "industries")

LANG_PREFIX = {"en": "", "zh": "zh", "th": "th", "vi": "vi"}
SOURCE_LANG = "zh"   # briefs are authored in Chinese; fall back to it when a
                     # target language is not yet translated.

# ---- per-language UI chrome (structural strings, not client copy) ----
UI = {
  "zh": {
    "nav": [("产品", "/zh/products/"), ("按行业", "/zh/products/by-industry/"),
            ("按环境", "/zh/products/by-environment/"), ("按材料", "/zh/products/by-material/"),
            ("新闻", "/zh/news/")],
    "samples": "申请样品", "home": "首页", "products": "产品", "by_industry": "按行业",
    "part1": "第一部分 · 行业概述", "overview": "行业概述",
    "products_eyebrow": "产品", "select_suffix": "选型",
    "go": "查看产品 →", "consult": "咨询选型（无单独页）",
    "cta_h": "选型拿不准？告诉我们工况，我们匹配材料",
    "cta_p": "申请样品", "cta_g": "咨询工程师",
  },
}

def L(node, lang):
    """Pick a language value from a {lang: value} dict, fallback to source."""
    if not isinstance(node, dict):
        return node or ""
    v = node.get(lang)
    if v:  # non-empty string or non-empty list
        return v
    return node.get(SOURCE_LANG) or ""

def esc(s):
    return html.escape(str(s or ""), quote=True)

CSS = """
:root{--blue:#1A56DB;--deep:#143C96;--green:#41A62A;--green-d:#358B22;--bg:#fff;--surface:#fff;--surface2:#f5f8fd;--tint:#eef3fc;--ink:#17203a;--muted:#5a6884;--faint:#8a97b3;--border:#dbe3f1;--sans:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
@media (prefers-color-scheme:dark){:root{--bg:#0d1424;--surface:#151f36;--surface2:#101a30;--tint:#152341;--ink:#e7edfa;--muted:#9aa8c6;--faint:#6f7ea0;--border:#28344f}}
:root[data-theme="dark"]{--bg:#0d1424;--surface:#151f36;--surface2:#101a30;--tint:#152341;--ink:#e7edfa;--muted:#9aa8c6;--faint:#6f7ea0;--border:#28344f}
:root[data-theme="light"]{--bg:#fff;--surface:#fff;--surface2:#f5f8fd;--tint:#eef3fc;--ink:#17203a;--muted:#5a6884;--faint:#8a97b3;--border:#dbe3f1}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);line-height:1.6;-webkit-font-smoothing:antialiased}
.wrap{max-width:1080px;margin:0 auto;padding:0 22px}
header{background:linear-gradient(90deg,var(--deep),var(--blue));position:sticky;top:0;z-index:20}
header .wrap{display:flex;align-items:center;gap:20px;height:58px}
.logo{font-weight:800;font-size:18px;letter-spacing:.5px;text-decoration:none}.logo .a{color:#8fe36a}.logo .b{color:#dbe6ff}
.nav{display:flex;gap:2px;margin-left:4px}
.nav a{color:#e5edff;text-decoration:none;font-size:13px;font-weight:600;padding:7px 10px;border-radius:7px}
.nav a:hover{background:rgba(255,255,255,.15)}
.hcta{margin-left:auto;background:var(--green);color:#fff!important;padding:8px 14px!important;font-weight:700;border-radius:7px;text-decoration:none}
.crumb{font-size:12px;color:var(--muted);padding:12px 0}.crumb a{color:var(--blue);text-decoration:none}
.hero{position:relative;border-radius:16px;overflow:hidden;margin-top:4px;min-height:300px;display:flex;align-items:flex-end;background:#12224b}
.hero img.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.55}
.hero::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(9,20,48,.92),rgba(20,60,150,.55) 70%,transparent)}
.hero .in{position:relative;padding:34px 40px;max-width:640px;color:#fff}
.hero .eye{font-size:12px;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:#8fe36a}
.hero h1{font-size:clamp(26px,4.6vw,40px);margin:10px 0 8px;line-height:1.12;text-wrap:balance}
.hero p{font-size:16px;color:#e2ebff;margin:0}
section{padding:36px 0}
.eyebrow{font-size:12px;font-weight:800;letter-spacing:1.4px;text-transform:uppercase;color:var(--blue)}
h2{font-size:24px;margin:8px 0 14px;letter-spacing:-.3px}
.lead{color:var(--muted);font-size:15.5px;max-width:74ch}.lead p{margin:0 0 12px}
.fc{margin-top:18px}
.fcrow{display:flex;align-items:flex-end;gap:2px;border-bottom:1px solid var(--border)}
.fcar{flex:none;width:34px;height:46px;border:none;background:transparent;color:var(--ink);font-size:28px;line-height:1;cursor:pointer;opacity:.6}
.fcar:hover{opacity:1}
.fctabs{display:flex;gap:4px;overflow-x:auto;flex:1;justify-content:center;scroll-behavior:smooth}.fctabs::-webkit-scrollbar{height:0}
.fctab{flex:none;max-width:210px;text-align:center;font-size:15px;font-weight:800;line-height:1.25;padding:15px 26px;cursor:pointer;white-space:normal;background:transparent;color:var(--ink);border:none;border-radius:14px 14px 0 0;position:relative;margin-bottom:-1px}
.fctab.on{background:#5b6ee8;color:#fff}
.fctab.on::after{content:"";position:absolute;left:0;right:0;bottom:0;height:4px;background:var(--blue)}
#fcpanel{margin-top:26px}
.cat-intro{color:var(--ink);font-size:16px;line-height:1.6;max-width:72ch;margin:8px auto 20px}
.mcards{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px;max-width:760px;margin:0 auto}
.mcard{display:flex;gap:13px;align-items:center;background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:11px;text-decoration:none;color:inherit;transition:box-shadow .15s,transform .15s}
a.mcard:hover{box-shadow:0 8px 22px rgba(20,60,150,.13);transform:translateY(-2px)}
.mcard img{width:66px;height:66px;border-radius:9px;object-fit:cover;flex:none;background:#e8eefb}
.mcard .ph{width:66px;height:66px;border-radius:9px;flex:none;background:linear-gradient(135deg,#e8eefb,#d3e0f6)}
.mcard .mn{font-size:15px;font-weight:800;margin:0}
.mcard .ml{font-size:12px;color:var(--muted);margin:3px 0 0;line-height:1.4}
.mcard .mgo{font-size:11.5px;font-weight:800;color:var(--blue);margin-top:5px;display:block}
.mcard.off{cursor:default}.mcard.off .mgo{color:var(--faint)}
.cta{margin:40px 0;background:linear-gradient(120deg,var(--deep),var(--blue));border-radius:16px;padding:28px 32px;color:#fff;display:flex;gap:20px;align-items:center;flex-wrap:wrap}
.cta h3{margin:0;font-size:21px;flex:1;min-width:240px}
.btn{padding:11px 20px;border-radius:9px;font-weight:700;text-decoration:none;font-size:14px}
.btn.p{background:var(--green);color:#fff}.btn.g{background:rgba(255,255,255,.14);color:#fff;border:1px solid rgba(255,255,255,.3);margin-left:10px}
@media (max-width:760px){.nav{display:none}}
""".strip()

JS = """
var CATS=%s;
function card(p){
  var im=p.img?('<img src="'+p.img+'" alt="" loading="lazy" onerror="this.outerHTML=\\'<span class=ph></span>\\'">'):'<span class="ph"></span>';
  var inner=im+'<div><p class="mn">'+p.n+'</p><p class="ml">'+p.l+'</p>'+
    (p.landing?'<span class="mgo">%s</span>':'<span class="mgo">%s</span>')+'</div>';
  return p.landing?'<a class="mcard" href="'+p.href+'">'+inner+'</a>':'<div class="mcard off">'+inner+'</div>';
}
function renderBar(active){
  var tabs=document.getElementById('fctabs'),panel=document.getElementById('fcpanel');
  tabs.innerHTML='';
  CATS.forEach(function(c,i){
    var b=document.createElement('button');b.className='fctab'+(i===active?' on':'');b.textContent=c.tab;
    b.onclick=function(){renderBar(i);b.scrollIntoView({inline:'center',block:'nearest',behavior:'smooth'});};
    tabs.appendChild(b);
  });
  var c=CATS[active];
  panel.innerHTML='<p class="cat-intro">'+c.intro+'</p><div class="mcards">'+c.prods.map(card).join('')+'</div>';
}
function fcScroll(d){document.getElementById('fctabs').scrollBy({left:d*180,behavior:'smooth'});}
renderBar(0);
""".strip()

def render_industry(data, lang):
    ui = UI.get(lang, UI[SOURCE_LANG])
    slug = data["slug"]
    prefix = LANG_PREFIX[lang]
    title = L(data["hero"]["title"], lang)
    # build CATS for JS
    cats = []
    for t in data["tiers"]:
        prods = []
        for p in t["products"]:
            href = "/%s/products/item/%s/" % (prefix, p["name"].lower().replace(" ", "-")) if p.get("landing") else "#"
            href = href.replace("//", "/")
            prods.append({"n": p["name"], "l": L(p.get("line", {}), lang),
                          "img": p.get("img", ""), "landing": bool(p.get("landing")),
                          "href": href})
        cats.append({"tab": L(t["name"], lang), "intro": L(t["intro"], lang), "prods": prods})
    cats_js = json.dumps(cats, ensure_ascii=False)
    js = JS % (cats_js, ui["go"], ui["consult"])

    nav = "".join('<a href="%s">%s</a>' % (esc(u), esc(n)) for n, u in ui["nav"])
    overview = "".join("<p>%s</p>" % esc(p) for p in L(data["overview"], lang))
    banner = data.get("banner_img", "")
    banner_html = ('<img class="bg" src="%s" alt="" loading="eager" onerror="this.style.display=\'none\'">' % esc(banner)) if banner else ""
    classify = L(data.get("classify_by", {}), lang)
    home_href = "/%s/" % prefix if prefix else "/"

    return """<!doctype html><html lang="%(lang)s"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(title)s — ETIA Label</title>
<style>%(css)s</style></head><body>
<header><div class="wrap">
  <a class="logo" href="%(home)s"><span class="a">◄ETIA</span><span class="b">·LABEL</span></a>
  <nav class="nav">%(nav)s</nav>
  <a href="%(home)sproducts/by-industry/%(slug)s/#contact" class="hcta">%(samples)s</a>
</div></header>
<div class="wrap">
  <div class="crumb"><a href="%(home)s">%(t_home)s</a> › <a href="%(home)sproducts/">%(t_prod)s</a> › <a href="%(home)sproducts/by-industry/">%(t_by)s</a> › <b>%(title)s</b></div>
  <div class="hero">%(banner)s<div class="in">
    <div class="eye">%(eyebrow)s</div><h1>%(title)s</h1><p>%(slogan)s</p>
  </div></div>
  <section>
    <div class="eyebrow">%(part1)s</div><h2>%(overview_t)s</h2>
    <div class="lead">%(overview)s</div>
  </section>
  <section style="padding-top:6px">
    <div class="eyebrow">%(prod_eye)s</div><h2>%(classify)s%(sel)s</h2>
    <div class="fc"><div class="fcrow">
      <button class="fcar" onclick="fcScroll(-1)">&lsaquo;</button>
      <div class="fctabs" id="fctabs"></div>
      <button class="fcar" onclick="fcScroll(1)">&rsaquo;</button>
    </div><div id="fcpanel"></div></div>
  </section>
  <div class="cta" id="contact"><h3>%(cta_h)s</h3>
    <div><a class="btn p" href="%(home)scontact/">%(cta_p)s</a><a class="btn g" href="%(home)scontact/">%(cta_g)s</a></div></div>
</div>
<script>%(js)s</script>
</body></html>""" % {
      "lang": "zh-CN" if lang == "zh" else lang, "title": esc(title), "css": CSS,
      "home": home_href, "nav": nav, "slug": esc(slug), "samples": esc(ui["samples"]),
      "t_home": esc(ui["home"]), "t_prod": esc(ui["products"]), "t_by": esc(ui["by_industry"]),
      "banner": banner_html, "eyebrow": esc(L(data["hero"]["eyebrow"], lang)),
      "slogan": esc(L(data["hero"]["slogan"], lang)),
      "part1": esc(ui["part1"]), "overview_t": esc(ui["overview"]), "overview": overview,
      "prod_eye": esc(ui["products_eyebrow"]), "classify": esc(classify), "sel": esc(ui["select_suffix"]),
      "cta_h": esc(ui["cta_h"]), "cta_p": esc(ui["cta_p"]), "cta_g": esc(ui["cta_g"]), "js": js,
    }

def build(slug, lang):
    data = json.load(open(os.path.join(IND_DIR, slug + ".json"), encoding="utf-8"))
    prefix = LANG_PREFIX[lang]
    outdir = os.path.join(ROOT, prefix, "products", "by-industry", slug)
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as f:
        f.write(render_industry(data, lang))
    return os.path.join(prefix, "products", "by-industry", slug, "index.html")

def main():
    out = build("wire-cable", "zh")
    print("built:", out)

if __name__ == "__main__":
    main()
