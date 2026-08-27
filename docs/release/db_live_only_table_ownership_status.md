# DB Live-Only Table Ownership Status

Generated at: `2026-08-26T17:20:25Z`
Commit: `107d58c62d28a0d0a7a094f69894809af40f8db0`

**Status:** `db-live-only-table-ownership-accepted`
**Policy:** `docs/architecture/db_live_only_table_ownership.yml`
**Accepted records:** `5/5`

## Records

| Table | Domain | Ownership | ORM model required | ORM model detected | Migration action | Beta blocking | Accepted |
|---|---|---|---:|---:|---|---:|---:|
| `consent_records` | `popia-consent` | `sql-owned` | False | False | `document-and-monitor` | False | True |
| `data_export_requests` | `data-subject-rights` | `sql-owned` | False | False | `document-and-monitor` | False | True |
| `erasure_requests` | `data-subject-rights` | `sql-owned` | False | False | `document-and-monitor` | False | True |
| `correction_requests` | `data-subject-rights` | `sql-owned` | False | False | `document-and-monitor` | False | True |
| `restriction_requests` | `data-subject-rights` | `sql-owned` | False | False | `document-and-monitor` | False | True |

## Blockers

- None

## No false-closure rules

- `sql-owned` means the table is documented as live SQL-owned and monitored, not ORM-managed.
- This status does not add ORM models.
- This status does not drop, rename, migrate, or backfill live tables.
- This status does not prove audit writes, backup/restore/rollback, or legal approval.
- If any table later becomes `migration-required`, it must become beta-blocking until migrated.
