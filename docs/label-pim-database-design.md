# 工业特种标签统一产品数据库（PIM）完整落地方案

> 适用范围：耐高温 / 耐化学特种标签（高温PI标签、PET高温标签、冶金超高温标签等极端工况产品）
> 覆盖品牌：3M、Brady（BradyID）、LINTEC、Avery Dennison（汽车/Medical/Pharmacy）、Polyonics、YS Tech Japan、Computype、Flexcon（汽车/Healthcare）、Mactac（Label Supply）、Mark Tech、ETIA（自研，etia-tech.com）
> 统一基准：**以3M五大维度分类体系为全局唯一标准**（行业应用 Application、面材类型 Facestock、胶水类型 Adhesive、耐温性能 Temperature、耐化学 Chemical Resistance）
> 设计原则：轻量化、可快速开发落地、一次录入多场景复用

---

# 模块1 数据库整体架构设计

## 1.1 分层逻辑（四层架构）

```
┌─────────────────────────────────────────────────────────────────┐
│  L3 应用输出层（多场景复用，统一API调取，零重复录入）              │
│  ├─ 内部销售选型查询端（后台多条件交叉筛选）                       │
│  ├─ 官网多行业垂直站点（汽车站/医疗站/冶金站…按行业集合页调取）     │
│  └─ 客户定制Catalog生成器（按客户工况自动筛选→生成专属电子目录）    │
├─────────────────────────────────────────────────────────────────┤
│  L2 统一主数据层（PIM核心，全库唯一事实源 Single Source of Truth）│
│  ├─ 产品主表 product（已对齐3M标准的标准化产品记录）               │
│  ├─ 物性参数表 product_property（耐温/耐化学/厚度等可筛选参数）    │
│  ├─ 文档附件表 product_document（TDS/手册/Notes与单品绑定）        │
│  └─ 产品-行业关联表 product_application（支撑行业集合页）          │
├─────────────────────────────────────────────────────────────────┤
│  L1 标准化映射层（解决多品牌分类不兼容的核心层）                   │
│  ├─ 3M基准字典表（行业/面材/胶水/耐温档位/耐化学等级 五套字典）     │
│  └─ 品牌分类映射表 brand_category_mapping（各品牌原始分类→3M标准） │
├─────────────────────────────────────────────────────────────────┤
│  L0 原始数据层（保留各品牌原貌，可追溯、可复核）                   │
│  ├─ 品牌表 brand                                                 │
│  └─ 产品主表中的"品牌原始字段"（原始分类名、原始规格描述原文留存）  │
└─────────────────────────────────────────────────────────────────┘
```

**分层要点：**

1. **L0保留原貌**：各品牌官网/TDS上的原始分类名、原始参数描述原文入库留存，不做破坏性覆盖，保证映射可追溯、可复核、可纠错；
2. **L1只做翻译**：映射层是"翻译器"，把 Brady 的 B-系列材料号、Polyonics 的 XF 系列、Avery 的 Fasson 分类等全部翻译成 3M 五维标准值，翻译规则本身入库（不写死在代码里），新品牌接入只需加映射记录，不改表结构；
3. **L2是唯一事实源**：所有前台应用（销售端、官网、Catalog生成器）只读 L2 标准化数据，不直接碰原始数据；
4. **L3只读复用**：三个应用场景通过同一套查询API调取 L2，一次录入、多场景复用，数据永远一致。

## 1.2 数据表关系（ER图）

```mermaid
erDiagram
    brand ||--o{ product : "1个品牌有多款产品"
    product ||--|| product_property : "1款产品1条物性参数"
    product ||--o{ product_document : "1款产品绑定多份文档"
    product ||--o{ product_application : "1款产品适配多个行业"
    application_dict ||--o{ product_application : "1个行业含多款产品"
    brand ||--o{ brand_category_mapping : "1个品牌多条映射规则"
    application_dict ||--o{ brand_category_mapping : "映射到行业字典"
    facestock_dict ||--o{ product : "面材字典约束"
    adhesive_dict ||--o{ product : "胶水字典约束"
    customer ||--o{ custom_catalog : "1个客户多份定制目录"
    custom_catalog ||--o{ catalog_item : "1份目录含多款产品"
    product ||--o{ catalog_item : "产品被目录引用"

    brand {
        bigint brand_id PK
        varchar brand_code
        tinyint brand_type "进口代理/自研"
    }
    product {
        bigint product_id PK
        bigint brand_id FK
        varchar model_no "型号"
        bigint facestock_id FK
        bigint adhesive_id FK
        text feature "F特性"
        text benefit "B优势"
        text application_desc "A适用工况"
    }
    product_property {
        bigint product_id PK_FK
        int temp_long_min "长期耐温下限℃"
        int temp_long_max "长期耐温上限℃"
        int temp_peak_max "短时峰值耐温℃"
        varchar chem_grade "耐化学等级"
    }
    product_document {
        bigint doc_id PK
        bigint product_id FK
        varchar doc_type "TDS/手册/Notes"
        varchar file_url
    }
    product_application {
        bigint id PK
        bigint product_id FK
        bigint app_id FK
    }
    application_dict {
        bigint app_id PK
        varchar app_code "行业编码"
    }
    brand_category_mapping {
        bigint map_id PK
        bigint brand_id FK
        varchar source_category "品牌原始分类"
        varchar target_dimension "对齐的3M维度"
        varchar target_value "对齐后标准值"
    }
```

