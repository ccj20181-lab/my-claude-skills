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
async function downloadFile(url, destPath, referer = '', retries = 3) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(destPath);
    // 根据协议选择模块
    const client = url.startsWith('https') ? https : http;

    const request = client.get(url, {
      headers: {
        'User-Agent': USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)],
        'Referer': referer,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/pdf',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
      },
      timeout: 30000
    }, (response) => {
      // 处理重定向
      if (response.statusCode === 301 || response.statusCode === 302 || response.statusCode === 307 || response.statusCode === 308) {
        if (response.headers.location) {
          console.log(`↪️ 正在重定向到: ${response.headers.location}`);
          file.close();
          fs.unlinkSync(destPath);
          downloadFile(response.headers.location, destPath, referer, retries).then(resolve).catch(reject);
          return;
        }
      }

      if (response.statusCode !== 200) {
        file.close();
        fs.unlink(destPath, () => {});
        reject(new Error(`HTTP Status Code: ${response.statusCode}`));
        return;
      }

      response.pipe(file);
      file.on('finish', () => {
        file.close(resolve);
      });
    }).on('error', (err) => {
      file.close();
      fs.unlink(destPath, () => {});

      // 重试逻辑
      if (retries > 0) {
        console.log(`⚠️ 下载失败，剩余重试次数: ${retries - 1}`);
        setTimeout(() => {
          downloadFile(url, destPath, referer, retries - 1).then(resolve).catch(reject);
        }, 1000);
      } else {
        reject(err);
      }
    });

    request.on('timeout', () => {
      request.destroy();
      file.close();
      fs.unlink(destPath, () => {});

      if (retries > 0) {
        console.log(`⚠️ 下载超时，剩余重试次数: ${retries - 1}`);
        setTimeout(() => {
          downloadFile(url, destPath, referer, retries - 1).then(resolve).catch(reject);
        }, 1000);
      } else {
        reject(new Error('Download timeout'));
      }
    });
  });
}

// 主执行函数
(async () => {
  // 参数1: 报告列表 (JSON字符串)
  // 参数2: 主题名称 (用于创建子文件夹)
  const targets = process.argv[2] ? JSON.parse(process.argv[2]) : [];
  const topic = process.argv[3] || '未分类报告';

  // 基础下载路径 - 跨平台兼容
  const homeDir = require('os').homedir();
  const baseDir = process.platform === 'win32'
    ? 'F:\\研究报告下载'
    : path.join(homeDir, 'Downloads', '研究报告下载');
  const downloadDir = path.join(baseDir, topic);

  // 确保目录存在
  if (!fs.existsSync(downloadDir)){
    fs.mkdirSync(downloadDir, { recursive: true });
  }

  console.log(`🚀 启动 Report Hunter 引擎 (HTTP Mode)...`);
  console.log(`📂 目标目录: ${downloadDir}`);
  console.log(`🎯 任务数量: ${targets.length}`);

  let successCount = 0;
  let failCount = 0;

  for (const item of targets) {
    console.log(`\n----------------------------------------`);
    console.log(`🔍 处理: ${item.title}`);
    console.log(`🔗 链接: ${item.url}`);

    const safeName = `[研报]_${item.title.replace(/[\\/:*?"<>|]/g, '_')}.pdf`;
    const savePath = path.join(downloadDir, safeName);

    // 跳过已存在的文件
    if (fs.existsSync(savePath)) {
      const stats = fs.statSync(savePath);
      if (stats.size > 2048) {
        console.log(`⏭️ 文件已存在，跳过: ${safeName}`);
        successCount++;
        continue;
      }
    }

    try {
      // 直接使用 HTTP 下载
      console.log(`📥 HTTP 强力下载中...`);
      await downloadFile(item.url, savePath, item.url);

      const stats = fs.statSync(savePath);
      if (stats.size < 2048) {
        throw new Error("文件过小，可能下载失败");
      }

      console.log(`✅ 下载成功: ${safeName} (${(stats.size/1024).toFixed(2)} KB)`);
      successCount++;

    } catch (e) {
      console.error(`❌ 下载失败: ${e.message}`);
      failCount++;
      if (fs.existsSync(savePath)) fs.unlinkSync(savePath);
    }
  }

  console.log(`\n🎉 任务汇总: 成功 ${successCount} / 失败 ${failCount}`);
})();
