---
name: finance-infographic
version: 2.1.0
description: 财经科普信息图生成器。使用 Gemini 3 Pro Image Preview 生成与参考图风格一致的信息图。支持主标题定制、双 API（Google官方/API易），按主题分类存放。用于将财经文案转换为图文并茂的信息图。
triggers:
  - 财经信息图
  - 生成信息图
  - finance infographic
author: finance-team
---

# 财经信息图生成器 v2.1

---

## ⚠️ 核心规则（必读！）

### 规则 #1: 使用用户的小标题作为md第一行

**这是最重要规则！**

md文件的第一行 `# 标题` 会直接以64px字号显示在图片上。

✅ **正确做法：使用用户原始文案中的小标题**

用户文案：
```
最新消息

截至2026年1月27日，白银价格突破108美元/盎司...
```

创建md文件：
```markdown
# 最新消息          ← ✅ 直接使用用户的小标题

截至2026年1月27日，白银价格突破108美元/盎司...
```

❌ **错误做法：AI自己概括主题**

```markdown
# 白银暴涨          ← ❌ 不要自己概括
## 最新消息
```

**记住：用户的小标题 = md第一行 = 图片主标题**

---

### 规则 #2: 推荐工作流程（减少返工）

```
步骤1: 创建md文件
  ✅ 第一行使用用户的小标题（如：最新消息）
  ✅ 使用 ## 分段，(1)(2) 或 - 列表

步骤2: 生成1张测试图
  python scripts/main.py "content/最新消息.md" --topic "白银暴涨"

步骤3: 检查质量（必须检查！）
  ✅ 右上角 logo
  ✅ 右下角标记
  ✅ 标题样式正确
  ✅ 信息密度合理
  如有问题，重新生成

步骤4: 确认后批量生成
  python scripts/main.py content/*.md --no-interactive
```

**为什么要先生成1张？**
- 避免批量生成后发现全部有问题
- 快速验证风格和样式是否正确
- 节省时间，减少返工

---

### 规则 #3: 生成后必须检查的项目

每张图必须包含：
- ✅ **右上角 logo**（品牌标识）
- ✅ **右下角标记**（品牌标识）
- ✅ **主标题样式**（与参考图一致）

**常见问题及解决：**
- logo/右下角标记缺失 → 重新生成（AI随机性）
- 标题样式不对 → 检查md第一行，重新生成
- 风格不一致 → 重新生成2-3次，选择最好的
- 信息密度低 → 增加数据点、对比、列表

---

## 快速开始

```bash
# 基础用法
python scripts/main.py "content/主题.md" --topic "主题名"

# 指定主标题（适用于结构化文案）
python scripts/main.py "md1.md" "md2.md" --titles "是什么" "为什么" --topic "主题"

# 交互式模式（推荐，支持确认步骤）
python scripts/main.py "content/主题.md" --interactive
```

## 核心功能

| 功能 | 说明 |
|------|------|
| 风格一致 | 对着参考图生成，多图风格统一 |
| 配置管理 | 支持 `config.yaml` 和 `.env`，不再硬编码路径 |
| 会话管理 | 按日期和主题自动组织输出 (`/Users/henry/Desktop/秒懂金融学院/信息图输出/YYYYMMDD-Topic/`) |
| 交互流程 | 支持 "分析 -> 确认 -> 生成" 的工作流 |
| 跨平台 | 完美支持 macOS、Windows 和 Linux |
| 双 API | Google 官方 / API易 可切换 |

## 命令行参数

### 主入口脚本：`scripts/main.py`

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `md_files` | md 文件路径列表（必选） | - |
| `--topic, -t` | 主题名称（文件夹名） | default |
| `--titles` | 主标题列表（与md文件对应） | 无 |
| `--no-interactive` | 禁用交互式模式 | 默认启用交互 |
| `--dry-run` | 仅生成提示词，跳过图片生成 | 关闭 |
| `--debug` | 开启调试日志 | 关闭 |
| `--provider` | API 提供商 (google/nanobanana) | 按配置 |
| `--output, -o` | 输出目录 | output/ |

