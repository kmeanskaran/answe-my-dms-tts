# DIFF

## HLD.md
```diff
--- v1/HLD.md
+++ current/HLD.md
@@ -2,12 +2,12 @@
 
 ## Overview
 - Project: `desysflow-oss`
-- Version: `v1`
+- Version: `v2`
 - Role: `Platform Engineer`
-- Preferred language: `python`
+- Preferred language: `Python`
 - Cloud target: `aws`
 
-Answer‑My‑DMS‑TTS is a serverless‑first, multi‑service platform that receives user queries, generates DM replies using LLMs, synthesizes speech in real‑time, and serves audio via CDN. It supports ~10k DAU with <200 ms p95 latency, scaling across AWS services.
+Answer‑My‑DMS‑TTS is a serverless‑first AWS platform that receives user queries, generates DM replies via an LLM, synthesizes speech in real‑time, and serves audio through CloudFront. It supports ~10k DAU with <200 ms p95 latency and scales across Lambda, ECS Fargate, and managed services.
 
 ### Project Overview
 - project-name: `desysflow-oss`
@@ -15,14 +15,14 @@
 - outcome: a high-level architecture baseline for the current working directory
 
 ## Architecture Summary
-- Gateway layer: API Gateway.
-- Service layer: Auth Service, DM Reply Service, Knowledge Base Service, TTS Service and more.
-- Database layer: PostgreSQL, DynamoDB, OpenSearch.
-- Cache layer: Redis Cache.
+- Gateway layer: API Gateway, IAM & KMS.
+- Service layer: Auth Lambda, Knowledge Base Service, DM Reply Service, LLM Inference Container and more.
+- Database layer: DynamoDB, RDS PostgreSQL.
+- Cache layer: ElastiCache Redis.
 - Queue layer: SQS Queue.
-- Storage layer: S3.
-- Monitoring layer: Monitoring Agent.
-- Cdn layer: CloudFront.
+- Storage layer: Audio Storage.
+- Monitoring layer: CloudWatch & X‑Ray.
+- Cdn layer: CDN Delivery.
 
 ## Scope and Assumptions
 ### Scope
@@ -36,25 +36,20 @@
 ## Components
 | Component | Type | Responsibility |
 | --- | --- | --- |
-| API Gateway | gateway | Front‑door, request routing, rate limiting, API key rotation |
-| Auth Service | service | JWT validation, IAM role assignment, audit logging |
-| DM Reply Service | service | LLM inference, context enrichment, async queueing |
-| Knowledge Base Service | service | OpenSearch queries, KB indexing, cache warm‑up |
-| TTS Service | service | GPU‑accelerated speech synthesis, audio storage |
-| Model Serving | service | SageMaker endpoint for LLM inference, versioning |
-| Training Pipeline | service | Data prep, fine‑tuning, job orchestration |
-| Experiment Tracker | service | MLflow tracking, metrics storage |
-| Batch Inference Engine | service | Scheduled inference jobs, cost‑optimized GPU usage |
-| Knowledge Base Indexer | service | ETL from S3 to OpenSearch, incremental updates |
-| Monitoring Agent | monitoring | Prometheus exporter, CloudWatch metrics, alerts |
-| PostgreSQL | database | Transactional data, user profiles, audit logs |
-| DynamoDB | database | Session state, short‑lived tokens, auto‑scaling |
-| OpenSearch | database | Full‑text KB search, low‑latency retrieval |
-| Redis Cache | cache | LRU caching for KB hits, session cache |
-| SQS Queue | queue | Decouple DM reply and TTS requests, back‑pressure |
-| S3 | storage | Audio blob storage, immutable backups |
-| CloudFront | cdn | Global CDN for audio, edge caching, TLS termination |
-| Secrets Manager | service | Secure storage of API keys, model creds |
+| API Gateway | gateway | Front‑end entry point, auth, throttling, request routing |
+| Auth Lambda | service | JWT validation, user context injection |
+| Knowledge Base Service | service | CRUD on KB metadata in DynamoDB, cache in ElastiCache |
+| DM Reply Service | service | Orchestrates LLM inference via Step Functions, stores context in Redis |
+| LLM Inference Container | service | Runs OpenAI‑compatible model on ECS Fargate, provisioned concurrency |
+| TTS Service | service | Synthesizes speech on ECS Fargate, queues via SQS |
+| Audio Storage | storage | S3 bucket with SSE‑S3, lifecycle to S3 Glacier |
+| CDN Delivery | cdn | CloudFront distribution caching audio, edge routing |
+| ElastiCache Redis | cache | Fast context lookup, LLM cache, TTL enforcement |
+| DynamoDB | database | KB metadata, audit logs, event store |
+| RDS PostgreSQL | database | Relational data for user profiles, audit, encrypted at rest |
+| SQS Queue | queue | Decouples TTS job submission, ensures durability |
+| CloudWatch & X‑Ray | monitoring | Observability, cold‑start metrics, cost alerts |
+| IAM & KMS | gateway | Least‑privilege roles, encryption keys for all services |
 
 ## Observed Codebase
 - Files scanned for symbols: 10
@@ -69,19 +64,16 @@
   - `src/answer_my_dms_tts/prompts.py` (python) | functions=build_system_prompt
 
 ## Data Flow
-- Step 1: User sends HTTPS request to API Gateway.
-- Step 2: API Gateway authenticates via Auth Service and applies rate limits.
-- Step 3: Auth Service validates JWT, assigns IAM role, logs audit.
-- Step 4: Request routed to DM Reply Service; DM Reply Service pulls context from Knowledge Base Service via OpenSearch.
-- Step 5: DM Reply Service sends inference request to Model Serving; receives reply text.
-- Step 6: DM Reply Service enqueues TTS job to SQS.
-- Step 7: TTS Service polls SQS, synthesizes speech on GPU cluster, stores audio in S3.
-- Step 8: S3 triggers CloudFront invalidation; audio served to user via CDN.
-- Step 9: Monitoring Agent streams metrics to CloudWatch; alerts on latency, queue depth, cache hit ratio.
+- Step 1: User sends HTTP request to API Gateway.
+- Step 2: API Gateway authenticates via Auth Lambda and forwards to DM Reply Service.
+- Step 3: DM Reply Service triggers Step Functions to invoke LLM Inference Container.
+- Step 4: LLM returns text, which DM Reply Service passes to TTS Service via SQS.
+- Step 5: TTS Service synthesizes audio, stores file in S3, publishes URL to CloudFront.
+- Step 6: API Gateway returns JSON with audio URL to the user.
 
 ## Scaling and Availability
-- Scaling strategy: API Gateway + Lambda for stateless endpoints auto‑scales to 10k req/s. DM Reply and TTS run on ECS Fargate GPU clusters with target tracking on CPU/GPU utilization. SQS queue depth triggers additional Fargate tasks. OpenSearch scales via shard re‑allocation; DynamoDB auto‑scales on read/write units. Redis cluster uses cluster mode with 3 shards, auto‑scaling memory. CloudFront edge caching reduces origin load. Budget caps enforced via AWS Budgets and cost‑explorer alerts.
-- Availability and DR: All services deployed in 3 AZs. RDS PostgreSQL uses Multi‑AZ with automated backups; OpenSearch has cross‑AZ replicas. ECS tasks use service‑level health checks and auto‑replacement. SQS and Redis clusters have failover. CloudFront provides edge failover. Disaster recovery: weekly S3 snapshots, cross‑region replication, and a 30‑day RDS point‑in‑time restore. SLA 99.95% with automated failover and manual rollback procedures.
+- Scaling strategy: Stateless Lambdas use provisioned concurrency for auth and KB CRUD; LLM and TTS run on ECS Fargate with target‑tracking autoscaling and spot pools; ElastiCache Redis cluster with read replicas; RDS PostgreSQL multi‑AZ with read replicas; SQS queues buffer spikes; CloudFront caches globally; CloudWatch alarms trigger scaling and cost alerts.
+- Availability and DR: Multi‑AZ RDS, ElastiCache with failover, SQS durable, API Gateway regional, Lambda concurrency limits, Step Functions stateful checkpoints, CloudFront edge caching, automated backups, IAM least‑privilege, KMS‑encrypted storage, 99.9% SLA with automated failover and health checks.
 - Failure isolation: Services are expected to fail independently with retries, timeout guards, and graceful degradation.
 - Recovery target guidance: Use rolling deploys and automated rollback triggers to reduce blast radius.
 
@@ -90,30 +82,29 @@
 - Traffic expectation: 10k DAU
 - Consistency model: eventual
 - Budget constraint: moderate
-- Growth projection: 2x in 12 months
+- Growth projection: 3x in 12 months
 - Reliability objective: high availability with graceful degradation on downstream failures.
 - Security baseline: least privilege, encrypted transport, and auditable operational controls.
 
 ## Trade-offs
-- Using managed services (Lambda, Fargate, RDS) reduces ops but limits custom GPU scheduling.
-- GPU‑based TTS offers <200 ms latency but incurs higher cost; mitigated by spot instances and budget caps.
-- OpenSearch provides fast KB search but requires cluster management; alternative DynamoDB would reduce cost but increase latency.
-- SQS decoupling adds latency but improves resilience and allows back‑pressure.
-- Redis LRU cache reduces DB load but introduces cache miss penalty; monitored via hit ratio.
-- CloudFront CDN adds extra cost but dramatically lowers origin load and egress charges.
-- Secrets Manager centralizes secrets but adds IAM complexity; least‑privilege roles are enforced.
+- Lambda for lightweight ops vs ECS for heavy LLM to avoid concurrency limits.
+- Provisioned concurrency adds cost but guarantees <200 ms latency.
+- SQS decoupling adds latency but improves resilience.
+- ElastiCache reduces DB load at memory cost.
+- Step Functions adds orchestration overhead but simplifies error handling.
+- S3 + CloudFront trade off storage cost for global low‑latency delivery.
 
 ## Capacity Estimates
-- requests_per_second: 400
-- storage: 2 TB
-- bandwidth: 5 GB/s
+- requests_per_second: 20
+- storage: 50GB
+- bandwidth: 600GB/month
 
 ## Prompt Context
 - Input request:
 ```text
 Role: Platform Engineer
 Project: answe-my-dms-tts
