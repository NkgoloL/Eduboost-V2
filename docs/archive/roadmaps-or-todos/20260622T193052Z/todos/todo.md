---
title: EduBoost V2 -- North Star TODO
status: archived-record
owner: documentation-governance
reviewers: [documentation-governance, evidence-custodian, release-management]
audience: evidence-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 180
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/archive, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# EduBoost V2 -- North Star TODO

**Purpose:** Execution-focused North Star for the next phase. This reflects the current green local backend unit baseline and separates repository-side completion from CI, runtime, external, legal, security, product, and beta-launch evidence.

**Last updated:** 2026-06-14 (Phase 1 corrective package verified complete; Phase 7 complete — deployment and security hardening done)
**Latest local backend unit result:** 2051 passed, 1 skipped, 1 warning
**Gap analysis:** Eduboost-V2_Gap_Analysis.md (2026-06-09)

## Status vocabulary

- `[x]` done: completed and locally/repository-side verified or explicitly confirmed.
- `[verify]` implemented but needs CI proof, staging proof, runtime evidence, or captured artefact.
- `[ ]` open: not done.
- `[external]` requires a person/system outside normal code work.
- `[post-beta]` cannot be completed until beta has actually run.
- `[blocked]` cannot proceed until predecessor evidence exists.

---

## 0. Current project state

- [x] Production-readiness backlog domains 05-20 have repository-side implementation evidence, docs, check scripts, unit tests, and Makefile targets.
- [x] Domains 00-04 are treated as previously integrated into the repository-side baseline.
- [x] POPIA/consent/audit/source-evidence repairs integrated.
- [x] AuthService and legacy unit-test compatibility repairs integrated.
- [x] Alembic migration graph repair from `code_338` integrated.
- [x] Full backend unit suite locally green: `2051 passed, 1 skipped, 1 warning`.
- [x] Cluster H phantom-entry problem identified and converted into concrete remediation tasks.
- [x] Documentation claim discipline established.
- [x] Recommended Operating Model documented and enforced by `make recommended-operating-model-check`.
- [x] Five-lane project assistance status documented and enforced by `make project-assistance-status-check`.
- [x] Outstanding TODO implementation plan compiled.
- [x] Phase 5 migration graph, startup DDL removal, and migration smoke verification completed locally.
- [x] Phase 1 corrective package verified complete against disposable PostgreSQL and corrective audit.
- [ ] EduBoost is **not public-beta-ready** with real learner data.
- [ ] EduBoost is **not production-launch-ready**.
- [ ] Next milestone: **CI green -> staging execution evidence -> controlled beta go/no-go -> production**.

---

# 10-step execution sequence

## 1. Freeze the local green baseline

| ID | Task | Evidence required | Status |
|---|---|---|---|
| NS-01 | Apply Alembic migration graph repair. | Migration graph test passes. | [x] |
| NS-02 | Rerun full unit suite. | `pytest -c pytest.ini tests/unit -q --no-cov` shows `2051 passed, 1 skipped`. | [x] |
| NS-03 | Commit migration graph repair and related POPIA/AuthService repairs. | Merged in `d25f6feb` / PR #223; refreshed local evidence in Phase 5 docs. | [x] |
| NS-04 | Record local test evidence. | `docs/release/unit_test_evidence.md` contains full output. | [x] |
| NS-05 | Triage non-failing warnings. | Warnings documented as accepted, fixed, or tracked. | [x] |
| NS-05A | Keep operating-model and project-assistance controls current. | Make checks pass. | [x] |

Current warnings to track:
- AsyncMock unawaited coroutine warning in `tests/unit/test_v2_services_full.py::TestLessonServiceV2::test_generate_enforces_quota`; accepted as non-failing test debt.

---

## 2. Make CI authoritative

