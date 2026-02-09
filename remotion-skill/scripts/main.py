#!/usr/bin/env python3
"""
秒懂金融视频生成器 - 主入口
Main entry point for Miaodong Finance Video Generator

Usage:
    python3 main.py --topic "IPO" --output ./output
    python3 main.py --topic "基金" --duration 120 --style compact
    python3 main.py --script ./script.json --output ./output  # Use existing script
"""

import os
import sys
import json
import argparse
import asyncio
import subprocess
import shutil
from pathlib import Path
from typing import Optional

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    GenerationConfig, VideoConfig, TTSConfig,
    SKILL_ROOT, REMOTION_DIR, OUTPUT_DIR,
    validate_config,
    get_icon_path
)
from content_generator import generate_script, save_script, load_script, VideoScript
from tts_minimax import MiniMaxTTS
from asset_matcher import match_all_scenes, check_assets_availability


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="秒懂金融视频生成器 - 根据主题生成财经科普视频"
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--topic", "-t",
        help="视频主题（如：IPO、基金、股票）"
    )
    input_group.add_argument(
        "--script", "-s",
        type=Path,
        help="使用已有的脚本文件（跳过内容生成）"
    )

    # Output options
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=OUTPUT_DIR,
        help="输出目录（默认：./output）"
    )

    # Generation options
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=150,
        help="目标时长（秒），默认150秒（2.5分钟）"
    )
    parser.add_argument(
        "--style",
        choices=["compact", "detailed"],
        default="detailed",
        help="风格：compact（精简）或 detailed（详细）"
    )
    parser.add_argument(
        "--voice",
        default=None,
        help="语音音色ID（默认：使用 MINIMAX_VOICE_ID 或 config.py 默认值）"
    )

    # Voice cloning options (MiniMax Voice Cloning API)
    parser.add_argument(
        "--clone-voice-from",
        type=Path,
        default=None,
        help="可选：从参考音频克隆音色（会创建/返回一个 voice_id 并用于本次生成）"
    )
    parser.add_argument(
        "--clone-voice-id",
        default="miaodong-custom-voice",
        help="可选：克隆后的 voice_id（默认：miaodong-custom-voice）"
    )
    parser.add_argument(
        "--clone-preview-text",
        default=None,
        help="可选：克隆后试听文本（会请求 demo_audio URL）"
    )

    # Execution options
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅生成脚本，不生成语音和视频"
    )
    parser.add_argument(
        "--skip-tts",
        action="store_true",
        help="跳过语音生成"
    )
    parser.add_argument(
        "--skip-render",
        action="store_true",
        help="跳过视频渲染"
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="在 Remotion Studio 中预览（不渲染）"
    )

    return parser.parse_args()


def _is_probably_mp3(path: Path) -> bool:
    """Best-effort check to avoid rendering with corrupted cached audio files."""
    try:
        head = path.read_bytes()[:4]
    except Exception:
        return False
    if head.startswith(b"ID3"):
        return True
    return len(head) >= 2 and head[0] == 0xFF and (head[1] & 0xE0) == 0xE0


async def generate_audio(script: VideoScript, output_dir: Path, config: TTSConfig) -> dict:
    """Generate audio for all scenes"""
    print("\n📢 Phase 2: 生成语音...")

    audio_dir = output_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    tts = MiniMaxTTS(config)

    audio_files = {}
    total_duration = 0

    # Reuse one HTTP session across scenes to reduce connection overhead / timeouts.
    import aiohttp
    timeout = aiohttp.ClientTimeout(total=180, connect=30, sock_connect=30, sock_read=180)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for i, scene in enumerate(script.scenes):
            print(f"  [{i+1}/{len(script.scenes)}] {scene.id}: {scene.text[:30]}...")

            output_path = audio_dir / f"{scene.id}.mp3"
            result = await tts.synthesize(scene.text, output_path, session=session)

            audio_files[scene.id] = {
                "path": str(output_path.relative_to(output_dir)),
                "duration_ms": result.duration_ms,
                "word_timestamps": result.word_timestamps
            }
            total_duration += result.duration_ms

    print(f"  ✓ 语音生成完成，总时长: {total_duration / 1000:.1f}秒")

    return {
        "files": audio_files,
        "total_duration_ms": total_duration
    }


