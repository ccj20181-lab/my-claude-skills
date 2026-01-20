# 飞书文档技术细节

> **注意**: 飞书文档的技术细节基于推测和初步分析，需要实际测试验证。

## URL 结构

### 主要域名

- `feishu.cn` - 国内版
- `docs.feishu.cn` - 文档专用域名
- `feishu.cc` - 国际版（Lark）

### URL 格式

```
https://feishu.cn/docx/{DOC_ID}
https://docs.feishu.cn/docx/{DOC_ID}
https://{domain}.feishu.cn/docx/{DOC_ID}
```

### 示例 URL

```
https://bytedance.feishu.cn/docx/xxxxxxxxxxxx
https://docs.feishu.cn/docx/xxxxxxxxxxxx
```

## 页面结构（待验证）

### 预期结构

飞书文档可能采用以下结构之一：

#### 结构 1: 直接渲染（最可能）

```html
<body>
  <div class="doc-container">
    <!-- 文档内容直接渲染 -->
  </div>
</body>
```

#### 结构 2: iframe 结构（类似钉钉）

```html
<body>
  <iframe src="...">
    <!-- 文档内容在 iframe 中 -->
  </iframe>
</body>
```

#### 结构 3: Shadow DOM

```html
<body>
  <div id="app"></div>
  <script>
    // 内容渲染在 Shadow DOM 中
  </script>
</body>
```

## 懒加载机制（待验证）

### 预期行为

1. **虚拟滚动**
   - 飞书可能使用类似技术
   - 需要实际测试验证

2. **动态加载**
   - 滚动时加载内容
   - 图片按需加载

### 测试计划

```javascript
// 测试 1: 检查 scrollHeight
const scrollHeight = await page.evaluate(() => document.body.scrollHeight);
console.log('Initial scrollHeight:', scrollHeight);

// 测试 2: 滚动后检查变化
await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
await page.waitForTimeout(3000);
const newScrollHeight = await page.evaluate(() => document.body.scrollHeight);
console.log('After scroll:', newScrollHeight);

// 测试 3: 检查 iframe
const hasIframe = await page.evaluate(() => !!document.querySelector('iframe'));
console.log('Has iframe:', hasIframe);
```

## 最佳参数配置（待验证）

### 视口尺寸

```javascript
{
  width: 1920,
  height: 1080
}
```

### 建议参数

| 参数 | 建议值 | 说明 |
|------|--------|------|
| 截图屏数 | 15 | 待测试验证 |
| 滚动等待 | 2000ms | 可能比钉钉快 |
| 初始等待 | 10000ms | 待测试验证 |

## 差异分析

### 与钉钉的差异

| 特性 | 钉钉 | 飞书 | 状态 |
|------|------|------|------|
| iframe 结构 | 是 | 未知 | 待验证 |
| 固定 scrollHeight | 是 | 未知 | 待验证 |
| 虚拟滚动 | 是 | 可能 | 待验证 |
| 加载速度 | 较慢 | 可能较快 | 待验证 |

## 测试检查清单

### 基础测试

- [ ] 访问飞书文档 URL
- [ ] 检查页面结构（iframe/直接渲染）
- [ ] 测试 scrollHeight 行为
- [ ] 验证滚动机制

### 功能测试

- [ ] 分屏截图（15 屏）
- [ ] PIL 拼接
- [ ] PDF 转换
- [ ] 输出质量检查

### 性能测试

- [ ] 初始加载时间
- [ ] 滚动渲染时间
- [ ] 最佳屏数
- [ ] 总耗时

## 验证步骤

### 1. 基础访问测试

```bash
node scripts/convert.js \
  --url "https://feishu.cn/docx/TEST_ID" \
  --platform lark \
  --screenshots 15 \
  --output ~/Desktop/
```

### 2. 结构检测测试

```javascript
// 在浏览器控制台运行
console.log('scrollHeight:', document.body.scrollHeight);
console.log('iframe:', document.querySelector('iframe'));
console.log('content:', document.querySelector('.doc-content'));
```

### 3. 滚动行为测试

```javascript
// 测试滚动后高度变化
window.scrollTo(0, 1000);
setTimeout(() => {
  console.log('After scroll:', document.body.scrollHeight);
}, 3000);
```

## 预期挑战

### 挑战 1: 身份验证

飞书文档可能需要登录：
- 解决方案：使用已登录的浏览器上下文
- 或使用 Cookie 注入

### 挑战 2: 权限限制

部分文档可能受权限保护：
- 检查访问权限
- 提供登录凭证

### 挑战 3: 结构差异

如果飞书不使用 iframe：
- 简化流程（跳过 iframe 提取）
- 直接访问主页 URL

## 更新计划

### 优先级

1. **高优先级**
   - [ ] 实际 URL 测试
   - [ ] 页面结构分析
   - [ ] 滚动行为验证

2. **中优先级**
   - [ ] 最佳参数调优
   - [ ] 性能测试
   - [ ] 错误处理

3. **低优先级**
   - [ ] 批量转换
   - [ ] 进度条
   - [ ] GUI 界面

## 参考资源

- 飞书开放平台: https://open.feishu.cn/
- 飞书文档帮助: https://help.feishu.cn/

## 贡献指南

如果你有飞书文档的实际测试经验，欢迎贡献：

1. 测试结果
2. 参数建议
3. 结构分析
4. 问题反馈

请提交 Issue 或 Pull Request！
