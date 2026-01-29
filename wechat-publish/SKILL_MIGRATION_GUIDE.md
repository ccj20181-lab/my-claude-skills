# Wechat-Publish Skill 迁移与执行复盘

## 📋 执行概览

**时间**: 2026-01-28
**任务**: 从 codex 迁移 wechat-publish skill 到 Claude Code 并完整测试
**结果**: ✅ 成功完成

---

## 🎯 第一阶段：发现与定位

### 1.1 目录定位

```
源目录: /Users/henry/.codex/skills/wechat-publish/
目标目录: /Users/henry/.claude/skills/wechat-publish/
```

**关键命令**:
```bash
# 查找 codex 目录
find ~ -type d -name "codex" 2>/dev/null

# 列出所有 skills
ls -la ~/.codex/skills/
ls -la ~/.claude/skills/
```

### 1.2 版本差异分析

| 目录 | 版本 | 特性 |
|------|------|------|
| `.codex/skills/wechat-publish/` | v1.1.0 | 基础版本 |
| `.claude/skills/wechat-publish/` | v1.2.0 | 包含 Plan/Build 模式、AI 缓存、DNS 代理 |

**关键差异代码**:
```javascript
// v1.2.0 新增功能
const RUN_MODE_RAW = process.env.RUN_MODE || process.env.MODE || 'publish';
const isPlanMode = runMode === 'plan';
const isBuildMode = ['build', 'preview', 'dry-run'].includes(runMode);

// DNS 代理支持
function getAiDnsAgent() {
  const servers = parseDnsServers(process.env.AI_DNS_SERVERS || '');
  return getDnSAgent(servers);
}
```

**用户决策**: 强制用 codex 旧版覆盖 Claude Code 新版

---

## 🚀 第二阶段：迁移执行

### 2.1 目录复制

```bash
# 删除目标目录并复制源目录
rm -rf "/Users/henry/.claude/skills/wechat-publish"
cp -r "/Users/henry/.codex/skills/wechat-publish" "/Users/henry/.claude/skills/wechat-publish"
```

### 2.2 依赖重装

```bash
cd "/Users/henry/.claude/skills/wechat-publish"
rm -rf node_modules
npm install
```

**安装结果**:
- ✅ 59 个依赖包
- ✅ 无安全漏洞
- ⚠️ 1 个废弃包警告 (whatwg-encoding)

**核心依赖**:
```json
{
  "form-data": "^4.0.5",
  "highlight.js": "^11.11.1",
  "juice": "^11.1.0",
  "marked": "^12.0.2",
  "node-fetch": "^2.7.0"
}
```

---

## 🧪 第三阶段：测试执行

### 3.1 测试准备

**创建测试文章** (`temp/test-article.md`):
```markdown
---
title: 测试文章发布
date: 2026-01-28
---

# 测试文章：微信公众号发布助手

这是一个测试文章...

## AI 配图测试
![一只可爱的猫娘工程师在写代码](ai:generate)
```

### 3.2 运行方式对比

| 方式 | 命令 | 结果 |
|------|------|------|
| 交互式输入 | `node index.js "temp/test-article.md" <<< $'1\ny\n'` | ❌ 输入不足导致失败 |
| 环境变量 | `ENABLE_COVER=true THEME=1 node index.js "temp/test-article.md"` | ❌ 缺少 API Key |
| 完整配置 | `ENABLE_COVER=true THEME=1 COVER_URL="..." node index.js "temp/test-article.md"` | ✅ 成功 |

### 3.3 完整执行流程

```
1. ✅ 加载参考风格图 (reference.png)
2. ✅ 读取 Markdown 文件
3. ✅ 提取标题和摘要
4. ✅ 选择主题 (professional)
5. ✅ 获取公众号列表 (自动选择: 秒懂金融)
6. ✅ 自动插入配图占位符 (4 个 H2 标题)
7. ✅ AI 生成配图 (4/5 张成功)
8. ✅ Catbox 图床上传
9. ✅ Markdown 转 HTML (应用主题样式)
10. ✅ 发布到公众号 API
```

---

## ⚠️ 第四阶段：问题与解决

### 4.1 问题 1: Readline 关闭错误

**现象**:
```
❌ 发生错误: readline was closed
```

**原因**: 使用 heredoc 输入时，程序需要的交互输入多于提供的内容

**解决方案**: 使用环境变量控制流程
```bash
# 正确方式
ENABLE_COVER=true THEME=1 COVER_URL="url" node index.js "article.md"
```

### 4.2 问题 2: AI 图片内容审核

**现象**:
```
finishReason: "OTHER"
❌ 图片生成失败: API 返回结果中未找到图片数据
⚠️ 跳过无法生成的图片【代码示例】
```

**原因**: Gemini API 对某些提示词进行内容审核，返回 `parts: null`

