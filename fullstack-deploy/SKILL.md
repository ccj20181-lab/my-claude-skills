---
name: fullstack-deploy
description: |
  全栈应用部署助手，专门用于 Supabase (后端数据库) + Cloudflare Pages (前端托管) 的部署流程。
  当用户需要：(1) 配置 Supabase 数据库连接 (2) 部署 Vite/React 应用到 Cloudflare Pages (3) 设置前后端环境变量 (4) 调试部署问题 时使用此 skill。
  触发关键词：部署、Supabase、Cloudflare、环境变量、上线、发布网站、数据库连接失败、部署失败。
---

# 全栈部署助手

帮助用户完成 Supabase + Cloudflare Pages 全栈应用部署。

## 部署流程概览

```
1. 后端配置 → 创建 Supabase 项目并获取凭据
2. 代码配置 → 配置环境变量和类型定义
3. 前端部署 → 部署到 Cloudflare Pages
4. 验证测试 → 验证数据库连接和部署成功
```

## 快速检查清单

在开始部署前，确认项目满足以下条件：

- [ ] package.json 中有 `build` 脚本
- [ ] 构建输出目录为 `dist`（Vite 默认）
- [ ] .gitignore 包含 `.env.local`
- [ ] **没有 wrangler.toml**（纯 Pages 项目不需要！）

---

## 阶段一：Supabase 后端配置

### 1.1 创建项目

引导用户：
1. 访问 https://supabase.com/dashboard
2. 点击 "New Project"
3. 填写项目名、设置数据库密码、选择区域 (推荐 Northeast Asia)
4. 等待 1-2 分钟项目初始化

### 1.2 获取凭据

位置：**Project Settings → API**

| 字段名 | 环境变量名 | 说明 |
|--------|------------|------|
| Project URL | `VITE_SUPABASE_URL` | 格式：`https://xxx.supabase.co` |
| anon public / Publishable key | `VITE_SUPABASE_ANON_KEY` | 格式：`eyJ...` 或 `sb_publishable_...` |

⚠️ **注意**：复制 anon public（不是 service_role）

### 1.3 建表

在 SQL Editor 中运行建表 SQL。→ 详见 [references/sql-templates.md](references/sql-templates.md)

---

## 阶段二：代码配置

根据项目框架配置环境变量：

| 框架 | 环境变量前缀 | 配置文件 |
|------|--------------|----------|
| Vite | `VITE_` | vite.config.ts |
| Next.js | `NEXT_PUBLIC_` | next.config.js |
| Create React App | `REACT_APP_` | .env |

→ 详见 [references/vite-env-config.md](references/vite-env-config.md) 获取完整配置模板

---

## 阶段三：Cloudflare Pages 部署

### 关键配置（⚠️ 重要！）

| 设置项 | 正确值 | 错误示例 |
|--------|--------|----------|
| Framework preset | **None** 或不选 | 不要选 VitePress |
| Build command | `npm run build` | - |
| Build output directory | `dist` | - |
| Deploy command | **留空！不要填任何内容** | ❌ `npx wrangler deploy` |

### 环境变量

在 Cloudflare Pages Dashboard 中添加：
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`

→ 详见 [references/cloudflare-pages.md](references/cloudflare-pages.md)

---

## 常见问题速查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 环境变量不生效 | Vite 要求 `VITE_` 前缀 | 重命名变量，重新构建 |
| 部署报错 Missing entry-point | Deploy command 填了 wrangler | 清空 Deploy command |
| 数据库连接失败 | anon key 为空或错误 | 检查 .env.local 和 Cloudflare 环境变量 |
| Framework preset 没有 Vite | Cloudflare 未内置 | 选择 None，手动配置 |

→ 详见 [references/troubleshooting.md](references/troubleshooting.md) 获取完整问题排查

---

## 交互式部署向导

当用户请求部署帮助时，按以下顺序逐步引导：

### 步骤 1：确认项目状态
询问：
- "项目使用什么框架？(Vite/Next.js/Create React App)"
- "是否已有 Supabase 项目？"

### 步骤 2：获取凭据
如果没有 Supabase 凭据，引导用户：
1. 创建 Supabase 项目
2. 复制 Project URL 和 anon key

### 步骤 3：配置代码
帮助用户：
1. 创建/更新 `.env.local`
2. 配置 vite.config.ts
3. 创建类型定义文件

### 步骤 4：部署
引导用户在 Cloudflare Pages 中：
1. 连接 Git 仓库
2. 正确配置构建设置
3. 添加环境变量

### 步骤 5：验证
1. 检查部署日志
2. 访问部署 URL
3. 测试数据库连接
