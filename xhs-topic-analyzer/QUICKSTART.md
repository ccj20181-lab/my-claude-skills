# 🚀 快速开始指南

> **xhs-topic-analyzer** - 小红书财经爆款选题分析器
> 版本: v1.1 (Anthropic SDK + 智谱 AI 兼容端点)

---

## 📋 前置条件

在开始之前，请确保主人已准备好：

- ✅ GitHub 仓库访问权限
- ✅ 智谱 AI API Key（已有）
- ✅ 小红书账号（需要登录获取 cookies）
- ✅ PushPlus Token（已有: `a6443f3a5d0f4b11a42c281f831b5c15`）

---

## 🎯 方案说明

浮浮酱为主人配置了 **Anthropic SDK + 智谱 AI 兼容端点** 方案喵～

**技术架构**:
```
GitHub Actions
    ↓
启动 xiaohongshu-mcp (端口 18060)
    ↓
Python 脚本 (agent_runner.py)
    ↓
Anthropic SDK → 智谱 AI 兼容端点
    ↓
HTTP 调用 MCP 搜索工具
    ↓
保存数据 → 推送微信
```

**API 配置**:
- `ANTHROPIC_AUTH_TOKEN`: `ede5dcfb6ee24bc1abb5e6a14887d6c7.wPIlUa0hkFFD9mbM`
- `ANTHROPIC_BASE_URL`: `https://open.bigmodel.cn/api/anthropic`

---

## 🔐 步骤 1: 配置 GitHub Secrets

### 1.1 打开 GitHub Secrets

1. 打开 GitHub 仓库
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**

### 1.2 添加以下 4 个 Secrets

#### Secret 1: ANTHROPIC_AUTH_TOKEN

```
Name: ANTHROPIC_AUTH_TOKEN
Value: ede5dcfb6ee24bc1abb5e6a14887d6c7.wPIlUa0hkFFD9mbM
```

#### Secret 2: ANTHROPIC_BASE_URL

```
Name: ANTHROPIC_BASE_URL
Value: https://open.bigmodel.cn/api/anthropic
```

#### Secret 3: XHS_COOKIES （重要！）

**如何获取小红书 Cookies：**

1. 打开浏览器，访问 https://www.xiaohongshu.com
2. 登录你的小红书账号
3. 按 `F12` 打开开发者工具
4. 点击 **Application** 标签（或 **存储**）
5. 左侧菜单展开 **Cookies** → `https://www.xiaohongshu.com`
6. 找到并复制以下 3 个 cookie 的值：
   - `a1`
   - `webId`
   - `web_session` 或 `webBuild`

7. 组合成 JSON 格式：

```json
{
  "a1": "你的a1值",
  "webId": "你的webId值",
  "web_session": "你的web_session值"
}
```

8. 添加到 GitHub Secrets：

```
Name: XHS_COOKIES
Value: {粘贴上面的整个 JSON 内容}
```

⚠️ **注意**: Cookies 每 7-30 天会过期，需要定期更新

#### Secret 4: WECHAT_PUSH_TOKEN

```
Name: WECHAT_PUSH_TOKEN
Value: a6443f3a5d0f4b11a42c281f831b5c15
```

---

## 📤 步骤 2: 提交代码

浮浮酱已经帮主人修改好了代码，现在提交到 GitHub 喵～

```bash
cd /Users/henry/.claude/skills/xhs-topic-analyzer

# 查看修改状态
git status

# 添加所有修改
git add .

# 提交代码
git commit -m "feat: 使用 Anthropic SDK + 智谱 AI 兼容端点

- 重写 agent_runner.py 使用 Anthropic SDK
- 移除 zhipuai 依赖
- 更新 GitHub Actions 环境变量
- MCP Server 端口改为 18060"

# 推送到 GitHub
git push
```

---

## 🧪 步骤 3: 测试运行

### 3.1 手动触发工作流

1. 进入 GitHub 仓库
2. 点击 **Actions** 标签
3. 选择 **"小红书财经爆款日报 (智谱 AI 版本)"**
4. 点击 **Run workflow**
5. 点击 **Run workflow** 确认

### 3.2 观察执行日志

点击运行记录，查看各个步骤：

✅ **预期结果**:
- ✓ Checkout 代码成功
- ✓ Python 环境设置成功
- ✓ xiaohongshu-mcp 安装成功
- ✓ Python 依赖安装成功
- ✓ Cookies 文件创建成功
- ✓ MCP Server 启动成功（端口 18060）
- ✓ **Anthropic Agent 运行成功**（关键！）
- ✓ 搜索到多条笔记
- ✓ 数据校验通过
- ✓ 微信推送成功
- ✓ 清理完成

### 3.3 验证微信推送

拿起手机 📱，打开微信，应该收到来自 **PushPlus** 的消息：

**标题**: 💰 小红书财经猎手 MM-DD

