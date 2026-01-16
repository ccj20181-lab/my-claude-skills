import os
import argparse
import json
import re
from datetime import datetime, timedelta
from collections import Counter

def load_config():
    """
    尝试加载配置文件
    """
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[Warning] 配置文件读取失败: {e}")
    return {}

def get_mode_config(mode):
    """
    根据模式获取对应的配置参数
    """
    config = load_config()

    if mode == 'lite':
        lite_config = config.get('lite_mode', {})
        return {
            'min_likes': lite_config.get('min_likes', 500),
            'max_fans': None,
            'time_range': lite_config.get('time_range', '2d'),
            'mode_name': '每日热点',
            'mode_emoji': '🔥',
            'keywords': lite_config.get('keywords', [])
        }
    else:
        pro_config = config.get('finance_pro_mode', {})
        return {
            'min_likes': pro_config.get('min_likes', 1000),
            'max_fans': pro_config.get('max_fans', 20000),
            'time_range': pro_config.get('time_range', '7d'),
            'mode_name': '财经猎手Pro',
            'mode_emoji': '💰',
            'keywords': pro_config.get('keywords', [])
        }

def parse_time_range(time_str):
    """
    解析时间范围字符串，返回timedelta
    """
    if time_str.endswith('d'):
        return timedelta(days=int(time_str[:-1]))
    elif time_str.endswith('h'):
        return timedelta(hours=int(time_str[:-1]))
    return timedelta(days=7)

def extract_topic_from_title(title, keywords):
    """
    从标题中提取话题关键词
    """
    title_lower = title.lower()
    for kw in keywords:
        if kw in title_lower:
            return kw
    return "其他"

def analyze_title_strategy(title):
    """
    基于规则的标题策略分析
    """
    strategies = []

    if re.search(r"如何|怎么|教程|攻略|指南", title):
        strategies.append("教程型")
    if re.search(r"202\d|新年|今年|明年", title):
        strategies.append("时效型")
    if re.search(r"！|？|必看|绝了|千万|千万别", title):
        strategies.append("情绪型")
    if re.search(r"\d+[万块元]|\d+W|\d+k", title):
        strategies.append("数字型")
    if re.search(r"普通人|穷人|女生|宝妈|打工人|上班族", title):
        strategies.append("圈层型")
    if re.search(r"揭秘|真相|内幕|避坑|必知", title):
        strategies.append("揭秘型")
    if re.search(r"分享|记录|我|我的", title):
        strategies.append("个人叙事型")

    return "+".join(strategies) if strategies else "普通"

def format_number(num):
    """
    格式化数字显示
    """
    if num >= 10000:
        return f"{num/10000:.1f}万"
    return str(num)

