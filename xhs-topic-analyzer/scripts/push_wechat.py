# -*- coding: utf-8 -*-
import requests
import argparse
import os
import sys
import json
import re
from datetime import datetime

def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[Warning] Config load failed: {e}")
    return {}

def get_note_url(note_id):
    """生成小红书笔记链接"""
    return f"https://www.xiaohongshu.com/explore/{note_id}"

def detect_mode_from_report(report_file):
    """从报告中检测模式"""
    if not os.path.exists(report_file):
        return 'finance-pro', '财经猎手Pro'

    with open(report_file, 'r', encoding='utf-8') as f:
        first_line = f.readline()

    if '每日热点' in first_line:
        return 'lite', '每日热点'
    elif '财经猎手Pro' in first_line or '财经猎手' in first_line:
        return 'finance-pro', '财经猎手Pro'
    else:
        return 'finance-pro', '财经热点'

def generate_content_with_links(summary_file):
    """生成带链接的内容"""
    if not os.path.exists(summary_file):
        return None

    with open(summary_file, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.strip().split('\n')
    clean_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        # 跳过表格
        if '|' in line and not line.startswith('#'):
            continue
        # 清理markdown
        line = line.replace('**', '')
        if line and not line.startswith('---'):
            clean_lines.append(line)

    return '\n'.join(clean_lines)

def push_to_wechat(token, summary_file, mode='finance-pro'):
    """推送内容到微信"""
    if not os.path.exists(summary_file):
        print(f"Error: File not found {summary_file}")
        return

    content = generate_content_with_links(summary_file)
    if not content:
        print("Error: Failed to generate content")
        return

    today = datetime.now().strftime("%m-%d")

    # 根据模式生成不同的标题
    if mode == 'lite':
        title = f"🔥 小红书每日热点 {today}"
    else:
        title = f"💰 小红书财经猎手 {today}"

    url = 'http://www.pushplus.plus/send'
    data = {
        "token": token,
        "title": title,
        "content": content,
        "template": "markdown"
    }

    try:
        response = requests.post(url, json=data, timeout=10)
        res_json = response.json()
        if res_json.get("code") == 200:
            print("[Success] 微信推送成功！请检查手机。")
        else:
            print(f"[Failed] {res_json.get('msg')}")
    except Exception as e:
        print(f"[Error] {e}")

def push_with_note_links(notes_data, mode='finance-pro'):
    """推送带笔记链接的内容"""
    today = datetime.now().strftime("%m-%d")

    if mode == 'lite':
        title = f"🔥 小红书每日热点 {today}"
    else:
        title = f"💰 小红书财经猎手 {today}"

    # 构建内容
    content = f"""## 秒懂金融 · {"每日热点" if mode == 'lite' else "财经猎手"} {today}

**抓取关键词**: 理财/基金/股票/黄金 | **共{len(notes_data)}篇热门笔记**

### TOP5爆款 (可点击查看原文)

"""

    for i, note in enumerate(notes_data[:5], 1):
        note_id = note.get('id', '')
        url = get_note_url(note_id)
        note_title = note.get('displayTitle', '无标题')[:30]
        nickname = note.get('nickname', '未知')
        likes = note.get('likedCount', 0)
        collects = note.get('collectedCount', 0)

        content += f"{i}. **{note_title}** - {nickname}\n"
        content += f"   [查看笔记]({url})\n"
        content += f"   (点赞{likes:,} 收藏{collects:,})\n\n"

    content += """### 选题风向标
- 关注时效性热点，结合当前市场行情
- 拆解高赞爆文的标题策略和内容结构
- 寻找低粉高赞的潜力账号学习借鉴

---
**秒懂金融 · 热点追踪**"""

    url = 'http://www.pushplus.plus/send'
    data = {
        "token": "a6443f3a5d0f4b11a42c281f831b5c15",
        "title": title,
        "content": content,
        "template": "markdown"
    }

    try:
        response = requests.post(url, json=data, timeout=10)
        res_json = response.json()
        if res_json.get("code") == 200:
            print("[Success] 推送成功！")
            return True
        else:
            print(f"[Failed] {res_json.get('msg')}")
            return False
    except Exception as e:
        print(f"[Error] {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', help='PushPlus Token')
    parser.add_argument('--file', required=True, help='Summary file path')
    parser.add_argument('--mode', default='auto', choices=['lite', 'finance-pro', 'auto'],
                        help='推送模式，auto表示自动检测')
    args = parser.parse_args()

    token = args.token
    if not token:
        config = load_config()
        token = config.get('wechat_push_token')

    if not token:
        print("Error: No token provided")
        sys.exit(1)

    # 检测模式
    mode = args.mode
    if mode == 'auto':
        mode, mode_name = detect_mode_from_report(args.file)
        print(f"[Info] 自动检测到模式: {mode_name}")

    push_to_wechat(token, args.file, mode)
