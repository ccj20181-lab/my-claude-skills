#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财经信息图生成器 - 支持选择 API，按主题分类存放

使用方式：
python scripts/batch_generate.py "md1.md" "md2.md" ... -r 4K --api google --topic "主题名"
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

    # 默认使用配置文件中的优先级
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


_ref_images_cache = None


def get_reference_images() -> List[Dict]:
    global _ref_images_cache
    if _ref_images_cache is not None:
        return _ref_images_cache

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

    _ref_images_cache = images
    return images


def build_prompt(content: str, main_title: str = None) -> str:
    """
    构建生成提示词

    Args:
        content: md文件内容
        main_title: 主标题（可选），如"是什么"、"为什么"、"怎么办"
    """
    title_instruction = ""
    if main_title:
        title_instruction = f"\n\n【主标题】\n{main_title}\n（使用这个作为信息图的主标题，字号必须固定为64px，样式与参考图完全一致）"

    return f"""【任务】看着这张参考图，生成一张全新内容的信息图，风格必须100%完全一致。

【核心要求 - 100%风格复刻】
**直接看着参考图来生成，保持完全相同的视觉风格，如同出自同一人之手：**

**必须保持的固定元素（重中之重）：**
1. **右上角logo**：必须保留，位置、大小、样式与参考图完全一致
2. **边框样式**：圆角、粗细、颜色、阴影效果必须完全一致
3. **主标题格式**：字号固定64px，字体、颜色、粗细、阴影、背景形状与参考图完全一致
4. **整体布局**：内容板块的排列方式、间距、比例与参考图完全一致

**其他视觉元素：**
- 背景颜色和渐变效果
- 小标题和正文的字体样式
- 卡片的圆角、边框、阴影、背景色
- 整体配色方案（主色、辅助色、文字色）
- 所有视觉元素的间距和比例

【内容要求】
- **图文并茂**：文字和视觉元素平衡结合
- **信息层次分明**：用小标题和视觉分隔分层次呈现
- **重点突出**：关键数字和概念用强调色标记
- **信息密度高**：在有限画面内呈现丰富内容

【内容来源 - 严格遵守】
- **只使用【文案】中的文字**，不得添加、修改、删除任何内容
- **逐字使用关键表述**，特别是编号如"(1)"、"(2)"、"第一步"等
- **参考图仅用于风格参考，不使用其文字内容**
{title_instruction}

【文案】
{content}

【输出要求】只输出图片。"""


def generate_image(content: str, api_url: str, api_key: str,
                   resolution: str = DEFAULT_RESOLUTION, main_title: str = None) -> Optional[bytes]:
    text_prompt = build_prompt(content, main_title)
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


def save_image(data: bytes, output_dir: str, index: int, timestamp: str) -> str:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"infographic_{timestamp}_{index:03d}.png"
    path = output_dir / filename
    path.write_bytes(data)
    return str(path)


def batch_generate(md_files: List[str], resolution: str = DEFAULT_RESOLUTION,
                   output_dir: str = OUTPUT_DIR, force_api: str = None,
                   topic: str = None, main_titles: List[str] = None) -> Dict:
    """
    批量生成信息图

    Args:
        md_files: md文件路径列表
        resolution: 分辨率
        output_dir: 输出根目录
        force_api: 强制使用指定 API ("google" 或 "nanobanana")
        topic: 主题文件夹名称
        main_titles: 主标题列表（可选），与md_files一一对应
    """
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results = {"success": True, "generated": [], "failed": []}

    # 如果指定了主题，创建主题文件夹
    if topic:
        output_dir = Path(output_dir) / topic
    else:
        output_dir = Path(output_dir)

    print(f"\n开始批量生成 {len(md_files)} 张信息图...")
    print(f"输出目录: {output_dir}")
    print("=" * 50)

    api_url, api_key, provider_name = get_api_config(force_api)
    print(f"[API] {provider_name} 已配置")
    print("=" * 50)

    print("\n[预加载] 参考图...")
    ref_images = get_reference_images()
    print(f"  [完成] 已加载 {len(ref_images)} 张参考图")

    for i, md_file in enumerate(md_files):
        print(f"\n[{i+1}/{len(md_files)}] 处理: {md_file}")

        content = Path(md_file).read_text(encoding="utf-8")
        print(f"  内容长度: {len(content)} 字符")

        # 获取对应的主标题
        main_title = main_titles[i] if main_titles and i < len(main_titles) else None
        if main_title:
            print(f"  主标题: {main_title}")

        if data := generate_image(content, api_url, api_key, resolution, main_title):
            path = save_image(data, output_dir, i, timestamp)
            results["generated"].append(path)
            print(f"  [成功] {path}")
        else:
            results["failed"].append(i)
            print(f"  [失败] 第 {i+1} 张")
        time.sleep(0.5)

    # 生成完成后删除临时 md 文件
    print("\n[清理] 删除临时 md 文件...")
    deleted = 0
    for md_file in md_files:
        try:
            Path(md_file).unlink()
            print(f"  已删除: {Path(md_file).name}")
            deleted += 1
        except Exception as e:
            print(f"  删除失败: {md_file} ({e})")
    print(f"  共删除 {deleted} 个文件")

    print("\n" + "=" * 50)
    print(f"完成！成功: {len(results['generated'])}, 失败: {len(results['failed'])}")
    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="财经信息图生成器 - 支持选择 API，按主题分类存放",
        epilog="示例:\n"
               "  python scripts/batch_generate.py md1.md md2.md -r 4K\n"
               "  python scripts/batch_generate.py md1.md -r 4K --api google\n"
               "  python scripts/batch_generate.py md1.md -r 4K --topic '英伟达市值'\n"
               "  python scripts/batch_generate.py md1.md md2.md md3.md --titles '是什么' '为什么' '怎么办'"
    )
    parser.add_argument("md_files", nargs="+", help="md文件路径列表")
    parser.add_argument("-r", "--resolution", choices=["1K", "2K", "4K"],
                        default="2K", help="分辨率")
    parser.add_argument("-o", "--output", default=OUTPUT_DIR, help="输出目录")
    parser.add_argument("--api", choices=["google", "nanobanana"],
                        help="强制使用指定 API (google 或 nanobanana)")
    parser.add_argument("--topic", default=None,
                        help="主题文件夹名称")
    parser.add_argument("--titles", nargs="+", default=None,
                        help="主标题列表，与md文件一一对应（如：'是什么' '为什么' '怎么办'）")
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

        # 询问是否需要自定义主标题
        print(f"\n检测到 {len(args.md_files)} 个md文件")
        print("是否需要为每张图指定不同的主标题？(y/n)")
        need_titles = input("选择: ").strip().lower()
        if need_titles == 'y':
            args.titles = []
            for i, md_file in enumerate(args.md_files):
                title = input(f"第{i+1}张图的主标题: ").strip()
                args.titles.append(title)

    results = batch_generate(
        md_files=args.md_files,
        resolution=args.resolution,
        output_dir=args.output,
        force_api=args.api,
        topic=args.topic,
        main_titles=args.titles
    )

    return 0 if results["success"] else 1


if __name__ == "__main__":
    exit(main())
