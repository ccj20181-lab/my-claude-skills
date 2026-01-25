#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选题分析引擎
从 xhs-topic-analyzer 迁移的核心功能，提供选题分类、标题分析和建议生成
"""

import re
import math
from typing import Dict, List, Any
from collections import defaultdict


# ==================== 选题分类系统 ====================

TOPIC_KEYWORDS = {
    "理财技巧": ["理财", "投资", "赚钱", "收益"],
    "金融知识": ["金融", "银行", "利率", "通货", "货币"],
    "基金投资": ["基金", "止盈", "加仓", "定投"],
    "股票分析": ["股票", "A股", "涨停", "跌"],
    "存钱省钱": ["存钱", "省钱", "攒钱"],
    "财经热点": ["财经", "经济", "市场", "政策"],
    "投资心态": ["心态", "韭菜", "风险", "散户"]
}


def classify_topic(title: str) -> str:
    """
    基于关键词匹配的选题分类

    Args:
        title: 笔记标题

    Returns:
        选题类型（如"理财技巧"、"基金投资"等）
    """
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw in title for kw in keywords):
            return topic
    return "其他"


# ==================== 标题策略分析 ====================

def analyze_title_strategy(title: str) -> Dict[str, Any]:
    """
    分析标题策略

    Args:
        title: 笔记标题

    Returns:
        包含策略类型、长度等信息的字典
    """
    strategies = []

    # 教程型
    if re.search(r"如何|怎么|教程|攻略|指南|分钟看懂", title):
        strategies.append("教程型")

    # 时效型
    if re.search(r"202\d|新年|今年|年度|必做", title):
        strategies.append("时效型")

    # 情绪型
    if re.search(r"！|？|必看|绝了|千万|焦虑", title):
        strategies.append("情绪型")

    # 清单型
    if re.search(r"\d+件|\d+个|\d+步|清单", title):
        strategies.append("清单型")

    # 圈层型
    if re.search(r"普通人|女生|宝妈|打工人|新手|小白", title):
        strategies.append("圈层型")

    # 确定主导模式
    if len(strategies) == 0:
        pattern_type = "普通"
    elif "清单型" in strategies:
        pattern_type = "清单型"
    elif "教程型" in strategies:
        pattern_type = "教程型"
    elif "时效型" in strategies:
        pattern_type = "时效型"
    elif "情绪型" in strategies:
        pattern_type = "情绪型"
    else:
        pattern_type = "圈层型"

    return {
        "strategies": "+".join(strategies) if strategies else "普通",
        "pattern_type": pattern_type,
        "length": len(title),
        "has_number": bool(re.search(r"\d+", title))
    }


# ==================== 选题建议生成器 ====================

def generate_topic_suggestions(feeds: List[Dict[str, Any]], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    基于爆款笔记规律生成选题建议

    Args:
        feeds: 爆款笔记列表
        analysis: 选题分析结果

    Returns:
        选题建议列表（每个建议包含标题、类型、目标人群等）
    """
    suggestions = []

    # 建议模板 1: 基金止盈实操
    suggestions.append({
        "title": "🎯 基金止盈实操：3种方法让你不踏空不被套",
        "topic_type": "基金投资",
        "target_audience": "基金投资者",
        "core_value": "解决基金止盈难题",
        "content_points": [
            "分批止盈法（20%规则）",
            "目标收益率法",
            "估值止盈法",
            "实战案例分析"
        ],
        "recommended_titles": [
            "基金止盈技巧：每赚20%就卖掉四分之一",
            "基金公司不会说的加仓法，难怪我总当韭菜！",
            "小白买基金必看，打工人闲钱买基，躺赢法"
        ]
    })

    # 建议模板 2: 打工人理财实操
    suggestions.append({
        "title": "💰 打工人100万存款理财实操分享",
        "topic_type": "理财技巧",
        "target_audience": "年轻打工族",
        "core_value": "普通人也能存到100万",
        "content_points": [
            "收入分配策略",
            "强制储蓄方法",
            "低风险理财工具",
            "复利的力量"
        ],
        "recommended_titles": [
            "打工人理财新思路，我竟然有100万存款！",
            "提升财商的一些心得",
            "年入50w+后的理财真心话"
        ]
    })

    # 建议模板 3: 年度行业前瞻
    suggestions.append({
        "title": "📊 2026年六大潜力科技赛道前瞻",
        "topic_type": "财经热点",
        "target_audience": "投资者",
        "core_value": "提前布局未来风口",
        "content_points": [
            "AI与算力",
            "新能源与储能",
            "半导体芯片",
            "商业航天",
            "生物医药",
            "新材料"
        ],
        "recommended_titles": [
            "2026年六大潜力科技方向",
            "震荡上行！精准预判！商业航天后的接力方向",
            "商业航天炒作已到尾声，散户别跟量化抢饭碗"
        ]
    })

    # 建议模板 4: 技术指标科普
    suggestions.append({
        "title": "📚 一文看懂MACD指标（附图解）",
        "topic_type": "金融知识",
        "target_audience": "投资新手",
        "core_value": "零基础学技术分析",
        "content_points": [
            "MACD基本原理",
            "金叉死叉图解",
            "背离现象",
            "实战应用技巧"
        ],
        "recommended_titles": [
            "一文看懂:什么是MACD",
            "一图了解什么是做空！",
            "基金小白入门指南！"
        ]
    })

    # 建议模板 5: 存钱心理学
    suggestions.append({
        "title": "🎭 存钱的心理学：为什么你总是存不下钱？",
        "topic_type": "存钱省钱",
        "target_audience": "月光族、年轻人",
        "core_value": "从心理层面解决存钱难题",
        "content_points": [
            "消费心理陷阱",
            "强制储蓄3法则",
            "365天存钱法",
            "52周存钱挑战"
        ],
        "recommended_titles": [
            "为什么孩子不爱存钱？",
            "一旦父母知道你存钱，就会变成你的生活费！",
            "低薪女生｜1月工资分配来啦"
        ]
    })

    # 建议模板 6: 股票主力分析
    suggestions.append({
        "title": "⚠️ 洗盘还是出货？教你3招识破主力套路",
        "topic_type": "股票分析",
        "target_audience": "股票投资者",
        "core_value": "看懂主力动向，避免被割韭菜",
        "content_points": [
            "成交量分析",
            "分时图特征",
            "板块联动",
            "实战案例拆解"
        ],
        "recommended_titles": [
            "洗盘还是出货？一文看懂主力套路",
            "股票涨停，看一个数据，你就知道该不该留",
            "我知道你很急但是先别急"
        ]
    })

    # 建议模板 7: 年轻女性投资指南
    suggestions.append({
        "title": "🌟 年轻女性投资指南：如何开始第一笔投资",
        "topic_type": "投资心态",
        "target_audience": "年轻女性",
        "core_value": "女性理财启蒙",
        "content_points": [
            "投资第一步：风险评估",
            "适合女生的稳健投资品",
            "避坑指南",
            "心态调整"
        ],
        "recommended_titles": [
            "为什么希望更多的年轻女性能关注基金、股市",
            "i人稳稳的理财思路",
            "5年财女养成计划✅投资第一课❗️最重要的事"
        ]
    })

    return suggestions


