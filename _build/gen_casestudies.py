#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Case Studies — a hub that lists cases, plus one big landing page per case.
Each case follows a fixed structure: title, image, and a structured article
(Application/Installation, Product, Challenges, Solution/Benefits). EN + ZH.
Image slots are placeholders for a later unified pass."""
import os
import gen_heatproof as hp
from gen_heatproof import esc, L, page, write, LANGS

HUB = "/case-studies/"

def _t(lang, en, zh): return zh if lang == "zh" else en

# ---- case data ------------------------------------------------------------
CASES = [
 {
  "slug": "fixture-traceability-carburizing",
  "title_en": "Improving Fixture Traceability in Automotive Carburizing Processes",
  "title_zh": "改善汽车渗碳工艺中的工装可追溯性",
  "app_en": "Metal fixtures used in carburizing processes",
  "app_zh": "用于渗碳工艺的金属工装",
  "product_en": "US-E (heat resistance up to 1,100 °C)",
  "product_zh": "US-E（耐温至 1,100 °C）",
  "chal_intro_en": "For rotating components such as gears, carburizing treatment is used to increase surface hardness. In this process, lot management at the fixture level is essential. Previously, fixture numbers and lot numbers were recorded manually using tablet input. This presented several challenges:",
  "chal_intro_zh": "对于齿轮等旋转部件,采用渗碳处理提高表面硬度 在此工艺中,工装层级的批次管理至关重要 此前,工装编号与批次编号靠平板手工录入,存在几个问题:",
  "chal_bullets_en": ["Human errors such as input mistakes or missing entries",
                      "Increased workload for operators due to manual data entry",
                      "Inconsistent traceability depending on the situation"],
  "chal_bullets_zh": ["输入错误或漏录等人为失误",
                      "手工录入增加操作人员工作量",
                      "追溯一致性因情况而异"],
  "chal_close_en": "As a result, reliable lot-to-fixture association was difficult to maintain.",
  "chal_close_zh": "结果,批次与工装之间难以保持可靠关联",
  "sol_intro_en": "US-E labels — capable of withstanding temperatures up to 1,100 °C as well as cleaning processes and mechanical impact during loading and transport — were bolt-mounted to the side of the trays.",
  "sol_intro_zh": "US-E 标签可承受高达 1,100 °C 的高温,以及装载运输过程中的清洗与机械冲击,以螺栓固定在托盘侧面",
  "sol_results_en": ["Identification data remains readable even after carburizing involving high temperature, washing and mechanical impact, ensuring stable identification accuracy",
                     "Transition from manual input to 2D-code scanning eliminates manual data entry — reducing operator workload and significantly minimizing human errors",
                     "Labels are permanently fixed to fixtures and can be reused repeatedly",
                     "Usage counts can be tracked for each individual fixture, making it easier to monitor fixture lifespan"],
  "sol_results_zh": ["即使经过高温、清洗与机械冲击的渗碳工艺,标识数据仍清晰可读,识别精度稳定",
                     "从手工录入转为二维码扫描,取消手工输入 —— 降低操作人员工作量,大幅减少人为失误",
                     "标签永久固定在工装上,可反复重复使用",
                     "可跟踪每个工装的使用次数,便于监控工装寿命"],
  "sol_close_en": "As a result, the reliability of lot management in the carburizing process was significantly improved — traceability accuracy, operational efficiency and fixture management were enhanced simultaneously.",
  "sol_close_zh": "由此,渗碳工艺的批次管理可靠性显著提升 —— 追溯精度、操作效率与工装管理同步增强",
 },
]

CSS = """<style>
.cshero{background:linear-gradient(120deg,#0c2555 0%,#16357d 52%,#1e50c7 100%);color:#fff}
.cshero .wrap{padding:54px 24px}.cshero .eyebrow{color:#9dbcff}
.cshero h1{color:#fff;font-size:34px;font-weight:800;line-height:1.18;margin:6px 0 0;max-width:24em}
.csfig{border:1px dashed #b9c6e6;background:#f5f8ff;border-radius:14px;padding:30px;text-align:center;color:#6b7ba6;max-width:70em}
.csfig .ph{font-size:12px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:#94a4cc}
.csfig .cap{font-size:13.5px;line-height:1.55;margin-top:8px;color:var(--mut)}
.cstbl{max-width:72em;border:1px solid var(--line);border-radius:14px;overflow:hidden;background:#fff}
.csrow{display:grid;grid-template-columns:220px 1fr;border-bottom:1px solid var(--line)}
.csrow:last-child{border-bottom:none}
.csrow .k{background:var(--bg);padding:20px 22px;font-weight:800;color:var(--blue-deep);font-size:14.5px;border-right:1px solid var(--line)}
.csrow .v{padding:20px 24px;font-size:15px;line-height:1.7;color:var(--ink)}
.csrow .v p{margin:0}.csrow .v p+p{margin-top:10px}
.csrow .v ul{margin:10px 0 0;padding-left:20px}.csrow .v li{margin:5px 0;line-height:1.6}
.csrow .v .rh{font-weight:800;color:var(--green-d);margin-top:14px}
.csgrid{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}
.cscard{border:1px solid var(--line);border-radius:14px;overflow:hidden;background:#fff;display:block;border-top:3px solid var(--blue)}
.cscard .cimg{background:var(--bg);border-bottom:1px solid var(--line);aspect-ratio:16/9;display:flex;align-items:center;justify-content:center;color:#a9b6d4;font-size:11px;font-weight:800;letter-spacing:.05em;text-transform:uppercase}
.cscard .cbody{padding:18px 20px}
.cscard .ceyebrow{font-size:11px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--blue)}
.cscard h3{font-size:17px;font-weight:800;color:var(--blue-deep);margin:6px 0 8px;line-height:1.3}
.cscard p{font-size:13.5px;color:var(--mut);line-height:1.55;margin:0}
.cscard .cmore{margin-top:12px;font-weight:700;color:var(--blue-deep);font-size:14px}
@media(max-width:820px){.csrow{grid-template-columns:1fr}.csrow .k{border-right:none;border-bottom:1px solid var(--line)}.csgrid{grid-template-columns:1fr}.cshero h1{font-size:27px}}
</style>"""


def _detail_path(c): return HUB + c["slug"] + "/"

def build_detail(lang, c):
    def T(en, zh): return esc(_t(lang, en, zh))
    contact = L(lang, "/contact/")
    path = _detail_path(c)
    hero = ('<section class="cshero"><div class="wrap"><div class="eyebrow">%s</div><h1>%s</h1>'
            '<div style="margin-top:20px"><a class="btn pri" href="%s">%s</a></div></div></section>') % (
        T("CASE STUDY", "案例研究"), T(c["title_en"], c["title_zh"]), contact, T("Talk to a Specialist", "咨询专家"))

    fig = ('<section class="blk"><div class="wrap"><div class="csfig"><div class="ph">%s</div>'
           '<div class="cap">%s</div></div></div></section>') % (
        T("Image", "配图"),
        T("Photo of the application — to be added.", "应用现场照片 —— 待补充"))

    chal = "<p>%s</p><ul>%s</ul><p>%s</p>" % (
        T(c["chal_intro_en"], c["chal_intro_zh"]),
        "".join("<li>%s</li>" % T(e, z) for e, z in zip(c["chal_bullets_en"], c["chal_bullets_zh"])),
        T(c["chal_close_en"], c["chal_close_zh"]))
    sol = "<p>%s</p><p class=\"rh\">%s</p><ul>%s</ul><p>%s</p>" % (
        T(c["sol_intro_en"], c["sol_intro_zh"]),
        T("▼ Results after implementation", "▼ 实施后结果"),
        "".join("<li>%s</li>" % T(e, z) for e, z in zip(c["sol_results_en"], c["sol_results_zh"])),
        T(c["sol_close_en"], c["sol_close_zh"]))

    def row(k_en, k_zh, v): return '<div class="csrow"><div class="k">%s</div><div class="v">%s</div></div>' % (T(k_en, k_zh), v)
    table = ('<section class="blk"><div class="wrap"><div class="cstbl">%s%s%s%s</div></div></section>') % (
        row("Application / Installation", "应用 / 安装", "<p>%s</p>" % T(c["app_en"], c["app_zh"])),
        row("Product", "产品", "<p>%s</p>" % T(c["product_en"], c["product_zh"])),
        row("Challenges", "挑战", chal),
        row("Solution / Benefits", "方案 / 收益", sol))

    body = CSS + fig + table + ('<div class="wrap">%s</div>' % hp.cta2(lang, "applications"))
    sname = _t(lang, "Case Studies", "案例")
    crumb = [(_t(lang, "Home", "首页"), "/"), (sname, HUB), (_t(lang, c["title_en"], c["title_zh"]), path)]
    write(lang, path, page(lang, path,
        _t(lang, c["title_en"] + " | ETIA Case Study", c["title_zh"] + " | ETIA 案例"),
        _t(lang, c["app_en"] + " — " + c["product_en"], c["app_zh"] + " —— " + c["product_zh"]),
        _t(lang, c["title_en"], c["title_zh"]), "", body, crumb, active="cases", hero=hero))
    if lang == "en": hp.track(path, "core")


def build_hub(lang):
    def T(en, zh): return esc(_t(lang, en, zh))
    contact = L(lang, "/contact/")
    hero = ('<section class="cshero"><div class="wrap"><h1>%s</h1>'
            '<div style="margin-top:20px"><a class="btn pri" href="%s">%s</a></div></div></section>') % (
        T("Case Studies", "案例研究"), contact, T("Talk to a Specialist", "咨询专家"))
    overview = ('<section class="blk"><div class="wrap"><p style="font-size:17px;line-height:1.7;color:var(--ink);max-width:70em">%s</p></div></section>') % T(
        "Real applications where the right label solved a real identification problem — the challenge, the product and the measurable result.",
        "真实应用中,合适的标签如何解决实际标识问题 —— 挑战、产品与可量化的结果")
    cards = ""
    for c in CASES:
        cards += ('<a class="cscard" href="%s"><div class="cimg">%s</div><div class="cbody">'
                  '<div class="ceyebrow">%s</div><h3>%s</h3><p>%s</p><div class="cmore">%s</div></div></a>') % (
            L(lang, _detail_path(c)), T("Image", "配图"),
            T("Case Study", "案例"), T(c["title_en"], c["title_zh"]),
            T(c["product_en"], c["product_zh"]), T("Read the case study →", "阅读案例 →"))
    grid = '<section class="blk alt"><div class="wrap"><div class="csgrid">%s</div></div></section>' % cards
    body = CSS + overview + grid + ('<div class="wrap">%s</div>' % hp.cta2(lang, "applications"))
    sname = _t(lang, "Case Studies", "案例")
    crumb = [(_t(lang, "Home", "首页"), "/"), (sname, HUB)]
    write(lang, HUB, page(lang, HUB,
        _t(lang, "Case Studies — Specialty Label Applications | ETIA", "案例研究 —— 特种标签应用 | ETIA"),
        _t(lang, "Real specialty-label applications: the identification challenge, the product used and the measurable result.",
                 "真实的特种标签应用:标识挑战、所用产品与可量化的结果"),
        sname, "", body, crumb, active="cases", hero=hero))
    if lang == "en": hp.track(HUB, "core")


def main():
    for lang in LANGS:
        build_hub(lang)
        for c in CASES:
            build_detail(lang, c)

if __name__ == "__main__":
    main()
