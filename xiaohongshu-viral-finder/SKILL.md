---
name: xiaohongshu-viral-finder
description: >
  小红书低粉爆文抓取与选题分析工具。当用户需要：
  (1) 搜索小红书财经/理财热门内容
  (2) 寻找低粉高赞的爆款笔记（粉丝少但点赞高）
  (3) 生成选题分析报告或 Excel 表格
  (4) 挖掘财经博主的选题灵感
  触发关键词："小红书选题"、"爆文分析"、"财经爆款"、"低粉爆文"、"选题挖掘"
license: MIT
---

# 小红书低粉爆文抓取工具

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

这是一个为"秒懂金融"账号设计的小红书选题挖掘工具。通过 xiaohongshu-mcp 自动搜索热门财经关键词，智能筛选"低粉爆文"（粉丝少但点赞高的隐形爆款），生成 Excel 分析报告并推送到微信。

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
| 博主粉丝数 | < 20,000 |
| 笔记点赞数 | > 1,000 |

### 默认行为

| 场景 | 默认处理 |
|------|---------|
| 未指定关键词 | 使用上述默认列表 |
| 未指定模式 | 使用"财经猎手Pro"模式 |
| 未配置 PushPlus Token | 跳过微信推送，仅生成 Excel |
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

对于每个关键词，使用 xiaohongshu-mcp 工具执行搜索。

---

## ⚠️ CRITICAL: Subagent Architecture for Data Fetching

### 问题根源

MCP 返回的用户主页数据极大（每个 ~13k tokens），直接在主 Agent 上下文中调用会导致：
- 4 个用户 = 52k tokens → 上下文爆满
- 19 个用户 = 247k tokens → 完全不可行

### 🏗️ 解决方案：Subagent 隔离架构

**核心思想**：将 MCP 数据抓取任务交给独立的 Subagent 或 Python 脚本执行，只返回精简后的结果到主 Agent。

```
┌─────────────────────────────────────────────────────────┐
│                     主 Agent                             │
│  - 解析用户指令                                          │
│  - 协调工作流                                            │
│  - 接收精简数据（每用户仅 ~50 tokens）                   │
│  - 生成报告                                              │
└────────────────────────┬────────────────────────────────┘
                         │ 调用
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Subagent / Python 脚本                      │
│  - 独立上下文执行 MCP 调用                               │
│  - 提取必要字段：粉丝数、昵称                           │
│  - 丢弃完整响应                                          │
│  - 返回精简 JSON                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 实现方式：Python 脚本封装 MCP 调用

### Step 2.1: 搜索阶段（主 Agent 执行）

使用 MCP 搜索笔记，收集候选列表：

```python
# 主 Agent 执行：搜索并收集候选
candidates = []
for keyword in keywords:
    results = mcp_search_feeds(keyword, filters={"publish_time": "一周内"})
    for note in results["feeds"]:
        if note["likes"] > 1000:  # 点赞初筛
            candidates.append({
                "note_id": note["id"],
                "title": note["title"],
                "likes": note["likes"],
                "user_id": note["user"]["user_id"],
                "xsec_token": note["xsec_token"]
            })

# 保存到临时文件
save_to_json("/tmp/xhs_candidates.json", candidates)
```

### Step 2.2: 粉丝数抓取（Python 脚本独立执行）

**创建并执行以下 Python 脚本**，该脚本通过 HTTP 直接调用 MCP 服务：

```python
#!/usr/bin/env python3
"""
独立脚本：批量获取用户粉丝数
运行方式：python3 fetch_followers.py
"""
import json
import requests

MCP_URL = "http://localhost:18060/mcp"

