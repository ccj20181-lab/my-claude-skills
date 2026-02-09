#!/usr/bin/env python3
"""
MiniMax Voice Cloning helper.

Workflow (per MiniMax docs):
1) Upload source audio -> file_id (purpose=voice_clone)
2) (Optional) Upload prompt audio -> file_id (purpose=prompt_audio)
3) POST /v1/voice_clone with file_id + voice_id (+ clone_prompt) to create a cloned voice_id

Note: Use only if you have the legal right / explicit consent to clone the provided voice.
"""

import argparse
import asyncio
import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any

import aiohttp


# MiniMax has multiple API domains; which one works depends on your API key.
# In practice, `api.minimaxi.com` and `api.minimax.chat` are common.
MINIMAX_BASE_URL = os.environ.get("MINIMAX_VOICE_CLONE_BASE_URL", "https://api.minimaxi.com").strip() or "https://api.minimaxi.com"


@dataclass
class UploadResult:
    file_id: int
    filename: str
    purpose: str


def _default_voice_id_for_file(path: Path) -> str:
    # Must start with an English letter; allow letters/digits/-/_; not end with -/_
    h = hashlib.md5(str(path).encode("utf-8")).hexdigest()[:10]
    return f"miaodong_{h}"


def _auth_header() -> Dict[str, str]:
    api_key = os.environ.get("MINIMAX_API_KEY", "").strip()
    if not api_key:
        raise ValueError("MINIMAX_API_KEY is required for voice cloning APIs (api.minimax.io).")
    return {"Authorization": f"Bearer {api_key}"}


async def upload_file(
    session: aiohttp.ClientSession,
    path: Path,
    purpose: str,
) -> UploadResult:
    if not path.exists():
        raise FileNotFoundError(str(path))

    url = f"{MINIMAX_BASE_URL}/v1/files/upload"
    data = aiohttp.FormData()
    data.add_field("purpose", purpose)
    # Keep file handle open during request
    f = path.open("rb")
    try:
        data.add_field("file", f, filename=path.name)
        async with session.post(url, headers=_auth_header(), data=data) as resp:
            txt = await resp.text()
            if resp.status != 200:
                raise RuntimeError(f"Upload failed: HTTP {resp.status} - {txt[:300]}")
    finally:
        f.close()

    payload = json.loads(txt)
    base = payload.get("base_resp")
    if base is not None:
        if base.get("status_code") != 0:
            raise RuntimeError(f"Upload failed: {base.get('status_msg') or payload}")

    file_obj = payload.get("file") or {}
    if "file_id" not in file_obj:
        raise RuntimeError(f"Upload failed: unexpected response: {payload}")
    file_id = int(file_obj["file_id"])
    return UploadResult(file_id=file_id, filename=file_obj.get("filename", path.name), purpose=file_obj.get("purpose", purpose))


async def clone_voice(
    session: aiohttp.ClientSession,
    *,
    source_file_id: int,
    voice_id: str,
    model: Optional[str] = None,
    preview_text: Optional[str] = None,
    prompt_audio_file_id: Optional[int] = None,
    prompt_text: Optional[str] = None,
    need_noise_reduction: bool = False,
    need_volume_normalization: bool = False,
) -> Dict[str, Any]:
    url = f"{MINIMAX_BASE_URL}/v1/voice_clone"
    body: Dict[str, Any] = {
        "file_id": source_file_id,
        "voice_id": voice_id,
        "need_noise_reduction": need_noise_reduction,
        "need_volume_normalization": need_volume_normalization,
    }

    if prompt_audio_file_id is not None or prompt_text is not None:
        if prompt_audio_file_id is None or prompt_text is None:
            raise ValueError("clone_prompt requires both prompt_audio_file_id and prompt_text.")
        body["clone_prompt"] = {"prompt_audio": prompt_audio_file_id, "prompt_text": prompt_text}

    if preview_text:
        body["text"] = preview_text
        body["model"] = model or "speech-2.8-hd"
    elif model:
        # Model is required only if preview text is provided, per docs.
        body["model"] = model

    headers = {"Content-Type": "application/json", **_auth_header()}
    async with session.post(url, headers=headers, json=body) as resp:
        txt = await resp.text()
        if resp.status != 200:
            raise RuntimeError(f"Voice clone failed: HTTP {resp.status} - {txt[:300]}")

    payload = json.loads(txt)
    base = payload.get("base_resp") or {}
    if base.get("status_code") != 0:
        raise RuntimeError(f"Voice clone failed: {base.get('status_msg') or payload}")

    return payload


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="MiniMax 音色快速复刻（voice_clone）")
    p.add_argument("--source-audio", required=True, type=Path, help="待复刻音频文件路径（mp3/m4a/wav，10s-5min）")
    p.add_argument("--voice-id", default=None, help="自定义 voice_id（必须以英文字母开头，长度>=8）")
    p.add_argument("--prompt-audio", default=None, type=Path, help="可选：示例音频（<8s）")
    p.add_argument("--prompt-text", default=None, help="可选：示例音频对应文本（与 prompt-audio 配套）")
    p.add_argument("--preview-text", default=None, help="可选：克隆后试听文本（<=1000字符），会返回 demo_audio URL")
    p.add_argument("--preview-model", default="speech-2.8-hd", help="可选：试听模型（默认 speech-2.8-hd）")
    p.add_argument("--quiet", action="store_true", help="少输出")
    return p.parse_args()


async def _run() -> int:
    args = parse_args()

    source_audio: Path = args.source_audio
    voice_id = args.voice_id or _default_voice_id_for_file(source_audio)

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=120)) as session:
        up = await upload_file(session, source_audio, "voice_clone")
        if not args.quiet:
            print(f"uploaded source_audio: file_id={up.file_id} filename={up.filename}")

        prompt_file_id: Optional[int] = None
        if args.prompt_audio:
            pr = await upload_file(session, args.prompt_audio, "prompt_audio")
            prompt_file_id = pr.file_id
            if not args.quiet:
                print(f"uploaded prompt_audio: file_id={pr.file_id} filename={pr.filename}")

        # Try clone. If voice_id already exists, auto-suffix to avoid hard failure.
        attempt = 0
        last_err: Optional[Exception] = None
        while attempt < 3:
            try_voice_id = voice_id if attempt == 0 else f"{voice_id}_{attempt}"
            try:
                payload = await clone_voice(
                    session,
                    source_file_id=up.file_id,
                    voice_id=try_voice_id,
                    model=args.preview_model if args.preview_text else None,
                    preview_text=args.preview_text,
                    prompt_audio_file_id=prompt_file_id,
                    prompt_text=args.prompt_text,
                )
                if not args.quiet:
                    demo_audio = payload.get("demo_audio") or ""
                    print(f"voice_id={try_voice_id}")
                    if demo_audio:
                        print(f"demo_audio={demo_audio}")
                else:
                    print(try_voice_id)
                return 0
            except Exception as e:
                last_err = e
                attempt += 1

        raise RuntimeError(str(last_err) if last_err else "voice clone failed")


def main() -> None:
    raise SystemExit(asyncio.run(_run()))


if __name__ == "__main__":
    main()
