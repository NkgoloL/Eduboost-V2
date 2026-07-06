---
title: DB Migration + Seed Repeatability Status
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

# DB Migration + Seed Repeatability Status

Generated at: `2026-06-27T02:18:52Z`
Commit: `88840fc52a05c694c6d313e57bc8cba4bcda4c63`

**Status:** `db-migration-seed-repeatability-not-proven`
**Raw Alembic SQL:** `temp/db_repeatability/alembic_upgrade_head.raw.sql`
**Supabase SQL:** `temp/db_repeatability/alembic_upgrade_head.supabase.sql`
**IRT seed SQL:** `temp/db_repeatability/seed_irt_items.sql`

## Summary

- Alembic head `20260516_0100` present: `True`
- Raw SQL lines: `1192`
- Supabase SQL lines: `1158`
- Removed chatter lines: `16`
- Removed broken null seed blocks: `2`
- Removed Supabase role lines: `2`
- Generated IRT seed rows: `1600`
- Unique IRT seed rows: `1600`

## Required runtime tables

| Table | DDL present |
|---|---:|
| `audit_events` | True |
| `audit_logs` | True |
| `calibration_audits` | True |
| `diagnostic_items` | True |
| `diagnostic_sessions` | True |
| `guardians` | True |
| `irt_items` | True |
| `item_exposures` | True |
| `knowledge_gaps` | True |
| `learner_profiles` | True |
| `lesson_feedback` | True |
| `lessons` | True |
| `mastery_snapshots` | True |
| `parental_consents` | True |
| `practice_queue` | True |
| `rlhf_exports` | True |
| `spaced_review_schedule` | True |
| `stripe_webhook_events` | True |
| `subject_mastery` | True |
| `topic_mastery` | True |

## Apply commands

```bash
# Generate checked SQL artifacts
make db-migration-seed-repeatability-status

# Apply manually to linked Supabase after review
npx --yes supabase db query --linked --file temp/db_repeatability/alembic_upgrade_head.supabase.sql
npx --yes supabase db query --linked --file temp/db_repeatability/seed_irt_items.sql
```

## Blockers

- alembic upgrade head --sql failed

## No false-closure rules

- This proves repeatable generation of Supabase-safe migration and IRT seed SQL.
- It does not prove remote apply unless the generated SQL is applied and verified separately.
- It does not decide whether `diagnostic_items` should be populated.
- It does not decide ownership of live-only POPIA/DSR tables.
- It does not prove audit writes or backup/restore/rollback posture.
