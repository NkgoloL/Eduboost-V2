# Database Migration Latest Run

**Status:** migration evidence passed
<!-- Status: migration evidence passed -->

- Captured at: `2026-05-16T12:48:25Z`
- Database URL: `postgresql+asyncpg://eduboost_user:***@localhost:5432/eduboost_test`
- Include downgrade: `False`
- JSON evidence: `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/docs/release/migration_latest.json`

| Step | Command | Return code | Passed |
|---|---|---:|---|
| alembic_current_before | `alembic current` | 0 | yes |
| alembic_upgrade_head | `alembic upgrade head` | 0 | yes |
| alembic_current_after | `alembic current` | 0 | yes |
| migration_graph_check | `/usr/bin/python3 scripts/verify_migration_graph.py` | 0 | yes |
| schema_integrity_check | `/usr/bin/python3 scripts/validate_schema_integrity.py` | 0 | yes |

## Command output

### alembic_current_before

```text
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

### alembic_upgrade_head

```text
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 0001_v2_consolidated, Initial V2 Consolidated Schema Migration
INFO  [alembic.runtime.migration] Running upgrade  -> 0001_v2_consolidated, Initial V2 Consolidated Schema Migration
INFO  [alembic.runtime.migration] Running upgrade 0001_v2_consolidated -> merge_2026_05_01, Merge Alembic heads into a single linear graph.
INFO  [alembic.runtime.migration] Running upgrade 0001_v2_consolidated -> merge_2026_05_01, Merge Alembic heads into a single linear graph.
INFO  [alembic.runtime.migration] Running upgrade merge_2026_05_01 -> 0005_seed_irt_items, Seed V2 IRT item bank with calibrated starter items.
INFO  [alembic.runtime.migration] Running upgrade merge_2026_05_01 -> 0005_seed_irt_items, Seed V2 IRT item bank with calibrated starter items.
INFO  [alembic.runtime.migration] Running upgrade merge_2026_05_01 -> 0002_add_missing_tables, Retire legacy missing-table migration in favour of canonical V2 schema.
INFO  [alembic.runtime.migration] Running upgrade merge_2026_05_01 -> 0002_add_missing_tables, Retire legacy missing-table migration in favour of canonical V2 schema.
INFO  [alembic.runtime.migration] Running upgrade 0002_add_missing_tables -> 0003_add_items_correct, Add items_correct to DiagnosticSession
INFO  [alembic.runtime.migration] Running upgrade 0002_add_missing_tables -> 0003_add_items_correct, Add items_correct to DiagnosticSession
INFO  [alembic.runtime.migration] Running upgrade 0003_add_items_correct -> 0004_add_rlhf_pipeline, Add RLHF pipeline tables
INFO  [alembic.runtime.migration] Running upgrade 0003_add_items_correct -> 0004_add_rlhf_pipeline, Add RLHF pipeline tables
INFO  [alembic.runtime.migration] Running upgrade 0004_add_rlhf_pipeline, 0005_seed_irt_items -> 94b628483fa7, Merge remaining heads 0004 and 0005
INFO  [alembic.runtime.migration] Running upgrade 0004_add_rlhf_pipeline, 0005_seed_irt_items -> 94b628483fa7, Merge remaining heads 0004 and 0005
INFO  [alembic.runtime.migration] Running upgrade 94b628483fa7 -> 0006, alembic/versions/0006_v2_audit_events.py
─────────────────────────────────────────────────────────────────────────────
Task 23: V2 Append-Only PostgreSQL Audit Service
INFO  [alembic.runtime.migration] Running upgrade 94b628483fa7 -> 0006, alembic/versions/0006_v2_audit_events.py
─────────────────────────────────────────────────────────────────────────────
Task 23: V2 Append-Only PostgreSQL Audit Service
INFO  [alembic.runtime.migration] Running upgrade 0006 -> 0007_caps_irt_item_bank, Expand the CAPS-aligned IRT item bank across Grades R-7 and core subjects.
INFO  [alembic.runtime.migration] Running upgrade 0006 -> 0007_caps_irt_item_bank, Expand the CAPS-aligned IRT item bank across Grades R-7 and core subjects.
INFO  [alembic.runtime.migration] Running upgrade 0007_caps_irt_item_bank -> 0008_lesson_completion_tracking, Track lesson completion timestamps for parent reporting and offline sync.
INFO  [alembic.runtime.migration] Running upgrade 0007_caps_irt_item_bank -> 0008_lesson_completion_tracking, Track lesson completion timestamps for parent reporting and offline sync.
INFO  [alembic.runtime.migration] Running upgrade 0008_lesson_completion_tracking -> 771fb3ac38b8, add missing production indexes and partial indexes
INFO  [alembic.runtime.migration] Running upgrade 0008_lesson_completion_tracking -> 771fb3ac38b8, add missing production indexes and partial indexes
INFO  [alembic.runtime.migration] Running upgrade 771fb3ac38b8 -> 0009_add_subject_mastery, Add subject_mastery table
INFO  [alembic.runtime.migration] Running upgrade 771fb3ac38b8 -> 0009_add_subject_mastery, Add subject_mastery table
INFO  [alembic.runtime.migration] Running upgrade 0009_add_subject_mastery -> 20260507_1200, POPIA consent states and tamper-evident audit chain.
INFO  [alembic.runtime.migration] Running upgrade 0009_add_subject_mastery -> 20260507_1200, POPIA consent states and tamper-evident audit chain.
INFO  [alembic.runtime.migration] Running upgrade 20260507_1200 -> 20260507_1330, database integrity constraints and production indexes.
INFO  [alembic.runtime.migration] Running upgrade 20260507_1200 -> 20260507_1330, database integrity constraints and production indexes.
INFO  [alembic.runtime.migration] Running upgrade 20260507_1330 -> 20260507_1500, Add AI/CAPS diagnostics safety metadata.
INFO  [alembic.runtime.migration] Running upgrade 20260507_1330 -> 20260507_1500, Add AI/CAPS diagnostics safety metadata.
INFO  [alembic.runtime.migration] Running upgrade 20260507_1500 -> 20260509_01, P1-02 — Alembic migration 0009: diagnostic_items table
=======================================================
Place this file at:
    alembic/versions/0009_add_diagnostic_items_table.py
