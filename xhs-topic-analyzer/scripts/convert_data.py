# -*- coding: utf-8 -*-
"""
转换 raw_search.json 为 pipeline.py 需要的格式
"""
import json
import sys
from datetime import datetime

def convert_raw_search(raw_file, output_file, top_n=10):
    """转换 raw_search.json 为标准格式"""
    print("=" * 60)
    print("转换 raw_search.json 为标准 data.json 格式")
    print("=" * 60)

    with open(raw_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # 收集所有笔记，按用户分组
    user_feeds = {}
    keywords = raw_data.get("search_config", {}).get("keywords", [])

    for keyword, feeds in raw_data.get("raw_feeds", {}).items():
        for feed in feeds:
            user_id = feed.get("userId", "")
            if not user_id:
                continue

            if user_id not in user_feeds:
                user_feeds[user_id] = {
                    "nickname": feed.get("nickname", ""),
                    "avatar": "",
                    "feeds": []
                }

            # 构建 noteCard 结构
            note_card = {
                "displayTitle": feed.get("displayTitle", ""),
                "time": "",  # 原始数据没有时间
                "interactInfo": {
                    "likedCount": feed.get("likedCount", "0"),
                    "collectedCount": feed.get("collectedCount", "0"),
                    "commentCount": feed.get("commentCount", "0")
                },
                "cover": {
                    "url": feed.get("cover", "")
                },
                "user": {
                    "userId": user_id,
                    "nickname": feed.get("nickname", ""),
                    "avatar": ""
                }
            }

            user_feeds[user_id]["feeds"].append({
                "id": feed.get("id", ""),
                "xsecToken": feed.get("xsecToken", ""),
                "noteCard": note_card
            })

    print(f"\n[步骤1] 统计原始数据")
    print(f"  - 总用户数: {len(user_feeds)}")
    print(f"  - 关键词: {keywords}")

    # 按点赞数排序用户
    user_scores = []
    for user_id, user_info in user_feeds.items():
        total_likes = sum(
            int(feed.get("noteCard", {}).get("interactInfo", {}).get("likedCount", 0) or 0)
            for feed in user_info.get("feeds", [])
        )
        user_scores.append({
            "user_id": user_id,
            "nickname": user_info.get("nickname", ""),
            "total_likes": total_likes,
            "feed_count": len(user_info.get("feeds", [])),
            "user_info": user_info
        })

    user_scores.sort(key=lambda x: x["total_likes"], reverse=True)
    top_users = user_scores[:top_n]

    print(f"\n[步骤2] Top {top_n} 用户（按点赞数排序）")
    for i, u in enumerate(top_users, 1):
        print(f"  {i}. {u['nickname']}: {u['total_likes']} 点赞, {u['feed_count']} 笔记")

    # 构建最终数据
    final_feeds = []
    final_users = {}

    for user_data in top_users:
        user_id = user_data["user_id"]
        fans = 0  # 简化处理，粉丝数设为0

        final_users[user_id] = {
            "userId": user_id,
            "nickname": user_data["nickname"],
            "avatar": user_data["user_info"].get("avatar", ""),
            "fans": fans,
            "feeds_count": user_data["feed_count"]
        }

        for feed in user_data["user_info"].get("feeds", []):
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

    final_data = {
        "feeds": final_feeds,
        "keywords": keywords,
        "fetched_at": datetime.now().isoformat(),
        "total_feeds": len(final_feeds),
        "unique_users": len(top_users),
        "with_fans_data": False,
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

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

    print(f"\n[步骤3] 保存结果")
    print(f"  - 输出文件: {output_file}")
    print(f"  - 笔记数: {len(final_feeds)}")
    print(f"  - 用户数: {len(top_users)}")
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)

    return final_data

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python convert_data.py <raw_search.json> <output.json> [top_n]")
        sys.exit(1)

    top_n = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    convert_raw_search(sys.argv[1], sys.argv[2], top_n)
