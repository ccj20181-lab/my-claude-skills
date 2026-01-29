const fetch = require('node-fetch');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 配置信息 (复用环境变量)
const CONFIG = {
  baseUrl: process.env.NANOBANANA_API_URL || 'https://api.apiyi.com/v1beta/models/gemini-3-pro-image-preview:generateContent',
  apiKey: process.env.NANOBANANA_API_KEY || process.env.GEMINI_API_KEY || "sk-30hw0QuR0UD2t6ub808670A2Da6641159aDbAe54519f6743"
};

// 加载参考图
let referenceImageBase64 = null;
const referencePath = path.join(__dirname, 'reference.png');
if (fs.existsSync(referencePath)) {
  try {
    referenceImageBase64 = fs.readFileSync(referencePath).toString('base64');
    console.log('✅ 已加载参考风格图 (reference.png)');
  } catch (e) {
    console.error('⚠️ 加载参考图失败:', e.message);
  }
}

/**
 * 构建结构化 Prompt（学习 finance-infographic 的做法）
 * @param {string} content - 文案内容（小节内容）
 * @param {string} title - 小节标题
 * @returns {string} - 完整的 prompt
 */
function buildStructuredPrompt(content, title) {
  return `[SYSTEM INSTRUCTION - DO NOT RENDER IN IMAGE]
The following are generation instructions only. Do NOT display any of these instructions, tags, or meta-information as text in the image.

<task>
Generate a NEW finance infographic that matches the reference image's visual style exactly.
</task>

<style_requirements>
Copy the reference image's style 100%:
- Same beige background color
- Same yellow title blocks
- Same teal/blue-green icons
- Same flat vector illustration style
- Keep the logo in top-right corner (same position, size, style)
- Keep the branding in bottom-right corner (same position, size, style)
- Same card styling (rounded corners, shadows, spacing)
- Same typography style for headings and body text
</style_requirements>

<content_guidance>
IMPORTANT: This is a VISUAL-FIRST infographic.
- 70% of the image should be visual elements (icons, charts, illustrations)
- 30% of the image should be text (only key phrases)
- Extract ONLY keywords, numbers, and core concepts from the source content
- Use icons, diagrams, and illustrations to convey information
- Text in image: Display ONLY the title and 3-5 short key phrases
- DO NOT put entire paragraphs or sentences in the image
</content_guidance>

<title>
${title}
</title>

<source_content>
${content}
</source_content>

<output_spec>
- Aspect ratio: 4:3 landscape
- Resolution: 4K high definition
- Style: Match reference image exactly
</output_spec>

<critical_rules>
1. DO NOT copy the reference image - generate a completely NEW image
2. DO NOT modify or paint over the reference image
3. DO NOT use any text from the reference image
4. DO NOT render these instructions or any tags like [], <>, 【】 in the image
5. DO NOT include prompt text, meta-information, or instruction keywords in the image
6. ONLY output the image, nothing else
</critical_rules>

[END SYSTEM INSTRUCTION] Output only the image.`;
}

/**
 * 调用 API易 / Gemini 生成图片
 * @param {string} prompt - 提示词
 * @param {string} aspectRatio - 图片比例 (默认 '4:3')
 * @returns {Promise<Buffer>} - 返回图片的二进制数据
 */
