# Todo: Test Velocity & Coverage

Last updated: 2026-06-02  
Branch: `remediation/phase0-phase1`  
Related: `Todo_Production_Grade.md`, `docs/engineering/coverage_debt.md`

Goal: **faster feedback on every PR** and **steady progress toward 80%+ meaningful `app/` coverage**.

---

## Phase 1 — Fast feedback (highest ROI)

Status: IMPLEMENTED and committed in aa51898e.

### 1.1 Split coverage from default pytest

- [x] Remove `--cov=app`, HTML/XML reports, and `--cov-fail-under=80` from default `pytest.ini` `addopts`
- [x] Add `pytest-coverage.ini` with full coverage settings
- [x] Keep `.coveragerc` (`concurrency = greenlet,thread`) for async-safe instrumentation
- [x] Document in `docs/testing/README.md`: when to use fast vs coverage runs

### 1.2 Makefile / developer commands

- [x] `make test-fast` → `pytest tests/unit -n auto --no-cov -m "not governance and not slow and not llm and not e2e"`
- [x] `make test-integration` → `pytest tests/integration --no-cov -q`
- [x] `make test-coverage` → unit+integration with `pytest-coverage.ini` and `COVERAGE_THRESHOLD`
- [x] `make test-coverage-full` → `pytest tests/` with coverage, fail-under 0
- [x] Change default `make test` to alias `test-fast`

### 1.3 Parallel unit execution (pytest-xdist)

- [x] Add `-n auto` to CI unit job (`ci-core.yml`, `ci-cd.yml` unit step)
- [ ] Confirm xdist + asyncio stability on full fast gate (run `make test-fast` locally/CI)
- [x] Keep integration job **serial**

### 1.4 Marker discipline

- [x] Register `@pytest.mark.governance` in `pytest.ini`
- [x] Auto-tag governance tests via `tests/governance_markers.py` (882 unit tests tagged)
- [x] Default PR filter: `-m "not governance and not slow and not llm and not e2e"`
- [x] Add `make test-governance` for nightly / docs-gate workflow

### 1.5 CI job tiering

- [x] **PR fast gate**: unit parallel `--no-cov` + integration `--no-cov`
- [x] **PR coverage gate**: `backend-coverage` job runs `make test-coverage`
- [x] **Nightly**: full suite + governance + coverage artifact upload (workflow_dispatch / scheduled — optional)
- [x] Align COVERAGE_THRESHOLD ratchet: 67 -> 70 -> 75 -> 80 (document dates in coverage_debt.md)


### 1.6 Phase 1 validation snapshot

- [x] make test-fast local validation executed with -n auto
- [x] Result: 1886 passed, 11 skipped, approximately 8 min
- [ ] Current cleanup item: 69 failing/errored concentrated around tests/unit/test_json_completion.py (likely env/settings or mock setup)
- [ ] Remaining Phase 1 follow-ups stay open: xdist CI stability confirmation and cleanup of failing json_completion tests

---

## Phase 2 — Coverage yield (move the 80% needle)

Prioritize tests that execute `app/` code paths, not doc/evidence assertions.

### 2.1 Routers (contract / delegation pattern)

Mirror `test_sprint2_auth_router_delegates.py`, `test_sprint3_popia_router_data_rights.py`, Sprint 6 additions.

- [x] `assessments` — `tests/unit/test_assessments_router_contract.py`
- [x] `billing` — `tests/unit/test_billing_router_contract.py`
- [x] `content_factory` (health/etl status) — `tests/unit/test_content_factory_router_contract.py`
- [ ] `diagnostics` — list/submit/session routes
- [ ] `lessons` — generate/complete/stream authz + consent
- [ ] `study_plans` — generate job acceptance
- [ ] `gamification` — profile/award-xp
- [ ] `parents` — progress/trust dashboard
- [ ] `admin_etl` — status/trigger paths (mock ETL)
- [ ] `jobs` — poll/status contract

### 2.2 Services & modules (line yield)

- [x] `app/modules/lessons/llm_gateway_v2.py` — `tests/unit/test_llm_gateway_v2.py`
- [x] `app/services/etl/etl_pipeline.py` (+ v3 audit) — `tests/unit/test_etl_pipeline.py`
- [ ] `app/services/etl/etl_pipeline_v2.py` — search, dataset export, FTS (sqlite temp)
- [ ] `app/services/etl/etl_pipeline_v3_additions.py` — split_dataset, contamination, bulk_review
- [ ] `app/services/quota_service.py` — expand edge cases (already strong; close gaps)
- [ ] `app/services/learner_service.py` — expand if service grows beyond thin wrapper
- [ ] `app/services/job_runtime_integrity.py` — complete branch coverage
- [ ] `app/services/diagnostic_transactional_response.py` — keep green (12 tests)
- [ ] `app/services/stripe_service.py` — webhook + checkout branches (mock Stripe)
- [ ] `app/services/content_factory*.py` — orchestrator/executor happy paths

