#!/usr/bin/env python3
"""建立/迁移内容架构层: 从现有 product 数据填充
  application(细分应用实体) / product_application_link / product_feature /
  product_benefit / feature_dict, 并生成 application_note & case_study 的
  样板(status=template, 正文留空, 推荐产品用真实匹配)。
可反复执行(先清空关联表再重填, 幂等)。不编造正文内容。
"""
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data/labels.db"

# 特性可控词表(对应各品牌 By Feature / Resistance 轴)
FEATURES = [
    ("HEAT", "耐高温", "Heat Resistant", "resistance"),
    ("COLD", "耐低温", "Cold / Cryogenic", "resistance"),
    ("CHEM", "耐化学", "Chemical Resistant", "resistance"),
    ("ABRASION", "耐磨", "Abrasion Resistant", "resistance"),
    ("MOISTURE", "耐潮湿", "Moisture Resistant", "resistance"),
    ("OUTDOOR", "耐候/抗UV", "Weather / UV", "resistance"),
    ("STERILE", "耐灭菌", "Sterilization", "resistance"),
    ("TAMPER", "防篡改", "Tamper Evident", "security"),
    ("ESD", "防静电", "Static Dissipative", "special"),
    ("FLAME", "阻燃", "Flame Retardant", "compliance"),
    ("UL", "UL/cUL认证", "UL Recognized", "compliance"),
    ("ROHS", "RoHS环保", "RoHS / Sustainable", "compliance"),
    ("HAZMAT", "危险品GHS", "Hazard Communication", "compliance"),
    ("LASER", "激光可打标", "Laser Markable", "print"),
    ("THERMAL", "热转印", "Thermal Transfer", "print"),
]
# 从产品 feature/benefit/名称文本 识别特性
FEAT_MATCH = [
    ("HEAT", r"high.?temp|耐高温|回流焊|reflow|autoclave.*heat"),
    ("COLD", r"cryo|冻存|low.?temp|耐低温|freezer|liquid nitrogen|-\d{2,3}"),
    ("CHEM", r"chemical|solvent|耐化学|acetone|mek|resistant to.*(solvent|chemical)"),
    ("ABRASION", r"abrasion|耐磨|scratch|scuff"),
    ("MOISTURE", r"moisture|humid|防潮|耐水|water resist"),
    ("OUTDOOR", r"\bUV\b|weather|outdoor|耐候|抗紫外"),
    ("STERILE", r"steriliz|autoclave|gamma|eto|灭菌"),
    ("TAMPER", r"tamper|destructible|防拆|易碎|frangible"),
    ("ESD", r"\besd\b|static diss|防静电"),
    ("FLAME", r"flame|self.?exting|阻燃|fr\b|halogen"),
    ("UL", r"\bUL\b|cUL|UL969"),
    ("ROHS", r"rohs|reach|sustainable|环保"),
    ("HAZMAT", r"ghs|hazard|bs.?5609|危险品|化学品"),
    ("LASER", r"laser|激光"),
    ("THERMAL", r"thermal transfer|热转印"),
]


def slugify(s):
    s = re.sub(r"[^\w\s-]", "", s or "").strip().lower()
    return re.sub(r"[\s_]+", "-", s)[:60] or "x"


