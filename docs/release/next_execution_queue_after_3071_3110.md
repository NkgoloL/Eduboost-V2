---
title: "Release — Next Execution Queue After DB-REPEATABILITY-001R / code_3071_3110"
status: "active"
owner: "release"
reviewers: ['release', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Next Execution Queue After DB-REPEATABILITY-001R / code_3071_3110

## Recommended next DB batches

1. `DB-OWNERSHIP-001R / code_3111_3150` — decide ownership for live-only POPIA/DSR tables: `consent_records`, `data_export_requests`, `erasure_requests`, `correction_requests`, and `restriction_requests`.
2. `DIAG-ITEMS-001R / code_3111_3150` — decide whether `diagnostic_items` should be populated or formally document `irt_items` as canonical.
3. `AUDIT-WRITE-001R / code_3111_3150` — exercise a staging flow that writes `audit_events`, then verify and attach evidence.
4. `DB-ROLLBACK-001R / code_3111_3150` — add migration rollback/restore evidence.

## Manual apply reference

```bash
make db-migration-seed-repeatability-status
npx --yes supabase db query --linked --file temp/db_repeatability/alembic_upgrade_head.supabase.sql
npx --yes supabase db query --linked --file temp/db_repeatability/seed_irt_items.sql
```
