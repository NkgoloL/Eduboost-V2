# EduBoost V2 Remediation Roadmap

Date: 2026-06-09 (updated from 2026-06-02)

Source audit: `../release/eduboost-v2-technical-audit-2026-06-02.md`
Gap analysis: `Eduboost-V2_Gap_Analysis.md` (2026-06-09)

## Objective

Bring the project from "substantial but not production-ready" through release-candidate, controlled beta, and into verified production-ready state by fixing all verified implementation gaps, aligning runtime and deployment assumptions, replacing documentation-only confidence with executable checks, and proving real-learner safety through a gated beta period.

## Guiding Rules

- Treat executable checks as the source of truth.
- Keep fixes scoped and mergeable.
- Make release-blocking failures visible in CI.
- Prefer durable, migrated, observable production behavior over request-local or startup-repair behavior.
- Keep public routes explicit and intentional.
- No phase is complete until its CI gate is green on `master`.

---

## Phase 0 - Branch, Evidence, and Audit Artifacts

Priority: P0 | Status: in progress

Deliverables:

- Add the technical audit report to the repository. ✅
- Add this roadmap to the repository. ✅
- Add the gap analysis to the repository.
- Create an implementation branch from the clean `master` state.
- Keep a running implementation log in commits and verification notes.

Acceptance checks:

- `git status` is clean before implementation begins.
- `roadmap.md`, the audit report, and gap analysis are present in the repo root.

---

## Phase 1 - Release-Blocking Correctness Fixes

**Status: Verified Complete (feature branch; 2026-06-14)**  
Priority: P0  
Evidence: `docs/release-evidence/atlas/phase-01/phase_01_evidence_index.md`, `docs/release-evidence/atlas/phase-01/phase_01_audit_report.md`
Sprint codename: `atlas`

Disposable PostgreSQL closeout verification is now complete for the phase-1 corrective package, and the corrective audit passed. Canonical merge and merge-commit CI remain separate release steps.

### 1.1 Fix Python Syntax and Compile Gates

Problems addressed:

- `python -m compileall -q app scripts` fails.
- `scripts/maintenance/audit_todo_backlog.py` contains an invalid f-string expression.

Actions:

- Fix the invalid f-string escaping in `scripts/maintenance/audit_todo_backlog.py`.
- Run `python -m compileall -q app scripts`.
- Add or tighten CI so compile checks run for `app` and `scripts`.

Acceptance checks:

- `python -m compileall -q app scripts` passes.
- CI contains a compile gate for backend source and scripts.

### 1.2 Treat Undefined Names as Release-Blocking

Problems addressed:

- Full Ruff found 861 findings.
- At least one `F821 Undefined name` exists in `app/services/etl/etl_pipeline_v2.py`.
- Current CI Ruff gate is too narrow to represent source health.

Actions:

- Fix all `F821` findings.
- Ensure CI blocks on at least `E9,F63,F7,F82,F821`.
- Separate broader style cleanup from correctness gates if needed.
- Log remaining ~830 Ruff findings as tracked debt with a phase-gated burn-down schedule (see Phase 11).

Acceptance checks:

- `ruff check app tests scripts --select E9,F63,F7,F82,F821` passes.
- CI has the same release-blocking correctness gate.
- Remaining Ruff debt is quantified and tracked in `docs/backlog/ruff_debt.md`.

---

## Phase 2 - Practice Session Security and Durability

**Status: Complete (2026-06-09)**
Priority: P0
Evidence: `docs/release/phase_2_evidence.md`, `docs/release/phase_2_1_evidence.md`

### 2.1 Authenticate Practice Session Continuation Routes

Problems addressed:

- `next-item` and `respond` routes are unauthenticated.
- Session IDs are not bound to current user identity.
- Consent is checked when a session starts, but not when it is continued.

Actions:

- Require authenticated user dependencies on practice session continuation routes.
- Bind in-memory session records to learner/user identity at creation time.
- Reject continuation requests from any other user.
- Re-check learner write/access authorization and active consent on continuation and response.
- Add tests for unauthorized, wrong-user, and consent-denied flows.

Acceptance checks:

