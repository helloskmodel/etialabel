#!/usr/bin/env python3
"""在导入后, 为每款产品归一化"二级细分应用"(sub_application), 建立 行业→应用 两层树.

数据来源(不编造, 全部来自抓取原文):
- 各品牌 records 里已带的 sub_application 字段(Computype/FLEXcon部分)
- source_category_raw 里的分类路径(FLEXcon Underhood/Bonding、Avery 各线)
- Brady 选型器的 printerLabelApplications
归一化: 把英文/杂乱原文映射到统一的中文二级应用名, 并归到某个一级行业。
无法归类的保持空, 不硬凑。
"""
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data/labels.db"

# 归一化规则: (正则匹配 sub_application 或 source_category_raw 原文) -> (标准中文二级应用, 归属一级行业app_code)
# 顺序敏感, 具体在前。行业为空表示跟随产品已有行业。
RULES = [
    # —— 汽车 ——
    (r"under\s?hood|车厢底|发动机舱|engine", "发动机舱/车厢底", "AUTOMOTIVE"),
    (r"\bVIN\b|vehicle identification", "VIN车架号", "AUTOMOTIVE"),
    (r"tire|tyre|轮胎", "轮胎标签", "AUTOMOTIVE"),
    (r"sun\s?visor|遮阳板", "遮阳板警示", "AUTOMOTIVE"),
    (r"airbag|安全气囊", "安全气囊", "AUTOMOTIVE"),
    (r"battery|电池|EV Battery", "动力电池", "AUTOMOTIVE"),
    (r"wire harness|线束", "线束标识", "AUTOMOTIVE"),
    (r"bonding|粘接|mount|foam tape|泡棉", "结构粘接/泡棉", "AUTOMOTIVE"),
    (r"laser etch|激光", "激光打标件", "AUTOMOTIVE"),
    # —— 电子 ——
    (r"circuit board|\bPCB\b|电路板", "电路板PCB", "ELECTRONICS"),
    (r"lens|cover bonding|镜头|后盖", "镜头/后盖粘接", "ELECTRONICS"),
    (r"component|元器件|smd", "元器件标识", "ELECTRONICS"),
    (r"rating|name\s?plate|铭牌|nameplate", "铭牌/额定标牌", "ELECTRONICS"),
    (r"esd|static|防静电|静电", "防静电ESD", "ELECTRONICS"),
    (r"overlaminate|覆膜|over-?laminat", "覆膜保护", "ELECTRONICS"),
    (r"datacom|data\s?com|服务器|data center", "数据中心/机房", "DATACOM"),
    (r"wire|cable|线缆|自贴膜|self-lam", "线缆标识", "DATACOM"),
    # —— 医疗 / 制药 / 实验室 ——
    (r"blood bag|血袋|isbt", "血袋标签", "MEDICAL"),
    (r"wearable|可穿戴|derma|skin", "医疗可穿戴", "MEDICAL"),
    (r"medical device|器械|medflex", "医疗器械本体", "MEDICAL"),
    (r"syringe|注射器|vial|安瓿|ampoule", "针剂/西林瓶", "PHARMACY"),
    (r"pharm|制药|drug|药", "药品包装", "PHARMACY"),
    (r"compound storage|化合物", "化合物库", "PHARMACY"),
    (r"clinical trial|临床", "临床试验", "PHARMACY"),
    (r"cryo|cryogenic|冻存|liquid nitrogen|液氮|-196", "低温冻存", "LAB_BIO"),
    (r"\bPCR\b|pcr tube", "PCR管", "LAB_BIO"),
    (r"microscope slide|载玻片|slide", "载玻片", "LAB_BIO"),
    (r"microplate|微孔板|well plate", "微孔板", "LAB_BIO"),
    (r"tube|vial|样本管|sample", "样本管/试管", "LAB_BIO"),
    (r"histology|组织|包埋|cassette", "组织病理", "LAB_BIO"),
    (r"chromatograph|色谱", "色谱耗材", "LAB_BIO"),
    (r"cell culture|细胞培养|labware", "细胞培养/耗材", "LAB_BIO"),
    (r"reagent|试剂", "试剂标签", "LAB_BIO"),
    (r"cannabis|大麻", "大麻检测", "LAB_BIO"),
    (r"laboratory|实验室|library book", "通用实验室", "LAB_BIO"),
    # —— 冶金 / 通用工业 ——
    (r"steel|钢|billet|钢坯|连铸|casting|锻|forging", "钢铁/铸锻件", "METALLURGY"),
    (r"aluminum|aluminium|铝|galvaniz|镀锌", "有色/表面处理", "METALLURGY"),
    (r"ceramic|陶瓷", "陶瓷制品", "MANUFACTURING"),
    (r"drum|barrel|ghs|hazard|危险品|化学品", "危化品GHS", "SAFETY"),
    (r"inspection|检验|inventory|资产|asset", "检验/资产追踪", "MANUFACTURING"),
    (r"garment|纺织|apparel|textile", "纺织服装", "MANUFACTURING"),
    (r"drive belt|conveyor|传送带|air spring|气弹簧", "工业部件", "MANUFACTURING"),
]


def classify(sub_raw, src_raw, name):
    hay = " ".join(filter(None, [sub_raw or "", src_raw or "", name or ""]))
    for pat, label, ind in RULES:
        if re.search(pat, hay, re.I):
            return label, ind
    return "", ""


def main():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    rows = db.execute("""SELECT p.product_id id, p.model_no m, p.product_name_en ne,
        p.sub_application sub, p.source_category_raw src FROM product p WHERE p.status=1""").fetchall()
    tree = defaultdict(lambda: defaultdict(int))
    n_set = 0
    for r in rows:
        label, ind = classify(r["sub"], r["src"], r["ne"] or r["m"])
        if label:
            db.execute("UPDATE product SET sub_application=? WHERE product_id=?", (label, r["id"]))
            n_set += 1
            tree[ind][label] += 1
        elif r["sub"]:
            # 保留原有非空 sub(如Computype原文), 但清掉冗长噪声
            db.execute("UPDATE product SET sub_application=? WHERE product_id=?", ("", r["id"]))
    db.commit()
    print(f"归一化二级应用: {n_set}/{len(rows)} 款已归类\n")
    ind_cn = {r["app_code"]: r["app_name_cn"] for r in
              db.execute("SELECT app_code, app_name_cn FROM application_dict")}
    for ind, subs in sorted(tree.items(), key=lambda x: -sum(x[1].values())):
        print(f"【{ind_cn.get(ind, ind)}】")
        for lab, n in sorted(subs.items(), key=lambda x: -x[1]):
            print(f"    {n:4d}  {lab}")
    db.close()


if __name__ == "__main__":
    main()
