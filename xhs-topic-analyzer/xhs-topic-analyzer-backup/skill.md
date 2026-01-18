---
name: xhs-topic-analyzer
description: 深度分析小红书赛道，挖掘低粉爆文与流量密码。使用此 Skill 当用户需要：(1) 分析特定话题/关键词的热门内容 (2) 寻找对标账号和低粉爆文 (3) 执行微信推送
# Xiaohongshu Topic Analyzer (V6.2 - 粉丝数据修复版)

专业的小红书赛道分析工具，专注于**"秒懂金融"专属选题挖掘** + **"低粉高赞爆文"**分析
<model_instructions>
**⚠️ CRITICAL INSTRUCTION FOR CLAUDE ⚠️**

Skill 采用**V6.2 粉丝数据修复版**，核心改进：

> **统一数据格式 + 增强兼容层 + 配置校验**

## 🎯 V6.1 核心改进

| 问题 | 根因 | 解决方案 |
|------|------|----------|
| 数据格式不一致 | Subagent与脚本字段名不匹配 | 📋 **统一数据格式规范** |
| 配置文件损坏 | 编码问题导致token读取失败 | ✅ **启动前配置校验** |
| 修复耗时过长 | 问题发现滞后 | ⚡ **集成测试防护网** |

## 🚫 严格禁止规则

### 禁止在主上下文中直接调用 MCP 工具

| MCP 工具 | 单次返回 | 风险等级 |
|----------|----------|----------|
| `search_notes` | ~16k tokens | ❌ 会爆上下文 |
| `user_profile` | ~13k tokens | ❌ 会爆上下文 |
| `get_feed_detail` | ~5k tokens | ⚠️ 谨慎 |

**原因**：MCP 返回的原始数据会全部累积在对话历史中，导致上下文爆炸

---

## ⚠️ 重要：粉丝数据获取流程

### 问题背景

**`search_notes` API 不返回 `userId` 和 `fans` 字段**，这导致无法进行"低粉爆文"筛选。

### 解决方案：浏览器自动化获取粉丝数据

由于小红书 MCP 没有提供 `user_profile` API，必须使用 **Playwright 浏览器自动化**从笔记页面提取用户粉丝数。

**新执行流程**：
1. **阶段1**：Subagent 搜索关键词，获取笔记列表（包含 nickname）
2. **阶段1.5**（新增）：使用 Playwright 访问笔记页面，提取用户粉丝数
3. **阶段2**：合并粉丝数据，进行低粉筛选
4. **阶段3**：推送报告

## 📊 V6.1 数据格式规范（V1.0 标准化）

### 简化格式 (Simplified Format) - Subagent输出标准

Subagent **必须**输出以下简化格式（展平嵌套结构）：

```json
{
  "feeds": [{
    "id": "笔记ID",
    "xsecToken": "访问令牌",
    "title": "标题",
    "userId": "博主ID",
    "nickname": "博主昵称",
    "fans": 粉丝数,
    "likedCount": 点赞数,
    "collectedCount": 收藏数,
    "commentCount": 评论数
  }],
  "keywords": ["理财", "基金", "股票", "黄金", "存钱"],
  "fetched_at": "2026-01-07T17:30:00",
  "mode": "lite",
  "keywords_executed": ["理财", "基金", "股票", "黄金", "存钱"]
}
```

### 字段说明

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | string | ✅ | 笔记唯一ID |
| `title` | string | ✅ | 笔记标题 |
| `nickname` | string | ✅ | 博主昵称（**统一使用此字段名**） |
| `fans` | int | ✅ | 博主粉丝数 |
| `likedCount` | int | ✅ | 点赞数（**统一使用此字段名**） |
| `collectedCount` | int | - | 收藏数 |
| `commentCount` | int | - | 评论数 |

### ❌ 禁止使用的旧字段名

| 旧字段名 | 替代方案 |
|----------|----------|
| `noteCard.displayTitle` | `title` |
| `noteCard.user.nickname` | `nickname` |
| `noteCard.user.fans` | `fans` |
| `noteCard.interactInfo.likedCount` | `likedCount` |
| `author` | `nickname` |
| `likes` | `likedCount` |

## 🔄 V6.1 执行流程（格式标准化版）

