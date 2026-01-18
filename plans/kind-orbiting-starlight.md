# xhs-topic-analyzer GitHub Actions 迁移实施计划

## 📋 项目概述

将 xhs-topic-analyzer skill 迁移到 GitHub Actions，实现云端定时自动执行。

### 核心目标
- ✅ 每天自动搜索小红书财经爆款笔记
- ✅ 深度分析选题并生成报告
- ✅ 自动推送到微信
- ✅ 无需本地环境，完全云端运行

---

## 🔍 现状分析

### 当前 Skill 架构

```
手动触发 (本地)
    ↓
Task Agent (Subagent)
    ↓ 调用 mcp__xiaohongshu__search_feeds
xiaohongshu-mcp (本地 MCP Server)
    ↓ 返回搜索结果
保存 data.json
    ↓
validate_config.py (配置校验)
    ↓
validate_data.py (数据校验)
    ↓
push_report.py (生成报告 + 推送微信)
    ↓ 调用 PushPlus API
微信接收报告
```

### 关键文件清单

| 文件 | 用途 | 迁移策略 |
|:---|:---|:---|
| `skill.md` | Skill 文档 | 📖 参考，不迁移 |
| `config.json` | 配置文件 | ⚙️ 拆分为环境变量 |
| `scripts/validate_config.py` | 配置校验 | ✅ 保留使用 |
| `scripts/validate_data.py` | 数据校验 | ✅ 保留使用 |
| `scripts/push_report.py` | 报告生成推送 | ✅ 保留使用 |

### 外部依赖清单

| 依赖 | 类型 | 凭证需求 |
|:---|:---|:---|
| Claude API | HTTP API | `ANTHROPIC_API_KEY` |
| xiaohongshu-mcp | MCP Server | `XHS_COOKIES` (登录) |
| PushPlus | HTTP API | `WECHAT_PUSH_TOKEN` |

---

## 🎯 迁移方案

### 技术选型

**优先方案：Claude Agent SDK + MCP HTTP Server**

#### 理由
1. ✅ GitHub Actions 官方支持 Claude Agent SDK
2. ✅ xiaohongshu-mcp 支持 HTTP Server 模式
3. ✅ 代码改动最小，复用现有脚本
4. ✅ 调试方便，日志清晰

#### 替代方案（不推荐）
- ❌ 直接调用小红书 API：需要逆向工程，不稳定
- ❌ 使用 Selenium 爬虫：资源占用大，GitHub Actions 限制多

### 新架构设计

```
GitHub Actions (cron 定时触发)
    ↓
Step 1: 准备环境
  - 安装 Python 3.11
  - 安装依赖 (anthropic, requests, etc.)
    ↓
Step 2: 启动 xiaohongshu-mcp HTTP Server
  - 使用 secrets.XHS_COOKIES 登录
  - 监听 localhost:3000
  - 健康检查
    ↓
Step 3: 运行 Claude Agent Runner (新增)
  - 使用 Anthropic SDK
  - 配置 MCP 工具 (http://localhost:3000)
  - 执行搜索任务
  - 输出 data.json
    ↓
Step 4: 数据校验
  - validate_config.py (可选)
  - validate_data.py
    ↓
Step 5: 生成报告并推送
  - push_report.py --file data.json
  - 调用 PushPlus API
    ↓
Step 6: 清理
  - 停止 MCP Server
  - 删除临时文件
```

---

## 📝 实施步骤

### Phase 1: 创建 Agent Runner 脚本

**文件**: `scripts/agent_runner.py`

**功能**:
- 使用 Anthropic SDK 调用 Claude API
- 配置 xiaohongshu-mcp HTTP 工具
- 传递搜索任务
- 接收并保存数据到 `data.json`

