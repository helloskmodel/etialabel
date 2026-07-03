# ETIA 特种标签统一产品数据库（轻量原型）

整合近10个代理品牌 + ETIA自研特种标签的统一产品库。设计方案见
[docs/label-pim-database-design.md](docs/label-pim-database-design.md)。

## 运行

```bash
pip install -r requirements.txt
python app/app.py
# 打开 http://127.0.0.1:5000
```

首次启动自动建库（SQLite：`data/labels.db`）并初始化品牌/行业/面材/胶水字典。

## 功能

| 入口 | 功能 |
|---|---|
| `/`（产品查询） | 按 品牌 / 行业应用Application / 面材Facestock / 胶水Adhesive / 耐温 / 耐化学 / 关键词 交叉筛选；结果一键导出Excel |
| `/admin`（数据管理） | ① 下载Excel导入模板 → 填写/修改 → 上传（按品牌+型号判重：存在即更新，不存在即新增，**改数据不用碰代码**）② TDS/手册/Notes文件上传并绑定单品，支持版本与对外公开控制 |
| `/product/<id>` | 单品详情：五维参数 + Feature/Benefit/Application三要素 + 绑定资料下载 |

## 数据导入约定

- 面材/胶水/行业列可填中文名、英文名或编码，未见过的新值自动创建字典项；
- 耐温档位 T1~T6 由「长期耐温上限」自动归档（≤80/120/180/260/500/以上）；
- 品牌原始分类原文填入 `source_category_raw` 列做 L0 留存，方便映射复核。

## 说明

原型用 SQLite 单机运行；生产部署按设计文档平移 MySQL 8 + 对象存储，
表结构字段一一对应。当前版本无登录鉴权，仅限内网/本机使用。