def get_user_followers(user_id, xsec_token):
    """调用 MCP 获取用户粉丝数，只返回需要的字段"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "user_profile",
            "arguments": {
                "user_id": user_id,
                "xsec_token": xsec_token
            }
        }
    }
    try:
        resp = requests.post(MCP_URL, json=payload, timeout=30)
        data = resp.json()
        # 只提取需要的字段！
        user_info = data.get("result", {}).get("userBasicInfo", {})
        return {
            "user_id": user_id,
            "followers": user_info.get("fans", 0),
            "nickname": user_info.get("nickname", "")
        }
    except Exception as e:
        return {"user_id": user_id, "followers": -1, "error": str(e)}

def main():
    # 读取候选数据
    with open("/tmp/xhs_candidates.json", "r") as f:
        candidates = json.load(f)
    
    # 去重用户 ID
    unique_users = {}
    for c in candidates:
        uid = c["user_id"]
        if uid not in unique_users:
            unique_users[uid] = c["xsec_token"]
    
    # 批量获取粉丝数
    followers_map = {}
    for uid, token in unique_users.items():
        result = get_user_followers(uid, token)
        followers_map[uid] = result["followers"]
        print(f"[OK] {result.get('nickname', uid)}: {result['followers']} 粉丝")
    
    # 保存结果（精简数据！）
    with open("/tmp/xhs_followers.json", "w") as f:
        json.dump(followers_map, f, ensure_ascii=False)
    
    print(f"\n✅ 完成！获取了 {len(followers_map)} 个用户的粉丝数")

if __name__ == "__main__":
    main()
```

### Step 2.3: 合并数据并筛选（主 Agent 执行）

```python
# 读取粉丝数据（精简！每用户仅一个数字）
with open("/tmp/xhs_followers.json", "r") as f:
    followers_map = json.load(f)

# 读取候选笔记
with open("/tmp/xhs_candidates.json", "r") as f:
    candidates = json.load(f)

# 筛选低粉爆文
viral_notes = []
for note in candidates:
    followers = followers_map.get(note["user_id"], 999999)
    if followers < 20000 and note["likes"] > 1000:
        note["followers"] = followers
        viral_notes.append(note)

# 按爆款指数排序
viral_notes.sort(key=lambda x: x["likes"] / max(x["followers"], 1), reverse=True)
```

---

## 📋 完整执行流程

```
1. [主Agent] 解析指令，确定关键词和模式
2. [主Agent] 调用 MCP 搜索，收集候选笔记
3. [主Agent] 保存候选到 /tmp/xhs_candidates.json
4. [主Agent] 创建 fetch_followers.py 脚本
5. [Bash]    执行 python3 fetch_followers.py
6. [主Agent] 读取 /tmp/xhs_followers.json（精简数据）
7. [主Agent] 合并、筛选、排序
8. [主Agent] 生成 Excel 报告
9. [主Agent] 推送微信（可选）
```

---

## 🚫 Anti-Pattern: 绝对禁止

```python
# ❌ 禁止：在主 Agent 上下文中直接调用 MCP 获取用户信息
for user_id in user_ids:
    profile = mcp__xiaohongshu__user_profile(user_id, token)  # 13k tokens!
    # 这会快速耗尽上下文
```

```python
# ✅ 正确：通过 Python 脚本独立执行
# 1. 创建脚本 fetch_followers.py
# 2. 执行：python3 fetch_followers.py
# 3. 读取精简结果
```

---

### Step 3: 计算爆款指数

```python
# 互动率 = (点赞 + 收藏 + 评论) / 粉丝数 × 100%
interaction_rate = (likes + favorites + comments) / followers * 100

# 爆款指数 = 互动率 × log10(点赞数)
viral_score = interaction_rate * math.log10(likes)
```

### Step 4: 生成 Excel 报告

使用 Python openpyxl 或 xlsxwriter 生成 Excel 文件：

| 列名 | 数据来源 |
|------|---------|
| 笔记标题 | note.title |
| 笔记点赞 | note.likes |
| 博主粉丝数 | author.followers |
| 笔记链接 | note.url |
| 互动率 | 计算值 |
| 爆款指数 | 计算值 |

文件命名格式：`小红书爆文分析_YYYYMMDD_HHMMSS.xlsx`

### Step 5: PushPlus 微信推送（可选）

如果配置了 PushPlus Token，生成简报并推送：

```python
import requests

def push_to_wechat(token, title, content):
    url = "http://www.pushplus.plus/send"
    data = {
        "token": token,
        "title": title,
        "content": content,
        "template": "markdown"
    }
    try:
        response = requests.post(url, json=data)
        return response.json()
    except Exception as e:
        log_error(f"推送失败: {e}")
        return None  # 静默失败，不中断流程
```

#### 推送内容模板

```markdown
# 📊 小红书财经爆文日报

**生成时间**: {timestamp}
**扫描关键词**: {keywords_count} 个
**发现爆文**: {total_notes} 条

## 🔥 TOP 5 爆款笔记

{top_5_notes_table}

## 💡 选题建议

1. 高互动话题: {topic_1}
2. 潜力选题: {topic_2}
3. 热门形式: {topic_3}

---
完整数据已保存至 Excel 文件
```

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

**微信推送**: ✅ 已推送 / ⚠️ 未配置 Token，已跳过

**TOP 3 爆文预览**:
| 标题 | 点赞 | 粉丝 | 爆款指数 |
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
[筛选] 符合低粉爆文条件: 47 条
[生成] Excel 文件已保存
[推送] 已发送至微信

## ✅ 执行完成
- Excel: ~/Documents/小红书爆文分析_20260113.xlsx
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
| `XHS_OUTPUT_DIR` | Excel 输出目录 | 当前工作目录 |

### 自定义阈值

用户可以在指令中指定自定义阈值：

```
搜索小红书爆文，粉丝上限5000，点赞下限500
```

解析后覆盖默认值。

---

## Trigger Examples

以下输入会触发此 Skill：

- "帮我分析小红书财经爆文"
- "小红书选题挖掘"
- "找一些理财领域的低粉爆文"
- "每日热点模式扫描小红书"
- "财经猎手Pro模式深度挖掘"

以下输入**不会**触发此 Skill：

- "小红书怎么注册" → 一般问题
- "帮我写一篇理财文章" → 内容创作
- "分析这篇笔记的数据" → 单篇分析
