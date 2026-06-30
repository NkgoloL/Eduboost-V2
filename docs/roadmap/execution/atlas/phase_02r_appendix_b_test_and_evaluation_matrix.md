# Phase 2R Appendix B — Test, Verification, and Evaluation Matrix

**Document version:** 1.4  
**Plan date:** 2026-06-16  
**Status:** Draft — approval required with the main Phase 2R execution plan  
**Canonical path:** `docs/roadmap/execution/atlas/phase_02r_appendix_b_test_and_evaluation_matrix.md`  
**Parent plan:** `docs/roadmap/execution/atlas/phase_02r_execution_plan.md`  
**Purpose:** Detailed verification gates, positive and negative E2E scenarios, relevance-judgment methodology, quality thresholds, and reproducible performance workload.

> This appendix is controlled by the main execution plan. A change that alters scope, architecture, success criteria, rights, thresholds, evidence, or audit requirements is a material plan amendment.

---

## 30. Test and Verification Plan

### 30.1 Test directories to create

```text
tests/unit/phase02r/
tests/integration/phase02r/
tests/security/phase02r/
tests/e2e/phase02r/
tests/fixtures/phase02r/
```

### 30.2 Planned gates

| Gate | Command/review | Environment | Minimum expected result | Failure policy | Evidence |
|---|---|---|---|---|---|
| Compile | `${PYTHON_BIN:-.venv/bin/python} -m compileall -q app scripts tests` | Clean checkout | Exit 0 | Fail closed | E-02R-090 |
| Ruff critical | `${PYTHON_BIN:-.venv/bin/python} -m ruff check app tests scripts --select E9,F63,F7,F82,F821` | Clean checkout | Exit 0 | Fail closed | E-02R-091 |
| Focused unit | `${PYTHON_BIN:-.venv/bin/python} -m pytest -q tests/unit/phase02r` | Local/CI | At least 120 tests; 0 fail; 0 unexpected skip | Fail closed | E-02R-092 |
| PostgreSQL integration | `${PYTHON_BIN:-.venv/bin/python} -m pytest -q tests/integration/phase02r` | Clean PostgreSQL + pgvector | At least 45 tests; 0 fail; 0 unexpected skip | Fail closed | E-02R-093 |
| Security negative | `${PYTHON_BIN:-.venv/bin/python} -m pytest -q tests/security/phase02r` | Isolated | At least 20 negative tests; 0 fail | Fail closed | E-02R-094 |
| API contract | `${PYTHON_BIN:-.venv/bin/python} -m pytest -q tests/unit/phase02r/test_api_* tests/integration/phase02r/test_api_*` | CI | At least 20 route/role/idempotency tests | Fail closed | E-02R-095 |
| Migration graph | `${PYTHON_BIN:-.venv/bin/python} scripts/verify_migration_graph.py` | Clean checkout | One expected head | Fail closed | E-02R-096 |
| Schema integrity | `${PYTHON_BIN:-.venv/bin/python} scripts/validate_schema_integrity.py` | Clean checkout | Exit 0 | Fail closed | E-02R-097 |
| Clean upgrade | `bash scripts/verify_phase02r_postgres.sh --clean-upgrade` | Empty DB | Upgrade to head, all constraints/indexes present | Fail closed | E-02R-098 |
| Upgrade from current head | `bash scripts/verify_phase02r_postgres.sh --upgrade-from-baseline` | Snapshot/fixture DB | Data preserved, classification counts reconcile | Fail closed | E-02R-099 |
| Downgrade/re-upgrade | `bash scripts/verify_phase02r_postgres.sh --roundtrip-safe` | Disposable DB | Only approved reversible range; no data corruption | Fail closed | E-02R-100 |
| Object/checksum | `bash scripts/verify_phase02r.sh --source-integrity` | Staging object store | 100% active source objects match manifest hashes | Fail closed | E-02R-101 |
| Backup restoration | `bash scripts/verify_phase02r.sh --backup-restore` | Isolated restore environment | DB/object restore, hashes, ACLs, and active-corpus reconstruction pass | Fail closed | E-02R-034 |
| Rights eligibility | `bash scripts/verify_phase02r.sh --rights` | Staging | 100% active memberships have approved required uses, translation/publication decisions, and satisfied structured conditions | Fail closed | E-02R-102 |
| Extraction quality | Curriculum review + `bash scripts/verify_phase02r.sh --extraction` | Staging | Sampling and automated thresholds pass | Fail closed | E-02R-103 |
| Mapping coverage | `bash scripts/verify_phase02r.sh --mapping-coverage` | Staging | Five strands, Terms 1–4, objectives trace to Tier 1 | Fail closed | E-02R-104 |
| Corpus reproducibility | `bash scripts/verify_phase02r.sh --corpus-rebuild` | Staging | Rebuild yields identical manifest hash | Fail closed | E-02R-105 |
| Activation concurrency | Integration test | PostgreSQL | One active version; no mixed reads; binding epoch consistent | Fail closed | E-02R-106 |
| Activation outbox/cache safety | Integration/E2E fault injection | PostgreSQL + cache + worker | Delayed, duplicate, failed, retried, and dead-lettered outbox delivery cannot select stale corpus data | Fail closed | E-02R-137 |
| Rollback | Integration/E2E | Staging | Prior eligible corpus restored atomically | Fail closed | E-02R-107 |
| Synthetic guard | `bash scripts/verify_phase02r.sh --synthetic-guard` | Staging/prod config | Zero synthetic memberships/hits | Fail closed | E-02R-108 |
| Grounded generation E2E | `bash scripts/verify_phase02r.sh --generation-e2e` | Staging | Positive and negative flows pass | Fail closed | E-02R-109 |
| Claim validation | Focused tests/evaluation | Staging | Unsupported curriculum claims blocked | Fail closed | E-02R-110 |
| Answer verification | Focused tests/evaluation | Staging | Edit invalidation and deterministic checks pass | Fail closed | E-02R-111 |
| Tutor grounding E2E | `bash scripts/verify_phase02r.sh --tutor-e2e` | Staging | Grounded and fallback flows pass | Fail closed | E-02R-112 |
| Legacy migration | `bash scripts/verify_phase02r.sh --legacy-reconciliation` | Staging | Inventory totals reconcile; no unclassified learner-serving artifact | Fail closed | E-02R-113 |
| Retrieval evaluation | `bash scripts/verify_phase02r.sh --evaluation` | Frozen corpus | 18+ positive; at least 10 negative or one per mandatory exclusion class, whichever is greater; aggregate and subgroup thresholds pass | Fail closed | E-02R-114 |
| Phase 1–7 regression | `bash scripts/verify_phase02r.sh --phase1-7-regression` | CI/PostgreSQL | All required suites pass; no new unexpected skip | Fail closed | E-02R-115 |
| OpenAPI drift | `${PYTHON_BIN:-.venv/bin/python} scripts/generate_openapi.py --check` | Clean checkout | Exit 0 | Fail closed | E-02R-116 |
| Architecture/import boundaries | Existing and new boundary checks | Clean checkout | Exit 0 | Fail closed | E-02R-117 |
| Atlas control set | `bash scripts/verify_phase02r.sh --atlas` | Clean checkout | Plan/report/evidence/audit schema valid | Fail closed | E-02R-118 |
| Full backend/frontend gates | Existing canonical commands | CI | All required gates green | Fail closed | E-02R-119 |
| Phase 0/equivalent baseline | `verify_phase0_or_equivalent_baseline.py` | Clean checkout/CI | Reproducibility controls pass | Fail closed | E-02R-127 |
| `02R` identifier compatibility | `validate_phase_identifier_compatibility.py` | Clean checkout | All canonical forms supported | Fail closed | E-02R-128 |
| Reviewer interface/CLI | UI/CLI contract, auth, audit and accessibility tests | Staging/CI | All decision domains operable and attributable | Fail closed | E-02R-129 |
| Study-plan grounding | Focused + E2E tests | Staging | Unsupported nodes blocked; provenance/staleness pass | Fail closed | E-02R-130 |
| Phase 7 coverage decomposition | Coverage contract tests | Staging | Six coverage measures reported separately | Fail closed | E-02R-131 |
| Phase 6 accounting | Usage reservation/finalisation tests | PostgreSQL/CI | All relevant operations accounted | Fail closed | E-02R-132 |
| Provenance display | API/UI role and redaction tests | Staging/CI | Audience views correct and access-controlled | Fail closed | E-02R-133 |
| Pre-merge candidate audit | Independent reproduction and sampling | Candidate commit/evidence | Candidate report and verdict complete; findings tracked | Fail closed | E-02R-135 |
| Post-merge auditor addendum | Independent merge-state review | Canonical merge commit | Merge-state addendum and final verdict complete | Fail closed | E-02R-136 |
| Combined final audit control | Audit-report validator | Canonical evidence pack | E-02R-123 explicitly references E-02R-135 and E-02R-136 | Fail closed | E-02R-123 |