def prepare_remotion_data(
    script: VideoScript,
    audio_data: Optional[dict],
    assets: list,
    output_dir: Path
) -> Path:
    """Prepare data file for Remotion"""
    print("\n📦 准备 Remotion 数据...")

    # === 复制音频文件到 public 目录 ===
    public_audio_dir = REMOTION_DIR / "public" / "audio"
    public_audio_dir.mkdir(parents=True, exist_ok=True)

    if audio_data:
        for scene_id, audio_info in audio_data.get("files", {}).items():
            source_path = output_dir / audio_info["path"]
            if source_path.exists():
                dest_path = public_audio_dir / f"{scene_id}.mp3"
                shutil.copy2(source_path, dest_path)
                print(f"  ✓ 复制音频: {scene_id}.mp3")

    # === 复制素材到 public 目录 ===
    public_assets_dir = REMOTION_DIR / "public" / "assets"
    public_icons_dir = public_assets_dir / "icons"
    public_icons_dir.mkdir(parents=True, exist_ok=True)

    def add_icon_to_public(icon_path: Optional[Path]) -> Optional[str]:
        if not icon_path or not icon_path.exists():
            return None
        dest_path = public_icons_dir / icon_path.name
        if not dest_path.exists():
            shutil.copy2(icon_path, dest_path)
            print(f"  ✓ 复制素材: {icon_path.name}")
        return f"assets/icons/{icon_path.name}"

    def pick_extra_icon_names(scene_type: str, primary_icon_name: Optional[str]) -> list:
        # Deterministic + simple: enough density without complex NLP.
        candidates_by_type = {
            "hook": ["stock_up", "money", "chart", "company"],
            "title": ["chart", "trend", "stock"],
            "question": ["risk", "company", "chart"],
            "explain": ["report", "money", "growth"],
            "analogy": ["company", "wallet", "coin"],
            "example": ["yuan", "dollar", "report"],
            "comparison": ["risk", "growth", "trend"],
            "summary": ["exchange", "trend", "money"],
            "cta": ["trend", "stock", "money"],
        }
        names = candidates_by_type.get(scene_type, ["money", "stock", "chart"])
        # Remove primary, keep unique, limit.
        out = []
        for n in names:
            if primary_icon_name and n == primary_icon_name:
                continue
            if n not in out:
                out.append(n)
        return out[:4]

    for asset in assets:
        # Primary icon
        add_icon_to_public(asset.icon_path)

    data = {
        "meta": {
            "topic": script.topic,
            "title": script.title,
            "fps": 30,
            "width": 1080,
            "height": 1440
        },
        "scenes": [],
        "audio": audio_data
    }

    for scene, asset in zip(script.scenes, assets):
        # Use audio duration if available, otherwise use static duration
        duration = scene.duration
        if audio_data and scene.id in audio_data.get("files", {}):
            audio_duration_ms = audio_data["files"][scene.id].get("duration_ms", 0)
            if audio_duration_ms > 0:
                duration = audio_duration_ms / 1000  # Convert ms to seconds

        scene_data = {
            "id": scene.id,
            "type": scene.type,
            "text": scene.text,
            "duration": duration,
            "character": {
                "type": scene.character,
                "path": None  # 使用 SVG 火柴人
            },
            "icon": {
                "name": asset.icon_name,
                "path": add_icon_to_public(asset.icon_path)
            } if asset.icon_name else None
        }

        # Extra icons to increase visual density (icon cloud).
        primary_name = asset.icon_name
        extra_icons = []
        for name in pick_extra_icon_names(scene.type, primary_name):
            p = get_icon_path(name)
            rel = add_icon_to_public(p) if p else None
            if rel:
                extra_icons.append({"name": name, "path": rel})
        if extra_icons:
            scene_data["extra_icons"] = extra_icons

        # Add audio timing if available
        if audio_data and scene.id in audio_data.get("files", {}):
            scene_data["audio"] = audio_data["files"][scene.id]

        data["scenes"].append(scene_data)

    # Write data file
    data_path = REMOTION_DIR / "src" / "data.json"
    data_path.parent.mkdir(parents=True, exist_ok=True)

    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"  ✓ 数据文件已生成: {data_path}")

    return data_path


def render_video(output_dir: Path, preview: bool = False) -> Optional[Path]:
    """Render video using Remotion"""
    print("\n🎬 Phase 3: 渲染视频...")

    # Check if Remotion project exists
    package_json = REMOTION_DIR / "package.json"
    if not package_json.exists():
        print("  ⚠️ Remotion 项目未初始化，请先运行:")
        print(f"     cd {REMOTION_DIR} && npm install")
        return None

    if preview:
        print("  启动 Remotion Studio 预览...")
        subprocess.run(
            ["npx", "remotion", "studio"],
            cwd=REMOTION_DIR
        )
        return None

    output_path = output_dir / "video.mp4"

    print("  渲染中...")
    result = subprocess.run(
        [
            "npx", "remotion", "render",
            "MiaodongVideo",
            str(output_path)
        ],
        cwd=REMOTION_DIR,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"  ❌ 渲染失败: {result.stderr}")
        return None

    print(f"  ✓ 视频已生成: {output_path}")
    return output_path


