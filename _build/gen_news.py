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
HUB = "/insights/"
SOURCE_LANG = "zh"
esc = hp.esc

UI = {
  "en": {"hub_title": "Resources", "hub_lede": "Market analysis, material knowledge and application know-how for durable industrial labels.",
         "read": "Read →", "back": "← All resources", "home": "Home", "news": "Resources",
         "hero_sub": "Industry News · Label & Labeling Knowledge",
         "sec_news": "Industry News", "sec_know": "Label & Labeling Knowledge",
         "soon": "More articles coming soon."},
  "zh": {"hub_title": "资讯", "hub_lede": "耐久工业标签的市场解读、材料知识与应用经验。",
         "read": "阅读 →", "back": "← 返回全部资讯", "home": "首页", "news": "资讯",
         "hero_sub": "行业动态 · 实验室与标签知识",
         "sec_news": "行业动态", "sec_know": "实验室与标签知识",
         "soon": "更多内容即将上线。"},
  "vi": {"hub_title": "Tài nguyên", "hub_lede": "Phân tích thị trường, kiến thức vật liệu và kinh nghiệm ứng dụng cho nhãn công nghiệp bền.",
         "read": "Đọc →", "back": "← Tất cả tài nguyên", "home": "Trang chủ", "news": "Tài nguyên",
         "hero_sub": "Tin ngành · Kiến thức nhãn & phòng lab",
         "sec_news": "Tin ngành", "sec_know": "Kiến thức nhãn & phòng lab",
         "soon": "Sẽ sớm có thêm bài viết."},
  "th": {"hub_title": "แหล่งข้อมูล", "hub_lede": "การวิเคราะห์ตลาด ความรู้ด้านวัสดุ และความเชี่ยวชาญการใช้งานสำหรับฉลากอุตสาหกรรมที่ทนทาน",
         "read": "อ่าน →", "back": "← แหล่งข้อมูลทั้งหมด", "home": "หน้าแรก", "news": "แหล่งข้อมูล",
         "hero_sub": "ข่าวอุตสาหกรรม · ความรู้ห้องแล็บและฉลาก",
         "sec_news": "ข่าวอุตสาหกรรม", "sec_know": "ความรู้ห้องแล็บและฉลาก",
         "soon": "เร็วๆ นี้จะมีบทความเพิ่มเติม"},
}

# Topic taxonomy — each article carries a "topic" key. The hub card cover is a
# color-coded gradient block (no photo) keyed to the topic; eyebrow + title sit
# on it. Colors: engineer=light blue, standard=light gray, experience=light
# green, news=light gray-purple, new product=light sand/camel.
TOPICS = {
  "engineer_guide": {"label": {
     "en": "Engineer Guide", "zh": "工程师指南", "vi": "Hướng dẫn kỹ sư", "th": "คู่มือวิศวกร"}},
  "industry_standard": {"label": {
     "en": "Industry Standards & Rules", "zh": "行业标准与规范", "vi": "Tiêu chuẩn & quy định ngành", "th": "มาตรฐานและกฎของอุตสาหกรรม"}},
  "industry_experience": {"label": {
     "en": "Industry Experience", "zh": "行业经验", "vi": "Kinh nghiệm ngành", "th": "ประสบการณ์ในอุตสาหกรรม"}},
  "news": {"label": {
     "en": "News", "zh": "行业动态", "vi": "Tin tức", "th": "ข่าวสาร"}},
  "new_product": {"label": {
     "en": "New Product", "zh": "新品发布", "vi": "Sản phẩm mới", "th": "สินค้าใหม่"}},
}

