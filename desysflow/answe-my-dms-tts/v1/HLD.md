# HLD

## Overview
- Project: `desysflow-oss`
- Version: `v1`
- Role: `Platform Engineer`
- Preferred language: `python`
- Cloud target: `aws`

Answer‑My‑DMS‑TTS is a serverless‑first, multi‑service platform that receives user queries, generates DM replies using LLMs, synthesizes speech in real‑time, and serves audio via CDN. It supports ~10k DAU with <200 ms p95 latency, scaling across AWS services.

### Project Overview
- project-name: `desysflow-oss`
- design-package: `answe-my-dms-tts`
- outcome: a high-level architecture baseline for the current working directory

## Architecture Summary
- Gateway layer: API Gateway.
- Service layer: Auth Service, DM Reply Service, Knowledge Base Service, TTS Service and more.
- Database layer: PostgreSQL, DynamoDB, OpenSearch.
- Cache layer: Redis Cache.
- Queue layer: SQS Queue.
- Storage layer: S3.
- Monitoring layer: Monitoring Agent.
- Cdn layer: CloudFront.

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
| API Gateway | gateway | Front‑door, request routing, rate limiting, API key rotation |
| Auth Service | service | JWT validation, IAM role assignment, audit logging |
| DM Reply Service | service | LLM inference, context enrichment, async queueing |
| Knowledge Base Service | service | OpenSearch queries, KB indexing, cache warm‑up |
| TTS Service | service | GPU‑accelerated speech synthesis, audio storage |
| Model Serving | service | SageMaker endpoint for LLM inference, versioning |
| Training Pipeline | service | Data prep, fine‑tuning, job orchestration |
| Experiment Tracker | service | MLflow tracking, metrics storage |
| Batch Inference Engine | service | Scheduled inference jobs, cost‑optimized GPU usage |
| Knowledge Base Indexer | service | ETL from S3 to OpenSearch, incremental updates |
| Monitoring Agent | monitoring | Prometheus exporter, CloudWatch metrics, alerts |
| PostgreSQL | database | Transactional data, user profiles, audit logs |
| DynamoDB | database | Session state, short‑lived tokens, auto‑scaling |
| OpenSearch | database | Full‑text KB search, low‑latency retrieval |
| Redis Cache | cache | LRU caching for KB hits, session cache |
| SQS Queue | queue | Decouple DM reply and TTS requests, back‑pressure |
| S3 | storage | Audio blob storage, immutable backups |
| CloudFront | cdn | Global CDN for audio, edge caching, TLS termination |
| Secrets Manager | service | Secure storage of API keys, model creds |

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
- Step 1: User sends HTTPS request to API Gateway.
- Step 2: API Gateway authenticates via Auth Service and applies rate limits.
- Step 3: Auth Service validates JWT, assigns IAM role, logs audit.
- Step 4: Request routed to DM Reply Service; DM Reply Service pulls context from Knowledge Base Service via OpenSearch.
- Step 5: DM Reply Service sends inference request to Model Serving; receives reply text.
- Step 6: DM Reply Service enqueues TTS job to SQS.
- Step 7: TTS Service polls SQS, synthesizes speech on GPU cluster, stores audio in S3.
- Step 8: S3 triggers CloudFront invalidation; audio served to user via CDN.
- Step 9: Monitoring Agent streams metrics to CloudWatch; alerts on latency, queue depth, cache hit ratio.

## Scaling and Availability
- Scaling strategy: API Gateway + Lambda for stateless endpoints auto‑scales to 10k req/s. DM Reply and TTS run on ECS Fargate GPU clusters with target tracking on CPU/GPU utilization. SQS queue depth triggers additional Fargate tasks. OpenSearch scales via shard re‑allocation; DynamoDB auto‑scales on read/write units. Redis cluster uses cluster mode with 3 shards, auto‑scaling memory. CloudFront edge caching reduces origin load. Budget caps enforced via AWS Budgets and cost‑explorer alerts.
- Availability and DR: All services deployed in 3 AZs. RDS PostgreSQL uses Multi‑AZ with automated backups; OpenSearch has cross‑AZ replicas. ECS tasks use service‑level health checks and auto‑replacement. SQS and Redis clusters have failover. CloudFront provides edge failover. Disaster recovery: weekly S3 snapshots, cross‑region replication, and a 30‑day RDS point‑in‑time restore. SLA 99.95% with automated failover and manual rollback procedures.
- Failure isolation: Services are expected to fail independently with retries, timeout guards, and graceful degradation.
- Recovery target guidance: Use rolling deploys and automated rollback triggers to reduce blast radius.

## Non-Functional Requirements
- Latency target: <200ms p95
- Traffic expectation: 10k DAU
- Consistency model: eventual
- Budget constraint: moderate
- Growth projection: 2x in 12 months
- Reliability objective: high availability with graceful degradation on downstream failures.
- Security baseline: least privilege, encrypted transport, and auditable operational controls.

## Trade-offs
- Using managed services (Lambda, Fargate, RDS) reduces ops but limits custom GPU scheduling.
- GPU‑based TTS offers <200 ms latency but incurs higher cost; mitigated by spot instances and budget caps.
- OpenSearch provides fast KB search but requires cluster management; alternative DynamoDB would reduce cost but increase latency.
- SQS decoupling adds latency but improves resilience and allows back‑pressure.
- Redis LRU cache reduces DB load but introduces cache miss penalty; monitored via hit ratio.
- CloudFront CDN adds extra cost but dramatically lowers origin load and egress charges.
- Secrets Manager centralizes secrets but adds IAM complexity; least‑privilege roles are enforced.

## Capacity Estimates
- requests_per_second: 400
- storage: 2 TB
- bandwidth: 5 GB/s

## Prompt Context
- Input request:
```text
Role: Platform Engineer
Project: answe-my-dms-tts
Preferred implementation language: python
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
