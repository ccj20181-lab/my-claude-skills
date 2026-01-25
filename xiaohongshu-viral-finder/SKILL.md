---
name: xiaohongshu-viral-finder
description: >
  小红书热门爆文抓取与选题分析工具。当用户需要：
  (1) 搜索小红书财经/理财热门内容
  (2) 寻找高互动的爆款笔记
  (3) 生成选题分析报告或 Excel 表格
  (4) 挖掘财经博主的选题灵感
  触发关键词："小红书选题"、"爆文分析"、"财经爆款"、"热门爆文"、"选题挖掘"
license: MIT
---

# 小红书热门爆文抓取与选题分析工具

## ⚡️ CRITICAL: Autonomous Execution Protocol

You MUST follow these rules strictly throughout the ENTIRE execution:

1. **DO NOT** ask for confirmation to proceed at any step
2. **DO NOT** ask "是否继续？", "需要更多信息吗？", "要我继续吗？"
3. **DO NOT** pause to summarize progress mid-execution
4. Generate the **FULL output** in ONE execution - from search to Excel generation
5. If data is missing, use the **defined defaults** silently
6. If an error occurs, **log and continue** - NEVER stop to ask the user
7. Complete ALL steps before responding to the user
8. Output the final Excel file path and PushPlus result summary at the END only

---

## Overview

这是一个为"秒懂金融"账号设计的小红书选题挖掘工具。通过 xiaohongshu-mcp 自动搜索热门财经关键词，智能筛选高互动爆款笔记，并深度分析选题规律，生成：
- 📊 **Excel 分析报告**（本地文件）
- 🌐 **GitHub Pages 仪表盘**（在线可视化，带历史记录）
- 📱 **微信推送简报**（PushPlus）

### 🎯 核心功能

1. **自动数据采集**：搜索小红书财经关键词，获取笔记数据
2. **智能筛选**：点赞 > 1,000 的高互动爆文
3. **爆款指数计算**：互动率 × log(点赞数)，量化爆文潜力
4. **选题深度分析**：
   - 7大财经类型自动分类
   - 5种标题策略识别
   - 高频关键词提取
   - 9个模板化选题建议
5. **仪表盘系统**：自动部署到 GitHub Pages，支持历史报告查看
6. **多端通知**：Excel + 微信推送 + 在线仪表盘

### 两种工作模式

| 模式 | 关键词数量 | 时间范围 | 适用场景 |
|------|-----------|---------|---------|
| 每日热点 | 5 个 | 48 小时内 | 快速扫描当日热门 |
| 财经猎手Pro | 9 个全部 | 7 天内 | 深度挖掘优质爆文 |

---

## Defaults & Assumptions

### 默认关键词列表

```
金融, 金融知识, 财经, 财经知识, 理财, 股票, 基金, 存钱, 投资理财
```

### 筛选标准

| 条件 | 阈值 |
|------|------|
| 笔记点赞数 | > 1,000 |

### 默认行为

| 场景 | 默认处理 |
|------|---------|
| 未指定关键词 | 使用上述默认列表 |
| 未指定模式 | 使用"财经猎手Pro"模式 |
| 未配置 PushPlus Token | 跳过微信推送，仅生成 Excel 和仪表盘 |
| 未配置 GitHub Pages 仓库 | 跳过仪表盘部署，仅生成 Excel |
| 搜索无结果 | 静默跳过，继续下一个关键词 |

---

## Workflow Execution

### Step 1: 解析用户指令

从用户输入中提取：
- 自定义关键词（如有）
- 工作模式（每日热点 / 财经猎手Pro）
- 自定义筛选条件（如有）

如果未指定，使用默认值，**不要询问用户**。

### Step 2: 遍历关键词搜索

对于每个关键词，使用 xiaohongshu-mcp 工具执行搜索：

