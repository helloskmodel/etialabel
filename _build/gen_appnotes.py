#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Application Notes — one SEO article per application. The sector page carries only
the two keyword cards (Challenge -> Recommendation); the richer material (Label
Purpose, Challenge, Risk of the Wrong Label and the full E-LABEL Solution with
Feature / Benefit / Specification) lives here as an indexed, sitemap-listed article.
Content source: the same _build/data/automotive_apps.json used by the sector page."""
import os, re, json
from urllib.parse import quote
import gen_heatproof as hp
from gen_heatproof import esc, L, page, write, LANGS
import gen_autoapps as auto
from gen_autoapps import _t, PROP_ZH, PROP_CHALLENGE, IC_INTRO, IC_CHAL, IC_SOL, IC_RISK

APPS = auto.APPS
HUB = "/application-notes/"

# Structured, hand-authored application notes (Industry/Application/Technology header +
# numbered sections). Data: _build/data/appnotes.json. These read as full technical
# articles and follow the client's canonical Application-Note structure.
_NOTES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "appnotes.json")
NOTES = json.load(open(_NOTES_FILE, encoding="utf-8"))["notes"] if os.path.exists(_NOTES_FILE) else []
NOTE_URLS = [HUB + n["slug"] + "/" for n in NOTES]


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
# Only applications flagged "note": true are published as full articles (first batch).
PUB = [(a, s) for a, s in zip(APPS, SLUGS) if a.get("note")]
ART_URLS = [HUB + s + "/" for a, s in PUB]

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
    purpose = _t(lang, a.get("purpose_en", ""), a.get("purpose_zh", ""))
    pr0 = next((p for p in a.get("products", []) if p.get("brand", "E-Label") != "Computype"), None)
    model = pr0["model"] if pr0 else ""
    feat = _t(lang, pr0.get("feature_en", ""), pr0.get("feature_zh", "")) if pr0 else ""
    ben = _t(lang, pr0.get("benefit_en", ""), pr0.get("benefit_zh", "")) if pr0 else ""
    def _lc(x): return (x[0].lower() + x[1:]) if x and not x[:2].isupper() else x

    # SEO article flow: Application -> Risks of the Wrong Label -> Material
    # Considerations -> Recommended Products -> ETIA Recommendation -> ETIA Support.
    # Keep the prose lean — one short line per section; the data does the talking.
    if zh:
        heads = ("应用", "用错标签的风险", "材料选型考量", "推荐产品", "ETIA 推荐", "ETIA 支持")
        p_app = purpose
        p_risk2 = risk
        p_mat = ("该应用需耐受:%s" % chal) if chal else ""
        p_rec = ("针对该应用,ETIA 推荐 %s" % model) if model else ""
        p_sup = "ETIA 提供应用评估、打样、供应与长期服务"
    else:
        heads = ("Application", "Risks of Using the Wrong Label", "Material Considerations", "Recommended Products", "ETIA Recommendation", "ETIA Support")
        p_app = purpose
        p_risk2 = risk
        p_mat = ("This label must withstand %s." % _lc(chal)) if chal else ""
        p_rec = ("ETIA recommends %s for this application." % model) if model else ""
        p_sup = "ETIA supports application review, sampling, supply and long-term service."

    keys = ("APPLICATION", "RISKS OF THE WRONG LABEL", "MATERIAL CONSIDERATIONS",
            "RECOMMENDED PRODUCTS", "ETIA RECOMMENDATION", "ETIA SUPPORT")

    # matched product card(s) — Feature / Benefit / Specification
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

    def _p(t): return ('<p>%s</p>' % esc(t)) if t else ""
    def _ns(num, key, heading, inner):
        return ('<div class="nnsec"><div class="num">%02d · %s</div><h2>%s</h2>%s</div>' % (
            num, esc(key), esc(heading), inner)) if inner else ""
    sec = _ns(1, keys[0], heads[0], _p(p_app))
    sec += _ns(2, keys[1], heads[1], _p(p_risk2))
    sec += _ns(3, keys[2], heads[2], _p(p_mat) + _chips(rec_items, "so"))
    if prod_html:
        sec += _ns(4, keys[3], heads[3], prod_html)
    sec += _ns(5, keys[4], heads[4], _p(p_rec))
    sec += _ns(6, keys[5], heads[5], _p(p_sup))

    area = ('<span class="anarea">%s</span>' % esc(area_txt)) if area_txt else ""
    body = CSS + CSS_NOTE + ('<section class="blk"><div class="wrap anwrap">%s%s</div></section>'
                  '<div class="wrap">%s</div>') % (area, sec, hp.cta2(lang, "applications"))
    lede = esc(purpose)
    title = _t(lang, "%s — Material Selection Guide & Application Note | ETIA" % a["name_en"],
                     "%s —— 材料选型指南与应用笔记 | ETIA" % a["name_zh"])
    desc = _t(lang, a["purpose_en"], a["purpose_zh"])
    crumb = [("Home", "/"), (_t(lang, "Application Notes", "应用笔记"), HUB), (name, path)]
    write(lang, path, page(lang, path, title, desc, name, lede, body, crumb, active="insights"))
    if lang == "en":
        hp.track(path, "notes")


CSS_NOTE = """<style>
/* clean engineering-document style — thin dividers, no boxes or fills */
.nnmeta{margin:2px 0 6px;border-top:1px solid var(--line)}
.nnmeta .row{display:grid;grid-template-columns:150px 1fr;gap:16px;padding:10px 2px;border-bottom:1px solid var(--line)}
.nnmeta .lab{font-size:10.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--faint);padding-top:2px}
.nnmeta .tags{font-size:14.5px;color:var(--ink);line-height:1.55}
.nnsec{margin-top:30px}
.nnsec .num{font-size:11px;font-weight:700;letter-spacing:.08em;color:var(--mut);text-transform:uppercase}
.nnsec h2{font-size:19px;font-weight:800;color:var(--blue-deep);margin:5px 0 10px;line-height:1.3}
.nnsec p{font-size:15.5px;line-height:1.75;color:var(--ink)}
.nncfg{margin-top:14px;border-left:3px solid var(--blue);padding:3px 0 3px 16px}
.nncfg .lab{font-size:10.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--mut);margin-bottom:4px}
.nncfg .val{font-size:14.5px;font-weight:700;color:var(--blue-deep);line-height:1.6}
.nnben{list-style:none;padding:0;margin:6px 0 0}
.nnben li{position:relative;padding:6px 0 6px 20px;font-size:15px;color:var(--ink);line-height:1.5;border-bottom:1px solid var(--bg)}
.nnben li::before{content:"—";position:absolute;left:0;top:6px;color:var(--blue);font-weight:700}
@media(max-width:700px){.nnmeta .row{grid-template-columns:1fr;gap:3px}.nnsec h2{font-size:18px}}
</style>"""


def build_note(lang, n):
    def H(e, z): return esc(_t(lang, e, z))
    path = HUB + n["slug"] + "/"
    title = _t(lang, n["title_en"], n["title_zh"])
    rows = ""
    for m in n.get("meta", []):
        tags = _t(lang, m["tags_en"], m["tags_zh"])
        rows += '<div class="row"><div class="lab">%s</div><div class="tags">%s</div></div>' % (
            H(m["label_en"], m["label_zh"]), esc(" · ".join(tags)))
    meta_html = ('<div class="nnmeta">%s</div>' % rows) if rows else ""
    secs = ""
    for idx, s in enumerate(n["sections"]):
        inner = ""
        if s.get("body_en") or s.get("body_zh"):
            inner += '<p>%s</p>' % esc(_t(lang, s.get("body_en", ""), s.get("body_zh", "")))
        if s.get("config_en") or s.get("config_zh"):
            cfg = _t(lang, s.get("config_en", []), s.get("config_zh", []))
            inner += '<div class="nncfg"><div class="lab">%s</div><div class="val">%s</div></div>' % (
                H("Recommended Configuration", "推荐配置"), esc(" · ".join(cfg)))
        if s.get("list_en") or s.get("list_zh"):
            items = _t(lang, s.get("list_en", []), s.get("list_zh", []))
            inner += '<ul class="nnben">%s</ul>' % "".join('<li>%s</li>' % esc(x) for x in items)
        secs += '<div class="nnsec"><div class="num">%02d · %s</div><h2>%s</h2>%s</div>' % (
            idx + 1, esc(s["key"]), H(s["h_en"], s["h_zh"]), inner)
    body = CSS_NOTE + ('<section class="blk"><div class="wrap anwrap">%s%s</div></section>'
                       '<div class="wrap">%s</div>') % (meta_html, secs, hp.cta2(lang, "applications"))
    desc = _t(lang, n["sections"][0].get("body_en", "")[:150], n["sections"][0].get("body_zh", "")[:70])
    crumb = [("Home", "/"), (_t(lang, "Application Notes", "应用笔记"), HUB), (title, path)]
    write(lang, path, page(lang, path,
        _t(lang, "%s — Application Note | ETIA" % n["title_en"], "%s —— 应用笔记 | ETIA" % n["title_zh"]),
        desc, title, "", body, crumb, active="insights"))
    if lang == "en":
        hp.track(path, "notes")


def build_hub(lang):
    zh = (lang == "zh")
    def H(e, z): return esc(_t(lang, e, z))
    blocks = ""
    # featured, hand-authored technical notes first
    if NOTES:
        fcards = ""
        for n in NOTES:
            fcards += ('<a class="ancard" href="%s"><h3>%s</h3><p>%s</p>'
                       '<div class="go">%s →</div></a>') % (
                L(lang, HUB + n["slug"] + "/"), esc(_t(lang, n["title_en"], n["title_zh"])),
                esc(_t(lang, n["sections"][0].get("body_en", ""), n["sections"][0].get("body_zh", ""))[:140]),
                H("Read", "阅读"))
        blocks += '<div class="angroup"><h2>%s</h2><div class="angrid">%s</div></div>' % (
            H("UV Curing", "UV 固化"), fcards)
    # published label notes under a single Automotive heading
    if PUB:
        cards = ""
        for a, s in PUB:
            name = _t(lang, a["name_en"], a["name_zh"])
            cards += ('<a class="ancard" href="%s"><h3>%s</h3><p>%s</p>'
                      '<div class="go">%s →</div></a>') % (
                L(lang, HUB + s + "/"), esc(name),
                esc(_t(lang, a["purpose_en"], a["purpose_zh"])),
                H("Read", "阅读"))
        blocks += '<div class="angroup"><h2>%s</h2><div class="angrid">%s</div></div>' % (
            H("Automotive Labels", "汽车标签"), cards)
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


URLS = [HUB] + ART_URLS + NOTE_URLS

def main():
    for lang in LANGS:
        build_hub(lang)
        for n in NOTES:
            build_note(lang, n)
        for a, s in PUB:
            build_article(lang, a, s)


if __name__ == "__main__":
    main()
