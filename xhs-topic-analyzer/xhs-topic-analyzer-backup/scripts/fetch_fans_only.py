# -*- coding: utf-8 -*-
"""
轻量级粉丝数据获取脚本
只提取粉丝数，大幅减少 token 消耗

使用方法：
1. 先运行 python fetch_with_fans.py raw_search.json "理财,基金" 生成用户列表
2. 或直接运行此脚本从 raw_search.json 生成精简用户列表
3. 根据提示手动调用 MCP API 获取粉丝数据
4. 运行 python merge_fans_data.py 合并结果
"""
import sys
import os

# 解决 Windows 控制台编码问题
if os.name == 'nt':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import json
from datetime import datetime
from pathlib import Path


def extract_top_users(raw_feeds, top_n=5):
    """
    只提取每个关键词下点赞最高的 top_n 个用户

    Args:
        raw_feeds: 原始搜索数据
        top_n: 每个关键词保留的Top用户数（默认5）

    Returns:
        dict: {user_id: {userId, nickname, xsec_token, total_likes, feed_ids}}
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

        interact_info = note_card.get("interactInfo", {})
        liked_count = interact_info.get("likedCount", 0)

        if user_id not in users:
            users[user_id] = {
                "userId": user_id,
                "nickname": user.get("nickname", ""),
                "xsec_token": feed.get("xsecToken", ""),
                "total_likes": 0,
                "feed_ids": []
            }

        users[user_id]["total_likes"] += liked_count
        users[user_id]["feed_ids"].append(feed.get("id"))

    # 按总点赞数排序，只保留 Top N
    sorted_users = sorted(users.items(), key=lambda x: x[1]["total_likes"], reverse=True)
    top_users = dict(sorted_users[:top_n])

    return top_users


def create_compact_user_list(raw_feeds, top_per_keyword=5):
    """
    从原始数据创建精简用户列表（只包含用户ID和token）

    Args:
        raw_feeds: 原始搜索数据（支持多种格式）
        top_per_keyword: 全局保留的Top用户数

    Returns:
        list: [{user_id, xsec_token, nickname, total_likes}]
    """
    # 统一转换为列表格式
    all_feeds = []
    if isinstance(raw_feeds, dict):
        # 格式1: {"关键词1": [...], "关键词2": [...]}
        for feeds in raw_feeds.values():
            if isinstance(feeds, list):
                all_feeds.extend(feeds)
    elif isinstance(raw_feeds, list):
        # 格式2: [...]
        all_feeds = raw_feeds
    elif isinstance(raw_feeds, dict) and "raw_feeds" in raw_feeds:
        # 格式3: {"raw_feeds": [...]}
        all_feeds = raw_feeds["raw_feeds"]

    # 按用户聚合（由于没有点赞数，按出现频率排序）
    user_data = {}
    for feed in all_feeds:
        if isinstance(feed, str):
            continue

        # 尝试从不同位置获取 userId
        user_id = feed.get("userId")
        nickname = ""

        # 适配 MCP 原始返回格式 (在 noteCard.user 中)
        if not user_id and "noteCard" in feed:
            user_info = feed["noteCard"].get("user", {})
            user_id = user_info.get("userId")
            nickname = user_info.get("nickname", "")

        if not user_id:
            continue

        if user_id not in user_data:
            user_data[user_id] = {
                "userId": user_id,
                "nickname": nickname,
                "xsec_token": feed.get("xsecToken", ""),
                "feed_count": 0
            }
        user_data[user_id]["feed_count"] += 1

    # 排序并选择 Top 用户（按笔记数量排序，因为没有点赞数）
    sorted_users = sorted(
        user_data.values(),
        key=lambda x: x["feed_count"],
        reverse=True
    )
    top_users = sorted_users[:top_per_keyword]

    return top_users


def save_compact_user_list(users, output_path):
    """
    保存精简用户列表（便于 Claude 调用 MCP）

    Args:
        users: 用户列表
        output_path: 输出路径
    """
    # 只保留 MCP API 需要的字段
    compact_users = []
    for u in users:
        compact_users.append({
            "userId": u["userId"],
            "xsec_token": u["xsec_token"],
            "nickname": u.get("nickname", ""),
            "feed_count": u.get("feed_count", 0)
        })

    data = {
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "total_users": len(compact_users),
            "note": "此文件包含精选用户列表，用于获取粉丝数据。每个用户只调用一次 user_profile API。"
        },
        "users": compact_users
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 精简用户列表已保存: {output_path}")
    print(f"  - 用户数: {len(compact_users)}")
    print(f"  - 预计 MCP API 调用次数: {len(compact_users)}")
    print(f"  - 预计 token 消耗: ~{len(compact_users) * 2000} (每个用户约 2000 tokens)")

    return data


def generate_mcp_prompt(users):
    """
    生成 Claude 调用的 MCP 指令

    Args:
        users: 用户列表

    Returns:
        str: 指令文本
    """
    prompt = """请为以下小红书用户获取粉丝数据：

