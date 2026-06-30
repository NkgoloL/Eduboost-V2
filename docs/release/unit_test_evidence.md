# Unit Test Evidence

Generated at: `2026-05-22T14:26:54Z`
Commit: `ec48d99ff48d4ad08572fa300cd0d50b25fbc0ec`
Branch: `codex/production_readiness`
Command: `pytest -c pytest.ini tests/unit -q --no-cov`
Exit code: `0`
Result: `2051 passed, 1 skipped, 1 warning in 616.67s (0:10:16)`
Raw log: `temp/release_evidence/ns04_unit_tests_final.log`

## Environment Notes

- Redis was started with `docker compose up -d redis` because the auth HTTP proof scripts exercise routes that connect to `localhost:6379`.
- The active virtualenv was missing the declared dev dependency `aiosqlite==0.22.1`; it was installed from the already-committed `requirements/dev.txt` declaration before rerunning the suite.

## Warning Triage

Status: accepted and tracked for follow-up.

- Warning: `RuntimeWarning: coroutine AsyncMockMixin._execute_mock_call was never awaited` in `tests/unit/test_v2_services_full.py::TestLessonServiceV2::test_generate_enforces_quota`.
- Impact: non-failing warning only; the full unit suite passed.
- Follow-up: adjust the mocked collaborator in that test so async call expectations are awaited or replaced with a synchronous mock where appropriate.

## Full Output

```text
........................................................................ [  3%]
........................................................................ [  7%]
......s................................................................. [ 10%]
........................................................................ [ 14%]
........................................................................ [ 17%]
........................................................................ [ 21%]
........................................................................ [ 24%]
........................................................................ [ 28%]
........................................................................ [ 31%]
........................................................................ [ 35%]
........................................................................ [ 38%]
........................................................................ [ 42%]
........................................................................ [ 45%]
........................................................................ [ 49%]
........................................................................ [ 52%]
........................................................................ [ 56%]
........................................................................ [ 59%]
........................................................................ [ 63%]
........................................................................ [ 66%]
........................................................................ [ 70%]
........................................................................ [ 73%]
........................................................................ [ 77%]
........................................................................ [ 80%]
........................................................................ [ 84%]
........................................................................ [ 87%]
........................................................................ [ 91%]
........................................................................ [ 94%]
........................................................................ [ 98%]
....................................                                     [100%]
=============================== warnings summary ===============================
tests/unit/test_v2_services_full.py::TestLessonServiceV2::test_generate_enforces_quota
  /usr/lib/python3.12/unittest/mock.py:2188: RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
    def __init__(self, name, parent):
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
2051 passed, 1 skipped, 1 warning in 616.67s (0:10:16)
```