| ID | Task | Evidence required | Status |
|---|---|---|---|
| NS-06 | Trigger GitHub Actions on `master`. | Passing Actions run URL committed to `docs/release/ci_evidence.md`. | [verify] |
| NS-07 | Ensure full unit suite runs in CI. | CI output with pass/skip counts. | [verify] |
| NS-08 | Ensure OpenAPI drift check runs in CI. | CI output proving `make openapi-check` passes. | [verify] |
| NS-09 | Ensure migration graph check runs in CI. | CI output proving migration graph is linear and resolvable. | [verify] |
| NS-10 | Ensure POPIA gate/sweep runs in CI. | CI output proving POPIA checks pass. | [verify] |
| NS-11 | Ensure frontend lint/type/unit checks run in CI. | CI output for lint, type-check, and tests. | [x] Phase 3 complete; 147/147 tests passing |
| NS-12 | Add/verify branch protection on `master`. | Screenshot/settings export in `docs/release/branch_protection_evidence.md`. | [external] |

---

## 3. Repair release-governance evidence and Cluster H inflation

| ID | Cluster H | Task | Evidence required | Status |
|---|---|---|---|---|
| NS-13 | H-01 | Run `make refresh-current-state` on clean checkout. | Committed `docs/current_state.md` with timestamp/current gate results. | [ ] |
| NS-14 | H-02 | Create sign-off manifest with blank named fields. | `docs/release/sign_off_manifest.md`. | [x] |
| NS-15 | H-03 | Create rollback runbook. | `docs/release/rollback_runbook.md` with API/frontend/database rollback commands. | [x] |
| NS-16 | H-04 | Create post-deploy smoke checklist. | `docs/release/post_deploy_smoke_checklist.md`. | [x] |
| NS-17 | H-05 | Create release bundle index. | `docs/release/release_bundle_v1.0.0-rc2.md` with real links only. | [x] |
| NS-18 | H-06 | Add PR template. | `.github/PULL_REQUEST_TEMPLATE.md`. | [x] |

---

## 4. Prove database and migration runtime behavior

| ID | Task | Evidence required | Status |
|---|---|---|---|
| NS-24 | Run `alembic upgrade head` against disposable PostgreSQL. | Migration evidence doc with full output. | [x] |
| NS-25 | Run schema integrity check against disposable DB. | Captured output in migration evidence doc. | [x] |
| NS-26 | Run downgrade/rollback path where supported. | Rollback evidence or documented non-downgrade rationale. | [x] |

---

## 5. Prove frontend/browser behavior against live backend

| ID | Task | Evidence required | Status |
|---|---|---|---|
| NS-27 | Run frontend coverage. | `docs/release/frontend_test_evidence.md`. | [ ] |
| NS-28 | Run Playwright E2E against live local or staging stack. | Browser E2E output and environment details. | [ ] |
| NS-29 | Verify critical UI flows (login, lesson generation, consent grant, POPIA export). | Evidence doc with screenshots or CLI output. | [ ] |
| NS-30 | Verify API/WS offline resilience implementation status. | Evidence doc with deferred scope notes. | [verify] |

---

## 6. Prove observability, backup, restore, and rollback

| ID | Cluster H | Task | Evidence required | Status |
|---|---|---|---|---|
| NS-32 | H-19 | Create operator runbook. | `docs/release/operator_runbook.md`. | [ ] |
| NS-33 | H-20 | Configure uptime monitoring for GET /api/v2/health/deep. | Monitoring evidence doc. | [external] |
| NS-34 | H-21 | Wire Alertmanager to a real alert channel and test. | Alertmanager evidence doc. | [ ] |
| NS-35 | | Execute backup dry-run. | Backup log with sha256 and table counts. | [ ] |
| NS-36 | | Execute restore drill. | Restore log proving data round-trip. | [ ] |
| NS-37 | | Execute rollback drill. | Rollback log with pre/post state comparison. | [ ] |
| NS-38 | H-18 | Define change-control policy. | `docs/release/change_control_policy.md`. | [ ] |
| NS-39 | | Run incident tabletop exercise. | Evidence doc with non-downgrade rationale. | [ ] |

---

## 7. Complete POPIA, legal, security, and governance approvals

