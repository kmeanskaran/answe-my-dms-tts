# LLD

## Implementation Scope
- Translate architecture into APIs, schemas, communication contracts, and operations controls.
- Provide implementation guidance while keeping interfaces and failure behavior explicit.
- Keep behavior deterministic across environments: local, staging, and production.

## Design Quality Notes
- Preferred language: python
- Latency requirement: <200ms p95
- Traffic estimate: 10k DAU
- Interfaces should stay explicit, testable, and version-safe across service boundaries.
- Data access paths should prefer clear ownership over implicit cross-service coupling.

## Observed Codebase
- Files scanned for symbols: 10
- Files with extracted symbols: 7
- Representative symbol-bearing files:
  - `src/answer_my_dms_tts/kb_manager.py` (python) | classes=KBError | functions=_base_url, _headers, list_knowledge_bases, create_knowledge_base, get_knowledge_base
  - `src/answer_my_dms_tts/dm_agent.py` (python) | classes=DMReplyAgent | functions=_load_kb_context, generate_dm_reply, generate_dm_reply_sync | methods=DMReplyAgent[__init__, generate_response]
  - `src/answer_my_dms_tts/config.py` (python) | classes=Settings | functions=_none_if_blank, load_settings
  - `src/answer_my_dms_tts/tts.py` (python) | classes=TTSError | functions=_auth_headers, synthesize_speech
  - `src/answer_my_dms_tts/app.py` (python) | functions=render_speech_button, clean_tts_text, render_app
  - `src/answer_my_dms_tts/main.py` (python) | functions=on_start, run
  - `src/answer_my_dms_tts/prompts.py` (python) | functions=build_system_prompt

## APIs
| Method | Path | Purpose | Request | Response |
| --- | --- | --- | --- | --- |
| POST | /api/v1/auth/login | Authenticate user, return JWT and refresh token | {"username":"string","password":"string"} | {"access_token":"string","refresh_token":"string","expires_in":3600} |
| POST | /api/v1/auth/refresh | Refresh JWT using refresh token | {"refresh_token":"string"} | {"access_token":"string","expires_in":3600} |
| POST | /api/v1/tts/synthesize | Queue TTS job, return job_id | {"text":"string","voice":"string","lang":"string"} | {"job_id":"string","status":"queued"} |
| GET | /api/v1/tts/status/{job_id} | Get TTS job status and audio URL if completed | {} | {"job_id":"string","status":"completed","audio_url":"string"} |
| GET | /api/v1/kb/list | List all knowledge bases for user | {} | {"knowledge_bases":[{"id":"string","name":"string"}]} |
| POST | /api/v1/kb/create | Create new knowledge base | {"name":"string","description":"string"} | {"id":"string","name":"string"} |
| GET | /api/v1/kb/{id} | Get knowledge base metadata | {} | {"id":"string","name":"string","description":"string"} |
| POST | /api/v1/dm/reply | Generate DM reply, idempotent via Idempotency-Key header | {"conversation_id":"string","message":"string","context":"string"} | {"reply_id":"string","status":"queued"} |
| GET | /api/v1/dm/reply/{reply_id} | Get DM reply status and content | {} | {"reply_id":"string","status":"completed","reply_text":"string"} |

## Schemas
| Schema | Type | Tables / Collections |
| --- | --- | --- |
| PostgreSQL | PostgreSQL | {'name': 'users', 'fields': ['id', 'username', 'email', 'hashed_password', 'created_at']}, {'name': 'api_keys', 'fields': ['id', 'user_id', 'key', 'expires_at', 'rotated_at']}, {'name': 'knowledge_bases', 'fields': ['id', 'user_id', 'name', 'description', 'created_at']}, {'name': 'tts_jobs', 'fields': ['id', 'user_id', 'text', 'voice', 'lang', 'status', 'audio_s3_key', 'created_at', 'updated_at']}, {'name': 'dm_replies', 'fields': ['id', 'conversation_id', 'message', 'context', 'reply_text', 'status', 'created_at', 'updated_at']} |
| Redis | Redis | {'name': 'kb_search_cache', 'fields': ['query_hash', 'results', 'ttl']}, {'name': 'tts_job_status', 'fields': ['job_id', 'status', 'audio_url', 'ttl']} |
| S3 | S3 | {'name': 'audio_files', 'fields': ['s3_key', 'metadata', 'created_at']} |

## Service Communication
- API Gateway -> Auth Service via REST: JWT issuance and validation
- Auth Service -> PostgreSQL via PostgreSQL: User & key lookup
- API Gateway -> TTS Service via REST: Synthesize request
- TTS Service -> TTS Worker via gRPC: Execute synthesis on GPU
- TTS Worker -> S3 via S3 API: Store audio file
- API Gateway -> DM Reply Service via REST: Generate reply request
- DM Reply Service -> DM Worker via gRPC: Generate reply using model
- DM Worker -> Knowledge Base Service via REST: Fetch KB context

## Caching
- Layer=API Gateway, tech=Redis (LRU eviction policy), ttl=300s, invalidation=Invalidate on write and on workflow completion.

## Error Handling
- Scenario=Downstream timeout: strategy=Retry with exponential backoff and bounded timeout budgets; fallback=Return a retriable error and emit an operational alert
- Scenario=Queue consumer failure: strategy=Retry with dead-letter routing after threshold breaches; fallback=Preserve the job for manual replay
- Scenario=Database write contention: strategy=Use idempotent writes and short-lived retries; fallback=Fail gracefully with audit logging

## Deployment
- containerization: Docker
- orchestration: Kubernetes
- ci_cd: GitHub Actions
- environments: ['dev', 'staging', 'prod']
- runtime_language: Python

## Security
- TLS for all north-south and east-west traffic
- Authentication and authorization at the edge and service layers
- Secrets managed outside the application runtime
- Structured audit logging for critical state changes

## Testing and Validation
- Contract tests for request/response schemas and compatibility.
- Integration tests for service communication and datastore boundaries.
- Resilience tests for timeout, retry, and fallback behavior.
- Load tests for critical APIs with p95/p99 tracking and alert thresholds.
- Security tests covering authn/authz controls and secret handling pathways.

## Future Improvements
- Add endpoint-by-endpoint SLA and idempotency contracts.
- Add schema migration/rollback playbooks for critical data models.
- Add detailed degradation modes for downstream dependency failures.
