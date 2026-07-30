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
         "featured": "Featured Product Solutions", "home": "Home", "products": "Products",
         "key_benefits": "Key Benefits",
         "sc_apps": "Typical Applications", "sc_containers": "Typical Containers", "sc_products": "Recommended Products", "sc_chemicals": "Typical Chemicals"},
  "zh": {"positioning": "产品概述", "challenges": "核心制程挑战", "features": "核心特性",
         "benefits": "客户价值", "spec": "产品规格", "applications": "适用场景",
         "certs": "测试与认证", "cta_btn": "邮件申请样品 & TDS",
         "cta_note": "本页无在线下载，样品与 TDS 仅通过邮件一对一发送。",
         "featured": "推荐产品方案", "home": "首页", "products": "产品",
         "key_benefits": "核心优势",
         "sc_apps": "典型应用", "sc_containers": "典型容器", "sc_products": "推荐产品", "sc_chemicals": "典型化学介质"},
  "vi": {"positioning": "Tổng quan", "challenges": "Thách thức sản xuất", "features": "Đặc tính",
         "benefits": "Lợi ích", "spec": "Thông số kỹ thuật", "applications": "Ứng dụng",
         "certs": "Kiểm tra & Chứng nhận", "cta_btn": "Yêu cầu mẫu & TDS qua Email",
         "cta_note": "Không tải xuống trực tuyến — mẫu và TDS được gửi riêng qua email.",
         "featured": "Giải pháp sản phẩm tiêu biểu", "home": "Trang chủ", "products": "Sản phẩm",
         "key_benefits": "Lợi ích chính",
         "sc_apps": "Ứng dụng điển hình", "sc_containers": "Vật chứa điển hình", "sc_products": "Sản phẩm đề xuất", "sc_chemicals": "Hóa chất điển hình"},
  "th": {"positioning": "ภาพรวม", "challenges": "ความท้าทายในการผลิต", "features": "คุณสมบัติ",
         "benefits": "ประโยชน์", "spec": "ข้อมูลจำเพาะ", "applications": "การใช้งาน",
         "certs": "การทดสอบและการรับรอง", "cta_btn": "ขอตัวอย่าง & TDS ทางอีเมล",
         "cta_note": "ไม่มีการดาวน์โหลดออนไลน์ — ตัวอย่างและ TDS จะถูกส่งทางอีเมล",
         "featured": "โซลูชันผลิตภัณฑ์แนะนำ", "home": "หน้าแรก", "products": "สินค้า",
         "key_benefits": "ประโยชน์หลัก",
         "sc_apps": "การใช้งานทั่วไป", "sc_containers": "ภาชนะทั่วไป", "sc_products": "ผลิตภัณฑ์แนะนำ", "sc_chemicals": "สารเคมีทั่วไป"},
}

def L(node, lang):
    if not isinstance(node, dict):
        return node or ""
    return node.get(lang) or node.get(SOURCE_LANG) or ""

