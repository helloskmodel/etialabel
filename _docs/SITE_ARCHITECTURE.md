# ETIA Label — Site Architecture & Content Blueprint (v2 · 唯一蓝图)

> 唯一事实来源。与 `CONTENT.md` / `PAGES.md` / 代码冲突时**以本文件为准**。
> 你据此写四语言文案 + 配 COS 图片;我据此重建单一数据驱动生成器。
> 承接 WORKING_AGREEMENT:内容进 `data/` 不进 `.py`;**绝不编造**,缺口标「待核实」;字数=文案预算。

_定稿于 2026-07-24,客户逐条确认。_

---

## 1. 技术架构(一套数据驱动生成器)
```
_build/
  build.py                     # 唯一入口
  render/ shell.py pages.py images.py
  data/ site.json industries.json environments.json materials.json products.json
        notes/<slug>.<lang>.md
```
删除所有孤立生成器与数据(gen_en / gen_steel / gen_wirecable / gen_healthcare / gen_pi / gen_prodline / gen_notes / *_data …)。

## 2. 四语言
| 语言 | 路径 | 策略 |
|---|---|---|
| English | `/`(x-default) | 源语言,先完整上线 |
| 中文 | `/zh/`(旧 `/cn/`→301) | 已有内容 |
| ไทย | `/th/` | 翻译到位一页发一页,缺页**回退英文** |
| Tiếng Việt | `/vi/` | 同上 |

字段级四语言,缺失回退 EN → 英文先整站上线,其余陆续补。每页输出完整互相 hreflang。

## 3. URL 结构(定死)
```
/                                 首页
/products/                        产品总览
/products/by-industry/            按行业(① 排第一)
/products/by-industry/<ind>/      行业落地页
/products/by-environment/         按环境(高温/深冷/化学/户外…)
/products/by-environment/<env>/
/products/by-material/            按基材(PI/PET/陶瓷金属…)
/products/by-material/<mat>/
/products/item/<line>/            产品线页(600字)   ┐ 三路径共用终点
/products/item/<sku>/             单品页(300字)     ┘
/application-notes/<slug>/        应用笔记
/about/  /service/  /contact/     公司/服务/联系
/privacy/ /cookies/ /terms/       法律
```
**三条路径同一套设计,最终都落到同一个产品页。** Cases 第一期不上。

## 4. 本期 6 个行业(按序)
1. **PCB**  `/products/by-industry/pcb/`  — ✅ 内容已给
2. **Automotive & Tire**  `/products/by-industry/automotive-tire/`  — ✅ 内容已给
3. **Wire & Cable**  `/products/by-industry/wire-cable/`  — ⬜ 待给
4. **Outdoor & Energy**  `/products/by-industry/outdoor-energy/`  — ⬜ 待给
5. **Medical & Pharmacy**  `/products/by-industry/medical-pharma/`  — ⬜ 待给
6. **Steel & Ceramics**  `/products/by-industry/steel-ceramics/`  — ⬜ 待给

> 待给的 4 个先上「内容整理中 / coming soon」占位(保持导航完整),**不编造参数**;内容到位即填。改一个数据标记即可隐藏/上线。

## 5. 行业落地页结构(By Industry / Environment / Material 通用)
| 顺序 | 区块 | 说明 | 字数(每语言) |
|---|---|---|---|
| 1 | **Hero** | "<行业> Labelling Solutions" + 一句 Slogan,**行业 Banner 背景** | 标题+slogan |
| 2 | **Part 1 行业介绍** | 该行业标识挑战 + ETIA 方案概述 | **300–400** |
| 3 | **产品列表 FlexCon Bar** | 横向 Tab 轮播(‹ › + 药丸 Tab + 选中蓝下划线),每 Tab=产品,显示 图+标题+说明。**两层分类的行业:Bar 上方加一排「一级」按钮**(一级切换,Bar 为二级) | Tab 说明各 15–30 |
| 4 | **用途卡 ×1** | Label 主要用途(**一张卡**) | 40–80 |
| 5 | **产品卡 1–3 张并列** | 对应产品介绍卡,点击→产品页 | 每卡 15–30 |

## 6. 产品页 = 两种 Landing(二选一,都含图 + 含 TDS 下载)
| 类型 | URL | 字数 | 用于 |
|---|---|---|---|
| 产品线页 | `/products/item/<line>/` | **600** | 一个产品家族/系列 |
| 单品页 | `/products/item/<sku>/` | **300** | 单个型号 |

内容:规格表 + 描述 + 产品图 + TDS 下载 + 所属行业/环境/材料链接。缺参数标「待核实」。

## 7. 应用笔记 `/application-notes/<slug>/`
**按产品来写**,每篇 **600 字**;带 **行业 / 材料 / 环境** 标签;**末尾附产品链接**。
已有:ESD-PCB、轮胎胎唇、VIN、导管UV固化。

## 8. 首页 `/`(结构已锁定,客户已给 EN+ZH)
Hero → 蓝色服务条(✓) → Why ETIA → What We Offer → 合作品牌 → 联系CTA。约 300–450 词。

## 9. 图片规范(你配 COS)
- **单一配置** `images.py`:`IMAGE_BASE` + `img(类别, slug)`,URL 全部计算。
- 命名全小写 ASCII、连字符、无空格无中文;**一套图四语言共用**;只用永久公开 URL(不用 `?q-sign-` 预签名)。
- **Banner vs 4:3**:首页 + 6 个行业页用 **Banner**;产品页、By-Environment/Material 内页用 **4:3**。
- **性能**(导出时执行):
  - 格式 **WebP**;每张带固定宽高。
  - Banner:宽 ≤1920px,≤**200KB**,首屏图**不 lazy-load**。
  - 4:3:宽 ≤1000px,≤**120KB**,首屏以下 lazy-load。
- 缺图 → 统一品牌灰渐变占位(不再静默移除)。
- COS 目录树:
```
/img/brand/etia-logo.svg  /img/brand/<partner>.png
/img/banners/home.jpg  /img/industries/<ind>.jpg           # Banner
/img/products/<sku>.jpg  /img/uses/<slug>.jpg  /img/materials/<mat>.jpg  # 4:3
```

## 10. 落地顺序
1. 重建生成器骨架(render/ + images.py)+ 删孤立脚本。
2. 建三路径 + 行业页/产品页/笔记模板。
3. 灌 **PCB + Automotive** 真实数据上线;其余 4 行业占位。
4. `/zh/` 迁移 + 四语言接线;th/vi 回退英文。
5. 通过 validate.py(0 断链/0 中文泄漏),推送到稳定 URL。
