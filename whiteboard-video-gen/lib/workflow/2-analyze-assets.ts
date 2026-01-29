import * as fs from 'fs';
import * as path from 'path';
import type { Script } from '../types/script';
import type {
  AssetManifest,
  AssetRequirement,
  AssetCategory,
  AssetStatus,
} from '../types/asset';
import { generatePromptFromNarration } from '../utils/prompt-templates.js';

/**
 * 素材名称前缀到类别的映射
 */
const ASSET_PREFIX_CATEGORY: Record<string, AssetCategory> = {
  'character': 'character',
  'char': 'character',
  'person': 'character',
  'icon': 'icon',
  'ico': 'icon',
  'decoration': 'decoration',
  'deco': 'decoration',
  'bg': 'background',
  'background': 'background',
  'obj': 'object',
  'object': 'object',
};

/**
 * 从素材名称推断类别
 */
function inferCategory(assetName: string): AssetCategory {
  const lowerName = assetName.toLowerCase();

  for (const [prefix, category] of Object.entries(ASSET_PREFIX_CATEGORY)) {
    if (lowerName.startsWith(prefix)) {
      return category;
    }
  }

  // 默认作为图标处理
  return 'icon';
}

/**
 * 检查素材是否已存在
 */
function checkAssetExists(
  projectRoot: string,
  assetName: string,
  videoId: string
): { exists: boolean; path?: string } {
  const PUBLIC_ASSETS_DIR = path.join(projectRoot, 'public/assets');
  const GENERATED_ASSETS_DIR = path.join(projectRoot, 'public/assets/generated');

  // 检查的路径优先级
  const searchPaths = [
    // 1. 生成的素材目录
    path.join(GENERATED_ASSETS_DIR, videoId, `${assetName}.png`),
    // 2. 公共素材目录
    path.join(PUBLIC_ASSETS_DIR, `${assetName}.png`),
    path.join(PUBLIC_ASSETS_DIR, `${assetName}.svg`),
    // 3. 分类子目录
    path.join(PUBLIC_ASSETS_DIR, 'icons', `${assetName}.png`),
    path.join(PUBLIC_ASSETS_DIR, 'icons', `${assetName}.svg`),
    path.join(PUBLIC_ASSETS_DIR, 'characters', `${assetName}.png`),
    path.join(PUBLIC_ASSETS_DIR, 'decorations', `${assetName}.png`),
  ];

  for (const searchPath of searchPaths) {
    if (fs.existsSync(searchPath)) {
      return { exists: true, path: searchPath };
    }
  }

  return { exists: false };
}

/**
 * 分析场景中的素材需求
 */
export function createAssetManifest(script: Script, projectRoot: string): AssetManifest {
  const videoId = script.metadata.id;
  const assetMap = new Map<string, AssetRequirement>();

  // 遍历所有场景
  script.scenes.forEach(scene => {
    scene.assets.forEach(assetRef => {
      const assetId = assetRef.name;

      // 如果已处理过,只添加使用场景
      if (assetMap.has(assetId)) {
        const existing = assetMap.get(assetId)!;
        if (!existing.usedInScenes.includes(`scene-${scene.index}`)) {
          existing.usedInScenes.push(`scene-${scene.index}`);
        }
        return;
      }

      // 推断类别
      const category = inferCategory(assetId);

      // 检查是否存在
      const existsCheck = checkAssetExists(projectRoot, assetId, videoId);
      const status: AssetStatus = assetRef.exists || existsCheck.exists ? 'exists' : 'missing';

      // 创建素材需求
      const requirement: AssetRequirement = {
        id: assetId,
        category,
        name: assetId,
        description: assetRef.description,
        status,
        existingPath: existsCheck.path,
        usedInScenes: [`scene-${scene.index}`],
      };

      // 如果缺失,生成 AI 提示词
      if (status === 'missing') {
        const prompt = generatePromptFromNarration(
          scene.narration,
          category,
          assetRef.description
        );

        requirement.generation = {
          prompt,
          priority: scene.index <= 2 ? 'high' : scene.index <= 4 ? 'medium' : 'low',
        };
      }

      assetMap.set(assetId, requirement);
    });
  });

  // 构建清单
  const assets = Array.from(assetMap.values());
  const manifest: AssetManifest = {
    videoId,
    generatedAt: new Date().toISOString(),
    totalCount: assets.length,
    existsCount: assets.filter(a => a.status === 'exists').length,
    missingCount: assets.filter(a => a.status === 'missing').length,
    assets,
  };

  return manifest;
}

/**
 * 主流程：分析素材
 */
export async function analyzeAssets(projectRoot: string, videoId: string) {
  const SCENES_DIR = path.join(projectRoot, 'content/scenes');
  const ASSETS_MANIFEST_DIR = path.join(projectRoot, 'content/assets-manifest');

  console.log(`\n🔍 Analyzing assets for: ${videoId}`);

  // 读取场景定义
  const scenesPath = path.join(SCENES_DIR, `${videoId}.scenes.json`);

  if (!fs.existsSync(scenesPath)) {
    throw new Error(`Scenes file not found: ${scenesPath}. Run step 1 first.`);
  }

  const script: Script = JSON.parse(fs.readFileSync(scenesPath, 'utf-8'));
  const manifest = createAssetManifest(script, projectRoot);

  // 确保输出目录存在
  if (!fs.existsSync(ASSETS_MANIFEST_DIR)) {
    fs.mkdirSync(ASSETS_MANIFEST_DIR, { recursive: true });
  }

  // 保存素材清单
  const outputPath = path.join(ASSETS_MANIFEST_DIR, `${videoId}.assets.json`);
  fs.writeFileSync(outputPath, JSON.stringify(manifest, null, 2), 'utf-8');

  console.log(`✅ Asset analysis complete!`);
  console.log(`   - Total assets: ${manifest.totalCount}`);
  console.log(`   - Existing: ${manifest.existsCount}`);
  console.log(`   - Missing: ${manifest.missingCount}`);
  console.log(`   - Output: ${outputPath}`);

  if (manifest.missingCount > 0) {
    console.log(`💡 Next step: Generate missing assets.`);
  }
}
