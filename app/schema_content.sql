-- =====================================================================
-- 内容架构层 schema —— Feature / Benefit / Application Notes / Case Study
-- 结构化 + 关联化, 支撑双向导航与SEO:
--   品牌+产品 → 应用 ;  行业+应用 → 产品+品牌
-- 与主 schema.sql 并存(在其之后 executescript)。全部 IF NOT EXISTS, 可反复执行。
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. 细分应用 application —— 把原来 product.sub_application(文本)升级为实体
--    每个应用归属一个一级行业(application_dict), 承载 SEO 落地页
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS application (
    application_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    app_code         TEXT NOT NULL UNIQUE,       -- 稳定编码/URL slug, 如 auto-underhood
    name_cn          TEXT NOT NULL,              -- 发动机舱/车厢底
    name_en          TEXT,
    industry_id      INTEGER REFERENCES application_dict(app_id),  -- 所属一级行业
    summary_cn       TEXT,                       -- 一句话应用简介
    summary_en       TEXT,
    seo_title        TEXT,                       -- <title>
    seo_desc         TEXT,                       -- meta description
    seo_slug         TEXT,                       -- /applications/<slug>
    is_hot           INTEGER NOT NULL DEFAULT 0, -- 首页/列表 Hot 标
    sort_order       INTEGER DEFAULT 100,
    status           INTEGER NOT NULL DEFAULT 1
);

-- 产品 ↔ 细分应用 (多对多: 一个产品可用于多个应用; 一个应用有多款产品)
CREATE TABLE IF NOT EXISTS product_application_link (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id     INTEGER NOT NULL REFERENCES product(product_id) ON DELETE CASCADE,
    application_id INTEGER NOT NULL REFERENCES application(application_id) ON DELETE CASCADE,
    is_recommended INTEGER NOT NULL DEFAULT 0,   -- 是否该应用的主推产品
    UNIQUE (product_id, application_id)
);
CREATE INDEX IF NOT EXISTS idx_pal_app ON product_application_link(application_id);
CREATE INDEX IF NOT EXISTS idx_pal_prod ON product_application_link(product_id);

-- ---------------------------------------------------------------------
-- 2. 特性 Feature —— 结构化 + 可控词表(对应各品牌 "By Feature/Resistance")
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS feature_dict (
    feature_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    feat_code    TEXT NOT NULL UNIQUE,           -- HEAT/COLD/CHEM/ABRASION/TAMPER/STERILE...
    name_cn      TEXT NOT NULL,                  -- 耐高温 / 耐低温 / 耐化学...
    name_en      TEXT,
    category     TEXT,                           -- resistance / compliance / print / other
    sort_order   INTEGER DEFAULT 100
);

CREATE TABLE IF NOT EXISTS product_feature (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id   INTEGER NOT NULL REFERENCES product(product_id) ON DELETE CASCADE,
    feature_id   INTEGER REFERENCES feature_dict(feature_id),  -- 可空: 自由特性
    text_cn      TEXT,                           -- 该产品这条特性的具体描述(原文)
    text_en      TEXT,
    sort_order   INTEGER DEFAULT 100
);
CREATE INDEX IF NOT EXISTS idx_pf_prod ON product_feature(product_id);
CREATE INDEX IF NOT EXISTS idx_pf_feat ON product_feature(feature_id);

-- ---------------------------------------------------------------------
-- 3. 优势 Benefit —— 结构化(用户获得的收益, 与feature区分)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS product_benefit (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id   INTEGER NOT NULL REFERENCES product(product_id) ON DELETE CASCADE,
    text_cn      TEXT,
    text_en      TEXT,
    sort_order   INTEGER DEFAULT 100
);
CREATE INDEX IF NOT EXISTS idx_pb_prod ON product_benefit(product_id);

