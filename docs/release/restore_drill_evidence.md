# Backup and Restore Drill Evidence

**Status:** pending runtime execution

This file records proof that a database backup can be restored into a disposable environment and pass post-restore checks.

## Required environment

| Field | Value |
|---|---|
| Source database | TODO |
| Restore target database | TODO |
| Backup artefact ID/path | TODO |
| Backup checksum | TODO |
| Commit SHA | TODO |
| Operator | TODO |
| Timestamp UTC | TODO |

## Required checks

| Check | Expected result | Evidence |
|---|---|---|
| Backup command completed | backup created | TODO |
| Backup checksum recorded | checksum available | TODO |
| Restore command completed | restore succeeded | TODO |
| `alembic current` after restore | at expected head | TODO |
| application smoke after restore | critical routes pass | TODO |
| data integrity spot checks | representative rows present | TODO |

## Command log

```bash
# paste commands and output here
```

## Decision

- [ ] Restore drill passed.
- [ ] Restore drill failed and release is blocked.
