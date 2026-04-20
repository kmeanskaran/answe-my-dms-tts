from __future__ import annotations

import os
from typing import BinaryIO

import requests


class TTSError(RuntimeError):
    pass


def _auth_headers() -> dict[str, str]:
    api_key = os.getenv("SMALLEST_API_KEY", "").strip()
    if not api_key:
        raise TTSError("SMALLEST_API_KEY is missing. Add it to your environment.")
    return {"Authorization": f"Bearer {api_key}"}


def clone_voice(sample_file: BinaryIO, filename: str) -> str:
    metadata = clone_voice_with_metadata(sample_file=sample_file, filename=filename)
    return metadata["voice_id"]


def clone_voice_with_metadata(sample_file: BinaryIO, filename: str) -> dict[str, str]:
    base_url = os.getenv("SMALLEST_BASE_URL", "https://api.smallest.ai").rstrip("/")
    clone_path = os.getenv("SMALLEST_CLONE_PATH", "/voices/clone")
    url = f"{base_url}{clone_path}"
    voice_name = os.getenv("SMALLEST_VOICE_NAME", "karan-clone")

    files = {"file": (filename, sample_file, "audio/wav")}
    data = {"name": voice_name}

    try:
        response = requests.post(
            url,
            headers=_auth_headers(),
            files=files,
            data=data,
            timeout=180,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise TTSError("Voice cloning request failed.") from exc

    payload = response.json()
    voice_id = payload.get("voice_id") or payload.get("id")
    if not voice_id:
        raise TTSError("Voice cloning succeeded but no voice_id was returned.")
    return {
        "voice_id": voice_id,
        "request_url": url,
        "voice_name": voice_name,
        "raw_response": response.text,
    }


def synthesize_speech(
    text: str,
    language_code: str,
    voice_id: str,
    speed: float | None = None,
) -> bytes:
    base_url = os.getenv("SMALLEST_BASE_URL", "https://api.smallest.ai").rstrip("/")
    tts_path = os.getenv("SMALLEST_TTS_PATH", "/waves/v1/lightning-v3.1/get_speech")
    url = f"{base_url}{tts_path}"
    output_format = os.getenv("SMALLEST_OUTPUT_FORMAT", "mp3")

    payload = {
        "text": text,
        "voice_id": voice_id,
        "language": language_code,
        "sample_rate": int(os.getenv("SMALLEST_SAMPLE_RATE", "24000")),
        "output_format": output_format,
        "speed": speed if speed is not None else float(os.getenv("SMALLEST_SPEED", "0.9")),
    }

    try:
        response = requests.post(
            url,
            headers={
                **_auth_headers(),
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=180,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        details = str(exc)
        if isinstance(exc, requests.HTTPError) and exc.response is not None:
            status = exc.response.status_code
            body = exc.response.text.strip().replace("\n", " ")
            details = f"{details} | status={status} | body={body[:500]}"
        raise TTSError(f"TTS request failed: {details}") from exc

    content_type = response.headers.get("Content-Type", "")
    if content_type.startswith("audio/"):
        return response.content

    data = response.json()

    # Supports APIs that return base64 or an audio URL.
    audio_b64 = data.get("audio_base64")
    if audio_b64:
        import base64

        return base64.b64decode(audio_b64)

    audio_url = data.get("audio_url")
    if audio_url:
        try:
            audio_resp = requests.get(audio_url, timeout=120)
            audio_resp.raise_for_status()
            return audio_resp.content
        except requests.RequestException as exc:
            raise TTSError("Failed to download synthesized audio.") from exc

    raise TTSError("TTS succeeded but no audio content was returned.")
