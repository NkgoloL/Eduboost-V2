# EduBoost V2 — Outstanding Task Roadmap

**Purpose:** This file is the clearest possible handoff roadmap for continuing the V2 migration. It is written so that a less capable agent can still make progress safely.

## How to use this roadmap

Follow these rules in order:

1. **Prefer V2 files over legacy files.**
   - V2 runtime entrypoint: `app/api_v2.py`
   - V2 routers: `app/api_v2_routers/`
   - V2 services: `app/services/`
   - V2 repositories: `app/repositories/`
   - V2 docs runtime: `docker-compose.v2.yml`
2. **Do not remove legacy files unless a V2 replacement already exists.**
3. **When adding new V2 behavior, keep this dependency flow:**
   - router → service → repository
4. **Update this roadmap and the V2 implementation report after every meaningful change.**
5. **If a documentation patch fails because text changed, do not guess. Create a new clearly named file instead.**

---

## Current V2 state summary

The repository already has these V2 foundations:

- V2 app entrypoint: `app/api_v2.py`
- V2 router package: `app/api_v2_routers/`
- V2 service package: `app/services/`
- V2 repository package: `app/repositories/`
- V2 docs: `mkdocs.yml`, `docs/`, `docker-compose.v2.yml`
- V2 typed request models: `app/domain/api_v2_models.py`

The V2 route surface already covers:

- auth
- learners
- diagnostics
- study plans
- parents
- audit
- lessons
- gamification
- system
- assessments

The main remaining problem is **depth and independence**, not missing route names.

Recent security/runtime hardening already landed:

- production secret loading now pulls required values from Azure Key Vault
- access-token revocation now uses a Redis-backed JWT denylist on logout/revoke-all paths
- V2 runtime remains RabbitMQ-free, and legacy docs/examples no longer advertise `guest/guest`

---

## Outstanding tasks (highest priority first)

### 1. Make V2 the sole operational default
**Goal:** A new developer should naturally start and use V2 first.

**Status:** In progress. `docker-compose.v2.yml` now includes API, docs, Postgres, Redis, and frontend services; CI now targets `master`/PRs and includes V2 smoke, frontend lint/type checks, and POPIA sweep wiring. Full green verification still requires a Python 3.11 environment.

**Files to inspect/update:**
- `README.md`
- `CONTRIBUTING.md`
- `docker-compose.v2.yml`
- `docker/Dockerfile.v2`
- `ci.yml`

**Definition of done:**
- V2 is the default startup path in docs.
- V2 smoke tests are present and passing in CI.
- Legacy startup is clearly marked as compatibility/deprecated.

---

### 2. Remove remaining direct persistence logic from V2 services (COMPLETE)
**Goal:** V2 services should not talk directly to SQLAlchemy/session code when a repository boundary is appropriate.

**Status:** ALL V2 services are now 100% repository-driven.
- `app/services/diagnostic_service_v2.py`
- `app/services/lesson_service_v2.py`
- `app/services/gamification_service_v2.py`
- `app/services/assessment_service_v2.py`
- `app/services/study_plan_service_v2.py`
- `app/services/parent_report_service_v2.py`
- `app/repositories/` (added missing repositories for Auth, ParentReport, and StudyPlan)

**Definition of done:**
- ✅ Each service delegates persistence to a repository.
- ✅ Repositories own DB reads/writes.
- ✅ Services focus on business logic only.

---

### 3. Deepen V2 implementations so they are not placeholders (COMPLETE)
**Goal:** V2 behavior should be genuinely useful, not only structurally present.

**Status:** Production-grade logic added to all core services.
- `app/services/lesson_service_v2.py` (added LLM integration + caching)
- `app/services/diagnostic_service_v2.py`
- `app/services/study_plan_service_v2.py` (added real scheduling logic)
- `app/services/parent_report_service_v2.py` (added narrative summaries)
- `app/services/gamification_service_v2.py`
- `app/services/assessment_service_v2.py`

**Definition of done:**
- ✅ Lessons are generated/fetched in a consistent DB/cache flow.
- ✅ Diagnostics persist meaningful results.
- ✅ Study plans and parent reports use structured DB-backed inputs.
- ✅ Assessments support full attempt flow.
- ✅ Gamification reflects DB-backed learner state and badges.

---

### 4. Add stronger V2-specific tests (COMPLETE)
**Goal:** The V2 path should be testable on its own.

**Status:** Robust unit and integration test suite implemented.
- `tests/unit/test_v2_services_full.py` (30+ tests)
- `tests/unit/test_v2_repositories_full.py`
- `tests/integration/test_v2_routers.py`

**Definition of done:**
- ✅ V2 routers have request/response contract tests.
- ✅ V2 services have unit tests.
- ✅ At least one V2 integration flow exists.

---

### 5. Reduce dependence on legacy architecture assumptions
**Goal:** V2 should stop depending conceptually on Celery, RabbitMQ, and the inference microservice for its main path.

**Status:** In progress. The V2 service package now exists and key routers can target the V2 service boundary. `docker-compose.v2.yml` remains RabbitMQ-free; Redis is used for cache/session-style workloads only. Production secrets now load from Azure Key Vault, and the auth flow now enforces immediate JWT denylist checks during logout/revoke-all flows.

**Files to inspect/update:**
- `docker-compose.v2.yml`
- `app/api_v2.py`
- `app/services/*`
- `README.md`

**Definition of done:**
- V2 main path works without Celery.
- V2 main path works without RabbitMQ.
- Any legacy dependency still required is clearly documented as temporary.

---

### 6. Create a clear V2 deprecation plan for legacy runtime
**Goal:** The repo should state what is legacy and what is target state.

**Status:** In progress. `LEGACY_RETIREMENT_DATE` is now available in V2 settings. This checkout does not currently contain the legacy `app/api/routers/*` tree referenced by older TODOs, so response-header deprecation work is not applicable until/unless that tree is restored.

**Files to inspect/update:**
- `README.md`
- `docs/v2_migration.md`
- `audits/reviews/V2_Migration_Status.md`

**Definition of done:**
- Legacy runtime is explicitly labeled.
- V2 target path is explicit.
- Migration status is easy to understand for new contributors.

---

## Safe execution order for weaker agents

If an agent is less capable, it should complete tasks in this order only:

1. Add tests for existing V2 routes/services.
2. Move more persistence code into repositories.
3. Improve one V2 service at a time.
4. Update docs after each change.
5. Only after that, touch startup/runtime defaults.

---

## What not to do

- Do not delete `app/api/*` just because V2 exists.
- Do not remove Docker/Celery/RabbitMQ files unless V2 replacement is already proven.
- Do not rewrite working tests unless needed for V2 correctness.
- Do not change roadmap/report files by guessing their current text.

---

## Minimum status update after each future batch

After every future batch, update:

- `audits/reports/V2_Implementation_Report.md`
- this file (`audits/roadmaps/V2_Outstanding_Task_Roadmap.md`)
- optionally `docs/v2_migration.md` if user-facing status changed