## 配置系统

推荐使用配置文件管理设置。

### 配置优先级

1. **命令行参数** - 最高优先级
2. **环境变量** (`.env`)
3. **项目配置** (`.finance-infographic/config.yaml`)
4. **用户配置** (`~/.finance-infographic/config.yaml`)
5. **默认配置** (`config.yaml.example`)

### 示例配置 (config.yaml)

```yaml
api:
  provider: nanobanana
  # key 和 url 也可在此配置，或使用环境变量

output:
  base_dir: "output"  # 相对路径或绝对路径
  resolution: "4K"
```

### 环境变量 (.env)

```bash
# API 优先级
API_PRIORITY=1

# API易 Nano Banana Pro
NANO_BANANA_API_KEY=sk-30hw0QuR0UD2t6ub808670A2Da6641159aDbAe54519f6743
NANO_BANANA_API_URL=https://api.apiyi.com/v1beta/models/gemini-3-pro-image-preview:generateContent

# Google API
GOOGLE_API_KEY=your_google_key_here
GOOGLE_API_URL=https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent

# 输出目录（可选）
FINANCE_OUTPUT_DIR=/path/to/output
```

## 文件结构

```
finance-infographic/
├── SKILL.md                # 入口文档
├── config.yaml.example     # 配置模板
├── .env.example            # 环境变量模板
├── requirements.txt        # Python 依赖
│
├── src/                    # 核心代码模块
│   ├── __init__.py
│   ├── config.py           # 配置加载
│   ├── session.py          # 会话管理
│   ├── workflow.py         # 工作流引擎
│   ├── api.py              # API 客户端
│   ├── prompts.py          # 提示词生成
│   └── utils.py            # 工具函数
│
├── scripts/
│   ├── main.py             # ⭐ 主入口脚本（推荐使用）
│   ├── batch_generate.py   # [已废弃] 旧版批量生成
│   └── generate_one_by_one.py  # [已废弃] 旧版逐张生成
│
├── references/
│   ├── templates/          # 提示词模板
│   │   └── base_prompt.md
│   ├── PROMPT.md           # 提示词详细说明
│   └── *.png               # 风格参考图
│
├── content/                # 用户 md 文件目录
│   └── *.md
│
├── examples/               # 示例文件
│   └── structured_example.md
│
└── output/                 # 默认输出目录
    └── YYYYMMDD-Topic/     # 会话目录
        ├── images/         # 生成的图片
        ├── source/         # 原始文案
        └── prompts/        # 使用的提示词
```

## 文案格式

### ⚠️ 重要：md第一行使用什么？

**md文件的第一行会直接显示在图片上（字号64px）**

**应该使用什么？**

✅ 使用**用户原始文案中的小标题**

示例：
```
用户文案：
  最新消息
  截至2026年1月27日，白银价格突破108美元/盎司...

正确做法：
  # 最新消息          ← 直接使用用户的小标题
  ## 截至2026年1月27日
  ...
```

❌ 不要自己概括主题
```
# 白银暴涨          ← ❌ 错误：这是AI概括的
## 最新消息
...
```

**记住：使用用户原始文案中的小标题，不要擅自修改或概括！**

---

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

对于结构化文案（如：是什么、为什么、怎么办），建议拆分成多个 md 文件：

**用户提供的文案结构：**
```
最新消息
[内容...]

是什么
[内容...]
```

**创建md文件时，第一行使用用户的小标题：**

**文件1 (最新消息.md):**
```markdown
# 最新消息          ← 使用用户的小标题
[内容...]
```

**文件2 (是什么.md):**
```markdown
# 是什么            ← 使用用户的小标题
[内容...]
```

然后使用 `--titles` 参数指定主标题（应与md文件第一行完全一致）：

```bash
python scripts/main.py \
  "是什么.md" "为什么.md" "怎么办.md" \
  --titles "是什么" "为什么" "怎么办" \
  --topic "智谱AI"
```