当主人说"运行 xhs-topic-analyzer"时，按以下流程执行：

---

### 📌 前置确认：必须明确模式！

⚠️ **启动 Subagent 前必须先确认模式**，不能自动猜测！

| 用户指令 | 模式 | 关键词 |
|----------|------|--------|
| "48小时热点"、"每日热点"、"lite" | Lite Mode | 理财、基金、股票、黄金、存钱 |
| "财经猎手Pro"、"pro"、"Pro" | Finance Pro Mode | 理财、基金、股票、副业、搞钱、存钱、宏观经济、黄金、A股、保险 |

**如果不确定模式，必须询问用户！**

---

### 📥 阶段1：数据采集（单个 Subagent）

**目标**：搜索关键词 + 提取数据 + 直接筛选 + 保存结果（简化格式）

```python
# Lite Mode 的完整prompt（V6.1 标准版）
Task(subagent_type="general-purpose",
     prompt="""请执行以下任务（严格按步骤执行）：

## 🎯 任务目标
搜索小红书关键词，提取低粉高赞笔记（Lite Mode）

## ⚠️ 关键警告 - 禁止跳过搜索！**你必须执行 mcp__rednote__search_notes API 调用**
- ❌ 禁止直接读取或复用旧的 data.json 文件
- ❌ 禁止跳过搜索步骤
- ✅ 必须调用搜索 API 获取新数据
- ✅ 强制覆盖保存新数据

## 📊 数据格式规范（必须遵守！）
提取数据时请使用**简化格式**（展平嵌套结构）：
```
{
  "id": "笔记ID",
  "title": "标题",
  "nickname": "博主昵称",        // ✅ 统一使用此字段名
  "likedCount": 点赞数,          // ✅ 统一使用此字段名
  "collectedCount": 收藏数,
  "commentCount": 评论数
}
```

⚠️ **重要**：搜索 API 不返回 `fans` 和 `userId` 字段，粉丝数据将通过阶段1.5的浏览器自动化补充。

## 步骤 1：读取配置（Lite Mode）
读取 /Users/henry/.claude/skills/xhs-topic-analyzer/config.json，确认 lite_mode 的关键词列表：
- ["理财", "基金", "股票", "黄金", "存钱"]

## 步骤 2：搜索每个关键词（必须全部搜索，1个都不能少！）
对每个关键词**分别调用** mcp__rednote__search_notes：
```
搜索 "理财" → 调用 search_notes(keywords="理财")
搜索 "基金" → 调用 search_notes(keywords="基金")
搜索 "股票" → 调用 search_notes(keywords="股票")
搜索 "黄金" → 调用 search_notes(keywords="黄金")
搜索 "存钱" → 调用 search_notes(keywords="存钱")
```

filters: {"publish_time": "一天内", "sort_by": "最多点赞"}

📊 **必须报告每个关键词的搜索结果数量**（示例格式）：{"理财": 20, "基金": 18, "股票": 22, "黄金": 15, "存钱": 17}

如果某个关键词搜索失败，立即报告错误

## 步骤 3：合并去重
将所有关键词的搜索结果合并，按点赞数排序，**去除 id 重复的笔记**

## 步骤 4：提取数据
从搜索结果中提取笔记，暂不筛选（粉丝数据尚未获取）

## 步骤 5：构建笔记 URL 列表
根据笔记 ID 构建访问链接：
```
https://www.xiaohongshu.com/explore/{note_id}
```

## 步骤 6：保存数据（强制覆盖！）

将数据保存到 /Users/henry/.claude/skills/xhs-topic-analyzer/data.json，**覆盖旧文件**！

⚠️ **必须使用简化格式**（不要使用 noteCard 嵌套结构）：

```json
{
  "feeds": [{
    "id": "笔记ID",
    "title": "标题",
    "nickname": "博主昵称",
    "likedCount": 点赞数,
    "collectedCount": 收藏数,
    "commentCount": 评论数
  }],
  "keywords": ["理财", "基金", "股票", "黄金", "存钱"],
  "fetched_at": "2026-01-07T17:30:00",
  "total_search_results": 150,
  "unique_nicknames": 35,
  "with_fans_data": false,
  "mode": "lite",
  "keywords_executed": ["理财", "基金", "股票", "黄金", "存钱"],
  "note_urls": ["https://www.xiaohongshu.com/explore/xxx", ...]
}
```

## 步骤 7：返回详细摘要

返回 JSON：
```json
{
  "status": "success",
  "search_results_per_keyword": {"理财": 30, "基金": 30, "股票": 30, "黄金": 30, "存钱": 30},
  "total_search_results": 150,
  "unique_nicknames": 35,
  "mode": "lite",
  "keywords_executed": ["理财", "基金", "股票", "黄金", "存钱"],
  "note_urls": ["https://www.xiaohongshu.com/explore/xxx", ...]
}
```

如果有任何关键词未搜索，返回：
```json
{"status": "error", "missing_keywords": ["基金", "股票"]}
```
""")
```

