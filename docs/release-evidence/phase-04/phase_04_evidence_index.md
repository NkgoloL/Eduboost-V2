# Phase 4 Evidence Index — IRT Quality and Self-Healing Controls

**Status:** Evidence Complete — independent audit pending  
**Source branch:** `feature/atlas-phase-04-irt-quality-and-self-healing`  
**Source commit:** `277e76ade48b6cb2b21f9d0856610f374cfcdc93`  
**Collected:** 2026-06-15T09:38:16Z

| Criterion | Status | Evidence |
|---|---|---|
| Approved minimum sample/data-quality policy | Verified | `raw/phase4_fast_verification.txt` |
| Healthy/monitor/review/quarantine/retire decisions | Verified | `raw/phase4_fast_verification.txt` |
| No automatic answer-position mutation | Verified | `raw/phase4_fast_verification.txt` |
| Quarantined/retired items excluded from serving | Verified | `raw/phase4_fast_verification.txt` and PostgreSQL run |
| Rewrites return to Phase 3 pending review | Verified | `raw/phase4_fast_verification.txt` |
| Durable nightly job and admin controls registered | Verified | `raw/phase4_fast_verification.txt` |
| Migration from Phase 3 and recovery | Verified | `raw/phase4_postgres_verification.txt` |
| Append-only calibration events | Verified | `raw/phase4_postgres_verification.txt` |
| Phase 1-3 regression | Verified | fast and PostgreSQL verification logs |
| Migration graph and schema integrity | Verified | `raw/migration_graph.txt`, `raw/schema_integrity.txt` |
| Raw evidence hashes | Verified | `raw/SHA256SUMS` |

No audit verdict is implied by this index. The phase remains open until an independent audit is completed against the canonical merge commit.
