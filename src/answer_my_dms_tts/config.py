from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    llm_model: str
    llm_base_url: str | None
    llm_api_key: str | None
    kb_id: str | None
    kb_context_file: str | None


def _none_if_blank(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def load_settings() -> Settings:
    load_dotenv()

    use_ollama = os.getenv("USE_OLLAMA", "true").strip().lower() in {"1", "true", "yes", "on"}

    if use_ollama:
        return Settings(
            llm_model=os.getenv("OLLAMA_MODEL", "gpt-oss:20b-cloud"),
            llm_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/") + "/v1",
            llm_api_key="ollama",
            kb_id=_none_if_blank(os.getenv("SMALLEST_KB_ID")),
            kb_context_file=_none_if_blank(os.getenv("KB_CONTEXT_FILE")),
        )

    return Settings(
        llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        llm_base_url=_none_if_blank(os.getenv("LLM_BASE_URL")),
        llm_api_key=_none_if_blank(os.getenv("LLM_API_KEY")) or _none_if_blank(os.getenv("OPENAI_API_KEY")),
        kb_id=_none_if_blank(os.getenv("SMALLEST_KB_ID")),
        kb_context_file=_none_if_blank(os.getenv("KB_CONTEXT_FILE")),
    )
