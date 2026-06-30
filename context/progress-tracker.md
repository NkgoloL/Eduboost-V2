# Progress Tracker

**Last updated:** 2026-06-12
**Authoritative trackers:** ../docs/roadmap/roadmap.md (17-phase plan), ../docs/todos/todo.md (North Star tasks)

Update after every completed RoadMap phase or major TODO milestone.

## Current Status

**Active RoadMap Phase:** Phase 8 (Privacy and Authorization Completion)
**Last completed:** Phase 7 (Deployment and Security Hardening) - 2026-06-12
**Next:** Phase 8 (Privacy and Authorization Completion)
**Quality gate:** RED (9/11 checks passing as of 2026-05-17)
**Local unit tests:** 2051 passed, 1 skipped, 1 warning

## RoadMap Phase Progress

### Phase 0 -- Branch, Evidence, and Audit Artifacts (complete)
- [x] Audit report added (../docs/release/eduboost-v2-technical-audit-2026-06-02.md)
- [x] ../docs/roadmap/roadmap.md created (17 phases)
- [x] Gap analysis added (Eduboost-V2_Gap_Analysis.md)
- [x] ../docs/todos/todo.md updated with 5 gap categories + beta period
- [x] Context files updated (this directory)
- [x] Clean implementation branch from master (phase-1/release-blocking-correctness)

### Phase 1 -- Release-Blocking Correctness Fixes (complete 2026-06-09)
- [x] 1.1 Fix compileall syntax error (no errors found; CI gate verified) in audit_todo_backlog.py
- [x] 1.1 Add CI compile gate for app and scripts (already active in ci-cd.yml)
- [x] 1.2 Fix all F821 (undefined name) findings (0 findings; gate passes)
- [x] 1.2 Add CI Ruff gate: E9,F63,F7,F82,F821 (already active; ~1,000 non-blocking debt in ruff_debt.md)

Evidence: `docs/release/phase_1_evidence.md`, `docs/backlog/ruff_debt.md`

### Phase 2 -- Practice Session Security (complete 2026-06-09)
- [x] 2.1 Authenticate practice session continuation routes (get_current_user + require_learner_write + require_active_consent on all 3 routes)
- [x] 2.1 Add tests for unauthorized/wrong-user/consent-denied
- [x] 2.2 Replace in-memory _SESSIONS with durable database storage (PracticeSessionRepository + Alembic migration)
- [x] 2.2 Add expiry (24h TTL) and cleanup behavior (practice_session_cleanup_job.py)
- [x] Dead _SESSIONS declaration removed from router.py (2026-06-10)

Evidence: `docs/release/phase_2_evidence.md`, `docs/release/phase_2_1_evidence.md`, PR #220

### Phase 3 -- Frontend Build Health (complete 2026-06-10)
- [x] 3.1 Reconcile frontend dependencies (dexie) - 651 packages, pnpm install --frozen-lockfile ✅
- [x] 3.2 Fix TypeScript errors - 0 runtime errors, 2 known non-blocking dexie type errors
- [x] 3.3 Fix Vitest TSX parsing - 147/147 tests passing in 26.55s ✅

Evidence: `docs/release/phase_3_evidence.md`, `../docs/roadmap/execution/phase_3_execution_plan.md`

### Phase 4 -- Runtime and Environment Alignment (complete 2026-06-10)
- [x] 4.1 Choose supported production Python version (3.12.3)
- [x] 4.2 Document decision (ADR-001 updated, ADR-026 created)
- [x] 4.3 Align Dockerfiles, docs, `.python-version`

Evidence: `docs/adr/ADR-026-python-version-alignment.md`

### Phase 5 -- Migrations and Schema Management (complete 2026-06-10)
- [x] 5.1 Repair migration graph and legacy exemptions
- [x] 5.2 Remove production startup schema repair from `app/api_v2.py`
- [x] 5.3 Prove migration correctness against a live PostgreSQL database
- [x] 5.4 Add migration checks to CI

Evidence: `docs/roadmap/execution/phase_5_implementation_report.md`, `docs/release/phase_5_evidence.md`, `docs/release/phase_5_implementation_audit.md`

### Phase 6 -- Durable Background Jobs (complete 2026-06-12)

Status: ✅ Complete — all 3 RoadMap acceptance criteria verified against live Docker stack
Branch: `phase-6/durable-background-jobs`

- [x] 6.1 Fix ARQ settings: `REDIS_URL` casing, `redis_settings` as class variable
- [x] 6.2 Wire worker into dev + prod Compose (docker-compose.yml, docker-compose.prod.yml)
- [x] 6.3 Migrate 3 critical routes → `enqueue_durable()`; 2 request-adjacent remain on `BackgroundTasks`
- [x] 6.4 Unit tests (5) and integration tests (3); all files compile clean
- [x] WorkerSettings namespace hygiene fixed (private `_cfg`, `_parsed`); RedisSettings init unified
- [x] Live Docker verification: restart-survival (6.4.3) ✅, worker startup health ✅, enqueue/dequeue proof ✅
- [x] Unit tests executed: 5/5 PASS on Python 3.12.3

