# -*- coding: utf-8 -*-
"""
创建最终的 data.json（只包含 Top 用户和他们的笔记）
"""
import json
import sys
import os
from datetime import datetime

def create_final_data(converted_file, fans_file, output_file, top_n=10):
    """创建只包含 Top 用户的 data.json"""
    print("=" * 60)
    print("创建最终 data.json（Top N 用户版）")
    print("=" * 60)

    # 读取转换后的数据
    with open(converted_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # 读取粉丝数据
    with open(fans_file, 'r', encoding='utf-8') as f:
        fans_data = json.load(f)

    users = raw_data.get("users", {})
    keywords = raw_data.get("metadata", {}).get("keywords", [])

    print(f"\n[步骤1] 统计原始数据")
    print(f"  - 总用户数: {len(users)}")
    print(f"  - 关键词: {keywords}")

    # 按粉丝数排序，筛选 Top N 用户
    user_scores = []
    for user_id, user_info in users.items():
        fans = fans_data.get(user_id, 0)
        total_likes = sum(
            int(feed.get("noteCard", {}).get("interactInfo", {}).get("likedCount", 0) or 0)
            for feed in user_info.get("feeds", [])
        )
        user_scores.append({
            "user_id": user_id,
            "nickname": user_info.get("nickname", ""),
            "fans": fans,
            "total_likes": total_likes,
            "feed_count": len(user_info.get("feeds", [])),
            "user_info": user_info
        })

    # 按粉丝数 + 点赞数综合排序
    user_scores.sort(key=lambda x: (x["fans"], x["total_likes"]), reverse=True)

    # 选择 Top N 用户
    top_users = user_scores[:top_n]

    print(f"\n[步骤2] Top {top_n} 用户")
    for i, u in enumerate(top_users, 1):
        print(f"  {i}. {u['nickname']}: {u['fans']} 粉丝, {u['total_likes']} 点赞, {u['feed_count']} 笔记")

    # 构建最终数据
    final_feeds = []
    final_users = {}

    for user_data in top_users:
        user_id = user_data["user_id"]
        fans = user_data["fans"]

        final_users[user_id] = {
            "userId": user_id,
            "nickname": user_data["nickname"],
            "avatar": user_data["user_info"].get("avatar", ""),
            "fans": fans,
            "feeds_count": user_data["feed_count"]
        }

        for feed in user_data["user_info"].get("feeds", []):
            # 确保 feed 有正确的粉丝数据
            note_card = feed.get("noteCard", {})
            if "user" not in note_card:
                note_card["user"] = {}
            note_card["user"]["fans"] = fans

            final_feed = {
                "id": feed.get("id", ""),
                "xsecToken": feed.get("xsecToken", ""),
                "noteCard": note_card
            }
            final_feeds.append(final_feed)

    # 构建最终 JSON
    final_data = {
        "feeds": final_feeds,
        "keywords": keywords,
        "fetched_at": datetime.now().isoformat(),
        "total_feeds": len(final_feeds),
        "unique_users": len(top_users),
        "with_fans_data": True,
        "top_users": [
            {
                "userId": u["userId"],
                "nickname": u["nickname"],
                "fans": u["fans"],
                "feed_count": u["feeds_count"]
            }
            for u in final_users.values()
        ]
    }

    # 保存
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

    print(f"\n[步骤3] 保存结果")
    print(f"  ✓ 输出文件: {output_file}")
    print(f"  - 笔记数: {len(final_feeds)}")
    print(f"  - 用户数: {len(top_users)}")

    print("\n" + "=" * 60)
    print("✓ 完成！")
    print("=" * 60)

    return final_data

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("用法: python create_final_data.py <converted.json> <fans.json> <output.json> [top_n]")
        print("示例: python create_final_data.py raw_data_converted.json fans.json data.json 10")
        sys.exit(1)

    top_n = int(sys.argv[4]) if len(sys.argv) > 4 else 10
    create_final_data(sys.argv[1], sys.argv[2], sys.argv[3], top_n)
