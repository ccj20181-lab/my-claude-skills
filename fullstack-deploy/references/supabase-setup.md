# Supabase 配置详细指南

## 目录
1. [创建账号和项目](#创建账号和项目)
2. [获取 API 凭据](#获取-api-凭据)
3. [建表和 RLS 配置](#建表和-rls-配置)
4. [常见问题](#常见问题)

---

## 创建账号和项目

### 1. 注册/登录
1. 访问 https://supabase.com
2. 点击 "Start your project" 或 "Sign Up"
3. 推荐使用 GitHub 账号登录（点击 "Continue with GitHub"）

### 2. 创建新项目
1. 进入 Dashboard 后点击 "New Project"
2. 填写项目信息：
   - **Name**: 项目名称（如 `moneymuse`）
   - **Database Password**: 设置数据库密码（牢记，但通常不会直接使用）
   - **Region**: 选择 `Northeast Asia (Tokyo)` 或最近的区域
3. 点击 "Create new project"
4. ⏳ 等待 1-2 分钟项目初始化完成

---

## 获取 API 凭据

### 位置
Project Settings（左侧菜单底部 ⚙️ 图标）→ API

### 需要复制的两个值

| 字段名 | 用途 | 说明 |
|--------|------|------|
| **Project URL** | `VITE_SUPABASE_URL` | 格式：`https://xxxxxxxx.supabase.co` |
| **anon public** 或 **Publishable key** | `VITE_SUPABASE_ANON_KEY` | 格式：`eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` 或 `sb_publishable_...` |

### ⚠️ 重要提醒
- 复制 **anon public** 或 **Publishable key**（两者等价）
- **不要**复制 service_role（这是后端专用密钥，有完整权限）
- anon key 可以安全地暴露在前端代码中

---

## 建表和 RLS 配置

### 进入 SQL Editor
1. 左侧菜单点击 SQL Editor（`<>` 图标）
2. 点击 "+ New query" 创建新查询

### 运行建表 SQL
粘贴 SQL 代码后点击 "Run" 按钮（或按 Cmd+Enter）

### 启用 Row Level Security (RLS)
```sql
-- 启用 RLS
ALTER TABLE your_table ENABLE ROW LEVEL SECURITY;

-- 创建公开访问策略（适用于不需要认证的场景）
CREATE POLICY "Public Access" ON your_table FOR ALL USING (true);
```

### 验证建表成功
1. 左侧菜单点击 "Table Editor"
2. 应该能看到刚创建的表
3. 点击表名可以查看/编辑数据

---

## 常见问题

### Q: 找不到 API 设置页面？
A: 左侧菜单最底部有个 ⚙️ 齿轮图标，点击后选择 "API"

### Q: anon key 变成了 Publishable key？
A: 两者完全等价，Supabase 更新了 UI 术语，功能相同

### Q: 建表报错 permission denied？
A: 确保使用 SQL Editor 而不是 Table Editor 创建表，SQL Editor 有完整权限

### Q: 数据库连接失败？
检查清单：
1. URL 是否正确（包含 https://）
2. Key 是否完整复制（很长的字符串）
3. 表是否存在
4. RLS 策略是否配置
