from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def estimate_tokens(text: str) -> int:
    stripped = text.strip()
    if not stripped:
        return 0
    return max(1, math.ceil(len(stripped) / 4))


def estimate_costs(question: str, answer: str, audio_bytes: bytes) -> dict[str, float]:
    llm_input_tokens = estimate_tokens(question)
    llm_output_tokens = estimate_tokens(answer)
    audio_chars = len(answer)
    audio_kb = len(audio_bytes) / 1024

    llm_input_rate = float(os.getenv("EST_LLM_INPUT_COST_PER_1K_TOKENS", "0"))
    llm_output_rate = float(os.getenv("EST_LLM_OUTPUT_COST_PER_1K_TOKENS", "0"))
    tts_char_rate = float(os.getenv("EST_TTS_COST_PER_1K_CHARS", "0"))
    audio_delivery_rate = float(os.getenv("EST_AUDIO_COST_PER_MB", "0"))

    llm_input_cost = (llm_input_tokens / 1000) * llm_input_rate
    llm_output_cost = (llm_output_tokens / 1000) * llm_output_rate
    tts_cost = (audio_chars / 1000) * tts_char_rate
    audio_delivery_cost = ((audio_kb / 1024) * audio_delivery_rate)
    total_cost = llm_input_cost + llm_output_cost + tts_cost + audio_delivery_cost

    return {
        "llm_input_tokens": llm_input_tokens,
        "llm_output_tokens": llm_output_tokens,
        "audio_chars": audio_chars,
        "audio_kb": round(audio_kb, 2),
        "llm_input_cost": round(llm_input_cost, 6),
        "llm_output_cost": round(llm_output_cost, 6),
        "tts_cost": round(tts_cost, 6),
        "audio_delivery_cost": round(audio_delivery_cost, 6),
        "total_cost": round(total_cost, 6),
    }


def append_jsonl_log(record: dict[str, Any], log_path: str = "logs/generations.jsonl") -> None:
    target = Path(log_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        **record,
    }
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
