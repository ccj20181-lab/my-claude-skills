# 建立 Claude Skills 专属仓库计划 (Claude Skills Repository Plan)

## 1. 目标 (Goal)
创建一个新的 GitHub 仓库，用于备份和管理您精心挑选的 15 个 Claude Code 技能。

## 2. 准备工作 (Preparation)
- **目标目录**: `~/Documents/my-claude-skills`
- **源目录**: `~/.claude/skills/`
- **需要处理的冲突**:
  - `xhs-topic-analyzer` 包含嵌套的 `.git` 目录（需要移除以避免 submodule 问题）。
  - 部分技能包含 `node_modules`（需要通过 `.gitignore` 忽略）。

## 3. 实施步骤 (Execution Steps)

### 第一阶段：本地仓库初始化 (Local Setup)
1. 创建目录 `~/Documents/my-claude-skills`。
2. 初始化 Git 仓库 (`git init`)。
3. 创建 `.gitignore` 文件，配置忽略项：
   - `node_modules/`
   - `.DS_Store`
   - `.env` (防止密钥泄露)
   - `dist/` (构建产物)

### 第二阶段：技能迁移 (Migration)
1. 将 `~/.claude/skills/` 下的所有技能目录复制到新仓库。
2. **关键操作**: 删除新仓库中 `xhs-topic-analyzer/.git` 目录，将其转换为普通文件夹。
3. 复制 `skills.json` 到根目录作为配置备份。

### 第三阶段：文档生成 (Documentation)
1. 创建 `README.md`，包含：
   - 仓库介绍
   - 当前收录的 15 个技能列表
   - 使用 `skillslm-manager` 恢复/安装这些技能的说明。

### 第四阶段：推送到 GitHub (Push to GitHub)
1. 提交所有更改到本地 Git。
2. 使用 `gh repo create` 创建远程仓库。
   - **名称**: `my-claude-skills` (暂定，执行时可确认)
   - **可见性**: `Private` (私有，为了安全起见，除非您指定公开)
3. 推送代码到远程仓库。

## 4. 验证 (Verification)
- 检查 GitHub 仓库页面是否包含所有文件。
- 确认 `node_modules` 未被上传。
- 确认没有嵌套的 submodule 指针。
