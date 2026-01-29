#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成蜗牛朋友圈微信聊天截图 (Hybrid Mode)
1. 使用 LLM 解析对话内容为结构化 JSON
2. 使用 Pillow 进行像素级精准渲染
"""
import sys
import io
import os
import json
import base64
import time
import re
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Any
import requests
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# --- Constants & Configuration ---
DEFAULT_RESOLUTION = "4K"
OUTPUT_DIR = "output"

# Visual Constants (Pixel Perfect)
WIDTH = 929
BG_COLOR = (247, 247, 247) # #F7F7F7
HEADER_COLOR = (237, 237, 237) # #EDEDED
GREEN_BUBBLE = (149, 236, 105) # #95EC69
WHITE_BUBBLE = (255, 255, 255)
TEXT_COLOR = (0, 0, 0)
RED_BOX_COLOR = (255, 0, 0)

# MacOS System Font
FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_SIZE = 42
LINE_HEIGHT = 56

AVATAR_SIZE = 125
AVATAR_MARGIN_SIDE = 30
BUBBLE_MARGIN_SIDE = 20
BUBBLE_PADDING = 30
MAX_BUBBLE_WIDTH = 600

def load_env_config():
    """加载环境变量配置"""
    finance_skill_dir = Path.home() / ".claude/skills/finance-infographic"
    env_file = finance_skill_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"  [已加载配置] {env_file}")
    else:
        print(f"  [警告] 未找到配置文件: {env_file}")

def get_api_config(force_api: str = None) -> Tuple[str, str, str]:
    """获取 API 配置"""
    load_env_config()

    if force_api == "google":
        api_key = os.environ.get("GOOGLE_API_KEY", "").strip()
        api_url = os.environ.get("GOOGLE_API_URL", "").strip()
        if api_key and api_url: return api_url, api_key, "Google Gemini 3 Pro"
        raise ValueError("未配置 Google API")

    if force_api == "nanobanana":
        api_key = os.environ.get("NANO_BANANA_API_KEY", "").strip()
        api_url = os.environ.get("NANO_BANANA_API_URL", "").strip()
        if api_key and api_url: return api_url, api_key, "API易 Nano Banana Pro"
        raise ValueError("未配置 API易")

    # Default priority
    priority = os.environ.get("API_PRIORITY", "1").strip()
    if priority == "1":
        api_key = os.environ.get("NANO_BANANA_API_KEY", "").strip()
        api_url = os.environ.get("NANO_BANANA_API_URL", "").strip()
        if api_key and api_url: return api_url, api_key, "API易 Nano Banana Pro"

    api_key = os.environ.get("GOOGLE_API_KEY", "").strip()
    api_url = os.environ.get("GOOGLE_API_URL", "").strip()
    if api_key and api_url: return api_url, api_key, "Google Gemini 3 Pro"

    raise ValueError("请至少配置一个 API")

# --- Rendering Logic (Pillow) ---

def load_resources(assets_dir: Path):
    avatar_path = assets_dir / "avatar_woniu.png"
    if avatar_path.exists():
        avatar = Image.open(avatar_path).convert("RGBA")
        avatar = avatar.resize((AVATAR_SIZE, AVATAR_SIZE), Image.Resampling.LANCZOS)
    else:
        print(f"  [警告] 头像未找到: {avatar_path}，使用灰色占位符")
        avatar = Image.new("RGBA", (AVATAR_SIZE, AVATAR_SIZE), (200, 200, 200))

    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except:
        print("  [警告] 系统字体未找到，使用默认字体")
        font = ImageFont.load_default()

    return avatar, font

def wrap_text(text, font, max_width):
    """Wrap text to fit max_width."""
    lines = []
    current_line = []

    for char in text:
        current_line.append(char)
        w = font.getlength("".join(current_line))
        if w > max_width:
            if len(current_line) > 1:
                lines.append("".join(current_line[:-1]))
                current_line = [char]
            else:
                lines.append("".join(current_line))
                current_line = []

    if current_line:
        lines.append("".join(current_line))

    return lines

def draw_bubble(draw, x, y, width, height, color, is_right):
    """Draw a rounded rectangle bubble with a triangle pointer."""
    radius = 15
    tri_w = 15
    tri_h = 20
    tri_y_offset = 35

    # Bubble Body
    draw.rounded_rectangle((x, y, x + width, y + height), radius=radius, fill=color)

    # Triangle Pointer
    if is_right:
        p1 = (x + width, y + tri_y_offset)
        p2 = (x + width + tri_w, y + tri_y_offset + tri_h // 2)
        p3 = (x + width, y + tri_y_offset + tri_h)
        draw.polygon([p1, p2, p3], fill=color)
    else:
        p1 = (x, y + tri_y_offset)
        p2 = (x - tri_w, y + tri_y_offset + tri_h // 2)
        p3 = (x, y + tri_y_offset + tri_h)
        draw.polygon([p1, p2, p3], fill=color)

def render_image(data: Dict[str, Any], assets_dir: Path) -> Image.Image:
    """Render the chat data to an image."""
    avatar_img, font = load_resources(assets_dir)

    title = data.get("title", "学员-雨萱🌸")
    messages = data.get("messages", [])

    # Initialize Canvas
    # Create a tall canvas first, then crop
    img_height = 10000  # Increased to support longer chats
    img = Image.new("RGB", (WIDTH, img_height), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Draw Header
    draw.rectangle((0, 0, WIDTH, 130), fill=HEADER_COLOR)

    # Draw Title
    title_bbox = font.getbbox(title)
    title_w = title_bbox[2] - title_bbox[0]
    draw.text(((WIDTH - title_w) // 2, 80), title, font=font, fill=(0, 0, 0))

    # Layout Loop
    current_y = 180

    for msg in messages:
        content = msg.get("content", "")
        speaker = msg.get("speaker", "other")
        is_me = (speaker == "me" or speaker == "teacher" or speaker == "woniu")
        is_highlight = msg.get("highlight", False)

        # Wrap text
        max_text_w = MAX_BUBBLE_WIDTH - BUBBLE_PADDING * 2
        lines = wrap_text(content, font, max_text_w)

        # Calculate Bubble Size
        text_height = len(lines) * LINE_HEIGHT
        bubble_w = 0
        for line in lines:
            line_w = font.getlength(line)
            if line_w > bubble_w:
                bubble_w = line_w

        bubble_w = int(bubble_w) + BUBBLE_PADDING * 2
        bubble_h = text_height + BUBBLE_PADDING * 1.5

        # Ensure min size
        bubble_w = max(bubble_w, 80)
        bubble_h = max(bubble_h, 80)

        # Draw Elements
        if is_me:
            # Right Side
            avatar_x = int(WIDTH - AVATAR_MARGIN_SIDE - AVATAR_SIZE)
            avatar_y = int(current_y)

            # Paste Avatar
            img.paste(avatar_img, (avatar_x, avatar_y), avatar_img)

            # Bubble Position
            bubble_x = int(avatar_x - 20 - bubble_w)
            bubble_y = int(current_y)

            draw_bubble(draw, bubble_x, bubble_y, bubble_w, bubble_h, GREEN_BUBBLE, is_right=True)

            # Text
            text_x = bubble_x + BUBBLE_PADDING
            text_y = bubble_y + BUBBLE_PADDING - 5
            for i, line in enumerate(lines):
                draw.text((text_x, text_y + i * LINE_HEIGHT), line, font=font, fill=TEXT_COLOR)

        else:
            # Left Side
            # Avatar is invisible (cropped style)
            bubble_x = 30 # Margin from left edge
            bubble_y = int(current_y)

            draw_bubble(draw, bubble_x, bubble_y, bubble_w, bubble_h, WHITE_BUBBLE, is_right=False)

            # Text
            text_x = bubble_x + BUBBLE_PADDING
            text_y = bubble_y + BUBBLE_PADDING - 5
            for i, line in enumerate(lines):
                draw.text((text_x, text_y + i * LINE_HEIGHT), line, font=font, fill=TEXT_COLOR)

            # Red Highlight Box
            if is_highlight:
                padding = 5
                box_x1 = bubble_x - padding
                box_y1 = bubble_y - padding
                box_x2 = bubble_x + bubble_w + padding
                box_y2 = bubble_y + bubble_h + padding

                # Hollow Red Rectangle, 4px width
                draw.rectangle((box_x1, box_y1, box_x2, box_y2), outline=RED_BOX_COLOR, width=4)

        current_y += max(bubble_h, AVATAR_SIZE) + 40

    # Final Crop
    final_img = img.crop((0, 0, WIDTH, current_y + 50))
    return final_img

# --- LLM Logic (Data Extraction) ---

def parse_chat_content(chat_content: str, api_url: str, api_key: str) -> Optional[Dict]:
    """Call LLM to parse chat content into JSON."""

    prompt = f"""