**关键代码逻辑**:
```python
import os
import json
from anthropic import Anthropic

def run_agent():
    # 1. 初始化 Anthropic 客户端
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # 2. 读取配置
    config = load_config()
    keywords = config.get("keywords", [])

    # 3. 构建任务提示词
    task_prompt = f"""
    请搜索小红书财经赛道爆款笔记：

    关键词: {keywords}
    筛选条件:
    - 发布时间: 3天内
    - 点赞数: ≥2000

    对每个关键词调用 mcp__xiaohongshu__search_feeds
    参数:
    - keyword: <关键词>
    - filters:
      - sort_by: "最多点赞"
      - publish_time: "一周内"
      - note_type: "不限"

    合并去重，筛选符合条件的笔记，保存到 data.json
    """

    # 4. 调用 Claude API
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        tools=[{
            "type": "custom",
            "name": "mcp__xiaohongshu__search_feeds",
            "mcp_server_url": "http://localhost:3000"
        }],
        messages=[{"role": "user", "content": task_prompt}]
    )

    # 5. 提取并保存数据
    save_data(response, "data.json")
```

**依赖**:
- `anthropic` >= 0.18.0
- `requests`

### Phase 2: 创建 GitHub Actions Workflow

**文件**: `.github/workflows/xhs-daily-report.yml`

**触发条件**:
- 定时: 每天 UTC 01:00 (北京时间 09:00)
- 手动: workflow_dispatch

**环境变量**:
```yaml
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  XHS_COOKIES: ${{ secrets.XHS_COOKIES }}
  WECHAT_PUSH_TOKEN: ${{ secrets.WECHAT_PUSH_TOKEN }}
```

**关键步骤**:

1. **Checkout 代码**
   ```yaml
   - uses: actions/checkout@v4
   ```

2. **设置 Python 环境**
   ```yaml
   - uses: actions/setup-python@v5
     with:
       python-version: '3.11'
   ```

3. **安装依赖**
   ```yaml
   - run: pip install -r requirements.txt
   ```

4. **启动 xiaohongshu-mcp Server**
   ```yaml
   - name: Start MCP Server
     run: |
       echo '${{ secrets.XHS_COOKIES }}' > /tmp/xhs_cookies.json
       nohup xiaohongshu-mcp --port 3000 --cookies /tmp/xhs_cookies.json > /tmp/mcp.log 2>&1 &
       sleep 5
       curl http://localhost:3000/health || echo "MCP Server started"
   ```

5. **运行 Agent Runner**
   ```yaml
   - name: Run Agent
     run: python scripts/agent_runner.py
   ```

6. **数据校验**
   ```yaml
   - name: Validate Data
     run: python scripts/validate_data.py data.json
   ```

7. **推送报告**
   ```yaml
   - name: Push Report
     run: python scripts/push_report.py --file data.json
   ```

8. **清理**
   ```yaml
   - name: Cleanup
     if: always()
     run: |
       pkill -f xiaohongshu-mcp || true
       rm -f /tmp/xhs_cookies.json data.json
   ```

### Phase 3: 创建 Requirements 文件

**文件**: `requirements.txt`

```
anthropic>=0.18.0
requests>=2.31.0
xiaohongshu-mcp>=1.0.0
```

### Phase 4: 更新 Config 文件

**文件**: `config.json`

**改动**:
- 移除敏感信息 `wechat_push_token`
- 保留关键词和筛选配置

**新内容**:
```json
{
    "keywords": [
        "金融",
        "金融知识",
        "财经",
        "财经热点",
        "理财",
        "理财知识",
        "基金",
        "股票",
        "存钱",
        "投资理财"
    ],
    "filters": {
        "publish_time": "3d",
        "min_likes": 2000
    },
    "exclude_keywords": [...]
}
```

### Phase 5: 创建部署文档

**文件**: `DEPLOYMENT.md`

**内容**:
1. GitHub Secrets 配置步骤
2. 如何获取各个凭证
3. 测试和验证流程
4. 故障排查指南

---

## 🔐 GitHub Secrets 配置清单

### 必需 Secrets

