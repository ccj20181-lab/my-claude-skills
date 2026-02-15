#!/usr/bin/env python3
"""
财经视频AI生成器 - 主入口
一键生成2分钟财经科普短视频
"""
import argparse
import asyncio
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 添加脚本目录到路径
SCRIPTS_DIR = Path(__file__).parent
import sys
sys.path.insert(0, str(SCRIPTS_DIR))

from config import (
    claude_config, image_config, video_config, tts_config,
    REMOTION_DIR, ensure_remotion_dirs
)
from content_generator import (
    Scene,
    Script,
    generate_script,
    rewrite_script_for_target_chars,
    save_script,
)
from image_generator import AIImageGenerator

# 复用 remotion-skill 的 TTS (延迟导入避免冲突)
tts_generate = None

DEFAULT_EXPORT_ROOT = Path("/Users/henry/Desktop/秒懂金融学院/视频输出")
DEFAULT_BOOK_COVER = Path(
    "/Users/henry/Desktop/秒懂金融学院/秒懂金融事项管理/秒懂金融书稿写作/秒懂金融归档/秒懂金融-立体.jpg"
)
DEFAULT_BOOK_OUTRO_TEXT = "系统学习，欢迎阅读我的新书《秒懂金融》。"
DEFAULT_BOOK_OUTRO_SECONDS = 3.0
MAX_BOOK_OUTRO_SECONDS = 3.0


def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("🎥 财经视频AI生成器 - Finance Video AI Generator")
    print("   极简手绘简笔画风格 | 固定2分钟 | 小红书3:4比例")
    print("=" * 60)


def check_dependencies():
    """检查依赖"""
    print("\n🔍 检查依赖...")

    issues = []

    # 检查 Python 包
    try:
        import anthropic
        print("  ✓ anthropic")
    except ImportError:
        issues.append("anthropic (pip install anthropic)")

    try:
        import aiohttp
        print("  ✓ aiohttp")
    except ImportError:
        issues.append("aiohttp (pip install aiohttp)")

    try:
        import requests
        print("  ✓ requests")
    except ImportError:
        issues.append("requests (pip install requests)")

    try:
        from dotenv import load_dotenv
        print("  ✓ python-dotenv")
    except ImportError:
        issues.append("python-dotenv (pip install python-dotenv)")

    try:
        from PIL import Image
        print("  ✓ Pillow")
    except ImportError:
        issues.append("Pillow (pip install Pillow)")

    if issues:
        print(f"\n⚠️ 缺少依赖包:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n请运行: pip install " + " ".join(issues))
        return False

    return True


def check_api_keys():
    """检查 API 密钥配置"""
    print("\n🔑 检查 API 配置...")

    configs = [
        ("Claude (脚本生成)", claude_config.is_configured),
        ("Gemini (图片生成)", image_config.is_configured),
        ("MiniMax TTS (语音合成)", tts_config.is_configured),
    ]

    all_ok = True
    for name, configured in configs:
        status = "✓" if configured else "✗"
        print(f"  {status} {name}")
        if not configured:
            all_ok = False

    return all_ok


def phase1_generate_script(
    topic: str, output_dir: Optional[Path] = None, save: bool = True
) -> Script:
    """Phase 1: 生成脚本"""
    print(f"\n📝 Phase 1: 智能脚本生成")
    print(f"   主题: {topic}")

    script = generate_script(topic=topic, target_duration=video_config.duration)
    if save and output_dir is not None:
        save_script(script, output_dir / "script.json")

    print(f"   ✓ 场景数: {len(script.scenes)}")
    print(f"   ✓ 总时长: {script.total_duration}秒")

    # 显示场景概览
    print("\n   场景概览:")
    for scene in script.scenes:
        print(f"   - {scene.id} [{scene.type}] {scene.duration}秒")
        print(f"     文案: {scene.text[:40]}...")
        print(f"     插画: {scene.image_prompt[:40]}...")

    return script


