#!/usr/bin/env python3
"""垂直专业站生成器 —— 一个数据库孵化多个"小而美"利基站, 内置 Google EEAT 结构化SEO.

用法: python3 scripts/build_microsite.py <vertical> [输出路径]
  vertical ∈ VERTICALS 的键: polyimide / automotive / metallurgy / medical
每个站是自包含单HTML(数据内嵌), 可直接传腾讯云COS/CloudBase静态托管。

EEAT 落地:
  Experience 经验  —— 20年行业positioning(取自项目自述), 真实案例入口
  Expertise 专业   —— 材料/温度/胶系技术科普段, 选型逻辑
  Authoritativeness—— 跨品牌聚合(N款/M品牌), 每款直连官方TDS
  Trustworthiness  —— 参数溯源、"官网未公布留空不臆造"透明声明、org信息
SEO: <title>/meta description/canonical/OG + JSON-LD(Organization/BreadcrumbList/ItemList/FAQPage)
"""
import html
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data/labels.db"
SITE = "https://label.etiatech.com"   # 部署后替换为真实域名

# ---------------------------------------------------------------- 垂直站配置
VERTICALS = {
    "polyimide": {
        "slug": "polyimide-labels",
        "h1": "聚酰亚胺高温标签",
        "tagline": "跨 8 大原厂品牌 · 一站选型 · -196℃ 到 300℃+ 全温区",
        "filter": "f.face_code='POLYIMIDE'",
        "accent": "#E0A93B", "accent2": "#C6871F", "ink": "#F1E9D8",
        "bg": "#171310", "surf": "#211B14", "line": "#3A2F22",
        "seo_title": "聚酰亚胺(PI)高温标签选型 | 3M/贝迪/Polyonics等8大品牌107款对比 - ETIA",
        "seo_desc": "聚酰亚胺高温标签一站选型:汇集3M、贝迪、Polyonics、琳得科等8大原厂品牌107款PI标签,耐温-196~300℃+,覆盖PCB、回流焊、动力电池、线缆标识,每款直连官方TDS。20年工业标签选型经验。",
        "why_title": "为什么选聚酰亚胺(PI)标签",
        "why": [
            ("耐温天花板", "聚酰亚胺薄膜长期耐温可达 260℃,短时峰值 300℃以上,是SMT回流焊、波峰焊过炉后仍保持条码可读的行业标准面材。"),
            ("尺寸稳定", "PI薄膜无增塑剂、高温不收缩不发脆,过炉多次仍不卷边、不变形,适合PCB全流程追溯。"),
            ("化学与阻燃", "耐焊剂、耐清洗溶剂;多数PI标签本征阻燃(UL94 V-0级),满足电子/新能源安规。"),
            ("宽温域", "配低温胶后可低至 -196℃(液氮),同一面材覆盖高温过炉到深冷冻存两端极端工况。"),
        ],
        "faq": [
            ("聚酰亚胺标签最高能耐多少度?", "长期连续耐温通常到 260℃,短时峰值(如回流焊过炉几十秒到几分钟)可达 300℃以上。具体以每款产品官方TDS为准,本站每款均标注并直连TDS。"),
            ("聚酰亚胺和耐高温PET标签怎么选?", "180℃以内、成本敏感的场景用耐高温PET即可;需要过回流焊(240~260℃)、或长期高温环境,必须用聚酰亚胺。本站可按'耐高温可达温度'直接筛选。"),
            ("哪些品牌有聚酰亚胺高温标签?", "本站汇集Polyonics、艾利丹尼森、贝迪、康普泰、富林康、琳得科、YS Tech、3M共8大原厂品牌的PI标签,可跨品牌对比耐温、胶系与认证。"),
            ("聚酰亚胺标签能用于低温冻存吗?", "可以。聚酰亚胺面材配专用低温胶后可耐受 -196℃ 液氮环境,本站含此类冻存管标签,按'耐低温可达'筛选即可。"),
        ],
    },
    # 其余垂直站(换filter+文案即可孵化), 先占位:
    "automotive": {"slug": "automotive-labels", "h1": "汽车标签解决方案",
        "tagline": "发动机舱 · 动力电池 · 线束 · VIN · 轮胎 全场景",
        "filter": "EXISTS(SELECT 1 FROM product_application pa JOIN application_dict d ON d.app_id=pa.app_id WHERE pa.product_id=p.product_id AND d.app_code='AUTOMOTIVE')",
        "accent": "#3D8BD4", "accent2": "#2C6BA8", "ink": "#E6EDF4",
        "bg": "#0E141B", "surf": "#182430", "line": "#2A3947",
        "seo_title": "汽车标签选型 | 发动机舱/动力电池/线束/VIN标签 多品牌对比 - ETIA",
        "seo_desc": "汽车行业标签一站选型,覆盖发动机舱耐高温、动力电池、线束标识、VIN码、轮胎标签,汇集3M/艾利丹尼森/富林康等多品牌,每款直连官方TDS。",
        "why_title": "汽车标签的严苛工况", "why": [], "faq": []},
    "metallurgy": {"slug": "steel-metallurgy-labels", "h1": "钢铁冶金追溯标签",
        "tagline": "钢坯 · 连铸 · 锻造 · 热处理 极端高温追溯",
        "filter": "EXISTS(SELECT 1 FROM product_application pa JOIN application_dict d ON d.app_id=pa.app_id WHERE pa.product_id=p.product_id AND d.app_code='METALLURGY')",
        "accent": "#D2691E", "accent2": "#A0491B", "ink": "#F0E6DC",
        "bg": "#191310", "surf": "#241A14", "line": "#3E2E22",
        "seo_title": "钢铁冶金高温追溯标签 | 钢坯/连铸/锻造 耐600~1200℃ - ETIA",
        "seo_desc": "钢铁冶金行业高温追溯标签,耐受600~1200℃钢坯、连铸、锻造、热处理工况,含可贴热面产品,每款直连官方数据。",
        "why_title": "冶金追溯的温度挑战", "why": [], "faq": []},
    "medical": {"slug": "medical-pharma-labels", "h1": "医药与医疗标签",
        "tagline": "冻存 · 血袋 · 灭菌 · 药品包装 · 诊断耗材",
        "filter": "EXISTS(SELECT 1 FROM product_application pa JOIN application_dict d ON d.app_id=pa.app_id WHERE pa.product_id=p.product_id AND d.app_code IN ('MEDICAL','PHARMACY','LAB_BIO'))",
        "accent": "#2E9E7A", "accent2": "#217A5E", "ink": "#E4F0EB",
        "bg": "#0D1714", "surf": "#16241F", "line": "#26382F",
        "seo_title": "医药医疗标签选型 | 冻存/血袋/灭菌/药品包装 多品牌 - ETIA",
        "seo_desc": "医药与医疗行业标签一站选型:液氮冻存管、血袋(ISBT 128)、耐高压灭菌、药品包装、诊断耗材,汇集康普泰/富林康等品牌,每款直连官方数据。",
        "why_title": "医疗合规与极端工况", "why": [], "faq": []},
}


