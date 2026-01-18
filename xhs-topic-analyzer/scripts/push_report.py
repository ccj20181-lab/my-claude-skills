# -*- coding: utf-8 -*-
"""
推送小红书热点选题报告到微信 (V8.1 - 深度选题分析)
专注财经赛道：3天内 + 2000赞以上
"""
import requests
import argparse
import os
import sys
import json
from datetime import datetime
from collections import Counter


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
                "collects": card.get("interactInfo", {}).get("collectedCount", 0),
                "comments": card.get("interactInfo", {}).get("commentCount", 0),
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
                "collects": item.get('collectedCount', 0),
                "comments": item.get('commentCount', 0),
                "url": f"https://www.xiaohongshu.com/explore/{item.get('id', '')}"
            }
            flat_data.append(flat_item)

    return flat_data


def analyze_topics(notes):
    """深度分析选题类型和特征"""

    # 关键词分类
    topic_keywords = {
        "理财技巧": ["存钱", "攒钱", "理财", "财富", "资产", "收益"],
        "金融知识": ["金融", "银行", "利率", "通货", "货币", "经济"],
        "投资教程": ["股票", "基金", "投资", "买入", "卖出", "持仓", "A股"],
        "财经热点": ["政策", "美国", "中国", "市场", "新闻", "分析", "观点"],
        "理财心态": ["心安", "底气", "焦虑", "稳定", "长期", "规划"],
        "生活理财": ["女生", "打工人", "年轻人", "新手", "小白", "入门"],
    }

    topic_counts = {topic: 0 for topic in topic_keywords.keys()}
    topic_examples = {topic: [] for topic in topic_keywords.keys()}

    for note in notes:
        title = note['title'].lower()
        matched = False
        for topic, keywords in topic_keywords.items():
            if any(kw in title for kw in keywords):
                topic_counts[topic] += 1
                if len(topic_examples[topic]) < 3:  # 每个类型最多保存3个例子
                    topic_examples[topic].append({
                        'title': note['title'],
                        'likes': note['likes']
                    })
                matched = True
                break

    # 标题长度分析
    title_lengths = [len(note['title']) for note in notes]
    avg_length = sum(title_lengths) / len(title_lengths) if title_lengths else 0

    # 互动率分析
    engagement_rates = []
    for note in notes:
        if note['likes'] > 0:
            engagement = (note['comments'] + note['collects']) / note['likes']
            engagement_rates.append(engagement)

    avg_engagement = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0

    return {
        'topic_distribution': topic_counts,
        'topic_examples': topic_examples,
        'avg_title_length': avg_length,
        'avg_engagement_rate': avg_engagement
    }