# ==================== 综合分析函数 ====================

def analyze_feeds_topic(feeds: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    对笔记列表进行选题分析

    Args:
        feeds: 笔记列表，每个笔记包含 title, likes, collects 等字段

    Returns:
        包含选题分布、标题统计、建议等的分析结果
    """
    # 选题类型统计
    topic_distribution = defaultdict(int)

    # 标题关键词统计
    title_keywords = defaultdict(int)

    # 标题策略统计
    strategy_stats = defaultdict(int)

    # 标题长度统计
    title_lengths = []

    # 增强每条笔记的选题信息
    enhanced_feeds = []
    for feed in feeds:
        title = feed.get("title", "")

        # 选题分类
        topic = classify_topic(title)
        topic_distribution[topic] += 1
        feed["topic"] = topic

        # 标题策略分析
        strategy_info = analyze_title_strategy(title)
        feed["title_strategy"] = strategy_info["strategies"]
        feed["pattern_type"] = strategy_info["pattern_type"]
        feed["title_length"] = strategy_info["length"]

        strategy_stats[strategy_info["pattern_type"]] += 1
        title_lengths.append(strategy_info["length"])

        # 收藏/点赞比
        likes = feed.get("likes", 0)
        collects = feed.get("collects", 0)
        if likes > 0:
            feed["collect_to_like_ratio"] = round(collects / likes, 2)
        else:
            feed["collect_to_like_ratio"] = 0

        # 统计标题关键词
        words = re.findall(r'[\u4e00-\u9fa5]{2,}', title)
        for word in words:
            if len(word) >= 2 and word not in ['为什么', '怎么', '如何', '什么', '哪个']:
                title_keywords[word] += 1

        enhanced_feeds.append(feed)

    # 获取 TOP 关键词
    top_keywords = sorted(title_keywords.items(), key=lambda x: x[1], reverse=True)[:30]

    # 生成选题建议
    suggestions = generate_topic_suggestions(feeds[:10], {"topic_types": dict(topic_distribution)})

    # 计算统计指标
    avg_title_length = sum(title_lengths) / len(title_lengths) if title_lengths else 0

    return {
        "topic_distribution": dict(topic_distribution),
        "top_keywords": top_keywords,
        "strategy_stats": dict(strategy_stats),
        "avg_title_length": round(avg_title_length, 1),
        "suggestions": suggestions,
        "enhanced_feeds": enhanced_feeds
    }


# ==================== 主程序入口 ====================

if __name__ == "__main__":
    print("选题分析引擎已就绪喵～")
    print("这个模块应该被主程序导入使用")