| Secret 名称 | 用途 | 获取方式 | 格式 |
|:---|:---|:---|:---|
| `ANTHROPIC_API_KEY` | Claude API 调用 | [Anthropic Console](https://console.anthropic.com/) | `sk-ant-api03-...` |
| `XHS_COOKIES` | 小红书登录 | 浏览器导出 cookies | JSON 字符串 |
| `WECHAT_PUSH_TOKEN` | 微信推送 | [PushPlus](http://www.pushplus.plus/) | 字符串 |

### 配置步骤

1. 进入 GitHub 仓库 Settings → Secrets and variables → Actions
2. 点击 "New repository secret"
3. 添加上述 3 个 Secrets

---

## ✅ 验证计划

### 本地测试

1. **测试 Agent Runner**
   ```bash
   # 启动 MCP Server
   xiaohongshu-mcp --port 3000 --cookies cookies.json &

   # 运行 Agent
   export ANTHROPIC_API_KEY="sk-ant-..."
   python scripts/agent_runner.py

   # 验证 data.json 生成
   ls -lh data.json
   ```

2. **测试完整流程**
   ```bash
   # 校验数据
   python scripts/validate_data.py data.json

   # 推送报告
   export WECHAT_PUSH_TOKEN="..."
   python scripts/push_report.py --file data.json --no-cleanup
   ```

### GitHub Actions 测试

1. **手动触发测试**
   - 进入 Actions 页面
   - 选择 workflow
   - 点击 "Run workflow"

2. **检查日志**
   - 每个 step 的输出
   - MCP Server 日志
   - Agent 执行结果

3. **验证推送**
   - 检查微信是否收到报告
   - 验证报告内容完整性

---

## 📊 风险评估

### 高风险项

| 风险 | 影响 | 缓解措施 |
|:---|:---|:---|
| XHS_COOKIES 过期 | 搜索失败 | 定期更新 + 告警通知 |
| Claude API 限流 | 执行失败 | 添加重试 + 监控用量 |
| MCP Server 启动失败 | 无法搜索 | 健康检查 + 详细日志 |

### 中风险项

| 风险 | 影响 | 缓解措施 |
|:---|:---|:---|
| 网络超时 | 偶尔失败 | 增加超时时间 + 重试 |
| 数据格式变化 | 校验失败 | 兼容性处理 + 版本锁定 |

---

## 💰 成本估算

### Claude API
- 每天 1 次执行
- 约 2000 input tokens + 4000 output tokens
- **月成本**: ~$2

### GitHub Actions
- Public 仓库: 免费
- Private 仓库: 每月 2000 分钟免费
  - 单次执行约 5 分钟
  - **完全免费**

### 总成本
**~$2/月** (仅 Claude API)

---

## 📅 实施时间表

| 阶段 | 任务 | 预计时间 |
|:---|:---|:---|
| Phase 1 | 创建 agent_runner.py | 30 分钟 |
| Phase 2 | 创建 GitHub Actions workflow | 20 分钟 |
| Phase 3 | 创建 requirements.txt | 5 分钟 |
| Phase 4 | 更新 config.json | 5 分钟 |
| Phase 5 | 创建部署文档 | 30 分钟 |
| Testing | 本地测试 + GitHub Actions 测试 | 30 分钟 |
| **总计** | | **~2 小时** |

---

## 🎯 成功标准

1. ✅ GitHub Actions 每天自动执行
2. ✅ 成功搜索并筛选爆款笔记
3. ✅ 微信接收到完整报告
4. ✅ 无手动干预
5. ✅ 日志清晰可追溯

---

## 📌 关键文件路径

### 需要创建的文件
- `scripts/agent_runner.py` - Agent 调用脚本
- `.github/workflows/xhs-daily-report.yml` - GitHub Actions 配置
- `requirements.txt` - Python 依赖
- `DEPLOYMENT.md` - 部署文档

### 需要修改的文件
- `config.json` - 移除敏感信息

### 保持不变的文件
- `scripts/validate_config.py`
- `scripts/validate_data.py`
- `scripts/push_report.py`
- `skill.md`

---

## 🚀 后续优化建议

1. **监控告警**
   - 添加执行失败通知
   - cookies 过期提醒

2. **数据持久化**
   - 保存历史数据到 GitHub
   - 生成趋势分析

3. **多时段执行**
   - 早晚各执行一次
   - 对比不同时段的热点

4. **扩展其他赛道**
   - 支持自定义关键词
   - 多赛道并行分析

---

**计划状态**: ✅ 已完成

**下一步**: 等待用户审核批准后开始实施
