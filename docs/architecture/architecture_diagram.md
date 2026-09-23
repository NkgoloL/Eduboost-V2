---
title: "EduBoost SA V2 — Architecture Diagram"
status: active
owner: architecture
reviewers: [architecture, engineering]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: '2026-09-22'
review_interval_days: 60
evidence_command: "make docs-housekeeping-check"
code_anchors:
  - app/core/arq_worker.py
  - app/frontend/package.json
  - app/jobs/
  - docs/architecture/README.md
---

# EduBoost SA V2 — Architecture Diagram

> **Note:** This diagram is the authoritative visual reference for the V2
> modular-monolith topology. Update it whenever a new bounded context is added
> or infrastructure dependency changes.

---

## Runtime Topology

```mermaid
graph TD
    subgraph Client["Client Layer"]
        Browser["Browser / Mobile PWA"]
    end

    subgraph Frontend["Frontend Process (port 3050)"]
        NextJS["Next.js 16.3.3 (React 19 · Node 20 · @next/swc)"]
    end

    subgraph Nginx["Reverse Proxy"]
        nginx["nginx (Proxy & TLS Termination)"]
    end

    subgraph Backend["Backend Process — Modular Monolith (port 8000)"]
        direction TB
        FastAPI["FastAPI · Uvicorn (4 workers)"]

        subgraph Routers["api_v2_routers/"]
            R_auth["auth"]
            R_learners["learners"]
            R_lessons["lessons"]
            R_plans["study_plans"]
            R_diag["diagnostics"]
            R_gamif["gamification"]
            R_onboard["onboarding"]
            R_parents["parents"]
            R_billing["billing"]
            R_consent["consent / consent_renewal"]
            R_popia["popia"]
            R_jobs["jobs"]
            R_system["system"]
        end

        subgraph Services["services/"]
            S_auth["auth_service"]
            S_learner["learner_service"]
            S_consent["consent_service"]
            S_plans["study_plan_service"]
            S_gamif["gamification_service"]
            S_parent["parent_service"]
            S_popia["popia_service"]
            S_billing["billing_service"]
            S_job["job_service"]
        end

        subgraph Modules["modules/ (self-contained engines)"]
            M_diag["diagnostics/"]
            M_lessons["lessons/"]
            M_caps["caps/"]
            M_ml["ml_sidecar/ (feature-flagged)"]
        end

        subgraph Repos["repositories/"]
            Rep_pg["PostgreSQL repos (SQLAlchemy)"]
            Rep_redis["Redis repos"]
        end

        subgraph Domain["domain/ + core/"]
            Pydantic["Pydantic models / enums"]
            Core["config · middleware · DB pool · exceptions · observability"]
        end
    end

    subgraph Worker["Background Worker Process"]
        ARQWorker["ARQ Worker Process (arq app.core.arq_worker.WorkerSettings)"]
    end

    subgraph Infra["Infrastructure"]
        PG["PostgreSQL 16 / pgvector"]
        Redis["Redis 7 (Jobs Queue & Cache)"]
        Prom["Prometheus"]
        Grafana["Grafana"]
    end

    Browser --> nginx
    nginx --> NextJS
    nginx --> FastAPI
    FastAPI --> Routers
    Routers --> Services
    Routers --> Modules
    Services --> Repos
    Modules --> Repos
    Repos --> Domain
    Services --> Domain
    Routers --> Domain
    Repos --> PG
    Repos --> Redis
    Services --> Redis
    Redis --> ARQWorker
    ARQWorker --> Services
    Core --> Prom
    Prom --> Grafana
```

---

## Layered Dependency Direction

```mermaid
graph LR
    A["api_v2_routers"] --> B["services / modules"]
    B --> C["repositories"]
    C --> D["domain · core"]
    D --> E["stdlib · third-party"]
```

Arrows represent **allowed import direction** only. No upward imports permitted. Routers must never import directly from repositories (enforced via `.importlinter`).

---

## Bounded Contexts

| Context | Router | Service | Module |
|---|---|---|---|
| auth | `auth.py` | `auth_service.py` | — |
| learners | `learners.py` | `learner_service.py` | — |
| consent | `consent.py`, `consent_renewal.py` | `consent_service.py` | — |
| diagnostics | `diagnostics.py` | — | `modules/diagnostics/` |
| lessons | `lessons.py` | — | `modules/lessons/` |
| study_plans | `study_plans.py` | `study_plan_service.py` | `modules/caps/` |
| gamification | `gamification.py` | `gamification_service.py` | — |
| parent_portal | `parents.py` | `parent_service.py` | — |
| popia | `popia.py` | `popia_service.py` | — |
| billing | `billing.py` | `billing_service.py` | — |
| jobs | `jobs.py` | `job_service.py` | `app/jobs/` (ARQ tasks) |
| observability | `system.py` | — | `core/observability.py` |

---

## Background Worker Architecture: ARQ (No Celery)

EduBoost V2 uses **Redis 7 + ARQ** (`app/core/arq_worker.py`) exclusively for background job execution, async content staging, and periodic maintenance tasks.
- **Worker Configuration**: Defined in `app/core/arq_worker.py` via `WorkerSettings` (Redis pool, cron jobs, retry policies).
- **Task Definitions**: Managed under `app/jobs/` with typed parameters and structured error handling.
- **Decommissioning**: Celery and Celery Beat have been completely decommissioned. Zero Celery imports are permitted across `app/` (enforced via `test $(git grep -rlE "^\s*(import|from)\s+celery\b" app/ | wc -l) -eq 0`).

---

## Infrastructure Note

The inference ML sidecar (`modules/ml_sidecar/`) is:
- Loaded in-process via `requirements-ml.txt` extras.
- Gated behind feature flags — **not active in production today**.
- Not a separately deployed microservice. Any future extraction requires a new ADR.

