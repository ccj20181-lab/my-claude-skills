# Claude官方Skill安装指南

## 📋 已安装的Skill列表

以下是Claude Code官方开源的skill：


### 🔧 agent-sdk-dev
- **描述**: Development kit for working with the Claude Agent SDK
- **类别**: development
- **作者**: Unknown
- **路径**: `/Users/henry/.claude/skills/agent-sdk-dev/`
- **源码**: ./plugins/agent-sdk-dev


### 🔧 claude-opus-4-5-migration
- **描述**: Migrate your code and prompts from Sonnet 4.x and Opus 4.1 to Opus 4.5.
- **类别**: development
- **作者**: William Hu
- **路径**: `/Users/henry/.claude/skills/claude-opus-4-5-migration/`
- **源码**: ./plugins/claude-opus-4-5-migration


### 🔧 code-review
- **描述**: Automated code review for pull requests using multiple specialized agents with confidence-based scoring to filter false positives
- **类别**: productivity
- **作者**: Boris Cherny
- **路径**: `/Users/henry/.claude/skills/code-review/`
- **源码**: ./plugins/code-review


### 🔧 commit-commands
- **描述**: Commands for git commit workflows including commit, push, and PR creation
- **类别**: productivity
- **作者**: Anthropic
- **路径**: `/Users/henry/.claude/skills/commit-commands/`
- **源码**: ./plugins/commit-commands


### 🔧 explanatory-output-style
- **描述**: Adds educational insights about implementation choices and codebase patterns (mimics the deprecated Explanatory output style)
- **类别**: learning
- **作者**: Dickson Tsai
- **路径**: `/Users/henry/.claude/skills/explanatory-output-style/`
- **源码**: ./plugins/explanatory-output-style


### 🔧 feature-dev
- **描述**: Comprehensive feature development workflow with specialized agents for codebase exploration, architecture design, and quality review
- **类别**: development
- **作者**: Siddharth Bidasaria
- **路径**: `/Users/henry/.claude/skills/feature-dev/`
- **源码**: ./plugins/feature-dev


### 🔧 frontend-design
- **描述**: Create distinctive, production-grade frontend interfaces with high design quality. Generates creative, polished code that avoids generic AI aesthetics.
- **类别**: development
- **作者**: Prithvi Rajasekaran & Alexander Bricken
- **路径**: `/Users/henry/.claude/skills/frontend-design/`
- **源码**: ./plugins/frontend-design


### 🔧 hookify
- **描述**: Easily create custom hooks to prevent unwanted behaviors by analyzing conversation patterns or from explicit instructions. Define rules via simple markdown files.
- **类别**: productivity
- **作者**: Daisy Hollman
- **路径**: `/Users/henry/.claude/skills/hookify/`
- **源码**: ./plugins/hookify


### 🔧 learning-output-style
- **描述**: Interactive learning mode that requests meaningful code contributions at decision points (mimics the unshipped Learning output style)
- **类别**: learning
- **作者**: Boris Cherny
- **路径**: `/Users/henry/.claude/skills/learning-output-style/`
- **源码**: ./plugins/learning-output-style


### 🔧 plugin-dev
- **描述**: Comprehensive toolkit for developing Claude Code plugins. Includes 7 expert skills covering hooks, MCP integration, commands, agents, and best practices. AI-assisted plugin creation and validation.
- **类别**: development
- **作者**: Daisy Hollman
- **路径**: `/Users/henry/.claude/skills/plugin-dev/`
- **源码**: ./plugins/plugin-dev


### 🔧 pr-review-toolkit
- **描述**: Comprehensive PR review agents specializing in comments, tests, error handling, type design, code quality, and code simplification
- **类别**: productivity
- **作者**: Anthropic
- **路径**: `/Users/henry/.claude/skills/pr-review-toolkit/`
- **源码**: ./plugins/pr-review-toolkit


### 🔧 ralph-wiggum
- **描述**: Interactive self-referential AI loops for iterative development. Claude works on the same task repeatedly, seeing its previous work, until completion.
- **类别**: development
- **作者**: Daisy Hollman
- **路径**: `/Users/henry/.claude/skills/ralph-wiggum/`
- **源码**: ./plugins/ralph-wiggum


### 🔧 security-guidance
- **描述**: Security reminder hook that warns about potential security issues when editing files, including command injection, XSS, and unsafe code patterns
- **类别**: security
- **作者**: David Dworken
- **路径**: `/Users/henry/.claude/skills/security-guidance/`
- **源码**: ./plugins/security-guidance


## 🚀 使用方法

### 1. 在Claude Code中使用Skill
您可以通过以下方式使用已安装的skill：

```bash
# 直接调用skill
/claude-code-skill-name

# 或者在配置文件中启用
```

### 2. 启用/禁用Skill
编辑skill配置文件：
```bash
# 编辑skill配置
nano ~/.claude/skills/skill-name/skill.config.json

# 设置 enabled 为 true
```

### 3. 查看已安装的Skill
```bash
# 列出所有skill
ls -la ~/.claude/skills/

# 查看skill详情
cat ~/.claude/skills/skill-name/skill.config.json
```

### 4. 更新Skill
```bash
# 重新运行安装脚本
bash install_claude_skills_v2.sh
```

## 📚 Skill分类说明

### 🔧 开发工具类 (Development)
- **agent-sdk-dev**: Claude Agent SDK开发工具包
- **plugin-dev**: Claude Code插件开发工具包
- **feature-dev**: 功能开发工作流
- **frontend-design**: 前端界面设计

### 🔍 代码质量类 (Productivity)
- **code-review**: 自动化代码审查
- **pr-review-toolkit**: PR审查工具包
- **commit-commands**: Git提交工作流
- **hookify**: 自定义Hook创建

### 🔒 安全类 (Security)
- **security-guidance**: 安全提醒

### 📖 学习类 (Learning)
- **explanatory-output-style**: 解释性输出风格
- **learning-output-style**: 交互式学习模式

### 🔄 特殊工具 (Special)
- **claude-opus-4-5-migration**: Claude版本迁移工具
- **ralph-wiggum**: 迭代开发循环

## 📁 文件结构

```
~/.claude/
├── skills/                    # Skill目录
│   ├── agent-sdk-dev/        # Agent SDK开发工具
│   ├── code-review/          # 代码审查工具
│   ├── feature-dev/         # 功能开发
│   ├── ...                   # 其他skill
│   └── README.md             # 本文件
└── skills.json               # 全局配置文件
```

## 📚 更多信息

- [Claude Code官方文档](https://code.claude.com/docs)
- [GitHub仓库](https://github.com/anthropics/claude-code)
- [Claude API文档](https://docs.anthropic.com)

## 🆘 故障排除

### Skill无法工作
1. 检查skill目录权限
2. 验证配置文件格式
3. 查看Claude Code日志

### 权限问题
```bash
chmod -R 755 ~/.claude/skills/
```

### 重置安装
```bash
# 删除skill目录
rm -rf ~/.claude/skills/

# 重新安装
bash install_claude_skills_v2.sh
```

## 更新日志

- **安装时间**: 2026年 1月 8日 星期四 10时50分07秒 CST
- **Skill数量**:       23
- **系统版本**: Darwin 23.5.0
