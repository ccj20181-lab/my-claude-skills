const fs = require('fs');
const path = require('path');
const fetch = require('node-fetch');
const FormData = require('form-data');
const { execSync } = require('child_process');

const MAX_WECHAT_IMAGE_BYTES = parseInt(process.env.WECHAT_IMAGE_MAX_BYTES || `${6 * 1024 * 1024}`, 10);
const MAX_WECHAT_IMAGE_WIDTH = parseInt(process.env.WECHAT_IMAGE_MAX_WIDTH || '2400', 10);
const WECHAT_IMAGE_QUALITY = parseInt(process.env.WECHAT_IMAGE_QUALITY || '92', 10);
const SKIP_IMAGE_RESIZE = process.env.SKIP_IMAGE_RESIZE === 'true';
const IMGBB_HOTLINK_PREFERENCE = process.env.IMGBB_HOTLINK || 'display'; // full|display|thumb
const IMAGE_PROXY = process.env.IMAGE_PROXY || 'https://images.weserv.nl/?w=2400&url=';
const IMAGE_PROXY_HOSTS = (process.env.IMAGE_PROXY_HOSTS || 'i.ibb.co,files.catbox.moe').split(',').map(s => s.trim()).filter(Boolean);
const IMAGE_HOST = process.env.IMAGE_HOST || 'catbox'; // catbox | imgbb

// 配置信息
const IMGBB_CONFIG = {
  apiKey: process.env.IMGBB_API_KEY || '9d823e5d2dc9c968daf476e4abfab336',
  endpoint: 'https://api.imgbb.com/1/upload'
};

const CATBOX_CONFIG = {
  endpoint: 'https://catbox.moe/user/api.php'
};

/**
 * 上传单张图片到 ImgBB
 * @param {string} localFilePath - 本地图片路径
 * @param {string} fileName - 可选的文件名
 * @returns {Promise<{success: boolean, url: string, deleteUrl: string}>}
 */
async function uploadToImgBB(localFilePath, fileName) {
  try {
    if (!fs.existsSync(localFilePath)) {
      throw new Error(`文件不存在: ${localFilePath}`);
    }

    // 使用 multipart/form-data 直传二进制，避免 base64 走 URLSearchParams
    // （base64 方式在部分场景会导致 ImgBB 返回低清缩略图链接）
    const form = new FormData();
    form.append('key', IMGBB_CONFIG.apiKey);
    form.append('image', fs.createReadStream(localFilePath), {
      filename: path.basename(localFilePath)
    });
    if (fileName) {
      form.append('name', fileName);
    }

    console.log(`正在上传图片: ${path.basename(localFilePath)}...`);

    const response = await fetch(IMGBB_CONFIG.endpoint, {
      method: 'POST',
      body: form,
      headers: form.getHeaders()
    });

    const result = await response.json();

    if (result.success) {
      // ImgBB 热链默认会根据账号设置降清晰度（无 Referer 时）
      // 使用 display_url/medium 可以避免 180x180 的缩略图
      const data = result.data || {};
      const fullUrl = (data.image && data.image.url) || data.url;
      const displayUrl = data.display_url || (data.medium && data.medium.url);
      const thumbUrl = data.thumb && data.thumb.url;

      let chosenUrl = fullUrl;
      // 如果启用了代理，优先走原图 URL，避免被 ImgBB 热链降清晰度
      if (!IMAGE_PROXY) {
        if (IMGBB_HOTLINK_PREFERENCE === 'display' && displayUrl) chosenUrl = displayUrl;
        if (IMGBB_HOTLINK_PREFERENCE === 'thumb' && thumbUrl) chosenUrl = thumbUrl;
      } else if (!chosenUrl && displayUrl) {
        chosenUrl = displayUrl;
      }

      const proxiedUrl = applyImageProxy(chosenUrl);
      console.log(`✅ 上传成功: ${proxiedUrl}`);
      return {
        success: true,
        url: proxiedUrl,
        deleteUrl: result.data.delete_url
      };
    } else {
      throw new Error(result.error ? result.error.message : '未知上传错误');
    }
  } catch (error) {
    console.error(`❌ 上传失败: ${error.message}`);
    throw error;
  }
}

