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

HUB = "/application-notes/"


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _entries():
    """Flat, globally-unique list of (sector, app, slug) across every sector."""
    seen, out = {}, []
    for sector, apps in auto.SECTORS:
        for a in apps:
            s = slug(a["name_en"])
            if s in seen:
                seen[s] += 1; s = "%s-%d" % (s, seen[s])
            else:
                seen[s] = 1
            out.append((sector, a, s))
    return out

ENTRIES = _entries()
ART_URLS = [HUB + s + "/" for _, _, s in ENTRIES]

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


def build_article(lang, sector, a, s):
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

    sec = ""
    # Challenge
    sec += ('<div class="ansec chal"><h2><span class="i">%s</span>%s</h2>%s%s</div>') % (
        IC_CHAL, H("Challenge", "应用挑战"), _chips(ch_items, "ch"),
        ('<p>%s</p>' % esc(chal_prose)) if chal_prose else "")
    # Risk of wrong label
    if risk_prose:
        sec += ('<div class="ansec risk"><h2><span class="i">%s</span>%s</h2>'
                '<div class="anriskbox"><p>%s</p></div></div>') % (
            IC_RISK, H("Risk of Wrong Label", "用错标签风险"), esc(risk_prose))
    # Recommended Solution — own-brand product card(s) with Feature / Benefit / Specification.
    # Computype (distributor lines) are held for now and skipped.
    prod_html = ""
    for pr in a.get("products", []):
        brand = pr.get("brand", "E-Label")
        if brand == "Computype":
            continue
        rows = ""
        for key, en, zh_l in (("feature", "Feature", "特性"), ("benefit", "Benefit", "收益"),
                              ("spec", "Specification", "规格")):
            val = _t(lang, pr.get(key + "_en", ""), pr.get(key + "_zh", ""))
            if val:
                rows += '<div class="row"><span>%s</span><p>%s</p></div>' % (H(en, zh_l), esc(val))
        url = L(lang, "/contact/?product=%s" % quote(pr["model"], safe=""))
        prod_html += ('<div class="anprod"><span class="avbrand">%s</span>'
                      '<div class="m">%s</div>%s<a class="cta" href="%s">%s</a></div>') % (
            esc(brand.upper()), esc(pr["model"]), rows, url, H("Talk to a Specialist", "咨询专家"))
    if prod_html:
        sec += ('<div class="ansec sol"><h2><span class="i">%s</span>%s</h2>%s</div>') % (
            IC_SOL, H("Recommended Solution", "推荐方案"), prod_html)
    # recommendation keyword chips as a quick reference under the solution
    if rec_items:
        sec += ('<div class="ansec sol"><h2><span class="i">%s</span>%s</h2>%s</div>') % (
            IC_INTRO, H("Material Properties", "材料属性"), _chips(rec_items, "so"))

    area_txt = _t(lang, a.get("area", ""), a.get("area_zh", a.get("area", "")))
    area = ('<span class="anarea">%s</span>' % esc(area_txt)) if area_txt else ""
    body = CSS + ('<section class="blk"><div class="wrap anwrap">%s%s</div></section>'
                  '<div class="wrap">%s</div>') % (area, sec, hp.cta2(lang, "applications"))
    lede = esc(_t(lang, a["purpose_en"], a["purpose_zh"]))
    title = _t(lang, "%s — Label Purpose, Challenge & Recommended Material | ETIA" % a["name_en"],
                     "%s —— 标签用途、应用挑战与推荐材料 | ETIA" % a["name_zh"])
    desc = _t(lang, a["purpose_en"], a["purpose_zh"])
    crumb = [("Home", "/"), (_t(lang, "Application Notes", "应用笔记"), HUB), (name, path)]
    write(lang, path, page(lang, path, title, desc, name, lede, body, crumb, active="insights"))
    if lang == "en":
        hp.track(path, "notes")


def build_hub(lang):
    zh = (lang == "zh")
    def H(e, z): return esc(_t(lang, e, z))
    # group articles by sector, in registry order
    order, groups = [], {}
    for sector, a, s in ENTRIES:
        key = sector["name_en"]
        if key not in groups:
            groups[key] = (sector, []); order.append(key)
        groups[key][1].append((a, s))
    blocks = ""
    for key in order:
        sector, items = groups[key]
        cards = ""
        for a, s in items:
            name = _t(lang, a["name_en"], a["name_zh"])
            cards += ('<a class="ancard" href="%s"><h3>%s</h3><p>%s</p>'
                      '<div class="go">%s →</div></a>') % (
                L(lang, HUB + s + "/"), esc(name),
                esc(_t(lang, a["purpose_en"], a["purpose_zh"])),
                H("Read", "阅读"))
        blocks += '<div class="angroup"><h2>%s</h2><div class="angrid">%s</div></div>' % (
            esc(_t(lang, sector["name_en"], sector["name_zh"])), cards)
    lede = H("Application-by-application guidance: what each label is for, the environment challenge it faces, the risk of the wrong label, and the recommended material.",
             "逐个应用的选型指引:每种标签的用途、面临的环境挑战、用错标签的风险,以及推荐的材料。")
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
        for sector, a, s in ENTRIES:
            build_article(lang, sector, a, s)


if __name__ == "__main__":
    main()