def esc(s):
    return html.escape(str(s or ""))


def fetch(vcfg):
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    rows = db.execute(f"""SELECT b.brand_name_cn bcn,b.brand_code bc,p.model_no m,p.product_name_cn nc,
      p.product_name_en ne,f.face_name_cn fc,a.adh_name_cn ac,p.temp_long_min t0,p.temp_long_max t1,
      p.temp_peak_max tp,p.temp_tier tier,p.chem_grade chem,p.thickness_um th,p.color c,
      p.certification cert,p.application_desc ds,p.sub_application sub,p.tds_url tds,p.source_url src,
      p.feature ft,p.benefit bn
      FROM product p JOIN brand b ON b.brand_id=p.brand_id
      LEFT JOIN facestock_dict f ON f.face_id=p.face_id
      LEFT JOIN adhesive_dict a ON a.adh_id=p.adh_id
      WHERE p.status=1 AND ({vcfg['filter']}) ORDER BY p.temp_long_max DESC""").fetchall()
    out = []
    for r in rows:
        d = {k: r[k] for k in r.keys() if r[k] not in (None, "")}
        for k in ("ft", "bn", "ds"):
            if k in d and len(d[k]) > 240:
                d[k] = d[k][:240] + "…"
        out.append(d)
    # 应用分布 & 品牌分布
    apps = {}
    brands = {}
    for d in out:
        if d.get("sub"):
            apps[d["sub"]] = apps.get(d["sub"], 0) + 1
        brands[d.get("bcn", "")] = brands.get(d.get("bcn", ""), 0) + 1
    db.close()
    return out, apps, brands


