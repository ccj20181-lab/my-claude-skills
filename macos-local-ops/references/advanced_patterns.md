# 高级用法模式

本文档介绍 macOS 本地操作 skill 的高级工作流自动化示例和配置技巧。

## 工作流自动化

### 场景 1: 每日整理下载文件夹

创建一个脚本 `cleanup_downloads.sh`:

```bash
#!/bin/bash
# 每日整理下载文件夹

SKILL_DIR="$HOME/.claude/skills/macos-local-ops/scripts"

# 将 PDF 移动到文档目录
python3 $SKILL_DIR/batch_ops.py move \
  --path ~/Downloads \
  --pattern "*.pdf" \
  --dest ~/Documents/PDFs \
  --execute

# 将图片移动到图片目录
python3 $SKILL_DIR/batch_ops.py move \
  --path ~/Downloads \
  --pattern "*.{jpg,png,gif}" \
  --dest ~/Pictures/Downloads \
  --execute

# 发送完成通知
python3 $SKILL_DIR/system_helpers.py notify \
  "整理完成" "下载文件夹已清理"
```

添加到 crontab:
```bash
# 每天下午 6 点执行
0 18 * * * ~/bin/cleanup_downloads.sh
```

### 场景 2: 项目快速启动

创建函数 `~/.zshrc`:

```bash
# 项目快速启动
function pjs() {
    cd ~/Development/$1
    python3 ~/.claude/skills/macos-local-ops/scripts/quick_open.py .
    code .
}
```

使用:
```bash
pjs my-project  # 打开项目目录并在 VS Code 中编辑
```

### 场景 3: 智能备份工作流

```bash
#!/bin/bash
# 智能备份脚本

SOURCE_DIR="$HOME/Documents"
BACKUP_DIR="$HOME/Backup/$(date +%Y%m%d)"
SKILL_DIR="$HOME/.claude/skills/macos-local-ops/scripts"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 查找最近修改的文件并复制
python3 $SKILL_DIR/smart_search.py "." \
  --path "$SOURCE_DIR" \
  --type name | head -20 | while read file; do
    cp "$file" "$BACKUP_DIR/"
done

# 发送通知
python3 $SKILL_DIR/system_helpers.py notify \
  "备份完成" "已备份到 $BACKUP_DIR"
```

## 智能别名配置

### Shell 别名

在 `~/.zshrc` 中添加:

```bash
# quick_open 别名
alias o='python3 ~/.claude/skills/macos-local-ops/scripts/quick_open.py'
alias desk='o d'
alias doc='o doc'
alias down='o down'

# smart_search 别名
alias s='python3 ~/.claude/skills/macos-local-ops/scripts/smart_search.py'
alias sn='s --type name'
alias sc='s --type content'

# batch_ops 别名
alias batch='python3 ~/.claude/skills/macos-local-ops/scripts/batch_ops.py'
alias brename='batch rename'
alias bmove='batch move'
alias bcopy='batch copy'

# system_helpers 别名
alias sys='python3 ~/.claude/skills/macos-local-ops/scripts/system_helpers.py'
alias notify='sys notify'
alias clip='sys clipboard'
alias shot='sys screenshot'
```

### 自定义快捷路径

在脚本中添加更多别名:

编辑 `scripts/quick_open.py`:

```python
ALIASES = {
    'd': '~/Desktop',
    'doc': '~/Documents',
    'down': '~/Downloads',
    'pics': '~/Pictures',
    'dev': '~/Development',
    'proj': '~/Projects',
    'notes': '~/Documents/Notes',
    'tmp': '/tmp',
}
```

## 组合命令模式

### 模式 1: 搜索后打开

```bash
# 搜索最近修改的代码文件并打开
file=$(python3 ~/.claude/skills/macos-local-ops/scripts/smart_search.py \
  ".py" --path ~/Documents --type name | head -1)

python3 ~/.claude/skills/macos-local-ops/scripts/quick_open.py "$file"
```

### 模式 2: 批量处理后通知

```bash
# 批量重命名照片
python3 ~/.claude/skills/macos-local-ops/scripts/batch_ops.py rename \
  --path ~/Desktop \
  --pattern "^IMG_" \
  --replacement "photo_" \
  --execute && \
python3 ~/.claude/skills/macos-local-ops/scripts/system_helpers.py notify \
  "重命名完成" "已处理桌面照片文件"
```

### 模式 3: 搜索结果批量移动

```bash
# 搜索所有 PDF 并移动到指定目录
python3 ~/.claude/skills/macos-local-ops/scripts/smart_search.py \
  ".pdf" --path ~/Downloads | while read file; do
  mv "$file" ~/Documents/PDFs/
done
```

## 与其他工具集成

### fzf 集成（模糊搜索）

```bash
# 安装 fzf
brew install fzf

# 使用 fzf 交互式选择文件
function sf() {
  file=$(python3 ~/.claude/skills/macos-local-ops/scripts/smart_search.py \
    "$1" --type name | fzf)

  if [ -n "$file" ]; then
    python3 ~/.claude/skills/macos-local-ops/scripts/quick_open.py "$file"
  fi
}
```

### Alfred 集成

创建 Alfred Workflow，运行脚本:

```bash
# 查询参数: {query}
python3 ~/.claude/skills/macos-local-ops/scripts/smart_search.py \
  "{query}" --type name
```

### Hazel 集成

在 Hazel 中添加规则，执行脚本:

```bash
# 当下载文件夹有新 PDF 时
python3 ~/.claude/skills/macos-local-ops/scripts/batch_ops.py move \
  --path ~/Downloads \
  --pattern "*.pdf" \
  --dest ~/Documents/PDFs \
  --execute
```

## 性能优化

### 1. 限制搜索范围

```bash
# 只搜索特定目录，而不是全局
python3 smart_search.py "项目" --path ~/Documents
```

### 2. 使用内容搜索时排除目录

```bash
# 创建 .rgignore 文件
echo "node_modules/" > ~/.rgignore
echo ".git/" >> ~/.rgignore
```

### 3. 批量操作分块处理

```bash
# 分批处理大量文件
for i in {1..10}; do
  python3 batch_ops.py rename \
    --path ~/Photos \
    --pattern "IMG_${i}*" \
    --replacement "photo_${i}_" \
    --execute
done
```

## 调试技巧

### 查看详细输出

```bash
# 使用 bash -x 调试脚本
bash -x your_workflow.sh
```

### 测试模式

```bash
# 先使用 --dry-run 预览
python3 batch_ops.py rename --path ~/Desktop --pattern "^IMG_" --replacement "photo_"

# 确认后再执行
python3 batch_ops.py rename --path ~/Desktop --pattern "^IMG_" --replacement "photo_" --execute
```

## 安全建议

1. **备份重要数据**: 在执行批量操作前先备份
2. **使用版本控制**: 对代码文件使用 Git
3. **测试模式**: 优先使用 `--dry-run` 预览
4. **确认操作**: 避免使用 `--force`，除非完全确定

## 进一步学习

- macOS 自动化: `man osascript`
- Spotlight 搜索: `man mdfind`
- ripgrep 高级用法: `man rg`
- Shell 脚本编程: `man bash`
