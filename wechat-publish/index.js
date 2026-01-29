#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const readline = require('readline');
const fetch = require('node-fetch');
const { convertToWechatHtml, THEMES } = require('./converter');
const themeKeys = Object.keys(THEMES);
const { processMarkdownImages } = require('./image-uploader');
const { generateCoverImage } = require('./cover-generator');
const { processAIPlaceholders, autoInsertImagePlaceholders } = require('./ai-service');

// 配置
const WECHAT_CONFIG = {
  apiKey: process.env.WECHAT_API_KEY || 'xhs_4ded7e5d7cef78a0cd27660b5be13db0',
  apiBase: process.env.WECHAT_API_BASE || 'https://wx.limyai.com/api/openapi'
};

// 工具函数：创建 CLI 交互接口
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function askQuestion(query) {
  return new Promise(resolve => rl.question(query, resolve));
}

// 工具函数：提取文章标题
function extractTitle(markdown) {
  // 1. 尝试从 YAML Frontmatter 提取
  const yamlMatch = markdown.match(/^---\n([\s\S]*?)\n---/);
  if (yamlMatch) {
    const yamlContent = yamlMatch[1];
    const titleMatch = yamlContent.match(/title:\s*(.*)/);
    if (titleMatch) return titleMatch[1].trim().replace(/^['"]|['"]$/g, '');
  }

  // 2. 尝试提取第一个 # 标题
  const h1Match = markdown.match(/^#\s+(.*)/m);
  if (h1Match) return h1Match[1].trim();

  return '未命名文章';
}

// 工具函数：提取摘要
function extractSummary(markdown) {
  // 移除标题、HTML标签、图片链接，提取前 100 字
  const plainText = markdown
    .replace(/^---\n[\s\S]*?\n---/, '') // 移除 yaml
    .replace(/#+\s+.*?\n/g, '') // 移除标题
    .replace(/!\[.*?\]\(.*?\)/g, '') // 移除图片
    .replace(/\[.*?\]\(.*?\)/g, '$1') // 保留链接文字
    .replace(/(\*\*|__)(.*?)\1/g, '$2') // 移除粗体
    .replace(/(\*|_)(.*?)\1/g, '$2') // 移除斜体
    .replace(/`.*?`/g, '') // 移除行内代码
    .replace(/\n+/g, ' ')
    .trim();

  return plainText.substring(0, 100) + '...';
}

// API: 获取公众号列表
async function getWechatAccounts() {
  try {
    const url = `${WECHAT_CONFIG.apiBase}/wechat-accounts`;
    console.log(`📡 请求公众号列表: ${url}`);

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'X-API-Key': WECHAT_CONFIG.apiKey,
        'Content-Type': 'application/json'
      }
    });

    const text = await response.text();
    // console.log(`📥 接口响应 (${response.status}):`, text.substring(0, 500)); // 调试用

    if (!response.ok) return [];

    const data = JSON.parse(text);
    // 适配不同的返回结构
    if (Array.isArray(data)) return data;
    if (data.data && Array.isArray(data.data)) return data.data;
    if (data.list && Array.isArray(data.list)) return data.list;

    // 适配 { data: { accounts: [] } } 结构
    if (data.data && data.data.accounts && Array.isArray(data.data.accounts)) return data.data.accounts;

    return [];
  } catch (e) {
    console.error('❌ 获取公众号列表失败:', e.message);
    return [];
  }
}

// API: 发布文章
async function publishArticle(payload) {
  const url = `${WECHAT_CONFIG.apiBase}/wechat-publish`;
  console.log(`正在发布到 API: ${url}`);

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'X-API-Key': WECHAT_CONFIG.apiKey,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  const data = await response.json();
  return {
    ok: response.ok,
    status: response.status,
    data
  };
}

async function main() {
  try {
    console.log('🚀 启动微信公众号发布助手...');

    // 1. 获取文件路径
    let filePath = process.argv[2];
    if (!filePath) {
      filePath = await askQuestion('请输入 Markdown 文件路径: ');
    }

    // 支持 ~ 路径
    if (filePath.startsWith('~')) {
      filePath = path.join(process.env.HOME, filePath.slice(1));
    }

    filePath = path.resolve(filePath);

    if (!fs.existsSync(filePath)) {
      throw new Error(`文件不存在: ${filePath}`);
    }

    // 2. 读取并预处理文件
    console.log(`📖 读取文件: ${path.basename(filePath)}`);
    const rawMarkdown = fs.readFileSync(filePath, 'utf-8');
    const title = extractTitle(rawMarkdown);
    const summary = extractSummary(rawMarkdown);
    console.log(`📝 标题: ${title}`);
    console.log(`📄 摘要: ${summary}`);

    // 3. 选择主题
    let selectedTheme = 'professional';
    if (process.env.THEME) {
      // 支持传入序号或名称
      if (/^\d+$/.test(process.env.THEME)) {
         const idx = parseInt(process.env.THEME) - 1;
         selectedTheme = themeKeys[idx] || 'professional';
      } else if (THEMES[process.env.THEME]) {
         selectedTheme = process.env.THEME;
      }
      console.log(`✅ 使用环境变量设置的主题: ${selectedTheme}`);
    } else {
      console.log('\n🎨 请选择排版主题:');
      themeKeys.forEach((key, index) => {
        console.log(`${index + 1}. ${key} (${index === 0 ? '默认' : ''})`);
      });

      const themeIndex = await askQuestion('请输入序号 (直接回车默认 1): ');
      selectedTheme = themeKeys[parseInt(themeIndex) - 1] || 'professional';
      console.log(`✅ 已选择主题: ${selectedTheme}`);
    }

    // 4. 选择公众号
    let wechatAppid = process.env.WECHAT_APPID || '';

    if (wechatAppid) {
       console.log(`✅ 使用环境变量设置的 AppID: ${wechatAppid}`);
    } else {
      console.log('\n🤖 正在获取公众号列表...');
      const accounts = await getWechatAccounts();

      if (accounts && accounts.length > 0) {
        if (accounts.length === 1) {
          // 只有一个公众号，自动选择
          // 适配接口字段: wechatAppid, name
          wechatAppid = accounts[0].wechatAppid || accounts[0].appid;
          const name = accounts[0].name || accounts[0].nick_name;
          console.log(`✅ 自动选择公众号: ${name} (${wechatAppid})`);
        } else {
          // 多个公众号，让用户选择
          console.log('📋 请选择目标公众号:');
          accounts.forEach((acc, idx) => {
            const name = acc.name || acc.nick_name;
            const appId = acc.wechatAppid || acc.appid;
            console.log(`${idx + 1}. ${name} (${appId})`);
          });

          const accIndex = await askQuestion('请输入序号: ');
          const selectedAcc = accounts[parseInt(accIndex) - 1];
          if (selectedAcc) {
            wechatAppid = selectedAcc.wechatAppid || selectedAcc.appid;
            const name = selectedAcc.name || selectedAcc.nick_name;
            console.log(`✅ 已选择: ${name}`);
          } else {
            console.log('⚠️ 选择无效，将跳过 AppID 设置（可能会导致发布失败）');
          }
        }
      } else {
        console.log('⚠️ 未获取到公众号列表，且未配置 WECHAT_APPID。');
        console.log('⚠️ 将尝试直接发布（不带 AppID）...');
      }
    }

    // 5. 图片处理流程
    console.log('\n🖼️ 开始处理图片...');

    // 5.0 自动插入配图 (New Feature: Image per H2)
    // 根据 H2 标题自动插入图片占位符
    const markdownWithPlaceholders = autoInsertImagePlaceholders(rawMarkdown);

    // 5.1 生成 AI 配图 (New Feature)
    // 扫描 ![prompt](ai:generate) 语法，生成本地图片
    // 使用文章所在目录的 .ai-images 子目录作为缓存目录，避免重复生成
    const aiImageCacheDir = path.join(path.dirname(filePath), '.ai-images');
    const markdownWithAIImages = await processAIPlaceholders(markdownWithPlaceholders, aiImageCacheDir);

    // 5.2 生成封面图
    let coverImageUrl = process.env.COVER_URL || '';
    let needCover = 'n';

    if (process.env.ENABLE_COVER) {
       needCover = process.env.ENABLE_COVER === 'true' ? 'y' : 'n';
       console.log(`✅ 环境变量配置 AI 封面: ${needCover}`);
    } else if (!coverImageUrl) {
       needCover = await askQuestion('是否生成 AI 封面图? (Y/n): ');
       if (!needCover) needCover = 'y'; // Default to Yes
    }

    if (needCover.toLowerCase() === 'y' && !coverImageUrl) {
       // 检查 Gemini Key
       if (!process.env.GEMINI_API_KEY && !process.env.NANOBANANA_API_KEY) {
         console.log('⚠️ 未检测到 API Key，尝试询问...');
         const key = await askQuestion('请输入 AI 生图 API Key: ');
         process.env.GEMINI_API_KEY = key; // 临时赋值给 Gemini
       }
       coverImageUrl = await generateCoverImage(title);
    }

    // 如果没有生成封面，询问是否使用本地图片或 URL
    if (!coverImageUrl) {
      if (process.env.THEME || process.env.ENABLE_COVER) {
         console.log('ℹ️ 自动模式：未提供封面图 URL，将使用默认占位图。');
      } else {
         const inputCover = await askQuestion('请输入封面图 URL (留空则不设置): ');
         if (inputCover) coverImageUrl = inputCover;
      }
    }

    // 兜底默认封面
    if (!coverImageUrl) {
        coverImageUrl = 'https://placehold.co/900x383/1a73e8/ffffff.png?text=WeChat+Publish';
    }

    // 5.3 处理正文图片 (本地上传 -> 图床)
    // 这里传入的是已经经过 AI 处理的 markdown，此时 AI 图片已变成 file://... 格式的本地路径
    const markdownWithRemoteImages = await processMarkdownImages(markdownWithAIImages, path.dirname(filePath));

    // 6. 转换 HTML
    console.log('\n⚙️ 正在转换 HTML...');
    const htmlContent = convertToWechatHtml(markdownWithRemoteImages, selectedTheme);

    // 7. 发布
    console.log('\n🚀 正在发送请求...');
    const payload = {
      // wechatAppid: wechatAppid,
      title: title.substring(0, 64),
      content: htmlContent,
      summary: summary.substring(0, 120),
      coverImage: coverImageUrl,
      contentFormat: "html",
      articleType: "news"
    };

    if (wechatAppid) {
        payload.wechatAppid = wechatAppid;
    }

    const result = await publishArticle(payload);

    const isSuccess = result.ok && result.data && (result.data.success === true || result.data.code === 0);

    if (isSuccess) {
      console.log('\n✨✨✨ 发布成功！✨✨✨');
      console.log('请前往微信公众号后台 -> 草稿箱 查看。');

      const responseData = result.data.data || result.data;
      if (responseData.mediaId || responseData.media_id) {
          console.log(`Media ID: ${responseData.mediaId || responseData.media_id}`);
      }
    } else {
      console.error('\n❌ 发布失败');
      console.error('Status:', result.status);
      console.error('Response:', JSON.stringify(result.data, null, 2));
    }

  } catch (error) {
    console.error('\n❌ 发生错误:', error.message);
  } finally {
    rl.close();
  }
}

main();
