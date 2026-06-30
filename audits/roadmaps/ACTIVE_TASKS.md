## Active Tasks (Agent Execution)

This file is the **authoritative checklist** for the work currently being executed in this repository.  
Each item should be closed only when implemented, verified (tests or runtime validation), and committed.

---

### 🎯 **MILESTONE: V2 Architecture Migration (2026-05-02)** ✅ COMPLETED

All recommendations from `EduBoost_Architecture_Recommendation.md` implemented. V1 code deleted entirely. Architecture restructured to modular monolith with PostgreSQL-backed audit trail.

#### Completed Deliverables
- [x] Delete V1 infrastructure (`app/api/`, legacy docker-compose files, RabbitMQ/Celery refs)
- [x] Delete temporary artifacts (`mnt/`, `scratch/`, `gemini-code-*.md`)
- [x] Reorganize CI/CD to `.github/workflows/ci-cd.yml`
- [x] Migrate core infrastructure to `app/core/` with PostgreSQL audit trail (`audit.py`)
- [x] Migrate routers to `app/api_v2_routers/` (auth, consent, lessons)
- [x] Reorganize domain modules: `app/modules/{auth,diagnostics,lessons,consent,learners,study_plans,gamification,parent_portal,rlhf}`
- [x] Migrate IRT engine to `modules/diagnostics/irt_engine.py`
- [x] Migrate LLM gateway to `modules/lessons/llm_gateway.py`
- [x] Centralize ORM models in `app/models/`
- [x] Reorganize tests: POPIA → `tests/popia/`, Smoke → `tests/smoke/`, IRT → `tests/unit/modules/diagnostics/`
- [x] Initialize all modules as Python packages
- [x] Update tracking documents (CHANGELOG, System_Status_Roadmap, ACTIVE_TASKS)

#### Next Immediate Work (Post-Migration)
- [ ] Verify module imports and dependencies (run pytest for circular imports)
- [ ] Replace Celery with `arq` (async Redis queue)
- [ ] Validate 80%+ unit test coverage on domain modules
- [ ] Test full stack in Docker (docker-compose.v2.yml)
- [ ] Run CI pipeline to ensure green status

---

### Scope: Backend functional verification + dummy data generator

- [x] **Docs scaffolding**
  - [x] Add/maintain this task list (`ACTIVE_TASKS.md`)
  - [x] Add/maintain an implementation log (`audits/recommendations/Implementation_Report.md`)

- [x] **Backend: functional verification**
  - [x] Ensure `pytest` runs in a local venv without Docker and without external LLM keys
  - [x] Make integration tests deterministic by stubbing inference in `APP_ENV=test`
  - [x] Fix any failing routers/services uncovered by tests until suite is green

- [x] **Dummy data generation (post-startup, silent)**
  - [x] Implement generator modules (DB writers) capable of creating up to **10,000** dummy records
  - [x] Ensure generation begins **only after** the API is up (post-startup background task)
  - [x] Make generation **silent** (no noisy logs; only errors should surface)
  - [x] Add idempotency/locking so multiple workers don’t double-generate

- [x] **Persistence floor**
  - [x] Keep **1/3 to 1/2** of generated dummy data persisted at all times
  - [x] Implement cleanup/rotation that never drops below the persistence floor
  - [x] Add configuration knobs (target size, floor ratio, cadence)

- [x] **Commits**
  - [x] Commit in small batches after each milestone (docs → backend green → generator → persistence floor)
  - [x] Implement frontend gamification and state management refactor
  - [x] Sync progress to Redmine

### Scope: EduBoost SA Issues and Solutions remediation

- [x] **Repository and environment hygiene**
  - [x] Removed tracked Celery Beat runtime artifact from the working tree and ignored future schedule files
  - [x] Deduplicated `requirements.txt`, added `aiosqlite`, and moved heavy local ML packages to `requirements-ml.txt`

- [x] **Database lifecycle**
  - [x] Reconciled Alembic into a single revision chain
  - [x] Removed duplicate `study_plans` creation and duplicate diagnostic-session index creation
  - [x] Aligned ORM and migrations for `items_correct`, parent verification tokens, reports, and dummy data points
  - [x] Updated Docker Compose to run Alembic migrations instead of mounting SQL schema init scripts

- [x] **Backend API contracts and POPIA controls**
  - [x] Fixed provider-router imports, fallback stream imports, and `system_prompt` handling
  - [x] Implemented missing `StudyPlanService` and `ParentPortalService` router-facing methods
  - [x] Moved parent report persistence to the canonical `reports` table
  - [x] Switched worker consent checks to the canonical `consent_audit` table
  - [x] Enforced guardian token ownership on parent/consent/deletion/access routes
  - [x] Added token `jti` revocation checks and encrypted guardian full names at registration

- [x] **Frontend, CI, and docs alignment**
  - [x] Updated frontend API client routes for study plans and parent reports
  - [x] Registered the service worker and aligned offline queue/cache routes with backend APIs
  - [x] Added frontend CI, POPIA test path, and smoke test path
  - [x] Updated README, development, architecture, and POPIA docs for ports, migrations, routes, and encryption

