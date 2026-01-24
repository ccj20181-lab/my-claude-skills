# SQL 建表模板

## 目录
1. [通用模板](#通用模板)
2. [常见表结构](#常见表结构)
3. [RLS 策略模板](#rls-策略模板)

---

## 通用模板

### 基础表结构

```sql
CREATE TABLE IF NOT EXISTS table_name (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  -- 在这里添加你的字段
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- 启用 RLS
ALTER TABLE table_name ENABLE ROW LEVEL SECURITY;

-- 公开访问策略（无需认证）
CREATE POLICY "Public Access" ON table_name FOR ALL USING (true);
```

### 带用户关联的表

```sql
CREATE TABLE IF NOT EXISTS table_name (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
  -- 在这里添加你的字段
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- 启用 RLS
ALTER TABLE table_name ENABLE ROW LEVEL SECURITY;

-- 用户只能访问自己的数据
CREATE POLICY "Users can access own data" ON table_name
  FOR ALL USING (auth.uid() = user_id);
```

---

## 常见表结构

### 选题/内容管理表

```sql
CREATE TABLE IF NOT EXISTS topics (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  title text NOT NULL,
  note text,
  series text NOT NULL,
  status text NOT NULL DEFAULT 'idea',
  is_urgent boolean DEFAULT false,
  target_date text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE topics ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public Access" ON topics FOR ALL USING (true);
```

### 用户配置表

```sql
CREATE TABLE IF NOT EXISTS user_settings (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
  theme text DEFAULT 'light',
  language text DEFAULT 'zh-CN',
  notifications_enabled boolean DEFAULT true,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can access own settings" ON user_settings
  FOR ALL USING (auth.uid() = user_id);
```

### 文章/博客表

```sql
CREATE TABLE IF NOT EXISTS posts (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  title text NOT NULL,
  content text,
  slug text UNIQUE,
  status text NOT NULL DEFAULT 'draft', -- draft, published, archived
  published_at timestamptz,
  author_id uuid REFERENCES auth.users(id),
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- 已发布文章公开可读
CREATE POLICY "Published posts are public" ON posts
  FOR SELECT USING (status = 'published');

-- 作者可以完全控制自己的文章
CREATE POLICY "Authors can manage own posts" ON posts
  FOR ALL USING (auth.uid() = author_id);
```

### 评论表

```sql
CREATE TABLE IF NOT EXISTS comments (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  post_id uuid REFERENCES posts(id) ON DELETE CASCADE,
  user_id uuid REFERENCES auth.users(id),
  content text NOT NULL,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE comments ENABLE ROW LEVEL SECURITY;

-- 所有人可读评论
CREATE POLICY "Comments are public" ON comments FOR SELECT USING (true);

-- 登录用户可以创建评论
CREATE POLICY "Users can create comments" ON comments
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- 用户只能删除自己的评论
CREATE POLICY "Users can delete own comments" ON comments
  FOR DELETE USING (auth.uid() = user_id);
```

---

## RLS 策略模板

### 完全公开访问

```sql
-- 任何人都可以读写
CREATE POLICY "Public Access" ON table_name FOR ALL USING (true);
```

### 仅登录用户可访问

```sql
-- 必须登录才能访问
CREATE POLICY "Authenticated users only" ON table_name
  FOR ALL USING (auth.uid() IS NOT NULL);
```

### 用户只能访问自己的数据

```sql
-- 需要表中有 user_id 字段
CREATE POLICY "Users access own data" ON table_name
  FOR ALL USING (auth.uid() = user_id);
```

### 公开读取，认证写入

```sql
-- 任何人可读
CREATE POLICY "Public read" ON table_name
  FOR SELECT USING (true);

-- 登录用户可写
CREATE POLICY "Authenticated write" ON table_name
  FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

CREATE POLICY "Authenticated update" ON table_name
  FOR UPDATE USING (auth.uid() IS NOT NULL);
```

---

## 使用说明

1. 在 Supabase 左侧菜单点击 **SQL Editor**
2. 点击 **+ New query**
3. 粘贴需要的 SQL 代码
4. 点击 **Run** 按钮（或按 Cmd+Enter）
5. 看到 ✅ Success 表示执行成功

### ⚠️ 注意事项
- 确保完整复制 SQL 代码
- 运行前检查表名是否正确
- 如果表已存在，`CREATE TABLE IF NOT EXISTS` 不会报错
- RLS 策略可以根据需求调整
