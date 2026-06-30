# Phase 6 Execution Plan — Durable Background Jobs

**Date**: 2026-06-10
**Updated**: 2026-06-12 (ALL COMPLETE — all 3 RoadMap criteria live-verified)
**Refresh**: 2026-06-14 (static/import/unit verification rerun)
**Status**: ✅ COMPLETE — all acceptance criteria verified
**Branch**: `phase-6/durable-background-jobs`
**Completed**: 6.1 (ARQ settings fix), 6.2 (Compose wiring), 6.3 (move work off BackgroundTasks), 6.4 (tests + evidence docs), 6.4.3 (restart-survival live-verified)
**Remaining**: Tracker closeout — PR merge, branch deletion
**Scope**: Replace request-adjacent placeholder job handling with durable ARQ worker wiring, compose/production deployment support, and verification evidence.
**Priority**: P1 (per [roadmap.md](../roadmap.md#L258-L281))

---

## Pre-Conditions

- [x] Branch `phase-6/durable-background-jobs` created (includes Phase 5 changes).
- [x] ARQ worker code already exists in `app/modules/jobs.py` (WorkerSettings, cron jobs).
- [x] Docker Compose is the deployment source of truth; worker service added to both dev and prod compose files.
- [x] Redis is running for live enqueue/dequeue verification (validated during Phase 6.4).

---

## Pre-Execution Baseline

### 6.0.1 — Background Job Split (captured 2026-06-10)

Current state from code inspection:

- [`app/core/jobs.py`](../../app/core/jobs.py) is a FastAPI `BackgroundTasks` wrapper with in-memory fallback state and Redis-backed job records.
- [`app/modules/jobs.py`](../../app/modules/jobs.py) already defines ARQ worker functions and cron schedules.
- [`app/jobs/consent_renewal_job.py`](../../app/jobs/consent_renewal_job.py) defines a consent renewal worker job entrypoint.
- [`app/services/arq_import_compat.py`](../../app/services/arq_import_compat.py) provides import-safe ARQ fallback types.
- The roadmap states that API routes still return job IDs through FastAPI `BackgroundTasks`, while ARQ job code exists but is not deployed.

### 6.0.2 — Deployment Wiring Check

Current repo scan indicates:

- `docker-compose.yml` exists, but Phase 6 worker wiring has not yet been verified in this session.
- The roadmap calls out missing worker deployment in Compose/production and a likely settings naming mismatch.

### 6.0.3 — CI / Verification Surface

Relevant checks already present in the repo:

- `scripts/check_arq_worker_import.py`
- `tests/unit/test_arq_worker_import_contract.py`
- `scripts/repair_arq_dependency_worker_import.py`
- `docs/release/arq_dependency_worker_import_repair_report.md`

Missing for Phase 6 completion:

- durable worker deployment evidence
- runtime enqueue/dequeue proof
- worker health/readiness evidence
- confirmation that request-adjacent `BackgroundTasks` usage is limited to non-critical paths

---

## Phase 6.1 — Fix ARQ Settings and Worker Wiring ✅ COMPLETE

### Problem Statement

The codebase already has ARQ job definitions, but the deployment/runtime path is not fully authoritative. The roadmap flags likely settings casing issues and missing worker deployment.

### Acceptance Criteria

- [x] ARQ settings resolve correctly for worker startup and runtime configuration.
- [x] ARQ worker entrypoint runs with the expected `WorkerSettings`.
- [x] The worker job set includes the durable jobs required by the roadmap.

### Implementation Tasks

- [x] Fixed `cfg.redis_url` → `cfg.REDIS_URL` (casing mismatch causing settings resolution failure).
- [x] Converted `redis_settings` from a `@classmethod` to a class variable on `WorkerSettings` (ARQ requires it as a simple attribute, not a method).
- [x] Import: added `from urllib.parse import urlparse` at module top.
- [x] Updated in-code comments in `app/jobs/consent_renewal_job.py` and `app/jobs/practice_session_cleanup_job.py` (`app/core/arq_worker.py` → `app/modules/jobs.py`).
- [x] Cron jobs (`consent_renewal`, `practice_session_cleanup`) already registered in `WorkerSettings`.

**Changed files:** `app/modules/jobs.py` (-18/+8), `app/jobs/consent_renewal_job.py`, `app/jobs/practice_session_cleanup_job.py`

---

## Phase 6.2 — Wire the Durable Worker into Compose / Production ✅ COMPLETE

### Problem Statement

The worker logic exists in code, but the deployment stack still needs an explicit service definition and startup path.

### Acceptance Criteria

- [x] Local Compose starts the ARQ worker successfully (service defined, `docker compose up worker`).
- [x] Production Compose / deployment manifests include the worker.
- [x] Redis connectivity is available to the worker in local and production-like environments (depends_on redis: service_healthy).

### Implementation Tasks

- [x] Added `worker` service to `docker-compose.yml`: uses `Dockerfile.v2`, command `arq app.modules.jobs.WorkerSettings`, env vars (`APP_ENV`, `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`).
- [x] Added `worker` service to `docker-compose.prod.yml`: same structure with production env vars plus `ENCRYPTION_KEY`, `ENCRYPTION_SALT`, `GROQ_API_KEY`, `ANTHROPIC_API_KEY`.
- [x] Both services depend on postgres and redis health checks.
- [x] Resource limits set (dev: 256M, prod: 768M memory).
- [x] Reuses existing `docker/Dockerfile.v2` (no separate worker Dockerfile needed).
- [x] `docker compose up worker` verified against a live Redis/Postgres stack during 2026-06-12 live proof.

**Changed files:** `docker-compose.yml` (+26), `docker-compose.prod.yml` (+29)

---

## Phase 6.3 — Move Durable Work Off Request-Adjacent BackgroundTasks ✅ COMPLETE

### Problem Statement

The roadmap requires durable jobs rather than request-scoped `BackgroundTasks` for long-running or restart-sensitive work. Currently, API routes return job IDs via FastAPI `BackgroundTasks` with in-memory fallback state. If the API process restarts, queued work is lost.

### Discovery (do first)

Before any code changes, audit the current job landscape:

- [x] **List all BackgroundTasks enqueue points.** Search `app/` for `background_tasks.add_task` and `BackgroundTasks` usage to find all non-durable job paths.
- [x] **Classify each job**: `[durable-required]`, `[durable-optional]`, or `[request-adjacent-ok]`.
  - *Durable-required*: lesson generation, study-plan generation, consent renewal, practice session cleanup, ETL pipeline runs.
  - *Durable-optional*: email notifications, analytics events.
  - *Request-adjacent-ok*: short-lived audit writes, metric increments.
- [x] **Document current state** as a table in the implementation report (route -> job name -> current mechanism -> target mechanism).

### Acceptance Criteria

- [x] Durable jobs are enqueued through ARQ (`await arq_queue.enqueue_job(...)`) rather than `background_tasks.add_task(...)`.
- [x] FastAPI `BackgroundTasks` remains limited to non-critical request-adjacent work (audit writes, metrics).
- [x] Durable work survives API restarts (live-verified 2026-06-12).

### Implementation Tasks

- [x] **6.3.1** Added an ARQ queue accessor in `app/modules/jobs.py` (`enqueue_durable(...)`) returning a job ID.
- [x] **6.3.2** Migrated lesson generation to `enqueue_durable("generate_lesson", ...)`.
- [x] **6.3.3** Migrated study-plan generation to `enqueue_durable("generate_study_plan", ...)`.
- [x] **6.3.4** Migrated consent renewal to the ARQ worker-backed path and confirmed the cron schedule remains registered.
- [x] **6.3.5** Migrated practice session cleanup to the cron-based worker path.
- [x] **6.3.6** Updated `app/core/jobs.py` to clearly document that it is now for non-durable, request-adjacent work only.
- [x] **6.3.7** Added/updated unit tests proving enqueue, worker execution, and post-execution status retrieval.

---

## Phase 6.4 — Add Worker Health, Readiness, and Verification Evidence ✅ COMPLETE

### Problem Statement

Phase 6 is not complete until the worker is proven in a live local or staging-style environment with captured evidence.

### Acceptance Criteria

- [x] Worker startup health/readiness is observable (`docker compose logs worker` shows successful Redis + DB connection).
- [x] Enqueue/dequeue or execute/status proof exists for at least one durable job (consent renewal).
- [x] Phase 6 evidence and audit docs are committed.

### Implementation Tasks

- [x] **6.4.1** Started the full stack (`docker compose up -d postgres redis worker`) and verified the worker connects.
- [x] **6.4.2** Triggered a durable job and captured the execution log.
- [x] **6.4.3** Prove restart-survival: worker/API restart path verified; queued ARQ job executed after worker restart on 2026-06-12.
- [x] **6.4.4** Ran `scripts/check_arq_worker_import.py` and confirmed it passes.
- [x] **6.4.5** Wrote `docs/release/phase_6_evidence.md` with captured outputs.
- [x] **6.4.6** Wrote `docs/roadmap/execution/phase_6_implementation_report.md`.
- [x] **6.4.7** Wrote `docs/release/phase_6_implementation_audit.md`.

---

## Evidence Output

| Artifact | Path | Status |
|----------|------|--------|
| Phase 6 execution plan | `docs/roadmap/execution/phase_6_execution_plan.md` | ✅ (this file) |
| Phase 6 implementation report | `docs/roadmap/execution/phase_6_implementation_report.md` | ✅ |
| Phase 6 evidence | `docs/release/phase_6_evidence.md` | ✅ |
| Phase 6 implementation audit | `docs/release/phase_6_implementation_audit.md` | ✅ |

---

## Success Criteria

**Phase 6 is complete when:**

- [x] ARQ worker service defined in local Compose (6.2)
- [x] ARQ settings correct: `REDIS_URL` casing, `redis_settings` as class var (6.1)
- [x] Durable jobs enqueued through ARQ, not `BackgroundTasks` (6.3)
- [x] Durable job tests cover enqueue, execution, and status retrieval (6.3)
- [x] API restart does not lose queued durable work (6.4) — **live-verified 2026-06-12**
- [x] Worker startup health/readiness verified against live Redis + Postgres (6.4)
- [x] Evidence and audit docs committed (6.4)

**RoadMap alignment** (from [roadmap.md](../roadmap.md#L258-L281)):

- [x] ARQ worker starts in local Compose ✅
- [x] Durable job tests cover enqueue, execution, and status retrieval ✅
- [x] API restart does not lose queued durable work ✅

---

## Close Checklist

- [x] Execution plan exists: `docs/roadmap/execution/phase_6_execution_plan.md` (this file)
- [x] Implementation report exists: `docs/roadmap/execution/phase_6_implementation_report.md`
- [x] Audit report exists: `docs/release/phase_6_implementation_audit.md`
- [x] Evidence files committed and accurate
- [x] `roadmap.md` Phase 6 status updated to "Code Complete (2026-06-11)" with Docker-pending note
- [x] `context/build-plan.md` Phase 6 status updated
- [x] `context/progress-tracker.md` updated
- [x] `docs/todos/todo.md` last-updated bumped
- [x] WorkerSettings namespace hygiene fixed (`_cfg`, `_parsed`)
- [x] RedisSettings initialization unified (manual urlparse in both paths)
- [x] Implementation report corrected — no longer overstates verification
- [x] Audit report corrected — honest about 2/3 RoadMap criteria unverified
- [x] Live Docker verification: restart-survival (6.4.3) — verified 2026-06-12
- [x] Live Docker verification: worker startup health — verified
- [x] Live Docker verification: enqueue/dequeue proof — verified
- [ ] Branch merged to `master` via PR
- [ ] Remote branch deleted after merge

---

## Next Phase

**Phase 7: Deployment and Security Hardening** — fix hardcoded URLs, security headers, CORS/CSP/HSTS, and route protection gaps after durable jobs are in place.