Minimum test counts are planning indicators, not proof of adequacy. Every mandatory scenario, invariant, negative path, concurrency condition, rights rule, and audit procedure must pass regardless of test quantity. A high test count cannot compensate for missing critical-path coverage.

Test-count changes require a plan amendment or implementation-report explanation; reducing coverage to obtain a pass is prohibited.

### 30.3 End-to-end positive flow

```text
approved inventory source
→ rights decision
→ acquire and verify object
→ extract pages/sections/chunks
→ review extraction
→ map and approve curriculum nodes
→ build/freeze/review corpus
→ atomic activation
→ retrieve
→ generate lesson/item
→ validate claims/calculations/answer
→ Phase 3 content review
→ publish
→ tutor retrieves grounded content
→ source change marks affected artifacts for review
```

### 30.4 Mandatory negative flows

```text
unapproved storage right → acquisition blocked
unapproved extraction right → extraction blocked
unapproved prompt right → generation blocked
unapproved learner excerpt right → excerpt hidden
superseded source → retrieval blocked
withdrawn source → retrieval and rollback blocked
no Tier 1 objective support → generation blocked
unapproved mapping → corpus build blocked
low-confidence unreviewed extraction → corpus build blocked
synthetic fixture → production corpus activation blocked
unsupported claim → artifact quarantined
mathematical mismatch → answer verification fails
educator quorum without answer verification → publication blocked
no tutor grounding → explicit non-authoritative fallback
source checksum mismatch → quarantine and incident alert
```