def generate_content(data_file):
    """生成推送内容（V8.1 - 深度分析版）"""
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

    # 深度分析
    analysis = analyze_topics(hits)

    today = datetime.now().strftime("%Y-%m-%d")

    # ========== 开始构建报告 ==========
    content = f"""## 💰 小红书财经爆款选题日报

**📅 {today}** | 筛选：点赞≥2000 | 时间：3天内 | 共 {len(hits)} 条

─────────────────────────────────────────

### 📊 TOP 10 热点选题

"""

    # TOP 10 笔记
    top10 = hits[:10]
    for i, note in enumerate(top10, 1):
        title = note['title']
        likes = format_number(note['likes'])
        collects = format_number(note['collects'])
        comments = format_number(note['comments'])
        author = note['author']
        url = note['url']

        content += f"**【第{i}名】** {title}\n"
        content += f"❤️ {likes}  |  ⭐ {collects}  |  💬 {comments}  |  @{author}\n"
        content += f"🔗 {url}\n\n"

    # ========== 选题分布分析 ==========
    content += """
─────────────────────────────────────────

### 📈 选题分布分析

"""

    sorted_topics = sorted(analysis['topic_distribution'].items(),
                          key=lambda x: x[1], reverse=True)

    for topic, count in sorted_topics:
        if count > 0:
            percentage = (count / len(hits)) * 100
            content += f"**{topic}**: {count}条 ({percentage:.1f}%)\n"
            # 展示该类型的代表性笔记
            if analysis['topic_examples'][topic]:
                example = analysis['topic_examples'][topic][0]
                content += f"  └ 代表：「{example['title']}」({format_number(example['likes'])}赞)\n"
            content += "\n"

    # ========== 深度选题洞察 ==========
    content += f"""
─────────────────────────────────────────

### 🔍 深度选题洞察

#### 📝 标题特征分析
- **平均标题长度**: {analysis['avg_title_length']:.0f} 字
- **最佳长度区间**: 15-25字（易读性与信息量平衡）
- **标题公式**: 数字+动作词+目标人群+价值点

#### 💬 互动数据洞察
- **平均互动率**: {analysis['avg_engagement_rate']:.2%}
- **高互动特征**: 实用性强、可操作性高的内容互动率更高
- **收藏/点赞比**: 收藏率高的内容往往是工具型、清单型选题

#### 🎯 爆款选题规律

**1. 时效型选题** （抓住时间节点）
- 特征：结合当下热点、节日、年度规划
- 关键词："2026"、"新年"、"年度计划"
- 流量密码：时间紧迫感 + 情感共鸣

**2. 教程型选题** （降低认知门槛）
- 特征：具体数字 + 步骤化教程
- 关键词："X分钟看懂"、"X步教你"、"零基础"
- 流量密码：简单易懂 + 即学即用

**3. 情绪型选题** （制造讨论点）
- 特征：观点鲜明、引发共鸣或争议
- 关键词："底气"、"心安"、"焦虑"
- 流量密码：情感共鸣 + 价值认同

**4. 清单型选题** （提供行动指南）
- 特征：可执行的具体建议清单
- 关键词："X件事"、"X个方法"、"必做清单"
- 流量密码：具体可操作 + 人群标签

─────────────────────────────────────────

### 💡 选题建议（可直接使用）

#### 🎯 秒懂金融小知识系列

1. **"1分钟看懂银行利率陷阱，存钱前必看"**
   - 切入点：用具体案例对比不同存款方式的收益差异
   - 目标人群：理财小白、存款新手
   - 内容要点：3-4个常见误区 + 正确做法

2. **"A股代码背后的秘密，新手必知的5个规则"**
   - 切入点：代码数字含义、板块分类、交易规则
   - 目标人群：股市新手、想入门的观望者
   - 内容要点：用表格或图示展示，简单易记

3. **"基金定投的黄金法则：3个时间点+2个止盈策略"**
   - 切入点：具体的定投时机选择和退出策略
   - 目标人群：基金定投新手
   - 内容要点：用实际数据说明，可复制性强

#### 🎯 每天秒懂财经热点系列

1. **"美联储降息对你钱包的3个直接影响"**
   - 切入点：宏观政策与个人理财的连接
   - 目标人群：关注财经但不懂宏观的普通人
   - 内容要点：房贷、存款、汇率3个维度

2. **"2026年这3个理财方向值得关注"**
   - 切入点：年度规划 + 趋势预判
   - 目标人群：想做年度理财规划的人
   - 内容要点：结合政策、市场、个人需求

3. **"通货膨胀下，普通人如何保护资产？"**
   - 切入点：当下痛点 + 实用建议
   - 目标人群：担心财富缩水的中等收入群体
   - 内容要点：3-5个具体可行的方法

#### 🎯 秒懂理财小技巧系列

1. **"月薪5000的存钱法：6个月存下2万"**
   - 切入点：具体收入 + 可实现的目标
   - 目标人群：打工人、低收入想存钱的人
   - 内容要点：预算分配 + 记账技巧 + 节流方法

2. **"女生理财必做的8件事，30岁前财务自由"**
   - 切入点：性别标签 + 年龄节点 + 诱人目标
   - 目标人群：20-30岁女性
   - 内容要点：从基础到进阶的理财清单

3. **"打工人副业理财两不误：时间管理+钱生钱"**
   - 切入点：双重焦虑（时间+金钱）的解决方案
   - 目标人群：想开副业的上班族
   - 内容要点：时间分配 + 理财规划 + 风险控制

─────────────────────────────────────────

### ⚠️ 内容创作要点

**标题撰写技巧**：
1. 使用具体数字（"3个"、"5000元"、"30天"）
2. 明确目标人群（"女生"、"新手"、"打工人"）
3. 突出价值点（"必看"、"必做"、"黄金法则"）
4. 制造紧迫感（"年前"、"2026"、"别错过"）

**内容结构建议**：
1. 开头：痛点引入或案例故事（50字内）
2. 中间：3-5个要点，用小标题分段
3. 结尾：总结 + 行动呼吁
4. 配图：清晰的图表、对比图、步骤图

**风险提示**：
• 避免承诺具体收益率（合规风险）
• 数据引用需标注来源
• 涉及股票、基金需加免责声明
• 时效性内容注明时间范围

─────────────────────────────────────────

### 📋 完整爆款笔记列表 ({len(hits)}条)

"""

    # 列出所有符合条件的笔记
    for i, note in enumerate(hits, 1):
        title = note['title']
        likes = format_number(note['likes'])
        author = note['author']
        url = note['url']

        content += f"{i}. **{title}** ({likes}赞) - @{author}\n"
        content += f"   {url}\n\n"

    content += f"""
─────────────────────────────────────────

📊 本次共筛选出 **{len(hits)} 条**爆款笔记
📅 数据时间：{today}
⏰ 抓取时间：{datetime.now().strftime("%H:%M:%S")}
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