**内容包括**:
- TOP 10 热点选题
- 选题分布分析
- 深度选题洞察
- 可直接使用的选题建议
- 完整爆款笔记列表

---

## 🏠 步骤 4: 本地测试（可选）

如果主人想在本地测试，浮浮酱准备了测试脚本喵～

### 4.1 准备小红书 Cookies

1. 按照上面的步骤获取小红书 cookies
2. 保存为 JSON 文件，例如：`/tmp/xhs_cookies.json`

```json
{
  "a1": "你的a1值",
  "webId": "你的webId值",
  "web_session": "你的web_session值"
}
```

### 4.2 启动 MCP Server

```bash
# 启动 xiaohongshu-mcp
xiaohongshu-mcp --port 18060 --headless --cookies /tmp/xhs_cookies.json &
```

### 4.3 设置环境变量并运行

```bash
# 设置环境变量
export ANTHROPIC_AUTH_TOKEN="ede5dcfb6ee24bc1abb5e6a14887d6c7.wPIlUa0hkFFD9mbM"
export ANTHROPIC_BASE_URL="https://open.bigmodel.cn/api/anthropic"

# 进入项目目录
cd /Users/henry/.claude/skills/xhs-topic-analyzer

# 运行测试
python scripts/agent_runner.py
```

### 4.4 测试推送报告

```bash
# 生成并推送报告
python scripts/push_report.py --file data.json
```

---

## 🎉 步骤 5: 上线运行

配置完成并测试成功后，系统将每天 **北京时间 09:00** 自动运行：

1. ✅ 搜索小红书财经爆款笔记（3天内+2000赞以上）
2. ✅ 深度分析选题规律
3. ✅ 生成可执行的选题建议
4. ✅ 推送报告到微信

### 定时任务

工作流默认设置为每天 UTC 01:00 执行（北京时间 09:00）

如需修改，编辑 `.github/workflows/xhs-daily-report.yml`:

```yaml
on:
  schedule:
    - cron: '0 1 * * *'  # UTC 01:00 = 北京时间 09:00
```

---

## 🔧 维护指南

### 定期检查（每 2 周）

- [ ] 检查小红书 cookies 是否过期（如果搜索失败）
- [ ] 查看 GitHub Actions 执行历史
- [ ] 验证微信推送是否正常
- [ ] 检查智谱 AI 账户余额

### 更新 Cookies

如果搜索返回空结果，通常是 cookies 过期了：

1. 重新登录小红书网页版
2. 获取最新的 cookies
3. 更新 GitHub Secret `XHS_COOKIES`

---

## 💰 成本说明

| 项目 | 月成本 |
|:---|:---|
| 智谱 AI (Anthropic 兼容端点) | 约 ¥2-3/月 |
| GitHub Actions (Public 仓库) | 免费 |
| PushPlus (免费版) | 免费 |
| **总计** | **约 ¥2-3/月** |

比使用 Claude 官方 API 便宜 **90%+** 喵～

---

## 🐛 故障排查

### 问题 1: 搜索返回空结果

**原因**: 小红书 cookies 过期

**解决**: 重新获取并更新 `XHS_COOKIES`

### 问题 2: MCP Server 启动失败

**原因**: cookies 格式错误或已过期

**解决**: 检查 `XHS_COOKIES` 是否为有效的 JSON 格式

### 问题 3: 微信推送失败

**原因**: PushPlus Token 无效

**解决**: 验证 `WECHAT_PUSH_TOKEN` 是否正确

### 问题 4: Anthropic API 调用失败

**原因**: API Key 错误或余额不足

**解决**:
1. 验证 `ANTHROPIC_AUTH_TOKEN` 是否正确
2. 检查智谱 AI 账户余额
3. 访问 [智谱控制台](https://open.bigmodel.cn/)

---

## 📚 参考资源

- [智谱 AI 开放平台](https://open.bigmodel.cn/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [xiaohongshu-mcp GitHub](https://github.com/xpzouying/xiaohongshu-mcp)
- [PushPlus 官网](http://www.pushplus.plus/)

---

## ✅ 完成检查清单

### 配置阶段
- [x] requirements.txt 已更新（移除 zhipuai）
- [x] agent_runner.py 已重写（使用 Anthropic SDK）
- [x] GitHub Actions workflow 已更新
- [ ] 代码已提交到 GitHub
- [ ] GitHub Secrets 已配置（4个）

### 测试阶段
- [ ] 手动触发工作流成功
- [ ] 收到微信推送报告
- [ ] 报告内容正确完整

### 上线阶段
- [ ] 定时任务正常运行
- [ ] 设置日历提醒（每2周检查cookies）

---

**文档版本**: v1.1
**更新时间**: 2026-01-20
**维护者**: 浮浮酱 ฅ'ω'ฅ

主人现在可以按照上面的步骤完成配置啦！完成配置后，每天早上 09:00 就能自动收到小红书财经爆款报告喵～ ✨(´｡• ᵕ •｡`) ♡
