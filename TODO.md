# EduBoost V2 — North Star TODO

**Purpose:** Execution-focused North Star for the next phase. This reflects the current green local backend unit baseline and separates repository-side completion from CI, runtime, external, legal, security, product, and beta-launch evidence.

**Last updated:** 2026-05-14  
**Latest local backend unit result:** `1702 passed, 29 skipped, 0 warnings`

## Status vocabulary

- `[x]` done: completed and locally/repository-side verified or explicitly confirmed.
- `[verify]` implemented but needs CI proof, staging proof, runtime evidence, or captured artefact.
- `[ ]` open: not done.
- `[external]` requires a person/system outside normal code work.
- `[post-beta]` cannot be completed until beta has actually run.
- `[blocked]` cannot proceed until predecessor evidence exists.

---

## 0. Current project state

- [x] Production-readiness backlog domains 05–20 have repository-side implementation evidence, docs, check scripts, unit tests, and Makefile targets.
- [x] Domains 00–04 are treated as previously integrated into the repository-side baseline, with remaining legal/manual/runtime items separated below.
- [x] POPIA/consent/audit/source-evidence repairs integrated.
- [x] AuthService and legacy unit-test compatibility repairs integrated.
- [x] Alembic migration graph repair from `code_338` integrated.
- [x] Full backend unit suite locally green: `1702 passed, 29 skipped, 0 warnings`.
- [x] Cluster H phantom-entry problem identified and converted into concrete remediation tasks.
- [x] Documentation claim discipline established: repository evidence must not be represented as legal, runtime, deployment, or launch approval.
- [ ] EduBoost is **not public-beta-ready** with real learner data.
- [ ] EduBoost is **not production-launch-ready**.
- [ ] Next milestone: **CI green -> staging execution evidence -> controlled beta go/no-go**.

---

# 10-step execution sequence

## 1. Freeze the local green baseline

| ID | Task | Evidence required | Status |
|---|---|---|---|
| NS-01 | Apply Alembic migration graph repair. | Migration graph test passes. | [x] |
| NS-02 | Rerun full unit suite. | `pytest -c pytest.ini tests/unit -q --no-cov` shows `1702 passed, 29 skipped`. | [x] |
| NS-03 | Commit migration graph repair and related POPIA/AuthService repairs. | Git commit containing repair files. | [ ] |
| NS-04 | Record local test evidence. | `docs/release/unit_test_evidence.md` contains full output. | [ ] |
| NS-05 | Triage non-failing warnings. | Warnings documented as accepted, fixed, or tracked. | [ ] |

Current warnings to track:

- Pydantic `model_version` protected namespace warning.
- AsyncMock unawaited coroutine warning in lesson repository test.
- AsyncMock unawaited coroutine warning in diagnostic repository/base test.
- AsyncMock unawaited coroutine warning in Redis lesson service test.

---

## 2. Make CI authoritative

| ID | Task | Evidence required | Status |
|---|---|---|---|
| NS-06 | Trigger GitHub Actions on `master`. | Passing Actions run URL committed to `docs/release/ci_evidence.md`. | [ ] |
| NS-07 | Ensure full unit suite runs in CI. | CI output with pass/skip counts. | [ ] |
| NS-08 | Ensure OpenAPI drift check runs in CI. | CI output proving `make openapi-check` passes. | [verify] |
| NS-09 | Ensure migration graph check runs in CI. | CI output proving migration graph is linear and resolvable. | [ ] |
| NS-10 | Ensure POPIA gate/sweep runs in CI. | CI output proving POPIA checks pass. | [ ] |
| NS-11 | Ensure frontend lint/type/unit checks run in CI. | CI output for lint, type-check, and tests. | [ ] |
| NS-12 | Add/verify branch protection on `master`. | Screenshot/settings export in `docs/release/branch_protection_evidence.md`. | [external] |

---

## 3. Repair release-governance evidence and Cluster H inflation

