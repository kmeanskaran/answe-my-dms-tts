# Atoms SDK Research Notes (April 19, 2026)

## Primary source URL
- https://atoms-docs.smallest.ai/dev/introduction/overview

## Deep links used
- Core concepts: https://atoms-docs.smallest.ai/dev/introduction/core-concepts/overview
- Agents overview: https://atoms-docs.smallest.ai/dev/build/agents/overview
- LLM settings: https://atoms-docs.smallest.ai/dev/build/agents/agent-configuration/llm-settings
- Bring your own model (Ollama, vLLM, LM Studio): https://atoms-docs.smallest.ai/dev/build/agents/agent-configuration/byom
- Knowledge base overview: https://atoms-docs.smallest.ai/dev/build/knowledge-base/overview
- API create KB: https://atoms-docs.smallest.ai/api-reference/knowledge-base/create-a-knowledge-base
- API list KBs: https://atoms-docs.smallest.ai/api-reference/knowledge-base/get-all-knowledge-bases
- API get KB: https://atoms-docs.smallest.ai/api-reference/knowledge-base/get-a-knowledge-base

## Key points mapped to rewrite

1. Core architecture
- Atoms uses nodes, events, graphs, and sessions.
- Implementation mapping:
  - `DMReplyAgent` (`OutputAgentNode`) in `dm_agent.py`
  - streaming event handling in `generate_response`
  - session lifecycle in `main.py`

2. DM agent pattern
- Agents are implemented as `OutputAgentNode` with real-time streaming.
- Implementation mapping:
  - prompt tuned for DM replies in `prompts.py`
  - `self.llm.chat(..., stream=True)` in `dm_agent.py`

3. External LLM selection
- Docs describe `OpenAIClient` as provider-agnostic via `base_url`.
- Ollama support shown with base URL `http://localhost:11434/v1` and API key placeholder.
- Implementation mapping:
  - `config.py` selects Ollama or any OpenAI-compatible endpoint
  - `dm_agent.py` injects `base_url`/`api_key` when configured

4. Knowledge base
- Docs emphasize KB grounding and `globalKnowledgeBaseId` linkage per agent.
- API reference confirms create/list/get endpoints.
- Implementation mapping:
  - `kb_manager.py` includes create/list/get wrappers
  - `.env` supports `SMALLEST_KB_ID`
  - `knowledge/dm_kb.md` provides local KB seed for immediate grounding

## Practical conclusion
- The rewritten project follows the documented Atoms SDK runtime model for agent execution.
- External LLM portability is implemented through OpenAI-compatible configuration.
- KB setup is supported via API helper + runtime metadata/context seeding.
