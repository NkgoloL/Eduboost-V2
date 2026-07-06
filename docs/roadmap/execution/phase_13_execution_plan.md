---
title: Phase 13 Execution Plan — Frontend and Product Completeness
status: active-control
owner: roadmap-governance
reviewers: [roadmap-governance, release-management, documentation-governance]
audience: roadmap-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 30
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/roadmap, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Phase 13 Execution Plan — Frontend and Product Completeness

**Date**: 2026-06-12
**Updated**: 2026-06-14
**Status**: Substantially remediated locally; live full-stack CI proof pending
**Branch**: `master`
**Base**: `origin/master`
**Source**: `docs/roadmap/roadmap.md` § Phase 13
**Priority**: P2
**Scope**: Fix and wire Playwright E2E suite, create content expansion roadmap, implement load testing, add a11y/PWA verification, verify multilingual lesson generation, and resolve Supabase-vs-raw-Postgres ADR.

## 2026-06-14 Audit Update

The original Phase 13 report overstated completion. A 2026-06-14 audit repaired the local E2E/tooling path and refreshed evidence:

- Root `pnpm`/Playwright dependencies are now reproducible via `pnpm-lock.yaml`.
- WSL has a user-local `pnpm` shim pinned to `9.14.4`, Playwright browser bundles, and required browser system libraries.
- `playwright.config.ts`, `Makefile`, `.github/workflows/e2e.yml`, and `.github/workflows/frontend-e2e.yml` now run Playwright from the repo root where `tests/e2e/` lives.
- `make frontend-e2e-mocked` passed 20 tests across chromium, firefox, webkit, Mobile Chrome, and Mobile Safari.
- `make frontend-e2e-smoke` passed 10 tests across the same browser projects.
- A deterministic multilingual lesson-generation smoke test now covers `en`, `zu`, `af`, and `xh`.

Remaining proof gaps are live GitHub Actions execution, full backend-backed E2E with seeded data, Lighthouse numeric score, real cached-lesson offline browser proof, and native-speaker review for Afrikaans/isiXhosa quality.

---

## Pre-Conditions

- [x] Phase 12 (Security Posture Deepening) merged to `master`
- [x] Phases 0–12 complete and verified
- [x] Branch `phase-13/frontend-product-completeness` created from `master`
- [x] Existing E2E suite at `tests/e2e/` (15 spec files: auth, diagnostic, learner, parent, privacy, study plan, lesson generation, etc.)
- [x] Playwright binary available at `.venv/bin/playwright`
- [x] `locust/` directory is empty — no load test scenarios yet
- [x] `docs/caps/` has Grade 4 Maths coverage but no roadmap for Grades R–3, 5–7
- [x] ADRs exist for many domains but no Supabase decision ADR
- [x] Frontend assessment report at `app/frontend/FRONTEND_ASSESSMENT_REPORT_2026-05-16.md`
- [x] Multilingual i18n infrastructure exists but lesson generation verification is unconfirmed

---

## Inventory of Gaps

| Area | Status | Action Needed |
|------|--------|---------------|
| Playwright E2E suite | ⚠️ Exists (15 specs) but untested against current codebase | Run suite, fix failures, wire into CI |
| Content expansion roadmap | ❌ Missing | Create `docs/caps/content_expansion_roadmap.md` for Grades R–3, 5–7 |
| Load testing (`locust/`) | ❌ Empty | Implement at least one Locust scenario targeting diagnostic + lesson endpoints |
| Accessibility (a11y) | ❌ No automated checks | Add axe-core/Lighthouse audit to CI; verify PWA offline behavior |
| PWA offline support | ❌ Unverified | Verify cached lessons work offline |
| Multilingual lesson generation | ⚠️ Infrastructure exists, end-to-end unverified | Verify one lesson per supported language (isiZulu, Afrikaans, isiXhosa) |
| Supabase vs raw Postgres decision | ❌ Undocumented | Create ADR documenting the decision; remove ambiguity from env files |

---

## Work Groups

### K.1 — Playwright E2E Suite Fix & CI Integration [P1]

**Run and fix** the existing Playwright E2E suite against the current codebase:

- [x] Run `tests/e2e/` suite locally with `pnpm exec playwright test` (or equivalent)
- [x] Fix failing command/workflow drift caused by wrong working directories, missing root lockfile, missing browser dependencies, and dev-server readiness
- [x] Verify critical learner journeys:
  - Authentication (register, login, logout, refresh)
  - Diagnostic flow (start, answer items, complete)
  - Lesson generation (study plan → lesson → completion)
  - Parent portal (review progress, manage consent)
  - Privacy flows (data export, erasure consent)
- [x] Add Playwright CI job to GitHub Actions (`.github/workflows/e2e.yml`):
  - Spin up backend + frontend Compose stack
  - Run Playwright against the stack
  - Upload failure screenshots as artifacts
- [x] Document how to run E2E tests locally in `docs/development/e2e_testing.md`

