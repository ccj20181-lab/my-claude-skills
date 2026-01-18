# -*- coding: utf-8 -*-
"""
推送小红书热点选题报告到微信 (V8.0 - 移除粉丝数据依赖)
专注财经赛道：3天内 + 2000赞以上
"""
import requests
import argparse
import os
import sys
import json
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


def format_number(num):
    """格式化数字"""
    try:
        num = int(num)
    except (ValueError, TypeError):
        num = 0
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
                "id": item.get('id', ''),
                "title": card.get("displayTitle", "") or "无标题",
                "author": card.get("user", {}).get("nickname", ""),
                "likes": card.get("interactInfo", {}).get("likedCount", 0),
                "url": f"https://www.xiaohongshu.com/explore/{item.get('id', '')}"
            }
            flat_data.append(flat_item)
        else:
            # 支持新格式（nickname）和旧格式（author）
            flat_item = {
                "id": item.get('id', ''),
                "title": item.get('title', '无标题'),
                "author": item.get('nickname') or item.get('author', ''),
                "likes": item.get('likedCount', 0) or item.get('likes', 0),
                "url": f"https://www.xiaohongshu.com/explore/{item.get('id', '')}"
            }
            flat_data.append(flat_item)

    return flat_data


def generate_content(data_file):
    """生成推送内容（移除粉丝数据依赖）"""
    raw_data = load_data(data_file)

    # 财经赛道爆款标准：2000赞以上
    min_likes = 2000
    hits = []

    for note in raw_data:
        likes = int(note.get('likes', 0))
        if likes >= min_likes:
            hits.append(note)

    # 按点赞排序
    hits = sorted(hits, key=lambda x: x['likes'], reverse=True)
    top5 = hits[:5]

    today = datetime.now().strftime("%Y-%m-%d")

    content = f"""## 💰 小红书财经爆款选题日报

**📅 {today}** | 筛选：点赞≥2000 | 时间：3天内

─────────────────────────────────────────

### 📊 TOP 5 热点选题

"""

    for i, note in enumerate(top5, 1):
        title = note['title']
        likes = format_number(note['likes'])
        author = note['author']
        url = note['url']

        content += f"**【第{i}名】** {title}\n"
        content += f"❤️ {likes}  |  @{author}\n"
        content += f"🔗 {url}\n\n"

    content += f"""
─────────────────────────────────────────

### 📈 选题分析

本期财经赛道TOP 5选题呈现三大特征：

1. **时效型选题** - 抓住时间节点和热点事件
2. **教程型选题** - 用具体数字+教程形式降低理解门槛
3. **情绪型选题** - 通过观点制造讨论点

**流量密码**：标题用具体数字 + 强动作词 + 目标人群标签

─────────────────────────────────────────

### 💡 选题建议

| 系列 | 建议方向 |
|:---|:---|
| 🎯 秒懂金融小知识 | 基础概念+具体案例，"X分钟看懂"框架 |
| 🎯 每天秒懂财经热点 | 时效性观点分析，结合热点事件 |
| 🎯 秒懂理财小技巧 | 可执行的行动清单，绑定特定人群 |

⚠️ **风险提示**
• 数据有时效性，过期内容参考价值降低
• 选题前请核实内容合规性

─────────────────────────────────────────

📊 本次共筛选出 {len(hits)} 条爆款笔记
"""

    return content


def cleanup_temp_files():
    """清理临时数据文件"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files_to_clean = ['data.json', 'fans.json']

    cleaned = []
    for filename in files_to_clean:
        filepath = os.path.join(base_dir, filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                cleaned.append(filename)
                print(f"[Cleanup] 已删除临时文件: {filename}")
            except Exception as e:
                print(f"[Warning] 删除 {filename} 失败: {e}")

    if cleaned:
        print(f"[Cleanup] 清理完成，共删除 {len(cleaned)} 个文件")
    else:
        print("[Cleanup] 没有需要清理的临时文件")


def push_to_wechat(token, content):
    """推送内容到微信"""
    today = datetime.now().strftime("%m-%d")
    title = f"💰 小红书财经猎手 {today}"

    url = 'http://www.pushplus.plus/send'
    data = {
        "token": token,
        "title": title,
        "content": content,
        "template": "markdown"
    }

    try:
        response = requests.post(url, json=data, timeout=30)
        res_json = response.json()
        if res_json.get("code") == 200:
            print("[Success] 推送成功！请检查手机。")
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
    parser.add_argument('--file', required=True, help='Data JSON file')
    parser.add_argument('--no-cleanup', action='store_true', help='不清理临时文件（调试用）')
    args = parser.parse_args()

    token = args.token
    if not token:
        config = load_config()
        token = config.get('wechat_push_token')

    if not token:
        print("Error: No token provided")
        sys.exit(1)

    content = generate_content(args.file)
    success = push_to_wechat(token, content)

    # 推送成功后清理临时文件（除非指定 --no-cleanup）
    if success and not args.no_cleanup:
        cleanup_temp_files()

    sys.exit(0 if success else 1)
