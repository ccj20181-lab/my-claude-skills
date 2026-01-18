#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Agent Runner for GitHub Actions
使用 Claude Agent SDK 调用小红书 MCP 工具搜索爆款笔记
"""

import os
import sys
import json
from datetime import datetime
from anthropic import Anthropic


def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[Error] 加载配置文件失败: {e}")
        sys.exit(1)


def build_task_prompt(config):
    """构建任务提示词"""
    keywords = config.get("keywords", [])
    filters = config.get("filters", {})
    min_likes = filters.get("min_likes", 2000)
    publish_time = filters.get("publish_time", "3d")

    keywords_str = "、".join(keywords)

    prompt = f"""请执行以下任务：

## 🎯 任务目标
搜索小红书关键词，提取近期爆款笔记（V8.1 - 无粉丝数据）

## ⚠️ 关键要求
- 必须调用 mcp__xiaohongshu__search_feeds API
- 禁止跳过搜索步骤或复用旧数据
- 强制覆盖保存新数据
- **不需要获取粉丝数据**

## 步骤 1：搜索关键词
对以下 {len(keywords)} 个关键词分别调用 mcp__xiaohongshu__search_feeds：

关键词列表: {keywords_str}

对每个关键词的调用参数：
- keyword: <关键词>
- filters:
  - sort_by: "最多点赞"（按点赞数排序）
  - publish_time: "一周内"（获取最新数据）
  - note_type: "不限"

报告每个关键词的搜索结果数量

## 步骤 2：合并去重
合并所有搜索结果，按点赞数排序，去除重复笔记

## 步骤 3：筛选爆款
严格筛选：
- 发布时间：{publish_time} 内
- 点赞数：≥{min_likes}

## 步骤 4：保存数据
保存到当前目录的 data.json 文件

格式（V8.1 - 需要 collectedCount 和 commentCount）：
```json
{{
  "feeds": [{{
    "id": "笔记ID",
    "title": "标题",
    "nickname": "博主昵称",
    "likedCount": 点赞数,
    "collectedCount": 收藏数,
    "commentCount": 评论数,
    "publishTime": "发布时间"
  }}],
  "keywords": {json.dumps(keywords, ensure_ascii=False)},
  "fetched_at": "{datetime.now().isoformat()}",
  "mode": "trending",
  "keywords_executed": []
}}
```

**重要**：不要包含 fans 字段

## 步骤 5：返回摘要
返回搜索结果统计和筛选后的笔记数量
"""

    return prompt


def run_agent():
    """运行 Claude Agent"""
    print("=" * 60)
    print("Claude Agent Runner - xhs-topic-analyzer")
    print("=" * 60)

    # 1. 检查环境变量
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[Error] 缺少 ANTHROPIC_API_KEY 环境变量")
        sys.exit(1)

    print("[Step 1] 初始化 Anthropic 客户端...")
    client = Anthropic(api_key=api_key)

    # 2. 加载配置
    print("[Step 2] 加载配置文件...")
    config = load_config()
    keywords = config.get("keywords", [])
    print(f"  ✓ 已加载 {len(keywords)} 个搜索关键词")

    # 3. 构建任务提示词
    print("[Step 3] 构建任务提示词...")
    task_prompt = build_task_prompt(config)

    # 4. 调用 Claude API
    print("[Step 4] 调用 Claude API...")
    print("  - Model: claude-3-5-sonnet-20241022")
    print("  - Max tokens: 8192")
    print("  - Tools: mcp__xiaohongshu__search_feeds")

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8192,
            messages=[{
                "role": "user",
                "content": task_prompt
            }]
        )

        print(f"  ✓ API 调用成功")
        print(f"  - Stop reason: {response.stop_reason}")
        print(f"  - Input tokens: {response.usage.input_tokens}")
        print(f"  - Output tokens: {response.usage.output_tokens}")

    except Exception as e:
        print(f"[Error] Claude API 调用失败: {e}")
        sys.exit(1)

    # 5. 检查是否生成了 data.json
    print("[Step 5] 检查数据文件...")
    data_file = "data.json"

    if not os.path.exists(data_file):
        print(f"[Error] 未找到 {data_file}")
        print("[Info] Agent 响应内容:")
        for block in response.content:
            if hasattr(block, 'text'):
                print(block.text)
        sys.exit(1)

    # 6. 验证数据文件
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        feeds = data.get("feeds", [])
        print(f"  ✓ 数据文件已生成")
        print(f"  - 笔记数量: {len(feeds)}")

        if len(feeds) > 0:
            print(f"  - 示例笔记: {feeds[0].get('title', 'N/A')[:30]}...")

    except Exception as e:
        print(f"[Error] 数据文件格式错误: {e}")
        sys.exit(1)

    print("=" * 60)
    print("✓ Agent 执行完成")
    print("=" * 60)


if __name__ == "__main__":
    run_agent()
