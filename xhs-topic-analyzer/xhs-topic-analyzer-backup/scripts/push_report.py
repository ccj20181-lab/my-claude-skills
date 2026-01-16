# -*- coding: utf-8 -*-
"""
推送小红书热点选题报告到微信
支持图片查看 + 表格内容
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


def load_fans_data():
    """
    加载粉丝数据（仅作为备用，优先使用 data.json 自带的粉丝数）

    注意：小红书搜索 API 返回的数据已包含 fans 字段，
    fans.json 仅在需要补充或覆盖时使用
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fans_path = os.path.join(base_dir, 'fans.json')
    if os.path.exists(fans_path):
        try:
            with open(fans_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # fans.json 格式是 {userId: fans} 或 {"users": {userId: {fans: xxx}}}
                if isinstance(data, dict):
                    # 检查是否是 {"users": {...}} 格式
                    if 'users' in data:
                        users = data['users']
                        result = {uid: info.get('fans', 0) for uid, info in users.items()}
                        print(f"[Info] fans.json (users格式) 加载了 {len(result)} 条记录")
                        return result
                    # 否则是 {userId: fans} 格式
                    print(f"[Info] fans.json (简单格式) 加载了 {len(data)} 条记录")
                    return data
        except Exception as e:
            print(f"[Warning] fans.json 读取失败: {e}")
    else:
        print(f"[Info] fans.json 不存在，将使用 data.json 自带的粉丝数据")
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
                "author_id": card.get("user", {}).get("userId", ""),
                "fans": card.get("user", {}).get("fans", 0),
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
                "author_id": item.get('userId', ''),
                "fans": item.get('fans', 0),
                "likes": item.get('likedCount', 0) or item.get('likes', 0),
                "url": f"https://www.xiaohongshu.com/explore/{item.get('id', '')}"
            }
            flat_data.append(flat_item)

    return flat_data


def generate_content(data_file, mode='finance-pro'):
    """生成推送内容"""
    raw_data = load_data(data_file)

    # 加载fans.json中的粉丝数据（仅作为备用）
    fans_data = load_fans_data()

    # 根据 mode 选择筛选配置
    if mode == 'lite':
        mode_config = {'min_likes': 500, 'max_fans': 20000}
    else:
        mode_config = {'min_likes': 1000, 'max_fans': 20000}
    hits = []
    fans_source_stats = {'from_data': 0, 'from_fans_json': 0, 'missing': 0}

    for note in raw_data:
        likes = int(note.get('likes', 0))
        user_id = note.get('author_id', '')

        # 粉丝数据来源优先级：
        # 1. data.json 自带的 fans 字段（搜索 API 返回）
        # 2. fans.json 补充数据
        # 3. 默认 0
        fans = int(note.get('fans', 0))

        if fans > 0:
            fans_source_stats['from_data'] += 1
        elif user_id and user_id in fans_data:
            fans = fans_data[user_id]
            fans_source_stats['from_fans_json'] += 1
        else:
            fans_source_stats['missing'] += 1

        if likes >= mode_config['min_likes'] and fans < mode_config['max_fans']:
            note_copy = {'likes': likes, 'fans': fans, **note}
            hits.append(note_copy)

    # 打印粉丝数据来源统计
    print(f"[Info] 粉丝数据来源: data.json={fans_source_stats['from_data']}, "
          f"fans.json={fans_source_stats['from_fans_json']}, 缺失={fans_source_stats['missing']}")

    # 按点赞排序
    hits = sorted(hits, key=lambda x: x['likes'], reverse=True)
    top5 = hits[:5]

    today = datetime.now().strftime("%Y-%m-%d")

    content = f"""## 💰 小红书热点选题日报

**📅 {today}** | 筛选：点赞>1000 | 粉丝<2.0万

─────────────────────────────────────────

### 📊 TOP 5 热点选题

"""

    for i, note in enumerate(top5, 1):
        title = note['title']
        likes = format_number(note['likes'])
        author = note['author']
        fans = format_number(note['fans'])
        url = note['url']

        content += f"**【第{i}名】** {title}\n"
        content += f"❤️ {likes}  |  @{author}  |  粉丝 {fans}\n"
        content += f"🔗 {url}\n\n"

    content += """
─────────────────────────────────────────

### 📈 热点选题分析

本期TOP 5选题呈现三大核心特征：**时效型选题**（2026年规划）借助时间节点引发情感共鸣；**教程型选题**（股票界面、A股扫盲）以"1分钟"等数字+教程形式降低认知门槛；**情绪型选题**（戒掉手机、卖房观点）通过颠覆性观点制造讨论点。流量密码在于：标题用具体数字+强动作词+目标人群标签（如"女生""新手"），内容兼顾实用价值与情绪触动。

─────────────────────────────────────────

### 💡 选题决策建议

| 系列 | 参考选题 | 建议 |
|:---|:---|:---|
| 🎯 秒懂金融小知识 | A股代码扫盲、1分钟看懂股票界面 | 选择与普通人生活相关的金融基础知识，用"X分钟看懂"框架 |
| 🎯 每天秒懂一个财经热点 | 2026长期主义计划 | 抓住时间节点和热点，输出时效性观点分析 |
| 🎯 秒懂理财小技巧 | 女生戒掉手机去做这6件事 | 输出可执行的理财行动清单，绑定特定人群标签 |

⚠️ **风险提示**
• 数据有时效性，过期内容参考价值降低
• 低粉爆文有偶然性，建议结合博主历史数据判断
• 选题前请核实内容合规性

─────────────────────────────────────────
📁 图片报告: F:/选题抓取/{date}_FinancePro/daily_report.png
""".format(date=datetime.now().strftime("%Y%m%d"))

    return content


def push_to_wechat(token, content, mode='finance-pro'):
    """推送内容到微信"""
    today = datetime.now().strftime("%m-%d")

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
    parser.add_argument('--mode', default='finance-pro', choices=['lite', 'finance-pro'])
    args = parser.parse_args()

    token = args.token
    if not token:
        config = load_config()
        token = config.get('wechat_push_token')

    if not token:
        print("Error: No token provided")
        sys.exit(1)

    content = generate_content(args.file, args.mode)
    success = push_to_wechat(token, content, args.mode)
    sys.exit(0 if success else 1)
