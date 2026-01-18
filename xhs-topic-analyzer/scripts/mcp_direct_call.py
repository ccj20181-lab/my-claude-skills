# -*- coding: utf-8 -*-
"""
直接调用 xiaohongshu-mcp 服务器（绕过 Claude 上下文限制）

使用方式：
1. python scripts/mcp_direct_call.py user_profile "user_id" "xsec_token"
2. python scripts/mcp_direct_call.py batch compact_users.json fans.json 2

优势：
- 响应不进入 Claude 上下文
- 直接只提取 fansCount 字段
- 支持批量处理

注意：
- MCP 服务器必须在 Claude Code 中先启动（HTTP 模式）
- 默认连接 http://localhost:18060/mcp
"""
import json
import sys
import os
import requests

# 解决 Windows 控制台编码问题
if os.name == 'nt':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


# MCP 服务器配置
MCP_SERVER_URL = "http://localhost:18060/mcp"
REQUEST_ID = 0


def _send_request(method, params):
    """
    发送 JSON-RPC 请求到 MCP 服务器

    Args:
        method: 方法名
        params: 参数

    Returns:
        dict: 响应结果
    """
    global REQUEST_ID
    REQUEST_ID += 1

    request = {
        "jsonrpc": "2.0",
        "id": REQUEST_ID,
        "method": method,
        "params": params
    }

    try:
        response = requests.post(
            MCP_SERVER_URL,
            json=request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        if response.status_code != 200:
            print(f"  ✗ HTTP 错误: {response.status_code}")
            return None

        return response.json()
    except requests.exceptions.ConnectionError:
        print(f"  ✗ 无法连接到 MCP 服务器 ({MCP_SERVER_URL})")
        print(f"    请确保 Claude Code 已启动，且 xiaohongshu-mcp 已连接")
        return None
    except Exception as e:
        print(f"  ✗ 请求异常: {e}")
        return None


def call_tool(tool_name, arguments):
    """调用 MCP 工具"""
    return _send_request("tools/call", {
        "name": tool_name,
        "arguments": arguments
    })


def extract_fans_count(response):
    """
    从 user_profile 响应中提取 fansCount

    Args:
        response: MCP API 响应

    Returns:
        int: 粉丝数，失败返回 None
    """
    try:
        # 解析响应
        if "result" in response:
            result = response["result"]
            if "content" in result:
                # 结构化响应
                for item in result["content"]:
                    if item.get("type") == "text":
                        text = item.get("text", "")
                        # 尝试解析 JSON
                        try:
                            data = json.loads(text)
                            # 尝试多种可能的字段名
                            return data.get("fansCount") or data.get("fans") or data.get("fans_count")
                        except json.JSONDecodeError:
                            # 可能是纯文本
                            import re
                            match = re.search(r'"fansCount"?:\s*(\d+)', text)
                            if match:
                                return int(match.group(1))
                            # 尝试从文本中提取数字
                            match = re.search(r'[:：]\s*(\d{3,})', text)
                            if match:
                                return int(match.group(1))
            elif "fansCount" in result:
                return result["fansCount"]
        elif "error" in response:
            print(f"  ✗ API 错误: {response['error']}")
            return None
        return None
    except Exception as e:
        print(f"  ✗ 解析错误: {e}")
        return None


def call_user_profile(user_id, xsec_token):
    """调用 user_profile API"""
    print(f"  获取用户 {user_id[:16]}... 的粉丝数")

    response = call_tool("user_profile", {
        "user_id": user_id,
        "xsec_token": xsec_token
    })

    if response is None:
        return None

    fans = extract_fans_count(response)
    if fans is not None:
        print(f"  ✓ 粉丝数: {fans:,}")
    else:
        print(f"  ✗ 未能提取粉丝数")
        # 打印原始响应（用于调试）
        print(f"  原始响应: {json.dumps(response, ensure_ascii=False, indent=2)[:500]}...")

    return fans


def batch_fetch(users, output_file, batch_size=2):
    """
    批量获取粉丝数据

    Args:
        users: 用户列表 [{userId, xsec_token, nickname}]
        output_file: 输出文件路径
        batch_size: 每批处理的用户数
    """
    fans_data = {}
    total = len(users)
    success_count = 0
    fail_count = 0

    for i in range(0, total, batch_size):
        batch = users[i:min(i + batch_size, total)]
        batch_num = i // batch_size + 1
        total_batches = (total + batch_size - 1) // batch_size

        print(f"\n[批次 {batch_num}/{total_batches}] 处理 {len(batch)} 个用户...")

        for user in batch:
            user_id = user.get("userId") or user.get("user_id")
            xsec_token = user.get("xsec_token")
            nickname = user.get("nickname", "N/A")

            if not user_id or not xsec_token:
                print(f"  ✗ 用户 {nickname} 缺少必要参数")
                fail_count += 1
                continue

            try:
                response = call_tool("user_profile", {
                    "user_id": user_id,
                    "xsec_token": xsec_token
                })

                if response is None:
                    print(f"  ✗ {nickname}: 连接失败")
                    fail_count += 1
                    continue

                fans = extract_fans_count(response)
                if fans is not None:
                    fans_data[user_id] = fans
                    print(f"  ✓ {nickname}: {fans:,} 粉丝")
                    success_count += 1
                else:
                    print(f"  ✗ {nickname}: 提取失败")
                    fail_count += 1
            except Exception as e:
                print(f"  ✗ {nickname}: 调用异常 - {e}")
                fail_count += 1

            # 每次调用后保存中间结果
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(fans_data, f, ensure_ascii=False, indent=2)

        print(f"  [批次 {batch_num} 完成] 成功: {success_count}, 失败: {fail_count}")

    print(f"\n✓ 批量获取完成！")
    print(f"  成功: {success_count}/{total}")
    print(f"  输出文件: {output_file}")

    return fans_data


def test_connection():
    """测试 MCP 服务器连接"""
    print(f"测试连接到 MCP 服务器: {MCP_SERVER_URL}")

    response = _send_request("tools/list", {})

    if response and "result" in response:
        tools = response["result"].get("tools", [])
        print(f"✓ 连接成功！可用工具数: {len(tools)}")
        print("  工具列表:")
        for tool in tools[:5]:  # 只显示前5个
            print(f"    - {tool.get('name', 'N/A')}")
        if len(tools) > 5:
            print(f"    ... 共 {len(tools)} 个工具")
        return True
    else:
        print("✗ 连接失败")
        print("  请确保:")
        print("  1. Claude Code 已启动")
        print("  2. xiaohongshu-mcp 工具已连接")
        print("  3. MCP 服务器正在运行")
        return False


def main():
    """主函数"""
    print("=" * 70)
    print("xiaohongshu-mcp 直接调用工具（绕过 Claude 上下文限制）")
    print("=" * 70)

    # 测试连接
    if not test_connection():
        print("\n连接测试失败，请检查 MCP 服务器状态")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("\n用法:")
        print("  测试连接:")
        print("    python scripts/mcp_direct_call.py test")
        print("")
        print("  单个用户:")
        print("    python scripts/mcp_direct_call.py user_profile <user_id> <xsec_token>")
        print("")
        print("  批量获取:")
        print("    python scripts/mcp_direct_call.py batch <users.json> <output.json> [batch_size]")
        print("")
        print("示例:")
        print("  python scripts/mcp_direct_call.py user_profile 621262ea000000001000c058 \"AB_1Y908fLk...\"")
        print("  python scripts/mcp_direct_call.py batch compact_users.json fans.json 2")
        sys.exit(1)

    command = sys.argv[1]

    if command == "test":
        print("\n连接测试完成")
        sys.exit(0)

    if command == "user_profile":
        # 单个用户模式
        if len(sys.argv) < 4:
            print("错误: 缺少 user_id 或 xsec_token")
            sys.exit(1)

        user_id = sys.argv[2]
        xsec_token = sys.argv[3]

        print(f"\n[单个用户模式]")
        print(f"  User ID: {user_id}")
        print(f"  XSec Token: {xsec_token[:32]}...")

        fans = call_user_profile(user_id, xsec_token)

        if fans is not None:
            print(f"\n✓ 粉丝数: {fans:,}")
        else:
            print(f"\n✗ 获取失败")

    elif command == "batch":
        # 批量模式
        if len(sys.argv) < 3:
            print("错误: 缺少 users.json 文件")
            sys.exit(1)

        users_file = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else "fans.json"
        batch_size = int(sys.argv[4]) if len(sys.argv) > 4 else 2

        if not os.path.exists(users_file):
            print(f"错误: 文件不存在 - {users_file}")
            sys.exit(1)

        # 加载用户列表
        with open(users_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        users = data.get("users", []) if isinstance(data, dict) else data

        print(f"\n[批量模式]")
        print(f"  用户列表: {users_file}")
        print(f"  用户数: {len(users)}")
        print(f"  批次大小: {batch_size}")
        print(f"  输出文件: {output_file}")

        fans_data = batch_fetch(users, output_file, batch_size)

        print(f"\n✓ 结果已保存到: {output_file}")

    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
