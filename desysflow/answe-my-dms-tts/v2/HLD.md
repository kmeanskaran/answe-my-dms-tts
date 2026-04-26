# HLD

## Overview
- Project: `desysflow-oss`
- Version: `v2`
- Role: `Platform Engineer`
- Preferred language: `Python`
- Cloud target: `aws`

Answer‑My‑DMS‑TTS is a serverless‑first AWS platform that receives user queries, generates DM replies via an LLM, synthesizes speech in real‑time, and serves audio through CloudFront. It supports ~10k DAU with <200 ms p95 latency and scales across Lambda, ECS Fargate, and managed services.

### Project Overview
- project-name: `desysflow-oss`
- design-package: `answe-my-dms-tts`
- outcome: a high-level architecture baseline for the current working directory

## Architecture Summary
- Gateway layer: API Gateway, IAM & KMS.
- Service layer: Auth Lambda, Knowledge Base Service, DM Reply Service, LLM Inference Container and more.
- Database layer: DynamoDB, RDS PostgreSQL.
- Cache layer: ElastiCache Redis.
- Queue layer: SQS Queue.
- Storage layer: Audio Storage.
- Monitoring layer: CloudWatch & X‑Ray.
- Cdn layer: CDN Delivery.

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
| API Gateway | gateway | Front‑end entry point, auth, throttling, request routing |
| Auth Lambda | service | JWT validation, user context injection |
| Knowledge Base Service | service | CRUD on KB metadata in DynamoDB, cache in ElastiCache |
| DM Reply Service | service | Orchestrates LLM inference via Step Functions, stores context in Redis |
| LLM Inference Container | service | Runs OpenAI‑compatible model on ECS Fargate, provisioned concurrency |
| TTS Service | service | Synthesizes speech on ECS Fargate, queues via SQS |
| Audio Storage | storage | S3 bucket with SSE‑S3, lifecycle to S3 Glacier |
| CDN Delivery | cdn | CloudFront distribution caching audio, edge routing |
| ElastiCache Redis | cache | Fast context lookup, LLM cache, TTL enforcement |
| DynamoDB | database | KB metadata, audit logs, event store |
| RDS PostgreSQL | database | Relational data for user profiles, audit, encrypted at rest |
| SQS Queue | queue | Decouples TTS job submission, ensures durability |
| CloudWatch & X‑Ray | monitoring | Observability, cold‑start metrics, cost alerts |
| IAM & KMS | gateway | Least‑privilege roles, encryption keys for all services |

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
- Step 1: User sends HTTP request to API Gateway.
- Step 2: API Gateway authenticates via Auth Lambda and forwards to DM Reply Service.
- Step 3: DM Reply Service triggers Step Functions to invoke LLM Inference Container.
- Step 4: LLM returns text, which DM Reply Service passes to TTS Service via SQS.
- Step 5: TTS Service synthesizes audio, stores file in S3, publishes URL to CloudFront.
- Step 6: API Gateway returns JSON with audio URL to the user.

## Scaling and Availability
- Scaling strategy: Stateless Lambdas use provisioned concurrency for auth and KB CRUD; LLM and TTS run on ECS Fargate with target‑tracking autoscaling and spot pools; ElastiCache Redis cluster with read replicas; RDS PostgreSQL multi‑AZ with read replicas; SQS queues buffer spikes; CloudFront caches globally; CloudWatch alarms trigger scaling and cost alerts.
- Availability and DR: Multi‑AZ RDS, ElastiCache with failover, SQS durable, API Gateway regional, Lambda concurrency limits, Step Functions stateful checkpoints, CloudFront edge caching, automated backups, IAM least‑privilege, KMS‑encrypted storage, 99.9% SLA with automated failover and health checks.
- Failure isolation: Services are expected to fail independently with retries, timeout guards, and graceful degradation.
- Recovery target guidance: Use rolling deploys and automated rollback triggers to reduce blast radius.

## Non-Functional Requirements
- Latency target: <200ms p95
- Traffic expectation: 10k DAU
- Consistency model: eventual
- Budget constraint: moderate
- Growth projection: 3x in 12 months
- Reliability objective: high availability with graceful degradation on downstream failures.
- Security baseline: least privilege, encrypted transport, and auditable operational controls.

## Trade-offs
- Lambda for lightweight ops vs ECS for heavy LLM to avoid concurrency limits.
- Provisioned concurrency adds cost but guarantees <200 ms latency.
- SQS decoupling adds latency but improves resilience.
- ElastiCache reduces DB load at memory cost.
- Step Functions adds orchestration overhead but simplifies error handling.
- S3 + CloudFront trade off storage cost for global low‑latency delivery.

## Capacity Estimates
- requests_per_second: 20
- storage: 50GB
- bandwidth: 600GB/month

## Prompt Context
- Input request:
```text
Role: Platform Engineer
Project: answe-my-dms-tts
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
Existing desysflow baseline: version v1 at /Users/karan/Documents/machine-learning/answe-my-dms-tts/desysflow/answe-my-dms-tts/v1
Baseline files loaded: SUMMARY.md, HLD.md, LLD.md, TECHNICAL_REPORT.md, NON_TECHNICAL_DOC.md
Baseline excerpt from SUMMARY.md:
# SUMMARY

- Command: `design`
- Effective mode: `fresh`
- Project: `answe-my-dms-tts`
- Version: `v1`
- Output: `/Users/karan/Documents/machine-learning/answe-my-dms-tts/desysflow/answe-my-dms-tts/v1`
- Language: `python`
- Style: `balanced`
- Cloud: `aws`
- Web search: `auto` -> `enabled`
- Parallel sub-agents: `enabled`
- Internal reviewer loop: `enabled`

Generated files:
- `HLD.md`
- `LLD.md`
- `TECHNICAL_REPORT.md`
- `NON_TECHNICAL_DOC.md`
- `diagram.mmd`
- `TREE.md`
- `METADATA.json`
- `CHANGELOG.md`
- `DIFF.md`
Baseline excerpt from HLD.md:
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
- Cdn laye...
Baseline excerpt from LLD.md:
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
  - `src/answer...
Baseline excerpt from TECHNICAL_REPORT.md:
# TECHNICAL REPORT

## Executive Summary
Prompt-driven workflow executed for role `Platform Engineer` and produced architecture artifacts for version `v1`.

## Document Control
- Project: `answe-my-dms-tts`
- Version: `v1`
- Role: `Platform Engineer`
- Style: `balanced`
- Cloud target: `aws`

## Sub-agent Topology
- Extractor -> template selector -> architecture generator -> edge-case injector -> primary selector.
- Diagram pipeline -> quality refinement.
- Report generator -> cloud infrastructure mapping.

## Parallel Execution Plan
- Repository context build runs in parallel (inventory, stack, modules, references).
- Document packaging runs in parallel where possible for markdown outputs.

## Internal Reviewer Loop
- Required-section validation and wording normalization pass.
- Mermaid prefix/shape validation pass.

## Context Bloat Fixes
- Representative files capped to `TOP_FILE_LIMI...
```

## Future Improvements
- Add workload-specific sizing validation against expected growth intervals.
- Add explicit cost/performance option sets per deployment model.
- Add migration runbooks for major architecture transitions.
