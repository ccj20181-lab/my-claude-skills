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
    visual_action: Optional[str] = None
    icon_keywords: Optional[List[str]] = None
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
      "visual_action": "circle",
      "icon_keywords": ["期货合约", "杠杆", "K线图"],
      "notes": "可选的制作备注"
    }
  ]
}
```

### visual_action 字段说明（手绘动画效果）
根据场景内容的语义选择最匹配的手绘动画：
- circle: 用于强调核心概念、重要数字（如"利率3.5%"）
- underline: 用于强调关键术语、定义（如"什么是IPO"）
- arrow: 用于因果关系、流程说明（如"买入→持有→卖出"）
- checkmark: 用于总结要点、确认事实（如"记住这三点"）
- bracket: 用于补充说明、旁注（如"换句话说..."）
- highlight: 用于数据对比、关键数据（如"涨了200%"）
- none: 不需要手绘效果的场景

### icon_keywords 字段说明
提供2-3个精准的中文关键词，用于匹配白板手绘风格素材图标。
关键词应与场景内容直接相关，例如：
- 讲解股票时：["股票投资", "K线图", "上升趋势箭头"]
- 讲解风险时：["风险管理", "盾牌保护", "止损"]
- 讲解银行时：["银行建筑", "人民币纸币", "信用卡"]

请确保：
1. 总时长控制在目标时长附近（允许±15秒浮动）
2. 每个场景的文案要适合口播，语速约每秒3-4个字
3. 选择与内容匹配的角色情绪和图标
4. 场景之间要有逻辑连贯性
5. 每个场景都要提供 visual_action 和 icon_keywords 字段
"""


def generate_script(
    topic: str,
    target_duration: int = 150,
    style: str = "detailed",
    model: str = "claude-opus-4-6-thinking"
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

    # Build API call parameters
    api_params = {
        "model": model,
        "max_tokens": 16000,
        "messages": [
            {"role": "user", "content": SYSTEM_PROMPT + "\n\n" + user_prompt}
        ],
    }

    # Thinking models require budget_tokens and don't support system parameter
    if "thinking" in model:
        api_params["thinking"] = {
            "type": "enabled",
            "budget_tokens": 10000
        }
    else:
        api_params["system"] = SYSTEM_PROMPT
        api_params["messages"] = [
            {"role": "user", "content": user_prompt}
        ]

    response = client.messages.create(**api_params)

    # Extract text from response (thinking models have multiple content blocks)
    response_text = ""
    for block in response.content:
        if block.type == "text":
            response_text = block.text
            break

    # Try to parse JSON (handle potential markdown code blocks)
    json_text = response_text
    if "```json" in response_text:
        json_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        json_text = response_text.split("```")[1].split("```")[0]

    json_text = json_text.strip()

    # Robust JSON parsing with fallback repair
    import re
    try:
        script_data = json.loads(json_text)
    except json.JSONDecodeError:
        # Try to fix common JSON issues from LLM output
        # Remove trailing commas before } or ]
        fixed = re.sub(r',\s*([}\]])', r'\1', json_text)
        # Remove control characters
        fixed = re.sub(r'[\x00-\x1f\x7f]', ' ', fixed)
        # Fix unescaped quotes inside strings (best effort)
        try:
            script_data = json.loads(fixed)
        except json.JSONDecodeError:
            # Last resort: extract the JSON object with regex
            match = re.search(r'\{[\s\S]*\}', fixed)
            if match:
                script_data = json.loads(match.group())
            else:
                raise ValueError(f"Failed to parse JSON from LLM response:\n{json_text[:500]}")

    # Convert to VideoScript object
    scenes = [
        Scene(
            id=s["id"],
            type=s["type"],
            text=s["text"],
            duration=s["duration"],
            character=s.get("character", "neutral"),
            icon=s.get("icon"),
            visual_action=s.get("visual_action"),
            icon_keywords=s.get("icon_keywords"),
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
            visual_action=s.get("visual_action"),
            icon_keywords=s.get("icon_keywords"),
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
