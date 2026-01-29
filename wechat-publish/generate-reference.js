#!/usr/bin/env node
/**
 * 生成 4:3 横版参考图
 * 使用原始竖版参考图作为风格输入，让 AI 生成一张风格完全一致的 4:3 横版版本
 */

const fetch = require('node-fetch');
const fs = require('fs');
const path = require('path');

// 配置
const CONFIG = {
  baseUrl: process.env.NANOBANANA_API_URL || 'https://api.apiyi.com/v1beta/models/gemini-3-pro-image-preview:generateContent',
  apiKey: process.env.NANOBANANA_API_KEY || process.env.GEMINI_API_KEY || "sk-30hw0QuR0UD2t6ub808670A2Da6641159aDbAe54519f6743"
};

// 原始竖版参考图路径 (来自 finance-infographic)
const ORIGINAL_REF_PATH = path.join(__dirname, '..', 'finance-infographic', 'references', 'reference.png');
const OUTPUT_PATH = path.join(__dirname, 'reference.png');

async function generateHorizontalReference() {
  console.log('🎨 开始生成 4:3 横版参考图...\n');

  // 1. 读取原始竖版参考图
  if (!fs.existsSync(ORIGINAL_REF_PATH)) {
    throw new Error(`原始参考图不存在: ${ORIGINAL_REF_PATH}`);
  }

  const originalImageBase64 = fs.readFileSync(ORIGINAL_REF_PATH).toString('base64');
  console.log('✅ 已加载原始竖版参考图');

  // 2. 构建 Prompt - 关键：让模型理解要生成新图而非复制
  const prompt = `【任务】看着这张参考图，生成一张风格100%完全一致的 4:3 横版财经信息图。

【核心要求 - 风格复刻】
你需要生成一张全新的图片，但视觉风格必须与参考图完全一致：
1. **背景色**：与参考图完全相同的米色/奶油色背景
2. **配色方案**：相同的黄色标题块、蓝绿色图标、棕色文字
3. **设计风格**：扁平化矢量插画风格，手绘感图标
4. **右上角Logo**：保留"秒懂金融"品牌标识，位置和样式一致
5. **右下角标识**：保留"@秒懂金融"水印，位置和样式一致
6. **字体风格**：标题和正文字体风格一致
7. **布局风格**：保持信息图的专业排版感

【内容要求】
这是一张"示例参考图"，用于后续图片生成的风格参考。
请生成一张关于"投资理财基础知识"主题的示例信息图，包含：
- 主标题：投资入门指南
- 2-3个信息板块
- 配套的扁平化图标
- 专业的财经信息图排版

【输出规格】
- 比例：4:3 横版构图
- 分辨率：4K 高清
- 风格：与参考图100%一致

【禁止事项】
- 禁止直接复制参考图的内容
- 禁止使用参考图中的文字
- 只复制风格，内容要全新

【输出要求】只输出图片。`;

  // 3. 构建请求 Payload
  const payload = {
    contents: [{
      parts: [
        {
          inlineData: {
            mimeType: 'image/png',
            data: originalImageBase64
          }
        },
        { text: prompt }
      ]
    }],
    generationConfig: {
      responseModalities: ['IMAGE'],
      imageConfig: {
        aspectRatio: '4:3',
        imageSize: '4K'
      }
    }
  };

  console.log('📤 正在调用 API 生成横版参考图...');

  // 4. 调用 API
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

  // 5. 解析图片数据
  let imageBase64 = null;
  try {
    const part = data.candidates[0].content.parts[0];
    if (part.inline_data && part.inline_data.data) {
      imageBase64 = part.inline_data.data;
    } else if (part.inlineData && part.inlineData.data) {
      imageBase64 = part.inlineData.data;
    }
  } catch (e) {
    console.error('解析响应失败:', JSON.stringify(data, null, 2));
    throw new Error('API 返回结果解析失败');
  }

  if (!imageBase64) {
    throw new Error('API 返回结果中未找到图片数据');
  }

  // 6. 保存图片
  const buffer = Buffer.from(imageBase64, 'base64');
  fs.writeFileSync(OUTPUT_PATH, buffer);

  console.log(`\n✅ 横版参考图已生成并保存: ${OUTPUT_PATH}`);

  // 7. 验证尺寸
  const { execSync } = require('child_process');
  try {
    const sipsOutput = execSync(`sips -g pixelWidth -g pixelHeight "${OUTPUT_PATH}"`).toString();
    console.log('📏 图片尺寸信息:');
    console.log(sipsOutput);
  } catch (e) {
    console.log('(无法获取尺寸信息)');
  }

  console.log('\n🎉 参考图生成完成！');
}

// 执行
generateHorizontalReference().catch(err => {
  console.error('❌ 生成失败:', err.message);
  process.exit(1);
});
