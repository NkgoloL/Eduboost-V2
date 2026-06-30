# Database Migration Evidence

**Status:** pending runtime execution
<!-- Status: pending runtime execution -->

This file is the stable release gate for database migration evidence. It must remain pending until a disposable PostgreSQL migration run is accepted by the release owner.

Latest raw migration output, when available:

- JSON: `docs/release/migration_latest.json`
- Markdown: `docs/release/migration_latest.md`

## Required environment

| Field | Value |
|---|---|
| Database name | TODO |
| Database host | TODO |
| Commit SHA | TODO |
| Alembic head before | TODO |
| Alembic head after | TODO |
| Operator | TODO |
| Timestamp UTC | TODO |

## Required checks

| Check | Expected result | Evidence |
|---|---|---|
| `alembic current` before upgrade | known baseline or empty DB | TODO |
| `alembic upgrade head` | succeeds | TODO |
| `alembic current` after upgrade | at repository head | TODO |
| schema integrity check | succeeds | TODO |
| migration graph check | single linear/resolvable head | TODO |
| downgrade/rollback path | succeeds or documented non-downgrade rationale | TODO |

## Command log

```bash
# paste accepted migration evidence commands and output here
```

## Decision

- [ ] Migration proof passed and is accepted for release evidence.
- [ ] Migration proof failed and release is blocked.