Evidence: `docs/roadmap/execution/phase_6_execution_plan.md`, `docs/roadmap/execution/phase_6_implementation_report.md`, `docs/release/phase_6_evidence.md`, `docs/release/phase_6_implementation_audit.md`

### Phase 7 -- Deployment and Security Hardening (complete 2026-06-12)
- [x] 7.1 Stripe redirect URLs → `settings.PUBLIC_FRONTEND_URL` (config.py, stripe_client.py)
- [x] 7.1 `auth_extended.py` `FRONTEND_BASE` consolidated to `settings.PUBLIC_FRONTEND_URL`
- [x] 7.2 ACA Bicep CORS `allowedOrigins: ['*']` → parameterized `corsAllowedOrigins`
- [x] 7.3 CSP hardened: production uses nonce-based policy, no `unsafe-inline`
- [x] 7.4 HSTS conditional on `settings.is_production()` — absent in dev/test
- [x] 7.5 Nginx rate-limit zone corrected from `/api/v1/auth/` → `/api/v2/auth/`
- [x] 7.6 V1 route shim cleaned: guard removed, 410 tombstone registered unconditionally
- [x] 7.7 `/metrics` IP-restricted in production (RFC-1918 + loopback only)
- [x] 7.8 `docker-compose.prod.yml` annotated as local-only; ACA uses `@secure()` params
- [x] 7.9 ADR-028: ACA declared authoritative production deployment target
- [x] 7.10 Tests: `test_security_headers.py` rewritten (8 tests covering HSTS, CSP, nonce, uniqueness)
- [x] 7.10 Bug fixes: duplicate `_production_key_vault_url_required` removed from config.py
- [x] ADR-027 (observability access control) and ADR-028 (deployment target) committed

Evidence: `docs/roadmap/execution/phase_7_implementation_report.md`, `docs/release/phase_7_evidence.md`

### Phases 8-16
See ../docs/roadmap/roadmap.md for full phase plans. This tracker will be updated as phases are executed.

## Verified Baseline (Already Implemented)

These are repository-side complete but need CI/staging/production proof:

- Backend: 2051 unit tests passing, 355 API routes, 28 routers, 22 modules
- Content: 120 Grade 4 Math diagnostic items, 24 lessons live
- POPIA: Consent, audit, erasure, export workflows (partial)
- Auth: JWT + keyring, token revocation, Redis-backed
- ETL: Content Factory pipeline with provenance tracking
- Monitoring: 3 Grafana dashboards, Prometheus metrics, structured logging
- CI/CD: 42 workflow files (many need gate tightening per Phase 9)

## Gap Categories (from Gap Analysis)

| Gap | Category | RoadMap Phase | Status |
|-----|----------|:---:|--------|
| GAP-1 | Technical Debt | Phase 11 | Pending |
| GAP-2 | Security Posture | Phase 12 | Pending |
| GAP-3 | Frontend/Product | Phase 13 | Pending |
| GAP-4 | Operational Readiness | Phase 14 | Pending |
| GAP-5 | Governance/Process | Phase 15 | Pending |
| -- | Beta Period | Phase 16 | Pending |

## Decisions Made During Build

| Date | Decision | Rationale | Reference |
|------|----------|-----------|-----------|
| 2026-05 | V1 deleted, V2 modular monolith | Architecture audit recommendation | ../CHANGELOG.md |
| 2026-05 | Celery replaced by ARQ | Single-node simplicity, Redis-backed | Phase 6 |
| 2026-05 | Groq primary LLM, Anthropic fallback | Speed + quality balance | .env.example |
| 2026-05 | PostgreSQL audit trail (not RabbitMQ) | Async writes, simpler ops | core/audit.py |
| 2026-06 | 17-phase RoadMap adopted | Gap analysis revealed 5 uncovered categories | ../docs/roadmap/roadmap.md |
| 2026-06 | Python 3.12.3 selected as target | Align with CI and requirements generation | Phase 4 |

## Notes

- All tracking is now dual: ../docs/roadmap/roadmap.md for phases, ../docs/todos/todo.md for tasks
- Context files reference both; update them together
- The 5 gap categories (GAP-1 through GAP-5) were identified 2026-06-09
- Beta period (Phase 16) is the final gate before any production claim

| 2026-06-09 | Phase 1 complete (no fixes needed) | Codebase already clean; compileall + ruff gates pass | phase_1_evidence.md |
| 2026-06-09 | ~1,000 Ruff findings deferred to Phase 11 | Only correctness-blocking rules gated; style debt tracked | ruff_debt.md |
