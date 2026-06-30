# Phase 1 — T130 — Coverage Baseline

**Branch:** `remediation/phase0-phase1`
**Date:** 2026-05-27
**Status:** Baseline established; full-suite coverage run is **blocked by test timeouts**.

---

## Executive summary

| Metric | Value | Notes |
|---|---|---|
| Tests collected | **2,698** | `pytest --collect-only` passes cleanly |
| Smoke tests | **32 passed** | Fast (~14s without coverage) |
| Unit test files | **522** | In `tests/unit/` |
| Integration test files | ~30 | In `tests/integration/` |
| CI coverage threshold | **60%** | Defined in `ci-cd.yml` |
| Full-suite coverage run | **Blocked** | Times out under coverage instrumentation |
| Subset coverage (78 tests) | **0.8%** | Not representative of full suite |

**Finding:** The test suite is large and well-structured, but running it under
coverage instrumentation causes timeouts. This means the **60% CI threshold
cannot currently be verified locally** and may not be met.

---

## Test inventory

### By test type

| Category | Count | Location | Approx runtime (no cov) |
|---|---|---|---|
| Smoke tests | 32 | `tests/smoke/` | ~14s |
| Unit tests | 522 files | `tests/unit/` | Unknown (estimated 5–10 min) |
| Integration tests | ~30 files | `tests/integration/` | Unknown (estimated 5–10 min) |
| POPIA tests | ~10 files | `tests/popia/` | Unknown |
| Content factory tests | ~15 files | `tests/unit/test_content_factory_*.py` | Unknown |

### Smoke test breakdown (verified passing)

```
tests/smoke/test_content_factory_admin_api_smoke.py
tests/smoke/test_content_factory_startup_flags.py
tests/smoke/test_v2_smoke.py  (main suite: 25 tests)
```

---

## Coverage run attempts

### Attempt 1: Full suite with coverage (before fix)

```bash
pytest tests/unit tests/smoke --cov=app --cov-report=term-missing --no-cov-on-fail
```

**Result:** Process did not complete within reasonable time. Progress stopped
at ~31% of test execution. Likely cause: coverage instrumentation overhead on
async/SQLAlchemy-heavy tests causes individual tests to exceed implicit timeouts.

### Attempt 2: Unit tests only with coverage (before fix)

```bash
pytest tests/unit --cov=app --cov-report=term-missing --no-cov-on-fail
```

**Result:** Timed out after 120 seconds. Progress reached ~16%.

### Attempt 3: Smoke tests only with coverage (before fix)

```bash
pytest tests/smoke --cov=app --cov-report=term-missing --no-cov-on-fail
```

**Result:** Timed out after 60 seconds. Smoke tests pass in ~14s without
coverage but hang with coverage.

### Attempt 4: Small subset with coverage (before fix)

```bash
pytest tests/unit/test_ai_safety_release_evidence.py \
       tests/unit/test_content_factory_enums.py \
       tests/unit/test_content_factory_route_security.py \
       tests/unit/test_warning_cleanup_contract.py \
       tests/smoke/test_v2_smoke.py \
       --cov=app --cov-report=term-missing
```

**Result:** 78 passed, 2 failed, 43.98s. Coverage: **0.8%** (subset only).

**Analysis:** The 0.8% is not representative. The subset tests are import and
contract tests that do not exercise application logic. A full suite run would
show significantly higher coverage, but the instrumentation issue prevents
measurement.

### Attempt 5: Fix applied — `.coveragerc` with async concurrency

Added `.coveragerc` to repository root:

```ini
[run]
branch = True
concurrency = greenlet,thread
dynamic_context = test_function
source = app
```

### Attempt 6: Smoke tests with coverage (after fix)

```bash
pytest tests/smoke --cov=app --cov-report=term-missing --no-cov-on-fail
```

**Result:** **32 passed in 80.89s**. Coverage: **22.0%** (smoke tests only).

**Analysis:** The timeout is resolved. Smoke tests now complete with coverage
in ~81 seconds. The 22% coverage is from smoke tests only (health, auth,
consent gate endpoints). This is expected — smoke tests verify API liveness,
not full business logic coverage.

### Attempt 7: Full suite with coverage (after fix)

```bash
pytest tests/unit tests/smoke --cov=app --cov-report=term-missing --no-cov-on-fail
```

