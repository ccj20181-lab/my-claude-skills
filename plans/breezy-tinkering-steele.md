# macOS 公文/办公常用字体一键安装计划

本计划旨在帮助用户自动下载并安装 macOS 缺失的公文和办公常用字体，解决跨平台文档乱码问题。

## 目标字体列表
- **核心公文四大金刚**: 仿宋_GB2312, 仿宋, 方正小标宋简体, 楷体_GB2312
- **常用办公字体**: 宋体, 黑体, 微软雅黑, 等线/思源黑体, 隶书, 幼圆

## 实施步骤

### 1. 准备工作
- 创建临时工作目录: `~/Downloads/claude_font_install_temp`

### 2. 下载字体资源
我们将使用 GitHub 上现有的字体集合仓库：
- **仓库 A (公文专用)**: `guorenxi/MacFonts` (包含仿宋_GB2312, 方正小标宋简体等)
- **仓库 B (Windows 常用)**: `zhyounger/FontsFromWindows` (包含宋体, 黑体, 微软雅黑, 隶书等)

使用 `git clone --depth 1` 命令下载以节省时间和流量。

### 3. 安装字体
- 遍历下载的目录，查找匹配的 `.ttf` 或 `.otf` 文件。
- 将字体文件复制到用户的字体目录: `~/Library/Fonts/`。
- *注意*: `~/Library/Fonts/` 是用户级字体目录，通常不需要 sudo 权限。

### 4. 验证与清理
- 检查 `~/Library/Fonts/` 下是否存在目标字体文件。
- 删除临时目录 `~/Downloads/claude_font_install_temp`。
- 提示用户重启 Word/WPS 以生效。

## 验证计划
- 运行 `ls -l ~/Library/Fonts/` 配合 grep 检查特定字体文件是否存在。
