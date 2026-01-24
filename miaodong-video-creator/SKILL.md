---
name: miaodong-video-creator
description: 秒懂金融视频创作工具。专为财经博主设计，将金融知识转化为通俗易懂的3:4竖屏科普视频。整合AI图片生成与Remotion视频制作，支持金融小知识、财经热点、概念拆解三种视频类型。使用场景：(1) 从财经主题生成完整科普视频 (2) 批量生成财经场景配图 (3) 创建与信息图风格一致的视频内容。触发词：秒懂视频、财经视频、金融科普视频。
---

# 秒懂金融视频创作工具

## 快速开始

### 对话式工作流（推荐）

```
用户: 帮我制作一个关于"IPO是什么"的金融小知识科普视频

Claude: 好的主人！让浮浮酱来帮你规划这个视频喵～

        📋 视频规划：
        - 类型：金融小知识科普
        - 时长：约45秒
        - 规格：3:4竖屏 (1080×1440)
        - 模板：Knowledge-Explainer

        🎬 场景规划：
        1. 开场 (5秒) - "秒懂金融" + "今天聊聊IPO"
        2. 概念解释 (12秒) - 什么是IPO，用小明故事说明
        3. 举例说明 (15秒) - 近期IPO案例配图
        4. 关键要点 (10秒) - 三个重点总结
        5. 结尾 (3秒) - 关注引导

        需要我开始生成素材吗？

用户: 可以，开始吧

Claude: [创建项目] → [生成5张3:4场景图片] → [生成Composition代码]

        ✅ 项目已创建：~/miaodong-videos/ipo-explainer/
        ✅ 5张AI图片已生成（3:4竖屏）
        ✅ Composition代码已就绪

        运行以下命令预览：
        cd ~/miaodong-videos/ipo-explainer && npx remotion studio
```

### 命令行工具

```bash
# 1. 创建 Remotion 项目（3:4竖屏）
python3 scripts/create_project.py --name ipo-explainer --path ~/miaodong-videos/

# 2. 批量生成场景图片（3:4比例）
python3 scripts/generate_scenes.py --config scenes.json --project ~/miaodong-videos/ipo-explainer/

# 3. 生成 Composition 代码（第二阶段）
python3 scripts/generate_composition.py --manifest scenes-manifest.json --template knowledge
```

## 视频规格（财经竖屏）

| 参数 | 值 | 说明 |
|------|-----|------|
| **宽高比** | 3:4 | 竖屏格式 |
| **分辨率** | 1080×1440 | 高清竖屏 |
| **帧率** | 30fps | 标准帧率 |
| **典型时长** | 30-90秒 | 科普短视频 |

## 三种视频模板

### 1. Knowledge-Explainer（金融小知识）

**适用于**：概念科普类内容，如"什么是IPO"、"什么是期货"

**场景结构**：
1. 开场标题 (3-5秒) - "秒懂金融" + 主题
2. 概念解释 (10-15秒) - 是什么 + 小明故事
3. 举例说明 (10-15秒) - 具体案例配图
4. 关键要点 (8-12秒) - 三个重点总结
5. 结尾引导 (3秒) - 关注/点赞

### 2. Hotspot-Analysis（财经热点）

**适用于**：时效性财经新闻解读，如"英伟达市值破万亿"

**场景结构**：
1. 热点引入 (5秒) - 新闻标题/数据
2. 事件解读 (15-20秒) - 发生了什么
3. 影响分析 (15-20秒) - 为什么重要
4. 投资启示 (10-15秒) - 怎么办
5. 结尾 (3秒)

### 3. Concept-Breakdown（概念拆解）

**适用于**：三段式分析，如"房贷新政：是什么、为什么、怎么看"

**场景结构**：
1. 开场 (5秒) - 主题引入
2. 是什么 (15-20秒) - 概念解释
3. 为什么 (15-20秒) - 原因分析
4. 怎么办 (15-20秒) - 行动建议
5. 结尾 (3秒)

## 场景配置格式

创建 `scenes.json` 配置文件：

```json
{
  "title": "IPO是什么",
  "type": "knowledge",
  "duration_seconds": 45,
  "resolution": {"width": 1080, "height": 1440},
  "fps": 30,
  "scenes": [
    {
      "id": "opening",
      "duration_frames": 150,
      "type": "title",
      "content": {
        "main_title": "秒懂金融",
        "sub_title": "今天聊聊IPO"
      },
      "background": {
        "prompt": "科技感深蓝色渐变背景，金融元素点缀，简洁现代，3:4竖屏",
        "style": "modern"
      }
    },
    {
      "id": "explanation",
      "duration_frames": 360,
      "type": "content",
      "content": {
        "text": "IPO就是首次公开募股...",
        "highlight_words": ["首次", "公开", "募股"]
      },
      "background": {
        "prompt": "股市交易大厅，绿色上涨箭头，简洁插画风格，3:4竖屏",
        "style": "illustration"
      }
    }
  ]
}
```

