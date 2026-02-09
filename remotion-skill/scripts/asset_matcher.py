"""
秒懂金融视频生成器 - 素材匹配模块
Asset matching logic for characters and icons
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from config import (
    CHARACTERS, ICONS,
    CHARACTERS_DIR, ICONS_DIR, BACKGROUNDS_DIR, LOGO_PATH,
    get_character_path, get_icon_path
)


@dataclass
class SceneAssets:
    """Assets matched for a single scene"""
    scene_id: str
    character_path: Optional[Path]
    character_type: str
    icon_path: Optional[Path]
    icon_name: Optional[str]
    background_path: Path


def get_background_path() -> Path:
    """Get the whiteboard background path"""
    bg_path = BACKGROUNDS_DIR / "whiteboard.png"
    if bg_path.exists():
        return bg_path
    # Return None if background doesn't exist (will use white fill)
    return None


def match_scene_assets(scene: Dict[str, Any]) -> SceneAssets:
    """
    Match assets for a single scene based on its content

    Args:
        scene: Scene dictionary with 'id', 'character', 'icon' etc.

    Returns:
        SceneAssets object with matched paths
    """
    scene_id = scene.get("id", "unknown")

    # Match character
    character_type = scene.get("character", "neutral")
    character_path = get_character_path(character_type)
    if not character_path.exists():
        character_path = get_character_path("default")

    # Match icon
    icon_name = scene.get("icon")
    icon_path = None
    if icon_name:
        icon_path = get_icon_path(icon_name)
        if icon_path and not icon_path.exists():
            icon_path = None

    # Get background
    background_path = get_background_path()

    return SceneAssets(
        scene_id=scene_id,
        character_path=character_path if character_path.exists() else None,
        character_type=character_type,
        icon_path=icon_path,
        icon_name=icon_name,
        background_path=background_path
    )


def match_all_scenes(scenes: List[Dict[str, Any]]) -> List[SceneAssets]:
    """
    Match assets for all scenes

    Args:
        scenes: List of scene dictionaries

    Returns:
        List of SceneAssets objects
    """
    return [match_scene_assets(scene) for scene in scenes]


def check_assets_availability() -> Dict[str, Any]:
    """
    Check which assets are available in the asset directories

    Returns:
        Dictionary with available assets info
    """
    result = {
        "logo": LOGO_PATH.exists(),
        "logo_path": str(LOGO_PATH) if LOGO_PATH.exists() else None,
        "characters": {},
        "icons": {},
        "backgrounds": []
    }

    # Check characters
    for name, filename in CHARACTERS.items():
        path = CHARACTERS_DIR / filename
        result["characters"][name] = {
            "exists": path.exists(),
            "path": str(path) if path.exists() else None
        }

    # Check icons
    for name, filename in ICONS.items():
        path = ICONS_DIR / filename
        result["icons"][name] = {
            "exists": path.exists(),
            "path": str(path) if path.exists() else None
        }

    # List background files
    if BACKGROUNDS_DIR.exists():
        for f in BACKGROUNDS_DIR.iterdir():
            if f.suffix.lower() in [".png", ".jpg", ".jpeg"]:
                result["backgrounds"].append({
                    "name": f.stem,
                    "path": str(f)
                })

    return result


def create_placeholder_assets(force: bool = False) -> Dict[str, int]:
    """
    Create placeholder assets for missing files

    Args:
        force: If True, overwrite existing files

    Returns:
        Dictionary with counts of created assets
    """
    from PIL import Image, ImageDraw

    created = {"characters": 0, "icons": 0, "backgrounds": 0}

    # Create character placeholders
    for name, filename in CHARACTERS.items():
        path = CHARACTERS_DIR / filename
        if force or not path.exists():
            # Create a simple placeholder image
            img = Image.new("RGBA", (200, 300), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)

            # Draw a simple stick figure
            # Head
            draw.ellipse([70, 20, 130, 80], outline=(50, 50, 50), width=3)
            # Body
            draw.line([100, 80, 100, 180], fill=(50, 50, 50), width=3)
            # Arms
            draw.line([100, 100, 50, 140], fill=(50, 50, 50), width=3)
            draw.line([100, 100, 150, 140], fill=(50, 50, 50), width=3)
            # Legs
            draw.line([100, 180, 60, 280], fill=(50, 50, 50), width=3)
            draw.line([100, 180, 140, 280], fill=(50, 50, 50), width=3)

            # Add expression based on character type
            if name == "happy":
                # Smile
                draw.arc([80, 40, 120, 70], 0, 180, fill=(50, 50, 50), width=2)
            elif name == "confused" or name == "thinking":
                # Question mark above head
                draw.text([95, 5], "?", fill=(50, 50, 50))
            elif name == "surprised":
                # Open mouth
                draw.ellipse([90, 55, 110, 70], outline=(50, 50, 50), width=2)

            img.save(path)
            created["characters"] += 1

    # Create icon placeholders
    for name, filename in ICONS.items():
        path = ICONS_DIR / filename
        if force or not path.exists():
            img = Image.new("RGBA", (100, 100), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)

            # Draw a simple circle with first letter
            draw.ellipse([10, 10, 90, 90], outline=(100, 100, 100), width=2)
            draw.text([40, 35], name[0].upper(), fill=(100, 100, 100))

            img.save(path)
            created["icons"] += 1

    # Create whiteboard background
    bg_path = BACKGROUNDS_DIR / "whiteboard.png"
    if force or not bg_path.exists():
        # Create a subtle whiteboard texture
        img = Image.new("RGB", (1080, 1440), (252, 252, 250))
        draw = ImageDraw.Draw(img)

        # Add subtle grid lines for whiteboard effect
        for x in range(0, 1080, 100):
            draw.line([x, 0, x, 1440], fill=(245, 245, 243), width=1)
        for y in range(0, 1440, 100):
            draw.line([0, y, 1080, y], fill=(245, 245, 243), width=1)

        img.save(bg_path)
        created["backgrounds"] += 1

    return created


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--create-placeholders":
        try:
            result = create_placeholder_assets()
            print(f"Created placeholders: {result}")
        except ImportError:
            print("PIL not available. Install with: pip install Pillow")
    else:
        # Check asset availability
        import json
        result = check_assets_availability()
        print(json.dumps(result, indent=2, ensure_ascii=False))
