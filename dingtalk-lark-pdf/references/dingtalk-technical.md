# 钉钉文档技术细节

## URL 结构

```
https://alidocs.dingtalk.com/i/nodes/{NODE_ID}
```

### 示例 URL

```
https://alidocs.dingtalk.com/i/nodes/DnRL6jAJMGrnOmD5cGqrdpPxWyMoPYe1
```

## 页面结构

### 主页特征

- **URL**: `alidocs.dingtalk.com/i/nodes/...`
- **结构**: 包含一个 `<iframe>` 元素
- **iframe 位置**: `<iframe src="...">` 在页面中

### iframe 特征

- **iframe URL**: 通常指向不同的域名或路径
- **内容**: 实际文档内容在 iframe 中渲染
- **提取方式**: `document.querySelector('iframe').src`

### 示例代码（提取 iframe URL）

```javascript
const iframeUrl = await page.evaluate(() => {
  const iframe = document.querySelector('iframe');
  return iframe ? iframe.src : null;
});
```

## 懒加载机制

### 关键发现

1. **虚拟滚动**
   - 使用虚拟滚动技术优化性能
   - 只渲染可见区域的内容

2. **固定 scrollHeight**
   - `document.body.scrollHeight` 始终返回 1080px
   - 无法通过滚动检测真实高度
   - 滚动不会增加 scrollHeight

3. **动态加载**
   - 滚动到指定位置后触发内容加载
   - 需要等待渲染完成（约 3000ms）

### 验证代码

```javascript
// 测试 scrollHeight
const scrollHeight = await page.evaluate(() => document.body.scrollHeight);
console.log('scrollHeight:', scrollHeight); // 始终 1080

// 测试滚动后高度
await page.evaluate(() => window.scrollTo(0, 1080));
await page.waitForTimeout(3000);
const newScrollHeight = await page.evaluate(() => document.body.scrollHeight);
console.log('newScrollHeight:', newScrollHeight); // 仍然是 1080
```

## 最佳参数配置

### 视口尺寸

```javascript
{
  width: 1920,
  height: 1080
}
```

### 截图参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 截图屏数 | 21 | 根据文档长度调整 |
| 滚动等待 | 3000ms | 每屏等待时间 |
| 初始等待 | 15000ms | 首次加载等待 |

### 滚动算法

```javascript
const viewportHeight = 1080;
for (let i = 0; i < 21; i++) {
  const scrollY = viewportHeight * i;
  await page.evaluate((y) => window.scrollTo(0, y), scrollY);
  await page.waitForTimeout(3000);
  await page.screenshot({ path: `screenshot_${i}.png` });
}
```

## 等待策略

### 必须使用的等待

- ✅ `waitUntil: 'domcontentloaded'` - DOM 内容加载完成
- ✅ 固定延迟 `waitForTimeout(15000)` - 等待初始渲染
- ✅ 滚动后等待 `waitForTimeout(3000)` - 等待内容加载

### 不能使用的等待

- ❌ `waitUntil: 'networkidle'` - 会超时（持续有网络请求）
- ❌ 自动检测高度变化 - 高度不变化

## 失败方案记录

### 方案 1: page.pdf()

```javascript
// ❌ 只获取 1 页
await page.pdf({ path: 'output.pdf' });
```

**结果**: 只生成 1 页 PDF，内容不完整。

### 方案 2: fullPage 截图

```javascript
// ❌ 只截取 1080px
await page.screenshot({ path: 'screenshot.png', fullPage: true });
```

**结果**: 只截取 1080px 高度，内容不完整。

### 方案 3: 自动滚动检测高度

```javascript
// ❌ scrollHeight 不变化
let lastHeight = 0;
while (true) {
  const newHeight = await page.evaluate(() => document.body.scrollHeight);
  if (newHeight === lastHeight) break;
  lastHeight = newHeight;
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(3000);
}
```

**结果**: 无限循环，scrollHeight 始终 1080。

## 成功方案

### 分屏滚动截图

```javascript
const viewportHeight = 1080;
const screenshotCount = 21;

for (let i = 0; i < screenshotCount; i++) {
  const scrollY = viewportHeight * i;
  await page.evaluate((y) => window.scrollTo(0, y), scrollY);
  await page.waitForTimeout(3000);
  await page.screenshot({ path: `screenshot_${i}.png` });
}
```

### PIL 拼接

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

### PDF 转换

```bash
# macOS
sips -s format pdf stitched.png --out output.pdf

# Linux
convert stitched.png output.pdf
```

## 测试案例

### 案例 1: 长文档

- **URL**: https://alidocs.dingtalk.com/i/nodes/DnRL6jAJMGrnOmD5cGqrdpPxWyMoPYe1
- **标题**: 1月生意金卡—一图看懂全网最香理财卡
- **内容长度**: 21 屏
- **输出**: 3.6 MB PDF
- **尺寸**: 1920 x 22680 px
- **耗时**: 约 60-90 秒

### 案例 2: 短文档

- **预计屏数**: 5-10 屏
- **建议配置**: 减少 `screenshotCount` 到 10

## 性能优化建议

### 减少等待时间

```javascript
// 如果网络快速，可以减少等待
{
  scrollWait: 2000,    // 从 3000 减到 2000
  initialWait: 10000,  // 从 15000 减到 10000
}
```

### 增加并发

```javascript
// 可以启动多个浏览器并发处理不同文档
// 但需要注意资源限制
```

## 常见问题

### Q: 为什么不能自动检测文档长度？

A: 钉钉文档使用虚拟滚动，`scrollHeight` 始终返回固定值（1080px），无法通过检测获取真实长度。

### Q: 如何确定最佳屏数？

A:
1. 先用默认 21 屏尝试
2. 如果 PDF 缺少内容，增加屏数
3. 如果 PDF 有空白重复，减少屏数

### Q: 为什么初始等待要 15 秒？

A: 钉钉文档需要加载大量资源（图片、样式、脚本），15 秒确保完全加载。

## 参考资源

- Playwright 文档: https://playwright.dev/
- PIL/Pillow 文档: https://pillow.readthedocs.io/
- sips 手册: `man sips`