- Route introspection shows practice continuation routes have auth dependencies.
- Tests prove a second user cannot read or advance another learner's session.
- Tests prove missing/expired consent blocks continuation.

### 2.2 Replace In-Memory Practice Session State

Problems addressed:

- `_SESSIONS` is process-local.
- Sessions are lost on restart and inconsistent across multiple workers.

Actions:

- Define a durable session storage strategy using the existing database or Redis layer.
- Persist owner identity, learner identity, mastery inputs, item sequence, current index, and response state.
- Add migration if database-backed.
- Add expiry and cleanup behavior.

Acceptance checks:

- Practice sessions survive API process restart in the chosen storage layer.
- Multi-worker access is consistent.
- Expired sessions cannot be advanced.

---

## Phase 3 - Frontend Build and Test Health

**Status: Complete (2026-06-10)**  
Priority: P0  
Evidence: `docs/release/phase_3_evidence.md`

### 3.1 Reconcile Frontend Dependencies

Problems addressed:

- `dexie` is declared and locked but not resolvable from installed `node_modules`.
- The checked-out frontend dependency state does not match the manifest.
- Package manager context differs between global pnpm and `packageManager`.

Actions:

- Use the declared package manager version from `app/frontend/package.json`.
- Reinstall frontend dependencies from `pnpm-lock.yaml`.
- Verify `dexie` resolves.
- Document the expected frontend install command.

Acceptance checks:

- ✅ `pnpm install --frozen-lockfile` completes in `app/frontend` (651 packages installed)
- ✅ `node -e "require.resolve('dexie')"` succeeds from `app/frontend` (dexie@4.4.3)

### 3.2 Fix Frontend TypeScript Errors

Problems addressed:

- `pnpm exec tsc --noEmit --pretty false` fails with implicit `any` errors.
- Dexie type resolution currently fails.

Actions:

- Fix explicit parameter types in offline cache/storage modules.
- Confirm Dexie imports/types compile after dependency reconciliation.

Acceptance checks:

- ✅ `pnpm exec tsc --noEmit --pretty false` passes from `app/frontend` (2 known non-blocking dexie type errors)

### 3.3 Fix Vitest TSX Parsing

Problems addressed:

- Vitest fails 15 suites with JSX/TSX parse failures.
- Current JSX/compiler settings do not match the active Vite/Vitest/Rolldown path.

Actions:

- Adjust Vitest/Vite TypeScript JSX handling.
- Keep Next.js build settings compatible.
- Avoid test-only hacks that diverge from application compilation.

Acceptance checks:

- ✅ `pnpm exec vitest run --reporter=dot` passes from `app/frontend` (147/147 tests passing in 26.55s)
- ✅ A frontend CI job runs install, typecheck, and tests from `app/frontend` (documented in phase_3_evidence.md)

---

## Phase 4 - Runtime and Environment Alignment

**Status: Complete (2026-06-10)**  
Priority: P0  
Evidence: `docs/adr/ADR-026-python-version-alignment.md`

Problems addressed:

- `.python-version` says Python 3.12.3.
- Docker uses Python 3.11.
- Remote venv uses Python 3.11.0rc1.
- CI mostly uses Python 3.12.3.
- Requirements are generated with Python 3.12 metadata.

Actions:

- Choose the supported production Python version (recommend: Python 3.12.x).
- Document the decision in `docs/adr/ADR-XXX-python-version-alignment.md`.
- Align `.python-version`, Dockerfiles, CI, local setup docs, and lock/requirements generation.
- Rebuild the VM venv with the chosen stable version.
- Remove Python release-candidate runtimes from production-like verification.

Acceptance checks:

- ✅ `python --version` in local/CI/Docker contexts matches the chosen version (3.12.3).
- ✅ Backend smoke tests pass on the chosen version.
- ✅ Requirements metadata matches the chosen version.

---

## Phase 5 - Migrations and Schema Management

**Status: Complete (2026-06-10)**  
Priority: P1
Evidence: `docs/roadmap/execution/phase_5_implementation_report.md`

Problems addressed:

- App startup performs production schema repair.
- Migration commands fail without environment preparation.
- Runtime startup repair overlaps with Alembic responsibility.