def topic_key(a):
    """Resolve an article's topic key. Prefer explicit 'topic'; else derive from
    category / cover_cat text; default to industry_standard."""
    tk = a.get("topic")
    if tk in TOPICS:
        return tk
    if a.get("category") == "news":
        return "news"
    cc = a.get("cover_cat") or {}
    en = ((cc.get("en") if isinstance(cc, dict) else cc) or "").lower()
    if "engineer" in en:
        return "engineer_guide"
    if "experience" in en:
        return "industry_experience"
    if "product" in en:
        return "new_product"
    if "standard" in en or "rule" in en:
        return "industry_standard"
    return "industry_standard"

# Controlled industry taxonomy (keys map to consistent 4-lang labels) — set
# each article's "industry" to a list of these keys.
INDUSTRY_LABELS = {
  "pcb":        {"en": "PCB & Electronics", "zh": "PCB 电子", "vi": "PCB & Điện tử", "th": "PCB และอิเล็กทรอนิกส์"},
  "medical":    {"en": "Medical & Pharma", "zh": "医疗医药", "vi": "Y tế & Dược", "th": "การแพทย์และยา"},
  "automotive": {"en": "Automotive", "zh": "汽车", "vi": "Ô tô", "th": "ยานยนต์"},
  "cable":      {"en": "Cable & Wire", "zh": "线缆", "vi": "Cáp & Dây", "th": "สายเคเบิล"},
  "steel":      {"en": "Steel & Metal", "zh": "钢铁金属", "vi": "Thép & Kim loại", "th": "เหล็กและโลหะ"},
  "outdoor":    {"en": "Outdoor & Durable", "zh": "户外耐候", "vi": "Ngoài trời", "th": "กลางแจ้ง"},
}

def _ind_label(key, lang):
    node = INDUSTRY_LABELS.get(key, {})
    return node.get(lang) or node.get("en") or key

def chips_html(a, lang, groups=("ind", "cat")):
    """Industry (accent) + label-category chips. `groups` selects which show."""
    out = ""
    if "ind" in groups:
        for key in a.get("industry", []):
            out += '<span class="nchip ind">%s</span>' % esc(_ind_label(key, lang))
    if "cat" in groups:
        for c in L(a.get("label_category", {}), lang):
            out += '<span class="nchip cat">%s</span>' % esc(c)
    return ('<div class="nchips">%s</div>' % out) if out else ""

def cover_category(a, lang):
    """Short classification/genre shown on the card cover. Prefers an explicit
    'cover_cat' (e.g. 'Engineer Selection Guide', 'Knowledge Sharing'), then the
    label category, then the industry name."""
    cc = a.get("cover_cat")
    if cc:
        v = L(cc, lang)
        if v:
            return v
    cats = L(a.get("label_category", {}), lang)
    if cats:
        return " · ".join(cats)
    inds = [_ind_label(k, lang) for k in a.get("industry", [])]
    return " · ".join(inds)

def seo_keywords(a):
    """Flat English keyword string from industry + category + tags for <meta>."""
    kw = [_ind_label(k, "en") for k in a.get("industry", [])]
    kw += (a.get("label_category", {}) or {}).get("en", [])
    kw += (a.get("tags", {}) or {}).get("en", [])
    seen, out = set(), []
    for k in kw:
        if k and k not in seen:
            seen.add(k); out.append(k)
    return ", ".join(out)

def L(node, lang):
    if not isinstance(node, dict):
        return node or ""
    v = node.get(lang)
    if v:
        return v
    # fall back to English for non-source languages (readable internationally),
    # then to the Chinese source.
    return node.get("en") or node.get(SOURCE_LANG) or ""

