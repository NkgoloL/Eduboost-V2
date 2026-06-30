# Restore Drill Evidence

**Status:** pending runtime execution
<!-- Status: pending runtime execution -->

| Field | Value |
|---|---|
| Result | Preflight failed; runtime restore not executed |
| Evidence URL/path | `make database-restore-dry-run` output captured in session |
| Operator | Codex |
| Notes | Missing `DATABASE_URL` and `BACKUP_ENCRYPTION_KEY`; target environment `staging` was accepted. Dry-run printed required verification steps. |
| Captured at | 2026-05-22T14:26:54Z |

## Checklists
- Backup checksum: TODO
- Restore command completed: TODO
- application smoke after restore: TODO
