#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Industry landing pages — one shared hub layout fed by per-industry data.

Layout: Hero (title + subtitle + intro) -> Why it matters -> Explore Solutions
(solution-category cards: description + Typical Applications + Explore Application
Notes) -> Download Resources -> Engineering Resources -> CTA. EN + ZH.

Owns /industries/<slug>/. Part of the six-industry IA (Automotive,
PCB & Electronics, Cable, Outdoor, Medical, Steel). Content is client-supplied;
no invented product specifications. The 'Download PDF' and some Engineering
Resource links are placeholders routed to /contact/ until the asset/page exists."""
import os
import gen_heatproof as hp
from gen_heatproof import esc, L, Lx, page, write, LANGS

AN = "/application-notes/"
CS = "/case-studies/"

def _t(lang, en, zh): return zh if lang == "zh" else en

# Shared UI vocabulary (en, zh).
UI = {
 "typical":   ("Typical Applications", "典型应用"),
 "explore_an":("Explore Application Notes", "查看应用笔记"),
 "dl_head":   ("Download Resources", "下载资源"),
 "dl_pdf":    ("Download PDF", "下载 PDF"),
 "eng_head":  ("Engineering Resources", "工程资源"),
 "r_an":      ("Application Notes", "应用笔记"),
 "r_ei":      ("Engineering Insights", "工程洞察"),
 "r_cs":      ("Case Studies", "案例研究"),
 "r_faq":     ("FAQ", "常见问题"),
 "talk":      ("Talk to an Application Engineer", "咨询应用工程师"),
 "why":       ("Why It Matters", "为什么重要"),
}

# Per-industry content. Every string is a (en, zh) pair.
DATA = {
 "automotive": {
  "path": "/industries/automotive-label-materials/",
  "banner": "https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com/INDUSTRY/AUTO.jpg",
  "eyebrow": ("AUTOMOTIVE LABELING", "汽车标签"),
  "title": ("Automotive Labeling Solutions", "汽车标签解决方案"),
  "subtitle": ("Reliable Identification Across the Automotive Lifecycle",
               "覆盖汽车全生命周期的可靠标识"),
  "intro": ("From component manufacturing and vehicle assembly to aftermarket service, durable labels enable traceability, safety, compliance, and permanent identification throughout the automotive lifecycle.",
            "从零部件制造、整车装配到售后服务,耐用标签在汽车全生命周期中实现可追溯、安全、合规与永久标识"),
  "why_title": ("Why Automotive Labeling Matters", "为什么汽车标签很重要"),
  "why": [
   ("Modern vehicles contain thousands of parts manufactured by multiple suppliers across different production facilities. Reliable labeling connects components, operators, production systems, and service information throughout the manufacturing process and the vehicle's operational life.",
    "现代汽车包含由多家供应商在不同生产基地制造的数千个零件 可靠的标签在整个制造过程与车辆使用寿命中,把零部件、操作人员、生产系统与服务信息连接起来"),
   ("Whether identifying a tire during production, marking a VIN plate, applying a high-voltage warning, or protecting against counterfeiting, the right labeling solution improves manufacturing efficiency, product quality, regulatory compliance, and long-term traceability.",
    "无论是生产中标识轮胎、打标 VIN 铭牌、粘贴高压警示,还是防伪保护,正确的标签方案都能提升制造效率、产品质量、法规合规与长期可追溯性"),
  ],
  "explore_title": ("Explore Automotive Labeling Solutions", "探索汽车标签解决方案"),
  "categories": [
   {"name": ("Production Tracking", "生产追踪"),
    "desc": ("Track parts, assemblies, tires, batteries, and work-in-process throughout automotive manufacturing.",
             "在汽车制造全过程中追踪零件、总成、轮胎、电池与在制品"),
    "apps": [("Tire Bead Labels","胎圈标签"),("WIP Tracking","在制品追踪"),
             ("Battery Cell Identification","电芯标识"),("Component Traceability","零部件追溯")]},
   {"name": ("Vehicle Identification", "车辆标识"),
    "desc": ("Permanent identification for vehicles, engines, batteries, and critical components throughout their service life.",
             "面向车辆、发动机、电池及关键部件的永久标识,贯穿整个使用寿命"),
    "apps": [("VIN Labels","VIN 标签"),("Rating Plates","铭牌"),
             ("Serial Number Labels","序列号标签"),("Component Identification","零部件标识")]},
   {"name": ("Safety & Warning", "安全与警示"),
    "desc": ("Provide clear and durable safety communication for operators, technicians, and end users.",
             "为操作人员、技师与终端用户提供清晰耐久的安全信息"),
    "apps": [("High Voltage Labels","高压标签"),("Warning Labels","警告标签"),
             ("Caution Labels","注意标签"),("Tire Pressure Labels","胎压标签")]},
   {"name": ("Compliance & Certification", "合规与认证"),
    "desc": ("Meet OEM specifications and international regulatory requirements with durable identification.",
             "以耐用标识满足 OEM 规范与国际法规要求"),
    "apps": [("Regulatory Labels","法规标签"),("Certification Labels","认证标签"),
             ("Compliance Identification","合规标识")]},
   {"name": ("Security & Brand Protection", "防伪与品牌保护"),
    "desc": ("Protect products against tampering, relabeling, and counterfeiting.",
             "保护产品免受篡改、重贴标与假冒"),
    "apps": [("Tamper-Evident Labels","防拆标签"),("Security Labels","安全标签"),
             ("Laser Markable Identification","激光打标标识")]},
  ],
  "guide_title": ("Automotive Labeling Solutions Guide", "汽车标签解决方案指南"),
  "guide_desc": ("Selection recommendations, application overview, and engineering considerations.",
                 "选型建议、应用概览与工程注意事项"),
  "cta_q": ("Need help selecting the right automotive labeling solution?",
            "需要帮助选择合适的汽车标签方案吗"),
  "meta_title": ("Automotive Labeling Solutions — Durable Vehicle Labels | ETIA",
                 "汽车标签解决方案 —— 耐用整车标签 | ETIA"),
 },
 "pcb": {
  "path": "/industries/circuit-board-pcb/",
  "banner": "",
  "eyebrow": ("PCB & ELECTRONICS LABELING", "PCB 与电子标签"),
  "title": ("PCB & Electronics Labeling Solutions", "PCB 与电子标签解决方案"),
  "subtitle": ("Reliable Identification Throughout Electronics Manufacturing",
               "贯穿电子制造全过程的可靠标识"),
  "intro": ("From bare PCBs and SMT assembly to testing and final product identification, durable labels maintain traceability throughout modern electronics manufacturing.",
            "从裸板 PCB、SMT 贴装到测试与成品标识,耐用标签在现代电子制造全过程中保持可追溯"),
  "why_title": ("Why PCB Labeling Matters", "为什么 PCB 标签很重要"),
  "why": [
   ("Accurate identification is essential for quality control, process management, and product traceability in electronics manufacturing. Labels must withstand solder reflow, cleaning chemicals, handling, testing, and long production cycles while maintaining barcode readability and print quality.",
    "在电子制造中,准确标识对质量控制、流程管理与产品可追溯至关重要 标签必须承受回流焊、清洗化学品、搬运、测试与长生产周期,同时保持条码可读性与打印质量"),
   ("Selecting the right labeling solution helps manufacturers improve production efficiency, reduce errors, and ensure reliable identification from assembly through final shipment.",
    "选择正确的标签方案能帮助制造商提升生产效率、减少差错,并确保从贴装到最终出货的可靠标识"),
  ],
  "explore_title": ("Explore PCB Labeling Solutions", "探索 PCB 标签解决方案"),
  "categories": [
   {"name": ("PCB Manufacturing", "PCB 制造"),
    "desc": ("Reliable identification throughout PCB fabrication and assembly.",
             "贯穿 PCB 制造与贴装的可靠标识"),
    "apps": [("Wash & Reflow Labels","水洗回流标签"),("Wash & Non-Reflow Labels","水洗非回流标签"),
             ("Post-Process Labels","后工序标签")]},
   {"name": ("SMT & Electronics Assembly", "SMT 与电子贴装"),
    "desc": ("Support component identification and process control throughout assembly.",
             "在贴装全过程中支持元件标识与流程控制"),
    "apps": [("Component Labels","元件标签"),("WIP Labels","在制品标签"),
             ("ESD-Safe Labels","防静电标签"),("Inspection Labels","检验标签")]},
   {"name": ("Product Identification", "产品标识"),
    "desc": ("Permanent identification for finished electronic products and assemblies.",
             "面向电子成品与总成的永久标识"),
    "apps": [("Rating Labels","铭牌标签"),("Product Labels","产品标签"),
             ("Asset Labels","资产标签"),("Serial Number Labels","序列号标签")]},
   {"name": ("Quality & Compliance", "质量与合规"),
    "desc": ("Maintain traceability and support manufacturing quality systems.",
             "保持可追溯并支撑制造质量体系"),
    "apps": [("Barcode Labels","条码标签"),("QR Code Labels","二维码标签"),
             ("Compliance Labels","合规标签"),("Calibration Labels","校准标签")]},
   {"name": ("Specialty Electronics", "特种电子"),
    "desc": ("Engineered labeling solutions for demanding electronics applications.",
             "面向严苛电子应用的工程化标签方案"),
    "apps": [("Laser Markable Labels","激光打标标签"),("Polyimide Labels","聚酰亚胺标签"),
             ("High Temperature Labels","耐高温标签")]},
  ],
  "guide_title": ("PCB Labeling Solutions Guide", "PCB 标签解决方案指南"),
  "guide_desc": ("Selection recommendations for PCB manufacturing and electronics assembly.",
                 "面向 PCB 制造与电子贴装的选型建议"),
  "cta_q": ("Need help selecting the right PCB labeling solution?",
            "需要帮助选择合适的 PCB 标签方案吗"),
  "meta_title": ("PCB & Electronics Labeling Solutions | ETIA",
                 "PCB 与电子标签解决方案 | ETIA"),
 },
}

CSS = """<style>
.inhero{background:linear-gradient(115deg,rgba(9,24,64,.94),rgba(16,44,120,.72) 55%,rgba(26,86,219,.42)),__BG__ #0c2555;color:#fff}
.inhero .wrap{padding:60px 24px}.inhero .eyebrow{color:#9dbcff;font-size:12px;font-weight:800;letter-spacing:.08em}
.inhero h1{color:#fff;font-size:38px;font-weight:800;line-height:1.14;margin:8px 0 6px;max-width:20em}
.inhero .isub{color:#cfe0ff;font-size:19px;font-weight:700;line-height:1.35;margin:0 0 14px;max-width:26em}
.inhero p{color:#eef3ff;font-size:16px;line-height:1.66;max-width:52em}
.inhero .btn{margin-top:22px}
.inwhy{max-width:60em}.inwhy p{font-size:16px;line-height:1.75;color:var(--ink)}.inwhy p+p{margin-top:14px}
.incat{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:22px}
.incard{border:1px solid var(--line);border-radius:14px;padding:24px;background:#fff}
.incard h3{font-size:18px;font-weight:800;color:var(--blue-deep);margin:0 0 8px}
.incard .cd{font-size:14.5px;line-height:1.6;color:var(--mut)}
.incard .tl{font-size:11px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--faint);margin:16px 0 8px}
.incard ul{list-style:none;padding:0;margin:0}
.incard li{position:relative;padding-left:18px;font-size:14.5px;line-height:1.7;color:var(--ink)}
.incard li:before{content:"";position:absolute;left:2px;top:11px;width:5px;height:5px;border-radius:50%;background:var(--blue)}
.incard .go{display:inline-block;margin-top:14px;font-size:13px;font-weight:700;color:var(--green-d)}
.indl{border:1px solid var(--line);border-left:4px solid var(--blue);border-radius:12px;background:var(--tint-blue);padding:22px 26px;margin-top:8px;display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap}
.indl .dt{font-size:17px;font-weight:800;color:var(--blue-deep)}
.indl .dd{font-size:14px;color:var(--mut);line-height:1.55;margin-top:4px;max-width:44em}
.inres{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:20px}
.inres a{border:1px solid var(--line);border-radius:12px;padding:20px 18px;background:#fff;text-decoration:none;font-weight:800;color:var(--blue-deep);font-size:15px;transition:.16s;display:flex;align-items:center;justify-content:space-between;gap:8px}
.inres a:hover{border-color:var(--blue);box-shadow:0 10px 26px rgba(20,40,90,.10);transform:translateY(-2px)}
.inres a .ar{color:var(--green-d);font-weight:700}
.incta{background:linear-gradient(120deg,#123a86,#1e50c7);border-radius:18px;padding:40px 28px;text-align:center;color:#fff;margin-top:8px}
.incta h2{color:#fff;font-size:24px;font-weight:800;margin:0 0 18px;line-height:1.3}
@media(max-width:820px){.incat{grid-template-columns:1fr}.inres{grid-template-columns:1fr 1fr}.inhero h1{font-size:29px}}
@media(max-width:520px){.inres{grid-template-columns:1fr}}
</style>"""


def build(lang, key):
    d = DATA[key]
    def T(pair): return esc(_t(lang, pair[0], pair[1]))
    def U(k): return esc(_t(lang, UI[k][0], UI[k][1]))
    path = d["path"]
    contact = Lx(lang, "/contact/")
    bg = ("url('%s') center/cover no-repeat," % d["banner"]) if d["banner"] else ""
    css = CSS.replace("__BG__", bg)

    hero = ('<section class="inhero"><div class="wrap"><div class="eyebrow">%s</div>'
            '<h1>%s</h1><div class="isub">%s</div><p>%s</p>'
            '<a class="btn pri" href="%s">%s</a></div></section>') % (
        T(d["eyebrow"]), T(d["title"]), T(d["subtitle"]), T(d["intro"]), contact, U("talk"))

    why = ('<section class="blk"><div class="wrap"><h2>%s</h2><div class="inwhy">%s</div>'
           '</div></section>') % (
        T(d["why_title"]), "".join("<p>%s</p>" % T(p) for p in d["why"]))

    cards = ""
    for c in d["categories"]:
        lis = "".join("<li>%s</li>" % T(a) for a in c["apps"])
        cards += ('<div class="incard"><h3>%s</h3><div class="cd">%s</div>'
                  '<div class="tl">%s</div><ul>%s</ul>'
                  '<a class="go" href="%s">%s →</a></div>') % (
            T(c["name"]), T(c["desc"]), U("typical"), lis, Lx(lang, AN), U("explore_an"))
    explore = ('<section class="blk" style="background:var(--tint-blue)"><div class="wrap">'
               '<h2>%s</h2><div class="incat">%s</div></div></section>') % (
        T(d["explore_title"]), cards)

    dl = ('<section class="blk"><div class="wrap"><h2>%s</h2><div class="indl">'
          '<div><div class="dt">%s</div><div class="dd">%s</div></div>'
          '<a class="btn sec" href="%s">%s →</a></div></div></section>') % (
        U("dl_head"), T(d["guide_title"]), T(d["guide_desc"]), contact, U("dl_pdf"))

    res_links = [("r_an", AN), ("r_ei", AN), ("r_cs", CS), ("r_faq", "/contact/")]
    res = ('<section class="blk"><div class="wrap"><h2>%s</h2><div class="inres">%s</div>'
           '</div></section>') % (
        U("eng_head"),
        "".join('<a href="%s">%s <span class="ar">→</span></a>' % (Lx(lang, u), U(k))
                for k, u in res_links))

    cta = ('<section class="blk"><div class="wrap"><div class="incta"><h2>%s</h2>'
           '<a class="btn pri" href="%s">%s</a></div></div></section>') % (
        T(d["cta_q"]), contact, U("talk"))

    body = css + why + explore + dl + res + cta
    home = _t(lang, "Home", "首页")
    inds = _t(lang, "Industries", "行业")
    crumb = [(home, "/"), (inds, "/industries/"), (_t(lang, d["title"][0], d["title"][1]), path)]
    write(lang, path, page(lang, path, _t(lang, d["meta_title"][0], d["meta_title"][1]),
        _t(lang, d["intro"][0], d["intro"][1]),
        _t(lang, d["title"][0], d["title"][1]), "", body, crumb, active="", hero=hero))
    if lang == "en":
        hp.track(path, "industries")


URLS = [d["path"] for d in DATA.values()]
def main():
    for lang in LANGS:
        for key in DATA:
            build(lang, key)

if __name__ == "__main__":
    main()
