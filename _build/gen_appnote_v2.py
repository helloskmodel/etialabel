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

BUILD = os.path.dirname(os.path.abspath(__file__))
ADIR = os.path.join(BUILD, "data", "appnotes")
HUB = "/application-notes/"
SOURCE_LANG = "zh"
esc = hp.esc

UI = {
  "en": {"eyebrow": "Application Note", "overview": "Project Overview",
         "challenges": "Application Requirements & Challenges",
         "solution": "Solution & Core Advantages", "value": "Customer Value",
         "cta_btn": "Request Samples & TDS by Email",
         "cta_note": "No online download — samples and the technical datasheet are sent one-to-one by email.",
         "home": "Home", "notes": "Application Notes",
         "hub_lede": "Engineering application notes: the process, the challenge, the solution and the recommended ETIA material — by application."},
  "zh": {"eyebrow": "应用笔记", "overview": "项目应用概述",
         "challenges": "应用要求与挑战", "solution": "解决方案与核心优势",
         "value": "客户应用价值", "cta_btn": "邮件申请样品 & TDS",
         "cta_note": "本页无在线下载，样品与技术数据表仅通过邮件一对一发送。",
         "home": "首页", "notes": "应用笔记",
         "hub_lede": "工程应用笔记：逐个应用讲清制程、挑战、解决方案与推荐的 ETIA 材料。"},
  "vi": {"eyebrow": "Ghi chú ứng dụng", "overview": "Tổng quan dự án",
         "challenges": "Yêu cầu & thách thức ứng dụng", "solution": "Giải pháp & ưu điểm cốt lõi",
         "value": "Giá trị cho khách hàng", "cta_btn": "Yêu cầu mẫu & TDS qua Email",
         "cta_note": "Không tải xuống trực tuyến — mẫu và bảng dữ liệu kỹ thuật được gửi riêng qua email.",
         "home": "Trang chủ", "notes": "Ghi chú ứng dụng",
         "hub_lede": "Ghi chú ứng dụng kỹ thuật: quy trình, thách thức, giải pháp và vật liệu ETIA được đề xuất — theo từng ứng dụng."},
  "th": {"eyebrow": "บันทึกการใช้งาน", "overview": "ภาพรวมโครงการ",
         "challenges": "ข้อกำหนดและความท้าทายในการใช้งาน", "solution": "โซลูชันและข้อเด่นสำคัญ",
         "value": "คุณค่าที่ลูกค้าได้รับ", "cta_btn": "ขอตัวอย่าง & TDS ทางอีเมล",
         "cta_note": "ไม่มีการดาวน์โหลดออนไลน์ — ตัวอย่างและเอกสารข้อมูลเทคนิคจะถูกส่งทางอีเมล",
         "home": "หน้าแรก", "notes": "บันทึกการใช้งาน",
         "hub_lede": "บันทึกการใช้งานเชิงวิศวกรรม: กระบวนการ ความท้าทาย โซลูชัน และวัสดุ ETIA ที่แนะนำ — ตามการใช้งาน"},
}

def L(node, lang):
    if not isinstance(node, dict):
        return node or ""
    return node.get(lang) or node.get(SOURCE_LANG) or ""

