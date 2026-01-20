#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书财经爆款选题分析脚本
分析搜索结果并生成选题建议报告
"""

import json
from datetime import datetime
from collections import defaultdict
import re

def analyze_feeds(search_results):
    """分析搜索结果，提取爆款笔记"""
    all_feeds = []
    seen_ids = set()

    for keyword, data in search_results.items():
        if 'feeds' not in data:
            continue

        for feed in data['feeds']:
            # 跳过无效笔记
            if feed.get('modelType') == 'rec_query':
                continue

            note_card = feed.get('noteCard', {})
            interact_info = note_card.get('interactInfo', {})
            liked_count = int(interact_info.get('likedCount', 0))

            # 筛选条件：点赞数 >= 2000
            if liked_count >= 2000:
                feed_id = feed.get('id', '')

                # 去重
                if feed_id in seen_ids:
                    continue
                seen_ids.add(feed_id)

                all_feeds.append({
                    'id': feed_id,
                    'xsec_token': feed.get('xsecToken', ''),
                    'title': note_card.get('displayTitle', ''),
                    'user': note_card.get('user', {}).get('nickname', ''),
                    'liked_count': liked_count,
                    'collected_count': int(interact_info.get('collectedCount', 0)),
                    'comment_count': int(interact_info.get('commentCount', 0)),
                    'shared_count': int(interact_info.get('sharedCount', 0)),
                    'type': note_card.get('type', ''),
                    'keyword': keyword
                })

    # 按点赞数排序
    all_feeds.sort(key=lambda x: x['liked_count'], reverse=True)
    return all_feeds

def analyze_topic_trends(feeds):
    """分析选题趋势"""
    # 标题关键词统计
    title_keywords = defaultdict(int)

    # 选题类型分类
    topic_types = {
        '理财技巧': 0,
        '金融知识科普': 0,
        '基金投资': 0,
        '股票分析': 0,
        '存钱省钱': 0,
        '财经热点': 0,
        '投资心态': 0,
        '其他': 0
    }

    for feed in feeds:
        title = feed['title']
        user = feed['user']

        # 统计标题中的常见词
        words = re.findall(r'[\u4e00-\u9fa5]{2,}', title)
        for word in words:
            if len(word) >= 2 and word not in ['为什么', '怎么', '如何', '什么', '哪个']:
                title_keywords[word] += 1

        # 分类统计
        if any(kw in title for kw in ['基金', '止盈', '加仓', '定投']):
            topic_types['基金投资'] += 1
        elif any(kw in title for kw in ['股票', 'A股', '涨停', '跌']):
            topic_types['股票分析'] += 1
        elif any(kw in title for kw in ['存钱', '省钱', '攒钱', '理财']):
            topic_types['存钱省钱'] += 1
        elif any(kw in title for kw in ['金融', '财经', '经济', '市场']):
            topic_types['财经热点'] += 1
        elif any(kw in title for kw in ['投资', '赚钱', '收益']):
            topic_types['理财技巧'] += 1
        elif any(kw in title for kw in ['知识', '了解', '科普', '看懂']):
            topic_types['金融知识科普'] += 1
        elif any(kw in title for kw in ['心态', '韭菜', '风险', '散户']):
            topic_types['投资心态'] += 1
        else:
            topic_types['其他'] += 1

    # 获取TOP关键词
    top_keywords = sorted(title_keywords.items(), key=lambda x: x[1], reverse=True)[:30]

    return {
        'topic_types': dict(topic_types),
        'top_keywords': top_keywords
    }

def generate_topic_suggestions(feeds, analysis):
    """生成选题建议"""
    suggestions = []

    # 基于爆款标题规律生成建议
    suggestions.append({
        'title': '🎯 基金止盈实操：3种方法让你不踏空不被套',
        'topic_type': '基金投资',
        'target_audience': '基金投资者',
        'core_value': '解决基金止盈难题',
        'content_points': [
            '分批止盈法（20%规则）',
            '目标收益率法',
            '估值止盈法',
            '实战案例分析'
        ],
        'recommended_titles': [
            '基金止盈技巧：每赚20%就卖掉四分之一',
            '基金公司不会说的加仓法，难怪我总当韭菜！',
            '小白买基金必看，打工人闲钱买基，躺赢法'
        ]
    })

    suggestions.append({
        'title': '💰 打工人100万存款理财实操分享',
        'topic_type': '理财技巧',
        'target_audience': '年轻打工族',
        'core_value': '普通人也能存到100万',
        'content_points': [
            '收入分配策略',
            '强制储蓄方法',
            '低风险理财工具',
            '复利的力量'
        ],
        'recommended_titles': [
            '打工人理财新思路，我竟然有100万存款！',
            '提升财商的一些心得',
            '年入50w+后的理财真心话'
        ]
    })

    suggestions.append({
        'title': '📊 2026年六大潜力科技赛道前瞻',
        'topic_type': '财经热点',
        'target_audience': '投资者',
        'core_value': '提前布局未来风口',
        'content_points': [
            'AI与算力',
            '新能源与储能',
            '半导体芯片',
            '商业航天',
            '生物医药',
            '新材料'
        ],
        'recommended_titles': [
            '2026年六大潜力科技方向',
            '震荡上行！精准预判！商业航天后的接力方向',
            '商业航天炒作已到尾声，散户别跟量化抢饭碗'
        ]
    })

    suggestions.append({
        'title': '📚 一文看懂MACD指标（附图解）',
        'topic_type': '金融知识科普',
        'target_audience': '投资新手',
        'core_value': '零基础学技术分析',
        'content_points': [
            'MACD基本原理',
            '金叉死叉图解',
            '背离现象',
            '实战应用技巧'
        ],
        'recommended_titles': [
            '一文看懂:什么是MACD',
            '一图了解什么是做空！',
            '基金小白入门指南！'
        ]
    })

    suggestions.append({
        'title': '🎭 存钱的心理学：为什么你总是存不下钱？',
        'topic_type': '存钱省钱',
        'target_audience': '月光族、年轻人',
        'core_value': '从心理层面解决存钱难题',
        'content_points': [
            '消费心理陷阱',
            '强制储蓄3法则',
            '365天存钱法',
            '52周存钱挑战'
        ],
        'recommended_titles': [
            '为什么孩子不爱存钱？',
            '一旦父母知道你存钱，就会变成你的生活费！',
            '低薪女生｜1月工资分配来啦'
        ]
    })

    suggestions.append({
        'title': '⚠️ 洗盘还是出货？教你3招识破主力套路',
        'topic_type': '股票分析',
        'target_audience': '股票投资者',
        'core_value': '看懂主力动向，避免被割韭菜',
        'content_points': [
            '成交量分析',
            '分时图特征',
            '板块联动',
            '实战案例拆解'
        ],
        'recommended_titles': [
            '洗盘还是出货？一文看懂主力套路',
            '股票涨停，看一个数据，你就知道该不该留',
            '我知道你很急但是先别急'
        ]
    })

    suggestions.append({
        'title': '🌟 年轻女性投资指南：如何开始第一笔投资',
        'topic_type': '投资心态',
        'target_audience': '年轻女性',
        'core_value': '女性理财启蒙',
        'content_points': [
            '投资第一步：风险评估',
            '适合女生的稳健投资品',
            '避坑指南',
            '心态调整'
        ],
        'recommended_titles': [
            '为什么希望更多的年轻女性能关注基金、股市',
            'i人稳稳的理财思路',
            '5年财女养成计划✅投资第一课❗️最重要的事'
        ]
    })

    return suggestions

def generate_report(feeds, analysis, suggestions):
    """生成分析报告"""
    total_likes = sum(f['liked_count'] for f in feeds)
    total_collects = sum(f['collected_count'] for f in feeds)
    total_comments = sum(f['comment_count'] for f in feeds)

    report = {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data_summary': {
            'total_keywords_searched': 10,
            'total_feeds_found': len(feeds),
            'total_likes': total_likes,
            'total_collects': total_collects,
            'total_comments': total_comments,
            'avg_likes': total_likes // len(feeds) if feeds else 0
        },
        'topic_analysis': analysis,
        'top_feeds': feeds[:30],  # TOP 30爆款笔记
        'suggestions': suggestions
    }

    return report

def format_markdown_report(report):
    """格式化为Markdown报告"""
    md = f"""# 小红书财经爆款选题分析报告