-Preferred implementation language: python
+Preferred implementation language: Python
 Cloud target: aws
 Design style: balanced
 Reference paths: main.py, pyproject.toml, README.md
@@ -129,6 +120,108 @@
   - `src/answer_my_dms_tts/main.py` (python) | functions=on_start, run
   - `src/answer_my_dms_tts/prompts.py` (python) | functions=build_system_prompt
 Design request: Create a production-grade architecture for the current codebase, including API boundaries, data flow, scaling, availability, and security.
+Existing desysflow baseline: version v1 at /Users/karan/Documents/machine-learning/answe-my-dms-tts/desysflow/answe-my-dms-tts/v1
+Baseline files loaded: SUMMARY.md, HLD.md, LLD.md, TECHNICAL_REPORT.md, NON_TECHNICAL_DOC.md
+Baseline excerpt from SUMMARY.md:
+# SUMMARY
+
+- Command: `design`
+- Effective mode: `fresh`
+- Project: `answe-my-dms-tts`
+- Version: `v1`
+- Output: `/Users/karan/Documents/machine-learning/answe-my-dms-tts/desysflow/answe-my-dms-tts/v1`
+- Language: `python`
+- Style: `balanced`
+- Cloud: `aws`
+- Web search: `auto` -> `enabled`
+- Parallel sub-agents: `enabled`
+- Internal reviewer loop: `enabled`
+
+Generated files:
+- `HLD.md`
+- `LLD.md`
+- `TECHNICAL_REPORT.md`
+- `NON_TECHNICAL_DOC.md`
+- `diagram.mmd`
+- `TREE.md`
+- `METADATA.json`
+- `CHANGELOG.md`
+- `DIFF.md`
+Baseline excerpt from HLD.md:
+# HLD
+
+## Overview
+- Project: `desysflow-oss`
+- Version: `v1`
+- Role: `Platform Engineer`
+- Preferred language: `python`
+- Cloud target: `aws`
+
+Answer‑My‑DMS‑TTS is a serverless‑first, multi‑service platform that receives user queries, generates DM replies using LLMs, synthesizes speech in real‑time, and serves audio via CDN. It supports ~10k DAU with <200 ms p95 latency, scaling across AWS services.
+
+### Project Overview
+- project-name: `desysflow-oss`
+- design-package: `answe-my-dms-tts`
+- outcome: a high-level architecture baseline for the current working directory
+
+## Architecture Summary
+- Gateway layer: API Gateway.
+- Service layer: Auth Service, DM Reply Service, Knowledge Base Service, TTS Service and more.
+- Database layer: PostgreSQL, DynamoDB, OpenSearch.
+- Cache layer: Redis Cache.
+- Queue layer: SQS Queue.
+- Storage layer: S3.
+- Monitoring layer: Monitoring Agent.
+- Cdn laye...
+Baseline excerpt from LLD.md:
+# LLD
+
+## Implementation Scope
+- Translate architecture into APIs, schemas, communication contracts, and operations controls.
+- Provide implementation guidance while keeping interfaces and failure behavior explicit.
+- Keep behavior deterministic across environments: local, staging, and production.
+
+## Design Quality Notes
+- Preferred language: python
+- Latency requirement: <200ms p95
+- Traffic estimate: 10k DAU
+- Interfaces should stay explicit, testable, and version-safe across service boundaries.
+- Data access paths should prefer clear ownership over implicit cross-service coupling.
+
+## Observed Codebase
+- Files scanned for symbols: 10
+- Files with extracted symbols: 7
+- Representative symbol-bearing files:
+  - `src/answer_my_dms_tts/kb_manager.py` (python) | classes=KBError | functions=_base_url, _headers, list_knowledge_bases, create_knowledge_base, get_knowledge_base
+  - `src/answer...
+Baseline excerpt from TECHNICAL_REPORT.md:
+# TECHNICAL REPORT
+
+## Executive Summary
+Prompt-driven workflow executed for role `Platform Engineer` and produced architecture artifacts for version `v1`.
+
+## Document Control
+- Project: `answe-my-dms-tts`
+- Version: `v1`
+- Role: `Platform Engineer`
+- Style: `balanced`
+- Cloud target: `aws`
+
+## Sub-agent Topology
+- Extractor -> template selector -> architecture generator -> edge-case injector -> primary selector.
+- Diagram pipeline -> quality refinement.
+- Report generator -> cloud infrastructure mapping.
+
+## Parallel Execution Plan
+- Repository context build runs in parallel (inventory, stack, modules, references).
+- Document packaging runs in parallel where possible for markdown outputs.
+
```