Analyze the following chat conversation between a teacher (Woniu/Me) and a student.
Extract the conversation into a structured JSON format.

Input Chat:
{chat_content}

Output Format (JSON Only):
{{
  "title": "Student Name (e.g. 学员-XXX)",
  "messages": [
    {{
      "speaker": "me" (if Woniu/Teacher) or "other" (if Student),
      "content": "message text",
      "highlight": true/false (Set to true ONLY for the single most enthusiastic/positive feedback message from the student. If multiple, pick the best one. Teacher messages are never highlighted.)
    }}
  ]
}}
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        print(f"  [正在分析] 调用 API 解析对话内容...")
        if "api.apiyi.com" in api_url:
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        else:
            response = requests.post(f"{api_url}?key={api_key}",
                                   headers={"Content-Type": "application/json"},
                                   json=payload, timeout=60)

        response.raise_for_status()
        data = response.json()

        text_response = ""
        if "candidates" in data:
            parts = data["candidates"][0].get("content", {}).get("parts", [])
            if parts:
                text_response = parts[0].get("text", "")

        if not text_response:
            print("  [错误] API 返回空内容")
            return None

        # Clean up Markdown code blocks if present
        text_response = text_response.strip()
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.startswith("```"):
            text_response = text_response[3:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]

        return json.loads(text_response)

    except Exception as e:
        print(f"  [错误] API 调用或 JSON 解析失败: {e}")
        return None

