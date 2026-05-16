# Warning Cleanup Register

This register tracks non-failing warnings observed after the repository-local green baseline.

## Current warning classes

| Warning | Source | Disposition |
|---|---|---|
| Hypothesis `.hypothesis` collection warning | `pytest.ini` `norecursedirs` replaced pytest defaults | Addressed by restoring default-style ignores including `.hypothesis`. |
| `AsyncMockMixin._execute_mock_call` was never awaited | Unit tests that used `AsyncMock()` for SQLAlchemy session objects where `db.add()` is synchronous | Addressed by explicitly setting synchronous `session.add = MagicMock()` in repository unit fixtures. |
| Redis asyncio connection cleanup after full suite | Redis client lifecycle / event-loop shutdown | Track for later teardown hardening if it recurs after CI run. |

## Policy

Warnings should not be hidden globally unless they are third-party noise with no project remediation path. Project-owned warnings should be fixed or tracked here.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_v2_repositories_full.py tests/unit/test_v2_services_full.py -q --no-cov
pytest -c pytest.ini tests/unit -q --no-cov
pytest -c pytest.ini -q --no-cov
```
