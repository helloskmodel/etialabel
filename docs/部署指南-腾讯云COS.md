# 把产品商城部署到你自己的腾讯云COS(5分钟,免代码)

部署后你会得到一个**国内秒开**的正式网址,发给同事/客户都能直接打开。

## 一、准备文件
产品商城就是一个文件:`etia-shop.html`(Claude已发你;或在仓库运行
`python3 scripts/build_web_catalog.py` 重新生成,数据更新后同理)。
**把它改名为 `index.html`**。

## 二、控制台三步上线
1. 登录 [腾讯云控制台 → 对象存储COS](https://console.cloud.tencent.com/cos)
   → 存储桶列表:用现有桶,或「创建存储桶」——
   地域选国内(如上海/广州),**访问权限选「公有读私有写」**,其余默认。
2. 进入桶 → 「文件列表」→ 上传刚才的 `index.html`。
3. 左侧「基础配置」→「静态网站」→ 开启,索引文档填 `index.html`,保存。
   页面会给出一个「访问节点」网址,形如
   `https://你的桶名.cos-website.ap-shanghai.myqcloud.com`
   ——**这就是你的产品商城正式地址**,打开即用。

## 三、日常更新
数据有增改后:重新生成HTML → 改名 index.html → 覆盖上传(同名即覆盖)。
网址不变,刷新即是新数据。

## 常见问题
- **想用自己的域名**(如 catalog.你的公司.com):静态网站页面可绑定自定义域名,
  但国内节点要求域名已ICP备案;没备案就先用访问节点网址,一样好用。
- **费用**:这个页面不到1MB,存储+流量一年通常不到1元。
- **TDS PDF 也想放COS**:可以,后续把TDS批量下载后传到同一个桶的 `tds/` 目录,
  商城里的下载链接可切换为你自己的COS地址(目前直链品牌官网,也能用)。
- **安全**:桶里只放这个页面时"公有读"没有风险;不要把内部Excel/数据库放进这个桶。

---

## ✅ 部署记录(2026-07-05 已上线)

- 存储桶:`etia-label-1303055923`(上海)
- **正式访问地址:https://etia-label-1303055923.cos-website.ap-shanghai.myqcloud.com**
- 内容:商城版产品库(7品牌894款)
- 日常更新:`python3 scripts/build_web_catalog.py` 生成 → 改名 `index.html` → COS文件列表覆盖上传,网址不变
- 踩坑备忘:必须用带 `cos-website` 的静态网站域名访问;带 `cos` 的对象域名会强制下载(腾讯云2024年起的安全策略)

---

## ✅ 最终上线(2026-07-05)—— 采用云开发CloudBase静态托管

腾讯云2024年后新建的COS桶默认域名在浏览器强制下载,故改用**云开发CloudBase**:
- **正式访问地址(对外发布用):**
  https://etia-labeltool-etialabel-d5gu5lm09d300fe5d.webapps.tcloudbase.com
- 部署方式:CloudBase控制台 → 应用托管「本地项目上传」→ 上传含 index.html 的文件夹
  → 项目框架「其他」、安装/构建命令留空、构建产物目录 ./、部署路径 /
- **重要:上传的 index.html 必须是包含 `<!doctype html><meta charset="utf-8">` 的完整版**
  (由 scripts/build_web_catalog.py 生成的商城版;缺charset头会中文乱码)
- 更新流程:重新生成 index.html → CloudBase同名覆盖上传重新部署 → 强刷(Ctrl+Shift+R)
- COS桶 etia-label-1303055923 保留,后续存放TDS PDF文件用
