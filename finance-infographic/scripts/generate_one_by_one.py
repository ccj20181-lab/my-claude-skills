#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逐张生成财经信息图 - 支持选择 API，按主题分类存放

使用方式：
python scripts/generate_one_by_one.py "md文件.md" -r 4K --api google --topic "主题名"
"""
import sys
import io
import os
import base64
import time
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DEFAULT_ASPECT_RATIO = "3:4"
DEFAULT_RESOLUTION = "2K"
OUTPUT_DIR = str(Path.home() / "finance-infographics")


def load_env_config():
    script_dir = Path(__file__).parent.parent
    env_file = script_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)


def get_api_config(force_api: str = None) -> Tuple[str, str, str]:
    """
    获取 API 配置
    force_api: 强制使用指定 API ("google" 或 "nanobanana")
    """
    load_env_config()

    if force_api == "google":
        api_key = os.environ.get("GOOGLE_API_KEY", "").strip()
        api_url = os.environ.get("GOOGLE_API_URL", "").strip()
        if api_key and api_url:
            return api_url, api_key, "Google Gemini 3 Pro"
        raise ValueError("未配置 Google API")

    if force_api == "nanobanana":
        api_key = os.environ.get("NANO_BANANA_API_KEY", "").strip()
        api_url = os.environ.get("NANO_BANANA_API_URL", "").strip()
        if api_key and api_url:
            return api_url, api_key, "API易 Nano Banana Pro"
        raise ValueError("未配置 API易")

    priority = os.environ.get("API_PRIORITY", "1").strip()

    if priority == "1":
        api_key = os.environ.get("NANO_BANANA_API_KEY", "").strip()
        api_url = os.environ.get("NANO_BANANA_API_URL", "").strip()
        if api_key and api_url:
            return api_url, api_key, "API易 Nano Banana Pro"
        print("  [警告] API易 未配置，回退到 Google API")

    api_key = os.environ.get("GOOGLE_API_KEY", "").strip()
    api_url = os.environ.get("GOOGLE_API_URL", "").strip()
    if api_key and api_url:
        return api_url, api_key, "Google Gemini 3 Pro"

    raise ValueError("请至少配置一个 API")


def get_reference_images() -> List[Dict]:
    """每次都重新加载参考图"""
    ref_dir = Path(__file__).parent.parent / "references"
    images = []

    if ref_dir.exists():
        for img_path in ref_dir.glob("*.png"):
            with open(img_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
                images.append({
                    "mimeType": "image/png",
                    "data": b64
                })

    return images


def build_prompt(content: str) -> str:
    return f"""首先看参考图，然后严格复刻所有样式生成新图。

【固定样式元素 - 必须与参考图100%相同】

第1项：右上角logo
- 位置：右上角固定位置
- 内容：参考图logo的文字内容
- 颜色：参考图logo的背景色和文字色
- 大小：与参考图logo相同的大小
- 形状：与参考图logo相同的形状（圆角矩形等）

第2项：主标题
- 字号：64px（固定不变）
- 颜色：参考图主标题的颜色
- 字体：参考图主标题的字体样式
- 背景：参考图主标题的背景形状和颜色
- 位置：与参考图主标题相同的位置

第3项：边框和卡片
- 边框圆角：参考图的圆角大小
- 边框粗细：参考图的边框粗细
- 边框颜色：参考图的边框颜色
- 阴影效果：参考图的阴影（偏移、模糊、颜色）
- 卡片背景：参考图的卡片背景色

第4项：配色方案
- 背景色：参考图的背景色和渐变
- 主色调：参考图的主要颜色
- 辅助色：参考图的辅助颜色
- 文字色：参考图的文字颜色
- 强调色：参考图用来强调的颜色

第5项：信息密度和布局
- 信息密度：参考图的密度水平（内容丰富程度）
- 布局结构：参考图的板块排列方式
- 间距：参考图的元素间距
- 比例：参考图的视觉比例

【严格禁止】
❌ logo：禁止改变位置、大小、内容、颜色、形状
❌ 主标题：禁止改变字号、颜色、字体、背景
❌ 边框：禁止改变圆角、粗细、颜色、阴影
❌ 配色：禁止改变任何颜色
❌ 密度：禁止降低信息密度或增加空白
❌ 风格：禁止改变绘图风格

【唯一允许的不同】
唯一的不同是：将参考图的文字内容替换为【文案】中的内容。所有视觉元素必须100%复刻。

【文案内容处理】
✅ 使用【文案】中的文字
✅ 保留编号：(1) (2) 第一步 第二步
❌ 禁止添加【文案】中没有的任何文字

【文案】
{content}