## 1.3 技术选型建议（轻量化落地）

| 层 | 选型 | 理由 |
|---|---|---|
| 数据库 | MySQL 8.0（或 PostgreSQL 15） | 单库即可承载万级SKU；JSON字段存耐化学明细，兼顾结构化筛选与灵活扩展 |
| 文件存储 | 对象存储（阿里云OSS / MinIO自建） | TDS/手册PDF只存URL入库，文件与记录解耦，附件表可绑定多版本 |
| 后端API | 一套 RESTful API（任意语言框架） | 内部销售端、官网垂直站、Catalog生成器共用同一查询接口 |
| Catalog渲染 | HTML模板 → PDF（Puppeteer/wkhtmltopdf） | 电子目录即"筛选结果+模板渲染"，零人工排版 |
| 后台管理 | 任意Admin框架（如 Django Admin / 若依） | 录入、映射维护、复核审批开箱即用，不自研 |

**规模预估**：10个品牌 × 平均100~300款特种标签 ≈ 1000~3000 SKU，单库单表毫无压力，无需分库分表、无需搜索引擎（MySQL复合索引足够支撑五维交叉筛选），严格轻量。

---

# 模块2 全表完整字段清单

> 命名约定：小写下划线；所有表含 `created_at`、`updated_at`、`is_deleted`（软删除）三个通用字段，下文不再重复列出。

## 2.1 品牌表 `brand`

| 字段名 | 类型 | 必填 | 说明 | 示例 |
|---|---|---|---|---|
| brand_id | BIGINT PK | ✔ | 主键自增 | 1 |
| brand_code | VARCHAR(32) 唯一 | ✔ | 品牌编码（英文短码） | `3M` / `BRADY` / `ETIA` |
| brand_name_en | VARCHAR(128) | ✔ | 英文名 | Avery Dennison |
| brand_name_cn | VARCHAR(128) |  | 中文名 | 艾利丹尼森 |
| brand_type | TINYINT | ✔ | **1=进口代理，2=自有自研** | 2（ETIA自研） |
| country | VARCHAR(64) |  | 品牌所属国 | 美国 / 日本 / 中国 |
| official_site | VARCHAR(256) |  | 官网 | https://www.etia-tech.com |
| business_scope | VARCHAR(512) |  | 该品牌在本司代理的产品线范围 | Avery仅代理：汽车、Medical、Pharmacy线 |
| is_benchmark | TINYINT | ✔ | 是否为分类基准品牌（仅3M=1） | 1 |
| sort_order | INT |  | 前台展示排序 | 10 |
| status | TINYINT | ✔ | 1=启用 0=停用 | 1 |

**初始化数据（11条）**：3M（基准）、Brady、LINTEC、Avery Dennison、Polyonics、YS Tech Japan、Computype、Flexcon、Mactac、Mark Tech、ETIA（brand_type=2）。

## 2.2 产品主表 `product`

| 字段名 | 类型 | 必填 | 说明 | 示例 |
|---|---|---|---|---|
| product_id | BIGINT PK | ✔ | 主键自增 | 1001 |
| brand_id | BIGINT FK→brand | ✔ | 所属品牌 | 5（Polyonics） |
| model_no | VARCHAR(64) | ✔ | 品牌官方型号（品牌内唯一） | XF-100 / 3M 7818 / B-8544 |
| internal_sku | VARCHAR(64) 唯一 | ✔ | 本司统一SKU编码（对内对外唯一检索码） | ETL-PI-P5-001 |
| product_name_cn | VARCHAR(256) | ✔ | 标准中文品名 | 聚酰亚胺高温哑光标签 |
| product_name_en | VARCHAR(256) |  | 英文品名 | Polyimide High-Temp Matte Label |
| **facestock_id** | BIGINT FK→facestock_dict | ✔ | **面材类型（3M标准字典值）** | PI聚酰亚胺 |
| **adhesive_id** | BIGINT FK→adhesive_dict | ✔ | **胶水类型（3M标准字典值）** | 高温丙烯酸压敏胶 |
| **feature** | TEXT | ✔ | **F-产品特性**（材料构成、表面处理、可打印方式等客观特性，支持富文本要点） | 25μm PI面材+哑光陶瓷涂层，热转印碳带打印 |
| **benefit** | TEXT | ✔ | **B-产品优势**（对客户的价值：省成本/免返工/过认证等） | 回流焊三次过炉不脱落不焦化，条码等级保持A级 |
| **application_desc** | TEXT | ✔ | **A-适用工况行业**（文字描述版；结构化版走 product_application 关联表） | PCB波峰焊/回流焊过程追溯；钢厂连铸坯高温追踪 |
| color | VARCHAR(64) |  | 颜色/外观 | 白色哑光 / 透明 / 银色 |
| print_method | VARCHAR(128) |  | 适配打印方式（多选，逗号分隔字典值） | 热转印,激光打标 |
| certification | VARCHAR(256) |  | 认证（多选） | UL969, RoHS, REACH, ISO10993（医疗） |
| liner_type | VARCHAR(64) |  | 底纸类型 | 格拉辛 / PET底 |
| supply_form | VARCHAR(64) |  | 供货形式 | 卷材 / 平张 / 模切成品 |
| moq | VARCHAR(64) |  | 起订量说明 | 1卷 / 5㎡ |
| source_category_raw | VARCHAR(512) |  | **L0留存：该品牌官网原始分类路径原文** | Brady: Materials > Polyimide > Workhorse Series |
| source_url | VARCHAR(512) |  | 品牌官网产品源页面URL（追溯用） | https://www.bradyid.com/... |
| is_published | TINYINT | ✔ | 是否对外发布（0=仅内部可见，1=官网可见） | 1 |
| status | TINYINT | ✔ | 1=在售 2=停产可替代 0=下架 | 1 |