CSS = """
<style>
.anhero{position:relative;overflow:hidden;color:#fff;min-height:250px;display:flex;align-items:flex-end;background:#0c2555}
.anhero img.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.4}
.anhero::after{content:"";position:absolute;inset:0;z-index:1;background:linear-gradient(90deg,rgba(9,20,48,.92),rgba(20,60,150,.5) 66%,transparent)}
.anhero .in{position:relative;z-index:2;max-width:1080px;margin:0 auto;width:100%;padding:40px 24px}
.anhero .k{font-size:12px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:#8fe36a}
.anhero h1{color:#fff;font-size:clamp(24px,4.3vw,37px);margin:10px 0 10px;line-height:1.16;max-width:22em}
.anhero .sub{color:#dbe6ff;font-size:17px;line-height:1.5;margin:0;max-width:44em}
.ansec{max-width:900px;margin:0 auto;padding:30px 24px}
.aneye{font-size:12px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:#1A56DB}
.ansec h2{font-size:22px;color:#143C96;margin:8px 0 14px}
.ansec p.tx{font-size:16px;line-height:1.78;color:#2c3a58;margin:0 0 14px}
.animg{width:100%;max-height:360px;object-fit:cover;border-radius:14px;margin:6px 0 20px;background:#e8eefb}
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
.angrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:18px;margin-top:8px}
.ancard{display:block;background:#fff;border:1px solid #dbe3f1;border-radius:14px;overflow:hidden;text-decoration:none;color:#17203a;transition:box-shadow .15s,transform .15s}
.ancard:hover{box-shadow:0 10px 26px rgba(20,60,150,.14);transform:translateY(-2px)}
.ancard .cimg{width:100%;aspect-ratio:16/9;object-fit:cover;background:#e8eefb;display:block}
.ancard .cbody{padding:16px 17px}
.ancard h3{font-size:17px;color:#143C96;margin:0 0 7px;line-height:1.3}
.ancard p{font-size:13.5px;color:#5a6884;margin:0 0 10px;line-height:1.55}
.ancard .go{font-size:12.5px;font-weight:800;color:#1A56DB}
@media (max-width:760px){
  .anhero .in{padding:26px 18px}.anhero h1{font-size:23px}.anhero .sub{font-size:15px}
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
    ui = UI.get(lang, UI[SOURCE_LANG])
    slug = d["slug"]
    path = HUB + slug + "/"
    title = L(d["title"], lang)
    subtitle = L(d.get("subtitle", {}), lang)
    banner = d.get("banner", "")
    bg = ('<img class="bg" src="%s" alt="" loading="eager" onerror="this.style.display=\'none\'">' % esc(banner)) if banner else ""
    # Hero shows eyebrow + title only (subtitle kept in data for meta/hub, not
    # rendered in the hero — it crowded the banner).
    hero = ('%s<section class="anhero">%s<div class="in"><div class="k">%s</div>'
            '<h1>%s</h1></div></section>') % (
        CSS, bg, esc(ui["eyebrow"]), esc(title))

    def sec(eye, h, inner):
        return '<section class="ansec"><div class="aneye">%s</div><h2>%s</h2>%s</section>' % (esc(eye), esc(h), inner)

    body = ""
    if L(d.get("overview", {}), lang):
        body += sec(ui["eyebrow"], ui["overview"], '<p class="tx">%s</p>' % esc(L(d["overview"], lang)))
    if L(d.get("challenges", {}), lang):
        body += sec(ui["challenges"], ui["challenges"], '<p class="tx">%s</p>' % esc(L(d["challenges"], lang)))

    # Solution: intro + optional image + advantage list + optional spec sub-blocks
    sol = ""
    if L(d.get("solution_intro", {}), lang):
        sol += '<p class="tx">%s</p>' % esc(L(d["solution_intro"], lang))
    img = d.get("image", "")
    if img:
        sol += '<img class="animg" src="%s" alt="" loading="lazy" onerror="this.remove()">' % esc(img)
    adv = d.get("advantages", {}).get(lang) or d.get("advantages", {}).get(SOURCE_LANG) or []
    if adv:
        sol += _adv(adv)
    extra = d.get("extra", {}).get(lang) or d.get("extra", {}).get(SOURCE_LANG) or []
    for block in extra:
        sol += '<div class="anxsub"><h3>%s</h3>%s</div>' % (esc(block.get("heading", "")), _adv(block.get("items", [])))
    if sol:
        body += sec(ui["solution"], ui["solution"], sol)

    if L(d.get("value", {}), lang):
        body += sec(ui["value"], ui["value"], '<p class="tx">%s</p>' % esc(L(d["value"], lang)))

    contact = hp.Lx(lang, "/contact/")
    body += ('<div class="ancta"><h3>%s</h3><p>%s</p><a class="anbtn" href="%s">%s</a></div>' % (
        esc(ui["cta_btn"]), esc(ui["cta_note"]), contact, esc(ui["cta_btn"])))

    crumb = [(ui["home"], "/"), (ui["notes"], HUB), (title, path)]
    content = hp.page(lang, path, title + " | ETIA", L(d.get("seo_desc", {}), lang) or subtitle or title,
                      title, "", body, crumb, active="insights", trust=False, hero=hero,
                      langs=d.get("langs", ["en", "zh", "vi", "th"]))
    hp.write(lang, path, content)
    if lang == "en":
        hp.track(path, "notes")

def build_hub(notes, lang):
    ui = UI.get(lang, UI[SOURCE_LANG])
    cards = ""
    for d in notes:
        if lang not in d.get("langs", ["en", "zh", "vi", "th"]):
            continue
        href = hp.Lx(lang, HUB + d["slug"] + "/")
        img = d.get("banner", "") or d.get("image", "")
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
        active="insights", langs=["en", "zh", "vi", "th"])
    hp.write(lang, HUB, content)

def main():
    slugs = sorted(f[:-5] for f in os.listdir(ADIR) if f.endswith(".json")) if os.path.isdir(ADIR) else []
    notes = [json.load(open(os.path.join(ADIR, s + ".json"), encoding="utf-8")) for s in slugs]
    # keep a stable hub order if a note declares "order"
    notes.sort(key=lambda d: d.get("order", 99))
    for lang in ["en", "zh", "vi", "th"]:
        build_hub(notes, lang)
        for d in notes:
            if lang in d.get("langs", ["en", "zh", "vi", "th"]):
                build_note(d, lang)
    print("appnotes v2:", [d["slug"] for d in notes], "x4 langs + hub")

if __name__ == "__main__":
    main()
