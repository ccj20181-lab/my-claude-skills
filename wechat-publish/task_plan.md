# 修复计划：WeChat-Publish 图片生成优化 v2

## 问题诊断

主人指出了三个严重问题，浮浮酱逐一分析如下：

### 问题1：参考图生成方式错误 ❌
**现象**：当前的 `reference.png` 只是从 finance-infographic 复制过来后做了简单裁剪（1792x1344），而不是让 AI 重新生成一张 4:3 横版的风格参考图。

**正确做法**：
1. 使用原始竖版参考图 (1792x2400) 作为输入
2. 调用 Gemini API，让模型"看着这张图，生成一张风格完全一致但比例为 4:3 横版的版本"
3. 将生成的新图保存为 `reference.png`，作为后续所有配图的风格参考

### 问题2：生成的图片直接复制参考图 ❌
**现象**：多张生成的图片直接"复制"了参考图，而不是根据文案内容生成风格一致的新图。

**根因分析**：
1. **Prompt 设计缺陷**：当前的 prompt 只是简单地附加了风格后缀，没有明确告诉模型：
   - "看着参考图的风格"
   - "但要根据文案内容生成全新的图片"
   - "参考图仅用于风格参考，不使用其内容"
2. **学习 finance-infographic 的正确做法**：
   - 使用结构化 prompt 模板（见 `references/templates/base_prompt.md`）
   - 明确 "禁止基于参考图涂抹生成"
   - 强调 "重新生成一张图片"

### 问题3：公众号草稿图片变成 1:1 且不清晰 ❌
**现象**：上传到图床后，在公众号草稿箱显示的图片变成了 1:1 比例且非常模糊。

**根因分析**：
1. **ImgBB 返回的 URL 可能是缩略图**：ImgBB API 返回多个 URL：
   - `data.url` - 可能是中等质量
   - `data.display_url` - 显示用 URL
   - `data.image.url` - 原图 URL（需要验证）
   - `data.thumb.url` - 缩略图 URL（最差质量）
2. 当前代码使用 `result.data.url`，需要验证是否是原图
3. 另一种可能：微信公众号 API 对图片有自己的处理逻辑

---

## 修复方案

### Phase 1: 生成正确的参考图 ✅
- [x] 创建脚本 `generate-reference.js`
- [x] 使用原始竖版参考图作为输入
- [x] 让 Gemini 生成 4:3 横版风格参考图 (4800x3584)
- [x] 保存为 `reference.png`

### Phase 2: 修复 Prompt 设计 ✅
- [x] 在 `ai-service.js` 中引入结构化 prompt 模板
- [x] 学习 finance-infographic 的 prompt 设计
- [x] 添加 `buildStructuredPrompt()` 函数
- [x] 添加 `extractSectionContent()` 函数提取小节内容
- [x] 每张图都有完整的结构化 prompt

### Phase 3: 修复图床问题 ✅
- [x] 确认 ImgBB 使用的是原图 URL
- [x] 修复 `converter.js` 图片渲染：
  - 添加 `aspect-ratio: 4/3` 样式
  - 添加 `data-w` 和 `data-ratio` 属性
  - 添加 `object-fit: cover` 防止变形

### Phase 4: 验证测试 ✅
- [x] 运行完整流程测试
- [x] 生成 7 张正文配图 + 1 张封面图
- [x] 所有图片尺寸均为 4800x3584 (4K 4:3)
- [x] 成功发布到公众号草稿箱
- [x] Media ID: IAk8eZEtU5G_0zQQlIwm6-z9wlnd8vtlLkuEPLgZbRb04kyOac9kDa2UGQ2JvVew

---

## 修复总结

### 本次修复的三个核心问题：

1. **参考图问题** ✅
   - 之前：只是简单裁剪竖版参考图
   - 现在：使用 AI 基于竖版图生成全新的 4:3 横版参考图

2. **图片复制问题** ✅
   - 之前：生成的图片直接复制参考图
   - 现在：使用结构化 Prompt（学习 finance-infographic）：
     - 明确"看着参考图的风格"
     - 明确"禁止复制参考图"
     - 明确"根据文案内容生成全新图片"
     - 每张图都提取对应小节的内容作为 Prompt

3. **图床/显示问题** ✅
   - 确认 ImgBB 返回的是原图 URL (8MB+)
   - 修复 HTML 图片渲染，添加 `aspect-ratio: 4/3` 样式
   - 添加 `data-w` 和 `data-ratio` 属性辅助微信保持比例

### 新增功能：
- `generate-reference.js` - 生成 4:3 横版参考图的脚本
- `buildStructuredPrompt()` - 构建结构化 Prompt
- `extractSectionContent()` - 提取 H2 小节内容

---

## 状态
**已完成** ✅
