#!/usr/bin/env python3
"""
财经视频AI生成器 - 配置管理
"""
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 基础路径
SKILL_DIR = Path(__file__).parent.parent.resolve()
REMOTION_DIR = SKILL_DIR / "remotion"
OUTPUT_BASE_DIR = SKILL_DIR / "output"
OUTPUT_DIR = OUTPUT_BASE_DIR  # 兼容 remotion-skill TTS 模块


@dataclass
@dataclass
class TTSConfig:
    """MiniMax TTS 配置"""
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("MINIMAX_API_KEY"))
    group_id: Optional[str] = field(default_factory=lambda: os.getenv("MINIMAX_GROUP_ID"))
    voice_id: str = field(default_factory=lambda: os.getenv("MINIMAX_VOICE_ID", "female-tianmei"))
    model: str = "speech-02-turbo"
    base_url: str = "https://api.minimax.chat/v1/t2a_v2"
    # 兼容 remotion-skill 的额外属性
    speed: float = 1.0
    pitch: int = 0
    volume: int = 100
    output_format: str = "mp3"
    sample_rate: int = 24000

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.group_id)


@dataclass
class ClaudeConfig:
    """Claude API 配置（脚本生成）
    支持智谱 GLM 兼容 API (通过 ANTHROPIC_BASE_URL)
    """
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    base_url: Optional[str] = field(default_factory=lambda: os.getenv("ANTHROPIC_BASE_URL"))
    model: str = "claude-sonnet-4-20250514"  # 智谱 GLM 会映射到 GLM-4
    max_tokens: int = 4096

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)


@dataclass
class ImageGeneratorConfig:
    """AI图片生成配置"""
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("NANO_BANANA_API_KEY"))
    api_url: str = field(default_factory=lambda: os.getenv(
        "NANO_BANANA_API_URL",
        "https://api.apiyi.com/v1beta/models/gemini-2.0-flash-exp-image-generation:generateContent"
    ))
    timeout: int = 120

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_url)


@dataclass
class VideoConfig:
    """视频配置（固定参数）"""
    duration: int = 120  # 固定2分钟
    fps: int = 30
    width: int = 1080
    height: int = 1440  # 3:4 小红书比例
    min_scenes: int = 10  # 增加场景数量下限，提升节奏
    max_scenes: int = 12  # 增加场景数量上限
    words_per_second: float = 4.5  # 目标语速，每秒 4-5 字


def get_output_dir(topic: str) -> Path:
    """获取输出目录路径"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = topic.replace(" ", "_").replace("/", "-")[:30]
    return OUTPUT_BASE_DIR / f"{safe_topic}_{timestamp}"


def ensure_remotion_dirs():
    """确保Remotion所需目录存在"""
    (REMOTION_DIR / "public" / "images").mkdir(parents=True, exist_ok=True)
    (REMOTION_DIR / "public" / "audio").mkdir(parents=True, exist_ok=True)


# 全局配置实例
tts_config = TTSConfig()
claude_config = ClaudeConfig()
image_config = ImageGeneratorConfig()
video_config = VideoConfig()