### Scope: Fourth Estate Migration & System Status Remediation

- [x] **Durable Audit Trail (Pillar 4)**
  - [x] Migrated Fourth Estate from Redis Streams to RabbitMQ for durable persistence
  - [x] Added `aio-pika` dependency and configured `RABBITMQ_URL`
  - [x] Integrated audit logging into `WorkerAgent` base class (automatic auditing)
  - [x] Implemented lifecycle hooks in `main.py` for RabbitMQ connection management

- [x] **System Status Report 2 Implementation**
  - [x] Consolidated all schema management under a single Alembic baseline
  - [x] Implemented and integration-tested end-to-end parental consent gating
  - [x] Defined canonical production deployment path (`docker-compose.prod.yml` and `nginx.prod.conf`)
  - [x] Fixed frontend port mapping and verified full stack boot
  - [x] Implemented E2E Playwright test suite for key learner journeys
  - [x] Executed POPIA "Chaos Sweep" for PII leakage prevention
  - [x] Introduced semantic versioning and release automation workflows
  - [x] Expanded Grafana dashboards for SLOs and LLM provider health
  - [x] Formalized `CONTRIBUTING.md` and consolidated `.env.example`

### Scope: Technical Report Hardening & Long-Term Roadmap

- [x] **Infrastructure Decoupling**
  - [x] Extracted `torch` and `transformers` into a dedicated `inference` microservice
  - [x] Optimized API image size from 4GB+ to <500MB
  - [x] Integrated `httpx` based inference gateway

- [x] **Observability & Logging**
  - [x] Integrated **Grafana Loki** and **Promtail** for log aggregation
  - [x] Registered missing learner-journey SLO counters in Prometheus
  - [x] Implemented Prometheus alerting rules (`alerts.yml`)

- [x] **AI Governance & Multilingual**
  - [x] Established **RLHF pipeline** foundations (feedback collection + export)
  - [x] Integrated multilingual support for **isiZulu**, **isiXhosa**, and **Afrikaans**
  - [x] Localized prompt templates for all target languages

- [x] **Compliance & Hardening**
  - [x] Completed **ConsentService** lifecycle (versioning + erasure grace period)
  - [x] Enforced **70% test coverage** quality gate in `pytest.ini`
  - [x] Created structured **Security Pen-Test Checklist** and runbook
  - [x] Enabled **PWA** manifest and service worker for offline installation

### Scope: V2 Baseline Pivot (docs/architecture/ARCHITECTURE.md)

- [x] **Phase 0 — Repository Bootstrap & Foundation**
  - [x] Scaffolded initial modular-monolith directories: `app/core`, `app/domain`, `app/repositories`, `app/services`
  - [x] Added foundational V2 modules: `config.py`, `security.py`, `logging.py`
  - [x] Added initial domain entities and learner repository abstraction
  - [x] Align runtime startup and Docker path with V2 single-node constraints

- [x] **Phase 1 — Boundary Enforcement**
  - [x] Migrate initial learner-facing business logic toward `app/services` and `app/repositories`
  - [x] Define append-only PostgreSQL audit table target to replace legacy broker dependency
  - [x] Introduce initial V2 API surface for learner read + audit feed
  - [x] Reduce direct router-to-persistence coupling across the wider application

- [x] **Phase 2+ — V2 Manifest Migration**
  - [x] Replace legacy completion claims in audit docs with V2 migration status
  - [x] Plan staged retirement of Celery/RabbitMQ/microservice-first assumptions
  - [x] Implement initial V2-safe equivalents using BackgroundTasks and modular monolith boundaries
  - [x] Add initial diagnostics + quota control to the V2 slice
  - [x] Complete migration of all legacy routes and workflows into V2 boundaries
  - [x] Replicate multi-file tracking/documentation structure for the V2 stream
  - [x] Promote dedicated `app/api_v2_routers/*` route surface and document legacy runtime as compatibility mode
  - [x] Expand V2 route families to include lessons, gamification, system, and assessments
  - [x] Deepen V2 service implementations (Lesson, StudyPlan, ParentReport) with production-grade logic
  - [x] Establish full repository layer (Auth, ParentReport, StudyPlan, Lesson, Diagnostic)
  - [x] Implement comprehensive V2 unit and integration test suite

- [x] **Phase 3 — Production Hardening & Cloud Deployment**
  - [x] Define Azure Container Apps (ACA) as the authoritative production target
  - [x] Create Bicep infrastructure-as-code for ACA environment and API app
  - [x] Implement ACA-ready Docker validation (`docker-compose.aca.yml`)
  - [x] Implement V2 cross-cutting concerns: RBAC, Right to Erasure, Analytics Hooks
  - [x] Implement 5-Pillar V2 Services: Judiciary, Ether, Fourth Estate (Postgres-backed)
  - [ ] Finalize CI/CD pipeline automation for ACA deployments
  - [ ] Execute final V2 verification suite in staging environment
