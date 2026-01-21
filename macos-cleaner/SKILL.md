---
name: macos-cleaner
description: Analyze and reclaim macOS disk space through intelligent cleanup recommendations. This skill should be used when users report disk space issues, need to clean up their Mac, or want to understand what's consuming storage. Focus on safe, interactive analysis with user confirmation before any deletions.
---

# macOS Cleaner

## Overview

Intelligently analyze macOS disk usage and provide actionable cleanup recommendations to reclaim storage space. This skill follows a **safety-first philosophy**: analyze thoroughly, present clear findings, and require explicit user confirmation before executing any deletions.

**Target users**: Users with basic technical knowledge who understand file systems but need guidance on what's safe to delete on macOS.

## Core Principles

1. **Safety First, Never Bypass**: NEVER execute dangerous commands (`rm -rf`, `mo clean`, etc.) without explicit user confirmation. No shortcuts, no workarounds.
2. **Value Over Vanity**: Your goal is NOT to maximize cleaned space. Your goal is to identify what is **truly useless** vs **valuable cache**. Clearing 50GB of useful cache just to show a big number is harmful.
3. **Network Environment Awareness**: Many users (especially in China) have slow/unreliable internet. Re-downloading caches can take hours. A cache that saves 30 minutes of download time is worth keeping.
4. **Impact Analysis Required**: Every cleanup recommendation MUST include "what happens if deleted" column. Never just list items without explaining consequences.
5. **Patience Over Speed**: Disk scans can take 5-10 minutes. NEVER interrupt or skip slow operations. Report progress to user regularly.
6. **User Executes Cleanup**: After analysis, provide the cleanup command for the user to run themselves. Do NOT auto-execute cleanup.
7. **Conservative Defaults**: When in doubt, don't delete. Err on the side of caution.

**ABSOLUTE PROHIBITIONS:**
- ❌ NEVER run `rm -rf` on user directories automatically
- ❌ NEVER run `mo clean` without dry-run preview first
- ❌ NEVER use `docker volume prune -f` or `docker system prune -a --volumes`
- ❌ NEVER skip analysis steps to save time
- ❌ NEVER append `--help` to Mole commands (except `mo --help`)
- ❌ NEVER recommend deleting useful caches just to inflate cleanup numbers

## Workflow Decision Tree

```
User reports disk space issues
           ↓
    Quick Diagnosis
           ↓
    ┌──────┴──────┐
    │             │
Immediate    Deep Analysis
 Cleanup      (continue below)
    │             │
    └──────┬──────┘
           ↓
  Present Findings
           ↓
   User Confirms
           ↓
   Execute Cleanup
           ↓
  Verify Results
```

## Quick Start

### Step 1: Quick Diagnosis with Mole

**Primary tool**: Use Mole for disk analysis. It provides comprehensive, categorized results.

```bash
# Check Mole installation
which mo && mo --version

# Install if needed
brew install tw93/tap/mole

# Run analysis via tmux (REQUIRED - Mole needs TTY)
tmux new-session -d -s mole -x 120 -y 40
tmux send-keys -t mole 'mo analyze' Enter

# Wait for scan (5-10 minutes for home directories)
# Be patient! Report progress to user regularly.
```

⚠️ **CRITICAL**: Home directory scans are SLOW (5-10 minutes). Inform user upfront and wait patiently.

### Step 2: Analyze Key Categories

After initial scan, systematically analyze these categories:

1. **System & Application Caches** - `~/Library/Caches/*`
2. **Application Remnants** - `~/Library/Application Support/*`
3. **Large Files** - Files >100MB in `~/Downloads`, `~/Documents`
4. **Developer Tools** - Docker, npm, pip, Homebrew caches

📖 **Detailed guides**: See `references/analysis-categories.md`

### Step 3: Present Findings

Format findings using the **standard report template** with impact analysis:

```markdown
## Disk Analysis Report

### Classification Legend
| Symbol | Meaning |
|--------|---------|
| 🟢 | **Absolutely Safe** - No negative impact |
| 🟡 | **Trade-off Required** - Useful cache, deletion has cost |
| 🔴 | **Do Not Delete** - Contains valuable data |

### Findings

| Item | Size | Classification | Impact If Deleted |
|------|------|----------------|-------------------|
| Trash | 643 MB | 🟢 | None |
| npm _cacache | 5 GB | 🟡 | 30min-2hr redownload |
| DerivedData | 10 GB | 🟡 | 10-30min rebuild |
| Docker volumes | 11 GB | 🔴 | **DATA LOSS** |
```

📖 **Report template**: See `references/report-template.md`

### Step 4: Execute with Confirmation

**CRITICAL**: Never execute deletions without explicit user confirmation.

Provide cleanup commands for user to run themselves:
```bash
# Example: Safe cleanup (user executes)
rm -rf ~/.Trash/*
rm -rf ~/.npm/_npx
brew cleanup -s
```

⚠️ **NEVER auto-execute** dangerous operations like Docker volume cleanup.

## Detailed Documentation

For comprehensive guides, see:

- **[Mole Usage Guide](references/mole-usage-guide.md)** - Complete Mole CLI workflow, tmux integration, multi-layer exploration
- **[Analysis Categories](references/analysis-categories.md)** - Detailed breakdown of cleanup targets by category
- **[Anti-Patterns](references/anti-patterns.md)** - What NOT to delete and why (valuable caches)
- **[Report Template](references/report-template.md)** - High-quality report format with examples
- **[Safety Guidelines](references/safety-guidelines.md)** - Comprehensive safety rules and confirmation workflows
- **[Troubleshooting](references/troubleshooting.md)** - Common issues and solutions
- **[Usage Examples](references/usage-examples.md)** - Real-world workflow examples

## Key Anti-Patterns to Avoid

**Do NOT recommend deleting these valuable caches:**

| Item | Why NOT to Delete | Real Impact |
|------|-------------------|-------------|
| **Xcode DerivedData** | 10+ GB | Build cache saves 10-30 min per rebuild |
| **npm _cacache** | 5+ GB | `npm install` redownloads everything (30min-2hr) |
| **~/.cache/uv** | 10+ GB | Python packages - slow to redownload |
| **Playwright browsers** | 3-4 GB | Redownload 2GB+ each time (30min-1hr) |

📖 **Complete anti-patterns list**: See `references/anti-patterns.md`

## When NOT to Use This Skill

- User wants automatic/silent cleanup (against safety-first principle)
- User needs Windows/Linux cleanup (macOS-specific skill)
- User has <10% disk usage (no cleanup needed)
- User wants to clean system files requiring SIP disable (security risk)

## Resources

### Documentation
- `references/` - Complete detailed guides
- `SKILL.md` (this file) - Quick reference

### External Tools
- **Mole**: https://github.com/tw93/Mole - Interactive disk cleanup tool

---

**Version**: 2.0 (Optimized - split into modular documentation)
**Last Updated**: 2026-01-21
