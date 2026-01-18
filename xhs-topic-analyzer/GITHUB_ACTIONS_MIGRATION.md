# xhs-topic-analyzer GitHub Actions 迁移方案

## 📋 目录
- [技术可行性分析](#技术可行性分析)
- [所需 API 和凭证清单](#所需-api-和凭证清单)
- [改造方案](#改造方案)
- [部署步骤](#部署步骤)
- [测试和验证](#测试和验证)

---

## 🔍 技术可行性分析

### ✅ 完全可行

这个 skill 迁移到 GitHub Actions **完全可行**，理由如下：

#### 1. **核心依赖分析**

| 组件 | 当前实现 | GitHub Actions 支持 | 可行性 |
|:---|:---|:---|:---:|
| Claude Agent SDK | ❌ 未使用 | ✅ 支持 | ✅ |
| 小红书 MCP | mcp__xiaohongshu | ✅ 可通过 HTTP MCP | ✅ |
| Python 环境 | Python 3.9+ | ✅ 原生支持 | ✅ |
| 定时执行 | ❌ 手动触发 | ✅ cron 支持 | ✅ |
| 微信推送 | PushPlus API | ✅ HTTP API | ✅ |

#### 2. **技术栈兼容性**

- **Python 脚本**: 完全兼容 GitHub Actions
- **HTTP API 调用**: 小红书搜索、微信推送都是 HTTP API
- **定时任务**: GitHub Actions 支持 cron 表达式
- **Claude Agent SDK**: GitHub Actions 官方支持

#### 3. **数据流分析**

```
GitHub Actions (定时触发)
    ↓
Claude Agent SDK (调用 Agent)
    ↓
小红书 MCP HTTP Server (搜索数据)
    ↓
Python 脚本处理 (分析、生成报告)
    ↓
PushPlus API (推送到微信)
```

---

## 🔑 所需 API 和凭证清单

### 必需配置的 GitHub Secrets

| Secret 名称 | 用途 | 获取方式 | 示例值 |
|:---|:---|:---|:---|
| `ANTHROPIC_API_KEY` | Claude API 调用 | [Anthropic Console](https://console.anthropic.com/) | `sk-ant-api03-...` |
| `XHS_COOKIES` | 小红书登录凭证 | 浏览器导出 cookies | JSON 格式 |
| `WECHAT_PUSH_TOKEN` | 微信推送令牌 | [PushPlus](http://www.pushplus.plus/) | `a6443f3a5d0f4b11a42c281f831b5c15` |

### 可选配置的 GitHub Variables

| Variable 名称 | 用途 | 默认值 | 说明 |
|:---|:---|:---|:---|
| `SEARCH_KEYWORDS` | 搜索关键词 | 见 config.json | JSON 数组 |
| `MIN_LIKES` | 最小点赞数 | `2000` | 筛选标准 |
| `PUBLISH_TIME` | 发布时间范围 | `3d` | 3天内 |

---

## 🛠️ 改造方案

### 方案概述

**优先使用 Claude Agent SDK + MCP HTTP Server 方案**

#### 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub Actions                        │
│  ┌───────────────────────────────────────────────────┐  │
│  │  1. Workflow 定时触发 (cron: 0 9 * * *)         │  │
│  │  2. 设置 Python 环境 (Python 3.11)               │  │
│  │  3. 启动 xiaohongshu-mcp HTTP Server            │  │
│  │  4. 调用 Claude Agent SDK                        │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              Claude Agent SDK (Python)                   │
│  ┌───────────────────────────────────────────────────┐  │
│  │  使用 Anthropic SDK 调用 Claude API              │  │
│  │  传递任务: "搜索小红书爆款笔记并分析"            │  │
│  │  工具配置: xiaohongshu-mcp (HTTP)                │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│           Claude API + xiaohongshu-mcp                   │
│  ┌───────────────────────────────────────────────────┐  │
│  │  1. Claude 调用 mcp__xiaohongshu__search_feeds   │  │
│  │  2. 搜索 10 个关键词                             │  │
│  │  3. 合并、去重、筛选数据                         │  │
│  │  4. 返回符合条件的笔记数据                       │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                Python 后处理脚本                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  1. validate_data.py - 数据校验                  │  │
│  │  2. push_report.py - 生成报告并推送              │  │
│  │  3. PushPlus API - 推送到微信                    │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 关键技术点

#### 1. **xiaohongshu-mcp HTTP Server**

在 GitHub Actions 中启动 MCP HTTP Server:

```yaml
- name: Start xiaohongshu-mcp server
  run: |
    pip install xiaohongshu-mcp
    # 使用 cookies 登录
    echo '${{ secrets.XHS_COOKIES }}' > /tmp/xhs_cookies.json
    nohup xiaohongshu-mcp --port 3000 --cookies /tmp/xhs_cookies.json &
    sleep 5
```

#### 2. **Claude Agent SDK 调用**

```python
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# 配置 MCP 工具
tools = [{
    "type": "computer_20241022",
    "name": "mcp__xiaohongshu__search_feeds",
    "mcp_server": "http://localhost:3000"
}]

# 调用 Agent
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,
    tools=tools,
    messages=[{
        "role": "user",
        "content": """请搜索小红书财经赛道爆款笔记..."""
    }]
)
```

#### 3. **数据持久化**

由于 GitHub Actions 是无状态的，数据处理流程：

```
Agent 输出 → data.json (临时文件)
          ↓
validate_data.py (校验)
          ↓
push_report.py (生成报告)
          ↓
PushPlus API (推送微信)
          ↓
自动清理临时文件
```

---

## 📂 文件结构

```
.github/
└── workflows/
    └── xhs-daily-report.yml       # GitHub Actions 工作流

scripts/
├── agent_runner.py                # 新增：Claude Agent SDK 调用脚本
├── validate_data.py               # 现有：数据校验
└── push_report.py                 # 现有：报告推送

config.json                        # 配置文件（不包含敏感信息）
requirements.txt                   # Python 依赖
```

---

## 🚀 改造步骤

### 步骤 1: 创建 Agent Runner 脚本

**文件**: `scripts/agent_runner.py`

功能:
- 使用 Claude Agent SDK 调用 Claude API
- 配置 xiaohongshu-mcp 工具
- 执行搜索任务并保存数据

### 步骤 2: 创建 GitHub Actions Workflow

**文件**: `.github/workflows/xhs-daily-report.yml`

功能:
- 定时触发 (每天早上 9 点)
- 启动 MCP Server
- 运行 Agent Runner
- 执行数据处理和推送

### 步骤 3: 配置环境变量

在 GitHub 仓库设置:
- Secrets: 敏感凭证
- Variables: 配置参数

### 步骤 4: 测试验证

- 手动触发测试
- 检查日志输出
- 验证微信推送

---

## 📊 成本估算

### Claude API 成本

假设每天执行一次:

| 项目 | 用量 | 单价 | 月成本 |
|:---|:---|:---|:---|
| Input tokens | ~2000 tokens/次 × 30天 | $3/M tokens | $0.18 |
| Output tokens | ~4000 tokens/次 × 30天 | $15/M tokens | $1.80 |
| **总计** | | | **$1.98/月** |

### GitHub Actions 成本

- **Public 仓库**: 完全免费
- **Private 仓库**: 每月 2000 分钟免费，单次执行约 5 分钟
  - 30 次执行 = 150 分钟/月
  - **完全在免费额度内**

### PushPlus 成本

- 免费版：每天 200 次推送
- **成本**: $0

**总成本**: ~$2/月 (仅 Claude API)

---

## ⚙️ 配置参数说明

### 1. ANTHROPIC_API_KEY

**用途**: Claude API 调用凭证

**获取方式**:
1. 访问 [Anthropic Console](https://console.anthropic.com/)
2. 注册/登录账号
3. 进入 API Keys 页面
4. 创建新的 API Key
5. 复制 key (格式: `sk-ant-api03-...`)

**安全提示**:
- 切勿提交到代码仓库
- 仅在 GitHub Secrets 中配置

### 2. XHS_COOKIES

**用途**: 小红书登录状态

**获取方式**:
1. 浏览器登录小红书网页版
2. 打开开发者工具 (F12)
3. 进入 Application/Storage → Cookies
4. 导出关键 cookies:
   ```json
   {
     "a1": "...",
     "webId": "...",
     "web_session": "..."
   }
   ```

**格式**: JSON 字符串

### 3. WECHAT_PUSH_TOKEN

**用途**: 微信推送令牌

**获取方式**:
1. 访问 [PushPlus](http://www.pushplus.plus/)
2. 微信扫码登录
3. 复制 Token

**示例**: `a6443f3a5d0f4b11a42c281f831b5c15`

---

## 🎯 优势分析

### 相比本地执行的优势

| 对比项 | 本地执行 | GitHub Actions |
|:---|:---|:---|
| 定时执行 | ❌ 需要手动 | ✅ 自动 cron |
| 环境依赖 | ❌ 本地环境 | ✅ 云端隔离 |
| 成本 | 💻 本地资源 | 💰 约 $2/月 |
| 可靠性 | ⚠️ 本地在线 | ✅ 云端高可用 |
| 日志记录 | ❌ 手动查看 | ✅ 自动归档 |
| 扩展性 | ⚠️ 有限 | ✅ 易扩展 |

---

## 📝 注意事项

### 1. **小红书 Cookies 有效期**

- Cookies 可能过期 (通常 7-30 天)
- 建议定期更新 `XHS_COOKIES` Secret
- 可添加告警机制检测登录失败

### 2. **GitHub Actions 限制**

- 单次执行最长 6 小时
- 日志保留 90 天
- Private 仓库免费额度: 2000 分钟/月

### 3. **Claude API 限制**

- Rate Limit: 根据套餐不同
- 建议监控 API 使用量
- 可配置重试机制

### 4. **数据安全**

- 所有敏感信息存储在 GitHub Secrets
- 临时文件在执行结束后自动清理
- 不在日志中输出敏感信息

---

## 🔧 故障排查

### 问题 1: MCP Server 启动失败

**现象**: Agent 无法连接到 MCP Server

**解决**:
```bash
# 检查端口占用
netstat -tuln | grep 3000

# 查看 MCP Server 日志
cat /tmp/mcp_server.log
```

### 问题 2: 小红书登录失效

**现象**: 搜索返回空结果或登录错误

**解决**:
1. 更新 `XHS_COOKIES` Secret
2. 检查 cookies 格式是否正确

### 问题 3: 微信推送失败

**现象**: 报告生成但未收到微信消息

**解决**:
1. 检查 `WECHAT_PUSH_TOKEN` 是否正确
2. 验证 PushPlus 服务状态
3. 检查推送限额

---

## 📚 相关文档

- [Claude Agent SDK 文档](https://docs.anthropic.com/claude/docs/agents)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [PushPlus 文档](http://www.pushplus.plus/doc/)
- [xiaohongshu-mcp 文档](https://github.com/...)

---

## 📅 版本历史

### V1.0 (2026-01-18)
- ✅ 初始迁移方案
- ✅ Claude Agent SDK 集成
- ✅ MCP HTTP Server 支持
- ✅ 定时任务配置

---

**文档状态**: ✅ 完成

**下一步**: 开始实施改造方案