> 生成时间：{report['generated_at']}

## 📊 数据概览

- **搜索关键词数**：{report['data_summary']['total_keywords_searched']} 个
- **符合条件笔记数**：{report['data_summary']['total_feeds_found']} 篇（点赞≥2000）
- **总点赞数**：{report['data_summary']['total_likes']:,}
- **总收藏数**：{report['data_summary']['total_collects']:,}
- **总评论数**：{report['data_summary']['total_comments']:,}
- **平均点赞数**：{report['data_summary']['avg_likes']:,}

## 🔥 爆款笔记 TOP 20

"""

    for i, feed in enumerate(report['top_feeds'][:20], 1):
        md += f"""
### {i}. {feed['title']}

- **博主**：{feed['user']}
- **点赞**：{feed['liked_count']:,} | **收藏**：{feed['collected_count']:,} | **评论**：{feed['comment_count']:,}
- **类型**：{feed['type']}
- **来源关键词**：{feed['keyword']}

---

"""

    # 选题类型分布
    md += "## 📈 选题类型分布\n\n"
    topic_types = report['topic_analysis']['topic_types']
    for topic_type, count in sorted(topic_types.items(), key=lambda x: x[1], reverse=True):
        md += f"- **{topic_type}**：{count} 篇\n"

    # 高频关键词
    md += "\n## 🔑 高频关键词 TOP 20\n\n"
    for keyword, count in report['topic_analysis']['top_keywords'][:20]:
        md += f"{keyword}（{count}次）  "

    # 选题建议
    md += "\n\n## 💡 可直接使用的选题建议\n\n"
    for i, suggestion in enumerate(report['suggestions'], 1):
        md += f"""
