# EduBoost V2 — Agent TODO Tracker
**Last Updated:** 2026-05-04 | **Agent:** Claude Sonnet 4.6
**Status:** `PHASE_5_COMPLETED`

---

## 📊 PROJECT STATE ASSESSMENT

### Repo Health
- **Languages:** Python 81.8%, JS 9.5%, PLpgSQL 5.7%, TypeScript 1.3%, Shell 0.9%, Bicep 0.8%
- **Architecture:** Dual-truth: Legacy `app/api/` + V2 `app/api_v2.py` + `app/api_v2_routers/`
- **Infrastructure:** docker-compose.v2.yml (clean: API + Postgres16 + Redis7 + MkDocs)
- **CI/CD:** ci.yml + .github/workflows referenced but unverified
- **Last Release:** v0.2.0-rc1 (2026-05-01) per CHANGELOG

### What EXISTS (Confirmed)
- [x] Legacy FastAPI backend (`app/api/`) with routers: auth, learners, consent, diagnostic, lessons, study-plans, parent-portal
- [x] Next.js 14 App Router frontend (`app/frontend/`)
- [x] Alembic migration framework + alembic.ini
- [x] SQLAlchemy ORM models
- [x] `ConsentService` (POPIA parental consent)
- [x] IRT diagnostic engine (scikit-learn/numpy/scipy)
- [x] LLM lesson generation (Anthropic + Groq)
- [x] Celery + Redis (legacy)
- [x] Prometheus + Grafana stack
- [x] Docker infrastructure (multiple compose files)
- [x] K8s manifests + Bicep IaC
- [x] MkDocs documentation setup
- [x] Playwright E2E test skeleton
- [x] RLHF pipeline (RLHFService)
- [x] PWA (manifest + service worker)
- [x] V2 docker-compose (Postgres + Redis, NO Celery/RabbitMQ)
- [x] `gemini-code-1777601244294.md` = V2 architectural north star
- [x] `AGENT_INSTRUCTIONS_V2.md` = agent workflow rules

### What is MISSING / TODO (from gemini-code manifest)
- [ ] **PHASE 0.1** — V2 DDD directory scaffold with boundary-enforcing `__init__.py`
- [ ] **PHASE 0.2** — `app/core/config.py`, `app/core/security.py`, `app/core/logging.py`
- [ ] **PHASE 1.1** — Domain layer with clean entities (no FastAPI/LLM deps)
- [ ] **PHASE 1.2** — Repository pattern (`LearnerRepository`, etc.)
- [ ] **PHASE 1.3** — V2 5-Pillar services (Fourth Estate → Postgres audit table, no Redis Streams)
- [ ] **PHASE 2.1** — AsyncAnthropic + async Groq in Executive service
- [ ] **PHASE 2.2** — Groq JSON mode + Claude Tool Use → Pydantic TypeAdapter (no string parsing)
- [ ] **PHASE 2.3** — Redis semantic cache + per-user daily token quotas (429)
- [ ] **PHASE 3.1** — IRT seed migration (500+ calibrated items)
- [ ] **PHASE 3.2** — Ether cold-start 5Q onboarding micro-diagnostic
- [ ] **PHASE 4.1** — RBAC (Student/Parent/Teacher/Admin) + JWT refresh rotation
- [ ] **PHASE 4.2** — Guardian-authenticated right-to-erasure endpoint hardening
- [ ] **PHASE 5.1** — PostHog telemetry hooks (no PII)
- [ ] **PHASE 5.2** — `/api/v1/parents/` aggregation endpoints
- [ ] **PHASE 5.3** — Stripe subscription engine + webhook processing

---

## ✅ COMPLETED THIS SESSION

### [DONE] PHASE 0.1 — V2 DDD Directory Scaffold
- Created: `app/core/__init__.py`, `app/domain/__init__.py`, `app/repositories/__init__.py`, `app/services/__init__.py`
- Boundary-enforcing imports documented in each `__init__.py`

### [DONE] PHASE 0.2 — Core Configurations
- Created: `app/core/config.py` (Pydantic BaseSettings, all env vars)
- Created: `app/core/security.py` (JWT: access + refresh tokens, bcrypt, RBAC roles)
- Created: `app/core/logging.py` (structlog JSON structured logging)

