# 小红书低粉爆文分析 - GitHub Pages部署指南

## 📊 功能概述

本项目提供三种方式查看小红书财经爆文分析结果：

1. **微信推送** - HTML格式,美观的卡片式设计,包含笔记链接
2. **GitHub Pages网站** - 交互式网页,支持搜索筛选
3. **Excel报告** - 详细的表格数据

---

## 🚀 GitHub Pages部署步骤

### 1. 启用GitHub Pages

1. 进入仓库的 **Settings** → **Pages**
2. **Source** 选择 **GitHub Actions**
3. 保存设置

### 2. 配置GitHub Secrets

在仓库的 **Settings** → **Secrets and variables** → **Actions** 中添加:

- `XHS_COOKIES`: 小红书登录cookies (JSON格式)
- `WECHAT_PUSH_TOKEN`: PushPlus推送token (可选)

### 3. 手动触发测试

进入 **Actions** → **小红书低粉爆文日报** → **Run workflow**

等待workflow执行完成,会自动触发GitHub Pages部署。

### 4. 访问网站

部署完成后,通过以下地址访问:

```
https://yourusername.github.io/xhs-topic-analyzer/
```

---

## 📁 项目结构

```
xhs-topic-analyzer/
├── docs/                           # GitHub Pages根目录
│   ├── index.html                  # 主页面
│   ├── assets/
│   │   ├── css/
│   │   │   └── style.css          # 样式文件
│   │   └── js/
│   │       └── app.js             # 交互脚本
│   └── data/
│       ├── viral-notes.json       # 笔记数据(每次更新)
│       └── metadata.json          # 元数据
├── scripts/
│   ├── viral_finder.py            # 主脚本
│   ├── push_html.py               # HTML推送模块
│   └── generate_html.py           # 网站数据生成器
└── .github/workflows/
    ├── xhs-viral-report.yml       # 主workflow(抓取数据)
    └── deploy-gh-pages.yml        # 部署workflow(GitHub Pages)
```

---

## 🔄 自动化流程

### 定时执行

- **每天北京时间 10:30** 自动执行
- 搜索关键词: 金融、金融知识、财经、理财、股票、基金等
- 筛选条件: 点赞≥1000, 粉丝≤20000

### Workflow触发链

1. **xhs-viral-report** 执行数据抓取
   - 搜索小红书笔记
   - 获取粉丝数据
   - 计算爆款指数
   - 生成JSON和Excel
   - 推送微信消息
   - 上传artifacts

2. **deploy-gh-pages** 自动触发部署
   - 下载JSON数据
   - 生成网站数据文件
   - 部署到GitHub Pages

---

## 💡 本地开发测试

### 测试微信推送

```bash
cd /Users/henry/.claude/skills/xhs-topic-analyzer
python3 scripts/viral_finder.py --config config.viral.json
```

### 测试网站生成

```bash
# 生成网站数据
python3 scripts/generate_html.py \
  --input ~/Documents/xhs_viral_notes_20250119_123456.json \
  --output docs/data

# 本地预览(需要HTTP服务器)
cd docs
python3 -m http.server 8000
# 访问 http://localhost:8000
```

---

## 📊 数据指标说明

### 爆款指数计算公式

```
互动率 = (点赞 + 收藏 + 评论) / 粉丝数 × 100%
爆款指数 = 互动率 × log10(点赞数 + 1)
```

**说明:**
- 互动率: 反映笔记的互动质量
- 爆款指数: 综合考虑互动量和点赞量,数值越高表示爆文潜力越大

---

## 🎨 网站功能

### 主要功能

- **📊 统计概览**: 显示发现的爆文数量、平均点赞、平均粉丝
- **🔍 搜索筛选**: 支持按标题搜索、按条件筛选(高赞/低粉/高爆款指数)
- **💡 选题洞察**: 自动分析最高爆款指数和低粉高赞案例
- **📥 数据导出**: 支持导出JSON格式数据
- **🔗 笔记链接**: 直接跳转小红书查看笔记

### 响应式设计

- 桌面端: 多列卡片布局
- 移动端: 单列布局,优化触摸交互

---

## 📝 配置文件说明

### config.viral.json

```json
{
  "mode": "viral",
  "keywords": ["金融", "金融知识", "财经", "理财"],
  "filters": {
    "min_likes": 1000,          // 最小点赞数
    "max_followers": 20000,      // 最大粉丝数
    "publish_time": "一周内"
  },
  "mcp_url": "http://localhost:18060/mcp",
  "output_dir": "~/Documents",
  "wechat_push_token": "your_token_here",
  "output_formats": ["json", "excel"],
  "push_wechat": true,
  "top_n": 10
}
```

---

## 🐛 常见问题

### Q: 微信推送显示乱码?

A: 确保使用了HTML模板格式(默认开启)。如遇问题,检查`push_html.py`模块是否正常导入。

### Q: GitHub Pages部署失败?

A: 检查以下几点:
1. 仓库Settings中Pages是否启用
2. workflow是否成功上传JSON artifact
3. 部署workflow是否有权限错误

### Q: 网站显示"加载中"?

A: 检查`docs/data/viral-notes.json`文件是否存在且格式正确。

---

## 📧 联系方式

如有问题,请提交Issue或Pull Request。

---

**更新时间**: 2025-01-19
**版本**: v1.0.0