def phase2_generate_images(
    script: Script,
    output_dir: Path,
    use_cache: bool = True,
    max_concurrent: int = 3,
    max_retries: int = 3
) -> dict:
    """Phase 2: AI 生成图片

    Args:
        script: 视频脚本
        output_dir: 输出目录
        use_cache: 是否使用缓存
        max_concurrent: 最大并发数
        max_retries: 最大重试次数
    """
    print(f"\n🎨 Phase 2: AI场景插画生成")
    print(f"   配置: 缓存={'启用' if use_cache else '禁用'}, 并发={max_concurrent}, 重试={max_retries}")

    try:
        generator = AIImageGenerator(
            max_retries=max_retries,
            parallel=(max_concurrent > 1)
        )
        image_paths = generator.generate_batch(
            script.scenes,
            output_dir / "images",
            use_cache=use_cache,
            max_concurrent=max_concurrent
        )
        print(f"   ✓ 生成插画: {len(image_paths)}张")
        return image_paths
    except Exception as e:
        print(f"   ✗ 图片生成失败: {e}")
        import traceback
        traceback.print_exc()
        return {}


async def phase3_generate_audio(
    scenes: List[Scene], output_dir: Path, tts_speed: Optional[float] = None
) -> Optional[dict]:
    """Phase 3: TTS 语音合成 (复用 remotion-skill)"""
    print(f"\n📢 Phase 3: 语音合成")

    # 延迟导入 remotion-skill 的 TTS（优先使用 Codex 目录）
    global tts_generate, tts_config
    remotion_skill_candidates = [
        Path.home() / ".codex" / "skills" / "remotion-skill" / "scripts",
        Path.home() / ".claude" / "skills" / "remotion-skill" / "scripts",
    ]
    remotion_skill_dir = next((p for p in remotion_skill_candidates if p.exists()), None)
    if remotion_skill_dir is None:
        print("   ✗ 未找到 remotion-skill/scripts，请先安装 remotion-skill")
        return None
    if str(remotion_skill_dir) not in sys.path:
        sys.path.insert(0, str(remotion_skill_dir))

    try:
        from tts_minimax import generate_speech
        # 使用 remotion-skill 的 TTSConfig
        from config import TTSConfig as RemotionTTSConfig
        tts_config = RemotionTTSConfig()
    except Exception as e:
        print(f"   ✗ 导入 TTS 模块失败: {e}")
        return None

    if not tts_config.api_key or not tts_config.group_id:
        print("   ⚠️ MiniMax TTS 未配置，跳过语音生成")
        return None

    if tts_speed is not None:
        # MiniMax speed 通常在 0.5-2.0，越小语速越慢
        tts_config.speed = max(0.5, min(2.0, tts_speed))
        print(f"   ⚙️ TTS语速: {tts_config.speed:.2f}")

    try:
        audio_dir = output_dir / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        audio_files = {}

        for i, scene in enumerate(scenes, 1):
            print(f"  [{i}/{len(scenes)}] {scene.id}: {scene.text[:30]}...")
            output_path = audio_dir / f"{scene.id}.mp3"
            meta_path = output_path.with_suffix(".json")

            # 强制刷新音频，避免 remotion-skill 直接复用旧 mp3 导致语速/文案变更不生效
            if output_path.exists():
                output_path.unlink()
            if meta_path.exists():
                meta_path.unlink()

            # 使用 remotion-skill 的 TTS (async版本)
            result = await generate_speech(scene.text, str(output_path), tts_config)
            audio_files[scene.id] = {
                "path": f"audio/{scene.id}.mp3",
                "duration_ms": result["duration_ms"],
                "word_timestamps": result.get("word_timestamps")
            }
            print(f"      ✓ 时长: {result['duration_ms']}ms")

        audio_data = {
            "files": audio_files,
            "total_duration_ms": sum(a["duration_ms"] for a in audio_files.values())
        }
        print(f"   ✓ 生成语音: {len(audio_files)}个")
        print(f"   ✓ 总时长: {audio_data['total_duration_ms']/1000:.1f}秒")
        return audio_data
    except Exception as e:
        print(f"   ✗ 语音生成失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def phase4_prepare_data(
    script: Script,
    audio_data: Optional[dict],
    image_paths: dict,
    output_dir: Path,
    scene_gap_seconds: float = 0.12,
    respect_script_duration: bool = False,
    book_cover_path: Optional[Path] = None,
    book_outro_seconds: float = DEFAULT_BOOK_OUTRO_SECONDS,
    book_outro_text: str = DEFAULT_BOOK_OUTRO_TEXT,
):
    """Phase 4: 准备 Remotion 数据"""
    print(f"\n📦 Phase 4: 数据准备")

    ensure_remotion_dirs()

    # 复制图片到 public 目录
    public_images_dir = REMOTION_DIR / "public" / "images"
    for scene_id, img_path in image_paths.items():
        src = output_dir / img_path
        if src.exists():
            dst = public_images_dir / f"{scene_id}.png"
            shutil.copy2(src, dst)
    print(f"   ✓ 复制图片: {len(image_paths)}个")

    # 复制音频到 public 目录
    if audio_data:
        public_audio_dir = REMOTION_DIR / "public" / "audio"
        for scene_id, audio_info in audio_data.get("files", {}).items():
            src = output_dir / audio_info["path"]
            if src.exists():
                dst = public_audio_dir / f"{scene_id}.mp3"
                shutil.copy2(src, dst)
        print(f"   ✓ 复制音频: {len(audio_data.get('files', {}))}个")

    # 生成 data.json
    data = {
        "meta": {
            "topic": script.topic,
            "title": script.title,
            "fps": video_config.fps,
            "width": video_config.width,
            "height": video_config.height
        },
        "scenes": [],
        "audio": audio_data,
    }

    scene_count = len(script.scenes)
    for idx, scene in enumerate(script.scenes):
        # 智能调整场景时长：
        # - 默认按音频时长 + 微小场景间隔，减少句子间空白停顿
        # - 可选尊重脚本预设时长（兼容旧行为）
        if audio_data and scene.id in audio_data.get("files", {}):
            audio_info = audio_data["files"][scene.id]
            audio_duration = audio_info["duration_ms"] / 1000
            # 最后一段不再追加额外间隔
            gap = 0 if idx == scene_count - 1 else max(scene_gap_seconds, 0)
            duration = round(audio_duration + gap, 2)
            if respect_script_duration:
                duration = max(duration, scene.duration)
        else:
            # 无音频时使用脚本预设时长
            duration = scene.duration

        scene_data = {
            "id": scene.id,
            "type": scene.type,
            "text": scene.text,
            "duration": duration,
            "image": f"images/{scene.id}.png",
            "visual_action": scene.visual_action,
        }

        if audio_data and scene.id in audio_data.get("files", {}):
            scene_data["audio"] = audio_data["files"][scene.id]

        data["scenes"].append(scene_data)

    data_path = REMOTION_DIR / "src" / "data.json"
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"   ✓ 数据文件: {data_path}")
    if audio_data:
        total_audio = audio_data.get("total_duration_ms", 0) / 1000
        total_video = sum(float(s.get("duration", 0)) for s in data["scenes"])
        extra_pause = max(total_video - total_audio, 0)
        print(
            f"   ✓ 节奏统计: 音频{total_audio:.1f}s, 视频{total_video:.1f}s, "
            f"额外停顿{extra_pause:.1f}s (scene_gap={scene_gap_seconds:.2f}s)"
        )

    # 书封结尾卡片（可选）
    if book_cover_path:
        static_image_path = copy_book_cover_to_public(book_cover_path)
        if static_image_path:
            data["book_outro"] = {
                "enabled": True,
                "image": static_image_path,
                "text": book_outro_text,
                "duration": max(0.1, min(float(book_outro_seconds), MAX_BOOK_OUTRO_SECONDS)),
            }
            with open(data_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(
                f"   ✓ 结尾书封: {book_cover_path} "
                f"(时长{min(float(book_outro_seconds), MAX_BOOK_OUTRO_SECONDS):.1f}s)"
            )
            if audio_data:
                final_total = total_video + min(float(book_outro_seconds), MAX_BOOK_OUTRO_SECONDS)
                print(f"   ✓ 预计成片总时长: {final_total:.1f}s")
        else:
            print(f"   ⚠️ 结尾书封未启用，文件不可用: {book_cover_path}")


def phase5_render_video(output_dir: Path) -> Optional[Path]:
    """Phase 5: 渲染视频"""
    print(f"\n🎬 Phase 5: 视频渲染")

    # 检查 Remotion 是否已安装
    node_modules = REMOTION_DIR / "node_modules"
    if not node_modules.exists():
        print("   ⚠️ Remotion 未安装，正在安装依赖...")
        result = subprocess.run(
            ["npm", "install"],
            cwd=REMOTION_DIR,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"   ✗ 安装失败: {result.stderr}")
            return None

    output_path = output_dir / "video.mp4"

    print(f"   渲染中...")
    result = subprocess.run(
        ["npx", "remotion", "render", "FinanceVideo", str(output_path),
         "--codec", "h264",
         "--crf", "20"],
        cwd=REMOTION_DIR,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"   ✗ 渲染失败: {result.stderr}")
        return None

    print(f"   ✓ 视频已生成: {output_path}")
    return output_path


def parse_topics(args) -> list:
    """解析主题列表"""
    if args.topics:
        # 支持逗号或空格分隔
        topics = args.topics.replace(",", " ").split()
        return [t.strip() for t in topics if t.strip()]
    elif args.topic:
        return [args.topic]
    return []


def sanitize_topic_name(topic: str) -> str:
    """清洗主题名用于目录"""
    cleaned = re.sub(r'[\\/:*?"<>|]+', "_", topic).strip()
    return cleaned or "未命名主题"


def export_voiceover_text(script: Script, output_dir: Path) -> Path:
    """导出口播文案文本"""
    output_path = output_dir / "口播文案.txt"
    lines = [f"主题：{script.topic}", f"标题：{script.title}", ""]
    for i, scene in enumerate(script.scenes, 1):
        lines.append(f"{i:02d}. [{scene.id} | {scene.type} | {scene.duration}s]")
        lines.append(scene.text.strip())
        lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"   ✓ 口播文案: {output_path}")
    return output_path