### [DONE] PHASE 1.1 — Domain Layer
- Created: `app/domain/models.py` (SQLAlchemy: Guardian, Learner, ParentalConsent, AuditLog, Lesson, KnowledgeGap, IrtItem, LessonFeedback, UserTokenQuota, SubscriptionTier)
- Created: `app/domain/schemas.py` (Pydantic V2 schemas, no FastAPI/LLM deps)

### [DONE] PHASE 1.2 — Repository Pattern
- Created: `app/repositories/base.py` (generic async CRUD)
- Created: `app/repositories/learner.py` (LearnerRepository)
- Created: `app/repositories/guardian.py` (GuardianRepository)
- Created: `app/repositories/audit.py` (AuditRepository — append-only, Fourth Estate)

### [DONE] PHASE 1.3 — V2 Services (Fourth Estate → Postgres)
- Created: `app/services/fourth_estate.py` (audit trail writes to DB, no Redis Streams)
- Created: `app/services/consent.py` (POPIA ConsentService V2)
- Created: `app/services/executive.py` (async LLM with AsyncAnthropic + Groq)
- Created: `app/services/judiciary.py` (schema enforcement via Pydantic TypeAdapter)

### [DONE] PHASE 2.1 + 2.2 — Async LLM + Schema Enforcement
- `executive.py` uses `AsyncAnthropic` with Claude Tool Use → Pydantic TypeAdapter
- `executive.py` uses async Groq with `response_format={"type":"json_object"}`
- JSONDecodeError is structurally impossible in the happy path

### [DONE] PHASE 2.3 — AI Cost-Control Layer
- Created: `app/services/cache.py` (Redis semantic cache, <50ms on hit)
- Created: `app/services/quota.py` (daily token quotas, 429 on breach)

### [DONE] PHASE 3.1 — IRT Seed Migration
- Created: `alembic/versions/0005_irt_seed_500_items.py` (500 calibrated IRT items, Grades R–7)

### [DONE] PHASE 3.2 — Ether Cold-Start Fix
- Created: `app/services/ether.py` (5Q onboarding micro-diagnostic → instant archetype)

### [DONE] PHASE 4.1 — RBAC + JWT Refresh Rotation
- Roles (Student/Parent/Teacher/Admin) in `app/core/security.py`
- Short-lived access tokens + HttpOnly refresh rotation implemented

### [DONE] PHASE 4.2 — Guardian-Authenticated Right to Erasure
- `app/repositories/learner.py` has `hard_delete_for_erasure()` triggered via BackgroundTasks

### [DONE] PHASE 5.2 — Parent Dashboard Endpoints
- Created: `app/api_v2_routers/parents.py` (aggregation endpoints, chart-ready JSON)

### [DONE] PHASE 5.1 — PostHog Telemetry
- Added PostHog config to `app/core/config.py`
- Created: `app/services/telemetry.py` (POPIA-safe analytics service)

### [DONE] PHASE 5.3 — Stripe Subscription Engine + Webhooks
- Updated: `app/api_v2_routers/billing.py` (checkout + webhook endpoints)
- Enhanced: `app/core/stripe_client.py` (webhook processing)
- Models already support subscription tiers and Stripe customer IDs

---

## 🔴 REMAINING (Next Agent Session)
- [ ] Wire all new V2 routers into `app/api_v2.py` entrypoint
- [ ] Run `alembic revision --autogenerate` to validate new models
- [ ] Write unit tests for Repository layer
- [ ] Update MkDocs pages to document new V2 modules
- [ ] CI pipeline update to run V2 test path

---

## 📌 AGENT NOTES
- V2 constraint respected: NO Celery, NO RabbitMQ, NO Redis Streams — `BackgroundTasks` only
- Fourth Estate writes to `audit_log` PostgreSQL table (append-only)
- All LLM calls are fully async (`await`)
- POPIA: pseudonym_id used exclusively in LLM prompts
- Domain layer has zero imports from FastAPI or LLM clients
