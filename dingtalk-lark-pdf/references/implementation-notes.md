# 实现笔记

## 项目背景

本项目旨在解决钉钉和飞书在线文档无法直接导出为 PDF 的问题。通过 Playwright 自动化浏览器操作，采用分屏截图+拼接方案，实现高质量 PDF 输出。

## 开发历程

### Phase 1: 问题探索

#### 尝试 1: page.pdf()

```javascript
await page.pdf({ path: 'output.pdf' });
```

**结果**: ❌ 只生成 1 页，内容不完整

**分析**:
- Playwright 的 `page.pdf()` 只捕获当前可见内容
- 无法处理虚拟滚动和懒加载

#### 尝试 2: fullPage 截图

```javascript
await page.screenshot({ path: 'screenshot.png', fullPage: true });
```

**结果**: ❌ 只截取 1080px 高度

**分析**:
- `fullPage: true` 依赖 `scrollHeight`
- 钉钉文档的 `scrollHeight` 始终返回 1080px

#### 尝试 3: 自动滚动检测高度

```javascript
let lastHeight = 0;
while (true) {
  const newHeight = await page.evaluate(() => document.body.scrollHeight);
  if (newHeight === lastHeight) break;
  lastHeight = newHeight;
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(3000);
}
```

**结果**: ❌ 无限循环

**分析**:
- 钉钉文档使用虚拟滚动
- `scrollHeight` 始终是 1080px，不会增长

### Phase 2: 解决方案

#### 方案 A: 固定滚动距离

**思路**:
- 不依赖高度检测
- 使用固定滚动距离（每屏 1080px）
- 预先设置屏数（如 21 屏）

**实现**:
```javascript
const viewportHeight = 1080;
for (let i = 0; i < 21; i++) {
  const scrollY = viewportHeight * i;
  await page.evaluate((y) => window.scrollTo(0, y), scrollY);
  await page.waitForTimeout(3000);
  await page.screenshot({ path: `screenshot_${i}.png` });
}
```

**结果**: ✅ 成功

#### 方案 B: PIL 拼接

**思路**:
- 使用 Python PIL 拼接所有截图
- 生成垂直长图

**实现**:
```python
from PIL import Image

images = [Image.open(f'screenshot_{i}.png') for i in range(21)]
total_height = len(images) * 1080
result = Image.new('RGB', (1920, total_height))

y_offset = 0
for img in images:
    result.paste(img, (0, y_offset))
    y_offset += 1080

result.save('stitched.png', 'PNG')
```

**结果**: ✅ 成功（22680px 长图）

#### 方案 C: PDF 转换

**思路**:
- 使用系统工具将长图转为 PDF
- macOS 用 sips，Linux 用 convert

**实现**:
```bash
# macOS
sips -s format pdf stitched.png --out output.pdf

# Linux
convert stitched.png output.pdf
```

**结果**: ✅ 成功（3.6 MB PDF）

### Phase 3: 优化改进

#### 改进 1: iframe 检测

**问题**:
- 钉钉文档内容在 iframe 中
- 直接访问主页无法截取完整内容

**解决**:
```javascript
// 先访问主页
await page.goto(mainUrl);

// 提取 iframe URL
const iframeUrl = await page.evaluate(() => {
  const iframe = document.querySelector('iframe');
  return iframe ? iframe.src : null;
});

// 访问 iframe URL
await page.goto(iframeUrl);
```

#### 改进 2: 等待策略优化

**问题**:
- `networkidle` 会超时
- 内容加载需要时间

**解决**:
```javascript
// 使用 domcontentloaded
await page.goto(url, { waitUntil: 'domcontentloaded' });

// 固定等待时间
await page.waitForTimeout(15000); // 初始加载
await page.waitForTimeout(3000);  // 每屏滚动后
```

#### 改进 3: 平台检测

**思路**:
- 根据 URL 自动识别平台
- 应用不同配置

**实现**:
```javascript
function detectPlatform(url) {
  if (url.includes('dingtalk.com')) return 'dingtalk';
  if (url.includes('feishu.cn')) return 'lark';
  return 'unknown';
}
```

## 关键发现

### 1. 虚拟滚动的陷阱

钉钉文档使用虚拟滚动优化性能：
- 只渲染可见区域
- `scrollHeight` 始终是视口高度
- 无法通过检测获取真实文档长度

**启示**: 不要信任 `scrollHeight`，使用固定滚动距离。

### 2. 懒加载的等待

