---
name: apiyi-image-generator
description: 高效图片生成器。使用 API易的 Gemini 3 Pro Image Preview 模型生成高质量图片，固定 4K 分辨率输出。
---

# API易图片生成器

## 快速开始

```bash
# 直接调用生成图片
python scripts/generate.py "你的生图要求描述"
```

## 核心功能

| 功能 | 说明 |
|------|------|
| 高效生成 | 直接调用 API易接口，快速响应 |
| 4K 分辨率 | 固定输出 4K 高清图片 |
| 简单易用 | 一行命令生成图片 |

## 命令行参数

| 参数 | 说明 | 默认 |
|------|------|------|
| `prompt` | 生图要求描述 | 必选 |
| `-o, --output` | 输出目录 | ~/generated-images |
| `--aspect-ratio` | 图片比例 | 1:1 |

## 配置

在 `.env` 文件中配置 API：

```bash
# API易 Nano Banana Pro
NANO_BANANA_API_KEY=your_key
NANO_BANANA_API_URL=https://api.apiyi.com/v1beta/models/gemini-3-pro-image-preview:generateContent
```

## 输出

图片保存到指定输出目录，文件名格式：`image_YYYYMMDD_HHMMSS.png`

## 使用示例

```bash
# 生成产品图
python scripts/generate.py "商业产品摄影，白色背景，一双半透明超薄丝袜优雅摆放"

# 生成风景图
python scripts/generate.py "美丽的日落海滩，金色阳光洒在波浪上"

# 生成人像图
python scripts/generate.py "年轻女性的职业肖像，柔和光线，简洁背景"
```
