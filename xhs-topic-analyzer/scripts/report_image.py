# -*- coding: utf-8 -*-
"""
生成图片格式的热点选题报告
微信推送专用 - 图片形式呈现表格
"""
import os
import json
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime


def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def get_mode_config(mode):
    """获取模式配置"""
    config = load_config()
    if mode == 'lite':
        cfg = config.get('lite_mode', {})
        return {
            'min_likes': cfg.get('min_likes', 500),
            'max_fans': None,
            'time_range': cfg.get('time_range', '2d'),
            'keywords': cfg.get('keywords', [])
        }
    else:
        cfg = config.get('finance_pro_mode', {})
        return {
            'min_likes': cfg.get('min_likes', 1000),
            'max_fans': cfg.get('max_fans', 20000),
            'time_range': cfg.get('time_range', '7d'),
            'keywords': cfg.get('keywords', [])
        }


def format_number(num):
    """格式化数字"""
    if num >= 10000:
        return f"{num/10000:.1f}万"
    return str(num)


def load_data(data_file):
    """加载数据"""
    with open(data_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    if isinstance(raw_data, dict) and "feeds" in raw_data:
        raw_data = raw_data["feeds"]

    flat_data = []
    for item in raw_data:
        if "noteCard" in item:
            card = item["noteCard"]
            flat_item = {
                "title": card.get("displayTitle", "") or "无标题",
                "author": card.get("user", {}).get("nickname", ""),
                "fans": card.get("user", {}).get("fans", 0),
                "likes": card.get("interactInfo", {}).get("likedCount", 0),
                "url": f"https://www.xiaohongshu.com/explore/{item.get('id', '')}"
            }
            flat_data.append(flat_item)
        else:
            flat_data.append(item)

    return flat_data


def wrap_text(draw, text, font, max_width):
    """文字换行处理"""
    if not text:
        return []
    words = text
    lines = []
    current_line = ""

    for char in words:
        test_line = current_line + char
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]
        if width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = char

    if current_line:
        lines.append(current_line)

    return lines if lines else [text]


