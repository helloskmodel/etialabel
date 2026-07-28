#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Product Landing pages (part 4 of the per-industry content model).

Data: _build/data/products/<slug>.json. Renders into the live shell.
Structure: Hero (title + tagline + email CTA) -> Positioning -> Challenges
-> Features (+ image) -> Benefits -> Specifications -> Applications ->
Certifications -> email CTA (samples & TDS by email; no online download).
Per-page `langs`; en/zh/vi/th supported. Content only from client briefs.
"""
import json, os
import gen_heatproof as hp

BUILD = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.join(BUILD, "data", "products")
SOURCE_LANG = "zh"
esc = hp.esc

UI = {
  "en": {"positioning": "Overview", "challenges": "Process Challenges", "features": "Features",
         "benefits": "Benefits", "spec": "Specifications", "applications": "Applications",
         "certs": "Testing & Certifications", "cta_btn": "Request Samples & TDS by Email",
         "cta_note": "No online download — samples and the TDS are sent one-to-one by email.",
         "home": "Home", "products": "Products"},
  "zh": {"positioning": "产品概述", "challenges": "核心制程挑战", "features": "核心特性",
         "benefits": "客户价值", "spec": "产品规格", "applications": "适用场景",
         "certs": "测试与认证", "cta_btn": "邮件申请样品 & TDS",
         "cta_note": "本页无在线下载，样品与 TDS 仅通过邮件一对一发送。",
         "home": "首页", "products": "产品"},
  "vi": {"positioning": "Tổng quan", "challenges": "Thách thức sản xuất", "features": "Đặc tính",
         "benefits": "Lợi ích", "spec": "Thông số kỹ thuật", "applications": "Ứng dụng",
         "certs": "Kiểm tra & Chứng nhận", "cta_btn": "Yêu cầu mẫu & TDS qua Email",
         "cta_note": "Không tải xuống trực tuyến — mẫu và TDS được gửi riêng qua email.",
         "home": "Trang chủ", "products": "Sản phẩm"},
  "th": {"positioning": "ภาพรวม", "challenges": "ความท้าทายในการผลิต", "features": "คุณสมบัติ",
         "benefits": "ประโยชน์", "spec": "ข้อมูลจำเพาะ", "applications": "การใช้งาน",
         "certs": "การทดสอบและการรับรอง", "cta_btn": "ขอตัวอย่าง & TDS ทางอีเมล",
         "cta_note": "ไม่มีการดาวน์โหลดออนไลน์ — ตัวอย่างและ TDS จะถูกส่งทางอีเมล",
         "home": "หน้าแรก", "products": "สินค้า"},
}

def L(node, lang):
    if not isinstance(node, dict):
        return node or ""
    return node.get(lang) or node.get(SOURCE_LANG) or ""

CSS = """
<style>
.phero{position:relative;overflow:hidden;color:#fff;min-height:250px;display:flex;align-items:flex-end;background:#12224b}
.phero img.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.42}
.phero::after{content:"";position:absolute;inset:0;z-index:1;background:linear-gradient(90deg,rgba(9,20,48,.92),rgba(20,60,150,.5) 66%,transparent)}
.phero .in{position:relative;z-index:2;max-width:1080px;margin:0 auto;width:100%;padding:38px 24px}
.phero .k{font-size:12px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:#8fe36a}
.phero h1{color:#fff;font-size:clamp(25px,4.4vw,38px);margin:10px 0 10px;line-height:1.15;max-width:20em}
.phero .tl{color:#dbe6ff;font-size:18px;margin:0 0 18px;max-width:36em}
.pbtn{display:inline-block;background:#41A62A;color:#fff;font-weight:800;font-size:14.5px;padding:12px 22px;border-radius:9px;text-decoration:none}
.pbtn:hover{background:#358B22}
.psec{max-width:900px;margin:0 auto;padding:30px 24px}
.peye{font-size:12px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:#1A56DB}
.psec h2{font-size:22px;color:#143C96;margin:8px 0 14px}
.psec .pos{font-size:16px;line-height:1.75;color:#2c3a58;margin:0}
.plist{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:10px}
.plist li{position:relative;padding-left:26px;font-size:15px;line-height:1.7;color:#41506e}
.plist li::before{content:"";position:absolute;left:0;top:8px;width:12px;height:12px;border-radius:3px;background:#dbe7fb}
.plist.ok li::before{background:#41A62A;border-radius:50%}
.plist.warn li::before{background:#e6b23a}
.ptblwrap{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:0 0 14px;border:1px solid #e3eaf6;border-radius:12px}
.ptbl{border-collapse:collapse;width:100%;min-width:520px;font-size:14.5px}
.ptbl th,.ptbl td{text-align:left;padding:11px 14px;border-bottom:1px solid #eef2f9}
.ptbl thead th{background:#f4f7fd;color:#143C96;font-weight:800;font-size:12.5px;letter-spacing:.02em;text-transform:uppercase;white-space:nowrap}
.ptbl tbody tr:last-child td{border-bottom:0}
.ptbl td:first-child{font-weight:700;color:#1A56DB;white-space:nowrap}
.ptbl tbody tr.esd td:first-child{color:#41A62A}
.ptnote{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:8px}
.ptnote li{position:relative;padding-left:20px;font-size:14px;line-height:1.6;color:#5a6885}
.ptnote li::before{content:"";position:absolute;left:0;top:7px;width:8px;height:8px;border-radius:2px;background:#dbe7fb}
.pfeat{display:grid;grid-template-columns:1fr;gap:20px}
.pfeat .pimg{width:100%;aspect-ratio:16/10;object-fit:cover;border-radius:12px;background:#e8eefb}
.pcta{max-width:900px;margin:34px auto;background:linear-gradient(120deg,#143C96,#1A56DB);border-radius:16px;padding:30px 30px;color:#fff}
.pcta h3{margin:0 0 8px;font-size:21px}
.pcta p{margin:0 0 16px;color:#dbe6ff;font-size:14.5px}
@media (max-width:760px){
  .phero .in{padding:26px 18px}.phero h1{font-size:24px}.phero .tl{font-size:15.5px}
  .psec{padding:20px 18px}.psec h2{font-size:20px}.psec .pos{font-size:14.5px;line-height:1.65}
  .plist li{font-size:14.5px}.pcta{padding:24px 20px}
}
</style>
"""

def section(eye, h, inner):
    return '<section class="psec"><div class="peye">%s</div><h2>%s</h2>%s</section>' % (esc(eye), esc(h), inner)

def ul(items, cls=""):
    return '<ul class="plist %s">%s</ul>' % (cls, "".join("<li>%s</li>" % esc(x) for x in items))

def spec_table(tbl, lang):
    """Render a per-row product table. Cells may be plain strings or {lang} dicts."""
    heads = L(tbl.get("headers", {}), lang)
    thead = "".join("<th>%s</th>" % esc(h) for h in heads)
    rows_html = ""
    for row in tbl.get("rows", []):
        cells = row["cells"] if isinstance(row, dict) else row
        cls = " class=\"esd\"" if isinstance(row, dict) and row.get("esd") else ""
        tds = "".join("<td>%s</td>" % esc(L(c, lang)) for c in cells)
        rows_html += "<tr%s>%s</tr>" % (cls, tds)
    html = ('<div class="ptblwrap"><table class="ptbl"><thead><tr>%s</tr></thead>'
            '<tbody>%s</tbody></table></div>') % (thead, rows_html)
    notes = L(tbl.get("notes", {}), lang)
    if notes:
        html += '<ul class="ptnote">%s</ul>' % "".join("<li>%s</li>" % esc(n) for n in notes)
    return html

def build_lang(d, lang):
    ui = UI.get(lang, UI[SOURCE_LANG])
    slug = d["slug"]
    path = "/products/item/%s/" % slug
    title = L(d["title"], lang)
    banner = d.get("banner", "")
    bg = ('<img class="bg" src="%s" alt="" loading="eager" onerror="this.style.display=\'none\'">' % esc(banner)) if banner else ""
    contact = hp.Lx(lang, "/contact/")
    hero = ('%s<section class="phero">%s<div class="in"><div class="k">%s</div>'
            '<h1>%s</h1><p class="tl">%s</p><a class="pbtn" href="%s">%s</a></div></section>') % (
        CSS, bg, esc(ui["products"]), esc(title), esc(L(d.get("tagline", {}), lang)), contact, esc(ui["cta_btn"]))

    body = ""
    if L(d.get("positioning", {}), lang):
        body += section(ui["positioning"], ui["positioning"], '<p class="pos">%s</p>' % esc(L(d["positioning"], lang)))
    if L(d.get("challenges", {}), lang):
        body += section(ui["challenges"], ui["challenges"], ul(L(d["challenges"], lang), "warn"))
    if L(d.get("features", {}), lang):
        pimg = d.get("product_img", "")
        img = ('<img class="pimg" src="%s" alt="" loading="lazy" onerror="this.remove()">' % esc(pimg)) if pimg else ""
        body += section(ui["features"], ui["features"], '<div class="pfeat">%s%s</div>' % (img, ul(L(d["features"], lang), "ok")))
    if L(d.get("benefits", {}), lang):
        body += section(ui["benefits"], ui["benefits"], ul(L(d["benefits"], lang), "ok"))
    if d.get("spec_table"):
        body += section(ui["spec"], ui["spec"], spec_table(d["spec_table"], lang))
    elif L(d.get("spec", {}), lang):
        body += section(ui["spec"], ui["spec"], ul(L(d["spec"], lang)))
    if L(d.get("applications", {}), lang):
        body += section(ui["applications"], ui["applications"], ul(L(d["applications"], lang)))
    if L(d.get("certifications", {}), lang):
        body += section(ui["certs"], ui["certs"], ul(L(d["certifications"], lang), "ok"))
    body += ('<div class="pcta"><h3>%s</h3><p>%s</p><a class="pbtn" href="%s">%s</a></div>' % (
        esc(ui["cta_btn"]), esc(ui["cta_note"]), contact, esc(ui["cta_btn"])))

    crumb = [(ui["home"], "/"), (ui["products"], "/products/"), (title, path)]
    content = hp.page(lang, path, title + " | ETIA", esc(L(d.get("tagline", {}), lang)),
                      title, "", body, crumb, active="products", trust=False, hero=hero,
                      langs=d.get("langs", ["en", "zh"]))
    hp.write(lang, path, content)
    if lang == "en":
        hp.track(path, "products")

def main():
    slugs = [f[:-5] for f in os.listdir(PDIR) if f.endswith(".json")] if os.path.isdir(PDIR) else []
    for slug in sorted(slugs):
        d = json.load(open(os.path.join(PDIR, slug + ".json"), encoding="utf-8"))
        for lang in d.get("langs", ["en", "zh"]):
            build_lang(d, lang)
        print("product:", slug, d.get("langs"))

if __name__ == "__main__":
    main()
