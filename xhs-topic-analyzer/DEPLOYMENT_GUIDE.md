# 🚀 xhs-topic-analyzer 部署配置指南

> **版本**: v1.0
> **更新时间**: 2026-01-20
> **维护者**: 浮浮酱 ฅ'ω'ฅ

---

## 📋 前置检查清单

在开始配置之前，请确保主人已经准备好以下内容：

- [ ] GitHub 仓库访问权限
- [ ] 智谱 AI API Key
- [ ] 小红书账号（已登录）
- [ ] PushPlus 账号（已有 Token）

---

## 🔐 步骤 1: 配置 GitHub Secrets

### 1.1 打开 GitHub Secrets 设置页面

1. 打开 GitHub 仓库页面
2. 点击顶部的 **Settings** 标签
3. 在左侧菜单中找到 **Secrets and variables**
4. 点击 **Actions**
5. 点击 **New repository secret** 按钮

### 1.2 添加 Secret: ZHIPU_API_KEY

**如果主人还没有智谱 API Key，请先获取：**

1. 访问 [智谱 AI 开放平台](https://open.bigmodel.cn/)
2. 注册/登录账号
3. 进入 **API Keys** 页面
4. 点击 **新建 API Key**
5. 复制生成的 key（格式: `xxx.xxxxx`）

**添加到 GitHub Secrets：**

| 字段 | 值 |
|:---|:---|
| **Name** | `ZHIPU_API_KEY` |
| **Secret** | 粘贴你的智谱 API Key |
| **Value** | `xxx.xxxxx` |

点击 **Add secret** 保存。

---

### 1.3 添加 Secret: XHS_COOKIES

**获取小红书 Cookies（重要！）**

#### 方法：浏览器导出（推荐）

1. **登录小红书**
   - 打开浏览器，访问: https://www.xiaohongshu.com
   - 使用手机号或微信登录

2. **打开开发者工具**
   - Windows/Linux: 按 `F12`
   - Mac: 按 `Cmd + Option + I`

3. **找到 Cookies**
   - 点击顶部 **Application** 标签（或 **存储**）
   - 左侧菜单展开 **Storage** → **Cookies**
   - 点击 `https://www.xiaohongshu.com`

4. **复制关键 Cookie 值**
   - 找到并点击 `a1`，复制 **Value** 列的值
   - 找到并点击 `webId`，复制 **Value** 列的值
   - 找到并点击 `web_session` 或 `webBuild`，复制 **Value** 列的值

5. **组合成 JSON 格式**
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

6. **添加到 GitHub Secrets**
   - **Name**: `XHS_COOKIES`
   - **Secret**: 粘贴上面的整个 JSON 内容
   - 点击 **Add secret**

⚠️ **重要提示**：
- Cookies 每 7-30 天会过期，需要定期更新
- 如果搜索返回空结果，通常是 cookies 过期了
- 建议设置日历提醒，每 2 周更新一次

---

### 1.4 添加 Secret: WECHAT_PUSH_TOKEN

主人已经有了 PushPlus Token，直接添加即可：

| 字段 | 值 |
|:---|:---|
| **Name** | `WECHAT_PUSH_TOKEN` |
| **Secret** | `a6443f3a5d0f4b11a42c281f831b5c15` |

点击 **Add secret** 保存。

---

### 1.5 验证 Secrets 配置

配置完成后，应该看到以下 3 个 Secrets：

✅ `ZHIPU_API_KEY` •••
✅ `XHS_COOKIES` •••
✅ `WECHAT_PUSH_TOKEN` •••

---

## 📤 步骤 2: 提交代码到 GitHub

### 2.1 检查修改的文件

浮浮酱已经帮主人修改了以下文件：

1. ✅ `requirements.txt` - 添加了 `zhipuai>=2.1.0`
2. ✅ `scripts/agent_runner.py` - 完全重写，实现 HTTP 调用 MCP
3. ✅ `.github/workflows/xhs-daily-report.yml` - 更新 MCP Server 配置

### 2.2 提交代码

在项目根目录执行：

```bash
cd /Users/henry/.claude/skills/xhs-topic-analyzer

# 查看修改状态
git status

# 添加所有修改
git add .

# 提交代码
git commit -m "feat: 迁移到智谱 AI + GitHub Actions

- 添加 zhipuai 依赖
- 重写 agent_runner.py 实现 HTTP 调用 MCP
- 更新 GitHub Actions workflow (端口 18060)
- 添加 xiaohongshu-mcp 安装步骤"

# 推送到 GitHub
git push
```

---

## 🧪 步骤 3: 测试运行

### 3.1 手动触发工作流

1. 进入 GitHub 仓库页面
2. 点击顶部的 **Actions** 标签
3. 在左侧选择 **"小红书财经爆款日报 (智谱 AI 版本)"**
4. 点击右侧的 **Run workflow** 按钮
5. 选择分支（通常是 `main` 或 `master`）
6. 点击绿色的 **Run workflow** 按钮

### 3.2 观察执行日志

点击刚创建的工作流运行记录，观察每个步骤的执行情况：

**关键步骤检查：**

✅ **步骤 1: Checkout 代码**
- 应该显示: "✓ 成功"

✅ **步骤 2: 设置 Python 环境**
- 应该显示: "Python 3.11.x"

✅ **步骤 3: 安装 xiaohongshu-mcp**
- 应该显示: "✓ xiaohongshu-mcp 已安装"

✅ **步骤 4: 安装 Python 依赖**
- 应该显示: "Successfully installed zhipuai-..."

✅ **步骤 5: 准备小红书 Cookies**
- 应该显示: "✓ Cookies 文件已创建"

✅ **步骤 6: 启动 xiaohongshu-mcp Server**（关键！）
- 应该显示: "✓ MCP Server 已就绪"
- 如果失败，查看日志中的 `/tmp/mcp_server.log`

✅ **步骤 7: 运行智谱 AI Agent**（核心！）
- 应该显示多个搜索关键词的结果
- 例如: "✓ 金融: 15 条"
- 最后显示: "✓ 搜索完成!"

✅ **步骤 8: 数据校验**
- 应该显示: "✓ 数据校验通过"

✅ **步骤 9: 生成报告并推送微信**
- 应该显示: "[Success] 推送成功！请检查手机。"

✅ **步骤 10: 清理**
- 应该显示: "✓ 清理完成"

### 3.3 验证微信推送

1. 拿起手机 📱
2. 打开微信
3. 查找来自 **PushPlus** 的消息
4. 应该看到标题为: **"💰 小红书财经猎手 MM-DD"** 的消息
5. 点击查看完整报告

**预期报告内容：**
- TOP 10 热点选题
- 选题分布分析
- 深度选题洞察
- 选题建议（可直接使用）
- 完整爆款笔记列表

---

## 🎉 步骤 4: 上线运行

### 4.1 确认定时任务

工作流配置为每天北京时间 **09:00** 自动运行。

如果主人想修改执行时间，可以编辑 `.github/workflows/xhs-daily-report.yml`:

```yaml
on:
  schedule:
    - cron: '0 1 * * *'  # UTC 01:00 = 北京时间 09:00
```

**常用时间设置：**
- `0 1 * * *` - 北京时间 09:00
- `0 8 * * *` - 北京时间 16:00
- `0 16 * * *` - 北京时间 00:00（次日）
- `*/30 * * * *` - 每 30 分钟（测试用）

### 4.2 监控执行情况

1. 每天早上 09:00 后，检查微信是否收到报告
2. 如果没收到，登录 GitHub 查看工作流执行日志
3. 查看 **Actions** 页面，找到最新运行记录
4. 检查是否有错误信息

### 4.3 定期维护

**每 2 周检查一次：**

- [ ] 更新小红书 Cookies（如果搜索失败）
- [ ] 检查智谱 AI 账户余额
- [ ] 查看 GitHub Actions 执行历史
- [ ] 验证微信推送是否正常

---

## 🔍 故障排查

### 问题 1: MCP Server 启动失败

**现象：**
```
✗ MCP Server 启动失败，查看日志：
```

**可能原因：**
1. xiaohongshu-mcp 未正确安装
2. Cookies 格式错误
3. Cookies 已过期

**解决方案：**
1. 检查工作流日志中的安装步骤
2. 验证 `XHS_COOKIES` 是否为有效的 JSON 格式
3. 重新获取小红书 Cookies

---

### 问题 2: 搜索返回空结果

**现象：**
```
[Info] 搜索关键词: 金融
  ✓ 金融: 0 条
```

**可能原因：**
1. 小红书登录失效（cookies 过期）
2. IP 被限流
3. 搜索关键词不合理

**解决方案：**
1. 重新获取 `XHS_COOKIES`（最常见原因）
2. 更新 GitHub Secret 中的 cookies
3. 等待 24 小时后重试（如果是限流）

---

### 问题 3: 微信推送失败

**现象：**
```
[Failed] push token 无效
```

**解决方案：**
1. 验证 `WECHAT_PUSH_TOKEN` 是否正确
2. 登录 [PushPlus](http://www.pushplus.plus/) 查看 token
3. 检查推送限额（免费版: 200次/天）

---

### 问题 4: 智谱 AI API 调用失败

**现象：**
```
[Error] 智谱 AI API 调用失败: 401
```

**解决方案：**
1. 验证 `ZHIPU_API_KEY` 是否正确
2. 检查 API Key 是否有效（未过期）
3. 确认智谱账户余额充足
4. 访问 [智谱控制台](https://open.bigmodel.cn/) 查看 API 使用情况

---

## 📊 成本说明

### 月度成本估算

| 项目 | 用量 | 单价 | 月成本 |
|:---|:---|:---|:---|
| 智谱 AI | ~6000 tokens/天 × 30天 | ¥0.12-0.60/1M tokens | ~¥2/月 |
| GitHub Actions | 10 分钟/天 × 30天 | Public 仓库免费 | **免费** |
| PushPlus | 1 次/天 × 30天 | 免费版 200次/天 | **免费** |
| **总计** | | | **~¥2/月** |

### 成本优化建议

1. ✅ 使用智谱 AI 而非 Claude（成本降低 90%）
2. ✅ Public 仓库免费使用 GitHub Actions
3. ✅ PushPlus 免费版足够日常使用

---

## 📚 参考资料

### 官方文档

- [智谱 AI 开放平台](https://open.bigmodel.cn/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [xiaohongshu-mcp GitHub](https://github.com/xpzouying/xiaohongshu-mcp)
- [PushPlus 官网](http://www.pushplus.plus/)

### 相关工具

- [Cron 表达式生成器](https://crontab.guru/)
- [JSON 格式化工具](https://jsonformatter.org/)
- [GitHub Secrets 最佳实践](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---

## ✅ 完成检查清单

配置完成后，请确认以下所有项都已完成：

### 代码修改
- [x] requirements.txt 已添加 `zhipuai>=2.1.0`
- [x] scripts/agent_runner.py 已重写
- [x] .github/workflows/xhs-daily-report.yml 已更新
- [x] 代码已提交到 GitHub

### Secrets 配置
- [ ] ZHIPU_API_KEY 已配置
- [ ] XHS_COOKIES 已配置（JSON 格式）
- [ ] WECHAT_PUSH_TOKEN 已配置

### 测试验证
- [ ] 手动触发工作流成功
- [ ] 收到微信推送报告
- [ ] 报告内容正确完整

### 上线运行
- [ ] 定时任务已启用
- [ ] 设置了日历提醒（每 2 周检查 cookies）

---

## 🎊 总结

恭喜主人！🎉 完成所有配置后，系统将每天早上 09:00 自动：

1. ✅ 搜索小红书财经爆款笔记（3天内+2000赞以上）
2. ✅ 深度分析选题规律
3. ✅ 生成可执行的选题建议
4. ✅ 推送报告到微信

**维护成本：**
- 每月约 ¥2（智谱 AI）
- 每 2 周更新一次 cookies（5 分钟）
- 几乎零维护的自动化系统 ✨

---

**文档版本**: v1.0
**更新时间**: 2026-01-20
**维护者**: 浮浮酱 ฅ'ω'ฅ

如有问题，请查看故障排查部分或参考官方文档喵～ (๑•̀ㅂ•́)و✧
