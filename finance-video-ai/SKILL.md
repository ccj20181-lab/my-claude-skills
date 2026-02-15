# 财经科普短视频 AI 生成器

> 极简手绘简笔画风格 | 固定2分钟 | 小红书3:4比例

## 触发词
生成视频、视频科普、秒懂视频、财经视频、finance video

## 📋 概述

这是一个专门用于生成财经科普短视频的 Skill，采用 AI 自动生成场景插画的方式，一键生成2分钟的极简手绘简笔画风格视频。

### 核心特点
- 🎨 **AI 生成插画**: 完全使用 Gemini API 生成极简手绘简笔画风格图片
- ⏱️ **固定时长**: 2分钟（120秒）
- 📱 **小红书优化**: 3:4 比例（1080×1440）
- 🎯 **一键生成**: 从主题到成品视频全流程自动化

### 与 remotion-skill 的区别
| 特性 | remotion-skill | finance-video-ai |
|------|---------------|-----------------|
| 图片来源 | 素材库 + SVG火柴人 | **AI生成插画** |
| 时长 | 可配置 | 固定120秒 |
| 工作流 | 多步骤 | 一键生成 |
| 风格 | 白板手绘 | 极简黑白涂鸦 |

---

## 🚀 快速开始

### 1. 环境配置

```bash
# 复制环境变量模板
cp ~/.codex/skills/finance-video-ai/.env.example ~/.codex/skills/finance-video-ai/.env

# 编辑 .env 文件，填写 API 密钥
nano ~/.codex/skills/finance-video-ai/.env
```

### 2. 安装依赖

```bash
# Python 依赖
cd ~/.codex/skills/finance-video-ai
pip3 install anthropic aiohttp requests python-dotenv Pillow

# Remotion 依赖（首次使用时自动安装）
cd remotion
npm install
```

### 3. 生成视频

```bash
# 完整流程（默认输出到 ~/Desktop/秒懂金融学院/视频输出/<主题>/）
cd ~/.codex/skills/finance-video-ai
python3 scripts/main.py --topic "IPO"

# 快速测试（仅生成脚本）
python3 scripts/main.py -t "基金定投" --dry-run

# 跳过语音生成
python3 scripts/main.py -t "股票" --skip-tts
```

默认产物目录结构：
`~/Desktop/秒懂金融学院/视频输出/<主题>/`
- `video.mp4`（成片）
- `口播文案.txt`（口播文案）
- `audio/*.mp3`（分场景音频）
- `script.json`（结构化脚本）

---

## 📁 目录结构

```
~/.codex/skills/finance-video-ai/
├── SKILL.md                    # 本文档
├── .env                        # API密钥配置
├── scripts/
│   ├── main.py                 # 主入口
│   ├── config.py               # 配置管理
│   ├── content_generator.py    # 脚本生成
│   ├── image_generator.py      # AI图片生成
│   └── tts_minimax.py          # TTS语音合成
├── remotion/                   # Remotion 渲染端
│   ├── src/
│   │   ├── Root.tsx
│   │   ├── Composition.tsx
│   │   ├── components/
│   │   ├── types/
│   │   └── theme/
│   └── public/
│       ├── images/             # AI生成的插画
│       └── audio/              # TTS语音文件
├── references/
│   └── style-guide.md          # 视觉风格指南
└── output/                     # 生成的视频输出
```

---

## 🔄 工作流程

```
用户输入主题
    │
    ▼
┌─────────────────────────────┐
│ Phase 1: 智能脚本生成        │
│ • Claude API 生成场景脚本    │
│ • 包含口播文案 + 图片描述     │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ Phase 2: AI 场景插画生成     │
│ • Gemini API 生成简笔画      │
│ • 极简黑白风格               │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ Phase 3: TTS 语音合成        │
│ • MiniMax API 生成语音       │
│ • 词级别时间戳               │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ Phase 4: 数据准备            │
│ • 生成 data.json             │
│ • 复制资源文件               │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ Phase 5: 视频渲染            │
│ • Remotion 渲染              │
│ • 输出 MP4                   │
└─────────────────────────────┘
```

---

## 🎨 视觉风格

### 极简手绘简笔画
- **背景**: 纯白色 `#FFFFFF`
- **线条**: 黑色细线 `#000000` (1-2px)
- **人物**: 圆形头部 + 线条身体
- **情绪**: 用符号表达（问号、感叹号等）
- **构图**: 大量留白，居中

