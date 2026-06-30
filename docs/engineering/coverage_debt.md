# Coverage Debt Register

**Owner:** Engineering
**Last updated:** 2026-06-02 (Phase 1 committed: aa51898e)
**Status:** Baseline established; recovery plan pending

---

## Coverage threshold ratchet plan

| Date | Coverage floor | Gate |
|---|---|---|
| 2026-06-02 | 67% | Active in CI (COVERAGE_THRESHOLD=67) |
| 2026-06-16 | 70% | Raise in .github/workflows/ci-cd.yml after fast-gate cleanup |
| 2026-06-30 | 75% | Raise after ETL/repository tranche is stable |
| 2026-07-14 | 80% | Production target floor |

Ratchet policy:
- Raise only when the previous floor is green for at least 3 consecutive CI runs on main.
- If CI regresses after a ratchet, fix tests/coverage first instead of lowering floor, unless release owner approves an exception.
- Every ratchet change requires a matching evidence update in audits/reports/Coverage_Audit_VM_YYYY-MM-DD.md.

---

## Current state

| Metric | Value | Target | Gap |
|---|---|---|---|
| Tests collected | 2,698 | — | — |
| Smoke tests passing | 32 | 32 | 0 |
| CI coverage threshold | 67% | 67% | 0 |
| Actual coverage | **57.5%** | 67% | **-9.5%** |
| Full-suite coverage run | **Complete** | Required | Done |

**Status:** Coverage baseline is established at 57.5%. The CI gate would fail
if run with coverage enforcement. The threshold is now 67%, so additional coverage uplift work is required before the next ratchet.

---

## Coverage timeout blocker (T130A) — RESOLVED

### Symptoms (before fix)

- `pytest tests/smoke --cov=app` times out after 60s (smoke tests pass in ~14s
  without coverage).
- `pytest tests/unit --cov=app` times out after 120s.
- Full suite coverage run does not complete.

### Root cause

Missing `concurrency` setting in `.coveragerc`. The default coverage tracer is
synchronous and does not handle async event loop switching efficiently.

### Fix applied

Added `.coveragerc` to repository root:

```ini
[run]
branch = True
concurrency = greenlet,thread
dynamic_context = test_function
source = app

[report]
precision = 1
skip_covered = False
show_missing = True

[html]
directory = coverage_html
```

### Results (after fix)

- Smoke tests with coverage: 32 passed in 80.89s (previously timed out)
- Full suite with coverage: 2,252 passed in 35:15, 57.5% coverage

---

## Module risk classification (T132)

Updated with actual coverage data from full-suite baseline:

| Module | Lines | Actual coverage | Criticality | Coverage risk | Rationale |
|---|---|---|---|---|---|
| `app.security` | 201 | 94.0% | **P0** | Low | Well-covered, minor gaps |
| `app.core` | 2,188 | 61.0% | **P0** | Medium | Security/config at 61% — acceptable but could improve |
| `app.api_v2_routers.auth` | ~200 | 38.7% (router avg) | **P0** | High | Auth router coverage is low — critical path |
| `app.api_v2_routers.popia` | ~250 | 38.7% (router avg) | **P0** | High | POPIA router coverage is low — legal requirement |
| `app.services.jwt_keyring` | ~260 | 53.9% (services avg) | **P0** | Medium | Key management — tested but not comprehensively |
| `app.services.stripe_service` | ~200 | 53.9% (services avg) | **P1** | Medium | Billing — average coverage, needs targeted tests |
| `app.services.content_factory` | ~1,500 | 53.9% (services avg) | **P1** | Medium | Content generation — average coverage |
| `app.modules.consent` | ~300 | 70.8% (modules avg) | **P0** | Low | POPIA consent — good coverage |
| `app.modules.lessons` | ~1,800 | 70.8% (modules avg) | **P1** | Low | Lesson generation — good coverage |
| `app.repositories` | 945 | 41.5% | **P1** | Medium | DB access — tested via integration but not directly |
| `app.modules.gamification` | ~400 | 70.8% (modules avg) | **P2** | Low | Gamification — good coverage |
| `app.modules.notifications` | ~250 | 70.8% (modules avg) | **P2** | Low | Notifications — good coverage |
| `app.services.etl` | ~1,400 | 53.9% (services avg) | **P2** | Low | ETL pipelines — average coverage |

---

## Quick-win test opportunities (T133)

Updated with actual coverage data. High-impact, low-effort targets to reach 60%:

1. **Auth router contract tests** — `app/api_v2_routers/auth.py` at 38.7% coverage.
   FastAPI TestClient with mocked services could add ~120 lines (~0.3% overall).

2. **POPIA router contract tests** — `app/api_v2_routers/popia.py` at 38.7% coverage.
   FastAPI TestClient with mocked ConsentService could add ~150 lines (~0.3% overall).

3. **Repository direct tests** — `app.repositories` at 41.5% coverage.
   In-memory DB tests could add ~400 lines (~0.9% overall).

4. **Service contract tests** — `app.services` at 53.9% coverage.
   Targeted tests for stripe_service, content_factory could add ~600 lines (~1.3% overall).

**Estimated quick-win impact:** ~1,270 lines of coverage (~2.8% overall) to reach
60% threshold.

---

## Recovery sprint plan (T134)

### Sprint 1: Unblock measurement — COMPLETE

- [x] T130A: Add `.coveragerc` with async concurrency settings.
- [x] T130B: Run full-suite coverage and record actual baseline (57.5%).
- [x] Document which tests are slow under coverage (all tests now complete in 35 min).

### Sprint 2: P0 security/auth coverage

- [x] Add JWT keyring unit tests.
- [x] Add token config unit tests.
- [x] Add security helper unit tests.
- [x] Add auth router contract tests.

### Sprint 3: P0 POPIA/consent coverage

- [x] Add POPIA router contract tests.
- [x] Add consent service unit tests.
- [x] Add consent repository unit tests.

### Sprint 4: P1 core product coverage

- [ ] Add content factory service tests.
- [ ] Add lesson generation pipeline tests.
- [ ] Add assessment service tests.

### Sprint 5: P1 repository coverage

- [ ] Add direct repository tests with in-memory DB.
- [ ] Add integration tests for critical paths.

---

## Exemptions (T136)

The following code categories may be exempted from coverage targets with
justification:

| Category | Example | Exemption rationale |
|---|---|---|
| Auto-generated schemas | `app/domain/schemas.py` (Pydantic) | Boilerplate, tested implicitly via request validation |
| Alembic migrations | `alembic/versions/*.py` | One-way migration code, tested via `alembic upgrade head` |
| Dev-only fixtures | `app/api_v2_routers/auth.py` dev guardian | Guarded by `if not settings.is_production()` |
| Envelope route boilerplate | `app/core/envelope_route.py` | Framework wrapper, tested via integration |
| Health check endpoints | `app/api_v2.py` health/ready | Always public, always returns 200 — low value to unit test |

**Process:** Any new exemption requires PR approval from Engineering lead.

---

## Validation

```bash
# 1. Confirm collection is clean
.venv/bin/python -m pytest --collect-only --no-cov -q

# 2. Confirm smoke tests pass
.venv/bin/python -m pytest tests/smoke --no-cov -q

# 3. Attempt coverage (should not timeout after .coveragerc fix)
.venv/bin/python -m pytest tests/ --cov=app --cov-report=term-missing --no-cov-on-fail -q
```
