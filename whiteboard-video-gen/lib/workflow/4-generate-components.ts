/**
 * 4-generate-components.ts - 生成 Remotion 视频组件代码
 */

import * as fs from 'fs';
import * as path from 'path';
import type { Script } from '../../types/script';
import type { AssetManifest } from '../../types/asset';

/**
 * Convert to PascalCase
 */
function toPascalCase(str: string): string {
  return str
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join('');
}

/**
 * Generate Remotion Scene Component
 */
function generateSceneComponent(
  scene: Script['scenes'][0],
  assets: AssetManifest['assets'],
  index: number,
  videoId: string,
  projectRoot: string
): string {
  const { title, duration, narration } = scene;

  // Resolve assets
  const sceneAssets = scene.assets.map((assetRef, i) => {
    const asset = assets.find(a => a.id === assetRef.name);
    let assetPath = `assets/generated/${videoId}/${assetRef.name}.png`;

    if (asset?.existingPath) {
      // Make path relative to public/
      if (asset.existingPath.startsWith('/')) {
         const publicDir = path.join(projectRoot, 'public');
         if (asset.existingPath.startsWith(publicDir)) {
            // Remove public dir prefix
            let rel = asset.existingPath.replace(publicDir, '');
            // Ensure no leading slash
            if (rel.startsWith('/')) rel = rel.substring(1);
            assetPath = rel;
         }
      } else {
         assetPath = asset.existingPath;
      }
    }

    return {
      name: assetRef.name,
      path: assetPath,
      description: assetRef.description,
      animation: i % 2 === 0 ? 'popIn' : 'slideUp',
      delay: i * 15 + 15,
    };
  });

  return `import { AbsoluteFill, Img, staticFile } from "remotion";
import { whiteboardTheme } from "../../../styles/whiteboard-theme";
import { useWhiteboardAnimations } from "../../../hooks/useWhiteboardAnimations";

/**
 * ${title}
 * Duration: ${duration}s
 */
export const Scene${index + 1} = () => {
  const { popIn, slideUp, fadeIn, typewriter, float } = useWhiteboardAnimations();

  return (
    <AbsoluteFill style={{
      backgroundColor: whiteboardTheme.colors.background,
      fontFamily: whiteboardTheme.typography.fontFamily.primary,
    }}>
      {/* Narration Text */}
      <div style={{
        position: 'absolute',
        top: whiteboardTheme.video.safeArea.vertical,
        left: whiteboardTheme.video.safeArea.horizontal,
        right: whiteboardTheme.video.safeArea.horizontal,
        fontSize: whiteboardTheme.typography.fontSize.lg,
        color: whiteboardTheme.colors.textPrimary,
        textAlign: 'center',
        lineHeight: whiteboardTheme.typography.lineHeight.relaxed,
        opacity: fadeIn(10),
        transform: \`translateY(\${slideUp(10, 20)}px)\`
      }}>
        {typewriter("${narration.replace(/"/g, '\\"')}", 15)}
      </div>

      {/* Assets */}
      ${sceneAssets.map((asset, i) => `
      <Img
        src={staticFile("${asset.path}")}
        style={{
          position: 'absolute',
          top: '50%',
          left: '${20 + (i * 30)}%',
          width: '25%',
          transform: \`
            translate(-50%, -50%)
            scale(\${popIn(${asset.delay})})
            translateY(\${float(0.05 + ${i} * 0.01, 10)}px)
          \`,
          objectFit: 'contain',
        }}
      />`).join('\n')}
    </AbsoluteFill>
  );
};
`;
}

/**
 * Generate Composition
 */
function generateComposition(
  script: Script,
  videoId: string,
  fps: number = 30
): string {
  const pascalVideoId = toPascalCase(videoId);

  const sceneImports = script.scenes.map((_, index) =>
    `import { Scene${index + 1} } from "./scenes/${videoId}/Scene${index + 1}";`
  ).join('\n');

  const sceneSequence = script.scenes.map((scene, index) => {
    // Calculate start frame
    const startFrame = script.scenes.slice(0, index).reduce((sum, s) => sum + s.duration * fps, 0);
    const duration = scene.duration * fps;

    return `      <Sequence from={${startFrame}} durationInFrames={${duration}}>
        <Scene${index + 1} />
      </Sequence>`;
  }).join('\n');

  return `import { AbsoluteFill, Sequence } from "remotion";
import { whiteboardTheme } from "../styles/whiteboard-theme";
${sceneImports}

export const ${pascalVideoId}Composition = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: whiteboardTheme.colors.background }}>
${sceneSequence}
    </AbsoluteFill>
  );
};
`;
}

/**
 * Main Workflow: Generate Components
 */
export async function generateComponents(projectRoot: string, videoId: string) {
  const SCENES_DIR = path.join(projectRoot, 'content/scenes');
  const ASSETS_MANIFEST_DIR = path.join(projectRoot, 'content/assets-manifest');
  const COMPONENTS_DIR = path.join(projectRoot, 'src/components');

  console.log(`\n🎬 Generating Remotion components for: ${videoId}`);

  // Read Scenes
  const scenesPath = path.join(SCENES_DIR, `${videoId}.scenes.json`);
  if (!fs.existsSync(scenesPath)) throw new Error(`Scenes not found: ${scenesPath}`);
  const script: Script = JSON.parse(fs.readFileSync(scenesPath, 'utf-8'));

  // Read Assets
  const manifestPath = path.join(ASSETS_MANIFEST_DIR, `${videoId}.assets.json`);
  if (!fs.existsSync(manifestPath)) throw new Error(`Manifest not found: ${manifestPath}`);
  const manifest: AssetManifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));

  // Create Component Dir
  const videoComponentsDir = path.join(COMPONENTS_DIR, 'scenes', videoId);
  if (!fs.existsSync(videoComponentsDir)) {
    fs.mkdirSync(videoComponentsDir, { recursive: true });
  }

  // Generate Scenes
  script.scenes.forEach((scene, index) => {
    const code = generateSceneComponent(scene, manifest.assets, index, videoId, projectRoot);
    fs.writeFileSync(path.join(videoComponentsDir, `Scene${index + 1}.tsx`), code);
    console.log(`   ✓ Scene${index + 1}`);
  });

  // Generate Composition
  const compCode = generateComposition(script, videoId);
  fs.writeFileSync(path.join(COMPONENTS_DIR, `${videoId}Composition.tsx`), compCode);
  console.log(`   ✓ Composition: ${videoId}Composition.tsx`);

  console.log(`\n✅ Components generated!`);
}
