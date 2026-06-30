# First Audit Runtime Wiring PR Checklist

## Scope

- [ ] Exactly one audit candidate wired
- [ ] Candidate uses `AuditRepositoryCompatAdapter`
- [ ] In-memory/non-DB tests pass
- [ ] No repository deletion
- [ ] No consent table merge
- [ ] No schema migration
- [ ] No route registration change
- [ ] No production database mutation

## Verification

```bash
make backend-implementation-421-430-full-check
pytest -c pytest.ini -q --no-cov
```

## Release owner decision

- [ ] Approved
- [ ] Blocked
- [ ] Requires changes
