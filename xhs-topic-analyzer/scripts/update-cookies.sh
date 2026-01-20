#!/bin/bash
# 小红书 Cookies 更新脚本
# 功能：快速更新 GitHub Secrets 中的小红书 Cookies
# 使用场景：当 Cookies 过期时（每 7-30 天）
# 作者：幽浮喵
# 日期：2025-01-20

set -e  # 遇到错误立即退出

REPO="ccj20181-lab/my-claude-skills"
COOKIES_FILE="/Users/henry/.claude/skills/xhs-topic-analyzer/bin/cookies.json"

echo "🍪 小红书 Cookies 更新工具"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查 Cookies 文件是否存在
if [ ! -f "$COOKIES_FILE" ]; then
    echo "❌ Cookies 文件不存在: $COOKIES_FILE"
    echo ""
    echo "💡 请先按照以下步骤获取新的 Cookies："
    echo "   1. 在浏览器中登录小红书"
    echo "   2. 打开开发者工具 (F12)"
    echo "   3. 切换到 Network 标签"
    echo "   4. 刷新页面，找到任意请求"
    echo "   5. 复制 Cookie 值并保存到 cookies.json"
    echo ""
    exit 1
fi

echo "📁 找到 Cookies 文件: $COOKIES_FILE"
echo "🔄 开始更新 XHS_COOKIES Secret..."

# 更新 Secret
gh secret set XHS_COOKIES --repo "$REPO" < "$COOKIES_FILE"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Cookies 已成功更新到 GitHub Secrets"
echo ""
echo "💡 提示：你可以手动测试 Workflow 是否正常运行"
echo "   gh workflow run xhs-daily-report-claude.yml --repo $REPO"
