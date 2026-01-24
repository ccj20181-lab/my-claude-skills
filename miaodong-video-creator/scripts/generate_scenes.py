#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Scenes - 批量生成财经场景图片

根据场景配置 JSON 文件，调用 API易 生成 3:4 竖屏场景图片
自动保存到 Remotion 项目的 public/scenes/ 目录
"""
import sys
import io
import os
import json
import argparse
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加 utils 到路径
sys.path.insert(0, str(Path(__file__).parent))
from utils.image_api import generate_and_save, get_api_config

# 预设风格的提示词增强
STYLE_ENHANCEMENTS = {
    "modern": "现代科技感，深蓝紫色渐变背景，简洁线条，霓虹光效点缀",
    "classic": "经典商务风格，白色背景，专业配色，简洁大气",
    "minimal": "极简设计风格，大色块，简洁几何形状，留白美学",
    "illustration": "扁平化插画风格，明快色彩，可爱卡通元素",
    "infographic": "信息图风格，数据可视化，图表元素，专业排版"
}

# 财经主题的提示词增强
FINANCE_ENHANCEMENTS = {
    "stock": "股票市场元素，K线图，涨跌箭头，交易数据",
    "investment": "投资理财元素，资产配置图，收益曲线",
    "banking": "银行金融元素，货币符号，安全稳健",
    "crypto": "加密货币元素，区块链，数字科技感",
    "insurance": "保险保障元素，安全盾牌，家庭保护",
    "realestate": "房地产元素，房屋建筑，城市天际线"
}

# 固定比例
ASPECT_RATIO = "3:4"
RESOLUTION = "4K"


def load_scene_config(config_path: str) -> Dict[str, Any]:
    """加载场景配置 JSON 文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def enhance_prompt(base_prompt: str, style: str = "modern", theme: str = None) -> str:
    """
    增强提示词，添加风格和财经主题元素

    Args:
        base_prompt: 基础提示词
        style: 风格类型
        theme: 财经主题

    Returns:
        增强后的提示词
    """
    parts = [base_prompt]

    # 添加风格增强
    if style in STYLE_ENHANCEMENTS:
        parts.append(STYLE_ENHANCEMENTS[style])

    # 添加财经主题增强
    if theme and theme in FINANCE_ENHANCEMENTS:
        parts.append(FINANCE_ENHANCEMENTS[theme])

    # 强调 3:4 竖屏
    parts.append("3:4竖屏构图，适合手机观看")

    # 强调高质量
    parts.append("高清细节，专业品质")

    return "，".join(parts)


def generate_scene_images(
    scenes: List[Dict],
    output_dir: Path,
    style: str = "modern",
    theme: str = None
) -> List[Dict]:
    """
    批量生成场景图片

    Args:
        scenes: 场景配置列表
        output_dir: 输出目录
        style: 预设风格
        theme: 财经主题

    Returns:
        生成结果列表（用于创建 manifest）
    """
    results = []
    total = len(scenes)

    print(f"\n🎨 开始生成 {total} 张场景图片")
    print(f"   风格: {style}")
    print(f"   输出: {output_dir}")
    print(f"{'=' * 50}")

    for i, scene in enumerate(scenes, 1):
        scene_id = scene.get("id", f"scene_{i:02d}")
        filename = f"scene_{i:02d}.png"
        output_path = output_dir / filename

        print(f"\n[{i}/{total}] 生成场景: {scene_id}")

        # 获取背景配置
        background = scene.get("background", {})
        base_prompt = background.get("prompt", "简洁的财经背景")
        scene_style = background.get("style", style)

        # 增强提示词
        full_prompt = enhance_prompt(base_prompt, scene_style, theme)
        print(f"   提示词: {full_prompt[:60]}...")

        # 生成并保存图片
        result_path = generate_and_save(
            prompt=full_prompt,
            output_path=output_path,
            aspect_ratio=ASPECT_RATIO,
            resolution=RESOLUTION
        )

        if result_path:
            result = {
                "id": scene_id,
                "image": f"scenes/{filename}",
                "startFrame": scene.get("start_frame", i * 150),
                "durationFrames": scene.get("duration_frames", 150),
                "content": scene.get("content", {}),
                "generated": True
            }
        else:
            result = {
                "id": scene_id,
                "image": f"scenes/{filename}",
                "generated": False,
                "error": "生成失败"
            }

        results.append(result)

        # 添加延迟，避免 API 限流
        if i < total:
            print("   ⏳ 等待 2 秒...")
            time.sleep(2)

    return results


def create_manifest(results: List[Dict], config: Dict, output_dir: Path) -> str:
    """
    创建资源清单 JSON

    Args:
        results: 生成结果列表
        config: 原始配置
        output_dir: 输出目录

    Returns:
        清单文件路径
    """
    manifest = {
        "title": config.get("title", "秒懂金融视频"),
        "type": config.get("type", "knowledge"),
        "resolution": config.get("resolution", {"width": 1080, "height": 1440}),
        "fps": config.get("fps", 30),
        "duration_seconds": config.get("duration_seconds", 30),
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "scenes": results,
        "stats": {
            "total": len(results),
            "success": sum(1 for r in results if r.get("generated", False)),
            "failed": sum(1 for r in results if not r.get("generated", False))
        }
    }

    manifest_path = output_dir / "scenes-manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\n📋 资源清单已创建: {manifest_path}")
    return str(manifest_path)


