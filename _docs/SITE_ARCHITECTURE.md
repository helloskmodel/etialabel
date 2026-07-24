# ETIA Label — Site Architecture & Content Blueprint (v2 · 唯一蓝图)

> 目的:把"网址 / 字数 / 页面结构 / 图片命名 / 四语言"一次性定死,取代仓库里三套互相打架的旧结构。
> 你们据此**写文案(四语言)** 和 **配 COS 图片**;我据此**重建单一数据驱动生成器**。
> Single source of truth. 若与 `CONTENT.md` / `PAGES.md` / 代码冲突,**以本文件为准**。

Status legend: 🔒 客户已锁定 · ✏️ 草稿 · ⬜ 待写 · 🖼 需配图

---

## 0. 铁律(承接 WORKING_AGREEMENT)
1. **唯一事实来源**:内容进 `data/`,不进 `.py`。本文件定结构,`data/` 填内容。
2. **绝不编造**:只用真实型号/参数;缺口标 `待核实 / Contact ETIA`,不猜。
3. **字数=目标预算**,给文案参考(按语言,中日韩按字符、英越泰按词,量级一致即可)。
4. **图片语言无关**:一套图四语言共用;命名全小写 ASCII、连字符、无空格无中文。

---

## 1. 技术架构(一套数据驱动生成器)
```
_build/
  build.py              # 唯一入口
  render/
    shell.py            # page()/nav/footer/全局CSS(从 gen_heatproof 抽出)
    pages.py            # 每种页面类型一个模板函数
    images.py           # 唯一图片配置:IMAGE_BASE + img(类别, slug)
  data/
    site.json           # 导航/公司信息/全局串(四语言)
    industries.json     # 行业 + 应用叶子
    materials.json      # 材料
    products.json       # 产品(结构相同,文案四语言)
    notes/<slug>.<lang>.md   # 应用笔记(长文)
    cases/<slug>.<lang>.md   # 案例(长文)
```
删除所有孤立生成器与数据(gen_en / gen_steel / gen_wirecable / gen_healthcare / gen_pi / gen_prodline / gen_notes / *_data …)。

---

## 2. URL 结构(定死,flat ≤3 层,SEO 友好)

四语言:英文根路径 = x-default;其余加前缀。
```
EN  /                 (x-default,源语言)
ZH  /zh/              (旧 /cn/ → 301 到 /zh/)
TH  /th/
VI  /vi/
```
每页输出**完整互相 hreflang**(en/zh/th/vi + x-default)。某语言缺页 → 自动回退英文。

| 路径 | 说明 |
|---|---|
| `/` | 首页 |
| `/industries/` | 行业总览 hub |
| `/industries/<industry>/` | 行业页(L1) |
| `/industries/<industry>/<application>/` | 应用叶子(L2)→ 汇聚产品 |
| `/applications/` · `/applications/<slug>/` | 按工艺/应用 路径 |
| `/materials/` · `/materials/<slug>/` | 按基材 路径 |
| `/products/` · `/products/<sku>/` | 产品总览 + 产品详情(PDP,三路径终点) |
| `/application-notes/` · `/application-notes/<slug>/` | 工程应用笔记 |
| `/case-studies/` · `/case-studies/<slug>/` | 案例 |
| `/about/` · `/service/` · `/contact/` | 公司 / 服务 / 联系 |
| `/privacy/` `/cookies/` `/terms/` | 法律页 |

> 取代旧的 `/products/by-industry/…` 与 `/industries/<x>-labeling-solutions/` 两套。slug 全小写英文连字符。

---

## 3. 页面清单(目标态 · 状态标注)

| 类型 | 数量(目标) | 已有素材 | 状态 |
|---|---|---|---|
| 首页 | 1 | 客户锁定 EN+ZH 文案 | 🔒✏️ |
| 行业 hub | 1 | — | ✏️ |
| 行业页 L1 | 8(电子/PCB·汽车·钢铁金属陶瓷·医疗·线缆·户外能源·… 待你确认清单) | Automotive/PCB/Steel/Medical/Cable 有草稿 | ✏️🖼 |
| 应用叶子 L2 | 按行业展开(先每行业 3–6 个) | 部分 | ⬜ |
| 材料页 | 6(PI/PET/陶瓷金属高温/低温耐候/阻燃ESD/合成纸) | Polyimide 有 | ✏️ |
| 产品 PDP | 按真实型号(先上有 TDS 的) | catalog 数据 | ⬜ |
| 应用笔记 | 现有若干 | ESD-PCB/Tire/VIN/Catheter 有 | ✏️ |
| 案例 | 现有若干 | 渗碳工装追溯 有 | ✏️ |
| 公司/服务/联系/法律 | 各 1 | service/contact/legal 有 | ✏️ |

> **需要你定**:L1 行业最终清单 + 本次真正上线的行业/材料/产品范围(其余标"待核实"占位,不编造)。

---

## 4. 每种页面的内容结构 + 字数预算(每语言)

### 4.1 首页 `/`  🔒(结构已锁定)
顺序:Hero → 蓝色服务条(✓) → Why ETIA → What We Offer → 合作品牌 → 联系 CTA
| 区块 | 内容 | 字数(每语言) |
|---|---|---|
| Hero | 眉题 + 主标题 + 短描述 + 2 按钮 | 眉题≤6 · 标题3–6 · 描述15–30 |
| 服务条 | 4 项 ✓ | 每项 2–4 |
| Why ETIA | 标题+引言+ Understand/Source/Develop/Support 4 动词 | 引言25–40;每动词15–25 |
| What We Offer | 3 卡(材料/应用工程/加工供应) | 每卡 标题3–5 + 15–25 |
| 合作品牌 | 1 句 + logo 墙 | 15–25 |
| 联系 CTA | 标题 + 1 句 | 标题5–8 + 12–20 |
| **合计可见文案** | | **≈ 300–450 词** |

