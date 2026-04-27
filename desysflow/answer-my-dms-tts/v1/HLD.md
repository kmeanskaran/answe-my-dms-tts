# HLD

## Overview
- Project: `desysflow-oss`
- Version: `v1`
- Role: `Platform Engineer`
- Preferred language: `Python`
- Cloud target: `aws`

Answer‑My‑DMS‑TTS is a Python microservice platform that generates DM replies and synthesizes speech using a knowledge base. It serves ~100k DAU with <200 ms p99 latency, scaling across AWS managed services.

### Project Overview
- project-name: `desysflow-oss`
- design-package: `answer-my-dms-tts`
- outcome: a high-level architecture baseline for the current working directory

## Architecture Summary
- Gateway layer: API Gateway.
- Service layer: Auth Service, DM Agent Service, Knowledge Base Client, TTS Service.
- Database layer: PostgreSQL RDS.
- Cache layer: Redis Cache.
- Queue layer: SQS Queue.
- Storage layer: S3 Audio Storage.
- Monitoring layer: CloudWatch Monitoring, IAM & KMS.
- Cdn layer: CloudFront CDN.

## Scope and Assumptions
### Scope
- Architecture-level design for service boundaries, data flow, scaling, and reliability.
- Delivery-ready HLD that can be refined into implementation tasks.
### Assumptions
- Current prompt and repository context represent the primary product scope.
- Non-functional targets are derived from extracted requirements when explicit values are missing.
- Cloud and runtime choices can be evolved in follow-up design iterations.

## Components
| Component | Type | Responsibility |
| --- | --- | --- |
| API Gateway | gateway | Ingress, routing, rate limiting, JWT validation |
| Auth Service | service | Validate JWTs, issue tokens, enforce scopes |
| DM Agent Service | service | Generate DM replies using KB context |
| Knowledge Base Client | service | Wrap external KB API calls, retry logic |
| TTS Service | service | Synthesize speech, cache audio, store in S3 |
| Redis Cache | cache | Cache KB data, TTS responses, reduce DB load |
| PostgreSQL RDS | database | Store config, user metadata, logs; read replicas for scaling |
| S3 Audio Storage | storage | Persist generated audio files, encrypted at rest |
| CloudFront CDN | cdn | Deliver audio to clients with low latency, edge caching |
| SQS Queue | queue | Decouple TTS job submission from processing, FIFO for ordering |
| CloudWatch Monitoring | monitoring | Collect metrics, logs, traces; alerting |
| IAM & KMS | monitoring | Fine‑grained permissions, encryption keys, VPC endpoints |

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

## Data Flow
- Step 1: Client sends JWT‑protected request to API Gateway.
- Step 2: API Gateway forwards to Auth Service for token validation.
- Step 3: Auth Service returns success; API Gateway routes to DM Agent Service.
- Step 4: DM Agent Service calls Knowledge Base Client to fetch context.
- Step 5: DM Agent generates reply text and pushes it to SQS.
- Step 6: TTS Service consumes job from SQS, checks Redis for cached audio.
- Step 7: If miss, TTS Service calls external TTS API, stores audio in S3, updates Redis.
- Step 8: TTS Service returns audio URL to DM Agent Service.
- Step 9: DM Agent Service returns reply text + audio URL to API Gateway.
- Step 10: API Gateway sends final response to client.

## Scaling and Availability
- Scaling strategy: ECS Fargate with target‑tracking autoscaling for DM/TTS services; pre‑warm containers to avoid.
- Availability and DR: Multi-instance deployment with health checks, retries, and controlled degradation across critical paths.
- Failure isolation: Services are expected to fail independently with retries, timeout guards, and graceful degradation.
- Recovery target guidance: Use rolling deploys and automated rollback triggers to reduce blast radius.

## Non-Functional Requirements
- Latency target: <200ms p99
- Traffic expectation: 100k DAU
- Consistency model: eventual
- Budget constraint: moderate
- Growth projection: 2x in 12 months
- Reliability objective: high availability with graceful degradation on downstream failures.
- Security baseline: least privilege, encrypted transport, and auditable operational controls.

## Trade-offs
- Asynchronous processing improves resilience and throughput but introduces operational complexity and eventual consistency boundaries.
- Caching reduces latency and database load but requires explicit invalidation discipline.
- Service separation improves ownership and scalability but increases inter-service coordination overhead.
- Training pipeline latency risk: GPU auto-scaling may introduce queue delays, potentially violating model freshness requirements.
- Feature store read latency: PostgreSQL may become a bottleneck under 100k DAU, impacting API latency.
- Model serving cold start: CPU horizontal scaling can cause cold starts, risking >200ms p99 latency.

## Capacity Estimates
- requests_per_second: 100k DAU
- storage: 2x in 12 months
- bandwidth: <200ms p99

## Prompt Context
- Input request:
```text
Role: Platform Engineer
Project: answer-my-dms-tts
Preferred implementation language: Python
Cloud target: aws
Design style: balanced
Reference paths: main.py, pyproject.toml, README.md
Observed codebase structure:
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
Design request: Create a production-grade architecture for the current codebase, including API boundaries, data flow, scaling, availability, and security.
```

## Future Improvements
- Add workload-specific sizing validation against expected growth intervals.
- Add explicit cost/performance option sets per deployment model.
- Add migration runbooks for major architecture transitions.