## LLD.md
```diff
--- v1/LLD.md
+++ current/LLD.md
@@ -6,7 +6,7 @@
 - Keep behavior deterministic across environments: local, staging, and production.
 
 ## Design Quality Notes
-- Preferred language: python
+- Preferred language: Python
 - Latency requirement: <200ms p95
 - Traffic estimate: 10k DAU
 - Interfaces should stay explicit, testable, and version-safe across service boundaries.
@@ -27,35 +27,23 @@
 ## APIs
 | Method | Path | Purpose | Request | Response |
 | --- | --- | --- | --- | --- |
-| POST | /api/v1/auth/login | Authenticate user, return JWT and refresh token | {"username":"string","password":"string"} | {"access_token":"string","refresh_token":"string","expires_in":3600} |
-| POST | /api/v1/auth/refresh | Refresh JWT using refresh token | {"refresh_token":"string"} | {"access_token":"string","expires_in":3600} |
-| POST | /api/v1/tts/synthesize | Queue TTS job, return job_id | {"text":"string","voice":"string","lang":"string"} | {"job_id":"string","status":"queued"} |
-| GET | /api/v1/tts/status/{job_id} | Get TTS job status and audio URL if completed | {} | {"job_id":"string","status":"completed","audio_url":"string"} |
-| GET | /api/v1/kb/list | List all knowledge bases for user | {} | {"knowledge_bases":[{"id":"string","name":"string"}]} |
-| POST | /api/v1/kb/create | Create new knowledge base | {"name":"string","description":"string"} | {"id":"string","name":"string"} |
-| GET | /api/v1/kb/{id} | Get knowledge base metadata | {} | {"id":"string","name":"string","description":"string"} |
-| POST | /api/v1/dm/reply | Generate DM reply, idempotent via Idempotency-Key header | {"conversation_id":"string","message":"string","context":"string"} | {"reply_id":"string","status":"queued"} |
-| GET | /api/v1/dm/reply/{reply_id} | Get DM reply status and content | {} | {"reply_id":"string","status":"completed","reply_text":"string"} |
+| POST | /api/v1/requests | Accepts new requests into API Gateway. | {'payload': 'object', 'metadata': 'object'} | {'request_id': 'string', 'status': 'accepted'} |
+| GET | /api/v1/requests/{id} | Fetches request status and result metadata. | {} | {'request_id': 'string', 'status': 'string', 'result': 'object'} |
 
 ## Schemas
 | Schema | Type | Tables / Collections |
 | --- | --- | --- |
-| PostgreSQL | PostgreSQL | {'name': 'users', 'fields': ['id', 'username', 'email', 'hashed_password', 'created_at']}, {'name': 'api_keys', 'fields': ['id', 'user_id', 'key', 'expires_at', 'rotated_at']}, {'name': 'knowledge_bases', 'fields': ['id', 'user_id', 'name', 'description', 'created_at']}, {'name': 'tts_jobs', 'fields': ['id', 'user_id', 'text', 'voice', 'lang', 'status', 'audio_s3_key', 'created_at', 'updated_at']}, {'name': 'dm_replies', 'fields': ['id', 'conversation_id', 'message', 'context', 'reply_text', 'status', 'created_at', 'updated_at']} |
-| Redis | Redis | {'name': 'kb_search_cache', 'fields': ['query_hash', 'results', 'ttl']}, {'name': 'tts_job_status', 'fields': ['job_id', 'status', 'audio_url', 'ttl']} |
-| S3 | S3 | {'name': 'audio_files', 'fields': ['s3_key', 'metadata', 'created_at']} |
+| RDS PostgreSQL (encryption at rest, read replicas) | RDS PostgreSQL (encryption at rest, read replicas) | {'name': 'requests', 'fields': ['id', 'status', 'payload', 'created_at', 'updated_at']}, {'name': 'audit_events', 'fields': ['id', 'request_id', 'event_type', 'created_at']} |
 
 ## Service Communication
-- API Gateway -> Auth Service via REST: JWT issuance and validation
-- Auth Service -> PostgreSQL via PostgreSQL: User & key lookup
-- API Gateway -> TTS Service via REST: Synthesize request
-- TTS Service -> TTS Worker via gRPC: Execute synthesis on GPU
-- TTS Worker -> S3 via S3 API: Store audio file
-- API Gateway -> DM Reply Service via REST: Generate reply request
-- DM Reply Service -> DM Worker via gRPC: Generate reply using model
-- DM Worker -> Knowledge Base Service via REST: Fetch KB context
+- API Gateway -> API Gateway via REST: Synchronous request routing and validation.
+- API Gateway -> Redis Cluster (global cache, no local LRU) via Redis: Read-through and write-through cache operations.
+- API Gateway -> RDS PostgreSQL (encryption at rest, read replicas) via SQL: Transactional persistence for system state.
+- API Gateway -> Kafka Cluster (3 brokers, partitioned topics, auto‑scaling storage) via Async: Publishes background work for deferred processing.
+- Kafka Cluster (3 brokers, partitioned topics, auto‑scaling storage) -> Auth Service via Queue Consumer: Processes asynchronous jobs and retries.
 
 ## Caching
-- Layer=API Gateway, tech=Redis (LRU eviction policy), ttl=300s, invalidation=Invalidate on write and on workflow completion.
+- Layer=API Gateway, tech=Redis Cluster (global cache, no local LRU), ttl=300s, invalidation=Invalidate on write and on workflow completion.
 
 ## Error Handling
 - Scenario=Downstream timeout: strategy=Retry with exponential backoff and bounded timeout budgets; fallback=Return a retriable error and emit an operational alert
```

