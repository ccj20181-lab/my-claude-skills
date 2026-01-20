#!/bin/bash

# 小红书 MCP 健康检查脚本
# 作者：幽浮喵
# 用途：检查并启动小红书 MCP 服务

MCP_PORT=18060
MCP_PROCESS="xiaohongshu-mcp"
MCP_BINARY="/Users/henry/.claude/xhs-topic-analyzer/bin/xiaohongshu-mcp-darwin-arm64"
LOG_FILE="/Users/henry/.claude/logs/mcp-check.log"

# 检查端口是否在监听
check_port() {
    lsof -i :$MCP_PORT > /dev/null 2>&1
    return $?
}

# 检查进程是否运行
check_process() {
    pgrep -f "$MCP_PROCESS" > /dev/null 2>&1
    return $?
}

# 启动 MCP 服务
start_mcp() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 启动小红书 MCP 服务..." >> "$LOG_FILE"
    nohup "$MCP_BINARY" -port :$MCP_PORT >> /Users/henry/.claude/logs/xiaohongshu-mcp-startup.log 2>&1 &
    sleep 2

    if check_port && check_process; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 小红书 MCP 服务启动成功" >> "$LOG_FILE"
        return 0
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 小红书 MCP 服务启动失败" >> "$LOG_FILE"
        return 1
    fi
}

# 主检查逻辑
if ! check_port || ! check_process; then
    start_mcp
fi

exit 0
