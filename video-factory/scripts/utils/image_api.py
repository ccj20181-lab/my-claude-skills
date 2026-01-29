import sys
import os
import base64
import time
from pathlib import Path
from typing import Optional, Tuple
import requests
from dotenv import load_dotenv

# Default constants
DEFAULT_ASPECT_RATIO = "3:4"
DEFAULT_RESOLUTION = "4K"

def load_env_config() -> None:
    """
    Load environment variables from various locations.
    Priority:
    1. Current skill directory (.env)
    2. apiyi-image-generator skill (.env)
    3. finance-infographic skill (.env)
    """
    # 1. Current skill (.env in video-factory root)
    # script_dir is .../video-factory/scripts/utils
    skill_root = Path(__file__).resolve().parent.parent.parent
    env_file = skill_root / ".env"

    if env_file.exists():
        load_dotenv(env_file)
        return

    # 2. apiyi-image-generator
    apiyi_env = Path.home() / ".claude" / "skills" / "apiyi-image-generator" / ".env"
    if apiyi_env.exists():
        load_dotenv(apiyi_env)
        return

    # 3. finance-infographic
    finance_env = Path.home() / ".claude" / "skills" / "finance-infographic" / ".env"
    if finance_env.exists():
        load_dotenv(finance_env)

def get_api_config() -> Tuple[str, str]:
    """Get API URL and Key from environment."""
    load_env_config()

    api_key = os.environ.get("NANO_BANANA_API_KEY", "").strip()
    api_url = os.environ.get("NANO_BANANA_API_URL", "").strip()

    if not api_key or not api_url:
        raise ValueError("API Key or URL not found. Please configure .env file.")

    return api_url, api_key

def generate_image_bytes(
    prompt: str,
    aspect_ratio: str = DEFAULT_ASPECT_RATIO,
    resolution: str = DEFAULT_RESOLUTION
) -> Optional[bytes]:
    """
    Generates an image and returns the bytes.
    """
    try:
        api_url, api_key = get_api_config()
    except ValueError as e:
        print(f"❌ API Config Error: {e}")
        return None

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect_ratio,
                "imageSize": resolution
            }
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    print(f"    - Calling API (Resolution: {resolution}, Ratio: {aspect_ratio})...")

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=180)
        response.raise_for_status()
        data = response.json()

        if "candidates" in data:
            for candidate in data["candidates"]:
                content = candidate.get("content", {})
                parts = content.get("parts", [])
                for part in parts:
                    if "inlineData" in part:
                        img_data = part["inlineData"].get("data", "")
                        if img_data:
                            return base64.b64decode(img_data)

        print("    ⚠️  No image data found in response.")
        return None

    except Exception as e:
        print(f"    ❌ Generation failed: {e}")
        return None

def save_image(data: bytes, output_path: Path) -> str:
    """Save image data to file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(data)
    return str(output_path)

def generate_and_save(
    prompt: str,
    output_path: Path,
    aspect_ratio: str = DEFAULT_ASPECT_RATIO,
    resolution: str = DEFAULT_RESOLUTION
) -> Optional[str]:
    """
    Generate and save an image to the specified path.
    """
    image_data = generate_image_bytes(prompt, aspect_ratio, resolution)

    if image_data:
        path = save_image(image_data, output_path)
        return path

    return None
