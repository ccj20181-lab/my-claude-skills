#!/usr/bin/env node

/**
 * 钉钉/飞书文档转 PDF 主脚本
 * 使用 agent-browser CLI 进行浏览器自动化
 */

const { program } = require('commander');
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const { detectPlatform, getPlatformConfig, isValidUrl } = require('./detect-platform');
const { extractTitleFromUrl, generateOutputPath, ensureDir, formatFileSize } = require('./utils');
const { screenshotToPdf, extractIframeUrl } = require('./screenshot');

// 配置命令行参数
program
  .name('dingtalk-lark-pdf')
  .description('钉钉/飞书文档转 PDF 工具 (使用 agent-browser)')
  .version('2.0.0')
  .requiredOption('-u, --url <url>', '文档 URL')
  .requiredOption('-o, --output <dir>', '输出目录')
  .option('-p, --platform <type>', '平台类型 (dingtalk/lark/auto)', 'auto')
  .option('-s, --screenshots <num>', '截图屏数', '21')
  .option('-w, --scroll-wait <ms>', '滚动等待时间（毫秒）', '3000')
  .option('-i, --initial-wait <ms>', '初始加载等待时间（毫秒）', '15000')
  .option('-t, --title <title>', '自定义文档标题')
  .parse(process.argv);

const options = program.opts();

/**
 * 执行 agent-browser 命令
 * @param {string} cmd - agent-browser 命令参数
 * @param {object} opts - 执行选项
 * @returns {string} 命令输出
 */
function runAgentBrowser(cmd, opts = {}) {
  const { timeout = 60000, silent = false } = opts;
  try {
    const result = execSync(`agent-browser ${cmd}`, {
      encoding: 'utf-8',
      timeout,
      stdio: silent ? 'pipe' : 'inherit'
    });
    return result || '';
  } catch (err) {
    if (!silent) {
      console.error(`⚠️ agent-browser 命令失败: ${cmd}`);
    }
    throw err;
  }
}

/**
 * 使用 agent-browser 提取 iframe URL
 * @param {string} url - 页面 URL
 * @returns {string|null} iframe URL
 */
async function extractIframeWithAgentBrowser(url) {
  try {
    console.log('🔍 检测钉钉文档 iframe 结构...');

    // 打开页面
    runAgentBrowser(`open "${url}"`, { silent: true, timeout: 120000 });
    runAgentBrowser('wait 5000', { silent: true });

    // 执行 JS 获取 iframe src
    const result = runAgentBrowser(
      'eval "(() => { const iframe = document.querySelector(\'iframe\'); return iframe ? iframe.src : null; })()"',
      { silent: true }
    );

    // 关闭浏览器
    try {
      runAgentBrowser('close', { silent: true });
    } catch (e) {
      // 忽略关闭错误
    }

    const iframeUrl = result.trim();

    if (iframeUrl && iframeUrl !== 'null') {
      console.log(`✓ 提取到 iframe URL: ${iframeUrl}\n`);
      return iframeUrl;
    }

    return null;
  } catch (err) {
    console.warn(`⚠️ 提取 iframe 失败: ${err.message}\n`);
    // 确保浏览器关闭
    try {
      runAgentBrowser('close', { silent: true });
    } catch (e) {
      // 忽略
    }
    return null;
  }
}

/**
 * 主函数
 */
async function main() {
  console.log('\n🚀 钉钉/飞书文档转 PDF 工具 (agent-browser 版)');
  console.log('================================\n');

  // 1. 验证 URL
  if (!isValidUrl(options.url)) {
    console.error('❌ 不支持的 URL 格式');
    console.error('   支持的域名: dingtalk.com, alidocs.dingtalk.com, feishu.cn, docs.feishu.cn');
    process.exit(1);
  }

  // 2. 检测平台
  let platform = options.platform;
  if (platform === 'auto') {
    platform = detectPlatform(options.url);
    console.log(`🔍 检测到平台: ${platform}\n`);
  }

  // 3. 获取平台配置
  const config = getPlatformConfig(platform);
  if (!config) {
    console.error(`❌ 未知平台: ${platform}`);
    process.exit(1);
  }

  console.log(`📋 平台配置: ${config.name}`);
  console.log(`   默认屏数: ${config.defaultScreenshots}`);
  console.log(`   滚动等待: ${config.defaultScrollWait}ms`);
  console.log(`   初始等待: ${config.defaultInitialWait}ms`);
  console.log(`   使用 iframe: ${config.hasIframe ? '是' : '否'}\n`);

  // 4. 解析参数
  const screenshotCount = parseInt(options.screenshots, 10) || config.defaultScreenshots;
  const scrollWait = parseInt(options.scrollWait, 10) || config.defaultScrollWait;
  const initialWait = parseInt(options.initialWait, 10) || config.defaultInitialWait;

  // 5. 生成输出路径
  ensureDir(options.output);
  const title = options.title || extractTitleFromUrl(options.url);
  const outputPath = generateOutputPath(title, options.output);

  console.log(`📄 输出文件: ${outputPath}\n`);

  // 6. 处理钉钉 iframe
  let targetUrl = options.url;
  if (platform === 'dingtalk' && config.hasIframe) {
    const iframeUrl = await extractIframeWithAgentBrowser(options.url);
    if (iframeUrl) {
      targetUrl = iframeUrl;
      console.log(`✓ 使用 iframe URL\n`);
    }
  }

  // 7. 开始转换
  console.log('🎬 开始转换...\n');

  const startTime = Date.now();

  try {
    await screenshotToPdf(targetUrl, outputPath, {
      platform,
      screenshotCount,
      scrollWait,
      initialWait,
      viewportWidth: config.viewportWidth,
      viewportHeight: config.viewportHeight,
    });

    const endTime = Date.now();
    const duration = ((endTime - startTime) / 1000).toFixed(1);

    // 8. 显示结果
    const stats = fs.statSync(outputPath);
    const fileSize = formatFileSize(stats.size);

    console.log('\n✅ 转换完成！');
    console.log('================================');
    console.log(`📁 文件路径: ${outputPath}`);
    console.log(`📏 文件大小: ${fileSize}`);
    console.log(`⏱️  耗时: ${duration} 秒`);
    console.log('================================\n');

  } catch (err) {
    console.error('\n❌ 转换失败:', err.message);
    console.error('\n💡 故障排查:');
    console.error('   1. 确认 agent-browser 已安装: which agent-browser');
    console.error('   2. 检查网络连接');
    console.error('   3. 确认文档访问权限');
    console.error('   4. 尝试增加 --screenshots 数量');
    console.error('   5. 尝试增加 --scroll-wait 和 --initial-wait 时间');
    console.error('');
    process.exit(1);
  }
}

// 运行主函数
main().catch((err) => {
  console.error('❌ 未预期的错误:', err);
  process.exit(1);
});
