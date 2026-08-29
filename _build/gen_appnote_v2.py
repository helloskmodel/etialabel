#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Application Notes v2 — data-driven, 4 languages (EN/ZH/VI/TH).

Data: _build/data/appnotes/<slug>.json. Owns the /application-notes/ hub (4-lang
override) and one page per note. Structure per client briefs: Hero (title +
subtitle) -> Project Overview -> Application Requirements & Challenges ->
Solution & Core Advantages (intro + advantage list + optional spec sub-blocks +
optional image) -> Customer Value -> email CTA. Content only from client docs.
"""
import json, os
import gen_heatproof as hp
import gen_product as gp

BUILD = os.path.dirname(os.path.abspath(__file__))
ADIR = os.path.join(BUILD, "data", "appnotes")
HUB = "/application-notes/"
SOURCE_LANG = "zh"
esc = hp.esc

def note_industry(d):
    """The application note's industry key (pcb/auto/cable/steel/medical/outdoor),
    from the JSON 'industry' field. Empty if unset."""
    return (d.get("industry") or "").strip()

def note_banner(d):
    """Uniform rule (mirrors products): an application note shows its industry's
    banner. Falls back to a per-note 'banner' only when no industry is set."""
    return gp.INDUSTRY_BANNERS.get(note_industry(d), "") or d.get("banner", "")

UI = {
  "en": {"eyebrow": "Application Note", "info": "Basic Application Information",
         "problems": "Existing Process & Problems", "solution": "Solution",
         "advantages": "Application Advantages", "applications": "Typical Applications",
         "cta_btn": "Request Samples & TDS by Email",
         "cta_note": "No online download — samples and the technical datasheet are sent one-to-one by email.",
         "home": "Home", "notes": "Application Notes",
         "hub_lede": "Engineering application notes: the application, the problem, the solution and the advantages — by process."},
  "zh": {"eyebrow": "应用笔记", "info": "基础应用信息",
         "problems": "现有工艺及问题", "solution": "解决方案", "advantages": "应用优势", "applications": "典型应用",
         "cta_btn": "邮件申请样品 & TDS",
         "cta_note": "本页无在线下载，样品与技术数据表仅通过邮件一对一发送。",
         "home": "首页", "notes": "应用笔记",
         "hub_lede": "工程应用笔记：逐个应用讲清基础信息、现有问题、解决方案与应用优势。"},
  "vi": {"eyebrow": "Ghi chú ứng dụng", "info": "Thông tin ứng dụng cơ bản",
         "problems": "Quy trình hiện tại & vấn đề", "solution": "Giải pháp",
         "advantages": "Ưu điểm ứng dụng", "applications": "Ứng dụng điển hình", "cta_btn": "Yêu cầu mẫu & TDS qua Email",
         "cta_note": "Không tải xuống trực tuyến — mẫu và bảng dữ liệu kỹ thuật được gửi riêng qua email.",
         "home": "Trang chủ", "notes": "Ghi chú ứng dụng",
         "hub_lede": "Ghi chú ứng dụng kỹ thuật: thông tin cơ bản, vấn đề, giải pháp và ưu điểm — theo quy trình."},
  "th": {"eyebrow": "บันทึกการใช้งาน", "info": "ข้อมูลการใช้งานพื้นฐาน",
         "problems": "กระบวนการปัจจุบันและปัญหา", "solution": "โซลูชัน",
         "advantages": "ข้อได้เปรียบในการใช้งาน", "applications": "การใช้งานทั่วไป", "cta_btn": "ขอตัวอย่าง & TDS ทางอีเมล",
         "cta_note": "ไม่มีการดาวน์โหลดออนไลน์ — ตัวอย่างและเอกสารข้อมูลเทคนิคจะถูกส่งทางอีเมล",
         "home": "หน้าแรก", "notes": "บันทึกการใช้งาน",
         "hub_lede": "บันทึกการใช้งานเชิงวิศวกรรม: ข้อมูลพื้นฐาน ปัญหา โซลูชัน และข้อได้เปรียบ — ตามกระบวนการ"},
}

def L(node, lang):
    if not isinstance(node, dict):
        return hp._tr(lang, node) if lang in ("id", "ms") and node else (node or "")
    if node.get(lang):
        return node[lang]
    if lang in ("id", "ms"):
        return hp._tr(lang, node.get("en") or node.get(SOURCE_LANG) or "")
    return node.get(SOURCE_LANG) or ""

CSS = """
<style>
.anhero{position:relative;overflow:hidden;color:#fff;min-height:320px;display:flex;align-items:center;background:#143C96;border-bottom:2px solid #fff}
.anhero img.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center right;opacity:1}
.anhero::after{content:"";position:absolute;inset:0;z-index:1;background:linear-gradient(90deg,rgba(20,60,150,.90) 16%,rgba(20,60,150,.50) 54%,rgba(20,60,150,.08))}
.anhero .in{position:relative;z-index:2;max-width:1080px;margin:0 auto;width:100%;padding:40px 24px}
.anhero .k{font-size:12px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:#8fe063}
.anhero h1{color:#fff;font-family:var(--sans);font-weight:800;font-size:40px;letter-spacing:-.01em;margin:2px 0 10px;line-height:1.12;max-width:22em}
.anhero .sub{color:#eef3ff;font-size:18px;font-weight:700;line-height:1.5;margin:0;max-width:44em}
.ansec{max-width:900px;margin:0 auto;padding:30px 24px}
.aneye{font-size:12px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:#1A56DB}
.ansec h2{font-size:22px;color:#143C96;margin:8px 0 14px}
.ansec p.tx{font-size:16px;line-height:1.78;color:#2c3a58;margin:0 0 14px}
.animg{width:100%;max-height:360px;object-fit:cover;border-radius:14px;margin:6px 0 20px;background:#e8eefb}
.angal{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px;margin:16px 0 20px}
.angfig{margin:0}
.angfig img{width:100%;aspect-ratio:3/4;object-fit:cover;border-radius:10px;background:#eef3fc;display:block}
.angfig figcaption{font-size:12.5px;color:#5a6885;margin-top:6px;text-align:center}
.anfacts{border:1px solid #e0e9f8;border-radius:12px;overflow:hidden;max-width:660px;margin:2px 0 0}
.anfrow{display:grid;grid-template-columns:180px 1fr}
.anfrow+.anfrow{border-top:1px solid #eef2f9}
.anfk{background:#f4f7fd;color:#143C96;font-weight:700;font-size:14px;padding:12px 16px}
.anfv{padding:12px 16px;font-size:14.5px;color:#2c3a58}
.anbul{list-style:none;padding:0;margin:6px 0 0;display:flex;flex-direction:column;gap:9px}
.anbul li{position:relative;padding-left:24px;font-size:15.5px;line-height:1.72;color:#41506e}
.anbul li::before{content:"";position:absolute;left:0;top:8px;width:11px;height:11px;border-radius:50%;background:#41A62A}
.anadv{list-style:none;padding:0;margin:14px 0 0;display:grid;grid-template-columns:1fr 1fr;gap:14px}
.anadv li{background:#f6f9ff;border:1px solid #e0e9f8;border-radius:12px;padding:15px 16px}
.anadv .lb{display:block;font-size:15px;font-weight:800;color:#143C96;margin:0 0 5px}
.anadv .tx{font-size:14px;line-height:1.62;color:#41506e;margin:0}
.anxsub{margin-top:22px}
.anxsub h3{font-size:16px;color:#0c2555;margin:0 0 10px}
.ancta{max-width:900px;margin:34px auto;background:linear-gradient(120deg,#143C96,#1A56DB);border-radius:16px;padding:30px;color:#fff}
.ancta h3{margin:0 0 8px;font-size:21px}
.ancta p{margin:0 0 16px;color:#dbe6ff;font-size:14.5px}
.anbtn{display:inline-block;background:#41A62A;color:#fff;font-weight:800;font-size:14.5px;padding:12px 22px;border-radius:9px;text-decoration:none}
.anbtn:hover{background:#358B22}
/* hub */
.anhub{max-width:1080px;margin:0 auto;padding:8px 24px 10px}
.angrid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:8px}
@media(max-width:900px){.angrid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:520px){.angrid{grid-template-columns:1fr}}
.ancard{display:block;background:#fff;border:1px solid #dbe3f1;border-radius:14px;overflow:hidden;text-decoration:none;color:#17203a;transition:box-shadow .15s,transform .15s}
.ancard:hover{box-shadow:0 10px 26px rgba(20,60,150,.14);transform:translateY(-2px)}
.ancard .cimg{width:100%;aspect-ratio:16/9;object-fit:cover;background:#e8eefb;display:block}
.ancard .cbody{padding:16px 17px}
.ancard h3{font-size:17px;color:#143C96;margin:0 0 7px;line-height:1.3}
.ancard p{font-size:13.5px;color:#5a6884;margin:0 0 10px;line-height:1.55}
.ancard .go{font-size:12.5px;font-weight:800;color:#1A56DB}
@media (max-width:760px){
  .anhero .in{padding:26px 18px}.anhero h1{font-size:27px}.anhero .sub{font-size:15px}
  .ansec{padding:20px 18px}.ansec h2{font-size:20px}.ansec p.tx{font-size:14.5px;line-height:1.7}
  .anadv{grid-template-columns:1fr}.ancta{padding:24px 20px}
}
</style>
"""

def _adv(items):
    return '<ul class="anadv">%s</ul>' % "".join(
        '<li><span class="lb">%s</span><p class="tx">%s</p></li>' % (esc(a.get("label", "")), esc(a.get("text", "")))
        for a in items)

def build_note(d, lang):
    ui = UI.get(lang, UI["en"])
    slug = d["slug"]
    path = HUB + slug + "/"
    title = L(d["title"], lang)
    subtitle = L(d.get("subtitle", {}), lang)
    banner = note_banner(d)
    bpos = d.get("banner_pos", "")
    bstyle = (' style="object-position:%s"' % esc(bpos)) if bpos else ""
    bg = ('<img class="bg" src="%s" alt="" loading="eager"%s onerror="this.style.display=\'none\'">' % (esc(banner), bstyle)) if banner else ""
    # Hero shows eyebrow + title only (subtitle kept in data for meta/hub, not
    # rendered in the hero — it crowded the banner).
    hero = ('%s<section class="anhero">%s<div class="in"><div class="k">%s</div>'
            '<h1>%s</h1><div style="margin-top:16px">%s</div></div></section>') % (
        CSS, bg, esc(ui["eyebrow"]), esc(title), hp.hero_cta(lang))

    def sec(eye, h, inner):
        return '<section class="ansec"><div class="aneye">%s</div><h2>%s</h2>%s</section>' % (esc(eye), esc(h), inner)

    def bullets(items):
        return '<ul class="anbul">%s</ul>' % "".join("<li>%s</li>" % esc(x) for x in items)

    def paras(v):  # intro may be a single string or a list of paragraphs
        if isinstance(v, list):
            return "".join('<p class="tx">%s</p>' % esc(x) for x in v if x)
        return ('<p class="tx">%s</p>' % esc(v)) if v else ""

    # Simple 4-point template: 1) basic info  2) existing process & problems
    # 3) solution (points)  4) application advantages.
    body = ""
    _n = [0]
    def nn():  # consecutive section numbers regardless of which sections exist
        _n[0] += 1
        return "%02d" % _n[0]

    # 1. Basic application information — facts table + location photos (gallery)
    info = L(d.get("info", {}), lang)
    gal = d.get("gallery", [])
    gal_html = ""
    if gal:
        figs = "".join(
            '<figure class="angfig"><img src="%s" alt="%s" loading="lazy" onerror="this.closest(\'figure\').remove()"><figcaption>%s</figcaption></figure>'
            % (esc(g.get("img", "")), esc(L(g.get("caption", {}), lang)), esc(L(g.get("caption", {}), lang)))
            for g in gal)
        gal_html = '<div class="angal">%s</div>' % figs
    if info or gal_html:
        rows = "".join('<div class="anfrow"><span class="anfk">%s</span><span class="anfv">%s</span></div>'
                       % (esc(i.get("label", "")), esc(i.get("value", ""))) for i in info)
        facts = ('<div class="anfacts">%s</div>' % rows) if info else ""
        body += sec(nn(), ui["info"], facts + gal_html)

    # 2. Existing process & problems — intro paragraph + problem bullets
    prob = d.get("problems", {})
    p_intro = L(prob.get("intro", {}), lang)
    p_items = L(prob.get("items", {}), lang)
    inner = paras(p_intro)
    if p_items:
        inner += bullets(p_items)
    p_outro = L(prob.get("outro", {}), lang)
    if p_outro:
        inner += paras(p_outro)
    if inner:
        body += sec(nn(), ui["problems"], inner)

    # 3. Solution — optional intro + labelled points (+ optional image/gallery)
    sol = ""
    solution = d.get("solution", {})
    s_intro = L(solution.get("intro", {}), lang)
    sol += paras(s_intro)
    img = d.get("image", "")
    if img:
        sol += '<img class="animg" src="%s" alt="" loading="lazy" onerror="this.remove()">' % esc(img)
    points = L(solution.get("points", {}), lang)
    if points:
        sol += _adv(points)
    if sol:
        body += sec(nn(), ui["solution"], sol)

    # 4. Application advantages — bullet list
    adv = L(d.get("advantages", {}), lang)
    if adv:
        body += sec(nn(), ui["advantages"], bullets(adv))

    # 5. Typical applications — bullet list
    apps = L(d.get("applications", {}), lang)
    if apps:
        body += sec(nn(), ui["applications"], bullets(apps))

    contact = hp.Lx(lang, "/contact/")
    body += ('<div class="ancta"><h3>%s</h3><p>%s</p><a class="anbtn" href="%s">%s</a></div>' % (
        esc(ui["cta_btn"]), esc(ui["cta_note"]), contact, esc(ui["cta_btn"])))

    crumb = [(ui["home"], "/"), (ui["notes"], HUB), (title, path)]
    content = hp.page(lang, path, title + " | ETIA", L(d.get("seo_desc", {}), lang) or subtitle or title,
                      title, "", body, crumb, active="insights", trust=False, hero=hero,
                      langs=d.get("langs", hp.NAV_PILLAR_LANGS))
    hp.write(lang, path, content)
    if lang == "en":
        hp.track(path, "notes")

def build_hub(notes, lang):
    ui = UI.get(lang, UI["en"])
    cards = ""
    for d in notes:
        if lang not in d.get("langs", hp.NAV_PILLAR_LANGS):
            continue
        href = hp.Lx(lang, HUB + d["slug"] + "/")
        img = note_banner(d) or d.get("image", "")
        cimg = ('<img class="cimg" src="%s" alt="" loading="lazy" onerror="this.style.display=\'none\'">' % esc(img)) if img else ""
        cards += ('<a class="ancard" href="%s">%s<div class="cbody"><h3>%s</h3><p>%s</p>'
                  '<div class="go">%s →</div></div></a>') % (
            href, cimg, esc(L(d["title"], lang)),
            esc(L(d.get("subtitle", {}), lang) or L(d.get("seo_desc", {}), lang)),
            esc({"en": "Read", "zh": "阅读", "vi": "Xem", "th": "อ่าน"}.get(lang, "Read")))
    body = CSS + '<div class="anhub"><div class="angrid">%s</div></div>' % cards
    crumb = [(ui["home"], "/"), (ui["notes"], HUB)]
    content = hp.page(lang, HUB,
        ui["notes"] + " | ETIA", ui["hub_lede"], ui["notes"], ui["hub_lede"], body, crumb,
        active="insights", langs=hp.NAV_PILLAR_LANGS)
    hp.write(lang, HUB, content)

def main():
    slugs = sorted(f[:-5] for f in os.listdir(ADIR) if f.endswith(".json")) if os.path.isdir(ADIR) else []
    notes = [json.load(open(os.path.join(ADIR, s + ".json"), encoding="utf-8")) for s in slugs]
    # keep a stable hub order if a note declares "order"
    notes.sort(key=lambda d: d.get("order", 99))
    for lang in hp.NAV_PILLAR_LANGS:
        build_hub(notes, lang)
        for d in notes:
            if lang in d.get("langs", hp.NAV_PILLAR_LANGS):
                build_note(d, lang)
    print("appnotes v2:", [d["slug"] for d in notes], "x4 langs + hub")
    # BANNER AUDIT — every note should resolve to an industry banner
    for d in notes:
        ind = note_industry(d)
        flag = "" if (ind in gp.INDUSTRY_BANNERS or d.get("banner")) else "  <-- NO BANNER"
        print("  appnote banner:", d["slug"], "[%s]" % (ind or "own-banner"), flag)

if __name__ == "__main__":
    main()
