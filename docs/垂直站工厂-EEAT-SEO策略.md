# 垂直专业站工厂 + Google EEAT SEO 策略

> 一个数据库(924款产品 + 应用/方案/案例内容层)→ 孵化多个"小而美"利基站。
> 复用 etiatech.com 的架构逻辑,针对细分行业/材料做独立SEO域,冲 Google 自然流量。
> 生成器:`scripts/build_microsite.py`,已产出 4 个垂直站(1个完整+3个骨架)。

## 一、架构复用:etiatech.com 逻辑 → 本库数据

| etiatech.com 页面逻辑 | 本库对应 | 已就绪 |
|---|---|---|
| Product = 品牌 + 技术 + 详情(Feature/Benefit/Application) | product + 面材/胶水 + product_feature/benefit + product_application_link | ✅ |
| Application = 行业 + 子应用 + 方案 + 效益 + 技术亮点 + 推荐产品 | application + application_note(痛点/方案/理由) + note_product | ✅(骨架,正文待填) |
| EEAT: 20年经验 + 验证案例 + 应用咨询 | Organization schema + case_study + 溯源透明声明 | ✅ |

## 二、四个垂直站(生成器已内置配置)

| 站点 | 覆盖产品 | 定位 | slug | 状态 |
|---|---|---|---|---|
| **聚酰亚胺高温标签** | 107(跨8品牌) | 材料垂直,权威在"跨品牌横向选型" | polyimide-labels | ✅ 完整(含技术科普+FAQ) |
| 汽车标签 | 426 | 行业垂直,场景细分强 | automotive-labels | 骨架(待补文案) |
| 钢铁冶金追溯 | 29 | 极端高温利基,竞争少易冲排名 | steel-metallurgy-labels | 骨架 |
| 医药与医疗 | 95 | 合规+冻存,高价值 | medical-pharma-labels | 骨架 |

生成命令:`python3 scripts/build_microsite.py polyimide`(输出自包含单HTML,直接传COS/CloudBase)。
新增垂直站 = 在 `VERTICALS` 加一段配置(过滤条件 + 文案 + 配色),无需改模板。

## 三、Google EEAT 落地(每个站都内置)

EEAT = Experience 经验 / Expertise 专业 / Authoritativeness 权威 / Trustworthiness 可信。
Google 对 YMYL 及专业采购类内容尤其看重。本站的落地方式:

| 要素 | 站内实现 |
|---|---|
| **Experience 经验** | 顶部"20年工业标签选型经验"positioning;未来接入真实客户案例(case_study) |
| **Expertise 专业** | "为什么选聚酰亚胺"技术科普段(温度/尺寸稳定/阻燃/宽温域)、选型逻辑、FAQ答疑 |
| **Authoritativeness 权威** | **核心差异化**:跨8品牌107款横向聚合(而非单一代理),品牌分布条 + 按应用筛选 |
| **Trustworthiness 可信** | 每款直连官方TDS可核验;"官网未公布参数一律留空,不臆造"透明声明;页脚org信息 |

**技术SEO(已内置代码):**
- `<title>` / `meta description` / `canonical` / Open Graph 每站独立且含关键词
- **JSON-LD 结构化数据**:Organization + BreadcrumbList + ItemList(产品) + FAQPage
  → 帮助 Google 出富媒体结果(FAQ折叠、面包屑、产品列表)
- 语义化 HTML(h1/h2 层级、section 分区、details/summary FAQ)
- 移动端自适应、快速加载(单文件内嵌,无外部请求)

## 四、上线与增长路径

1. **域名策略**:主站 + 子域/子目录各承载一个垂直站,例如
   `polyimide.etiatech.com` 或 `etiatech.com/polyimide-labels`(子目录更利于主域权重累积)。
2. **内容深化(EEAT关键)**:把 application_note / case_study 的正文填实——
   每个细分应用一篇"痛点→方案→选型→成效",这是 Google 判断"专业深度"的核心。
   骨架和推荐产品已自动生成,只需补专业正文。
3. **内链**:垂直站 ↔ 主商城 ↔ 产品详情页,用 product_application_link 的双向关系自动生成内链,
   传递权重、延长停留。
4. **持续更新**:数据/内容更新后一条命令重新生成,`Last-Modified` 更新利于重新抓取。
5. **外链与信号**:发布真实TDS对比、选型白皮书,吸引行业引用(权威度)。

## 五、下一步建议(按ROI排序)

1. 先把**聚酰亚胺站**部署上线(已完整),验证 SEO 收录与转化。
2. 为**钢铁冶金**站补文案——竞争最少、极端高温是ETIA强项,最易冲到首页。
3. 把 application_note 正文逐步填实(参考贵司62篇应用方案模式),持续喂 EEAT。
4. 汽车/医疗站文案量大,可分阶段补。
