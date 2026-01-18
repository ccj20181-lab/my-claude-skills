# Xiaohongshu MCP Server 完整配置和运行计划

## 📋 项目概述

### 项目信息
- **GitHub 仓库**: https://github.com/xpzouying/xiaohongshu-mcp
- **官方博客**: https://www.haha.ai/xiaohongshu-mcp
- **星标数**: 7.9k+（活跃维护）
- **开发语言**: Go (97.9%)
- **部署方式**: 二进制文件 / Docker / 源码编译

### 与 rednote-mcp 的区别

| 特性 | xiaohongshu-mcp | rednote-mcp |
|------|----------------|-------------|
| 开发者 | xpzouying | 未明确 |
| 维护状态 | ✅ 活跃维护 | 基础功能 |
| 通信方式 | HTTP (端口 18060) | stdio |
| 功能完整性 | 完整（发布、搜索、获取详情） | 基础搜索和登录 |
| 数据获取 | 支持发布时间、粉丝数等完整数据 | 缺少发布时间 |

---

## ✅ 当前状态

### 已安装组件
1. ✅ **xiaohongshu-mcp 二进制文件**: `/usr/local/bin/xiaohongshu-mcp`
2. ✅ **xiaohongshu-login 登录工具**: `/Users/henry/.claude/skills/xhs-topic-analyzer/bin/xiaohongshu-login-darwin-arm64`
3. ✅ **Claude Code 配置**: 已在 `config.json` 中配置 `rednote` MCP Server

### 未配置项
1. ❌ **Xiaohongshu MCP Server 未运行**: 端口 18060 未被占用
2. ❌ **未在 Claude Code 中配置**: 缺少 xiaohongshu-mcp 的 MCP 配置
3. ❌ **未登录**: 未执行登录初始化

---

## 🎯 解决方案

### 方案概述
配置并启动 Xiaohongshu MCP Server，确保能够：
1. 成功登录小红书账号
2. 正常提供 MCP API 服务
3. 获取完整的笔记数据（包括发布时间）
4. 与 xhs-topic-analyzer skill 集成

---

## 📝 实施步骤

### 阶段 1：首次登录（必须）

**1.1 运行登录工具**
```bash
cd /Users/henry/.claude/skills/xhs-topic-analyzer/bin
./xiaohongshu-login-darwin-arm64
```

**1.2 登录流程**
1. 工具会自动打开无头浏览器
2. 跳转到小红书登录页面
3. 手动完成登录操作（扫码或账号密码）
4. 登录成功后自动保存 Cookie

**1.3 Cookie 存储位置**
```bash
# Cookie 会保存在当前目录的 cookies 文件夹
/Users/henry/.claude/skills/xhs-topic-analyzer/bin/cookies/
```

---

### 阶段 2：启动 MCP Server

**2.1 启动服务（后台运行）**
```bash
cd /Users/henry/.claude/skills/xhs-topic-analyzer/bin

# 方式1：前台运行（测试用）
./xiaohongshu-mcp-darwin-arm64 -headless=true -port=:18060

# 方式2：后台运行（推荐）
nohup ./xiaohongshu-mcp-darwin-arm64 -headless=true -port=:18060 > /tmp/xiaohongshu-mcp.log 2>&1 &

# 方式3：使用 screen 或 tmux
screen -S xiaohongshu-mcp
./xiaohongshu-mcp-darwin-arm64 -headless=true -port=:18060
# Ctrl+A+D 退出 screen
```

**2.2 验证服务运行**
```bash
# 检查端口占用
lsof -i :18060

# 测试 HTTP 接口
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}' \
  http://localhost:18060/mcp

# 查看日志（如果使用后台运行）
tail -f /tmp/xiaohongshu-mcp.log
```

---

### 阶段 3：在 Claude Code 中配置

**3.1 添加 MCP 配置**
```bash
# 使用 Claude Code CLI 添加
claude config mcp add xiaohongshu-mcp http://localhost:18060/mcp

# 或手动编辑配置文件
```

**3.2 手动编辑配置文件**
编辑 `/Users/henry/.claude/config.json`：

```json
{
  "primaryApiKey": "zcf",
  "mcpServers": {
    "macos_automator": {
      "command": "npx",
      "args": ["-y", "@steipete/macos-automator-mcp@latest"]
    },
    "rednote": {
      "command": "rednote-mcp",
      "args": ["--stdio"]
    },
    "xiaohongshu-mcp": {
      "url": "http://localhost:18060/mcp",
      "description": "小红书内容发布和数据获取服务"
    }
  }
}
```

**3.3 启用权限**
编辑 `/Users/henry/.claude/settings.json`：

