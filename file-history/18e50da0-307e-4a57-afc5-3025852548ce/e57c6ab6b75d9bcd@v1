
const { chromium } = require('playwright');
const TARGET_URL = 'https://bigmodel.cn/glm-coding';

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  console.log('Navigating to ' + TARGET_URL);
  await page.goto(TARGET_URL);

  // Wait a bit for fonts to load
  await page.waitForTimeout(2000);

  const fontInfo = await page.evaluate(() => {
    const results = {};

    // Check body
    const bodyStyle = window.getComputedStyle(document.body);
    results.body = bodyStyle.fontFamily;

    // Check specific elements likely to have text
    const selectors = ['h1', 'h2', 'p', '.text-content', 'div'];

    results.elements = [];

    selectors.forEach(sel => {
        const el = document.querySelector(sel);
        if (el && el.innerText && el.innerText.trim().length > 0) {
            const style = window.getComputedStyle(el);
            results.elements.push({
                tag: sel,
                textSnippet: el.innerText.substring(0, 20),
                fontFamily: style.fontFamily,
                renderedFonts: style.fontFamily // Standard JS can't get *actual* rendered font without DevTools protocol, but computed stack gives clues
            });
        }
    });

    return results;
  });

  console.log('Font Information:');
  console.log(JSON.stringify(fontInfo, null, 2));

  await page.screenshot({ path: '/tmp/font_check.png', fullPage: false });
  console.log('Snapshot taken at /tmp/font_check.png');

  await browser.close();
})();
