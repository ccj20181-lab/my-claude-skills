const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  console.log('启动智能研报抓取助手...');
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({
    acceptDownloads: true // 允许下载
  });
  const page = await context.newPage();

  // 目标下载目录
  const downloadDir = path.join(process.env.USERPROFILE || 'C:\\Users\\cj', 'Desktop');
  console.log(`目标下载目录: ${downloadDir}`);

  try {
    // 策略：搜索 filetype:pdf
    // 我们利用必应搜索（相对友好）来找 PDF
    const keyword = '智慧城市产业研究报告 filetype:pdf';
    console.log(`正在搜索: ${keyword}`);

    await page.goto(`https://cn.bing.com/search?q=${encodeURIComponent(keyword)}`, {
        waitUntil: 'domcontentloaded',
        timeout: 60000
    });

    await page.waitForTimeout(3000);

    // 提取搜索结果中的 PDF 链接
    // 必应的搜索结果链接通常在 h2 a 中
    const links = await page.evaluate(() => {
        const anchors = Array.from(document.querySelectorAll('li.b_algo h2 a'));
        return anchors.map(a => ({
            title: a.innerText,
            url: a.href
        }));
    });

    console.log(`找到 ${links.length} 个潜在报告链接，开始尝试下载前 3 个...`);

    let successCount = 0;

    for (let i = 0; i < Math.min(3, links.length); i++) {
        const link = links[i];
        console.log(`[${i+1}/3] 正在尝试下载: ${link.title}`);

        try {
            // 注意：有些链接点击后会直接下载，有些会跳转预览
            // 我们尝试直接请求该 URL 并保存
            // Playwright 的下载处理通常需要触发事件，但对于直接文件链接，我们可以用 fetch

            // 创建一个新的页面去触发下载，避免干扰主流程
            const newPage = await context.newPage();

            // 监听下载事件
            const downloadPromise = newPage.waitForEvent('download', { timeout: 15000 });

            try {
                // 访问链接，如果是 PDF 通常会触发浏览器下载行为
                await newPage.goto(link.url, { waitUntil: 'domcontentloaded', timeout: 15000 });
            } catch (e) {
                // 忽略导航超时，因为有时候下载触发了就不会完成导航
            }

            // 等待下载开始
            const download = await downloadPromise;
            const suggestedName = download.suggestedFilename();
            const safeName = `[研报]_${suggestedName}`;
            const savePath = path.join(downloadDir, safeName);

            await download.saveAs(savePath);
            console.log(`✅ 成功下载: ${safeName}`);
            successCount++;

            await newPage.close();

        } catch (e) {
            console.log(`⚠️ 下载失败 (${link.title}): 可能是预览页而非直接下载链，跳过。(${e.message})`);
            // 如果是普通的网页预览，我们其实可以截图，但这里先专注下载
        }

        // 礼貌间隔
        await page.waitForTimeout(2000);
    }

    console.log(`\n🎉 任务完成！共下载 ${successCount} 份报告到桌面。`);

  } catch (error) {
    console.error('发生错误:', error);
  } finally {
    await browser.close();
  }
})();
