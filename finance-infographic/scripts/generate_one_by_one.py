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
OUTPUT_DIR = "F:/finance-infographics"


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
    return f"""【任务】基于【文案】生成一张信息图，图文并茂，信息密度高。

【核心要求 - 风格必须100%复刻参考图，如同出自同一人之手】

你必须让这张图片与参考图的视觉风格**完全一样，如同出自同一人之手**：

1. **背景颜色和渐变**：必须与参考图一模一样，不能有任何色差
2. **主标题样式**：
   - **字体大小固定为64px**：这是图片中主标题的标准字号，**绝对不能改变**
   - **颜色**：与参考图的主标题颜色完全一致
   - **粗细**：与参考图的主标题粗细完全一致
   - **阴影**：与参考图的主标题阴影完全一致
   - **背景形状**：与参考图的主标题背景形状完全一致
3. **小标题样式**：字体大小、颜色、背景样式都与参考图完全一致
4. **正文样式**：字体大小、颜色、间距都与参考图完全一致
5. **卡片样式**：圆角、边框、阴影、背景色都与参考图完全一致
6. **配色方案**：所有颜色（主色、辅助色、文字色）都与参考图完全一致
7. **布局结构**：内容板块的排列方式、间距都与参考图完全一致

【重要警告】
- **如同出自同一人之手**：每一处细节都要与参考图完全一样
- **主标题字号固定为64px**：这是唯一标准，不能因主标题文字多少而改变
- **其他视觉元素也必须固定**：不能因内容长短而改变任何样式

【内容要求 - 图文并茂，信息密度高】
- **图文平衡**：文字和视觉元素要恰到好处地结合
- **相得益彰**：视觉元素要能辅助理解文字内容，文字要能诠释视觉元素的意义
- **信息密度高**：在有限的画面内呈现丰富的内容
- **层次分明**：使用小标题和视觉分隔分层次呈现内容
- **重点突出**：关键数字、关键概念要用强调色突出

【核心要求 - 内容100%来自文案】
- **只使用【文案】中的文字**，不要添加、修改、删除任何内容
- **必须逐字使用文案中的关键表述**，特别是带编号的步骤和重要概念
- **如果文案中有"(1)"、"(2)"、"第一步"等编号，图片中必须一模一样

【参考图】用于风格参考，但**不要使用参考图中的任何文字**。

【文案】
{content}

【输出】只输出图片，不要任何文字说明。"""


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
