
import os
from PIL import Image, ImageDraw, ImageFont

# Constants
WIDTH = 929 # Match reference
BG_COLOR = (247, 247, 247) # #F7F7F7
HEADER_COLOR = (237, 237, 237) # #EDEDED
GREEN_BUBBLE = (149, 236, 105) # #95EC69
WHITE_BUBBLE = (255, 255, 255)
TEXT_COLOR = (0, 0, 0)
RED_BOX_COLOR = (255, 0, 0)

FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_SIZE = 42 # Approximate for 929px width
LINE_HEIGHT = 56 # 1.3-1.4x font size

AVATAR_SIZE = 125 # Slightly smaller than extracted 155 to fit nicely? Or use 140.
AVATAR_MARGIN_SIDE = 30
BUBBLE_MARGIN_SIDE = 20 # Distance from screen edge if no avatar (left) or from avatar (right)
BUBBLE_PADDING = 30
MAX_BUBBLE_WIDTH = 600

ASSETS_DIR = os.path.expanduser("~/.claude/skills/woniu-pyq/assets")
OUTPUT_DIR = os.path.expanduser("~/.claude/skills/woniu-pyq/output")

def load_resources():
    avatar_path = os.path.join(ASSETS_DIR, "avatar_woniu.png")
    if os.path.exists(avatar_path):
        avatar = Image.open(avatar_path).convert("RGBA")
        avatar = avatar.resize((AVATAR_SIZE, AVATAR_SIZE), Image.Resampling.LANCZOS)
    else:
        # Fallback square
        avatar = Image.new("RGBA", (AVATAR_SIZE, AVATAR_SIZE), (200, 200, 200))

    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except:
        print("Font not found, using default")
        font = ImageFont.load_default()

    return avatar, font

def wrap_text(text, font, max_width):
    """Wrap text to fit max_width."""
    lines = []
    current_line = []

    # Simple character based wrapping for CJK, but need to handle words for English
    # For simplicity, treating everything as chars, but strictly `text` might have English.
    # A robust approach uses `font.getlength`.

    # Hacky simple wrapping
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
    """Draw a rounded rectangle bubble."""
    radius = 15
    # For right bubble, triangle is on the right. For left, on the left.
    # Triangle size
    tri_w = 15
    tri_h = 20
    tri_y_offset = 35 # From top

    # Bubble rect
    rect_x = x
    if is_right:
        # x is the top-left of the bubble rect (excluding triangle)
        pass
    else:
        # x is top-left, but we need space for triangle on left?
        # Let's assume x is the visual start of the bubble body.
        pass

    draw.rounded_rectangle((x, y, x + width, y + height), radius=radius, fill=color)

    # Triangle
    if is_right:
        # Pointing right
        p1 = (x + width, y + tri_y_offset)
        p2 = (x + width + tri_w, y + tri_y_offset + tri_h // 2)
        p3 = (x + width, y + tri_y_offset + tri_h)
        draw.polygon([p1, p2, p3], fill=color)
    else:
        # Pointing left
        p1 = (x, y + tri_y_offset)
        p2 = (x - tri_w, y + tri_y_offset + tri_h // 2)
        p3 = (x, y + tri_y_offset + tri_h)
        draw.polygon([p1, p2, p3], fill=color)

def render_screenshot():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    avatar_img, font = load_resources()

    # Sample Data
    messages = [
        {"speaker": "other", "content": "老师，告诉您一个好消息！", "highlight": False},
        {"speaker": "other", "content": "我刚刚查了成绩，笔试第一名！太感谢您的指导了！", "highlight": True},
        {"speaker": "me", "content": "哇！太棒了！恭喜恭喜！🎉", "highlight": False},
        {"speaker": "me", "content": "这一段时间的努力没白费，面试也要加油哦！", "highlight": False},
        {"speaker": "other", "content": "嗯嗯，我会继续努力的！到时候还需要老师帮忙模拟面试呢。", "highlight": False},
    ]

    title = "学员-雨萱🌸"

    # Layout State
    current_y = 180 # Start after header + status bar area

    # 1. Measure total height needed (optional, or just create huge canvas and crop)
    # Let's create a large canvas
    img_height = 3000
    img = Image.new("RGB", (WIDTH, img_height), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Draw Header
    draw.rectangle((0, 0, WIDTH, 130), fill=HEADER_COLOR)
    # Title
    title_bbox = font.getbbox(title)
    title_w = title_bbox[2] - title_bbox[0]
    draw.text(((WIDTH - title_w) // 2, 80), title, font=font, fill=(0, 0, 0))

    # Draw Status Bar (Mockup - usually just time)
    # Skipping detailed status bar for now, just header background is fine.

    for msg in messages:
        content = msg["content"]
        is_me = (msg["speaker"] == "me")
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
        bubble_h = text_height + BUBBLE_PADDING * 1.5 # Extra padding at bottom

        # Ensure min size
        bubble_w = max(bubble_w, 80)
        bubble_h = max(bubble_h, 80)

        # Position
        if is_me:
            # Right side
            avatar_x = int(WIDTH - AVATAR_MARGIN_SIDE - AVATAR_SIZE)
            avatar_y = int(current_y)

            # Draw Avatar
            img.paste(avatar_img, (avatar_x, avatar_y), avatar_img)

            # Bubble Position
            # Right edge of bubble should be: avatar_x - bubble_margin
            bubble_x = int(avatar_x - 20 - bubble_w)
            bubble_y = int(current_y)

            draw_bubble(draw, bubble_x, bubble_y, bubble_w, bubble_h, GREEN_BUBBLE, is_right=True)

            # Draw Text
            text_x = bubble_x + BUBBLE_PADDING
            text_y = bubble_y + BUBBLE_PADDING - 5
            for i, line in enumerate(lines):
                draw.text((text_x, text_y + i * LINE_HEIGHT), line, font=font, fill=TEXT_COLOR)

        else:
            # Left side
            # No avatar (invisible, cropped)
            # So bubble starts from left margin
            bubble_x = 30 # Margin from left screen edge since avatar is cropped
            bubble_y = current_y

            draw_bubble(draw, bubble_x, bubble_y, bubble_w, bubble_h, WHITE_BUBBLE, is_right=False)

            # Draw Text
            text_x = bubble_x + BUBBLE_PADDING
            text_y = bubble_y + BUBBLE_PADDING - 5
            for i, line in enumerate(lines):
                draw.text((text_x, text_y + i * LINE_HEIGHT), line, font=font, fill=TEXT_COLOR)

            # Draw Red Box if highlight
            if is_highlight:
                # Hollow Red Rectangle
                # Add some padding around the bubble
                padding = 5
                box_x1 = bubble_x - padding
                box_y1 = bubble_y - padding
                box_x2 = bubble_x + bubble_w + padding
                box_y2 = bubble_y + bubble_h + padding

                # Draw thick red line
                draw.rectangle((box_x1, box_y1, box_x2, box_y2), outline=RED_BOX_COLOR, width=4)

        # Update Y
        current_y += max(bubble_h, AVATAR_SIZE) + 40

    # Crop final image
    final_img = img.crop((0, 0, WIDTH, current_y + 50))
    save_path = os.path.join(OUTPUT_DIR, "test_render_v1.png")
    final_img.save(save_path)
    print(f"Saved test render to {save_path}")

if __name__ == "__main__":
    render_screenshot()
