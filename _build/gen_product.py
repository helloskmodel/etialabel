#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Product Landing pages (part 4 of the per-industry content model).

Data: _build/data/products/<slug>.json. Renders into the live shell.
Structure: Hero (title + tagline + email CTA) -> Positioning -> Challenges
-> Features (+ image) -> Benefits -> Specifications -> Applications ->
Certifications -> email CTA (samples & TDS by email; no online download).
Per-page `langs`; en/zh/vi/th supported. Content only from client briefs.
"""
import json, os, re
import gen_heatproof as hp

BUILD = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.join(BUILD, "data", "products")
SOURCE_LANG = "zh"
esc = hp.esc

# ---- Generated product image: a 4:3 label tile carrying a Code 39 barcode + the
# model code. Used as the uniform "product photo" for label lines that ship no
# photo (e.g. the E-Series polyimide family). Rendered as inline SVG (no files).
_CODE39 = {
    '0':'nnnwwnwnn','1':'wnnwnnnnw','2':'nnwwnnnnw','3':'wnwwnnnnn','4':'nnnwwnnnw',
    '5':'wnnwwnnnn','6':'nnwwwnnnn','7':'nnnwnnwnw','8':'wnnwnnwnn','9':'nnwwnnwnn',
    'A':'wnnnnwnnw','B':'nnwnnwnnw','C':'wnwnnwnnn','D':'nnnnwwnnw','E':'wnnnwwnnn',
    'F':'nnwnwwnnn','G':'nnnnnwwnw','H':'wnnnnwwnn','I':'nnwnnwwnn','J':'nnnnwwwnn',
    'K':'wnnnnnnww','L':'nnwnnnnww','M':'wnwnnnnwn','N':'nnnnwnnww','O':'wnnnwnnwn',
    'P':'nnwnwnnwn','Q':'nnnnnnwww','R':'wnnnnnwwn','S':'nnwnnnwwn','T':'nnnnwnwwn',
    'U':'wwnnnnnnw','V':'nwwnnnnnw','W':'wwwnnnnnn','X':'nwnnwnnnw','Y':'wwnnwnnnn',
    'Z':'nwwnwnnnn','-':'nwnnnnwnw','.':'wwnnnnwnn',' ':'nwwnnnwnn','*':'nwnnwnwnn',
}

def _model_code(slug):
    c = slug.upper()
    return re.sub(r'^XF(\d)', r'XF-\1', c)   # xf58 -> XF-58, xf-504 -> XF-504

def barcode_label_svg(code, eyebrow="POLYONICS"):
    """Inline SVG: a 4:3 printed-label tile — Code 39 barcode on top, model code below."""
    seq = "*" + "".join(ch for ch in code.upper() if ch in _CODE39) + "*"
    N, W = 1.0, 2.6
    x = 0.0; bars = []
    for ch in seq:
        pat = _CODE39.get(ch)
        if not pat:
            continue
        for i, e in enumerate(pat):
            w = W if e == 'w' else N
            if i % 2 == 0:      # even elements are bars
                bars.append((x, w))
            x += w
        x += N                  # narrow inter-character gap
    total = x or 1.0
    TARGET, X0, BY, BH = 208.0, 56.0, 78.0, 74.0
    sc = TARGET / total
    rects = "".join('<rect x="%.2f" y="%d" width="%.2f" height="%d" fill="#101828"/>'
                    % (X0 + bx * sc, BY, max(bw * sc, 0.4), BH) for bx, bw in bars)
    return (
        '<svg class="bclbl" viewBox="0 0 320 240" preserveAspectRatio="xMidYMid meet" '
        'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="%s">'
        '<rect width="320" height="240" fill="#eef3fc"/>'
        '<rect x="34" y="34" width="252" height="172" rx="10" fill="#fff" stroke="#dbe3f1"/>'
        '<text x="60" y="58" font-family="ui-monospace,Menlo,Consolas,monospace" font-size="8" '
        'letter-spacing="2.5" fill="#9fb0cf">%s</text>'
        '%s'
        '<text x="160" y="188" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace" '
        'font-size="24" font-weight="700" letter-spacing="2" fill="#143C96">%s</text>'
        '</svg>') % (esc(code), esc(eyebrow), rects, esc(code))

def is_eseries(slug):
    """The E-Series polyimide family (E-8xxx) — uniform barcode tile, no photos."""
    return bool(re.match(r'^e-8\d', slug.lower()))

UI = {
  "en": {"positioning": "Overview", "challenges": "Process Challenges", "features": "Features",
         "benefits": "Benefits", "spec": "Specifications", "applications": "Applications",
         "certs": "Testing & Certifications", "cta_btn": "Request Samples & TDS by Email",
         "cta_note": "No online download — samples and the TDS are sent one-to-one by email.",
         "featured": "Featured Product Solutions", "home": "Home", "products": "Products",
         "key_benefits": "Key Benefits", "structure": "Construction",
         "sc_apps": "Typical Applications", "sc_containers": "Typical Containers", "sc_products": "Recommended Products", "sc_chemicals": "Typical Chemicals", "sc_steril": "Typical Sterilization"},
  "zh": {"positioning": "产品概述", "challenges": "核心制程挑战", "features": "核心特性",
         "benefits": "客户价值", "spec": "产品规格", "applications": "适用场景",
         "certs": "测试与认证", "cta_btn": "邮件申请样品 & TDS",
         "cta_note": "本页无在线下载，样品与 TDS 仅通过邮件一对一发送。",
         "featured": "推荐产品方案", "home": "首页", "products": "产品",
         "key_benefits": "核心优势", "structure": "产品结构",
         "sc_apps": "典型应用", "sc_containers": "典型容器", "sc_products": "推荐产品", "sc_chemicals": "典型化学介质", "sc_steril": "灭菌方式"},
  "vi": {"positioning": "Tổng quan", "challenges": "Thách thức sản xuất", "features": "Đặc tính",
         "benefits": "Lợi ích", "spec": "Thông số kỹ thuật", "applications": "Ứng dụng",
         "certs": "Kiểm tra & Chứng nhận", "cta_btn": "Yêu cầu mẫu & TDS qua Email",
         "cta_note": "Không tải xuống trực tuyến — mẫu và TDS được gửi riêng qua email.",
         "featured": "Giải pháp sản phẩm tiêu biểu", "home": "Trang chủ", "products": "Sản phẩm",
         "key_benefits": "Lợi ích chính", "structure": "Cấu tạo",
         "sc_apps": "Ứng dụng điển hình", "sc_containers": "Vật chứa điển hình", "sc_products": "Sản phẩm đề xuất", "sc_chemicals": "Hóa chất điển hình", "sc_steril": "Phương pháp tiệt trùng"},
  "th": {"positioning": "ภาพรวม", "challenges": "ความท้าทายในการผลิต", "features": "คุณสมบัติ",
         "benefits": "ประโยชน์", "spec": "ข้อมูลจำเพาะ", "applications": "การใช้งาน",
         "certs": "การทดสอบและการรับรอง", "cta_btn": "ขอตัวอย่าง & TDS ทางอีเมล",
         "cta_note": "ไม่มีการดาวน์โหลดออนไลน์ — ตัวอย่างและ TDS จะถูกส่งทางอีเมล",
         "featured": "โซลูชันผลิตภัณฑ์แนะนำ", "home": "หน้าแรก", "products": "สินค้า",
         "key_benefits": "ประโยชน์หลัก", "structure": "โครงสร้าง",
         "sc_apps": "การใช้งานทั่วไป", "sc_containers": "ภาชนะทั่วไป", "sc_products": "ผลิตภัณฑ์แนะนำ", "sc_chemicals": "สารเคมีทั่วไป", "sc_steril": "วิธีการฆ่าเชื้อ"},
}

def L(node, lang):
    if not isinstance(node, dict):
        return node or ""
    # fall back to English for vi/th (readable internationally), then the zh source.
    return node.get(lang) or node.get("en") or node.get(SOURCE_LANG) or ""

CSS = """
<style>
.phero{position:relative;overflow:hidden;color:#fff;min-height:320px;display:flex;align-items:center;background:#143C96;border-bottom:2px solid #fff}
.phero img.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center right;opacity:1}
.phero::after{content:"";position:absolute;inset:0;z-index:1;background:linear-gradient(90deg,rgba(20,60,150,.90) 16%,rgba(20,60,150,.50) 54%,rgba(20,60,150,.08))}
.phero .in{position:relative;z-index:2;max-width:1080px;margin:0 auto;width:100%;padding:38px 24px}
.phero .k{font-size:12px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:#8fe063}
.phero h1{color:#fff;font-family:var(--sans);font-weight:800;font-size:40px;letter-spacing:-.01em;margin:2px 0 10px;line-height:1.12;max-width:20em}
.phero .tl{color:#eef3ff;font-size:18px;font-weight:700;margin:0 0 18px;max-width:40em}
.pbtn{display:inline-block;background:#41A62A;color:#fff;font-weight:800;font-size:14.5px;padding:12px 22px;border-radius:9px;text-decoration:none}
.pbtn:hover{background:#358B22}
.psec{max-width:900px;margin:0 auto;padding:15px 24px}
.psec:first-of-type{padding-top:26px}
.peye{font-size:12px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:#1A56DB}
.psec h2{font-size:22px;color:#143C96;margin:6px 0 10px}
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
.ptbl a.pmlink{display:inline-flex;align-items:center;gap:6px;color:#1A56DB;text-decoration:none;border-bottom:1.5px solid #bcd0f5;padding-bottom:1px}
.ptbl a.pmlink:hover{border-bottom-color:#1A56DB}
.ptbl a.pmlink .pmgo{font-weight:800;color:#41A62A}
.ptbl tbody tr.esd td:first-child{color:#41A62A}
.ptbl tbody tr.grp td{background:#eef3fb;color:#143C96;font-weight:800;font-size:12px;letter-spacing:.04em;text-transform:uppercase;padding:9px 14px}
.ptnote{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:8px}
.ptnote li{position:relative;padding-left:20px;font-size:14px;line-height:1.6;color:#5a6885}
.ptnote li::before{content:"";position:absolute;left:0;top:7px;width:8px;height:8px;border-radius:2px;background:#dbe7fb}
.pfeat{display:grid;grid-template-columns:210px 1fr;gap:24px;align-items:start}
@media(max-width:620px){.pfeat{grid-template-columns:1fr;gap:16px}.pfeat .pimg{max-width:100%}}
.pdiagram{margin:0;display:flex;gap:26px;align-items:center;justify-content:center;flex-wrap:wrap}
.pdiagram figure{margin:0;text-align:center}
.pdiagram img{max-width:100%;max-height:230px;border-radius:12px;background:#f4f7ff}
.pdiagram figcaption{font-size:12.5px;color:#5a6885;margin-top:8px;max-width:280px}
.pdleg{list-style:none;padding:0;margin:0;text-align:left;display:flex;flex-direction:column;gap:9px}
.pdleg li{font-size:14px;line-height:1.5;color:#41506e}
.pimg{width:100%;max-width:210px;aspect-ratio:16/10;object-fit:contain;border-radius:12px;background:#e8eefb}
.pimg.lbl{aspect-ratio:4/3;overflow:hidden;display:grid;place-items:center}
.pimg.lbl svg.bclbl{width:100%;height:100%;display:block}
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
/* two-column scenario card: left = process, right = products (name + material) */
.pscncard.pscn2{display:grid;grid-template-columns:1.5fr 1fr;gap:22px;align-items:start;flex-direction:unset}
.pscn-l{display:flex;flex-direction:column;gap:6px}
.pscn-r{border-left:1px solid #e6ecf6;padding-left:20px}
.pscn-rh{font-size:10px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:#8593ad;margin-bottom:6px}
.pscn-prod{padding:9px 0;border-bottom:1px solid #f0f3fa}
.pscn-prod:last-child{border-bottom:0}
.pscn-prod b{display:block;font-size:14px;color:#143C96;font-weight:700;line-height:1.3}
.pscn-prod span{font-size:12.5px;color:#5a6885}
@media(max-width:640px){.pscncard.pscn2{grid-template-columns:1fr;gap:14px}.pscn-r{border-left:0;border-top:1px solid #eef2f9;padding-left:0;padding-top:12px}}
/* temperature tab bar — same component as the industry "Choose a category" */
.scnfc{margin-top:6px}
.scnfcrow{display:flex;align-items:flex-end;gap:2px;border-bottom:1px solid #dbe3f1}
.scnar{flex:none;width:34px;height:46px;border:none;background:transparent;color:#143C96;font-size:26px;line-height:1;cursor:pointer;opacity:.6}
.scnar:hover{opacity:1}
.scntabs{display:flex;gap:4px;overflow-x:auto;flex:1;justify-content:safe center;-webkit-overflow-scrolling:touch}
.scntabs::-webkit-scrollbar{height:0}
.scntab{flex:none;font-size:13.5px;font-weight:700;line-height:1.25;padding:10px 16px;cursor:pointer;white-space:nowrap;background:transparent;color:#143C96;border:none;border-radius:9px 9px 0 0;position:relative;margin-bottom:-1px;font-family:inherit}
.scntab.on{background:#5b6ee8;color:#fff}
.scntab.on::after{content:"";position:absolute;left:0;right:0;bottom:0;height:3px;background:#1A56DB}
#scnpanel{margin-top:20px;max-width:820px;margin-left:auto;margin-right:auto}
#scnpanel .pscncard+.pscncard{margin-top:14px}
/* dimensional container around the temperature tabs + panel */
.scnbox{background:#f4f7ff;border:1px solid #e3eaf6;border-radius:16px;padding:16px 18px 22px;box-shadow:0 8px 26px rgba(20,60,150,.08)}
.scnbox .scnfcrow{border-bottom-color:#d6e0f2}
#scnpanel .pscncard{background:#fff;border-color:#dbe6fb;box-shadow:0 6px 18px rgba(20,60,150,.1)}
@media(max-width:760px){.scntab{font-size:12.5px;padding:9px 13px}.scnbox{padding:12px 12px 18px}}
@media (max-width:760px){
  .phero .in{padding:26px 18px}.phero h1{font-size:27px}.phero .tl{font-size:15.5px}
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

def _scn_panel(s, ui, lang="en"):
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
    if s.get("sterilization"):
        sub += subblock(ui["sc_steril"], s["sterilization"])
    if s.get("containers"):
        sub += subblock(ui["sc_containers"], s["containers"])
    if s.get("chemicals"):
        sub += subblock(ui["sc_chemicals"], s["chemicals"])
    # products_list = [{name, material}] renders a right-hand product column.
    # A plain "products" string stays a single-column sub-block (legacy behaviour).
    prods = s.get("products_list")
    if s.get("products") and not prods:
        sub += subblock(ui["sc_products"], s["products"])
    left = '<div class="pr">%s</div><h3>%s</h3><p>%s</p>%s%s' % (
        esc(s.get("process", "")), esc(title), esc(s.get("desc", "")), sub, apline)
    if prods:
        def _prow(p):
            nm = esc(p.get("name", ""))
            name_html = ('<a href="%s">%s</a>' % (hp.Lx(lang, p["url"]), nm)) if p.get("url") else nm
            return '<div class="pscn-prod"><b>%s</b><span>%s</span></div>' % (name_html, esc(p.get("material", "")))
        rows = "".join(_prow(p) for p in prods)
        right = '<div class="pscn-rh">%s</div>%s' % (esc(ui["sc_products"]), rows)
        return ('<div class="pscncard pscn2"><div class="pscn-l">%s</div>'
                '<div class="pscn-r">%s</div></div>') % (left, right)
    return '<div class="pscncard">%s</div>' % left

def scenarios_html(items, ui, lang="en"):
    # Temperature tab bar — same component as the industry "Choose a category":
    # text tabs = temperature ranges, arrows scroll, selected tab highlighted;
    # the selected temperature's description card renders below.
    cats = [{"tab": s.get("temp", ""), "html": _scn_panel(s, ui, lang)} for s in items]
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
        link = row.get("link") if isinstance(row, dict) else None
        tds = ""
        for i, c in enumerate(cells):
            txt = esc(L(c, lang))
            if link and i == 0:
                txt = '<a class="pmlink" href="%s">%s <span class="pmgo">→</span></a>' % (hp.Lx(lang, link), txt)
            tds += "<td>%s</td>" % txt
        rows_html += "<tr%s>%s</tr>" % (cls, tds)
    html = ('<div class="ptblwrap"><table class="ptbl"><thead><tr>%s</tr></thead>'
            '<tbody>%s</tbody></table></div>') % (thead, rows_html)
    notes = L(tbl.get("notes", {}), lang)
    if notes:
        html += '<ul class="ptnote">%s</ul>' % "".join("<li>%s</li>" % esc(n) for n in notes)
    return html

# Per-industry hero banners (same images used on the industry landing pages).
# Every product landing page shows its industry's banner; a product with its own
# `banner` still wins, otherwise it falls back to the industry banner here.
_COS = "https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com/"
INDUSTRY_BANNERS = {
    "pcb":     _COS + "INDUSTRY/PCB-BANNERNEW.jpg",
    "auto":    _COS + "INDUSTRY/AUTO-BANNER",
    "cable":   _COS + "INDUSTRY/CABLE-BANNER",
    "steel":   _COS + "INDUSTRY/STEEL-BANNER",
    "medical": _COS + "INDUSTRY/MEDICAL-BANNER",
    "outdoor": _COS + "INDUSTRY/OURDOOR-BANNER",
}
PRODUCT_INDUSTRY = {
    # PCB / electronics
    "apex": "pcb", "e-series": "pcb", "xf58": "pcb", "xf78": "pcb", "xf-603": "pcb",
    "e-2712": "pcb", "e-2913": "pcb",
    # automotive
    "e-2512bl": "auto", "e-2813": "auto", "e-2814": "auto",
    # wire & cable
    "e-6033": "cable", "e-6034": "cable",
    # steel / high-temp HP series
    "hp-700t": "steel", "hp-800c": "steel", "hp-901": "steel",
    "hp-cbr11": "steel", "hp-cbr13": "steel", "hp-l80": "steel", "hp-l90": "steel",
    "hp-m83": "steel", "hp-x2049": "steel", "hp-x2080": "steel",
    # medical / lab (incl. low-temp / cryogenic series)
    "e-4812": "medical", "e-4532": "medical",
    "e-6333": "medical", "e-4533": "medical", "e-3635": "medical", "e-4813": "medical",
}
# Slugs that are environment Solution pages, not industry products — they keep
# their own (enviroment-*) banner and are exempt from the industry-banner rule.
SOLUTION_SLUGS = {
    "high-heat-identification", "cold-chain-cryogenic-labels",
    "chemical-resistant-labels", "sterilization-labels",
}

def product_industry(d, slug):
    """Resolve a product's industry: JSON 'industry' field first, then the
    hardcoded map. Returns '' for Solution pages and anything unmapped."""
    return (d.get("industry") or PRODUCT_INDUSTRY.get(slug, "")).strip()

# Brand axis — a product is either an imported Polyonics line or ETIA's own.
# One product record can be scanned by both its Industry page and its Brand page.
PRODUCT_BRAND = {
    "apex": "polyonics", "xf58": "polyonics", "xf78": "polyonics",
}
BRAND_NAMES = {
    "polyonics": {"en": "Polyonics", "zh": "Polyonics", "vi": "Polyonics", "th": "Polyonics"},
    "heatproof": {"en": "HEATPROOF", "zh": "HEATPROOF", "vi": "HEATPROOF", "th": "HEATPROOF"},
    "etia":      {"en": "ETIA (in-house)", "zh": "ETIA 自研", "vi": "ETIA (tự sản xuất)", "th": "ETIA (ผลิตเอง)"},
}

def product_brand(d, slug):
    """Resolve a product's brand key ('polyonics' | 'heatproof' | 'etia'): JSON
    'brand' field first, then the hardcoded map; every HP- part falls back to the
    HEATPROOF brand, everything else to ETIA in-house."""
    b = (d.get("brand") or PRODUCT_BRAND.get(slug, "")).strip().lower()
    if b:
        return b
    if slug.startswith("hp-"):
        return "heatproof"
    return "etia"

def build_lang(d, lang):
    ui = UI.get(lang, UI[SOURCE_LANG])
    slug = d["slug"]
    path = "/products/item/%s/" % slug
    title = L(d["title"], lang)
    # UNIFORM RULE, no exceptions: every product landing page shows its industry
    # banner. The industry comes from the JSON "industry" field (preferred) or the
    # hardcoded PRODUCT_INDUSTRY map. It ALWAYS wins over any per-product "banner".
    # Only pages with no industry at all (the environment Solution pages) keep their
    # own banner. See product_industry() + the build audit that flags omissions.
    banner = INDUSTRY_BANNERS.get(product_industry(d, slug), "") or d.get("banner", "")
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
            '<h1>%s</h1>%s%s</div></section>') % (
        CSS, bg, esc(L(d.get("eyebrow", {}), lang) or ui["products"]), esc(title), tl_html, hp.hero_cta(lang))

    body = ""
    if L(d.get("positioning", {}), lang):
        body += section(ui["positioning"], ui["positioning"], '<p class="pos">%s</p>' % esc(L(d["positioning"], lang)))
    # optional construction/structure diagram: {"img":, "title":{lang}, "caption":{lang}, "legend":{lang:[...]}}
    dg = d.get("diagram")
    if dg and dg.get("img"):
        dtitle = L(dg.get("title", {}), lang) or ui.get("structure", "Construction")
        cap = L(dg.get("caption", {}), lang)
        capf = ('<figcaption>%s</figcaption>' % esc(cap)) if cap else ""
        leg = L(dg.get("legend", {}), lang)
        legf = ('<ul class="pdleg">%s</ul>' % "".join("<li>%s</li>" % esc(x) for x in leg)) if leg else ""
        body += section(dtitle, dtitle,
            '<div class="pdiagram"><figure><img src="%s" alt="" loading="lazy" onerror="this.closest(\'.pdiagram\').remove()">%s</figure>%s</div>' % (esc(dg["img"]), capf, legf))
    if d.get("highlight") and L(d["highlight"].get("title", {}), lang):
        body += highlight_html(d["highlight"], lang)
    if L(d.get("challenges", {}), lang):
        body += section(ui["challenges"], ui["challenges"], ul(L(d["challenges"], lang), "warn"))
    if L(d.get("features", {}), lang):
        pimg = d.get("product_img", "")
        if pimg:
            img = '<img class="pimg" src="%s" alt="" loading="lazy" onerror="this.remove()">' % esc(pimg)
        elif is_eseries(slug):
            # E-Series family: uniform 4:3 barcode tile (barcode on top, E-XXXX below)
            img = '<div class="pimg lbl">%s</div>' % barcode_label_svg(_model_code(slug), "ETIA")
        else:
            img = ""
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
        body += section("", ui["applications"], scenarios_html(L(d["scenarios"], lang), ui, lang))
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
    unbannered = []   # products that would render with NO banner at all
    misc = []         # non-solution products with no industry (fell back to own banner)
    for slug in sorted(slugs):
        d = json.load(open(os.path.join(PDIR, slug + ".json"), encoding="utf-8"))
        ind = product_industry(d, slug)
        eff_banner = INDUSTRY_BANNERS.get(ind, "") or d.get("banner", "")
        if slug not in SOLUTION_SLUGS:
            if not ind:
                (unbannered if not eff_banner else misc).append(slug)
        for lang in d.get("langs", ["en", "zh"]):
            build_lang(d, lang)
        print("product:", slug, "[%s]" % (ind or "—"), d.get("langs"))
    # Banner audit — so a big batch of new products can't silently ship without a
    # banner. Any product here needs an "industry" (or a PRODUCT_INDUSTRY entry).
    known = set(INDUSTRY_BANNERS)
    bad_ind = sorted({s for s in slugs if s not in SOLUTION_SLUGS
                      and product_industry(json.load(open(os.path.join(PDIR, s + ".json"), encoding="utf-8")), s)
                      not in known | {""}})
    if misc:
        print("BANNER AUDIT ⚠  no industry set (used own banner):", misc)
    if bad_ind:
        print("BANNER AUDIT ⚠  UNKNOWN industry value:", bad_ind, "-> allowed:", sorted(known))
    if unbannered:
        print("BANNER AUDIT ❌  NO BANNER AT ALL (set 'industry' in the JSON):", unbannered)
    else:
        print("BANNER AUDIT ✓  every product has a banner")

if __name__ == "__main__":
    main()