| ID | Cluster H | Task | Evidence required | Status |
|---|---|---|---|---|
| NS-40 | H-13 | Run POPIA sweep. | `docs/release/popia_sweep_evidence.md` with 0 issues or tracked exceptions. | [ ] |
| NS-41 | | Submit POPIA docs for legal review. | Legal review record. | [external] |
| NS-42 | | Obtain security review or pen-test decision. | Security sign-off or documented accepted-risk rationale. | [external] |
| NS-43 | H-15 | Fill and sign sign-off manifest. | Signed `docs/release/sign_off_manifest.md`. | [ ] |
| NS-44 | H-16 | Create release decision log. | `docs/release/release_decision_log.md`. | [ ] |

---

## 8. Resolve content/product readiness

| ID | Task | Evidence required | Status |
|---|---|---|---|
| NS-45 | Confirm current CAPS approved items count. | `docs/ai/caps_safety_evidence/2026-05-11.md` records 14 approved starter items. | [ ] |
| NS-46 | Submit AI-generated content for educator review. | Review sign-off or accepted-risk rationale. | [external] |
| NS-47 | Re-run launch content validation. | `python3 scripts/validate_launch_content.py --strict` passes. | [ ] |
| NS-48 | Add independent answer-key validation plan. | Evidence doc with non-downgrade rationale. | [ ] |
| NS-49 | Define Grade 4 Mathematics completeness criteria for beta. | Documented criteria in `docs/beta/scope.md`. | [ ] |
| NS-50 | Plan content expansion beyond Grade 4 Mathematics. | Roadmap entry in `docs/caps/expansion_plan.md`. | [ ] |
| NS-51 | Verify isiZulu, Afrikaans, isiXhosa lesson generation. | Evidence of working multilingual generation. | [ ] |

---

## 9. Implement staging/beta readiness

| ID | Task | Evidence required | Status |
|---|---|---|---|
| NS-52 | Decide billing model: free beta or paid beta. | Decision record in `docs/beta/billing_decision.md`. | [ ] |
| NS-53 | Implement Stripe/payment integration if paid beta. | Stripe webhook tests and checkout flow evidence. | [ ] |
| NS-54 | Implement beta feature flags. | Flag config and toggle test evidence. | [ ] |
| NS-55 | Set up beta feedback intake (form, endpoint, or tool). | Feedback intake test evidence. | [ ] |
| NS-56 | Create beta acceptance criteria. | `docs/beta/acceptance_criteria.md`. | [ ] |
| NS-57 | Create known-issues file. | `docs/beta/known_issues.md` -- must not be empty. | [ ] |
| NS-58 | Run staging smoke tests. | Staging smoke test output. | [ ] |
| NS-59 | Verify staging telemetry (Grafana dashboards populated). | Dashboard screenshot or API output. | [ ] |
| NS-60 | Create GitHUb issue templates for beta. | `.github/ISSUE_TEMPLATE/beta_bug.md` and `beta_feedback.md`. | [ ] |

---

## 10. Execute staging, beta readiness, and final go/no-go

| ID | Cluster H | Task | Evidence required | Status |
|---|---|---|---|---|
| NS-57 | | Deploy to staging. | Staging deployment log. | [ ] |
| NS-58 | | Run staging smoke tests. | Staging smoke test output. | [ ] |
| NS-59 | | Verify staging telemetry (Grafana dashboards populated). | Dashboard screenshot or API output. | [ ] |
| NS-60 | H-22 | Create GitHUb issue templates for beta. | `.github/ISSUE_TEMPLATE/beta_bug.md` and `beta_feedback.md`. | [ ] |
| NS-61 | H-24 | Confirm beta exit criteria before production launch. | `docs/release/beta_exit_criteria.md` with real data. | [ ] |
| NS-62 | H-25 | Create final project closeout attestation. | `docs/release/final_project_closeout_attestation.md` with sign-offs. | [ ] |
| NS-63 | | Tag release after beta exit criteria met. | Git tag `v1.0.0-rc3`. | [ ] |
| NS-64 | H-26 | Sign final closeout after evidence is complete. | Signed closeout in doc with real data. | [ ] |
| NS-65 | | Conduct post-beta retrospective. | Retro document capturing lessons learned. | [post-beta] |