CSS = """
<style>
.nwrap{max-width:820px;margin:0 auto;padding:0 22px}
.nhero{position:relative;overflow:hidden;color:#fff;min-height:320px;display:flex;align-items:center;background:#12224b;border-bottom:2px solid #fff}
.nhero img.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center right;opacity:1}
.nhero::after{content:"";position:absolute;inset:0;z-index:1;background:linear-gradient(90deg,rgba(20,60,150,.90) 16%,rgba(20,60,150,.50) 54%,rgba(20,60,150,.08))}
.nhero .in{position:relative;z-index:2;max-width:1080px;margin:0 auto;width:100%;padding:34px 24px}
.nhero .k{font-size:12px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:#8fe063}
.nhero h1{color:#fff;font-family:var(--sans);font-weight:800;font-size:40px;letter-spacing:-.01em;margin:2px 0 10px;line-height:1.12;max-width:24em}
.nhero .sub{color:#eef3ff;font-size:18px;font-weight:700;margin:0;max-width:40em}
.ntags{display:flex;gap:7px;flex-wrap:wrap;margin:14px 0 0}
.ntag{font-size:12px;font-weight:700;color:#1A56DB;background:#eef3fc;padding:4px 11px;border-radius:999px}
/* structured industry / label-category chips */
.nchips{display:flex;gap:6px;flex-wrap:wrap;margin:10px 0 0}
.nchip{font-size:11.5px;font-weight:800;letter-spacing:.02em;padding:3px 10px;border-radius:999px;line-height:1.5}
.nchip.ind{color:#fff;background:#1A56DB}
.nchip.cat{color:#2c7a1e;background:#e6f5e0}
.nhero .nchip.cat{color:#d7ffcf;background:rgba(65,166,42,.30)}
.nhero .nchips{margin-top:12px}
.ncard .nchips{margin:0 0 2px}
.ncard .nchip{font-size:10.5px;padding:2px 8px}
.art{max-width:760px;margin:0 auto;padding:34px 22px}
.art .leadrow{overflow:hidden;margin:0 0 22px}
.art .leadimg{float:left;width:230px;max-width:40%;height:auto;border-radius:10px;border:1px solid #e2e9f5;margin:3px 22px 10px 0}
.art .leadrow .lead{margin:0}
@media(max-width:560px){.art .leadimg{float:none;width:100%;max-width:100%;margin:0 0 14px}}
.art .lead{font-size:17px;line-height:1.8;color:#2c3a58;margin:0 0 22px;font-weight:500}
.art h2{font-size:20px;color:#143C96;margin:26px 0 10px}
.art p{font-size:15.5px;line-height:1.85;color:#41506e;margin:0 0 12px}
.nback{display:inline-block;margin:8px 0 0;font-size:14px;font-weight:700;color:#1A56DB;text-decoration:none}
.nctarow{display:flex;flex-wrap:wrap;gap:12px;margin:26px 0 6px}
.ncta{display:inline-flex;align-items:center;padding:12px 22px;border-radius:26px;font-size:15px;font-weight:800;text-decoration:none;background:#1A56DB;color:#fff}
.ncta:nth-child(2){background:#16a34a}
.ncta:hover{filter:brightness(1.06)}
/* hub — text section headers that split News vs Knowledge */
.nsec{max-width:1080px;margin:0 auto;padding:0 22px}
.nsechd{margin:34px 0 14px;border-bottom:1px solid #e2e9f5;padding-bottom:10px}
.nsechd .k{font-size:11px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:#1A56DB}
.nsechd h2{margin:3px 0 0;font-size:23px;color:#143C96;font-family:var(--sans);font-weight:800;line-height:1.1}
.nrow{display:flex;flex-wrap:nowrap;overflow-x:auto;gap:18px;padding:2px 0 14px;scroll-snap-type:x mandatory;-webkit-overflow-scrolling:touch}
.nrow::-webkit-scrollbar{height:6px}
.nrow::-webkit-scrollbar-thumb{background:#c7d3ea;border-radius:6px}
.nrow .ncard{flex:0 0 258px;scroll-snap-align:start}
.nsoon{color:#5a6884;font-size:14px;padding:8px 2px 18px}
/* hub */
.ncards{max-width:1080px;margin:0 auto;padding:4px 22px 10px;display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:22px}
.ncard{background:#fff;border:1px solid #dbe3f1;border-radius:16px;overflow:hidden;text-decoration:none;color:inherit;display:flex;flex-direction:column;transition:box-shadow .15s,transform .15s}
.ncard:hover{box-shadow:0 14px 34px rgba(20,60,150,.14);transform:translateY(-3px)}
.ncard img{aspect-ratio:16/9;object-fit:cover;width:100%;background:#e8eefb}
/* article cover = a topic color gradient (no photo); eyebrow + title sit on it */
.ncov{position:relative;min-height:158px;overflow:hidden;display:flex}
.ncov .novl{position:relative;z-index:2;display:flex;flex-direction:column;gap:9px;padding:18px 20px;width:100%}
.ncov .novl .k{font-size:11px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;opacity:.95}
.ncov .novl .ncovh{margin:0;font-family:var(--sans);font-weight:800;font-size:19px;line-height:1.3;letter-spacing:-.01em}
/* topic color themes — light gradient + readable dark ink */
.ncov.t-engineer_guide{background:linear-gradient(135deg,#e8f1ff,#c2daff)}
.ncov.t-engineer_guide .novl{color:#173a86}.ncov.t-engineer_guide .k{color:#2f5fc4}
.ncov.t-industry_standard{background:linear-gradient(135deg,#f2f4f8,#d6dde8)}
.ncov.t-industry_standard .novl{color:#2f3c54}.ncov.t-industry_standard .k{color:#5a6884}
.ncov.t-industry_experience{background:linear-gradient(135deg,#e6f6e1,#c2e8bb)}
.ncov.t-industry_experience .novl{color:#215e17}.ncov.t-industry_experience .k{color:#3a8a2a}
.ncov.t-news{background:linear-gradient(135deg,#efecf8,#d4cdea)}
.ncov.t-news .novl{color:#443873}.ncov.t-news .k{color:#6a5da8}
.ncov.t-new_product{background:linear-gradient(135deg,#f6efe0,#e7d4b4)}
.ncov.t-new_product .novl{color:#6d4e21}.ncov.t-new_product .k{color:#9d7231}
.ncard .cb{padding:15px 18px 18px;display:flex;flex-direction:column;gap:8px;flex:1}
.ncard .kind{font-size:10.5px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:#1A56DB}
.ncard h3.ntitle{margin:0;font-size:16.5px;font-weight:800;line-height:1.32;color:#17203a}
.ncard h3{margin:0;font-size:17px;line-height:1.35;color:#17203a}
.ncard .cs{font-size:13.5px;color:#5a6884;line-height:1.5;flex:1}
.ncard .go{font-size:13.5px;font-weight:800;color:#41A62A}
@media (max-width:760px){
  .nhero{min-height:250px}
  .nhero .in{padding:24px 18px}
  .nhero h1{font-size:27px}
  .nhero .sub{font-size:15px}
  .art{padding:22px 18px}
  .art .lead{font-size:15.5px;line-height:1.66;margin:0 0 16px}
  .art h2{font-size:18px;margin:20px 0 8px}
  .art p{font-size:14.5px;line-height:1.7;margin:0 0 10px}
  .ncards{padding:4px 18px 6px;gap:16px}
  .nsec{padding:0 18px}
  .nsechd{min-height:118px;margin:24px 0 14px}
  .nsechd .t{padding:15px 18px}
  .nsechd .t h2{font-size:20px}
  .nrow .ncard{flex:0 0 230px}
}
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
            '<h1>%s</h1><p class="sub">%s</p>%s%s<div style="margin-top:16px">%s</div></div></section>') % (
        CSS, bg, esc(L(TOPICS[topic_key(a)]["label"], lang)), esc(title), esc(L(a.get("subtitle", {}), lang)),
        chips_html(a, lang), ('<div class="ntags">%s</div>' % tags) if tags else "", hp.hero_cta(lang))
    lead_img = a.get("lead_img", "")
    limg = ('<img class="leadimg" src="%s" alt="" loading="lazy" onerror="this.remove()">' % esc(lead_img)) if lead_img else ""
    body = ('<div class="art"><div class="leadrow">%s<p class="lead">%s</p></div>'
            % (limg, esc(L(a.get("lead", {}), lang))))
    for sec in L(a.get("sections", {}), lang):
        if sec.get("h"):
            body += "<h2>%s</h2>" % esc(sec["h"])
        for p in sec.get("ps", []):
            body += "<p>%s</p>" % esc(p)
    ctas = a.get("cta", [])
    if ctas:
        body += '<div class="nctarow">' + "".join(
            '<a class="ncta" href="%s">%s</a>' % (hp.Lx(lang, c["url"]), esc(L(c.get("label", {}), lang)))
            for c in ctas) + '</div>'
    body += '<a class="nback" href="%s">%s</a></div>' % (hp.Lx(lang, HUB), esc(ui["back"]))
    crumb = [(ui["home"], "/"), (ui["hub_title"], HUB), (title, path)]
    content = hp.page(lang, path, title + " | ETIA", esc(L(a.get("subtitle", {}), lang)),
                      title, "", body, crumb, active="insights", trust=False, hero=hero,
                      langs=hp.NAV_PILLAR_LANGS, keywords=seo_keywords(a))
    hp.write(lang, path, content)
    if lang == "en":
        hp.track(path, "core")

def _card(a, lang, ui):
    # Cover = a topic-colored gradient block (no photo). Eyebrow (topic label) +
    # the full article title sit on the color; the card body holds the industry
    # chips, subtitle and read link.
    key = topic_key(a)
    t = TOPICS.get(key, TOPICS["industry_standard"])
    cover = ('<div class="ncov t-%s"><div class="novl">'
             '<div class="k">%s</div><h3 class="ncovh">%s</h3></div></div>') % (
        key, esc(L(t["label"], lang)), esc(L(a["title"], lang)))
    return ('<a class="ncard" href="%s">%s<div class="cb">%s'
            '<p class="cs">%s</p><span class="go">%s</span></div></a>') % (
        hp.Lx(lang, HUB + a["slug"] + "/"), cover,
        chips_html(a, lang, groups=("ind",)),
        esc(L(a.get("subtitle", {}), lang)), esc(ui["read"]))

def build_hub(lang):
    ui = UI.get(lang, UI[SOURCE_LANG])
    arts = json.load(open(DATA, encoding="utf-8"))["articles"]
    # One unified grid — no News/Knowledge split; topic is shown by cover color.
    cards = "".join(_card(a, lang, ui) for a in arts)
    grid = '<div class="nsec"><div class="ncards">%s</div></div>' % cards
    # 20-year trust bar under the hero, then the article grid
    body = hp.home_trustbar(lang) + CSS + grid
    crumb = [(ui["home"], "/"), (ui["hub_title"], HUB)]
    # brand Insight hero — single main visual with a subtle Ken Burns zoom (no carousel)
    s = hp.HOME2.get(lang, hp.HOME2["en"])["sections"][2]
    hero = hp.hero_single_anim(lang, hp.section_banner(2, lang), s["eyebrow"], s["h2"], ui["hero_sub"])
    content = hp.page(lang, HUB, ui["hub_title"] + " | ETIA", ui["hub_lede"],
                      ui["hub_title"], "", body, crumb, active="insights", trust=False, hero=hero,
                      langs=hp.NAV_PILLAR_LANGS)
    hp.write(lang, HUB, content)
    if lang == "en":
        hp.track(HUB, "core")

def main():
    arts = json.load(open(DATA, encoding="utf-8"))["articles"]
    for lang in ["en", "zh", "vi", "th"]:
        build_hub(lang)
        for a in arts:
            build_article(a, lang)
        print("news:", hp.PREFIX[lang] + HUB, "+", len(arts), "articles")

if __name__ == "__main__":
    main()