def create_sample_config(output_path: str) -> None:
    """创建示例配置文件"""
    sample = {
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
                    "prompt": "科技感深蓝色渐变背景，金融元素点缀，简洁现代",
                    "style": "modern"
                }
            },
            {
                "id": "explanation",
                "duration_frames": 360,
                "type": "content",
                "content": {
                    "text": "IPO就是首次公开募股，是指一家企业第一次将它的股份向公众出售",
                    "highlight_words": ["首次", "公开", "募股"]
                },
                "background": {
                    "prompt": "股市交易大厅，明亮现代，简洁插画风格",
                    "style": "illustration"
                }
            },
            {
                "id": "example",
                "duration_frames": 450,
                "type": "content",
                "content": {
                    "text": "小明开了家烤鸭店，生意火爆开了好几家连锁，想要上市融资...",
                    "character": "xiaoming"
                },
                "background": {
                    "prompt": "可爱的小明角色在烤鸭店前，卡通插画风格，温馨场景",
                    "style": "illustration"
                }
            },
            {
                "id": "keypoints",
                "duration_frames": 300,
                "type": "summary",
                "content": {
                    "points": [
                        "IPO = 首次公开募股 = 上市",
                        "帮企业融资、扩大规模",
                        "股票打新是投资者参与方式"
                    ]
                },
                "background": {
                    "prompt": "总结要点背景，三个并列卡片布局，清晰层次",
                    "style": "infographic"
                }
            },
            {
                "id": "ending",
                "duration_frames": 90,
                "type": "ending",
                "content": {
                    "text": "关注秒懂金融，每天学点财经知识"
                },
                "background": {
                    "prompt": "结尾引导背景，关注按钮，温暖渐变色",
                    "style": "modern"
                }
            }
        ]
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sample, f, indent=2, ensure_ascii=False)

    print(f"✅ 示例配置已创建: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="批量生成财经场景图片（3:4竖屏）",
        epilog="示例:\\n"
               "  python3 scripts/generate_scenes.py --config scenes.json --project ~/miaodong-videos/ipo/\\n"
               "  python3 scripts/generate_scenes.py --sample  # 创建示例配置",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--config", help="场景配置 JSON 文件")
    parser.add_argument("--project", help="Remotion 项目路径")
    parser.add_argument("--style", default="modern",
                        choices=list(STYLE_ENHANCEMENTS.keys()),
                        help="预设风格 (默认: modern)")
    parser.add_argument("--theme",
                        choices=list(FINANCE_ENHANCEMENTS.keys()),
                        help="财经主题增强")
    parser.add_argument("--sample", action="store_true",
                        help="创建示例配置文件")
    parser.add_argument("--output", help="自定义输出目录（覆盖 project/public/scenes）")

    args = parser.parse_args()

    # 创建示例配置
    if args.sample:
        create_sample_config("sample-scenes.json")
        return 0

    # 验证必要参数
    if not args.config or not args.project:
        parser.error("--config 和 --project 参数是必需的（或使用 --sample 创建示例）")

    # 验证配置文件存在
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        return 1

    # 验证项目路径
    project_path = Path(args.project)
    if not project_path.exists():
        print(f"❌ 项目路径不存在: {project_path}")
        print(f"   请先使用 create_project.py 创建项目")
        return 1

    # 确定输出目录
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = project_path / "public" / "scenes"

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n🎬 秒懂金融场景图片生成器")
    print(f"{'=' * 50}")

    # 验证 API 配置
    try:
        api_url, api_key = get_api_config()
        print(f"✅ API 配置已加载")
    except ValueError as e:
        print(f"❌ API 配置错误: {e}")
        return 1

    # 加载配置
    config = load_scene_config(str(config_path))
    scenes = config.get("scenes", [])

    if not scenes:
        print(f"❌ 配置文件中没有场景定义")
        return 1

    print(f"📄 已加载配置: {config.get('title', '未命名')}")
    print(f"   场景数量: {len(scenes)}")
    print(f"   视频类型: {config.get('type', 'knowledge')}")

    # 生成图片
    results = generate_scene_images(
        scenes=scenes,
        output_dir=output_dir,
        style=args.style,
        theme=args.theme
    )

    # 创建资源清单
    manifest_path = create_manifest(results, config, output_dir)

    # 统计结果
    success = sum(1 for r in results if r.get("generated", False))
    failed = len(results) - success

    print(f"\n{'=' * 50}")
    print(f"🎉 生成完成!")
    print(f"   成功: {success} 张")
    print(f"   失败: {failed} 张")
    print(f"   清单: {manifest_path}")

    if failed > 0:
        print(f"\n⚠️ 有 {failed} 张图片生成失败，可以重新运行脚本")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(main())
