---
name: planning-with-files
description: Transforms workflow to use Manus-style persistent markdown files for planning, progress tracking, and knowledge storage. Use when starting complex tasks, multi-step projects, research tasks, or when the user mentions planning, organizing work, tracking progress, or wants structured output.
---

# Planning with Files

Work like Manus: Use persistent markdown files as your "working memory on disk."

## Quick Start

Before ANY complex task:

1. **Create `task_plan.md`** in the working directory
2. **Define phases** with checkboxes
3. **Update after each phase** - mark [x] and change status
4. **Read before deciding** - refresh goals in attention window

## The 3-File Pattern

For every non-trivial task, create THREE files:

| File | Purpose | When to Update |
|------|---------|----------------|
| `task_plan.md` | Track phases and progress | After each phase |
| `notes.md` | Store findings and research | During research |
| `[deliverable].md` | Final output | At completion |

## Core Workflow

```
Loop 1: Create task_plan.md with goal and phases
Loop 2: Research → save to notes.md → update task_plan.md
Loop 3: Read notes.md → create deliverable → update task_plan.md
Loop 4: Deliver final output
```

### The Loop in Detail

**Before each major action:**
```bash
Read task_plan.md  # Refresh goals in attention window
```

**After each phase:**
```bash
Edit task_plan.md  # Mark [x], update status
```

**When storing information:**
```bash
Write notes.md     # Don't stuff context, store in file
```

## task_plan.md Template

Create this file FIRST for any complex task:

```markdown
# Task Plan: [Brief Description]

## Goal
[One sentence describing the end state]

## Phases
- [ ] Phase 1: Plan and setup
- [ ] Phase 2: Research/gather information
- [ ] Phase 3: Execute/build
- [ ] Phase 4: Review and deliver

## Key Questions
1. [Question to answer]
2. [Question to answer]

## Decisions Made
- [Decision]: [Rationale]

## Errors Encountered
- [Error]: [Resolution]

## Status
**Currently in Phase X** - [What I'm doing now]
```

## notes.md Template

For research and findings:

```markdown
# Notes: [Topic]

## Sources

### Source 1: [Name]
- URL: [link]
- Key points:
  - [Finding]
  - [Finding]

## Synthesized Findings

### [Category]
- [Finding]
- [Finding]
```

## Critical Rules

### 1. ALWAYS Create Plan First
Never start a complex task without `task_plan.md`. This is non-negotiable.

### 2. Read Before Decide
Before any major decision, read the plan file. This keeps goals in your attention window.

### 3. Update After Act
After completing any phase, immediately update the plan file:
- Mark completed phases with [x]
- Update the Status section
- Log any errors encountered

### 4. Store, Don't Stuff
Large outputs go to files, not context. Keep only paths in working memory.

### 5. Log All Errors
Every error goes in the "Errors Encountered" section. This builds knowledge for future tasks.

## When to Use This Pattern

**Use 3-file pattern for:**
- Multi-step tasks (3+ steps)
- Research tasks
- Building/creating something
- Tasks spanning multiple tool calls
- Anything requiring organization

**Skip for:**
- Simple questions
- Single-file edits
- Quick lookups

## Anti-Patterns to Avoid

| Don't | Do Instead |
|-------|------------|
| Use TodoWrite for persistence | Create `task_plan.md` file |
| State goals once and forget | Re-read plan before each decision |
| Hide errors and retry | Log errors to plan file |
| Stuff everything in context | Store large content in files |
| Start executing immediately | Create plan file FIRST |

## Advanced Patterns

See [reference.md](reference.md) for:
- Attention manipulation techniques
- Error recovery patterns
- Context optimization from Manus

See [examples.md](examples.md) for:
- Real task examples
- Complex workflow patterns


## User-Learned Best Practices & Constraints

> **Auto-Generated Section**: This section is maintained by `skill-evolution-manager`. Do not edit manually.
> **Last Updated**: 2025-01-25

---

### ✅ 已验证的最佳实践

#### 1. 三文件模式 (The 3-File Pattern)

对于任何复杂任务，创建以下三个文件：

| 文件 | 用途 | 更新时机 |
|------|------|---------|
| `task_plan.md` | 跟踪阶段和进度 | 每个阶段完成后 |
| `notes.md` | 存储发现和研究 | 研究过程中 |
| `[deliverable].md` | 最终产出 | 完成时 |

**核心优势**：
- ✅ 将工作记忆持久化到磁盘
- ✅ 减少上下文占用
- ✅ 便于长期回顾和知识沉淀

#### 2. 完整复盘模板

复盘文档应包含以下核心章节：

```markdown
## 执行概况
- 任务名称、时间、工具、成果

## 执行流程复盘
- Phase 1-4 详细记录

## 技术亮点
- 架构优化、代码改进、搜索策略

## 问题与解决
- 遇到的问题、原因分析、解决方案

## 经验总结
- 成功要素、改进空间

## 知识沉淀
- 关键决策、最佳实践、可复用模式

## 附录
- 完整报告列表、参考资料
```

#### 3. 结构化数据呈现

使用表格和代码块提高可读性：

| 批次 | 数量 | 主题 | 成功率 |
|------|------|------|--------|
| 第一批 | 1 | 信通院AI发展报告 | 1/1 (100%) |
| 第二批 | 4 | 国际技术报告 | 4/4 (100%) |

---

### 🎓 真实案例

#### 案例 1: AI 研究报告下载任务复盘 (2025-01-25)

**任务背景**：
- 执行技能迁移（Playwright → agent-browser）
- 批量下载 AI 研究报告
- 创建完整复盘文档

