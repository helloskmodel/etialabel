#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Application Notes — one SEO article per application. The sector page carries only
the two keyword cards (Challenge -> Recommendation); the richer material (Label
Purpose, Challenge, Risk of the Wrong Label and the full E-LABEL Solution with
Feature / Benefit / Specification) lives here as an indexed, sitemap-listed article.
Content source: the same _build/data/automotive_apps.json used by the sector page."""
import re
from urllib.parse import quote
import gen_heatproof as hp
from gen_heatproof import esc, L, page, write, LANGS
import gen_autoapps as auto
from gen_autoapps import _t, PROP_ZH, PROP_CHALLENGE, IC_INTRO, IC_CHAL, IC_SOL, IC_RISK

APPS = auto.APPS
HUB = "/application-notes/"


def slug(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s


def _slugs():
    seen, out = {}, []
    for a in APPS:
        s = slug(a["name_en"])
        if s in seen:                       # guarantee uniqueness
            seen[s] += 1; s = "%s-%d" % (s, seen[s])
        else:
            seen[s] = 1
        out.append(s)
    return out

SLUGS = _slugs()
ART_URLS = [HUB + s + "/" for s in SLUGS]

CSS = """<style>
.anwrap{max-width:900px}
.anlede{font-size:18px;line-height:1.7;color:var(--ink)}
.anarea{display:inline-block;background:var(--tint-blue);color:var(--blue-deep);font-size:12px;font-weight:800;border-radius:20px;padding:5px 14px;margin-bottom:14px}
.ansec{margin-top:30px}
.ansec h2{font-size:20px;color:var(--blue-deep);display:flex;align-items:center;gap:10px;margin-bottom:12px}
.ansec h2 .i{width:24px;height:24px;flex:0 0 auto;color:var(--blue)}.ansec h2 .i svg{width:24px;height:24px}
.ansec.risk h2{color:#c0341d}.ansec.risk h2 .i{color:#c0341d}
.ansec.chal h2{color:#c2621f}.ansec.chal h2 .i{color:#c2621f}
.ansec.sol h2{color:var(--green-d)}.ansec.sol h2 .i{color:var(--green-d)}
.ansec p{font-size:15.5px;line-height:1.7;color:var(--ink)}
.anchips{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 12px}
.anchip{font-size:12.5px;font-weight:700;border-radius:20px;padding:5px 13px;line-height:1.25}
.anchip.ch{background:#fff1e8;color:#b4531a;border:1px solid #f4cdb0}
.anchip.so{background:var(--mint);color:var(--green-d);border:1px solid #cfe6c5}
.anriskbox{background:#fff6f2;border:1px solid #f4cdb0;border-left:4px solid #e0762f;border-radius:10px;padding:15px 20px}
.anriskbox p{color:#8a3f14;margin:0}
.anprod{border:1px solid var(--line);border-radius:14px;padding:22px 24px;background:#fff;margin-top:4px}
.anprod .avbrand{display:inline-block;font-size:11px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--green-d);background:var(--mint);border:1px solid #cfe6c5;border-radius:6px;padding:3px 9px}
.anprod .m{font-weight:800;color:var(--blue-deep);font-size:22px;margin:10px 0 2px}
.anprod .row{margin-top:13px}
.anprod .row span{display:block;color:var(--faint);font-weight:800;text-transform:uppercase;font-size:10.5px;letter-spacing:.05em;margin-bottom:2px}
.anprod .row p{font-size:14.5px;color:var(--ink);line-height:1.55;margin:0}
.anprod .cta{display:inline-block;margin-top:18px;font-weight:800;color:#fff;background:var(--green-d);border-radius:8px;padding:10px 18px;text-decoration:none;font-size:14px}
/* index */
.angroup{margin-top:34px}
.angroup h2{font-size:15px;text-transform:uppercase;letter-spacing:.05em;color:var(--mut);margin-bottom:14px}
.angrid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.ancard{display:flex;flex-direction:column;border:1px solid var(--line);border-radius:12px;padding:20px 20px;background:#fff;text-decoration:none;transition:.16s}
.ancard:hover{border-color:var(--blue);box-shadow:0 12px 30px rgba(20,40,90,.12);transform:translateY(-3px)}
.ancard h3{font-size:16px;color:var(--blue-deep);font-weight:800;line-height:1.3}
.ancard p{font-size:13px;color:var(--mut);line-height:1.55;margin-top:8px;flex:1}
.ancard .go{font-size:12.5px;font-weight:700;color:var(--green-d);margin-top:14px}
@media(max-width:820px){.angrid{grid-template-columns:1fr}}
</style>"""


def _chips(items, cls):
    return '<div class="anchips">%s</div>' % "".join(
        '<span class="anchip %s">%s</span>' % (cls, esc(x)) for x in items)


def build_article(lang, a, s):
    zh = (lang == "zh")
    def H(e, z): return esc(_t(lang, e, z))
    path = HUB + s + "/"
    name = _t(lang, a["name_en"], a["name_zh"])
    # Challenge chips (stressors) + prose
    seen = set(); ch_items = []
    for pr in a.get("props", []):
        pair = PROP_CHALLENGE.get(pr)
        if pair and pair[0] not in seen:
            seen.add(pair[0]); ch_items.append(_t(lang, pair[0], pair[1]))
    rec_items = [_t(lang, pr, PROP_ZH.get(pr, pr)) for pr in a.get("props", [])]
    chal_prose = _t(lang, a.get("challenge_en", ""), a.get("challenge_zh", ""))
    risk_prose = _t(lang, a.get("risk_en", ""), a.get("risk_zh", ""))

    area_txt = _t(lang, a.get("area", ""), a.get("area_zh", a.get("area", "")))
    chal = _t(lang, a.get("challenge_en", ""), a.get("challenge_zh", ""))
    risk = _t(lang, a.get("risk_en", ""), a.get("risk_zh", ""))
    pr0 = next((p for p in a.get("products", []) if p.get("brand", "E-Label") != "Computype"), None)
    model = pr0["model"] if pr0 else ""
    feat = _t(lang, pr0.get("feature_en", ""), pr0.get("feature_zh", "")) if pr0 else ""
    ben = _t(lang, pr0.get("benefit_en", ""), pr0.get("benefit_zh", "")) if pr0 else ""
    def _lc(x): return (x[0].lower() + x[1:]) if x and not x[:2].isupper() else x

    # Prose article, composed from the application's data — reads as an authored
    # technical note rather than a datasheet.
    if zh:
        Hs = ("概述", "应用环境", "用错标签的代价", "推荐方案", "我们的方法")
        p_ov = "在整车的%s,%s不仅是部件上的一个标记,更承载着车辆在整个生命周期中所依赖的安全、警示与可追溯信息,由于这些信息必须从装配线一直保持到多年使用之后,标签结构的选择是一项工程决策,而非收尾环节" % (area_txt, a["name_zh"])
        p_env = "该位置会让标签持续面对:%s,这些因素分别作用于标签系统的不同部分——与基材的粘接、面材的尺寸稳定性,以及印刷图文的耐久性——正是它们长期叠加的作用,让通用材料失效" % chal
        p_risk = "%s,在以安全与法规合规为准绳的行业里,标签一旦脱落或不可读,绝非外观瑕疵——它可能导致停线、返工,甚至成为现场安全与召回隐患,选错材料的代价远不止一张标签的价格" % risk
        p_sol = "针对该应用,ETIA 推荐 %s,其结构为:%s——正是针对上述工况而设计,%s,从贴附之初到部件的整个使用周期,标签始终保持粘接与印刷信息完好" % (model, feat, ben)
        p_close = "ETIA 的每一次推荐都从应用出发,而非从产品出发,如果您的工况有所不同——更高的温区、更低表面能的基材、更严格的合规要求——我们会先测试、再匹配,然后才给出建议"
    else:
        Hs = ("Overview", "The operating environment", "The cost of the wrong label", "Recommended solution", "The ETIA approach")
        p_ov = "Across the %s, %s do more than mark a part — they carry the safety, warning and traceability information a vehicle depends on throughout its life. Because that information has to remain intact from the assembly line through years of service, the label construction is an engineering choice, not a finishing touch." % ((a.get("area", "") or "").lower(), a["name_en"])
        p_env = "This position exposes the label to a combination of stressors: %s. Each acts on a different part of the label system — the adhesive bond to the substrate, the dimensional stability of the facestock and the durability of the printed image — and it is their sustained combination, not any single condition, that defeats general-purpose materials." % chal
        p_risk = "%s In an industry governed by safety and regulatory compliance, a label that lifts or becomes unreadable is not a cosmetic defect — it can stop a line, force rework, or become a field-safety and recall liability. The cost of the wrong material is measured in far more than the price of a label." % risk
        p_sol = "For this application ETIA specifies %s. Its construction is purpose-built: %s — engineered directly against the conditions above. In service it %s. From first application through the full life of the part, the label keeps its adhesion and its printed information intact." % (model, feat, _lc(ben))
        p_close = "Every ETIA recommendation starts from the application, not the product. If your conditions differ — a hotter zone, a lower-energy surface, a tighter compliance requirement — we test and match the construction before we recommend it."

    # matched product card (Feature / Benefit / Specification) — sits inside the Solution section
    prod_html = ""
    for pr in a.get("products", []):
        if pr.get("brand", "E-Label") == "Computype":
            continue
        rows = ""
        for key, en, zh_l in (("feature", "Feature", "特性"), ("benefit", "Benefit", "收益"),
                              ("spec", "Specification", "规格")):
            val = _t(lang, pr.get(key + "_en", ""), pr.get(key + "_zh", ""))
            if val:
                rows += '<div class="row"><span>%s</span><p>%s</p></div>' % (H(en, zh_l), esc(val))
        url = L(lang, "/contact/?product=%s" % quote(pr["model"], safe=""))
        brand = pr.get("brand", "E-Label")
        prod_html += ('<div class="anprod"><span class="avbrand">%s</span>'
                      '<div class="m">%s</div>%s<a class="cta" href="%s">%s</a></div>') % (
            esc("E-LABEL" if brand == "E-Label" else brand.upper()),
            esc(pr["model"]), rows, url, H("Talk to a Specialist", "咨询专家"))

    sec = '<div class="ansec"><h2>%s</h2><p>%s</p></div>' % (esc(Hs[0]), esc(p_ov))
    if chal:
        sec += ('<div class="ansec chal"><h2><span class="i">%s</span>%s</h2><p>%s</p>%s</div>') % (
            IC_CHAL, esc(Hs[1]), esc(p_env), _chips(ch_items, "ch"))
    if risk:
        sec += ('<div class="ansec risk"><h2><span class="i">%s</span>%s</h2><p>%s</p></div>') % (
            IC_RISK, esc(Hs[2]), esc(p_risk))
    if pr0:
        sec += ('<div class="ansec sol"><h2><span class="i">%s</span>%s</h2><p>%s</p>%s%s</div>') % (
            IC_SOL, esc(Hs[3]), esc(p_sol), prod_html, _chips(rec_items, "so"))
    sec += '<div class="ansec"><h2>%s</h2><p>%s</p></div>' % (esc(Hs[4]), esc(p_close))

    area = ('<span class="anarea">%s</span>' % esc(area_txt)) if area_txt else ""
    body = CSS + ('<section class="blk"><div class="wrap anwrap">%s%s</div></section>'
                  '<div class="wrap">%s</div>') % (area, sec, hp.cta2(lang, "applications"))
    lede = esc(_t(lang, a["purpose_en"], a["purpose_zh"]))
    title = _t(lang, "%s — Application Note & Material Selection Guide | ETIA" % a["name_en"],
                     "%s —— 应用笔记与选型指南 | ETIA" % a["name_zh"])
    desc = _t(lang, a["purpose_en"], a["purpose_zh"])
    crumb = [("Home", "/"), ("Application Notes", HUB), (name, path)]
    write(lang, path, page(lang, path, title, desc, name, lede, body, crumb, active="insights"))
    if lang == "en":
        hp.track(path, "notes")


def build_hub(lang):
    zh = (lang == "zh")
    def H(e, z): return esc(_t(lang, e, z))
    # group articles by area, in first-seen order
    order, groups = [], {}
    for a, s in zip(APPS, SLUGS):
        ar = a.get("area", "Other")
        if ar not in groups:
            groups[ar] = []; order.append(ar)
        groups[ar].append((a, s))
    blocks = ""
    for ar in order:
        cards = ""
        for a, s in groups[ar]:
            name = _t(lang, a["name_en"], a["name_zh"])
            cards += ('<a class="ancard" href="%s"><h3>%s</h3><p>%s</p>'
                      '<div class="go">%s →</div></a>') % (
                L(lang, HUB + s + "/"), esc(name),
                esc(_t(lang, a["purpose_en"], a["purpose_zh"])),
                H("Read", "阅读"))
        az = groups[ar][0][0].get("area_zh", ar)
        blocks += '<div class="angroup"><h2>%s</h2><div class="angrid">%s</div></div>' % (
            esc(_t(lang, ar, az)), cards)
    lede = H("Application-by-application guidance: what each label is for, the environment challenge it faces, the risk of the wrong label, and the recommended E-LABEL material.",
             "逐个应用的选型指引:每种标签的用途、面临的环境挑战、用错标签的风险,以及推荐的 E-LABEL 材料。")
    body = CSS + ('<section class="blk"><div class="wrap">%s</div></section>'
                  '<div class="wrap">%s</div>') % (blocks, hp.cta2(lang, "applications"))
    crumb = [("Home", "/"), ("Application Notes", HUB)]
    write(lang, HUB, page(lang, HUB,
        _t(lang, "Application Notes — Label Selection Guidance by Application | ETIA",
                 "应用笔记 —— 按应用的标签选型指引 | ETIA"),
        _t(lang, "Label selection guidance by application — purpose, environment challenge, risk of the wrong label and recommended E-LABEL material.",
                 "按应用的标签选型指引 —— 用途、环境挑战、用错标签的风险与推荐 E-LABEL 材料。"),
        _t(lang, "Application Notes", "应用笔记"), lede, body, crumb, active="insights"))
    if lang == "en":
        hp.track(HUB, "notes")


URLS = [HUB] + ART_URLS

def main():
    for lang in LANGS:
        build_hub(lang)
        for a, s in zip(APPS, SLUGS):
            build_article(lang, a, s)


if __name__ == "__main__":
    main()
