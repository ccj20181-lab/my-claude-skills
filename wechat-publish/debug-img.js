const fetch = require('node-fetch');

const API_KEY = process.env.NANOBANANA_API_KEY || "sk-30hw0QuR0UD2t6ub808670A2Da6641159aDbAe54519f6743";
const API_URL = process.env.NANOBANANA_API_URL || "https://api.apiyi.com/v1beta/models/gemini-3-pro-image-preview:generateContent";

async function testGen(ratio) {
  console.log(`Testing ratio: ${ratio}`);

  const payload = {
    contents: [{
      parts: [{ text: "A cute cat engineer, comic style" }]
    }],
    generationConfig: {
      responseModalities: ["IMAGE"],
      imageConfig: {
        aspectRatio: ratio
      }
    }
  };

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`
      },
      body: JSON.stringify(payload)
    });

    console.log(`Status: ${response.status}`);
    const data = await response.json();

    if (data.candidates && data.candidates[0].content.parts[0].inlineData) {
        console.log("Success: Image data received");
        const buffer = Buffer.from(data.candidates[0].content.parts[0].inlineData.data, 'base64');
        const fs = require('fs');
        const filename = `debug_${ratio.replace(':','-')}.png`;
        fs.writeFileSync(filename, buffer);
        console.log(`Saved to ${filename}`);

        // Use sips to check dimensions
        const { execSync } = require('child_process');
        try {
            const output = execSync(`sips -g pixelWidth -g pixelHeight ${filename}`).toString();
            console.log("Dimensions:", output.trim());
        } catch (e) {
            console.error("Failed to check dimensions");
        }
    } else {
        console.log("Failed structure:", JSON.stringify(data, null, 2));
    }

  } catch (e) {
    console.error("Error:", e);
  }
}

testGen("4:3");
testGen("16:9");
