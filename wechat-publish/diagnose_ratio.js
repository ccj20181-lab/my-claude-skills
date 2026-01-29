const fetch = require('node-fetch');
const fs = require('fs');
const { execSync } = require('child_process');

const API_KEY = process.env.NANOBANANA_API_KEY || "sk-30hw0QuR0UD2t6ub808670A2Da6641159aDbAe54519f6743";
const API_URL = process.env.NANOBANANA_API_URL || "https://api.apiyi.com/v1beta/models/gemini-3-pro-image-preview:generateContent";

async function test(ratio, size) {
  console.log(`\nTesting ratio: ${ratio}, size: ${size}`);
  const payload = {
    contents: [{ parts: [{ text: "A test image of a cat, comic style, (horizontal composition), 4:3 aspect ratio" }] }],
    generationConfig: {
      responseModalities: ["IMAGE"],
      imageConfig: {
        aspectRatio: ratio,
        imageSize: size
      }
    }
  };

  try {
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${API_KEY}` },
      body: JSON.stringify(payload)
    });

    if (res.status !== 200) {
        console.log(`Error: ${res.status} - ${await res.text()}`);
        return;
    }

    const data = await res.json();
    if (data.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data) {
       const buf = Buffer.from(data.candidates[0].content.parts[0].inlineData.data, 'base64');
       const fname = `test_${String(ratio).replace(':','-')}_${size}.png`;
       fs.writeFileSync(fname, buf);
       console.log(`Saved ${fname}`);
       try {
         const dims = execSync(`sips -g pixelWidth -g pixelHeight ${fname}`).toString();
         console.log(`Dimensions for ${ratio}/${size}:\n${dims.trim()}`);
       } catch(e) { console.error("sips failed"); }
    } else {
       console.log("No image data received");
    }
  } catch (e) { console.error(e); }
}

(async () => {
  // Test 1: The user's requested 4:3 (which failed)
  await test('4:3', '4K');

  // Test 2: Standard landscape 16:9
  await test('16:9', '4K');

  // Test 3: String description "LANDSCAPE" (if supported?)
  // await test('LANDSCAPE', '4K');

  // Test 4: Remove imageSize, maybe 4K is causing fallback?
  await test('4:3', undefined);

  // Test 5: 16:9 without imageSize
  await test('16:9', undefined);
})();