| ID | Cluster H | Task | Evidence required | Status |
|---|---|---|---|---|
| NS-13 | H-01 | Run `make refresh-current-state` on clean checkout. | Committed `docs/current_state.md` with timestamp/current gate results. | [ ] |
| NS-14 | H-02 | Create sign-off manifest with blank named fields. | `docs/release/sign_off_manifest.md`. | [ ] |
| NS-15 | H-03 | Create rollback runbook. | `docs/release/rollback_runbook.md` with API/frontend/database rollback commands and Alembic downgrade target. | [ ] |
| NS-16 | H-04 | Create post-deploy smoke checklist. | `docs/release/post_deploy_smoke_checklist.md` covering `/health/deep`, login, lesson generation, consent grant, POPIA export. | [ ] |
| NS-17 | H-05 | Create release bundle index. | `docs/release/release_bundle_v1.0.0-rc2.md` with real links only. | [ ] |
| NS-18 | H-06 | Add PR template. | `.github/PULL_REQUEST_TEMPLATE.md`. | [ ] |
| NS-19 | H-07 | Create release hygiene checklist. | `docs/release/release_hygiene_checklist.md`. | [ ] |
| NS-20 | H-14 | Create release state snapshot. | `docs/release/release_state_snapshot.md` with SHA, test counts, TODO counts, known issues, deferred items. | [ ] |
| NS-21 | H-17 | Create audit trail index. | `docs/release/audit_trail_index.md`. | [ ] |
| NS-22 | H-26 | Replace terminal Cluster H phantom entries with final closure certificate. | `docs/release/final_closure_certificate.md`, signed only at release. | [external] |
| NS-23 | H cleanup | Update `docs/project_status.md` by deleting/consolidating phantom Cluster H entries. | Single honest `Cluster H — Beta Release Governance` section linking evidence. | [ ] |

---

## 4. Prove database and migration runtime behavior

| ID | Task | Evidence required | Status |
|---|---|---|---|
| NS-24 | Run `alembic upgrade head` against disposable PostgreSQL. | `docs/release/migration_evidence.md` with full output. | [ ] |
| NS-25 | Run schema integrity check against disposable DB. | Captured output in migration evidence. | [ ] |
| NS-26 | Run downgrade/rollback path where supported. | Rollback evidence or documented non-downgrade rationale. | [ ] |

---

## 5. Prove frontend/browser behavior against backend

| ID | Task | Evidence required | Status |
|---|---|---|---|
| NS-27 | Run frontend coverage. | `docs/release/frontend_test_evidence.md`. | [ ] |
| NS-28 | Run Playwright/browser E2E against live local or staging backend. | Browser E2E output and environment details. | [ ] |
| NS-29 | Verify critical UI flows. | Evidence for login, dashboard, lesson generation, consent, POPIA export. | [ ] |
| NS-30 | Verify PWA/offline sync implementation status. | Implemented endpoint evidence or explicit deferred scope entry. | [ ] |
| NS-31 | Verify parent dashboard implementation status. | Passing test/live evidence or explicit deferred scope entry. | [ ] |

---

## 6. Prove observability, backup, restore, rollback, and operator readiness

| ID | Cluster H | Task | Evidence required | Status |
|---|---|---|---|---|
| NS-32 | H-19 | Create operator runbook. | `docs/release/operator_runbook.md`. | [ ] |
| NS-33 | H-20 | Configure uptime monitor for `GET /api/v2/health/deep`. | `docs/release/monitoring_evidence.md`. | [external] |
| NS-34 | H-21 | Wire Alertmanager to alert channel and fire test alert. | `docs/release/alertmanager_evidence.md`. | [external] |
| NS-35 | — | Execute backup dry-run. | Backup log with timestamp/checksum. | [ ] |
| NS-36 | — | Execute restore drill. | Restore log plus post-restore smoke test evidence. | [ ] |
| NS-37 | — | Execute rollback drill against staging/disposable environment. | Rollback evidence and runbook corrections. | [ ] |
| NS-38 | H-18 | Define change-control policy. | `docs/release/change_control_policy.md`. | [external] |
| NS-39 | — | Run incident tabletop. | `docs/release/incident_tabletop_evidence.md`. | [external] |

---

## 7. Complete POPIA, legal, security, and governance approvals

| ID | Cluster H | Task | Evidence required | Status |
|---|---|---|---|---|
| NS-40 | H-13 | Run POPIA sweep. | `docs/release/popia_sweep_evidence.md` with 0 issues or tracked exceptions. | [ ] |
| NS-41 | — | Submit POPIA docs for legal review. | Legal review record. | [external] |
| NS-42 | — | Obtain security review or pen-test decision. | Security sign-off or scoped finding report. | [external] |
| NS-43 | H-15 | Fill and sign sign-off manifest. | `docs/release/sign_off_manifest.md` with real names/dates/signatures. | [external] |
| NS-44 | H-16 | Create release decision log. | `docs/release/release_decision_log.md`. | [external] |

