import * as fs from 'fs';
import * as path from 'path';
import type { GenerationProgress, AssetGenerationResult } from '../types/asset';

const API_CONFIG = {
  getApiUrl: () => {
    const fullUrl = process.env.NANO_BANANA_API_URL?.trim();
    if (fullUrl) return fullUrl;
    return 'https://api.apiyi.com/v1beta/models/gemini-3-pro-image-preview:generateContent';
  },
  getApiKey: () => process.env.NANO_BANANA_API_KEY || process.env.APIYI_API_KEY || '',
  defaultAspectRatio: '3:4',
  defaultResolution: '2K',
} as const;

export interface ImageGenerationRequest {
  prompt: string;
  size?: '1024x1024' | '1536x1536' | '2048x2048';
}

export async function generateImage(
  request: ImageGenerationRequest
): Promise<{ success: boolean; imageData?: string; error?: string }> {
  const apiKey = API_CONFIG.getApiKey();

  if (!apiKey) {
    return { success: false, error: 'APIYI_API_KEY environment variable not set' };
  }

  try {
    const apiUrl = API_CONFIG.getApiUrl();
    const isApiyi = apiUrl.includes('api.apiyi.com');

    const response = await fetch(
      isApiyi ? apiUrl : `${apiUrl}?key=${apiKey}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(isApiyi ? { 'Authorization': `Bearer ${apiKey}` } : {}),
        },
        body: JSON.stringify({
          contents: [{ parts: [{ text: request.prompt }] }],
          generationConfig: {
            responseModalities: ['IMAGE'],
            imageConfig: {
              aspectRatio: API_CONFIG.defaultAspectRatio,
              imageSize: API_CONFIG.defaultResolution,
            },
          },
        }),
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      return { success: false, error: `API error: ${response.status} - ${errorText}` };
    }

    const data: any = await response.json();

    if (data.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data) {
      return {
        success: true,
        imageData: data.candidates[0].content.parts[0].inlineData.data,
      };
    }

    return { success: false, error: 'No image data in response' };
  } catch (error) {
    return {
      success: false,
      error: `Request failed: ${error instanceof Error ? error.message : String(error)}`,
    };
  }
}

export async function generateAndSaveImage(
  prompt: string,
  outputPath: string
): Promise<AssetGenerationResult> {
  const startTime = Date.now();

  // Simple retry logic
  for (let attempt = 1; attempt <= 3; attempt++) {
    const result = await generateImage({ prompt });

    if (result.success && result.imageData) {
      try {
        const dir = path.dirname(outputPath);
        if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

        fs.writeFileSync(outputPath, Buffer.from(result.imageData, 'base64'));

        return {
          assetId: path.basename(outputPath, path.extname(outputPath)),
          success: true,
          outputPath,
          duration: Date.now() - startTime,
        };
      } catch (err) {
        return {
          assetId: path.basename(outputPath),
          success: false,
          error: String(err),
          duration: Date.now() - startTime,
        };
      }
    }

    if (attempt < 3) await new Promise(r => setTimeout(r, 2000));
  }

  return {
    assetId: path.basename(outputPath),
    success: false,
    error: 'Max retries exceeded',
    duration: Date.now() - startTime,
  };
}

export async function generateBatch(
  items: Array<{ id: string; prompt: string; outputPath: string }>,
  options?: { onProgress?: (p: GenerationProgress) => void }
): Promise<AssetGenerationResult[]> {
  const results: AssetGenerationResult[] = [];
  const progress: GenerationProgress = {
    total: items.length,
    completed: 0,
    succeeded: 0,
    failed: 0,
  };

  for (const item of items) {
    progress.current = item.id;
    options?.onProgress?.(progress);

    const result = await generateAndSaveImage(item.prompt, item.outputPath);
    results.push(result);

    progress.completed++;
    if (result.success) progress.succeeded++;
    else progress.failed++;

    options?.onProgress?.(progress);
    if (progress.completed < progress.total) await new Promise(r => setTimeout(r, 2000));
  }

  return results;
}

export function checkApiKeyConfigured(): boolean {
  return !!API_CONFIG.getApiKey();
}

export function getApiStatus(): {
  configured: boolean;
  baseUrl: string;
  model: string;
} {
  return {
    configured: checkApiKeyConfigured(),
    baseUrl: API_CONFIG.getApiUrl(),
    model: 'gemini-3-pro-image-preview',
  };
}