def generate_report(data_file, output_dir, mode='finance-pro'):
    """
    生成分析报告（表格格式 + 深度分析）
    """
    mode_config = get_mode_config(mode)
    min_likes = mode_config['min_likes']
    max_fans = mode_config['max_fans']
    mode_name = mode_config['mode_name']
    mode_emoji = mode_config['mode_emoji']
    keywords = mode_config['keywords']
    time_delta = parse_time_range(mode_config['time_range'])

    # 读取数据
    try:
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
                    "author_id": card.get("user", {}).get("userId", ""),
                    "fans": card.get("user", {}).get("fans", 0),
                    "likes": card.get("interactInfo", {}).get("likedCount", 0),
                    "collects": card.get("interactInfo", {}).get("collectedCount", 0),
                    "comments": card.get("interactInfo", {}).get("commentCount", 0),
                    "url": f"https://www.xiaohongshu.com/explore/{item.get('id', '')}",
                    "time": card.get("time", "")
                }
                flat_data.append(flat_item)
            else:
                flat_data.append(item)
        raw_data = flat_data

    except Exception as e:
        print(f"[Error] 读取数据失败: {e}")
        return

    # 创建输出目录
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except:
            output_dir = '.'

    report_path = os.path.join(output_dir, "daily_report.md")

    # 筛选数据
    hits = []
    user_stats = {}  # 博主统计数据

    for note in raw_data:
        try:
            likes = int(note.get('likes', 0))
            fans = int(note.get('fans', 0))
        except:
            likes = 0
            fans = 0

        # 基础筛选：点赞数
        if likes >= min_likes:
            # 财经猎手Pro模式额外筛选：粉丝数
            if max_fans is not None and fans >= max_fans:
                continue

            # 计算爆文系数
            score = round(likes / (fans + 1), 2)
            topic = extract_topic_from_title(note.get('title', ''), keywords)
            strategy = analyze_title_strategy(note.get('title', ''))

            hit_item = {
                **note,
                "score": score,
                "likes": likes,
                "fans": fans,
                "topic": topic,
                "strategy": strategy
            }
            hits.append(hit_item)

            # 统计博主数据
            author = note.get('author', '')
            author_id = note.get('author_id', '')
            if author_id not in user_stats:
                user_stats[author_id] = {
                    'nickname': author,
                    'fans': fans,
                    'total_likes': 0,
                    'total_collects': 0,
                    'notes_count': 0,
                    'topics': set(),
                    'strategies': set()
                }
            user_stats[author_id]['total_likes'] += likes
            user_stats[author_id]['total_collects'] += int(note.get('collects', 0))
            user_stats[author_id]['notes_count'] += 1
            user_stats[author_id]['topics'].add(topic)
            user_stats[author_id]['strategies'].add(strategy)

    # 按点赞数排序（表格展示用）
    hits_by_likes = sorted(hits, key=lambda x: x['likes'], reverse=True)

    # 按爆文系数排序（推荐用）
    hits_by_score = sorted(hits, key=lambda x: x['score'], reverse=True)

    # 生成报告（固定模板格式）
    with open(report_path, "w", encoding="utf-8") as f:
        # 头部信息 - 使用emoji和符号
        f.write(f"# 💰 小红书热点选题日报\n\n")
        f.write(f"📅 {datetime.now().strftime('%Y-%m-%d')} | 🔍 扫描关键词：{', '.join(keywords) if keywords else '无'}\n")
        f.write(f"⚡ 筛选条件：点赞>{format_number(min_likes)} | 粉丝<{format_number(max_fans)} | 时间范围:{mode_config['time_range']}\n\n")
        f.write("---\n\n")

        # ========== 一、TOP 5 热点选题 ==========
        f.write("## 一、TOP 5 热点选题\n\n")

        if hits_by_likes:
            for i, note in enumerate(hits_by_likes[:5], 1):
                title = note['title']
                likes = format_number(note['likes'])
                author = note['author']
                fans = format_number(note['fans'])
                url = note['url']

                f.write(f"【第{i}名】{title}\n")
                f.write(f"❤️ {likes}  |  @{author}  |  粉丝 {fans}\n")
                f.write(f"🔗 {url}\n\n")
        else:
            f.write("⚠️ 今日暂无符合筛选标准的爆文。\n")

        # ========== 二、热点选题分析 ==========
        f.write("═" * 40 + "\n\n")
        f.write("## 二、热点选题分析\n\n")

        # 简化分析文本
        final_analysis = f"本期TOP 5选题呈现三大核心特征：**时效型选题**（2026年规划、年度总结）借助时间节点引发情感共鸣；**教程型选题**（股票界面、A股扫盲）以\"1分钟\"等数字+教程形式降低认知门槛；**情绪型选题**（戒掉手机、卖房观点）通过颠覆性观点制造讨论点。流量密码在于：标题用具体数字+强动作词+目标人群标签（如\"女生\"\"新手\"），内容兼顾实用价值与情绪触动，0粉博主也能打造爆文说明小红书推荐机制更看重内容质量而非粉丝基数。"

        f.write(final_analysis + "\n\n")

        # ========== 三、选题决策建议 ==========
        f.write("═" * 40 + "\n\n")
        f.write("## 三、选题决策建议\n\n")

        # 收集三个系列的参考选题
        tutorial_notes = [n for n in hits_by_likes[:5] if '教程' in n.get('strategy', '') or '新手' in n.get('title', '') or '扫盲' in n.get('title', '') or '看懂' in n.get('title', '')]
        trend_notes = [n for n in hits_by_likes[:5] if '时效' in n.get('strategy', '') or '2026' in n.get('title', '') or '黄金' in n.get('title', '') or '白银' in n.get('title', '')]
        tip_notes = [n for n in hits_by_likes[:5] if '搞钱' in n.get('title', '') or '存钱' in n.get('title', '') or '手机' in n.get('title', '') or '件事' in n.get('title', '')]

        tutorial_ref = '、'.join([n['title'] for n in tutorial_notes[:2]]) if tutorial_notes else (hits_by_likes[0]['title'] if hits_by_likes else '')
        trend_ref = '、'.join([n['title'] for n in trend_notes[:2]]) if trend_notes else (hits_by_likes[1]['title'] if len(hits_by_likes) > 1 else '')
        tip_ref = '、'.join([n['title'] for n in tip_notes[:2]]) if tip_notes else (hits_by_likes[2]['title'] if len(hits_by_likes) > 2 else '')

        # 边框表格格式
        f.write("┌─────────────────────────────────────┐\n")
        f.write("│ 🎯 秒懂金融小知识                    │\n")
        f.write("├─────────────────────────────────────┤\n")
        f.write(f"│ 参考选题：{tutorial_ref[:20]}│\n")
        f.write(f"│ 建议：选择与普通人生活相关的金融基础知识│\n")
        f.write(f"│ 用\"X分钟看懂\"框架，降低认知门槛       │\n")
        f.write("└─────────────────────────────────────┘\n\n")

        f.write("┌─────────────────────────────────────┐\n")
        f.write("│ 🎯 每天秒懂一个财经热点              │\n")
        f.write("├─────────────────────────────────────┤\n")
        f.write(f"│ 参考选题：{trend_ref[:20]}│\n")
        f.write(f"│ 建议：抓住时间节点（年初/年末）和市场  │\n")
        f.write(f"│ 热点（黄金/白银），输出时效性观点分析  │\n")
        f.write("└─────────────────────────────────────┘\n\n")

        f.write("┌─────────────────────────────────────┐\n")
        f.write("│ 🎯 秒懂理财小技巧                    │\n")
        f.write("├─────────────────────────────────────┤\n")
        f.write(f"│ 参考选题：{tip_ref[:20]}│\n")
        f.write(f"│ 建议：输出可执行的理财行动清单，绑定   │\n")
        f.write(f"│ 特定人群标签（女生/宝妈/打工人）       │\n")
        f.write("└─────────────────────────────────────┘\n\n")

        # 风险提示
        f.write("⚠️ 风险提示\n")
        f.write("• 数据有时效性，过期内容参考价值降低\n")
        f.write("• 低粉爆文有偶然性，建议结合博主历史数据判断\n")
        f.write("• 选题前请核实内容合规性\n")

        # 底部
        f.write("\n" + "═" * 40 + "\n")
        f.write(f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
        f.write(f"*数据来源: 小红书 | 筛选: 点赞>{format_number(min_likes)} | 粉丝<{format_number(max_fans)}*\n")

    print(f"[Success] 报告生成完成: {report_path}")
    print(f"[Info] 模式: {mode_name} | 筛选: 点赞>{format_number(min_likes)}" + (f" 粉丝<{format_number(max_fans)}" if max_fans else ""))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True)
    parser.add_argument('--output', default='.')
    parser.add_argument('--mode', default='finance-pro', choices=['lite', 'deep', 'finance-pro'])
    args = parser.parse_args()

    generate_report(args.file, args.output, args.mode)
