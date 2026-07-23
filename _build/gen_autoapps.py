#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Automotive Label Solutions — application sector landing at
/industries/automotive-label-materials/. 19 flat applications (no Level-1 layering)
shown as FLEXcon tabs; each tab has a single Introduction box + product cards below.
Product detail landing pages are future work. Content: _build/data/automotive_apps.json.
Runs AFTER gen_ind_landing so it owns /industries/automotive-label-materials/."""
import os, json, re
from urllib.parse import quote
import gen_heatproof as hp
from gen_heatproof import esc, L, Lx, page, write, LANGS

_D = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "automotive_apps.json"), encoding="utf-8"))
APPS = _D["apps"]
BANNER = _D["banner"]
PATH = "/industries/automotive-label-materials/"
AN_HUB = "/application-notes/"   # each application's full write-up lives here
ALL_LANGS = ["en", "zh", "vi", "th"]   # the automotive sector is fully 4-language
_LI = {"en": 0, "zh": 1, "vi": 2, "th": 3}

def _an_slug(name): return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

def _t(lang, en, zh, vi=None, th=None):
    return {"zh": zh, "vi": vi if vi is not None else en, "th": th if th is not None else en}.get(lang, en)
def _pk(lang, tup):
    i = _LI.get(lang, 0)
    return tup[i] if i < len(tup) else tup[0]
def _tn(lang, d, base):   # translate an app field with _en/_zh/_vi/_th suffixes
    return d.get(base + "_" + lang) or d.get(base + "_en", "")

# Shared 4-language property vocabulary — (en, zh, vi, th). Recommendation chip.
PROP = {
 "Abrasion-Resistant": ("Abrasion-Resistant","耐磨","Chống mài mòn","ทนการเสียดสี"),
 "Chemical-Resistant": ("Chemical-Resistant","耐化学","Chống hóa chất","ทนสารเคมี"),
 "Corrosion-Resistant": ("Corrosion-Resistant","耐腐蚀","Chống ăn mòn","ทนการกัดกร่อน"),
 "Heat-Resistant": ("Heat-Resistant","耐热","Chịu nhiệt","ทนความร้อน"),
 "High-Temperature-Resistant": ("High-Temperature-Resistant","耐高温","Chịu nhiệt độ cao","ทนอุณหภูมิสูง"),
 "Humidity-Resistant": ("Humidity-Resistant","耐潮湿","Chống ẩm","ทนความชื้น"),
 "Oil-Resistant": ("Oil-Resistant","耐油污","Chống dầu","ทนน้ำมัน"),
 "Temperature-Resistant": ("Temperature-Resistant","耐温变","Chịu biến thiên nhiệt","ทนการเปลี่ยนอุณหภูมิ"),
 "UV-Resistant": ("UV-Resistant","耐紫外","Chống tia UV","ทนรังสียูวี"),
 "Water-Resistant": ("Water-Resistant","耐水","Chống nước","ทนน้ำ"),
 "Waterproof": ("Waterproof","防水","Chống thấm nước","กันน้ำ"),
 "Weather-Resistant": ("Weather-Resistant","耐候","Chịu thời tiết","ทนสภาพอากาศ"),
 "Laser-Markable": ("Laser-Markable","激光打标","Khắc laser được","พิมพ์ด้วยเลเซอร์ได้"),
 "Tamper-Evident": ("Tamper-Evident","防拆","Chống giả mạo","ป้องกันการงัดแงะ"),
 "Flexible": ("Flexible","柔性","Linh hoạt","ยืดหยุ่น"),
}
# Challenge (stressor) paired to each property — (en, zh, vi, th).
PROP_CHALLENGE = {
 "Heat-Resistant": ("High Temperature","高温","Nhiệt độ cao","อุณหภูมิสูง"),
 "High-Temperature-Resistant": ("High Temperature","高温","Nhiệt độ cao","อุณหภูมิสูง"),
 "Chemical-Resistant": ("Chemicals","化学品","Hóa chất","สารเคมี"),
 "Oil-Resistant": ("Oil / Fluids","油污","Dầu / chất lỏng","น้ำมัน / ของเหลว"),
 "Humidity-Resistant": ("Moisture","潮湿","Độ ẩm","ความชื้น"),
 "UV-Resistant": ("UV Exposure","紫外线","Tia UV","รังสียูวี"),
 "Weather-Resistant": ("Weather / Outdoor","户外候变","Thời tiết / ngoài trời","สภาพอากาศ / กลางแจ้ง"),
 "Abrasion-Resistant": ("Abrasion","磨损","Mài mòn","การเสียดสี"),
 "Water-Resistant": ("Water","水","Nước","น้ำ"),
 "Waterproof": ("Water / Rain Exposure","淋雨/浸水","Nước / mưa","น้ำ / ฝน"),
 "Corrosion-Resistant": ("Corrosion","腐蚀","Ăn mòn","การกัดกร่อน"),
 "Temperature-Resistant": ("Temperature Cycling","温度变化","Chu kỳ nhiệt","การเปลี่ยนอุณหภูมิ"),
 "Tamper-Evident": ("Tamper Risk","防拆需求","Nguy cơ giả mạo","ความเสี่ยงการงัดแงะ"),
 "Laser-Markable": ("Permanent Marking","永久标识","Đánh dấu vĩnh viễn","การทำเครื่องหมายถาวร"),
 "Flexible": ("Flexing / Bending","弯曲变形","Uốn cong","การโค้งงอ"),
}
# back-compat: PROP_ZH used by gen_appnotes
PROP_ZH = {k: v[1] for k, v in PROP.items()}

def _svg(p): return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">%s</svg>' % p)
IC_INTRO = _svg('<circle cx="12" cy="12" r="9"/><path d="M12 16v-5M12 8h.01"/>')
IC_CHAL = _svg('<path d="M12 3 2 20h20L12 3z"/><path d="M12 10v5M12 18h.01"/>')
IC_SOL  = _svg('<path d="M12 3 4 6.5v5c0 4.6 3.2 7.7 8 9.5 4.8-1.8 8-4.9 8-9.5v-5L12 3z"/><path d="m9 12 2 2 4-4"/>')
# Risk-of-wrong-label — shield with an X (what goes wrong if the label is mismatched)
IC_RISK = _svg('<path d="M12 3 4 6.5v5c0 4.6 3.2 7.7 8 9.5 4.8-1.8 8-4.9 8-9.5v-5L12 3z"/><path d="m9.5 9.5 5 5M14.5 9.5l-5 5"/>')

UI = {
 "browse": ("Browse by Application","按应用浏览","Duyệt theo ứng dụng","เรียกดูตามการใช้งาน"),
 "products": ("Recommended Products","推荐产品","Sản phẩm đề xuất","ผลิตภัณฑ์แนะนำ"),
 "challenge": ("Challenge","应用挑战","Thách thức","ความท้าทาย"),
 "recommend": ("Recommendation","推荐方案","Khuyến nghị","คำแนะนำ"),
 "feature": ("Feature","特性","Đặc tính","คุณสมบัติ"),
 "benefit": ("Benefit","收益","Lợi ích","ประโยชน์"),
 "spec": ("Specification","规格","Thông số","ข้อกำหนด"),
 "talk": ("Talk to a Specialist","咨询专家","Trao đổi với chuyên gia","ปรึกษาผู้เชี่ยวชาญ"),
 "details": ("View details","查看详情","Xem chi tiết","ดูรายละเอียด"),
 "eyebrow": ("AUTOMOTIVE · LABELING SOLUTIONS","汽车 · 标签解决方案","Ô TÔ · GIẢI PHÁP NHÃN","ยานยนต์ · โซลูชันฉลาก"),
 "name": ("Automotive Labeling Solutions","汽车标签解决方案","Giải pháp nhãn ô tô","โซลูชันฉลากยานยนต์"),
 "subhead": ("Reliable labeling solutions for vehicle identification, safety, warning, and component tracking. Designed to withstand heat, chemicals, abrasion, fluids, and outdoor exposure throughout the vehicle lifecycle.",
             "面向车辆标识、安全、警示与部件追踪的可靠标签方案 专为在整车生命周期中承受高温、化学品、磨损、油液与户外暴露而设计",
             "Giải pháp nhãn đáng tin cậy cho nhận diện xe, an toàn, cảnh báo và theo dõi linh kiện. Được thiết kế để chịu nhiệt, hóa chất, mài mòn, chất lỏng và phơi nhiễm ngoài trời trong suốt vòng đời của xe.",
             "โซลูชันฉลากที่เชื่อถือได้สำหรับการระบุยานพาหนะ ความปลอดภัย การเตือน และการติดตามชิ้นส่วน ออกแบบให้ทนความร้อน สารเคมี การเสียดสี ของเหลว และการสัมผัสกลางแจ้งตลอดอายุการใช้งานของรถ"),
 "intro": ("Match each application by environment challenge to the recommended E-LABEL material. Label purpose, risk of the wrong label and full product specifications are covered in Application Notes.",
           "按每个应用面临的环境挑战,匹配推荐的 E-LABEL 材料。标签用途、用错标签的风险与完整产品规格,详见 Application Notes。",
           "Ghép mỗi ứng dụng theo thách thức môi trường với vật liệu E-LABEL được đề xuất. Mục đích nhãn, rủi ro dùng sai nhãn và thông số sản phẩm đầy đủ có trong Ghi chú ứng dụng.",
           "จับคู่แต่ละการใช้งานตามความท้าทายด้านสภาพแวดล้อมกับวัสดุ E-LABEL ที่แนะนำ วัตถุประสงค์ของฉลาก ความเสี่ยงของการใช้ฉลากผิด และข้อกำหนดผลิตภัณฑ์ฉบับเต็มอยู่ในแอปพลิเคชันโน้ต"),
 "exp_eyebrow": ("EXPLORE PRODUCTS","浏览产品","KHÁM PHÁ SẢN PHẨM","สำรวจผลิตภัณฑ์"),
 "exp_title": ("Explore Label Products","浏览标签产品","Khám phá sản phẩm nhãn","สำรวจผลิตภัณฑ์ฉลาก"),
 "exp_sub": ("Durable label materials selected for vehicle identification, under-hood, fluids and outdoor exposure. Browse the full range in the product catalog.",
             "面向车辆标识、发动机舱、油液与户外暴露精选的耐用标签材料 在产品目录中浏览完整系列",
             "Vật liệu nhãn bền được chọn cho nhận diện xe, khoang động cơ, chất lỏng và phơi nhiễm ngoài trời. Duyệt toàn bộ dải sản phẩm trong danh mục.",
             "วัสดุฉลากทนทานที่คัดสรรสำหรับการระบุยานพาหนะ ใต้ฝากระโปรง ของเหลว และกลางแจ้ง เรียกดูผลิตภัณฑ์ทั้งหมดในแคตตาล็อก"),
 "browse_all": ("Browse all products","浏览全部产品","Xem tất cả sản phẩm","ดูผลิตภัณฑ์ทั้งหมด"),
 "learn_eyebrow": ("APPLICATION NOTES","应用笔记","GHI CHÚ ỨNG DỤNG","แอปพลิเคชันโน้ต"),
 "learn_title": ("Learn from Application Notes","从应用笔记中学习","Tìm hiểu từ ghi chú ứng dụng","เรียนรู้จากแอปพลิเคชันโน้ต"),
 "learn_sub": ("Engineering guidance on where each label is used, what it must survive, and how to choose the right material.",
               "工程视角讲解每种标签用在哪、要承受什么、如何选对材料",
               "Hướng dẫn kỹ thuật về nơi dùng mỗi nhãn, phải chịu được gì và cách chọn vật liệu phù hợp.",
               "คำแนะนำเชิงวิศวกรรมว่าฉลากแต่ละแบบใช้ที่ไหน ต้องทนอะไร และเลือกวัสดุอย่างไร"),
 "all_notes": ("All application notes","全部应用笔记","Tất cả ghi chú ứng dụng","แอปพลิเคชันโน้ตทั้งหมด"),
 "read": ("Read","阅读","Đọc","อ่าน"),
}

# Curated "Explore Label Products" cards for the industry landing (link to the
# product catalog; per-family product pages are future work). (en, zh, vi, th) pairs.
EXPLORE_CARDS = [
 {"t": ("Durable Polyester Labels","耐用聚酯标签","Nhãn polyester bền","ฉลากโพลีเอสเตอร์ทนทาน"),
  "d": ("Vehicle and component identification that resists heat, humidity and abrasion.",
        "耐高温、耐潮湿、耐磨的车辆与部件标识",
        "Nhận diện xe và linh kiện chịu nhiệt, ẩm và mài mòn.",
        "การระบุยานพาหนะและชิ้นส่วนที่ทนความร้อน ความชื้น และการเสียดสี")},
 {"t": ("Laser-Markable VIN Labels","激光打标 VIN 标签","Nhãn VIN khắc laser","ฉลาก VIN พิมพ์เลเซอร์"),
  "d": ("Permanent, tamper-evident vehicle identification for lifetime traceability.",
        "永久、防拆的车辆标识,支持全生命周期追溯",
        "Nhận diện xe vĩnh viễn, chống giả mạo cho truy xuất trọn đời.",
        "การระบุยานพาหนะถาวร ป้องกันการงัดแงะ เพื่อการติดตามตลอดอายุ")},
 {"t": ("Oil & Chemical Resistant Labels","耐油耐化学标签","Nhãn chống dầu & hóa chất","ฉลากทนน้ำมันและสารเคมี"),
  "d": ("Under-hood, battery and fluid-reservoir labels that hold through oil and chemical contact.",
        "发动机舱、电池与油液罐标签,耐油污与化学品接触不脱落",
        "Nhãn khoang động cơ, ắc-quy và bình chứa chịu dầu và hóa chất.",
        "ฉลากใต้ฝากระโปรง แบตเตอรี่ และถังของเหลว ที่ทนน้ำมันและสารเคมี")},
 {"t": ("Low-Temperature Labels","低温标签","Nhãn nhiệt độ thấp","ฉลากอุณหภูมิต่ำ"),
  "d": ("Cold-chain and cryogenic apply that stays bonded at deep-freeze temperatures.",
        "冷链与深冷贴附,在极低温下仍牢固粘接",
        "Dán chuỗi lạnh và siêu lạnh, bám chắc ở nhiệt độ đông sâu.",
        "การติดในห่วงโซ่ความเย็นและอุณหภูมิต่ำมาก คงการยึดเกาะที่อุณหภูมิแช่แข็ง")},
]

# Application notes that belong to this industry (slug + title/blurb, EN+ZH notes).
LEARN_NOTES = [
 {"slug": "tire-bead-labels",
  "t": ("Tire Bead Labels","轮胎胎圈标签"),
  "d": ("Reliable barcode identification from green tire production through vulcanization, inspection and final assembly.",
        "从绿胎生产、硫化、检验到总装的可靠条码标识")},
 {"slug": "vin-labels",
  "t": ("VIN Labels","VIN 标签"),
  "d": ("Permanent vehicle identification for lifetime traceability — laser-markable, weather- and chemical-resistant, tamper-evident.",
        "面向全生命周期追溯的永久车辆标识 可激光打标、耐候耐化学、防篡改")},
]

CSS = """<style>
.avhero{background:linear-gradient(115deg,rgba(9,24,64,.92),rgba(16,44,120,.66) 55%,rgba(26,86,219,.30)),url('__BANNER__') center/cover no-repeat #0c2555;color:#fff}
.avhero .wrap{padding:56px 24px}.avhero .eyebrow{color:#9dbcff}
.avhero h1{color:#fff;font-size:38px;font-weight:800;line-height:1.14;margin:6px 0 12px;max-width:20em}
.avhero p{color:#eef3ff;font-size:16px;line-height:1.6;max-width:56em}
.avovbody{max-width:70em}.avovbody p{font-size:17px;line-height:1.7;color:var(--ink)}
.avmod{margin-top:8px}
.avtabsrow{display:flex;align-items:center;gap:6px;border-bottom:1px solid var(--line)}
.avtabs{display:flex;gap:24px;overflow-x:auto;scrollbar-width:none;flex:1}.avtabs::-webkit-scrollbar{display:none}
.avtab{white-space:nowrap;background:none;border:none;padding:12px 0;font-size:15px;font-weight:700;color:var(--mut);cursor:pointer;border-bottom:3px solid transparent;margin-bottom:-1px}
.avtab.on{color:var(--blue-deep);border-bottom-color:var(--blue)}
.avarrow{background:none;border:none;font-size:20px;color:var(--mut);cursor:pointer;padding:4px 6px}
.avpanel{padding-top:24px}
.av3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;align-items:start}
.av2{display:grid;grid-template-columns:1fr 1fr;gap:14px;align-items:start;max-width:760px}
.avbox{border:1px solid var(--line);border-radius:12px;padding:18px 20px;background:#fff}
.avbox .h{display:flex;align-items:center;gap:12px;margin-bottom:10px}
.avbox .h .i{width:28px;height:28px;flex:0 0 auto}.avbox .h .i svg{width:28px;height:28px}
.avbox .h .e{font-size:12px;font-weight:800;letter-spacing:.04em;text-transform:uppercase}
.avbox .area{display:inline-block;background:var(--tint-blue);color:var(--blue-deep);font-size:11.5px;font-weight:700;border-radius:20px;padding:4px 12px;margin-bottom:10px}
.avbox p{font-size:14px;color:var(--ink);line-height:1.55}
.avchips{display:flex;flex-wrap:wrap;gap:7px;margin-top:2px}
.avchip{font-size:12px;font-weight:700;border-radius:20px;padding:5px 12px;line-height:1.25}
.avchip.ch{background:#fff1e8;color:#b4531a;border:1px solid #f4cdb0}
.avchip.so{background:var(--mint);color:var(--green-d);border:1px solid #cfe6c5}
.avrec{margin-top:12px;display:flex;align-items:center;flex-wrap:wrap;gap:8px;font-size:13px;font-weight:800;color:var(--green-d)}
.avrec span{background:var(--green-d);color:#fff;border-radius:5px;padding:2px 7px;font-size:10px;letter-spacing:.05em}
.avplw{margin-top:26px}.avplh{font-size:12px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--mut);margin-bottom:12px}
.avplg{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}
.avplc{display:flex;flex-direction:column;border:1px solid var(--line);border-radius:12px;padding:18px 20px;background:#fff;text-decoration:none;transition:.16s}
.avplc:hover{border-color:var(--blue);box-shadow:0 12px 30px rgba(20,40,90,.12);transform:translateY(-3px)}
.avplc .avbrand{align-self:flex-start;font-size:10px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--green-d);background:var(--mint);border:1px solid #cfe6c5;border-radius:6px;padding:2px 8px;margin-bottom:8px}
.avplc .avbrand.cp{color:#5b3fa0;background:#f1edfb;border-color:#ddd2f3}
.avplc .avdist{font-size:11px;color:var(--faint);font-weight:600;margin-top:3px}
.avplc .t{font-weight:800;color:var(--blue-deep);font-size:16px;line-height:1.3}
.avplc .m{font-size:13px;font-weight:700;color:var(--blue);margin-top:7px}
.avplc .sp{font-size:12.5px;color:var(--ink);margin-top:7px;line-height:1.4}
.avplc .sp span{display:block;color:var(--faint);font-weight:800;text-transform:uppercase;font-size:10px;letter-spacing:.04em;margin-bottom:1px}
.avplc .go{font-size:12.5px;font-weight:700;color:var(--green-d);margin-top:12px}
.avrisk{margin-top:18px;background:#fff6f2;border:1px solid #f4cdb0;border-left:4px solid #e0762f;border-radius:10px;padding:13px 18px;font-size:14px;color:#8a3f14;line-height:1.6}
.avrisk .rl{font-weight:800;color:#c2621f;display:block;margin-bottom:3px;font-size:11px;text-transform:uppercase;letter-spacing:.04em}
.avplc.avfc{cursor:default}
.avplc.avfc:hover{transform:none;box-shadow:none;border-color:var(--line)}
.avplc.avfc .fd{font-size:13.5px;color:var(--mut);line-height:1.6;margin-top:9px}
@media(max-width:820px){
 .avplg{grid-template-columns:1fr}
 .av3{grid-template-columns:1fr;gap:10px}
 /* the 2 keyword cards stay side-by-side (one row) on mobile — kept compact */
 .av2{grid-template-columns:1fr 1fr;gap:9px}
 .avbox{padding:11px 12px}
 .avbox .h{margin-bottom:7px;gap:8px}.avbox .h .i,.avbox .h .i svg{width:18px;height:18px}
 .avbox .h .e{font-size:11px}
 .avchips{gap:5px}.avchip{font-size:11px;padding:3px 8px}
 .avrec{font-size:11.5px;gap:6px;margin-top:9px}.avrec span{font-size:9px;padding:2px 5px}
}
/* Explore Label Products + Learn from Application Notes (industry hub) */
.avxg{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px;margin-top:20px}
.avxc{display:block;border:1px solid var(--line);border-radius:14px;padding:22px;background:#fff;text-decoration:none;transition:.16s}
.avxc:hover{border-color:var(--blue);box-shadow:0 12px 30px rgba(20,40,90,.12);transform:translateY(-3px)}
.avxc .xt{font-weight:800;color:var(--blue-deep);font-size:16.5px;line-height:1.3}
.avxc .xd{font-size:13.5px;color:var(--mut);line-height:1.6;margin-top:9px}
.avxc .xgo{font-size:12.5px;font-weight:700;color:var(--green-d);margin-top:14px}
.avng{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px;margin-top:20px}
.avnc{display:block;border:1px solid var(--line);border-radius:14px;padding:22px;background:#fff;text-decoration:none;transition:.16s}
.avnc:hover{border-color:var(--blue);box-shadow:0 12px 30px rgba(20,40,90,.12);transform:translateY(-3px)}
.avnc .nt{font-weight:800;color:var(--blue-deep);font-size:17px;line-height:1.3}
.avnc .ndd{font-size:14px;color:var(--mut);line-height:1.6;margin-top:9px}
.avnc .ngo{font-size:12.5px;font-weight:700;color:var(--green-d);margin-top:14px}
.avmore{margin-top:22px}
@media(max-width:820px){.avxg,.avng{grid-template-columns:1fr}}
</style>""".replace("__BANNER__", BANNER)

def build_sector(lang):
    def U(k): return esc(_pk(lang, UI[k]))
    contact = Lx(lang, "/contact/")
    hero = ('<section class="avhero"><div class="wrap">'
            '<h1>%s</h1><div style="margin-top:20px"><a class="btn pri" href="%s">%s</a></div>'
            '</div></section>') % (U("name"), contact, U("talk"))
    overview = ('<section class="blk"><div class="wrap"><div class="avovbody"><p>%s</p></div></div></section>') % U("subhead")
    # Explore Label Products — curated entry cards into the product catalog
    # (per-family product pages are future work; all link to /products/ for now).
    products_url = Lx(lang, "/products/")
    xcards = "".join(
        '<a class="avxc" href="%s"><div class="xt">%s</div><div class="xd">%s</div>'
        '<div class="xgo">→</div></a>' % (
            products_url, esc(_pk(lang, c["t"])), esc(_pk(lang, c["d"])))
        for c in EXPLORE_CARDS)
    explore = ('<section class="blk"><div class="wrap"><div class="eyebrow">%s</div>'
               '<h2>%s</h2><div class="sub">%s</div><div class="avxg">%s</div>'
               '<div class="avmore"><a class="btn sec" href="%s">%s →</a></div>'
               '</div></section>') % (
        U("exp_eyebrow"), U("exp_title"), U("exp_sub"), xcards, products_url, U("browse_all"))
    # Learn from Application Notes — industry notes (EN+ZH only; vi/th fall back to the EN note).
    def note_url(slug):
        return Lx(lang, AN_HUB + slug + "/") if lang in ("en", "zh") else (AN_HUB + slug + "/")
    ncards = "".join(
        '<a class="avnc" href="%s"><div class="nt">%s</div><div class="ndd">%s</div>'
        '<div class="ngo">%s →</div></a>' % (
            note_url(n["slug"]), esc(_t(lang, n["t"][0], n["t"][1])),
            esc(_t(lang, n["d"][0], n["d"][1])), U("read"))
        for n in LEARN_NOTES)
    notes_hub = Lx(lang, AN_HUB) if lang in ("en", "zh") else AN_HUB
    learn = ('<section class="blk" style="background:var(--tint-blue)"><div class="wrap">'
             '<div class="eyebrow">%s</div><h2>%s</h2><div class="sub">%s</div>'
             '<div class="avng">%s</div><div class="avmore"><a class="btn sec" href="%s">%s →</a></div>'
             '</div></section>') % (
        U("learn_eyebrow"), U("learn_title"), U("learn_sub"), ncards, notes_hub, U("all_notes"))
    body = CSS + overview + explore + learn + ('<div class="wrap">%s</div>' % hp.cta2(lang, "applications", hp.Lx))
    home = _t(lang, "Home", "首页", "Trang chủ", "หน้าแรก")
    inds = _t(lang, "Industries", "行业", "Ngành", "อุตสาหกรรม")
    sname = _pk(lang, UI["name"])
    crumb = [(home, "/"), (inds, "/industries/"), (sname, PATH)]
    title = _t(lang, "Automotive Labeling Solutions — Durable Vehicle Labels | ETIA",
                     "汽车标签解决方案 —— 耐用整车标签 | ETIA",
                     "Giải pháp nhãn ô tô — Nhãn xe bền vững | ETIA",
                     "โซลูชันฉลากยานยนต์ — ฉลากรถที่ทนทาน | ETIA")
    write(lang, PATH, page(lang, PATH, title, _pk(lang, UI["subhead"]),
        sname, "", body, crumb, active="", hero=hero, langs=ALL_LANGS))
    if lang == "en": hp.track(PATH, "industries")

URLS = [PATH]
def main():
    for lang in ALL_LANGS:
        build_sector(lang)

if __name__ == "__main__":
    main()
