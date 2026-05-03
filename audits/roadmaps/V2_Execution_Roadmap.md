# EduBoost V2 — Execution Roadmap

**Purpose:** This roadmap mirrors the existing audit-driven execution style, but for the V2 architectural pivot introduced in `docs/architecture/V2_ARCHITECTURE.md`.

## Phase 0 — Baseline
- [x] Scaffold `app/core`, `app/domain`, `app/repositories`, `app/services`
- [x] Add `app/api_v2.py`
- [x] Add MkDocs + mkdocstrings documentation baseline

## Phase 1 — Core Vertical Slices
- [x] Learner read flow in V2
- [x] Append-only PostgreSQL audit target in V2
- [x] Auth/session and refresh-token rotation in V2
- [x] Study-plan generation flow in V2
- [x] Parent reporting flow in V2
- [x] Diagnostic flow in V2
- [x] Redis-backed quota/caching service in V2

## Phase 2 — Runtime Promotion
- [x] Add `docker-compose.v2.yml`
- [x] Add `docker/Dockerfile.v2`
- [x] Make V2 the default documented runtime entrypoint
- [x] Isolate legacy runtime as compatibility mode only (documentation/runtime guidance)

## Phase 2.5 — Route Surface Promotion
- [x] Create dedicated `app/api_v2_routers/*` package
- [x] Move active V2 endpoints behind dedicated V2 router modules
- [x] Migrate lessons, gamification, system, and assessments into V2 router modules

## Phase 2.6 — Deep Replacement
- [ ] Replace simplified V2 placeholder implementations with fully native V2 logic
- [ ] Remove remaining legacy module dependencies from V2 services
- [ ] Make V2 the sole operational architecture

## Phase 3 — Full Replacement
- [ ] Migrate remaining legacy routes into V2 boundaries
- [ ] Remove Celery dependence from active product paths
- [ ] Remove RabbitMQ dependence from active product paths
- [ ] Retire inference-microservice-first assumptions from the main product path
- [ ] Consolidate auth/RBAC across all runtime paths
- [ ] Complete parent, learner, diagnostic, audit, and system route replacement

## Phase 4 — V2 Launch Readiness
- [ ] V2 docs fully replace legacy setup docs
- [ ] V2 quality gates cover new API surface
- [ ] V2 runtime becomes primary deployment target
- [ ] Legacy runtime explicitly marked deprecated
