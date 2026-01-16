const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const https = require('https');
const http = require('http');

// --- 配置区域 ---
const USER_AGENTS = [
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'
];

// 高防下载函数 (支持 HTTP 和 HTTPS)
async function downloadFile(url, destPath, referer = '') {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(destPath);
    // 根据协议选择模块
    const client = url.startsWith('https') ? https : http;

    const request = client.get(url, {
      headers: {
        'User-Agent': USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)],
        'Referer': referer,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
      },
      timeout: 30000
    }, (response) => {
      // 处理重定向
      if (response.statusCode === 301 || response.statusCode === 302) {
        if (response.headers.location) {
            console.log(`↪️ 正在重定向到: ${response.headers.location}`);
            downloadFile(response.headers.location, destPath, referer).then(resolve).catch(reject);
            return;
        }
      }

      if (response.statusCode !== 200) {
        reject(new Error(`HTTP Status Code: ${response.statusCode}`));
        return;
      }

      response.pipe(file);
      file.on('finish', () => {
        file.close(resolve);
      });
    }).on('error', (err) => {
        fs.unlink(destPath, () => {});
        reject(err);
    });
  });
}

// 主执行函数
(async () => {
  // 参数1: 报告列表 (JSON字符串)
  // 参数2: 主题名称 (用于创建子文件夹)
  const targets = process.argv[2] ? JSON.parse(process.argv[2]) : [];
  const topic = process.argv[3] || '未分类报告';

  // 基础下载路径 F:\研究报告下载
  const baseDir = 'F:\\研究报告下载';
  const downloadDir = path.join(baseDir, topic);

  // 确保目录存在
  if (!fs.existsSync(downloadDir)){
      fs.mkdirSync(downloadDir, { recursive: true });
  }

  console.log(`🚀 启动 Report Hunter 引擎...`);
  console.log(`📂 目标目录: ${downloadDir}`);
  console.log(`🎯 任务数量: ${targets.length}`);

  const browser = await chromium.launch({
      headless: false,
      args: ['--disable-blink-features=AutomationControlled']
  });

  const context = await browser.newContext({
      userAgent: USER_AGENTS[0],
      viewport: { width: 1366, height: 768 },
      acceptDownloads: true,
      ignoreHTTPSErrors: true
  });

  let successCount = 0;
  let failCount = 0;

  for (const item of targets) {
    console.log(`\n----------------------------------------`);
    console.log(`🔍 处理: ${item.title}`);
    console.log(`🔗 链接: ${item.url}`);

    const safeName = `[研报]_${item.title.replace(/[\\/:*?"<>|]/g, '_')}.pdf`;
    const savePath = path.join(downloadDir, safeName);

    try {
        // 策略1: 浏览器原生下载
        console.log(`trying 浏览器原生下载...`);
        const page = await context.newPage();

        try {
            const downloadPromise = page.waitForEvent('download', { timeout: 10000 });
            await page.goto(item.url, { timeout: 25000, waitUntil: 'domcontentloaded' });
            const download = await downloadPromise;
            await download.saveAs(savePath);
            console.log(`✅ [Browser] 下载成功: ${safeName}`);
            successCount++;
        } catch (browserError) {
            console.log(`⚠️ 浏览器自动下载失败 (${browserError.message.split('\n')[0]}), 切换至 HTTP 强力模式...`);

            // 策略2: Node.js 模拟请求下载
            await downloadFile(item.url, savePath, item.url);

            const stats = fs.statSync(savePath);
            if (stats.size < 2048) throw new Error("文件过小");

            console.log(`✅ [HTTP] 下载成功: ${safeName} (${(stats.size/1024).toFixed(2)} KB)`);
            successCount++;
        } finally {
            await page.close();
        }

    } catch (e) {
        console.error(`❌ 下载彻底失败: ${e.message}`);
        failCount++;
        if (fs.existsSync(savePath)) fs.unlinkSync(savePath);
    }
  }

  await browser.close();
  console.log(`\n🎉 任务汇总: 成功 ${successCount} / 失败 ${failCount}`);
})();