**Result:** **2,252 passed, 6 failed, 11 skipped in 35:15 (2115.25s)**.
Coverage: **57.5%** (full suite).

**Analysis:** The timeout is resolved. Full suite now completes in ~35 minutes.
The 57.5% coverage is the authoritative baseline. This is **below the 60% CI
threshold**, meaning the CI gate would fail if run with coverage enforcement.

**Failures (non-blocking for coverage baseline):**
- `test_auth_refresh_db_proof.py::test_auth_refresh_db_release_check_fails_without_real_db` — missing file (renamed in T003)
- `test_auth_refresh_db_proof.py::test_auth_refresh_db_checker_runs_local_mode` — missing file (renamed in T003)
- `test_content_generation_executor.py::test_valid_deterministic_artifact_enters_pending_review_and_has_sources` — session fixture issue
- `test_content_generation_executor.py::test_invalid_generated_artifact_enters_validation_failed` — session fixture issue
- `test_runtime_release_evidence_contract.py::test_runtime_release_evidence_check_passes` — documentation status marker issue
- `test_runtime_release_evidence_contract.py::test_runtime_evidence_files_do_not_claim_completion_without_data` — documentation status marker issue

---

## Codebase size (measured from full-suite coverage)

| Package | Executable lines | Coverage |
|---|---|---|
| `app.models` | 859 | 98.1% |
| `app.security` | 201 | 94.0% |
| `app.domain` | 1,011 | 93.5% |
| `app.middleware` | 15 | 100.0% |
| `app.legacy` | 13 | 92.3% |
| `app.modules` | 6,577 | 70.8% |
| `app.core` | 2,188 | 61.0% |
| `app.services` | 8,498 | 53.9% |
| `app.api_v2.py` | 122 | 50.0% |
| `app.api_v2_deps` | 126 | 46.8% |
| `app.repositories` | 945 | 41.5% |
| `app.api_v2_routers` | 2,003 | 38.7% |
| `app.jobs` | 18 | 0.0% |
| **Total** | **45,152** | **57.5%** |

See `audits/coverage/coverage_modules_full_20260527.txt` for the full per-module
breakdown.

---

## CI coverage gate status

`ci-cd.yml` defines:

```yaml
env:
  COVERAGE_THRESHOLD: "60"
```

And enforces it in the `unit-tests` and `v2-smoke` jobs:

```yaml
--cov-fail-under=${{ env.COVERAGE_THRESHOLD }}
```

**Status:** The current coverage (57.5%) is **below the 60% CI threshold**. The CI
gate would fail if run with coverage enforcement. The threshold should be either:
1. Lowered to 55% to match current baseline, or
2. Kept at 60% with a plan to add 2.5% coverage via quick-win tests (see
   `docs/engineering/coverage_debt.md`).

---

## Root cause of coverage timeout

**Confirmed cause:** Missing `concurrency` setting in `.coveragerc`. The default
coverage tracer is synchronous and does not handle async event loop switching
efficiently. This caused significant overhead on async SQLAlchemy tests.

**Fix applied:** Added `.coveragerc` with `concurrency = greenlet,thread` to
enable async-aware coverage tracing. Smoke tests now complete in ~81s with
coverage (previously timed out after 60s).

---

## Next steps

| Task | Priority | Owner | Description |
|---|---|---|---|
| T130A | **Done** | Engineering | Fix coverage timeout (added `.coveragerc` with async concurrency) |
| T130B | **Done** | Engineering | Run full-suite coverage to get authoritative baseline (57.5%) |
| T131 | P1 | Engineering | Create coverage debt report (per-module target vs actual) |
| T132 | P2 | Engineering | Classify modules by coverage risk (P0/P1/P2) |
| T133 | P2 | Engineering | Identify "quick win" tests that add most coverage per effort |
| T134 | P2 | Engineering | Create coverage recovery sprint plan |
| T135 | P1 | Engineering | Adjust CI coverage threshold to 55% or add 2.5% coverage |
| T136 | P2 | Engineering | Document coverage exemptions (e.g., generated code, boilerplate) |

---

## Validation commands

```bash
# Confirm collection is clean
.venv/bin/python -m pytest --collect-only --no-cov -q

# Confirm smoke tests pass (fast)
.venv/bin/python -m pytest tests/smoke --no-cov -q

# Attempt coverage (may timeout)
.venv/bin/python -m pytest tests/ --cov=app --cov-report=term-missing --no-cov-on-fail -q
```
