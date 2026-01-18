const { chromium } = require('playwright');
const path = require('path');

(async () => {
  console.log('启动浏览器中 (直达结果页模式)...');
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await context.newPage();

  try {
    // 直接构造搜索 URL，跳过首页输入步骤
    const query = encodeURIComponent('陈材杰');
    console.log(`正在直接访问搜索结果页: ${query}`);

    await page.goto(`https://www.baidu.com/s?wd=${query}`, {
        waitUntil: 'domcontentloaded',
        timeout: 45000
    });

    console.log('等待页面渲染...');
    await page.waitForTimeout(3000);

    // 尝试滚动一下，触发懒加载内容
    await page.mouse.wheel(0, 500);
    await page.waitForTimeout(1000);

    const title = await page.title();
    console.log(`页面标题: ${title}`);

    const screenshotPath = path.resolve(process.cwd(), 'search_result_ccj_direct.png');
    await page.screenshot({ path: screenshotPath });
    console.log(`📸 截图已保存至: ${screenshotPath}`);

  } catch (error) {
    console.error('发生错误:', error);
  } finally {
    await browser.close();
  }
})();
