const { chromium } = require('playwright');
const path = require('path');

(async () => {
  console.log('启动浏览器中...');
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 } // 设置大一点的分辨率，保证图表完整显示
  });
  const page = await context.newPage();

  try {
    console.log('正在访问东方财富美元指数页面...');
    // 使用更具体的行情页面 URL
    await page.goto('https://quote.eastmoney.com/unify/r/100.UDI', { waitUntil: 'networkidle' });

    console.log('等待页面加载...');
    await page.waitForTimeout(5000); // 强制多等一会，让异步数据加载

    // 尝试寻找包含 K 线图的容器
    // 东方财富的新版页面通常有一个 canvas 或者特定的 chart 容器
    // 我们尝试定位主要的行情区域

    // 模拟鼠标滚动，触发懒加载
    await page.mouse.wheel(0, 300);
    await page.waitForTimeout(1000);

    const title = await page.title();
    console.log(`页面标题: ${title}`);

    // 定位到K线图区域进行截图
    // 如果找不到特定元素，就截取首屏的特定区域

    // 尝试等待 canvas 元素（通常是图表）
    try {
        await page.waitForSelector('canvas', { timeout: 5000 });
        console.log('检测到图表 Canvas 元素');
    } catch (e) {
        console.log('未检测到 Canvas，可能是图片或SVG');
    }

    const screenshotPath = path.resolve(process.cwd(), 'usd_chart_fixed.png');

    // 截取第一屏的中间部分，通常是图表所在位置
    // Clip 参数: x, y, width, height
    await page.screenshot({
        path: screenshotPath,
        clip: { x: 0, y: 100, width: 1200, height: 800 }
    });

    console.log(`📸 优化后的截图已保存至: ${screenshotPath}`);

  } catch (error) {
    console.error('发生错误:', error);
  } finally {
    await browser.close();
  }
})();
