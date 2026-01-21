#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书爆款选题分析器 - 直接 HTTP 版本
通过 requests 直接调用小红书 API，无需 MCP Server
"""

import os
import sys
import json
import time
import subprocess
import requests
from datetime import datetime


# 小红书 API 配置
XHS_API_BASE = "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"

# 统一 cookies 管理路径
UNIFIED_COOKIES = os.path.expanduser("~/.xiaohongshu-mcp/cookies.json")
MANAGER_SCRIPT = os.path.expanduser("~/.xiaohongshu-mcp/cookies-manager.sh")


def ensure_cookies():
    """确保 cookies 存在且有效"""
    if not os.path.exists(UNIFIED_COOKIES):
        print("[Info] 未找到统一 cookies 文件，运行登录流程...")
        print(f"[Info] 请手动运行: {MANAGER_SCRIPT} login")
        sys.exit(1)

    # 检查 cookies 状态
    if os.path.exists(MANAGER_SCRIPT):
        result = subprocess.run(
            [MANAGER_SCRIPT, "status"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print("[Warn] Cookies 已过期或无效")
            print(f"[Info] 请运行: {MANAGER_SCRIPT} login")
            sys.exit(1)

    return UNIFIED_COOKIES


def load_cookies():
    """加载小红书 cookies"""
    # 首先确保 cookies 存在且有效
    ensure_cookies()

    # 从统一 cookies 文件加载
    if not os.path.exists(UNIFIED_COOKIES):
        print(f"[Error] Cookies 文件不存在: {UNIFIED_COOKIES}")
        print(f"[Info] 请运行: {MANAGER_SCRIPT} login")
        sys.exit(1)

    try:
        with open(UNIFIED_COOKIES, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        print(f"  ✓ 已从统一文件加载 {len(cookies)} 个 cookies")
        return cookies
    except json.JSONDecodeError as e:
        print(f"[Error] Cookies 文件格式错误: {e}")
        print(f"[Info] 请运行: {MANAGER_SCRIPT} login")
        sys.exit(1)
    except Exception as e:
        print(f"[Error] 读取 cookies 失败: {e}")
        sys.exit(1)


def build_cookies_dict(cookies):
    """构建 requests 的 cookies 字典"""
    if isinstance(cookies, dict):
        return cookies
    elif isinstance(cookies, list):
        return {cookie['name']: cookie['value'] for cookie in cookies}
    else:
        return {}


def search_xiaohongshu(keyword, cookies_dict):
    """搜索小红书笔记"""
    print(f"[Info] 搜索关键词: {keyword}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.xiaohongshu.com/",
        "Origin": "https://www.xiaohongshu.com",
    }

    params = {
        "keyword": keyword,
        "page": 1,
        "page_size": 20,
        "search_id": "",
        "sort": "general_ranking",  # 综合排序
        "note_type": 0,  # 0=全部
    }

    try:
        response = requests.get(
            XHS_API_BASE,
            params=params,
            cookies=cookies_dict,
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                items = data.get("data", {}).get("items", [])
                notes = []

                for item in items:
                    if item.get("model_type") == "note":
                        note_card = item.get("note_card", {})
                        note_data = {
                            "id": note_card.get("id", ""),
                            "title": note_card.get("display_title", ""),
                            "nickname": note_card.get("user", {}).get("nickname", ""),
                            "likedCount": note_card.get("interact_info", {}).get("liked_count", 0),
                            "collectedCount": note_card.get("interact_info", {}).get("collected_count", 0),
                            "commentCount": note_card.get("interact_info", {}).get("comment_count", 0),
                            "publishTime": note_card.get("time", ""),
                        }
                        notes.append(note_data)

                print(f"  ✓ {keyword}: {len(notes)} 条")
                return notes
            else:
                print(f"  ✗ {keyword}: API 返回失败 - {data.get('msg', 'Unknown error')}")
                return []
        else:
            print(f"  ✗ {keyword}: HTTP {response.status_code}")
            return []

    except Exception as e:
        print(f"  ✗ {keyword}: 请求失败 - {e}")
        return []


def filter_explosive_feeds(all_feeds, min_likes):
    """筛选爆款笔记（点赞数 ≥ min_likes）"""
    filtered = []

    for feed in all_feeds:
        likes = int(feed.get("likedCount", 0))

        if likes >= min_likes:
            filtered.append(feed)

    return filtered


def main():
    """主函数"""
    print("=" * 60)
    print("小红书财经爆款分析器 - 直接 HTTP 版本")
    print("=" * 60)

    # 1. 加载配置
    print("[Step 1] 加载配置文件...")
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'config.json'
    )

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"[Error] 加载配置文件失败: {e}")
        sys.exit(1)

    keywords = config.get("keywords", [])
    min_likes = config.get("filters", {}).get("min_likes", 2000)

    print(f"  ✓ 已加载 {len(keywords)} 个搜索关键词")
    print(f"  ✓ 筛选条件: 点赞数 ≥ {min_likes}")

    # 2. 加载 cookies
    print("\n[Step 2] 加载小红书 Cookies...")
    cookies = load_cookies()
    cookies_dict = build_cookies_dict(cookies)
    print(f"  ✓ 已加载 {len(cookies_dict)} 个 cookies")

    # 3. 搜索所有关键词
    print(f"\n[Step 3] 开始搜索 {len(keywords)} 个关键词...")
    all_feeds = []

    for i, keyword in enumerate(keywords, 1):
        print(f"\n[{i}/{len(keywords)}] 搜索: {keyword}")
        feeds = search_xiaohongshu(keyword, cookies_dict)
        all_feeds.extend(feeds)

        # 添加延迟避免请求过快
        if i < len(keywords):
            time.sleep(2)

    if not all_feeds:
        print("\n[Error] 未搜索到任何笔记")
        print("[Info] 可能原因:")
        print("  1. 小红书 cookies 已过期")
        print("  2. 搜索关键词不合理")
        print("  3. IP 被限流")
        sys.exit(1)

    print(f"\n  ✓ 共搜索到 {len(all_feeds)} 条笔记")

    # 4. 筛选爆款
    print(f"\n[Step 4] 筛选爆款笔记 (点赞≥{min_likes})...")
    filtered = filter_explosive_feeds(all_feeds, min_likes)

    if not filtered:
        print(f"[Warning] 未找到点赞数 ≥ {min_likes} 的爆款笔记")
        print(f"[Info] 搜索到的最高点赞数: {max(f.get('likedCount', 0) for f in all_feeds)}")
        sys.exit(1)

    print(f"  ✓ 筛选出 {len(filtered)} 条爆款笔记")

    # 5. 去重并排序
    print(f"\n[Step 5] 去重并排序...")
    seen = set()
    unique_feeds = []

    for feed in filtered:
        feed_id = feed["id"]
        if feed_id not in seen:
            seen.add(feed_id)
            unique_feeds.append(feed)

    unique_feeds.sort(key=lambda x: x["likedCount"], reverse=True)

    print(f"  ✓ 去重后剩余 {len(unique_feeds)} 条笔记")
    if len(unique_feeds) > 0:
        print(f"  ✓ TOP 1: {unique_feeds[0]['title'][:30]}... ({unique_feeds[0]['likedCount']}赞)")

    # 6. 保存数据
    print(f"\n[Step 6] 保存数据...")
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

    # 7. 统计信息
    print("\n" + "=" * 60)
    print("✓ 搜索完成!")
    print("=" * 60)
    print(f"搜索关键词数: {len(keywords)}")
    print(f"总笔记数: {len(all_feeds)}")
    print(f"爆款笔记数: {len(unique_feeds)} (点赞≥{min_likes})")
    if len(unique_feeds) > 0:
        print(f"最高点赞数: {unique_feeds[0]['likedCount']}")
        print(f"最低点赞数: {unique_feeds[-1]['likedCount']}")
    print(f"\n数据文件: {output_file}")
    print(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