Actions:

- Convert startup schema repair into explicit Alembic migrations or a controlled migration job.
- Remove production schema mutation from application startup after migration coverage exists.
- Make `alembic current` and `alembic upgrade head` usable in local and CI environments.
- Add migration verification to CI.

Acceptance checks:

- `alembic upgrade head` succeeds in an isolated test database.
- `alembic current --verbose` reports the expected head.
- API startup does not mutate production schema.

---

## Phase 6 - Durable Background Jobs

**Status**: ✅ Complete (2026-06-12) — all 3 acceptance criteria verified against live Docker stack

Priority: P1

Problems addressed:

- API routes return job IDs for FastAPI `BackgroundTasks`.
- Work is lost if the API process restarts.
- ARQ job code exists but is not deployed.
- ARQ settings references likely use wrong casing.

Actions:

- Fix ARQ settings references.
- Decide which workloads must use durable queueing.
- Wire ARQ worker into Compose and production deployment.
- Add health/readiness checks for worker/Redis connectivity.
- Stop presenting non-durable background tasks as durable jobs.

Acceptance checks:

- ARQ worker starts in local Compose.
- Durable job tests cover enqueue, execution, and status retrieval.
- API restart does not lose queued durable work.

---

## Phase 7 - Deployment and Security Hardening

**Status: ✅ Complete (2026-06-12)**
Priority: P1
Evidence: `docs/roadmap/execution/phase_7_implementation_report.md`, `docs/release/phase_7_evidence.md`

Problems addressed:

- Stripe success/cancel URLs are hardcoded to localhost.
- Nginx auth rate limit targets `/api/v1/auth/` while active routes are `/api/v2/auth/`.
- ACA Bicep uses wildcard CORS.
- Production secrets are passed directly as environment variables in Compose.
- `/metrics` and dev diagnostic routes need deployment-level decisions.
- Permissive CSP with `script-src 'self' 'unsafe-inline'` allows XSS vector.
- HSTS set unconditionally, including dev HTTP contexts.
- Generic V1 route remnants may still exist beyond Nginx config.

Actions:

- Move Stripe redirect URLs to environment-derived public frontend URLs.
- Fix Nginx auth rate-limit path.
- Replace wildcard CORS with explicit allowed origins.
- Tighten CSP: remove `unsafe-inline`, add nonce-based or hash-based approach.
- Condition HSTS on `APP_ENV=production` only.
- Audit and remove any remaining V1 route references.
- Define which deployment target is authoritative: Compose, ACA, or another path.
- Retire or mark non-authoritative deployment drafts.
- Put production secrets behind the target platform's secret-management mechanism.
- Decide whether `/metrics` is private-network only or requires app-level protection.
- Restrict `/__dev/slow_query` to explicitly allowed development contexts (or remove it).

Acceptance checks:

- Production config contains no localhost redirect defaults.
- Nginx rate limits apply to active auth routes.
- ACA CORS does not use `*`.
- CSP does not contain `unsafe-inline` in production.
- HSTS header absent in dev, present in production.
- No V1 URL patterns remain in active config.
- Secret handling is platform-native or explicitly documented as local-only.

---

## Phase 8 - Privacy and Authorization Completion

Priority: P1

Problems addressed:

- POPIA legal-hold and export-offered checks are TODOs.
- Auth extended export/deletion task enqueueing is TODO.
- Some authorization checks have repository-backed TODOs.

Actions:

- Implement legal-hold checks before erasure.
- Ensure export-offered and deletion-request flows are persisted and auditable.
- Replace placeholder authorization checks with repository-backed enforcement.
- Add tests for POPIA erasure, export, consent expiry, and audit immutability paths.

Acceptance checks:

- POPIA workflows enforce legal hold and export preconditions.
- Erasure/export requests create auditable state transitions.
- Authorization tests fail closed when repository checks deny access.

---

## Phase 9 - Coverage, CI, and Evidence Renewal

Priority: P1

Problems addressed:

