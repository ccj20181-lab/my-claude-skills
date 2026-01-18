# -*- coding: utf-8 -*-
"""
合并 data.json 和 fans.json
"""
import json
import sys

def merge_fans(data_file, fans_file, output_file):
    """合并粉丝数据到 data.json"""
    print("=" * 60)
    print("合并粉丝数据到 data.json")
    print("=" * 60)

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(fans_file, 'r', encoding='utf-8') as f:
        fans_data = json.load(f)

    # 创建粉丝映射
    fans_map = {}
    for user in fans_data.get("top_users_pending_fans_fetch", []):
        user_id = user.get("userId", "")
        fans_map[user_id] = user.get("fans_count", 0)

    print(f"\n[步骤1] 粉丝数据映射")
    for uid, fans in fans_map.items():
        print(f"  - {uid}: {fans} 粉丝")

    # 更新 feeds 中的粉丝数据
    feeds_updated = 0
    for feed in data.get("feeds", []):
        note_card = feed.get("noteCard", {})
        user = note_card.get("user", {})
        user_id = user.get("userId", "")
        if user_id in fans_map:
            user["fans"] = fans_map[user_id]
            feeds_updated += 1

    print(f"\n[步骤2] 更新笔记数据")
    print(f"  - 更新的笔记数: {feeds_updated}")

    # 更新 top_users 中的粉丝数据
    top_users_updated = 0
    for user in data.get("top_users", []):
        user_id = user.get("userId", "")
        if user_id in fans_map:
            user["fans"] = fans_map[user_id]
            top_users_updated += 1

    print(f"\n[步骤3] 更新用户数据")
    print(f"  - 更新的用户数: {top_users_updated}")

    # 更新 with_fans_data 标志
    data["with_fans_data"] = True

    # 保存
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n[步骤4] 保存结果")
    print(f"  - 输出文件: {output_file}")
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)

    return data

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("用法: python merge_fans.py <data.json> <fans.json> <output.json>")
        sys.exit(1)

    merge_fans(sys.argv[1], sys.argv[2], sys.argv[3])
