# 故障排查指南

本文档介绍 macOS 本地操作 skill 的常见问题和解决方案。

## Spotlight 索引问题

### 问题 1: mdfind 搜索不到文件

**症状**: 使用 `smart_search.py` 搜索时返回空结果

**原因**: Spotlight 索引未建立或损坏

**解决方案**:

```bash
# 1. 检查 Spotlight 是否启用
sudo mdutil -s /

# 2. 如果显示 "Indexing disabled"，重新启用
sudo mdutil -i on /

# 3. 重建索引
sudo mdutil -E /

# 4. 等待索引重建（可能需要几分钟）
# 查看索引进度
mdutil -s /
```

### 问题 2: 某个目录不被索引

**症状**: 特定目录下的文件搜索不到

**原因**: 目录在 Spotlight 隐私设置中

**解决方案**:

```bash
# 方法 1: 系统设置
# 系统设置 → Siri 与 Spotlight → 隐私
# 移除对应的目录

# 方法 2: 命令行强制索引特定目录
mdimport ~/Documents
```

## 权限问题

### 问题 3: 无法执行脚本

**症状**: `Permission denied` 错误

**解决方案**:

```bash
# 给脚本添加执行权限
chmod +x ~/.claude/skills/macos-local-ops/scripts/*.py

# 验证权限
ls -l ~/.claude/skills/macos-local-ops/scripts/
```

### 问题 4: 无法访问某些目录

**症状**: `Permission denied` 或操作被拒绝

**解决方案**:

```bash
# 1. 检查目录权限
ls -ld ~/Desktop

# 2. 如果需要，修复权限
chmod 755 ~/Desktop

# 3. 对于系统目录，使用 sudo（谨慎）
sudo python3 script.py
```

## 依赖工具问题

### 问题 5: ripgrep 未安装

**症状**: `未找到 ripgrep (rg)` 错误

**解决方案**:

```bash
# 使用 Homebrew 安装
brew install ripgrep

# 验证安装
rg --version

# 重新运行内容搜索
python3 ~/.claude/skills/macos-local-ops/scripts/smart_search.py \
  "关键词" --type content
```

### 问题 6: Python 版本过低

**症状**: 脚本运行报语法错误

**解决方案**:

```bash
# 检查 Python 版本
python3 --version

# 如果版本 < 3.8，升级 Python
brew install python@3.11

# 确保使用正确的 Python
which python3
```

## 批量操作问题

### 问题 7: 批量重命名失败

**症状**: 文件没有被重命名

**可能原因**:

1. 正则表达式错误
```bash
# 测试正则表达式
python3 -c "import re; print(re.sub(r'^IMG_', 'photo_', 'IMG_001.jpg'))"
```

2. 目标文件已存在
```bash
# 检查目标文件
ls -la ~/Desktop/photo_*
```

3. 权限不足
```bash
# 检查文件权限
ls -l ~/Desktop/IMG_*
```

### 问题 8: 目标目录不存在

**症状**: `错误: 目标目录不存在`

**解决方案**:

```bash
# 创建目标目录
mkdir -p ~/Documents/PDFs
mkdir -p ~/Backup

# 重新执行批量操作
python3 batch_ops.py move --path ~/Downloads --pattern "*.pdf" --dest ~/Documents/PDFs
```

## 系统交互问题

### 问题 9: 通知不显示

**症状**: 通知命令执行成功但看不到通知

**解决方案**:

```bash
# 1. 检查通知权限
# 系统设置 → 通知 → Terminal（或你的终端应用）
# 确保允许通知

# 2. 测试通知
osascript -e 'display notification "测试" with title "通知测试"'

# 3. 尝试不同的声音
python3 system_helpers.py notify "测试" "消息" --sound Ping
```

### 问题 10: 截图保存失败

**症状**: `错误: 截图失败`

**解决方案**:

```bash
# 1. 检查目录权限
mkdir -p ~/Desktop
ls -ld ~/Desktop

# 2. 检查磁盘空间
df -h

# 3. 测试截图命令
screencapture ~/Desktop/test.png
```

## 性能问题

### 问题 11: 搜索很慢

**症状**: `smart_search.py` 响应时间长

**解决方案**:

```bash
# 1. 限制搜索范围
python3 smart_search.py "关键词" --path ~/Documents

# 2. 使用更具体的搜索词
python3 smart_search.py "项目文档"  # 而不是 "文档"

# 3. 限制结果数量
python3 smart_search.py "关键词" --limit 10

# 4. 对于内容搜索，使用 ripgrep
python3 smart_search.py "TODO" --type content --path ~/Documents
```

### 问题 12: 批量操作卡住

**症状**: 批量操作长时间无响应

**解决方案**:

```bash
# 1. 使用 Ctrl+C 中断
# 2. 分批处理
python3 batch_ops.py rename --path ~/Photos --pattern "IMG_0*" --replacement "photo_0_"

# 3. 使用 --execute 前先测试
python3 batch_ops.py rename --path ~/Photos --pattern "IMG_0*" --replacement "photo_0_"
```

## 日志和调试

### 启用详细输出

```bash
# 在脚本中添加调试信息
python3 -u script.py 2>&1 | tee debug.log

# 使用 bash 调试模式
bash -x your_workflow.sh
```

### 检查系统日志

```bash
# 查看终端日志
log show --predicate 'process == "Terminal"' --last 1h

# 查看 Spotlight 索引日志
log show --predicate 'subsystem == "com.apple.metadata.mds"' --last 1h
```

## 常见错误信息

### `command not found: python3`

```bash
# 安装 Python
brew install python

# 或使用系统自带
/usr/bin/python3 script.py
```

### `mdfind: command not found`

```bash
# mdfind 是系统自带工具，检查是否在 PATH 中
which mdfind
# 应该输出: /usr/bin/mdfind
```

### `osascript: command not found`

```bash
# osascript 是系统自带工具
which osascript
# 应该输出: /usr/bin/osascript
```

## 获取帮助

如果以上方案都无法解决问题：

1. 检查 macOS 版本:
```bash
sw_vers
```

2. 检查脚本版本:
```bash
head -5 ~/.claude/skills/macos-local-ops/scripts/*.py
```

3. 查看完整错误信息:
```bash
python3 script.py --help
python3 script.py 2>&1 | tee error.log
```

4. 重新安装 skill:
```bash
cd ~/.claude/skills/macos-local-ops
git pull origin main
```

## 预防性维护

### 定期重建索引

```bash
# 添加到 crontab，每月重建一次
0 0 1 * * sudo mdutil -E /
```

### 保持工具更新

```bash
# 更新 Homebrew 工具
brew upgrade ripgrep python

# 更新 skill
cd ~/.claude/skills/macos-local-ops
git pull
```

### 备份配置

```bash
# 备份 skill 配置
cp -r ~/.claude/skills/macos-local-ops ~/backup/
```
