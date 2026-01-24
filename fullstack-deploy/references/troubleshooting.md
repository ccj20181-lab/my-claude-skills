# 问题排查指南

## 目录
1. [Supabase 相关问题](#supabase-相关问题)
2. [Cloudflare Pages 相关问题](#cloudflare-pages-相关问题)
3. [Vite 构建问题](#vite-构建问题)
4. [环境变量问题](#环境变量问题)

---

## Supabase 相关问题

### 问题：数据库连接失败

**症状**：
- 页面显示 "连接失败" 或 "Cloud sync disabled"
- 控制台报错 `Failed to fetch` 或 `401 Unauthorized`

**排查步骤**：
1. 检查 URL 是否正确（包含 `https://`）
2. 检查 anon key 是否完整复制
3. 确认表是否存在（Table Editor 查看）
4. 确认 RLS 策略是否配置

**解决方案**：
```sql
-- 确保 RLS 策略允许访问
ALTER TABLE your_table ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public Access" ON your_table FOR ALL USING (true);
```

### 问题：anon key 找不到了

**说明**：Supabase 更新了 UI，anon key 现在叫 "Publishable key"

**位置**：Project Settings → API → Project API keys → anon / Publishable key

### 问题：建表 SQL 报错

**常见错误**：`syntax error at or near "xxx"`

**原因**：SQL 代码复制不完整

**解决**：确保完整复制 SQL 代码，从 `CREATE` 开始到最后的 `;` 结束

---

## Cloudflare Pages 相关问题

### 问题：Missing entry-point to Worker script

**完整错误**：
```
✘ [ERROR] Missing entry-point to Worker script or to assets directory
```

**原因**：Deploy command 填写了 `npx wrangler deploy`

**解决**：
1. 进入项目 Settings → Builds & deployments
2. 点击 Edit configurations
3. **清空 Deploy command 字段**（什么都不填！）
4. 保存并重新部署

### 问题：Deploy command 清空后无法保存

**原因**：可能创建项目时选择了错误的类型（Workers 而不是 Pages）

**解决**：
1. 删除当前项目（Settings → Delete project）
2. 重新创建，选择 **Pages** 标签
3. 正确配置构建设置

### 问题：Framework preset 没有 Vite 选项

**解决**：选择 **None**，然后手动填写：
- Build command: `npm run build`
- Build output directory: `dist`

### 问题：404 错误（SPA 路由）

**症状**：首页正常，刷新其他页面显示 404

**原因**：SPA 路由需要重定向配置

**解决**：创建 `public/_redirects` 文件：
```
/*    /index.html   200
```

---

## Vite 构建问题

### 问题：本地构建失败

**排查步骤**：
```bash
# 1. 清理缓存
rm -rf node_modules dist
npm install

# 2. 运行构建
npm run build

# 3. 查看具体错误
```

### 问题：TypeScript 类型错误

**症状**：`import.meta.env.VITE_XXX` 类型报错

**解决**：创建 `vite-env.d.ts`：
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

### 问题：react-dom 版本冲突

**症状**：`npm install` 警告版本不兼容

**解决**：确保 react 和 react-dom 版本一致：
```json
{
  "dependencies": {
    "react": "18.2.0",
    "react-dom": "18.2.0"
  }
}
```

---

## 环境变量问题

### 问题：环境变量在本地不生效

**排查清单**：
1. [ ] 文件名是否是 `.env.local`（不是 `.env`）
2. [ ] 变量名是否以 `VITE_` 开头
3. [ ] 是否重启了开发服务器
4. [ ] vite.config.ts 是否正确配置了 define

### 问题：环境变量在生产环境不生效

**排查清单**：
1. [ ] Cloudflare Pages 中是否添加了环境变量
2. [ ] 变量名是否与代码中完全一致（区分大小写）
3. [ ] 添加变量后是否重新部署

### 问题：敏感信息泄露

**⚠️ 注意**：
- `VITE_` 前缀的变量会被打包到前端代码中
- anon key 可以安全暴露（受 RLS 保护）
- service_role key **绝不能**暴露在前端

---

## 快速诊断流程图

```
部署失败？
│
├─ 构建阶段失败
│   ├─ npm install 失败 → 检查 package.json
│   ├─ npm run build 失败 → 本地运行 npm run build 查看错误
│   └─ TypeScript 错误 → 检查类型定义
│
├─ 部署阶段失败
│   ├─ Missing entry-point → 清空 Deploy command
│   └─ wrangler 相关错误 → 删除 wrangler.toml，清空 Deploy command
│
└─ 运行时失败
    ├─ 数据库连接失败 → 检查 Supabase 凭据和 RLS
    ├─ 环境变量空 → 检查 Cloudflare 环境变量配置
    └─ 404 错误 → 添加 _redirects 文件
```