def copy_book_cover_to_public(book_cover_path: Path) -> Optional[str]:
    """复制书封到 Remotion public，返回 staticFile 路径"""
    if not book_cover_path.exists():
        return None

    ext = book_cover_path.suffix.lower() or ".jpg"
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        ext = ".jpg"
    target_name = f"book_cover{ext}"
    target_path = REMOTION_DIR / "public" / target_name
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(book_cover_path, target_path)
    return target_name


def script_total_chars(script: Script) -> int:
    """统计脚本总字数"""
    return sum(len((scene.text or "").strip()) for scene in script.scenes)


def estimate_audio_seconds(
    script: Script, tts_speed: float, chars_per_second_at_speed1: float = 5.8
) -> float:
    """估算固定语速下的口播时长"""
    if tts_speed <= 0:
        tts_speed = 1.0
    total_chars = script_total_chars(script)
    return total_chars / (chars_per_second_at_speed1 * tts_speed) if total_chars > 0 else 0.0


def estimate_total_video_seconds(
    script: Script,
    tts_speed: float,
    scene_gap: float,
    book_outro_seconds: float,
    chars_per_second_at_speed1: float = 5.8,
) -> float:
    """估算总时长：口播 + 场景间隔 + 书封结尾"""
    audio_seconds = estimate_audio_seconds(script, tts_speed, chars_per_second_at_speed1)
    gaps = max(len(script.scenes) - 1, 0) * max(scene_gap, 0)
    outro = max(book_outro_seconds, 0)
    return audio_seconds + gaps + outro


