# 🔐 GitHub Secrets 配置清单

> **xhs-topic-analyzer** - 小红书财经爆款选题分析器
> 配置日期: 2026-01-20

---

## 📋 配置清单

主人需要在 GitHub 仓库配置以下 **4 个 Secrets**：

### ✅ Secret 1: ANTHROPIC_AUTH_TOKEN

```
Name: ANTHROPIC_AUTH_TOKEN
Value: ede5dcfb6ee24bc1abb5e6a14887d6c7.wPIlUa0hkFFD9mbM
```

**状态**: 主人已有 ✅

---

### ✅ Secret 2: ANTHROPIC_BASE_URL

```
Name: ANTHROPIC_BASE_URL
Value: https://open.bigmodel.cn/api/anthropic
```

**状态**: 主人已有 ✅

---

### ⚠️ Secret 3: XHS_COOKIES (需要配置)

**如何获取小红书 Cookies：**

#### 步骤 1: 登录小红书

1. 打开浏览器
2. 访问: https://www.xiaohongshu.com
3. 使用手机号或微信登录

#### 步骤 2: 打开开发者工具

- **Windows/Linux**: 按 `F12`
- **Mac**: 按 `Cmd + Option + I`

#### 步骤 3: 找到 Cookies

1. 点击顶部 **Application** 标签（或 **存储**）
2. 左侧菜单展开 **Cookies**
3. 点击 `https://www.xiaohongshu.com`

#### 步骤 4: 复制 Cookie 值

找到并复制以下 3 个 cookie 的 **Value** 列：

1. **a1**
   - 点击 `a1`
   - 复制 **Value** 列的内容

2. **webId**
   - 点击 `webId`
   - 复制 **Value** 列的内容

3. **web_session** 或 `webBuild`
   - 点击 `web_session` 或 `webBuild`
   - 复制 **Value** 列的内容

#### 步骤 5: 组合成 JSON 格式

```json
{
  "a1": "你的a1值",
  "webId": "你的webId值",
  "web_session": "你的web_session值"
}
```

**示例：**
```json
{
  "a1": "17c3b8a8e1234567890abcdef1234567890",
  "webId": "abc123def456-7890-1234-5678-90abcdef1234",
  "web_session": "0123456789abcdef=0123456789abcdef"
}
```

#### 步骤 6: 添加到 GitHub Secrets

1. 打开 GitHub 仓库
2. 进入 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 填写:
   ```
   Name: XHS_COOKIES
   Value: {粘贴上面的整个 JSON 内容}
   ```
5. 点击 **Add secret**

⚠️ **注意**:
- Cookies 每 7-30 天会过期，需要定期更新
- 如果搜索返回空结果，通常是 cookies 过期了
- 建议设置日历提醒，每 2 周更新一次

**状态**: ⚠️ **需要主人配置**

---

### ✅ Secret 4: WECHAT_PUSH_TOKEN

```
Name: WECHAT_PUSH_TOKEN
Value: a6443f3a5d0f4b11a42c281f831b5c15
```

**状态**: 已有 ✅

---

## 🚀 配置步骤

### 第一步: 打开 GitHub Secrets 设置

1. 打开 GitHub 仓库页面
2. 点击顶部的 **Settings** 标签
3. 在左侧菜单中找到 **Secrets and variables**
4. 点击 **Actions**

### 第二步: 添加 Secrets

点击 **New repository secret** 按钮，依次添加上述 4 个 Secrets。

### 第三步: 验证配置

配置完成后，应该看到以下 4 个 Secrets：

- ✅ ANTHROPIC_AUTH_TOKEN •••
- ✅ ANTHROPIC_BASE_URL •••
- ✅ XHS_COOKIES •••
- ✅ WECHAT_PUSH_TOKEN •••

---

## 🧪 测试运行

配置完成后，测试一下是否正常工作：

### 1. 手动触发工作流

1. 进入 GitHub 仓库的 **Actions** 页面
2. 选择 **"小红书财经爆款日报 (智谱 AI 版本)"** 工作流
3. 点击 **Run workflow** 按钮
4. 点击 **Run workflow** 确认

### 2. 观察执行日志

点击运行记录，查看各个步骤的执行情况。

**预期结果：**
- ✅ MCP Server 启动成功（端口 18060）
- ✅ Anthropic Agent 运行成功
- ✅ 搜索到多条笔记
- ✅ data.json 文件生成
- ✅ 微信推送成功
- ✅ 收到微信消息

### 3. 验证微信推送

拿起手机 📱，打开微信，应该收到来自 **PushPlus** 的消息。

---

## 📚 参考文档

详细配置说明请参考：
- **QUICKSTART.md** - 完整的快速开始指南
- **实施计划** - 技术方案和故障排查

---

## ✅ 完成检查

配置完成后，请确认以下所有项：

### Secrets 配置
- [ ] ANTHROPIC_AUTH_TOKEN 已配置
- [ ] ANTHROPIC_BASE_URL 已配置
- [ ] XHS_COOKIES 已配置（JSON 格式）
- [ ] WECHAT_PUSH_TOKEN 已配置

### 测试验证
- [ ] 手动触发工作流成功
- [ ] 收到微信推送报告
- [ ] 报告内容正确完整

### 上线运行
- [ ] 设置日历提醒（每 2 周检查 cookies）
- [ ] 等待定时执行（每天 09:00）

---

**文档版本**: v1.0
**更新时间**: 2026-01-20
**维护者**: 浮浮酱 ฅ'ω'ฅ

主人配置完成后，每天早上 09:00 就能自动收到小红书财经爆款报告啦！✨
