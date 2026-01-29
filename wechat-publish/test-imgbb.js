const fs = require('fs');
const path = require('path');
const fetch = require('node-fetch');

const IMGBB_CONFIG = {
  apiKey: process.env.IMGBB_API_KEY || '9d823e5d2dc9c968daf476e4abfab336',
  endpoint: 'https://api.imgbb.com/1/upload'
};

async function testImgBBUpload() {
  // 使用一张测试图片
  const testImage = path.join(__dirname, 'temp', 'ai_gen_1769565473928_08aue.png');

  if (!fs.existsSync(testImage)) {
    console.error('测试图片不存在');
    return;
  }

  const imageData = fs.readFileSync(testImage);
  const base64Image = imageData.toString('base64');

  console.log('📤 上传测试图片到 ImgBB...');
  console.log(`原图大小: ${(imageData.length / 1024 / 1024).toFixed(2)} MB`);

  const params = new URLSearchParams();
  params.append('key', IMGBB_CONFIG.apiKey);
  params.append('image', base64Image);

  const response = await fetch(IMGBB_CONFIG.endpoint, {
    method: 'POST',
    body: params
  });

  const result = await response.json();

  if (result.success) {
    console.log('\n✅ 上传成功！返回的 URL 结构：\n');
    console.log('data.url:', result.data.url);
    console.log('data.display_url:', result.data.display_url);
    console.log('data.image.url:', result.data.image?.url);
    console.log('data.thumb.url:', result.data.thumb?.url);
    console.log('data.medium.url:', result.data.medium?.url);
    console.log('\n完整返回数据：');
    console.log(JSON.stringify(result.data, null, 2));
  } else {
    console.error('上传失败:', result);
  }
}

testImgBBUpload().catch(console.error);