def load_script_from_file(script_path: Path) -> Script:
    """从 JSON 文件加载脚本"""
    with open(script_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    scenes = []
    for i, scene_data in enumerate(data.get("scenes", []), 1):
        scenes.append(
            Scene(
                id=scene_data.get("id", f"scene_{i:02d}"),
                type=scene_data.get("type", "explain"),
                text=scene_data.get("text", ""),
                duration=int(scene_data.get("duration", 8)),
                visual_action=scene_data.get("visual_action", "none"),
                image_prompt=scene_data.get("image_prompt", ""),
            )
        )

    if not scenes:
        raise ValueError(f"脚本无有效场景: {script_path}")

    return Script(
        topic=data.get("topic", "unknown"),
        title=data.get("title", "财经科普视频"),
        total_duration=int(data.get("totalDuration", 120)),
        scenes=scenes,
    )


def reuse_existing_images(
    script: Script, reuse_from: Path, output_dir: Path
) -> Tuple[Dict[str, str], List[Scene]]:
    """复用已有图片素材，返回(已复用映射, 缺失场景列表)"""
    source_images_dir = reuse_from / "images"
    target_images_dir = output_dir / "images"
    target_images_dir.mkdir(parents=True, exist_ok=True)

    reused: Dict[str, str] = {}
    missing: List[Scene] = []
    for scene in script.scenes:
        src = source_images_dir / f"{scene.id}.png"
        dst = target_images_dir / f"{scene.id}.png"
        if src.exists():
            if src.resolve() != dst.resolve():
                shutil.copy2(src, dst)
            reused[scene.id] = f"images/{scene.id}.png"
        else:
            missing.append(scene)

    print(f"   ♻️ 复用图片: {len(reused)}张, 待生成: {len(missing)}张")
    return reused, missing


def reuse_existing_audio(
    script: Script, reuse_from: Path, output_dir: Path
) -> Tuple[Optional[dict], List[Scene]]:
    """复用已有音频素材，返回(音频数据, 缺失场景列表)"""
    source_audio_dir = reuse_from / "audio"
    target_audio_dir = output_dir / "audio"
    target_audio_dir.mkdir(parents=True, exist_ok=True)

    audio_files = {}
    missing: List[Scene] = []

    for scene in script.scenes:
        src_mp3 = source_audio_dir / f"{scene.id}.mp3"
        src_meta = source_audio_dir / f"{scene.id}.json"
        dst_mp3 = target_audio_dir / f"{scene.id}.mp3"

        if not src_mp3.exists():
            missing.append(scene)
            continue

        if src_mp3.resolve() != dst_mp3.resolve():
            shutil.copy2(src_mp3, dst_mp3)
        duration_ms = int(scene.duration * 1000)
        word_timestamps = None
        if src_meta.exists():
            try:
                with open(src_meta, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                duration_ms = int(meta.get("duration_ms", duration_ms))
                word_timestamps = meta.get("word_timestamps")
            except Exception as e:
                print(f"   ⚠️ 音频元数据读取失败 {src_meta.name}: {e}")

        audio_files[scene.id] = {
            "path": f"audio/{scene.id}.mp3",
            "duration_ms": duration_ms,
            "word_timestamps": word_timestamps,
        }

    if not audio_files:
        print("   ♻️ 未复用到音频")
        return None, script.scenes

    total_duration_ms = sum(item["duration_ms"] for item in audio_files.values())
    print(f"   ♻️ 复用音频: {len(audio_files)}段, 待生成: {len(missing)}段")
    return {"files": audio_files, "total_duration_ms": total_duration_ms}, missing


def merge_audio_data(base: Optional[dict], extra: Optional[dict]) -> Optional[dict]:
    """合并两份音频数据"""
    if not base and not extra:
        return None

    merged_files = {}
    if base:
        merged_files.update(base.get("files", {}))
    if extra:
        merged_files.update(extra.get("files", {}))

    return {
        "files": merged_files,
        "total_duration_ms": sum(v.get("duration_ms", 0) for v in merged_files.values()),
    }


async def main():
    parser = argparse.ArgumentParser(
        description="财经视频AI生成器 - 一键生成2分钟财经科普短视频",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 单主题生成
  python3 scripts/main.py --topic "IPO"              # 完整流程
  python3 scripts/main.py -t "基金定投"              # 简写
  python3 scripts/main.py -t "股票" --dry-run        # 仅生成脚本
  python3 scripts/main.py -t "债券" --skip-tts       # 跳过语音
  python3 scripts/main.py -t "保险" --skip-render    # 跳过渲染

  # 批量生成
  python3 scripts/main.py --topics "IPO,基金,股票"    # 批量生成多个主题
  python3 scripts/main.py -T "IPO 基金 股票"          # 空格分隔

  # 缓存管理
  python3 scripts/main.py -t "IPO" --clear-cache      # 生成前清除缓存
  python3 scripts/main.py -t "IPO" --no-cache         # 禁用缓存

  # 性能调优
  python3 scripts/main.py -t "IPO" --concurrent 5     # 调整并发数
  python3 scripts/main.py -t "IPO" --max-retries 5    # 调整重试次数
  python3 scripts/main.py -t "IPO" --sequential       # 禁用并行生成

  # 复用已有素材（默认复用 script/images/audio）
  python3 scripts/main.py -t "对冲基金" --reuse-from "./output/对冲基金_20260215_063211"
        """
    )
    # 输入选项
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--topic", "-t", help="视频主题")
    input_group.add_argument("--topics", "-T", help="批量生成多个主题（逗号或空格分隔）")

    parser.add_argument("--output", "-o", type=Path, default=None, help="输出目录")
    parser.add_argument(
        "--export-root",
        type=Path,
        default=DEFAULT_EXPORT_ROOT,
        help=f"输出根目录（默认: {DEFAULT_EXPORT_ROOT}）",
    )
    parser.add_argument("--dry-run", action="store_true", help="仅生成脚本（快速测试）")
    parser.add_argument("--skip-tts", action="store_true", help="跳过语音生成")
    parser.add_argument("--skip-render", action="store_true", help="跳过视频渲染")
    parser.add_argument("--no-check", action="store_true", help="跳过依赖检查")
    parser.add_argument("--target-duration", type=float, default=120.0, help="目标总时长（秒）")
    parser.add_argument(
        "--target-tolerance",
        type=float,
        default=6.0,
        help="目标时长容差（秒，默认: 6）",
    )
    parser.add_argument(
        "--script-attempts",
        type=int,
        default=3,
        help="脚本生成尝试次数（默认: 3）",
    )
    parser.add_argument("--scene-gap", type=float, default=0.12, help="场景间停顿秒数 (默认: 0.12)")
    parser.add_argument("--tts-speed", type=float, default=1.0, help="TTS基准语速 (0.5-2.0，默认: 1.0)")
    parser.add_argument(
        "--use-script-duration",
        action="store_true",
        help="按脚本预设时长延展场景（可能导致句间停顿偏长）",
    )
    parser.add_argument(
        "--book-cover",
        type=Path,
        default=DEFAULT_BOOK_COVER,
        help="结尾书封图片路径",
    )
    parser.add_argument(
        "--book-outro-seconds",
        type=float,
        default=DEFAULT_BOOK_OUTRO_SECONDS,
        help=f"结尾书封展示时长（秒，默认: {DEFAULT_BOOK_OUTRO_SECONDS}，最大: {MAX_BOOK_OUTRO_SECONDS}）",
    )
    parser.add_argument(
        "--book-outro-text",
        type=str,
        default=DEFAULT_BOOK_OUTRO_TEXT,
        help="结尾书封小字文案",
    )

    # 缓存选项
    parser.add_argument("--no-cache", action="store_true", help="禁用图片缓存")
    parser.add_argument("--clear-cache", action="store_true", help="生成前清除图片缓存")
    parser.add_argument("--reuse-from", type=Path, default=None, help="复用已有输出目录中的素材")
    parser.add_argument("--reuse-script", action="store_true", help="复用已有 script.json")
    parser.add_argument("--reuse-images", action="store_true", help="复用已有图片素材")
    parser.add_argument("--reuse-audio", action="store_true", help="复用已有音频素材")

    # 性能选项
    parser.add_argument("--concurrent", "-c", type=int, default=3, help="图片生成并发数 (默认: 3)")
    parser.add_argument("--max-retries", type=int, default=3, help="图片生成重试次数 (默认: 3)")
    parser.add_argument("--sequential", action="store_true", help="禁用并行生成，改用串行")

    # 图片生成器选项
    parser.add_argument("--image-timeout", type=int, default=120, help="图片生成超时秒数 (默认: 120)")
    args = parser.parse_args()

    # reuse-from 默认开启全量复用
    if args.reuse_from and not (args.reuse_script or args.reuse_images or args.reuse_audio):
        args.reuse_script = True
        args.reuse_images = True
        args.reuse_audio = True

    if args.scene_gap < 0:
        args.scene_gap = 0
    args.target_duration = max(10.0, float(args.target_duration))
    args.target_tolerance = max(1.0, float(args.target_tolerance))
    args.script_attempts = max(1, int(args.script_attempts))
    args.tts_speed = max(0.5, min(2.0, float(args.tts_speed)))
    requested_outro = max(0.1, float(args.book_outro_seconds))
    if requested_outro > MAX_BOOK_OUTRO_SECONDS:
        print(
            f"⚠️ 结尾书封时长 {requested_outro:.1f}s 超过上限，已自动限制为 "
            f"{MAX_BOOK_OUTRO_SECONDS:.1f}s"
        )
    args.book_outro_seconds = min(requested_outro, MAX_BOOK_OUTRO_SECONDS)
    args.export_root = args.export_root.expanduser().resolve()
    args.book_cover = args.book_cover.expanduser().resolve() if args.book_cover else None

    # 解析主题列表
    topics = parse_topics(args)
    if not topics:
        print("❌ 请提供至少一个主题")
        return

    print_banner()

    # 检查依赖
    if not args.no_check:
        if not check_dependencies():
            return
        if not check_api_keys():
            print("\n⚠️ 部分 API 未配置，某些功能可能不可用")

    # 处理缓存清除
    if args.clear_cache:
        try:
            from image_generator import AIImageGenerator
            gen = AIImageGenerator(max_retries=1, parallel=False)
            cleared = gen.clear_cache()
            print(f"\n🗑️ 已清除 {cleared} 个缓存图片")
        except Exception as e:
            print(f"\n⚠️ 清除缓存失败: {e}")

    # 批量生成
    if len(topics) > 1:
        print(f"\n📦 批量生成模式: {len(topics)} 个主题")
        for i, topic in enumerate(topics, 1):
            print(f"\n{'='*50}")
            print(f"  [{i}/{len(topics)}] 处理主题: {topic}")
            print(f"{'='*50}")
            await process_single_topic(
                topic, args,
                custom_output_dir=args.output / topic if args.output else None
            )
        print(f"\n✅ 批量生成完成！共处理 {len(topics)} 个主题")
    else:
        # 单主题生成
        await process_single_topic(topics[0], args)


async def process_single_topic(topic: str, args, custom_output_dir: Path = None):
    """处理单个主题的生成"""
    reuse_from = args.reuse_from.expanduser().resolve() if args.reuse_from else None
    if reuse_from and not reuse_from.exists():
        print(f"\n⚠️ 复用目录不存在，已忽略: {reuse_from}")
        reuse_from = None

    # 设置输出目录
    if custom_output_dir:
        output_dir = custom_output_dir
    elif args.output:
        output_dir = args.output
    else:
        topic_dir = sanitize_topic_name(topic)
        output_dir = args.export_root / topic_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n📁 输出目录: {output_dir}")

    # Phase 1: 生成脚本 / 复用脚本
    script = None
    if reuse_from and args.reuse_script:
        script_path = reuse_from / "script.json"
        if script_path.exists():
            script = load_script_from_file(script_path)
            save_script(script, output_dir / "script.json")
            print(f"   ♻️ 已复用脚本: {script_path}")
        else:
            print(f"   ⚠️ 未找到可复用脚本: {script_path}")

    if script is None:
        best_script: Optional[Script] = None
        best_delta = float("inf")
        print(
            f"\n🎯 脚本时长规划: 目标{args.target_duration:.1f}s, 固定语速{args.tts_speed:.2f}, "
            f"最多尝试{args.script_attempts}次"
        )
        for attempt in range(1, args.script_attempts + 1):
            print(f"\n   ├─ 脚本尝试 {attempt}/{args.script_attempts}")
            candidate = phase1_generate_script(topic, output_dir=None, save=False)
            estimated_total = estimate_total_video_seconds(
                candidate,
                tts_speed=args.tts_speed,
                scene_gap=args.scene_gap,
                book_outro_seconds=args.book_outro_seconds,
            )
            delta = abs(estimated_total - args.target_duration)
            print(
                f"   └─ 估算总时长: {estimated_total:.1f}s "
                f"(目标{args.target_duration:.1f}s, 偏差{delta:.1f}s)"
            )
            if delta < best_delta:
                best_script = candidate
                best_delta = delta
            if delta <= args.target_tolerance:
                break

        script = best_script if best_script else phase1_generate_script(topic, output_dir=None, save=False)

        # 二次长度校准：保持场景结构不变，仅重写 text
        for refine_round in range(1, 3):
            estimated_total = estimate_total_video_seconds(
                script,
                tts_speed=args.tts_speed,
                scene_gap=args.scene_gap,
                book_outro_seconds=args.book_outro_seconds,
            )
            delta = abs(estimated_total - args.target_duration)
            if delta <= args.target_tolerance:
                break

            target_audio_seconds = (
                args.target_duration
                - args.book_outro_seconds
                - args.scene_gap * max(len(script.scenes) - 1, 0)
            )
            target_audio_seconds = max(20.0, target_audio_seconds)
            target_chars = int(target_audio_seconds * 5.8 * args.tts_speed)
            min_chars = max(200, target_chars - 45)
            max_chars = target_chars + 45

            print(
                f"\n🛠️ 文案长度校准 {refine_round}/2: 当前估算{estimated_total:.1f}s, "
                f"目标{args.target_duration:.1f}s, 目标字数{min_chars}-{max_chars}"
            )
            refined = rewrite_script_for_target_chars(script, min_chars, max_chars)
            refined_estimated = estimate_total_video_seconds(
                refined,
                tts_speed=args.tts_speed,
                scene_gap=args.scene_gap,
                book_outro_seconds=args.book_outro_seconds,
            )
            refined_delta = abs(refined_estimated - args.target_duration)
            print(
                f"   ✓ 校准后估算: {refined_estimated:.1f}s "
                f"(偏差{refined_delta:.1f}s)"
            )
            if refined_delta <= delta:
                script = refined

        save_script(script, output_dir / "script.json")

    # 导出口播文案
    export_voiceover_text(script, output_dir)

    if args.dry_run:
        print("\n🏃 Dry run 完成")
        print(f"📁 输出目录: {output_dir}")
        return

    # Phase 2: AI 生成图片（优先复用）
    image_paths: Dict[str, str] = {}
    missing_image_scenes = script.scenes
    if reuse_from and args.reuse_images:
        reused_images, missing_image_scenes = reuse_existing_images(script, reuse_from, output_dir)
        image_paths.update(reused_images)

    if missing_image_scenes:
        partial_script = Script(
            topic=script.topic,
            title=script.title,
            total_duration=script.total_duration,
            scenes=missing_image_scenes,
        )
        generated_images = phase2_generate_images(
            partial_script,
            output_dir,
            use_cache=not args.no_cache,
            max_concurrent=args.concurrent if not args.sequential else 1,
            max_retries=args.max_retries,
        )
        image_paths.update(generated_images)
    else:
        print("\n🎨 Phase 2: AI场景插画生成")
        print("   ♻️ 所有图片已复用，跳过生成")

    if len(image_paths) < len(script.scenes):
        print("\n✗ 图片生成失败，无法继续")
        return

    # Phase 3: TTS（优先复用）
    audio_data = None
    missing_audio_scenes = script.scenes
    tts_speed_to_use = args.tts_speed
    print(f"\n⚙️ 固定语速模式: TTS语速={tts_speed_to_use:.2f}")
    if reuse_from and args.reuse_audio:
        audio_data, missing_audio_scenes = reuse_existing_audio(script, reuse_from, output_dir)

    if missing_audio_scenes:
        if not args.skip_tts and tts_config and tts_config.is_configured:
            generated_audio = await phase3_generate_audio(
                missing_audio_scenes, output_dir, tts_speed=tts_speed_to_use
            )
            audio_data = merge_audio_data(audio_data, generated_audio)
        elif args.skip_tts:
            print("\n⏭️ 跳过语音生成")
        else:
            print("\n⏭️ TTS 未配置，跳过语音生成")
    elif audio_data:
        print("\n📢 Phase 3: 语音合成")
        print("   ♻️ 所有音频已复用，跳过生成")

    # Phase 4: 准备数据
    phase4_prepare_data(
        script,
        audio_data,
        image_paths,
        output_dir,
        scene_gap_seconds=args.scene_gap,
        respect_script_duration=args.use_script_duration,
        book_cover_path=args.book_cover,
        book_outro_seconds=args.book_outro_seconds,
        book_outro_text=args.book_outro_text,
    )

    # Phase 5: 渲染
    if not args.skip_render:
        video_path = phase5_render_video(output_dir)
        if video_path:
            print(f"\n✅ 完成！视频已生成: {video_path}")
        else:
            print("\n⚠️ 视频渲染失败")
    else:
        print("\n⏭️ 跳过视频渲染")

    print(f"\n📁 输出目录: {output_dir}")


if __name__ == "__main__":
    asyncio.run(main())
