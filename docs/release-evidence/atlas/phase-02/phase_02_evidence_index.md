# Phase 2 Evidence Pack and Index

**Status:** Complete — live closure evidence captured
**Evidence source state:** verified PostgreSQL integration proof

## 1. Criterion traceability

| Criterion | Evidence | Status |
|---|---|---|
| Vector schema and index verified | Migration SQL, PostgreSQL test, Compose definition, and live query plans | Verified |
| Unapproved/out-of-scope content excluded | Unit policy tests, PostgreSQL negative tests, and live fail-closed retrieval proof | Verified |
| Fallback conditions controlled | Unit tests for embedding/vector/no-hit fallback | Verified |
| Retrieval thresholds pass | Evaluation framework, fixture, and live threshold run | Verified |
| Migration/recovery pass | Upgrade/downgrade verification script and live PostgreSQL run | Verified |
| Generation source chunks attributable | Source-context integration tests and live artifact provenance | Verified |

## 2. Collected raw evidence

Package raw evidence includes:

- `phase2_environment.txt`
- `phase2_unit_tests.txt`
- `phase2_and_phase1_tests.txt`
- `phase2_ruff.txt`
- `phase2_migration_graph.txt`
- `phase2_alembic_head.txt`
- `phase2_migration_offline.sql`
- `phase2_verify_script.txt`
- `phase2_patch_apply_verify.txt`

Current headline results:

```text
15 passed
Phase 1 regression: 95 passed, 2 database-gated skips
Combined regression: 110 passed, 9 database-gated skips
Patch application verification: passed
All checks passed!
Migration graph OK: 36 revisions, head=20260614_1200_p2_retrieval
22 passed
7 passed
Alembic upgrade, downgrade, and re-upgrade completed against live PostgreSQL
```

## 3. Live closure evidence

The closure proof files are:

- `phase2_live_closure_evidence.md`
- `phase2_live_closure_evidence.json`

Live proof highlights:

- PostgreSQL migration head: `20260614_1200_p2_retrieval`
- Retrieval evaluation passed: `True`
- Evaluation dataset: `phase2-technical-acceptance-v1`
- Evaluation metrics: `recall_at_k: 1.0`, `mean_reciprocal_rank: 1.0`, `unsafe_hit_count: 0`
- Generated artifact status: `ContentArtifactStatus.PENDING_REVIEW`
- Source rows written: `2`
- Retrieved chunks: `whole-numbers`, `geometry`
- Excluded chunk: `draft-whole-numbers`
- Query plans captured for semantic and HNSW probes

## 4. Closure integrity

The live closure evidence is sufficient to close Phase 2 because it binds the evaluation, retrieval, migration, and provenance claims to the same verified disposable PostgreSQL run.

## 5. Evidence integrity

Before archival:

- calculate SHA-256 for every raw artifact;
- store exact commands and exit codes;
- exclude secrets, raw learner queries and personal information;
- retain only query fingerprints in logs;
- bind all evidence to the merge commit and environment identity.