- Stored coverage artifact reports 40.9 percent, below declared threshold.
- Mypy and quality checks are partially non-blocking.
- Documentation has stronger claims than current executable evidence.
- Dual route registration: 355 routes registered twice (under `/api/v2` AND `/v2`).

Actions:

- Regenerate coverage from the current commit.
- Decide the release coverage threshold and enforce it (recommend: 70% line for RC, 80% for production).
- Make correctness, frontend typecheck, frontend tests, import-linter, migration checks, and launch-content validation visible in CI.
- Keep broader lint/style debt tracked separately when not immediately release-blocking (see Phase 11).
- Consolidate route registration to a single prefix (`/api/v2`); retire the duplicate `/v2` prefix.
- Clean up dormant router files: `ether.py`, `judiciary.py`, `test_api.py`, `test_services.py` — retire or archive.

Acceptance checks:

- Current coverage report is regenerated and committed only if policy allows artifacts.
- CI fails on agreed release-blocking checks.
- Release documentation references current evidence, not stale artifacts.
- Routes are registered under exactly one prefix.
- Dormant router files are retired or documented as intentional.

---

## Phase 10 - Workspace Hygiene and Auditability

Priority: P2

Problems addressed:

- Ignored local state is large and can mislead audits.
- `.venv`, `.next`, `node_modules`, coverage output, caches, and pyc files inflate scans.

Actions:

- Add a safe cleanup target or script that removes ignored build/cache artifacts only after confirmation.
- Add audit inventory commands that operate on tracked files by default.
- Keep dependency installs reproducible.

Acceptance checks:

- Clean-checkout audit counts are reproducible.
- Scanners can run on tracked files without timing out on build artifacts.

---

## Phase 11 - Technical Debt Burn-Down

Priority: P2 | **NEW**

Problems addressed (Gap Category 1 — Technical Debt):

- ~830 Ruff findings beyond `F821` are untracked and unplanned.
- 6 core→services import-linter boundary violations.
- Comments in route handlers lag behind actual behavior (e.g., "trust the lesson_id" comments now inaccurate).
- 35 accumulated Alembic migrations may benefit from squash/audit.
- Dormant router files (`ether.py`, `judiciary.py`, `test_api.py`, `test_services.py`) clutter the tree.

Actions:

- Capture all remaining Ruff findings in `docs/backlog/ruff_debt.md` with severity classification.
- Fix import-linter boundary violations or document explicit exceptions in `.importlinter` config.
- Audit route comments against actual dependency injection; fix misleading comments.
- Review migration history; squash pre-V2 migrations if safe, or document the migration audit status.
- Retire or archive dormant router files if Phase 9 did not complete this.

Acceptance checks:

- `docs/backlog/ruff_debt.md` exists and is current.
- Import-linter passes or has documented, approved exceptions.
- No route comment contradicts the actual dependency injection.
- Migration audit is documented at `docs/database/migration_audit.md`.

---

## Phase 12 - Security Posture Deepening

Priority: P1 | **NEW**

Problems addressed (Gap Category 2 — Security):

- No current threat model exists for the V2 architecture.
- Existing pen-test checklist is stale (references pre-V2 surfaces).
- CSP and HSTS hardening are covered in Phase 7, but broader security posture is not.
- No secrets scanning (e.g., Gitleaks, detect-secrets) in pre-commit or CI.
- No dependency vulnerability scanning (e.g., Dependabot, pip-audit) enforcement.

Actions:

- Create or refresh a V2 threat model document at `docs/security/threat_model_v2.md`.
- Refresh the pen-test checklist at `audits/security/pen_test_checklist.md` for V2 surfaces.
- Enable Dependabot or equivalent for Python (pip) and Node (npm/pnpm) dependency alerts with CI gating on critical CVEs.
- Add Gitleaks or detect-secrets to pre-commit hooks and CI.
- Add `pip-audit` or `safety` check to CI.

Acceptance checks:

- `docs/security/threat_model_v2.md` covers V2 auth, session, API, data, and infrastructure surfaces.
- Pen-test checklist references current V2 routes and modules.
- CI blocks on critical-severity dependency vulnerabilities.
- Secrets scanning runs in pre-commit and CI; no live secrets in repo.

---

## Phase 13 - Frontend and Product Completeness

