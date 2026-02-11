"""
秒懂金融视频生成器 - 配置管理
Configuration management for Miaodong Finance Video Generator
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

# Base paths
SKILL_ROOT = Path(__file__).parent.parent
ASSETS_DIR = SKILL_ROOT / "assets"
REMOTION_DIR = SKILL_ROOT / "remotion"
OUTPUT_DIR = SKILL_ROOT / "output"
OUTPUT_BASE = Path.home() / "Desktop" / "秒懂金融学院" / "视频输出"


def get_output_dir(topic: str, base: Optional[Path] = None) -> Path:
    """生成路径: ~/Desktop/秒懂金融学院/视频输出/{主题名}/"""
    safe_topic = "".join(c for c in topic if c not in r'\/:*?"<>|')
    return (base or OUTPUT_BASE) / safe_topic.strip()
REFERENCES_DIR = SKILL_ROOT / "references"


def _load_dotenv(dotenv_path: Path) -> None:
    """
    Load env vars from a local .env file (no dependencies).
    - Only sets variables that are not already present in os.environ.
    - Supports simple KEY=VALUE lines (optionally quoted).
    """
    try:
        if not dotenv_path.exists():
            return
        for raw in dotenv_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'").strip('"')
            if key and key not in os.environ:
                os.environ[key] = value
    except Exception:
        # Best-effort only: env loading should not crash the pipeline.
        return


# Allow configuration without touching shell rc files.
_load_dotenv(SKILL_ROOT / ".env")

# Asset subdirectories
CHARACTERS_DIR = ASSETS_DIR / "characters"
ICONS_DIR = ASSETS_DIR / "icons"
BACKGROUNDS_DIR = ASSETS_DIR / "backgrounds"
LOGO_PATH = ASSETS_DIR / "logo.png"


def build_icon_index() -> dict:
    """Scan assets/icons/ directory and build stem → filename mapping."""
    index = {}
    if ICONS_DIR.exists():
        for f in ICONS_DIR.iterdir():
            if f.is_file() and f.suffix.lower() in (".png", ".jpg", ".jpeg", ".svg", ".webp"):
                # Use stem without extension as key
                stem = f.stem
                # Remove trailing " 1" duplicates (prefer the one without suffix)
                if stem.endswith(" 1") and (ICONS_DIR / f"{stem[:-2]}{f.suffix}").exists():
                    continue
                index[stem] = f.name
    return index


ICON_INDEX = build_icon_index()

# Semantic keyword → icon name mapping for richer asset matching
ICON_KEYWORDS = {
    "期货": ["期货合约", "套利", "风险管理", "K线图", "合同文件"],
    "股票": ["股票投资", "K线图", "上升趋势箭头", "股票证书", "图表分析"],
    "基金": ["基金定投", "公募基金", "私募基金", "投资", "分红派息"],
    "债券": ["债券", "债券证书", "合同文件", "银行建筑", "国债"],
    "利率": ["银行建筑", "人民币符号", "上升趋势箭头", "加息降息", "央行logo"],
    "杠杆": ["火箭上升", "风险管理", "K线图", "止损", "天平秤"],
    "合约": ["合同文件", "期货合约", "签名笔", "印章"],
    "风险": ["风险管理", "盾牌保护", "止损", "天平秤", "保险保障"],
    "投资": ["投资", "股票投资", "资产配置", "投资回报率", "财富图标"],
    "银行": ["银行建筑", "人民币纸币", "信用卡", "ATM机", "银行卡"],
    "通胀": ["通货膨胀", "人民币符号", "购买力", "CPI指数"],
    "央行": ["央行logo", "货币政策", "加息降息", "银行建筑"],
    "IPO": ["IPO上市", "股票证书", "华尔街标志", "上升趋势箭头"],
    "房产": ["房产投资", "房价", "房子建筑", "贷款"],
    "黄金": ["黄金金条", "白银", "钻石宝石", "保险箱"],
    "外汇": ["汇率", "外汇储备", "美元符号", "英镑符号", "日元符号"],
    "区块链": ["区块链", "比特币符号", "以太坊符号", "数字货币"],
    "退休": ["退休规划", "储蓄", "时间价值", "复利"],
    "税务": ["税务", "财务报表", "计算器", "关税"],
    "保险": ["保险保障", "盾牌保护", "保险箱", "合同文件"],
    "理财": ["资产配置", "财商教育", "预算管理", "收入来源"],
    "农民": ["购物车", "钱包", "供需关系"],
    "工厂": ["工厂", "齿轮机械", "供需关系"],
    "科技": ["笔记本电脑", "服务器", "数据库", "网络连接"],
    "贸易": ["关税", "世界地图", "握手合作", "包裹快递"],
    "消费": ["购物车", "信用卡", "消费升级", "手机支付"],
    "储蓄": ["储蓄", "钱包", "保险箱", "金币堆"],
    "债务": ["债务", "贷款", "破产", "赤字"],
    "收益": ["盈余", "上升趋势箭头", "投资回报率", "分红派息"],
    "亏损": ["赤字", "下降趋势箭头", "破产", "熊市"],
    "牛市": ["上升趋势箭头", "火箭上升", "股票投资"],
    "熊市": ["熊市", "下降趋势箭头", "止损"],
    "周期": ["周期波浪图", "周期理论", "时钟", "沙漏"],
}


@dataclass
class VideoConfig:
    """Video output configuration"""
    width: int = 1080
    height: int = 1440  # 3:4 aspect ratio for Xiaohongshu
    fps: int = 30
    format: str = "mp4"
    codec: str = "h264"


@dataclass
class TTSConfig:
    """MiniMax TTS configuration"""
    api_key: str = field(default_factory=lambda: os.environ.get(
        "MINIMAX_API_KEY",
        ""
    ))
    group_id: str = field(default_factory=lambda: os.environ.get("MINIMAX_GROUP_ID", ""))
    model: str = "speech-02-hd"
    voice_id: str = field(default_factory=lambda: os.environ.get("MINIMAX_VOICE_ID", "miaodong-custom-voice"))  # 秒懂金融克隆音色
    speed: float = 1.0
    pitch: int = 0
    volume: int = 100
    output_format: str = "mp3"
    sample_rate: int = 24000


@dataclass
class SceneType:
    """Scene type definitions with timing recommendations"""
    name: str
    description: str
    min_duration: int  # seconds
    max_duration: int  # seconds
    default_duration: int  # seconds


# Scene type catalog
SCENE_TYPES = {
    "hook": SceneType(
        name="hook",
        description="开场钩子，抓住注意力",
        min_duration=8,
        max_duration=12,
        default_duration=10
    ),
    "title": SceneType(
        name="title",
        description="标题展示 + 主题引入",
        min_duration=5,
        max_duration=8,
        default_duration=6
    ),
    "question": SceneType(
        name="question",
        description="抛出核心问题，引发思考",
        min_duration=10,
        max_duration=15,
        default_duration=12
    ),
    "explain": SceneType(
        name="explain",
        description="概念深度解释",
        min_duration=15,
        max_duration=25,
        default_duration=20
    ),
    "analogy": SceneType(
        name="analogy",
        description="生活化类比，帮助理解",
        min_duration=15,
        max_duration=20,
        default_duration=18
    ),
    "example": SceneType(
        name="example",
        description="具体案例/数据说明",
        min_duration=15,
        max_duration=20,
        default_duration=18
    ),
    "comparison": SceneType(
        name="comparison",
        description="对比展示（如利弊对比）",
        min_duration=15,
        max_duration=20,
        default_duration=18
    ),
    "summary": SceneType(
        name="summary",
        description="要点回顾总结",
        min_duration=10,
        max_duration=15,
        default_duration=12
    ),
    "cta": SceneType(
        name="cta",
        description="结尾引导（关注/点赞）",
        min_duration=8,
        max_duration=10,
        default_duration=8
    ),
}


# Character emotion mappings
CHARACTERS = {
    "thinking": "thinking.png",
    "happy": "happy.png",
    "confused": "confused.png",
    "pointing": "pointing.png",
    "waving": "waving.png",
    "surprised": "surprised.png",
    "neutral": "neutral.png",
    "default": "neutral.png",
}

# Icon category mappings - 映射到实际的白板手绘风格素材文件
ICONS = {
    # Currency & Money
    "money": "金币堆_白板手绘.png",
    "coin": "金币堆_白板手绘.png",
    "cash": "人民币纸币_白板手绘.png",
    "wallet": "钱包_白板手绘.png",
    "yuan": "人民币符号_白板手绘.png",
    "dollar": "美元符号_白板手绘.png",

    # Markets
    "stock": "股票投资_白板手绘.png",
    "stock_up": "上升趋势箭头_白板手绘.png",
    "stock_down": "下降趋势箭头_白板手绘.png",
    "chart": "K线图_白板手绘.png",
    "trend": "股票投资_白板手绘.png",
    "candlestick": "K线图_白板手绘.png",

    # Institutions
    "bank": "银行建筑_白板手绘.png",
    "company": "办公楼_白板手绘.png",
    "government": "财政政策_白板手绘.png",
    "exchange": "纽交所_白板手绘.png",

    # Concepts
    "risk": "风险管理_白板手绘.png",
    "profit": "盈余_白板手绘.png",
    "loss": "赤字_白板手绘.png",
    "growth": "火箭上升_白板手绘.png",
    "dividend": "分红派息_白板手绘.png",

    # Actions
    "buy": "购物车_白板手绘.png",
    "sell": "股票证书_白板手绘.png",
    "trade": "套利_白板手绘.png",
    "invest": "投资.png",

    # Documents
    "contract": "合同文件_白板手绘.png",
    "report": "财务报表_白板手绘.png",
    "certificate": "证书文凭_白板手绘.png",

    # IPO Related
    "ipo": "IPO上市_白板手绘.png",
    "listing": "IPO上市_白板手绘.png",
    "public": "IPO上市_白板手绘.png",
}


@dataclass
class GenerationConfig:
    """Overall generation configuration"""
    topic: str
    target_duration: int = 150  # 2.5 minutes default
    style: str = "detailed"  # compact | detailed
    video: VideoConfig = field(default_factory=VideoConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    output_dir: Path = field(default_factory=lambda: OUTPUT_DIR)

    def __post_init__(self):
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)


def get_character_path(character_type: str) -> Path:
    """Get the full path for a character image"""
    filename = CHARACTERS.get(character_type, CHARACTERS["default"])
    return CHARACTERS_DIR / filename


def get_icon_path(icon_name: str) -> Optional[Path]:
    """Get the full path for an icon image, with ICON_INDEX fallback."""
    # 1. Try legacy ICONS dict first
    filename = ICONS.get(icon_name)
    if filename:
        p = ICONS_DIR / filename
        if p.exists():
            return p

    # 2. Try ICON_INDEX (stem-based lookup)
    # Direct stem match
    for stem, fname in ICON_INDEX.items():
        if stem == icon_name or icon_name in stem:
            p = ICONS_DIR / fname
            if p.exists():
                return p

    # 3. Try partial match with _白板手绘 suffix
    candidate = f"{icon_name}_白板手绘"
    if candidate in ICON_INDEX:
        return ICONS_DIR / ICON_INDEX[candidate]

    return None


def validate_config(config: GenerationConfig) -> List[str]:
    """Validate configuration and return list of issues"""
    issues = []

    if not config.topic:
        issues.append("Topic is required")

    if config.target_duration < 60:
        issues.append("Target duration should be at least 60 seconds")

    if config.target_duration > 300:
        issues.append("Target duration should not exceed 300 seconds (5 minutes)")

    if not config.tts.api_key:
        issues.append("MINIMAX_API_KEY environment variable not set")

    if not config.tts.group_id:
        issues.append("MINIMAX_GROUP_ID environment variable not set")

    if not LOGO_PATH.exists():
        issues.append(f"Logo file not found at {LOGO_PATH}")

    return issues
