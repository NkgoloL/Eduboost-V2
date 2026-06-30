# EduBoost V2 Production Grade P0 Blocker Tracker

Date: 2026-06-01
Status: Supporting roadmap tracker. Root `TODO.md` remains the authoritative execution index.
Goal: Close all audit gaps, reach production readiness, and enforce backend coverage greater than or equal to 80 percent.

## Execution Rules

- Treat root `TODO.md` as the single authoritative execution tracker; use this file as supporting P0 blocker detail.
- Do not mark a task done without evidence committed in repo.
- Every completed item must include test or command output in PR notes.

## P0 Blockers (Must Complete First)

### 1) Fix test bootstrap and environment parsing

- [ ] Update environment parsing for ALLOWED_ORIGINS so tests do not fail on plain-string values.
- [ ] Ensure app startup works with .env, .env.example, and CI env.
- [ ] Add a settings unit test that validates accepted ALLOWED_ORIGINS formats.
- [ ] Add a startup smoke test that imports app.api_v2 without SettingsError.

Acceptance criteria:
- pytest collection runs without ModuleNotFoundError or SettingsError.
- CI and local test bootstrap use the same deterministic settings contract.

### 2) Enforce one authoritative deployment target

- [ ] Pick one production target and document it as canonical (Azure Container Apps or Docker Compose, but one source of truth).
- [ ] Remove or archive non-authoritative deployment docs/manifests from active runbooks.
- [ ] Fix docker-compose.prod.yml and nginx config path mismatch.
- [ ] Align reverse proxy upstreams with defined services only.
- [ ] Add deployment smoke validation script for the canonical path.

Acceptance criteria:
- Production deployment docs and manifests are internally consistent.
- A clean deployment dry run succeeds from documented steps.

### 3) POPIA P0 compliance verification

- [ ] Complete end-to-end right-to-erasure verification across Postgres, Redis, and object storage.
- [ ] Complete consent enforcement verification on all learner-data paths.
- [ ] Ensure all sensitive POPIA actions emit audit events with consistent schema.
- [ ] Add POPIA compliance matrix test mapping route to consent gate to audit event.

Acceptance criteria:
- POPIA end-to-end tests pass and prove erasure and consent enforcement.
- Audit evidence exists for consent grant, revoke, export request, erasure request, and erasure completion.

### 4) Raise and enforce test coverage to 80 percent

- [ ] Set CI backend coverage gate to minimum 80 percent line coverage.
- [ ] Add branch coverage measurement and enforce non-zero branch data.
- [ ] Exclude dead legacy-only paths from gate only if formally archived and documented.
- [ ] Publish coverage report artifact per CI run.

Acceptance criteria:
- coverage.xml reports backend line coverage greater than or equal to 80 percent.
- CI fails on coverage regression below threshold.

## P1 High Priority Hardening

### 5) Security verification completion

- [ ] Convert penetration checklist into executable tests where possible.
- [ ] Add tests for token revocation, cross-tenant access denial, and auth rate limits.
- [ ] Add LLM safety tests for judiciary rejection and PII scrub enforcement.
- [ ] Complete and document breach response operational playbook contacts and timelines.

Acceptance criteria:
- Security checklist items are evidenced by tests or signed operational runbooks.
- No open critical security checklist item remains.

### 6) Dependency and vulnerability management

- [ ] Install and wire pip-audit in CI.
- [ ] Add npm audit and container image scan to release gate.
- [ ] Patch critical and high CVEs first.
- [ ] Create monthly dependency upgrade policy with compatibility test matrix.

Acceptance criteria:
- CI generates vulnerability reports every run.
- Release blocked on critical CVEs.

### 7) Production readiness checks and release controls

- [ ] Convert docs/release_checklist.md into a release gate checklist used in CI/CD.
- [ ] Add migration verification: alembic upgrade head and alembic downgrade smoke path in staging.
- [ ] Add readiness and health probes validation in staging.
- [ ] Add rollback drill documentation with verified steps.

Acceptance criteria:
- Tagged release requires all release gate checks green.
- Rollback procedure is tested and documented.

## P1 Coverage Workstream (Targeted Test Additions)

### 8) Add tests for low coverage core modules

- [ ] app/core/llm_gateway.py
- [ ] app/api_v2_routers/popia.py
- [ ] app/repositories/audit_repository.py
- [ ] app/services/popia_service.py
- [ ] app/core/security.py
- [ ] app/core/token_revocation.py
- [ ] app/modules/diagnostics/irt_engine.py

Per-module minimum target:
- [ ] Core and security modules: at least 85 percent
- [ ] POPIA routes and services: at least 90 percent
- [ ] Repository layer: at least 80 percent

### 9) Add integration and contract tests

- [ ] Auth flow: login, refresh, revoke, revoked-token denial.
- [ ] Guardian isolation: Guardian A cannot access Guardian B learner data.
- [ ] Full learner journey: consent, diagnostic, plan, lesson, report, erasure.
- [ ] Audit contract: event schema and append-only behavior.
- [ ] Deployment contract smoke tests against staging.

Acceptance criteria:
- Integration suite passes in CI.
- Coverage increase is sustained across 3 consecutive runs.

## P2 Governance and Documentation Cleanup

### 10) Eliminate contradictory status documents

- [ ] Publish one canonical current-state report and archive contradictory snapshots.
- [ ] Add report versioning and validity date section.
- [ ] Define ownership for status, security, compliance, and deployment docs.

### 11) Environment variable contract normalization

- [ ] Generate environment variable reference from app/core/config.py.
- [ ] Ensure docs/environment_variables.md matches runtime settings exactly.
- [ ] Add CI check that flags undocumented required settings.

### 12) Legacy decommission plan

- [ ] Mark legacy runtime paths with deprecation deadline.
- [ ] Remove legacy-only test and code paths after parity is confirmed.
- [ ] Keep explicit migration map from legacy path to V2 path.

Acceptance criteria:
- Legacy compatibility surface is minimized and time-boxed.

## CI Pipeline Requirements for Production Grade

- [ ] lint and type checks pass.
- [ ] unit plus integration tests pass.
- [ ] backend coverage greater than or equal to 80 percent.
- [ ] pip-audit, npm audit, and image scan pass policy.
- [ ] migration checks pass.
- [ ] release checklist gate passes.

## Definition of Done for Production Grade

- [ ] All P0 tasks complete with evidence.
- [ ] All P1 tasks complete or formally risk-accepted with written sign-off.
- [ ] Backend coverage gate enforced at greater than or equal to 80 percent in CI.
- [ ] POPIA end-to-end controls tested and passing.
- [ ] Canonical deployment path documented and reproducibly deployable.
- [ ] Security and vulnerability gates are active and green.

## Suggested Execution Order (Sprints)

Sprint 1
- P0 sections 1 and 2

Sprint 2
- P0 sections 3 and 4

Sprint 3
- P1 sections 5 and 6

Sprint 4
- P1 sections 7 to 9

Sprint 5
- P2 sections 10 to 12 and final production sign-off