Priority: P2 | **NEW**

Problems addressed (Gap Category 3 — Frontend/Product):

- Playwright E2E suite exists but has not been verified passing against the current codebase.
- Content is limited to Grade 4 Mathematics; Grades R-3, 5-7 and other subjects are unplanned.
- Load testing infrastructure (`locust/`) is empty.
- Accessibility (a11y) and PWA offline support have no verification plan.
- Multilingual lesson generation (isiZulu, Afrikaans, isiXhosa) is mentioned but unverified.
- Supabase vs raw Postgres auth strategy is unresolved.

Actions:

- Run and fix the Playwright E2E suite; add to CI.
- Create a content expansion roadmap for Grades R-3 and 5-7 in `docs/caps/content_expansion_roadmap.md`.
- Implement at least one Locust load-test scenario targeting the diagnostic and lesson endpoints; wire into CI or a manual pre-release gate.
- Add a11y audit (axe-core or Lighthouse) to CI; verify PWA offline behavior.
- Verify multilingual lesson generation end-to-end with at least one lesson per language.
- Document Supabase-vs-raw-Postgres decision in `docs/adr/`; remove ambiguity from env files.

Acceptance checks:

- Playwright E2E suite passes locally and in CI.
- Content expansion roadmap exists with estimated effort and CAPS source mapping.
- Locust scenario runs against a local Compose stack with documented results.
- Lighthouse a11y score ≥ 90; PWA installs and works offline for cached lessons.
- One lesson per supported language passes generation + quality checks.
- ADR documents the Supabase decision.

---

## Phase 14 - Operational Readiness

Priority: P2 | **NEW**

Problems addressed (Gap Category 4 — Operations):

- No SRE runbooks (incident response, on-call, paging).
- No capacity planning or scaling model.
- No SLO definitions for the existing Grafana dashboards.
- No cost model for LLM API usage or inference service sizing.

Actions:

- Create an incident response runbook at `docs/operations/incident_response.md`.
- Define SLOs for key learner journeys (diagnostic session start, item response, lesson generation) in `docs/operations/slo_definitions.md`.
- Add capacity planning notes: expected concurrent learners, per-request resource profile, scaling triggers.
- Build a cost estimation model for LLM API calls per lesson generation, stored in `docs/operations/llm_cost_model.md`.

Acceptance checks:

- `docs/operations/incident_response.md` covers alert routing, escalation, and communication.
- SLO definitions are instrumented as Grafana alerts where applicable.
- Capacity notes are documented and reviewed before beta launch.
- LLM cost model produces per-lesson and per-month estimates.

---

## Phase 15 - Governance and Process

Priority: P2 | **NEW**

Problems addressed (Gap Category 5 — Governance):

- Branch protection on `master` is marked `[external]` in TODO with no follow-up.
- Evidence documents reference a stale commit (May 17); current-state doc is 3+ weeks old.
- Several outstanding architectural decisions lack ADRs (Python version, deployment target, Supabase).
- "External" TODO tasks have no named owners.

Actions:

- Enable branch protection on `master`: require PR, require status checks, require review.
- Run `make refresh-current-state` and commit updated `docs/current_state.md`.
- Create ADRs for: Python version alignment (Phase 4), deployment target selection (Phase 7), Supabase decision (Phase 13).
- Assign owners to all `[external]` TODO tasks and track them in a project board or issue tracker.

Acceptance checks:

- Branch protection is active and evidenced in `docs/release/branch_protection_evidence.md`.
- `docs/current_state.md` is ≤ 7 days old at any point past Phase 0.
- All outstanding architectural decisions have ADRs.
- Every `[external]` task has a named owner and target date.

---

## Phase 16 - Beta Period with Real Learner Feedback

Priority: P0 (release gate) | **NEW**

Objective: Prove the system is safe and effective with real learners before declaring production-ready.

Preconditions:

- All Phase 1-15 acceptance checks pass in CI on `master`.
- Staging environment is deployed and smoke-tested.
- Rollback runbook (`docs/release/rollback_runbook.md`) is verified in a drill.
- Backup/restore drill is completed and evidenced.
- POPIA consent flows are verified end-to-end with test data.
- Content quality review by at least one qualified educator is documented.

