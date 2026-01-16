---
name: skillslm-manager
description: "Manage Claude Code Skills using skillslm package manager. Use when users need to: (1) discover and list available skills, (2) install new skills (single or batch), (3) update existing skills, (4) set up team or project environments with specific skill combinations, (5) troubleshoot skill installation issues, or (6) ask about skill management best practices. Handles all skillslm commands including install, update, list, and custom configurations."
---

# skillslm Manager

Manage Claude Code Skills using the skillslm package manager - discover, install, update, and organize skills efficiently.

## Core Workflow

When a user requests skill management, follow this decision tree:

```
User request
├─ "What skills are available?" → List skills
├─ "Install [skill-name]" → Install single skill
├─ "Set up [environment type]" → Install preset combination
├─ "Update skills" → Update existing skills
└─ "Having trouble with..." → Troubleshoot
```

## Quick Start

### List Available Skills

```bash
# List all skills from official repository
npx skillslm install anthropics/skills --list

# List from custom repository
npx skillslm install owner/repo --list
```

### Install Single Skill

```bash
# Template
npx skillslm install <skill-name> --agent claude-code --global --yes

# Examples
npx skillslm install pdf --agent claude-code --global --yes
npx skillslm install mcp-builder --agent claude-code --global --yes
```

**Key flags:**
- `--global` - Install to `~/.claude/skills/` (recommended)
- `--agent claude-code` - Target Claude Code
- `--yes` - Skip confirmation (for automation)

### Install Multiple Skills (Batch)

```bash
# Template
npx skillslm install anthropics/skills \
  --skill <name1> --skill <name2> --skill <name3> \
  --agent claude-code --global --yes

# Example: Document processing setup
npx skillslm install anthropics/skills \
  --skill pdf --skill docx --skill pptx --skill xlsx \
  --agent claude-code --global --yes
```

## Common Scenarios

### Scenario 1: New User Setup

User says: "I'm new, what should I install?"

```bash
# Install essential skills
npx skillslm install anthropics/skills \
  --skill mcp-builder \
  --skill skill-creator \
  --agent claude-code --global --yes
```

### Scenario 2: Document Processing

User says: "I need to work with PDFs and Word documents"

```bash
npx skillslm install anthropics/skills \
  --skill pdf --skill docx \
  --agent claude-code --global --yes
```

### Scenario 3: Web Development

User says: "Set up for frontend development"

```bash
npx skillslm install anthropics/skills \
  --skill frontend-design \
  --skill distinctive-frontend-design \
  --agent claude-code --global --yes
```

### Scenario 4: Complete Environment

User says: "Install everything I might need"

Refer to `references/preset-combinations.md` for full installation commands.

## Interactive Installation

For users who prefer menus over commands:

```bash
# Launch interactive mode
npx skillslm install anthropics/skills
```

This presents:
- Skill selection checkboxes
- Installation scope choice (global/project)
- Confirmation before installing

## Update Skills

```bash
# Update specific skill
npx skillslm update <skill-name> --dir ~/.claude/skills

# Examples
npx skillslm update pdf --dir ~/.claude/skills
npx skillslm update mcp-builder --dir ~/.claude/skills
```

For batch updates, see `scripts/update-all.sh`.

## Verify Installation

```bash
# Check global skills
ls -la ~/.claude/skills/

# Check project skills
ls -la .claude/skills/

# Verify specific skill
ls -la ~/.claude/skills/<skill-name>/SKILL.md
```

## Troubleshooting

### Issue: npx command not found

**Solution**: Install Node.js

```bash
# macOS
brew install node

# Ubuntu/Debian
sudo apt install nodejs npm
```

### Issue: Permission errors

**Solution**: Use global installation

```bash
# Use --global flag to install to user directory
npx skillslm install <skill> --agent claude-code --global --yes
```

### Issue: Skill not appearing in Claude Code

**Solution**: Verify and fix permissions

```bash
# Check if file exists
ls -la ~/.claude/skills/<skill-name>/SKILL.md

# Fix permissions
chmod -R 755 ~/.claude/skills/

# Restart Claude Code
```

### Issue: Network timeouts

**Solution**: Check network or retry later. GitHub access required for downloads.

## Best Practices

1. **Prefer Global Installation** - Use `--global` flag
   - Skills available across all projects
   - Avoid duplication
   - Easier to manage

2. **Batch Related Skills** - Install together
   - More efficient than multiple commands
   - Ensures compatible versions
   - Saves time

3. **Use Automation Flags** - Add `--yes` for scripts
   - Skip confirmation prompts
   - Enable CI/CD integration
   - Streamline workflows

4. **Regular Updates** - Keep skills current
   - Monthly update schedule recommended
   - Use batch update script
   - Review changelogs

## Advanced Usage

### Custom Repositories

```bash
# List skills from community repo
npx skillslm install community-org/skills --list

# Install from custom repo
npx skillslm install community-org/skills \
  --skill custom-skill \
  --agent claude-code --global --yes
```

### Project-Specific Skills

```bash
# Install to project directory (omit --global)
cd /path/to/project
npx skillslm install project-skill --agent claude-code --yes

# Skills install to .claude/skills/
```

### Environment Variables

```bash
# Use proxy if needed
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080

npx skillslm install <skill> --agent claude-code --global --yes
```

## Resources

### scripts/

- `install-presets.sh` - Interactive menu for preset combinations
- `update-all.sh` - Batch update all installed skills

### references/

- `preset-combinations.md` - Pre-configured skill sets for common needs
- `command-reference.md` - Complete command syntax and options
- `common-skills.md` - Catalog of frequently used skills

**Usage**: When users need detailed information, load the appropriate reference file.

## Key Principles

**When responding to skill management requests:**

1. **Start Simple** - Show the minimal command that works
2. **Explain Flags** - Briefly note what each flag does
3. **Provide Context** - Mention why a choice (global vs project) matters
4. **Offer Alternatives** - Suggest related skills when relevant
5. **Verify Success** - Show how to confirm installation worked

**Always use `--agent claude-code --global --yes` for standard installations unless:**
- User explicitly wants project-level
- User requests interactive mode
- Installing to non-Claude-Code agent

