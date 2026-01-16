# -*- coding: utf-8 -*-
"""
小红书数据收集脚本（含粉丝数据）
自动为每个笔记作者获取粉丝数据
"""
import json
import sys
import os
from datetime import datetime
from pathlib import Path

def extract_unique_users(raw_feeds):
    """
    从原始搜索结果中提取所有唯一的用户信息

    Args:
        raw_feeds: MCP search_feeds 返回的原始数据列表

    Returns:
        dict: {user_id: {userId, nickname, avatar, xsec_token, feeds: []}}
    """
    users = {}

    for feed in raw_feeds:
        # 跳过非笔记类型
        if feed.get("modelType") != "note":
            continue

        note_card = feed.get("noteCard", {})
        if not note_card:
            continue

        user = note_card.get("user", {})
        user_id = user.get("userId")

        if not user_id:
            continue

        # 如果是新用户，初始化
        if user_id not in users:
            users[user_id] = {
                "userId": user_id,
                "nickname": user.get("nickname", ""),
                "avatar": user.get("avatar", ""),
                "xsec_token": feed.get("xsecToken", ""),
                "fans": 0,  # 待获取
                "feeds": []  # 该用户的笔记列表
            }

        # 将笔记添加到该用户的列表中
        users[user_id]["feeds"].append({
            "id": feed.get("id"),
            "xsecToken": feed.get("xsecToken", ""),
            "title": note_card.get("displayTitle", ""),
            "type": note_card.get("type", ""),
            "likedCount": note_card.get("interactInfo", {}).get("likedCount", 0),
            "collectedCount": note_card.get("interactInfo", {}).get("collectedCount", 0),
            "commentCount": note_card.get("interactInfo", {}).get("commentCount", 0),
            "sharedCount": note_card.get("interactInfo", {}).get("sharedCount", 0),
            "cover": note_card.get("cover", {})
        })

    return users

def save_raw_data(raw_feeds, keywords, output_path):
    """
    保存原始数据（用于后续获取粉丝数据）

    Args:
        raw_feeds: 原始搜索数据
        keywords: 搜索关键词列表
        output_path: 输出文件路径
    """
    # 提取唯一用户
    users = extract_unique_users(raw_feeds)

    data = {
        "metadata": {
            "fetched_at": datetime.now().isoformat(),
            "keywords": keywords,
            "total_feeds": len(raw_feeds),
            "unique_users": len(users)
        },
        "users": users,
        "raw_feeds": raw_feeds
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 原始数据已保存: {output_path}")
    print(f"  - 笔记数: {len(raw_feeds)}")
    print(f"  - 唯一用户数: {len(users)}")

    return users

def enrich_with_fans_data(users_data, fans_data):
    """
    将粉丝数据整合到用户数据中

    Args:
        users_data: 原始用户数据
        fans_data: 粉丝数据 {user_id: fans_count}

    Returns:
        dict: 整合后的用户数据
    """
    for user_id, user_info in users_data.items():
        if user_id in fans_data:
            user_info["fans"] = fans_data[user_id]
        else:
            user_info["fans"] = 0  # 未获取到则设为0

    return users_data

def create_final_data(users_data, keywords, output_path):
    """
    创建最终的 data.json 文件（符合 pipeline.py 要求）

    Args:
        users_data: 包含粉丝数据的用户信息
        keywords: 搜索关键词
        output_path: 输出路径
    """
    final_feeds = []

    # 遍历所有用户和他们的笔记
    for user_id, user_info in users_data.items():
        fans = user_info.get("fans", 0)

        for feed in user_info.get("feeds", []):
            # 创建符合 pipeline 要求的数据格式
            final_feed = {
                "id": feed["id"],
                "xsecToken": feed["xsecToken"],
                "noteCard": {
                    "type": feed["type"],
                    "displayTitle": feed["title"],
                    "user": {
                        "userId": user_id,
                        "nickname": user_info["nickname"],
                        "avatar": user_info["avatar"],
                        "fans": fans  # 关键：必须包含粉丝数
                    },
                    "interactInfo": {
                        "likedCount": feed["likedCount"],
                        "collectedCount": feed["collectedCount"],
                        "commentCount": feed["commentCount"],
                        "sharedCount": feed["sharedCount"]
                    },
                    "cover": feed["cover"]
                }
            }
            final_feeds.append(final_feed)

    final_data = {
        "feeds": final_feeds,
        "keywords": keywords,
        "fetched_at": datetime.now().isoformat(),
        "total_feeds": len(final_feeds),
        "unique_users": len(users_data),
        "with_fans_data": True
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 最终数据已保存: {output_path}")
    print(f"  - 笔记数: {len(final_feeds)}")
    print(f"  - 用户数: {len(users_data)}")
    print(f"  - 包含粉丝数据: ✓")

    return final_data

def main():
    """主函数"""
    print("=" * 70)
    print("小红书数据收集脚本（含粉丝数据获取）")
    print("=" * 70)

    if len(sys.argv) < 3:
        print("\n用法:")
        print("  python fetch_with_fans.py <raw_data.json> <keywords> [output]")
        print("\n参数:")
        print("  raw_data.json  - 包含MCP搜索结果的JSON文件")
        print("  keywords       - 搜索关键词，用逗号分隔 (例如: 理财,基金,股票)")
        print("  output         - 可选，输出文件路径 (默认: data.json)")
        print("\n示例:")
        print("  python fetch_with_fans.py raw_search_results.json 理财,基金,股票")
        sys.exit(1)

    raw_file = sys.argv[1]
    keywords_str = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else "data.json"

    # 读取原始数据
    print(f"\n[步骤1] 读取原始数据: {raw_file}")
    if not os.path.exists(raw_file):
        print(f"✗ 错误: 文件不存在 - {raw_file}")
        sys.exit(1)

    with open(raw_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # 提取关键词列表
    keywords = [k.strip() for k in keywords_str.split(',')]
    print(f"  关键词: {keywords}")

    # 检查原始数据格式
    if isinstance(raw_data, dict) and "raw_feeds" in raw_data:
        raw_feeds = raw_data["raw_feeds"]
    elif isinstance(raw_data, list):
        raw_feeds = raw_data
    else:
        print(f"✗ 错误: 不支持的数据格式")
        sys.exit(1)

    print(f"  笔记数: {len(raw_feeds)}")

    # 保存原始数据并提取用户
    print(f"\n[步骤2] 提取唯一用户信息...")
    users = save_raw_data(raw_feeds, keywords, "raw_data_with_users.json")

    # 提示需要手动获取粉丝数据
    print(f"\n[步骤3] ⚠️  需要获取粉丝数据！")
    print(f"\n请使用 MCP 工具为以下用户获取粉丝数据：")
    print(f"总用户数: {len(users)}")
    print(f"\n建议使用以下命令格式（需要逐个调用）：")
    print(f"  mcp__xiaohongshu-mcp__user_profile")
    print(f"  参数: user_id, xsec_token")

    # 保存用户列表供参考
    users_list_file = "users_to_fetch.txt"
    with open(users_list_file, 'w', encoding='utf-8') as f:
        for user_id, user_info in users.items():
            f.write(f"{user_id}\t{user_info['nickname']}\t{user_info['xsec_token']}\n")

    print(f"\n✓ 用户列表已保存: {users_list_file}")
    print(f"\n获取粉丝数据后，请运行:")
    print(f"  python merge_fans_data.py <fans_data.json> {output_file}")

    print("\n" + "=" * 70)
    print("✓ 数据准备完成！等待获取粉丝数据...")
    print("=" * 70)

if __name__ == "__main__":
    main()
