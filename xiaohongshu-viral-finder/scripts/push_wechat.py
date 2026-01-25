#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信推送脚本
集成 PushPlus API，推送选题分析简报到微信
"""

import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional


# ==================== PushPlus 推送 ====================

def push_to_wechat(token: str, title: str, content: str, template: str = "markdown") -> Optional[Dict[str, Any]]:
    """
    推送消息到微信

    Args:
        token: PushPlus Token
        title: 消息标题
        content: 消息内容（支持 Markdown）
        template: 模板类型（html 或 markdown）

    Returns:
        API 响应结果，失败返回 None
    """
    url = "http://www.pushplus.plus/send"

    data = {
        "token": token,
        "title": title,
        "content": content,
        "template": template
    }

    try:
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print("[WARN] PushPlus 请求超时")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[WARN] PushPlus 推送失败: {e}")
        return None
    except Exception as e:
        print(f"[WARN] PushPlus 未知错误: {e}")
        return None


# ==================== 生成推送内容 ====================

def generate_push_content(feeds: List[Dict[str, Any]], analysis: Dict[str, Any]) -> str:
    """
    生成推送内容（Markdown 格式）

    Args:
        feeds: 笔记列表
        analysis: 分析结果

    Returns:
        Markdown 格式的推送内容
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_notes = len(feeds)

    # TOP 5 爆款笔记
    top5 = feeds[:5]

    # 选题分布
    topic_dist = analysis.get("topic_distribution", {})
    top_topics = sorted(topic_dist.items(), key=lambda x: x[1], reverse=True)[:5]

    # 标题策略
    strategy_stats = analysis.get("strategy_stats", {})

    # 选题建议（取前3个）
    suggestions = analysis.get("suggestions", [])[:3]

    md = f"""# 📊 小红书财经爆文分析报告

**生成时间**: {timestamp}
**发现爆文**: {total_notes} 条

---

## 🔥 TOP 5 爆款笔记

"""

    for i, feed in enumerate(top5, 1):
        title = feed.get("title", "")
        likes = feed.get("likes", 0)
        collects = feed.get("collects", 0)
        comments = feed.get("comments", 0)
        topic = feed.get("topic", "")
        note_url = f"https://www.xiaohongshu.com/explore/{feed.get('id', '')}"

        md += f"""
### {i}. {title}

- **选题类型**: {topic}
- **互动数据**: 👍{likes:,}  ⭐{collects:,}  💬{comments:,}
- **笔记链接**: [查看详情]({note_url})

---

"""

    # 选题分布
    md += "## 📈 选题分布统计\n\n"

    for topic, count in top_topics:
        percentage = count / total_notes * 100 if total_notes > 0 else 0
        md += f"- **{topic}**: {count} 篇 ({percentage:.1f}%)\n"

    # 标题策略
    md += "\n## 📝 标题策略分析\n\n"

    for strategy, count in sorted(strategy_stats.items(), key=lambda x: x[1], reverse=True):
        md += f"- **{strategy}**: {count} 篇\n"

    # 选题建议
    md += "\n## 💡 精选选题建议\n\n"

    for i, suggestion in enumerate(suggestions, 1):
        md += f"""
### {i}. {suggestion['title']}

- **选题类型**: {suggestion['topic_type']}
- **目标人群**: {suggestion['target_audience']}
- **核心价值**: {suggestion['core_value']}

**内容要点**:
"""
        for point in suggestion.get("content_points", []):
            md += f"- {point}\n"

        md += "\n**参考标题**:\n"
        for title in suggestion.get("recommended_titles", []):
            md += f"- {title}\n"

        md += "\n---\n"

    # 高频关键词
    top_keywords = analysis.get("top_keywords", [])[:15]
    if top_keywords:
        md += "## 🔑 高频关键词 TOP 15\n\n"
        keywords_str = "  ".join([f"{kw}({count})" for kw, count in top_keywords])
        md += keywords_str + "\n"

    md += "\n---\n\n"
    md += "*完整数据已保存至 Excel 文件，请查看附件*"

    return md


def generate_summary_content(feeds: List[Dict[str, Any]], analysis: Dict[str, Any]) -> str:
    """
    生成简化版推送内容（用于快速通知）

    Args:
        feeds: 笔记列表
        analysis: 分析结果

    Returns:
        Markdown 格式的简化内容
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_notes = len(feeds)

    # TOP 3 爆款
    top3 = feeds[:3]

    # 选题分布 TOP 3
    topic_dist = analysis.get("topic_distribution", {})
    top_topics = sorted(topic_dist.items(), key=lambda x: x[1], reverse=True)[:3]

    md = f"""# 📊 小红书爆文日报

{timestamp} | 发现 {total_notes} 条高互动爆文

## 🔥 TOP 3 爆款

"""

    for i, feed in enumerate(top3, 1):
        title = feed.get("title", "")
        likes = feed.get("likes", 0)
        collects = feed.get("collects", 0)
        md += f"{i}. **{title}**\n   👍{likes:,}  ⭐{collects:,}\n\n"

    md += "## 📈 热门选题\n\n"
    for topic, count in top_topics:
        md += f"- {topic}: {count} 篇\n"

    md += "\n*完整报告已生成 Excel 文件*"

    return md


# ==================== 主程序入口 ====================

if __name__ == "__main__":
    print("微信推送脚本已就绪喵～")
    print("这个模块应该被主程序导入使用")
