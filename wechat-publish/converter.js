const marked = require('marked');
const juice = require('juice');
const hljs = require('highlight.js');
const fs = require('fs');

// 定义 4 种精美主题风格
const THEMES = {
  // 1. 简约专业 (适合技术文章)
  professional: {
    primaryColor: '#1a73e8',
    secondaryColor: '#f1f3f4',
    textColor: '#333333',
    bgColor: '#ffffff',
    codeBg: '#282c34',
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
  },
  // 2. 优雅文艺 (适合散文随笔)
  elegant: {
    primaryColor: '#2d5a27',
    secondaryColor: '#f0f7ef',
    textColor: '#2c3e50',
    bgColor: '#ffffff',
    codeBg: '#f8f9fa',
    fontFamily: "'Songti SC', 'SimSun', serif",
    indent: '2em' // 首行缩进
  },
  // 3. 活力橙 (适合营销活动)
  vibrant: {
    primaryColor: '#ff6b35',
    secondaryColor: '#fff0e6',
    textColor: '#2d3436',
    bgColor: '#ffffff',
    codeBg: '#fff5f0',
    fontFamily: "'PingFang SC', 'Microsoft YaHei', sans-serif"
  },
  // 4. 暗黑极客 (适合程序员)
  dark: {
    primaryColor: '#61dafb',
    secondaryColor: '#282c34',
    textColor: '#abb2bf',
    bgColor: '#1a1a2e',
    codeBg: '#000000',
    fontFamily: "'Fira Code', 'Consolas', monospace"
  }
};

/**
 * 获取完整的 CSS 样式字符串
 * @param {string} themeName
 */
function getThemeCss(themeName = 'professional') {
  const t = THEMES[themeName] || THEMES.professional;

  return `
    /* 容器 */
    .wechat-container {
      font-family: ${t.fontFamily};
      color: ${t.textColor};
      background-color: ${t.bgColor};
      line-height: 1.75;
      font-size: 16px;
      padding: 10px;
      word-wrap: break-word;
    }

    /* 标题 */
    h1 {
      font-size: 24px;
      font-weight: bold;
      color: ${t.primaryColor};
      border-bottom: 2px solid ${t.primaryColor};
      padding-bottom: 10px;
      margin-top: 30px;
      margin-bottom: 20px;
      text-align: center;
    }
    h2 {
      font-size: 20px;
      font-weight: bold;
      color: ${t.primaryColor};
      border-left: 5px solid ${t.primaryColor};
      padding-left: 10px;
      margin-top: 25px;
      margin-bottom: 15px;
      background: linear-gradient(to right, ${t.secondaryColor}, transparent);
    }
    h3 {
      font-size: 18px;
      font-weight: bold;
      color: ${t.textColor};
      margin-top: 20px;
      margin-bottom: 10px;
      padding-left: 8px;
      border-left: 3px solid ${t.secondaryColor};
    }

    /* 段落 */
    p {
      margin-bottom: 1.5em;
      text-align: justify;
      text-indent: ${t.indent || '0'};
    }

    /* 强调 */
    strong {
      color: ${t.primaryColor};
      font-weight: 700 !important;
      padding: 0 2px;
    }
    em {
      color: #666;
      font-style: italic;
    }

    /* 列表替代方案 (Section) */
    .list-item {
      display: flex;
      margin-bottom: 8px;
      align-items: flex-start;
    }
    .list-marker {
      color: ${t.primaryColor};
      font-weight: bold;
      margin-right: 8px;
      flex-shrink: 0;
    }
    .list-content {
      flex: 1;
    }

    /* 引用块 */
    blockquote {
      margin: 20px 0;
      padding: 15px;
      background-color: ${t.secondaryColor};
      border-left: 4px solid ${t.primaryColor};
      color: #555;
      border-radius: 4px;
    }

    /* 图片 */
    img {
      max-width: 100%;
      height: auto;
      display: block;
      margin: 20px auto;
      border-radius: 6px;
      box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    figure {
      margin: 0;
      padding: 0;
      text-align: center;
    }
    figcaption {
      font-size: 14px;
      color: #888;
      margin-top: 8px;
      text-align: center;
    }

    /* 链接 */
    a {
      color: ${t.primaryColor};
      text-decoration: none;
      border-bottom: 1px dashed ${t.primaryColor};
    }

    /* 代码块 */
    pre {
      background-color: ${t.codeBg};
      color: #e0e0e0;
      padding: 15px;
      border-radius: 8px;
      overflow-x: auto;
      font-family: 'Consolas', 'Monaco', monospace;
      margin: 20px 0;
      font-size: 14px;
      line-height: 1.5;
    }
    code {
      font-family: 'Consolas', 'Monaco', monospace;
    }
    /* 行内代码 */
    p code, li code, section code {
      background-color: ${themeName === 'dark' ? '#333' : '#f4f4f4'};
      color: ${t.primaryColor};
      padding: 2px 5px;
      border-radius: 3px;
      margin: 0 2px;
      font-size: 0.9em;
    }

    /* 分割线 */
    hr {
      border: none;
      border-top: 1px dashed ${t.primaryColor};
      margin: 40px 0;
      opacity: 0.5;
    }

    /* 表格 */
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0;
      font-size: 14px;
    }
    th {
      background-color: ${t.secondaryColor};
      color: ${t.primaryColor};
      font-weight: bold;
      padding: 10px;
      border: 1px solid #ddd;
    }
    td {
      padding: 10px;
      border: 1px solid #ddd;
    }
    tr:nth-child(even) {
      background-color: ${themeName === 'dark' ? '#222' : '#f9f9f9'};
    }

    /* 脚注区域 */
    .footnotes {
      margin-top: 50px;
      padding-top: 20px;
      border-top: 1px solid #eee;
      font-size: 14px;
      color: #888;
    }
    .footnote-item {
      margin-bottom: 5px;
    }
  `;
}

