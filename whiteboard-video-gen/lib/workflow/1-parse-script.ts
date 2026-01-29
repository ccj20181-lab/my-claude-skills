import * as fs from 'fs';
import * as path from 'path';
import type {
  Script,
  ScriptMetadata,
  ScriptScene,
  ScriptAssetRef,
  SceneType,
  ScriptParseResult,
} from '../types/script.js';

/**
 * 场景类型关键词映射
 */
const SCENE_TYPE_KEYWORDS: Record<string, SceneType> = {
  '开场': 'hook',
  '钩子': 'hook',
  'hook': 'hook',
  '标题': 'title',
  'title': 'title',
  '故事': 'story',
  '案例': 'story',
  'story': 'story',
  '问题': 'problem',
  'problem': 'problem',
  '概念': 'concept',
  '解释': 'concept',
  'concept': 'concept',
  '比喻': 'metaphor',
  '类比': 'metaphor',
  'metaphor': 'metaphor',
  '流程': 'process',
  '步骤': 'process',
  'process': 'process',
  '总结': 'summary',
  'summary': 'summary',
  '结尾': 'outro',
  '收尾': 'outro',
  'outro': 'outro',
};

/**
 * 解析 frontmatter 元数据
 */
function parseMetadata(content: string): { metadata: Partial<ScriptMetadata>; body: string } {
  const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);

  if (!frontmatterMatch) {
    return { metadata: {}, body: content };
  }

  const [, frontmatter, body] = frontmatterMatch;
  const metadata: Partial<ScriptMetadata> = {};

  // 解析 YAML 风格的 frontmatter
  frontmatter.split('\n').forEach(line => {
    const match = line.match(/^(\w+):\s*(.+)$/);
    if (match) {
      const [, key, value] = match;
      switch (key) {
        case 'id':
          metadata.id = value.trim();
          break;
        case 'title':
          metadata.title = value.trim().replace(/^["']|["']$/g, '');
          break;
        case 'duration':
          metadata.duration = parseInt(value, 10);
          break;
        case 'author':
          metadata.author = value.trim();
          break;
        case 'createdAt':
          metadata.createdAt = value.trim();
          break;
        case 'tags':
          metadata.tags = value
            .replace(/^\[|\]$/g, '')
            .split(',')
            .map(t => t.trim());
          break;
      }
    }
  });

  return { metadata, body };
}

/**
 * 检测场景类型
 */
function detectSceneType(title: string): SceneType {
  const lowerTitle = title.toLowerCase();

  for (const [keyword, type] of Object.entries(SCENE_TYPE_KEYWORDS)) {
    if (lowerTitle.includes(keyword.toLowerCase())) {
      return type;
    }
  }

  return 'concept'; // 默认类型
}

/**
 * 解析场景内容
 */
function parseScene(
  heading: string,
  content: string,
  index: number
): ScriptScene {
  const title = heading.replace(/^#+\s*/, '').trim();
  const type = detectSceneType(title);

  // 解析时长
  const durationMatch = content.match(/时长[：:]\s*(\d+)\s*秒?/);
  const duration = durationMatch ? parseInt(durationMatch[1], 10) : 3;

  // 解析文案/旁白
  const narrationMatch = content.match(/(?:文案|旁白)[：:]\s*[""]?([^""]+)[""]?/);
  const narration = narrationMatch ? narrationMatch[1].trim() : '';

  // 解析画面描述
  const visualMatch = content.match(/(?:画面|视觉)[：:]\s*(.+)/);
  const visual = visualMatch ? visualMatch[1].trim() : undefined;

  // 解析素材需求
  const assets: ScriptAssetRef[] = [];
  const assetSection = content.match(/素材[需求]*[：:]\s*([\s\S]*?)(?=\n##|\n\n|$)/);

  if (assetSection) {
    const assetLines = assetSection[1].split('\n').filter(l => l.trim().startsWith('-'));
    assetLines.forEach(line => {
      // 格式: - asset_name (描述) [已存在]
      const assetMatch = line.match(/-\s*(\w+)\s*[（(]([^）)]+)[）)]\s*(\[已存在\])?/);
      if (assetMatch) {
        assets.push({
          name: assetMatch[1],
          description: assetMatch[2],
          exists: !!assetMatch[3],
        });
      }
    });
  }

  return {
    index,
    type,
    title,
    duration,
    narration,
    visual,
    assets,
  };
}

/**
 * 解析完整文案内容
 */
function parseScriptContent(content: string, videoId: string): ScriptParseResult {
  try {
    const { metadata, body } = parseMetadata(content);

    // 确保有必要的元数据
    const fullMetadata: ScriptMetadata = {
      id: metadata.id || videoId,
      title: metadata.title || videoId,
      duration: metadata.duration || 30,
      author: metadata.author,
      createdAt: metadata.createdAt || new Date().toISOString().split('T')[0],
      tags: metadata.tags,
    };

    // 按 ## 分割场景
    const sceneBlocks = body.split(/(?=^##\s)/m).filter(block => block.trim());
    const scenes: ScriptScene[] = [];

    sceneBlocks.forEach((block, index) => {
      const lines = block.split('\n');
      const heading = lines[0];

      if (heading.startsWith('## ')) {
        const sceneContent = lines.slice(1).join('\n');
        scenes.push(parseScene(heading, sceneContent, index + 1));
      }
    });

    return {
      success: true,
      script: {
        metadata: fullMetadata,
        scenes,
        rawContent: content,
      },
    };
  } catch (error) {
    return {
      success: false,
      errors: [error instanceof Error ? error.message : String(error)],
    };
  }
}

/**
 * 主流程：解析脚本文件
 */
export async function parseScript(projectRoot: string, videoId: string) {
  const SCRIPTS_DIR = path.join(projectRoot, 'content/scripts');
  const SCENES_DIR = path.join(projectRoot, 'content/scenes');

  console.log(`\n📝 Parsing script: ${videoId}`);

  // 读取文案文件
  const scriptPath = path.join(SCRIPTS_DIR, `${videoId}.md`);

  if (!fs.existsSync(scriptPath)) {
    throw new Error(`Script file not found: ${scriptPath}`);
  }

  const content = fs.readFileSync(scriptPath, 'utf-8');
  const result = parseScriptContent(content, videoId);

  if (!result.success || !result.script) {
    throw new Error(`Parse failed: ${result.errors?.join(', ')}`);
  }

  // 确保输出目录存在
  if (!fs.existsSync(SCENES_DIR)) {
    fs.mkdirSync(SCENES_DIR, { recursive: true });
  }

  // 保存场景定义
  const outputPath = path.join(SCENES_DIR, `${videoId}.scenes.json`);
  fs.writeFileSync(outputPath, JSON.stringify(result.script, null, 2), 'utf-8');

  console.log(`✅ Script parsed successfully!`);
  console.log(`   - Scenes: ${result.script.scenes.length}`);
  console.log(`   - Total duration: ${result.script.metadata.duration}s`);
  console.log(`   - Output: ${outputPath}`);
}