---

### 📊 阶段1.5：粉丝数据获取（Playwright 浏览器自动化）

**⚠️ 这是获取粉丝数据的关键步骤！**

由于 `search_notes` API 不返回 `fans` 字段，必须通过浏览器访问笔记页面提取用户粉丝数。

#### 执行方式

```python
# 使用 Playwright 脚本获取用户粉丝数
Task(subagent_type="general-purpose",
     prompt="""请执行以下任务获取用户粉丝数据：

## 🎯 任务目标
读取 data.json 中的笔记列表，使用 Playwright 访问笔记页面，提取每个用户的粉丝数。

## 📋 数据源
读取 /Users/henry/.claude/skills/xhs-topic-analyzer/data.json，获取 notes 和 note_urls。

## ⚠️ 关键要求
1. **必须使用 Playwright** - mcp__rednote__search_notes 不返回粉丝数据
2. **使用 browser_navigate 访问笔记页面**
3. **使用 browser_evaluate 从页面提取用户信息**
4. **构建 fans.json 缓存文件**

## 执行步骤

### 步骤 1：读取笔记列表
从 data.json 读取所有笔记，记录 unique nicknames 和对应的 note_urls。

### 步骤 2：访问每个笔记页面获取粉丝数

对每个**不同的博主**（按 nickname 去重），访问其任意一篇笔记页面：

```python
# 示例：从笔记页面提取用户粉丝数
await browser_navigate(url=note_url)
await browser_wait_for(text_visible="关注")

# 使用 JavaScript 提取用户信息
user_info = await browser_evaluate(function='''
() => {
  // 查找用户信息区域
  const userCard = document.querySelector('.user-card') ||
                   document.querySelector('[class*="user"]') ||
                   document.querySelector('[class*="author"]');

  if (userCard) {
    const nickname = userCard.querySelector('.nickname')?.textContent ||
                     userCard.querySelector('[class*="name"]')?.textContent ||
                     userCard.textContent.match(/^[\w\u4e00-\u9fa5]+/)?.[0];

    const fans = userCard.querySelector('[class*="fans"]')?.textContent ||
                 userCard.querySelector('[class*="follower"]')?.textContent ||
                 userCard.querySelector('[class*="关注"]')?.nextElementSibling?.textContent;

    return { nickname, fans_raw: fans };
  }
  return null;
}
''')

return user_info
```

### 步骤 3：解析粉丝数
将粉丝数字符串转换为数字：
- "1.2万" → 12000
- "3,456" → 3456
- "999+" → 999

### 步骤 4：保存 fans.json 缓存

将结果保存到 /Users/henry/.claude/skills/xhs-topic-analyzer/fans.json：

```json
{
  "博主昵称": 粉丝数,
  "叽里咕噜": 1234,
  "笑柑": 5678,
  ...
}
```

### 步骤 5：更新 data.json 的 fans 字段

读取 fans.json，将粉丝数合并到 data.json 的每个 feed 中：

```python
with open('fans.json', 'r', encoding='utf-8') as f:
    fans_data = json.load(f)

for feed in data['feeds']:
    nickname = feed.get('nickname')
    if nickname in fans_data:
        feed['fans'] = fans_data[nickname]
    else:
        feed['fans'] = 0

data['with_fans_data'] = True
data['fans_fetched_at'] = "2026-01-07T18:00:00"