```python
import sys
sys.path.insert(0, 'scripts')

# 使用 MCP 搜索
results = mcp__xiaohongshu__search_feeds(
    keyword="理财",
    filters={
        "publish_time": "一周内",
        "sort_by": "最多点赞"
    }
)

# 提取笔记数据
candidates = []
for note in results["feeds"]:
    likes = note.get("likes", 0)
    if likes > 1000:  # 筛选高互动笔记
        candidates.append({
            "id": note["id"],
            "title": note["title"],
            "likes": likes,
            "collects": note.get("collects", 0),
            "comments": note.get("comments", 0),
            "xsec_token": note.get("xsec_token", "")
        })
```

### Step 3: 计算爆款指数

```python
import math

# 互动率 = (点赞 + 收藏 + 评论) / 1000
interaction_rate = (likes + collects + comments) / 1000

# 爆款指数 = 互动率 × log10(点赞数)
viral_score = interaction_rate * math.log10(likes)
```

### Step 4: 选题分析增强

使用 `topic_analyzer.py` 对筛选后的爆文进行深度选题分析：

```python
from scripts.topic_analyzer import analyze_feeds_topic

# 对爆文进行选题分析
analysis_result = analyze_feeds_topic(viral_notes)

# 返回结果包含：
# - topic_distribution: 选题类型分布（7大财经类别）
# - top_keywords: 高频关键词 TOP 30
# - strategy_stats: 标题策略统计
# - avg_title_length: 平均标题长度
# - suggestions: 9个模板化选题建议
# - enhanced_feeds: 增强后的笔记数据（含选题分类、标题策略等）
```

**增强的数据字段**：
```python
{
    # 原有字段...
    "title": "女生理财必做的8件事",
    "likes": 3500,
    "collects": 1200,
    "comments": 150,
    "viral_score": 87.5,

    # 新增字段
    "topic": "理财技巧",              # 选题分类（7大财经类型）
    "title_strategy": "清单型+圈层型", # 标题策略
    "pattern_type": "清单型",         # 主导模式
    "title_length": 17,               # 标题长度
    "collect_to_like_ratio": 0.34     # 收藏/点赞比
}
```

### Step 5: 生成 Excel 报告（增强版）

使用 `generate_excel.py` 生成多工作表分析报告：

```python
from scripts.generate_excel import generate_excel_report

output_path = "~/Documents/小红书爆文分析_20260123_183000.xlsx"
generate_excel_report(enhanced_feeds, analysis_result, output_path)
```

**工作表结构**：

| 工作表 | 内容 | 列名示例 |
|--------|------|---------|
| 完整数据 | 所有爆文的详细数据 | 标题、选题分类、标题策略、点赞、收藏、评论、爆款指数、链接 |
| 选题分布 | 7大财经选题类型统计 | 选题类型、笔记数量、占比 |
| 标题策略 | 5种标题模式统计 | 策略类型、笔记数量、占比 |
| 选题建议 | 9个可直接使用的选题建议 | 建议标题、选题类型、目标人群、核心价值、内容要点、参考标题 |

文件命名格式：`小红书爆文分析_YYYYMMDD_HHMMSS.xlsx`

### Step 6: GitHub Pages 仪表盘部署（推荐）⭐

抓取完成后，自动生成 HTML 报告并部署到 GitHub Pages：

```python
from scripts.deploy_to_ghpages import deploy_dashboard

# 部署到 GitHub Pages
success, report_filename = deploy_dashboard(
    feeds=enhanced_feeds,           # 增强后的笔记数据
    analysis=analysis_result,       # 选题分析结果
    deploy_dir="/Users/henry/gh-pages-deploy",
    branch="gh-pages"
)

if success:
    print(f"✅ GitHub Pages 已更新: {report_filename}")
    print(f"🌐 访问: https://ccj20181-lab.github.io/xhs-viral-report/")
else:
    print(f"⚠️ 部署失败: {report_filename}")
```

**自动化流程**：
1. 生成 HTML 报告（100% 复用现有模板样式）
2. 更新 `metadata.json`（追加历史记录）
3. 执行 `git add/commit/push`
4. GitHub Pages 网站自动刷新

