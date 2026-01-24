# Cloudflare Pages 部署详细指南

## 目录
1. [创建 Pages 项目](#创建-pages-项目)
2. [构建配置](#构建配置)
3. [环境变量配置](#环境变量配置)
4. [常见错误和解决方案](#常见错误和解决方案)

---

## 创建 Pages 项目

### 1. 登录 Cloudflare
访问 https://dash.cloudflare.com

### 2. 创建项目
1. 左侧菜单点击 "Workers & Pages"
2. 点击 "Create" 按钮
3. 选择 **"Pages"** 标签（⚠️ 不是 Workers！）
4. 点击 "Connect to Git"
5. 选择 GitHub，授权后选择仓库

---

## 构建配置

### ⚠️ 关键配置（必须正确！）

| 设置项 | 正确值 | 说明 |
|--------|--------|------|
| **Production branch** | `main` | 或你的主分支名 |
| **Framework preset** | `None` | ⚠️ 不要选 VitePress 或其他 |
| **Build command** | `npm run build` | 标准构建命令 |
| **Build output directory** | `dist` | Vite 默认输出目录 |
| **Deploy command** | **留空！** | ⚠️ 最重要：什么都不填！ |

### 为什么 Deploy command 必须留空？
- Cloudflare Pages 会自动处理静态文件部署
- 填写 `npx wrangler deploy` 会报错：`Missing entry-point`
- 这个字段是给 Workers 用的，Pages 项目不需要

### Framework preset 选项说明
如果列表中没有你使用的框架（如 Vite），选择 **None** 然后手动填写：
- Build command: `npm run build`
- Build output directory: `dist`

---

## 环境变量配置

### 在哪里配置？

**方法 1：创建项目时配置**
在创建项目页面，展开 "Environment variables" 区域

**方法 2：项目创建后配置**
项目页面 → Settings → Environment variables

### 需要添加的变量

| 变量名 | 示例值 |
|--------|--------|
| `VITE_SUPABASE_URL` | `https://xxxxxxxx.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | `sb_publishable_xxxx...` 或 `eyJ...` |

### ⚠️ 重要提醒
- 变量名必须与代码中使用的完全一致
- Vite 项目必须使用 `VITE_` 前缀
- 添加变量后需要重新部署才能生效

---

## 常见错误和解决方案

### 错误 1: Missing entry-point to Worker script

```
✘ [ERROR] Missing entry-point to Worker script or to assets directory
```

**原因**：Deploy command 填写了 `npx wrangler deploy`

**解决**：
1. 进入项目 Settings → Builds & deployments
2. 点击 Edit configurations
3. 清空 Deploy command 字段
4. 保存并重新部署

### 错误 2: Build command failed

```
Failed: build command exited with code 1
```

**可能原因**：
1. package.json 中没有 `build` 脚本
2. 依赖安装失败
3. TypeScript 类型错误

**解决**：
1. 确保本地 `npm run build` 能成功
2. 检查 package.json 的 `scripts.build`

### 错误 3: 环境变量不生效

**可能原因**：
1. 变量名拼写错误
2. 缺少 `VITE_` 前缀
3. 添加后未重新部署

**解决**：
1. 检查变量名是否与代码中完全一致
2. 确保使用正确的前缀
3. 重新触发部署

### 错误 4: 404 页面（SPA 路由问题）

**原因**：SPA 路由在刷新时找不到对应文件

**解决**：在 `public/` 目录创建 `_redirects` 文件：
```
/*    /index.html   200
```

---

## 重新部署

### 方法 1：Retry deployment
1. 进入 Deployments 页面
2. 找到失败的部署
3. 点击右边的 ⋮ 菜单
4. 选择 "Retry deployment"

### 方法 2：Create new deployment
1. 点击 "Create deployment"
2. 选择 "Deploy from branch"
3. 选择 main 分支
4. 点击 "Deploy"

### 方法 3：推送新代码
向仓库推送任意 commit，会自动触发新部署
