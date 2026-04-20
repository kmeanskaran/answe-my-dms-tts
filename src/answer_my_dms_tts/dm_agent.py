from __future__ import annotations

import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from smallestai.atoms.agent.clients.openai import OpenAIClient
from smallestai.atoms.agent.nodes import OutputAgentNode

from .config import Settings
from .prompts import build_system_prompt


def _load_kb_context(path: str | None) -> str | None:
    if not path:
        return None
    target = Path(path)
    if not target.exists() or not target.is_file():
        return None
    text = target.read_text(encoding="utf-8").strip()
    return text[:6000] if text else None


class DMReplyAgent(OutputAgentNode):
    def __init__(self, settings: Settings):
        super().__init__(name="dm-reply-agent")

        llm_kwargs: dict[str, object] = {
            "model": settings.llm_model,
            "temperature": 0.3,
            "max_tokens": 220,
        }
        if settings.llm_base_url:
            llm_kwargs["base_url"] = settings.llm_base_url
        if settings.llm_api_key:
            llm_kwargs["api_key"] = settings.llm_api_key

        self.llm = OpenAIClient(**llm_kwargs)

        kb_context = _load_kb_context(settings.kb_context_file)
        if settings.kb_id:
            kb_tag = f"Connected Atoms KB ID: {settings.kb_id}"
            kb_context = f"{kb_tag}\n\n{kb_context}" if kb_context else kb_tag

        self.context.add_message({"role": "system", "content": build_system_prompt(kb_context)})

    async def generate_response(self):
        response = await self.llm.chat(messages=self.context.messages, stream=True)
        async for chunk in response:
            if chunk.content:
                yield chunk.content


async def generate_dm_reply(
    *,
    settings: Settings,
    question: str,
    language_label: str,
    tone: str = "Natural",
) -> str:
    agent = DMReplyAgent(settings)
    agent.context.add_message(
        {
            "role": "user",
            "content": (
                f"Write a DM reply in {language_label}. "
                f"Tone: {tone}. "
                "Keep it concise and ready to send.\n\n"
                f"Incoming DM:\n{question.strip()}"
            ),
        }
    )

    chunks: list[str] = []
    async for chunk in agent.generate_response():
        chunks.append(chunk)

    return "".join(chunks).strip()


def generate_dm_reply_sync(
    *,
    settings: Settings,
    question: str,
    language_label: str,
    tone: str = "Natural",
) -> str:
    # Streamlit can already have an active event loop, so run the async agent call
    # in a separate thread with its own loop.
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            asyncio.run,
            generate_dm_reply(
                settings=settings,
                question=question,
                language_label=language_label,
                tone=tone,
            ),
        )
        return future.result()
