---
title: DB Live-Only Table Ownership Status
status: release-record
owner: release-management
reviewers: [release-management, evidence-custodian, documentation-governance]
audience: release-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 180
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/release, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# DB Live-Only Table Ownership Status

Generated at: `2026-06-27T02:18:49Z`
Commit: `88840fc52a05c694c6d313e57bc8cba4bcda4c63`

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