**输出结构**：
```
gh-pages-deploy/
├── index.html              # 仪表盘主页
├── assets/
│   ├── css/style.css       # 自定义样式
│   └── js/app.js          # 仪表盘逻辑
├── reports/
│   └── report-YYYYMMDD-HHMMSS.html  # 报告内容
└── data/
    └── metadata.json       # 历史报告元数据
```

**访问地址**：`https://ccj20181-lab.github.io/xhs-viral-report/`

### Step 7: PushPlus 微信推送（可选）

使用 `push_wechat.py` 生成增强推送内容：

```python
from scripts.push_wechat import push_to_wechat, generate_push_content

# 生成推送内容
content = generate_push_content(enhanced_feeds, analysis_result)

# 推送到微信
result = push_to_wechat(
    token=PUSHPLUS_TOKEN,
    title="📊 小红书财经爆文分析报告",
    content=content
)
```

#### 推送内容模板（增强版）

```markdown
# 📊 小红书财经爆文分析报告

**生成时间**: {timestamp}
**发现爆文**: {total_notes} 条

## 🔥 TOP 5 爆款笔记

1. **笔记标题**（选题类型）
   - 互动数据: 👍{likes}  ⭐{collects}  💬{comments}
   - 笔记链接: [查看详情](url)

...

## 📈 选题分布统计

- **理财技巧**: 15 篇 (25.0%)
- **基金投资**: 12 篇 (20.0%)
- **存钱省钱**: 10 篇 (16.7%)
...

## 📝 标题策略分析

- **清单型**: 25 篇
- **教程型**: 18 篇
- **时效型**: 12 篇
...

## 💡 精选选题建议

### 1. 🎯 基金止盈实操：3种方法让你不踏空不被套

- **选题类型**: 基金投资
- **目标人群**: 基金投资者
- **核心价值**: 解决基金止盈难题

**内容要点**:
- 分批止盈法（20%规则）
- 目标收益率法
- 估值止盈法
- 实战案例分析

**参考标题**:
- 基金止盈技巧：每赚20%就卖掉四分之一
- 基金公司不会说的加仓法，难怪我总当韭菜！
- 小白买基金必看，打工人闲钱买基，躺赢法

...

## 🔑 高频关键词 TOP 15

理财  基金  投资  存钱  股票  小白  打工人  教程  必看  ...

---
*完整数据已保存至 Excel 文件，请查看附件*
```

---

## 📋 完整执行流程

```
1.  [主Agent] 解析指令，确定关键词和模式
2.  [主Agent] 调用 MCP 搜索，收集候选笔记
3.  [主Agent] 筛选点赞 > 1000 的笔记
4.  [主Agent] 计算爆款指数并排序
5.  [主Agent] 导入 topic_analyzer.py，进行选题分析
6.  [主Agent] 生成增强版 Excel 报告（多工作表）
7.  [主Agent] 自动部署到 GitHub Pages（推荐）⭐
8.  [主Agent] 生成增强版微信推送内容并推送（可选）
```

**脚本说明**：
- `scripts/topic_analyzer.py`: 选题分析引擎，提供分类、策略分析、建议生成
- `scripts/generate_excel.py`: 多工作表 Excel 报告生成器
- `scripts/html_template.py`: HTML 报告模板生成器（复用现有样式）
- `scripts/deploy_to_ghpages.py`: GitHub Pages 自动部署脚本
- `scripts/push_wechat.py`: 增强微信推送，包含选题分布和建议

---

## Error Handling (Log & Continue)

| 错误类型 | 处理方式 | 示例 |
|---------|---------|------|
| 搜索无结果 | 跳过该关键词 | `[INFO] 关键词"投资理财"无结果，跳过` |
| 网络超时 | 重试 3 次后跳过 | `[WARN] 重试 3 次失败，跳过该请求` |
| MCP 调用失败 | 记录错误，继续 | `[ERROR] MCP 调用失败: {error}，继续其他` |
| 笔记详情获取失败 | 跳过该笔记 | `[INFO] 笔记 {id} 详情获取失败，跳过` |
| PushPlus 推送失败 | 记录失败，不阻塞 | `[WARN] 推送失败: {error}，已保存本地` |

