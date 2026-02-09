---
name: miaodong-video
description: 秒懂金融视频科普生成器。根据主题一键生成2-3分钟财经科普视频，白板手绘风格，支持MiniMax语音合成。触发词：生成视频、视频科普、秒懂视频、财经视频、miaodong video。
---

# 秒懂金融视频生成器

根据金融主题自动生成 2-3 分钟的财经科普视频，专为小红书平台优化。

## 特点

- 🎬 **一键生成**: 输入主题，自动生成完整视频
- 📐 **小红书优化**: 3:4 竖版 (1080x1440)，完美适配平台
- 🎨 **白板手绘风格**: 简洁清晰的视觉设计
- 🎭 **火柴人动画**: 可爱的角色表情增加趣味性
- 🔊 **AI 语音合成**: MiniMax TTS 自然中文口播
- 📝 **智能脚本**: LLM 自动生成场景化内容

## 快速开始

```bash
# 进入 skill 目录
cd "$HOME/.codex/skills/remotion-skill"

# 生成视频（完整流程）
python3 scripts/main.py --topic "IPO" --output ./output

# 仅生成脚本（预览内容）
python3 scripts/main.py --topic "基金" --dry-run

# 使用已有脚本
python3 scripts/main.py --script ./output/script.json --output ./output
```

## 工作流程

```
用户输入主题 (如 "IPO")
        ↓
┌─────────────────────────────────────────┐
│  Phase 1: 内容生成 (Python + Claude)     │
│  - 生成场景化视频脚本                     │
│  - 自动拆分为 hook/explain/summary 等场景 │
└─────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────┐
│  Phase 2: 资产生成                       │
│  - MiniMax TTS 生成语音                  │
│  - 匹配火柴人形象和图标                   │
└─────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────┐
│  Phase 3: 视频渲染 (Remotion)            │
│  - 应用白板手绘主题                       │
│  - 渲染最终 MP4 视频                     │
└─────────────────────────────────────────┘
        ↓
    输出 MP4 视频
```

## 环境配置

### 必需环境变量

```bash
# MiniMax TTS API (用于语音合成)
export MINIMAX_API_KEY="your_api_key"
export MINIMAX_GROUP_ID="your_group_id"

# 可选：默认使用的 voice_id（用于克隆音色或自定义音色）
export MINIMAX_VOICE_ID="miaodong-custom-voice"

# Anthropic API (用于脚本生成，如果未设置则使用默认)
export ANTHROPIC_API_KEY="your_api_key"
```

### 安装依赖

```bash
# Python 依赖
pip install anthropic aiohttp

# Remotion 依赖
cd remotion && npm install
```

## 命令行选项

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--topic, -t` | 视频主题 | 必填 |
| `--output, -o` | 输出目录 | ./output |
| `--duration, -d` | 目标时长（秒） | 150 (2.5分钟) |
| `--style` | 风格: compact/detailed | detailed |
| `--voice` | 语音音色ID | female-tianmei |
| `--dry-run` | 仅生成脚本 | false |
| `--skip-tts` | 跳过语音生成 | false |
| `--skip-render` | 跳过视频渲染 | false |
| `--preview` | 在 Remotion Studio 预览 | false |

## 场景类型

脚本会自动组合以下场景类型：

| 类型 | 用途 | 时长建议 |
|------|------|----------|
| `hook` | 开场钩子，抓住注意力 | 8-12秒 |
| `title` | 标题展示 + 主题引入 | 5-8秒 |
| `question` | 抛出核心问题 | 10-15秒 |
| `explain` | 概念深度解释 | 15-25秒 |
| `analogy` | 生活化类比 | 15-20秒 |
| `example` | 具体案例说明 | 15-20秒 |
| `comparison` | 对比展示 | 15-20秒 |
| `summary` | 要点回顾 | 10-15秒 |
| `cta` | 结尾引导 | 8-10秒 |

## 素材库

### 火柴人形象 (`assets/characters/`)

| 文件名 | 用途 |
|--------|------|
| `thinking.png` | 思考、疑问场景 |
| `happy.png` | 明白、总结场景 |
| `confused.png` | 问题引入场景 |
| `pointing.png` | 讲解、指示场景 |
| `waving.png` | 开头/结尾场景 |

### 金融图标 (`assets/icons/`)

- 货币类: money, coin, cash, wallet, yuan, dollar
- 市场类: stock, stock_up, stock_down, chart, trend
- 机构类: bank, company, government, exchange
- 概念类: risk, profit, loss, growth, dividend

### 生成占位素材

```bash
python3 scripts/asset_matcher.py --create-placeholders
```

## 输出文件

生成完成后，输出目录包含：

```
output/
├── script.json          # 视频脚本
├── audio/               # 语音文件
│   ├── scene_01.mp3
│   ├── scene_01.json    # 时间戳
│   └── ...
└── video.mp4            # 最终视频
```

## 自定义开发

### 修改视觉主题

编辑 `remotion/src/theme/whiteboard.ts` 调整颜色、字体等。

### 添加新场景类型

1. 在 `scripts/config.py` 添加场景定义
2. 在 `remotion/src/types/scene.ts` 添加类型
3. 在 `remotion/src/components/Scene.tsx` 添加渲染逻辑

### 预览 Remotion Studio

```bash
cd remotion && npm run dev
```

## 参考文档

- [场景模板库](references/scene-templates.md)
- [视觉风格指南](references/style-guide.md)
- [TTS 配置说明](references/tts-config.md)

## 依赖的 Skills

- `remotion-best-practices` - Remotion 动画和音频最佳实践
- `miaodong-finance-writer` - 秒懂金融写作风格规范（可选参考）

## 示例

### 生成 IPO 科普视频

```bash
python3 scripts/main.py --topic "IPO" --duration 150
```

### 生成简短版基金介绍

```bash
python3 scripts/main.py --topic "基金" --duration 90 --style compact
```

### 预览脚本内容

```bash
python3 scripts/main.py --topic "股票" --dry-run
```
