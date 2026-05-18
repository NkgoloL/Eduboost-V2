# Restore Drill Evidence

**Status:** pending runtime execution
<!-- Status: pending runtime execution -->

This file is the stable release gate for backup/restore drill evidence. It must remain pending until a real backup and restore drill is accepted by the release owner.

Latest raw restore output, when available:

- JSON: `docs/release/restore_latest.json`
- Markdown: `docs/release/restore_latest.md`

## Required environment

| Field | Value |
|---|---|
| Source database | TODO |
| Backup checksum | TODO |
| Backup file size | TODO |
| Restore target host | TODO |
| Commit SHA | TODO |
| Operator | TODO |
| Timestamp UTC | TODO |

## Required checks

| Check | Expected result | Evidence |
|---|---|---|
| Backup checksum | verified and matches source | TODO |
| Restore command completed | succeeds without errors | TODO |
| application smoke after restore | health endpoints respond correctly | TODO |
| Data integrity validation | all critical tables match source | TODO |
| Permission structure intact | user roles and access levels correct | TODO |

## Command log

```bash
# paste accepted restore evidence commands and output here
```

## Decision

- [ ] Restore drill passed and is accepted for release evidence.
- [ ] Restore drill failed and release is blocked.