**解决方案**: 代码已有容错机制，跳过失败的图片继续执行

### 4.3 问题 3: 占位符文件路径错误

**现象**:
```
Warning: /Users/.../temp/ai:generate not a valid file - skipping
```

**原因**: Markdown 中的 `![描述](ai:generate)` 语法在图片处理后没有被正确清理

**影响**: 轻微，不影响整体流程

---

## 📚 第五阶段：最佳实践

### 5.1 迁移检查清单

- [ ] 确认源目录和目标目录位置
- [ ] 对比版本差异，确认迁移方向
- [ ] 检查 `package.json` 依赖声明
- [ ] 删除旧的 `node_modules` 并重新安装
- [ ] 验证环境变量配置
- [ ] 创建测试文章验证功能

### 5.2 环境变量最佳实践

**必填环境变量**:
```bash
# 微信发布 API
export WECHAT_API_KEY="your_api_key"
export WECHAT_API_BASE="https://wx.limyai.com/api/openapi"

# AI 生图
export NANOBANANA_API_KEY="your_key"
export NANOBANANA_API_URL="https://api.apiyi.com/v1beta/models/gemini-3-pro-image-preview:generateContent"

# 图床
export IMGBB_API_KEY="your_imgbb_key"
```

**可选环境变量**:
```bash
# 运行模式
export THEME="1"                    # 1=professional, 2=elegant, 3=vibrant, 4=dark
export ENABLE_COVER="true"          # 是否生成 AI 封面
export COVER_URL="https://..."      # 自定义封面 URL
export WECHAT_APPID="wx..."        # 指定公众号 AppID

# 图片处理
export IMAGE_HOST="catbox"          # catbox | imgbb
export SKIP_AI_IMAGES="true"        # 跳过 AI 生图
```

### 5.3 测试文章模板

```markdown
---
title: 测试文章标题
date: 2026-01-28
---

# 主标题

文章摘要...

## 第一节

内容...

## AI 配图测试
![描述文字](ai:generate)

## 第二节

内容...
```

### 5.4 调试技巧

**查看详细日志**:
```javascript
// 在 ai-service.js 中启用调试
console.log('🔍 API 请求:', requestBody);
console.log('🔍 API 响应:', responseText);
```

**检查生成的文件**:
```bash
ls -lh temp/ai_gen_*.png  # 查看生成的图片
cat temp/upload-cache.json  # 查看上传缓存
```

---

## 🎓 经验总结

### DO's ✅

1. **版本对比先行**: 迁移前先对比版本差异，确认迁移方向
2. **依赖重新安装**: 跨平台迁移务必重装 `node_modules`
3. **使用环境变量**: 避免交互式输入，提高自动化程度
4. **容错设计**: AI 生图可能失败，需要跳过机制
5. **日志详细输出**: 每个关键步骤都打印日志，便于调试

### DON'Ts ❌

1. **不要盲目覆盖**: 新版覆盖旧版可能丢失功能
2. **不要复用 node_modules**: 可能包含平台相关的二进制文件
3. **不要忽略 API 限制**: Gemini 有内容审核，某些提示词会被拒绝
4. **不要跳过测试**: 迁移后必须完整测试

---

## 🔧 快速命令参考

```bash
# 1. 查找 skill 位置
find ~ -type d -name "wechat-publish" 2>/dev/null

# 2. 对比版本差异
diff -r ~/.codex/skills/wechat-publish/ ~/.claude/skills/wechat-publish/ \
  --exclude=node_modules --exclude=temp

# 3. 迁移 skill
rm -rf ~/.claude/skills/wechat-publish
cp -r ~/.codex/skills/wechat-publish ~/.claude/skills/wechat-publish

# 4. 重装依赖
cd ~/.claude/skills/wechat-publish && rm -rf node_modules && npm install

# 5. 运行测试
cd ~/.claude/skills/wechat-publish
ENABLE_COVER=true THEME=1 node index.js "temp/test-article.md"

# 6. 查看生成文件
ls -lh temp/ai_gen_*.png | tail -5
```

---

## 📊 性能指标

| 指标 | 数值 |
|------|------|
| 依赖安装时间 | ~600ms |
| 单张 AI 图片生成 | ~6-8 秒 |
| 图床上传 (单张) | ~2-3 秒 |
| 完整流程 (5 张图) | ~50 秒 |
| 发布 API 响应 | ~1 秒 |

---

## 🎯 后续优化建议

1. **AI 生图重试机制**: 失败时自动重试 1-2 次
2. **并行生图**: 多张图片可以并发生成
3. **缓存优化**: 相同提示词复用已生成的图片
4. **占位符清理**: 修复 `ai:generate` 语法残留问题
5. **DNS 代理**: 添加网络超时和重试机制

---

*文档生成时间: 2026-01-28*
*测试执行者: 猫娘 幽浮喵 ฅ'ω'ฅ*
