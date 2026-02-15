#!/usr/bin/env python3
"""
财经视频AI生成器 - 智能脚本生成
使用 Claude API 生成视频脚本，包含口播文案和图片描述
"""
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional
import anthropic

from config import claude_config, video_config


BANNED_OUTRO_PATTERNS = [
    r"下期",
    r"下次",
    r"下节",
    r"下回",
    r"下一期",
    r"后面.*讲",
]
SAFE_OUTRO_TEXT = "系统学习，欢迎阅读我的新书《秒懂金融》。"


# 系统提示词（针对极简简笔画风格优化）
SYSTEM_PROMPT = """你是"财经科普视频"的首席内容策划师，专门创作2分钟的财经科普短视频脚本。

## 输出格式
输出JSON格式的视频脚本，固定总时长120秒（2分钟），包含10-12个场景。

## 场景类型及时长分配（12场景，总计120秒）
严格按照以下时长分配生成每个场景：

| 场景类型 | 时长 | 数量 | 说明 |
|---------|------|------|------|
| hook | 8秒 | 1 | 开场钩子，1句话抓住注意力 |
| title | 4秒 | 1 | 标题展示 |
| concept | 10秒 | 1 | 核心概念引入 |
| detail_1 | 10秒 | 2 | 详细解释 x2 |
| analogy | 10秒 | 1 | 类比说明 |
| example | 10秒 | 2 | 案例 x2 |
| data | 10秒 | 1 | 数据支撑 |
| summary | 8秒 | 1 | 总结 |
| cta | 4秒 | 1 | 结尾引导 |

**总计：12场景，120秒**

## 关键约束
1. **总时长**：严格120秒，每个场景时长严格按照上表分配
2. **信息密度**：口播文案要紧凑，每秒 4-5 个字
3. **干货优先**：删除一切废话、重复、口水话
4. **节奏明快**：场景切换快，不在一个点上纠缠
5. **文案风格**：央视纪录片级别 - 简洁、有力、信息量大

## ⚠️ 文案字数要求（严格执行！）
每个场景的口播文案必须达到以下字数，确保在正常固定语速下接近120秒总时长：

| 场景类型 | 预设时长 | 文案字数要求 |
|---------|---------|------------|
| hook | 8秒 | 52-62字 |
| title | 4秒 | 22-30字 |
| concept | 10秒 | 62-74字 |
| detail_1 | 10秒 | 62-74字 |
| analogy | 10秒 | 62-74字 |
| example | 10秒 | 62-74字 |
| data | 10秒 | 62-74字 |
| summary | 8秒 | 52-62字 |
| cta | 4秒 | 22-30字 |

**总计目标字数：620-760字，确保视频总时长接近120秒**

## 文案质量要求
- 每句文案必须包含实质性信息
- 删除"大家好啊"、"今天我们来聊聊"等废话开头
- 直接切入主题，用问题或数据抓住注意力
- 避免重复表述同一个观点
- 用具体数字和案例支撑观点
- 结尾简洁有力，不拖泥带水

## 结尾限制（必须遵守）
- 禁止出现“下期讲讲…/下期再聊…/下次讲…”等预告式表述
- 结尾 CTA 统一使用当前闭环表述，例如：
  - “系统学习，欢迎阅读我的新书《秒懂金融》。”
  - “想系统提升财商，欢迎阅读《秒懂金融》。”

## image_prompt 字段说明（关键！）
为每个场景生成插画描述，用于AI生成极简手绘简笔画风格的图片：

### 风格要求（AI会自动添加风格约束）：
- 纯白色背景
- 黑色细线条（1-2px）
- 极简手绘简笔画风格
- 简笔人物：圆形头部 + 线条身体
- 用符号表达情绪（问号、感叹号、星星等）
- 手绘随意感，轻微抖动
- 大量留白，居中构图

### 描述示例：
- "一个困惑的简笔人物，头顶有大大的问号，双手摊开"
- "简笔人物站在巨大的硬币旁边，硬币比人还大"
- "两个简笔人物在对话，一个在解释，一个在点头理解"
- "简笔人物看着上升的箭头，表情开心"
- "简笔人物站在天平旁边，天平一边是钱一边是风险"

### 场景内容与插画对应：
- hook: 困惑/好奇的人物 + 问号等符号
- explain: 讲解的人物 + 相关图标
- analogy: 场景化的简笔插画
- example: 数据/案例的可视化
- summary: 总结要点 + 开心的人物

## 输出JSON示例
```json
{
  "topic": "IPO",
  "title": "两分钟看懂IPO上市",
  "totalDuration": 120,
  "scenes": [
    {
      "id": "scene_01",
      "type": "hook",
      "text": "你知道为什么公司都想上市吗？上市到底有什么好处？",
      "duration": 10,
      "visual_action": "circle",
      "image_prompt": "一个简笔人物好奇地看着前方，头顶有大大的问号，旁边有一个公司的简笔画轮廓"
    },
    {
      "id": "scene_02",
      "type": "title",
      "text": "今天带你两分钟看懂IPO",
      "duration": 6,
      "visual_action": "none",
      "image_prompt": "简笔人物举着一块写着IPO的牌子，表情自信"
    },
    {
      "id": "scene_03",
      "type": "explain",
      "text": "IPO就是首次公开募股，公司第一次向公众发行股票，从私人公司变成上市公司。",
      "duration": 20,
      "visual_action": "underline",
      "image_prompt": "简笔人物站在黑板前讲解，黑板上写着IPO三个字母，有箭头指向股票图标"
    }
  ]
}
```

## 注意事项
1. 总时长严格控制在120秒
2. 每个场景的文案要适合口播，语速约每秒3-4个字
3. image_prompt要具体描述画面内容，AI会自动添加风格约束
4. 场景之间要有逻辑连贯性
5. 文案要通俗易懂，避免专业术语，多用类比和生活化表达"""


