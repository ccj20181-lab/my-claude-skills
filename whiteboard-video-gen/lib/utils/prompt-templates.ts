import type { AssetCategory } from '../types/asset';

export const BASE_STYLE_PROMPT = `
Style requirements:
- Hand-drawn whiteboard illustration style
- Clean white/off-white background (#FAFAFA)
- Simple black outlines with slight hand-drawn imperfections
- Minimal color palette (black, with occasional accent colors)
- Flat design, no gradients or shadows
- Cartoon/doodle aesthetic
- PNG format with transparent background
- High contrast, clear lines
`.trim();

export const CATEGORY_STYLE_PROMPTS: Record<AssetCategory, string> = {
  character: `
Character style:
- Simple cartoon character
- Friendly, approachable expression
- Minimalist features (dot eyes, simple smile)
- Business casual or professional attire for finance topics
- Full body or upper body as needed
- Consistent proportions
`.trim(),

  icon: `
Icon style:
- Simple line art icon
- Single concept, instantly recognizable
- Uniform stroke width
- Centered composition
- Square aspect ratio (1:1)
- No text or labels
`.trim(),

  decoration: `
Decoration style:
- Hand-drawn decorative element
- Arrows, underlines, circles, stars, sparkles
- Whimsical, playful feel
- Light, not overpowering
`.trim(),

  background: `
Background style:
- Subtle texture or pattern
- Does not distract from foreground content
- Light colors only
`.trim(),

  object: `
Object style:
- Simple illustration of physical object
- Recognizable silhouette
- Slight perspective if needed
`.trim(),
};

export const FINANCE_THEME_PROMPT = `
Finance/Business context:
- Professional but approachable
- Use common financial symbols (¥, $, %, charts)
- Include recognizable business elements
- Make abstract concepts concrete
`.trim();

export function generateAssetPrompt(
  description: string,
  category: AssetCategory,
  additionalContext?: string
): string {
  const parts: string[] = [];
  parts.push(`Create an illustration of: ${description}`);
  parts.push(BASE_STYLE_PROMPT);
  parts.push(CATEGORY_STYLE_PROMPTS[category]);
  parts.push(FINANCE_THEME_PROMPT);

  if (additionalContext) {
    parts.push(`Additional context: ${additionalContext}`);
  }

  return parts.join('\n\n');
}

export function generatePromptFromNarration(
  narration: string,
  category: AssetCategory,
  assetName: string
): string {
  const keyPhrases = narration
    .replace(/[，。？！、"']/g, ' ')
    .split(/\s+/)
    .filter(w => w.length > 1)
    .slice(0, 5);

  const description = `${assetName} - visual representation for: "${keyPhrases.join(', ')}"`;
  return generateAssetPrompt(description, category, `Related narration: ${narration}`);
}
