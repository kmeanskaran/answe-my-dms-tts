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
| GET | /knowledge_bases | List all knowledge bases | {} | [{id, name, created_at}] |
| POST | /knowledge_bases | Create a new knowledge base | {name, description} | {id, name, description, created_at} |
| GET | /knowledge_bases/{id} | Get knowledge base details | {} | {id, name, description, created_at, documents} |
| POST | /dm/reply | Generate DM reply using KB context | {user_id, dm_text, kb_id} | {reply_text, confidence} |
| POST | /tts/synthesize | Synthesize speech from text | {text, voice} | {audio_url, duration} |

## Schemas
| Schema | Type | Tables / Collections |
| --- | --- | --- |
| knowledge_base_db | PostgreSQL | {'name': 'knowledge_bases', 'fields': ['id', 'name', 'description', 'created_at']}, {'name': 'documents', 'fields': ['id', 'kb_id', 'content', 'metadata', 'created_at']} |
| feature_cache | Redis | {'name': 'kb_context', 'fields': ['kb_id', 'vector', 'timestamp']} |
| audio_storage | S3 | {'name': 'audio_files', 'fields': ['audio_id', 's3_key', 'created_at']} |

## Service Communication
- API Gateway -> DM Agent via REST: DM reply requests
- DM Agent -> KB Manager via REST: KB context fetch
- DM Agent -> TTS Service via REST: Synthesize speech
- DM Agent -> Feature Store via gRPC: Feature vector lookup
- Feature Store -> Redis Cache via Redis: Cache read/write

## Caching
- Layer=Local LRU, tech=Python LRUCache, ttl=300s, invalidation=LRU eviction, TTL refresh on access
- Layer=Redis Cluster, tech=Redis, ttl=600s, invalidation=TTL expiration, manual flush on KB update

## Error Handling
- Scenario=KB fetch timeout: strategy=Retry 3 times with exponential backoff, fallback to default KB; fallback=Return generic reply
- Scenario=TTS synthesis failure: strategy=Retry once, log error, return error message; fallback=Notify user of service outage
- Scenario=Database connection lost: strategy=Circuit breaker, retry after 5s, fallback to cache; fallback=Serve cached KB context if available
- Scenario=Cache miss: strategy=Fetch from DB, populate cache; fallback=Proceed with DB data
- Scenario=Invalid request payload: strategy=Return 400 with validation error; fallback=None

## Deployment
- containerization: Docker
- orchestration: ECS Fargate with Service Auto Scaling
- ci_cd: GitHub Actions: build, test, push, deploy
- environments: ['dev', 'staging', 'prod']

## Security
- TLS 1.3 for all service traffic
- JWT auth for API Gateway
- IAM roles with least privilege per service
- Secrets Manager for API keys and DB creds
- PostgreSQL encryption at rest
- S3 bucket encryption and versioning
- VPC isolation with private subnets
- Network ACLs and security groups
- Rate limiting on API Gateway
- Input validation and sanitization

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