**Evidence:** Passing E2E suite, `.github/workflows/e2e.yml`, `docs/development/e2e_testing.md`
**Risk:** Medium — upstream route/auth changes may require spec updates

### K.2 — Content Expansion Roadmap [P2]

- [x] Create `docs/caps/content_expansion_roadmap.md` covering:
  - Grades R–3 (Foundation Phase) per CAPS: Home Language, First Additional Language, Mathematics
  - Grades 5–7 (Intermediate & Senior Phase) per CAPS: Languages, Mathematics, Natural Sciences, Social Sciences
  - Estimated item/lesson counts per grade and subject
  - Source material acquisition strategy (existing OER, publisher partnerships, AI-assisted generation)
  - Effort estimates and sequencing recommendations
- [x] Cross-reference with existing `docs/caps/grade4_maths_coverage_matrix.md` to ensure consistency

**Evidence:** `docs/caps/content_expansion_roadmap.md`
**Risk:** Low — planning/documentation effort

### K.3 — Load Testing Scenario [P2]

- [x] Create `locust/` directory with a basic Locust setup:
  - `locustfile.py` with at least one realistic user scenario:
    - Learner: register → login → start diagnostic → answer items → view study plan → generate lesson
  - `README.md` with setup/run instructions
  - `requirements.txt` (or reference from `requirements-dev.txt`)
- [x] Document target metrics (requests/sec, p50/p95 latency, error rate) in a test plan
- [ ] Verify the scenario runs against a local Docker Compose stack
- [ ] Optionally wire into CI as a manual-trigger workflow (not blocking)

**Evidence:** `locust/locustfile.py`, `locust/README.md`, documented test results
**Risk:** Low — new files, no breaking changes

### K.4 — Accessibility & PWA Verification [P2]

- [x] Add a11y audit step/check to frontend verification:
  - Use `axe-playwright` or `@axe-core/playwright` in existing Playwright specs
  - Assert no critical/serious a11y violations on key pages (login, diagnostic, lesson, parent portal)
  - Track Lighthouse a11y score as a non-blocking report
- [ ] Verify PWA offline behavior:
  - Confirm service worker registration works (`npx playwright` test or manual)
  - Verify a cached lesson renders without network
  - Document any gaps in `docs/development/pwa_offline_plan.md`
- [x] Set a target: Lighthouse a11y score ≥ 90

**Evidence:** Playwright a11y assertions in E2E suite, `docs/development/pwa_offline_plan.md`
**Risk:** Low — assertions added to existing test infrastructure

### K.5 — Multilingual Lesson Generation Verification [P2]

- [x] Identify current supported languages (isiZulu, Afrikaans, isiXhosa, English)
- [x] Run mock lesson generation smoke for each language
- [x] Verify:
  - Prompt template correctly handles the target language
  - Output contains the expected language (basic content check)
  - Fallback behavior works when LLM output quality is low
- [x] Document language support status and known gaps in `docs/caps/multilingual_status.md`
- [x] Add a CI-compatible smoke test that generates one lesson per language with the deterministic provider

**Evidence:** `docs/caps/multilingual_status.md`, CI smoke test or manual verification log
**Risk:** Low — verification work, API calls may have small cost

### K.6 — Supabase Decision ADR [P2]

- [x] Create ADR (e.g. `docs/adr/ADR-029-supabase-auth-strategy.md`) documenting:
  - Context: Supabase vs raw Postgres auth — ambiguity in env files and deployment docs
  - Decision: Which approach is authoritative (or if both are supported, the boundary)
  - Consequences: env var requirements, migration paths, auth flow impacts
- [x] Update `.env.example` and any deployment docs to remove ambiguity
- [ ] If Supabase is retained for auth, verify the integration is tested in E2E suite

**Evidence:** `docs/adr/ADR-029-supabase-auth-strategy.md`, updated `.env.example`
**Risk:** Low — documentation and config cleanup

---

## Execution Order

```
Week 1:  K.1 (E2E suite fix & CI) — highest risk, unblocks other work
         K.6 (Supabase ADR) — quick documentation win, clarifies auth context for E2E

Week 2:  K.2 (content expansion roadmap) — planning
         K.3 (load testing) — new implementation
         K.5 (multilingual verification) — testing

Week 3:  K.4 (a11y & PWA) — assertions + documentation
         Integration testing across all work groups
         Implementation report
```

---

## Definition of Done

- [ ] Playwright E2E suite passes locally and in CI (`.github/workflows/e2e.yml`)
- [x] `docs/development/e2e_testing.md` documents how to run E2E tests
- [x] `docs/caps/content_expansion_roadmap.md` created for Grades R–3 and 5–7
- [x] `locust/locustfile.py` exists with at least one learner scenario
- [x] a11y contract assertions/checks exist; PWA offline behavior documented
- [x] `docs/caps/multilingual_status.md` created with per-language verification results
- [x] `docs/adr/ADR-029-supabase-auth-strategy.md` created and `.env.example` updated
- [x] Implementation report written
- [x] Changes merged to `master`
