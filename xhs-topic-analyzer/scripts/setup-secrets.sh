#!/bin/bash
# GitHub Secrets 自动配置脚本
# 功能：一次性配置所有 GitHub Actions Secrets
# 作者：幽浮喵
# 日期：2025-01-20

set -e  # 遇到错误立即退出

REPO="ccj20181-lab/my-claude-skills"
COOKIES_FILE="/Users/henry/.claude/skills/xhs-topic-analyzer/bin/cookies.json"

echo "🔧 开始配置 GitHub Secrets for $REPO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. 配置 ANTHROPIC_AUTH_TOKEN
echo "📝 配置 ANTHROPIC_AUTH_TOKEN..."
echo "ede5dcfb6ee24bc1abb5e6a14887d6c7b.wPIlUa0hkFFD9mbM" | \
    gh secret set ANTHROPIC_AUTH_TOKEN --repo "$REPO"
echo "✅ ANTHROPIC_AUTH_TOKEN 已配置"

# 2. 配置 ANTHROPIC_BASE_URL
echo "📝 配置 ANTHROPIC_BASE_URL..."
echo "https://open.bigmodel.cn/api/anthropic" | \
    gh secret set ANTHROPIC_BASE_URL --repo "$REPO"
echo "✅ ANTHROPIC_BASE_URL 已配置"

# 3. 配置 WECHAT_PUSH_TOKEN
echo "📝 配置 WECHAT_PUSH_TOKEN..."
echo "a6443f3a5d0f4b11a42c281f831b5c15" | \
    gh secret set WECHAT_PUSH_TOKEN --repo "$REPO"
echo "✅ WECHAT_PUSH_TOKEN 已配置"

# 4. 配置 XHS_COOKIES
echo "📝 配置 XHS_COOKIES..."
if [ ! -f "$COOKIES_FILE" ]; then
    echo "❌ Cookies 文件不存在: $COOKIES_FILE"
    exit 1
fi
gh secret set XHS_COOKIES --repo "$REPO" < "$COOKIES_FILE"
echo "✅ XHS_COOKIES 已配置"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 所有 Secrets 配置完成！"
echo ""
echo "📋 当前已配置的 Secrets："
gh secret list --repo "$REPO"
