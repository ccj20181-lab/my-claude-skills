#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API易图片生成器 - 高效生成 4K 高清图片

使用方式：
python scripts/generate.py "你的生图要求描述"
"""
import sys
import io
import os
import base64
import time
import argparse
from pathlib import Path
from typing import Optional
import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DEFAULT_OUTPUT_DIR = str(Path.home() / "generated-images")
DEFAULT_ASPECT_RATIO = "1:1"
DEFAULT_RESOLUTION = "4K"


def load_env_config():
    """加载环境配置"""
    script_dir = Path(__file__).parent.parent
    env_file = script_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)


def get_api_config() -> tuple[str, str]:
    """获取 API 配置"""
    load_env_config()

    api_key = os.environ.get("NANO_BANANA_API_KEY", "").strip()
    api_url = os.environ.get("NANO_BANANA_API_URL", "").strip()

    if not api_key or not api_url:
        raise ValueError("未配置 API易，请检查 .env 文件")

    return api_url, api_key


def generate_image(prompt: str, api_url: str, api_key: str,
                   aspect_ratio: str = DEFAULT_ASPECT_RATIO,
                   resolution: str = DEFAULT_RESOLUTION) -> Optional[bytes]:
    """
    生成单张图片

    Args:
        prompt: 生图要求描述
        api_url: API 地址
        api_key: API 密钥
        aspect_ratio: 图片比例 (1:1, 3:4, 16:9 等)
        resolution: 分辨率 (1K, 2K, 4K)

    Returns:
        图片二进制数据，失败返回 None
    """
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect_ratio,
                "imageSize": resolution
            }
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        print(f"正在生成图片...")
        print(f"  分辨率: {resolution}")
        print(f"  比例: {aspect_ratio}")

        response = requests.post(api_url, headers=headers, json=payload, timeout=180)
        response.raise_for_status()
        data = response.json()

        # 解析响应获取图片
        if "candidates" in data:
            for candidate in data["candidates"]:
                content = candidate.get("content", {})
                parts = content.get("parts", [])
                for part in parts:
                    if "inlineData" in part:
                        img_data = part["inlineData"].get("data", "")
                        if img_data:
                            return base64.b64decode(img_data)

        print(f"  [警告] 未找到图片数据")
        return None

    except Exception as e:
        print(f"  [错误] {e}")
        return None


def save_image(data: bytes, output_dir: str, filename: str) -> str:
    """保存图片到文件"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    path.write_bytes(data)
    return str(path)


def main():
    parser = argparse.ArgumentParser(
        description="API易图片生成器 - 高效生成 4K 高清图片",
        epilog="示例:\n"
               "  python scripts/generate.py '美丽的日落海滩'\n"
               "  python scripts/generate.py '产品摄影' -o ~/images"
    )
    parser.add_argument("prompt", help="生图要求描述")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT_DIR,
                        help="输出目录")
    parser.add_argument("--aspect-ratio", default=DEFAULT_ASPECT_RATIO,
                        help="图片比例 (默认: 1:1)")

    args = parser.parse_args()

    # 获取 API 配置
    try:
        api_url, api_key = get_api_config()
        print(f"[API] API易 已配置")
    except ValueError as e:
        print(f"[错误] {e}")
        return 1

    # 生成图片
    image_data = generate_image(args.prompt, api_url, api_key, args.aspect_ratio)

    if image_data:
        # 保存图片
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.png"
        path = save_image(image_data, args.output, filename)

        print(f"\n[成功] 图片已保存到: {path}")
        return 0
    else:
        print(f"\n[失败] 图片生成失败")
        return 1


if __name__ == "__main__":
    exit(main())