> 索引：`(brand_id)`、`(facestock_id)`、`(adhesive_id)`、`(internal_sku)` 唯一、`(model_no, brand_id)` 唯一。

## 2.3 物性参数表 `product_property`（与产品主表1:1，专供筛选）

> 极端工况核心表：所有可量化、可筛选的物性参数集中于此，字段设计已适配 **高温PI标签（≤300℃）、PET高温标签（≤200℃）、冶金超高温标签（≥1000℃短时）** 的取值范围。

| 字段名 | 类型 | 必填 | 说明 | 示例 |
|---|---|---|---|---|
| product_id | BIGINT PK & FK→product | ✔ | 与产品主表1:1 | 1001 |
| **temp_long_min** | SMALLINT | ✔ | 长期耐温下限（℃，可负） | -40 |
| **temp_long_max** | SMALLINT | ✔ | **长期连续耐温上限（℃）——核心筛选字段** | 260 |
| **temp_peak_max** | SMALLINT |  | 短时峰值耐温（℃）+ 见 temp_peak_duration | 1100（冶金标签） |
| temp_peak_duration | VARCHAR(32) |  | 峰值耐受时长 | 30min / 3次×90s回流焊 |
| **temp_tier** | VARCHAR(16) | ✔ | 耐温档位（由temp_long_max自动归档，见模块3归一化规则）：T1~T6 | T5 |
| **chem_grade** | CHAR(1) | ✔ | **耐化学综合等级（3M基准A/B/C/D）——核心筛选字段** | A |
| chem_detail | JSON |  | 分项耐化学明细：`{"溶剂":"优","酸":"良","碱":"良","油污":"优","醇类":"优","高压清洗":"良"}` | 见左 |
| thickness_face_um | SMALLINT |  | 面材厚度（μm） | 25 |
| thickness_adh_um | SMALLINT |  | 胶层厚度（μm） | 20 |
| thickness_total_um | SMALLINT |  | 总厚度含底纸（μm） | 88 |
| adhesion_n25mm | DECIMAL(6,2) |  | 180°剥离力（N/25mm，不锈钢板） | 8.50 |
| tack_initial | VARCHAR(64) |  | 初粘性描述/球号 | 12# |
| min_apply_temp | SMALLINT |  | 最低施贴温度（℃） | 10 |
| surface_energy_fit | VARCHAR(128) |  | 适贴表面类型（低表面能PP/PE、粗糙铸件、油面等） | 低表面能塑料,粉末喷涂面 |
| outdoor_life | VARCHAR(64) |  | 户外耐候年限 | 5年 / 不适用 |
| abrasion_resist | VARCHAR(16) |  | 耐磨等级（优/良/中/不适用） | 优 |
| flame_rating | VARCHAR(32) |  | 阻燃等级 | UL94 V-0 |
| esd_safe | TINYINT |  | 是否防静电型（电子行业筛选项） | 1 |
| autoclave_resist | TINYINT |  | 是否耐高压灭菌（医疗行业筛选项，134℃蒸汽） | 1 |
| ln2_resist | TINYINT |  | 是否耐液氮/深低温（-196℃，医疗冻存筛选项） | 0 |
| property_note | VARCHAR(512) |  | 物性备注（数据来源TDS版本号等） | 数据源：TDS Rev.2024-03 |

> 索引：`(temp_long_max)`、`(temp_tier)`、`(chem_grade)`——支撑耐温、耐化学高频筛选。

## 2.4 文档附件表 `product_document`（1款产品绑定多份资料）