@dataclass
class Scene:
    """场景数据结构"""
    id: str
    type: str           # hook/title/question/explain/analogy/example/summary/cta
    text: str           # 口播文案
    duration: int       # 秒数
    visual_action: str  # 手绘动画类型
    image_prompt: str   # AI生图描述（必需）

    def to_dict(self):
        return asdict(self)


@dataclass
class Script:
    """视频脚本"""
    topic: str
    title: str
    total_duration: int
    scenes: List[Scene]

    def to_dict(self):
        return {
            "topic": self.topic,
            "title": self.title,
            "totalDuration": self.total_duration,
            "scenes": [s.to_dict() for s in self.scenes]
        }


def sanitize_scene_text(text: str, scene_type: str) -> str:
    """清洗不合规结尾话术"""
    if scene_type not in {"cta", "summary"}:
        return text

    normalized = text.replace(" ", "")
    if any(re.search(pattern, normalized) for pattern in BANNED_OUTRO_PATTERNS):
        return SAFE_OUTRO_TEXT
    return text


def generate_script(topic: str, target_duration: int = 120) -> Script:
    """
    使用 Claude API 生成视频脚本

    Args:
        topic: 视频主题
        target_duration: 目标时长（秒）

    Returns:
        Script: 生成的脚本对象
    """
    if not claude_config.is_configured:
        raise ValueError("Claude API 未配置，请设置 ANTHROPIC_API_KEY")

    # 支持自定义 base_url（如智谱 GLM 兼容 API）
    client_kwargs = {"api_key": claude_config.api_key}
    if claude_config.base_url:
        client_kwargs["base_url"] = claude_config.base_url
        print(f"  📍 使用自定义 API: {claude_config.base_url}")

    client = anthropic.Anthropic(**client_kwargs)

    user_prompt = f"""请为以下财经主题生成2分钟（120秒）的科普视频脚本：

主题：{topic}

## 严格要求
1. **总时长**：严格120秒，每个场景严格按照以下时长分配：
   - hook: 8秒 (1个)
   - title: 4秒 (1个)
   - concept: 10秒 (1个)
   - detail_1: 10秒 (2个)
   - analogy: 10秒 (1个)
   - example: 10秒 (2个)
   - data: 10秒 (1个)
   - summary: 8秒 (1个)
   - cta: 4秒 (1个)
   - **总计：12场景，120秒**

2. **信息密度**：口播文案每秒4-5个字，干货满满

3. **⚠️ 文案字数要求（最重要！）**：
   - 10秒场景 → 文案必须 62-74 字
   - 8秒场景 → 文案必须 52-62 字
   - 4秒场景 → 文案必须 22-30 字
   - **总字数必须达到 620-760 字，才能撑起 120 秒视频！**

4. **节奏明快**：场景切换快，不水文
5. **每个场景都要有 image_prompt**：极简简笔插画描述
6. **禁止出现“下期讲讲”之类预告词**

请直接输出JSON格式的脚本，不要添加任何解释性文字。"""

    print(f"  🤖 正在调用 Claude API 生成脚本...")

    response = client.messages.create(
        model=claude_config.model,
        max_tokens=claude_config.max_tokens,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )

    # 解析响应 - 遍历所有 content blocks 找到文本内容
    content = ""
    for block in response.content:
        if hasattr(block, 'text') and block.text:
            content = block.text
            break
        elif hasattr(block, 'thinking') and block.thinking:
            # 如果只有 thinking 没有 text，记录但不中断
            content = block.thinking

    if not content:
        content = str(response.content[0])

    # 尝试提取 JSON
    json_str = content
    if "```json" in content:
        json_str = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        json_str = content.split("```")[1].split("```")[0].strip()

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"  ⚠️ JSON 解析失败，尝试修复...")
        # 尝试修复常见的 JSON 问题
        json_str = json_str.replace("'", '"')
        json_str = json_str.replace(",]", "]")
        json_str = json_str.replace(",}", "}")
        data = json.loads(json_str)

    # 构建 Script 对象
    scenes = []
    for scene_data in data.get("scenes", []):
        scene = Scene(
            id=scene_data.get("id", f"scene_{len(scenes)+1:02d}"),
            type=scene_data.get("type", "explain"),
            text=sanitize_scene_text(
                scene_data.get("text", ""), scene_data.get("type", "explain")
            ),
            duration=scene_data.get("duration", 15),
            visual_action=scene_data.get("visual_action", "none"),
            image_prompt=scene_data.get("image_prompt", "")
        )
        scenes.append(scene)

    script = Script(
        topic=data.get("topic", topic),
        title=data.get("title", f"两分钟看懂{topic}"),
        total_duration=data.get("totalDuration", 120),
        scenes=scenes
    )

    # 时长验证与修正
    actual_duration = sum(s.duration for s in scenes)

    # 如果时长不足 115 秒（允许小范围偏差），发出警告
    if actual_duration < 115:
        print(f"  ⚠️ 时长不足: 实际{actual_duration}秒，目标{target_duration}秒")

    # 如果时长超出 125 秒，也发出警告
    if actual_duration > 125:
        print(f"  ⚠️ 时长超出: 实际{actual_duration}秒，目标{target_duration}秒")

    # 时长符合要求时显示成功信息
    if 115 <= actual_duration <= 125:
        print(f"  ✓ 时长验证通过: {actual_duration}秒 (目标{target_duration}秒)")

    # 计算信息密度（每秒字数）
    total_words = sum(len(s.text) for s in scenes)
    words_per_second = total_words / actual_duration if actual_duration > 0 else 0
    print(f"  📊 信息密度: 约{words_per_second:.1f}字/秒 (目标4-5字/秒)")

    return script


