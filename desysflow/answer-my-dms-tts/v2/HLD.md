# HLD

## Overview
- Project: `desysflow-oss`
- Version: `v2`
- Role: `Platform Engineer`
- Preferred language: `Python`
- Cloud target: `aws`

Answer‑My‑DMS‑TTS is a Python microservice platform that generates DM replies, synthesizes speech, and serves a React frontend. It handles ~100k DAU with <200 ms p99 latency, deployed on AWS managed services.

### Project Overview
- project-name: `desysflow-oss`
- design-package: `answer-my-dms-tts`
- outcome: a high-level architecture baseline for the current working directory

## Architecture Summary
- Gateway layer: API Gateway.
- Service layer: Auth Service, DM Reply Service, TTS Service, Knowledge Base Client and more.
- Database layer: PostgreSQL RDS.
- Cache layer: Redis Cache.
- Queue layer: SQS Queue.
- Storage layer: S3 Audio Bucket.
- Monitoring layer: CloudWatch Monitoring.
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
| API Gateway | gateway | Expose REST endpoints, rate limit, auth integration |
| Auth Service | service | JWT issuance, user validation, permission checks |
| DM Reply Service | service | Generate DM replies using knowledge base context |
| TTS Service | service | Synthesize speech, store audio in S3 |
| Knowledge Base Client | service | CRUD operations on external KB API |
| Redis Cache | cache | Cache KB queries and TTS job status |
| SQS Queue | queue | Queue TTS jobs for asynchronous processing |
| PostgreSQL RDS | database | Persist user metadata, DM logs, job records |
| S3 Audio Bucket | storage | Store generated audio files, serve via CDN |
| CloudFront CDN | cdn | Cache static assets and audio, reduce latency |
| CloudWatch Monitoring | monitoring | Collect metrics, logs, alarms for all services |
| React Frontend | service | UI for DM reply and TTS playback, served from CloudFront |

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
- Step 1: User hits React app, requests DM reply via API Gateway.
- Step 2: API Gateway authenticates via Auth Service, forwards to DM Reply Service.
- Step 3: DM Reply Service fetches KB context from Knowledge Base Client, caches in Redis.
- Step 4: DM Reply Service returns text reply to frontend.
- Step 5: Frontend requests TTS synthesis; API Gateway forwards to TTS Service.
- Step 6: TTS Service queues job in SQS, returns job ID.
- Step 7: Background worker consumes SQS, calls external TTS API, stores audio in S3.
- Step 8: Worker updates job status in Redis and PostgreSQL.
- Step 9: Frontend polls or receives webhook, retrieves audio URL from S3 via CloudFront.
- Step 10: User plays audio; CDN serves cached content.

## Scaling and Availability
- Scaling strategy: Horizontal auto‑scaling via ECS/Fargate with target‑tracking on CPU/latency. Redis cluster scales via node addition. SQS scales automatically. PostgreSQL uses read replicas. CloudFront caches globally. S3 is inherently scalable.
- Availability and DR: 99.99% SLA achieved with multi‑AZ RDS, ECS service replicas, S3, CloudFront, and SQS. Disaster recovery via automated cross‑region S3 replication, RDS snapshots, and failover to secondary region within 15 minutes.
- Failure isolation: Services are expected to fail independently with retries, timeout guards, and graceful degradation.
- Recovery target guidance: Use rolling deploys and automated rollback triggers to reduce blast radius.

## Non-Functional Requirements
- Latency target: <200ms p99
- Traffic expectation: 100k DAU
- Consistency model: eventual
- Budget constraint: moderate
- Growth projection: 3x in 12 months
- Reliability objective: high availability with graceful degradation on downstream failures.
- Security baseline: least privilege, encrypted transport, and auditable operational controls.

## Trade-offs
- Managed services chosen for rapid ops and cost control, sacrificing fine‑grained tuning.
- Eventual consistency in Redis and SQS reduces latency but may delay job status updates.
- S3 + CloudFront for audio storage offers high durability but higher egress costs.
- Using API Gateway + Lambda for auth simplifies deployment but adds cold‑start risk.
- Single‑region deployment reduces complexity but limits cross‑region failover speed.

## Capacity Estimates
- requests_per_second: 10000
- storage: 500GB/month audio, 200GB DB
- bandwidth: 500GB/day outbound

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
Design request: i need a frontend functionalities as well in react js
Existing desysflow baseline: version v1 at /Users/karan/Documents/machine-learning/answer-my-dms-tts/desysflow/answer-my-dms-tts/v1
Baseline files loaded: SUMMARY.md, HLD.md, LLD.md, TECHNICAL_REPORT.md, NON_TECHNICAL_DOC.md
Baseline excerpt from SUMMARY.md:
# SUMMARY

- Command: `design`
- Effective mode: `fresh`
- Project: `answer-my-dms-tts`
- Version: `v1`
- Output: `/Users/karan/Documents/machine-learning/answer-my-dms-tts/desysflow/answer-my-dms-tts/v1`
- Language: `Python`
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
###...
Baseline excerpt from LLD.md:
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
  - `src/answe...
Baseline excerpt from TECHNICAL_REPORT.md:
# TECHNICAL REPORT

## Executive Summary
Prompt-driven workflow executed for role `Platform Engineer` and produced architecture artifacts for version `v1`.

## Document Control
- Project: `answer-my-dms-tts`
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
- Representative files capped to `TOP_FILE_LIM...
```

## Future Improvements
- Add workload-specific sizing validation against expected growth intervals.
- Add explicit cost/performance option sets per deployment model.
- Add migration runbooks for major architecture transitions.
