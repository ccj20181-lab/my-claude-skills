---
name: finance-infographic
description: 使用 Gemini 3 Pro Image Preview 生成财经信息图。让AI直接观察参考图并100%复刻其视觉风格（边框、logo、标题、配色、布局），仅替换文字内容。支持主标题定制、双API切换、按主题分类。用于将财经文案转换为风格统一的系列信息图。触发时机：用户说"生成信息图"、"做图"、"制作财经科普图"或提供md文件要求生成时。
---

# 财经信息图生成器

## 使用场景

- 将财经科普文章转换为信息图
- 制作系列财经热点解读图片
- 生成风格统一的财经知识卡片

## 核心原理

**让AI直接看参考图，复刻所有视觉元素，仅替换文字内容。**

已验证方案：✅ 直接看图（稳定）  ❌ 描述设计规范（不稳定）

## 快速开始

```bash
# 推荐：逐张生成（4K分辨率，稳定）
python scripts/generate_one_by_one.py "content/文章.md" -r 4K --topic "主题名"

# 系列图生成
python scripts/generate_one_by_one.py "content/是什么.md" -r 4K --topic "主题"
python scripts/generate_one_by_one.py "content/为什么.md" -r 4K --topic "主题"
python scripts/generate_one_by_one.py "content/怎么办.md" -r 4K --topic "主题"
```

## 工作流程

### 第1步：准备md文件

在 `content/` 目录创建markdown文件：

```markdown
# 主标题

## 章节1
内容...

## 章节2
(1) 要点1
(2) 要点2
```

### 第2步：运行脚本生成

```bash
python scripts/generate_one_by_one.py "content/文件.md" -r 4K --topic "主题名"
```

脚本会：
1. 加载 `references/` 目录下的参考图
2. 使用三步式提示词让AI观察→生成→处理
3. 保存到 `~/finance-infographics/[主题名]/`

### 第3步：检查固定元素

验证生成的图片包含：
- ✅ 右上角logo（位置、大小、样式与参考图一致）
- ✅ 统一的边框样式（圆角、粗细、颜色、阴影）
- ✅ 主标题字号64px（颜色、字体、背景与参考图一致）
- ✅ 统一的配色方案和布局

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `md_file` | md文件路径（必选） | - |
| `-r, --resolution` | 1K/2K/4K | 4K |
| `--api` | google/nanobanana | 按配置 |
| `--topic` | 主题名称（创建文件夹） | 无 |
| `-o, --output` | 输出目录 | ~/finance-infographics |

## md文件格式规范

### 单图模式

```markdown
# 主标题

## 章节1
内容...

## 章节2
内容...

(1) 步骤1
(2) 步骤2
```

### 系列图模式（推荐）

拆分成多个md文件，逐张生成：

**是什么.md**：
```markdown
# 智谱AI是什么

## 核心介绍
内容...
```

**为什么.md**：
```markdown
# 为什么成为第一

## 原因1
内容...
```

**怎么办.md**：
```markdown
# 普通人怎么参与

## 方式1
内容...
```

## API配置

在 `.env` 文件配置：

```bash
# API优先级: 1=API易(推荐), 2=Google
API_PRIORITY=1

# API易 Nano Banana Pro
NANO_BANANA_API_KEY=your_key
NANO_BANANA_API_URL=https://api.apiyi.com/v1beta/models/gemini-3-pro-image-preview:generateContent

# Google API
GOOGLE_API_KEY=your_key
GOOGLE_API_URL=https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent
```

## 输出位置

```
~/finance-infographics/[主题名]/
└── infographic_YYYYMMDD_HHMMSS_000.png
```

## 提示词策略（已优化）

使用**"固定样式元素列表"式提示词**（第二版）：

### 核心结构

列出5项固定样式元素，每项包括具体检查维度：
1. **右上角logo**：位置、内容、颜色、大小、形状
2. **主标题**：字号64px、颜色、字体、背景、位置
3. **边框和卡片**：圆角、粗细、颜色、阴影、背景
4. **配色方案**：背景色、主色调、辅助色、文字色、强调色
5. **信息密度和布局**：密度水平、布局结构、间距、比例

### 改进历程

**第一版（三步流程）**：
- 观察→生成→处理
- 问题：logo和标题不一致、信息密度不够、绘图风格不一致

**第二版（固定元素列表）**：
- 直接列出5项固定元素和检查维度
- 明确禁止：❌logo、❌主标题、❌边框、❌配色、❌密度、❌风格
- 强调"唯一的不同是文字内容"

**核心转变**：
- 从"让AI观察"到"直接告诉AI具体要复刻什么"
- 从"抽象要求"到"具体检查点"
- 从"流程式"到"清单式"

详细说明见 [PROMPT.md](references/PROMPT.md)

## 常见问题

### Q: logo偶尔缺失怎么办？

A: 这是严重错误。检查参考图是否正确加载，重新生成。新提示词已加强logo约束。

### Q: 为什么不用文字描述设计规范？

A: 已经验证过，描述规范让AI读取会导致风格不稳定。直接看图效果更好。

### Q: 4K生成时内存溢出（Exit Code 137）？

A: 使用 `generate_one_by_one.py` 逐张生成，不要用 `batch_generate.py`。

### Q: 如何确保系列图风格一致？

A: 使用相同的参考图、相同的API、相同的 `-r` 分辨率参数。

## 文件结构

```
finance-infographic/
├── SKILL.md                    # 本文档
├── .env                        # API配置
├── content/                    # md文件存放目录
├── scripts/
│   ├── generate_one_by_one.py  # 逐张生成（推荐⭐⭐⭐⭐⭐）
│   └── batch_generate.py       # 批量生成（不推荐⭐⭐）
└── references/
    ├── PROMPT.md               # 提示词详细说明
    └── 微信图片_*.png          # 风格参考图
```

## 示例

### 示例1：生成单张图

```bash
python scripts/generate_one_by_one.py "content/IPO介绍.md" -r 4K --topic "IPO科普"
```

### 示例2：生成系列图

```bash
# 1. 创建3个md文件
# content/智谱AI是什么.md
# content/为什么成为第一.md
# content/普通人怎么参与.md

# 2. 逐张生成
python scripts/generate_one_by_one.py "content/智谱AI是什么.md" -r 4K --topic "智谱AI"
python scripts/generate_one_by_one.py "content/为什么成为第一.md" -r 4K --topic "智谱AI"
python scripts/generate_one_by_one.py "content/普通人怎么参与.md" -r 4K --topic "智谱AI"
```

输出到 `~/finance-infographics/智谱AI/`，3张图风格统一。

## 核心要点

1. **参考图最重要**：所有风格都来自参考图，确保参考图在 `references/` 目录
2. **固定元素列表法**：列出5项固定元素+检查维度，比"让AI观察"更有效
3. **低自由度约束**：❌明确列出6项禁止，减少AI自主发挥空间
4. **逐张生成稳定**：4K分辨率务必用 `generate_one_by_one.py`

## 实践验证

已验证方案：
- ✅ 直接看图（稳定）
- ✅ 固定元素列表（第二版优化）
- ❌ 描述设计规范（不稳定）
- ❌ 三步流程（约束力不足）

关键教训：**给AI的"观察自由度"太大会导致不一致**，必须直接列出要复刻的具体元素和检查维度。
