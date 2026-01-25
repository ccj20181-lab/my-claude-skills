---
name: xiaohongshu-to-pdf
description: >
  小红书图文笔记转PDF工具。当用户需要：
  (1) 将小红书笔记保存为PDF格式
  (2) 批量导出小红书图文内容
  (3) 归档小红书财经/理财/投资笔记

  触发关键词："小红书转PDF"、"保存笔记为PDF"、"导出小红书"、"小红书存档"
license: MIT
---

# 小红书笔记转PDF工具

## 功能概述

将小红书图文笔记转换为PDF文档，保留标题、作者、正文和所有图片。

## 使用场景

- 保存小红书笔记为PDF格式
- 批量导出小红书图文内容
- 归档小红书财经/理财/投资笔记

## 工作流程

### 1. 获取用户输入

用户可能提供：
- 小红书笔记URL（需要解析feed_id）
- feed_id + xsec_token（直接使用）
- 笔记关键词（需先搜索）

解析URL规则：
- URL格式: `https://www.xiaohongshu.com/explore/{feed_id}`
- 提取 `{feed_id}` 部分作为笔记ID

### 2. 获取笔记数据

使用MCP工具获取笔记详情：
```python
mcp__xiaohongshu__get_feed_detail(feed_id="{feed_id}", xsec_token="{xsec_token}")
```

返回数据包含：
- `title`: 笔记标题
- `desc`: 正文内容
- `author`: 作者信息（nickname等）
- `images`: 图片URL列表
- 互动数据（likes, collects等）

### 3. 生成PDF

执行转换脚本：
```bash
python3 /Users/henry/.claude/skills/xiaohongshu-to-pdf/scripts/xhs_to_pdf.py \
  --feed-id "{feed_id}" \
  --xsec-token "{xsec_token}" \
  --output "{output_path}"
```

脚本会：
1. 注册中文字体（自动检测系统字体）
2. 下载所有图片到临时目录
3. 使用reportlab生成PDF
4. PDF包含：标题、作者、正文、所有图片
5. 输出路径：默认为桌面，文件名格式 `{标题}_{时间戳}.pdf`

### 4. 输出结果

向用户返回：
- PDF文件完整路径
- 文件大小
- 笔记基本信息（标题、作者、图片数量）

## 使用示例

### 示例1: 直接提供feed_id

**用户输入**: "把笔记 6412345678 转成PDF"

**执行步骤**:
1. 请求用户提供xsec_token
2. 调用 `get_feed_detail` 获取笔记数据
3. 执行转换脚本
4. 返回PDF路径

### 示例2: 提供URL

**用户输入**: "把这个链接转PDF: https://www.xiaohongshu.com/explore/6412345678"

**执行步骤**:
1. 解析URL提取feed_id: `6412345678`
2. 请求xsec_token或尝试从已有数据获取
3. 后续流程同示例1

### 示例3: 批量导出

**用户输入**: "导出这个博主的最近5篇笔记为PDF"

**执行步骤**:
1. 获取用户主页（user_profile）
2. 遍历前5篇笔记
3. 逐个转换为PDF
4. 返回所有PDF路径列表

## 默认行为

### 输出路径
- 默认: `~/Desktop/`
- 可通过参数自定义: `--output /path/to/dir`

### 文件命名
- 格式: `{标题}_{时间戳}.pdf`
- 标题会清理特殊字符，限制长度为50字符

### 中文字体
- 自动检测系统字体（按优先级）：
  - **macOS**: PingFangSC-Regular.ttf (~/Library/Fonts/)，STHeiti Medium.ttc (/System/Library/Fonts/)
  - **Linux**: DroidSansFallbackFull.ttf, wqy-microhei.ttc
  - **Windows**: msyh.ttc, simsun.ttc
- 支持TTF和TTC格式（TTC会自动使用第一个子字体）
- 如果字体缺失，使用默认字体（中文可能显示异常）

### 错误处理
- 下载图片失败: 跳过该图片，继续处理
- 字体缺失: 使用默认字体（中文可能显示异常）
- MCP调用失败: 提示用户检查登录状态

## 故障排查

### PDF中文显示乱码

**症状**: PDF中的中文显示为方框或乱码

**解决方案**:

1. **检查字体是否已注册**
   - 运行脚本时应看到：`✓ 已注册中文字体: /path/to/font.ttf`
   - 如果看到：`⚠ 警告: 未找到可用的中文字体`，则需要进行第2步

2. **macOS用户**:
   - 优先安装PingFang SC字体到用户目录：`~/Library/Fonts/PingFangSC-Regular.ttf`
   - 或使用系统自带字体：`/System/Library/Fonts/STHeiti Medium.ttc`

3. **Linux用户**:
   ```bash
   sudo apt-get install fonts-wqy-microhei
   # 或
   sudo apt-get install fonts-wqy-zenhei
   ```

4. **Windows用户**:
   - 确保系统安装了Microsoft YaHei字体（通常默认已安装）
   - 检查 `C:/Windows/Fonts/msyh.ttc` 是否存在

5. **使用字体验证工具**:
   ```bash
   python3 /Users/henry/.claude/skills/xiaohongshu-to-pdf/scripts/check_fonts.py
   ```

### 图片下载失败

**症状**: PDF中缺少部分图片

**解决方案**:
- 检查网络连接
- 某些图片可能需要登录才能访问（确保小红书MCP已登录）
- 图片URL可能已过期

### MCP调用失败

**症状**: 脚本提示需要使用MCP工具获取数据

**解决方案**:
- 确保小红书MCP已登录：`mcp__xiaohongshu__get_login_qrcode`
- 检查xsec_token是否正确（从feed列表获取）

## 注意事项

1. **登录要求**: 使用前需要先登录小红书（使用 `mcp__xiaohongshu__get_login_qrcode`）
2. **xsec_token**: 从feed列表或笔记详情中获取
3. **依赖库**: 需要安装 `reportlab` 和 `requests`
4. **临时文件**: 使用后自动清理临时目录

## User-Learned Best Practices & Constraints

> **Auto-Generated Section**: This section is maintained by `skill-evolution-manager`. Do not edit manually.

### User Preferences
- Prefer urlDefault over urlPre for images.
- 批量转换时需要实时进度反馈
- 遇到错误时希望看到详细的失败原因
- 希望能够跳过无法访问的笔记而不是中断整个流程
- 批量处理应该先验证笔记可访问性再开始转换

### Known Fixes & Workarounds
- Fixed 403 Forbidden error when downloading images by adding Referer header.
- Added PIL support for WebP to PNG conversion.
- Preserve full image URLs for signature verification.
- 批量转换脚本必须先通过MCP获取笔记数据，不能直接调用xhs_to_pdf.py
- 图片大小限制需要同时控制宽度和高度：使用min(ratio_width, ratio_height)
- 添加max_height = 20 * cm限制，防止图片过大导致PDF生成失败
- 转换流程应该是：MCP获取数据 → 保存为JSON → 调用转换器 → 生成PDF

### Custom Instruction Injection

当用户要求批量转换小红书笔记时：1) 先使用webReader获取网页内容提取笔记列表 2) 使用mcp__xiaohongshu__search_feeds搜索笔记获取feed_id 3) 逐篇使用mcp__xiaohongshu__get_feed_detail获取详细数据 4) 保存为JSON文件 5) 调用convert_single_note.py转换 6) 提供详细的进度反馈和错误说明