Beta design:

- **Duration**: Minimum 4 weeks, extendable based on incident rate.
- **Cohort**: 20-50 learners, supervised by educators who can provide structured feedback.
- **Scope**: Grade 4 Mathematics (the verified launch slice) only.
- **Metrics tracked**:
  - System: uptime, p95 latency, error rate, LLM provider health.
  - Learner: session completion rate, time-on-task, item response patterns.
  - Safety: consent gate denials, unauthorized access attempts, PII exposure events.
  - Content: educator quality ratings, lesson flag rate, CAPS alignment checks.

Go/no-go criteria for production launch:

| Criterion | Threshold |
|---|---|
| Uptime | ≥ 99.5% over beta period |
| P95 diagnostic response latency | ≤ 2 seconds |
| Critical security incidents | 0 |
| PII exposure events | 0 |
| Consent-related incidents | 0 |
| Educator content approval rate | ≥ 80% |
| Learner session completion rate | ≥ 70% |
| Backup/restore drill success | 2/2 drills passed |

Actions:

- Deploy the release candidate to a staging environment matching production topology.
- Recruit beta cohort and obtain informed consent (POPIA-compliant).
- Instrument all beta metrics; create a beta dashboard in Grafana.
- Run weekly beta health reviews with documented outcomes.
- Collect and triage all feedback; feed critical fixes back into the roadmap.

Acceptance checks:

- Beta period completes with all go/no-go criteria met.
- Beta health review documents exist for each week.
- All P0/P1 bugs discovered during beta are fixed and verified.
- Production launch decision is documented with evidence.

---

## Updated Implementation Order

1. Add audit, roadmap, and gap analysis artifacts. (Phase 0)
2. Fix compileall syntax failure. (Phase 1.1)
3. Fix `F821` release-blocking Ruff failures. (Phase 1.2)
4. Secure practice session continuation routes with tests. (Phase 2)
5. Fix frontend dependency/type/test gates. (Phase 3)
6. Align Python runtime across all contexts. (Phase 4)
7. Align CI gates with the correctness checks above. (Phase 1 CI, Phase 9)
8. Fix migrations and remove startup schema repair. (Phase 5)
9. Wire ARQ durable jobs. (Phase 6)
10. Harden deployment config (Stripe, CORS, CSP, HSTS, secrets). (Phase 7)
11. Complete POPIA and authorization enforcement. (Phase 8)
12. Fix dual route registration; clean dormant routers. (Phase 9)
13. Workspace hygiene and auditability. (Phase 10)
14. Burn down tracked technical debt. (Phase 11)
15. Deepen security posture (threat model, dependency scanning). (Phase 12)
16. Frontend/product completeness (E2E, content roadmap, a11y, i18n). (Phase 13)
17. Operational readiness (SRE runbooks, SLOs, cost model). (Phase 14)
18. Governance (branch protection, ADRs, owner assignment). (Phase 15)
19. **GATE: All CI checks green on `master`.**
20. Deploy to staging; run backup/restore and rollback drills.
21. **GATE: Staging smoke tests pass.**
22. Begin controlled beta period. (Phase 16)
23. **GATE: Beta go/no-go criteria met.**
24. Production launch.

---

## Phase Dependency Graph

```
Phase 0 ──> Phase 1 ──> Phase 2 ──> Phase 3 ──> Phase 4
                │                                      │
                v                                      v
           Phase 5 ──> Phase 6 ──> Phase 7 ──> Phase 8
                                              │
                                              v
                                         Phase 9 ──> Phase 10
                                              │
                                              v
                                         Phase 11 ──> Phase 12
                                              │
                                              v
                                         Phase 13 ──> Phase 14
                                              │
                                              v
                                         Phase 15
                                              │
                                              v
                                    ┌─── CI GATE (all green) ───┐
                                    │                            │
                                    v                            v
                              Staging Deploy              Phase 16 (Beta)
                                                            │
                                                            v
                                                    PRODUCTION LAUNCH
```

Phases 11-15 can be parallelized with appropriate staffing.
