# Changelog

All notable changes to EduBoost SA are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Release cadence:
  - Patch (0.x.Y): bug fixes, documentation, dependency updates — no DB migration
  - Minor (0.X.0): new features, non-breaking API changes — may include migration
  - Major (X.0.0): breaking API changes, major schema changes — requires migration guide

---

## [Unreleased]

### 🔧 Hardening: Final Documentation & Infrastructure Alignment (2026-05-06)

**Status**: Repository documentation and core infrastructure synchronized with the V2 Modular Monolith state.

#### Added
- **Agent Instructions**: New `AGENT_INSTRUCTIONS_V2.md` in root with TDD, POPIA, and `arq` mandates.
- **Docker Sync**: Restored `docker-compose.v2.yml` and updated `docker-compose.prod.yml` to reflect the full V2 stack (FastAPI, Next.js, arq, PostgreSQL, Redis).
- **Architecture Stability**: Renamed architecture manifest to a stable path at `docs/architecture/ARCHITECTURE.md`.

#### Changed
- **Requirements**: Replaced Celery/Flower with `arq` in `requirements/base.in`.
- **Cleanup**: Removed all residual traces of the transient `gemini-code-*` filename from the entire repository.
- **README**: Updated "Compose File Map" and documentation links for consistency.

---

## [1.0.0-rc1] — 2026-05-04

### ⚠️ BREAKING: Complete V2 Architectural Migration (2026-05-02)

**Status**: Architecture restructured from five-pillar monolith to modular monolith. **V1 code deleted entirely.** All recommendations from `EduBoost_Architecture_Recommendation.md` implemented.

#### Added
- **Modular Architecture**: Domain modules structured as bounded contexts (`app/modules/{auth,diagnostics,lessons,consent,learners,study_plans,gamification,parent_portal,rlhf}`)
- **Core Infrastructure**: New shared kernel (`app/core/`) with:
  - Async SQLAlchemy session management (`database.py`)
  - Pydantic config with Azure Key Vault integration (`config.py`)
  - JWT + encryption utilities (`security.py`)
  - PostgreSQL-backed audit trail (async writes, non-blocking) (`audit.py`)
  - Prometheus metrics infrastructure (`metrics.py`)
  - FastAPI middleware: rate limiting, request ID, request timing (`middleware.py`)
  - Global exception handlers (`exceptions.py`)
  - Dependency injection helpers (`dependencies.py`)
  - Generic base repository pattern (`base.py`)
- **ORM Models**: Centralized SQLAlchemy models (`app/models/__init__.py`) — Alembic-managed
- **LLM Gateway Abstraction**: Provider-agnostic interface with Groq (primary) + Anthropic (fallback) in `app/modules/lessons/llm_gateway.py`
- **IRT Engine**: Diagnostic scoring logic isolated in `app/modules/diagnostics/irt_engine.py`
- **Background Jobs**: Migration from Celery to `arq` (async Redis queue) for single-node simplicity
- **Consent Middleware**: POPIA gate as FastAPI dependency — impossible to forget, visible in OpenAPI
- **GitHub Workflows**: CI/CD moved to `.github/workflows/ci-cd.yml` (standard location)
- **Test Reorganization**: 
  - `tests/popia/test_popia_compliance.py` — compliance test suite
  - `tests/smoke/test_v2_smoke.py` — v2 smoke tests
  - `tests/unit/modules/diagnostics/test_irt_engine.py` — IRT unit tests

#### Removed
- ✅ **V1 API layer** (`app/api/`) — no active clients, zero migration obligation
- ✅ **RabbitMQ** — audit trail now PostgreSQL-backed with async writes
- ✅ **Celery + Flower** — replaced by `arq` (async Redis queue)
- ✅ **Five-pillar metaphor** — `Executive`, `Judiciary`, `Fourth Estate`, `Ether` services
  - Audit policy replaced by `core/audit.py` async writer
  - Judiciary policy logic absorbed into `core/dependencies.py` consent middleware
- ✅ **Legacy compose files** — `docker-compose.yml`, `docker-compose.prod.yml`
- ✅ **Temporary artifacts** — `mnt/`, `scratch/`, `gemini-code-*.md`
- ✅ **Old domain structure** — `app/domain/`, `app/services/`

#### Changed
- **Infrastructure Target**: Azure Container Apps (ACA) + managed PostgreSQL + managed Redis
- **Secrets**: Azure Key Vault integration in `core/config.py` (local `.env` fallback for dev)
- **API Entrypoint**: Single `app/api_v2.py` aggregating routers from `api_v2_routers/`
- **Repositories**: Now live in `app/repositories/` with base class in `core/base.py`
- **Exception Handling**: Unified in `core/exceptions.py` — all endpoints use same stack trace formatting

#### Infrastructure (Production)
| Component | Service | Notes |
|---|---|---|
| Backend | Azure Container Apps | Single node, auto-scale to zero |
| Frontend | Azure Static Web Apps or ACA | Managed, no ops burden |
| Database | Azure Database for PostgreSQL Flexible | South Africa North region, POPIA-compliant |
| Cache / Jobs | Azure Cache for Redis | Managed, for arq background jobs |
| Inference | ACA sidecar container | Isolated torch/transformers, internal-only |
| Secrets | Azure Key Vault | Centralized, audited secret access |
| Observability | Grafana Cloud (free tier) | Managed Prometheus + Loki, no self-hosted |
| CDN / WAF | Azure Front Door | SSL termination, South Africa PoP |

