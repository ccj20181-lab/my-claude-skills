import time
import base64
from pathlib import Path
from typing import Optional, List
import json

from .config import Config
from .utils import ensure_dir, logger

class Session:
    def __init__(self, topic: str, config: Config):
        self.topic = topic
        self.config = config
        self.timestamp = time.strftime('%Y%m%d_%H%M%S')
        self.session_dir = self._init_session_dir()

    def _init_session_dir(self) -> Path:
        """Initialize the session directory structure."""
        base_output = self.config.get_output_path()
        date_str = time.strftime('%Y%m%d')

        # Format: output/20260124-topic/
        session_path = base_output / f"{date_str}-{self.topic}"
        ensure_dir(session_path)

        # Create subdirectories for better organization
        ensure_dir(session_path / "images")
        ensure_dir(session_path / "prompts")
        ensure_dir(session_path / "source")

        logger.info(f"Session initialized at: {session_path}")
        return session_path

    def save_source(self, content: str, title: str) -> Path:
        """Save the original source content."""
        file_path = self.session_dir / "source" / f"{title}.md"
        file_path.write_text(content, encoding='utf-8')
        return file_path

    def save_analysis(self, analysis: str, title: str) -> Path:
        """Save the content analysis."""
        file_path = self.session_dir / "source" / f"{title}_analysis.md"
        file_path.write_text(analysis, encoding='utf-8')
        return file_path

    def save_prompt(self, prompt: str, index: int, title: str) -> Path:
        """Save the generated prompt for debugging/archiving."""
        filename = f"{index:03d}_{title}_prompt.txt"
        file_path = self.session_dir / "prompts" / filename
        file_path.write_text(prompt, encoding='utf-8')
        return file_path

    def save_image(self, image_data: bytes, index: int, title: str) -> Path:
        """Save the generated image."""
        filename = f"infographic_{self.timestamp}_{index:03d}_{title}.png"
        file_path = self.session_dir / "images" / filename
        file_path.write_bytes(image_data)
        logger.info(f"Image saved: {file_path}")
        return file_path

    def get_reference_images(self, references_dir: Path) -> List[dict]:
        """Load reference images for the API."""
        images = []
        if not references_dir.exists():
            logger.warning(f"Reference directory not found: {references_dir}")
            return images

        for img_path in references_dir.glob('*.png'):
            try:
                with open(img_path, 'rb') as f:
                    b64 = base64.b64encode(f.read()).decode('utf-8')
                    images.append({'mimeType': 'image/png', 'data': b64})
            except Exception as e:
                logger.error(f"Failed to load reference image {img_path}: {e}")

        return images