def render(vkey):
    v = VERTICALS[vkey]
    prods, apps, brands = fetch(v)
    n = len(prods)
    nb = len([b for b in brands if b])
    tds_n = sum(1 for d in prods if d.get("tds"))
    temps = [d["t1"] for d in prods if "t1" in d]
    tmax = max(temps) if temps else 0
    tmins = [d["t0"] for d in prods if "t0" in d]
    tmin = min(tmins) if tmins else 0
    canonical = f"{SITE}/{v['slug']}"

    # JSON-LD 结构化数据(EEAT/SEO)
    ld = [
        {"@context": "https://schema.org", "@type": "Organization",
         "name": "ETIA 特种标签", "url": SITE,
         "description": "深耕工业特种标签20年,代理3M/Brady/LINTEC/Avery/Polyonics等全球品牌,提供一站式选型与技术支持。",
         "knowsAbout": ["工业标签", "聚酰亚胺标签", "高温标签", "标签选型"]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首页", "item": SITE},
            {"@type": "ListItem", "position": 2, "name": v["h1"], "item": canonical}]},
        {"@context": "https://schema.org", "@type": "ItemList", "name": v["h1"],
         "numberOfItems": n,
         "itemListElement": [
            {"@type": "ListItem", "position": i + 1,
             "item": {"@type": "Product", "name": f"{d.get('bcn','')} {d.get('m','')}",
                      "brand": d.get("bcn", ""),
                      "material": "聚酰亚胺" if vkey == "polyimide" else d.get("fc", ""),
                      "url": d.get("tds") or d.get("src", "")}}
            for i, d in enumerate(prods[:50])]},
    ]
    if v.get("faq"):
        ld.append({"@context": "https://schema.org", "@type": "FAQPage",
                   "mainEntity": [{"@type": "Question", "name": q,
                                   "acceptedAnswer": {"@type": "Answer", "text": a}}
                                  for q, a in v["faq"]]})
    ld_json = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)

    data_json = json.dumps(prods, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    why_html = "".join(
        f'<div class="why-card"><h3>{esc(t)}</h3><p>{esc(b)}</p></div>' for t, b in v.get("why", []))
    app_chips = "".join(
        f'<button class="fchip" data-sub="{esc(s)}">{esc(s)} <b>{c}</b></button>'
        for s, c in sorted(apps.items(), key=lambda x: -x[1]))
    brand_row = "".join(
        f'<span class="brand-badge">{esc(b)} <b>{c}</b></span>' for b, c in sorted(brands.items(), key=lambda x: -x[1]) if b)
    faq_html = "".join(
        f'<details class="faq"><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in v.get("faq", []))

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(v['seo_title'])}</title>
<meta name="description" content="{esc(v['seo_desc'])}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(v['seo_title'])}">
<meta property="og:description" content="{esc(v['seo_desc'])}">
<meta property="og:url" content="{canonical}">
{ld_json}
<style>
:root{{--acc:{v['accent']};--acc2:{v['accent2']};--ink:{v['ink']};--bg:{v['bg']};
  --surf:{v['surf']};--line:{v['line']};--mut:#9a9186;}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{margin:0;background:var(--bg);color:var(--ink);
  font:15px/1.7 "PingFang SC","Hiragino Sans GB","Microsoft YaHei",system-ui,sans-serif}}
a{{color:var(--acc)}}
.wrap{{max-width:1200px;margin:0 auto;padding:0 22px}}
header{{position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--bg) 90%,transparent);
  backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}}
