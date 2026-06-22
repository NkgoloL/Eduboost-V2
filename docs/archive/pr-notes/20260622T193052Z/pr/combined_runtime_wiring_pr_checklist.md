# Combined Runtime Wiring PR Checklist

## Scope

- [ ] Exactly one consent runtime candidate
- [ ] Read-only deep-readiness plan only
- [ ] No consent table merge
- [ ] No route registration change unless separately approved
- [ ] No DB write from public health/readiness
- [ ] No Alembic stamp/baseline
- [ ] Full tests pass

## Verification

```bash
make backend-implementation-431-450-full-check
pytest -c pytest.ini -q --no-cov
```