## 使用示例

### 示例1：基础单图生成

```bash
python scripts/main.py "content/文章.md" --topic "IPO"
```

### 示例2：结构化多图生成（推荐）

```bash
python scripts/main.py \
  "content/是什么.md" \
  "content/为什么.md" \
  "content/怎么办.md" \
  --titles "是什么" "为什么" "怎么办" \
  --topic "智谱AI上市"
```

### 示例3：指定输出目录

```bash
python scripts/main.py "content/主题.md" \
  --topic "主题" \
  --output ~/Desktop/infographics
```

### 示例4：非交互模式（适合脚本调用）

```bash
python scripts/main.py "content/主题.md" --no-interactive --topic "主题"
```


## 提示词原则

生成图片时使用以下核心原则：

1. **固定元素一致性**：右上角logo、右下角标识、主标题必须严格一致
2. **风格复刻**：对着参考图生成，如出同一人之手
3. **内容忠实**：逐字使用 md 文件中的文字
4. **图文并茂**：文字与视觉元素平衡，相得益彰
5. **主标题定制**：支持为每张图指定不同的主标题

详细提示词模式参见 [PROMPT.md](references/PROMPT.md)。

## 输出

图片保存位置由 `config.yaml` 中的 `output.base_dir` 决定：
- 默认位置：`finance-infographic/output/YYYYMMDD-Topic/`
- 自动分类：所有生成物（图片、提示词、源码）都会自动整理到该会话目录下

## 注意事项

### 质量检查（重要！）

生成后请检查每张图是否包含：

**必须有：**
- ✅ 右上角 logo
- ✅ 右下角标记
- ✅ 主标题样式正确

**应该有：**
- ✅ 整体风格与参考图一致
- ✅ 信息密度合理（不太空也不太挤）
- ✅ 内容层次分明

**常见问题解决：**
- logo/右下角标记缺失 → 重新生成
- 标题样式不对 → 检查md第一行，重新生成
- 风格不一致 → 重新生成2-3次
- 信息密度低 → 参考 examples/structured_example.md

---

### 主标题建议
- 结构化文案建议使用 `--titles` 参数
- 主标题应使用用户的小标题（如：最新消息、是什么等）
- 不要AI自己概括主题
- `--titles` 参数应与md文件第一行完全一致

### 质量保证
- 如果发现 logo 缺失，需要重新生成
- 如果风格不一致，检查参考图是否正确加载，重新生成
- 建议先生成1张测试图，确认后再批量生成

---

## 脚本说明

| 脚本 | 状态 | 用途 |
|------|------|------|
| `main.py` | ⭐ 推荐 | 主入口，完整功能支持 |
| `batch_generate.py` | ⚠️ 已废弃 | 旧版批量生成（仅兼容保留） |
| `generate_one_by_one.py` | ⚠️ 已废弃 | 旧版逐张生成（仅兼容保留） |

> **注意**：旧版脚本仍可使用，但会显示废弃警告。建议迁移到 `main.py`。

---

## User-Learned Best Practices & Constraints

> **Auto-Generated Section**: This section is maintained by `skill-evolution-manager`. Do not edit manually.

### User Preferences
- 生成后应主动打开输出文件夹让用户预览
- 单张图片需要重新生成时，只需传入对应的单个 md 文件
- 生成图片分辨率默认为 4K

### Known Fixes & Workarounds (v2.1)
- ✅ 移除了所有硬编码路径，改为 config 驱动
- ✅ 增加 Human-in-the-Loop 交互确认机制
- ✅ 会话输出自动归档到 output/YYYYMMDD-Topic
- ✅ 旧脚本重构为 src/ 模块的薄包装，保持向后兼容
- ✅ 移除了自动删除用户文件的危险代码
- ✅ 改进了异常处理和错误提示

### Custom Instruction Injection
如需指定自定义输出目录，使用 `-o` 参数：
```bash
python scripts/main.py "file.md" -o ~/Desktop/infographics --topic "主题"
```
