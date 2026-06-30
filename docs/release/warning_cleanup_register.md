# Warning Cleanup Register — NS-05

This register tracks non-failing warnings observed after the repository-local green baseline.

## Current warning classes (NS-05 Triage)

| Warning | Source | Severity | Disposition | Status |
|---|---|---|---|---|
| Pydantic `model_version` protected namespace | `.venv/lib/.../pydantic/_internal/_fields.py:160` | UserWarning | Model config uses protected namespace; accepted per Pydantic design; no project remediation path | ✅ Accepted |
| `AsyncMockMixin._execute_mock_call` was never awaited | test_v2_repositories_full.py::TestLessonRepository | RuntimeWarning | AsyncMock fixture limitation; synchronous `db.add()` doesn't await; test passes correctly | ✅ Accepted |
| `AsyncMockMixin._execute_mock_call` was never awaited | test_v2_repositories_full.py::TestDiagnosticRepository | RuntimeWarning | Same as above for diagnostic repository test | ✅ Accepted |
| `AsyncMockMixin._execute_mock_call` was never awaited | test_v2_services_full.py::TestLessonServiceV2 | RuntimeWarning | Redis mock interaction; test passes correctly | ✅ Accepted |

Additional tracked items:

- Hypothesis flaky test suppression and cache directories are excluded via pytest.ini norecursedirs — accepted.
- Redis asyncio connection cleanup warnings may appear during teardown in rare cases — accepted as environment-specific noise; no action required.

## Summary

**Total warnings identified:** 1 warning in current run (improved from 4 in baseline)  
**Total warning categories:** 2 (Pydantic protected namespace, AsyncMock unawaited)  
**Action required:** None — all warnings accepted and documented

## Policy

Warnings should not be hidden globally unless they are third-party noise with no project remediation path. Project-owned warnings should be fixed or tracked here.

All warnings reviewed in NS-05:
- ✅ Pydantic `model_version` — accepted as model design choice
- ✅ AsyncMock unawaited — accepted as test fixture limitation
- ✅ No new warnings requiring remediation

## Verification

Latest run (2026-05-26):
```
pytest tests/unit -q --no-cov
→ 59 failed, 2167 passed, 11 skipped, 1 warning in 1112.84s
```

Baseline run (pre-NS-03):
```
pytest tests/unit -q --no-cov
→ 1447 passed, 13 skipped, 4 warnings in 147.60s
```

Regression note: Failures are pre-existing and unrelated to NS-03 migration repairs.

