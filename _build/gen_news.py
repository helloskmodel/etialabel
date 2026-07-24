#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""News / Insights section — hub (image-top cover cards) + article pages.

Data: _build/data/news.json. Renders into the live shell (gen_heatproof.page).
Chinese first; English fields fall back to zh source until translated.
"""
import json, os
import gen_heatproof as hp

BUILD = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BUILD, "data", "news.json")
HUB = "/news/"
SOURCE_LANG = "zh"
esc = hp.esc

UI = {
  "en": {"hub_title": "News & Insights", "hub_lede": "Selection guidance, certifications and application know-how for durable industrial labels.",
         "read": "Read →", "back": "← All articles", "home": "Home", "news": "News"},
  "zh": {"hub_title": "新闻与洞察", "hub_lede": "耐久工业标签的选型指南、认证科普与应用知识。",
         "read": "阅读 →", "back": "← 返回全部文章", "home": "首页", "news": "新闻"},
}

def L(node, lang):
    if not isinstance(node, dict):
        return node or ""
    v = node.get(lang)
    if v:
        return v
    return node.get(SOURCE_LANG) or ""

CSS = """
<style>
.nwrap{max-width:820px;margin:0 auto;padding:0 22px}
.nhero{position:relative;overflow:hidden;color:#fff;min-height:240px;display:flex;align-items:flex-end;background:#12224b}
.nhero img.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.5}
.nhero::after{content:"";position:absolute;inset:0;z-index:1;background:linear-gradient(90deg,rgba(9,20,48,.9),rgba(20,60,150,.5) 68%,transparent)}
.nhero .in{position:relative;z-index:2;max-width:1080px;margin:0 auto;width:100%;padding:34px 24px}
.nhero .k{font-size:12px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:#8fe36a}
.nhero h1{color:#fff;font-size:clamp(24px,4vw,36px);margin:10px 0 8px;line-height:1.16;max-width:24em}
.nhero .sub{color:#dbe6ff;font-size:17px;margin:0;max-width:40em}
.ntags{display:flex;gap:7px;flex-wrap:wrap;margin:14px 0 0}
.ntag{font-size:12px;font-weight:700;color:#1A56DB;background:#eef3fc;padding:4px 11px;border-radius:999px}
.art{max-width:760px;margin:0 auto;padding:34px 22px}
.art .lead{font-size:17px;line-height:1.8;color:#2c3a58;margin:0 0 22px;font-weight:500}
.art h2{font-size:20px;color:#143C96;margin:26px 0 10px}
.art p{font-size:15.5px;line-height:1.85;color:#41506e;margin:0 0 12px}
.nback{display:inline-block;margin:8px 0 0;font-size:14px;font-weight:700;color:#1A56DB;text-decoration:none}
/* hub */
.ncards{max-width:1080px;margin:0 auto;padding:30px 22px 10px;display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:22px}
.ncard{background:#fff;border:1px solid #dbe3f1;border-radius:16px;overflow:hidden;text-decoration:none;color:inherit;display:flex;flex-direction:column;transition:box-shadow .15s,transform .15s}
.ncard:hover{box-shadow:0 14px 34px rgba(20,60,150,.14);transform:translateY(-3px)}
.ncard img{aspect-ratio:16/9;object-fit:cover;width:100%;background:#e8eefb}
.ncard .cb{padding:16px 18px 18px;display:flex;flex-direction:column;gap:9px;flex:1}
.ncard .kind{font-size:10.5px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:#1A56DB}
.ncard h3{margin:0;font-size:17px;line-height:1.35;color:#17203a}
.ncard .cs{font-size:13.5px;color:#5a6884;line-height:1.5;flex:1}
.ncard .go{font-size:13.5px;font-weight:800;color:#41A62A}
</style>
"""

def build_article(a, lang):
    ui = UI.get(lang, UI[SOURCE_LANG])
    slug = a["slug"]
    path = HUB + slug + "/"
    title = L(a["title"], lang)
    banner = a.get("banner", "")
    bg = ('<img class="bg" src="%s" alt="" loading="eager" onerror="this.style.display=\'none\'">' % esc(banner)) if banner else ""
    tags = "".join('<span class="ntag">%s</span>' % esc(t) for t in L(a.get("tags", {}), lang))
    hero = ('%s<section class="nhero">%s<div class="in"><div class="k">%s</div>'
            '<h1>%s</h1><p class="sub">%s</p>%s</div></section>') % (
        CSS, bg, esc(ui["news"]), esc(title), esc(L(a.get("subtitle", {}), lang)),
        ('<div class="ntags">%s</div>' % tags) if tags else "")
    body = '<div class="art"><p class="lead">%s</p>' % esc(L(a.get("lead", {}), lang))
    for sec in L(a.get("sections", {}), lang):
        if sec.get("h"):
            body += "<h2>%s</h2>" % esc(sec["h"])
        for p in sec.get("ps", []):
            body += "<p>%s</p>" % esc(p)
    body += '<a class="nback" href="%s">%s</a></div>' % (hp.Lx(lang, HUB), esc(ui["back"]))
    crumb = [(ui["home"], "/"), (ui["hub_title"], HUB), (title, path)]
    content = hp.page(lang, path, title + " | ETIA", esc(L(a.get("subtitle", {}), lang)),
                      title, "", body, crumb, active="news", trust=False, hero=hero)
    hp.write(lang, path, content)
    if lang == "en":
        hp.track(path, "core")

def build_hub(lang):
    ui = UI.get(lang, UI[SOURCE_LANG])
    arts = json.load(open(DATA, encoding="utf-8"))["articles"]
    cards = ""
    for a in arts:
        banner = a.get("banner", "")
        img = ('<img src="%s" alt="" loading="lazy" onerror="this.remove()">' % esc(banner)) if banner else ""
        cards += ('<a class="ncard" href="%s">%s<div class="cb"><span class="kind">%s</span>'
                  '<h3>%s</h3><p class="cs">%s</p><span class="go">%s</span></div></a>') % (
            hp.Lx(lang, HUB + a["slug"] + "/"), img, esc(ui["news"]),
            esc(L(a["title"], lang)), esc(L(a.get("subtitle", {}), lang)), esc(ui["read"]))
    body = CSS + '<div class="ncards">%s</div>' % cards
    crumb = [(ui["home"], "/"), (ui["hub_title"], HUB)]
    content = hp.page(lang, HUB, ui["hub_title"] + " | ETIA", ui["hub_lede"],
                      ui["hub_title"], ui["hub_lede"], body, crumb, active="news", trust=False)
    hp.write(lang, HUB, content)
    if lang == "en":
        hp.track(HUB, "core")

def main():
    arts = json.load(open(DATA, encoding="utf-8"))["articles"]
    for lang in ["en", "zh"]:
        build_hub(lang)
        for a in arts:
            build_article(a, lang)
        print("news:", hp.PREFIX[lang] + HUB, "+", len(arts), "articles")

if __name__ == "__main__":
    main()
