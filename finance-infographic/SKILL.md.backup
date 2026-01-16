---
name: finance-infographic
description: 财经科普信息图生成器。使用 Gemini 3 Pro Image Preview 生成与参考图风格一致的信息图。支持主标题定制、双 API（Google官方/API易），按主题分类存放。用于将财经文案转换为图文并茂的信息图。
---

# 财经信息图生成器

## 快速开始

```bash
# 基础用法
python scripts/batch_generate.py "content/主题.md" -r 4K --api nanobanana --topic "主题名"

# 指定主标题（适用于结构化文案）
python scripts/batch_generate.py "md1.md" "md2.md" "md3.md" -r 4K --titles "是什么" "为什么" "怎么办" --topic "主题"

# 交互式模式（推荐）
python scripts/batch_generate.py "content/主题.md" -r 4K --interactive
```

## 核心功能

| 功能 | 说明 |
|------|------|
| 风格一致 | 对着参考图生成，多图风格统一 |
| 固定元素一致 | 边框、logo、主标题格式严格保持一致 |
| 主标题定制 | 支持为每张图指定不同的主标题 |
| 内容忠实 | 逐字使用用户文案 |
| 双 API | Google 官方 / API易 可切换 |
| 分类存放 | 按主题自动创建文件夹 |

## 命令行参数

### 必选参数

- `md_files`: md 文件路径列表

### 可选参数

| 参数 | 说明 | 默认 |
|------|------|------|
| `-r, --resolution` | 分辨率：1K/2K/4K | 2K |
| `--api` | API 选择：google/nanobanana | 按配置 |
| `--topic` | 主题名称（创建文件夹） | 无 |
| `--titles` | 主标题列表（与md文件对应） | 无 |
| `--interactive` | 交互式模式 | 关闭 |
| `-o, --output` | 输出目录 | F:/finance-infographics |

### 分辨率（3:4 比例）

| 标准 | 尺寸 |
|------|------|
| 1K | 768×1024 |
| 2K | 1024×1366 |
| 4K | 1536×2048 |

## md 文件格式

### 单图模式

```markdown
# 主标题

## 章节1
内容...

## 章节2
内容...

(1) 步骤1...
(2) 步骤2...
```

### 多图结构化模式（推荐）

对于结构化文案（如：是什么、为什么、怎么办），建议拆分成多个md文件：

**文件1 (是什么.md)：**
```markdown
# 智谱AI是什么

## 核心介绍
内容...

## 创始团队
内容...
```

**文件2 (为什么.md)：**
```markdown
# 为什么成为第一个

## 原因1
内容...

## 原因2
内容...
```

**文件3 (怎么办.md)：**
```markdown
# 普通人怎么参与

## 方式1
内容...

## 风险提示
内容...
```

然后使用 `--titles` 参数指定主标题：

```bash
python scripts/batch_generate.py "是什么.md" "为什么.md" "怎么办.md" -r 4K --titles "是什么" "为什么" "怎么办" --topic "智谱AI"
```

## 配置

在 `.env` 文件中配置 API：

```bash
# API 优先级: 1=API易(推荐), 2=Google
API_PRIORITY=1

# API易 Nano Banana Pro
NANO_BANANA_API_KEY=your_key
NANO_BANANA_API_URL=https://api.apiyi.com/v1beta/models/gemini-3-pro-image-preview:generateContent

# Google API
GOOGLE_API_KEY=your_key
GOOGLE_API_URL=https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent
```

## 输出

图片保存到 `F:/finance-infographics/[主题名]/`，文件名格式：`infographic_YYYYMMDD_HHMMSS_000.png`

## 固定元素要求

生成的信息图必须严格保持以下固定元素一致：

### 1. 右上角logo
- 必须出现在每张图的右上角
- 位置、大小、样式与参考图完全一致
- **这是品牌标识，绝对不能缺失**

### 2. 边框样式
- 圆角、粗细、颜色必须一致
- 阴影效果必须一致
- 整体卡片形状与参考图相同

### 3. 主标题格式
- **字号固定为64px**，不随标题长度改变
- 字体、颜色、粗细、阴影与参考图一致
- 背景形状（如有）与参考图一致

### 4. 整体布局
- 内容板块排列方式一致
- 元素间距和比例一致

## 提示词原则

生成图片时使用以下核心原则：

1. **固定元素一致性**：边框、logo、主标题必须严格一致
2. **风格复刻**：对着参考图生成，如出同一人之手
3. **内容忠实**：逐字使用 md 文件中的文字
4. **图文并茂**：文字与视觉元素平衡，相得益彰
5. **主标题定制**：支持为每张图指定不同的主标题

详细提示词模式参见 [PROMPT.md](references/PROMPT.md)。

## 文件结构

```
finance-infographic/
├── SKILL.md              # 入口文档
├── .env                  # API 配置
├── content/              # md 文件目录
│   └── *.md
├── scripts/
│   ├── batch_generate.py      # 批量生成（主脚本）
│   └── generate_one_by_one.py # 逐张生成
├── references/
│   ├── PROMPT.md              # 提示词详细模式
│   └── 微信图片_*.png          # 风格参考图
└── examples/
    └── structured_example.md  # 结构化文案示例
```

## 使用示例

### 示例1：基础单图生成

```bash
python scripts/batch_generate.py "content/文章.md" -r 4K --api nanobanana --topic "IPO"
```

### 示例2：结构化多图生成（推荐）

```bash
# 先创建3个md文件：是什么.md、为什么.md、怎么办.md
# 然后运行：
python scripts/batch_generate.py \
  "content/是什么.md" \
  "content/为什么.md" \
  "content/怎么办.md" \
  -r 4K \
  --titles "是什么" "为什么" "怎么办" \
  --topic "智谱AI上市" \
  --api nanobanana
```

### 示例3：交互式使用

```bash
# 直接运行，会询问API选择、主题、是否需要自定义主标题
python scripts/batch_generate.py "md1.md" "md2.md" "md3.md" -r 4K --interactive
```

## 注意事项

1. **固定元素检查**：生成后请检查每张图是否包含：
   - ✅ 右上角logo
   - ✅ 一致的边框样式
   - ✅ 一致的主标题格式

2. **主标题建议**：
   - 结构化文案（是什么/为什么/怎么办）建议使用 `--titles` 参数
   - 主标题应简洁明确，通常2-5个字
   - 字号固定64px，不随长度改变

3. **质量保证**：
   - 如果发现logo缺失，需要重新生成
   - 如果风格不一致，检查参考图是否正确加载

## 脚本说明

| 脚本 | 用途 |
|------|------|
| `batch_generate.py` | 批量生成多张信息图（支持主标题定制） |
| `generate_one_by_one.py` | 逐张生成，可选 |
