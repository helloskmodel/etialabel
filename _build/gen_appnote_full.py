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
}, {
 "slug": "tire-bead-labels",
 "title_en": "Tire Bead Labels",
 "title_zh": "轮胎胎圈标签",
 "blurb_en": "Reliable barcode identification from green tire production through vulcanization, inspection and final assembly — the challenges, what the label must do, and how to choose the material.",
 "blurb_zh": "从绿胎生产、硫化、检验到总装的可靠条码标识 —— 挑战、标签要做到什么,以及如何选材",
}, {
 "slug": "vin-labels",
 "title_en": "VIN Labels",
 "title_zh": "VIN 标签",
 "blurb_en": "Permanent vehicle identification for lifetime traceability — laser-markable, weather- and chemical-resistant, tamper-evident. Challenges, requirements and material selection.",
 "blurb_zh": "面向全生命周期追溯的永久车辆标识 —— 可激光打标、耐候耐化学、防篡改 挑战、要求与选材",
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
.afck{list-style:none;padding:0;margin:12px 0 0;display:grid;grid-template-columns:1fr 1fr;gap:8px 24px}
.afck li{position:relative;padding-left:28px;font-size:15px;line-height:1.55;color:var(--ink)}
.afck li:before{content:"✓";position:absolute;left:0;color:var(--green-d);font-weight:800}
.affq{border-bottom:1px solid var(--line);padding:15px 0}.affq:last-child{border-bottom:none}
.affq h3{font-size:15.5px;font-weight:800;color:var(--blue-deep);margin:0 0 6px}
.affq p{font-size:14.5px;color:var(--ink);line-height:1.65;margin:0}
@media(max-width:640px){.afck{grid-template-columns:1fr}}
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


def build_tire_bead(lang):
    def T(en, zh): return esc(_t(lang, en, zh))
    contact = L(lang, "/contact/")
    path = HUB + "tire-bead-labels/"
    img = lambda en, zh: '<div class="afimg"><b>%s</b>  %s</div>' % (T("Image", "配图"), T(en, zh))

    tags = ["Green Tire", "Vulcanization", "WIP Tracking", "Barcode", "Rubber"]
    tags_zh = ["绿胎", "硫化", "在制品追踪", "条码", "橡胶"]
    hero = ('<section class="afhero"><div class="wrap"><div class="eyebrow">%s</div>'
            '<h1>%s</h1><p>%s</p><div class="aftags">%s</div>'
            '<div class="afbtns"><a class="btn pri" href="%s">%s</a>'
            '<a class="btn on-dark" href="%s">%s</a></div></div></section>') % (
        T("AUTOMOTIVE LABELING", "汽车标签"),
        T("Reliable Barcode Identification Through Tire Manufacturing", "贯穿轮胎制造的可靠条码标识"),
        T("Tire bead labels provide reliable barcode identification from green tire production through vulcanization, inspection and final assembly. Designed for demanding rubber manufacturing environments, they help manufacturers maintain traceability, production efficiency and accurate WIP tracking.",
          "轮胎胎圈标签在从绿胎生产、硫化、检验到总装的全过程中提供可靠的条码标识 面向严苛的橡胶制造环境,帮助制造商保持可追溯性、生产效率与准确的在制品（WIP）追踪"),
        "".join('<span class="aftag">%s</span>' % esc(_t(lang, e, z)) for e, z in zip(tags, tags_zh)),
        contact, T("Request Samples", "索取样品"), contact, T("Talk to an Engineer", "咨询工程师"))

    def sec(num, key_en, key_zh, head_en, head_zh, inner):
        return ('<div class="afsec"><div class="num">%s · %s</div><h2>%s</h2>%s</div>') % (
            num, T(key_en, key_zh), T(head_en, head_zh), inner)

    s1 = sec("01", "APPLICATION", "用途", "Application Overview", "用途概述",
        _t(lang, "<p>Tire bead labels are applied to green tires or tire beads before curing. They carry barcode or serialized identification throughout the manufacturing process, allowing every tire to be tracked from production to final inspection.</p><p>Typical applications include passenger vehicles, truck tires, bus tires, OTR tires and specialty rubber products.</p>",
                 "<p>轮胎胎圈标签在硫化前贴附于绿胎或胎圈 它们在整个制造过程中承载条码或序列化标识,使每条轮胎都能从生产追踪到最终检验</p><p>典型应用包括乘用车、卡车胎、客车胎、工程机械（OTR）胎与特种橡胶制品</p>")
        + img("Label applied to the tire bead / green tire", "贴在胎圈 / 绿胎上的标签"))

    chal = [("High curing temperatures", "高硫化温度"), ("High molding pressure", "高成型压力"),
            ("Rubber expansion", "橡胶膨胀"), ("Process oils", "工艺油"),
            ("Mechanical handling", "机械搬运"), ("Barcode readability after vulcanization", "硫化后条码可读性")]
    s2 = sec("02", "ENGINEERING CHALLENGES", "工程挑战", "Engineering Challenges", "工程挑战",
        ('<p>%s</p><ul class="aful">%s</ul>' % (
            T("Tire manufacturing exposes labels to some of the harshest production conditions. Typical challenges include:",
              "轮胎制造让标签面临最苛刻的生产条件之一 典型挑战包括:"),
            "".join('<li>%s</li>' % T(e, z) for e, z in chal)))
        + img("Curing press / green tire under molding pressure", "硫化机 / 成型压力下的绿胎"))

    must = [("Stay attached to rubber", "牢固粘附于橡胶"), ("Survive vulcanization", "经受硫化"),
            ("Maintain barcode readability", "保持条码可读"), ("Resist heat and pressure", "耐热耐压"),
            ("Support high-speed scanning", "支持高速扫描"), ("Enable full production traceability", "实现完整生产追溯")]
    s3 = sec("03", "WHAT THE LABEL MUST DO", "标签要做到什么", "What the Label Must Do", "标签要做到什么",
        '<ul class="afck">%s</ul>' % "".join('<li>%s</li>' % T(e, z) for e, z in must))

    s4 = sec("04", "MATERIAL SELECTION", "材料选择", "Choosing the Right Material", "如何选对材料",
        _t(lang, "<p>Material selection depends on rubber type, curing temperature, production process and barcode requirements. Engineers should consider adhesive compatibility with green rubber, heat resistance during vulcanization, barcode durability and printing technology to ensure reliable identification throughout manufacturing.</p>",
                 "<p>材料选择取决于橡胶类型、硫化温度、生产工艺与条码要求 工程师应考虑与生胶的胶粘剂兼容性、硫化过程中的耐热性、条码耐久性与打印技术,以确保整个制造过程中标识可靠</p>"))

    prods = [("E-2313", "E-Label", "Green-tire / bead, pre-cure vulcanization", "绿胎 / 胎圈,预硫化"),
             ("TS1100P / TS1134P", "Computype", "Green-tire / bead, pre-cure vulcanization", "绿胎 / 胎圈,预硫化")]
    ptbl = ('<table class="afptbl"><tr><th>%s</th><th>%s</th><th>%s</th></tr>%s</table>') % (
        T("Product", "产品"), T("Brand", "品牌"), T("Suitable For", "适用于"),
        "".join('<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (esc(p), esc(b), T(se, sz)) for p, b, se, sz in prods))
    s5 = sec("05", "RECOMMENDATION", "推荐", "Recommendation", "推荐",
        _t(lang, "<p>For pre-cure tire identification, ETIA recommends E-Label <b>E-2313</b> — a heat-stabilized polyester construction with a vulcanization-grade high-temperature acrylic adhesive, validated for high-temperature, high-pressure curing. ETIA supplies genuine materials and provides local application support to match the construction to your compound and cure recipe.</p>",
                 "<p>用于预硫化轮胎标识,ETIA 推荐 E-Label <b>E-2313</b> —— 热稳定聚酯构造,配硫化级高温丙烯酸胶,经高温高压硫化验证 ETIA 供应正品材料,并提供本地应用支持,使构造匹配你的胶料与硫化配方</p>")
        + ptbl)

    faq = [("Can tire labels survive vulcanization?", "轮胎标签能经受硫化吗?",
            "Yes, when designed for tire manufacturing and matched to the curing process.", "可以,前提是为轮胎制造设计并与硫化工艺匹配"),
           ("Should labels be applied before curing?", "标签应在硫化前贴吗?",
            "Most tire bead labels are applied before vulcanization to enable continuous WIP tracking.", "多数轮胎胎圈标签在硫化前贴附,以实现连续的在制品追踪"),
           ("Can barcodes still be scanned after curing?", "硫化后条码还能扫描吗?",
            "Properly selected materials maintain barcode readability after heat and pressure exposure.", "选对材料后,标签在经受高温高压后仍保持条码可读")]
    s6 = sec("06", "FAQ", "常见问题", "FAQ", "常见问题",
        '<div class="affaq">%s</div>' % "".join(
            '<div class="affq"><h3>%s</h3><p>%s</p></div>' % (T(qe, qz), T(ae, az)) for qe, qz, ae, az in faq))

    cta = ('<section class="blk alt"><div class="wrap"><div class="cta cta-q"><h3>%s</h3><p>%s</p>'
           '<div class="btns"><a class="btn pri" href="%s">%s</a>'
           '<a class="btn on-dark" href="%s">%s</a></div></div></div></section>') % (
        T("Need help selecting the right tire label?", "需要帮助选对轮胎标签吗?"),
        T("Our application engineers can recommend suitable materials based on your tire manufacturing process.",
          "我们的应用工程师可根据你的轮胎制造工艺推荐合适的材料"),
        contact, T("Request Samples", "索取样品"), contact, T("Talk to an Engineer", "咨询工程师"))

    body = (CSS + '<section class="blk"><div class="wrap afwrap">%s</div></section>' % (s1 + s2 + s3 + s4 + s5 + s6)) + cta
    title = _t(lang, "Tire Bead Labels — Barcode ID for Tire Manufacturing | ETIA",
                     "轮胎胎圈标签 —— 轮胎制造条码标识 | ETIA")
    desc = _t(lang, "Tire bead labels for reliable barcode identification through green tire production, vulcanization and inspection. ETIA helps engineers select the material.",
                    "轮胎胎圈标签,在绿胎生产、硫化与检验全程提供可靠条码标识 ETIA 协助工程师选材")
    name = _t(lang, "Tire Bead Labels", "轮胎胎圈标签")
    crumb = [("Home", "/"), (_t(lang, "Application Notes", "应用笔记"), HUB), (name, path)]
    art = {"@context": "https://schema.org", "@type": "TechArticle", "headline": name, "description": desc,
           "articleSection": _t(lang, "Application Note", "应用笔记"),
           "inLanguage": ("zh-CN" if lang == "zh" else "en"),
           "publisher": {"@type": "Organization", "name": "ETIA Label"}}
    faq_schema = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": _t(lang, qe, qz),
         "acceptedAnswer": {"@type": "Answer", "text": _t(lang, ae, az)}} for qe, qz, ae, az in faq]}
    write(lang, path, page(lang, path, title, desc, name, "", body, crumb, schema_extra=[art, faq_schema], active="insights", hero=hero))
    if lang == "en": hp.track(path, "notes")


