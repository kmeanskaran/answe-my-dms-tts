from __future__ import annotations

import os
from typing import Any

import requests


class AtomsError(RuntimeError):
    pass


def _auth_headers() -> dict[str, str]:
    api_key = os.getenv("SMALLEST_API_KEY", "").strip()
    if not api_key:
        raise AtomsError("SMALLEST_API_KEY is missing. Add it to your environment.")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def atoms_base_url() -> str:
    return os.getenv("SMALLEST_ATOMS_BASE_URL", "https://api.smallest.ai/atoms/v1").rstrip("/")


def build_agent_payload(
    *,
    name: str,
    description: str,
    voice_id: str,
    knowledge_base_id: str | None,
    prompt: str,
    language_code: str = "en",
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "name": name,
        "description": description,
        "workflowType": "single_prompt",
        "language": {
            "enabled": language_code,
            "switching": {
                "isEnabled": True,
                "minWordsForDetection": 2,
                "strongSignalThreshold": 0.7,
                "weakSignalThreshold": 0.3,
                "minConsecutiveForWeakThresholdSwitch": 2,
            },
        },
        "synthesizer": {
            "voiceConfig": {
                "model": os.getenv(
                    "SMALLEST_ATOMS_VOICE_MODEL",
                    "waves_lightning_large_voice_clone",
                ),
                "voiceId": voice_id,
            },
            "speed": float(os.getenv("SMALLEST_SPEED", "0.85")),
            "consistency": float(os.getenv("SMALLEST_ATOMS_CONSISTENCY", "0.5")),
            "similarity": float(os.getenv("SMALLEST_ATOMS_SIMILARITY", "0.5")),
            "enhancement": float(os.getenv("SMALLEST_ATOMS_ENHANCEMENT", "1")),
        },
        "slmModel": os.getenv("SMALLEST_ATOMS_SLM_MODEL", "electron"),
        "globalPrompt": prompt,
        "defaultVariables": {},
    }
    if knowledge_base_id:
        payload["globalKnowledgeBaseId"] = knowledge_base_id
    return payload


def create_knowledge_base(name: str, description: str) -> str:
    try:
        response = requests.post(
            f"{atoms_base_url()}/knowledgebase",
            headers=_auth_headers(),
            json={"name": name, "description": description},
            timeout=60,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise AtomsError("Failed to create Atoms knowledge base.") from exc

    payload = response.json()
    kb_id = payload.get("data")
    if not kb_id:
        raise AtomsError("Atoms knowledge base creation returned no ID.")
    return kb_id


def create_agent(payload: dict[str, Any]) -> str:
    try:
        response = requests.post(
            f"{atoms_base_url()}/agent",
            headers=_auth_headers(),
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise AtomsError("Failed to create Atoms agent.") from exc

    data = response.json()
    agent_id = data.get("data")
    if not agent_id:
        raise AtomsError("Atoms agent creation returned no ID.")
    return agent_id


def _candidate_message_paths(agent_id: str) -> list[str]:
    configured = os.getenv("SMALLEST_ATOMS_MESSAGE_PATH", "").strip()
    if configured:
        return [configured.format(agent_id=agent_id)]

    return [
        f"/agent/{agent_id}/message",
        f"/agent/{agent_id}/chat",
        f"/agents/{agent_id}/message",
        f"/agents/{agent_id}/chat",
    ]


def _extract_text(value: Any) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None

    if isinstance(value, dict):
        for key in (
            "output",
            "response",
            "answer",
            "text",
            "message",
            "content",
            "reply",
        ):
            candidate = _extract_text(value.get(key))
            if candidate:
                return candidate
        for nested in value.values():
            candidate = _extract_text(nested)
            if candidate:
                return candidate
        return None

    if isinstance(value, list):
        for item in value:
            candidate = _extract_text(item)
            if candidate:
                return candidate
        return None

    return None


def generate_dm_reply(
    *,
    agent_id: str,
    question: str,
    language_label: str,
    session_id: str | None = None,
) -> str:
    payload: dict[str, Any] = {
        "message": question,
        "input": question,
        "query": question,
        "sessionId": session_id or os.getenv("SMALLEST_ATOMS_SESSION_ID", "streamlit-dm-demo"),
        "variables": {
            "requested_language": language_label,
            "use_case": "dm_reply_audio",
        },
        "metadata": {
            "channel": "dm",
            "language": language_label,
            "format": "text_for_tts",
        },
    }

    last_error: requests.RequestException | None = None

    for relative_path in _candidate_message_paths(agent_id):
        url = f"{atoms_base_url()}{relative_path}"
        try:
            response = requests.post(
                url,
                headers=_auth_headers(),
                json=payload,
                timeout=90,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            last_error = exc
            continue

        data = response.json()
        text = _extract_text(data)
        if text:
            return text

        raise AtomsError("Atoms agent responded, but no reply text was found in the response.")

    if last_error is not None:
        raise AtomsError(
            "Failed to reach the Atoms agent message endpoint. "
            "Set SMALLEST_ATOMS_MESSAGE_PATH if your workspace uses a different route."
        ) from last_error

    raise AtomsError("Atoms agent message endpoint is not configured.")
