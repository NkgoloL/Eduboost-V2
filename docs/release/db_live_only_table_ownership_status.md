---
title: "Release — DB Live-Only Table Ownership Status"
status: "active"
owner: "release"
reviewers: ['release', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-17"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# DB Live-Only Table Ownership Status

Generated at: `2026-09-17T09:42:00Z`
Commit: `51b18bfc46fef2bac2a7762e43b51982fb1316b6`

**Status:** `db-live-only-table-ownership-accepted`
**Policy:** `docs/architecture/db_live_only_table_ownership.yml`
**Accepted records:** `5/5`

## Records

| Table | Domain | Ownership | ORM model required | ORM model detected | Migration action | Beta blocking | Accepted |
|---|---|---|---:|---:|---|---:|---:|
| `consent_records` | `popia-consent` | `legacy-retired` | False | False | `dropped-via-reconcile-migration-20260913_2300` | False | True |
| `data_export_requests` | `data-subject-rights` | `legacy-retired` | False | False | `dropped-via-reconcile-migration-20260913_2300` | False | True |
| `erasure_requests` | `data-subject-rights` | `legacy-retired` | False | False | `dropped-via-reconcile-migration-20260913_2300` | False | True |
| `correction_requests` | `data-subject-rights` | `legacy-retired` | False | False | `dropped-via-reconcile-migration-20260913_2300` | False | True |
| `restriction_requests` | `data-subject-rights` | `legacy-retired` | False | False | `dropped-via-reconcile-migration-20260913_2300` | False | True |

## Blockers

- None

## No false-closure rules

- `sql-owned` means the table is documented as live SQL-owned and monitored, not ORM-managed.
- `legacy-retired` means the table was dropped via reconciliation migration and is no longer present.
- This status does not add ORM models.
- This status does not drop, rename, migrate, or backfill live tables.
- This status does not prove audit writes, backup/restore/rollback, or legal approval.
- If any table later becomes `migration-required`, it must become beta-blocking until migrated.