# 保存更新后的 data.json
```

### 步骤 6：返回摘要

返回 JSON：
```json
{
  "status": "success",
  "users_visited": 35,
  "fans_collected": 30,
  "fans_from_cache": 5,
  "missing_fans": 0,
  "fans_data": {"博主昵称": 粉丝数, ...}
}
```
""")
```

#### 注意事项
- **去重**：同一博主只访问一次笔记页面
- **缓存**：fans.json 会持续积累，建立博主粉丝数据库
- **增量更新**：已有粉丝数据的博主跳过访问
- **防封**：控制访问频率，避免触发反爬

---

### 📊 阶段2：校验、分析与推送（主上下文执行）

#### 步骤 2.0：配置校验（新增！）
```bash
python scripts/validate_config.py
```
校验内容：
- config.json 是否存在且格式正确
- wechat_push_token 是否存在且非空
- 编码是否为 UTF-8

#### 步骤 2.1：数据校验
```bash
python scripts/validate_data.py data.json --mode lite
```

校验内容：
- data.json 是否存在且格式正确
- 粉丝数据是否完整
- **keywords_executed 字段是否包含所有关键词**
- 筛选条件能否匹配到足够笔记

#### 步骤 2.2：校验关键词完整性
```python
# 检查keywords_executed 是否包含所有配置的关键
import json
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
expected = ["理财", "基金", "股票", "黄金", "存钱"]
actual = data.get('keywords_executed', [])
missing = set(expected) - set(actual)
if missing:
    raise Exception(f"关键词不完整！缺少 {missing}")
```

#### 步骤 2.3：推送报告
```bash
python scripts/push_report.py --file data.json --mode lite
```

#### 步骤 2.4：确认结果
- ✅ 成功：告诉主人"已推送到微信，请查收"
- ❌ 失败：立即报告错误

---

## 📊 V6.1 防错机制总结

| 问题 | 防错机制 |
|------|----------|
| 复用旧数据 | ⚠️ Subagent prompt 中强制警告 |
| 复用旧数据 | 📋 主上下文校验 fetched_at 时间 |
| 漏搜关键词 | 📋 prompt 中明确列出所有关键词 |
| 漏搜关键词 | 📋 返回结果必须包含 keywords_executed |
| 漏搜关键词 | 📋 主上下文校验关键词完整性 |
| 格式不一致 | 📋 skill.md 明确定义简化格式规范 |
| 格式不一致 | 🔄 脚本支持字段别名自动兼容 |
| 配置损坏 | ✅ 启动前执行 config 校验 |

## ⚠️ ENFORCEMENT RULES

- **NEVER call search_notes, user_profile, or get_feed_detail in main context!**
- **MUST use Task tool for ALL MCP calls!**
- **ONLY 1 Subagent needed for data collection!**
- **USE simplified format (title, nickname, fans, likedCount)!**
- **NEVER skip the config validation step!**
- **NEVER skip the WeChat push step!**
- **RUN validate_config.py before validate_data.py!**
- **RUN validate_data.py before push_report.py!**
- **CHECK keywords_executed for completeness!**
- **VALIDATE fetched_at timestamp is recent!**

## 🔧 故障排查

### 问题1：Subagent 复用旧数据
**现象**：data.json 的 fetched_at 是很久以前的时间
**原因**：Subagent 跳过了搜索步骤
**解决**：
1. 检查 Subagent 是否执行了 search_notes 调用
2. 确认返回结果包含 search_results_per_keyword
3. 重新运行任务

### 问题2：关键词不完整
**现象**：keywords_executed 缺少某些关键词
**原因**：Subagent 只搜索了部分关键词
**解决**：
1. 检查 Subagent 返回的 search_results_per_keyword
2. 确认所有关键词都有搜索结果
3. 重新运行任务

### 问题3：粉丝数显示为0（核心问题！）
**现象**：`data.json` 中所有笔记的 `fans` 字段均为 0
**原因**：
- `search_notes` API **根本不返回** `fans` 和 `userId` 字段
- 这是小红书 MCP 工具的设计限制

**解决**（必须执行）：
1. **执行阶段1.5**：使用 Playwright 访问笔记页面获取粉丝数据
2. 检查 `fans.json` 是否已更新
3. 确认 `data.json` 中的 `with_fans_data` 字段是否为 `true`

