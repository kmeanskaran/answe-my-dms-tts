# LLD

## Implementation Scope
- Translate architecture into APIs, schemas, communication contracts, and operations controls.
- Provide implementation guidance while keeping interfaces and failure behavior explicit.
- Keep behavior deterministic across environments: local, staging, and production.

## Design Quality Notes
- Preferred language: Python
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
| POST | /api/v1/requests | Accepts new requests into API Gateway. | {'payload': 'object', 'metadata': 'object'} | {'request_id': 'string', 'status': 'accepted'} |
| GET | /api/v1/requests/{id} | Fetches request status and result metadata. | {} | {'request_id': 'string', 'status': 'string', 'result': 'object'} |

## Schemas
| Schema | Type | Tables / Collections |
| --- | --- | --- |
| RDS PostgreSQL (encryption at rest, read replicas) | RDS PostgreSQL (encryption at rest, read replicas) | {'name': 'requests', 'fields': ['id', 'status', 'payload', 'created_at', 'updated_at']}, {'name': 'audit_events', 'fields': ['id', 'request_id', 'event_type', 'created_at']} |

## Service Communication
- API Gateway -> API Gateway via REST: Synchronous request routing and validation.
- API Gateway -> Redis Cluster (global cache, no local LRU) via Redis: Read-through and write-through cache operations.
- API Gateway -> RDS PostgreSQL (encryption at rest, read replicas) via SQL: Transactional persistence for system state.
- API Gateway -> Kafka Cluster (3 brokers, partitioned topics, auto‑scaling storage) via Async: Publishes background work for deferred processing.
- Kafka Cluster (3 brokers, partitioned topics, auto‑scaling storage) -> Auth Service via Queue Consumer: Processes asynchronous jobs and retries.

## Caching
- Layer=API Gateway, tech=Redis Cluster (global cache, no local LRU), ttl=300s, invalidation=Invalidate on write and on workflow completion.

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
