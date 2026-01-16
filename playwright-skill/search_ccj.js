const { chromium } = require('playwright');
const path = require('path');

(async () => {
  console.log('启动浏览器中...');
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await context.newPage();

  try {
    console.log('正在访问百度...');
    await page.goto('https://www.baidu.com', { waitUntil: 'domcontentloaded' });

    console.log('输入搜索词: 陈材杰');
    await page.fill('#kw', '陈材杰');
    await page.click('#su');

    console.log('等待搜索结果...');
    await page.waitForSelector('#content_left', { timeout: 10000 });

    // 给页面一点时间加载图片等资源
    await page.waitForTimeout(2000);

    const title = await page.title();
    console.log(`页面标题: ${title}`);

    const screenshotPath = path.resolve(process.cwd(), 'search_result_ccj.png');
    await page.screenshot({ path: screenshotPath });
    console.log(`📸 搜索结果截图已保存至: ${screenshotPath}`);

  } catch (error) {
    console.error('发生错误:', error);
  } finally {
    await browser.close();
  }
})();