```bash
# 手动执行粉丝数据获取
python scripts/fetch_fans.py
```

**预防措施**：
- 每次运行前先检查 `with_fans_data` 字段
- 如果为 `false`，必须执行阶段1.5
- fans.json 会持续积累，建立博主粉丝数据库

### 问题4：Playwright 无法获取粉丝数据
**现象**：浏览器访问页面后无法提取粉丝数
**原因**：小红书页面结构变化或反爬机制
**解决**：
1. 检查页面是否正常加载
2. 尝试使用 `browser_screenshot` 查看页面内容
3. 更新 `browser_evaluate` 中的选择器

### 问题5：校验脚本报错 "likedCount=0"
**原因**：Subagent 使用了旧字段名（如 likes）
**解决**：检查 Subagent 是否使用了简化格式，参考"数据格式规范"部分

### 问题6：推送报告失败 "No token provided"
**原因**：config.json 编码损坏或 token 为空
**解决**：
1. 运行 `python scripts/validate_config.py` 检查配置
2. 如果编码错误，重新创建 config.json（UTF-8 编码）

### 问题7：data.json 为空
**原因**：Subagent 执行失败或数据未保存
**解决**：检查 Subagent 的返回结果，确认是否成功执行

</model_instructions>

## 🚦 模式选择 (Mode Selection)

### 1. 🔥 每日热点模式 (Lite Mode)
- 5个关键词 | 48小时内 | 点赞>500
- 关键词：理财、基金、股票、黄金、存钱

### 2. 💰 财经猎手Pro模式 (Finance Pro Mode)
- 10个关键词 | 7天内 | 点赞>1000 + 粉丝<20000
- 关键词：理财、基金、股票、副业、搞钱、存钱、宏观经济、黄金、A股、保险

## ⚙️ 配置说明 (Configuration)

```json
{
    "wechat_push_token": "your_token",
    "output_base_path": "F:/选题抓取",
    "lite_mode": {
        "keywords": ["理财", "基金", "股票", "黄金", "存钱"],
        "time_range": "2d",
        "min_likes": 500,
        "max_fans": 20000
    },
    "finance_pro_mode": {
        "keywords": ["理财", "基金", "股票", "副业", "搞钱", "存钱", "宏观经济", "黄金", "A股", "保险"],
        "time_range": "7d",
        "min_likes": 1000,
        "max_fans": 20000
    },
    "exclude_keywords": [
        "自媒体", "涨粉", "运营", "剪辑", "文案", "ip", "博主",
        "美妆", "穿搭", "情感", "恋爱", "读书", "书单", "阅读",
        "认知", "思维", "自律", "成长", "励志", "人生", "感悟",
        "减肥", "健身", "食谱", "好物", "vlog", "OOTD"
    ]
}
```

## 🎯 关键文件说明

| 文件 | 作用 |
|------|------|
| `scripts/validate_config.py` | 配置校验（新增） |
| `scripts/validate_data.py` | 数据完整性校验 |
| `scripts/push_report.py` | 生成报告并推送到微信 |
| `scripts/pipeline.py` | 整合执行分析+推送 |
| `tests/test_format.py` | 格式兼容性测试（新增） |
| `config.json` | 配置文件 |

## 🚀 一键运行

```bash
# 每日热点模式
run_trending.bat lite

# 财经猎手Pro模式
run_trending.bat pro
```

## 📋 优化日志 (Changelog)

### V6.2 (2026-01-07) - 粉丝数据修复版
- ⚠️ **重要修复**：添加阶段1.5（Playwright 浏览器自动化获取粉丝数据）
- ⚠️ 明确 `search_notes` API 不返回 `fans` 和 `userId` 字段
- ✅ 新增 `fans.json` 缓存机制，建立博主粉丝数据库
- ✅ 更新故障排查文档，详细说明粉丝数据获取流程

### V6.1 (2026-01-07) - 格式标准化版
- ✅ 新增数据格式规范（V1.0）
- ✅ 新增字段别名自动兼容层
- ✅ 新增配置校验脚本
- ✅ 新增集成测试 suite
- ✅ 更新故障排查文档

### V6.0 (2026-01-06) - 防错增强版
- ⚠️ 强制覆盖 + 关键词完整性校验