#### Migration Checklist (Completed)
- [x] Delete all V1 code and legacy infrastructure
- [x] Move CI pipeline to `.github/workflows/`
- [x] Migrate core infrastructure to `app/core/`
- [x] Migrate routers to `app/api_v2_routers/`
- [x] Reorganize domain modules into `app/modules/`
- [x] Centralize ORM models in `app/models/`
- [x] Reorganize tests by domain
- [x] Create Python package structure (__init__.py for all modules)

#### Next Steps (Backlog)
- [ ] Replace Celery with arq in background job handlers
- [ ] Validate 80% unit test coverage on all domain modules
- [ ] Complete POPIA compliance test suite
- [ ] Deploy to ACA staging environment via updated CI
- [ ] Set up Grafana Cloud dashboards (prod observability)
- [ ] Complete security pen test checklist

---

### Added (Other)
- `requirements-ml.txt` separates torch/transformers from base install (#4)
- `INCLUDE_ML` Docker build argument gates heavyweight ML deps (#4)
- Playwright E2E test suite covering diagnostic → study plan → lesson → parent portal (#6)
- `scripts/popia_sweep.py` automated POPIA audit of LLM prompt paths and consent gates (#7)
- Grafana dashboard: Learner Journey SLOs (`grafana/dashboards/learner_journey.json`) (#9)
- Grafana dashboard: LLM Provider Health (`grafana/dashboards/llm_provider_health.json`) (#9)
- Consolidated `.env.example` (removed duplicate `env.example`) (#10)
- `CONTRIBUTING.md` developer onboarding and contribution guidelines (#10)

### Changed (Other)
- `docker-compose.v2.yml` now the canonical dev stack (v1 and prod variants deleted)
- Alembic migration `0001` now sole source of truth for schema (SQL scripts removed from compose startup) (#1)

### Fixed
- Removed stale RabbitMQ references from all docker-compose files

---

## [0.2.0-rc1] — 2026-05-01

### Added
- **Inference Microservice**: Decoupled `torch` and `transformers` into a standalone service (`docker/Dockerfile.inference`).
- **Log Aggregation**: Integrated **Grafana Loki** and **Promtail** for centralized, structured logging.
- **Multilingual Support**: Added isiZulu (`zu`), Afrikaans (`af`), and isiXhosa (`xh`) lesson generation with localized cultural context.
- **RLHF Pipeline**: Implemented `RLHFService` for capturing lesson feedback and exporting preference datasets (OpenAI/Anthropic formats).
- **PWA Support**: Added `manifest.json` and service worker integration for installability and offline resilience.
- **SLO Instrumentation**: Added missing business-value Prometheus metrics for consent, diagnostic sessions, study plans, and lesson volume.
- **Security Runbook**: Comprehensive penetration testing checklist in `audits/security/pen_test_checklist.md`.
- **Alembic Revision 0004**: Added `lesson_feedback` and `rlhf_exports` tables.

### Changed
- **API Optimization**: Reduced API container footprint from ~4GB to **<500MB** by removing ML dependencies.
- **Inference Gateway**: Refactored `inference_gateway.py` to use HTTP calls (`httpx`) to the inference sidecar.
- **Metrics**: Registered all learner-journey SLO counters in `app/api/core/metrics.py`.

### Security
- **PII Scrubbing**: Enhanced `RLHFService` with automatic regex-based PII scrubbing for free-text comments.
- **Isolation**: Inference service is isolated from the public internet, reachable only via internal Docker network.

---

## [0.1.0-beta] — 2026-04-30

First tagged beta release. Establishes foundational architecture.

### Added
- FastAPI backend with routers: auth, learners, consent, diagnostic, lessons, study-plans, parent-portal
- Next.js 14 App Router frontend: dashboard, lesson view, diagnostic, parent portal
- Alembic migration `0001`: guardians, learners, parental_consents, diagnostic_sessions, study_plans, audit_log
- `ConsentService` — POPIA parental consent service layer with grant/revoke/erasure
- `ParentalConsent` ORM model with `is_active` property and annual renewal logic
- IRT-based diagnostic engine (scikit-learn, numpy, scipy)
- LLM lesson generation via Anthropic Claude and Groq (with pseudonym_id isolation)
- Celery + Redis async task queue with Beat scheduler
- Prometheus + Grafana observability stack
- Docker Compose local development stack (9 services)
- GitHub Actions CI skeleton (lint + test)
- AGENT_INSTRUCTIONS.md TDD-loop paradigm for autonomous agents

### Security
- Emails stored as SHA-256 hash + pgcrypto-encrypted ciphertext (never plaintext)
- Learner real UUID never sent to LLM providers — pseudonym_id used exclusively
- Soft-delete pattern for right-to-erasure (POPIA Section 24)
- Annual consent renewal enforced via `expires_at` column

---

[Unreleased]: https://github.com/NkgoloL/edo-boost-main/compare/v0.2.0-rc1...HEAD
[0.2.0-rc1]: https://github.com/NkgoloL/edo-boost-main/compare/v0.1.0-beta...v0.2.0-rc1
[0.1.0-beta]: https://github.com/NkgoloL/edo-boost-main/releases/tag/v0.1.0-beta
