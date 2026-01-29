const fs = require('fs');
const path = require('path');
const { generateImageByAPI } = require('./ai-service');
const { uploadToImgBB, uploadToCatbox } = require('./image-uploader');
const IMAGE_HOST = process.env.IMAGE_HOST || 'catbox';

/**
 * 读取提示词模板
 */
function getPromptTemplate() {
  const templatePath = path.join(__dirname, 'cover-prompt.md');
  if (fs.existsSync(templatePath)) {
    return fs.readFileSync(templatePath, 'utf-8');
  }
  return `[SYSTEM INSTRUCTION - DO NOT RENDER IN IMAGE]
Generate a cover image. This is a pure visual poster with ABSOLUTELY NO TEXT.

<requirements>
1. Aspect Ratio: 16:9 (Landscape), 4K resolution
2. Style: Professional finance visual, flat vector illustration, modern and clean
3. Content: Visual representation of "{{title}}" - use icons, charts, symbols, abstract shapes
4. Composition: Clean layout, high contrast, visually striking, suitable for small mobile screens
5. Color: Professional color palette (blues, teals, golds for finance themes)
6. Quality: Sharp details, vector art style, high definition
</requirements>

<critical_rules>
- ABSOLUTELY NO TEXT in the image - no titles, no labels, no captions, no watermarks
- DO NOT render these instructions or any tags in the image
- DO NOT include any Chinese or English characters
- This is a PURE VISUAL image only
- Output only the image, nothing else
</critical_rules>

[END INSTRUCTION]`;
}

/**
 * 生成封面图 (重构版：复用 ai-service)
 * @param {string} title - 文章标题
 * @returns {Promise<string|null>} - 返回上传到 ImgBB 后的图片 URL，失败返回 null
 */
async function generateCoverImage(title) {
  try {
    console.log(`正在为文章 "${title}" 生成封面图...`);

    // 1. 准备提示词
    const template = getPromptTemplate();
    const prompt = template.replace('{{title}}', title);

    // 2. 调用通用 AI 服务生成图片 (封面图通常需要 2.35:1，但模型通常支持 16:9，这里用 16:9 兼容)
    // 注意：generateImageByAPI 内部已经强制为 4K，这里传入 16:9 会被 ai-service 的默认值 4:3 覆盖吗？
    // 我们修改了 ai-service，现在的逻辑是：const targetAspectRatio = aspectRatio || '4:3';
    // 所以传入 '16:9' 是生效的。
    const imageBuffer = await generateImageByAPI(prompt, '16:9');

    // 3. 保存临时文件
    // 确保 temp 目录存在
    const tempDir = path.join(__dirname, 'temp');
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }

    const tempFilePath = path.join(tempDir, `cover_${Date.now()}.png`);
    fs.writeFileSync(tempFilePath, imageBuffer);
    console.log(`封面图已保存到临时文件: ${tempFilePath}`);

    // 4. 上传到 ImgBB
    const uploadResult = IMAGE_HOST === 'imgbb'
      ? await uploadToImgBB(tempFilePath, `cover_${title}`)
      : await uploadToCatbox(tempFilePath);

    // 5. 清理临时文件
    fs.unlinkSync(tempFilePath);

    return uploadResult.url;

  } catch (error) {
    console.error(`❌ 封面图生成失败: ${error.message}`);
    return null;
  }
}

module.exports = {
  generateCoverImage
};