def generate_image_report(data_file, output_path, mode='finance-pro'):
    """生成图片格式的报告"""

    mode_config = get_mode_config(mode)
    min_likes = mode_config['min_likes']
    max_fans = mode_config['max_fans']
    keywords = mode_config['keywords']
    time_range = mode_config['time_range']

    # 加载数据
    raw_data = load_data(data_file)

    # 筛选数据
    hits = []
    for note in raw_data:
        try:
            likes = int(note.get('likes', 0))
            fans = int(note.get('fans', 0))
        except:
            likes = 0
            fans = 0

        if likes >= min_likes:
            if max_fans is not None and fans >= max_fans:
                continue
            hits.append({
                **note,
                'likes': likes,
                'fans': fans
            })

    # 按点赞数排序
    hits_by_likes = sorted(hits, key=lambda x: x['likes'], reverse=True)
    top5 = hits_by_likes[:5]

    # 图片设置
    img_width = 600
    header_height = 120
    row_height = 80
    footer_height = 100
    table_height = header_height + row_height * len(top5) + footer_height

    # 背景色
    bg_color = (250, 250, 252)  # 浅灰蓝背景
    header_color = (255, 120, 80)  # 橙色标题栏
    row_even = (255, 255, 255)
    row_odd = (248, 248, 250)
    text_color = (50, 50, 50)
    link_color = (0, 122, 204)

    # 创建图片
    img = Image.new('RGB', (img_width, table_height), bg_color)
    draw = ImageDraw.Draw(img)

    # 尝试加载中文字体
    try:
        # Windows系统字体路径
        font_path = "C:/Windows/Fonts/msyh.ttc"
        title_font = ImageFont.truetype(font_path, 28)
        header_font = ImageFont.truetype(font_path, 18)
        cell_font = ImageFont.truetype(font_path, 14)
        small_font = ImageFont.truetype(font_path, 12)
    except:
        # 使用默认字体
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        cell_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # 绘制标题
    title_text = "💰 小红书热点选题日报"
    bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = bbox[2] - bbox[0]
    draw.text(((img_width - title_width) / 2, 20), title_text, font=title_font, fill=(40, 40, 40))

    # 绘制副标题
    sub_text = f"📅 {datetime.now().strftime('%Y-%m-%d')} | 🔍 {', '.join(keywords[:5])}..."
    bbox = draw.textbbox((0, 0), sub_text, font=cell_font)
    sub_width = bbox[2] - bbox[0]
    draw.text(((img_width - sub_width) / 2, 60), sub_text, font=cell_font, fill=(120, 120, 120))

    sub_text2 = f"⚡ 筛选：点赞>{format_number(min_likes)} | 粉丝<{format_number(max_fans)} | {time_range}"
    bbox = draw.textbbox((0, 0), sub_text2, font=cell_font)
    sub_width2 = bbox[2] - bbox[0]
    draw.text(((img_width - sub_width2) / 2, 85), sub_text2, font=cell_font, fill=(120, 120, 120))

    # 绘制分隔线
    draw.line([(20, 115), (img_width - 20, 115)], fill=(200, 200, 200), width=2)

    # 绘制表格头部
    y = header_height
    col_widths = [250, 60, 80, 80, 80]  # 标题、点赞、博主、粉丝、链接
    col_names = ["笔记标题", "点赞", "博主", "粉丝", "链接"]
    x_positions = [20]

    for w in col_widths[:-1]:
        x_positions.append(x_positions[-1] + w)

    # 表头背景
    draw.rectangle([(20, y), (img_width - 20, y + 40)], fill=header_color)

    # 表头文字
    for i, (x, name, w) in enumerate(zip(x_positions, col_names, col_widths)):
        bbox = draw.textbbox((0, 0), name, font=header_font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        draw.text((x + (w - text_w) / 2, y + (40 - text_h) / 2), name, font=header_font, fill=(255, 255, 255))

    y += 40

    # 绘制表格内容
    for row_idx, note in enumerate(top5):
        # 交替行颜色
        row_color = row_even if row_idx % 2 == 0 else row_odd
        draw.rectangle([(20, y), (img_width - 20, y + row_height)], fill=row_color)

        # 绘制行线
        draw.line([(20, y + row_height - 1), (img_width - 20, y + row_height - 1)], fill=(220, 220, 220), width=1)

        # 第1列：笔记标题
        title = note['title'][:18] + "..." if len(note['title']) > 18 else note['title']
        draw.text((x_positions[0] + 5, y + 25), title, font=cell_font, fill=text_color)

        # 第2列：点赞
        likes_text = format_number(note['likes'])
        bbox = draw.textbbox((0, 0), likes_text, font=cell_font)
        text_w = bbox[2] - bbox[0]
        draw.text((x_positions[1] + (col_widths[1] - text_w) / 2, y + 30), likes_text, font=cell_font, fill=text_color)

        # 第3列：博主
        author = "@" + note['author']
        author = author[:8] if len(author) > 8 else author
        draw.text((x_positions[2] + 5, y + 30), author, font=cell_font, fill=text_color)

        # 第4列：粉丝
        fans_text = format_number(note['fans'])
        bbox = draw.textbbox((0, 0), fans_text, font=cell_font)
        text_w = bbox[2] - bbox[0]
        draw.text((x_positions[3] + (col_widths[3] - text_w) / 2, y + 30), fans_text, font=cell_font, fill=text_color)

        # 第5列：链接
        link_text = "🔗 查看"
        bbox = draw.textbbox((0, 0), link_text, font=cell_font)
        text_w = bbox[2] - bbox[0]
        draw.text((x_positions[4] + (col_widths[4] - text_w) / 2, y + 30), link_text, font=cell_font, fill=link_color)

        y += row_height

    # 绘制底部分析
    y += 20
    draw.line([(20, y), (img_width - 20, y)], fill=(200, 200, 200), width=2)
    y += 15

    # 热点选题分析
    analysis_title = "📊 热点选题分析"
    draw.text((25, y), analysis_title, font=header_font, fill=(40, 40, 40))
    y += 30

    analysis_text = "本期TOP 5选题呈现时效型、教程型、情绪型三大特征。" \
                    "流量密码在于：标题用数字+动作词+目标人群标签，" \
                    "内容兼顾实用价值与情绪触动，0粉博主也能打造爆文。"
    lines = wrap_text(draw, analysis_text, cell_font, img_width - 60)
    for line in lines:
        draw.text((25, y), line, font=cell_font, fill=(80, 80, 80))
        y += 22

    # 选题决策建议
    y += 15
    draw.line([(20, y), (img_width - 20, y)], fill=(200, 200, 200), width=2)
    y += 15

    suggestion_title = "💡 选题决策建议"
    draw.text((25, y), suggestion_title, font=header_font, fill=(40, 40, 40))
    y += 30

    # 三个系列建议
    suggestions = [
        ("🎯 秒懂金融小知识", "选择与普通人生活相关的金融基础知识，用\"X分钟看懂\"框架"),
        ("🎯 每天秒懂一个财经热点", "抓住时间节点和热点（黄金/白银），输出时效性观点分析"),
        ("🎯 秒懂理财小技巧", "输出可执行的理财行动清单，绑定特定人群标签")
    ]

    for series_name, suggestion in suggestions:
        # 系列标题
        draw.text((25, y), series_name, font=cell_font, fill=(255, 120, 80))
        y += 22
        # 建议内容
        lines = wrap_text(draw, suggestion, cell_font, img_width - 60)
        for line in lines:
            draw.text((35, y), "• " + line, font=cell_font, fill=(80, 80, 80))
            y += 20
        y += 8

    # 底部时间
    y = table_height - 35
    footer_text = f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')} | 数据来源: 小红书"
    bbox = draw.textbbox((0, 0), footer_text, font=small_font)
    footer_width = bbox[2] - bbox[0]
    draw.text(((img_width - footer_width) / 2, y), footer_text, font=small_font, fill=(150, 150, 150))

    # 保存图片
    img.save(output_path, 'PNG', quality=95)
    print(f"[Success] 图片报告已生成: {output_path}")
    return output_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("用法: python report_image.py <data.json> <output.png> [--mode lite|finance-pro]")
        sys.exit(1)

    data_file = sys.argv[1]
    output_path = sys.argv[2]
    mode = 'finance-pro'
    if len(sys.argv) > 3 and sys.argv[3] == 'lite':
        mode = 'lite'

    generate_image_report(data_file, output_path, mode)
