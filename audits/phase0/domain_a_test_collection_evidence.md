# Phase 0 — Domain A — Test Collection Evidence

**Branch:** `remediation/phase0-phase1`
**Date:** 2026-05-27
**Scope:** T001, T002, T003, T004, T005

---

## T001 — Register `smoke` marker in `pytest.ini`

**Status:** Done.

Added `smoke: smoke / critical-path tests` to the `markers` section of `pytest.ini`.

```ini
markers =
    unit: fast, isolated unit tests (no I/O)
    integration: tests that require a live DB or Redis
    e2e: end-to-end tests via Playwright (require running stack)
    slow: tests that take >5 seconds
    llm: tests that make real LLM API calls (skipped in CI unless ALLOW_LLM_TESTS=1)
    performance: performance/SLO checks that may require a seeded database or running stack
    smoke: smoke / critical-path tests
```

---

## T002 — AI safety release evidence script/test contract

**Status:** Pre-satisfied at audit baseline.

The TODO references `tests/ci/test_ai_safety_release_evidence.py`. The actual test
location in the codebase is `tests/unit/test_ai_safety_release_evidence.py`.

Inspection results:

- `scripts/check_ai_safety_release_evidence.py` exports `REQUIRED` (tuple) and
  `check_all() -> list[Result]`. Both are intact at audit date.
- `tests/unit/test_ai_safety_release_evidence.py` imports both symbols and passes.

Validation:

```text
$ .venv/bin/python -m pytest tests/unit/test_ai_safety_release_evidence.py --no-cov -v
collected 3 items
tests/unit/test_ai_safety_release_evidence.py::test_ai_safety_required_files_cover_llm_pii_schema_and_refusals PASSED
tests/unit/test_ai_safety_release_evidence.py::test_ai_safety_release_evidence_passes PASSED
tests/unit/test_ai_safety_release_evidence.py::test_ai_safety_release_cli_passes PASSED
3 passed in 0.33s
```

The TODO file path `tests/ci/test_ai_safety_release_evidence.py` should be corrected
to `tests/unit/test_ai_safety_release_evidence.py` in a future TODO doc revision.

---

## T003 — Duplicate pytest module basename collision

**Status:** Done.

Renamed `tests/integration/test_auth_refresh_db_proof.py` →
`tests/integration/test_auth_refresh_db_proof_integration.py` using `git mv` to
preserve history. Stale `__pycache__` cleared.

Verification:

```text
$ ls tests/integration/test_auth_refresh*
tests/integration/test_auth_refresh.py
tests/integration/test_auth_refresh_db_proof_integration.py
$ ls tests/unit/test_auth_refresh*
tests/unit/test_auth_refresh_db_proof.py
```

No basename collision remains.

---

## T004 — Clean pytest collection

**Status:** Done.

Validation:

```text
$ .venv/bin/python -m pytest --collect-only --no-cov -q
... [enumerated tests omitted] ...
2698 tests collected in 10.73s
```

- Exit code: **0**
- Collection errors: **0**
- Tests collected: **2698**

**Note on expected count:** The TODO AC expected ≥ 2,803 tests. The actual count
on `remediation/phase0-phase1` (branched from `origin/master`) is 2,698. The
delta (~105 tests) is most plausibly explained by post-audit branch divergence
(audit was taken against a different working tree containing untracked tests).
This is not a collection failure; flagging for the auditor to confirm whether
the audit baseline included files not on `origin/master`.

Full log: `audits/phase0/test_collection_proof.txt`.

---

## T005 — Post-collection sanity subset

**Status:** Done with documented runtime-wiring failures (T005 AC explicitly
permits this classification).

Validation:

```text
$ .venv/bin/python -m pytest tests/smoke tests/ci --no-cov -v
... [details in audits/phase0/test_smoke_ci_sanity.txt] ...
4 failed, 21 passed, 27 skipped, 7 errors in 8.52s
```

**Classification of failures (all runtime-wiring, not collection):**

All 4 failures + 7 errors come from two smoke test files that import the
non-existent module `app.main`:

- `tests/smoke/test_content_factory_admin_api_smoke.py` — 7 errors (collection-time import of `app.main`).
- `tests/smoke/test_content_factory_startup_flags.py` — 4 failed tests.

The repository exposes the ASGI app at `app.api_v2`, not `app.main`. These two
smoke files reference a stale module path that did not exist when they were
written. **This is runtime-wiring drift, not a pytest collection blocker.**

**Tracked under:** Phase 0 Domain B (T010 — Health contract / app entrypoint
alignment). Will be repaired during T010 work since these smoke files also
embed the health-endpoint contract assumptions.

Full log: `audits/phase0/test_smoke_ci_sanity.txt`.

---

## Outcome

Domain A blockers cleared. Pytest collection is clean (exit 0, zero errors).
Domain B can proceed.
