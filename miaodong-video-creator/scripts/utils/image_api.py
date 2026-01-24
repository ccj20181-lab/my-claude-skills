#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image API Utility - 封装 API易 图片生成接口

复用 apiyi-image-generator 的 API 配置，固定 3:4 竖屏输出
"""
import sys
import io
import os
import base64
import time
from pathlib import Path
from typing import Optional, Tuple
import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 固定视频规格：3:4 竖屏
DEFAULT_ASPECT_RATIO = "3:4"
DEFAULT_RESOLUTION = "4K"  # 1080x1440


def load_env_config() -> None:
    """加载环境配置，优先从当前 skill 目录，其次从 apiyi-image-generator"""
    # 优先级 1: 当前 skill 目录的 .env
    script_dir = Path(__file__).parent.parent.parent
    env_file = script_dir / ".env"

    if env_file.exists():
        load_dotenv(env_file)
        return

    # 优先级 2: apiyi-image-generator 的 .env
    apiyi_env = Path.home() / ".claude" / "skills" / "apiyi-image-generator" / ".env"
    if apiyi_env.exists():
        load_dotenv(apiyi_env)
        return

    # 优先级 3: finance-infographic 的 .env
    finance_env = Path.home() / ".claude" / "skills" / "finance-infographic" / ".env"
    if finance_env.exists():
        load_dotenv(finance_env)


def get_api_config() -> Tuple[str, str]:
    """获取 API 配置"""
    load_env_config()

    api_key = os.environ.get("NANO_BANANA_API_KEY", "").strip()
    api_url = os.environ.get("NANO_BANANA_API_URL", "").strip()

    if not api_key or not api_url:
        raise ValueError("未配置 API易，请检查 .env 文件或确保 apiyi-image-generator 已配置")

    return api_url, api_key


def generate_image(
    prompt: str,
    api_url: str,
    api_key: str,
    aspect_ratio: str = DEFAULT_ASPECT_RATIO,
    resolution: str = DEFAULT_RESOLUTION
) -> Optional[bytes]:
    """
    生成单张图片

    Args:
        prompt: 生图要求描述
        api_url: API 地址
        api_key: API 密钥
        aspect_ratio: 图片比例，默认 3:4 竖屏
        resolution: 分辨率，默认 4K

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
        print(f"  正在生成图片...")
        print(f"    分辨率: {resolution}")
        print(f"    比例: {aspect_ratio}")

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
                            print(f"  ✅ 图片生成成功")
                            return base64.b64decode(img_data)

        print(f"  ⚠️ 未找到图片数据")
        return None

    except requests.exceptions.Timeout:
        print(f"  ❌ 请求超时（180秒）")
        return None
    except requests.exceptions.RequestException as e:
        print(f"  ❌ 请求失败: {e}")
        return None
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return None


def save_image(data: bytes, output_path: Path) -> str:
    """保存图片到文件"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(data)
    return str(output_path)


def generate_and_save(
    prompt: str,
    output_path: Path,
    aspect_ratio: str = DEFAULT_ASPECT_RATIO,
    resolution: str = DEFAULT_RESOLUTION
) -> Optional[str]:
    """
    生成并保存图片

    Args:
        prompt: 生图要求描述
        output_path: 输出文件路径
        aspect_ratio: 图片比例
        resolution: 分辨率

    Returns:
        保存的文件路径，失败返回 None
    """
    try:
        api_url, api_key = get_api_config()
    except ValueError as e:
        print(f"  ❌ API配置错误: {e}")
        return None

    image_data = generate_image(prompt, api_url, api_key, aspect_ratio, resolution)

    if image_data:
        path = save_image(image_data, output_path)
        print(f"  📁 已保存: {path}")
        return path

    return None