## TECHNICAL_REPORT.md
```diff
--- v1/TECHNICAL_REPORT.md
+++ current/TECHNICAL_REPORT.md
@@ -1,11 +1,11 @@
 # TECHNICAL REPORT
 
 ## Executive Summary
-Prompt-driven workflow executed for role `Platform Engineer` and produced architecture artifacts for version `v1`.
+Prompt-driven workflow executed for role `Platform Engineer` and produced architecture artifacts for version `v2`.
 
 ## Document Control
 - Project: `answe-my-dms-tts`
-- Version: `v1`
+- Version: `v2`
 - Role: `Platform Engineer`
 - Style: `balanced`
 - Cloud target: `aws`
@@ -49,14 +49,14 @@
 - consistency_requirement: eventual
 - budget_constraint: moderate
 - region: us-east-1
-- scale_growth_projection: 2x in 12 months
-- critical_features: ['real-time TTS synthesis', 'knowledge base retrieval', 'DM reply generation', 'secure API endpoints', 'scalable architecture', 'high availability']
+- scale_growth_projection: 3x in 12 months
+- critical_features: ['API Gateway integration', 'DM reply generation via LLM', 'Real-time TTS synthesis', 'CDN audio delivery', 'Knowledge base CRUD', 'Authentication & authorization', 'Monitoring & observability', 'Scalable serverless architecture', 'High availability and fault tolerance']
 
 ## Architecture Signals
-- HLD components generated: 19
-- LLD API endpoints generated: 9
-- Cloud target: `aws`
-- Language target: `python`
+- HLD components generated: 14
+- LLD API endpoints generated: 2
+- Cloud target: `aws`
+- Language target: `Python`
 
 ## Quality and Risks
 - Primary quality focus: maintainability, reliability, and observability.
@@ -67,7 +67,7 @@
 ```text
 Role: Platform Engineer
 Project: answe-my-dms-tts
