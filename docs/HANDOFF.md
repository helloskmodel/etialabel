# 交接文档 — 新会话从这里继续

> 本文档供新的 Claude Code 会话（或任何接手的开发者）快速上手。
> 上一会话完成时间：2026-07-03

## 一、项目是什么

ETIA（深耕工业特种标签20年，代理3M/Brady/LINTEC/Avery/Polyonics/YS Tech/Computype/Flexcon/Mactac/Mark Tech + 自研品牌）的**统一产品数据库**：
把近10个品牌互不兼容的分类体系全部对齐 **3M五维标准**（行业应用Application / 面材Facestock / 胶水Adhesive / 耐温 / 耐化学），实现一站式选型查询、TDS资料归档、行业集合页、客户定制Catalog生成。

## 二、已完成（都在本分支 `claude/label-pim-database-design-r3rqds`）

| 成果 | 位置 |
|---|---|
| 完整数据库设计方案（4模块：架构/全表字段/映射规则/两大功能流程） | `docs/label-pim-database-design.md` ←**先读这个** |
| 可运行系统：Flask+SQLite，查询口子+Excel导入口子+TDS上传绑定 | `app/`（`python app/app.py` 即跑，见 `README.md`） |
| 24款主流型号种子数据（AI知识初稿，全部待核实） | `data/samples/seed_知识初稿_待核实.xlsx` |
| 建库脚本（首次启动自动执行） | `app/schema.sql` |

系统功能已端到端测试通过：Excel导入（品牌+型号判重，重复导入=更新）、四维交叉筛选（品牌/Application/Facestock/Adhesive + 耐温≥N℃ + 耐化学等级 + 关键词）、结果导出Excel、TDS文件上传绑定单品与回下载。

## 三、未完成 = 新会话的首要任务：抓取真实产品数据

上一会话网络策略为 Trusted（白名单），无法访问品牌官网，已要求用户将环境
Network access 改为 **Full**。开工前先自检网络：

```bash
curl -sS -o /dev/null -w "%{http_code}" --cacert /root/.ccr/ca-bundle.crt https://www.3m.com/
# 200/301 = 网络已放开; 000/403 = 仍被防火墙拦, 停下来告知用户改环境设置
```

### 目标1：3M 标签目录（约197个产品）——分类基准，最优先

- 入口：`https://www.3m.com/3M/en_US/p/c/labels/`
- 已探明技术情报：该目录是 **Oracle Endeca/ATG Guided Search** 架构。翻页参数：`No`=起始偏移、`Nrpp`=每页条数、`N`=facet维度ID（多值用`+`连接）。筛选面板的 Application 计数（Automotive 145 / Electronics 143 / Manufacturing 193 / Transportation 150 等）即 Endeca refinement counts
- 抓取路径：① 首页HTML里找内嵌JSON（`window.__`、`application/ld+json`）与 assembler/JSON 端点；② 递增`No`翻页拿全清单；③ 兜底方案：逐产品详情页（`/p/d/...`）解析 JSON-LD Product 块
- 注意站点有 Akamai 防护，带浏览器UA；必要时用 Playwright（chromium 在 `/opt/pw-browsers/chromium`，勿运行 playwright install）

### 目标2：Brady 材料选型器（约103种标签材料）

- 入口：`https://d37iyw84027v1q.cloudfront.net/Common/msapp/index.html`（大小写 common 均可）
- 这是静态托管的选型小程序，数据大概率在同目录 JS bundle 引用的 `.json` 文件里：下载 index.html → 找 JS → grep 出数据文件URL → 一次拿全
- 材料为 B-系列编号（B-423、B-717、B-727、B-8544……）

### 目标3（次优先）：其余品牌

LINTEC medical（https://www.lintec-global.com/products/label/labelstocks/applications/medical/）、
Avery（汽车/Medical/Pharmacy线）、Polyonics、Flexcon（汽车/Healthcare）、
Mactac（https://www.mactac.com/labelsupply）、Computype、YS Tech、Mark Tech。

## 四、数据入库规则（必须遵守）

1. 清洗对齐按 `docs/label-pim-database-design.md` 模块3执行：五维必填；耐温档位T1~T6按长期耐温上限归档（≤80/120/180/260/500/以上）；耐化学A/B/C/D（耐强溶剂浸泡=A、耐IPA等擦拭=B、仅耐水油=C、无=D）
2. 品牌原始分类原文存 `source_category_raw`，产品源页面URL存 `source_url`——不可省略，用于人工复核
3. **官网没写的参数留空，绝不编造**
4. 入库方式：生成Excel（列结构参照 `data/samples/seed_知识初稿_待核实.xlsx` 或 /admin 页模板），启动系统后 POST 到 `/admin/import`，或直接让用户在网页上传。原始抓取JSON/HTML 存 `data/raw/`（已gitignore，大文件勿入git）
5. 种子数据里的24款是AI知识初稿：抓到同型号官方数据后直接覆盖（导入自动判重更新）

## 五、用户沟通须知

- 用户是行业专家但**非程序员**：汇报用大白话，多截图（Playwright截图后 SendUserFile），少贴代码
- 用户高度在意 token 花销：探路/翻页等脏活派后台子代理并行干，主对话只留结论
- 用户可能从 claude.ai 网页版Chat收集数据后粘贴/传文件过来：任何格式（表格文字/Excel/CSV）都解析入库，同样遵守第四节规则
- 所有成果 commit + push 到本分支；未经用户同意不开PR、不合并main

## 六、后续路线图（数据入库后）

1. 全品牌数据复核工作流（confidence标记 + 待复核清单导出）
2. 行业集合页（方案模块4.1）
3. 客户定制Catalog生成器：工况表单→匹配评分→PDF/H5（方案模块4.2）
4. 生产化部署：SQLite→MySQL8 + 对象存储 + 登录鉴权