详细风格指南请参考 `references/style-guide.md`

---

## ⚙️ 配置说明

### 环境变量
```bash
# Claude API (脚本生成)
ANTHROPIC_API_KEY=your_key

# API易 - Gemini图片生成
NANO_BANANA_API_KEY=your_key
NANO_BANANA_API_URL=https://api.apiyi.com/v1beta/models/gemini-2.0-flash-exp-image-generation:generateContent

# MiniMax TTS (语音合成)
MINIMAX_API_KEY=your_key
MINIMAX_GROUP_ID=your_group_id
MINIMAX_VOICE_ID=female-tianmei
```

### 命令行参数
| 参数 | 简写 | 说明 |
|------|------|------|
| `--topic` | `-t` | 视频主题（必需） |
| `--output` | `-o` | 输出目录 |
| `--dry-run` | | 仅生成脚本，快速测试 |
| `--skip-tts` | | 跳过语音生成 |
| `--skip-render` | | 跳过视频渲染 |
| `--no-check` | | 跳过依赖检查 |
| `--target-duration` | | 目标总时长（默认 `120` 秒） |
| `--target-tolerance` | | 目标时长容差（秒，默认 `6`） |
| `--script-attempts` | | 脚本生成尝试次数（默认 `3`） |
| `--scene-gap` | | 场景间停顿秒数（默认 `0.12`，更小更紧凑） |
| `--tts-speed` | | 固定语速，默认 `1.0`（建议保持固定） |
| `--use-script-duration` | | 使用脚本预设时长（会拉长句间停顿，不建议） |
| `--export-root` | | 输出根目录（默认 `~/Desktop/秒懂金融学院/视频输出`） |
| `--book-cover` | | 结尾书封图片路径 |
| `--book-outro-seconds` | | 结尾书封展示时长（秒，默认3，最大3） |
| `--book-outro-text` | | 结尾小字文案 |
| `--reuse-from` | | 复用已有输出目录素材（默认复用脚本/图片/音频） |
| `--reuse-script` | | 仅复用 `script.json` |
| `--reuse-images` | | 仅复用图片，缺失才调用生图 API |
| `--reuse-audio` | | 仅复用音频，缺失才调用 TTS |

### 高效复用示例
```bash
# 在已有视频基础上重新渲染（不重复生图/配音）
python3 scripts/main.py -t "对冲基金" \
  --reuse-from "./output/对冲基金_20260215_063211" \
  --no-check

# 仅调紧口播节奏（缩短句间停顿）
python3 scripts/main.py -t "对冲基金" \
  --reuse-from "./output/对冲基金_20260215_063211" \
  --scene-gap 0.08 \
  --no-check

# 在已有图片基础上重做口播并逼近120秒
python3 scripts/main.py -t "对冲基金" \
  --reuse-from "./output/对冲基金_20260215_063211" \
  --reuse-images \
  --target-duration 120 \
  --no-check
```

---

## 📊 场景类型

| 类型 | 时长 | 说明 |
|------|------|------|
| hook | 10秒 | 开场钩子，抓住注意力 |
| title | 6秒 | 标题展示 |
| question | 12秒 | 抛出核心问题 |
| explain | 20秒 | 核心概念解释 |
| analogy | 18秒 | 生活化类比 |
| example | 18秒 | 具体案例 |
| summary | 12秒 | 要点总结 |
| cta | 8秒 | 结尾引导 |

---

## ⚠️ 注意事项

1. **API 密钥**: 确保所有必需的 API 密钥已配置
2. **图片生成**: Gemini 生成图片可能需要 30-60 秒
3. **风格一致性**: AI 生成的简笔画风格可能略有差异
4. **Node.js**: 需要 Node.js 18+ 运行 Remotion

---

## 🐛 故障排除

### 图片生成失败
```
检查 NANO_BANANA_API_KEY 和 NANO_BANANA_API_URL 是否正确配置
```

### Remotion 渲染失败
```bash
# 重新安装依赖
cd ~/.codex/skills/finance-video-ai/remotion
rm -rf node_modules
npm install
```

### TTS 语音失败
```
检查 MINIMAX_API_KEY 和 MINIMAX_GROUP_ID 是否正确配置
```

---

## 📝 更新日志

### v1.0.0 (2024-01)
- 初始版本
- 支持完整视频生成流程
- AI 自动生成场景插画
- 极简手绘简笔画风格
