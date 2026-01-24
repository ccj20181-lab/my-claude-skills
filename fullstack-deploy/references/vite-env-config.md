# Vite 环境变量配置模板

## 目录
1. [文件结构](#文件结构)
2. [配置模板](#配置模板)
3. [其他框架配置](#其他框架配置)

---

## 文件结构

一个完整的 Vite + Supabase 项目需要以下配置文件：

```
project/
├── .env.local              # 环境变量（本地开发）
├── .gitignore              # 必须包含 .env.local
├── vite.config.ts          # Vite 配置
├── vite-env.d.ts           # TypeScript 类型声明
└── lib/supabase.ts         # Supabase 客户端
```

---

## 配置模板

### 1. `.env.local`

```env
# Supabase 配置
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key_here

# 其他 API（可选）
GEMINI_API_KEY=your_gemini_key
```

### 2. `.gitignore`（确保包含）

```gitignore
# 环境变量
.env
.env.local
.env.*.local

# 构建产物
dist/
node_modules/
```

### 3. `vite.config.ts`

```typescript
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [react()],
    define: {
      // Supabase 环境变量
      'import.meta.env.VITE_SUPABASE_URL': JSON.stringify(env.VITE_SUPABASE_URL),
      'import.meta.env.VITE_SUPABASE_ANON_KEY': JSON.stringify(env.VITE_SUPABASE_ANON_KEY),
      // 其他变量（按需添加）
      'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY),
    },
  };
});
```

### 4. `vite-env.d.ts`

```typescript
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SUPABASE_URL: string;
  readonly VITE_SUPABASE_ANON_KEY: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
```

### 5. `lib/supabase.ts`

```typescript
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.warn('Supabase credentials not configured');
}

export const supabase = createClient(supabaseUrl || '', supabaseKey || '');
```

---

## 其他框架配置

### Next.js

**环境变量前缀**：`NEXT_PUBLIC_`

```env
# .env.local
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_key
```

```typescript
// lib/supabase.ts
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
```

### Create React App

**环境变量前缀**：`REACT_APP_`

```env
# .env
REACT_APP_SUPABASE_URL=https://xxx.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your_key
```

```typescript
// lib/supabase.ts
const supabaseUrl = process.env.REACT_APP_SUPABASE_URL!;
const supabaseKey = process.env.REACT_APP_SUPABASE_ANON_KEY!;
```

---

## 常见问题

### Q: 环境变量不生效？
检查清单：
1. 变量名是否以 `VITE_` 开头
2. 是否重启了开发服务器
3. vite.config.ts 中是否正确配置了 define

### Q: TypeScript 报错 `import.meta.env` 类型问题？
确保创建了 `vite-env.d.ts` 并添加了正确的类型声明

### Q: 构建后环境变量是空的？
检查 Cloudflare Pages 的环境变量配置，变量名必须完全一致