# --- Main ---

def save_image_to_disk(img: Image.Image, output_dir: Path, filename: str) -> str:
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / filename
    img.save(file_path)
    return str(file_path)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate WeChat screenshot from chat content (Hybrid Mode)')
    parser.add_argument('--content', help='Path to markdown file containing chat content', default=None)
    parser.add_argument('--text', help='Direct chat content string', default=None)
    args = parser.parse_args()

    print("\n" + "="*60)
    print("蜗牛朋友圈 - 微信聊天截图生成器 (Hybrid Pixel-Perfect)")
    print("="*60 + "\n")

    script_dir = Path(__file__).parent.parent
    assets_dir = script_dir / "assets"

    # Ensure assets exist
    if not (assets_dir / "avatar_woniu.png").exists():
        print(f"[错误] 缺失资源文件: avatar_woniu.png")
        print(f"请先运行提取脚本或手动放置头像到 {assets_dir}")
        return

    # Load Chat Content
    chat_content = ""
    if args.text:
        chat_content = args.text.replace('\\n', '\n')
        print("[已加载] 聊天记录: (来自命令行输入)")
    elif args.content:
        content_file = Path(args.content)
        if not content_file.exists():
            print(f"[错误] 未找到聊天记录文件: {content_file}")
            return
        chat_content = content_file.read_text(encoding="utf-8")
        print(f"[已加载] 聊天记录: {content_file.name}")
    else:
        content_file = script_dir / "content" / "chat_record_sample.md"
        if not content_file.exists():
            print(f"[错误] 未找到聊天记录文件: {content_file}")
            return
        chat_content = content_file.read_text(encoding="utf-8")
        print(f"[已加载] 聊天记录: {content_file.name}")

    # API Config
    try:
        api_url, api_key, provider_name = get_api_config()
        print(f"[API] {provider_name} 已配置\n")
    except ValueError as e:
        print(f"[错误] {e}")
        return

    # Step 1: Parse Content with LLM
    print("[1/2] 正在智能分析对话结构...")
    chat_data = parse_chat_content(chat_content, api_url, api_key)

    if not chat_data:
        print("[失败] 无法解析对话内容")
        return

    print(f"  [成功] 解析完成: 标题='{chat_data.get('title')}', 消息数={len(chat_data.get('messages', []))}")

    # Step 2: Render Image
    print("[2/2] 正在进行像素级渲染...")
    try:
        final_image = render_image(chat_data, assets_dir)

        # Save
        output_dir = script_dir / OUTPUT_DIR
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"wechat_chat_hybrid_{timestamp}.png"
        saved_path = save_image_to_disk(final_image, output_dir, filename)

        print(f"\n[完成] 截图已保存: {saved_path}")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n[失败] 渲染过程出错: {e}")
        import traceback
        traceback.print_exc()
        print("="*60 + "\n")

if __name__ == "__main__":
    main()
