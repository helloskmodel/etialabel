# 部署说明 · Deploy Guide

把这个静态网站跑起来看真实效果。**看整站不需要域名** —— Vercel 会给一个免费的
`xxxx.vercel.app` 网址,整站可点击、图片能加载、四语言切换器正常。域名是最后一步。

- 站点类型:纯静态 HTML(无需构建 / no build step)
- 配置文件:`vercel.json`(clean URLs + trailingSlash + 301 重定向,已就位)
- 分支:`claude/etia-label-website-dev-tjsqxg`

---

## 方式 A · Vercel(推荐,约 3 分钟,免费网址)

1. 打开 **https://vercel.com** → 用 **GitHub** 账号登录。
2. **Add New… → Project** → **Import** 仓库 `helloskmodel/etialabel`。
   - 如果没看到仓库:点 *Adjust GitHub App Permissions*,授权访问该仓库。
3. 在 Import 配置页:
   - **Framework Preset**: `Other`
   - **Root Directory**: `./`(默认)
   - **Build Command**: 留空(关掉 Override,或填 `echo skip`)
   - **Output Directory**: 留空(默认根目录)
   - **Install Command**: 留空
4. **Deploy** → 等 20–40 秒 → 得到 `https://etialabel-xxxx.vercel.app`。
   点开就能逛整站(首页四语言、六大行业、产品页、严选中心)。

### 让它部署 dev 分支的内容
Vercel 默认部署仓库的默认分支。两种做法任选:
- **最简单**:每个分支都会自动生成一个 *Preview* 部署。进 Vercel 项目 →
  **Deployments** → 找到 `claude/etia-label-website-dev-tjsqxg` 的部署 → 打开它的
  预览网址即可。
- **设为正式**:项目 **Settings → Git → Production Branch** 改成
  `claude/etia-label-website-dev-tjsqxg` → 重新 Deploy。

> 之后每次往这个分支 push,Vercel 会自动重新部署,网址不变。

---

## 方式 B · 绑定域名(等你确定域名后,可选)

`.vercel.app` 网址随时能用;要换成正式域名时:

1. Vercel 项目 → **Settings → Domains → Add** → 输入域名
   (如 `www.etialabel.com`,或子域名 `label.etiatech.com`)。
2. Vercel 会给出需要添加的 DNS 记录,例如:
   - 顶级域 `@` → **A** 记录 `76.76.21.21`
   - `www` 或子域 → **CNAME** `cname.vercel-dns.com`
3. 到你的 DNS 面板**加这一条记录**即可 —— 不要动现有域名的 nameserver
   (以免影响 etiatech.com 老站/邮箱)。以 Vercel 后台实际给出的值为准。

> 注意:代码里 canonical / hreflang / sitemap 目前写死为 `https://www.etialabel.com`。
> 若最终用别的域名,告诉我,我把生成器里的 `SITE` 改掉再重新生成。

---

## 方式 C · Cloudflare Pages(备选,同样免费根路径托管)

若用 Cloudflare:Pages → Connect to Git → 选仓库与分支 → Framework preset `None`
→ Build command 留空 → Build output directory `/` → Deploy。同样得到免费
`*.pages.dev` 网址。

> 不建议用 GitHub Pages 的“项目站点”:它会把站点放在 `/etialabel/` 子路径下,
> 而本站用的是根路径绝对链接(`/products/...`),会导致内链失效 —— 除非绑定自定义域名。

---

## 部署前自检(可选)
仓库里有构建与校验脚本:

```bash
python3 _build/build.py       # 重新生成整站(462+ 页,四语首页)
python3 _build/validate.py    # 校验:断链 / hreflang / 温度分离 / 中文泄漏 —— 应为 0 errors
```

有问题随时找我。