```json
{
  "permissions": {
    "allow": [
      // ... 其他权限
      "mcp__xiaohongshu"  // 确保包含此权限
    ]
  }
}
```

**3.4 重启 Claude Code**
配置修改后需要重启 Claude Code 以加载新的 MCP Server

---

### 阶段 4：验证功能

**4.1 测试登录状态**
在 Claude Code 中调用：
```javascript
mcp__xiaohongshu__check_login_status()
```

**4.2 测试搜索功能**
```javascript
mcp__xiaohongshu__search_feeds({
  keyword: "股票",
  page: 1,
  page_size: 20
})
```

**4.3 测试获取详情**
```javascript
mcp__xiaohongshu__get_feed_detail({
  url: "小红书笔记URL"
})
```

**4.4 验证返回数据**
检查返回的笔记是否包含：
- ✅ publish_time（发布时间）
- ✅ liked_count（点赞数）
- ✅ collected_count（收藏数）
- ✅ comment_count（评论数）
- ✅ user（用户信息，包括粉丝数）

---

## 🔧 Xiaohongshu MCP Server API 接口

### 工具列表

| 工具名 | 功能 | 参数 |
|--------|------|------|
| `check_login_status` | 检查登录状态 | 无 |
| `publish_content` | 发布图文内容 | title, content, images[] |
| `publish_with_video` | 发布视频内容 | title, content, video_path |
| `list_feeds` | 获取推荐列表 | page, page_size |
| `search_feeds` | 搜索内容 | keyword, page, page_size |
| `get_feed_detail` | 获取帖子详情 | url, xsec_token |
| `post_comment_to_feed` | 发表评论 | note_id, xsec_token, comment_text |
| `user_profile` | 获取用户信息 | user_id, xsec_token |

### 关键数据结构

**笔记详情示例**：
```json
{
  "title": "股票入门指南",
  "desc": "内容描述",
  "type": "normal",
  "liked_count": 2500,
  "collected_count": 500,
  "comment_count": 120,
  "share_count": 30,
  "user": {
    "nickname": "财经博主",
    "fan_id": "粉丝数",
    "fans_count": 15000
  },
  "publish_time": "2026-01-15T10:30:00Z",  // ✅ 包含发布时间
  "time": "3天前",
  "note_id": "笔记ID"
}
```

---

## 🚀 启动脚本

### 创建系统服务（可选）

**3.1 创建启动脚本**
```bash
cat > /usr/local/bin/start-xiaohongshu-mcp.sh << 'EOF'
#!/bin/bash
cd /Users/henry/.claude/skills/xhs-topic-analyzer/bin
nohup ./xiaohongshu-mcp-darwin-arm64 -headless=true -port=:18060 > /tmp/xiaohongshu-mcp.log 2>&1 &
echo "Xiaohongshu MCP Server 已启动"
EOF

chmod +x /usr/local/bin/start-xiaohongshu-mcp.sh
```

**3.2 创建停止脚本**
```bash
cat > /usr/local/bin/stop-xiaohongshu-mcp.sh << 'EOF'
#!/bin/bash
killall xiaohongshu-mcp-darwin-arm64
echo "Xiaohongshu MCP Server 已停止"
EOF

chmod +x /usr/local/bin/stop-xiaohongshu-mcp.sh
```

**3.3 创建 macOS Launch Agent（开机自启）**
```bash
cat > ~/Library/LaunchAgents/com.xiaohongshu.mcp.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.xiaohongshu.mcp</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/henry/.claude/skills/xhs-topic-analyzer/bin/xiaohongshu-mcp-darwin-arm64</string>
        <string>-headless=true</string>
        <string>-port=:18060</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/xiaohongshu-mcp.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/xiaohongshu-mcp.error.log</string>
</dict>
</plist>
EOF

# 加载服务
launchctl load ~/Library/LaunchAgents/com.xiaohongshu.mcp.plist

# 启动服务
launchctl start com.xiaohongshu.mcp
```

---

## 📊 与 xhs-topic-analyzer 集成

### 修改 SKILL.md

在 `/Users/henry/.claude/skills/xhs-topic-analyzer/SKILL.md` 中更新：

```markdown
## 阶段1：数据采集（使用 Xiaohongshu MCP Server）

启动 Subagent 搜索关键词并提取数据：

\`\`\`python
Task(subagent_type="general-purpose",
     prompt="""请执行以下任务：

## 🎯 任务目标
使用 Xiaohongshu MCP Server 搜索近期爆款笔记

## ⚠️ 关键要求
- 必须调用 mcp__xiaohongshu__search_feeds API
- 每个关键词搜索 2 页（每页 20 条）
- 筛选条件：3天内 + 点赞≥2000

## 步骤 1：读取配置
读取 config.json 获取关键词列表

## 步骤 2：搜索每个关键词
对每个关键词调用：
\`\`\`python
mcp__xiaohongshu__search_feeds({
  "keyword": "金融",
  "page": 1,
  "page_size": 20
})
\`\`\`

## 步骤 3：提取完整数据
从搜索结果中提取：
- title, desc, publish_time  ✅ 包含发布时间！
- liked_count, collected_count, comment_count
- user.nickname, user.fans_count  ✅ 包含粉丝数！

## 步骤 4：保存数据
保存到 data.json（简化格式）
""")
\`\`\`
```

