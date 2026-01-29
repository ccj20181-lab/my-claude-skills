import time
import json
from pathlib import Path
from typing import List, Dict, Any
from utils.image_api import generate_and_save

class AssetGenerator:
    """
    Handles the generation of assets (images) for the scenes.
    """

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.public_scenes_path = self.project_path / "public" / "scenes"
        self.public_scenes_path.mkdir(parents=True, exist_ok=True)

    def generate_assets(self, scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Iterates through scenes and generates images for those that have prompts.
        Updates the scene objects with the local image paths.
        """
        print(f"\n🎨 Starting Asset Generation for {len(scenes)} scenes...")

        updated_scenes = []

        for i, scene in enumerate(scenes):
            scene_id = scene.get("id", f"scene_{i}")
            prompt = scene.get("image_prompt")

            # Skip if no prompt (e.g. text-only scene, though usually we want backgrounds)
            if not prompt:
                updated_scenes.append(scene)
                continue

            filename = f"{scene_id}.png"
            output_path = self.public_scenes_path / filename
            relative_path = f"scenes/{filename}"

            # Check if exists (cache)
            if output_path.exists():
                print(f"  [{i+1}/{len(scenes)}] Using cached: {filename}")
                scene["image"] = relative_path
                updated_scenes.append(scene)
                continue

            print(f"  [{i+1}/{len(scenes)}] Generating: {scene_id}")
            print(f"     Prompt: {prompt[:60]}...")

            saved_path = generate_and_save(prompt, output_path)

            if saved_path:
                scene["image"] = relative_path
                scene["generated"] = True
            else:
                scene["error"] = "Generation failed"
                scene["image"] = ""

            updated_scenes.append(scene)

            # Rate limiting / Sleep to be nice to the API
            if i < len(scenes) - 1:
                time.sleep(2)

        return updated_scenes

    def save_manifest(self, scenes: List[Dict[str, Any]], meta: Dict[str, Any]):
        """
        Saves the final data structure to src/data.json so the React app can read it.
        This effectively acts as the 'database' for the video.
        """
        data = {
            "meta": meta,
            "scenes": scenes,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        data_path = self.project_path / "src" / "data.json"
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ Data saved to {data_path}")
