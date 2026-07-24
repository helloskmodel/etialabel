#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Data-driven industry-page override (v2 design) rendered INTO the live shell.

Reads _build/data/industries/<slug>.json and rebuilds the industry landing
page with the agreed structure — Hero (title + one-line slogan) -> Industry
Overview (~300 words) -> FlexCon Bar by performance tier -> tier intro ->
small product cards -> important products link to a product Landing.

Uses gen_heatproof's page() shell (same header / nav / footer as the rest of
the site) and writes over the gen_industry output. Runs AFTER gen_industry in
build.py. Content lives in the JSON (en + zh, zh = source, fall back to zh).
"""
import json, os, html
import gen_heatproof as hp

BUILD = os.path.dirname(os.path.abspath(__file__))
IND_DIR = os.path.join(BUILD, "data", "industries")
SOURCE_LANG = "zh"

UI = {
  "en": {"overview": "Industry Overview", "eyebrow_ov": "Industry Overview",
         "go": "View product →", "consult": "Consult · no dedicated page",
         "home": "Home", "cta_h": "Not sure which cable label? Tell us the conditions — we match the material.",
         "cta_p": "Request Samples", "cta_g": "Ask an Engineer"},
  "zh": {"overview": "行业概述", "eyebrow_ov": "行业概述",
         "go": "查看产品 →", "consult": "咨询选型 · 无单独页",
         "home": "首页", "cta_h": "线缆标识选型拿不准？告诉我们工况，我们匹配材料",
         "cta_p": "申请样品", "cta_g": "咨询工程师"},
}

def L(node, lang):
    if not isinstance(node, dict):
        return node or ""
    return node.get(lang) or node.get(SOURCE_LANG) or ""

esc = hp.esc

CSS = """
<style>
.wchero{position:relative;overflow:hidden;color:#fff;min-height:280px;display:flex;align-items:flex-end;background:#12224b}
.wchero img.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.5}
.wchero::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(9,20,48,.94),rgba(20,60,150,.55) 72%,transparent)}
.wchero .in{position:relative;max-width:1080px;margin:0 auto;width:100%;padding:40px 24px}
.wchero .eye{font-size:12px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#8fe36a}
.wchero h1{color:#fff;font-size:clamp(26px,4.4vw,40px);margin:10px 0 8px;line-height:1.14;max-width:20em}
.wchero .slog{color:#dbe6ff;font-size:19px;font-weight:600;margin:0;max-width:30em}
.wcsec{max-width:1080px;margin:0 auto;padding:34px 24px}
.wceye{font-size:12px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:#1A56DB}
.wcsec h2{font-size:24px;margin:8px 0 14px;color:#143C96}
.wcov p{color:#41506e;font-size:15.5px;line-height:1.75;max-width:74ch;margin:0 0 12px}
.wcfc{margin-top:16px}
.wcfcrow{display:flex;align-items:flex-end;gap:2px;border-bottom:1px solid #dbe3f1}
.wcar{flex:none;width:34px;height:46px;border:none;background:transparent;color:#143C96;font-size:26px;line-height:1;cursor:pointer;opacity:.6}
.wcar:hover{opacity:1}
.wctabs{display:flex;gap:4px;overflow-x:auto;flex:1;justify-content:center}
.wctabs::-webkit-scrollbar{height:0}
.wctab{flex:none;max-width:220px;text-align:center;font-size:15px;font-weight:800;line-height:1.25;padding:15px 24px;cursor:pointer;white-space:normal;background:transparent;color:#143C96;border:none;border-radius:14px 14px 0 0;position:relative;margin-bottom:-1px}
.wctab.on{background:#5b6ee8;color:#fff}
.wctab.on::after{content:"";position:absolute;left:0;right:0;bottom:0;height:4px;background:#1A56DB}
#wcpanel{margin-top:24px;max-width:760px;margin-left:auto;margin-right:auto}
.wccatintro{color:#2c3a58;font-size:16px;line-height:1.7;margin:8px auto 20px}
.wcmcards{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px}
.wcmcard{display:flex;gap:13px;align-items:center;background:#fff;border:1px solid #dbe3f1;border-radius:12px;padding:11px;text-decoration:none;color:#17203a;transition:box-shadow .15s,transform .15s}
a.wcmcard:hover{box-shadow:0 8px 22px rgba(20,60,150,.13);transform:translateY(-2px)}
.wcmcard img{width:64px;height:64px;border-radius:9px;object-fit:cover;flex:none;background:#e8eefb}
.wcmcard .ph{width:64px;height:64px;border-radius:9px;flex:none;background:linear-gradient(135deg,#e8eefb,#d3e0f6)}
.wcmcard .mn{font-size:15px;font-weight:800;margin:0}
.wcmcard .ml{font-size:12px;color:#5a6884;margin:3px 0 0;line-height:1.4}
.wcmcard .mgo{font-size:11.5px;font-weight:800;color:#1A56DB;margin-top:5px;display:block}
.wcmcard.off{cursor:default}.wcmcard.off .mgo{color:#8a97b3}
</style>
"""

JS_TMPL = """
<script>
(function(){
var CATS=%(cats)s, GO=%(go)s, CS=%(consult)s;
function card(p){
  var im=p.img?('<img src="'+p.img+'" alt="" loading="lazy" onerror="this.outerHTML=\\'<span class=ph></span>\\'">'):'<span class="ph"></span>';
  var inner=im+'<div><p class="mn">'+p.n+'</p><p class="ml">'+p.l+'</p>'+(p.landing?('<span class="mgo">'+GO+'</span>'):('<span class="mgo">'+CS+'</span>'))+'</div>';
  return p.landing?'<a class="wcmcard" href="'+p.href+'">'+inner+'</a>':'<div class="wcmcard off">'+inner+'</div>';
}
function render(a){
  var tabs=document.getElementById('wctabs'),panel=document.getElementById('wcpanel');
  tabs.innerHTML='';
  CATS.forEach(function(c,i){
    var b=document.createElement('button');b.className='wctab'+(i===a?' on':'');b.textContent=c.tab;
    b.onclick=function(){render(i);b.scrollIntoView({inline:'center',block:'nearest',behavior:'smooth'});};
    tabs.appendChild(b);
  });
  var c=CATS[a];
  panel.innerHTML='<p class="wccatintro">'+c.intro+'</p><div class="wcmcards">'+c.prods.map(card).join('')+'</div>';
}
window.wcScroll=function(d){document.getElementById('wctabs').scrollBy({left:d*180,behavior:'smooth'});};
render(0);
})();
</script>
"""

def build_lang(data, lang):
    ui = UI.get(lang, UI[SOURCE_LANG])
    slug = data["slug"]
    path = "/industries/%s/" % slug
    title = L(data["hero"]["title"], lang)

    # CATS for the FlexCon bar
    cats = []
    for t in data["tiers"]:
        prods = []
        for p in t["products"]:
            prods.append({"n": p["name"], "l": L(p.get("line", {}), lang),
                          "img": p.get("img", ""), "landing": bool(p.get("landing")),
                          "href": "#"})  # product Landing pages: next step
        cats.append({"tab": L(t["name"], lang), "intro": L(t["intro"], lang), "prods": prods})

    banner = data.get("banner_img", "")
    bg = ('<img class="bg" src="%s" alt="" loading="eager" onerror="this.style.display=\'none\'">' % esc(banner)) if banner else ""
    hero = ('%s<section class="wchero">%s<div class="in">'
            '<div class="eye">%s</div><h1>%s</h1><p class="slog">%s</p></div></section>') % (
        CSS, bg, esc(L(data["hero"]["eyebrow"], lang)), esc(title), esc(L(data["hero"]["slogan"], lang)))

    overview = "".join("<p>%s</p>" % esc(p) for p in L(data["overview"], lang))
    body = ('<section class="wcsec wcov"><div class="wceye">%s</div><h2>%s</h2>%s</section>'
            '<section class="wcsec"><div class="wceye">Products</div><h2>%s</h2>'
            '<div class="wcfc"><div class="wcfcrow">'
            '<button class="wcar" onclick="wcScroll(-1)">&lsaquo;</button>'
            '<div class="wctabs" id="wctabs"></div>'
            '<button class="wcar" onclick="wcScroll(1)">&rsaquo;</button>'
            '</div><div id="wcpanel"></div></div></section>') % (
        esc(ui["eyebrow_ov"]), esc(ui["overview"]), overview, esc(L(data["classify_by"], lang)))
    body += JS_TMPL % {"cats": json.dumps(cats, ensure_ascii=False),
                       "go": json.dumps(ui["go"], ensure_ascii=False),
                       "consult": json.dumps(ui["consult"], ensure_ascii=False)}

    crumb = [(ui["home"], "/"), (title, path)]
    content = hp.page(lang, path, L(data["seo_title"], lang), L(data["seo_desc"], lang),
                      title, "", body, crumb, active="app", trust=False, hero=hero)
    hp.write(lang, path, content)  # overwrites gen_industry output; path already tracked there
    return (hp.PREFIX[lang] + path)

def main():
    # Both languages get the v2 design + real products (model numbers are facts,
    # not translation). English prose (overview / tier intros) is a draft
    # translation of the Chinese brief, pending client review.
    for slug in ["wire-cable"]:
        data = json.load(open(os.path.join(IND_DIR, slug + ".json"), encoding="utf-8"))
        for lang in ["en", "zh"]:
            out = build_lang(data, lang)
            print("industry v2:", out)

if __name__ == "__main__":
    # allow standalone run after hp is importable
    main()