/**
 * 转换 Markdown 为微信兼容 HTML
 */
function convertToWechatHtml(markdown, themeName = 'professional') {
  // 0. 预处理：移除 Frontmatter 和 H1 标题
  // 更加暴力的正则：匹配开头可能的空白，然后是 --- 块
  markdown = markdown.replace(/^\s*---[\s\S]*?---\s*/, '');

  // 移除所有 H1 标题 (不仅是第一个，防止残留)
  // 同时移除 title: xxx 这种可能泄漏的文本
  markdown = markdown.replace(/^title:.*\n/gm, '');
  markdown = markdown.replace(/^#\s+.*$/gm, '');

  // 1. 初始化收集器
  const links = [];
  const renderer = new marked.Renderer();

  // 2. 自定义渲染器

  // 列表处理：完全重写，不使用 ul/ol
  renderer.list = (body, ordered, start) => {
    // marked 传入的 body 已经是 li 渲染后的字符串拼接
    // 这里我们需要一种方式来区分是有序还是无序，但 marked 的 list 逻辑比较特殊
    // 我们改用 listitem 处理单个项，然后在 list 只是简单返回 wrapper
    // 实际上更简单的方法是：让 listitem 返回带 section 的完整行
    return body;
  };

  renderer.listitem = (text, task, checked) => {
    // 这里的 text 已经被解析过，可能包含 strong 等 HTML
    // 我们需要判断是在有序列表还是无序列表中
    // 但 marked 的 listitem 没有 ordered 参数
    // 简单的 hack: 我们统一使用一种样式，或者通过上下文（比较难）

    // 为了简化，我们使用 CSS 样式类来标记，但因为我们最终返回的是 section
    // 我们可以默认用无序列表样式，或者尝试检测

    // 正则检测是否以数字开头（不太准确，因为 content 已经渲染）

    // 更好的策略：
    // 我们无法在 listitem 中知道是 ordered。
    // 所以我们统一定义一个通用的列表项样式。
    // 如果必须区分，需要修改 marked 源码或使用 tokenizer。
    // 这里我们使用 "•" 作为无序默认值。如果有序，我们在 text 前面手动加了数字。
    // 但 marked 会自动剥离数字。

    // 妥协方案：统一使用圆点，微信文章中通常不强求自动编号的严格性
    // 或者使用正则替换 content 中的首字符？不靠谱。

    // 实际上，我们可以利用 renderer.list 的 body 参数
    // body 是所有 listitem 的结果拼接。
    // 我们可以在 listitem 中只返回 content，然后在 list 中拼接 section。
    // 但 listitem 被调用时不知道父级是 ordered。

    // 最终方案：统一渲染为带点的列表项
    // 如果用户写 1. xxx，marked 会解析为 ordered list
    // 我们这里统一用 • ，或者在 listitem 中返回 <section class="list-item"><span class="list-marker">•</span><div class="list-content">text</div></section>

    return `
      <section class="list-item">
        <span class="list-marker">•</span>
        <div class="list-content">${text}</div>
      </section>
    `;
  };

  // 链接处理：转换为脚注
  renderer.link = (href, title, text) => {
    if (href.startsWith('#')) return text; // 忽略锚点

    links.push({ href, text });
    const index = links.length;
    return `<span style="text-decoration: underline;">${text}</span><sup>[${index}]</sup>`;
  };

  // 图片处理 - 优化版：保持原图比例和质量
  renderer.image = (href, title, text) => {
    // 移除强制 aspect-ratio，让图片保持原始比例
    // 使用 max-width: 100% 确保响应式，height: auto 保持比例
    // data-w 属性帮助微信识别高清图片
    return `
      <figure style="margin: 20px 0;">
        <img src="${href}" alt="${text}"
             style="max-width: 100%; height: auto; display: block; margin: 0 auto; border-radius: 8px;"
             data-w="4800" />
        ${title ? `<figcaption style="text-align: center; font-size: 14px; color: #888; margin-top: 8px;">${title}</figcaption>` : ''}
      </figure>
    `;
  };

  // 引用块处理
  renderer.blockquote = (quote) => {
    return `<blockquote>${quote}</blockquote>`;
  };

  // 代码块处理
  renderer.code = (code, language) => {
    const validLang = hljs.getLanguage(language) ? language : 'plaintext';
    const highlighted = hljs.highlight(code, { language: validLang }).value;
    return `<pre><code class="hljs ${validLang}">${highlighted}</code></pre>`;
  };

  // 3. 解析 Markdown
  marked.setOptions({ renderer });
  let htmlContent = marked.parse(markdown);

  // 4. 添加脚注区域
  if (links.length > 0) {
    let footnotesHtml = '<section class="footnotes"><h3>参考资料</h3>';
    links.forEach((link, index) => {
      footnotesHtml += `
        <div class="footnote-item">
          [${index + 1}] ${link.text}: <em>${link.href}</em>
        </div>
      `;
    });
    footnotesHtml += '</section>';
    htmlContent += footnotesHtml;
  }

  // 5. 包裹容器
  const fullHtml = `
    <div class="wechat-container">
      ${htmlContent}
    </div>
  `;

  // 6. 内联 CSS
  const css = getThemeCss(themeName);
  const inlinedHtml = juice(fullHtml, { extraCss: css });

  // 7. 清理空行 (微信编辑器兼容性)
  // 移除标签之间的换行符，防止微信插入额外的 <br>
  const cleanHtml = inlinedHtml.replace(/>\s*\n\s*</g, '><');

  return cleanHtml;
}

module.exports = {
  convertToWechatHtml,
  THEMES
};