---

# NEW: Gap Coverage -- 5 Categories from 2026-06-09 Analysis

## GAP-1: Technical Debt Cleanup (was missing)

| ID | Gap | Task | Status |
|---|---|---|---|
| G1-01 | 830 non-F821 Ruff findings | Triage remaining Ruff findings into `[now]`, `[next]`, `[later]` buckets. Block CI only on `[now]`. | [ ] |
| G1-02 | Core -> Services import violations (6 boundary breaks) | Fix import-linter violations: llm_gateway, consent_gate, stripe_client, analytics should not import from app.services. | [ ] |
| G1-03 | Comments lagging code | Audit route files with "trust the lesson_id" comments; align comments with actual authorization helpers. | [ ] |
| G1-04 | Dual route registration (355 routes x2) | Decide: keep only /api/v2 or /v2; remove duplicate registration. | [ ] |
| G1-05 | 35 Alembic migrations debt | Squash migrations into a baseline migration after Phase 5 schema cleanup. | [ ] |
| G1-06 | Dormant router files (ether.py, judiciary.py, test_api.py, test_services.py) | Archive or delete unregistered router files. | [ ] |

## GAP-2: Security Hardening (was partially missing)

| ID | Gap | Task | Status |
|---|---|---|---|
| G2-01 | Permissive CSP (unsafe-inline for script-src and style-src) | Replace unsafe-inline with nonce-based or hash-based CSP. | [x] Phase 7.3 |
| G2-02 | HSTS set unconditionally (breaks dev HTTP) | Condition HSTS on APP_ENV=production. | [x] Phase 7.4 |
| G2-03 | /metrics unauthenticated | Add app-level auth or document private-network-only policy with enforcement in deployment config. | [x] Phase 7.7 (IP allowlist + ADR-027) |
| G2-04 | /__dev/slow_query should be removed in production-like environments | Restrict to explicit dev-only context or remove entirely. | [x] Phase 7.7 (gated by is_production()) |
| G2-05 | V1 remnants in Nginx config | Audit all Nginx, Compose, and Bicep for /api/v1 references; replace or remove. | [x] Phase 7.5/7.6 |
| G2-06 | No threat model or updated pen-test plan | Create threat model document. Refresh pen-test checklist from stale audit version. | [ ] |
| G2-07 | Secret rotation not operationalized | Implement JWT secret rotation with keyring and add rotation drill to runbook. | [ ] |

## GAP-3: Frontend & Product Completeness (was missing)

| ID | Gap | Task | Status |
|---|---|---|---|
| G3-01 | No Playwright E2E verification for broken suites | Fix and run Playwright suites: diagnostic -> study plan -> lesson -> parent portal flow. | [ ] |
| G3-02 | Grade 4-only launch content | Create phased content expansion plan for Grades R-3, 5-7, and other subjects. | [ ] |
| G3-03 | No load testing (locust/ directory empty) | Implement Locust load tests for critical paths: login, diagnostic, lesson generation. | [ ] |
| G3-04 | Accessibility (a11y) not verified | Run a11y audit with axe-core or Lighthouse; file issues for WCAG 2.1 AA gaps. | [ ] |
| G3-05 | PWA offline support not verified | Test offline lesson access, service worker caching, and manifest installability. | [ ] |
| G3-06 | Multilingual lesson generation not verified | Run isiZulu, Afrikaans, isiXhosa lesson generation with cultural context validation. | [ ] |
| G3-07 | Supabase vs raw Postgres auth strategy not decided | Document decision and align implementation; remove unused Supabase surface if raw Postgres wins. | [ ] |

## GAP-4: Operational Readiness (was missing)