### {i}. {suggestion['title']}

- **选题类型**：{suggestion['topic_type']}
- **目标人群**：{suggestion['target_audience']}
- **核心价值**：{suggestion['core_value']}

**内容要点**：
"""
        for point in suggestion['content_points']:
            md += f"- {point}\n"

        md += f"""
**参考标题**：
"""
        for title in suggestion['recommended_titles']:
            md += f"- {title}\n"

        md += "\n---\n"

    # 爆款规律总结
    md += """
## 📝 爆款规律总结

### 1. 选题规律

- **时效型选题**：结合当前热点（如商业航天、美联储降息、2026展望）
- **教程型选题**：步骤化教学，强调可操作性（止盈技巧、存钱方法）
- **情绪型选题**：引发共鸣（韭菜心态、存钱焦虑、打工人理财）
- **清单型选题**：数字汇总（38位大佬操作、六大科技方向）

### 2. 标题创作技巧

- **数字吸引**：使用具体数字（100万存款、20%止盈、六大方向）
- **疑问句式**：为什么、怎么、如何（为什么存不下钱？）
- **痛点直击**：戳中用户焦虑（韭菜、踏空、被套）
- **对比强烈**：震荡上行、洗盘vs出货
- **表情符号**：🎯💰📊🔥等增加视觉吸引力

### 3. 内容结构建议

- **开头**：用痛点或热点引入，快速抓住注意力
- **中间**：结构化呈现，使用列表、图表、步骤
- **结尾**：给出可执行建议或引发思考

### 4. 风险提示

⚠️ **注意**：
- 避免使用"稳赚""暴富"等夸大宣传语
- 投资类内容需添加风险提示
- 理财建议要适合普通用户，避免高风险操作

---

## 🎯 下一步行动

1. 根据上述选题建议，选择适合自己定位的方向
2. 结合自身专业优势，深挖细分领域
3. 保持内容更新频率，积累粉丝基础
4. 关注数据反馈，持续优化内容策略

---

*本报告由 xhs-topic-analyzer 自动生成*
"""

    return md

# 主程序
if __name__ == '__main__':
    print("开始分析小红书财经爆款选题喵～")

    # 这里会由主程序传入数据
    print("分析脚本已就绪！")
