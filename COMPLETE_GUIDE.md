# Claude官方Skill完整使用指南

## 🎯 概述

本指南包含了Claude Code官方开源的所有Skill和Agent的详细使用方法。

## 📦 已安装的Skill


### 🔧 Anthropic
- **位置**: `/Users/henry/.claude/skills/Anthropic/`
- **文件列表**:

### 🔧 Boris Cherny
- **位置**: `/Users/henry/.claude/skills/Boris Cherny/`
- **文件列表**:

### 🔧 Daisy Hollman
- **位置**: `/Users/henry/.claude/skills/Daisy Hollman/`
- **文件列表**:

### 🔧 David Dworken
- **位置**: `/Users/henry/.claude/skills/David Dworken/`
- **文件列表**:

### 🔧 Dickson Tsai
- **位置**: `/Users/henry/.claude/skills/Dickson Tsai/`
- **文件列表**:

### 🔧 Prithvi Rajasekaran & Alexander Bricken
- **位置**: `/Users/henry/.claude/skills/Prithvi Rajasekaran & Alexander Bricken/`
- **文件列表**:

### 🔧 Siddharth Bidasaria
- **位置**: `/Users/henry/.claude/skills/Siddharth Bidasaria/`
- **文件列表**:

### 🔧 William Hu
- **位置**: `/Users/henry/.claude/skills/William Hu/`
- **文件列表**:

### 🔧 agent-sdk-dev
- **位置**: `/Users/henry/.claude/skills/agent-sdk-dev/`
- **文件列表**:

### 🔧 claude-code-plugins
- **位置**: `/Users/henry/.claude/skills/claude-code-plugins/`
- **文件列表**:

### 🔧 claude-opus-4-5-migration
- **位置**: `/Users/henry/.claude/skills/claude-opus-4-5-migration/`
- **文件列表**:

### 🔧 code-review
- **位置**: `/Users/henry/.claude/skills/code-review/`
- **文件列表**:

### 🔧 commit-commands
- **位置**: `/Users/henry/.claude/skills/commit-commands/`
- **文件列表**:

### 🔧 explanatory-output-style
- **位置**: `/Users/henry/.claude/skills/explanatory-output-style/`
- **文件列表**:

### 🔧 feature-dev
- **位置**: `/Users/henry/.claude/skills/feature-dev/`
- **文件列表**:

### 🔧 frontend-design
- **位置**: `/Users/henry/.claude/skills/frontend-design/`
- **文件列表**:

### 🔧 hookify
- **位置**: `/Users/henry/.claude/skills/hookify/`
- **文件列表**:

### 🔧 learning-output-style
- **位置**: `/Users/henry/.claude/skills/learning-output-style/`
- **文件列表**:

### 🔧 plugin-dev
- **位置**: `/Users/henry/.claude/skills/plugin-dev/`
- **文件列表**:

### 🔧 pr-review-toolkit
- **位置**: `/Users/henry/.claude/skills/pr-review-toolkit/`
- **文件列表**:

### 🔧 ralph-wiggum
- **位置**: `/Users/henry/.claude/skills/ralph-wiggum/`
- **文件列表**:

### 🔧 security-guidance
- **位置**: `/Users/henry/.claude/skills/security-guidance/`
- **文件列表**:

## 🚀 使用方法

### 1. 启用Skill
在Claude Code中，您可以通过以下方式使用skill：

```bash
# 直接调用skill（如果支持）
/skill-name

# 或者通过配置文件
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

## 📚 常用Skill类别

### 🔧 开发工具
- **agent-sdk-dev**: Claude Agent SDK开发工具
- **plugin-dev**: Claude Code插件开发
- **feature-dev**: 功能开发工作流
- **frontend-design**: 前端设计工具

### 🔍 代码质量
- **code-review**: 代码审查工具
- **pr-review-toolkit**: PR审查工具
- **commit-commands**: Git提交工作流

### 📖 学习辅助
- **explanatory-output-style**: 解释性输出
- **learning-output-style**: 交互式学习

### 🔒 安全
- **security-guidance**: 安全提醒

### 🔄 特殊工具
- **claude-opus-4-5-migration**: 版本迁移
- **ralph-wiggum**: 迭代开发
- **hookify**: Hook创建

## 🛠️ 维护命令

### 更新Skill
```bash
# 重新运行安装脚本
bash install_claude_skills_complete.sh
```

### 清理安装
```bash
rm -rf ~/.claude/skills/
bash install_claude_skills_complete.sh
```

### 查看日志
```bash
# 查看Claude Code日志
tail -f ~/.claude/logs/claude-code.log
```

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
│   ├── README.md            # 基础指南
│   ├── QUICK_REFERENCE.md   # 快速参考
│   ├── SKILL_INDEX.md       # Skill索引
│   └── COMPLETE_GUIDE.md    # 完整指南
└── skills.json              # 全局配置
```

## 📞 支持

- [官方文档](https://code.claude.com/docs)
- [GitHub仓库](https://github.com/anthropics/claude-code)
- [Claude API文档](https://docs.anthropic.com)

## 更新日志
- **安装时间**: 2026年 1月 8日 星期四 10时57分23秒 CST
- **安装版本**: Complete Edition