| ID | Gap | Task | Status |
|---|---|---|---|
| G4-01 | No SRE runbooks | Create incident response runbook, on-call rotation plan, and escalation policy. | [ ] |
| G4-02 | No capacity planning | Document expected learner load, API throughput targets, and scaling model (ACA auto-scale config). | [ ] |
| G4-03 | No SLO definitions | Define SLOs for API latency, diagnostic response time, lesson generation time. Add to Grafana. | [ ] |
| G4-04 | No LLM cost model | Estimate per-lesson and per-diagnostic LLM API costs. Set budget alerts. | [ ] |
| G4-05 | No disaster recovery plan beyond backup/restore drills | Create DR plan with RPO (Recovery Point Objective) and RTO (Recovery Time Objective) targets. | [ ] |
| G4-06 | No log retention or PII scrubbing policy | Define log retention periods; ensure PII scrubbing in logs. | [ ] |

## GAP-5: Governance & Process (was missing)

| ID | Gap | Task | Status |
|---|---|---|---|
| G5-01 | Branch protection not evidenced | Enable branch protection on master; require PR reviews and passing CI before merge. | [external] |
| G5-02 | Stale evidence (current_state.md is 3+ weeks old) | Run `make refresh-current-state` weekly; add CI check for staleness > 7 days. | [ ] |
| G5-03 | No decision log for outstanding choices | Create ADR for: deployment target (Compose vs ACA), Python version (3.11 vs 3.12), Supabase role. | [ ] |
| G5-04 | External tasks have no owners | Assign named owners to all [external] tasks; track in project board. | [ ] |
| G5-05 | No code review policy | Document code review requirements in ../../CONTRIBUTING.md; enforce via branch protection. | [ ] |
| G5-06 | No release manager identified | Assign release manager role for v1.0.0-rc cycle. | [external] |

---

## Beta Period (NEW Section)

| ID | Task | Evidence required | Status |
|---|---|---|---|
| B-01 | Define beta cohort (target: N learners, M educators). | `docs/beta/cohort_plan.md`. | [ ] |
| B-02 | Create beta onboarding flow (consent, account creation). | Onboarding test evidence. | [ ] |
| B-03 | Set up beta feedback collection (in-app + survey). | Feedback pipeline test. | [ ] |
| B-04 | Define beta success metrics (engagement, completion, accuracy gain). | `docs/beta/success_metrics.md`. | [ ] |
| B-05 | Run beta for minimum 2 weeks with real learners. | Beta period log with metrics. | [post-beta] |
| B-06 | Collect and triage beta feedback. | Triage board with categorized issues. | [post-beta] |
| B-07 | Fix P0/P1 issues discovered during beta. | Fixed-issue register. | [post-beta] |
| B-08 | Conduct beta retrospective. | Retro document. | [post-beta] |
| B-09 | Make production go/no-go decision based on beta metrics. | `docs/release/production_go_no_go.md`. | [post-beta] |

---

## Completion summary

| Area | Status |
|---|---|
| Repository-side production-readiness baseline
- [x] Phase 1: Release-Blocking Correctness Fixes (2026-06-09) | [x] complete |
| Operating-model and project-assistance controls | [x] documented and checked |
| TODO implementation plan | [x] compiled and checked |
| CI green on master | [ ] open |
| Release-governance evidence | [ ] partially open |
| Database migration runtime proof | [ ] open |
| Frontend/browser behavior proof | [ ] open |
| Observability/backup/restore/rollback proof | [ ] open |
| POPIA/legal/security sign-offs | [ ] open |
| Content/product readiness | [ ] open |
| Staging deployment + smoke tests | [ ] open |
| **Technical debt cleanup (GAP-1)** | **[ ] NEW** |
| **Security hardening (GAP-2)** | **[ ] NEW** |
| **Frontend/product completeness (GAP-3)** | **[ ] NEW** |
| **Operational readiness (GAP-4)** | **[ ] NEW** |
| **Governance & process (GAP-5)** | **[ ] NEW** |
| **Beta period with real learners** | **[ ] NEW** |
| Controlled beta go/no-go | [ ] blocked |
| Post-beta production go/no-go | [ ] blocked |

## Rule for marking tasks complete

Do not mark an item [x] unless its evidence artifact exists and can be linked.

Acceptable evidence includes:
- committed file path
- passing CI run URL
- captured CLI output
- signed document
- dashboard screenshot
- staging/production log

Do not mark items complete based on implementation intent or documentation-only confidence.
