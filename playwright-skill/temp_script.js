const { chromium } = require('playwright');
const path = require('path');

(async () => {
  console.log('启动浏览器中...');
  const browser = await chromium.launch({ headless: false }); // 设为 false 让您能看到（虽然是在后台）
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    console.log('正在访问东方财富美元指数页面...');
    await page.goto('https://quote.eastmoney.com/unify/r/100.UDI', { waitUntil: 'domcontentloaded' });

    // 等待价格元素出现 (根据页面结构调整选择器，这里假设是常见的类名)
    // 东方财富页面的价格通常在特定的 ID 或 Class 下，为了稳妥，我们先截图
    await page.waitForTimeout(3000); // 等待数据加载

    const title = await page.title();
    console.log(`页面标题: ${title}`);

    // 尝试获取价格 (这是一个通用猜测，如果失败会通过截图确认)
    // 东方财富详情页的价格通常在 .zxj 这个class里，或者类似的结构
    // 这里我们主要依赖截图作为证据

    const screenshotPath = path.resolve(process.cwd(), 'usd_index.png');
    await page.screenshot({ path: screenshotPath, fullPage: false });
    console.log(`📸 截图已保存至: ${screenshotPath}`);

    // 尝试提取页面文本作为辅助
    const text = await page.evaluate(() => document.body.innerText.slice(0, 500));
    console.log('页面前500字内容摘要:', text);

  } catch (error) {
    console.error('发生错误:', error);
  } finally {
    await browser.close();
  }
})();