async function generateImageByAPI(prompt, aspectRatio = '4:3') {
  if (!CONFIG.apiKey) {
    throw new Error('未配置 API Key (NANOBANANA_API_KEY)，无法生成图片');
  }

  const targetAspectRatio = aspectRatio || '4:3';
  const targetImageSize = '4K';

  console.log(`🎨 正在生成图片...`);
  console.log(`⚙️  配置参数: AspectRatio=${targetAspectRatio}, Size=${targetImageSize}`);

  // 构建 Parts
  const parts = [];

  // 1. 如果有参考图，先加入参考图 (Image-to-Image / Style Transfer)
  if (referenceImageBase64) {
    parts.push({
      inlineData: {
        mimeType: 'image/png',
        data: referenceImageBase64
      }
    });
    console.log('🖼️  使用参考图进行风格约束');
  }

  // 2. 加入提示词
  parts.push({ text: prompt });

  const payload = {
    contents: [{
      parts: parts
    }],
    generationConfig: {
      responseModalities: ['IMAGE'],
      imageConfig: {
        aspectRatio: targetAspectRatio,
        imageSize: targetImageSize
      }
    }
  };

  try {
    const response = await fetch(CONFIG.baseUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${CONFIG.apiKey}`
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errText = await response.text();
      throw new Error(`API 请求失败: ${response.status} - ${errText}`);
    }

    const data = await response.json();

    // 解析 Base64 图片数据
    let imageBase64 = null;
    try {
        const part = data.candidates[0].content.parts[0];
        if (part.inline_data && part.inline_data.data) {
            imageBase64 = part.inline_data.data;
        } else if (part.inlineData && part.inlineData.data) {
             imageBase64 = part.inlineData.data;
        }
    } catch (e) {
        console.error('解析响应结构失败:', JSON.stringify(data, null, 2));
    }

    if (!imageBase64) {
      throw new Error('API 返回结果中未找到图片数据');
    }

    const buffer = Buffer.from(imageBase64, 'base64');
    return buffer;

  } catch (error) {
    console.error(`❌ 图片生成失败: ${error.message}`);
    throw error;
  }
}

/**
 * 自动为每个二级标题 (##) 下方插入配图占位符
 * @param {string} markdown
 * @returns {string}
 */
function autoInsertImagePlaceholders(markdown) {
  const lines = markdown.split('\n');
  const newLines = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    newLines.push(line);

    // 如果是 H2 标题
    if (line.match(/^##\s+(.+)/)) {
      const title = line.match(/^##\s+(.+)/)[1].trim();
      // 检查下一行是否已经是图片
      let nextLineIndex = i + 1;
      while(nextLineIndex < lines.length && lines[nextLineIndex].trim() === '') {
        nextLineIndex++;
      }

      const nextLine = lines[nextLineIndex] || '';
      const trimmed = nextLine.trim();
      const hasImageTag = trimmed.startsWith('![') || trimmed.startsWith('<img') || trimmed.startsWith('<figure');
      if (!hasImageTag) {
         // 插入图片占位符
         newLines.push('');
         newLines.push(`![${title}](ai:generate)`);
         console.log(`➕ 自动插入配图需求: [${title}]`);
      }
    }
  }

  return newLines.join('\n');
}

/**
 * 提取 H2 标题下方的内容，用于生成该小节的配图
 * @param {string} markdown - 完整的 Markdown 内容
 * @param {string} h2Title - H2 标题文字
 * @returns {string} - 该小节的内容
 */
function extractSectionContent(markdown, h2Title) {
  const lines = markdown.split('\n');
  let capturing = false;
  let content = [];

  for (const line of lines) {
    // 检查是否是目标 H2 标题
    if (line.match(/^##\s+(.+)/)) {
      const title = line.match(/^##\s+(.+)/)[1].trim();
      if (title === h2Title) {
        capturing = true;
        continue;
      } else if (capturing) {
        // 遇到下一个 H2，停止捕获
        break;
      }
    }

    // 遇到 H1 也停止
    if (capturing && line.match(/^#\s+/)) {
      break;
    }

    if (capturing) {
      // 跳过图片占位符
      if (!line.match(/^!\[.*\]\(ai:/)) {
        content.push(line);
      }
    }
  }

  return content.join('\n').trim();
}

/**
 * 生成基于标题的哈希文件名（确保相同标题生成相同文件名）
 * @param {string} title - 标题
 * @returns {string} - 哈希后的文件名（不含扩展名）
 */
function generateHashedFilename(title) {
  // 简单的哈希函数：将字符串转换为数字
  let hash = 0;
  for (let i = 0; i < title.length; i++) {
    const char = title.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // 转换为32位整数
  }
  // 使用绝对值并转为16进制
  const hexHash = Math.abs(hash).toString(16).padStart(8, '0');
  return `ai_${hexHash}`;
}

/**
 * 从旧的 temp 目录迁移最近生成的图片
 * @param {string} oldTempDir - 旧的 temp 目录路径
 * @param {string} newCacheDir - 新的缓存目录路径
 * @param {Array} replacements - 需要迁移的图片信息数组
 */
function migrateOldImages(oldTempDir, newCacheDir, replacements) {
  if (!fs.existsSync(oldTempDir)) {
    return;
  }

  console.log(`\n🔍 检测到旧 temp 目录，尝试迁移最近生成的图片...`);

  // 获取 temp 目录中的所有 png 文件，按修改时间排序（最新的在前）
  const files = fs.readdirSync(oldTempDir)
    .filter(f => f.startsWith('ai_gen_') && f.endsWith('.png'))
    .map(f => ({
      name: f,
      path: path.join(oldTempDir, f),
      mtime: fs.statSync(path.join(oldTempDir, f)).mtime
    }))
    .sort((a, b) => b.mtime - a.mtime);

  if (files.length === 0) {
    return;
  }

  console.log(`📋 找到 ${files.length} 个旧图片文件`);

  // 按顺序将最新的图片分配给各个标题
  let migratedCount = 0;
  for (const item of replacements) {
    const targetPath = path.join(newCacheDir, `${item.hashedFilename}.png`);

    // 如果目标文件已存在，跳过
    if (fs.existsSync(targetPath)) {
      continue;
    }

    // 使用下一个最新的图片文件
    if (migratedCount < files.length) {
      const sourceFile = files[migratedCount];
      try {
        fs.copyFileSync(sourceFile.path, targetPath);
        console.log(`✅ 迁移: ${sourceFile.name} -> ${item.hashedFilename}.png`);
        migratedCount++;
      } catch (e) {
        console.error(`⚠️ 迁移失败: ${e.message}`);
      }
    }
  }

  if (migratedCount > 0) {
    console.log(`🎉 成功迁移 ${migratedCount} 张图片到缓存目录\n`);
  }
}

/**
 * 扫描并处理 Markdown 中的 AI 图片占位符
 * 语法: ![提示词](ai:generate) 或 ![提示词](ai:1:1) 指定比例
 * @param {string} markdown - Markdown 内容
 * @param {string} cacheDir - 缓存文件存放目录（通常在文章所在目录的 .ai-images 子目录）
 * @returns {Promise<string>} - 替换为本地路径后的 Markdown
 */
async function processAIPlaceholders(markdown, cacheDir) {
  // 匹配 ![alt](ai:generate) 或 ![alt](ai:1:1)
  const regex = /!\[(.*?)\]\(ai:(.*?)\)/g;
  let match;
  let replacements = [];

  // 1. 扫描所有占位符
  while ((match = regex.exec(markdown)) !== null) {
    const [fullMatch, title, param] = match;

    // 解析参数，param 可能是 "generate" 或 "1:1", "16:9" 等
    let aspectRatio = '4:3'; // 默认统一为 4:3 横版
    if (param && param !== 'generate' && param !== 'gen') {
      aspectRatio = param.trim();
    }

    // 提取该小节的内容
    const sectionContent = extractSectionContent(markdown, title);

    // 使用结构化 Prompt（核心改进！）
    const structuredPrompt = buildStructuredPrompt(sectionContent || title, title);

    // 生成基于标题的哈希文件名
    const hashedFilename = generateHashedFilename(title);

    replacements.push({
      fullMatch,
      prompt: structuredPrompt,
      originalTitle: title,
      aspectRatio: '4:3', // 强制 4:3
      hashedFilename
    });
  }

  if (replacements.length === 0) return markdown;

  console.log(`🤖 发现 ${replacements.length} 个 AI 配图需求，开始处理...`);

  // 确保缓存目录存在
  if (!fs.existsSync(cacheDir)) {
    fs.mkdirSync(cacheDir, { recursive: true });
    console.log(`📁 创建缓存目录: ${cacheDir}`);
  }

  // 尝试从旧 temp 目录迁移图片
  const oldTempDir = path.join(__dirname, 'temp');
  migrateOldImages(oldTempDir, cacheDir, replacements);

  let newMarkdown = markdown;

  // 2. 逐个处理（检查缓存或生成）
  for (const item of replacements) {
    const imagePath = path.join(cacheDir, `${item.hashedFilename}.png`);

    try {
      // 检查缓存：如果图片已存在（包括刚迁移的），直接复用
      if (fs.existsSync(imagePath)) {
        console.log(`\n📝 【${item.originalTitle}】图片已存在，跳过生成 ♻️`);
        console.log(`✅ 使用缓存: ${item.hashedFilename}.png`);
      } else {
        // 缓存不存在，调用 API 生成
        console.log(`\n📝 正在为【${item.originalTitle}】生成配图...`);
        const imageBuffer = await generateImageByAPI(item.prompt, item.aspectRatio);

        // 保存到缓存目录
        fs.writeFileSync(imagePath, imageBuffer);
        console.log(`✅ 图片已保存: ${item.hashedFilename}.png`);

        // 验证图片尺寸
        try {
          const dimensionOutput = execSync(`sips -g pixelWidth -g pixelHeight "${imagePath}"`).toString();
          const widthMatch = dimensionOutput.match(/pixelWidth: (\d+)/);
          const heightMatch = dimensionOutput.match(/pixelHeight: (\d+)/);
          if (widthMatch && heightMatch) {
            const width = parseInt(widthMatch[1]);
            const height = parseInt(heightMatch[1]);
            if (width < 2000 || height < 2000) {
              console.error(`⚠️ WARNING: Low resolution (${width}x${height}).`);
            } else {
              console.log(`📏 尺寸确认: ${width}x${height} (4K OK)`);
            }
          }
        } catch (e) {
          // 静默处理
        }
      }

      // 替换 Markdown 中的链接为本地绝对路径
      const altText = item.originalTitle;
      const newTag = `![${altText}](${imagePath})`;
      newMarkdown = newMarkdown.replace(item.fullMatch, newTag);

    } catch (err) {
      console.error(`⚠️ 跳过无法生成的图片【${item.originalTitle}】: ${err.message}`);
    }
  }

  return newMarkdown;
}

module.exports = {
  generateImageByAPI,
  processAIPlaceholders,
  autoInsertImagePlaceholders,
  buildStructuredPrompt,
  generateHashedFilename
};
