# 内容架构说明 —— Feature / Benefit / Application Notes / Case Study + SEO

> 目标:把"特性、优势、应用方案、案例"从散落文本升级为**结构化实体 + 关联**,
> 实现双向导航(品牌+产品↔行业+应用),天然支撑 SEO 落地页。
> 已建库并从现有 924 款产品迁移数据。定义在 `app/schema_content.sql`,
> 迁移脚本 `scripts/build_content_architecture.py`(幂等,可反复跑)。

## 一、实体关系(ER)

```
        品牌 brand
          │ 1
          │ *
        产品 product ───────< 结构化特性 product_feature >──── 特性词表 feature_dict
          │  │  │                (耐高温/耐低温/耐化学/防篡改/UL…可筛可SEO)
          │  │  └──────────< 结构化优势 product_benefit
          │  │
          │  └──────────────< 应用方案 application_note >──── note_product ──> 产品(推荐)
          │                        │
          │  ┌─────────────────────┘ (方案挂在应用上, 也回指产品)
          │  │
   product_application_link (产品 ↔ 细分应用, 多对多)
          │  │
          * │ *
        细分应用 application ──(属于)── 行业 application_dict
             │  │
             │  └──────────< 应用方案 application_note (每个应用 N 篇方案)
             │
             └──< case_application >── 案例 case_study ──< case_product >── 产品
                                          (案例可同时挂 应用 与 产品)
```

一句话:**每个产品**有 特性/优势/应用方案/案例;**每个应用**有 产品/方案/案例。

## 二、表清单(新增 11 张)

| 表 | 作用 | 现有数据迁移量 |
|---|---|---|
| `application` | 细分应用实体(原 product.sub_application 升级) | 33 个应用 |
| `product_application_link` | 产品 ↔ 细分应用(多对多) | 393 条关联 |
| `feature_dict` | 特性可控词表(15类:耐高温/低温/化学/磨/UL/阻燃…) | 15 |
| `product_feature` | 产品结构化特性(可带词表tag) | 3463 行(704 带tag) |
| `product_benefit` | 产品结构化优势 | 1445 行 |
| `application_note` | 应用方案(痛点/方案/推荐理由 + SEO) | 33 样板(正文待填) |
| `note_product` | 方案 ↔ 推荐产品 | 102 条 |
| `case_study` | 案例(挑战/方案/成效 + SEO) | 33 样板(正文待填) |
| `case_product` | 案例 ↔ 产品 | — |
| `case_application` | 案例 ↔ 应用 | — |
| `v_application_full`(视图) | 应用视角聚合(产品数/品牌数/方案数/案例数) | — |

> 样板(status=`template`)只建了骨架与**真实推荐产品**(按 TDS/耐温匹配前 5),
> **正文一律留空**——痛点/方案/成效由产品工程师填写或从品牌应用手册整理,不编造。
> 状态机:`template`(自动骨架) → `draft`(编辑中) → `published`(对外可见/进SEO)。

## 三、SEO 与双向导航(核心价值)

同一套关联,支撑四类落地页与两个方向的检索:

| 落地页类型 | URL 规划 | 数据来源 | 满足的搜索意图 |
|---|---|---|---|
| 产品页 | `/products/{brand}/{model}` | product + feature/benefit + 所属应用 + 方案/案例 | "3M 7812 用在哪" |
| 应用页 | `/applications/{slug}` | application + 该应用全部产品(跨品牌) + 方案/案例 | "PCB 标签 选什么" |
| 方案页 | `/application-notes/{slug}` | application_note + 推荐产品 | "回流焊 标签 方案" |
| 案例页 | `/case-studies/{slug}` | case_study + 关联产品/应用 | "某厂 冻存 标签 案例" |

**方向一**(品牌+产品 → 应用):`product → product_application_link → application`
→ 产品页自动列出"本产品可用于哪些应用",每个应用可点进应用页。

**方向二**(行业+应用 → 产品+品牌):`application → product_application_link → product → brand`
→ 应用页自动列出"本应用有哪些产品、覆盖哪些品牌",可按五维再筛。

SEO 字段(`seo_title/seo_desc/seo_slug`)在 application / application_note / case_study
三类实体上都预留,发布时填写;`is_hot` 控制首页/列表精选位。

## 四、下一步(内容与前台)

1. **前台页面**:在商城基础上加"应用方案 / 案例"两个入口(卡片列表 + 详情),
   数据已就绪,推荐产品自动带出。
2. **内容录入**:管理端加 Application Note / Case Study 的编辑表单(填痛点/方案/成效、
   勾选推荐产品、设 SEO 与发布状态)。
3. **填充正文**:按你们参考站(62 篇应用方案)的模式,逐个应用补写专业内容;
   骨架和编码(AN-AUTO-001 / CS-ELEC-001)已生成,填空即可。
4. **静态化输出**:`build_web_catalog.py` 可扩展为一并导出应用/方案/案例页,
   生成带正确 `<title>/<meta>` 的静态 HTML,直接吃 SEO。