## 操作说明
对每个用户调用 mcp__xiaohongshu-mcp__user_profile，然后只提取粉丝数：

## 用户列表
"""

    for i, u in enumerate(users, 1):
        prompt += f"{i}. user_id: {u['userId']}, xsec_token: {u['xsec_token']}, 笔记数: {u.get('feed_count', 0)}\n"

    prompt += """
## 输出格式
请按以下格式返回结果（只需要粉丝数字段）：
```json
{
  "userId": "xxx",
  "fansCount": 12345
}
```

## 注意事项
1. 只需要提取 fansCount 字段，不需要笔记列表
2. 建议每次调用 2-3 个用户，避免超出上下文限制
3. 完成后将结果保存到 fans_data.json
"""

    return prompt


def save_mcp_prompt(users, output_path="mcp_prompt.txt"):
    """保存 MCP 调用指令"""
    prompt = generate_mcp_prompt(users)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(prompt)

    print(f"\n✓ MCP 指令已保存: {output_path}")
    return prompt


def main():
    """主函数"""
    print("=" * 70)
    print("轻量级粉丝数据获取工具")
    print("只提取粉丝数，大幅减少 token 消耗")
    print("=" * 70)

    if len(sys.argv) < 2:
        print("\n用法:")
        print("  python fetch_fans_only.py <raw_data.json> [top_n] [output]")
        print("\n参数:")
        print("  raw_data.json  - raw_search.json 文件路径")
        print("  top_n          - 可选，保留的Top用户数 (默认: 10)")
        print("  output         - 可选，输出文件路径 (默认: compact_users.json)")
        print("\n示例:")
        print("  python fetch_fans_only.py raw_search.json 10")
        print("  python fetch_fans_only.py raw_search.json 5 compact_users.json")
        sys.exit(1)

    raw_file = sys.argv[1]
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    output_file = sys.argv[3] if len(sys.argv) > 3 else "compact_users.json"

    # 读取原始数据
    print(f"\n[步骤1] 读取原始数据: {raw_file}")
    if not os.path.exists(raw_file):
        print(f"✗ 错误: 文件不存在 - {raw_file}")
        sys.exit(1)

    with open(raw_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # 提取关键词列表（如果有）
    keywords = []
    if isinstance(raw_data, dict):
        if "raw_feeds" in raw_data:
            raw_feeds = raw_data["raw_feeds"]
            keywords = raw_data.get("metadata", {}).get("keywords", [])
        elif "feeds" in raw_data:
            raw_feeds = raw_data["feeds"]
            keywords = raw_data.get("keywords", [])
        else:
            # 格式: {"关键词1": [...], "关键词2": [...]}
            raw_feeds = []
            for feeds in raw_data.values():
                if isinstance(feeds, list):
                    raw_feeds.extend(feeds)
            keywords = list(raw_data.keys())
    elif isinstance(raw_data, list):
        raw_feeds = raw_data
    else:
        print(f"✗ 错误: 不支持的数据格式")
        sys.exit(1)

    print(f"  笔记数: {len(raw_feeds)}")
    if keywords:
        print(f"  关键词: {keywords}")

    # 创建精简用户列表
    print(f"\n[步骤2] 提取 Top {top_n} 用户...")
    users = create_compact_user_list(raw_feeds, top_per_keyword=top_n)

    # 保存精简用户列表
    print(f"\n[步骤3] 保存精简用户列表...")
    save_compact_user_list(users, output_file)

    # 保存 MCP 指令
    print(f"\n[步骤4] 生成 MCP 调用指令...")
    save_mcp_prompt(users, "mcp_prompt.txt")

    # 显示摘要
    print("\n" + "=" * 70)
    print("摘要")
    print("=" * 70)
    print(f"  原始笔记数: {len(raw_feeds)}")
    print(f"  精选用户数: {len(users)}")

    # 计算批次数
    batch_size = 2
    num_batches = (len(users) + batch_size - 1) // batch_size

    print(f"\n" + "=" * 70)
    print("⚠️ 下一步操作（必须使用 Task 工具启动 Subagent！）")
    print("=" * 70)
    print("""
# ⚠️ 严格禁止：在主上下文中直接调用 user_profile！

# ✅ 正确方式：使用 Task 工具启动 Subagent

# 1. 运行并行获取脚本
python scripts/auto_fetch_fans_parallel.py compact_users.json fans.json 2

# 2. 启动 N 个 Subagent（并行执行）
Task(subagent_type="general-purpose",
     prompt="请读取 batch_prompts/batch_1.txt 并执行。只提取 fansCount，直接返回 JSON。")

Task(subagent_type="general-purpose",
     prompt="请读取 batch_prompts/batch_2.txt 并执行。只提取 fansCount，直接返回 JSON。")

... 以此类推

# 3. 收集结果并继续
python scripts/merge_fans_data.py fans.json data.json
python scripts/pipeline.py --file data.json --mode finance-pro
""")
    print("=" * 70)


if __name__ == "__main__":
    main()