CSS = """
<style>
.phero{position:relative;overflow:hidden;color:#fff;min-height:250px;display:flex;align-items:flex-end;background:#143C96;border-bottom:2px solid #fff}
.phero img.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center right;opacity:1}
.phero::after{content:"";position:absolute;inset:0;z-index:1;background:linear-gradient(90deg,rgba(20,60,150,.90) 16%,rgba(20,60,150,.50) 54%,rgba(20,60,150,.08))}
.phero .in{position:relative;z-index:2;max-width:1080px;margin:0 auto;width:100%;padding:38px 24px}
.phero .k{font-size:12px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:#8fe063}
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
.ptbl tbody tr.grp td{background:#eef3fb;color:#143C96;font-weight:800;font-size:12px;letter-spacing:.04em;text-transform:uppercase;padding:9px 14px}
.ptnote{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:8px}
.ptnote li{position:relative;padding-left:20px;font-size:14px;line-height:1.6;color:#5a6885}
.ptnote li::before{content:"";position:absolute;left:0;top:7px;width:8px;height:8px;border-radius:2px;background:#dbe7fb}
.pfeat{display:grid;grid-template-columns:1fr;gap:20px}
.pfeat .pimg{width:100%;aspect-ratio:16/10;object-fit:cover;border-radius:12px;background:#e8eefb}
.pcta{max-width:900px;margin:34px auto;background:linear-gradient(120deg,#143C96,#1A56DB);border-radius:16px;padding:30px 30px;color:#fff}
.pcta h3{margin:0 0 8px;font-size:21px}
.pcta p{margin:0 0 16px;color:#dbe6ff;font-size:14.5px}
.pwhy{font-size:16px;line-height:1.75;color:#2c3a58;margin:0 0 16px}
.phl{background:linear-gradient(120deg,#0e1c3f,#1a3d8f);border-radius:16px;padding:26px 28px;color:#fff}
.phl-eye{font-size:12px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:#8fe36a}
.phl-t{color:#fff;font-size:24px;margin:8px 0 12px;line-height:1.2}
.phl-b{color:#dbe6ff;font-size:15.5px;line-height:1.75;margin:0 0 14px}
.phl .plist li{color:#eaf1ff}
.phl .plist li::before{background:#8fe36a}
.phl-links{display:flex;flex-wrap:wrap;gap:12px;margin-top:18px}
.phl-lnk{display:inline-block;background:rgba(255,255,255,.14);color:#fff;font-weight:700;font-size:13.5px;padding:9px 16px;border-radius:8px;text-decoration:none;border:1px solid rgba(255,255,255,.25)}
.phl-lnk:hover{background:rgba(255,255,255,.26)}
.pscn{display:grid;grid-template-columns:repeat(auto-fill,minmax(255px,1fr));gap:16px}
.pscncard{border:1px solid #e3eaf6;border-radius:14px;padding:18px;background:#fff;display:flex;flex-direction:column;gap:6px}
.pscncard .tmp{font-size:17px;font-weight:800;color:#41A62A;line-height:1.2}
.pscncard .pr{font-size:11.5px;font-weight:700;color:#8593ad;text-transform:uppercase;letter-spacing:.05em}
.pscncard h3{margin:2px 0 0;font-size:16px;color:#143C96;line-height:1.3}
.pscncard p{margin:0;font-size:14px;line-height:1.6;color:#41506e}
.pscncard .ap{margin-top:auto;padding-top:8px;font-size:12.5px;color:#5a6885;line-height:1.55;border-top:1px solid #eef2f9}
.pscn-sub{font-size:12.5px;line-height:1.55;color:#41506e;margin-top:4px}
.pscn-lb{display:block;font-size:10px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:#8593ad;margin-bottom:1px}
.pscncard .pscn-sub:first-of-type{margin-top:8px;padding-top:8px;border-top:1px solid #eef2f9}
/* temperature tab bar — same component as the industry "Choose a category" */
.scnfc{margin-top:6px}
.scnfcrow{display:flex;align-items:flex-end;gap:2px;border-bottom:1px solid #dbe3f1}
.scnar{flex:none;width:34px;height:46px;border:none;background:transparent;color:#143C96;font-size:26px;line-height:1;cursor:pointer;opacity:.6}
.scnar:hover{opacity:1}
.scntabs{display:flex;gap:4px;overflow-x:auto;flex:1;justify-content:center;-webkit-overflow-scrolling:touch}
.scntabs::-webkit-scrollbar{height:0}
.scntab{flex:none;font-size:13.5px;font-weight:700;line-height:1.25;padding:10px 16px;cursor:pointer;white-space:nowrap;background:transparent;color:#143C96;border:none;border-radius:9px 9px 0 0;position:relative;margin-bottom:-1px;font-family:inherit}
.scntab.on{background:#5b6ee8;color:#fff}
.scntab.on::after{content:"";position:absolute;left:0;right:0;bottom:0;height:3px;background:#1A56DB}
#scnpanel{margin-top:20px;max-width:760px;margin-left:auto;margin-right:auto}
#scnpanel .pscncard+.pscncard{margin-top:14px}
/* dimensional container around the temperature tabs + panel */
.scnbox{background:#f4f7ff;border:1px solid #e3eaf6;border-radius:16px;padding:16px 18px 22px;box-shadow:0 8px 26px rgba(20,60,150,.08)}
.scnbox .scnfcrow{border-bottom-color:#d6e0f2}
#scnpanel .pscncard{background:#fff;border-color:#dbe6fb;box-shadow:0 6px 18px rgba(20,60,150,.1)}
@media(max-width:760px){.scntab{font-size:12.5px;padding:9px 13px}.scnbox{padding:12px 12px 18px}}
@media (max-width:760px){
  .phero .in{padding:26px 18px}.phero h1{font-size:24px}.phero .tl{font-size:15.5px}
  .psec{padding:20px 18px}.psec h2{font-size:20px}.psec .pos{font-size:14.5px;line-height:1.65}
  .plist li{font-size:14.5px}.pcta{padding:24px 20px}
}
</style>
"""

