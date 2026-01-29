#!/usr/bin/env -S npx tsx
import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';
import chalk from 'chalk';
import { parseScript } from './lib/workflow/1-parse-script.ts';
import { analyzeAssets } from './lib/workflow/2-analyze-assets.ts';
import { generateAssets } from './lib/workflow/3-generate-assets.ts';
import { generateComponents } from './lib/workflow/4-generate-components.ts';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Main execution function
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command) {
    console.log(chalk.red('Please provide a command or video ID.'));
    console.log(chalk.gray('Usage: whiteboard-video-gen <video-id> | scaffold'));
    process.exit(1);
  }

  if (command === 'scaffold') {
    await scaffoldProject();
  } else {
    await runGenerator(command);
  }
}

async function scaffoldProject() {
  console.log(chalk.blue('Scaffolding new Whiteboard Video project...'));

  const projectRoot = process.cwd();
  const templateDir = path.join(__dirname, 'templates');

  try {
    // 1. Ensure src/hooks exists
    const hooksDir = path.join(projectRoot, 'src/hooks');
    await fs.ensureDir(hooksDir);

    // 2. Copy useWhiteboardAnimations.ts
    const hookSource = path.join(templateDir, 'hooks/useWhiteboardAnimations.ts');
    const hookDest = path.join(hooksDir, 'useWhiteboardAnimations.ts');

    if (await fs.pathExists(hookSource)) {
       await fs.copy(hookSource, hookDest);
       console.log(chalk.green('✓ Created src/hooks/useWhiteboardAnimations.ts'));
    } else {
       console.log(chalk.yellow(`⚠ Template hook not found at ${hookSource}`));
    }

    // 3. Ensure src/styles exists
    const stylesDir = path.join(projectRoot, 'src/styles');
    await fs.ensureDir(stylesDir);

    // 4. Copy whiteboard-theme.ts
    const themeSource = path.join(templateDir, 'whiteboard-theme.ts');
    const themeDest = path.join(stylesDir, 'whiteboard-theme.ts');

    if (await fs.pathExists(themeSource)) {
       await fs.copy(themeSource, themeDest);
       console.log(chalk.green('✓ Created src/styles/whiteboard-theme.ts'));
    } else {
        console.log(chalk.yellow(`⚠ Template theme not found at ${themeSource}`));
    }

    console.log(chalk.blue('\nScaffolding complete! You can now run the generator.'));

  } catch (error) {
    console.error(chalk.red('Scaffold failed:'), error);
  }
}

async function runGenerator(videoId) {
  console.log(chalk.green(`Starting generation for video: ${videoId}`));

  const projectRoot = process.cwd();

  try {
    // Step 1: Parse Script
    console.log(chalk.blue('\n[1/4] Parsing Script...'));
    await parseScript(projectRoot, videoId);

    // Step 2: Analyze Assets
    console.log(chalk.blue('\n[2/4] Analyzing Assets...'));
    await analyzeAssets(projectRoot, videoId);

    // Step 3: Generate Assets (API)
    console.log(chalk.blue('\n[3/4] Generating Assets...'));
    await generateAssets(projectRoot, videoId);

    // Step 4: Generate Components
    console.log(chalk.blue('\n[4/4] Generating Components...'));
    await generateComponents(projectRoot, videoId);

    // Ensure hooks and theme exist
    await scaffoldProject();

    console.log(chalk.greenBright(`\n✨ Video generation for ${videoId} completed!`));
    console.log(chalk.white(`Run 'npm start' or 'npx remotion preview' to view it.`));

  } catch (error) {
    console.error(chalk.red('\n❌ Workflow failed:'), error);
    process.exit(1);
  }
}

main().catch(console.error);