.nav{{max-width:1200px;margin:0 auto;padding:13px 22px;display:flex;align-items:center;gap:20px}}
.brand{{font-weight:800;letter-spacing:.06em;font-size:18px}}
.brand b{{color:var(--acc)}}
.nav a{{color:var(--mut);text-decoration:none;font-size:14px}}.nav a:hover{{color:var(--ink)}}
.cta-top{{margin-left:auto;background:var(--acc);color:#1a1408;padding:8px 18px;border-radius:7px;
  font-weight:700;font-size:14px;text-decoration:none}}
/* hero */
.hero{{padding:64px 0 46px;position:relative;overflow:hidden}}
.hero::after{{content:"";position:absolute;right:-140px;top:-80px;width:520px;height:520px;
  background:radial-gradient(circle,var(--acc) 0,transparent 62%);opacity:.14;pointer-events:none}}
.eyebrow{{color:var(--acc);font-weight:700;letter-spacing:.16em;font-size:12.5px;text-transform:uppercase}}
.hero h1{{font-size:clamp(30px,5.4vw,52px);line-height:1.1;margin:14px 0 10px;font-weight:800;text-wrap:balance;letter-spacing:-.01em}}
.hero .tag{{font-size:clamp(15px,2.2vw,19px);color:var(--mut);max-width:640px}}
.metrics{{display:flex;flex-wrap:wrap;gap:34px;margin:34px 0 8px}}
.metric b{{display:block;font-size:38px;font-weight:800;color:var(--acc);font-variant-numeric:tabular-nums;line-height:1}}
.metric span{{color:var(--mut);font-size:13px}}
.hero-cta{{display:inline-block;margin-top:26px;background:var(--acc);color:#1a1408;padding:13px 30px;
  border-radius:9px;font-weight:800;font-size:16px;text-decoration:none}}
.hero-cta:hover{{background:var(--acc2)}}
/* EEAT 信任条 */
.trustbar{{border-top:1px solid var(--line);border-bottom:1px solid var(--line);background:var(--surf)}}
.trustbar .wrap{{display:flex;flex-wrap:wrap;gap:26px;padding:18px 22px;font-size:13.5px;color:var(--mut)}}
.trustbar b{{color:var(--ink)}}
/* sections */
section{{padding:52px 0}}
.eyebrow2{{color:var(--acc);font-weight:700;font-size:13px;letter-spacing:.1em}}
h2{{font-size:clamp(22px,3.4vw,32px);margin:8px 0 26px;font-weight:800;text-wrap:balance}}
.why-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}}
.why-card{{background:var(--surf);border:1px solid var(--line);border-radius:13px;padding:22px}}
.why-card h3{{margin:0 0 8px;font-size:17px;color:var(--acc)}}
.why-card p{{margin:0;color:var(--mut);font-size:14px}}
.brand-strip{{display:flex;flex-wrap:wrap;gap:10px;margin-top:8px}}
.brand-badge{{background:var(--surf);border:1px solid var(--line);border-radius:20px;padding:5px 14px;font-size:13.5px}}
.brand-badge b{{color:var(--acc)}}
/* 产品筛选+网格 */
.filters{{display:flex;flex-wrap:wrap;gap:8px;margin:6px 0 22px}}
.fchip{{background:var(--surf);border:1px solid var(--line);color:var(--ink);border-radius:20px;
  padding:5px 14px;font-size:13px;cursor:pointer}}