| 字段名 | 类型 | 必填 | 说明 | 示例 |
|---|---|---|---|---|
| doc_id | BIGINT PK | ✔ | 主键自增 | 50001 |
| product_id | BIGINT FK→product | ✔ | 绑定单品 | 1001 |
| **doc_type** | VARCHAR(16) | ✔ | 文档类型枚举：**TDS**（技术数据表）/ **BROCHURE**(官方产品手册) / **NOTES**(应用说明) / MSDS / CERT(认证证书) / CASE(应用案例图文) | TDS |
| doc_title | VARCHAR(256) | ✔ | 文档标题 | Polyonics XF-100 TDS |
| file_url | VARCHAR(512) | ✔ | 对象存储文件地址 | oss://etia-pim/tds/xf100_v3.pdf |
| file_format | VARCHAR(16) | ✔ | pdf / docx / jpg | pdf |
| file_size_kb | INT |  | 文件大小 | 842 |
| language | VARCHAR(8) | ✔ | zh / en / ja | en |
| version | VARCHAR(32) |  | 版本号（同型号TDS可多版本共存，最新版置顶） | Rev.2024-03 |
| is_latest | TINYINT | ✔ | 是否当前有效版本 | 1 |
| **is_public** | TINYINT | ✔ | **对外可见性：1=官网可下载，0=仅内部/仅随定制Catalog发出** | 0 |
| upload_by | VARCHAR(64) |  | 上传人 | zhang.san |

> 规则：每款产品 `doc_type=TDS 且 is_latest=1` 的记录**必须存在且唯一**（录入审核卡点）；Notes 可多条（不同工况一条一记）。

## 2.5 行业映射表（两张表配合）

### 2.5.1 行业应用字典表 `application_dict`（3M Application 基准字典）

| 字段名 | 类型 | 必填 | 说明 | 示例 |
|---|---|---|---|---|
| app_id | BIGINT PK | ✔ | 主键 | 3 |
| app_code | VARCHAR(32) 唯一 | ✔ | 行业编码（与官网垂直站点路由一一对应） | `ELECTRONICS` |
| app_name_cn | VARCHAR(64) | ✔ | 行业中文名 | 电子制造 |
| app_name_en | VARCHAR(64) | ✔ | 行业英文名 | Electronics |
| parent_id | BIGINT |  | 父级行业（二级细分用，如 电子→PCB过程追溯） | 0=一级 |
| typical_condition | VARCHAR(512) |  | 该行业典型工况摘要（选型提示用） | 回流焊260℃×3次、助焊剂、清洗剂 |
| site_slug | VARCHAR(64) |  | 官网垂直站点URL路径 | /industry/electronics |
| banner_img | VARCHAR(512) |  | 行业集合页头图 | oss://... |
| sort_order | INT |  | 展示排序 | 1 |
| status | TINYINT | ✔ | 启用/停用 | 1 |

**一级行业初始化字典（对齐3M Application并覆盖全部代理品牌产品线）：**

| app_code | 行业 | 覆盖品牌产品线来源 |
|---|---|---|
| ELECTRONICS | 电子制造（PCB/SMT） | 3M、Polyonics、Brady、YS Tech、ETIA |
| METALLURGY | 冶金钢铁（超高温） | ETIA、Polyonics、Mark Tech |
| AUTOMOTIVE | 汽车制造 | Avery汽车线、Flexcon汽车线、3M、ETIA |
| MEDICAL | 医疗器械 | LINTEC Medical、Avery Medical、Flexcon Healthcare |
| PHARMACY | 制药 | Avery Pharmacy、Computype |
| LAB_BIO | 实验室/生物样本 | Computype、Brady |
| ENERGY_CHEM | 能源化工 | Brady、Mactac、ETIA |
| AEROSPACE | 航空航天 | Polyonics、3M |
| GENERAL_IND | 通用工业资产追踪 | Mactac、Mark Tech、全品牌 |

### 2.5.2 产品-行业关联表 `product_application`（多对多）

| 字段名 | 类型 | 必填 | 说明 | 示例 |
|---|---|---|---|---|
| id | BIGINT PK | ✔ | 主键 | 90001 |
| product_id | BIGINT FK→product | ✔ | 产品 | 1001 |
| app_id | BIGINT FK→application_dict | ✔ | 行业 | 3 |
| is_primary | TINYINT | ✔ | 是否该产品主打行业（行业集合页排序权重） | 1 |
| scene_note | VARCHAR(256) |  | 该行业下的具体应用场景备注 | 回流焊过炉PCB板号追溯 |

> 唯一索引：`(product_id, app_id)`。

## 2.6 标准字典表（3M基准，支撑面材/胶水/耐化学筛选）

### `facestock_dict` 面材字典

| 字段 | 说明 |
|---|---|
| facestock_id / face_code / face_name_cn / face_name_en / temp_capability_hint / sort_order / status | 结构同类字典 |

**初始化值（对齐3M面材分类，覆盖极端工况）**：PI聚酰亚胺（POLYIMIDE）、PET聚酯（POLYESTER）、耐高温PET（HT_PET）、陶瓷/金属基超高温复合（CERAMIC_METAL，冶金专用）、PEN、PPS、铝箔（ALU_FOIL）、PP、PE、PVC、聚烯烃POF、醋酸布/玻璃布（CLOTH）、Tyvek、纸类（PAPER）、合成纸（SYNTHETIC_PAPER）。

### `adhesive_dict` 胶水字典

