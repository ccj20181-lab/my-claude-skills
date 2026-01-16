# Common Skills Catalog

Frequently used skills from the anthropics/skills repository.

## Essential Skills

### mcp-builder
**Purpose**: Guide for creating MCP (Model Context Protocol) servers

**Use when**: Building integrations with external services

**Install**:
```bash
npx skillslm install mcp-builder --agent claude-code --global --yes
```

### skill-creator
**Purpose**: Guide for creating custom Claude Code skills

**Use when**: Developing new skills to extend Claude's capabilities

**Install**:
```bash
npx skillslm install skill-creator --agent claude-code --global --yes
```

## Document Processing Skills

### pdf
**Purpose**: PDF manipulation - extract text, merge, split, fill forms

**Use when**: Working with PDF documents

**Install**:
```bash
npx skillslm install pdf --agent claude-code --global --yes
```

### docx
**Purpose**: Word document creation and editing with tracked changes

**Use when**: Creating or modifying .docx files

**Install**:
```bash
npx skillslm install docx --agent claude-code --global --yes
```

### pptx
**Purpose**: PowerPoint presentation creation and editing

**Use when**: Building slide decks

**Install**:
```bash
npx skillslm install pptx --agent claude-code --global --yes
```

### xlsx
**Purpose**: Excel spreadsheet manipulation with formulas and formatting

**Use when**: Working with spreadsheets

**Install**:
```bash
npx skillslm install xlsx --agent claude-code --global --yes
```

## Development Skills

### frontend-design
**Purpose**: Create production-grade frontend interfaces with high design quality

**Use when**: Building web components, pages, or applications

**Install**:
```bash
npx skillslm install frontend-design --agent claude-code --global --yes
```

### distinctive-frontend-design
**Purpose**: Create distinctive, polished frontend code avoiding generic AI aesthetics

**Use when**: Building unique, creative web interfaces

**Install**:
```bash
npx skillslm install distinctive-frontend-design --agent claude-code --global --yes
```

### sdd-development
**Purpose**: Specification-Driven Development methodology

**Use when**: Following test-first, library-first development workflows

**Install**:
```bash
npx skillslm install sdd-development --agent claude-code --global --yes
```

## Design Skills

### canvas-design
**Purpose**: Create visual art in PNG and PDF using design principles

**Use when**: Designing posters, graphics, or static art pieces

**Install**:
```bash
npx skillslm install canvas-design --agent claude-code --global --yes
```

### theme-factory
**Purpose**: Apply consistent themes to artifacts (slides, docs, HTML)

**Use when**: Styling documents with pre-defined or custom themes

**Install**:
```bash
npx skillslm install theme-factory --agent claude-code --global --yes
```

### brand-guidelines
**Purpose**: Apply Anthropic's official brand colors and typography

**Use when**: Creating content with Anthropic branding

**Install**:
```bash
npx skillslm install brand-guidelines --agent claude-code --global --yes
```

### algorithmic-art
**Purpose**: Create algorithmic art using p5.js with seeded randomness

**Use when**: Generating generative art or flow fields

**Install**:
```bash
npx skillslm install algorithmic-art --agent claude-code --global --yes
```

## Product Knowledge

### product-self-knowledge
**Purpose**: Authoritative reference for Anthropic products

**Use when**: Users ask about Claude.ai, Claude Code, API features, pricing, limits

**Install**:
```bash
npx skillslm install product-self-knowledge --agent claude-code --global --yes
```

## Skill Combinations by Use Case

### Document Automation
```bash
npx skillslm install anthropics/skills \
  --skill pdf --skill docx --skill pptx --skill xlsx \
  --agent claude-code --global --yes
```

### Web Development
```bash
npx skillslm install anthropics/skills \
  --skill frontend-design --skill distinctive-frontend-design \
  --agent claude-code --global --yes
```

### Tool Development
```bash
npx skillslm install anthropics/skills \
  --skill mcp-builder --skill skill-creator \
  --agent claude-code --global --yes
```

### Creative Work
```bash
npx skillslm install anthropics/skills \
  --skill canvas-design --skill theme-factory --skill algorithmic-art \
  --agent claude-code --global --yes
```

## Finding More Skills

**List all available skills**:
```bash
npx skillslm install anthropics/skills --list
```

**Explore community repositories**:
```bash
npx skillslm install <org>/<repo> --list
```

## Skill Dependencies

Some skills work better together:

- **theme-factory** + **canvas-design** - Styled visual content
- **mcp-builder** + **skill-creator** - Tool development
- **frontend-design** + **theme-factory** - Themed web interfaces
- **pdf** + **docx** - Document conversion workflows