def section(eye, h, inner):
    eyehtml = ('<div class="peye">%s</div>' % esc(eye)) if eye else ""
    return '<section class="psec">%s<h2>%s</h2>%s</section>' % (eyehtml, esc(h), inner)

def highlight_html(h, lang):
    pts = L(h.get("points", {}), lang)
    links = ""
    for lk in h.get("links", []):
        links += '<a class="phl-lnk" href="%s">%s →</a>' % (
            hp.Lx(lang, "/products/item/%s/" % lk["slug"]), esc(L(lk.get("label", {}), lang)))
    linkshtml = ('<div class="phl-links">%s</div>' % links) if links else ""
    return ('<section class="psec"><div class="phl"><div class="phl-eye">%s</div>'
            '<h2 class="phl-t">%s</h2><p class="phl-b">%s</p>%s%s</div></section>') % (
        esc(L(h.get("eyebrow", {}), lang)), esc(L(h.get("title", {}), lang)),
        esc(L(h.get("body", {}), lang)), (ul(pts, "ok") if pts else ""), linkshtml)

def _temp_color(mid):
    """Cold -> warm colour for a temperature bar, keyed to absolute °C."""
    if mid < -50:  return "#1547d6"   # cryogenic — deep blue
    if mid < 10:   return "#2b9fd6"   # frozen / cold chain — cyan
    if mid < 40:   return "#8aa0c0"   # ambient — grey
    if mid < 200:  return "#e6a23a"   # warm — amber
    if mid < 600:  return "#ef7a2a"   # hot — orange
    return "#e0492a"                  # ultra-high — red

def _segcolor(s):
    if isinstance(s.get("lo"), (int, float)) and isinstance(s.get("hi"), (int, float)):
        return _temp_color((s["lo"] + s["hi"]) / 2.0)
    return "#8aa0c0"

def _scn_panel(s, ui):
    """The description card shown below the selected temperature tab. One product =
    one card; extra cards stack here when a temperature maps to several products."""
    def subblock(label, text):
        return '<div class="pscn-sub"><span class="pscn-lb">%s</span>%s</div>' % (esc(label), esc(text))
    title = ("%s %s" % (s.get("icon", ""), s.get("title", ""))).strip()
    apps = s.get("apps", "")
    sub = ""
    apline = ""
    if isinstance(apps, list):
        if apps:
            sub += subblock(ui["sc_apps"], " · ".join(apps))
    elif apps:
        apline = '<div class="ap">%s</div>' % esc(apps)
    if s.get("containers"):
        sub += subblock(ui["sc_containers"], s["containers"])
    if s.get("chemicals"):
        sub += subblock(ui["sc_chemicals"], s["chemicals"])
    if s.get("products"):
        sub += subblock(ui["sc_products"], s["products"])
    return ('<div class="pscncard"><div class="pr">%s</div><h3>%s</h3><p>%s</p>%s%s</div>') % (
        esc(s.get("process", "")), esc(title), esc(s.get("desc", "")), sub, apline)

def scenarios_html(items, ui):
    # Temperature tab bar — same component as the industry "Choose a category":
    # text tabs = temperature ranges, arrows scroll, selected tab highlighted;
    # the selected temperature's description card renders below.
    cats = [{"tab": s.get("temp", ""), "html": _scn_panel(s, ui)} for s in items]
    static_tabs = "".join(
        '<button type="button" class="scntab%s">%s</button>' % ((" on" if i == 0 else ""), esc(c["tab"]))
        for i, c in enumerate(cats))
    static_panel = cats[0]["html"] if cats else ""
    bar = ('<div class="scnbox"><div class="scnfc"><div class="scnfcrow">'
           '<button class="scnar" type="button" onclick="scnScroll(-1)">&lsaquo;</button>'
           '<div class="scntabs" id="scntabs">%s</div>'
           '<button class="scnar" type="button" onclick="scnScroll(1)">&rsaquo;</button>'
           '</div><div id="scnpanel">%s</div></div></div>') % (static_tabs, static_panel)
    js = ('<script>(function(){var C=%s;'
          'function render(i){var t=document.getElementById("scntabs"),p=document.getElementById("scnpanel");t.innerHTML="";'
          'C.forEach(function(c,j){var b=document.createElement("button");b.type="button";b.className="scntab"+(j===i?" on":"");'
          'b.textContent=c.tab;b.onclick=function(){render(j);b.scrollIntoView({inline:"center",block:"nearest",behavior:"smooth"});};'
          't.appendChild(b);});p.innerHTML=C[i].html;}'
          'window.scnScroll=function(d){document.getElementById("scntabs").scrollBy({left:d*180,behavior:"smooth"});};'
          'render(0);})();</script>') % json.dumps(cats, ensure_ascii=False)
    return bar + js