-- ---------------------------------------------------------------------
-- 4. 应用方案 Application Note —— 挂在应用上, 关联推荐产品
--    正文分段: 痛点/方案/推荐理由; status 控制草稿/发布
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS application_note (
    note_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    note_code      TEXT UNIQUE,                  -- AN-AUTO-001 格式
    title_cn       TEXT NOT NULL,
    title_en       TEXT,
    application_id INTEGER REFERENCES application(application_id),
    industry_id    INTEGER REFERENCES application_dict(app_id),
    problem_cn     TEXT,                         -- 痛点/工况挑战
    solution_cn    TEXT,                         -- 解决方案
    why_cn         TEXT,                         -- 选型推荐理由
    body_html      TEXT,                         -- 可选: 富文本正文
    seo_title      TEXT,
    seo_desc       TEXT,
    seo_slug       TEXT,                         -- /application-notes/<slug>
    is_hot         INTEGER NOT NULL DEFAULT 0,
    status         TEXT NOT NULL DEFAULT 'draft',-- draft / published / template
    created_at     TEXT DEFAULT (datetime('now','localtime')),
    updated_at     TEXT DEFAULT (datetime('now','localtime'))
);

-- 应用方案 ↔ 推荐产品 (多对多)
CREATE TABLE IF NOT EXISTS note_product (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id    INTEGER NOT NULL REFERENCES application_note(note_id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES product(product_id) ON DELETE CASCADE,
    sort_order INTEGER DEFAULT 100,
    UNIQUE (note_id, product_id)
);
CREATE INDEX IF NOT EXISTS idx_np_note ON note_product(note_id);
CREATE INDEX IF NOT EXISTS idx_np_prod ON note_product(product_id);

-- ---------------------------------------------------------------------
-- 5. 案例 Case Study —— 可挂在 产品 和/或 应用 上(两边都能列案例)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS case_study (
    case_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    case_code    TEXT UNIQUE,                    -- CS-ELEC-001
    title_cn     TEXT NOT NULL,
    title_en     TEXT,
    customer     TEXT,                           -- 客户/行业(可脱敏)
    industry_id  INTEGER REFERENCES application_dict(app_id),
    challenge_cn TEXT,                           -- 挑战
    solution_cn  TEXT,                           -- 方案
    result_cn    TEXT,                           -- 成效/量化结果
    body_html    TEXT,
    seo_title    TEXT,
    seo_desc     TEXT,
    seo_slug     TEXT,                           -- /case-studies/<slug>
    is_hot       INTEGER NOT NULL DEFAULT 0,
    status       TEXT NOT NULL DEFAULT 'draft',
    created_at   TEXT DEFAULT (datetime('now','localtime')),
    updated_at   TEXT DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS case_product (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id    INTEGER NOT NULL REFERENCES case_study(case_id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES product(product_id) ON DELETE CASCADE,
    UNIQUE (case_id, product_id)
);
CREATE TABLE IF NOT EXISTS case_application (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id        INTEGER NOT NULL REFERENCES case_study(case_id) ON DELETE CASCADE,
    application_id INTEGER NOT NULL REFERENCES application(application_id) ON DELETE CASCADE,
    UNIQUE (case_id, application_id)
);
CREATE INDEX IF NOT EXISTS idx_cp_prod ON case_product(product_id);
CREATE INDEX IF NOT EXISTS idx_cp_case ON case_product(case_id);
CREATE INDEX IF NOT EXISTS idx_ca_app  ON case_application(application_id);

-- =====================================================================
-- 双向查询能力(视图), 直接支撑SEO落地页与导航:
--   v_product_full  : 产品视角(品牌/五维/所属应用/方案数/案例数)
--   v_application_full: 应用视角(行业/产品数/品牌数/方案数/案例数)
-- =====================================================================
CREATE VIEW IF NOT EXISTS v_application_full AS
SELECT a.application_id, a.app_code, a.name_cn, a.name_en, a.is_hot, a.status,
       d.app_code AS industry_code, d.app_name_cn AS industry_cn,
       (SELECT COUNT(*) FROM product_application_link l WHERE l.application_id=a.application_id) AS product_cnt,
       (SELECT COUNT(DISTINCT p.brand_id) FROM product_application_link l
          JOIN product p ON p.product_id=l.product_id WHERE l.application_id=a.application_id) AS brand_cnt,
       (SELECT COUNT(*) FROM application_note n WHERE n.application_id=a.application_id) AS note_cnt,
       (SELECT COUNT(*) FROM case_application c WHERE c.application_id=a.application_id) AS case_cnt
FROM application a
LEFT JOIN application_dict d ON d.app_id=a.industry_id;
