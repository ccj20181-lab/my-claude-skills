# xhs-topic-analyzer GitHub Actions 部署指南

## 📋 部署概述

本指南将帮助您将 xhs-topic-analyzer skill 部署到 GitHub Actions，实现每天自动搜索小红书财经爆款笔记并推送到微信。

---

## 🔐 步骤 1: 配置 GitHub Secrets

### 需要配置的 3 个 Secrets

在 GitHub 仓库中配置以下敏感信息：

#### 1.1 ANTHROPIC_API_KEY

**用途**: Claude API 调用凭证

**获取方式**:
1. 访问 [Anthropic Console](https://console.anthropic.com/)
2. 注册/登录账号
3. 进入 "API Keys" 页面
4. 点击 "Create Key" 创建新的 API Key
5. 复制生成的 key（格式：`sk-ant-api03-...`）

**配置步骤**:
1. 进入 GitHub 仓库页面
2. 点击 Settings → Secrets and variables → Actions
3. 点击 "New repository secret"
4. Name: `ANTHROPIC_API_KEY`
5. Secret: 粘贴您的 API Key
6. 点击 "Add secret"

#### 1.2 XHS_COOKIES

**用途**: 小红书登录状态

**获取方式**:
1. 使用 Chrome 浏览器访问 [小红书网页版](https://www.xiaohongshu.com/)
2. 登录您的小红书账号
3. 按 F12 打开开发者工具
4. 进入 "Application" 标签页
5. 左侧选择 Storage → Cookies → https://www.xiaohongshu.com
6. 找到并复制以下关键 cookies 的值：
   - `a1`
   - `webId`
   - `web_session`

**格式化为 JSON**:
```json
{
  "a1": "你的a1值",
  "webId": "你的webId值",
  "web_session": "你的web_session值"
}
```

**配置步骤**:
1. 进入 GitHub 仓库页面
2. 点击 Settings → Secrets and variables → Actions
3. 点击 "New repository secret"
4. Name: `XHS_COOKIES`
5. Secret: 粘贴上面格式化的 JSON 字符串
6. 点击 "Add secret"

⚠️ **重要提示**:
- Cookies 可能在 7-30 天后过期
- 如果发现推送失败，首先检查是否需要更新 cookies
- 建议定期（每月）更新一次

#### 1.3 WECHAT_PUSH_TOKEN

**用途**: 微信推送令牌

**获取方式**:
1. 访问 [PushPlus 官网](http://www.pushplus.plus/)
2. 使用微信扫码登录
3. 进入管理后台
4. 复制您的 Token（一串字符串）

**配置步骤**:
1. 进入 GitHub 仓库页面
2. 点击 Settings → Secrets and variables → Actions
3. 点击 "New repository secret"
4. Name: `WECHAT_PUSH_TOKEN`
5. Secret: 粘贴您的 PushPlus Token
6. 点击 "Add secret"

---

## 🚀 步骤 2: 启用 GitHub Actions

### 2.1 检查文件是否存在

确保以下文件已存在于仓库中：

```
xhs-topic-analyzer/
├── .github/
│   └── workflows/
│       └── xhs-daily-report.yml    ✅ 必需
├── scripts/
│   ├── agent_runner.py              ✅ 必需
│   ├── validate_data.py             ✅ 必需
│   └── push_report.py               ✅ 必需
├── config.json                      ✅ 必需
└── requirements.txt                 ✅ 必需
```

### 2.2 启用 Actions

1. 进入 GitHub 仓库页面
2. 点击 "Actions" 标签页
3. 如果看到提示 "Workflows aren't being run on this repository"
4. 点击 "I understand my workflows, go ahead and enable them"

---

## ✅ 步骤 3: 测试运行

### 3.1 手动触发测试

1. 进入 Actions 页面
2. 左侧选择 "小红书财经爆款日报" workflow
3. 点击右上角 "Run workflow" 按钮
4. 选择分支（通常是 `main`）
5. 点击绿色的 "Run workflow" 按钮

### 3.2 查看执行日志

1. 刷新页面，等待 workflow 运行
2. 点击刚刚创建的 run
3. 点击 "generate-report" job
4. 查看每个 step 的详细日志：
   - ✅ Checkout 代码
   - ✅ 设置 Python 环境
   - ✅ 安装依赖
   - ✅ 启动 xiaohongshu-mcp Server
   - ✅ 运行 Claude Agent
   - ✅ 数据校验
   - ✅ 生成报告并推送微信
   - ✅ 清理

### 3.3 验证微信推送

1. 检查微信是否收到推送消息
2. 验证报告内容是否完整：
   - TOP 10 热点选题
   - 选题分布分析
   - 深度选题洞察
   - 选题建议
   - 完整爆款笔记列表

---

## 📅 步骤 4: 定时任务配置

### 4.1 默认定时

Workflow 默认配置为每天 **北京时间 09:00** 自动执行：

```yaml
schedule:
  - cron: '0 1 * * *'  # UTC 01:00 = 北京时间 09:00
```

### 4.2 自定义执行时间

如果需要修改执行时间，编辑 `.github/workflows/xhs-daily-report.yml`：

**常用时间表**:
- 北京时间 08:00: `cron: '0 0 * * *'`
- 北京时间 09:00: `cron: '0 1 * * *'` (默认)
- 北京时间 10:00: `cron: '0 2 * * *'`
- 北京时间 12:00: `cron: '0 4 * * *'`
- 北京时间 18:00: `cron: '0 10 * * *'`

**cron 表达式格式**:
```
分钟 小时 日 月 星期
0    1   *  *  *
│    │   │  │  │
│    │   │  │  └─ 星期几 (0-6，0=周日)
│    │   │  └──── 月份 (1-12)
│    │   └─────── 日期 (1-31)
│    └──────────── 小时 (0-23，UTC 时间)
└───────────────── 分钟 (0-59)
```

⚠️ **注意**: GitHub Actions 使用 UTC 时间，需要减 8 小时转换为北京时间。

### 4.3 多次执行

如果需要一天执行多次，添加多个 cron 表达式：

```yaml
schedule:
  - cron: '0 1 * * *'   # 北京时间 09:00
  - cron: '0 10 * * *'  # 北京时间 18:00
```

---

## 🔧 步骤 5: 故障排查

### 问题 1: MCP Server 启动失败

**现象**:
- 日志显示 "MCP Server 启动失败"
- Agent 执行报错

**排查步骤**:
1. 检查 `XHS_COOKIES` Secret 是否正确配置
2. 验证 cookies 格式是否为有效 JSON
3. 确认 cookies 是否已过期（重新获取）

**解决方法**:
```bash
# 重新获取 cookies 并更新 Secret
1. 浏览器重新登录小红书
2. 导出新的 cookies
3. 更新 GitHub Secret: XHS_COOKIES
```

### 问题 2: Claude API 调用失败

**现象**:
- 日志显示 "Claude API 调用失败"
- 错误信息: "Invalid API key" 或 "Rate limit exceeded"

**排查步骤**:
1. 检查 `ANTHROPIC_API_KEY` Secret 是否正确
2. 验证 API Key 是否有效
3. 检查 API 使用量是否超限

**解决方法**:
```bash
# 验证 API Key
1. 登录 Anthropic Console
2. 检查 API Key 状态
3. 查看使用量和配额
4. 如需要，创建新的 API Key 并更新 Secret
```

### 问题 3: 微信推送失败

**现象**:
- Agent 执行成功，但未收到微信消息
- 日志显示 "推送失败"

**排查步骤**:
1. 检查 `WECHAT_PUSH_TOKEN` Secret 是否正确
2. 验证 PushPlus Token 是否有效
3. 检查推送限额（免费版每天 200 次）

**解决方法**:
```bash
# 验证 Token
1. 登录 PushPlus
2. 检查 Token 状态
3. 查看推送记录和限额
4. 如需要，更新 Secret
```

### 问题 4: 数据校验失败

**现象**:
- 日志显示 "数据校验失败"
- 符合条件的笔记数量为 0

**可能原因**:
1. 搜索关键词没有返回结果
2. 筛选条件过于严格（点赞≥2000）
3. 发布时间范围太窄（3天内）

**解决方法**:
```bash
# 调整筛选条件
1. 编辑 config.json
2. 降低 min_likes (如改为 1000)
3. 扩大时间范围 (如改为 7d)
4. 提交更改并重新运行
```

---

## 📊 步骤 6: 监控和维护

### 6.1 查看执行历史

1. 进入 Actions 页面
2. 查看所有 workflow runs
3. 点击任意 run 查看详细日志
4. 检查成功率和失败原因

### 6.2 接收失败通知

Workflow 已配置自动失败通知：
- 如果执行失败，会自动推送通知到微信
- 通知包含失败日志链接

### 6.3 定期维护

**建议维护计划**:

| 项目 | 频率 | 说明 |
|:---|:---|:---|
| 更新 XHS_COOKIES | 每月 | 防止 cookies 过期 |
| 检查 API 用量 | 每周 | 避免超限 |
| 查看执行日志 | 每天 | 及时发现问题 |
| 更新依赖包 | 每季度 | 保持最新版本 |

---

## 💰 成本说明

### Claude API
- **每天 1 次执行**
- 约 2000 input tokens + 4000 output tokens
- **月成本**: 约 $2 USD

### GitHub Actions
- **Public 仓库**: 完全免费
- **Private 仓库**:
  - 免费额度: 2000 分钟/月
  - 单次执行: 约 5 分钟
  - 30 次执行: 150 分钟/月
  - **结论**: 完全在免费额度内

### PushPlus
- 免费版: 每天 200 次推送
- **成本**: $0

**总成本**: 约 $2 USD/月 (仅 Claude API)

---

## 📞 获取帮助

### 常见问题

1. **Q: 为什么没有收到推送？**
   - A: 检查 WECHAT_PUSH_TOKEN 是否正确，查看 Actions 日志确认执行状态

2. **Q: 如何修改搜索关键词？**
   - A: 编辑 `config.json` 中的 `keywords` 字段

3. **Q: 可以一天执行多次吗？**
   - A: 可以，修改 `.github/workflows/xhs-daily-report.yml` 中的 `schedule`

4. **Q: 如何查看历史报告？**
   - A: Actions 会自动保存报告为 artifacts，保留 7 天

### 联系支持

- GitHub Issues: 在仓库提交 issue
- 文档: 查看 `GITHUB_ACTIONS_MIGRATION.md`
- 计划文档: 查看 `/Users/henry/.claude/plans/kind-orbiting-starlight.md`

---

## ✅ 部署检查清单

完成部署后，请确认以下项目：

- [ ] 已配置 ANTHROPIC_API_KEY Secret
- [ ] 已配置 XHS_COOKIES Secret
- [ ] 已配置 WECHAT_PUSH_TOKEN Secret
- [ ] 已启用 GitHub Actions
- [ ] 手动触发测试成功
- [ ] 收到微信推送消息
- [ ] 报告内容完整准确
- [ ] 定时任务配置正确

---

**部署完成！** 🎉

您的 xhs-topic-analyzer 现在已经在云端自动运行啦！每天早上 9 点会自动收到小红书财经爆款选题报告。