### 4.2 行业 hub `/industries/`
Hero(H1 + 引言25–35)· 8 行业卡(每卡 标题 + 15–25)· 说明段 60–100 · CTA。**合计 ≈ 250–400 词**

### 4.3 行业页 L1 `/industries/<industry>/`
| 区块 | 字数 |
|---|---|
| Hero(H1 5–9 + 引言 20–35) | — |
| 行业挑战/引入 | 80–130 |
| 应用叶子网格(4–8 卡,每卡标题+15–25) | — |
| 推荐产品(3–6,数据驱动,少文案) | 每条≤15 |
| 案例引流 | 25–40 |
| FAQ(3–5 组,Q 8–12 / A 30–50) | — |
| CTA | 固定 |
| **合计** | **≈ 450–750 词** |

### 4.4 应用叶子 / 应用页 `/…/<application>/` · `/applications/<slug>/`
Hero+引言20–30 · What/Why 90–150 · 需求表(结构化)· 匹配产品2–6 · FAQ 2–4。**合计 ≈ 350–550 词**

### 4.5 材料页 `/materials/<slug>/`
Hero+引言20–30 · 材料特性 80–120 + 属性表 · 典型产品/用途。**合计 ≈ 300–450 词**

### 4.6 产品详情 PDP `/products/<sku>/`
H1+一句descriptor · **规格表(核心,结构化)** · 描述 50–90 · 所属行业/应用链接 · TDS 下载 · FAQ 2–3。**文案 ≈ 150–300 词**(规格驱动)

### 4.7 应用笔记 `/application-notes/<slug>/`  (工程 Standard V1.0,7 段)
Hero · 背景 · 挑战 · 方案 · 验证/数据 · 结果 · 选型建议。**≈ 600–1000 词**

### 4.8 案例 `/case-studies/<slug>/`
挑战 / 方案 / 结果 三段 + 参数表。**≈ 300–500 词**

### 4.9 公司/服务/联系/法律
About 250–450 · Service 300–500(4 承诺)· Contact 表单+4 地点(固定)· 法律页按模板。

---

## 5. 图片架构(你按此配 COS)

### 5.1 命名规范
- **单一配置**:`images.py` 里一个 `IMAGE_BASE`(COS 域名)+ `img(类别, slug)`;URL 全部计算,不手贴。
- 全小写 ASCII、连字符、无空格无中文;**一套图四语言共用**。
- 只用**永久公开 URL**,绝不用 `?q-sign-…` 预签名链接(1 小时过期)。
- 缺图 → 统一品牌灰渐变占位,不再静默 `this.remove()`。

### 5.2 COS 目录树(镜像 `/img/`)
```
/img/
  brand/etia-logo.svg          # + etia-logo.png 兜底
  brand/<partner>.png          # polyonics / ys-tech / flexcon / computype (透明)
  home/hero.jpg                # 或 hero-1..6.jpg(应用马赛克)
  banners/<page>.jpg           # 各页头 banner
  industries/<industry>.jpg    # 行业页 hero(建议 21:9)
  industries/<industry>/<application>.jpg   # 应用卡缩略(4:3)
  materials/<slug>.jpg
  products/<sku>.jpg           # 产品图(1:1)
  cases/<slug>/<n>.jpg         # 案例图(16:9)
  service/<slug>.jpg           # 服务图(4:3)
```

### 5.3 各页所需图(★=上线必需 ○=可选)
| 页面 | 图片 | 建议比例 |
|---|---|---|
| 首页 | ★ hero(1 张或 5–6 张马赛克)· ★ 合作品牌 logo ×5 · ○ What We Offer 线性图标 | 16:9 / 透明PNG |
| 行业 hub | ○ 每行业缩略 ×8 | 4:3 |
| 行业页 L1 | ★ hero ×1 · ○ 应用卡缩略 | 21:9 / 4:3 |
| 应用叶子 | ○ 场景图 ×1 | 16:9 |
| 材料页 | ○ 材料/卷料图 | 4:3 |
| 产品 PDP | ○ 产品图 ×1 | 1:1 |
| 案例 | ★ 现场图 ×1–3 | 16:9 |
| 服务页 | ○ 承诺配图 ×4 | 4:3 |

---

## 6. 四语言规则
- 字段级四语言(`{en,zh,th,vi}`),缺失回退 EN → **英文可先整站上线,中/泰/越陆续补,不用等齐**。
- 长文(笔记/案例)按语言分文件:`data/notes/<slug>.en.md` / `.zh.md` / `.th.md` / `.vi.md`。
- 中文迁 `/zh/`,旧 `/cn/` 做 301。
- 每页 hreflang 输出全部已存在语言 + x-default。

---

## 7. 你现在要定/给我的
1. **L1 行业最终清单**(上面 8 个是草案)+ 本次上线范围。
2. **四语言文案**:按第 4 节字数预算填 `data/`(或先给 EN)。
3. **COS 图片**:按第 5 节命名上传。
4. 确认默认:语言=英文先上/其余回退 · 中文=`/zh/`+301 · 图片=COS。

> 有出入直接改本文件对应行——这就是唯一改动入口。
