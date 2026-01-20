# 钉钉/飞书文档转 PDF Skill

## 功能概述

这是一个专门用于将钉钉和飞书在线文档转换为 PDF 格式的工具。通过 Playwright 自动化浏览器操作，采用分屏截图+拼接方案，完美处理懒加载内容。

### 支持的平台

- **钉钉文档** (alidocs.dingtalk.com) - 完全支持，已验证
- **飞书文档** (feishu.cn / docs.feishu.cn) - 基本支持，待验证

### 核心特性

- 自动检测平台类型（钉钉/飞书）
- 智能处理 iframe 结构（钉钉文档）
- 分屏滚动截图，解决懒加载问题
- Python PIL 拼接长图
- 高质量 PDF 输出
- 支持自定义参数（屏数、滚动等待时间等）

## 技术方案

### 为什么需要特殊处理？

钉钉/飞书文档采用虚拟滚动和懒加载技术，传统的 `page.pdf()` 和 `page.screenshot({ fullPage: true })` 无法获取完整内容。

### 技术挑战

1. **iframe 结构** - 钉钉文档内容在嵌套的 iframe 中
2. **懒加载** - 内容按需加载，滚动时动态渲染
3. **高度检测失效** - scrollHeight 始终返回固定值（1080px）
4. **无限滚动模拟** - 需要精确控制滚动距离和等待时间

### 解决方案

```
1. 提取 iframe URL（如果存在）
2. 设置固定视口（1920 x 1080）
3. 分屏滚动截图（固定 21 屏或自定义）
4. Python PIL 拼接长图
5. 转换为 PDF（sips/convert）
```

## 安装

### 前置要求

- Node.js >= 18
- Python 3.x (带 PIL/Pillow 库)
- macOS 或 Linux 系统

### 安装依赖

```bash
cd ~/.claude/skills/dingtalk-lark-pdf
npm install
pip3 install Pillow
```

## 使用方法

### 基本用法

```bash
node scripts/convert.js --url "https://alidocs.dingtalk.com/i/nodes/..." --output ~/Desktop/
```

### 完整参数

```bash
node scripts/convert.js \
  --url "文档 URL" \
  --output ~/Desktop/ \
  --platform dingtalk \
  --screenshots 21 \
  --scroll-wait 3000 \
  --initial-wait 15000
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--url` | 文档 URL（必需） | - |
| `--output` | 输出目录（必需） | - |
| `--platform` | 平台类型（dingtalk/lark/auto） | auto |
| `--screenshots` | 截图屏数 | 21 |
| `--scroll-wait` | 每屏滚动等待时间（毫秒） | 3000 |
| `--initial-wait` | 初始加载等待时间（毫秒） | 15000 |

## 使用示例

### 钉钉文档

```bash
node scripts/convert.js \
  --url "https://alidocs.dingtalk.com/i/nodes/DnRL6jAJMGrnOmD5cGqrdpPxWyMoPYe1" \
  --output ~/Desktop/
```

### 飞书文档

```bash
node scripts/convert.js \
  --url "https://feishu.cn/docx/xxxxx" \
  --platform lark \
  --output ~/Desktop/
```

### 长文档（增加屏数）

```bash
node scripts/convert.js \
  --url "文档 URL" \
  --screenshots 30 \
  --scroll-wait 4000 \
  --output ~/Desktop/
```

## 工作流程

```
1. 平台检测
   └─> 根据 URL 判断是钉钉还是飞书

2. 提取 iframe URL（钉钉专用）
   └─> 访问主页获取 iframe src

3. 初始化浏览器
   └─> Playwright 启动 Chromium
   └─> 设置视口 1920x1080

4. 分屏截图
   └─> 滚动到指定位置（每屏 1080px）
   └─> 等待渲染完成
   └─> 截图保存

5. 拼接长图
   └─> Python PIL 垂直拼接所有截图

6. 转换 PDF
   └─> sips (macOS) 或 convert (Linux)
```

## 故障排查

### 问题：截图数量不足

