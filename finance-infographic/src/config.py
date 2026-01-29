import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

from .utils import get_project_root, logger

@dataclass
class APIConfig:
    provider: str = "nanobanana"  # google or nanobanana
    google_key: str = ""
    google_url: str = ""
    nanobanana_key: str = ""
    nanobanana_url: str = ""
    timeout: int = 180

@dataclass
class OutputConfig:
    base_dir: str = "/Users/henry/Desktop/秒懂金融学院/信息图输出"  # 个人专用路径
    resolution: str = "4K"

@dataclass
class Config:
    api: APIConfig = field(default_factory=APIConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    @classmethod
    def load(cls) -> 'Config':
        """
        Load configuration from multiple sources with precedence:
        1. Environment variables (.env)
        2. Project config (./.finance-infographic/config.yaml)
        3. User config (~/.finance-infographic/config.yaml)
        4. Default config (config.yaml.example)
        """
        # Load environment variables
        load_dotenv(get_project_root() / '.env')

        config_data = {}

        # Load from config files in order (later overrides earlier)
        config_files = [
            get_project_root() / 'config.yaml.example',
            Path.home() / '.finance-infographic' / 'config.yaml',
            get_project_root() / '.finance-infographic' / 'config.yaml'
        ]

        for config_file in config_files:
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        file_data = yaml.safe_load(f)
                        if file_data:
                            _deep_update(config_data, file_data)
                            logger.debug(f"Loaded config from {config_file}")
                except Exception as e:
                    logger.warning(f"Failed to load config from {config_file}: {e}")

        # Override with environment variables
        env_map = {
            'GOOGLE_API_KEY': ('api', 'google_key'),
            'GOOGLE_API_URL': ('api', 'google_url'),
            'NANO_BANANA_API_KEY': ('api', 'nanobanana_key'),
            'NANO_BANANA_API_URL': ('api', 'nanobanana_url'),
            'FINANCE_OUTPUT_DIR': ('output', 'base_dir'),
        }

        for env_var, path in env_map.items():
            val = os.environ.get(env_var)
            if val:
                _set_nested(config_data, path, val)

        # Build Config object
        api_data = config_data.get('api', {})
        output_data = config_data.get('output', {})

        return cls(
            api=APIConfig(
                provider=api_data.get('provider', 'nanobanana'),
                google_key=api_data.get('google_key', ''),
                google_url=api_data.get('google_url', ''),
                nanobanana_key=api_data.get('nanobanana_key', ''),
                nanobanana_url=api_data.get('nanobanana_url', ''),
                timeout=api_data.get('timeout', 180)
            ),
            output=OutputConfig(
                base_dir=output_data.get('base_dir', 'output'),
                resolution=output_data.get('resolution', '4K')
            )
        )

    def get_output_path(self) -> Path:
        """Resolve the output directory path."""
        path = Path(self.output.base_dir)
        if not path.is_absolute():
            path = get_project_root() / path
        return path

def _deep_update(base_dict: Dict, update_dict: Dict) -> Dict:
    """Recursively update a dictionary."""
    for key, value in update_dict.items():
        if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
            _deep_update(base_dict[key], value)
        else:
            base_dict[key] = value
    return base_dict

def _set_nested(d: Dict, path: tuple, value: Any):
    """Set value in nested dictionary using path tuple."""
    current = d
    for part in path[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]
    current[path[-1]] = value