-Preferred implementation language: python
+Preferred implementation language: Python
 Cloud target: aws
 Design style: balanced
 Reference paths: main.py, pyproject.toml, README.md
@@ -83,14 +83,116 @@
   - `src/answer_my_dms_tts/main.py` (python) | functions=on_start, run
   - `src/answer_my_dms_tts/prompts.py` (python) | functions=build_system_prompt
 Design request: Create a production-grade architecture for the current codebase, including API boundaries, data flow, scaling, availability, and security.
+Existing desysflow baseline: version v1 at /Users/karan/Documents/machine-learning/answe-my-dms-tts/desysflow/answe-my-dms-tts/v1
+Baseline files loaded: SUMMARY.md, HLD.md, LLD.md, TECHNICAL_REPORT.md, NON_TECHNICAL_DOC.md
+Baseline excerpt from SUMMARY.md:
+# SUMMARY
+
+- Command: `design`
+- Effective mode: `fresh`
+- Project: `answe-my-dms-tts`
+- Version: `v1`
+- Output: `/Users/karan/Documents/machine-learning/answe-my-dms-tts/desysflow/answe-my-dms-tts/v1`
+- Language: `python`
+- Style: `balanced`
+- Cloud: `aws`
+- Web search: `auto` -> `enabled`
+- Parallel sub-agents: `enabled`
+- Internal reviewer loop: `enabled`
+
+Generated files:
+- `HLD.md`
+- `LLD.md`
+- `TECHNICAL_REPORT.md`
+- `NON_TECHNICAL_DOC.md`
+- `diagram.mmd`
+- `TREE.md`
+- `METADATA.json`
+- `CHANGELOG.md`
+- `DIFF.md`
+Baseline excerpt from HLD.md:
+# HLD
+
+## Overview
+- Project: `desysflow-oss`
+- Version: `v1`
+- Role: `Platform Engineer`
+- Preferred language: `python`
+- Cloud target: `aws`
+
+Answer‑My‑DMS‑TTS is a serverless‑first, multi‑service platform that receives user queries, generates DM replies using LLMs, synthesizes speech in real‑time, and serves audio via CDN. It supports ~10k DAU with <200 ms p95 latency, scaling across AWS services.
+
+### Project Overview
+- project-name: `desysflow-oss`
+- design-package: `answe-my-dms-tts`
+- outcome: a high-level architecture baseline for the current working directory
+
+## Architecture Summary
+- Gateway layer: API Gateway.
+- Service layer: Auth Service, DM Reply Service, Knowledge Base Service, TTS Service and more.
+- Database layer: PostgreSQL, DynamoDB, OpenSearch.
+- Cache layer: Redis Cache.
+- Queue layer: SQS Queue.
+- Storage layer: S3.
+- Monitoring layer: Monitoring Agent.
+- Cdn laye...
+Baseline excerpt from LLD.md:
+# LLD
+
+## Implementation Scope
+- Translate architecture into APIs, schemas, communication contracts, and operations controls.
+- Provide implementation guidance while keeping interfaces and failure behavior explicit.
+- Keep behavior deterministic across environments: local, staging, and production.
+
+## Design Quality Notes
+- Preferred language: python
+- Latency requirement: <200ms p95
+- Traffic estimate: 10k DAU
+- Interfaces should stay explicit, testable, and version-safe across service boundaries.
+- Data access paths should prefer clear ownership over implicit cross-service coupling.
+
+## Observed Codebase
+- Files scanned for symbols: 10
+- Files with extracted symbols: 7
+- Representative symbol-bearing files:
+  - `src/answer_my_dms_tts/kb_manager.py` (python) | classes=KBError | functions=_base_url, _headers, list_knowledge_bases, create_knowledge_base, get_knowledge_base
+  - `src/answer...
+Baseline excerpt from TECHNICAL_REPORT.md:
+# TECHNICAL REPORT
+
+## Executive Summary
+Prompt-driven workflow executed for role `Platform Engineer` and produced architecture artifacts for version `v1`.
+
+## Document Control
+- Project: `answe-my-dms-tts`
+- Version: `v1`
+- Role: `Platform Engineer`
+- Style: `balanced`
+- Cloud target: `aws`
+
+## Sub-agent Topology
+- Extractor -> template selector -> architecture generator -> edge-case injector -> primary selector.
+- Diagram pipeline -> quality refinement.
+- Report generator -> cloud infrastructure mapping.
+
+## Parallel Execution Plan
+- Repository context build runs in parallel (inventory, stack, modules, references).
+- Document packaging runs in parallel where possible for markdown outputs.
+
+## Internal Reviewer Loop
+- Required-section validation and wording normalization pass.
+- Mermaid prefix/shape validation pass.
+
+## Context Bloat Fixes
+- Representative files capped to `TOP_FILE_LIMI...
 ```
 
 ## External References
-- [AWS Polly Text-To-Speech Service: Configuration, Benefits, Features - GeeksforGeeks](https://www.geeksforgeeks.org/how-to-configure-aws-polly-text-to-speech-service/) - March 24, 2025 -AWS Polly isa cloud-based text-to-speech service that converts written text into realistic speech. By offering a variety of voices in multiple l
-- [Text to speech: AWS Polly. Text-to-Speech (TTS) technology… | by Tejas Gupta | Medium](https://medium.com/@2017tejasgupta/text-to-speech-aws-polly-a0533112a7aa) - January 14, 2023 -Text to speech: AWS Polly Text-to-Speech (TTS) technologyconverts written text into spoken language. This process analyzes text to determine a
-- [Text to Speech with AWS Polly: My Hands-On Implementation Guide | by Sangeethasaravanan | Medium](https://sangeethasaravanan.medium.com/text-to-speech-with-aws-polly-my-hands-on-implementation-guide-a07de731cc7b) - October 9, 2025 -Before anything else, you need an AWS account and valid credentials — specifically the Access Key and Secret Key.
-- [AWS Polly Text to Speech (tts) | liteLLM](https://docs.litellm.ai/docs/providers/aws_polly) - import litellm import os # Option 1: Environment variables (recommended) os.environ["AWS_ACCESS_KEY_ID"] = "your-access-key" os.environ["AWS_SECRET_ACCESS_KEY"]
-- [AWS Marketplace: Speech-to-Text, Text-to-Speech, & Voice Agent API (Self-Hosted in AWS)](https://aws.amazon.com/marketplace/pp/prodview-kpdktvzdiey4s) - Finally, we use a Text-to-Speech (TTS) engine, such as ElevenLabs , to convert the response back into audio and play it for the user. The entire process is buil
+- [FreeTTS: Free OnlineTexttoSpeech, Audio Converter, and More](https://freetts.com/) - SpeechtoText. Transcribe your voice intotextwith high accuracy.FreeTTS is an online audio toolkit that brings togethertexttospeech,speechtotext, vocal remover, 
+- [AI Voice Generator andText-to-SpeechTool -AmazonPolly -AWS](https://aws.amazon.com/polly/) - AmazonPolly offers freetext-to-speechAIservicesfor one year after you sign up - up to a minimum usage threshold. The threshold varies from 100 thousand characte
+- [FreeTexttoSpeechwith Gemini and ChatGPT AI Voices](https://www.naturalreaders.com/online/) - Text-to-speech(TTS) reads aloudtextfromdocuments, PDFs, websites, and books using natural-sounding AI voices.
+- [GitHub - openclaw/openclaw: Your own personal AI assistant.](https://github.com/openclaw/openclaw/) - OpenClaw is a personal AI assistant you run on your own devices. Itanswersyou on the channels you already use. It can speak and listen on macOS/iOS/Android, and
+- [EdgeTexttoSpeechVoice Reader - ChromeWebStore](https://chromewebstore.google.com/detail/edge-text-to-speech-voice/jeenjljjokaobgdbemlplaidbjfliknl) - EdgeTTSReader: High-QualityText-to-SpeechBring your browsing experience to life with EdgeTTSReader, the ultimatetext-to-speech(TTS) extension powered by Microso
 
 ## Future Improvements
 - Add automated architecture quality scoring across reliability, cost, and security dimensions.
```

