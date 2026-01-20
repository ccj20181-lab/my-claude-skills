#!/usr/bin/env node

/**
 * 截图拼接模块
 * 处理分屏滚动截图和拼接
 */

const { chromium } = require('playwright');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

/**
 * 提取 iframe URL（钉钉专用）
 * @param {Page} page - Playwright Page 对象
 * @returns {string|null} iframe URL
 */
async function extractIframeUrl(page) {
  try {
    const iframeUrl = await page.evaluate(() => {
      const iframe = document.querySelector('iframe');
      return iframe ? iframe.src : null;
    });

    if (!iframeUrl) {
      throw new Error('No iframe found in page');
    }

    console.log(`✓ 提取到 iframe URL: ${iframeUrl}`);
    return iframeUrl;
  } catch (err) {
    console.error('✗ 提取 iframe URL 失败:', err.message);
    throw err;
  }
}

/**
 * 分屏滚动截图
 * @param {string} url - 文档 URL（或 iframe URL）
 * @param {object} options - 配置选项
 * @returns {Array<string>} 截图文件路径列表
 */
async function captureScreenshots(url, options = {}) {
  const {
    screenshotCount = 21,
    scrollWait = 3000,
    initialWait = 15000,
    viewportWidth = 1920,
    viewportHeight = 1080,
    tempDir = '/tmp',
  } = options;

  console.log(`\n📸 开始分屏截图 (${screenshotCount} 屏)`);
  console.log(`   视口: ${viewportWidth}x${viewportHeight}`);
  console.log(`   滚动等待: ${scrollWait}ms`);
  console.log(`   初始等待: ${initialWait}ms\n`);

  const browser = await chromium.launch({
    headless: true,
  });

  const context = await browser.newContext({
    viewport: { width: viewportWidth, height: viewportHeight },
  });

  const page = await context.newPage();
  const screenshotFiles = [];

  try {
    // 访问页面
    console.log(`🌐 访问页面: ${url}`);
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });

    // 等待初始加载
    console.log(`⏳ 等待页面加载 (${initialWait}ms)`);
    await page.waitForTimeout(initialWait);

    // 分屏截图
    for (let i = 0; i < screenshotCount; i++) {
      const scrollY = viewportHeight * i;

      console.log(`📷 截图 ${i + 1}/${screenshotCount} (scrollY: ${scrollY}px)`);

      // 滚动到指定位置
      await page.evaluate((y) => window.scrollTo(0, y), scrollY);

      // 等待渲染
      await page.waitForTimeout(scrollWait);

      // 截图
      const screenshotPath = path.join(tempDir, `screenshot_${i}.png`);
      await page.screenshot({
        path: screenshotPath,
        fullPage: false,
      });

      screenshotFiles.push(screenshotPath);
    }

    console.log(`\n✓ 截图完成: ${screenshotFiles.length} 张`);
    return screenshotFiles;
  } catch (err) {
    console.error('✗ 截图失败:', err.message);
    throw err;
  } finally {
    await browser.close();
  }
}

/**
 * 使用 Python PIL 拼接长图
 * @param {Array<string>} screenshotFiles - 截图文件路径列表
 * @param {string} outputPath - 输出文件路径
 */
function stitchImages(screenshotFiles, outputPath) {
  console.log('\n🔧 拼接长图...');

  // 创建 Python 脚本
  const pythonScript = `
import sys
from PIL import Image

screenshot_files = ${JSON.stringify(screenshotFiles)}
output_path = "${outputPath}"

try:
    # 打开所有截图
    images = [Image.open(f) for f in screenshot_files]

    # 获取尺寸
    width, height = images[0].size
    total_height = len(images) * height

    # 创建新图像
    result = Image.new('RGB', (width, total_height))

    # 拼接图像
    y_offset = 0
    for img in images:
        result.paste(img, (0, y_offset))
        y_offset += height

    # 保存
    result.save(output_path, 'PNG')
    print(f"✓ 长图已保存: {output_path}")
    print(f"  尺寸: {width}x{total_height}px")

except Exception as e:
    print(f"✗ 拼接失败: {e}", file=sys.stderr)
    sys.exit(1)
`;

  const scriptPath = path.join('/tmp', 'stitch_images.py');
  fs.writeFileSync(scriptPath, pythonScript);

  try {
    execSync(`python3 ${scriptPath}`, { stdio: 'inherit' });
  } catch (err) {
    throw new Error(`拼接失败: ${err.message}`);
  }
}

/**
 * 转换为 PDF
 * @param {string} imagePath - 图像文件路径
 * @param {string} pdfPath - PDF 文件路径
 */
function convertToPdf(imagePath, pdfPath) {
  console.log('\n📄 转换为 PDF...');

  try {
    // macOS 使用 sips
    execSync(`sips -s format pdf "${imagePath}" --out "${pdfPath}"`, {
      stdio: 'inherit',
    });
    console.log(`✓ PDF 已保存: ${pdfPath}`);
  } catch (err) {
    // 如果 sips 失败，尝试使用 convert (ImageMagick)
    try {
      execSync(`convert "${imagePath}" "${pdfPath}"`, { stdio: 'inherit' });
      console.log(`✓ PDF 已保存: ${pdfPath}`);
    } catch (err2) {
      throw new Error(`PDF 转换失败: ${err2.message}`);
    }
  }
}

/**
 * 完整的截图拼接流程
 * @param {string} url - 文档 URL
 * @param {string} outputPath - 输出 PDF 路径
 * @param {object} options - 配置选项
 * @returns {string} PDF 文件路径
 */
async function screenshotToPdf(url, outputPath, options = {}) {
  const tempDir = '/tmp';
  const tempFiles = [];

  try {
    // 1. 分屏截图
    const screenshotFiles = await captureScreenshots(url, {
      ...options,
      tempDir,
    });
    tempFiles.push(...screenshotFiles);

    // 2. 拼接长图
    const stitchedPath = path.join(tempDir, 'stitched.png');
    stitchImages(screenshotFiles, stitchedPath);
    tempFiles.push(stitchedPath);

    // 3. 转换 PDF
    convertToPdf(stitchedPath, outputPath);

    return outputPath;
  } finally {
    // 清理临时文件
    tempFiles.forEach((file) => {
      try {
        if (fs.existsSync(file)) {
          fs.unlinkSync(file);
        }
      } catch (err) {
        // 忽略清理错误
      }
    });
  }
}

module.exports = {
  extractIframeUrl,
  captureScreenshots,
  stitchImages,
  convertToPdf,
  screenshotToPdf,
};