### 2.3 Repositories (continue Sprint 5)

- [x] Assessment + gamification — `tests/unit/test_v2_repositories_full.py`
- [ ] Remaining repos under `app/repositories/` (learner, lesson, diagnostic, consent, item_bank)
- [ ] Pattern: in-memory SQLite / mocked `AsyncSession`, assert SQL shape and return mapping

### 2.4 Integration production paths

One happy-path per critical journey; mock persistence unless testing transactions.

- [x] Assessment list + submit — `tests/integration/test_assessment_production_path.py`
- [ ] Extend `test_learner_flow_contract.py` with diagnostic submit step
- [ ] Signup/register → consent grant → lesson generate (or document dev-session-only scope)
- [ ] POPIA export/erasure smoke (existing tests — ensure in PR integration job)
- [ ] Billing webhook isolated test (may exist — avoid duplicate)

---

## Phase 3 — Measurement & gates

### 3.1 Authoritative coverage runs

- [x] CI job publishes coverage.xml + HTML as workflow artifacts
- [x] Stop committing stale coverage.xml to repo (or regenerate on release only)
- [ ] Record baseline in `audits/reports/Coverage_Audit_VM_YYYY-MM-DD.md` after each ratchet
- [ ] Fix/disable tests that prevent full-suite completion (track failure count trend)

### 3.2 Ratchet & scope

- [x] CI floor 67% — `.github/workflows/ci-cd.yml`
- [ ] Per-package `--cov-fail-under` for `app.api_v2_routers`, `app.services`, `app.repositories`
- [ ] PR diff coverage (optional: `diff-cover` or Codecov) — new/changed lines ≥ 70%
- [x] Branch coverage reporting enabled and reviewed (.coveragerc branch = True)

### 3.3 Slow test hygiene

- [ ] `pytest --durations=25` on unit job monthly; mark top offenders `@pytest.mark.slow`
- [ ] Replace redundant evidence tests with single manifest checker where possible

---

## Phase 4 — E2E & release evidence

- [ ] Keep Playwright in `frontend-e2e.yml` (`workflow_dispatch` or staging-only)
- [ ] Add staging-smoke workflow step referencing fast integration paths
- [ ] Final production hardening evidence pack (link from `Todo_Production_Grade.md`)
- [ ] Go/no-go checklist: fast gates green + coverage ≥ current ratchet + integration green

---

## Phase 5 — Optional advanced

- [ ] Hypothesis/factory fixtures for API models (reduce boilerplate)
- [ ] Shared `FakeAuthService` / `FakeConsent` fixtures in `tests/conftest.py`
- [ ] DB-per-xdist-worker for integration (only if integration parallelized)
- [ ] Mutation testing on auth/POPIA slice (low priority)

---

## Suggested execution order

| Week | Focus | Exit criteria |
|------|--------|----------------|
| 1 | Phase 1.1–1.3 | `make test-fast` &lt; 5 min local; CI unit uses `-n auto --no-cov` |
| 2 | Phase 1.4–1.5 + 2.1 (3 routers) | PR gate excludes governance; 3 new router contract files |
| 3 | Phase 2.2 ETL v2/v3 + 2.3 repos | +5–8% line coverage on services/repos |
| 4 | Phase 3.1–3.2 | Authoritative CI coverage artifact; ratchet to 70% |
| 5+ | Phase 2.4 + 4 | Integration paths + release evidence closure |

---

## Commands (target state)

```bash
# Daily / PR
make test-fast
make test-integration

# Before merge / weekly
make test-coverage

# Nightly CI
make test-coverage-full
make test-governance
```

---

## Done (Sprint 6 baseline)

- [x] Nightly coverage/governance workflow scaffold added (.github/workflows/backend-nightly-coverage.yml)

- [x] Phase 1 infrastructure split and fast-gate optimization committed (aa51898e)

- [x] `.coveragerc` restored
- [x] CI `COVERAGE_THRESHOLD` raised to 67
- [x] LLM gateway v2, ETL pipeline, router contracts, assessment integration path
- [x] See commit: `sprint6: add coverage tranche for ETL, LLM gateway v2, and router contracts`

---

## Tracking

Update this file when completing phases. Cross-link progress in `Todo_Production_Grade.md` under “Remaining To Reach Production Grade”.
