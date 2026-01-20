#!/bin/bash
# 本地测试脚本 - xhs-topic-analyzer
# 使用 Anthropic SDK + 智谱 AI 兼容端点

set -e  # 遇到错误立即退出

echo "========================================"
echo "小红书财经爆款分析器 - 本地测试"
echo "========================================"
echo ""

# 检查环境变量
if [ -z "$ANTHROPIC_AUTH_TOKEN" ]; then
    echo "❌ 错误: 缺少 ANTHROPIC_AUTH_TOKEN 环境变量"
    echo ""
    echo "请先设置环境变量:"
    echo "  export ANTHROPIC_AUTH_TOKEN='ede5dcfb6ee24bc1abb5e6a14887d6c7.wPIlUa0hkFFD9mbM'"
    echo "  export ANTHROPIC_BASE_URL='https://open.bigmodel.cn/api/anthropic'"
    exit 1
fi

# 设置默认 BASE_URL
export ANTHROPIC_BASE_URL=${ANTHROPIC_BASE_URL:-"https://open.bigmodel.cn/api/anthropic"}

echo "✓ 环境变量配置:"
echo "  ANTHROPIC_AUTH_TOKEN: ${ANTHROPIC_AUTH_TOKEN:0:20}..."
echo "  ANTHROPIC_BASE_URL: $ANTHROPIC_BASE_URL"
echo ""

# 检查 cookies 文件
COOKIES_FILE=${1:-"/tmp/xhs_cookies.json"}

if [ ! -f "$COOKIES_FILE" ]; then
    echo "❌ 错误: Cookies 文件不存在: $COOKIES_FILE"
    echo ""
    echo "请先创建 cookies 文件:"
    echo "  1. 打开浏览器，登录小红书"
    echo "  2. 按 F12 打开开发者工具"
    echo "  3. 复制 cookies (a1, webId, web_session)"
    echo "  4. 保存为 JSON 文件: $COOKIES_FILE"
    echo ""
    echo "示例格式:"
    echo '  {"a1":"xxx","webId":"xxx","web_session":"xxx"}'
    exit 1
fi

echo "✓ Cookies 文件: $COOKIES_FILE"
echo ""

# 检查 xiaohongshu-mcp 是否安装
if ! command -v xiaohongshu-mcp &> /dev/null; then
    echo "❌ 错误: xiaohongshu-mcp 未安装"
    echo ""
    echo "请先安装:"
    echo "  npm install -g xiaohongshu-mcp-steve"
    exit 1
fi

# 检查 MCP Server 是否已运行
if curl -s http://localhost:18060/ > /dev/null 2>&1; then
    echo "✓ MCP Server 已在运行 (端口 18060)"
else
    echo "启动 MCP Server..."
    nohup xiaohongshu-mcp --port 18060 --headless --cookies "$COOKIES_FILE" > /tmp/mcp_server.log 2>&1 &
    MCP_PID=$!

    # 等待服务启动
    echo "等待 MCP Server 启动..."
    for i in {1..15}; do
        if curl -s http://localhost:18060/ > /dev/null 2>&1; then
            echo "✓ MCP Server 启动成功"
            break
        fi
        if [ $i -eq 15 ]; then
            echo "❌ MCP Server 启动失败"
            echo "查看日志: cat /tmp/mcp_server.log"
            exit 1
        fi
        sleep 1
        echo "  等待中... ($i/15)"
    done
fi

echo ""
echo "========================================"
echo "开始运行分析..."
echo "========================================"
echo ""

# 运行 agent
cd "$(dirname "$0")"
python scripts/agent_runner.py

echo ""
echo "========================================"
echo "测试完成!"
echo "========================================"
echo ""
echo "数据文件: data.json"
echo ""
echo "如需推送报告到微信，运行:"
echo "  python scripts/push_report.py --file data.json"
echo ""
