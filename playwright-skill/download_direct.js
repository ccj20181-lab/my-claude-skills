const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const https = require('https');

// Tavily 搜索到的直链列表
const PDF_URLS = [
    { title: '2024广州智慧城市白皮书', url: 'https://zfcj.gz.gov.cn/attachment/7/7864/7864885/9783025.pdf' },
    { title: '华为城市数智化2030', url: 'https://www-file.huawei.com/-/media/corp2020/pdf/giv/2024/digital_intelligent_urban_transformation_2030_cn.pdf' },
    { title: '智慧城市板块专题报告', url: 'https://www.ssif.com.hk/ssif-api/uploads/analysis-report/tc/20241118.pdf' },
    { title: '信通院城市全域数字化转型', url: 'https://www.caict.ac.cn/english/research/whitepapers/202504/P020250401512570054520.pdf' }
];

(async () => {
  console.log('启动直链下载模式...');
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({ acceptDownloads: true });

  const downloadDir = path.join(process.env.USERPROFILE || 'C:\\Users\\cj', 'Desktop');

  for (const item of PDF_URLS) {
    console.log(`\n⬇️ 正在下载: ${item.title}`);
    const page = await context.newPage();

    try {
        // 尝试触发下载
        const downloadPromise = page.waitForEvent('download', { timeout: 10000 });

        try {
            await page.goto(item.url, { timeout: 15000, waitUntil: 'domcontentloaded' });
        } catch(e) {
            // 忽略导航错误，因为直接访问文件可能会中止导航
        }

        // 检查是否触发了下载事件
        try {
            const download = await downloadPromise;
            const fileName = `[研报]_${item.title}.pdf`;
            await download.saveAs(path.join(downloadDir, fileName));
            console.log(`✅ 成功保存: ${fileName}`);
        } catch (e) {
            console.log(`ℹ️ 浏览器未触发自动下载，尝试手动抓取流...`);
            // 如果没触发下载（比如浏览器直接预览了），我们尝试用 fetch 拿数据
            const response = await page.request.get(item.url);
            if (response.ok()) {
                const buffer = await response.body();
                const fileName = `[研报]_${item.title}.pdf`;
                fs.writeFileSync(path.join(downloadDir, fileName), buffer);
                console.log(`✅ 手动保存成功: ${fileName}`);
            } else {
                console.log(`❌ 下载失败: HTTP ${response.status()}`);
            }
        }

    } catch (error) {
        console.error(`❌ 处理出错: ${error.message}`);
    } finally {
        await page.close();
    }
  }

  await browser.close();
  console.log('\n🎉 所有任务处理完毕！');
})();
