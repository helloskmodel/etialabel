#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""METALS / STEEL sector — mirrors the Electronics/PCB methodology.
Level 1: /industries/steel/ (Application Landing — process tab module + product lines).
Level 2: /industries/steel/hot-billet-direct-labeling/ (Product-Line Landing — HP-700T).
Runs AFTER gen_ind_landing so it owns /industries/steel/. EN + ZH.
VI/TH copy saved in _docs/sources/steel/ for a future 4-language rollout."""
import gen_heatproof as hp
from gen_heatproof import esc, L, page, write, LANGS

STEEL_BANNER = "https://eitalabel-1303055923.cos.ap-singapore.myqcloud.com/A%E3%83%BBHERO%20banner%206%20%E7%BB%84/HP9001609.jpg"
def _t(lang, en, zh): return zh if lang == "zh" else en

def _svg(p): return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
                     'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">%s</svg>' % p)
IC_WHERE = _svg('<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>')
IC_CHAL  = _svg('<path d="M12 3 2 20h20L12 3z"/><path d="M12 10v5M12 18h.01"/>')
IC_HOW   = _svg('<path d="M3 12h4l2-7 4 14 2-7h6"/>')
IC_SOLVE = _svg('<path d="M12 3 4 6.5v5c0 4.6 3.2 7.7 8 9.5 4.8-1.8 8-4.9 8-9.5v-5L12 3z"/><path d="m9 12 2 2 4-4"/>')
CHK = _svg('<path d="m5 12 4 4L19 7"/>')
DOC = _svg('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/>')

STEEL_CSS = """<style>
.sthero{background:linear-gradient(115deg,rgba(10,30,80,.90),rgba(20,60,150,.50) 55%,rgba(26,86,219,.10)),url('__BANNER__') center/cover no-repeat #0e2a63;color:#fff}
.sthero .wrap{padding:56px 24px}.sthero .eyebrow{color:#9dbcff}
.sthero h1{color:#fff;font-size:38px;font-weight:800;line-height:1.14;margin:6px 0 12px;max-width:20em}
.sthero p{color:#eef3ff;font-size:16px;line-height:1.6;max-width:56em}
.stbadge{display:inline-block;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.3);color:#fff;font-weight:700;font-size:12.5px;border-radius:20px;padding:5px 13px;margin:0 7px 8px 0}
.plsub{color:var(--mut);font-size:15px;margin:-6px 0 16px;max-width:66em}
.ovbody{max-width:66em}.ovbody p{font-size:16px;line-height:1.75;color:var(--ink);margin-bottom:16px}
.ovbody p.ovlead{font-size:19px;font-weight:700;color:var(--blue-deep);line-height:1.55}
.failul{list-style:none;padding:0;margin:8px 0 0;display:grid;grid-template-columns:1fr 1fr;gap:0 40px}
.failul li{padding:12px 0 12px 26px;position:relative;font-size:15px;color:var(--ink);line-height:1.55;border-bottom:1px solid var(--line)}
.failul li:before{content:"\\2717";position:absolute;left:2px;top:12px;color:#c2621f;font-weight:800}
.stmod{margin-top:8px}
.sttabsrow{display:flex;align-items:center;gap:6px;border-bottom:1px solid var(--line)}
.sttabs{display:flex;gap:24px;overflow-x:auto;scrollbar-width:none;flex:1}.sttabs::-webkit-scrollbar{display:none}
.sttab{white-space:nowrap;background:none;border:none;padding:12px 0;font-size:15px;font-weight:700;color:var(--mut);cursor:pointer;border-bottom:3px solid transparent;margin-bottom:-1px}
.sttab.on{color:var(--blue-deep);border-bottom-color:var(--blue)}
.starrow{background:none;border:none;font-size:20px;color:var(--mut);cursor:pointer;padding:4px 6px}
.stpanel{padding-top:24px}
.st4{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.stbox{border:1px solid var(--line);border-radius:12px;padding:18px 20px;background:#fff}
.stbox .h{display:flex;align-items:center;gap:12px;margin-bottom:8px}
.stbox .h .i{width:30px;height:30px;flex:0 0 auto}.stbox .h .i svg{width:30px;height:30px}
.stbox .h .e{font-size:12px;font-weight:800;letter-spacing:.04em;text-transform:uppercase}
.stbox p{font-size:14.5px;color:var(--ink);line-height:1.55}
.sttbl{width:100%;border-collapse:collapse;font-size:14.5px}
.sttbl th{text-align:left;background:#f4f7fd;color:var(--blue-deep);font-weight:800;font-size:12px;letter-spacing:.03em;text-transform:uppercase;padding:11px 12px;border-bottom:2px solid var(--line)}
.sttbl td{padding:11px 12px;border-bottom:1px solid var(--line);color:var(--ink);vertical-align:top}
.sttbl td.k{font-weight:800;color:var(--blue-deep);white-space:nowrap}
.stgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px}
.stcard{display:block;border:1px solid var(--line);border-radius:12px;padding:18px 18px 16px;background:#fff;text-decoration:none;transition:.16s}
.stcard:hover{border-color:var(--blue);box-shadow:0 12px 30px rgba(20,40,90,.12);transform:translateY(-3px)}
.stcard .t{font-weight:800;color:var(--blue-deep);font-size:16px}
.stcard .m{font-size:12.5px;font-weight:800;color:var(--green-d);margin:4px 0}
.stcard .go{font-size:12.5px;font-weight:700;color:var(--blue);margin-top:8px}
.flist{display:grid;grid-template-columns:1fr 1fr;gap:2px 44px}
.frow{display:flex;gap:14px;align-items:flex-start;padding:15px 0;border-bottom:1px solid var(--line)}
.frow .c{flex:0 0 auto;width:22px;height:22px;color:var(--green-d)}.frow .c svg{width:22px;height:22px}
.frow .tx h4{font-size:15.5px;color:var(--blue-deep);margin-bottom:3px}.frow .tx p{font-size:14px;color:var(--ink);line-height:1.5}
.sysflow{background:#0e2a63;color:#eaf1ff;border-radius:14px;padding:26px 24px;font-size:15px;line-height:2;max-width:640px}
.sysflow b{color:#fff}.sysflow .ar{color:#8fb4ff;display:block;margin:2px 0}
.doclist{display:flex;flex-direction:column;gap:9px;max-width:820px}
.docr{display:flex;align-items:center;gap:13px;padding:12px 16px;border:1px solid var(--line);border-radius:10px;background:#fff;text-decoration:none;transition:.15s}
.docr:hover{border-color:var(--blue);background:#f8faff}
.docr .i{flex:0 0 auto;width:22px;height:22px;color:var(--blue)}.docr .i svg{width:22px;height:22px}
.docr .n{flex:1;font-size:14.5px;font-weight:700;color:var(--ink)}
.docr .g{font-size:11px;font-weight:800;color:var(--mut);border:1px solid var(--line);border-radius:6px;padding:2px 7px}
.faq details{border-bottom:1px solid var(--line);padding:14px 0}
.faq summary{font-weight:700;color:var(--blue-deep);font-size:15.5px;cursor:pointer;list-style:none}
.faq summary::-webkit-details-marker{display:none}
.faq summary:before{content:"+";color:var(--blue);font-weight:800;margin-right:10px}
.faq details[open] summary:before{content:"\\2013"}
.faq p{font-size:14.5px;color:var(--ink);line-height:1.6;margin-top:8px;padding-left:22px}
@media(max-width:820px){.st4,.failul,.flist{grid-template-columns:1fr}}
</style>""".replace("__BANNER__", STEEL_BANNER)

# ------------------------------------------------- Level 1: Application Landing
# 4 application types (tab): (name, Where, Challenge, How, Solves)
APP_TYPES = [
 (("Direct Hot Application", "热态直贴"),
  ("Slabs and billets straight out of continuous casting; coils after hot rolling.",
   "连铸出坯后的板坯、钢坯,热轧后的钢卷。"),
  ("Surface temperature at application is 550–750℃; the surface is rough and scale-covered. The label must bond instantly and must not burn.",
   "贴附瞬间对象表面 550–750℃,表面粗糙、覆盖氧化皮,标签必须瞬间贴牢且不燃烧。"),
  ("A robotic labeling system applies the label automatically at the roller table — personnel never touch the heat source.",
   "由机器人贴标系统在辊道旁自动贴附,人员完全不接触热源。"),
  ("Hot material has a unique identity from the moment it is produced — no more “remember the position” or “estimate the heat number.”",
   "热态物料从产出那一刻起就有唯一身份,不再靠“记位置”“估炉次”。")),
 (("Through-Process Labels", "过程标签"),
  ("Pickling and annealing of wire and bar; hot forging and long-cycle annealing of forged parts.",
   "线材 / 棒材的酸洗与退火、锻件的热锻与长时间退火。"),
  ("The label must first be immersed in acid (H₂SO₄ / HCl), then baked in a furnace for 10–18 hours — chemical attack and long-duration heat stacked together.",
   "标签要先泡酸(H₂SO₄ / HCl)、再进炉烧 10~18 小时,化学腐蚀与长时间高温叠加。"),
  ("Applied at ambient temperature; the label travels with the workpiece through the entire heat-treatment chain and is still scannable at furnace exit.",
   "常温下贴附,标签随工件走完整个热处理链,出炉后仍可扫码。"),
  ("Heat treatment is where batches are most often lost. If the label survives, traceability is unbroken.",
   "热处理是最容易丢批次的环节,标签活下来 = 追溯不断链。")),
 (("Heat Treatment Tags", "热处理挂牌"),
  ("Reusable jigs, fixtures, baskets and molds that cycle repeatedly.",
   "反复循环使用的工装、夹具、料筐、模具。"),
  ("Not single-use — must stay readable through dozens to hundreds of thermal cycles.",
   "不是一次性使用,而是要承受几十上百次热循环仍可读。"),
  ("Mechanically fixed (wired / riveted) to the asset for the long term.",
   "机械固定(绑扎 / 铆接)在资产上,长期跟随。"),
  ("Tooling asset management, cycle counting and end-of-life alerts.",
   "工装资产管理、使用次数统计、寿命预警。")),
 (("On-Site Printing & Integration", "现场打印与集成"),
  ("Runs through all of the above scenarios.",
   "贯穿以上所有场景。"),
  ("Heat / batch numbers must be produced and applied in real time and fed back downstream.",
   "炉次 / 批号需实时生成、贴附并向下游回传。"),
  ("Thermal transfer printer + high-temperature ribbon; MES pushes the heat / batch number, printed and applied immediately; scanning stations feed data back.",
   "热转印打印机 + 高温色带,MES 实时下发炉次 / 批号,打印后即时贴附;扫码站回传数据。"),
  ("The barcode becomes the live data entry point that binds physical material to MES.",
   "条码成为实时数据入口,将物理物料与 MES 绑定。")),
]
# process map: (process, state, survive, type)
PROC_MAP = [
 (("Continuous casting → slab / billet","连铸 → 板坯 / 钢坯"),("750℃ red-hot, scale","750℃ 赤热、氧化皮"),("Ultra-high-temp direct","超高温直贴"),("Direct hot","热态直贴")),
 (("Hot rolling → coil","热轧 → 钢卷"),("550℃","550℃"),("High-temp, curved surface","高温直贴、卷曲面"),("Direct hot","热态直贴")),
 (("Pickling","酸洗"),("Ambient, strong acid","常温,强酸浸泡"),("Chemical attack","化学腐蚀"),("Through-process","过程标签")),
 (("Annealing","退火"),("800℃ × 10h","800℃ × 10h"),("Prolonged heat","长时高温"),("Through-process","过程标签")),
 (("Forging + heat treatment","锻造 + 热处理"),("800℃ → 1100℃ × 18h","800℃ → 1100℃ × 18h"),("Extreme heat + duration","极端温度 + 超长时间"),("Through-process","过程标签")),
 (("Jigs / baskets","工装 / 料筐"),("Repeated furnace entry","反复进炉"),("Many thermal cycles","多次热循环"),("Tags","挂牌")),
 (("Finished goods → warehouse","成品入库"),("Ambient","常温"),("Machine-readable","需机读"),("Scan & feedback","扫码回传")),
]
# choose-by-process cards: (title, metric, url)
CHOOSE = [
 (("Hot billet direct application","热态钢坯 Billet 直贴"),"750℃","/industries/steel/hot-billet-direct-labeling/"),
 (("Hot slab direct application","热态板坯 Slab 直贴"),"750℃","/contact/"),
 (("Hot coil direct application","热态钢卷 Coil 直贴"),"550℃","/contact/"),
 (("Wire rod pickling + annealing","线材酸洗 + 退火追溯"),"800℃ × 10h","/contact/"),
 (("Forged part heat treatment","锻件热处理追溯"),"1100℃ × 18h","/contact/"),
]
BENEFITS_L1 = [
 ("Manual tagging time in the hot zone approaches zero; safety risk eliminated","高温区人工挂牌作业时间趋近于 0,消除安全风险"),
 ("Barcodes readable across the full chain; batch mix-ups and wrong material drop significantly","全流程条码可读,混批 / 错料显著下降"),
 ("Scanning replaces visual verification at warehouse-in; identification throughput rises","扫码入库替代目视核对,识别效率提升"),
 ("Quality claims can be traced back to a specific heat number","质量异议可回溯至具体炉次"),
 ("No inkjet equipment maintenance, no paint consumables","免去喷码设备维护与油漆耗材"),
]
FAIL_L1 = [
 ("Paper / PET labels — carbonize above 200℃","纸 / PET 标签 —— 200℃ 以上直接碳化"),
 ("Inkjet / paint — sits on the scale; flakes off with it, burns away in the furnace","喷码 / 油漆 —— 附着在氧化皮上,随之脱落,进炉后烧尽"),
 ("Manual tagging — personnel must approach a 700℃ heat source; slow and unsafe","人工挂牌 —— 需靠近 700℃ 热源,效率低且不安全"),
 ("Stamping / punch — not machine-readable, no real-time MES link","钢印 / 打点 —— 无法机读,无法实时对接 MES"),
]
FAQ_L1 = [
 ("Will it really stick to scale?","真的能贴在氧化皮上吗?"),
 ("Is the label still there after pickling?","酸洗后标签还在吗?"),
 ("Can it integrate with our MES?","能对接我们的 MES 吗?"),
 ("Is there a minimum order quantity?","有最小订量吗?"),
]

def build_steel_landing(lang):
    zh = (lang == "zh")
    def H(e, z): return esc(_t(lang, e, z))
    contact = L(lang, "/contact/")
    # hero
    hero = ('<section class="sthero"><div class="wrap"><div class="eyebrow">%s</div>'
            '<h1>%s</h1><p>%s</p><div style="margin-top:20px"><a class="btn pri" href="%s">%s</a></div>'
            '</div></section>') % (
        H("HEATPROOF™ · Extreme Temperature Identification Solutions", "HEATPROOF™ · 极端温度标识解决方案"),
        H("One Label. One Journey. Complete Traceability Through Extreme Heat.",
          "一张标签,一段旅程,穿越极端高温的完整可追溯。"),
        H("Extreme Heat-Resistant Labels and Tags", "极端耐高温标签与挂牌"),
        contact, H("Talk to a Specialist", "咨询专家"))
    # HEATPROOF overview
    ov_ps = [
      ("In extreme manufacturing environments, product identity is often lost when conventional identification methods fail.",
       "在极端制造环境中,当传统标识方式失效时,产品身份往往随之丢失。"),
      ("HEATPROOF™ introduces a new generation of thermal traceability solutions — enabling direct hot application labels, heat treatment labels and durable tags that maintain product identification through extreme temperatures, chemical exposure and demanding thermal processes.",
       "HEATPROOF™ 带来新一代热追溯解决方案 —— 提供热态直贴标签、热处理标签与耐用挂牌,让产品标识在极端温度、化学暴露与严苛热处理工艺中始终保持。"),
      ("From steel and aluminum processing to ceramics and advanced manufacturing, HEATPROOF™ helps manufacturers create, maintain and verify one continuous product identity from production to final delivery.",
       "从钢铁、铝加工到陶瓷与先进制造,HEATPROOF™ 帮助制造商从生产到最终交付,创建、保持并验证一致连续的产品身份。"),
    ]
    overview = ('<section class="blk"><div class="wrap"><div class="ovbody">%s</div></div></section>') % (
        "".join('<p%s>%s</p>' % ((' class="ovlead"' if i == 0 else ''), H(e, z)) for i, (e, z) in enumerate(ov_ps)))
    # why + fail
    fails = "".join('<li>%s</li>' % H(e, z) for e, z in FAIL_L1)
    why = ('<section class="blk"><div class="wrap"><h2>%s</h2>'
           '<p class="plsub">%s</p><ul class="failul">%s</ul></div></section>') % (
        H("Why the Steel Industry Needs Heat-Resistant Labels", "钢铁行业为什么需要耐高温标签"),
        H("At the moment material needs to be identified, it is often still red-hot, covered in scale, and about to enter an even harsher process. Conventional labels all fail here:",
          "物料在被识别的那一刻,往往还是红热的、带氧化皮的、即将进入更严苛工序的。普通标签在这里全部失效:"),
        fails)
    # application-type tab module
    tabs = ""; panels = ""
    for i, (nm, wh, ch, hw, sv) in enumerate(APP_TYPES):
        tabs += '<button class="sttab%s" onclick="stTab(this,%d)">%s</button>' % (" on" if i == 0 else "", i, H(*nm))
        def box(ic, lbl, col, val):
            return ('<div class="stbox"><div class="h"><span class="i" style="color:%s">%s</span>'
                    '<span class="e" style="color:%s">%s</span></div><p>%s</p></div>') % (col, ic, col, lbl, H(*val))
        panels += ('<div class="stpanel" data-i="%d" style="display:%s"><div class="st4">%s%s%s%s</div></div>') % (
            i, "block" if i == 0 else "none",
            box(IC_WHERE, H("Where", "用在哪"), "var(--blue)", wh),
            box(IC_CHAL, H("Challenge", "核心挑战"), "#c2621f", ch),
            box(IC_HOW, H("How it works", "怎么用"), "var(--blue)", hw),
            box(IC_SOLVE, H("What it solves", "解决什么"), "var(--green-d)", sv))
    st_js = ("<script>function stTab(b,i){var m=b.closest('.stmod');"
             "m.querySelectorAll('.sttab').forEach(function(x,j){x.classList.toggle('on',j===i);});"
             "m.querySelectorAll('.stpanel').forEach(function(p){p.style.display=(+p.getAttribute('data-i')===i)?'block':'none';});}"
             "function stScroll(b,d){b.closest('.sttabsrow').querySelector('.sttabs').scrollBy({left:d*240,behavior:'smooth'});}</script>")
    types = ('<section class="blk" style="background:#f4f7fd"><div class="wrap"><h2>%s</h2><div class="stmod">'
             '<div class="sttabsrow"><button class="starrow" onclick="stScroll(this,-1)">&lsaquo;</button>'
             '<div class="sttabs">%s</div><button class="starrow" onclick="stScroll(this,1)">&rsaquo;</button></div>'
             '%s</div></div></section>%s') % (
        H("Types of Label Application in the Steel Industry", "钢铁行业的标签应用类型"), tabs, panels, st_js)
    # process map table
    mrows = "".join('<tr><td class="k">%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
        H(*a), H(*b), H(*c), H(*d)) for a, b, c, d in PROC_MAP)
    mheads = "".join('<th>%s</th>' % H(*h) for h in [("Process","工序"),("Material state","对象状态"),("What the label must survive","标签面临的考验"),("Application type","应用类型")])
    pmap = ('<section class="blk"><div class="wrap"><h2>%s</h2>'
            '<div class="ptable-wrap" style="overflow-x:auto"><table class="sttbl"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
            '</div></section>') % (H("Label Application Map Across the Steel Process Chain", "钢铁全流程标签应用地图"), mheads, mrows)
    # choose by process cards
    ccards = "".join('<a class="stcard" href="%s"><div class="t">%s</div><div class="m">%s</div><div class="go">%s</div></a>' % (
        L(lang, u), H(*t), esc(m), H("View solution →", "查看方案 →")) for t, m, u in CHOOSE)
    choose = ('<section class="blk" style="background:#f4f7fd"><div class="wrap"><h2>%s</h2>'
              '<div class="stgrid">%s</div></div></section>') % (
        H("Choose Your Application by Process", "按工序选择你的应用场景"), ccards)
    # benefits
    brows = "".join('<div class="frow"><div class="c">%s</div><div class="tx"><p>%s</p></div></div>' % (CHK, H(e, z)) for e, z in BENEFITS_L1)
    ben = ('<section class="blk"><div class="wrap"><h2>%s</h2><div class="flist">%s</div></div></section>') % (
        H("Industry-Level Benefits", "行业收益概览"), brows)
    # faq
    faqs = "".join('<details><summary>%s</summary></details>' % H(*q) for q in FAQ_L1)
    faq = ('<section class="blk" style="background:#f4f7fd"><div class="wrap"><h2>%s</h2><div class="faq">%s</div></div></section>') % (
        H("FAQ", "常见问题"), faqs)
    body = STEEL_CSS + overview + why + types + pmap + choose + ben + faq + ('<div class="wrap">%s</div>' % hp.cta2(lang, "applications"))
    path = "/industries/steel/"
    crumb = [("Home" if not zh else "首页", "/"), ("Industries" if not zh else "行业", "/industries/"),
             ("Steel Industry" if not zh else "钢铁行业", path)]
    write(lang, path, page(lang, path,
        _t(lang, "Heat-Resistant Label Applications for the Steel Industry | ETIA",
                 "钢铁行业耐高温标签应用 | ETIA"),
        _t(lang, "Heat-resistant barcode labels for the steel industry — 750℃ direct hot application, pickling and 800℃ annealing traceability, from continuous casting to warehouse.",
                 "面向钢铁行业的耐高温条码标签 —— 750℃ 热态直贴、酸洗与 800℃ 退火追溯,从连铸到入库全流程。"),
        _t(lang, "Heat-Resistant Label Applications in the Steel Industry", "钢铁行业耐高温标签应用"), "",
        body, crumb, active="", hero=hero))
    if lang == "en": hp.track(path, "industries")

# ------------------------------------------------- Level 2: HP-700T product line
HP_BADGES = [("750℃ Direct","750℃ 直贴"),("Robot-Ready","机器人自动化"),("Works on Scale","氧化皮适应"),("Scannable While Hot","热态可扫")]
HP_FEATURES = [
 (("750℃ direct application","750℃ 直贴耐受"),("Application surface up to 750℃ — the label does not burn, curl or fall off.","贴附面温度可达 750℃,标签不燃烧、不卷边、不脱落。")),
 (("Instant high-temperature adhesive","高温瞬时粘接胶"),("Softens and bonds on contact, anchoring into the pores of the scale as it cools — not a conventional pressure-sensitive mechanism.","接触即软化贴合,冷却后锚固于氧化皮孔隙,非常规压敏胶原理。")),
 (("Scale-surface adaptability","氧化皮表面适应性"),("Engineered for rough, uneven billet surfaces with loose scale.","针对粗糙、不平整、带浮皮的钢坯表面设计。")),
 (("High-contrast imaging when hot","热态高对比成像"),("The barcode retains contrast even against the billet's own glow, supporting hot-state scanning.","钢坯自发光条件下条码仍保持反差,支持热态扫描。")),
 (("Thermal shock resistance","抗热冲击"),("Withstands rapid cooling on the bed or localized water spray without cracking or peeling.","承受冷床自然冷却 / 局部喷水的骤冷,不龟裂剥落。")),
 (("Robot-compatible","机器人贴标兼容"),("Roll-fed supply for continuous feeding on automatic labelers without jamming.","卷装供料,可配自动贴标机连续送标,不卡带。")),
 (("On-site thermal transfer printing","现场热转印打印"),("Supports print-and-apply with heat numbers pushed live from MES.","支持 MES 实时下发炉次号即打即贴。")),
 (("Resists scale flake-off","抗氧化皮脱落"),("Deep anchoring means loose scale doesn't take the label with it.","贴附深度渗入,浮皮脱落不带走标签。")),
]
HP_BENEFITS = [
 (("Removes manual work from the hot zone","消除热区人工作业"),("Operators no longer approach 750℃ billets to tag them; hot-zone manual work approaches zero.","操作工不再靠近 750℃ 钢坯挂牌,高温区人工作业趋近于 0。")),
 (("Identity from the moment of production","钢坯自产出即有身份"),("A unique barcode right after the cut — batch attribution survives even a scrambled stack.","切断后立即获得唯一条码,堆垛乱序也不丢批次。")),
 (("Identity confirmed before furnace entry","入炉前身份确认"),("Scanning replaces manual checking; a single billet is identified in seconds.","扫码替代人工核对,单坯识别数秒完成。")),
 (("Heat number traceability","炉次可回溯"),("Quality claims on finished goods trace straight back to the specific caster heat and billet number.","成品质量异议可直接回溯至具体连铸炉次与坯号。")),
 (("Fewer mix-ups and misrouting","减少混批与错送"),("Charging errors and wrong-mill deliveries drop significantly.","装炉错误、错送轧线的情况显著减少。")),
 (("No maintenance burden","免维护成本"),("No inkjet equipment cleaning, no paint consumables.","无喷码设备清洗维护、无油漆耗材。")),
 (("Seamless MES integration","MES 无缝对接"),("The barcode is the data entry point; manual ledger entry is eliminated.","条码即数据入口,取消手工台账录入。")),
]
HP_SPECS = [
 (("Model","型号"),("HP-700T","HP-700T")),
 (("Product category","产品类别"),("Direct Hot Application label","热态直贴标签(Direct Hot Application)")),
 (("Max. application temperature","最高贴附温度"),("<strong>750℃</strong>","<strong>750℃</strong>")),
 (("Applicable objects","适用对象"),("Steel billet / steel slab","钢坯 Billet / 板坯 Slab")),
 (("Applicable surface","适用表面"),("Rough, scale-covered hot steel surfaces","氧化皮覆盖的粗糙热态钢表面")),
 (("Base material","基材"),("Heat-resistant metal substrate","耐高温金属基材")),
 (("Adhesive","胶黏剂"),("High-temperature anchoring adhesive","高温专用锚固型胶")),
 (("Printing method","印刷方式"),("Thermal transfer (dedicated high-temp ribbon) / pre-print","热转印(专用高温色带)/ 预印")),
 (("Supply form","供货形式"),("Roll (for automatic labelers) / sheet","卷装(适配自动贴标机)/ 单张")),
 (("Application method","贴附方式"),("Robotic labeling / manual tagging pole","机器人自动贴标 / 手动贴标杆")),
 (("Storage","保存条件"),("Ambient, away from light; use within 12 months","常温避光,建议 12 个月内使用")),
]
HP_DOCS = [
 (("HP-700T technical spec sheet","HP-700T 技术规格书"),("Direct download","直接下载")),
 (("Safety Data Sheet (SDS)","安全数据表 SDS"),("Direct download","直接下载")),
 (("RoHS / REACH compliance declaration","RoHS / REACH 合规声明"),("Direct download","直接下载")),
 (("750℃ heat resistance test report","750℃ 耐温测试报告"),("Gated","留资下载")),
 (("Hot billet direct application case study","钢坯直贴案例研究"),("Gated","留资下载")),
 (("Steel industry selection guide","钢铁行业选型手册"),("Gated","留资下载")),
 (("Application work instruction","贴附作业指导书"),("Gated","留资下载")),
]
HP_FAQ = [
 ("Scale keeps flaking off — will the label come off with it?","氧化皮持续脱落,标签会一起掉吗?"),
 ("Is 750℃ the billet temperature or the label's temperature limit?","750℃ 是钢坯温度还是标签耐温上限?"),
 ("The billet glows — can the barcode still be scanned while hot?","钢坯自发光,条码在热态下能扫到吗?"),
 ("Does the label survive the reheating furnace (1200℃)?","后续入加热炉(1200℃)标签还在吗?"),
 ("Can our existing robot be converted into a labeling station?","已有机器人能改造成贴标工位吗?"),
 ("Minimum order quantity and lead time?","最小订量与交期?"),
]

def build_hp700t(lang):
    zh = (lang == "zh")
    def H(e, z): return esc(_t(lang, e, z))
    def R(e, z): return _t(lang, e, z)  # raw (pre-formatted HTML)
    contact = L(lang, "/contact/")
    badges = "".join('<span class="stbadge">%s</span>' % H(*b) for b in HP_BADGES)
    hero = ('<section class="sthero"><div class="wrap"><div class="eyebrow">%s</div>'
            '<h1>%s</h1><p>%s</p><div style="margin:12px 0 0">%s</div>'
            '<div style="margin-top:18px"><a class="btn pri" href="%s">%s</a> '
            '<a class="btn on-dark" href="%s">%s</a></div></div></section>') % (
        H("STEEL · DIRECT HOT APPLICATION", "钢铁 · 热态直贴"),
        H("HP-700T — 750℃ Direct Application Label for Hot Steel Billets", "HP-700T — 750℃ 热态钢坯直贴标签"),
        H("Applied directly to a 750℃ billet surface — anchors into the scale, stays scannable through cooling, transport and stacking.",
          "直接贴附于 750℃ 钢坯表面 —— 锚固氧化皮,在降温、转运、堆垛全程保持可扫。"),
        badges, L(lang, "/contact/?product=HP-700T&type=sample"), H("FREE SAMPLE", "免费样品"),
        contact, H("Talk to a Specialist", "咨询专家"))
    # application
    app = ('<section class="blk"><div class="wrap"><h2>%s</h2>'
           '<p class="plsub">%s</p>'
           '<p style="max-width:64em;font-size:15px;line-height:1.75;color:var(--ink);margin-bottom:14px"><strong>%s</strong> %s</p>'
           '<p style="max-width:64em;font-size:15px;line-height:1.75;color:var(--ink)"><strong>%s</strong> %s</p>'
           '</div></section>') % (
        H("The Specific Application", "具体应用"),
        H("Billets cut from the continuous caster, with end-face temperatures around 750℃, covered in scale that keeps flaking off. They wait on the cooling bed, are transported, stacked, and eventually go into the reheating furnace or straight to the mill.",
          "连铸机切断后的钢坯,端面温度约 750℃,表面覆盖氧化皮并持续脱落。钢坯在冷床等待、转运、堆垛,最终进入加热炉或直送轧机。"),
        H("The pain:", "痛点:"),
        H("Between the caster cut and stacking, the billet has no physical identity. Inkjet cannot form a legible mark on 750℃ scale; manual tagging requires an operator to carry a pole up to a hot billet.",
          "连铸切断到堆垛之间,钢坯没有物理身份。喷码在 750℃ 氧化皮上无法成型;人工挂牌需操作工携带挂牌杆靠近热坯。"),
        H("How HP-700T works:", "HP-700T 的做法:"),
        H("A robotic station downstream of the cutting machine: MES pushes the heat number → thermal transfer printer prints on the spot → the robot applies the label to the billet end face. The adhesive softens on contact and penetrates the scale pores, anchoring as it cools. The barcode stays scannable through cooling, crane transport and stacking; a scanning station confirms identity before furnace entry and feeds it back to MES.",
          "在切断机后方设置机器人贴标工位:MES 下发炉次号 → 热转印打印机现场打印 → 机器人在钢坯端面自动贴附。胶层接触瞬间软化、渗入氧化皮孔隙,冷却后形成机械锚固。钢坯在降温、行车转运、堆垛期间条码持续可扫;入炉前由扫码站确认身份并回传 MES。"))
    # features
    frows = "".join('<div class="frow"><div class="c">%s</div><div class="tx"><h4>%s</h4><p>%s</p></div></div>' % (CHK, H(*t), H(*d)) for t, d in HP_FEATURES)
    feat = '<section class="blk" style="background:#f4f7fd"><div class="wrap"><h2>%s</h2><div class="flist">%s</div></div></section>' % (H("Features", "产品特性"), frows)
    # benefits
    brows = "".join('<div class="frow"><div class="c">%s</div><div class="tx"><h4>%s</h4><p>%s</p></div></div>' % (IC_SOLVE, H(*t), H(*d)) for t, d in HP_BENEFITS)
    ben = '<section class="blk"><div class="wrap"><h2>%s</h2><div class="flist">%s</div></div></section>' % (H("Benefits", "客户收益"), brows)
    # specification + alt models + note
    srows = "".join('<tr><td class="k">%s</td><td>%s</td></tr>' % (H(*k), R(*v)) for k, v in HP_SPECS)
    alt = ('<h3 style="margin:24px 0 8px;color:var(--blue-deep)">%s</h3>'
           '<div class="ptable-wrap" style="overflow-x:auto;max-width:640px"><table class="sttbl"><thead><tr><th></th><th>HP-700T</th><th>HP-600</th></tr></thead><tbody>'
           '<tr><td class="k">%s</td><td>750℃</td><td>550℃</td></tr>'
           '<tr><td class="k">%s</td><td>%s</td><td>%s</td></tr>'
           '<tr><td class="k">%s</td><td>%s</td><td>%s</td></tr></tbody></table></div>') % (
        H("Alternative Models for This Process", "同工序备选型号"),
        H("Max. application temp","最高贴附温度"),
        H("Typical objects","典型对象"), H("Billets, slabs","钢坯、板坯"), H("Coils, aluminum sows","钢卷、铝锭"),
        H("When to choose","适用判断"), H("High-temp stock straight from the caster","连铸直出高温坯"), H("Objects already cooled / post-hot-rolling","已降温或热轧后对象"))
    note = '<p class="plsub" style="margin-top:14px;border-left:3px solid var(--green);padding-left:12px">%s</p>' % H(
        "Selection note: go by the measured surface temperature at the application point, not furnace temperature. If it falls between 550–750℃, request samples of both models and validate on site.",
        "选型提示:请以实测贴附点表面温度为准,而非炉温。表面温度介于 550–750℃ 时,建议同时索取两款样品做现场验证。")
    spec = '<section class="blk" style="background:#f4f7fd"><div class="wrap"><h2>%s</h2><div class="ptable-wrap" style="overflow-x:auto;max-width:760px"><table class="sttbl"><tbody>%s</tbody></table></div>%s%s</div></section>' % (
        H("Specification", "规格"), srows, alt, note)
    # system flow
    steps = [("MES / ERP (pushes heat number)","MES / ERP(下发炉次号)"),
             ("Thermal transfer printer + high-temp ribbon","热转印打印机 + 高温色带"),
             ("Robotic labeling → 750℃ hot billet (end-face)","机器人贴标 → 750℃ 热态钢坯(端面)"),
             ("Cooling bed / transport / stacking (stays readable)","冷床 / 转运 / 堆垛(条码持续可读)"),
             ("Scanning station before furnace entry → feedback to MES","入炉前扫码站 → 回传 MES")]
    flow = "".join('<b>%s</b>%s' % (H(*s), ('<span class="ar">↓</span>' if i < len(steps)-1 else '')) for i, s in enumerate(steps))
    system = '<section class="blk"><div class="wrap"><h2>%s</h2><div class="sysflow">%s</div></div></section>' % (H("System", "系统构成"), flow)
    # case study
    cs = ('<section class="blk" style="background:#f4f7fd"><div class="wrap"><h2>%s</h2>'
          '<p class="plsub" style="font-weight:700;color:var(--blue-deep)">%s</p>'
          '<div class="flist" style="grid-template-columns:1fr">%s</div></div></section>') % (
        H("Case Study", "案例研究"),
        H("Continuous casting line at a steel plant · Direct application on hot billets", "某钢厂连铸线 · 热态钢坯直贴"),
        "".join('<div class="frow"><div class="c">%s</div><div class="tx"><h4>%s</h4><p>%s</p></div></div>' % (CHK, H(*t), H(*d)) for t, d in [
            (("Background","背景"),("Billets managed by recorded position; inserted jobs and scrambled stacks caused frequent batch errors.","钢坯依靠位置记录管理,插单与堆垛乱序导致批次归属频繁出错。")),
            (("Challenge","挑战"),("750℃ measured at the application point, with scale continuously flaking off.","贴附点实测 750℃,表面氧化皮持续脱落。")),
            (("Solution","方案"),("Robotic labeling station after the cutter; HP-700T + on-site thermal transfer; scanning station before furnace entry.","切断机后设机器人贴标工位,HP-700T + 热转印现场打印,入炉前设扫码站。")),
            (("Result","结果"),("Manual hot-zone tagging eliminated; billet batch errors dropped significantly; charging records fed back to MES automatically.","高温区人工挂牌取消;钢坯批次错误显著下降;入炉记录自动回传 MES。")),
        ]))
    # documents
    docs = "".join('<a class="docr" href="%s"><span class="i">%s</span><span class="n">%s</span><span class="g">%s</span></a>' % (
        L(lang, "/contact/?doc=%s" % (i)) if g[0] == "Gated" else contact, DOC, H(*n), H(*g)) for i, (n, g) in enumerate(HP_DOCS))
    docsec = '<section class="blk"><div class="wrap"><h2>%s</h2><p class="plsub">%s</p><div class="doclist">%s</div></div></section>' % (
        H("Documents", "资料下载"),
        H("Direct downloads plus gated documents (leave your email to receive them).", "部分资料可直接下载,标注“留资”的请留下邮箱后获取。"), docs)
    # faq
    faqs = "".join('<details><summary>%s</summary></details>' % H(*q) for q in HP_FAQ)
    faq = '<section class="blk" style="background:#f4f7fd"><div class="wrap"><h2>%s</h2><div class="faq">%s</div></div></section>' % (H("FAQ", "常见问题"), faqs)
    body = STEEL_CSS + app + feat + ben + spec + system + cs + docsec + faq + ('<div class="wrap">%s</div>' % hp.cta2(lang, "product-detail"))
    path = "/industries/steel/hot-billet-direct-labeling/"
    crumb = [("Home" if not zh else "首页", "/"), ("Industries" if not zh else "行业", "/industries/"),
             ("Steel Industry" if not zh else "钢铁行业", "/industries/steel/"),
             ("HP-700T Hot Billet Labeling" if not zh else "HP-700T 热态钢坯直贴", path)]
    write(lang, path, page(lang, path,
        _t(lang, "HP-700T — 750℃ Direct Application Label for Hot Steel Billets | ETIA",
                 "HP-700T — 750℃ 热态钢坯直贴标签 | ETIA"),
        _t(lang, "HP-700T applies directly to 750℃ hot steel billets, anchors into scale and stays scannable through cooling, transport and stacking. Robot-ready, thermal-transfer printable.",
                 "HP-700T 直接贴附于 750℃ 热态钢坯,锚固氧化皮,在降温、转运、堆垛全程保持可扫。支持机器人自动贴标与热转印打印。"),
        _t(lang, "HP-700T — 750℃ Direct Application Label for Hot Steel Billets", "HP-700T — 750℃ 热态钢坯直贴标签"), "",
        body, crumb, active="", hero=hero))
    if lang == "en": hp.track(path, "products")

URLS = []
def main():
    for lang in LANGS:
        build_steel_landing(lang)
        build_hp700t(lang)
    URLS.extend(["/industries/steel/", "/industries/steel/hot-billet-direct-labeling/"])

if __name__ == "__main__":
    main()