INFO  [alembic.runtime.migration] Running upgrade 20260507_1500 -> 20260509_01, P1-02 — Alembic migration 0009: diagnostic_items table
=======================================================
Place this file at:
    alembic/versions/0009_add_diagnostic_items_table.py
INFO  [alembic.runtime.migration] Running upgrade 20260509_01 -> 20260509_02, P1-03 — Alembic migration 0010: item_exposures table
=====================================================
Place this file at:
    alembic/versions/0010_add_item_exposures_table.py
INFO  [alembic.runtime.migration] Running upgrade 20260509_01 -> 20260509_02, P1-03 — Alembic migration 0010: item_exposures table
=====================================================
Place this file at:
    alembic/versions/0010_add_item_exposures_table.py
INFO  [alembic.runtime.migration] Running upgrade 20260509_02 -> 20260510_0100, Add AL LLM safety fields to lessons.
INFO  [alembic.runtime.migration] Running upgrade 20260509_02 -> 20260510_0100, Add AL LLM safety fields to lessons.
INFO  [alembic.runtime.migration] Running upgrade 20260510_0100 -> 20260510_0200, Add diagnostics assessment lifecycle and mastery tables.
INFO  [alembic.runtime.migration] Running upgrade 20260510_0100 -> 20260510_0200, Add diagnostics assessment lifecycle and mastery tables.
INFO  [alembic.runtime.migration] Running upgrade 20260510_0200 -> 20260510_0300, alembic/versions/0010_popia_consent_audit_dsr.py
Creates all POPIA-related tables (§4.1 §4.3 §4.5).
Sets up row-level trigger to prevent UPDATE/DELETE on audit_events.
INFO  [alembic.runtime.migration] Running upgrade 20260510_0200 -> 20260510_0300, alembic/versions/0010_popia_consent_audit_dsr.py
Creates all POPIA-related tables (§4.1 §4.3 §4.5).
Sets up row-level trigger to prevent UPDATE/DELETE on audit_events.
INFO  [alembic.runtime.migration] Running upgrade 20260510_0300 -> 20260516_0100, alembic/versions/20260516_0100_remove_base_sentinel.py
INFO  [alembic.runtime.migration] Running upgrade 20260510_0300 -> 20260516_0100, alembic/versions/20260516_0100_remove_base_sentinel.py
DEBUG: Creating enum itemtype
DEBUG: Creating enum subjectcode
DEBUG: Creating enum language
DEBUG: Creating enum reviewstatus
DEBUG: Creating enum itemsource
DEBUG: Creating enum difficultyband
```

### alembic_current_after

```text
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
20260516_0100 (head)
```

### migration_graph_check

```text
Migration graph OK: 21 revisions, head=20260516_0100
```

### schema_integrity_check

```text
Schema integrity OK
```