**关键原则**：任何单点失败都不应阻塞整体流程。

---

## Output Format

执行完成后，输出以下内容：

```markdown
## ✅ 执行完成

**扫描结果**:
- 关键词数量: X 个
- 搜索笔记总数: X 条
- 符合条件爆文: X 条

**输出文件**:
- Excel: `/path/to/小红书爆文分析_20260113_183000.xlsx`
- 🌐 仪表盘: `https://username.github.io/repo-name/` (如已配置)

**部署状态**:
- GitHub Pages: ✅ 已更新仪表盘 / ⚠️ 未配置仓库，已跳过
- 微信推送: ✅ 已推送 / ⚠️ 未配置 Token，已跳过

**TOP 3 爆文预览**:
| 标题 | 点赞 | 收藏 | 爆款指数 |
|------|------|------|---------|
| ... | ... | ... | ... |
```

---

## Few-Shot Examples

### ✅ Good Case: 一步到位执行

**用户输入**:
> 帮我分析小红书财经爆文

**正确执行**:
```
[执行中] 使用默认关键词列表，财经猎手Pro模式
[搜索] 金融... 找到 18 条笔记
[搜索] 金融知识... 找到 22 条笔记
[搜索] 财经... 找到 15 条笔记
...
[筛选] 符合高互动条件: 47 条
[分析] 选题分析完成
[生成] Excel 文件已保存
[部署] GitHub Pages 仪表盘已更新
[推送] 已发送至微信

## ✅ 执行完成
- Excel: ~/Documents/小红书爆文分析_20260113.xlsx
- 🌐 仪表盘: https://username.github.io/xhs-viral-report/
- 微信推送: ✅ 已发送
```

### ❌ Anti-Pattern: 禁止中途询问

**错误示例 1 - 询问确认**:
```
我找到了 47 条符合条件的笔记。
是否需要我继续生成 Excel 文件？  ← ❌ 禁止！
```

**错误示例 2 - 询问缺失信息**:
```
您没有指定关键词，请告诉我要搜索哪些关键词？  ← ❌ 禁止！
正确做法: 静默使用默认关键词列表
```

**错误示例 3 - 中途报告进度**:
```
已完成 3 个关键词的搜索，还有 6 个待搜索。
要继续吗？  ← ❌ 禁止！
正确做法: 静默执行所有关键词，最后一次性报告结果
```

---

## Configuration

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `PUSHPLUS_TOKEN` | PushPlus 推送 Token | 无（跳过推送） |
| `GITHUB_PAGES_REPO` | GitHub Pages 仓库（格式: username/repo-name） | 无（跳过仪表盘部署） |
| `XHS_OUTPUT_DIR` | Excel 输出目录 | 当前工作目录 |

### GitHub Pages 设置

要启用自动仪表盘部署功能：

1. **创建 GitHub 仓库**（如果还没有）
   ```bash
   gh repo create xhs-viral-report --public
   ```

2. **设置环境变量**
   ```bash
   export GITHUB_PAGES_REPO="your-username/xhs-viral-report"
   ```

3. **首次自动部署**
   - 首次运行会自动创建 gh-pages 分支
   - 自动生成仪表盘框架和静态资源
   - 后续运行会自动更新历史记录

### 自定义阈值

用户可以在指令中指定自定义阈值：

```
搜索小红书爆文，点赞下限500
```

解析后覆盖默认值。

---

## Trigger Examples

以下输入会触发此 Skill：

- "帮我分析小红书财经爆文"
- "小红书选题挖掘"
- "找一些理财领域的热门爆文"
- "每日热点模式扫描小红书"
- "财经猎手Pro模式深度挖掘"

以下输入**不会**触发此 Skill：

- "小红书怎么注册" → 一般问题
- "帮我写一篇理财文章" → 内容创作
- "分析这篇笔记的数据" → 单篇分析
