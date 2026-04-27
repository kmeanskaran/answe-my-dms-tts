# LLD

## Implementation Scope
- Translate architecture into APIs, schemas, communication contracts, and operations controls.
- Provide implementation guidance while keeping interfaces and failure behavior explicit.
- Keep behavior deterministic across environments: local, staging, and production.

## Design Quality Notes
- Preferred language: Python
- Latency requirement: <200ms p99
- Traffic estimate: 100k DAU
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
| POST | /api/auth/login | Authenticate user and return JWT. | {"email":"string","password":"string"} | {"access_token":"string","refresh_token":"string","expires_in":3600} |
| GET | /api/auth/refresh | Refresh access token. | {} | {"access_token":"string","expires_in":3600} |
| GET | /api/knowledge_bases | List all knowledge bases for user. | {} | [{"id":"uuid","name":"string","created_at":"timestamp"}] |
| POST | /api/knowledge_bases | Create a new knowledge base. | {"name":"string"} | {"id":"uuid","name":"string","created_at":"timestamp"} |
| GET | /api/knowledge_bases/{id} | Get knowledge base details. | {} | {"id":"uuid","name":"string","created_at":"timestamp"} |
| POST | /api/dm/reply | Generate DM reply using KB context. | {"message":"string","kb_id":"uuid"} | {"reply_id":"uuid","reply_text":"string","created_at":"timestamp"} |
| GET | /api/dm/reply/{id} | Retrieve generated DM reply. | {} | {"reply_id":"uuid","reply_text":"string","created_at":"timestamp"} |
| POST | /api/tts/synthesize | Submit text for TTS synthesis. | {"text":"string","voice":"string"} | {"job_id":"uuid","status":"queued"} |
| GET | /api/tts/status/{job_id} | Retrieve TTS job status. | {} | {"status":"string","progress":0} |

## Schemas
| Schema | Type | Tables / Collections |
| --- | --- | --- |
| Apache Cassandra | Apache Cassandra | {'name': 'requests', 'fields': ['id', 'status', 'payload', 'created_at', 'updated_at']}, {'name': 'audit_events', 'fields': ['id', 'request_id', 'event_type', 'created_at']} |

## Service Communication
- API Gateway -> API Gateway via REST: Synchronous request routing and validation.
- API Gateway -> Redis Cluster via Redis: Read-through and write-through cache operations.
- API Gateway -> Apache Cassandra via SQL: Transactional persistence for system state.
- API Gateway -> Apache Kafka via Async: Publishes background work for deferred processing.
- Apache Kafka -> Auth Service via Queue Consumer: Processes asynchronous jobs and retries.

## Caching
- Layer=API Gateway, tech=Redis Cluster, ttl=300s, invalidation=Invalidate on write and on workflow completion.

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
