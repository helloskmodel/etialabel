-- 特种标签统一产品数据库 轻量原型 schema (SQLite)
-- 生产环境按 docs/label-pim-database-design.md 平移至 MySQL 8

CREATE TABLE IF NOT EXISTS brand (
    brand_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_code    TEXT NOT NULL UNIQUE,
    brand_name_en TEXT NOT NULL,
    brand_name_cn TEXT,
    brand_type    INTEGER NOT NULL DEFAULT 1,  -- 1=进口代理 2=自研
    official_site TEXT,
    sort_order    INTEGER DEFAULT 100,
    status        INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS application_dict (
    app_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    app_code    TEXT NOT NULL UNIQUE,
    app_name_cn TEXT NOT NULL,
    app_name_en TEXT NOT NULL,
    sort_order  INTEGER DEFAULT 100,
    status      INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS facestock_dict (
    face_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    face_code    TEXT NOT NULL UNIQUE,
    face_name_cn TEXT NOT NULL,
    face_name_en TEXT NOT NULL,
    sort_order   INTEGER DEFAULT 100,
    status       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS adhesive_dict (
    adh_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    adh_code    TEXT NOT NULL UNIQUE,
    adh_name_cn TEXT NOT NULL,
    adh_name_en TEXT NOT NULL,
    sort_order  INTEGER DEFAULT 100,
    status      INTEGER NOT NULL DEFAULT 1
);

-- 原型阶段: 物性参数并入产品主表; 生产环境按设计文档拆 product_property 1:1 表
CREATE TABLE IF NOT EXISTS product (
    product_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_id         INTEGER NOT NULL REFERENCES brand(brand_id),
    model_no         TEXT NOT NULL,
    product_name_cn  TEXT,
    product_name_en  TEXT,
    face_id          INTEGER REFERENCES facestock_dict(face_id),
    adh_id           INTEGER REFERENCES adhesive_dict(adh_id),
    color            TEXT,
    print_method     TEXT,
    temp_long_min    INTEGER,
    temp_long_max    INTEGER,          -- 长期耐温上限℃ 核心筛选
    temp_peak_max    INTEGER,
    temp_tier        TEXT,             -- T1~T6 自动归档
    chem_grade       TEXT,             -- A/B/C/D
    thickness_um     INTEGER,
    feature          TEXT,             -- F 特性
    benefit          TEXT,             -- B 优势
    application_desc TEXT,             -- A 适用工况描述
    certification    TEXT,
    source_category_raw TEXT,          -- L0留存: 品牌原始分类原文
    source_url       TEXT,
    tds_url          TEXT,             -- 官方TDS外链(本地文件走 product_document)
    is_published     INTEGER NOT NULL DEFAULT 1,
    status           INTEGER NOT NULL DEFAULT 1,
    created_at       TEXT DEFAULT (datetime('now','localtime')),
    updated_at       TEXT DEFAULT (datetime('now','localtime')),
    UNIQUE (brand_id, model_no)
);
CREATE INDEX IF NOT EXISTS idx_product_face ON product(face_id);
CREATE INDEX IF NOT EXISTS idx_product_adh  ON product(adh_id);
CREATE INDEX IF NOT EXISTS idx_product_temp ON product(temp_long_max);

CREATE TABLE IF NOT EXISTS product_application (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL REFERENCES product(product_id) ON DELETE CASCADE,
    app_id     INTEGER NOT NULL REFERENCES application_dict(app_id),
    UNIQUE (product_id, app_id)
);

CREATE TABLE IF NOT EXISTS product_document (
    doc_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL REFERENCES product(product_id) ON DELETE CASCADE,
    doc_type   TEXT NOT NULL DEFAULT 'TDS',   -- TDS/BROCHURE/NOTES/MSDS/CERT
    doc_title  TEXT NOT NULL,
    file_path  TEXT NOT NULL,                 -- data/uploads/ 下相对路径
    language   TEXT DEFAULT 'en',
    version    TEXT,
    is_latest  INTEGER NOT NULL DEFAULT 1,
    is_public  INTEGER NOT NULL DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now','localtime'))
);
CREATE INDEX IF NOT EXISTS idx_doc_product ON product_document(product_id);