def main():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    db.executescript((ROOT / "app/schema_content.sql").read_text(encoding="utf-8"))

    # 幂等: 清空派生表(仅本脚本填的, 不动人工内容除template外)
    for t in ("product_application_link", "product_feature", "product_benefit", "note_product"):
        db.execute(f"DELETE FROM {t}")
    db.execute("DELETE FROM application_note WHERE status='template'")
    db.execute("DELETE FROM case_study WHERE status='template'")
    db.execute("DELETE FROM application")

    # feature_dict 词表
    for code, cn, en, cat in FEATURES:
        db.execute("INSERT OR IGNORE INTO feature_dict(feat_code,name_cn,name_en,category) VALUES(?,?,?,?)",
                   (code, cn, en, cat))
    fid = {r["feat_code"]: r["feature_id"] for r in db.execute("SELECT feat_code,feature_id FROM feature_dict")}

    # ---- 1. application 实体: 由 distinct sub_application + 所属行业 生成 ----
    #      行业归属取该应用下产品最常见的行业(排除多标污染, 用 SUB_IND 逻辑: 直接看已归类行业)
    from collections import defaultdict, Counter
    rows = db.execute("""SELECT sub_application sub, product_id id FROM product
                         WHERE sub_application IS NOT NULL AND sub_application!=''""").fetchall()
    app_products = defaultdict(list)
    for r in rows:
        app_products[r["sub"]].append(r["id"])
    # 应用→行业: 用归一化规则(权威), 而非产品多标签众数, 避免串味
    import importlib.util as _u
    _spec = _u.spec_from_file_location("bs", ROOT / "scripts/build_subapplications.py")
    _bs = _u.module_from_spec(_spec); _spec.loader.exec_module(_bs)
    code_by_cn = {r["app_name_cn"]: r["app_id"] for r in db.execute("SELECT app_id,app_name_cn FROM application_dict")}
    code_id = {r["app_code"]: r["app_id"] for r in db.execute("SELECT app_id,app_code FROM application_dict")}
    label_ind = {}
    for _pat, _label, _ind in _bs.RULES:
        label_ind.setdefault(_label, code_id.get(_ind))
    ind_by_app = {sub: label_ind.get(sub) for sub in app_products}

    en_map = {  # 常见应用英文名(用于SEO), 缺的留空
        "电路板PCB": "PCB Labeling", "铭牌/额定标牌": "Rating & Name Plate",
        "覆膜保护": "Overlaminate", "防静电ESD": "ESD-Safe Labeling",
        "轮胎标签": "Tire Labeling", "发动机舱/车厢底": "Under-Hood Labeling",
        "结构粘接/泡棉": "Bonding & Foam Tape", "动力电池": "EV Battery Labeling",
        "低温冻存": "Cryogenic Storage", "PCR管": "PCR Tube", "载玻片": "Microscope Slide",
        "样本管/试管": "Tubes & Vials", "血袋标签": "Blood Bag", "药品包装": "Pharma Packaging",
        "线缆标识": "Wire & Cable ID", "医疗可穿戴": "Medical Wearable",
    }
    app_id_by_name = {}
    for sub, pids in sorted(app_products.items(), key=lambda x: -len(x[1])):
        ind = ind_by_app.get(sub)
        code = slugify(en_map.get(sub, sub)) + "-" + str(abs(hash(sub)) % 9973)
        cur = db.execute("""INSERT INTO application(app_code,name_cn,name_en,industry_id,
                            seo_slug,is_hot,status) VALUES(?,?,?,?,?,?,1)""",
                         (code, sub, en_map.get(sub, ""), ind, slugify(en_map.get(sub, sub)),
                          1 if len(pids) >= 30 else 0))
        aid = cur.lastrowid
        app_id_by_name[sub] = aid
        # product_application_link: 该应用的所有产品
        for pid in pids:
            db.execute("INSERT OR IGNORE INTO product_application_link(product_id,application_id) VALUES(?,?)",
                       (pid, aid))

    # ---- 2. feature / benefit 结构化拆分 ----
    for r in db.execute("SELECT product_id id, feature, benefit, product_name_en ne FROM product"):
        # benefit: 按 ; 拆行
        for i, seg in enumerate([x.strip() for x in re.split(r"[;；]\s*", r["benefit"] or "") if x.strip()][:12]):
            db.execute("INSERT INTO product_benefit(product_id,text_en,sort_order) VALUES(?,?,?)",
                       (r["id"], seg, i))
        # feature: 拆行 + 识别可控特性tag
        hay = f"{r['feature'] or ''} {r['ne'] or ''}"
        matched = set()
        for code, pat in FEAT_MATCH:
            if re.search(pat, hay, re.I):
                matched.add(code)
        segs = [x.strip() for x in re.split(r"[;；]\s*", r["feature"] or "") if x.strip()][:12]
        if segs:
            for i, seg in enumerate(segs):
                # 该段命中的第一个特性tag
                tag = next((c for c, p in FEAT_MATCH if re.search(p, seg, re.I)), None)
                db.execute("INSERT INTO product_feature(product_id,feature_id,text_en,sort_order) VALUES(?,?,?,?)",
                           (r["id"], fid.get(tag), seg, i))
        else:
            for code in matched:  # 无feature文本但从名称识别出特性
                db.execute("INSERT INTO product_feature(product_id,feature_id,sort_order) VALUES(?,?,0)",
                           (r["id"], fid[code]))

    # ---- 3. Application Note & Case Study 样板(template, 正文空, 推荐产品真实) ----
    ind_cn = {r["app_id"]: r["app_name_cn"] for r in db.execute("SELECT app_id,app_name_cn FROM application_dict")}
    ind_abbr = {"电子制造": "ELEC", "汽车制造": "AUTO", "医疗器械": "MED",
                "制药": "PHARMA", "实验室/生物样本": "LAB", "数据通信/线缆": "DATA",
                "冶金钢铁": "METAL", "安全标识": "SAFE", "通用制造": "MFG"}
    seq = defaultdict(int)
    for sub, aid in app_id_by_name.items():
        ind = ind_by_app.get(sub)
        icn = ind_cn.get(ind, "通用")
        ab = ind_abbr.get(icn, "GEN")
        seq[ab] += 1
        # 该应用主推产品: 取带TDS、五维较全的前5款
        prods = db.execute("""SELECT p.product_id id FROM product_application_link l
            JOIN product p ON p.product_id=l.product_id
            WHERE l.application_id=? ORDER BY (p.tds_url IS NOT NULL) DESC, p.temp_long_max DESC LIMIT 5""",
            (aid,)).fetchall()
        # Application Note 样板
        ncur = db.execute("""INSERT INTO application_note(note_code,title_cn,application_id,industry_id,
            problem_cn,solution_cn,why_cn,seo_slug,is_hot,status)
            VALUES(?,?,?,?,?,?,?,?,?, 'template')""",
            (f"AN-{ab}-{seq[ab]:03d}", f"{sub} 应用方案", aid, ind,
             "", "", "", slugify(sub)+f"-note", 0))
        nid = ncur.lastrowid
        for i, pr in enumerate(prods):
            db.execute("INSERT OR IGNORE INTO note_product(note_id,product_id,sort_order) VALUES(?,?,?)",
                       (nid, pr["id"], i))
        # Case Study 样板
        ccur = db.execute("""INSERT INTO case_study(case_code,title_cn,industry_id,
            challenge_cn,solution_cn,result_cn,seo_slug,status)
            VALUES(?,?,?,?,?,?,?, 'template')""",
            (f"CS-{ab}-{seq[ab]:03d}", f"{sub} 客户案例", ind, "", "", "",
             slugify(sub)+"-case"))
        cid = ccur.lastrowid
        db.execute("INSERT OR IGNORE INTO case_application(case_id,application_id) VALUES(?,?)", (cid, aid))
        for pr in prods[:2]:
            db.execute("INSERT OR IGNORE INTO case_product(case_id,product_id) VALUES(?,?)", (cid, pr["id"]))

    db.commit()

    # ---- 报告 ----
    def n(q):
        return db.execute(q).fetchone()[0]
    print("内容架构已建立/迁移:")
    print(f"  application 细分应用实体:   {n('SELECT COUNT(*) FROM application')}")
    print(f"  product_application_link:  {n('SELECT COUNT(*) FROM product_application_link')} 条产品-应用关联")
    print(f"  product_feature 结构化特性: {n('SELECT COUNT(*) FROM product_feature')} 行 (含tag {n('SELECT COUNT(*) FROM product_feature WHERE feature_id IS NOT NULL')})")
    print(f"  product_benefit 结构化优势: {n('SELECT COUNT(*) FROM product_benefit')} 行")
    print(f"  application_note 样板:      {n('SELECT COUNT(*) FROM application_note')} (待填正文)")
    print(f"  note_product 推荐产品关联:  {n('SELECT COUNT(*) FROM note_product')} 条")
    print(f"  case_study 样板:            {n('SELECT COUNT(*) FROM case_study')} (待填正文)")
    print("\n  应用视角样例(v_application_full 前8):")
    for r in db.execute("SELECT name_cn,industry_cn,product_cnt,brand_cnt,note_cnt,case_cnt FROM v_application_full ORDER BY product_cnt DESC LIMIT 8"):
        print(f"    {r['name_cn']:12s} 行业:{r['industry_cn'] or '—':8s} 产品{r['product_cnt']:3d} 品牌{r['brand_cnt']} 方案{r['note_cnt']} 案例{r['case_cnt']}")
    db.close()


if __name__ == "__main__":
    main()
