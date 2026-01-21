# GitHub Secrets 配置指南

## 📋 概述

为了让财经简报自动化系统正常运行，需要在GitHub仓库中配置API密钥。本指南将详细说明配置步骤。

## 🔧 需要配置的Secret

### ANTHROPIC_AUTH_TOKEN

**用途**：调用智谱AI API生成财经简报

**Secret值**：
```
ede5dcfb6ee24bc1abb5e6a14887d6c7.wPIlUa0hkFFD9mbM
```

**说明**：
- 新的环境变量名称（兼容旧版的ANTHROPIC_API_KEY）
- 用于认证智谱BigModel的GLM-4 Plus模型
- Base URL: https://open.bigmodel.cn/api/anthropic

## 📝 配置步骤

### 方法一：通过网页界面配置

1. **访问仓库设置**
   - 打开浏览器，访问：https://github.com/ccj20181-lab/daily-tech-digest
   - 点击仓库页面顶部的 **Settings** 标签

2. **进入Secrets配置页面**
   - 在左侧菜单中找到 **Secrets and variables**
   - 点击 **Actions**
   - 进入 "Secrets and variables" 页面

3. **创建新Secret**
   - 点击 **New repository secret** 按钮
   - 在 **Name** 辏入框中输入：`ANTHROPIC_AUTH_TOKEN`
   - 在 **Value** 输入框中粘贴：`ede5dcfb6ee24bc1abb5e6a14887d6c7.wPIlUa0hkFFD9mbM`
   - 点击 **Add secret** 按钮保存

4. **验证配置**
   - 确认Secret列表中出现了 `ANTHROPIC_AUTH_TOKEN`
   - Value显示为已隐藏（••••••），这是正常的安全显示

### 方法二：通过GitHub CLI配置（推荐）

如果您已安装GitHub CLI（gh），可以使用命令快速配置：

```bash
# 设置Secret
gh secret set ANTHROPIC_AUTH_TOKEN --body "ede5dcfb6ee24bc1abb5e6a14887d6c7.wPIlUa0hkFFD9mbM" --repo ccj20181-lab/daily-tech-digest

# 验证Secret已设置
gh secret list --repo ccj20181-lab/daily-tech-digest
```

## ✅ 验证配置

配置完成后，可以通过以下方式验证：

### 1. 手动触发工作流

1. 访问：https://github.com/ccj20181-lab/daily-tech-digest/actions
2. 点击左侧的 **"每日财经简报生成器"** 工作流
3. 点击右侧的 **"Run workflow"** 按钮
4. 选择 **main** 分支
5. 点击 **"Run workflow"** 确认

### 2. 查看运行日志

在工作流运行页面：
- 点击运行记录查看详细信息
- 检查 **"运行财经简报生成脚本"** 步骤
- 如果看到 `[完成] 已保存` 的输出，说明配置成功

### 3. 检查生成的简报

访问：https://github.com/ccj20181-lab/daily-tech-digest/tree/main/digests

查看最新的 `latest.md` 文件，确认简报内容正常生成。

## 🔒 安全提示

1. **不要泄露Secret**
   - Secret值仅在GitHub仓库设置中可见
   - 不要在代码、公开文档中暴露Secret值
   - 如果怀疑泄露，立即删除并重新生成

2. **定期更换密钥**
   - 建议每3-6个月更换一次API密钥
   - 更换后记得更新GitHub Secret

3. **最小权限原则**
   - 仅配置必要的Secret
   - 不配置未使用的敏感信息

## 🛠️ 故障排除

### 问题1：工作流运行失败

**错误信息**：
```
ValueError: 请设置 ANTHROPIC_AUTH_TOKEN 或 ANTHROPIC_API_KEY 环境变量
```

**解决方案**：
- 检查Secret名称是否正确（`ANTHROPIC_AUTH_TOKEN`）
- 确认Secret值是否完整复制
- 尝试重新运行工作流

### 问题2：API调用失败

**错误信息**：
```
anthropic.APIError: Invalid API key
```

**解决方案**：
- 验证API密钥是否有效
- 检查智谱AI账户状态
- 联系智谱AI客服确认密钥状态

### 问题3：工作流超时

**错误信息**：
```
Timeout: The operation has timed out
```

**解决方案**：
- 检查网络连接
- 确认智谱API服务状态
- 稍后重试工作流

## 📚 相关资源

- **智谱AI开放平台**：https://open.bigmodel.cn/
- **GitHub Actions文档**：https://docs.github.com/en/actions
- **GitHub Secrets文档**：https://docs.github.com/en/actions/security-guides/encrypted-secrets

## 💡 额外配置（可选）

### PUSHPLUS_TOKEN（微信推送）

如果需要微信推送功能，可以额外配置：

**Secret名称**：`PUSHPLUS_TOKEN`
**获取方式**：
1. 访问：http://www.pushplus.plus/
2. 注册并登录
3. 获取Token
4. 按照上述步骤添加到GitHub Secrets

配置后，每日简报生成成功会自动推送到微信。

---

**配置完成后，系统将在每天北京时间 06:30 自动生成财经简报！** 📈✨