**使用模式**：
1. **执行前**：阅读迁移计划文档，理解技术方案
2. **执行中**：渐进式迁移，先简单后复杂
3. **执行后**：调用 planning-with-files 创建复盘

**关键成功要素**：
- ✅ 充分的前期准备
- ✅ 渐进式执行策略
- ✅ 灵活的搜索策略
- ✅ 完整的经验沉淀

**成果**：
- 23 份报告，183 MB
- 完整的复盘文档（包含执行流程、技术亮点、问题解决）
- 可复用的模式和决策记录

#### 案例 2: 技能迁移复盘 (2025-01-25)

**任务背景**：
- 将 report-hunter 从 Playwright 迁移到纯 HTTP 模式
- 将 dingtalk-lark-pdf 迁移到 agent-browser CLI
- Git 提交并推送

**复盘亮点**：
1. **架构演进清晰**：详细记录了 v1.0 → v1.1.0 的变更
2. **技术决策明确**：为什么要移除 Playwright
3. **最佳实践提炼**：批量处理、三维过滤、重试机制

**知识沉淀**：
- 关键技术决策（移除 vs 替换）
- 跨平台路径处理规范
- 错误处理分类（可重试 vs 不可重试）
- Git 提交规范（Conventional Commits）

---

### 💡 复盘技巧

#### 1. 结构化思考

创建复盘文档时，按照以下逻辑组织：

```
What (发生了什么)
  ↓
Why (为什么这样)
  ↓
How (怎么做的)
  ↓
Result (结果如何)
  ↓
Lesson (学到了什么)
```

#### 2. 数据驱动

使用具体数据支撑结论：
- ❌ "下载速度很快"
- ✅ "平均下载速度：3-5 秒/份"
- ❌ "成功率很高"
- ✅ "下载成功率：100% (23/23)"

#### 3. 提炼模式

从具体案例中提炼可复用的模式：
- **渐进式迁移**：先简单后复杂
- **三维过滤**：权威性 → 时效性 → 相关性
- **批量处理**：JSON 数组提高效率

#### 4. 记录决策

不仅要记录"做了什么"，还要记录"为什么这样做"：
```
决策：移除 Playwright 而非替换
原因：对于 report-hunter，纯 HTTP 模式已足够
结果：节省 ~100MB+ 空间，更轻量、更稳定
```

---

### ⚠️ 常见陷阱

#### 陷阱 1: 复盘过于简略

**错误做法**：
```markdown
任务完成了，下载了23份报告。
```

**正确做法**：
```markdown
## 执行概况
- 任务：下载人工智能领域高质量研究报告
- 成果：23 份报告，183 MB
- 成功率：100%

## 执行流程
（详细记录每个阶段）

## 技术亮点
（提炼可复用的模式）
```

#### 陷阱 2: 缺少数据支撑

**错误做法**：
```markdown
下载速度很快，效果很好。
```

**正确做法**：
```markdown
| 指标 | 数值 |
|------|------|
| 下载成功率 | 100% (23/23) |
| 平均速度 | 3-5 秒/份 |
| 总大小 | 183 MB |
```

#### 陷阱 3: 只记录成功，不记录失败

**错误做法**：只记录成功下载的案例

**正确做法**：
- ✅ 记录遇到的问题
- ✅ 分析失败原因
- ✅ 记录解决方案
- ✅ 总结避免方法

---

### 🔮 进阶技巧

#### 1. 知识图谱化

将多个复盘关联起来，形成知识网络：

```
技能迁移（Playwright → agent-browser）
    ↓
report-hunter 优化（纯 HTTP 模式）
    ↓
研报下载（23 份，183 MB）
    ↓
复盘文档（可复用模式沉淀）
```

#### 2. 模式库构建

从多个案例中提炼通用模式：

| 模式名称 | 适用场景 | 核心要点 |
|---------|---------|---------|
| 渐进式迁移 | 技能升级 | 先简单后复杂，逐步验证 |
| 三维过滤 | 搜索策略 | 权威性→时效性→相关性 |
| 批量处理 | 效率优化 | JSON 数组统一处理 |
| 完整复盘 | 知识沉淀 | 执行流程+技术亮点+经验总结 |

#### 3. 持续迭代

每次任务后都进行复盘，形成闭环：

```
执行 → 复盘 → 提炼 → 优化 → 再执行
```

---

### 📊 复盘质量检查清单

完成复盘后，使用以下清单检查质量：

**内容完整性**：
- [ ] 执行概况（任务、时间、成果）
- [ ] 详细流程（分阶段记录）
- [ ] 技术亮点（架构、代码、策略）
- [ ] 问题解决（遇到的问题、原因、方案）
- [ ] 经验总结（成功要素、改进空间）
- [ ] 知识沉淀（决策、实践、模式）

**数据支撑**：
- [ ] 具体数据（数量、大小、耗时）
- [ ] 成功率统计
- [ ] 对比分析（前后对比）

**可读性**：
- [ ] 结构清晰（使用标题、表格）
- [ ] 代码示例（关键代码片段）
- [ ] 图表展示（数据可视化）

**可复用性**：
- [ ] 提炼模式（从案例到模式）
- [ ] 记录决策（Why + How）
- [ ] 附带资源（参考资料、链接）

---

### 💡 使用建议

1. **每次复杂任务后都复盘**
   - 多步骤任务（3+ 步）
   - 跨 Skill 协作
   - 技术迁移或升级

2. **复盘文档单独保存**
   - 使用有意义的文件名
   - 包含日期和主题
   - 便于后续查阅

3. **定期回顾复盘**
   - 每月回顾一次
   - 提炼共性模式
   - 更新最佳实践

4. **分享给团队**
   - 将复盘经验同步到团队
   - 形成知识库
   - 持续迭代优化