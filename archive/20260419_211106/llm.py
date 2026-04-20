from __future__ import annotations

import os
from pathlib import Path
from typing import TypedDict

import requests

from prompts import SYSTEM_PROMPT, build_user_prompt


class LLMError(RuntimeError):
    pass


class KnowledgeSource(TypedDict):
    name: str
    path: str
    content: str


def load_knowledge_sources(data_dir: str = "data") -> list[KnowledgeSource]:
    base = Path(data_dir)
    if not base.exists():
        return []

    sources: list[KnowledgeSource] = []
    for md_file in sorted(base.glob("*.md")):
        content = md_file.read_text(encoding="utf-8").strip()
        if not content:
            continue
        sources.append(
            {
                "name": md_file.stem,
                "path": str(md_file),
                "content": content,
            }
        )

    return sources


def load_markdown_knowledge(data_dir: str = "data") -> str:
    chunks = [f"# {source['name']}\n{source['content']}" for source in load_knowledge_sources(data_dir)]

    return "\n\n".join(chunks)


def generate_response(question: str, language_label: str, data_dir: str = "data") -> str:
    knowledge_context = load_markdown_knowledge(data_dir=data_dir)

    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "gpt-oss:20b-cloud")
    timeout_s = int(os.getenv("OLLAMA_TIMEOUT", "120"))

    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": build_user_prompt(
                    question=question,
                    language_label=language_label,
                    knowledge_context=knowledge_context,
                ),
            },
        ],
    }

    try:
        response = requests.post(
            f"{base_url.rstrip('/')}/api/chat",
            json=payload,
            timeout=timeout_s,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise LLMError(
            "Failed to reach Ollama. Check if Ollama is running and model is available."
        ) from exc

    data = response.json()
    content = data.get("message", {}).get("content", "").strip()
    if not content:
        raise LLMError("Ollama returned an empty response.")

    return content


def generate_response_with_context(
    question: str,
    language_label: str,
    data_dir: str = "data",
) -> tuple[str, list[KnowledgeSource]]:
    sources = load_knowledge_sources(data_dir=data_dir)
    return generate_response(question=question, language_label=language_label, data_dir=data_dir), sources
