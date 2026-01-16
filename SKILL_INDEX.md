# Claude官方Skill索引

## 📋 已安装的Skill列表

以下是Claude Code官方开源的所有skill：


### 🔧 agent-sdk-dev
- **位置**: `/Users/henry/.claude/skills/agent-sdk-dev/`
- **配置文件**: `/Users/henry/.claude/skills/agent-sdk-dev/skill.config.json`


### 🔧 claude-opus-4-5-migration
- **位置**: `/Users/henry/.claude/skills/claude-opus-4-5-migration/`
- **配置文件**: `/Users/henry/.claude/skills/claude-opus-4-5-migration/skill.config.json`


### 🔧 code-review
- **位置**: `/Users/henry/.claude/skills/code-review/`
- **配置文件**: `/Users/henry/.claude/skills/code-review/skill.config.json`


### 🔧 commit-commands
- **位置**: `/Users/henry/.claude/skills/commit-commands/`
- **配置文件**: `/Users/henry/.claude/skills/commit-commands/skill.config.json`


### 🔧 explanatory-output-style
- **位置**: `/Users/henry/.claude/skills/explanatory-output-style/`
- **配置文件**: `/Users/henry/.claude/skills/explanatory-output-style/skill.config.json`


### 🔧 feature-dev
- **位置**: `/Users/henry/.claude/skills/feature-dev/`
- **配置文件**: `/Users/henry/.claude/skills/feature-dev/skill.config.json`


### 🔧 frontend-design
- **位置**: `/Users/henry/.claude/skills/frontend-design/`
- **配置文件**: `/Users/henry/.claude/skills/frontend-design/skill.config.json`


### 🔧 hookify
- **位置**: `/Users/henry/.claude/skills/hookify/`
- **配置文件**: `/Users/henry/.claude/skills/hookify/skill.config.json`


### 🔧 learning-output-style
- **位置**: `/Users/henry/.claude/skills/learning-output-style/`
- **配置文件**: `/Users/henry/.claude/skills/learning-output-style/skill.config.json`


### 🔧 plugin-dev
- **位置**: `/Users/henry/.claude/skills/plugin-dev/`
- **配置文件**: `/Users/henry/.claude/skills/plugin-dev/skill.config.json`


### 🔧 pr-review-toolkit
- **位置**: `/Users/henry/.claude/skills/pr-review-toolkit/`
- **配置文件**: `/Users/henry/.claude/skills/pr-review-toolkit/skill.config.json`


### 🔧 ralph-wiggum
- **位置**: `/Users/henry/.claude/skills/ralph-wiggum/`
- **配置文件**: `/Users/henry/.claude/skills/ralph-wiggum/skill.config.json`


### 🔧 security-guidance
- **位置**: `/Users/henry/.claude/skills/security-guidance/`
- **配置文件**: `/Users/henry/.claude/skills/security-guidance/skill.config.json`


## 📁 文件结构

```
~/.claude/
├── skills/                    # Skill目录
│   ├── agent-sdk-dev/        # Agent SDK工具
│   ├── code-review/          # 代码审查
│   ├── feature-dev/         # 功能开发
│   ├── plugin-dev/          # 插件开发
│   ├── frontend-design/     # 前端设计
│   ├── security-guidance/   # 安全提醒
│   ├── ...                  # 其他skill
│   └── SKILL_INDEX.md       # 本文件
└── skills.json               # 全局配置文件
```

## 🚀 使用方法

### 1. 启用Skill
在Claude Code中，您可以通过以下方式使用skill：
```bash
# 直接调用skill（如果支持）
/skill-name
```

### 2. 配置Skill
编辑skill配置文件：
```bash
nano ~/.claude/skills/skill-name/skill.config.json
```

### 3. 查看Skill详情
```bash
# 查看skill目录
ls -la ~/.claude/skills/skill-name/

# 查看配置文件
cat ~/.claude/skills/skill-name/skill.config.json
```

## 📚 更多信息

- [官方文档](https://code.claude.com/docs)
- [GitHub仓库](https://github.com/anthropics/claude-code/tree/main/plugins)
- [Claude API文档](https://docs.anthropic.com)

- **安装时间**: 2026年 1月 8日 星期四 10时59分52秒 CST
- **安装版本**: Final Edition
