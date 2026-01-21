const { chromium } = require('playwright');
const fs = require('fs');
const { execSync } = require('child_process');

const TARGET_URL = 'https://alidocs.dingtalk.com/i/nodes/DnRL6jAJMGrnOmD5cGqrdpPxWyMoPYe1?utm_scene=person_space&utm_source=dingdoc_doc&utm_medium=dingdoc_doc_splitview';
const PDF_PATH = '/Users/henry/Desktop/1月生意金卡—一图看懂全网最香理财卡.pdf';

(async () => {
  console.log('🚀 启动浏览器...');
  const browser = await chromium.launch({
    headless: false,
    slowMo: 100
  });

  const page = await browser.newPage({
    viewport: { width: 1920, height: 1080 }
  });

  console.log('📄 正在访问文档主页:', TARGET_URL);
  await page.goto(TARGET_URL, {
    waitUntil: 'domcontentloaded',
    timeout: 120000
  });

  console.log('⏳ 等待页面加载...');
  await page.waitForTimeout(5000);

  console.log('🔍 查找 iframe URL...');
  await page.waitForSelector('iframe', { timeout: 10000 });

  const iframeSrc = await page.locator('iframe').getAttribute('src');
  console.log(`✅ 找到 iframe URL: ${iframeSrc.substring(0, 80)}...`);

  await page.close();

  console.log('📄 直接访问 iframe URL...');
  const contentPage = await browser.newPage({
    viewport: { width: 1920, height: 1080 }
  });

  await contentPage.goto(iframeSrc, {
    waitUntil: 'domcontentloaded',
    timeout: 120000
  });

  console.log('⏳ 等待内容加载...');
  await contentPage.waitForTimeout(15000);

  // 尝试多次向下滚动，每次滚动一屏
  console.log('📜 开始手动滚动并截取屏幕...');
  const screenshots = [];
  const viewportHeight = 1080;
  const viewportWidth = 1920;

  // 先滚动回顶部
  await contentPage.evaluate(() => window.scrollTo(0, 0));
  await contentPage.waitForTimeout(2000);

  // 截取第一屏
  const screenshot1 = await contentPage.screenshot({
    path: '/tmp/screenshot_1.png'
  });
  screenshots.push('/tmp/screenshot_1.png');
  console.log('📸 已截取第 1 屏');

  // 向下滚动并截取
  for (let i = 1; i <= 20; i++) {
    const scrollY = viewportHeight * i;
    await contentPage.evaluate((y) => window.scrollTo(0, y), scrollY);
    await contentPage.waitForTimeout(3000);

    const screenshotPath = `/tmp/screenshot_${i + 1}.png`;
    await contentPage.screenshot({ path: screenshotPath });
    screenshots.push(screenshotPath);
    console.log(`📸 已截取第 ${i + 1} 屏 (scrollY: ${scrollY})`);
  }

  await browser.close();

  console.log(`📸 总共截取了 ${screenshots.length} 屏`);

  // 使用 Python 拼接所有截图
  console.log('🔧 正在拼接截图...');
  const pythonScript = `
from PIL import Image
import os

screenshot_files = ${JSON.stringify(screenshots)}
images = [Image.open(f) for f in screenshot_files]

# 计算总高度（简单叠加，可能会有重叠）
total_height = len(images) * 1080
result = Image.new('RGB', (1920, total_height))

y_offset = 0
for img in images:
    result.paste(img, (0, y_offset))
    y_offset += 1080

result.save('/tmp/stitched.png', 'PNG')
print(f'拼接完成，总高度: {total_height}px')
`;

  execSync(`python3 -c "${pythonScript.replace(/"/g, '\\"')}"`, {
    stdio: 'inherit'
  });

  console.log('✅ 截图拼接完成');

  // 转换为 PDF
  console.log('📄 正在转换为 PDF...');
  try {
    execSync(`sips -s format pdf /tmp/stitched.png --out "${PDF_PATH}"`, {
      stdio: 'inherit'
    });
    console.log(`✅ PDF 已保存到: ${PDF_PATH}`);

    const stats = fs.statSync(PDF_PATH);
    console.log(`📦 文件大小: ${(stats.size / 1024).toFixed(2)} KB`);
  } catch (error) {
    console.error('❌ PDF 转换失败，尝试使用 Python PIL...');
    execSync(`python3 -c "
from PIL import Image
img = Image.open('/tmp/stitched.png')
if img.mode != 'RGB':
    img = img.convert('RGB')
img.save('${PDF_PATH}', 'PDF', resolution=150.0, quality=95)
print('PDF 已保存')
"`, { stdio: 'inherit' });
  }

  // 清理临时文件
  screenshots.forEach(f => {
    if (fs.existsSync(f)) fs.unlinkSync(f);
  });
  if (fs.existsSync('/tmp/stitched.png')) {
    fs.unlinkSync('/tmp/stitched.png');
  }
  console.log('🗑️ 临时文件已清理');

  console.log('✨ 完成！');
})();