## 脚本使用说明

### create_project.py - 创建 Remotion 项目

```bash
# 基础用法
python3 scripts/create_project.py --name 项目名

# 完整参数
python3 scripts/create_project.py \
  --name ipo-explainer \
  --path ~/miaodong-videos/ \
  --template knowledge
```

**参数说明**：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--name` | 项目名称 | 必填 |
| `--path` | 项目路径 | ~/miaodong-videos/ |
| `--template` | 模板类型 | knowledge |

**模板类型**：
- `knowledge` - 金融小知识科普
- `hotspot` - 财经热点解读
- `breakdown` - 概念拆解

### generate_scenes.py - 批量生成场景图片

```bash
# 基础用法
python3 scripts/generate_scenes.py --config scenes.json --project 项目路径

# 完整参数
python3 scripts/generate_scenes.py \
  --config scenes.json \
  --project ~/miaodong-videos/ipo-explainer/ \
  --style modern
```

**参数说明**：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--config` | 场景配置 JSON 文件 | 必填 |
| `--project` | Remotion 项目路径 | 必填 |
| `--style` | 预设风格 | modern |

**预设风格**：
- `modern` - 现代科技感（深蓝/紫色渐变）
- `classic` - 经典商务风（白底+品牌色）
- `minimal` - 极简风格（大色块+简洁线条）

## 与现有 Skills 协作

### 与 miaodong-finance-writer 配合

1. 先用 `miaodong-finance-writer` 生成文案
2. 再用 `miaodong-video-creator` 将文案转为视频

### 与 finance-infographic 风格一致

- 使用相同的品牌色彩
- 保持相同的边框/圆角样式
- logo 位置和样式一致

## 配置

复用 `apiyi-image-generator` 的 API 配置：

```bash
# .env 文件（自动复用 apiyi-image-generator 的配置）
NANO_BANANA_API_KEY=your_key
NANO_BANANA_API_URL=https://api.apiyi.com/v1beta/models/gemini-3-pro-image-preview:generateContent
```

## 文件结构

```
miaodong-video-creator/
├── SKILL.md                          # 主文档（本文件）
├── .env                              # API 配置（软链接到 apiyi）
│
├── scripts/
│   ├── create_project.py             # 创建 Remotion 项目
│   ├── generate_scenes.py            # 批量生成场景图片
│   ├── generate_composition.py       # 生成 Composition 代码（第二阶段）
│   └── utils/
│       ├── image_api.py              # 封装 apiyi 图片生成
│       └── templates.py              # 模板渲染工具
│
├── references/
│   ├── video-templates.md            # 财经视频模板指南（第二阶段）
│   ├── scene-prompts.md              # 财经场景图片提示词库
│   └── style-consistency.md          # 风格一致性指南（第二阶段）
│
└── assets/
    └── templates/
        ├── knowledge-explainer/      # 金融小知识科普模板
        ├── hotspot-analysis/         # 财经热点解读模板（第二阶段）
        └── concept-breakdown/        # 概念拆解模板（第二阶段）
```

## 输出

- **项目路径**：`~/miaodong-videos/[项目名]/`
- **场景图片**：`public/scenes/scene_01.png`, `scene_02.png`, ...
- **资源清单**：`public/scenes/scenes-manifest.json`

## 预览和渲染

```bash
# 预览
cd ~/miaodong-videos/ipo-explainer && npx remotion studio

# 渲染
cd ~/miaodong-videos/ipo-explainer && npx remotion render src/index.ts MyVideo out/video.mp4
```

## 注意事项

1. **图片比例**：所有场景图片固定为 3:4 竖屏（1080×1440）
2. **中文字体**：Remotion 项目需要配置中文字体支持
3. **品牌一致性**：保持与 finance-infographic 相同的视觉风格
4. **文案来源**：建议使用 miaodong-finance-writer 生成的文案

## 实现阶段

### MVP（当前）
- ✅ SKILL.md 基础文档
- ✅ `create_project.py` - 3:4竖屏项目创建
- ✅ `generate_scenes.py` - 批量场景图片生成
- ✅ Knowledge-Explainer 模板
- ✅ `references/scene-prompts.md` - 财经提示词库

### 第二阶段（计划中）
- [ ] `generate_composition.py` - TSX 代码生成
- [ ] Hotspot-Analysis 模板
- [ ] Concept-Breakdown 模板
- [ ] 中文字体自动配置

### 第三阶段（计划中）
- [ ] 与 miaodong-finance-writer 深度集成
- [ ] 与 finance-infographic 风格同步
- [ ] 自动渲染输出
- [ ] 字幕/配音支持