def rewrite_script_for_target_chars(
    script: Script,
    min_total_chars: int,
    max_total_chars: int,
) -> Script:
    """
    在保持场景结构不变的前提下，仅重写口播文案长度。

    - 保留 scene.id/type/duration/visual_action/image_prompt
    - 仅重写 text
    """
    if not claude_config.is_configured:
        return script

    client_kwargs = {"api_key": claude_config.api_key}
    if claude_config.base_url:
        client_kwargs["base_url"] = claude_config.base_url
    client = anthropic.Anthropic(**client_kwargs)

    scene_structure = [
        {
            "id": s.id,
            "type": s.type,
            "duration": s.duration,
            "visual_action": s.visual_action,
            "image_prompt": s.image_prompt,
            "text": s.text,
        }
        for s in script.scenes
    ]

    prompt = f"""你是财经短视频脚本精修专家。请在不改变场景结构的情况下，仅重写口播文案 text。

硬性要求：
1) 必须保留每个场景的 id/type/duration/visual_action/image_prompt 原值不变
2) 只允许修改 text
3) 全部 text 总字数必须在 {min_total_chars}-{max_total_chars} 之间
4) 禁止出现“下期讲讲/下次讲/下一期”等预告式表述
5) 结尾 CTA 建议使用：系统学习，欢迎阅读我的新书《秒懂金融》。
6) 输出必须是 JSON，结构同输入

输入脚本：
{json.dumps({"topic": script.topic, "title": script.title, "totalDuration": script.total_duration, "scenes": scene_structure}, ensure_ascii=False)}
"""

    response = client.messages.create(
        model=claude_config.model,
        max_tokens=claude_config.max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )

    content = ""
    for block in response.content:
        if hasattr(block, "text") and block.text:
            content = block.text
            break
    if not content:
        return script

    json_str = content
    if "```json" in content:
        json_str = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        json_str = content.split("```")[1].split("```")[0].strip()

    try:
        data = json.loads(json_str)
    except Exception:
        return script

    # 根据原场景 ID 回填固定字段，避免结构漂移
    original_by_id = {s.id: s for s in script.scenes}
    new_scenes: List[Scene] = []
    for raw in data.get("scenes", []):
        scene_id = raw.get("id")
        if scene_id not in original_by_id:
            continue
        base = original_by_id[scene_id]
        new_scenes.append(
            Scene(
                id=base.id,
                type=base.type,
                duration=base.duration,
                visual_action=base.visual_action,
                image_prompt=base.image_prompt,
                text=sanitize_scene_text(raw.get("text", base.text), base.type),
            )
        )

    if len(new_scenes) != len(script.scenes):
        return script

    return Script(
        topic=script.topic,
        title=data.get("title", script.title),
        total_duration=script.total_duration,
        scenes=new_scenes,
    )


def save_script(script: Script, output_path: Path) -> None:
    """保存脚本到 JSON 文件"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(script.to_dict(), f, ensure_ascii=False, indent=2)
    print(f"  ✓ 脚本已保存: {output_path}")


if __name__ == "__main__":
    # 测试脚本生成
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "IPO"

    print(f"测试脚本生成: {topic}")
    script = generate_script(topic)
    print(f"场景数: {len(script.scenes)}")
    print(f"总时长: {script.total_duration}秒")
    for scene in script.scenes:
        print(f"  - {scene.id} [{scene.type}] {scene.duration}秒: {scene.text[:30]}...")