## NON_TECHNICAL_DOC.md
```diff
--- v1/NON_TECHNICAL_DOC.md
+++ current/NON_TECHNICAL_DOC.md
@@ -1,7 +1,7 @@
 # NON-TECHNICAL DOC
 
 ## Product Summary
-- Answer‑My‑DMS‑TTS is a serverless‑first, multi‑service platform that receives user queries, generates DM replies using LLMs, synthesizes speech in real‑time, and serves audio via CDN. It supports ~10k DAU with <200 ms p95 latency, scaling across AWS services.
+- Answer‑My‑DMS‑TTS is a serverless‑first AWS platform that receives user queries, generates DM replies via an LLM, synthesizes speech in real‑time, and serves audio through CloudFront. It supports ~10k DAU with <200 ms p95 latency and scales across Lambda, ECS Fargate, and managed services.
 
 ## Business Value
 - Provides a local-first workflow for turning product ideas and source code into clear architecture outputs.
```

## SUMMARY.md
```diff
--- v1/SUMMARY.md
+++ current/SUMMARY.md
@@ -1,11 +1,11 @@
 # SUMMARY
 
 - Command: `design`
-- Effective mode: `fresh`
+- Effective mode: `refine`
 - Project: `answe-my-dms-tts`
-- Version: `v1`
-- Output: `/Users/karan/Documents/machine-learning/answe-my-dms-tts/desysflow/answe-my-dms-tts/v1`
-- Language: `python`
+- Version: `v2`
+- Output: `/Users/karan/Documents/machine-learning/answe-my-dms-tts/desysflow/answe-my-dms-tts/v2`
+- Language: `Python`
 - Style: `balanced`
 - Cloud: `aws`
 - Web search: `auto` -> `enabled`
```