只输出图片。"""


def generate_one_image(content: str, api_url: str, api_key: str,
                       resolution: str = DEFAULT_RESOLUTION) -> Optional[bytes]:
    """生成单张图片"""
    text_prompt = build_prompt(content)
    ref_images = get_reference_images()

    parts = []

    if ref_images:
        for img in ref_images:
            parts.append({"inlineData": img})
        print(f"  [已加载 {len(ref_images)} 张参考图]")

    parts.append({"text": text_prompt})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": DEFAULT_ASPECT_RATIO,
                "imageSize": resolution
            }
        }
    }

    try:
        if "api.apiyi.com" in api_url:
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
            response = requests.post(api_url, headers=headers, json=payload, timeout=180)
        else:
            response = requests.post(f"{api_url}?key={api_key}", headers={"Content-Type": "application/json"}, json=payload, timeout=180)

        response.raise_for_status()
        data = response.json()

        if "candidates" in data:
            for part in data["candidates"][0].get("content", {}).get("parts", []):
                if "inlineData" in part:
                    return base64.b64decode(part["inlineData"].get("data", ""))

        print(f"  [警告] 未找到图片数据")
        return None
    except Exception as e:
        print(f"  [错误] {e}")
        return None


def save_image(data: bytes, output_dir: str, filename: str) -> str:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    path.write_bytes(data)
    return str(path)


def generate_one(md_file: str, resolution: str = DEFAULT_RESOLUTION,
                 output_dir: str = OUTPUT_DIR, force_api: str = None,
                 topic: str = None) -> bool:
    """
    逐张生成信息图

    Args:
        md_file: md文件路径
        resolution: 分辨率
        output_dir: 输出根目录
        force_api: 强制使用指定 API ("google" 或 "nanobanana")
        topic: 主题文件夹名称
    """
    api_url, api_key, provider_name = get_api_config(force_api)
    print(f"\n[API] {provider_name} 已配置")

    # 如果指定了主题，创建主题文件夹
    if topic:
        output_dir = Path(output_dir) / topic
    else:
        output_dir = Path(output_dir)

    content = Path(md_file).read_text(encoding="utf-8")
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"infographic_{timestamp}_000.png"

    print(f"\n{'='*50}")
    print(f"生成图片: {md_file}")
    print(f"输出目录: {output_dir}")
    print(f"内容长度: {len(content)} 字符")
    print(f"{'='*50}")

    if data := generate_one_image(content, api_url, api_key, resolution):
        path = save_image(data, output_dir, filename)
        print(f"\n  [成功] {path}")

        # 生成完成后删除临时 md 文件
        print("\n[清理] 删除临时 md 文件...")
        try:
            Path(md_file).unlink()
            print(f"  已删除: {Path(md_file).name}")
        except Exception as e:
            print(f"  删除失败: {md_file} ({e})")

        return True
    else:
        print(f"\n  [失败]")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="逐张生成财经信息图 - 支持选择 API，按主题分类存放",
        epilog="示例:\n"
               "  python scripts/generate_one_by_one.py md.md -r 4K\n"
               "  python scripts/generate_one_by_one.py md.md -r 4K --api google\n"
               "  python scripts/generate_one_by_one.py md.md -r 4K --topic '期权'\n"
               "  python scripts/generate_one_by_one.py md.md -r 4K --interactive"
    )
    parser.add_argument("md_file", help="md文件路径")
    parser.add_argument("-r", "--resolution", choices=["1K", "2K", "4K"], default="4K", help="分辨率")
    parser.add_argument("-o", "--output", default=OUTPUT_DIR, help="输出目录")
    parser.add_argument("--api", choices=["google", "nanobanana"],
                        help="强制使用指定 API (google 或 nanobanana)")
    parser.add_argument("--topic", default=None, help="主题文件夹名称")
    parser.add_argument("--interactive", action="store_true",
                        help="交互式模式：询问用户选择")

    args = parser.parse_args()

    # 如果指定了交互式模式，询问用户
    if args.interactive:
        print("\n" + "="*50)
        print("请选择要使用的 API")
        print("="*50)
        print("\n  [1] API易 Nano Banana Pro (默认，性价比高)")
        print("  [2] Google Gemini 3 Pro (官方 API)")

        api_choice = input("\n请输入编号 (1-2): ").strip()
        if api_choice == "2":
            args.api = "google"
        else:
            args.api = "nanobanana"

        print("\n请输入主题名称（用于创建文件夹存放图片）")
        print("例如：IPO、英伟达市值、比特币 等")
        topic = input("主题名称: ").strip()
        if topic:
            args.topic = topic

    generate_one(
        md_file=args.md_file,
        resolution=args.resolution,
        output_dir=args.output,
        force_api=args.api if args.api == "google" else None,
        topic=args.topic
    )


if __name__ == "__main__":
    exit(main())
