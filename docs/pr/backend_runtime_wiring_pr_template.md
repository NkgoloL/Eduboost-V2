# Backend Runtime Wiring PR Template

## Scope

- [ ] Exactly one low-risk audit/consent call path wired
- [ ] Adapter-backed canonical payload used
- [ ] No repository deletion
- [ ] No consent table merge
- [ ] No Alembic stamp/baseline
- [ ] No public health write probe

## Evidence

```bash
make backend-runtime-enablement-full-check
pytest -c pytest.ini -q --no-cov
```

## Decision

- [ ] Approved for merge
- [ ] Blocked
