---
name: xhs-topic-analyzer
description: 小红书爆款选题分析工具。使用此 Skill 当用户需要：(1) 搜索小红书近期爆款笔记 (2) 筛选3天内发布且点赞≥2000的笔记 (3) 生成选题报告并推送到微信。专注金融财经领域，自动化采集爆款内容。
---

# 小红书爆款选题分析器 (V7.0 - 简化版)

专业的小红书爆款笔记挖掘工具，自动搜索近期高赞内容并生成分析报告。

## 🎯 核心功能

搜索小红书金融财经领域的近期爆款笔记（3天内发布，点赞≥2000），自动生成选题报告并推送到微信。

## 📋 执行流程

当主人说"运行 xhs-topic-analyzer"时，按以下流程执行：

### 阶段1：数据采集（Subagent）

启动 Subagent 搜索关键词并提取数据：

```python
Task(subagent_type="general-purpose",
     prompt="""请执行以下任务：

## 🎯 任务目标
搜索小红书关键词，提取近期爆款笔记

## ⚠️ 关键要求
- 必须调用 mcp__xiaohongshu__search_feeds API
- 禁止跳过搜索步骤或复用旧数据
- 强制覆盖保存新数据
- 需要先登录小红书账号（使用 mcp__xiaohongshu__get_login_qrcode）

## 步骤 1：读取配置
读取 /Users/henry/.claude/skills/xhs-topic-analyzer/config.json，获取：
- keywords: 10个搜索关键词
- filters.publish_time: "3d"
- filters.min_likes: 2000

## 步骤 2：搜索每个关键词
对每个关键词分别调用 mcp__xiaohongshu__search_feeds(keyword="<关键词>", filters={...})
参数：
- keyword: 搜索关键词
- filters.sort_by: "最多点赞"（按点赞数排序）
- filters.publish_time: "一周内"（获取最新数据）
- filters.note_type: "不限"

报告每个关键词的搜索结果数量

## 步骤 3：合并去重
合并所有搜索结果，按点赞数排序，去除重复笔记

## 步骤 4：筛选爆款
严格筛选：
- 发布时间：3天内
- 点赞数：≥2000

## 步骤 5：保存数据
保存到 /Users/henry/.claude/skills/xhs-topic-analyzer/data.json

格式：
```json
{
  "feeds": [{
    "id": "笔记ID",
    "title": "标题",
    "nickname": "博主昵称",
    "likedCount": 点赞数,
    "collectedCount": 收藏数,
    "commentCount": 评论数,
    "publishTime": "发布时间"
  }],
  "keywords": [...],
  "fetched_at": "时间戳",
  "mode": "trending",
  "keywords_executed": [...]
}
```

## 步骤 6：返回摘要
返回搜索结果统计和筛选后的笔记数量
""")
```

### 阶段2：校验与推送

**步骤 2.1：配置校验**
```bash
python3 /Users/henry/.claude/skills/xhs-topic-analyzer/scripts/validate_config.py
```

**步骤 2.2：数据校验**
```bash
python3 /Users/henry/.claude/skills/xhs-topic-analyzer/scripts/validate_data.py
```

**步骤 2.3：推送报告**
```bash
python3 /Users/henry/.claude/skills/xhs-topic-analyzer/scripts/push_report.py
```

## ⚙️ 配置说明

配置文件路径：`/Users/henry/.claude/skills/xhs-topic-analyzer/config.json`

```json
{
    "wechat_push_token": "your_token",
    "output_base_path": "/path/to/output",
    "keywords": [
        "金融", "金融知识", "财经", "财经热点",
        "理财", "理财知识", "基金", "股票",
        "存钱", "投资理财"
    ],
    "filters": {
        "publish_time": "3d",
        "min_likes": 2000
    },
    "exclude_keywords": [...]
}
```

## 🔧 关键脚本说明

| 脚本 | 功能 |
|------|------|
| `validate_config.py` | 配置文件校验 |
| `validate_data.py` | 数据完整性校验 |
| `push_report.py` | 生成报告并推送到微信 |
| `pipeline.py` | 整合执行流程 |

## ⚠️ 重要限制

1. **使用 xiaohongshu-mcp 服务** - 必须使用 mcp__xiaohongshu__search_feeds
2. **禁止在主上下文直接调用 MCP 工具** - 使用 Task 工具调用 Subagent
3. **强制覆盖旧数据** - 每次运行必须获取最新数据
4. **严格筛选条件** - 3天内 + 2000赞以上

## 📊 数据格式规范

使用简化格式（展平嵌套结构）：

```json
{
  "id": "笔记ID",
  "title": "标题",
  "nickname": "博主昵称",
  "likedCount": 点赞数,
  "collectedCount": 收藏数,
  "commentCount": 评论数,
  "publishTime": "发布时间"
}
```

## 🔧 故障排查

### 问题1：搜索结果为空
**检查**：config.json 中的关键词是否正确
**解决**：调整关键词或降低筛选标准

### 问题2：推送失败
**检查**：wechat_push_token 是否有效
**解决**：运行 validate_config.py 检查配置

### 问题3：数据格式错误
**检查**：data.json 是否使用简化格式
**解决**：参考"数据格式规范"部分修正

## 📝 版本历史

### V7.0 (2026-01-18) - 重大重构
- ✅ 移除粉丝数据获取（不再需要）
- ✅ 移除模式区分（统一为爆款模式）
- ✅ 简化工作流程
- ✅ 更新关键词：10个金融财经关键词
- ✅ 严格筛选：3天内 + 2000赞以上
