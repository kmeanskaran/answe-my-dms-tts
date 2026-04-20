from __future__ import annotations

import os
from typing import Any

import requests
from dotenv import load_dotenv


class KBError(RuntimeError):
    pass


def _base_url() -> str:
    return os.getenv("SMALLEST_ATOMS_BASE_URL", "https://atoms-api.smallest.ai/api/v1").rstrip("/")


def _headers() -> dict[str, str]:
    api_key = os.getenv("SMALLEST_API_KEY", "").strip()
    if not api_key:
        raise KBError("SMALLEST_API_KEY is missing.")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def list_knowledge_bases() -> list[dict[str, Any]]:
    load_dotenv()
    response = requests.get(f"{_base_url()}/knowledgebase", headers=_headers(), timeout=60)
    response.raise_for_status()
    payload = response.json()
    return payload.get("data", [])


def create_knowledge_base(name: str, description: str = "") -> str:
    load_dotenv()
    response = requests.post(
        f"{_base_url()}/knowledgebase",
        headers=_headers(),
        json={"name": name, "description": description},
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    kb_id = payload.get("data")
    if not kb_id:
        raise KBError("Create KB response did not include an ID.")
    return kb_id


def get_knowledge_base(kb_id: str) -> dict[str, Any]:
    load_dotenv()
    response = requests.get(f"{_base_url()}/knowledgebase/{kb_id}", headers=_headers(), timeout=60)
    response.raise_for_status()
    payload = response.json()
    return payload.get("data", {})
