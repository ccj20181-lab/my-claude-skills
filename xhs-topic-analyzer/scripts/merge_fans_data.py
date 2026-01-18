# -*- coding: utf-8 -*-
"""
合并粉丝数据并生成最终的 data.json
"""
import json
import sys
import os
from datetime import datetime

def load_raw_data(file_path):
    """加载包含用户信息的原始数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_fans_data(file_path):
    """
    加载粉丝数据

    Args:
        file_path: 粉丝数据文件，格式为 JSON:
                  {
                    "user_id1": fans_count1,
                    "user_id2": fans_count2,
                    ...
                  }

    Returns:
        dict: {user_id: fans_count}
    """
    if not os.path.exists(file_path):
        print(f"警告: 粉丝数据文件不存在 - {file_path}")
        print("将使用 fans=0 继续处理...")
        return {}

    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_final_data(raw_data, fans_data, output_path):
    """
    创建最终的 data.json 文件（符合 pipeline.py 要求）

    Args:
        raw_data: 原始数据（包含 users 和 raw_feeds）
        fans_data: 粉丝数据 {user_id: fans_count}
        output_path: 输出路径
    """
    # 提取用户数据
    users = raw_data.get("users", {})

    # 整合粉丝数据
    for user_id, user_info in users.items():
        if user_id in fans_data:
            user_info["fans"] = fans_data[user_id]
            print(f"  ✓ {user_info['nickname']}: {fans_data[user_id]} 粉丝")
        else:
            user_info["fans"] = 0
            print(f"  ✗ {user_info['nickname']}: 未获取到粉丝数据")

    # 生成最终数据
    final_feeds = []
    keywords = raw_data.get("metadata", {}).get("keywords", [])

    for user_id, user_info in users.items():
        fans = user_info.get("fans", 0)

        for feed in user_info.get("feeds", []):
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
                        "fans": fans  # 关键字段
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
        "unique_users": len(users),
        "with_fans_data": True
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 最终数据已保存: {output_path}")
    print(f"  - 笔记数: {len(final_feeds)}")
    print(f"  - 用户数: {len(users)}")
    print(f"  - 包含粉丝数据: ✓")

    return final_data

def main():
    """主函数"""
    print("=" * 70)
    print("合并粉丝数据并生成最终 data.json")
    print("=" * 70)

    if len(sys.argv) < 3:
        print("\n用法:")
        print("  python merge_fans_data.py <fans_data.json> <output.json>")
        print("\n参数:")
        print("  fans_data.json - 包含粉丝数据的JSON文件")
        print("                   格式: {\"user_id1\": 1000, \"user_id2\": 2000, ...}")
        print("  output.json    - 输出文件路径 (默认: data.json)")
        print("\n示例:")
        print("  python merge_fans_data.py fans.json data.json")
        sys.exit(1)

    fans_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "data.json"

    # 读取原始数据
    # 优先尝试 raw_search.json
    raw_data_file = "raw_search.json"
    if not os.path.exists(raw_data_file):
        # 兼容旧文件名
        raw_data_file = "raw_data_with_users.json"

    print(f"\n[步骤1] 读取原始数据: {raw_data_file}")

    if not os.path.exists(raw_data_file):
        print(f"✗ 错误: 找不到原始数据文件 - {raw_data_file}")
        print(f"请先运行搜索步骤生成原始数据")
        sys.exit(1)

    raw_data = load_raw_data(raw_data_file)

    # 兼容性处理：如果 raw_data 是 {"keyword": [list]} 格式，需要转换结构
    if "users" not in raw_data:
        print("  ! 检测到原始格式，正在转换结构...")
        all_feeds = []
        keywords = []

        # 提取 feeds 和 keywords
        if "feeds" in raw_data:
            all_feeds = raw_data["feeds"]
            keywords = raw_data.get("keywords", [])
        else:
            keywords = list(raw_data.keys())
            for k, v in raw_data.items():
                if isinstance(v, list):
                    all_feeds.extend(v)

        # 重构 users 字典
        users_dict = {}
        for feed in all_feeds:
            if isinstance(feed, str): continue

            # 深度查找 userId
            note_card = feed.get("noteCard", {})
            user_info = note_card.get("user", {})
            user_id = user_info.get("userId")
            if not user_id:
                user_id = feed.get("userId")

            if not user_id: continue

            if user_id not in users_dict:
                users_dict[user_id] = {
                    "userId": user_id,
                    "nickname": user_info.get("nickname", ""),
                    "avatar": user_info.get("avatar", ""),
                    "feeds": []
                }

            # 简化 feed 并添加到用户
            users_dict[user_id]["feeds"].append(feed)

        # 重新封装 raw_data
        raw_data = {
            "users": users_dict,
            "metadata": {"keywords": keywords}
        }
        print(f"  ✓ 结构转换完成: {len(users_dict)} 个用户")

    # 读取粉丝数据

    # 读取粉丝数据
    print(f"\n[步骤2] 读取粉丝数据: {fans_file}")
    fans_data = load_fans_data(fans_file)

    # 生成最终数据
    print(f"\n[步骤3] 生成最终数据...")
    final_data = create_final_data(raw_data, fans_data, output_file)

    print("\n" + "=" * 70)
    print("✓ 数据合并完成！")
    print(f"✓ 现在可以运行: python scripts/pipeline.py --file {output_file} --mode finance-pro")
    print("=" * 70)

if __name__ == "__main__":
    main()
