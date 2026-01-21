# GitHub Actions 配置指南

## 📋 概述

本指南将帮助您配置 `xhs-topic-analyzer` 的 GitHub Actions 自动化工作流，实现每天自动搜索小红书财经爆款笔记并推送到微信。

---

## 🔑 需要配置的 GitHub Secrets

在 GitHub 仓库中，需要配置以下 3 个 Secrets：

### 1. ANTHROPIC_AUTH_TOKEN ⭐

**用途**: Claude API 调用凭证（通过硅基流动代理）

**获取方式**:
您已经提供了硅基流动的 API Token！

```
ede5dcfb6ee24bc1abb5e6a14887d6c7.wPIlUa0hkFFD9mbM
```

**配置步骤**:
1. 打开 GitHub 仓库页面
2. 进入 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 填写信息：
   - **Name**: `ANTHROPIC_AUTH_TOKEN`
   - **Secret**: `ede5dcfb6ee24bc1abb5e6a14887d6c7.wPIlUa0hkFFD9mbM`
5. 点击 **Add secret**

---

### 2. ANTHROPIC_BASE_URL

**用途**: Claude API 代理地址（硅基流动）

**值**:
```
https://open.bigmodel.cn/api/anthropic
```

**配置步骤**:
1. 在 **Secrets and variables** → **Actions** 页面
2. 点击 **New repository secret**
3. 填写信息：
   - **Name**: `ANTHROPIC_BASE_URL`
   - **Secret**: `https://open.bigmodel.cn/api/anthropic`
4. 点击 **Add secret**

---

### 3. XHS_COOKIES

**用途**: 小红书登录凭证

**获取方式**:

#### 方法一：浏览器导出（推荐）

1. 打开浏览器，登录小红书网页版：https://www.xiaohongshu.com
2. 按 `F12` 打开开发者工具
3. 进入 **Application** → **Storage** → **Cookies**
4. 查找并导出以下 cookies：

```json
{
  "a1": "你的a1值",
  "webId": "你的webId值",
  "web_session": "你的web_session值"
}
```

5. 复制整个 JSON 内容

#### 方法二：使用 MCP 工具获取

如果您已通过 MCP 工具登录小红书，可以直接读取 cookies 文件。

**配置步骤**:
1. 在 **Secrets and variables** → **Actions** 页面
2. 点击 **New repository secret**
3. 填写信息：
   - **Name**: `XHS_COOKIES`
   - **Secret**: (粘贴上面获取的 JSON 内容)
4. 点击 **Add secret**

---

### 4. WECHAT_PUSH_TOKEN

**用途**: 微信推送令牌

**值**:
```
a6443f3a5d0f4b11a42c281f831b5c15
```

**配置步骤**:
1. 在 **Secrets and ** Secrets and variables** → **Actions** 页面
2. 点击 **New repository secret**
3. 填写信息：
   - **Name**: `WECHAT_PUSH_TOKEN`
   - **Secret**: `a6443f3a5d0f4b11a42c281f831b5c15`
4. 点击 **Add secret**

---

## ✅ 配置验证清单

配置完成后，您的 Secrets 应该如下所示：

| Secret 名称 | 值示例 | 状态 |
|:---|:---|:---|
| `ANTHROPIC_AUTH_TOKEN` | `ede5dcfb6ee24bc1abb5e6a14887d6c7b...` | ✅ |
| `ANTHROPIC_BASE_URL` | `https://open.bigmodel.cn/api/anthropic` | ✅ |
| `XHS_COOKIES` | `{"a1":"...", "webId":"...", ...}` | ✅ |
| `WECHAT_PUSH_TOKEN` | `a6443f3a5d0f4b11a42c281f831b5c15` | ✅ |

---

## 🚀 测试工作流

配置完成后，您可以手动触发工作流进行测试：

### 手动触发步骤

1. 进入 GitHub 仓库的 **Actions** 页面
2. 选择左侧的 **"小红书财经爆款日报 (Claude Agent)"** 工作流
3. 点击右侧的 **"Run workflow"** 按钮
4. 选择分支（默认 `main`）
5. 点击 **"Run workflow"** 确认