async def main():
    """Main execution flow"""
    args = parse_args()

    print("=" * 50)
    print("🎥 秒懂金融视频生成器")
    print("=" * 50)

    # Setup configuration
    # Normalize to absolute path so Remotion render output path is stable regardless of cwd.
    output_dir = Path(args.output).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine which voice_id to use.
    # Priority: --voice > cloned voice_id > MINIMAX_VOICE_ID/config default
    voice_id = args.voice or TTSConfig().voice_id

    # Optional: clone voice from reference audio.
    if args.clone_voice_from:
        from voice_clone_minimax import upload_file, clone_voice
        import aiohttp

        source_audio = Path(args.clone_voice_from).expanduser().resolve()
        clone_voice_id = args.clone_voice_id
        print(f"\n🧬 语音克隆: {source_audio}")

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=180)) as session:
            up = await upload_file(session, source_audio, "voice_clone")
            try:
                payload = await clone_voice(
                    session,
                    source_file_id=up.file_id,
                    voice_id=clone_voice_id,
                    model="speech-2.8-hd" if args.clone_preview_text else None,
                    preview_text=args.clone_preview_text,
                )
                demo_audio = payload.get("demo_audio")
                print(f"  ✓ voice_id: {clone_voice_id}")
                if demo_audio:
                    print(f"  ✓ demo_audio: {demo_audio}")
                voice_id = clone_voice_id
            except Exception as e:
                # If cloning fails (e.g. voice_id already exists), we still proceed using the provided voice_id.
                print(f"  ⚠️ 语音克隆失败（将继续尝试使用 voice_id={clone_voice_id} 进行合成）: {e}")
                voice_id = clone_voice_id

    tts_config = TTSConfig(voice_id=voice_id)

    # Phase 1: Generate or load script
    if args.script:
        print(f"\n📄 加载脚本: {args.script}")
        script = load_script(args.script)
    else:
        print(f"\n📝 Phase 1: 生成脚本 - 主题: {args.topic}")
        script = generate_script(
            topic=args.topic,
            target_duration=args.duration,
            style=args.style
        )

        # Save script
        script_path = output_dir / "script.json"
        save_script(script, script_path)
        print(f"  ✓ 脚本已保存: {script_path}")

    print(f"\n  标题: {script.title}")
    print(f"  场景数: {len(script.scenes)}")
    print(f"  预计时长: {script.total_duration}秒")

    if args.dry_run:
        print("\n🏃 Dry run 模式 - 仅生成脚本")
        print("\n脚本内容:")
        print(script.to_json())
        return

    # Match assets
    print("\n🎨 匹配素材...")
    assets = match_all_scenes([s.__dict__ for s in script.scenes])

    # Check asset availability
    availability = check_assets_availability()
    # Characters are optional now (we render a built-in SVG avatar instead of image assets).
    missing_chars = 0
    missing_icons = sum(1 for v in availability["icons"].values() if not v["exists"])

    if missing_chars > 0 or missing_icons > 0:
        print(f"  ⚠️ 缺少 {missing_chars} 个角色素材, {missing_icons} 个图标素材")
        print("     可运行: python3 asset_matcher.py --create-placeholders 生成占位图")

    # Phase 2: Generate audio
    audio_data = None
    if not args.skip_tts:
        if not tts_config.api_key:
            print("\n⚠️ 跳过语音生成（MINIMAX_API_KEY 未设置）")
        elif not tts_config.group_id:
            print("\n⚠️ 跳过语音生成（MINIMAX_GROUP_ID 未设置）")
        else:
            try:
                audio_data = await generate_audio(script, output_dir, tts_config)
            except Exception as e:
                print(f"\n❌ 语音生成失败: {e}")
                print("   你可以先用 --skip-tts 跑通渲染链路，或检查 MINIMAX_API_KEY / MINIMAX_GROUP_ID 是否正确。")
                audio_data = None
    else:
        print("\n⏭️ 跳过语音生成")
        # Load existing audio metadata if available
        audio_dir = output_dir / "audio"
        if audio_dir.exists():
            print("  📂 加载已有音频元数据...")
            audio_files = {}
            total_duration = 0
            for scene in script.scenes:
                json_path = audio_dir / f"{scene.id}.json"
                mp3_path = audio_dir / f"{scene.id}.mp3"
                if json_path.exists() and mp3_path.exists():
                    if not _is_probably_mp3(mp3_path):
                        print(f"  ⚠️ 跳过损坏音频: {mp3_path}")
                        continue
                    with open(json_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    audio_files[scene.id] = {
                        "path": f"audio/{scene.id}.mp3",
                        "duration_ms": meta.get("duration_ms", scene.duration * 1000),
                        "word_timestamps": meta.get("word_timestamps")
                    }
                    total_duration += meta.get("duration_ms", 0)
            if audio_files:
                audio_data = {
                    "files": audio_files,
                    "total_duration_ms": total_duration
                }
                print(f"  ✓ 已加载 {len(audio_files)} 个音频文件，总时长: {total_duration / 1000:.1f}秒")

    # Prepare Remotion data
    prepare_remotion_data(script, audio_data, assets, output_dir)

    # Phase 3: Render video
    if not args.skip_render:
        video_path = render_video(output_dir, preview=args.preview)
        if video_path:
            print(f"\n✅ 完成！视频已生成: {video_path}")
    else:
        print("\n⏭️ 跳过视频渲染")

    print("\n" + "=" * 50)
    print("📁 输出目录:", output_dir)
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
