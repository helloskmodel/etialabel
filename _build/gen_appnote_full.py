#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Full engineering Application Notes per the ETIA Application Note Generation
Standard V1.0 — hero, 7 sections, CTA, SEO, image slots. Engineering voice;
ETIA positioned as authorized distributor / solution provider (supplies,
recommends, supports — never 'we manufacture'). No invented specifications.
EN + ZH. Image slots are placeholders for the later unified image pass."""
import os
import gen_heatproof as hp
from gen_heatproof import esc, L, page, write, LANGS

HUB = "/application-notes/"

def _t(lang, en, zh): return zh if lang == "zh" else en

# Featured full notes, surfaced on the Application Notes hub.
FEATURED = [{
 "slug": "green-tire-wip-tracking",
 "title_en": "Green Tire WIP Tracking Labels",
 "title_zh": "绿胎在制品（WIP）追踪标签",
 "blurb_en": "Barcode traceability that survives high-temperature, high-pressure tire vulcanization — where it is used, why ordinary labels fail, and how to choose a pre-cure construction.",
 "blurb_zh": "在高温高压硫化中仍可读的条码追溯 —— 用在哪、普通标签为何失效,以及如何选择预硫化（pre-cure）构造",
}]

CSS = """<style>
.afhero{background:linear-gradient(120deg,#0c2555 0%,#16357d 52%,#1e50c7 100%);color:#fff}
.afhero .wrap{padding:52px 24px}.afhero .eyebrow{color:#9dbcff}
.afhero h1{color:#fff;font-size:34px;font-weight:800;line-height:1.16;margin:6px 0 10px;max-width:20em}
.afhero p{color:#eef3ff;font-size:15.5px;line-height:1.65;max-width:54em}
.aftags{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}
.aftag{font-size:12px;font-weight:700;color:#dfe9ff;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.22);border-radius:20px;padding:5px 12px}
.afbtns{margin-top:20px;display:flex;gap:12px;flex-wrap:wrap}
.afwrap{max-width:64em}
.afsec{margin-top:34px}
.afsec .num{font-size:11px;font-weight:800;letter-spacing:.08em;color:var(--mut);text-transform:uppercase}
.afsec h2{font-size:21px;font-weight:800;color:var(--blue-deep);margin:5px 0 12px;line-height:1.3}
.afsec p{font-size:15.5px;line-height:1.75;color:var(--ink)}.afsec p+p{margin-top:12px}
.afchips{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}
.afchip{font-size:12.5px;font-weight:700;border-radius:20px;padding:6px 13px;background:#fff1e8;color:#b4531a;border:1px solid #f4cdb0}
.afh3{font-size:14px;font-weight:800;color:var(--blue-deep);margin:18px 0 8px;letter-spacing:.01em}
.aftbl{width:100%;border-collapse:collapse;font-size:14.5px;background:#fff;border:1px solid var(--line);border-radius:12px;overflow:hidden;max-width:52em}
.aftbl td{padding:11px 16px;border-bottom:1px solid var(--line);line-height:1.55}.aftbl tr:last-child td{border-bottom:none}
.aftbl td:first-child{background:var(--bg);font-weight:700;color:var(--blue-deep);width:210px}
.afptbl{width:100%;border-collapse:collapse;font-size:14px;background:#fff;border:1px solid var(--line);border-radius:12px;overflow:hidden}
.afptbl th,.afptbl td{padding:10px 14px;text-align:left;border-bottom:1px solid var(--line)}
.afptbl th{background:var(--tint-blue);color:var(--blue-deep);font-weight:800;font-size:12px}
.afptbl td:first-child{font-weight:800;color:var(--blue-deep)}.afptbl tr:last-child td{border-bottom:none}
.aful{margin:12px 0 0;padding-left:20px}.aful li{margin:7px 0;font-size:15px;line-height:1.6;color:var(--ink)}
.afrel{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}
.afrel a{font-size:14px;font-weight:700;color:var(--blue-deep);border:1px solid var(--line);border-radius:20px;padding:7px 15px}
.afimg{border:1px dashed #c2cde6;background:#f6f9ff;border-radius:12px;padding:14px 18px;margin-top:16px;color:#7d8db3;font-size:12.5px;line-height:1.5}
.afimg b{color:#5f719c;font-weight:800;letter-spacing:.04em;text-transform:uppercase;font-size:11px}
@media(max-width:820px){.aftbl td:first-child{width:150px}.afhero h1{font-size:27px}}
</style>"""


def build_green_tire(lang):
    def T(en, zh): return esc(_t(lang, en, zh))
    contact = L(lang, "/contact/")
    path = HUB + "green-tire-wip-tracking/"
    img = lambda en, zh: '<div class="afimg"><b>%s</b>  %s</div>' % (T("Image", "配图"), T(en, zh))

    # HERO
    tags = ["Green Tire", "WIP Tracking", "Barcode", "High Heat", "Rubber", "Traceability"]
    tags_zh = ["绿胎", "在制品追踪", "条码", "高温", "橡胶", "可追溯"]
    hero = ('<section class="afhero"><div class="wrap"><div class="eyebrow">%s</div>'
            '<h1>%s</h1><p>%s</p><div class="aftags">%s</div>'
            '<div class="afbtns"><a class="btn pri" href="%s">%s</a>'
            '<a class="btn on-dark" href="%s">%s</a></div></div></section>') % (
        T("Automotive · Tire Manufacturing", "汽车 · 轮胎制造"),
        T("Barcode Traceability That Survives Vulcanization", "在硫化中仍可读的条码追溯"),
        T("In tire manufacturing, every green (uncured) tire is tracked from building through curing. The barcode label is applied to raw, tacky rubber and then driven through high-temperature, high-pressure vulcanization. Ordinary labels smear, lift or char before the tire leaves the mold. This note covers where green-tire WIP labels are used, what they must survive, why standard labels fail, and how ETIA helps engineers select a pre-cure construction that keeps the barcode scannable through the whole process.",
          "在轮胎制造中,每条绿胎（未硫化胎）都要从成型一直追踪到硫化 条码标签贴在生的、发黏的橡胶上,再经历高温高压硫化 普通标签在轮胎出模前就糊、翘或焦化 本笔记介绍绿胎 WIP 标签用在哪、必须承受什么、普通标签为何失效,以及 ETIA 如何协助工程师选择让条码全程可扫的预硫化构造"),
        "".join('<span class="aftag">%s</span>' % esc(_t(lang, e, z)) for e, z in zip(tags, tags_zh)),
        contact, T("Request Samples", "索取样品"), contact, T("Talk to an Engineer", "咨询工程师"))

    def sec(num, key_en, key_zh, head_en, head_zh, inner):
        return ('<div class="afsec"><div class="num">%s · %s</div><h2>%s</h2>%s</div>') % (
            num, T(key_en, key_zh), T(head_en, head_zh), inner)

    # 01 Application Overview
    s1 = sec("01", "APPLICATION", "用途", "Application Overview", "用途概述",
        _t(lang, "<p>Green-tire WIP labels are applied at the tire-building stage, before curing. As each ply, belt and tread is assembled into an uncured “green” tire, a barcode label is placed on the sidewall or bead area to carry the build spec, lot and routing data. That label is the tire’s identity as it moves through buffering, storage and into the curing press. After vulcanization, the same code links the finished tire back to its build record for quality traceability and recall management. Because it rides through the entire cure, the label — not just the print — has to survive the process intact.</p>",
          "<p>绿胎 WIP 标签在轮胎成型阶段、硫化之前贴附 当各层帘布、带束与胎面组装成未硫化的“绿胎”时,在胎侧或胎圈区域贴上条码标签,承载成型规格、批次与流转信息 这枚标签就是轮胎在缓存、存储直到进硫化机全程的身份 硫化后,同一条码把成品胎与其成型记录关联,用于质量追溯与召回管理 由于它要随整轮硫化,必须是标签本身（而不仅是印字）完好走出工序</p>")
        + img("Green tire on the building drum / label placement on the sidewall", "成型鼓上的绿胎 / 胎侧贴标位置"))

    # 02 Engineering Challenges
    reqs = ["High Heat", "High Pressure", "Green-Rubber Adhesion", "Chemical Resistance", "Barcode Durability", "Dimensional Stability"]
    reqs_zh = ["高温", "高压", "生胶粘接", "耐化学", "条码耐久", "尺寸稳定"]
    s2 = sec("02", "ENGINEERING CHALLENGES", "工程挑战", "What the Label Must Withstand", "标签必须承受什么",
        _t(lang, "<p>Vulcanization is one of the harshest label environments in automotive manufacturing. In the curing press the green tire is shaped against a hot mold under high internal pressure, typically around 180 °C, for several minutes. The label sits on a tacky, low-surface-energy rubber compound that is still flowing and expanding as it cures. It is exposed to mold-release agents, curing chemistry and steam or gas pressure. Through all of that, the barcode must stay dimensionally stable, unsmeared and machine-readable.</p>",
          "<p>硫化是汽车制造中对标签最苛刻的环境之一 在硫化机中,绿胎在高内压下贴着热模成型,温度通常约 180 °C,持续数分钟 标签贴在发黏、低表面能、仍在流动与膨胀固化的橡胶胶料上 它还接触脱模剂、硫化化学品与蒸汽或气体压力 在这一切之下,条码必须保持尺寸稳定、不糊且可机读</p>")
        + ('<div class="afh3">%s</div><div class="afchips">%s</div>' % (
            T("Key Requirements", "关键要求"),
            "".join('<span class="afchip">%s</span>' % esc(_t(lang, e, z)) for e, z in zip(reqs, reqs_zh))))
        + img("Curing press / mold with a green tire loading", "硫化机 / 装入绿胎的模具"))

    # 03 Why Ordinary Labels Fail
    s3 = sec("03", "WHY ORDINARY LABELS FAIL", "普通标签为何失效", "Why Ordinary Labels Fail", "普通标签为何失效",
        _t(lang, "<p>A standard paper or general-purpose polyester label is built for flat, clean, room-temperature surfaces — the opposite of a green tire. On uncured rubber the adhesive never keys in, so edges lift and the label can be thrown off in the press. At vulcanization temperature a standard facestock shrinks, distorts or discolors, and thermal-transfer print made with an ordinary ribbon smears or fades until the barcode drops below a scannable grade. Mold-release agents and curing by-products attack unprotected topcoats. The result is a broken traceability chain exactly where it matters most — between the build record and the finished tire.</p>",
          "<p>普通纸质或通用聚酯标签是为平整、洁净、常温表面设计的 —— 与绿胎正相反 在未硫化橡胶上,胶粘剂无法咬合,边缘翘起,标签可能在硫化机中被甩掉 在硫化温度下,普通面材收缩、变形或变色,用普通碳带的热转印字迹会糊或褪,直到条码降到无法扫描的等级 脱模剂与硫化副产物侵蚀无保护的涂层 结果就是在最关键处 —— 成型记录与成品胎之间 —— 追溯链断裂</p>")
        + img("Failed label after cure: smeared/curled barcode vs. a readable one", "硫化后失效标签:糊/翘的条码 vs 可读的条码"))

    # 04 Recommended Material Solution
    mat_rows = [
        ("Recommended Brand", "推荐品牌", "E-Label (also available: Computype)", "E-Label（另有 Computype 可选）"),
        ("Recommended Product", "推荐产品", "E-2313", "E-2313"),
        ("Face Material", "面材", "Heat-stabilized polyester", "热稳定聚酯"),
        ("Adhesive", "胶粘剂", "Vulcanization-grade high-temperature acrylic", "硫化级高温丙烯酸"),
        ("Printing Method", "打印方式", "Thermal transfer", "热转印"),
        ("Application Stage", "贴附阶段", "Green-tire building, pre-cure", "绿胎成型,预硫化"),
        ("Typical Temperature", "典型温度", "~180 °C high-pressure vulcanization", "约 180 °C 高压硫化"),
    ]
    mtbl = '<table class="aftbl">%s</table>' % "".join(
        '<tr><td>%s</td><td>%s</td></tr>' % (T(ke, kz), T(ve, vz)) for ke, kz, ve, vz in mat_rows)
    why = [("Heat-stabilized polyester holds its dimensions through the cure, so the barcode stays in grade",
            "热稳定聚酯在硫化中保持尺寸,条码等级不掉"),
           ("Vulcanization-grade high-temperature acrylic bonds to tacky green rubber and holds through cure",
            "硫化级高温丙烯酸胶能粘住发黏的生胶并在硫化中保持粘接"),
           ("Pre-cure construction validated for high-temperature, high-pressure vulcanization",
            "预硫化构造,经高温高压硫化验证"),
           ("Barcode remains machine-readable after the tire leaves the mold",
            "轮胎出模后条码仍可机读"),
           ("Maintains full-process traceability from green tire to finished tire",
            "保持从绿胎到成品胎的全流程追溯")]
    s4 = sec("04", "RECOMMENDED MATERIAL SOLUTION", "推荐材料方案", "Recommended Material Solution", "推荐材料方案",
        mtbl
        + ('<div class="afh3">%s</div><ul class="aful">%s</ul>' % (
            T("Why this material?", "为什么选这种材料?"),
            "".join('<li>%s</li>' % T(e, z) for e, z in why))))

    # 05 Recommended Products
    prods = [("E-2313", "E-Label", "Green-tire WIP, pre-cure vulcanization", "绿胎 WIP,预硫化"),
             ("TS1100P / TS1134P", "Computype", "Green-tire WIP, pre-cure vulcanization", "绿胎 WIP,预硫化")]
    ptbl = ('<table class="afptbl"><tr><th>%s</th><th>%s</th><th>%s</th></tr>%s</table>') % (
        T("Product", "产品"), T("Brand", "品牌"), T("Suitable For", "适用于"),
        "".join('<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (esc(p), esc(b), T(se, sz)) for p, b, se, sz in prods))
    s5 = sec("05", "RECOMMENDED PRODUCTS", "推荐产品", "Recommended Products", "推荐产品",
        ptbl + img("Product roll / label on green rubber", "产品卷料 / 贴在生胶上的标签"))

    # 06 Engineering Tips
    tips = [("Apply to a clean, dry bead or sidewall area; keep mold-release overspray off the bond zone",
             "贴在洁净、干燥的胎圈或胎侧区域;避免脱模剂喷到粘接区"),
            ("Match label size to the flattest available area to limit edge stress in the press",
             "让标签尺寸匹配最平整的可用区域,减少硫化中的边缘应力"),
            ("Use a high-temperature ribbon and verify barcode grade after cure, not just before",
             "使用高温碳带,并在硫化后（而不仅是硫化前）核验条码等级"),
            ("Confirm compatibility with your specific rubber compound and cure recipe — formulations vary",
             "确认与你具体的橡胶胶料与硫化配方兼容 —— 配方各不相同"),
            ("Validate scan performance on the finished tire under production lighting and scanner optics",
             "在产线照明与扫描器光学条件下,验证成品胎上的扫描表现")]
    s6 = sec("06", "ENGINEERING TIPS", "工程提示", "Engineering Tips", "工程提示",
        '<ul class="aful">%s</ul>' % "".join('<li>%s</li>' % T(e, z) for e, z in tips))

    # 07 Related Applications
    rel = [("Tire Pressure Labels", "胎压标签", "/industries/automotive-label-materials/"),
           ("VIN Labels", "VIN 标签", "/application-notes/vin-labels/"),
           ("Battery Labels", "电池标签", "/industries/automotive-label-materials/"),
           ("Wire Harness Labels", "线束标签", "/industries/automotive-label-materials/"),
           ("Under-Hood Labels", "发动机舱标签", "/industries/automotive-label-materials/"),
           ("Warning Labels", "警示标签", "/industries/automotive-label-materials/")]
    s7 = sec("07", "RELATED APPLICATIONS", "相关应用", "Related Applications", "相关应用",
        '<div class="afrel">%s</div>' % "".join(
            '<a href="%s">%s</a>' % (L(lang, u), T(e, z)) for e, z, u in rel))

    cta = ('<section class="blk alt"><div class="wrap"><div class="cta cta-q"><h3>%s</h3><p>%s</p>'
           '<div class="btns"><a class="btn pri" href="%s">%s</a>'
           '<a class="btn on-dark" href="%s">%s</a></div></div></div></section>') % (
        T("Need Help Selecting the Right Material?", "需要帮助选对材料吗?"),
        T("Every manufacturing process is different. ETIA application engineers can recommend suitable label materials based on your production process, environmental conditions and performance requirements.",
          "每条产线都不一样 ETIA 应用工程师可根据你的生产工艺、环境条件与性能要求,推荐合适的标签材料"),
        contact, T("Request Samples", "索取样品"), contact, T("Talk to an Engineer", "咨询工程师"))

    body = (CSS + '<section class="blk"><div class="wrap afwrap">%s</div></section>' % (s1 + s2 + s3 + s4 + s5 + s6 + s7)) + cta
    title = _t(lang, "Green Tire WIP Tracking Labels for Vulcanization | ETIA",
                     "绿胎 WIP 追踪标签（耐硫化）| ETIA")
    desc = _t(lang, "Barcode labels for green-tire WIP tracking that survive high-temperature, high-pressure vulcanization. ETIA helps engineers select pre-cure label materials.",
                    "用于绿胎 WIP 追踪、可耐高温高压硫化的条码标签 ETIA 协助工程师选择预硫化标签材料")
    name = _t(lang, "Green Tire WIP Tracking Labels", "绿胎在制品（WIP）追踪标签")
    crumb = [("Home", "/"), (_t(lang, "Application Notes", "应用笔记"), HUB), (name, path)]
    art = {"@context": "https://schema.org", "@type": "TechArticle", "headline": name, "description": desc,
           "articleSection": _t(lang, "Application Note", "应用笔记"),
           "inLanguage": ("zh-CN" if lang == "zh" else "en"),
           "publisher": {"@type": "Organization", "name": "ETIA Label"}}
    write(lang, path, page(lang, path, title, desc, name, "", body, crumb, schema_extra=[art], active="insights", hero=hero))
    if lang == "en": hp.track(path, "notes")


def main():
    for lang in LANGS:
        build_green_tire(lang)


if __name__ == "__main__":
    main()
