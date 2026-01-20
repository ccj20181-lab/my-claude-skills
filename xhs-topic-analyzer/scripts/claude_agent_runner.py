#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Agent Runner for GitHub Actions
使用 Anthropic SDK (通过硅基流动代理) + 小红书 MCP 搜索爆款笔记
"""

import os
import sys
import json
import subprocess
import time
import requests
from datetime import datetime

try:
    from anthropic import Anthropic
except ImportError:
    print("正在安装 anthropic 包...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "anthropic"])
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


def start_mcp_server(cookies_path):
    """启动小红书 MCP HTTP Server"""
    print("启动小红书 MCP Server...")

    # 检查 xiaohongshu-mcp 是否存在（GitHub Actions 环境中已预安装）
    try:
        subprocess.run(["which", "xiaohongshu-mcp"], capture_output=True, check=True)
        print("✓ xiaohongshu-mcp 已就绪")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[Error] xiaohongshu-mcp 未找到")
        print("请确保在 GitHub Actions 中已正确安装 xiaohongshu-mcp")
        sys.exit(1)

    # 启动 MCP Server
    cmd = [
        "xiaohongshu-mcp", "serve",
        "--port", "3000",
        "--cookies", cookies_path
    ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # 等待服务启动
    print("等待 MCP Server 启动...")
    for i in range(15):
        try:
            response = requests.get("http://localhost:3000/health", timeout=2)
            if response.status_code == 200:
                print("✓ MCP Server 已就绪")
                return process
        except:
            pass
        print(f"等待中... ({i+1}/15)")
        time.sleep(2)

    # 检查是否成功启动
    try:
        response = requests.get("http://localhost:3000/health", timeout=2)
        if response.status_code == 200:
            print("✓ MCP Server 已就绪")
            return process
    except:
        pass

    print("[Error] MCP Server 启动失败")
    print("查看日志:")
    print(process.stderr.read())
    process.kill()
    sys.exit(1)


def run_claude_agent(api_key, base_url, config):
    """运行 Claude Agent"""
    print("\n" + "="*60)
    print("Claude Agent Runner - xhs-topic-analyzer")
    print("="*60)

    keywords = config.get("keywords", [])
    filters = config.get("filters", {})
    min_likes = filters.get("min_likes", 2000)

    keywords_str = "、".join(keywords)

    # 构建 MCP 工具配置
    tools = [{
        "type": "computer_20241022",
        "name": "mcp__xiaohongshu__search_feeds",
        "computer_20241022": {
            "mcp_server": {
                "url": "http://localhost:3000"
            }
        }
    }]

    # 初始化 Anthropic 客户端
    print("\n[Step 1] 初始化 Anthropic 客户端...")
    print(f"  - Base URL: {base_url}")
    print(f"  - Model: claude-sonnet-4-20250514")

    client = Anthropic(
        api_key=api_key,
        base_url=base_url
    )

    # 构建任务提示词
    print(f"\n[Step 2] 构建任务提示词...")
    task_prompt = f"""请执行小红书财经赛道爆款笔记分析任务：

## 🎯 任务目标
搜索小红书财经赛道关键词，提取近期爆款笔记（点赞≥2000）

## 📋 搜索关键词
{keywords_str}

## ⚙️ 搜索参数
每个关键词调用 mcp__xiaohongshu__search_feeds，参数：
- keyword: <关键词>
- filters:
  - sort_by: "最多点赞"
  - publish_time: "一周内"
  - note_type: "不限"

## 🔍 执行步骤
1. 对每个关键词调用搜索 API
2. 合并所有搜索结果
3. 筛选条件：点赞数 ≥ {min_likes}
4. 去重（按笔记ID）
5. 按点赞数降序排列
6. 保存到 data.json 文件

## 📄 输出格式
```json
{{
  "feeds": [{{
    "id": "笔记ID",
    "title": "标题",
    "user": "博主昵称",
    "liked_count": 点赞数,
    "collected_count": 收藏数,
    "comment_count": 评论数,
    "type": "类型",
    "keyword": "来源关键词"
  }}],
  "total_feeds": <总数>,
  "fetched_at": "<时间戳>"
}}
```

## ⚠️ 重要提醒
- 必须调用真实的 mcp__xiaohongshu__search_feeds API
- 不能编造数据
- 需要完整搜索所有 {len(keywords)} 个关键词

请开始执行任务！
"""

    # 调用 Claude API
    print(f"\n[Step 3] 调用 Claude API...")
    print(f"  - Keywords: {len(keywords)} 个")
    print(f"  - Max tokens: 16384")
    print(f"  - Tools: mcp__xiaohongshu__search_feeds")

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=16384,
            tools=tools,
            messages=[{
                "role": "user",
                "content": task_prompt
            }]
        )

        print(f"\n  ✓ API 调用成功")
        print(f"  - Usage: {response.usage.total_tokens} tokens")
        print(f"  - Input: {response.usage.input_tokens} tokens")
        print(f"  - Output: {response.usage.output_tokens} tokens")

        return response

    except Exception as e:
        print(f"\n[Error] Claude API 调用失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """主函数"""
    # 1. 检查环境变量
    api_key = os.environ.get("ANTHROPIC_AUTH_TOKEN")
    base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
    cookies_json = os.environ.get("XHS_COOKIES")

    if not api_key:
        print("[Error] 缺少 ANTHROPIC_AUTH_TOKEN 环境变量")
        sys.exit(1)

    if not cookies_json:
        print("[Error] 缺少 XHS_COOKIES 环境变量")
        sys.exit(1)

    # 2. 保存 cookies 到临时文件
    cookies_file = "/tmp/xhs_cookies.json"
    with open(cookies_file, 'w', encoding='utf-8') as f:
        f.write(cookies_json)
    print(f"✓ Cookies 文件已创建: {cookies_file}")

    # 3. 启动 MCP Server
    mcp_process = start_mcp_server(cookies_file)

    try:
        # 4. 加载配置
        print("\n[Info] 加载配置文件...")
        config = load_config()
        print(f"✓ 已加载 {len(config.get('keywords', []))} 个关键词")

        # 5. 运行 Claude Agent
        response = run_claude_agent(api_key, base_url, config)

        # 6. 检查生成的数据文件
        print("\n[Step 4] 检查生成的数据文件...")
        data_file = "data.json"

        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            feeds = data.get("feeds", [])
            print(f"✓ 数据文件已生成")
            print(f"  - 笔记数量: {len(feeds)}")

            if len(feeds) > 0:
                print(f"  - 示例: {feeds[0].get('title', 'N/A')[:50]}...")
                print(f"  - 总点赞数: {sum(f.get('liked_count', 0) for f in feeds):,}")

        else:
            print(f"[Warning] 未找到 {data_file}")
            print("[Info] Claude 响应内容:")
            print(response.content)

    finally:
        # 7. 清理：停止 MCP Server
        print("\n[Step 5] 清理资源...")
        mcp_process.terminate()
        mcp_process.wait()

        # 删除 cookies 文件
        if os.path.exists(cookies_file):
            os.remove(cookies_file)
            print(f"✓ 已删除 {cookies_file}")

        print("✓ 清理完成")

    print("\n" + "="*60)
    print("✓ Agent Runner 执行完成")
    print("="*60)


if __name__ == "__main__":
    main()