.fchip.on{{background:var(--acc);border-color:var(--acc);color:#1a1408;font-weight:700}}
.fchip b{{opacity:.7;font-weight:600}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px}}
.card{{background:var(--surf);border:1px solid var(--line);border-radius:13px;overflow:hidden;cursor:pointer;
  transition:transform .15s,border-color .15s;display:flex;flex-direction:column}}
.card:hover{{transform:translateY(-3px);border-color:var(--acc)}}
.card .sw{{height:104px;display:flex;align-items:center;justify-content:center;
  background:linear-gradient(135deg,var(--acc2),var(--acc));position:relative}}
.card .chip-mock{{background:#fff;color:#241a08;border-radius:6px;padding:8px 12px;font-weight:800;
  font-size:15px;box-shadow:0 3px 10px rgba(0,0,0,.3);transform:rotate(-2deg)}}
.card .bc{{position:absolute;top:8px;left:8px;background:rgba(0,0,0,.4);color:#fff;font-size:11px;
  padding:2px 8px;border-radius:10px}}
.card .info{{padding:12px 14px;display:flex;flex-direction:column;gap:7px;flex:1}}
.card .nm{{font-size:14px;font-weight:600;line-height:1.4;display:-webkit-box;-webkit-line-clamp:2;
  -webkit-box-orient:vertical;overflow:hidden}}
.tags{{display:flex;flex-wrap:wrap;gap:4px}}
.tg{{border:1px solid var(--line);border-radius:5px;padding:0 7px;font-size:11px;color:var(--mut);line-height:19px}}
.tg.hot{{background:var(--acc);color:#1a1408;border:none;font-weight:700}}
.card .ft{{margin-top:auto;font-size:12px;color:var(--acc);font-weight:600}}
/* drawer */
#dm{{position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:40;display:none}}
#dm.on{{display:block}}
#dw{{position:fixed;top:0;right:-620px;width:min(600px,96vw);height:100vh;background:var(--surf);
  border-left:1px solid var(--line);z-index:41;transition:right .25s;overflow-y:auto;padding:24px}}
#dw.on{{right:0}}
#dw h3{{margin:0 0 4px;font-size:22px}}
#dw .sub{{color:var(--mut);margin:0 0 14px;font-size:13px}}
.spec{{width:100%;border-collapse:collapse;margin:8px 0 16px}}
.spec th{{text-align:left;color:var(--mut);font-weight:600;font-size:12.5px;padding:6px 10px 6px 0;
  border-bottom:1px solid var(--line);white-space:nowrap;width:92px;vertical-align:top}}
.spec td{{padding:6px 0;border-bottom:1px solid var(--line);font-size:13.5px}}
.dw-cta{{display:inline-block;background:var(--acc);color:#1a1408;padding:11px 24px;border-radius:9px;
  font-weight:800;text-decoration:none;margin:6px 8px 6px 0}}
.dw-cta.sec{{background:transparent;color:var(--acc);border:1.5px solid var(--acc)}}
.blk{{background:var(--bg);border:1px solid var(--line);border-radius:9px;padding:11px 14px;margin:10px 0;font-size:13px;color:var(--mut)}}
.blk b{{color:var(--ink)}}
/* faq */
.faq{{background:var(--surf);border:1px solid var(--line);border-radius:10px;padding:0 16px;margin-bottom:10px}}
.faq summary{{padding:15px 0;font-weight:600;cursor:pointer;list-style:none}}
.faq summary::-webkit-details-marker{{display:none}}
.faq summary::before{{content:"+ ";color:var(--acc);font-weight:800}}
.faq[open] summary::before{{content:"− "}}
.faq p{{margin:0 0 15px;color:var(--mut);font-size:14px}}
footer{{border-top:1px solid var(--line);padding:36px 0;color:var(--mut);font-size:13px}}
footer b{{color:var(--ink)}}
.disc{{font-size:12px;color:var(--mut);margin-top:10px}}
@media(max-width:640px){{.metrics{{gap:20px}}.metric b{{font-size:30px}}}}
</style>
</head>
<body>
<header><div class="nav">
  <span class="brand">ETIA<b>·</b>特种标签</span>
  <a href="#products">产品选型</a><a href="#why">技术</a><a href="#apps">应用</a><a href="#faq">常见问题</a>
  <a class="cta-top" href="#products">开始选型</a>
</div></header>

<div class="hero"><div class="wrap">
  <div class="eyebrow">工业特种标签 · 20年选型经验</div>
  <h1>{esc(v['h1'])}</h1>
  <p class="tag">{esc(v['tagline'])}</p>
  <div class="metrics">
    <div class="metric"><b>{n}</b><span>款在库产品</span></div>
    <div class="metric"><b>{nb}</b><span>大原厂品牌</span></div>
    <div class="metric"><b>{tmin}~{tmax}℃</b><span>覆盖温区</span></div>
    <div class="metric"><b>{tds_n}</b><span>份官方TDS直连</span></div>
  </div>
  <a class="hero-cta" href="#products">按工况筛选产品 →</a>
</div></div>

<div class="trustbar"><div class="wrap">
  <span>✔ 跨 <b>{nb}</b> 大原厂品牌横向对比,非单一代理</span>
  <span>✔ 每款参数<b>直连官方TDS</b>可核验</span>
  <span>✔ 官网未公布参数<b>一律留空,不臆造</b></span>
</div></div>

{"<section id='why'><div class='wrap'><div class='eyebrow2'>技术专业 EXPERTISE</div><h2>"+esc(v['why_title'])+"</h2><div class='why-grid'>"+why_html+"</div></div></section>" if why_html else ""}

<section id="products"><div class="wrap">
  <div class="eyebrow2">一站选型 AUTHORITATIVE</div>
  <h2>按应用场景筛选 · {n} 款跨品牌产品</h2>
  <div class="brand-strip">{brand_row}</div>
  <div class="filters" id="filters"><button class="fchip on" data-sub="">全部 <b>{n}</b></button>{app_chips}</div>
  <div class="grid" id="grid"></div>
</div></section>

{"<section id='apps'><div class='wrap'><div class='eyebrow2'>应用覆盖</div><h2>典型应用场景</h2><div class='why-grid'>"+"".join(f"<div class='why-card'><h3>{esc(s)}</h3><p>{c} 款适用产品 · 点上方筛选查看</p></div>" for s,c in sorted(apps.items(),key=lambda x:-x[1])[:6])+"</div></div></section>" if apps else ""}

{"<section id='faq'><div class='wrap'><div class='eyebrow2'>常见问题 FAQ</div><h2>选型答疑</h2>"+faq_html+"</div></section>" if faq_html else ""}

<footer><div class="wrap">
  <b>ETIA 特种标签</b> · 深耕工业特种标签20年 · 代理 3M / Brady / LINTEC / Avery Dennison / Polyonics / Computype / FLEXcon 等全球品牌<br>
  一站式选型 · TDS资料归档 · 应用方案 · 客户定制Catalog
  <div class="disc">本站产品参数均来自各品牌官方产品页 / 技术数据表(TDS) / 官方选型器,可点击每款产品核验来源。官网未公布的参数一律留空,不做臆造。本站为选型参考,最终以官方TDS为准。</div>
</div></footer>

<div id="dm" onclick="closeDw()"></div><div id="dw"></div>
<script id="d" type="application/json">{data_json}</script>
<script>
const P=JSON.parse(document.getElementById('d').textContent);
function esc(s){{return String(s==null?'':s).replace(/[&<>"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]))}}
let sub='';
function render(){{
  const list=P.filter(p=>!sub||p.sub===sub);
  document.getElementById('grid').innerHTML=list.map((p,i)=>`
    <div class="card" data-i="${{i}}">
      <div class="sw"><span class="bc">${{esc(p.bcn||p.bc)}}</span><div class="chip-mock">${{esc(p.m)}}</div></div>
      <div class="info"><div class="nm">${{esc(p.nc||p.ne||p.m)}}</div>
        <div class="tags">
          ${{p.ac?`<span class="tg">${{esc(p.ac)}}</span>`:''}}
          ${{p.t1!=null?`<span class="tg hot">耐温${{p.t1}}℃</span>`:''}}
          ${{p.chem&&p.chem!=='D'?`<span class="tg">耐化学${{p.chem}}</span>`:''}}
          ${{p.sub?`<span class="tg">${{esc(p.sub)}}</span>`:''}}
        </div>
        <div class="ft">${{p.tds?'✓ 官方TDS · ':''}}查看详情 →</div>
      </div></div>`).join('');
  window._list=list;
}}
document.getElementById('filters').onclick=e=>{{const b=e.target.closest('.fchip');if(!b)return;
  document.querySelectorAll('.fchip').forEach(c=>c.classList.remove('on'));b.classList.add('on');
  sub=b.dataset.sub;render();}};
document.getElementById('grid').onclick=e=>{{const c=e.target.closest('.card');if(c)openDw(window._list[+c.dataset.i]);}};
function openDw(p){{
  document.getElementById('dw').innerHTML=`
   <div class="sub" style="float:right;cursor:pointer" onclick="closeDw()">✕ 关闭</div>
   <h3>${{esc(p.bcn||p.bc)}} ${{esc(p.m)}}</h3>
   <p class="sub">${{esc(p.nc||'')}}<br>${{esc(p.ne||'')}}</p>
   <table class="spec">
     <tr><th>面材</th><td>${{esc(p.fc||'聚酰亚胺')}}</td></tr>
     <tr><th>胶水</th><td>${{esc(p.ac||'—')}}</td></tr>
     <tr><th>长期耐温</th><td>${{p.t0!=null?p.t0+' ~ ':''}}${{p.t1!=null?p.t1+' ℃':'—'}}${{p.tp!=null?' (峰值'+p.tp+'℃)':''}}</td></tr>
     <tr><th>厚度/颜色</th><td>${{p.th!=null?p.th+' μm':'—'}} / ${{esc(p.c||'—')}}</td></tr>
     <tr><th>耐化学</th><td>${{esc(p.chem||'—')}}</td></tr>
     <tr><th>认证</th><td>${{esc(p.cert||'—')}}</td></tr>
     <tr><th>应用</th><td>${{esc(p.sub||'—')}}</td></tr>
   </table>
   ${{p.ds?`<div class="blk"><b>产品介绍</b><br>${{esc(p.ds)}}</div>`:''}}
   ${{p.bn?`<div class="blk"><b>优势</b><br>${{esc(p.bn)}}</div>`:''}}
   <div style="margin-top:14px">
     ${{p.tds?`<a class="dw-cta" href="${{esc(p.tds)}}" target="_blank" rel="noopener">⬇ 官方TDS</a>`:''}}
     ${{p.src&&p.src!==p.tds?`<a class="dw-cta sec" href="${{esc(p.src)}}" target="_blank" rel="noopener">品牌源页 ↗</a>`:''}}
   </div>
   <div class="disc" style="margin-top:14px">数据来源可核验;官网未公布字段留空不臆造。</div>`;
  document.getElementById('dw').classList.add('on');document.getElementById('dm').classList.add('on');
}}
window.closeDw=()=>{{document.getElementById('dw').classList.remove('on');document.getElementById('dm').classList.remove('on')}};
addEventListener('keydown',e=>{{if(e.key==='Escape')closeDw()}});
render();
</script>
</body>
</html>
"""


def main():
    vkey = sys.argv[1] if len(sys.argv) > 1 else "polyimide"
    if vkey not in VERTICALS:
        print("可用垂直站:", ", ".join(VERTICALS))
        sys.exit(1)
    outp = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / f"data/microsite-{vkey}.html"
    outp.write_text(render(vkey), encoding="utf-8")
    print(f"{outp}: {VERTICALS[vkey]['h1']} 生成完成 ({round(len(outp.read_text())/1024)} KB)")


if __name__ == "__main__":
    main()