---

## 31. Real-Corpus Evaluation Plan

### 31.1 Dataset construction order

```text
ingest approved sources
→ review extraction
→ approve mappings
→ freeze corpus
→ activate in evaluation environment
→ select real chunk IDs
→ author natural learner queries
→ multilingual review
→ dataset approval
→ immutable dataset hash
→ evaluation
```

### 31.2 Required cases

- at least one positive case for every strand-language combination: `5 strands × 3 languages = 15` mandatory combinations;
- at least 18 positive cases overall, with additional ambiguity, spelling-variation, and cross-lingual cases;
- at least 10 negative cases **or one per mandatory exclusion class, whichever is greater**;
- Terms 1–4;
- natural learner wording and spelling variation;
- ambiguous query;
- wrong grade;
- wrong subject;
- blocked rights;
- expired rights;
- superseded source;
- withdrawn source;
- wrong authoritative version;
- wrong language;
- unpublished generated content;
- low-quality or unreviewed extraction;
- synthetic fixture;
- activation-key mismatch;
- cross-lingual fallback cases.

Every case must carry subgroup labels for language, strand, term, authority/translation state, and retrieval mode (`same_language` or `cross_lingual`).

### 31.3 Relevance judgments and pooling

Each positive query must include curriculum-reviewed graded relevance judgments rather than a single expected chunk ID:

