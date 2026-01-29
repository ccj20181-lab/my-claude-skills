import path from "node:path";
import { readFile } from "node:fs/promises";
import type { CliArgs } from "../types";

export function getDefaultModel(): string {
  return "google/gemini-2.0-flash-001";
}

function getNanoBananaApiKey(): string | null {
  return process.env.NANO_BANANA_API_KEY || process.env.OPENAI_API_KEY || null;
}

function getNanoBananaBaseUrl(): string {
  let base = process.env.NANO_BANANA_API_URL || process.env.OPENAI_BASE_URL || "https://api.nanobanana.com/v1";
  return base.replace(/\/+$/g, "");
}

function getGoogleImageSize(args: CliArgs): "1K" | "2K" | "4K" {
  if (args.imageSize) return args.imageSize as "1K" | "2K" | "4K";
  return args.quality === "2k" ? "2K" : "1K";
}

function addAspectRatioToPrompt(prompt: string, ar: string | null): string {
  if (!ar) return prompt;
  return `${prompt} Aspect ratio: ${ar}.`;
}

async function readImageAsBase64(p: string): Promise<{ data: string; mimeType: string }> {
  const buf = await readFile(p);
  const ext = path.extname(p).toLowerCase();
  let mimeType = "image/png";
  if (ext === ".jpg" || ext === ".jpeg") mimeType = "image/jpeg";
  else if (ext === ".gif") mimeType = "image/gif";
  else if (ext === ".webp") mimeType = "image/webp";
  return { data: buf.toString("base64"), mimeType };
}

function extractInlineImageData(response: {
  candidates?: Array<{ content?: { parts?: Array<{ inlineData?: { data?: string } }> } }>;
}): string | null {
  for (const candidate of response.candidates || []) {
    for (const part of candidate.content?.parts || []) {
      const data = part.inlineData?.data;
      if (typeof data === "string" && data.length > 0) return data;
    }
  }
  return null;
}

async function postNanoBananaJson<T>(model: string, body: unknown): Promise<T> {
  const apiKey = getNanoBananaApiKey();
  if (!apiKey) throw new Error("NANO_BANANA_API_KEY or OPENAI_API_KEY is required");

  const baseUrl = getNanoBananaBaseUrl();

  // 处理模型名称：如果是 google/gemini-xxx，去掉 google/ 前缀，或者保留（取决于 API 易的要求）
  // 通常 API 易支持 models/google/gemini-xxx:generateContent 或者 models/gemini-xxx:generateContent
  // 我们这里保留原样，但在构建 URL 时可能需要调整

  // 假设 BaseURL 是 https://api.nanobanana.com/v1
  // 我们需要拼接成 https://api.nanobanana.com/v1/models/{model}:generateContent

  let cleanModel = model;
  if (cleanModel.startsWith("models/")) {
      cleanModel = cleanModel.slice("models/".length);
  }

  // 构造 URL
  const url = `${baseUrl}/models/${cleanModel}:generateContent`;

  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${apiKey}`,
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`NanoBanana API error (${res.status}): ${err}`);
  }

  return (await res.json()) as T;
}

export async function generateImage(
  prompt: string,
  model: string,
  args: CliArgs
): Promise<Uint8Array> {
  const promptWithAspect = addAspectRatioToPrompt(prompt, args.aspectRatio);
  const parts: Array<{ text?: string; inlineData?: { data: string; mimeType: string } }> = [];

  for (const refPath of args.referenceImages) {
    const { data, mimeType } = await readImageAsBase64(refPath);
    parts.push({ inlineData: { data, mimeType } });
  }

  parts.push({ text: promptWithAspect });

  const imageConfig: { imageSize: "1K" | "2K" | "4K"; aspectRatio?: string } = {
    imageSize: getGoogleImageSize(args),
  };

  // NanoBanana (Google Protocol) 支持在 imageConfig 中直接传 aspectRatio (3:4, 4:3, 16:9, etc)
  // baoyu-image-gen 默认只在 Prompt 里加 Aspect Ratio，但也兼容直接传参
  if (args.aspectRatio) {
      // 简单的映射，Google API 接受 "16:9", "4:3", "1:1" 等
      imageConfig.aspectRatio = args.aspectRatio;
  }

  console.log(`Generating image with NanoBanana (Model: ${model})...`, imageConfig);

  const response = await postNanoBananaJson<{
    candidates?: Array<{ content?: { parts?: Array<{ inlineData?: { data?: string } }> } }>;
  }>(model, {
    contents: [
      {
        role: "user",
        parts,
      },
    ],
    generationConfig: {
      responseModalities: ["IMAGE"],
      imageConfig,
    },
  });

  console.log("Generation completed.");

  const imageData = extractInlineImageData(response);
  if (imageData) return Uint8Array.from(Buffer.from(imageData, "base64"));

  throw new Error("No image in response");
}
