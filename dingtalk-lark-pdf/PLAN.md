# 钉钉/飞书文档转 PDF Skill 优化计划

## 问题分析

### 当前问题
用户报告：虽然显示截取了21屏，但实际所有截图都是第一页的重复内容。

### 根本原因分析

#### 1. **固定滚动距离失效**
```javascript
// 当前代码
const scrollY = viewportHeight * i;
await page.evaluate((y) => window.scrollTo(0, y), scrollY);
```

**问题**：
- 飞书文档可能使用了自定义滚动容器
- `window.scrollTo` 可能不会触发虚拟滚动
- 内容可能需要特定的滚动方式才能加载

#### 2. **缺少内容变化检测**
当前没有任何机制验证：
- 滚动是否真的发生了
- 内容是否真的在变化
- 新内容是否已经加载

#### 3. **等待时间不足**
- 3000ms 可能不够让飞书文档加载内容
- 需要等待网络请求完成
- 需要等待 DOM 更新

#### 4. **没有实际高度检测**
完全依赖固定屏数，没有检测文档真实长度

## 改进方案

### 方案 1: 智能滚动 + 内容变化检测 ⭐ 推荐

#### 核心思路
1. **检测滚动容器**
   - 识别真实滚动元素（不是 window）
   - 飞书文档可能使用自定义容器

2. **增量滚动策略**
   - 每次滚动一小步（如 500px）
   - 等待内容加载
   - 检测内容是否变化

3. **内容去重检测**
   - 计算截图哈希值
   - 如果哈希相同，说明内容未变化
   - 跳过重复截图

4. **自动结束检测**
   - 连续 N 次内容未变化 → 结束
   - 滚动到页面底部 → 结束
   - 达到最大屏数 → 结束

#### 实现伪代码
```javascript
async function smartCaptureScreenshots(url, options) {
  const { maxScreenshots = 50, scrollStep = 500 } = options;

  // 1. 检测滚动容器
  const scrollContainer = await detectScrollContainer(page);

  // 2. 读取滚动容器高度
  let lastHash = null;
  let duplicateCount = 0;
  let scrollY = 0;

  for (let i = 0; i < maxScreenshots; i++) {
    // 滚动
    await page.evaluate((y, container) => {
      if (container === 'window') {
        window.scrollTo(0, y);
      } else {
        document.querySelector(container).scrollTop = y;
      }
    }, scrollY, scrollContainer);

    // 等待加载
    await waitForContentLoad(page);

    // 截图
    const screenshotPath = await captureScreenshot(page, i);

    // 计算哈希
    const hash = await calculateImageHash(screenshotPath);

    // 去重检测
    if (hash === lastHash) {
      duplicateCount++;
      if (duplicateCount >= 3) {
        console.log('内容未变化，结束截图');
        break;
      }
    } else {
      duplicateCount = 0;
      lastHash = hash;
    }

    scrollY += scrollStep;
  }
}
```

### 方案 2: 模拟真实用户滚动

#### 核心思路
模拟用户使用鼠标滚轮或触摸板滚动的行为：
- 使用 `page.mouse.wheel()` 模拟滚轮
- 小步多次滚动
- 更自然的滚动速度

#### 实现伪代码
```javascript
async function humanLikeScroll(page, distance) {
  const steps = 10;
  const stepDistance = distance / steps;

  for (let i = 0; i < steps; i++) {
    await page.mouse.wheel(0, stepDistance);
    await page.waitForTimeout(100);
  }
}
```

### 方案 3: Playwright 原生滚动方法

#### 使用 `page.evaluate()` + 滚动到元素
```javascript
// 滚动到页面底部
await page.evaluate(() => {
  window.scrollTo(0, document.body.scrollHeight);
});

// 等待新内容加载
await page.waitForFunction(() => {
  return document.body.scrollHeight > window.scrollY + window.innerHeight;
});
```

### 方案 4: 结合多种策略 ⭐⭐ 最优方案

#### 组合策略
1. **第一阶段**：检测滚动容器和文档结构
2. **第二阶段**：尝试多种滚动方式
   - window.scrollTo
   - 元素滚动
   - 鼠标滚轮
3. **第三阶段**：验证内容变化
   - 哈希检测
   - DOM 元素检测
4. **第四阶段**：智能截取
   - 只保留内容变化的截图
   - 自动去重

## 实现计划

### Phase 1: 诊断工具
创建诊断函数，帮助理解页面结构：

```javascript
async function diagnosePage(page) {
  const info = await page.evaluate(() => {
    return {
      // 滚动容器
      scrollHeight: document.body.scrollHeight,
      scrollY: window.scrollY,

      // 检查是否有自定义滚动容器
      customScrollers: Array.from(document.querySelectorAll('[style*="overflow"]'))
        .map(el => ({
          tag: el.tagName,
          overflow: el.style.overflow,
          height: el.scrollHeight,
        })),

      // 主要内容容器
      mainContainers: Array.from(document.querySelectorAll('[class*="content"], [class*="container"], [class*="wiki"]'))
        .map(el => ({
          tag: el.tagName,
          class: el.className,
          height: el.scrollHeight,
        })),
    };
  });

  console.log('页面诊断信息:', JSON.stringify(info, null, 2));
  return info;
}
```

### Phase 2: 改进滚动函数

