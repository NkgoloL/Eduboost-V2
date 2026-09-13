# DB Live-Only Table Ownership Status

Generated at: `2026-09-13T20:45:41Z`
Commit: `f9c9d1112cd560a40a5d2f2c433829aea7c41894`

**Status:** `db-live-only-table-ownership-accepted`
**Policy:** `docs/architecture/db_live_only_table_ownership.yml`
**Accepted records:** `5/5`

## Records

| Table | Domain | Ownership | ORM model required | ORM model detected | Migration action | Beta blocking | Accepted |
|---|---|---|---:|---:|---|---:|---:|
| `consent_records` | `popia-consent` | `orm-managed` | True | True | `none` | False | True |
| `data_export_requests` | `data-subject-rights` | `orm-managed` | True | True | `none` | False | True |
| `erasure_requests` | `data-subject-rights` | `orm-managed` | True | True | `none` | False | True |
| `correction_requests` | `data-subject-rights` | `orm-managed` | True | True | `none` | False | True |
| `restriction_requests` | `data-subject-rights` | `orm-managed` | True | True | `none` | False | True |

## Blockers

- None

## No false-closure rules

- `sql-owned` means the table is documented as live SQL-owned and monitored, not ORM-managed.
- This status does not add ORM models.
- This status does not drop, rename, migrate, or backfill live tables.
- This status does not prove audit writes, backup/restore/rollback, or legal approval.
- If any table later becomes `migration-required`, it must become beta-blocking until migrated.