## CHANGELOG.md
```diff
--- v1/CHANGELOG.md
+++ current/CHANGELOG.md
@@ -1,9 +1,9 @@
 # CHANGELOG
 
-## v1
+## v2
 - Command: `design`
-- Effective mode: `fresh`
-- Language: `python`
+- Effective mode: `refine`
+- Language: `Python`
 - Focus: `n/a`
 - Report style: `balanced`
 - Cloud target: `aws`
```

## diagram.mmd
```diff
--- v1/diagram.mmd
+++ current/diagram.mmd
@@ -1,20 +1,20 @@
 flowchart TD
-  client[Client]
-  gateway[API Gateway]
-  auth[Secure Auth Service]
-  core[Core Services]
-  datastore[Data Store]
-  cache[Cache]
-  queue[Async Queue]
-  observability[Observability]
-  secrets[Secrets Manager]
-
-  client -->|HTTPS request| gateway
-  gateway -->|auth| auth
-  auth -->|authorized| core
-  core -->|read/write| datastore
-  core -->|cache| cache
-  core -->|publish| queue
-  queue -->|consume| core
-  core -->|metrics| observability
-  auth -->|secrets| secrets
+    n1["Client"]
+    n2["API Gateway"]
+    n3["API Gateway"]
+    n4["Auth Service"]
+    n5["Knowledge Base Service"]
+    n6["LLM Generation Service"]
+    n7["TTS Service"]
+    n8["RDS PostgreSQL (encryption at rest, read replicas)"]
+    n9["Redis Cluster (global cache, no local LRU)"]
+    n10["Kafka Cluster (3 brokers, partitioned topics, auto‑scaling storage)"]
+    n1 -->|request| n2
+    n2 -->|route| n3
+    n2 -->|route| n4
+    n2 -->|route| n5
+    n2 -->|route| n6
+    n2 -->|route| n7
+    n3 -->|read/write| n8
+    n3 -->|cache| n9
+    n3 -->|publish| n10
```
