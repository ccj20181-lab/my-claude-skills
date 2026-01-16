const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  console.log('启动智能研报抓取助手 (魔改版)...');
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({ acceptDownloads: true });
  const page = await context.newPage();

  const downloadDir = path.join(process.env.USERPROFILE || 'C:\\Users\\cj', 'Desktop');

  try {
    // 策略优化：直接去一些容易下载 PDF 的聚合站点搜索，或者用更精准的 Google/Bing 语法
    // 这里我们尝试搜索 "filetype:pdf 智慧城市 2024"
    const keyword = '智慧城市 发展白皮书 2024 filetype:pdf';
    console.log(`正在搜索: ${keyword}`);

    await page.goto(`https://cn.bing.com/search?q=${encodeURIComponent(keyword)}`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(3000);

    // 抓取所有看上去像 PDF 的链接
    const links = await page.evaluate(() => {
        const anchors = Array.from(document.querySelectorAll('a'));
        return anchors
            .filter(a => a.href.toLowerCase().endsWith('.pdf') || a.innerText.includes('PDF'))
            .map(a => ({ title: a.innerText.trim() || '未命名报告', url: a.href }))
            .filter(link => link.url.startsWith('http') && link.title.length > 5) // 过滤无效链接
            .slice(0, 5); // 取前5个
    });

    console.log(`找到 ${links.length} 个潜在 PDF 链接:`);
    links.forEach(l => console.log(`- ${l.title}: ${l.url}`));

    if (links.length === 0) {
        console.log('未找到直接的 PDF 链接，尝试访问第一条搜索结果...');
        // 如果没找到直接连接，就去点第一个结果，看看里面有没有
    }

    let successCount = 0;

    for (const link of links) {
        console.log(`\n⬇️ 正在尝试下载: ${link.title}`);
        try {
            const page2 = await context.newPage();
            // 有些 PDF 是直接在浏览器打开的，我们需要拦截请求或者保存
            const response = await page2.goto(link.url, { timeout: 30000, waitUntil: 'networkidle' });

            // 检查 Content-Type
            const contentType = response.headers()['content-type'];
            if (contentType && contentType.includes('application/pdf')) {
                const buffer = await response.body();
                const safeName = link.title.replace(/[\\/:*?"<>|]/g, '_') + '.pdf';
                const savePath = path.join(downloadDir, safeName);
                fs.writeFileSync(savePath, buffer);
                console.log(`✅ 已保存: ${safeName}`);
                successCount++;
            } else {
                console.log(`⚠️ 目标不是 PDF (Type: ${contentType})，跳过。`);
            }
            await page2.close();
        } catch (e) {
            console.log(`❌ 下载出错: ${e.message}`);
        }
    }

  } catch (error) {
    console.error('发生全局错误:', error);
  } finally {
    await browser.close();
  }
})();