**初始化值（对齐3M胶系分类）**：高温丙烯酸压敏胶（HT_ACRYLIC）、标准丙烯酸胶（ACRYLIC）、硅胶系（SILICONE，超高温/难粘表面）、橡胶系（RUBBER，高初粘）、可移除胶（REMOVABLE）、超强永久胶（AGGRESSIVE_PERM，低表面能/粗糙面）、低温冷贴胶（COLD_TEMP，医疗冻存）、医用低致敏胶（MEDICAL_GRADE）、无胶/机械固定（NONE，冶金挂签）。

### 耐化学等级基准（存 `product_property.chem_grade`，枚举无需单独建表）

| 等级 | 定义（对齐3M Chemical Resistance测试口径） |
|---|---|
| A | 耐强溶剂（MEK/丙酮/二甲苯）+强酸碱浸泡，外观与条码可读性无变化 |
| B | 耐常规溶剂（IPA/乙醇/汽油/机油）擦拭及短时浸泡 |
| C | 耐水、清洁剂、油污，不耐溶剂浸泡 |
| D | 仅耐日常环境，无耐化学要求场景 |

## 2.7 客户与定制目录表（支撑核心拓展功能②）

### `customer` 客户表

| 字段名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| customer_id | BIGINT PK | ✔ | 主键 |
| customer_name | VARCHAR(256) | ✔ | 客户公司名 |
| industry_app_id | BIGINT FK→application_dict | ✔ | 客户所属行业 |
| contact / phone / email | VARCHAR |  | 联系人信息 |
| sales_owner | VARCHAR(64) | ✔ | 归属销售 |
| condition_profile | JSON |  | 客户工况档案（沉淀复用）：`{"temp_max":300,"chem":["溶剂","助焊剂"],"surface":"FR4板材","process":"回流焊x3"}` |

### `custom_catalog` 定制目录主表

| 字段名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| catalog_id | BIGINT PK | ✔ | 主键 |
| customer_id | BIGINT FK→customer | ✔ | 目录归属客户 |
| catalog_title | VARCHAR(256) | ✔ | 目录标题（自动生成：客户名+专属选型目录+日期） |
| filter_snapshot | JSON | ✔ | 生成时的筛选条件快照（可追溯、可一键重新生成） |
| product_count | INT | ✔ | 收录产品数 |
| output_pdf_url | VARCHAR(512) |  | 生成的PDF文件地址 |
| output_h5_url | VARCHAR(512) |  | 在线H5目录链接（可发微信） |
| include_tds | TINYINT | ✔ | 是否打包附TDS |
| status | TINYINT | ✔ | 1=草稿 2=已生成 3=已发送客户 |
| created_by | VARCHAR(64) | ✔ | 生成人（销售） |

### `catalog_item` 目录明细表

| 字段名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| id | BIGINT PK | ✔ | 主键 |
| catalog_id | BIGINT FK→custom_catalog | ✔ | 所属目录 |
| product_id | BIGINT FK→product | ✔ | 收录产品 |
| match_score | DECIMAL(5,2) |  | 系统匹配得分（排序依据，见模块4算法） |
| is_recommended | TINYINT | ✔ | 是否销售人工置顶推荐 |
| sales_note | VARCHAR(512) |  | 销售针对该客户的补充说明（打印进目录） |
| sort_order | INT | ✔ | 目录内排序 |

---

# 模块3 多品牌数据标准化映射方案（3M基准）

## 3.1 基准定义：3M五大维度

所有品牌产品入库时，**必须完成五维对齐**，缺一不可发布：

| # | 维度 | 落库位置 | 标准值域 |
|---|---|---|---|
| D1 | 行业应用 Application | `product_application` 关联表 | `application_dict` 9个一级行业（可挂多个） |
| D2 | 面材类型 Facestock | `product.facestock_id` | `facestock_dict` 15个标准面材 |
| D3 | 胶水类型 Adhesive | `product.adhesive_id` | `adhesive_dict` 9个标准胶系 |
| D4 | 耐温性能 Temperature | `product_property.temp_tier`（档位）+ 精确数值字段 | T1~T6六档（见3.3） |
| D5 | 耐化学 Chemical Resistance | `product_property.chem_grade` | A/B/C/D四级（见2.6） |

## 3.2 映射机制：`brand_category_mapping` 映射规则表

映射规则**入库而非写死代码**，新品牌/新分类只加数据不改结构：

| 字段名 | 类型 | 必填 | 说明 | 示例 |
|---|---|---|---|---|
| map_id | BIGINT PK | ✔ | 主键 | 201 |
| brand_id | BIGINT FK→brand | ✔ | 来源品牌 | 2（Brady） |
| source_field | VARCHAR(64) | ✔ | 品牌原始字段/分类轴名称 | Material Series |
| source_value | VARCHAR(256) | ✔ | 品牌原始分类值（原文） | B-8544 Metallized Polyester |
| target_dimension | VARCHAR(8) | ✔ | 对齐目标维度 D1~D5 | D2 |
| target_value | VARCHAR(128) | ✔ | 对齐后的3M标准值（字典code） | HT_PET |
| mapping_type | TINYINT | ✔ | 1=字典直映（分类名→标准值）2=规则映射（数值→档位）3=人工判定 | 1 |
| rule_expr | VARCHAR(256) |  | 规则表达式（mapping_type=2时用） | `temp_long_max BETWEEN 181 AND 300 → T5` |
| confidence | TINYINT | ✔ | 置信度：1=官方文档明确 2=推断待复核 | 1 |
| reviewed_by | VARCHAR(64) |  | 复核人（产品工程师） | li.si |
| note | VARCHAR(512) |  | 依据说明（引用TDS页码等） | 见B-8544 TDS第2页耐温数据 |

