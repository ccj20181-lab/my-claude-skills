from typing import List, Dict, Any
import json
from pathlib import Path
from engine.base_template import BaseTemplate

class Template(BaseTemplate):
    def get_meta(self) -> Dict[str, Any]:
        return {
            "name": "whiteboard-hand",
            "description": "Hand-drawn whiteboard animation style",
            "width": 1080,
            "height": 1440
        }

    def get_structure(self, topic: str) -> List[Dict[str, Any]]:
        """
        Generates the 8-step structure for the whiteboard video.
        For this MVP, we generate a mock structure based on the topic.
        In a real implementation, this would call an LLM.
        """
        # Mock data generation based on topic
        return [
            {
                "id": "scene_01_hook",
                "type": "hook",
                "duration_seconds": 4,
                "text": f"你听说过{topic}吗？",
                "image_prompt": f"Hand-drawn whiteboard style, a confused stick figure character thinking about {topic}, question marks floating, simple black line sketch"
            },
            {
                "id": "scene_02_title",
                "type": "title",
                "duration_seconds": 3,
                "title": "秒懂科普",
                "subtitle": f"什么是 {topic}？",
                "image_prompt": f"Hand-drawn whiteboard style, icon representing {topic}, minimalist, simple black lines"
            },
            {
                "id": "scene_03_story",
                "type": "story",
                "duration_seconds": 5,
                "text": "想象一下，你正在处理一个超级复杂的迷宫...",
                "image_prompt": "Hand-drawn whiteboard style, a stick figure standing in front of a huge complex maze, simple sketch"
            },
            {
                "id": "scene_04_problem",
                "type": "problem",
                "duration_seconds": 5,
                "text": "普通电脑走迷宫，只能一条路一条路试，太慢了！",
                "image_prompt": "Hand-drawn whiteboard style, a turtle moving slowly, clock ticking, simple sketch"
            },
            {
                "id": "scene_05_concept",
                "type": "concept",
                "duration_seconds": 5,
                "text": f"{topic}就像是有分身术，能同时走所有路！",
                "image_prompt": f"Hand-drawn whiteboard style, multiple stick figures exploring paths simultaneously, representing {topic}, simple sketch"
            },
            {
                "id": "scene_06_analogy",
                "type": "analogy",
                "duration_seconds": 5,
                "text": "这就是它的神奇之处，速度快到不可思议。",
                "image_prompt": "Hand-drawn whiteboard style, a rocket launching, speed lines, simple sketch"
            },
            {
                "id": "scene_07_summary",
                "type": "summary",
                "duration_seconds": 5,
                "points": ["并行计算", "量子叠加", "极速处理"],
                "image_prompt": "Hand-drawn whiteboard style, a checklist with 3 checkmarks, simple sketch"
            },
            {
                "id": "scene_08_ending",
                "type": "ending",
                "duration_seconds": 3,
                "text": "关注我，每天涨知识！",
                "image_prompt": "Hand-drawn whiteboard style, a happy stick figure waving, 'Subscribe' button, simple sketch"
            }
        ]

    def generate_prompts(self, script: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # In this template, prompts are generated in get_structure for simplicity of the mock.
        # But we ensure they follow the style guide.
        for scene in script:
            if "image_prompt" not in scene:
                 scene["image_prompt"] = f"Hand-drawn whiteboard style, illustrating {scene.get('text', 'concept')}, simple black line sketch"
        return script

    def get_react_files(self) -> Dict[str, str]:
        """
        Returns the React component files.
        We read these from the 'components' directory relative to this script.
        """
        current_dir = Path(__file__).parent
        components_dir = current_dir / "components"

        files = {}

        if components_dir.exists():
            for file_path in components_dir.iterdir():
                if file_path.is_file():
                    filename = file_path.name
                    with open(file_path, "r", encoding="utf-8") as f:
                        files[filename] = f.read()

        return files
