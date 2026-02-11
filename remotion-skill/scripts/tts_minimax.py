"""
秒懂金融视频生成器 - MiniMax TTS 集成模块
MiniMax Text-to-Speech integration for voice generation
"""

import os
import json
import hashlib
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from config import TTSConfig, OUTPUT_DIR


@dataclass
class TTSResult:
    """Result of TTS generation"""
    audio_path: Path
    duration_ms: int
    text: str
    word_timestamps: Optional[List[Dict[str, Any]]] = None


class MiniMaxTTS:
    """MiniMax TTS API client"""

    BASE_URL = "https://api.minimax.chat/v1/t2a_v2"

    def __init__(self, config: Optional[TTSConfig] = None):
        self.config = config or TTSConfig()
        self._validate_config()

    def _validate_config(self):
        if not self.config.api_key:
            raise ValueError("MINIMAX_API_KEY is required. Set it via environment variable.")
        if not self.config.group_id:
            raise ValueError("MINIMAX_GROUP_ID is required. Set it via environment variable.")

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        content = f"{text}_{self.config.voice_id}_{self.config.speed}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def _is_probably_mp3(self, path: Path) -> bool:
        """
        Best-effort integrity check to avoid reusing corrupted cache files.
        We accept either an ID3 header or an MPEG frame sync (0xFFEx/0xFFFx).
        """
        try:
            head = path.read_bytes()[:4]
        except Exception:
            return False

        if len(head) < 2:
            return False
        if head.startswith(b"ID3"):
            return True
        # Frame sync: 0xFF followed by 0b111xxxxx
        return head[0] == 0xFF and (head[1] & 0xE0) == 0xE0

    async def _download_audio(self, session: aiohttp.ClientSession, url: str) -> bytes:
        for attempt in range(3):
            try:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        raise RuntimeError(f"Failed to download TTS audio: {resp.status} - {await resp.text()}")
                    return await resp.read()
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == 2:
                    raise RuntimeError(f"Failed to download TTS audio after retries: {e}") from e
                await asyncio.sleep(1.0 * (2 ** attempt))

    def _looks_like_hex(self, s: str) -> bool:
        s = s.strip()
        if len(s) < 200:
            return False
        if len(s) % 2 != 0:
            return False
        # Hex-only payloads are used by MiniMax in some cases.
        for ch in s:
            if ch not in "0123456789abcdefABCDEF":
                return False
        return True

    def _decode_audio_bytes(self, audio_field: str) -> bytes:
        import base64

        audio_str = audio_field.strip()
        if "base64," in audio_str:
            audio_str = audio_str.split("base64,", 1)[1].strip()

        # Some MiniMax responses return hex-encoded bytes (e.g. starts with "494433" == "ID3").
        if self._looks_like_hex(audio_str):
            return bytes.fromhex(audio_str)

        # Add padding if omitted.
        padding = (-len(audio_str)) % 4
        if padding:
            audio_str += "=" * padding

        return base64.b64decode(audio_str)

    async def synthesize(
        self,
        text: str,
        output_path: Optional[Path] = None,
        use_cache: bool = True
        ,
        session: Optional[aiohttp.ClientSession] = None
    ) -> TTSResult:
        """
        Synthesize speech from text

        Args:
            text: Text to convert to speech
            output_path: Optional output path for audio file
            use_cache: Whether to use cached audio if available

        Returns:
            TTSResult with audio path and metadata
        """
        # Generate output path if not provided
        if output_path is None:
            cache_key = self._get_cache_key(text)
            output_path = OUTPUT_DIR / "audio" / f"{cache_key}.mp3"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Check cache
        if use_cache and output_path.exists():
            # Avoid reusing corrupted mp3s (common when API returns URL but we mistakenly base64-decode it).
            if not self._is_probably_mp3(output_path):
                try:
                    output_path.unlink()
                except Exception:
                    pass
            else:
                # Read cached metadata if available
                meta_path = output_path.with_suffix(".json")
                if meta_path.exists():
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    return TTSResult(
                        audio_path=output_path,
                        duration_ms=meta.get("duration_ms", 0),
                        text=text,
                        word_timestamps=meta.get("word_timestamps"),
                    )

                # If metadata is missing but the file seems valid, still reuse it.
                return TTSResult(
                    audio_path=output_path,
                    duration_ms=0,
                    text=text,
                    word_timestamps=None,
                )

        # Make API request
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.config.model,
            "text": text,
            "stream": False,
            "voice_setting": {
                "voice_id": self.config.voice_id,
                "speed": self.config.speed,
                "vol": self.config.volume / 100,
                "pitch": self.config.pitch
            },
            "audio_setting": {
                "sample_rate": self.config.sample_rate,
                "format": "mp3"
            },
            "timber_weights": [
                {"voice_id": self.config.voice_id, "weight": 1}
            ]
        }

        url = f"{self.BASE_URL}?GroupId={self.config.group_id}"

        timeout = aiohttp.ClientTimeout(total=120, connect=30, sock_connect=30, sock_read=120)
        close_session = False
        if session is None:
            session = aiohttp.ClientSession(timeout=timeout)
            close_session = True

        try:
            result = None
            last_err: Optional[Exception] = None
            for attempt in range(3):
                try:
                    async with session.post(url, headers=headers, json=payload) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            raise RuntimeError(f"TTS API error: {response.status} - {error_text}")
                        result = await response.json()
                    break
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    last_err = e
                    if attempt == 2:
                        raise RuntimeError(f"TTS request failed after retries: {e}") from e
                    await asyncio.sleep(1.0 * (2 ** attempt))

            if result is None:
                raise RuntimeError(f"TTS request failed: {last_err}")
        finally:
            if close_session:
                await session.close()

        # Check for API errors
        if result.get("base_resp", {}).get("status_code") != 0:
            error_msg = result.get("base_resp", {}).get("status_msg", "Unknown error")
            raise RuntimeError(f"TTS API error: {error_msg}")

        # Decode and save audio:
        # MiniMax may return either base64 audio bytes or a URL (esp. for longer audios).
        data = result.get("data") or {}
        audio_field = data.get("audio") or data.get("audio_url") or data.get("url")
        if not isinstance(audio_field, str) or not audio_field.strip():
            raise RuntimeError(f"Unexpected TTS response: missing audio field. Keys: {list(data.keys())}")

        audio_field = audio_field.strip()
        if audio_field.startswith("http://") or audio_field.startswith("https://"):
            timeout = aiohttp.ClientTimeout(total=120, connect=30, sock_connect=30, sock_read=120)
            async with aiohttp.ClientSession(timeout=timeout) as dl_sess:
                audio_data = await self._download_audio(dl_sess, audio_field)
        else:
            audio_data = self._decode_audio_bytes(audio_field)

        with open(output_path, "wb") as f:
            f.write(audio_data)

        # Validate and attempt a best-effort conversion if file looks invalid.
        if not self._is_probably_mp3(output_path):
            # If ffmpeg is available, try re-muxing/re-encoding to mp3.
            # This makes the pipeline robust even if API returns a different container/codec.
            import shutil as _shutil
            if _shutil.which("ffmpeg"):
                tmp_in = output_path.with_suffix(".bin")
                tmp_out = output_path.with_suffix(".fixed.mp3")
                try:
                    tmp_in.write_bytes(audio_data)
                    proc = await asyncio.create_subprocess_exec(
                        "ffmpeg",
                        "-y",
                        "-hide_banner",
                        "-loglevel",
                        "error",
                        "-i",
                        str(tmp_in),
                        "-vn",
                        "-acodec",
                        "libmp3lame",
                        "-ar",
                        str(self.config.sample_rate),
                        str(tmp_out),
                    )
                    rc = await proc.wait()
                    if rc == 0 and tmp_out.exists() and self._is_probably_mp3(tmp_out):
                        tmp_out.replace(output_path)
                    else:
                        raise RuntimeError("ffmpeg conversion did not produce a valid mp3")
                finally:
                    try:
                        tmp_in.unlink(missing_ok=True)
                    except Exception:
                        pass
                    try:
                        tmp_out.unlink(missing_ok=True)
                    except Exception:
                        pass
            if not self._is_probably_mp3(output_path):
                raise RuntimeError(
                    "TTS audio file is not a valid mp3 after decoding. "
                    "Most likely the API returned a URL but was parsed incorrectly, "
                    "or the response audio format differs from the requested one."
                )

        # Extract metadata
        duration_ms = result["extra_info"].get("audio_length", 0)
        word_timestamps = result["extra_info"].get("word_timestamps")

        # Save metadata for caching
        meta_path = output_path.with_suffix(".json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({
                "text": text,
                "text_hash": hashlib.md5(text.encode()).hexdigest(),  # 文本哈希用于验证
                "duration_ms": duration_ms,
                "word_timestamps": word_timestamps,
                "voice_id": self.config.voice_id
            }, f, ensure_ascii=False, indent=2)

        return TTSResult(
            audio_path=output_path,
            duration_ms=duration_ms,
            text=text,
            word_timestamps=word_timestamps
        )

    async def synthesize_scenes(
        self,
        scenes: List[Dict[str, Any]],
        output_dir: Path
    ) -> List[TTSResult]:
        """
        Synthesize audio for multiple scenes

        Args:
            scenes: List of scene dictionaries with 'id' and 'text'
            output_dir: Directory to save audio files

        Returns:
            List of TTSResult objects
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        results = []
        for scene in scenes:
            scene_id = scene["id"]
            text = scene["text"]
            output_path = output_dir / f"{scene_id}.mp3"

            result = await self.synthesize(text, output_path)
            results.append(result)

        return results


async def generate_speech(
    text: str,
    output_path: str,
    config: Optional[TTSConfig] = None
) -> Dict[str, Any]:
    """
    Convenience function to generate speech

    Args:
        text: Text to convert to speech
        output_path: Path to save the audio file
        config: Optional TTS configuration

    Returns:
        Dictionary with audio_path, duration_ms, and word_timestamps
    """
    tts = MiniMaxTTS(config)
    result = await tts.synthesize(text, Path(output_path))

    return {
        "audio_path": str(result.audio_path),
        "duration_ms": result.duration_ms,
        "word_timestamps": result.word_timestamps
    }


def generate_speech_sync(
    text: str,
    output_path: str,
    config: Optional[TTSConfig] = None
) -> Dict[str, Any]:
    """Synchronous wrapper for generate_speech"""
    return asyncio.run(generate_speech(text, output_path, config))


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python3 tts_minimax.py <text> <output_path>")
        sys.exit(1)

    text = sys.argv[1]
    output_path = sys.argv[2]

    print(f"Generating speech for: {text[:50]}...")
    result = generate_speech_sync(text, output_path)
    print(f"Audio saved to: {result['audio_path']}")
    print(f"Duration: {result['duration_ms']}ms")