**执行方式**：录入端选择品牌原始分类后，系统查映射表自动回填五维标准值 → 置信度=2的进入"待复核"队列，由产品工程师人工确认后方可发布。

## 3.3 数值型维度归一化规则（D4耐温 / D5耐化学）

**耐温档位 T1~T6（按长期连续耐温上限 `temp_long_max` 自动归档）：**

| 档位 | 长期耐温上限 | 典型产品形态 | 典型场景 |
|---|---|---|---|
| T1 | ≤80℃ | 普通PP/纸标签 | 常温资产追踪 |
| T2 | 81~120℃ | 标准PET标签 | 一般设备铭牌 |
| T3 | 121~180℃ | 高温PET标签 | 汽车引擎周边、涂装烘烤 |
| T4 | 181~260℃ | PI聚酰亚胺标签 | SMT回流焊、波峰焊 |
| T5 | 261~500℃ | 特种PI/PPS/铝箔复合 | 电泳烘烤、玻璃退火 |
| T6 | >500℃（短时峰值可≥1000℃） | 陶瓷/金属基冶金标签 | 钢坯、连铸、锻造追踪 |

> 归一化细则：① 品牌TDS只给峰值不给长期值时，按"峰值×0.7"估算长期值并标 confidence=2 待复核；② 华氏度一律换算摄氏度取整；③ 区间值取下限作为承诺值（对客户保守承诺原则）。

**耐化学等级归一化**：各品牌测试口径不一（3M按试剂浸泡、Brady按擦拭圈数、Polyonics按IPC标准），统一换算规则：凡官方声明耐受 MEK/二甲苯/强酸碱任一项浸泡→A；声明耐IPA/汽油/机油擦拭→B；仅声明耐水耐油污→C；无声明→D。原始测试描述保留在 `chem_detail` JSON 与 `property_note` 中，不丢信息。

## 3.4 各品牌 → 3M 映射规则明细

| 品牌 | 原始分类逻辑 | 映射转换规则（→3M五维） |
|---|---|---|
| **3M**（基准） | Application/面材/胶系/耐温/耐化学 | 直接入库，零转换；作为字典值来源 |
| **Brady (BradyID)** | 按材料号体系（B-xxx）分类，如 B-717 PI、B-8544 金属化PET | D2：材料号前缀→面材字典直映（B-717→POLYIMIDE）；D3：TDS胶系栏直映；D4/D5：TDS数值按3.3归档；D1：官网Application栏多对多映射 |
| **LINTEC** | 按应用场景分类（Medical等），labelstock按面材+胶型号组合命名 | D1：Medical线→MEDICAL；D2/D3：labelstock构成拆解直映；D4/D5：数值归档；医疗特性字段（灭菌/冻存）落 `autoclave_resist`/`ln2_resist` |
| **Avery Dennison** | 按Fasson物料体系+行业BU（Automotive/Medical/Pharmacy） | D1：按代理BU直映 AUTOMOTIVE/MEDICAL/PHARMACY；D2/D3：Fasson编码拆面材+胶水直映；D4/D5：数值归档 |
| **Polyonics** | 按材料技术系列（XF高温PI、防静电、阻燃等） | D2：XF系→POLYIMIDE为主；ESD系列落 `esd_safe=1`；D1：官网Markets栏映射（多为ELECTRONICS/AEROSPACE）；D4：Polyonics标称峰值多、按3.3规则折算长期值 |
| **YS Tech Japan** | 按耐热温度带+用途命名（日系习惯） | D4：温度带直接归档T档；D1：用途名映射行业；D2/D3：TDS拆解；日文资料入库时 `language=ja` 留原文档 |
| **Computype** | 按应用流程分类（实验室、血袋、灭菌流程等服务导向） | D1：→LAB_BIO/MEDICAL/PHARMACY；D2/D3：其底层物料反查直映；耐低温冻存特性落 `ln2_resist` |
| **Flexcon** | 按行业组合（汽车/Healthcare）+ 材料家族（THERMLfilm等） | D1：按代理线直映 AUTOMOTIVE/MEDICAL；D2：材料家族名→面材直映（THERMLfilm→HT_PET）；D4/D5数值归档 |
| **Mactac (labelsupply)** | 按面材大类+胶系目录式分类，与3M轴系天然接近 | 五维基本一一直映，映射成本最低；缺耐化学数据的标 D 级+confidence=2 待补测 |
| **Mark Tech** | 按用途系列（高温挂签/贴标） | D1：→METALLURGY/GENERAL_IND；D2：挂签类无胶产品 D3=NONE；D4：多落T5/T6 |
| **ETIA自研** | 自研料号体系 | **直接按3M五维定义料号属性，源头即标准**，无需映射；`brand_type=2` 在前台标注"自研"，与代理品并列检索 |

