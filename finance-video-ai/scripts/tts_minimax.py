#!/usr/bin/env python3
"""
财经视频AI生成器 - MiniMax TTS 语音合成
复用自 remotion-skill
"""
import aiohttp
import asyncio
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

from config import tts_config


@dataclass
class WordTimestamp:
    """词语时间戳"""
    word: str
    start_ms: int
    end_ms: int


@dataclass
class TTSResult:
    """TTS合成结果"""
    audio_path: Path
    duration_ms: int
    word_timestamps: Optional[List[WordTimestamp]] = None


class MiniMaxTTS:
    """MiniMax TTS 客户端"""

    def __init__(self, config=None):
        self.config = config or tts_config
        if not self.config.is_configured:
            raise ValueError("MiniMax TTS 未配置，请设置 MINIMAX_API_KEY 和 MINIMAX_GROUP_ID")

    async def synthesize(
        self,
        text: str,
        output_path: Path,
        session: Optional[aiohttp.ClientSession] = None
    ) -> TTSResult:
        """
        合成语音

        Args:
            text: 要合成的文本
            output_path: 输出文件路径
            session: aiohttp 会话（可选，用于连接复用）

        Returns:
            TTSResult: 合成结果
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "text": text,
            "voice_setting": {
                "voice_id": self.config.voice_id,
                "speed": 1.0,
                "vol": 1.0,
                "pitch": 0
            },
            "audio_setting": {
                "sample_rate": 32000,
                "bitrate": 128000,
                "format": "mp3",
                "channel": 1
            },
            "language": "zh-CN",
            "model": self.config.model
        }

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

        url = f"{self.config.base_url}?GroupId={self.config.group_id}"

        close_session = False
        if session is None:
            session = aiohttp.ClientSession()
            close_session = True

        try:
            async with session.post(url, json=payload, headers=headers, timeout=60) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"TTS API 错误 ({response.status}): {error_text}")

                data = await response.json()

                # 检查响应
                base_resp = data.get("base_resp", {})
                if base_resp.get("status_code") != 0:
                    raise Exception(f"TTS 错误: {base_resp.get('status_msg', '未知错误')}")

                # 获取音频数据
                audio_data = data.get("data", {}).get("audio", "")
                if not audio_data:
                    raise Exception("响应中没有音频数据")

                # 解码并保存音频
                import base64
                audio_bytes = base64.b64decode(audio_data)
                output_path.write_bytes(audio_bytes)

                # 获取时长信息
                duration_ms = data.get("data", {}).get("duration_ms", 0)

                # 获取词语时间戳（如果有）
                word_timestamps = None
                trace_result = data.get("trace_result", {})
                if trace_result:
                    word_timestamps = []
                    for chunk in trace_result.get("text_chunks", []):
                        for word_info in chunk.get("words", []):
                            word_timestamps.append(WordTimestamp(
                                word=word_info.get("word", ""),
                                start_ms=word_info.get("start_ms", 0),
                                end_ms=word_info.get("end_ms", 0)
                            ))

                return TTSResult(
                    audio_path=output_path,
                    duration_ms=duration_ms,
                    word_timestamps=word_timestamps if word_timestamps else None
                )

        finally:
            if close_session:
                await session.close()


async def generate_audio_for_scenes(
    scenes: list,
    output_dir: Path,
    config=None
) -> dict:
    """
    为多个场景生成音频

    Args:
        scenes: 场景列表
        output_dir: 输出目录
        config: TTS配置（可选）

    Returns:
        音频文件信息字典
    """
    tts = MiniMaxTTS(config)
    audio_dir = output_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    audio_files = {}

    async with aiohttp.ClientSession() as session:
        for i, scene in enumerate(scenes, 1):
            print(f"  [{i}/{len(scenes)}] {scene.id}: {scene.text[:30]}...")

            output_path = audio_dir / f"{scene.id}.mp3"

            try:
                result = await tts.synthesize(scene.text, output_path, session=session)
                audio_files[scene.id] = {
                    "path": f"audio/{scene.id}.mp3",
                    "duration_ms": result.duration_ms,
                    "word_timestamps": [
                        {"word": w.word, "start_ms": w.start_ms, "end_ms": w.end_ms}
                        for w in result.word_timestamps
                    ] if result.word_timestamps else None
                }
                print(f"      ✓ 时长: {result.duration_ms}ms")
            except Exception as e:
                print(f"      ✗ 失败: {e}")
                # 创建空的音频信息
                audio_files[scene.id] = {
                    "path": f"audio/{scene.id}.mp3",
                    "duration_ms": scene.duration * 1000,  # 使用预设时长
                    "word_timestamps": None
                }

    return {
        "files": audio_files,
        "total_duration_ms": sum(a["duration_ms"] for a in audio_files.values())
    }


if __name__ == "__main__":
    # 测试 TTS
    async def test():
        print("测试 MiniMax TTS...")
        tts = MiniMaxTTS()

        test_text = "你好，这是一个测试语音。"
        output_path = Path("test_tts.mp3")

        result = await tts.synthesize(test_text, output_path)
        print(f"✓ 音频已生成: {result.audio_path}")
        print(f"  时长: {result.duration_ms}ms")

    asyncio.run(test())