/**
 * 上传单张图片到 Catbox (匿名直链，无防盗链限制)
 * @param {string} localFilePath
 * @returns {Promise<{success: boolean, url: string}>}
 */
async function uploadToCatbox(localFilePath) {
  try {
    if (!fs.existsSync(localFilePath)) {
      throw new Error(`文件不存在: ${localFilePath}`);
    }

    const form = new FormData();
    form.append('reqtype', 'fileupload');
    form.append('fileToUpload', fs.createReadStream(localFilePath), {
      filename: path.basename(localFilePath)
    });

    console.log(`正在上传图片(猫盒): ${path.basename(localFilePath)}...`);

    const response = await fetch(CATBOX_CONFIG.endpoint, {
      method: 'POST',
      body: form,
      headers: form.getHeaders()
    });

    const text = (await response.text()).trim();
    if (!response.ok || !text.startsWith('http')) {
      throw new Error(`Catbox 上传失败: ${text}`);
    }

    console.log(`✅ 上传成功: ${text}`);
    return { success: true, url: text };
  } catch (error) {
    console.error(`❌ Catbox 上传失败: ${error.message}`);
    throw error;
  }
}

/**
 * 读取本地图片尺寸 (依赖 macOS 自带 sips)
 * @param {string} localFilePath
 * @returns {{width:number, height:number}|null}
 */
function getImageDimensions(localFilePath) {
  try {
    const output = execSync(`sips -g pixelWidth -g pixelHeight "${localFilePath}"`).toString();
    const widthMatch = output.match(/pixelWidth: (\\d+)/);
    const heightMatch = output.match(/pixelHeight: (\\d+)/);
    if (widthMatch && heightMatch) {
      return {
        width: parseInt(widthMatch[1], 10),
        height: parseInt(heightMatch[1], 10)
      };
    }
  } catch (e) {
    // 忽略尺寸获取失败，使用基础标签
  }
  return null;
}

/**
 * 将过大的图片压缩/缩放到微信友好尺寸
 * @param {string} localFilePath
 * @returns {{path:string, dims:{width:number,height:number}|null}}
 */
function prepareImageForUpload(localFilePath) {
  let dims = getImageDimensions(localFilePath);
  let stats = null;
  try {
    stats = fs.statSync(localFilePath);
  } catch (e) {
    return { path: localFilePath, dims };
  }

  const tooLarge = stats.size > MAX_WECHAT_IMAGE_BYTES;
  const tooWide = dims && dims.width > MAX_WECHAT_IMAGE_WIDTH;

  if (SKIP_IMAGE_RESIZE || (!tooLarge && !tooWide)) {
    return { path: localFilePath, dims };
  }

  const ext = path.extname(localFilePath);
  const baseName = path.basename(localFilePath, ext);
  const tempDir = path.join(__dirname, 'temp', 'processed');
  if (!fs.existsSync(tempDir)) {
    fs.mkdirSync(tempDir, { recursive: true });
  }

  const outputPath = path.join(tempDir, `${baseName}_wechat.jpg`);
  try {
    // -Z: 让最长边不超过指定值；formatOptions 为 JPEG 质量
    execSync(`sips -Z ${MAX_WECHAT_IMAGE_WIDTH} -s format jpeg -s formatOptions ${WECHAT_IMAGE_QUALITY} "${localFilePath}" --out "${outputPath}"`);
    dims = getImageDimensions(outputPath);
    return { path: outputPath, dims };
  } catch (e) {
    // 失败则回退原图
    return { path: localFilePath, dims };
  }
}

/**
 * 推断图片类型
 * @param {string} filePath
 * @returns {string}
 */
function inferImageType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (ext === '.png') return 'png';
  if (ext === '.webp') return 'webp';
  return 'jpeg';
}

