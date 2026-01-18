# skillslm Command Reference

Complete syntax and options for all skillslm commands.

## install Command

### Basic Syntax

```bash
npx skillslm install <source> [options]
```

### Parameters

**source** (required)
- Skill name: `mcp-builder`
- GitHub URL: `https://github.com/anthropics/skills/tree/main/skills/pdf`
- Repository: `anthropics/skills`
- Shorthand: `anthropics/skills/skills/docx`

### Options

| Flag | Description | Example |
|------|-------------|---------|
| `-g, --global` | Install to global directory (~/.claude/skills/) | `--global` |
| `-a, --agent <name>` | Target AI agent (default: claude-code) | `--agent cursor` |
| `-s, --skill <name>` | Specify skill to install (repeatable) | `--skill pdf --skill docx` |
| `-y, --yes` | Skip confirmation prompts | `--yes` |
| `-l, --list` | List available skills only | `--list` |
| `--dir <path>` | Custom installation directory (legacy) | `--dir ./skills` |
| `--legacy` | Use legacy installation mode | `--legacy` |

### Installation Modes

**Global Installation** (Recommended)
```bash
npx skillslm install <skill> --agent claude-code --global --yes
```
- Location: `~/.claude/skills/`
- Available to all projects
- Easier to manage

**Project Installation**
```bash
npx skillslm install <skill> --agent claude-code --yes
```
- Location: `.claude/skills/`
- Project-specific
- Isolated from other projects

**Custom Directory** (Legacy)
```bash
npx skillslm install <skill> --dir ./my-skills --legacy
```
- Location: Specified path
- Manual management required

### Examples

**Single skill**
```bash
npx skillslm install pdf --agent claude-code --global --yes
```

**Multiple skills**
```bash
npx skillslm install anthropics/skills \
  --skill pdf --skill docx --skill pptx \
  --agent claude-code --global --yes
```

**Interactive mode**
```bash
npx skillslm install anthropics/skills
```

**List skills**
```bash
npx skillslm install anthropics/skills --list
```

**From custom repository**
```bash
npx skillslm install owner/repo --skill custom-skill --agent claude-code --global --yes
```

## update Command

### Syntax

```bash
npx skillslm update <skill-name> --dir <skills-directory>
```

### Examples

```bash
# Update single skill
npx skillslm update pdf --dir ~/.claude/skills

# Update multiple skills (requires script)
# See scripts/update-all.sh
```

## list Command

### Syntax

```bash
npx skillslm list
```

Lists all skills from the default anthropics/skills repository.

## Supported AI Agents

| Agent | Identifier | Project Path | Global Path |
|-------|-----------|--------------|-------------|
| Claude Code | `claude-code` | `.claude/skills` | `~/.claude/skills` |
| Cursor | `cursor` | `.cursor/skills` | `~/.cursor/skills` |
| Codex | `codex` | `.codex/skills` | `~/.codex/skills` |
| OpenCode | `opencode` | `.opencode/skill` | `~/.config/opencode/skill` |
| Amp | `amp` | `.agents/skills` | `~/.config/agents/skills` |
| Kilo Code | `kilo` | `.kilocode/skills` | `~/.kilocode/skills` |
| Roo Code | `roo` | `.roo/skills` | `~/.roo/skills` |
| Goose | `goose` | `.goose/skills` | `~/.config/goose/skills` |
| Antigravity | `antigravity` | `.agent/skills` | `~/.gemini/antigravity/skills` |

## URL Formats

skillslm accepts multiple URL formats:

**Full GitHub URL**
```bash
npx skillslm install https://github.com/anthropics/skills/tree/main/skills/mcp-builder
```

**Repository shorthand**
```bash
npx skillslm install anthropics/skills
```

**Skill path shorthand**
```bash
npx skillslm install anthropics/skills/skills/pdf
```

**Skill name** (uses default repository)
```bash
npx skillslm install mcp-builder
```

## Environment Variables

**Proxy Support**
```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

## Exit Codes

- `0` - Success
- `1` - Error (validation, network, permissions)

## Common Patterns

**CI/CD Installation**
```bash
#!/bin/bash
npx skillslm install anthropics/skills \
  --skill pdf --skill docx \
  --agent claude-code --global --yes
```

**Conditional Installation**
```bash
if [ ! -d ~/.claude/skills/pdf ]; then
  npx skillslm install pdf --agent claude-code --global --yes
fi
```

**Team Setup Script**
```bash
#!/bin/bash
SKILLS="mcp-builder skill-creator frontend-design pdf docx"
SKILL_ARGS=""
for skill in $SKILLS; do
  SKILL_ARGS="$SKILL_ARGS --skill $skill"
done

npx skillslm install anthropics/skills \
  $SKILL_ARGS \
  --agent claude-code --global --yes
```
