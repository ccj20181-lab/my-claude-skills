Always respond in Chinese-simplified

Always use python3 when executing Python scripts

When calling skills, always read the skill documentation first before using them properly

## Claude Code Skills Directory

All Claude Code skills are installed in: `/Users/henry/.claude/skills/`

When working with skills:
- The skills directory contains all available skills
- Each skill has its own subdirectory with a SKILL.md file
- To use a skill, first read its SKILL.md documentation
- Skills are registered in `/Users/henry/.claude/skills.json`

## GitHub 自动同步规则

**重要：每次操作 skills 后必须同步到 GitHub 仓库**

当执行以下任一操作后，**必须**自动提交并推送到 GitHub 仓库：
- 安装新 skill（使用 skillslm 或直接复制）
- 更新现有 skill
- 卸载/删除 skill

### 同步步骤
1. 检查 git 状态：`git status`
2. 添加所有变更：`git add -A`
3. 创建提交（使用有意义的 commit message）
4. 推送到远程：`git push`

### Commit Message 格式
```
[skill/action] skill-name: brief description

示例：
- [skill/install] Installed pdf skill for document processing
- [skill/update] Updated mcp-builder to latest version
- [skill/remove] Uninstalled unused skill: old-skill
```

**仓库路径：** `~/.claude/` 是 git 仓库根目录
**远程仓库：** （需要主人配置远程仓库 URL）