/**
 * 为 ImgBB 链接套一层代理，规避热链限制（无 Referer 时会返回 180x180）
 * @param {string} url
 * @returns {string}
 */
function applyImageProxy(url) {
  if (!IMAGE_PROXY) return url;
  try {
    const parsed = new URL(url);
    if (!IMAGE_PROXY_HOSTS.includes(parsed.hostname)) return url;
  } catch (e) {
    return url;
  }
  return `${IMAGE_PROXY}${encodeURIComponent(url)}`;
}

/**
 * 扫描 Markdown 内容中的本地图片并上传替换
 * @param {string} markdown - Markdown 内容
 * @param {string} basePath - Markdown 文件所在的目录，用于解析相对路径
 * @returns {Promise<string>} - 替换后的 Markdown
 */
async function processMarkdownImages(markdown, basePath) {
  // 匹配 markdown 图片语法: ![alt](path "title")
  // 排除已经是网络图片的链接 (http:// 或 https://)
  const regex = /!\[(.*?)\]\(((?!http|https).*?)(?:\s+"(.*?)")?\)/g;
  let match;
  let replacements = [];

  // 第一步：收集所有需要上传的图片
  while ((match = regex.exec(markdown)) !== null) {
    const [fullMatch, alt, imgPath, title] = match;
    let absolutePath = imgPath;

    // 处理相对路径
    if (!path.isAbsolute(imgPath)) {
      absolutePath = path.resolve(basePath, imgPath);
    }

    replacements.push({
      fullMatch,
      alt,
      title,
      absolutePath
    });
  }

  if (replacements.length === 0) {
    return markdown;
  }

  console.log(`发现 ${replacements.length} 张本地图片，开始处理...`);

  // 第二步：并发上传所有图片
  // 使用 Map 缓存已上传的图片，避免重复上传
  const uploadCache = new Map();
  let newMarkdown = markdown;

  for (const item of replacements) {
    try {
      let imageUrl;
      const prepared = prepareImageForUpload(item.absolutePath);

      if (uploadCache.has(item.absolutePath)) {
        imageUrl = uploadCache.get(item.absolutePath);
        console.log(`使用缓存图片: ${path.basename(item.absolutePath)}`);
      } else {
        const result = IMAGE_HOST === 'imgbb'
          ? await uploadToImgBB(prepared.path, item.alt)
          : await uploadToCatbox(prepared.path);
        imageUrl = applyImageProxy(result.url);
        uploadCache.set(item.absolutePath, imageUrl);
      }

      // 读取尺寸并生成微信友好的 img 标签
      const dims = prepared.dims;
      const imgType = inferImageType(prepared.path);

      const dataRatio = dims ? (dims.height / dims.width).toFixed(4) : null;
      const dataW = dims ? dims.width : null;

      const placeholder = 'data:image/gif;base64,R0lGODlhAQABAAAAACw=';
      const attrs = [
        `src="${placeholder}"`,
        `data-src="${imageUrl}"`,
        `alt="${item.alt}"`
      ];
      if (dataW) attrs.push(`data-w="${dataW}"`);
      if (dataRatio) attrs.push(`data-ratio="${dataRatio}"`);
      if (imgType) attrs.push(`data-type="${imgType}"`);

      const figcaption = item.title ? `<figcaption>${item.title}</figcaption>` : '';
      const newTag = `<figure><img ${attrs.join(' ')} />${figcaption}</figure>`;

      // 替换内容 (注意：简单的 replace 可能会替换错相同的字符串，最好按位置替换或确保唯一性)
      // 这里为简单起见使用全局替换，假设 fullMatch 是唯一的或内容一致
      newMarkdown = newMarkdown.replace(item.fullMatch, newTag);

    } catch (error) {
      console.error(`处理图片 ${item.absolutePath} 失败，将保留原路径: ${error.message}`);
    }
  }

  return newMarkdown;
}

module.exports = {
  uploadToImgBB,
  uploadToCatbox,
  processMarkdownImages
};