---

## 8. Resolve content/product readiness

| ID | Task | Evidence required | Status |
|---|---|---|---|
| NS-45 | Confirm current CAPS approved item count. | Item-bank report with approved vs candidate counts. | [ ] |
| NS-46 | Submit AI-generated candidate items for educator review. | Review/sign-off records. | [external] |
| NS-47 | Reach or explicitly defer launch item-bank threshold. | Approved item evidence or beta-scope limitation document. | [ ] |
| NS-48 | Add independent answer-key validation plan. | Implementation or documented external review workflow. | [ ] |
| NS-49 | Define supported beta grades/subjects/languages. | Beta product scope document. | [ ] |
| NS-50 | Create known issues and limitations file. | `docs/release/known_issues.md`; must not be empty. | [ ] |
| NS-51 | Define beta acceptance criteria. | `docs/release/beta_acceptance_criteria.md` with actual metrics and thresholds. | [external] |

---

## 9. Implement or explicitly defer monetization and communications

| ID | Task | Evidence required | Status |
|---|---|---|---|
| NS-52 | Decide beta billing mode: free beta or paid beta. | Decision recorded in release bundle/product scope. | [ ] |
| NS-53 | If paid beta: implement Stripe/payment provider integration. | Checkout, webhook, subscription lifecycle, quota gating tests. | [ ] |
| NS-54 | If free beta: explicitly disable billing and document deferred monetization. | Feature flag/config + release note. | [ ] |
| NS-55 | Implement transactional notifications or defer. | Email/provider integration, templates, preferences, delivery logs, or deferred scope. | [ ] |
| NS-56 | Verify password reset / consent renewal / progress report communication path. | Tests or manual evidence. | [ ] |

---

## 10. Execute staging, beta readiness, and final go/no-go

| ID | Cluster H | Task | Evidence required | Status |
|---|---|---|---|---|
| NS-57 | — | Deploy to staging. | Staging deployment log. | [ ] |
| NS-58 | — | Run staging smoke tests. | Smoke output covering API, frontend, CORS, security headers. | [ ] |
| NS-59 | — | Verify staging telemetry and alerts. | Dashboard/alert evidence. | [ ] |
| NS-60 | H-22 | Create GitHub issue templates. | `.github/ISSUE_TEMPLATE/bug_report.md`, `feature_request.md`, `incorrect_content.md`, `popia_concern.md`. | [ ] |
| NS-61 | H-24 | Confirm beta exit criteria before launch. | `docs/release/beta_acceptance_criteria.md`. | [external] |
| NS-62 | — | Conduct formal beta go/no-go. | Signed release decision log. | [external] |
| NS-63 | H-25 | After beta ends, write beta outcome report. | `docs/release/beta_outcome_report.md`. | [post-beta] |
| NS-64 | H-26 | Sign final closure certificate only after evidence is complete. | Signed `docs/release/final_closure_certificate.md`. | [external] |
| NS-65 | — | Tag release candidate / beta release only after all required gates pass. | GitHub Release/tag with evidence bundle. | [external] |

---

## Completion summary

| Area | Status |
|---|---|
| Repository-side production-readiness baseline | [x] complete |
| Full local backend test baseline | [x] green: `1702 passed, 29 skipped` |
| CI on this fork | [ ] open |
| Branch protection | [external] open |
| Staging execution | [ ] open |
| Runtime DB migration proof | [ ] open |
| Backup/restore/rollback drill | [ ] open |
| Legal/security approval | [external] open |
| CAPS educator approval | [external] open |
| Billing/notifications decision | [ ] open |
| Controlled beta go/no-go | [external] open |
| Public beta / production launch | [blocked] blocked |

---

## Rule for marking tasks complete

Do not mark an item `[x]` unless its evidence artefact can be opened and read.

Acceptable evidence includes:

- committed file path,
- passing CI URL,
- captured command output,
- signed review document,
- screenshot/settings export for external systems,
- staging/deployment logs,
- test result artefact.

A document that merely says “evidence added” is not evidence.
