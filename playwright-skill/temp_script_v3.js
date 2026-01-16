const { chromium } = require('playwright');
const path = require('path');

(async () => {
  console.log('启动浏览器中 (第3次尝试)...');
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await context.newPage();

  try {
    // 换一个更轻量的URL：新浪财经的美元指数移动版页面（通常更简洁）
    // 或者还是用东方财富，但放宽加载条件
    console.log('正在访问新浪财经...');
    await page.goto('https://finance.sina.com.cn/money/forex/hq/DINIW.shtml', {
        waitUntil: 'domcontentloaded',
        timeout: 45000
    });

    console.log('等待关键元素渲染...');
    // 新浪财经的图表通常在 .chart-box 或类似结构
    await page.waitForTimeout(5000);

    // 尝试关闭可能的弹窗 (如果有)

    const screenshotPath = path.resolve(process.cwd(), 'usd_final_attempt.png');
    await page.screenshot({ path: screenshotPath });
    console.log(`📸 截图已保存至: ${screenshotPath}`);

  } catch (error) {
    console.error('发生错误:', error);
  } finally {
    await browser.close();
  }
})();