```json
{
  "query_id": "…",
  "relevance_judgments": {
    "chunk-version-id-a": 3,
    "chunk-version-id-b": 2,
    "chunk-version-id-c": 1
  },
  "judgment_completeness": "pooled",
  "pool_depth": 10,
  "reviewers": ["…"],
  "approved_at": "…"
}
```

Grades mean:

```text
3 = directly authoritative and sufficient
2 = highly relevant supporting passage
1 = partially relevant/contextual
0 = not relevant
```

The evaluation owner must document:

- whether judgments are exhaustive or pooled;
- how candidate pools were created;
- how multiple valid passages were handled;
- disagreement resolution;
- curriculum reviewer approval;
- dataset and judgment hashes.

Where a query has only one canonical relevant target, report Hit Rate@5 and Recall@5. Precision@5 and nDCG@5 are used only where the approved relevance pool supports them.

### 31.4 Metrics

```text
Recall@K
MRR
Precision@K
nDCG
unsafe_hit_count
blocked_rights_hit_count
withdrawn_hit_count
superseded_hit_count
wrong_version_hit_count
wrong_language_hit_count
synthetic_hit_count
fallback_rate
p50/p95 latency
grounding_sufficiency_rate
unsupported_claim_rate
answer_verification_failure_rate
```

All retrieval and integrity metrics must also be reported by:

```text
language
strand
term
authority_or_translation_state
same_language_vs_cross_lingual
```

No subgroup may contain a blocked-rights, withdrawn, superseded, wrong-version, synthetic, unreviewed, activation-key-mismatch, or silent wrong-language-authority hit. Report sample sizes and confidence limitations for every subgroup.

### 31.5 Pre-approved minimum closure thresholds

These thresholds are frozen by plan approval and must not be lowered after viewing evaluation results without a material plan amendment, renewed approval, and complete re-run.

#### Retrieval quality

```text
Recall@5                       >= 0.90
Mean Reciprocal Rank           >= 0.75
Precision@5                    >= 0.60
nDCG@5                         >= 0.80
Positive-case fallback rate    <= 0.05
p95 retrieval latency          <= 1.50 seconds on the documented staging profile
```

Subgroup quality floors:

```text
Recall@5 by delivery language   >= 0.85
Recall@5 by strand              >= 0.80
```

Terms and authority/translation/retrieval-mode subgroups must be reported even where sample sizes are too small for a standalone pass/fail threshold; any material weakness requires a documented corrective action before closure.

The latency profile must document hardware, database size, index size, network topology, warm/cold-cache policy, and concurrency.


Latency is measured with a separate reproducible performance workload, not the small curriculum-quality dataset:

```text
minimum measured queries: 500
warm-up requests: documented and excluded
concurrency levels: 1, 5, and 10
cold-cache and warm-cache runs: separate
timeouts, errors, and fallbacks: included
query distribution and activation keys: documented
```

The performance dataset, environment, harness version, and raw samples must be hashed and retained.

#### Grounding and validation

```text
Grounding sufficiency rate on supported positive cases                 >= 0.95
Observed unsupported mandatory curriculum claims reaching publication    = 0
Observed answer-verification false-positive publications                  = 0
Observed silent wrong-language authority claims                           = 0
```

#### Zero-tolerance corpus and retrieval integrity

- zero blocked-rights hits;
- zero withdrawn hits;
- zero superseded hits;
- zero wrong-version authoritative hits;
- zero synthetic production hits;
- zero unreviewed mapping or extraction hits;
- zero corpus-manifest mismatches;
- zero retrieval hits outside the resolved activation key;
- zero learner-facing restricted excerpts beyond approved rights.

A quality threshold may be made stricter without weakening the plan. Any proposed relaxation requires a material amendment approved before the replacement dataset run.

Each zero-observed result must report the evaluated sample size, scenario classes, adversarial coverage, and confidence limitations. Operational policy remains zero tolerance even though finite evaluation cannot establish a true population error rate of zero.

---

