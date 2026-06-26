# DB Migration + Seed Repeatability Status

Generated at: `2026-06-24T11:30:00Z`
Commit: `f5d72b8380da6403371ea91f6c8298626ba07aa1`

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
