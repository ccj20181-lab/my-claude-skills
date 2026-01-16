# Claude Skill 快速参考

## 🎯 常用Skill命令

### 代码开发
```bash
/feature-dev          # 功能开发工作流
/plugin-dev           # 插件开发
/agent-sdk-dev        # Agent SDK开发
/frontend-design      # 前端设计
```

### 代码质量
```bash
/code-review          # 代码审查
/pr-review-toolkit    # PR审查
/commit-commands      # 提交工作流
```

### 学习辅助
```bash
/explanatory-output-style  # 解释性输出
/learning-output-style    # 交互式学习
```

### 特殊工具
```bash
/claude-opus-4-5-migration  # 版本迁移
/ralph-wiggum               # 迭代开发
/hookify                    # Hook创建
/security-guidance          # 安全提醒
```

## ⚙️ 配置文件位置
- Skill目录: `~/.claude/skills/`
- 全局配置: `~/.claude/skills.json`
- Skill配置: `~/.claude/skills/skill-name/skill.config.json`

## 🔧 常用操作
```bash
# 列出所有skill
ls ~/.claude/skills/

# 查看skill配置
cat ~/.claude/skills/skill-name/skill.config.json

# 启用skill
编辑 skill.config.json 设置 "enabled": true

# 更新skill
bash install_claude_skills_v2.sh
```