**症状**：生成的 PDF 缺少内容

**解决方案**：
```bash
# 增加截图屏数
node scripts/convert.js --url "..." --screenshots 30
```

### 问题：截图内容未加载

**症状**：截图显示空白或加载中

**解决方案**：
```bash
# 增加等待时间
node scripts/convert.js --url "..." --scroll-wait 5000 --initial-wait 20000
```

### 问题：无法提取 iframe URL

**症状**：报错 "Failed to extract iframe URL"

**解决方案**：
- 检查网络连接
- 确认文档访问权限
- 手动提供 iframe URL（需修改代码）

### 问题：PDF 文件过大

**症状**：PDF 文件超过 10 MB

**解决方案**：
- PNG 转换前压缩截图
- 使用 PDF 优化工具

## 技术细节

### 最佳参数配置

| 参数 | 钉钉文档 | 飞书文档 |
|------|----------|----------|
| 视口宽度 | 1920 | 1920 |
| 视口高度 | 1080 | 1080 |
| 默认屏数 | 21 | 15（待验证） |
| 滚动等待 | 3000ms | 2000ms（待验证） |
| 初始等待 | 15000ms | 10000ms（待验证） |

### 核心算法

```javascript
// 固定滚动距离，不依赖高度检测
const viewportHeight = 1080;
for (let i = 0; i < screenshotCount; i++) {
  const scrollY = viewportHeight * i;
  await page.evaluate((y) => window.scrollTo(0, y), scrollY);
  await page.waitForTimeout(scrollWait);
  await page.screenshot({ path: `screenshot_${i}.png` });
}
```

### 为什么不用自动检测高度？

钉钉文档使用虚拟滚动，`document.body.scrollHeight` 始终返回固定值（1080px），无法通过滚动检测真实高度。

## 项目结构

```
dingtalk-lark-pdf/
├── SKILL.md                    # 本文档
├── LICENSE.txt                 # MIT 许可证
├── package.json                # Node.js 依赖
├── references/                 # 技术参考文档
│   ├── dingtalk-technical.md   # 钉钉技术细节
│   ├── lark-technical.md       # 飞书技术细节
│   └── implementation-notes.md # 实现笔记
└── scripts/                    # 脚本目录
    ├── convert.js              # 主转换脚本
    ├── screenshot.js           # 截图拼接模块
    ├── detect-platform.js      # 平台检测
    └── utils.js                # 工具函数
```

## 依赖说明

### Node.js 依赖

- `playwright` (^1.57.0) - 浏览器自动化
- `commander` (^11.0.0) - 命令行参数解析

### Python 依赖

- `Pillow` - 图片处理（拼接长图）

### 系统工具

- `sips` (macOS) 或 `convert` (Linux) - PDF 转换

## 触发关键词

当用户提到以下关键词时，可以使用此 skill：

- "钉钉转 PDF"
- "飞书转 PDF"
- "文档转 PDF"
- "钉钉文档转换"
- "飞书文档转换"
- "alidocs.dingtalk.com"
- "feishu.cn"

## 开发计划

### 已完成

- ✅ 钉钉文档支持
- ✅ iframe URL 提取
- ✅ 分屏截图方案
- ✅ PIL 拼接长图
- ✅ PDF 转换
- ✅ 平台自动检测

### 待验证

- ⏳ 飞书文档测试
- ⏳ 飞书滚动行为
- ⏳ 跨平台兼容性

### 未来优化

- [ ] 自动检测最佳屏数
- [ ] 智能等待时间调整
- [ ] 去重检测（避免重复截图）
- [ ] 批量转换支持
- [ ] 进度条显示

## 测试案例

### 成功案例

**钉钉文档**
- URL: https://alidocs.dingtalk.com/i/nodes/DnRL6jAJMGrnOmD5cGqrdpPxWyMoPYe1
- 内容：21 屏
- 输出：3.6 MB PDF
- 耗时：约 60-90 秒

## License

MIT License - 详见 LICENSE.txt

## 贡献

欢迎提交 Issue 和 Pull Request！
