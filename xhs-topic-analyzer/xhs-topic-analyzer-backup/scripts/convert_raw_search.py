# -*- coding: utf-8 -*-
"""
转换 Subagent 保存的 raw_search.json 为 pipeline.py 期望的格式
"""
import json
import sys
import os
from datetime import datetime

def convert_raw_search(input_file, output_file):
    """转换 raw_search.json 为兼容格式"""
    print("=" * 60)
    print("转换 raw_search.json 格式")
    print("=" * 60)

    # 读取原始数据
    with open(input_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # 提取搜索结果
    search_results = raw_data.get("search_results", {})
    keywords = raw_data.get("keywords", [])
    total_feeds = raw_data.get("total_feeds", 0)

    print(f"\n[步骤1] 解析搜索结果")
    print(f"  - 关键词数: {len(keywords)}")
    print(f"  - 总笔记数: {total_feeds}")

    # 构建 users 字典
    users_dict = {}
    all_feeds = []

    for keyword, feeds in search_results.items():
        if not isinstance(feeds, list):
            continue

        for feed in feeds:
            if not isinstance(feed, dict):
                continue

            # 提取用户信息
            user_id = feed.get("userId")
            nickname = feed.get("nickname", "")
            xsec_token = feed.get("xsecToken", "")

            if not user_id:
                continue

            # 构造成 noteCard 格式
            note_card = {
                "type": "normal",
                "displayTitle": "",  # 简化格式没有标题
                "user": {
                    "userId": user_id,
                    "nickname": nickname,
                    "avatar": "",
                    "fans": 0  # 稍后填充
                },
                "interactInfo": {
                    "likedCount": feed.get("likedCount", "0"),
                    "collectedCount": "0",
                    "commentCount": "0",
                    "sharedCount": "0"
                },
                "cover": {
                    "url": ""
                }
            }

            # 构建完整笔记格式
            full_feed = {
                "id": feed.get("id", ""),
                "xsecToken": xsec_token,
                "noteCard": note_card
            }

            all_feeds.append(full_feed)

            # 添加到用户字典
            if user_id not in users_dict:
                users_dict[user_id] = {
                    "userId": user_id,
                    "nickname": nickname,
                    "avatar": "",
                    "feeds": [],
                    "xsec_token": xsec_token  # 保存 xsec_token 供后续使用
                }

            users_dict[user_id]["feeds"].append(full_feed)

    print(f"\n[步骤2] 统计结果")
    print(f"  - 唯一用户数: {len(users_dict)}")
    print(f"  - 笔记总数: {len(all_feeds)}")

    # 构建兼容格式
    compatible_data = {
        "users": users_dict,
        "metadata": {
            "keywords": keywords,
            "created_at": datetime.now().isoformat(),
            "total_feeds": total_feeds
        }
    }

    # 保存
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(compatible_data, f, ensure_ascii=False, indent=2)

    print(f"\n[步骤3] 保存结果")
    print(f"  ✓ 已保存到: {output_file}")

    print("\n" + "=" * 60)
    print("✓ 转换完成！")
    print("=" * 60)

    return compatible_data

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python convert_raw_search.py <input.json> <output.json>")
        print("示例: python convert_raw_search.py raw_search.json raw_data_converted.json")
        sys.exit(1)

    convert_raw_search(sys.argv[1], sys.argv[2])