### 查看执行日志

1. 点击进入工作流运行详情
2. 查看各个步骤的执行日志
3. 确认：
   - ✅ MCP Server 启动成功
   - ✅ Claude API 调用成功
   - ✅ 数据文件生成
   - ✅ 微信推送成功

---

## 📅 定时执行

工作流已配置为每天北京时间 09:00 自动执行（UTC 01:00）

### 修改定时时间

如果需要修改执行时间，编辑 `.github/workflows/xhs-daily-report-claude.yml` 文件：

```yaml
on:
  schedule:
    - cron: '0 1 * * *'  # UTC 01:00 = 北京时间 09:00
```

**Cron 表达式说明**:
- `0 1 * * *` - 每天 UTC 01:00
- `30 2 * * *` - 每天 UTC 02:30（北京 10:30）
- `0 3 * * 1` - 每周一 UTC 03:00（北京 11:00）

---

## 🔧 故障排查

### 问题 1: MCP Server 启动失败

**现象**: 日志显示 "MCP Server 启动失败"

**解决方案**:
1. 检查 `xiaohongshu-mcp` 包是否正确安装
2. 验证 `XHS_COOKIES` 格式是否正确
3. 确认 cookies 是否有效（未过期）

---

### 问题 2: Claude API 调用失败

**现象**: API 返回 401 或 403 错误

**解决方案**:
1. 验证 `ANTHROPIC_AUTH_TOKEN` 是否正确
2. 检查 token 是否有效（未过期）
3. 确认硅基流动账户余额充足

---

### 问题 3: 小红书登录失效

**现象**: 搜索返回空结果

**解决方案**:
1. 重新登录小红书网页版
2. 导出新的 cookies
3. 更新 `XHS_COOKIES` Secret

---

### 问题 4: 微信推送失败

**现象**: 报告生成但未收到微信消息

**解决方案**:
1. 检查 `WECHAT_PUSH_TOKEN` 是否正确
2. 登录 PushPlus 查看推送历史
3. 确认推送未超过限额（免费版：200次/天）

---

## 📊 成本估算

### Claude API 成本（硅基流动）

假设每天执行一次，每次约 6000 tokens：

| 项目 | 用量 | 单价 | 月成本 |
|:---|:---|:---|:---|
| Input tokens | ~2000 × 30天 | ¥0.12/1M tokens | ¥0.72 |
| Output tokens | ~4000 × 30天 | ¥0.60/1M tokens | ¥1.44 |
| **总计** | | | **~¥2/月** |

### GitHub Actions 成本

- **Public 仓库**: 完全免费
- **Private 仓库**: 2000 分钟/月免费额度
  - 每次执行约 5-10 分钟
  - 30 次执行 = 150 分钟/月
  - **完全在免费额度内** ✅

### PushPlus 成本

- 免费版：200 次/天
- 每天 1 次 = 30 次/月
- **完全免费** ✅

**总成本**: 约 ¥2/月

---

## 🎯 配置完成后的效果

配置成功后，您将：

1. ✅ **每天自动执行**：每天早上 9:00 自动搜索
2. ✅ **自动推送微信**：分析报告直接推送到微信
3. ✅ **云端稳定运行**：不依赖本地环境
4. ✅ **完整数据追踪**：GitHub Actions 保留执行日志

---

## 📝 相关文档

- [Claude API 文档](https://docs.anthropic.com/)
- [硅基流动文档](https://siliconflow.cn/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [PushPlus 文档](http://www.pushplus.plus/doc/)

---

## 🎉 快速开始

1. ✅ 按照"配置步骤"添加 4 个 Secrets
2. ✅ 使用"手动触发"测试工作流
3. ✅ 等待每天早上 9:00 自动执行
4. ✅ 在微信接收每日爆款分析报告

---

**文档版本**: v1.0
**最后更新**: 2026-01-20
**维护者**: 浮浮酱 ฅ'ω'ฅ
