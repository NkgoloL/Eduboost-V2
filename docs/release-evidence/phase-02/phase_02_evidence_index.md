# Phase 2 Evidence Pack and Index

**Status:** Partial — implementation evidence collected; canonical PostgreSQL and post-merge evidence pending
**Evidence source state:** preparation overlay, not a canonical merge commit

## 1. Criterion traceability

| Criterion | Evidence | Status |
|---|---|---|
| Vector schema and index verified | Migration SQL, PostgreSQL test and Compose definition | Pending live DB execution |
| Unapproved/out-of-scope content excluded | Unit policy tests and PostgreSQL negative tests | Code verified; live DB pending |
| Fallback conditions controlled | Unit tests for embedding/vector/no-hit fallback | Verified locally |
| Retrieval thresholds pass | Evaluation framework and fixture | Final approved dataset pending |
| Migration/recovery pass | Upgrade/downgrade verification script | Pending live DB execution |
| Generation source chunks attributable | Source-context integration tests | Verified locally; E2E pending |

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
```

## 3. Required integration evidence

The integrating branch must add:

- branch, base SHA, feature commit and merge SHA;
- clean-worktree output;
- supported Python/tool versions;
- `docker compose` image digest for `pgvector/pgvector:pg16`;
- migration from Phase 1 head to Phase 2 head;
- clean database to Phase 2 head;
- Phase 2 downgrade and re-upgrade;
- `vector(1536)` typmod proof;
- HNSW and GIN index inventory;
- query plans on a representative corpus;
- full PostgreSQL test output with zero skips;
- approved evaluation dataset hash and reviewer;
- Recall@K, MRR, Precision@K and unsafe-hit results;
- source-filter negative-test output;
- source mutation/version/reindex evidence;
- Phase 1 end-to-end generation provenance sample;
- backup/restore/reindex drill;
- post-merge CI URL and artifacts.

## 4. Evidence integrity

Before closure:

- calculate SHA-256 for every raw artifact;
- store exact commands and exit codes;
- exclude secrets, raw learner queries and personal information;
- retain only query fingerprints in logs;
- bind all evidence to the merge commit and environment identity.

## 5. Current limitation

Docker was unavailable in the preparation environment. No claim is made that PostgreSQL migration, vector indexing, query-plan, recovery or full integration tests have already passed.
