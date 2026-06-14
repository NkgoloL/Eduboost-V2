# Phase 2 Execution Plan — Semantic Retrieval and Grounding

**Status:** Ready for integration; execution approval required before branch work begins
**Target branch:** `feature/atlas-phase-02-grounded-semantic-retrieval`
**Depends on:** Phase 1 merged and post-merge verified, migration head `20260614_0900_p1_validation`
**Objective:** retrieve only approved, correctly scoped source chunks and propagate immutable provenance into Phase 1 generation.

## 1. Start gate

Phase 2 may start only when:

- [ ] Phase 1 is `Verified Complete` on the canonical branch.
- [ ] The Phase 1 merge SHA and CI run are recorded.
- [ ] This plan is reviewed and approved.
- [ ] A disposable PostgreSQL 16 environment with the `vector` extension is available.
- [ ] The embedding deployment and data-transfer assessment are approved.
- [ ] The curriculum owner approves the release evaluation dataset and thresholds.

## 2. Architecture decision

### Canonical corpus

Phase 2 introduces independent source-corpus tables:

- `retrieval_source_documents`
- `retrieval_source_chunks`

Generated-artifact source rows are evidence of previous generation; they are not the retrieval corpus. The generation source-context service is therefore redirected to the canonical retrieval tables.

### Embeddings

| Environment | Provider | Model/deployment | Dimensions |
|---|---|---|---:|
| CI/test | Deterministic hashing | `eduboost-hashing-1536` v1 | 1536 |
| Staging/production | Azure OpenAI | Approved `text-embedding-3-small` deployment | 1536 |

The deterministic provider is forbidden in staging and production.

### Search policy

1. Semantic vector search is primary.
2. Full-text fallback is permitted only when:
   - embedding generation fails;
   - the vector query fails; or
   - no vector hit reaches the minimum semantic score.
3. Semantic and fallback paths apply the same mandatory filters.
4. Searchable statuses are fixed to `approved`, `indexed`, and `training_ready`.
5. Incompatible licences, low-quality sources, wrong scope/CAPS/grade/subject/language, and unauthorized permission scopes are always excluded.

## 3. Work packages

### P2.1 — Schema and migration

- Add canonical document/chunk models.
- Add `vector(1536)` extension and column.
- Add HNSW cosine index.
- Add GIN full-text expression index.
- Add filter, version, uniqueness, dimension, quality, and grade controls.
- Add upgrade from the Phase 1 head and a reversible Phase 2 downgrade.

**Acceptance:** clean migration, supported-head upgrade, downgrade/upgrade recovery, correct vector typmod, and expected indexes.

### P2.2 — Embedding providers

- Add the Azure embedding provider.
- Add deterministic CI provider with production guard.
- Normalize provider errors.
- Validate dimensions and finite values.

**Acceptance:** 1536-value vectors, stable CI output, Azure error normalization, deterministic provider rejected in production.

### P2.3 — Retrieval repository and service

- Implement vector similarity search.
- Implement approval-preserving full-text fallback.
- Apply scope, CAPS, grade, subject, language, permission, quality, status, licence, model, and version filters.
- Add minimum semantic-score gate.
- Return full provenance without exposing raw query text in logs.

**Acceptance:** unapproved, out-of-scope, low-quality, unauthorized, and incompatible-license sources never appear.

### P2.4 — Corpus indexing and recovery

- Upsert versioned documents and chunks.
- Embed only searchable sources.
- Remove stale chunks when a document version changes.
- Add document reindex command.
- Add an importer for approved records from the existing SQLite ETL store.
- Preserve hashes, versions, mappings, page/section citations, and source metadata.

**Acceptance:** reindex is deterministic; stale chunks are removed; draft/rejected records have no embeddings; rollback and reindex are documented.

### P2.5 — Phase 1 integration

- Replace artifact-source lookup in `ContentGenerationSourceContextService`.
- Resolve source chunks from the canonical approved corpus.
- Fail closed for missing or filtered requested chunks.
- Propagate document/chunk IDs, hashes, mappings, quality, licence, and status into the Phase 1 provenance bundle.

**Acceptance:** a generated artifact can prove exactly which immutable source chunks informed it.

### P2.6 — Evaluation and operational proof

- Add unit and PostgreSQL integration tests.
- Add a retrieval evaluation framework with Recall@K, MRR, Precision@K, and unsafe-hit count.
- Add HNSW and full-text index proof.
- Add migration and recovery verification scripts.
- Capture latency and query-plan evidence on a representative corpus.

**Minimum release thresholds:**

- Recall@5 ≥ 0.80
- MRR ≥ 0.60
- unsafe/unapproved hit count = 0
- all approved-filter negative tests pass
- migration/recovery tests pass

The included JSON dataset is a technical fixture. It must be replaced or formally approved by the curriculum owner before closure.

## 4. Security, privacy and data controls

- Query logs contain a SHA-256 fingerprint, not learner query text.
- No learner identifier is stored in the retrieval corpus.
- Permission scope is server-enforced.
- Production embeddings use the approved Azure endpoint and DPA/data-transfer controls.
- Unapproved documents cannot be made searchable merely by having an embedding.
- Full-text fallback cannot relax approval, licence, quality, scope, or permission rules.

## 5. Rollback and recovery

- Application rollback remains compatible because Phase 1 does not depend on the new tables until the Phase 2 code is deployed.
- Phase 2 migration downgrade removes only Phase 2 tables and indexes; it retains the shared `vector` extension.
- Reindexing can reconstruct vectors from versioned chunk content.
- Source hashes and document versions detect source drift.
- Backup of source documents/chunks is required before destructive corpus replacement.

## 6. Verification commands

```bash
./scripts/verify_phase2.sh
./scripts/verify_phase2_postgres.sh
SEMANTIC_EMBEDDING_PROVIDER=deterministic \
  python scripts/phase2_evaluate_retrieval.py \
  --dataset data/retrieval/phase2_evaluation_set.json \
  --output docs/release-evidence/phase-02/retrieval_metrics.json
```

## 7. Required control set

| Artifact | Path |
|---|---|
| Execution plan | `docs/roadmap/execution/phase_02_execution_plan.md` |
| Implementation report | `docs/roadmap/execution/phase_02_implementation_report.md` |
| Evidence pack/index | `docs/release-evidence/phase-02/phase_02_evidence_index.md` |
| Independent audit | `docs/release-evidence/phase-02/phase_02_audit_report.md` |

## 8. Closure rule

Phase 2 cannot be marked complete until:

- all plan acceptance criteria are reconciled in the implementation report;
- PostgreSQL, migration, retrieval-quality, filtering, provenance, reindex and recovery evidence is frozen against the merge commit;
- the approved evaluation thresholds pass;
- the PR is merged and post-merge CI passes; and
- an independent audit issues a passing verdict with no blocking findings.
