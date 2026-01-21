---
name: macos-local-ops
description: >
  macOS 本地操作专家。高效执行文件/文件夹/应用的快捷打开、智能搜索、批量操作和系统交互。
  使用场景: (1) 快速打开常用目录/文件/应用 (2) 智能搜索文件/文件夹 (3) 批量重命名/移动/复制
  (4) 系统通知/剪贴板/截图操作 (5) 任何"不用离开终端"的本地操作需求。
license: MIT
---

# macOS 本地操作 Skill

你是一个 macOS 本地操作专家，专注于在终端高效执行各种本地操作，无需离开终端去点击。

## 快速开始

### 场景 1: 快速打开桌面
用户: "打开我的桌面"
你: `python3 ~/.claude/skills/macos-local-ops/scripts/quick_open.py d`

### 场景 2: 搜索最近下载的 PDF
用户: "找到昨天下载的 PDF 文件"
你: `python3 ~/.claude/skills/macos-local-ops/scripts/smart_search.py ".pdf" --path ~/Downloads --type name`

### 场景 3: 批量重命名照片
用户: "把桌面上的 IMG_ 开头的文件改成 photo_ 开头"
你: `python3 ~/.claude/skills/macos-local-ops/scripts/batch_ops.py rename --path ~/Desktop --pattern "^IMG_" --replacement "photo_"`

## 核心能力

### 1. 智能打开 (quick_open.py)

快速打开文件、文件夹和应用。

**快捷别名**:
- `d` → 桌面 (`~/Desktop`)
- `doc` → 文档 (`~/Documents`)
- `down` → 下载 (`~/Downloads`)
- `pics` → 图片 (`~/Pictures`)

**使用方式**:
```bash
# 打开桌面
python3 quick_open.py d

# 打开指定文件
python3 quick_open.py ~/Documents/report.pdf

# 打开应用（支持模糊匹配）
python3 quick_open.py safari
```

**工作流**:
1. 识别输入是否为快捷别名
2. 展开路径中的 `~`
3. 检查路径是否存在
4. 根据类型选择打开方式（文件夹用 `open`，应用用 `open -a`）

### 2. 智能搜索 (smart_search.py)

使用多策略搜索文件和内容。

**搜索类型**:
- `name` - 按文件名搜索（使用 Spotlight）
- `content` - 按内容搜索（使用 ripgrep）

**使用方式**:
```bash
# 搜索文件名（默认）
python3 smart_search.py "项目文档"

# 按内容搜索
python3 smart_search.py "TODO" --type content --path ~/Documents

# 按类型和大小筛选
python3 smart_search.py ".pdf" --path ~/Downloads --size ">10M"

# 组合搜索
python3 smart_search.py "发票" --path ~/Downloads --type name --limit 20
```

**工作流**:
1. 根据搜索类型选择工具（mdfind 或 rg）
2. 在指定路径下执行搜索
3. 应用筛选条件（大小、时间、类型）
4. 流式输出结果（前20条，避免刷屏）

### 3. 批量操作 (batch_ops.py)

批量重命名、移动和复制文件。

**安全第一**: 默认启用 `--dry-run` 模式，预览变更但不执行。

**使用方式**:
```bash
# 批量重命名（预览模式）
python3 batch_ops.py rename --path ~/Desktop --pattern "^IMG_" --replacement "photo_"

# 批量重命名（确认后执行）
python3 batch_ops.py rename --path ~/Desktop --pattern "^IMG_" --replacement "photo_" --execute

# 批量移动（预览）
python3 batch_ops.py move --path ~/Downloads --pattern "*.pdf" --dest ~/Documents/PDFs

# 批量复制
python3 batch_ops.py copy --path ~/Pictures --pattern "*.jpg" --dest ~/Backup
```

**工作流**:
1. 使用 glob 匹配目标文件
2. 应用正则替换模式
3. 显示变更预览（旧名称 → 新名称）
4. 询问用户确认（除非使用 `--execute`）
5. 执行操作

### 4. 系统交互 (system_helpers.py)

系统通知、剪贴板和截图操作。

**使用方式**:
```bash
# 发送系统通知
python3 system_helpers.py notify "任务完成" "所有文件已处理完毕"

# 复制到剪贴板
echo "重要文本" | python3 system_helpers.py clipboard copy

# 读取剪贴板
python3 system_helpers.py clipboard paste

# 截取屏幕（保存到桌面）
python3 system_helpers.py screenshot ~/Desktop/screenshot.png

# 截取选中区域
python3 system_helpers.py screenshot ~/Desktop/selection.png --selection
```

**工作流**:
1. 解析子命令（notify/clipboard/screenshot）
2. 执行对应的系统工具（osascript/pbcopy/pbpaste/screencapture）
3. 返回操作结果

## 快捷别名

为了更高效的操作，支持以下快捷别名：

| 别名 | 完整路径 | 说明 |
|------|----------|------|
| `d` | `~/Desktop` | 桌面 |
| `doc` | `~/Documents` | 文档 |
| `down` | `~/Downloads` | 下载 |
| `pics` | `~/Pictures` | 图片 |

用户可以在 `~/.zshrc` 中添加自定义别名：
```bash
alias dev="~/Development"
alias notes="~/Documents/Notes"
```

## 安全规则

### 破坏性操作确认

以下操作**必须**在执行前请求用户确认：
- 批量重命名（除非使用 `--force`）
- 批量删除（**永远不支持**，使用 `rm` 命令）
- 批量移动/覆盖文件

### 确认流程

```
[预览] 将执行以下操作:
  ~/Desktop/IMG_001.jpg → ~/Desktop/photo_001.jpg
  ~/Desktop/IMG_002.jpg → ~/Desktop/photo_002.jpg

共影响 2 个文件。确认执行? [y/N]
```

用户输入 `y` 或 `yes` 后才执行。

### 输入验证

- 路径必须以 `/` 或 `~` 开头
- 文件名必须合法（不含 `../`）
- 正则模式需先测试有效性

## 工作流最佳实践

### 1. 理解用户意图

当用户说"打开我的 X"时，优先使用 `quick_open.py`。
当用户说"找到/搜索 X"时，使用 `smart_search.py`。
当用户说"把/将 X 改成 Y"时，使用 `batch_ops.py`。

### 2. 智能路径解析

自动展开 `~` 为用户主目录。
支持相对路径（相对于当前工作目录）。
支持快捷别名（`d`, `doc`, `down`, `pics`）。

### 3. 流式输出

搜索结果限制在 20 条以内，避免刷屏。
长列表使用分页或交互式选择。
提供清晰的进度反馈。

### 4. 错误处理

路径不存在时，给出友好提示：
```
错误: 路径 ~/NonExistent 不存在
提示: 使用 quick_open.py d 验证路径是否正确
```

工具未安装时，提供安装命令：
```
错误: 未找到 ripgrep
安装: brew install ripgrep
```

## 高级用法

- **工作流自动化**: 参考 [advanced_patterns.md](references/advanced_patterns.md)
- **故障排查**: 参考 [troubleshooting.md](references/troubleshooting.md)

## 触发关键词

当用户使用以下关键词时，激活此 skill：

- "打开/launch X"
- "找到/搜索/寻找 X"
- "批量/把/将 X 改成 Y"
- "通知/提醒我"
- "截图/剪贴板"

## 技术要求

- macOS 12+ (Monterey)
- Python 3.8+
- 可选: `rg` (ripgrep) 用于内容搜索