def ul(items, cls=""):
    return '<ul class="plist %s">%s</ul>' % (cls, "".join("<li>%s</li>" % esc(x) for x in items))

def spec_table(tbl, lang):
    """Render a per-row product table. Cells may be plain strings or {lang} dicts."""
    heads = L(tbl.get("headers", {}), lang)
    ncols = len(heads)
    thead = "".join("<th>%s</th>" % esc(h) for h in heads)
    rows_html = ""
    for row in tbl.get("rows", []):
        # group divider row: spans all columns
        if isinstance(row, dict) and row.get("group"):
            rows_html += '<tr class="grp"><td colspan="%d">%s</td></tr>' % (ncols, esc(L(row["group"], lang)))
            continue
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
    # banner_pos: optional object-position override so a page can steer which part
    # of the photo shows (e.g. "center bottom" to reveal the bottles). Defaults to
    # the shared "center right" crop used by every other hero.
    bpos = d.get("banner_pos", "")
    bstyle = (' style="object-position:%s"' % esc(bpos)) if bpos else ""
    bg = ('<img class="bg" src="%s" alt="" loading="eager"%s onerror="this.style.display=\'none\'">' % (esc(banner), bstyle)) if banner else ""
    contact = hp.Lx(lang, "/contact/")
    # tagline stays in data for the meta description; hero_tagline:false hides it from the hero
    tl_html = ('<p class="tl">%s</p>' % esc(L(d.get("tagline", {}), lang))) if d.get("hero_tagline", True) else ""
    hero = ('%s<section class="phero">%s<div class="in"><div class="k">%s</div>'
            '<h1>%s</h1>%s<a class="pbtn" href="%s">%s</a></div></section>') % (
        CSS, bg, esc(L(d.get("eyebrow", {}), lang) or ui["products"]), esc(title), tl_html, contact, esc(ui["cta_btn"]))

    body = ""
    if L(d.get("positioning", {}), lang):
        body += section(ui["positioning"], ui["positioning"], '<p class="pos">%s</p>' % esc(L(d["positioning"], lang)))
    if d.get("highlight") and L(d["highlight"].get("title", {}), lang):
        body += highlight_html(d["highlight"], lang)
    if L(d.get("challenges", {}), lang):
        body += section(ui["challenges"], ui["challenges"], ul(L(d["challenges"], lang), "warn"))
    if L(d.get("features", {}), lang):
        pimg = d.get("product_img", "")
        img = ('<img class="pimg" src="%s" alt="" loading="lazy" onerror="this.remove()">' % esc(pimg)) if pimg else ""
        body += section(ui["features"], ui["features"], '<div class="pfeat">%s%s</div>' % (img, ul(L(d["features"], lang), "ok")))
    if L(d.get("benefits", {}), lang):
        body += section(ui["benefits"], ui["benefits"], ul(L(d["benefits"], lang), "ok"))
    if d.get("why"):
        w = d["why"]
        heading = L(w.get("heading", {}), lang)
        # Why (rationale) and Benefit (key benefits list) are separate sections.
        if L(w.get("intro", {}), lang):
            body += section("", heading or ui["benefits"], '<p class="pwhy">%s</p>' % esc(L(w["intro"], lang)))
        if L(w.get("items", {}), lang):
            body += section("", ui["key_benefits"], ul(L(w["items"], lang), "ok"))
    if L(d.get("scenarios", {}), lang):
        body += section("", ui["applications"], scenarios_html(L(d["scenarios"], lang), ui))
    if L(d.get("featured", {}), lang):
        body += section("", ui["featured"], ul(L(d["featured"], lang), "ok"))
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

    # No products hub — breadcrumb is Home > Title (matches the industry pages)
    crumb = [(ui["home"], "/"), (title, path)]
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