## 3.5 新品录入标准SOP（保障数据质量）

```
① 收集：品牌官网页+官方TDS（PDF入 product_document，is_latest=1）
② 留存：原始分类路径原文 → product.source_category_raw / source_url
③ 翻译：系统查 brand_category_mapping 自动回填五维；无匹配规则→新增映射记录
④ 复核：confidence=2 的记录由产品工程师核对TDS后确认
⑤ 卡点：五维齐全 + TDS已绑定 + FBA三要素非空 → 才允许 is_published=1
⑥ 发布：即刻同步可见于 内部销售端 / 官网行业站 / Catalog生成器（同库同API）
```

---

# 模块4 行业集合页 + 客户定制Catalog自动生成实现流程

## 4.0 统一查询API（一套接口，三端复用）

所有场景共用同一个产品查询接口，仅参数不同：

```
GET /api/products
参数（全部可选、可交叉组合）：
  brand_id[]      品牌（多选）
  brand_type      1=进口代理 2=自研
  app_code[]      行业应用（多选）
  temp_tier[]     耐温档位 T1~T6（多选）
  temp_min_need   耐温数值精确筛选（返回 temp_long_max >= 该值）
  chem_grade[]    耐化学等级（多选，A隐含满足B/C/D需求）
  facestock_id[]  面材材质（多选）
  adhesive_id[]   胶水类型（多选）
  keyword         型号/品名模糊搜索
  is_published    官网端强制=1；内部销售端不限
  sort / page / page_size
返回：产品卡片列表（型号、品牌+代理/自研标识、五维标签、FBA摘要、TDS下载链接[按is_public过滤]）
```

对应SQL核心（复合索引直接支撑，无需搜索引擎）：

```sql
SELECT p.*, pp.temp_long_max, pp.temp_tier, pp.chem_grade, b.brand_name_cn, b.brand_type
FROM product p
JOIN product_property pp ON pp.product_id = p.product_id
JOIN brand b             ON b.brand_id = p.brand_id
JOIN product_application pa ON pa.product_id = p.product_id
JOIN application_dict a  ON a.app_id = pa.app_id
WHERE a.app_code IN ('ELECTRONICS')          -- 行业
  AND pp.temp_long_max >= 260                -- 耐温
  AND pp.chem_grade IN ('A','B')             -- 耐化学
  AND p.facestock_id IN (1)                  -- 面材=PI
  AND p.is_published = 1 AND p.status = 1
ORDER BY pa.is_primary DESC, pp.temp_long_max DESC;
```

## 4.1 核心功能①：行业集合页（官网多垂直站点）

**实现流程：**

```
application_dict（行业字典）
      │  每个 app_code 对应一个垂直站路由 /industry/{site_slug}
      ▼
页面渲染时调用 GET /api/products?app_code=XXX&is_published=1
      │
      ▼
行业集合页自动生成，无需为各行业单独维护产品数据
```

**页面结构（每个行业站相同模板，数据驱动）：**

1. **行业头部**：`application_dict` 的行业名、头图、`typical_condition` 典型工况摘要；
2. **二级场景导航**：该行业下 `parent_id` 子行业Tab（如医疗站：高压灭菌 / 深低温冻存 / 器械追溯）；
3. **侧边筛选器**：在行业已锁定前提下，剩余四维（品牌/耐温/耐化学/面材）+胶水继续交叉过滤——筛选器选项**按当前结果集动态聚合**（带数量角标，空选项自动隐藏）；
4. **产品卡片流**：`is_primary=1` 主打产品置顶，卡片含 品牌标识（代理/自研角标）、五维参数标签、Benefit一句话卖点、TDS下载（`is_public=1`才显示）；
5. **SEO**：行业页URL、标题、描述由字典字段生成，支撑官网多行业垂直站获客。

**新增行业站点成本**：`application_dict` 加1条记录 + 产品打好关联 = 新垂直站自动上线，零开发。

## 4.2 核心功能②：客户定制Catalog自动生成

**端到端流程（销售操作 ≤5分钟出目录）：**

