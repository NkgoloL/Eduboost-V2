# Runtime Integration PR Template

## Scope

- [ ] One scoped runtime integration target
- [ ] No route registration unless explicitly approved
- [ ] No schema migration
- [ ] No destructive data operation
- [ ] Tests added or updated
- [ ] Rollback path documented

## Evidence

```bash
make backend-runtime-integration-readiness-full-check
pytest -c pytest.ini -q --no-cov
```

## Decision

- [ ] Approved
- [ ] Blocked
- [ ] Requires changes
