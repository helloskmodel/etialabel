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
         "home": "首页", "cta_h": "选型拿不准？告诉我们工况，我们匹配材料",
         "cta_p": "申请样品", "cta_g": "咨询工程师"},
  "vi": {"overview": "Tổng quan ngành", "eyebrow_ov": "Tổng quan ngành",
         "go": "Xem sản phẩm →", "consult": "Tư vấn · chưa có trang riêng",
         "home": "Trang chủ", "cta_h": "Chưa chắc chọn nhãn nào? Cho chúng tôi biết điều kiện — chúng tôi ghép vật liệu.",
         "cta_p": "Yêu cầu mẫu", "cta_g": "Hỏi kỹ sư"},
  "th": {"overview": "ภาพรวมอุตสาหกรรม", "eyebrow_ov": "ภาพรวมอุตสาหกรรม",
         "go": "ดูสินค้า →", "consult": "ปรึกษา · ไม่มีหน้าเฉพาะ",
         "home": "หน้าแรก", "cta_h": "ไม่แน่ใจว่าจะเลือกฉลากใด? บอกเงื่อนไขการใช้งาน แล้วเราจะจับคู่วัสดุให้",
         "cta_p": "ขอตัวอย่าง", "cta_g": "สอบถามวิศวกร"},
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
.wchero::after{content:"";position:absolute;inset:0;z-index:1;background:linear-gradient(90deg,rgba(9,20,48,.9),rgba(20,60,150,.5) 68%,transparent)}
.wchero .in{position:relative;z-index:2;max-width:1080px;margin:0 auto;width:100%;padding:40px 24px}
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
.wctab{flex:none;max-width:200px;text-align:center;font-size:13.5px;font-weight:700;line-height:1.25;padding:10px 16px;cursor:pointer;white-space:normal;background:transparent;color:#143C96;border:none;border-radius:9px 9px 0 0;position:relative;margin-bottom:-1px}
.wctab.on{background:#5b6ee8;color:#fff}
.wctab.on::after{content:"";position:absolute;left:0;right:0;bottom:0;height:3px;background:#1A56DB}
.wctab.hasic{display:flex;flex-direction:column;align-items:center;gap:4px;padding:8px 14px;min-width:74px}
.wctab .tabic{font-size:23px;line-height:1;display:block}
.wctab .tabic svg{width:25px;height:25px;display:block}
.wctab .tablb{font-size:12px;font-weight:700;line-height:1.15}
.wcsubrow{display:none;align-items:center;gap:2px;max-width:860px;margin:16px auto 0}
.wcsub{display:flex;flex-wrap:nowrap;overflow-x:auto;gap:8px;flex:1;justify-content:flex-start;-webkit-overflow-scrolling:touch}
.wcsub::-webkit-scrollbar{height:0}
.wcsubtab{flex:none;font-size:13px;font-weight:600;padding:7px 14px;border-radius:20px;border:1px solid #dbe3f1;background:#fff;color:#41506e;cursor:pointer;white-space:nowrap}
.wcsubtab.on{background:#eef2ff;border-color:#5b6ee8;color:#143C96;font-weight:700}
.wcsubtab:hover{border-color:#5b6ee8}
.wcdt .mn{font-size:17px;font-weight:800;color:#143C96;margin:2px 0 6px}
.wcdt .ml{font-size:15px;line-height:1.65;color:#41506e;margin:0 0 10px}
.wcgo{font-size:13px;font-weight:800;color:#1A56DB;text-decoration:none}
.wcgo.off{color:#8a97b3}
#wcpanel{margin-top:24px;max-width:760px;margin-left:auto;margin-right:auto}
.wccatimg{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:12px;display:block;margin:0 auto 16px;background:#e8eefb}
.wc2col{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start;max-width:720px;margin:0 auto 16px}
.wc2col .wccatimg{margin:0;width:100%;height:140px;object-fit:cover;aspect-ratio:auto}
.wccatcard{background:#f4f7fd;border:1px solid #e6ecf7;border-radius:12px;padding:15px 18px;display:flex;align-items:center}
.wccatcard .wccatintro{margin:0;text-align:left;font-size:15px;line-height:1.62;color:#2c3a58}
#wcpanel .wcmcards{max-width:720px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}
#wcpanel .wcmcards.wcone{grid-template-columns:1fr;max-width:720px}
@media(max-width:760px){.wc2col{grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}.wc2col .wccatimg{height:120px}.wccatcard{padding:12px 13px}.wccatcard .wccatintro{font-size:12.5px;line-height:1.48}#wcpanel .wcmcards,#wcpanel .wcmcards.wcone{grid-template-columns:1fr}}
.wccatintro{color:#2c3a58;font-size:16px;line-height:1.7;margin:8px auto 20px}
.wcmcards{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px}
.wcmcard{display:flex;gap:13px;align-items:center;background:#fff;border:1px solid #dbe3f1;border-radius:12px;padding:11px;text-decoration:none;color:#17203a;transition:box-shadow .15s,transform .15s}
a.wcmcard:hover{box-shadow:0 8px 22px rgba(20,60,150,.13);transform:translateY(-2px)}
.wcmcard .ic{width:44px;height:44px;border-radius:8px;flex:none;overflow:hidden;background:#f2f5fa;align-self:flex-start}
.wcmcard .ic .cim{width:100%;height:100%;object-fit:cover;display:block}
.wcmcard .mn{font-size:15px;font-weight:800;margin:0}
.wcmcard .ml{font-size:12px;color:#5a6884;margin:3px 0 0;line-height:1.4}
.wcmcard .mgo{font-size:11.5px;font-weight:800;color:#1A56DB;margin-top:5px;display:block}
.wcmcard.off{cursor:default}.wcmcard.off .mgo{color:#8a97b3}
.wcmcard.big{flex-direction:column;align-items:stretch;gap:0;padding:0;overflow:hidden}
.wcmcard.big .ic{width:100%;height:140px;border-radius:0;align-self:stretch}
.wcmcard.big>div{padding:13px 15px}
.wcmcard.big .ml{font-size:13px}
@media(max-width:760px){.wcmcard.big .ic{height:150px}}
@media (max-width:760px){
  .wchero{min-height:210px}
  .wchero .in{padding:24px 18px}
  .wchero h1{font-size:24px;margin:8px 0 6px}
  .wchero .slog{font-size:15.5px}
  .wcsec{padding:20px 18px}
  .wcsec h2{font-size:20px;margin:6px 0 9px}
  .wcov p{font-size:14.5px;line-height:1.62;margin:0 0 8px}
  .wccatintro{font-size:14.5px;line-height:1.58;margin:6px auto 14px}
  .wctab{font-size:12.5px;padding:9px 13px}
  #wcpanel{margin-top:16px}
  .wcmcard .ic{width:40px;height:40px}
}
</style>
"""

JS_TMPL = """
<script>
(function(){
var CATS=%(cats)s, GO=%(go)s, SUBNAV=%(subnav)s, HIDE_INTRO=%(hide_intro)s, BIG_IMG=%(big_img)s;
function card(p,hideName){
  var cls='wcmcard'+(BIG_IMG?' big':'')+(p.landing?'':' off');
  var im=p.img?('<span class="ic"><img class="cim" src="'+p.img+'" alt="" loading="lazy" onerror="this.parentNode.remove()"></span>'):'';
  var nm=hideName?'':'<p class="mn">'+p.n+'</p>';
  var inner=im+'<div>'+nm+'<p class="ml">'+p.l+'</p>'+(p.landing?('<span class="mgo">'+GO+'</span>'):'')+'</div>';
  return p.landing?'<a class="'+cls+'" href="'+p.href+'">'+inner+'</a>':'<div class="'+cls+'">'+inner+'</div>';
}
// top row: [image | category-description card]; falls back to plain intro when no image
function topRow(c){
  if(HIDE_INTRO) return '';
  if(!c.img) return c.intro?('<p class="wccatintro">'+c.intro+'</p>'):'';
  var intro=c.intro?('<div class="wccatcard"><p class="wccatintro">'+c.intro+'</p></div>'):'<div class="wccatcard"></div>';
  return '<div class="wc2col"><img class="wccatimg" src="'+c.img+'" alt="" loading="lazy" onerror="this.remove()">'+intro+'</div>';
}
// two-level detail: render the selected sub-application under a category
function renderSub(a,sel){
  var c=CATS[a],sub=document.getElementById('wcsub'),panel=document.getElementById('wcpanel');
  sub.innerHTML='';
  c.prods.forEach(function(p,j){
    var b=document.createElement('button');b.className='wcsubtab'+(j===sel?' on':'');b.textContent=p.n;
    b.onclick=function(){renderSub(a,j);b.scrollIntoView({inline:'center',block:'nearest',behavior:'smooth'});};
    sub.appendChild(b);
  });
  // pill already names the product, so hide the name in the detail card (no repeat)
  panel.innerHTML=topRow(c)+'<div class="wcmcards wcone">'+card(c.prods[sel],true)+'</div>';
}
function render(a){
  var tabs=document.getElementById('wctabs'),panel=document.getElementById('wcpanel'),sub=document.getElementById('wcsub');
  tabs.innerHTML='';
  CATS.forEach(function(c,i){
    var b=document.createElement('button');b.className='wctab'+(i===a?' on':'')+(c.icon?' hasic':'');
    if(c.icon){b.innerHTML='<span class="tabic">'+c.icon+'</span><span class="tablb">'+c.tab+'</span>';}else{b.textContent=c.tab;}
    b.onclick=function(){render(i);b.scrollIntoView({inline:'center',block:'nearest',behavior:'smooth'});};
    tabs.appendChild(b);
  });
  var subrow=document.getElementById('wcsubrow');
  if(SUBNAV){ if(subrow) subrow.style.display='flex'; renderSub(a,0); return; }
  if(subrow){ subrow.style.display='none'; }
  var c=CATS[a];
  panel.innerHTML=topRow(c)+'<div class="wcmcards">'+c.prods.map(function(p){return card(p,false);}).join('')+'</div>';
}
window.wcScroll=function(d){document.getElementById('wctabs').scrollBy({left:d*180,behavior:'smooth'});};
window.wcSubScroll=function(d){document.getElementById('wcsub').scrollBy({left:d*200,behavior:'smooth'});};
render(0);
})();
</script>
"""

def build_lang(data, lang):
    ui = UI.get(lang, UI[SOURCE_LANG])
    slug = data["slug"]
    path = "%s%s/" % (data.get("base", "/industries/"), slug)
    title = L(data["hero"]["title"], lang)

    # CATS for the FlexCon bar
    cats = []
    for t in data["tiers"]:
        prods = []
        for p in t["products"]:
            pslug = p.get("slug", "")
            purl = p.get("url", "")  # optional arbitrary link target (e.g. a combined card -> an industry page)
            if purl:
                href = hp.Lx(lang, purl); is_landing = True
            elif pslug and p.get("landing"):
                href = hp.Lx(lang, "/products/item/%s/" % pslug); is_landing = True
            else:
                href = "#"; is_landing = False
            pname = p["name"]
            pname = L(pname, lang) if isinstance(pname, dict) else pname
            prods.append({"n": pname, "l": L(p.get("line", {}), lang),
                          "img": p.get("img", ""), "landing": is_landing,
                          "href": href})
        tabval = t.get("tab")
        tab = L(tabval, lang) if isinstance(tabval, dict) else (tabval or L(t["name"], lang))
        cats.append({"tab": tab, "intro": L(t["intro"], lang),
                     "img": t.get("img", ""), "icon": t.get("icon", ""), "prods": prods})

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
            '</div><div class="wcsubrow" id="wcsubrow"><button class="wcar" onclick="wcSubScroll(-1)">&lsaquo;</button>'
            '<div class="wcsub" id="wcsub"></div>'
            '<button class="wcar" onclick="wcSubScroll(1)">&rsaquo;</button></div><div id="wcpanel"></div></div></section>') % (
        esc(ui["eyebrow_ov"]), esc(ui["overview"]), overview, esc(L(data["classify_by"], lang)))
    body += JS_TMPL % {"cats": json.dumps(cats, ensure_ascii=False),
                       "go": json.dumps(ui["go"], ensure_ascii=False),
                       "subnav": "true" if data.get("subnav") else "false",
                       "hide_intro": "true" if data.get("hide_intro") else "false",
                       "big_img": "true" if data.get("big_img") else "false"}

    crumb = [(ui["home"], "/"), (title, path)]
    content = hp.page(lang, path, L(data["seo_title"], lang), L(data["seo_desc"], lang),
                      title, "", body, crumb, active="app", trust=False, hero=hero,
                      langs=data.get("langs", ["en", "zh"]))
    hp.write(lang, path, content)  # overwrites gen_industry output; path already tracked there
    if lang == "en" and data.get("track"):  # new pages (not from gen_industry) need tracking
        hp.track(path, "products")
    return (hp.PREFIX[lang] + path)

def main():
    # Both languages get the v2 design + real products (model numbers are facts,
    # not translation). English prose (overview / tier intros) is a draft
    # translation of the Chinese brief, pending client review.
    for slug in ["wire-cable", "outdoor-energy", "pcb", "steel", "automotive", "heat-resistant", "low-temperature", "flame-retardant", "weather-resistant", "medical"]:
        data = json.load(open(os.path.join(IND_DIR, slug + ".json"), encoding="utf-8"))
        for lang in data.get("langs", ["en", "zh"]):
            out = build_lang(data, lang)
            print("industry v2:", out)

if __name__ == "__main__":
    # allow standalone run after hp is importable
    main()
