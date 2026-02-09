"""
秒懂金融视频生成器 - 内容生成模块
Content generation module using LLM for script creation
"""

import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import anthropic

from config import SCENE_TYPES, GenerationConfig


@dataclass
class Scene:
    """Single scene in the video script"""
    id: str
    type: str
    text: str
    duration: int
    character: str
    icon: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class VideoScript:
    """Complete video script with all scenes"""
    topic: str
    title: str
    total_duration: int
    scenes: List[Scene]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "title": self.title,
            "totalDuration": self.total_duration,
            "scenes": [asdict(scene) for scene in self.scenes]
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


SYSTEM_PROMPT = """你是"秒懂金融"的首席内容策划师，专门为小红书平台创作财经科普视频脚本。

## 你的创作风格
- 用最通俗易懂的语言解释复杂金融概念
- 善用生活化类比，让金融知识不再枯燥
- 语言亲切自然，像朋友聊天一样
- 内容有深度但不晦涩
- 适当使用疑问句增加互动感

## 输出格式要求
你需要输出一个JSON格式的视频脚本，包含以下场景类型（根据内容灵活组合）：

场景类型说明：
- hook (8-12秒): 开场钩子，用一个有趣的问题或现象抓住注意力
- title (5-8秒): 标题展示，简短引入主题
- question (10-15秒): 抛出核心问题，引发观众思考
- explain (15-25秒): 核心概念深度解释
- analogy (15-20秒): 用生活化的类比帮助理解
- example (15-20秒): 具体案例或数据说明
- comparison (15-20秒): 对比展示，如利弊分析
- summary (10-15秒): 要点回顾总结
- cta (8-10秒): 结尾引导关注点赞

角色情绪选择（用于火柴人形象）：
- thinking: 思考、疑惑
- happy: 开心、理解了
- confused: 困惑、不解
- pointing: 讲解、指示
- waving: 打招呼、告别
- surprised: 惊讶
- neutral: 中性

图标选择（金融相关）：
- 货币类: money, coin, cash, wallet, yuan, dollar
- 市场类: stock, stock_up, stock_down, chart, trend, candlestick
- 机构类: bank, company, government, exchange
- 概念类: risk, profit, loss, growth, dividend
- 动作类: buy, sell, trade, invest
- 文档类: contract, report, certificate

## 输出JSON格式示例
```json
{
  "topic": "主题",
  "title": "视频标题（吸引人的标题）",
  "totalDuration": 150,
  "scenes": [
    {
      "id": "scene_01",
      "type": "hook",
      "text": "场景口播文案",
      "duration": 10,
      "character": "confused",
      "icon": "stock_up",
      "notes": "可选的制作备注"
    }
  ]
}
```

请确保：
1. 总时长控制在目标时长附近（允许±15秒浮动）
2. 每个场景的文案要适合口播，语速约每秒3-4个字
3. 选择与内容匹配的角色情绪和图标
4. 场景之间要有逻辑连贯性
"""


def generate_script(
    topic: str,
    target_duration: int = 150,
    style: str = "detailed",
    model: str = "claude-sonnet-4-20250514"
) -> VideoScript:
    """
    Generate a video script for the given topic

    Args:
        topic: The finance topic to explain
        target_duration: Target video duration in seconds
        style: "compact" for shorter videos, "detailed" for more thorough explanation
        model: Claude model to use

    Returns:
        VideoScript object containing the complete script
    """
    client = anthropic.Anthropic()

    style_guidance = ""
    if style == "compact":
        style_guidance = "请使用精简风格，重点突出，减少案例和类比场景。"
    else:
        style_guidance = "请使用详细风格，包含丰富的案例和类比帮助理解。"

    user_prompt = f"""请为以下金融主题创作一个视频脚本：

主题：{topic}
目标时长：{target_duration}秒（约{target_duration // 60}分{target_duration % 60}秒）
风格要求：{style_guidance}

请直接输出JSON格式的脚本，不要有其他文字说明。"""

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )

    # Extract JSON from response
    response_text = response.content[0].text

    # Try to parse JSON (handle potential markdown code blocks)
    json_text = response_text
    if "```json" in response_text:
        json_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        json_text = response_text.split("```")[1].split("```")[0]

    script_data = json.loads(json_text.strip())

    # Convert to VideoScript object
    scenes = [
        Scene(
            id=s["id"],
            type=s["type"],
            text=s["text"],
            duration=s["duration"],
            character=s.get("character", "neutral"),
            icon=s.get("icon"),
            notes=s.get("notes")
        )
        for s in script_data["scenes"]
    ]

    return VideoScript(
        topic=script_data["topic"],
        title=script_data["title"],
        total_duration=script_data["totalDuration"],
        scenes=scenes
    )


def save_script(script: VideoScript, output_path: str) -> None:
    """Save the script to a JSON file"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(script.to_json())


def load_script(input_path: str) -> VideoScript:
    """Load a script from a JSON file"""
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    scenes = [
        Scene(
            id=s["id"],
            type=s["type"],
            text=s["text"],
            duration=s["duration"],
            character=s.get("character", "neutral"),
            icon=s.get("icon"),
            notes=s.get("notes")
        )
        for s in data["scenes"]
    ]

    return VideoScript(
        topic=data["topic"],
        title=data["title"],
        total_duration=data["totalDuration"],
        scenes=scenes
    )


if __name__ == "__main__":
    # Test script generation
    import sys

    topic = sys.argv[1] if len(sys.argv) > 1 else "IPO"
    print(f"Generating script for topic: {topic}")

    script = generate_script(topic, target_duration=150)
    print(script.to_json())