滚动后内容需要时间加载：
- 图片加载需要时间
- DOM 渲染需要时间
- 网络请求需要时间

**启示**: 使用固定等待时间（3000ms），而不是依赖网络状态。

### 3. iframe 的复杂性

钉钉文档使用 iframe 隔离内容：
- 需要两层访问
- iframe URL 可能动态生成
- 提取失败需要降级处理

**启示**: 先尝试提取 iframe，失败则使用原 URL。

## 最佳实践总结

### 参数配置

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| 视口宽度 | 1920 | 标准桌面宽度 |
| 视口高度 | 1080 | 标准桌面高度 |
| 截图屏数 | 21 | 根据文档调整 |
| 滚动等待 | 3000ms | 平衡速度和质量 |
| 初始等待 | 15000ms | 确保完全加载 |

### 代码组织

```
scripts/
├── convert.js           # 主脚本（命令行接口）
├── screenshot.js        # 核心逻辑（截图拼接）
├── detect-platform.js   # 平台检测
└── utils.js             # 工具函数
```

**优点**:
- 职责分离
- 易于测试
- 便于维护

### 错误处理

```javascript
try {
  // 主逻辑
} catch (err) {
  console.error('转换失败:', err.message);
  console.error('故障排查:');
  console.error('  1. 检查网络连接');
  console.error('  2. 确认文档访问权限');
  console.error('  3. 尝试增加截图数量');
  process.exit(1);
}
```

## 性能分析

### 时间消耗

| 阶段 | 耗时 | 占比 |
|------|------|------|
| 浏览器启动 | 2-3s | 5% |
| 初始加载 | 15s | 25% |
| 分屏截图 | 45-60s | 65% |
| PIL 拼接 | 2-3s | 3% |
| PDF 转换 | 1-2s | 2% |
| **总计** | **65-85s** | **100%** |

### 优化空间

1. **减少等待时间**
   - 网络快时可以减少 `scrollWait`
   - 文档短时可以减少 `screenshotCount`

2. **并发处理**
   - 多个文档可以并发转换
   - 需要注意资源限制

3. **缓存机制**
   - 缓存浏览器实例
   - 避免重复启动

## 未来优化

### 短期优化

- [ ] 自动检测最佳屏数
- [ ] 智能等待时间调整
- [ ] 去重检测（避免重复截图）
- [ ] 进度条显示

### 中期优化

- [ ] 批量转换支持
- [ ] 配置文件支持
- [ ] GUI 界面
- [ ] Docker 镜像

### 长期优化

- [ ] 云端服务
- [ ] API 接口
- [ ] 浏览器扩展
- [ ] 移动端支持

## 测试策略

### 单元测试

```javascript
// 测试平台检测
assert.equal(detectPlatform('https://dingtalk.com/doc'), 'dingtalk');
assert.equal(detectPlatform('https://feishu.cn/doc'), 'lark');

// 测试文件名清理
assert.equal(sanitizeFilename('a<b>c'), 'a_b_c');
```

### 集成测试

```bash
# 测试钉钉文档
node scripts/convert.js \
  --url "https://alidocs.dingtalk.com/i/nodes/TEST" \
  --output /tmp/test.pdf

# 验证输出
ls -lh /tmp/test.pdf
```

### 性能测试

```bash
# 测量执行时间
time node scripts/convert.js --url "..." --output /tmp/
```

## 常见错误

### 错误 1: Timeout

```
Error: Timeout 60000ms exceeded
```

**原因**: 网络慢或服务器响应慢

**解决**:
- 增加超时时间
- 检查网络连接
- 尝试使用 VPN

### 错误 2: iframe not found

```
Error: No iframe found in page
```

**原因**: 页面结构变化或访问失败

**解决**:
- 检查 URL 是否正确
- 确认文档访问权限
- 手动提供 iframe URL

### 错误 3: 拼接失败

```
Error: PIL 拼接失败
```

**原因**: Pillow 未安装或截图损坏

**解决**:
```bash
pip3 install Pillow
```

## 参考资源

### 工具文档

- [Playwright](https://playwright.dev/)
- [Pillow](https://pillow.readthedocs.io/)
- [Commander.js](https://github.com/tj/commander.js)

### 相关项目

- [puppeteer-pdf](https://github.com/westy92/html-pdf-node)
- [pdf-lib](https://github.com/Hopding/pdf-lib)

## 贡献者

- Henry - 初始实现

## 许可证

MIT License
