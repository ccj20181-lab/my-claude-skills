# 场景模板库

本文档提供各类场景的内容模板和最佳实践。

## Hook 场景（开场钩子）

### 目的
在前 3 秒抓住观众注意力，引发好奇心。

### 模板

**疑问式**
```
"你知道吗？[令人惊讶的事实]"
"为什么[常见现象]？"
"[数字]% 的人不知道[某个知识点]"
```

**故事式**
```
"上周，我的朋友[简短故事开头]..."
"听说某公司[发生的事]，这意味着什么？"
```

**痛点式**
```
"你是不是也遇到过[常见问题]？"
"每次看到[某个术语]就头疼？"
```

### 示例
```json
{
  "type": "hook",
  "text": "听说某公司上市了，股价涨了3倍！这钱是哪来的？",
  "duration": 10,
  "character": "confused",
  "icon": "stock_up"
}
```

---

## Title 场景（标题展示）

### 目的
清晰展示视频主题，让观众知道将要学到什么。

### 模板
```
"今天我们来聊聊[主题]"
"[主题]到底是什么？"
"3 分钟搞懂[主题]"
```

### 示例
```json
{
  "type": "title",
  "text": "什么是 IPO？",
  "duration": 6,
  "character": "neutral"
}
```

---

## Question 场景（抛出问题）

### 目的
引导观众思考，增加互动感和参与感。

### 模板
```
"你有没有想过，[问题]？"
"很多人问我，[问题]？"
"先来思考一个问题：[问题]"
```

### 示例
```json
{
  "type": "question",
  "text": "公司上市到底能赚多少钱？这些钱又是从哪来的呢？",
  "duration": 12,
  "character": "thinking",
  "icon": "money"
}
```

---

## Explain 场景（核心解释）

### 目的
深入解释核心概念，是视频的主体内容。

### 原则
- 先给定义，再展开说明
- 使用简单词汇，避免专业术语堆砌
- 一个场景解释一个概念

### 模板
```
"[概念]，简单说就是[通俗解释]"
"[概念]的意思是[定义]，比如[简单例子]"
```

### 示例
```json
{
  "type": "explain",
  "text": "IPO 就是首次公开募股，简单说就是公司第一次向公众卖股票",
  "duration": 18,
  "character": "pointing",
  "icon": "stock"
}
```

---

## Analogy 场景（类比说明）

### 目的
用生活化的例子帮助理解抽象概念。

### 原则
- 选择日常生活中常见的事物
- 类比要准确，不能误导
- 说明类比的对应关系

### 模板
```
"这就像[生活场景]，[对应关系]"
"你可以把[概念]想象成[类比物]"
"举个例子，就像你[日常行为]一样"
```

### 示例
```json
{
  "type": "analogy",
  "text": "这就像你开了一家蛋糕店，生意越来越好，想开更多分店但是钱不够，于是你决定让大家入股，大家出钱帮你开店，以后分红",
  "duration": 20,
  "character": "happy",
  "icon": "company"
}
```

---

## Example 场景（案例说明）

### 目的
用具体案例或数据增强说服力。

### 原则
- 使用真实或典型案例
- 数据要准确且有来源
- 案例要与前文呼应

### 模板
```
"比如[公司/案例]，[具体情况]"
"拿[案例]来说，[分析]"
"数据显示，[统计结果]"
```

### 示例
```json
{
  "type": "example",
  "text": "比如阿里巴巴 2014 年在美国上市，一次就融了 250 亿美元，成为当时最大的 IPO",
  "duration": 15,
  "character": "pointing",
  "icon": "chart"
}
```

---

## Comparison 场景（对比分析）

### 目的
通过对比帮助理解差异或权衡利弊。

### 模板
```
"[A] 和 [B] 的区别在于..."
"上市有好处也有坏处：好处是[X]，坏处是[Y]"
"[方式A] 适合[情况A]，[方式B] 适合[情况B]"
```

