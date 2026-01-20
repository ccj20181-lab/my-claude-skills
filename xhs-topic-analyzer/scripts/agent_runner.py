#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anthropic SDK + 智谱 AI 兼容端点 Agent Runner
通过 HTTP 直接调用 xiaohongshu-mcp 搜索爆款笔记
"""

import os
import sys
import json
import requests
from datetime import datetime
from anthropic import Anthropic


# MCP Server 配置
MCP_SERVER_URL = "http://localhost:18060/mcp"


def load_config():
    """加载配置文件"""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'config.json'
    )
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[Error] 加载配置文件失败: {e}")
        sys.exit(1)


def create_anthropic_client():
    """创建 Anthropic 客户端（使用智谱 AI 兼容端点）"""
    api_key = os.environ.get("ANTHROPIC_AUTH_TOKEN")
    base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://open.bigmodel.cn/api/anthropic")

    if not api_key:
        print("[Error] 缺少 ANTHROPIC_AUTH_TOKEN 环境变量")
        sys.exit(1)

    return Anthropic(
        api_key=api_key,
        base_url=base_url
    )


def call_mcp_tool(tool_name, arguments):
    """直接调用 MCP 工具 (HTTP JSON-RPC)"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }

    try:
        response = requests.post(MCP_SERVER_URL, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()

        if "result" in result:
            return result["result"]
        elif "error" in result:
            print(f"[Error] MCP 调用返回错误: {result['error']}")
            return None
        else:
            print(f"[Error] MCP 调用失败: {result}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"[Error] MCP Server 连接失败: {e}")
        print(f"[Info] 请确保 MCP Server 正在运行: {MCP_SERVER_URL}")
        return None


def search_feeds(keyword):
    """搜索小红书笔记"""
    print(f"[Info] 搜索关键词: {keyword}")

    result = call_mcp_tool("search_feeds", {
        "keyword": keyword,
        "filters": {
            "sort_by": "最多点赞",
            "publish_time": "一周内",
            "note_type": "不限"
        }
    })

    if not result:
        print(f"[Warning] 搜索 {keyword} 返回空结果")
        return []

    # 解析返回数据
    if isinstance(result, dict) and "content" in result:
        for item in result["content"]:
            if item.get("type") == "text":
                try:
                    data = json.loads(item.get("text", "{}"))
                    feeds = data.get("feeds", [])
                    print(f"  ✓ {keyword}: {len(feeds)} 条")
                    return feeds
                except json.JSONDecodeError as e:
                    print(f"[Warning] 解析搜索结果失败: {e}")
                    continue

    # 如果直接返回列表
    elif isinstance(result, list):
        print(f"  ✓ {keyword}: {len(result)} 条")
        return result

    print(f"[Warning] 搜索 {keyword} 未能解析结果")
    return []


def filter_explosive_feeds(all_feeds, min_likes):
    """筛选爆款笔记（点赞数 ≥ min_likes）"""
    filtered = []

    for feed in all_feeds:
        # 兼容不同的数据格式
        if "noteCard" in feed:
            note_card = feed.get("noteCard", {})
            likes = int(note_card.get("interactInfo", {}).get("likedCount", 0))
            collects = int(note_card.get("interactInfo", {}).get("collectedCount", 0))
            comments = int(note_card.get("interactInfo", {}).get("commentCount", 0))
            publish_time = note_card.get("time", "")
            user_info = note_card.get("user", {})
        else:
            likes = int(feed.get("likedCount", 0))
            collects = int(feed.get("collectedCount", 0))
            comments = int(feed.get("commentCount", 0))
            publish_time = feed.get("publishTime", "")
            user_info = {}

        # 筛选爆款
        if likes >= min_likes:
            filtered.append({
                "id": feed.get("id", ""),
                "title": feed.get("title", "") or feed.get("noteCard", {}).get("displayTitle", "无标题"),
                "nickname": feed.get("nickname", "") or user_info.get("nickname", "未知"),
                "likedCount": likes,
                "collectedCount": collects,
                "commentCount": comments,
                "publishTime": publish_time
            })

    return filtered


def main():
    """主函数"""
    print("=" * 60)
    print("Anthropic SDK + 智谱 AI - xhs-topic-analyzer")
    print("=" * 60)

    # 1. 创建 Anthropic 客户端
    print("[Step 1] 初始化 Anthropic 客户端...")
    client = create_anthropic_client()
    base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://open.bigmodel.cn/api/anthropic")
    print(f"  ✓ Base URL: {base_url}")

    # 2. 加载配置
    print("\n[Step 2] 加载配置文件...")
    config = load_config()
    keywords = config.get("keywords", [])
    min_likes = config.get("filters", {}).get("min_likes", 2000)

    print(f"  ✓ 已加载 {len(keywords)} 个搜索关键词")
    print(f"  ✓ 筛选条件: 点赞数 ≥ {min_likes}")

    # 3. 检查 MCP Server 连接
    print("\n[Step 3] 检查 MCP Server 连接...")
    try:
        response = requests.get(f"{MCP_SERVER_URL.replace('/mcp', '')}/", timeout=5)
        print(f"  ✓ MCP Server 运行正常")
    except requests.exceptions.RequestException:
        print(f"  ✗ 无法连接到 MCP Server: {MCP_SERVER_URL}")
        print(f"  [Info] 请确保 xiaohongshu-mcp 已启动")
        sys.exit(1)

    # 4. 搜索所有关键词
    print(f"\n[Step 4] 开始搜索 {len(keywords)} 个关键词...")
    all_feeds = []

    for i, keyword in enumerate(keywords, 1):
        print(f"\n[{i}/{len(keywords)}] 搜索: {keyword}")
        feeds = search_feeds(keyword)
        all_feeds.extend(feeds)

        # 添加延迟避免请求过快
        if i < len(keywords):
            import time
            time.sleep(1)

    if not all_feeds:
        print("\n[Error] 未搜索到任何笔记")
        print("[Info] 可能原因:")
        print("  1. 小红书 cookies 已过期")
        print("  2. 搜索关键词不合理")
        print("  3. IP 被限流")
        sys.exit(1)

    print(f"\n  ✓ 共搜索到 {len(all_feeds)} 条笔记")

    # 5. 筛选爆款
    print(f"\n[Step 5] 筛选爆款笔记 (点赞≥{min_likes})...")
    filtered = filter_explosive_feeds(all_feeds, min_likes)

    if not filtered:
        print(f"[Warning] 未找到点赞数 ≥ {min_likes} 的爆款笔记")
        print(f"[Info] 搜索到的最高点赞数: {max(f.get('likedCount', 0) for f in all_feeds)}")
        sys.exit(1)

    print(f"  ✓ 筛选出 {len(filtered)} 条爆款笔记")

    # 6. 去重并排序
    print(f"\n[Step 6] 去重并排序...")
    seen = set()
    unique_feeds = []

    for feed in filtered:
        feed_id = feed["id"]
        if feed_id not in seen:
            seen.add(feed_id)
            unique_feeds.append(feed)

    unique_feeds.sort(key=lambda x: x["likedCount"], reverse=True)

    print(f"  ✓ 去重后剩余 {len(unique_feeds)} 条笔记")
    print(f"  ✓ TOP 1: {unique_feeds[0]['title'][:30]}... ({unique_feeds[0]['likedCount']}赞)")

    # 7. 保存数据
    print(f"\n[Step 7] 保存数据...")
    output = {
        "feeds": unique_feeds,
        "keywords": keywords,
        "fetched_at": datetime.now().isoformat(),
        "total_feeds": len(unique_feeds),
        "mode": "trending"
    }

    output_file = "data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"  ✓ 数据已保存到 {output_file}")

    # 8. 统计信息
    print("\n" + "=" * 60)
    print("✓ 搜索完成!")
    print("=" * 60)
    print(f"搜索关键词数: {len(keywords)}")
    print(f"总笔记数: {len(all_feeds)}")
    print(f"爆款笔记数: {len(unique_feeds)} (点赞≥{min_likes})")
    print(f"最高点赞数: {unique_feeds[0]['likedCount']}")
    print(f"最低点赞数: {unique_feeds[-1]['likedCount']}")
    print(f"\n数据文件: {output_file}")
    print(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