```javascript
async function smartScroll(page, targetY, options = {}) {
  const { method = 'auto', step = 500, delay = 200 } = options;

  // 尝试不同的滚动方式
  const methods = {
    window: () => page.evaluate((y) => window.scrollTo(0, y), targetY),
    element: () => page.evaluate((y) => {
      const el = document.querySelector('.wiki-content') || document.body;
      el.scrollTop = y;
    }, targetY),
    wheel: async () => {
      const currentY = await page.evaluate(() => window.scrollY);
      const delta = targetY - currentY;
      const steps = Math.ceil(Math.abs(delta) / step);

      for (let i = 0; i < steps; i++) {
        await page.mouse.wheel(0, Math.sign(delta) * step);
        await page.waitForTimeout(delay);
      }
    },
  };

  // 执行滚动
  if (methods[method]) {
    await methods[method]();
  } else {
    // auto: 尝试所有方法，检测哪个有效
    for (const [name, fn] of Object.entries(methods)) {
      if (name !== 'auto') {
        try {
          await fn();
          await page.waitForTimeout(500);
          const actualY = await page.evaluate(() => window.scrollY);
          if (actualY > 0) return name;
        } catch (err) {
          continue;
        }
      }
    }
  }
}
```

### Phase 3: 内容变化检测

```javascript
async function detectContentChange(page, screenshotPath) {
  // 方法1: 图片哈希
  const hash = calculateImageHash(screenshotPath);

  // 方法2: DOM 检测
  const domInfo = await page.evaluate(() => {
    const firstElement = document.elementFromPoint(960, 540); // 屏幕中心
    return {
      tagName: firstElement?.tagName,
      textContent: firstElement?.textContent?.substring(0, 100),
      className: firstElement?.className,
    };
  });

  return { hash, domInfo };
}
```

### Phase 4: 智能截图流程

```javascript
async function intelligentCapture(url, options) {
  const {
    maxScreenshots = 50,
    scrollStep = 500,
    maxDuplicates = 3,
    waitAfterScroll = 3000,
  } = options;

  // 1. 诊断页面
  const pageInfo = await diagnosePage(page);

  // 2. 选择滚动方式
  const scrollMethod = pageInfo.customScrollers.length > 0 ? 'element' : 'window';

  // 3. 智能截图
  const screenshots = [];
  let lastHash = null;
  let duplicateCount = 0;
  let scrollY = 0;

  for (let i = 0; i < maxScreenshots; i++) {
    // 滚动
    await smartScroll(page, scrollY, { method: scrollMethod });

    // 等待
    await page.waitForTimeout(waitAfterScroll);

    // 截图
    const path = await captureScreenshot(page, i);
    const { hash } = await detectContentChange(page, path);

    // 去重
    if (hash === lastHash) {
      duplicateCount++;
      console.log(`⚠️  重复内容 (${duplicateCount}/${maxDuplicates})`);
      if (duplicateCount >= maxDuplicates) {
        console.log('✓ 内容未变化，结束截图');
        break;
      }
    } else {
      duplicateCount = 0;
      screenshots.push(path);
    }

    lastHash = hash;
    scrollY += scrollStep;
  }

  return screenshots;
}
```

## 测试计划

### 测试用例 1: 飞书文档
```bash
node scripts/convert.js \
  --url "https://forchangesz.feishu.cn/wiki/ZMlkwBzjniIPJhk1eJNc21bZnZc" \
  --output ~/Desktop/ \
  --scroll-method auto
```

### 测试用例 2: 钉钉文档
```bash
node scripts/convert.js \
  --url "https://alidocs.dingtalk.com/i/nodes/..." \
  --output ~/Desktop/
```

### 验证指标
- [ ] 截图内容不重复
- [ ] 覆盖完整文档
- [ ] 文件大小合理
- [ ] 转换时间可接受

## 优化参数建议

| 参数 | 钉钉 | 飞书 |
|------|------|------|
| 滚动方式 | window | element/auto |
| 滚动步长 | 1080 | 500 |
| 滚动等待 | 3000ms | 4000ms |
| 初始等待 | 15000ms | 20000ms |
| 最大重复次数 | 3 | 5 |

## 文件修改清单

### 需要修改的文件
1. `scripts/screenshot.js` - 核心截图逻辑
2. `scripts/convert.js` - 添加新参数
3. `SKILL.md` - 更新文档
4. `references/lark-technical.md` - 补充飞书发现

### 需要新增的文件
1. `scripts/diagnose.js` - 页面诊断工具（可选）
2. `scripts/image-hash.js` - 图片哈希工具

## 风险评估

### 低风险
- ✅ 添加诊断功能（不影响现有逻辑）
- ✅ 添加新参数（向后兼容）

### 中风险
- ⚠️ 修改滚动逻辑（需要充分测试）
- ⚠️ 添加去重检测（可能误判）

### 缓解措施
1. 保留原有逻辑作为后备方案
2. 添加 `--legacy-mode` 参数
3. 详细的日志输出帮助调试
4. 先在测试环境验证

## 下一步行动

1. ✅ 创建诊断函数
2. ✅ 实现智能滚动
3. ✅ 添加内容检测
4. ✅ 测试验证
5. ✅ 更新文档
6. ✅ 同步到 GitHub

---

**计划状态**: 待批准
**预估时间**: 30-45 分钟
**优先级**: 高（用户反馈的关键问题）
