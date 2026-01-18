# Preset Skill Combinations

Pre-configured skill sets for common development needs. Copy and execute commands directly.

## 1. Essential (Recommended for All Users)

**Skills**: mcp-builder, skill-creator

**Use for**: Learning to create MCP servers and custom skills

```bash
npx skillslm install anthropics/skills \
  --skill mcp-builder \
  --skill skill-creator \
  --agent claude-code --global --yes
```

## 2. Document Processing

**Skills**: pdf, docx, pptx, xlsx

**Use for**: Working with PDFs, Word docs, PowerPoint, Excel

```bash
npx skillslm install anthropics/skills \
  --skill pdf \
  --skill docx \
  --skill pptx \
  --skill xlsx \
  --agent claude-code --global --yes
```

## 3. Web Development

**Skills**: frontend-design, distinctive-frontend-design

**Use for**: Building frontend interfaces and components

```bash
npx skillslm install anthropics/skills \
  --skill frontend-design \
  --skill distinctive-frontend-design \
  --agent claude-code --global --yes
```

## 4. Full-Stack Developer

**Skills**: frontend-design, mcp-builder, sdd-development, pdf, docx

**Use for**: Complete development environment

```bash
npx skillslm install anthropics/skills \
  --skill mcp-builder \
  --skill skill-creator \
  --skill frontend-design \
  --skill sdd-development \
  --skill pdf \
  --skill docx \
  --agent claude-code --global --yes
```

## 5. Content Creation

**Skills**: canvas-design, theme-factory, brand-guidelines, algorithmic-art

**Use for**: Design work, branding, visual content

```bash
npx skillslm install anthropics/skills \
  --skill canvas-design \
  --skill theme-factory \
  --skill brand-guidelines \
  --skill algorithmic-art \
  --agent claude-code --global --yes
```

## 6. Complete Installation

**Skills**: All public skills from anthropics/skills

**Use for**: Maximum functionality (use disk space wisely)

```bash
npx skillslm install anthropics/skills \
  --skill mcp-builder \
  --skill skill-creator \
  --skill pdf \
  --skill docx \
  --skill pptx \
  --skill xlsx \
  --skill frontend-design \
  --skill distinctive-frontend-design \
  --skill canvas-design \
  --skill theme-factory \
  --skill brand-guidelines \
  --skill algorithmic-art \
  --skill sdd-development \
  --skill product-self-knowledge \
  --agent claude-code --global --yes
```

## Mixing and Matching

Combine skills from different presets:

```bash
# Example: Web development + document processing
npx skillslm install anthropics/skills \
  --skill frontend-design \
  --skill pdf \
  --skill docx \
  --agent claude-code --global --yes
```

## Team Standard Setup

Recommended baseline for development teams:

```bash
npx skillslm install anthropics/skills \
  --skill mcp-builder \
  --skill skill-creator \
  --skill frontend-design \
  --skill pdf \
  --skill docx \
  --agent claude-code --global --yes
```