---

## ⚠️ 注意事项

### 1. 端口冲突
- 默认端口：18060
- 如被占用，使用 `-port` 参数指定其他端口

### 2. Cookie 过期
- Cookie 有效期约 7-30 天
- 过期后需要重新运行 `xiaohongshu-login`

### 3. 并发限制
- 建议每秒请求不超过 5 次
- 避免触发小红书反爬机制

### 4. 浏览器依赖
- 首次运行会自动下载 Chromium（约 150MB）
- 确保网络通畅

### 5. 发布限制
- 标题不超过 20 字
- 正文不超过 1000 字
- 建议每天发帖不超过 50 篇

---

## 🔍 故障排除

### 问题 1：无法连接到 MCP Server
```bash
# 检查服务是否运行
ps aux | grep xiaohongshu-mcp

# 检查端口
lsof -i :18060

# 查看日志
tail -f /tmp/xiaohongshu-mcp.log
```

### 问题 2：登录失败
```bash
# 清除 Cookie 重新登录
rm -rf /Users/henry/.claude/skills/xhs-topic-analyzer/bin/cookies/
./xiaohongshu-login-darwin-arm64
```

### 问题 3：搜索无结果
- 检查关键词是否正确
- 确认已登录
- 查看服务器日志

### 问题 4：返回数据缺少发布时间
- 确认使用的是 `xiaohongshu-mcp` 而不是 `rednote-mcp`
- 检查 API 返回的原始数据
- 查看 GitHub Issues 是否有相关问题

---

## 📝 执行命令清单

```bash
# 1. 首次登录
cd /Users/henry/.claude/skills/xhs-topic-analyzer/bin
./xiaohongshu-login-darwin-arm64

# 2. 启动 MCP Server（后台运行）
nohup ./xiaohongshu-mcp-darwin-arm64 -headless=true -port=:18060 > /tmp/xiaohongshu-mcp.log 2>&1 &

# 3. 验证服务
lsof -i :18060
curl -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}' \
  http://localhost:18060/mcp

# 4. 配置 Claude Code（手动编辑 config.json）
# 添加 xiaohongshu-mcp 配置

# 5. 启用权限（手动编辑 settings.json）
# 添加 mcp__xiaohongshu 权限

# 6. 重启 Claude Code

# 7. 在 Claude Code 中测试
# mcp__xiaohongshu__check_login_status()
# mcp__xiaohongshu__search_feeds({keyword: "股票", page: 1, page_size: 20})
```

---

## ✅ 验证标准

### 成功标准
1. ✅ MCP Server 在端口 18060 正常运行
2. ✅ 登录状态显示为已登录
3. ✅ 搜索功能返回完整数据（包括发布时间和粉丝数）
4. ✅ 可以获取笔记详情
5. ✅ xhs-topic-analyzer skill 能够正常工作

### 测试用例
```javascript
// 测试 1：检查登录状态
mcp__xiaohongshu__check_login_status()
// 期望返回：{ logged_in: true }

// 测试 2：搜索关键词
mcp__xiaohongshu__search_feeds({
  keyword: "股票",
  page: 1,
  page_size: 5
})
// 期望返回：包含 publish_time 字段的笔记数组

// 测试 3：获取详情
mcp__xiaohongshu__get_feed_detail({
  url: "小红书笔记URL"
})
// 期望返回：完整的笔记信息，包括发布时间和用户粉丝数
```

---

## 🎯 下一步

配置完成后，可以：
1. 更新 xhs-topic-analyzer skill 使用 xiaohongshu-mcp
2. 实现完整的爆款笔记筛选（3天内 + 2000赞以上）
3. 自动化选题分析和报告生成
4. 集成微信推送功能

---

## 📚 参考资源

- **GitHub 仓库**: https://github.com/xpzouying/xiaohongshu-mcp
- **官方文档**: https://www.haha.ai/xiaohongshu-mcp
- **疑难杂症**: https://github.com/xpzouying/xiaohongshu-mcp/issues/56
- **n8n 集成教程**: https://github.com/xpzouying/xiaohongshu-mcp/blob/main/examples/n8n/README.md
