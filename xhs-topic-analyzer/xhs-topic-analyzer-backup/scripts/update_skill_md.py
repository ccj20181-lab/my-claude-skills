# -*- coding: utf-8 -*-
"""更新 SKILL.md 文件"""
import os

skill_md_path = os.path.join(os.path.dirname(__file__), '..', 'SKILL.md')

new_content = '''---
name: xhs-topic-analyzer
description: 深度分析小红书赛道，挖掘低粉爆文与流量密码。使用此 Skill 当用户需要：(1) 分析特定话题/关键词的热门内容 (2) 寻找对标账号和低粉爆文 (3) 执行微信推送。

# Xiaohongshu Topic Analyzer (V3.4 Fix - 完整数据版)

专业的小红书赛道分析工具，专注于**"秒懂金融"专属选题挖掘**和**"低粉爆文"**分析。

<model_instructions>
**⚠️ CRITICAL INSTRUCTION FOR CLAUDE ⚠️**

This skill enforces a **Strict Engineering Pipeline**. Do not rely on LLM improvisation.

**MANDATORY: Every execution MUST end with WeChat push!**

## 🚫 严格禁止规则（违反会导致上下文爆炸）

### ❌ 禁止在主上下文中直接调用任何 MCP 工具

**绝对禁止**在当前对话中直接调用以下 MCP 工具：

| MCP 工具 | 单次返回 | 10次累积 | 风险等级 |
|----------|----------|----------|----------|
| `search_feeds` | ~16k tokens | ~160k tokens | ❌ 会爆炸 |
| `user_profile` | ~13k tokens | ~130k tokens | ❌ 会爆炸 |
| `get_feed_detail` | ~5k tokens | ~50k tokens | ⚠️ 谨慎 |

```python
# ❌ 错误：主上下文中调用
mcp__xiaohongshu-mcp__search_feeds(keyword="理财", ...)
mcp__xiaohongshu-mcp__user_profile(user_id="...", xsec_token="...")
mcp__xiaohongshu-mcp__get_feed_detail(...)
```

**原因**：MCP 返回的原始数据会全部累积在对话历史中，导致上下文爆炸

**惩罚**：违反此规则会导致任务失败

## ✅ 强制执行流程

当主人说"运行 xhs-topic-analyzer"时，必须严格按以下顺序执行：

### 步骤 0: 启动 Subagent 执行所有 MCP 调用（关键步骤）

**⚠️ 这是唯一正确的方式！必须使用 Task 工具！**

所有 MCP 调用必须在 Subagent 中执行，主上下文只接收精简结果：

```bash
# 0.1 启动 Subagent 执行完整数据搜索
Task(subagent_type="general-purpose",
     prompt="""请执行以下任务（严格按步骤执行）：

## 任务目标
搜索小红书财经热点数据，并获取完整笔记信息

## 步骤 1: 读取配置
读取 config.json 获取 finance_pro_mode 的关键词列表

## 步骤 2: 搜索每个关键词
对每个关键词调用 mcp__xiaohongshu-mcp__search_feeds：
- filters: {"publish_time": "一周内", "sort_by": "最多点赞"}

## 步骤 3: 提取 Top 10 用户并获取完整笔记信息
按总点赞数排序，提取 Top 10 用户

对 Top 10 用户的每条笔记，调用 mcp__xiaohongshu-mcp__get_feed_detail 获取：
- 笔记标题 (noteCard.displayTitle)
- 发布时间 (noteCard.time)
- 点赞数 (noteCard.interactInfo.likedCount)
- 收藏数 (noteCard.interactInfo.collectedCount)
- 评论数 (noteCard.interactInfo.commentCount)
- 封面图 (noteCard.cover.url)
- 用户信息 (noteCard.user: userId, nickname, avatar)

## 步骤 4: 保存完整笔记数据（必须！）
将完整笔记数据保存到 raw_search.json

## 步骤 5: 提取 Top 用户
按总点赞数排序，提取 Top 10 用户，保存到 compact_users.json

## 步骤 6: 获取 Top 10 用户的粉丝数据
调用 mcp__xiaohongshu-mcp__user_profile 获取粉丝数，保存到 fans.json

## 步骤 7: 返回结果
直接返回精简摘要：
{"status": "success", "total_feeds": 200, "unique_users": 50, "top_users": 10}""")
```

**原则**：主上下文只看到 Task 完成的消息和精简结果 (~500 tokens)，而不是 ~160k tokens 的原始数据

### 步骤 1: 读取 Subagent 返回的精简数据

```bash
python scripts/create_final_data.py raw_search.json fans.json data.json 10
python scripts/pipeline.py --file data.json --mode finance-pro
```

### 步骤 2: 确认微信推送

- ✅ 成功：告诉主人"已推送到微信，请查收 ✓"
- ❌ 失败：立即报告错误

## 📊 架构对比

| 指标 | ❌ 错误方式 | ✅ 正确方式 |
|------|-------------|------------|
| MCP 调用位置 | 主上下文 | **Subagent** |
| 主上下文累积 | ~160k+ tokens | ~500 tokens |
| 数据完整性 | 不完整 | **完整** |

## 📝 完整数据格式要求

**pipeline.py 和分析报告期望的数据必须包含：**
- 笔记标题 (displayTitle)
- 发布时间 (time)
- 点赞数 (likedCount)
- 博主粉丝数 (fans)

## ⚠️ ENFORCEMENT RULES
- **NEVER call search_feeds, user_profile, or get_feed_detail in main context!**
- **MUST use Task tool for ALL MCP calls!**
- **MUST save complete data (title, time, likes, fans) to files!**
- **NEVER skip the WeChat push step!**
</model_instructions>

## 🚦 模式选择 (Mode Selection)

### 1. 🔥 每日热点模式 (Lite Mode)
- 5个关键词 | 48小时内 | 点赞>500

### 2. 💰 财经猎手Pro模式 (Finance Pro Mode)
- 10个关键词 | 7天内 | 点赞>1000 + 粉丝<20000

## ⚙️ 配置说明 (Configuration)

```json
{
    "wechat_push_token": "your_token",
    "output_base_path": "F:\\选题抓取",
    "finance_pro_mode": {
        "keywords": ["理财", "基金", "股票", "副业", "搞钱", "存钱", "宏观经济", "黄金", "A股", "保险"],
        "time_range": "7d",
        "min_likes": 1000,
        "max_fans": 20000
    }
}
```

## 🎯 关键文件说明

| 文件 | 作用 |
|------|------|
| `scripts/create_final_data.py` | 合并数据，生成 data.json |
| `scripts/pipeline.py` | 执行分析+推送 |
| `scripts/push_wechat.py` | 推送到微信 |

## ⚡ 一键运行

```bash
# 财经猎手Pro模式
run_trending.bat pro
```
'''

with open(skill_md_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print('SKILL.md 已更新！')
print(f'文件路径: {skill_md_path}')
