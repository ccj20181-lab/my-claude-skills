/**
 * 3-generate-assets.ts - AI 素材生成脚本
 */

import * as fs from 'fs';
import * as path from 'path';
import { config } from 'dotenv';
import type { AssetManifest, GenerationProgress } from '../../types/asset';
import { generateBatch, getApiStatus } from '../utils/apiyi-gemini.js';

// Load .env
config();

/**
 * Print progress bar
 */
function printProgress(progress: GenerationProgress): void {
  const percent = Math.round((progress.completed / progress.total) * 100);
  const bar = '█'.repeat(Math.floor(percent / 5)) + '░'.repeat(20 - Math.floor(percent / 5));

  process.stdout.write(
    `\r[${bar}] ${percent}% (${progress.succeeded}✓ ${progress.failed}✗)`
  );
}

/**
 * Main workflow: Generate Assets
 */
export async function generateAssets(projectRoot: string, videoId: string) {
  const ASSETS_MANIFEST_DIR = path.join(projectRoot, 'content/assets-manifest');
  const GENERATED_ASSETS_DIR = path.join(projectRoot, 'public/assets/generated');

  console.log(`\n🎨 Generating assets for: ${videoId}`);

  // Read Manifest
  const manifestPath = path.join(ASSETS_MANIFEST_DIR, `${videoId}.assets.json`);
  if (!fs.existsSync(manifestPath)) {
    throw new Error(`Asset manifest not found: ${manifestPath}`);
  }

  const manifest: AssetManifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));

  // Filter missing assets
  const missingAssets = manifest.assets.filter(
    a => (a.status === 'missing' || a.status === 'failed') && a.generation
  );

  if (missingAssets.length === 0) {
    console.log('✅ All assets already exist! Nothing to generate.');
    return;
  }

  // Check API (only if we need to generate)
  const apiStatus = getApiStatus();
  if (!apiStatus.configured) {
    throw new Error('APIYI_API_KEY environment variable not set.');
  }

  // Sort by priority (high > medium > low)
  const priorityOrder = { high: 0, medium: 1, low: 2 };
  missingAssets.sort(
    (a, b) =>
      priorityOrder[a.generation!.priority] - priorityOrder[b.generation!.priority]
  );

  console.log(`   - Missing assets to generate: ${missingAssets.length}`);

  // Ensure output directory exists
  const outputDir = path.join(GENERATED_ASSETS_DIR, videoId);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Prepare tasks
  const tasks = missingAssets.map(asset => ({
    id: asset.id,
    prompt: asset.generation!.prompt,
    outputPath: path.join(outputDir, `${asset.id}.png`),
  }));

  console.log('🚀 Starting generation...\n');

  // Execute batch
  const results = await generateBatch(tasks, {
    onProgress: printProgress,
    delayBetween: 2000,
  });

  console.log('\n\n✅ Batch generation finished.');

  // Update Manifest
  const successIds = new Set(results.filter(r => r.success).map(r => r.assetId));
  const failedIds = new Set(results.filter(r => !r.success).map(r => r.assetId));

  manifest.assets.forEach(asset => {
    if (successIds.has(asset.id)) {
      asset.status = 'generated';
      asset.existingPath = path.join(outputDir, `${asset.id}.png`);
    } else if (failedIds.has(asset.id)) {
      asset.status = 'failed';
    }
  });

  // Update counts
  manifest.existsCount = manifest.assets.filter(
    a => a.status === 'exists' || a.status === 'generated'
  ).length;
  manifest.missingCount = manifest.assets.filter(
    a => a.status === 'missing' || a.status === 'failed'
  ).length;
  manifest.generatedAt = new Date().toISOString();

  // Save updated manifest
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2), 'utf-8');

  // Report
  const succeeded = results.filter(r => r.success).length;
  const failed = results.filter(r => !r.success).length;

  console.log(`📊 Results: ${succeeded} succeeded, ${failed} failed.`);
}