### 示例
```json
{
  "type": "comparison",
  "text": "上市的好处是能快速融到大量资金，坏处是公司信息要公开，而且要接受监管",
  "duration": 18,
  "character": "pointing"
}
```

---

## Summary 场景（要点总结）

### 目的
回顾重点，加深印象。

### 原则
- 提炼 2-3 个核心要点
- 使用简短有力的句子
- 可以用数字或列表形式

### 模板
```
"总结一下，[主题]就是[核心定义]"
"记住这三点：第一[X]，第二[Y]，第三[Z]"
"简单来说，[一句话总结]"
```

### 示例
```json
{
  "type": "summary",
  "text": "总结一下：IPO 就是公司第一次卖股票给公众，目的是融资扩张，代价是要接受公开监管",
  "duration": 12,
  "character": "happy"
}
```

---

## CTA 场景（行动引导）

### 目的
引导关注、点赞、收藏，建立持续连接。

### 模板
```
"如果觉得有用，记得点赞收藏！"
"关注我，学更多理财知识～"
"下期我们聊[预告主题]，记得关注！"
```

### 示例
```json
{
  "type": "cta",
  "text": "如果觉得有用，记得点赞收藏！关注秒懂金融，下期我们聊基金怎么选～",
  "duration": 8,
  "character": "waving"
}
```

---

## 完整脚本示例

```json
{
  "topic": "IPO",
  "title": "公司上市就是圈钱？揭秘IPO的真相",
  "totalDuration": 150,
  "scenes": [
    {
      "id": "scene_01",
      "type": "hook",
      "text": "听说某公司上市了，股价涨了3倍！这钱是哪来的？",
      "duration": 10,
      "character": "confused",
      "icon": "stock_up"
    },
    {
      "id": "scene_02",
      "type": "title",
      "text": "什么是 IPO？",
      "duration": 6,
      "character": "neutral"
    },
    {
      "id": "scene_03",
      "type": "question",
      "text": "公司上市到底能赚多少钱？这些钱又是从哪来的呢？",
      "duration": 12,
      "character": "thinking",
      "icon": "money"
    },
    {
      "id": "scene_04",
      "type": "explain",
      "text": "IPO 就是首次公开募股，简单说就是公司第一次向公众卖股票",
      "duration": 18,
      "character": "pointing",
      "icon": "stock"
    },
    {
      "id": "scene_05",
      "type": "analogy",
      "text": "这就像你开了一家蛋糕店，生意越来越好想开分店但钱不够，于是让大家入股，出钱帮你开店以后分红",
      "duration": 20,
      "character": "happy",
      "icon": "company"
    },
    {
      "id": "scene_06",
      "type": "explain",
      "text": "公司上市后，普通人就可以买它的股票了，公司拿到钱去扩张，股东未来可以分红或者卖股票赚差价",
      "duration": 22,
      "character": "pointing",
      "icon": "trade"
    },
    {
      "id": "scene_07",
      "type": "example",
      "text": "比如阿里巴巴2014年在美国上市，一次就融了250亿美元，成为当时最大的IPO",
      "duration": 15,
      "character": "surprised",
      "icon": "chart"
    },
    {
      "id": "scene_08",
      "type": "comparison",
      "text": "上市的好处是能快速融到大量资金，坏处是公司信息要公开，而且要接受监管",
      "duration": 18,
      "character": "pointing"
    },
    {
      "id": "scene_09",
      "type": "summary",
      "text": "总结一下：IPO就是公司第一次卖股票给公众，目的是融资扩张，代价是要接受公开监管",
      "duration": 12,
      "character": "happy"
    },
    {
      "id": "scene_10",
      "type": "cta",
      "text": "如果觉得有用，记得点赞收藏！关注秒懂金融，下期我们聊基金怎么选～",
      "duration": 8,
      "character": "waving"
    }
  ]
}
```