def build_vin(lang):
    def T(en, zh): return esc(_t(lang, en, zh))
    contact = L(lang, "/contact/")
    path = HUB + "vin-labels/"
    img = lambda en, zh: '<div class="afimg"><b>%s</b>  %s</div>' % (T("Image", "配图"), T(en, zh))

    tags = ["VIN Labels", "Vehicle Identification", "Laser Marking", "Automotive", "Traceability"]
    tags_zh = ["VIN 标签", "车辆识别", "激光打标", "汽车", "可追溯"]
    hero = ('<section class="afhero"><div class="wrap"><div class="eyebrow">%s</div>'
            '<h1>%s</h1><p>%s</p><div class="aftags">%s</div>'
            '<div class="afbtns"><a class="btn pri" href="%s">%s</a>'
            '<a class="btn on-dark" href="%s">%s</a></div></div></section>') % (
        T("AUTOMOTIVE LABELING", "汽车标签"),
        T("Permanent Vehicle Identification for Lifetime Traceability", "面向全生命周期追溯的永久车辆标识"),
        T("VIN labels provide permanent vehicle identification throughout manufacturing, registration, service and the vehicle's operating life. Designed for demanding automotive environments, they support compliance, traceability and product security while maintaining long-term readability.",
          "VIN 标签在制造、注册、维修与整车使用寿命全程提供永久车辆标识 面向严苛的汽车环境,支撑合规、可追溯与产品防伪,并保持长期可读"),
        "".join('<span class="aftag">%s</span>' % esc(_t(lang, e, z)) for e, z in zip(tags, tags_zh)),
        contact, T("Request Samples", "索取样品"), contact, T("Talk to an Engineer", "咨询工程师"))

    def sec(num, key_en, key_zh, head_en, head_zh, inner):
        return ('<div class="afsec"><div class="num">%s · %s</div><h2>%s</h2>%s</div>') % (
            num, T(key_en, key_zh), T(head_en, head_zh), inner)

    s1 = sec("01", "APPLICATION", "用途", "Application Overview", "用途概述",
        _t(lang, "<p>Vehicle Identification Number (VIN) labels are applied to designated locations on the vehicle, including the dashboard, door pillar, engine compartment or other OEM-defined positions. They identify each vehicle throughout production, registration, after-sales service, recalls and lifecycle management.</p>",
                 "<p>车辆识别代号（VIN）标签贴于车辆的指定位置,包括仪表台、门柱、发动机舱或其他 OEM 规定的位置 它们在生产、注册、售后服务、召回与全生命周期管理中标识每一台车辆</p>")
        + img("VIN label on the dashboard / door pillar", "仪表台 / 门柱上的 VIN 标签"))

    chal = [("UV exposure", "紫外线暴露"), ("Automotive fluids", "汽车油液"),
            ("Heat and humidity", "高温与潮湿"), ("Outdoor weathering", "户外风化"),
            ("Cleaning chemicals", "清洗化学品"), ("Tampering attempts", "篡改企图"),
            ("Laser marking quality", "激光打标质量")]
    s2 = sec("02", "ENGINEERING CHALLENGES", "工程挑战", "Engineering Challenges", "工程挑战",
        ('<p>%s</p><ul class="aful">%s</ul>' % (
            T("VIN labels are expected to remain readable for the entire life of the vehicle. Typical challenges include:",
              "VIN 标签需在整车寿命期内保持可读 典型挑战包括:"),
            "".join('<li>%s</li>' % T(e, z) for e, z in chal)))
        + img("Vehicle exterior under outdoor weathering / cleaning", "户外风化 / 清洗中的车身"))

    must = [("Permanent identification", "永久标识"), ("High laser contrast", "高激光对比度"),
            ("Chemical resistance", "耐化学"), ("Weather resistance", "耐候"),
            ("Barcode readability", "条码可读"), ("Tamper-evident performance", "防篡改表现")]
    s3 = sec("03", "WHAT THE LABEL MUST DO", "标签要做到什么", "What the Label Must Do", "标签要做到什么",
        '<ul class="afck">%s</ul>' % "".join('<li>%s</li>' % T(e, z) for e, z in must))

    s4 = sec("04", "MATERIAL SELECTION", "材料选择", "Choosing the Right Material", "如何选对材料",
        _t(lang, "<p>Selecting a VIN label requires balancing durability, security and production efficiency. Engineers should evaluate the mounting surface, marking technology, environmental exposure, required service life and any tamper-evident or regulatory requirements before choosing a label material.</p>",
                 "<p>选择 VIN 标签需要在耐久、防伪与生产效率之间权衡 工程师在选材前应评估贴附表面、打标技术、环境暴露、所需使用寿命,以及任何防篡改或法规要求</p>"))

    prods = [("E-2512BL", "E-Label", "VIN / permanent vehicle ID, laser-markable, tamper-evident", "VIN / 永久车辆标识,激光可打标,防篡改")]
    ptbl = ('<table class="afptbl"><tr><th>%s</th><th>%s</th><th>%s</th></tr>%s</table>') % (
        T("Product", "产品"), T("Brand", "品牌"), T("Suitable For", "适用于"),
        "".join('<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (esc(p), esc(b), T(se, sz)) for p, b, se, sz in prods))
    s5 = sec("05", "RECOMMENDED SOLUTIONS", "推荐方案", "Recommended Solutions", "推荐方案",
        _t(lang, "<p>For permanent, tamper-evident vehicle identification, ETIA recommends E-Label <b>E-2512BL</b> — a laser-markable acrylic facestock with a high-strength, chemical-resistant adhesive and a destructible, tamper-evident construction, rated -40 to 150 °C. ETIA supplies genuine materials and helps engineers match the construction to the mounting surface and compliance requirements.</p>",
                 "<p>用于永久、防篡改的车辆标识,ETIA 推荐 E-Label <b>E-2512BL</b> —— 激光可打标丙烯酸面材,配高强度耐化学胶与易碎防篡改结构,耐温 -40 至 150 °C ETIA 供应正品材料,并协助工程师使构造匹配贴附表面与合规要求</p>")
        + ptbl)

    faq = [("Can VIN labels be removed?", "VIN 标签能被撕下吗?",
            "Tamper-evident materials are designed to leave visible evidence if removal is attempted.", "防篡改材料在被尝试撕除时会留下明显痕迹"),
           ("Why use laser-markable labels?", "为什么用激光可打标标签?",
            "Laser marking provides permanent, high-resolution identification without ink or ribbons.", "激光打标无需油墨或碳带,提供永久、高分辨率的标识"),
           ("How long should a VIN label last?", "VIN 标签应能用多久?",
            "Automotive VIN labels are typically designed to remain legible throughout the vehicle's service life.", "汽车 VIN 标签通常设计为在整车使用寿命期内保持可读")]
    s6 = sec("06", "FAQ", "常见问题", "FAQ", "常见问题",
        '<div class="affaq">%s</div>' % "".join(
            '<div class="affq"><h3>%s</h3><p>%s</p></div>' % (T(qe, qz), T(ae, az)) for qe, qz, ae, az in faq))

    cta = ('<section class="blk alt"><div class="wrap"><div class="cta cta-q"><h3>%s</h3><p>%s</p>'
           '<div class="btns"><a class="btn pri" href="%s">%s</a>'
           '<a class="btn on-dark" href="%s">%s</a></div></div></div></section>') % (
        T("Need help selecting the right VIN label?", "需要帮助选对 VIN 标签吗?"),
        T("ETIA helps automotive manufacturers select durable label materials for vehicle identification, compliance and traceability.",
          "ETIA 协助汽车制造商为车辆标识、合规与可追溯选择耐久的标签材料"),
        contact, T("Request Samples", "索取样品"), contact, T("Talk to an Engineer", "咨询工程师"))

    body = (CSS + '<section class="blk"><div class="wrap afwrap">%s</div></section>' % (s1 + s2 + s3 + s4 + s5 + s6)) + cta
    title = _t(lang, "VIN Labels — Permanent Vehicle Identification | ETIA", "VIN 标签 —— 永久车辆标识 | ETIA")
    desc = _t(lang, "VIN labels for permanent vehicle identification — laser-markable, weather- and chemical-resistant, tamper-evident. ETIA helps engineers select the material.",
                    "永久车辆标识用 VIN 标签 —— 可激光打标、耐候耐化学、防篡改 ETIA 协助工程师选材")
    name = _t(lang, "VIN Labels", "VIN 标签")
    crumb = [("Home", "/"), (_t(lang, "Application Notes", "应用笔记"), HUB), (name, path)]
    art = {"@context": "https://schema.org", "@type": "TechArticle", "headline": name, "description": desc,
           "articleSection": _t(lang, "Application Note", "应用笔记"),
           "inLanguage": ("zh-CN" if lang == "zh" else "en"),
           "publisher": {"@type": "Organization", "name": "ETIA Label"}}
    faq_schema = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": _t(lang, qe, qz),
         "acceptedAnswer": {"@type": "Answer", "text": _t(lang, ae, az)}} for qe, qz, ae, az in faq]}
    write(lang, path, page(lang, path, title, desc, name, "", body, crumb, schema_extra=[art, faq_schema], active="insights", hero=hero))
    if lang == "en": hp.track(path, "notes")


def main():
    for lang in LANGS:
        build_green_tire(lang)
        build_tire_bead(lang)
        build_vin(lang)


if __name__ == "__main__":
    main()