```
STEP 1 录入客户工况（表单，30秒）
  ├─ 选客户（customer表，工况档案condition_profile可复用上次记录）
  ├─ 行业：电子制造          → app_code
  ├─ 最高工作温度：300℃      → temp_min_need=300
  ├─ 化学接触：助焊剂+清洗剂  → chem_grade∈{A,B}
  ├─ 面材偏好：不限/指定PI    → facestock_id（可空）
  └─ 品牌偏好：不限/只看自研  → brand_type（可空）
        │
        ▼
STEP 2 自动匹配（调用统一API，两级逻辑）
  ├─ 硬条件过滤：耐温 ≥ 需求值、耐化学等级 ≥ 需求级、行业匹配 → 不达标一律排除
  └─ 匹配评分排序 match_score（0~100）：
       耐温余量适配度 40分   —— 略高于需求得满分，过度冗余（贵）适当降分
     + 耐化学等级适配 30分   —— 等级恰好满足>过度超配
     + 行业主打契合   20分   —— is_primary=1 加分
     + 自研优先       10分   —— brand_type=2 加分（毛利导向，可配置开关）
        │
        ▼
STEP 3 人工微调（可跳过）
  ├─ 销售在匹配结果中勾选/剔除、拖拽排序
  ├─ 置顶推荐款 is_recommended=1
  └─ 每款可加 sales_note（针对该客户的备注，打印进目录）
        │
        ▼
STEP 4 一键生成电子Catalog
  ├─ 写入 custom_catalog（含 filter_snapshot 条件快照）+ catalog_item 明细
  ├─ HTML模板渲染 → PDF（封面：客户名+定制目录+日期；每页一款：
  │    图片 + 五维参数表 + Feature/Benefit/Application三要素 + 应用Notes摘要）
  ├─ include_tds=1 时：自动打包该批产品最新版TDS（is_latest=1）为附件ZIP
  └─ 同步生成在线H5链接（手机/微信可直接转发客户）
        │
        ▼
STEP 5 存档复用
  ├─ 目录永久存档，客户工况变化时基于 filter_snapshot 一键重新生成
  └─ 数据库产品更新后，旧目录可"刷新再版"（同条件重跑匹配）
```

**匹配SQL示例（STEP 2硬条件+评分）：**

```sql
SELECT p.product_id, p.model_no, b.brand_name_cn, b.brand_type,
  ( LEAST(40, 40 - (pp.temp_long_max - 300) / 10)            -- 耐温余量适配
  + CASE WHEN pp.chem_grade = 'A' THEN 30 ELSE 25 END         -- 耐化学适配
  + CASE WHEN pa.is_primary = 1 THEN 20 ELSE 10 END           -- 行业主打
  + CASE WHEN b.brand_type = 2 THEN 10 ELSE 0 END             -- 自研优先
  ) AS match_score
FROM product p
JOIN product_property pp ON pp.product_id = p.product_id
JOIN brand b ON b.brand_id = p.brand_id
JOIN product_application pa ON pa.product_id = p.product_id
JOIN application_dict a ON a.app_id = pa.app_id
WHERE a.app_code = 'ELECTRONICS'
  AND pp.temp_long_max >= 300
  AND pp.chem_grade IN ('A','B')
  AND p.status = 1
ORDER BY match_score DESC
LIMIT 30;
```

## 4.3 一库多用复用架构（数据复用能力落地）

```
                    ┌────────────────────────┐
                    │   L2 统一主数据库（唯一录入源）│
                    └───────────┬────────────┘
                          统一查询API /api/products
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
  内部销售选型端            官网多行业垂直站          Catalog生成器
  is_published不限         is_published=1强制        继承销售端权限
  全字段可见               is_public=1文档才可下载    可选打包内部TDS
  含停产可替代品(status=2)  仅在售品                  仅在售品
```

- **一次录入**：产品在后台录一次，五维打标+TDS绑定完成即三端同步生效；
- **权限差异只在API参数层**控制（发布状态、文档可见性），不复制数据、不建第二套库；
- **前台改版零影响**：垂直站点增删、目录模板换版式，均不触碰数据层。

## 4.4 落地实施排期建议（轻量三阶段）

| 阶段 | 周期 | 交付物 |
|---|---|---|
| 一期：库+录入 | 3~4周 | 建表（模块2全部表）、后台录入端、映射表初始化、3M+ETIA自研两品牌数据先行入库打样 |
| 二期：检索+行业页 | 3周 | 统一查询API、内部销售筛选端、官网行业集合页模板上线（先开电子/冶金/医疗3站验证） |
| 三期：Catalog+全量 | 3~4周 | 定制Catalog生成器（PDF+H5）、其余8个品牌按SOP批量映射入库、全部行业站开通 |

---

## 附：方案与需求逐条对照自查

| 需求 | 落点 |
|---|---|
| 单品完整字段（基础信息+FBA三要素+资料绑定） | 模块2：product + product_property + product_document |
| 全品牌对齐3M标准、映射转换逻辑 | 模块3：五维基准 + brand_category_mapping + 11品牌规则明细 + 归一化规则 |
| 品牌/行业/耐温/耐化学/面材多条件交叉筛选 | 模块4.0 统一API + 复合索引SQL |
| 行业集合页单独调取 | 模块4.1：application_dict 驱动的数据化垂直站 |
| 客户工况自动匹配→专属电子Catalog | 模块4.2：硬过滤+评分排序+PDF/H5生成+条件快照存档 |
| 一次录入多场景复用 | 模块4.3：单库单API三端复用 |
| 极端工况字段适配（PI/高温PET/冶金超高温） | 模块2.3：T1~T6档位、峰值耐温+时长、灭菌/冻存/防静电等专项字段 |
| TDS/手册文件关联单品 | 模块2.4：多类型多版本文档表 + is_latest/is_public 管控 |
