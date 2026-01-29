import json
from pathlib import Path
from typing import List, Dict, Any
from engine.base_template import BaseTemplate

class KnowledgeExplainerTemplate(BaseTemplate):
    """
    Knowledge Explainer Template (Ported from Miaodong Video Creator).
    Focuses on financial concepts and educational content.
    """

    def get_meta(self) -> Dict[str, Any]:
        return {
            "name": "knowledge-explainer",
            "description": "Financial concept explainer with 3:4 aspect ratio",
            "width": 1080,
            "height": 1440,
            "fps": 30,
            "default_duration": 45,
            "composition_id": "KnowledgeExplainer"
        }

    def get_structure(self, topic: str) -> List[Dict[str, Any]]:
        """
        Parses a topic into a structured script.
        For now, this generates a skeleton based on the topic.
        In a real implementation, this would call an LLM to generate the content.
        """
        # Default structure for "Knowledge Explainer"
        # 1. Title
        # 2. Concept Explanation
        # 3. Example
        # 4. Summary
        # 5. Ending

        # Placeholder content generation (Mocking LLM output for now)
        return [
            {
                "id": "scene_01",
                "type": "title",
                "duration_seconds": 5,
                "content": {
                    "main_title": topic,
                    "sub_title": "秒懂金融概念"
                },
                "background": {
                    "prompt": "Modern tech background with financial elements, dark blue theme",
                    "style": "modern"
                }
            },
            {
                "id": "scene_02",
                "type": "content",
                "duration_seconds": 12,
                "content": {
                    "text": f"{topic} is a key financial concept that every investor should know...",
                    "highlight_words": [topic, "Investor", "Concept"]
                },
                "background": {
                    "prompt": f"Illustration representing {topic}, professional and clear",
                    "style": "illustration"
                }
            },
            {
                "id": "scene_03",
                "type": "content",
                "duration_seconds": 15,
                "content": {
                    "text": "For example, imagine you are opening a lemonade stand...",
                    "character": "xiaoming"
                },
                "background": {
                    "prompt": "Cute character illustration, lemonade stand example, warm colors",
                    "style": "illustration"
                }
            },
            {
                "id": "scene_04",
                "type": "summary",
                "duration_seconds": 10,
                "content": {
                    "points": [
                        f"Point 1 about {topic}",
                        "Point 2: Why it matters",
                        "Point 3: How to use it"
                    ]
                },
                "background": {
                    "prompt": "Infographic style background, three distinct sections",
                    "style": "infographic"
                }
            },
            {
                "id": "scene_05",
                "type": "ending",
                "duration_seconds": 3,
                "content": {
                    "text": "Follow Miaodong Finance for more"
                },
                "background": {
                    "prompt": "Gradient background with subscribe button visual",
                    "style": "modern"
                }
            }
        ]

    def generate_prompts(self, script: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enhances the script with full image generation prompts.
        """
        style_enhancements = {
            "modern": "modern tech style, dark blue purple gradient, neon lights, clean lines, 3:4 vertical",
            "illustration": "flat illustration style, bright colors, cute cartoon elements, 3:4 vertical",
            "infographic": "infographic style, data visualization, clean typography, professional, 3:4 vertical"
        }

        for scene in script:
            bg = scene.get("background", {})
            base_prompt = bg.get("prompt", "")
            style = bg.get("style", "modern")

            enhancement = style_enhancements.get(style, style_enhancements["modern"])
            full_prompt = f"{base_prompt}, {enhancement}, high quality, detailed"

            # Store the full prompt for the asset generator to use
            scene["image_prompt"] = full_prompt

        return script

    def get_react_files(self) -> Dict[str, str]:
        """
        Returns the React component content.
        Reads all files from the 'components' directory.
        """
        current_dir = Path(__file__).parent
        components_dir = current_dir / "components"

        files = {}

        if components_dir.exists():
            for file_path in components_dir.iterdir():
                if file_path.is_file():
                    # Use the relative path (e.g., "Composition.tsx", "Root.tsx")
                    filename = file_path.name
                    with open(file_path, "r", encoding="utf-8") as f:
                        files[filename] = f.read()

        return files
