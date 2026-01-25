#!/usr/bin/env python3
"""
yt-dlp 视频下载脚本
支持从 1000+ 网站下载视频
"""

import sys
import json
import subprocess
from pathlib import Path


def get_video_info(url):
    """获取视频信息"""
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--dump-json",
        "--skip-download",
        url
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        return {
            "title": info.get("title", "Unknown"),
            "duration": info.get("duration_string", "Unknown"),
            "uploader": info.get("uploader", "Unknown"),
            "view_count": info.get("view_count", "Unknown"),
            "upload_date": info.get("upload_date", "Unknown"),
            "thumbnail": info.get("thumbnail", ""),
        }
    except subprocess.CalledProcessError as e:
        return {"error": f"获取视频信息失败: {e.stderr}"}
    except json.JSONDecodeError:
        return {"error": "解析视频信息失败"}


def download_video(url, output_dir="~/Downloads/videos", quality="best", format="mp4",
                   subtitles=False, audio_only=False):
    """
    下载视频

    Args:
        url: 视频URL
        output_dir: 输出目录
        quality: 视频质量 (best/1080p/720p/480p)
        format: 视频格式 (mp4/mkv/webm)
        subtitles: 是否下载字幕
        audio_only: 是否只下载音频

    Returns:
        下载结果信息
    """
    output_dir = Path(output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    # 构建 yt-dlp 命令
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "-o", str(output_dir / "%(title)s.%(ext)s"),
        "--no-playlist"
    ]

    # 音频或视频
    if audio_only:
        cmd.extend(["-x", "--audio-format", "mp3", "--audio-quality", "0"])
    else:
        # 视频质量选择
        quality_formats = {
            "best": "bestvideo+bestaudio/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]"
        }
        cmd.extend(["-f", quality_formats.get(quality, quality_formats["best"])])
        cmd.extend(["--merge-output-format", format])

    # 字幕
    if subtitles:
        cmd.extend([
            "--write-subs",
            "--sub-lang", "zh-Hans,zh-Hant,en",
            "--embed-subs"
        ])

    cmd.append(url)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # 从输出中提取文件名
        lines = result.stdout.split('\n')
        for line in lines:
            if '[download] Destination:' in line:
                filename = line.split('Destination:')[-1].strip()
                return {
                    "success": True,
                    "file": filename,
                    "message": result.stdout
                }
        return {"success": True, "message": result.stdout}
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "error": f"下载失败: {e.stderr}",
            "stdout": e.stdout,
            "stderr": e.stderr
        }


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python download.py <URL> [options]")
        print("选项:")
        print("  --output DIR     输出目录 (默认: ~/Downloads/videos)")
        print("  --quality Q      视频质量 (best/1080p/720p/480p)")
        print("  --format F       视频格式 (mp4/mkv/webm)")
        print("  --subtitles      下载字幕")
        print("  --audio-only     仅下载音频")
        print("  --info           只获取视频信息")
        sys.exit(1)

    url = sys.argv[1]

    # 解析参数
    args = {
        "output_dir": "~/Downloads/videos",
        "quality": "best",
        "format": "mp4",
        "subtitles": False,
        "audio_only": False
    }

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            args["output_dir"] = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--quality" and i + 1 < len(sys.argv):
            args["quality"] = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--format" and i + 1 < len(sys.argv):
            args["format"] = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--subtitles":
            args["subtitles"] = True
            i += 1
        elif sys.argv[i] == "--audio-only":
            args["audio_only"] = True
            i += 1
        elif sys.argv[i] == "--info":
            info = get_video_info(url)
            print(json.dumps(info, indent=2, ensure_ascii=False))
            sys.exit(0)
        else:
            i += 1

    result = download_video(url, **args)

    if result.get("success"):
        print("✓ 下载成功!")
        if "file" in result:
            print(f"文件: {result['file']}")
        sys.exit(0)
    else:
        print("✗ 下载失败:", result.get("error"))
        sys.exit(1)


if __name__ == "__main__":
    main()
