# Phase 2R Appendix D — Independent Audit and Sampling Plan

**Document version:** 1.4  
**Plan date:** 2026-06-16  
**Status:** Draft — approval required with the main Phase 2R execution plan  
**Canonical path:** `docs/roadmap/execution/atlas/phase_02r_appendix_d_audit_sampling.md`  
**Parent plan:** `docs/roadmap/execution/atlas/phase_02r_execution_plan.md`  
**Purpose:** Auditor competence, independence, sampling floors, mandatory reproduction procedures, and verdict rules.

> This appendix is controlled by the main execution plan. A change that alters scope, architecture, success criteria, rights, thresholds, evidence, or audit requirements is a material plan amendment.

---

## 34. Phase Audit Plan

### 34.1 Auditor competence and independence

The technical auditor must understand PostgreSQL/Alembic, retrieval systems, immutable provenance, API/security controls, test/evidence integrity, and AI grounding limitations.

Curriculum and rights determinations require separate competent reviewers. One person may perform multiple roles only with an explicit conflict declaration and compensating independent reproduction.

### 34.2 Sampling requirements

| Audit area | Minimum sample/coverage | Independent procedure |
|---|---|---|
| Plan timing and source state | 100% | Verify plan approval commit predates substantive implementation; inspect Git history and clean source state |
| Source inventory | 100% of required rows | Reconcile completeness register to active corpus sources |
| Authority and rights | 100% of active source versions | Inspect authority evidence, every required per-use decision, translation/publication permission where used, and machine evaluation of structured conditions |
| Original objects/checksums | 100% of active source files | Independently hash/download or verify immutable object versions |
| Extraction | At least 10 pages or 10% per source version, whichever is greater; include all low-confidence pages in active chunks and representative tables/formulas | Compare rendered source pages with stored page/section/chunk text and warnings |
| Mapping | 100% of Tier 1 strand/topic/objective nodes; at least 20% of chunk mappings per strand, minimum 10 | Trace nodes to source sections and reviewer rationale |
| Corpus manifest | 100% membership/hash verification | Rebuild manifest and compare SHA-256; inspect ineligible exclusion |
| Activation/rollback/outbox | 100% critical scenarios | Reproduce concurrency, database-atomic switch, delayed/duplicate/failed outbox delivery, stale-cache rejection, rollback, and blocked prior version |
| Retrieval evaluation | 100% of approved cases | Independently run dataset and inspect prohibited-hit counts |
| Grounded generation | Minimum 18 artifacts across five strands and three languages, including lesson and assessment outputs | Inspect provenance, claims, source support, overlap, validation and publication state |
| Answer verification | 100% of assessment artifacts in the audit generation sample, minimum 12 | Recalculate or reproduce checker; edit one artifact and confirm invalidation |
| Tutor | Minimum 3 grounded and 2 negative/fallback cases per language | Inspect retrieved chunks, corpus version, output claims and fallback wording |
| Legacy migration | 100% aggregate reconciliation plus targeted sample of every classification | Reconcile counts and verify learner-serving exclusions |
| Security | All mandatory negative scenarios | Reproduce blocked URL/file/rights/source/prompt-injection cases |
| Evidence | 100% index entries and hashes | Validate `SHA256SUMS.txt`, source commit, command outputs, failures/warnings |
| Merge/CI | 100% | Verify canonical merge SHA and post-merge required CI |

### 34.3 Mandatory audit procedures

The auditor must independently:

- verify plan approval timing and start flag history;
- inspect source scope and completeness;
- sample/reproduce acquisition and checksum verification;
- inspect all active rights decisions and reproduce structured-condition evaluation for at least one allowed and one denied/expired case per condition class in use;
- compare source pages to extracted pages/chunks;
- inspect curriculum mapping decisions;
- query active, superseded, withdrawn, and blocked versions;
- test that a blocked/superseded source cannot be retrieved;
- reproduce a corpus build and manifest hash;
- reproduce activation and rollback;
- generate grounded lessons/items and inspect stored provenance;
- inject unsupported curriculum claims and verify rejection;
- verify copying controls;
- independently recalculate assessment answers;
- prove educator quorum does not set verification;
- test tutor grounding and safe fallback;
- inspect legacy classification and serving exclusions;
- verify metrics/runbooks for source withdrawal and grounding failure;
- validate evidence hashes, merge SHA, and post-merge CI.

### 34.4 Two-stage audit evidence identities

The audit lifecycle produces two independently identifiable records:

1. **E-02R-135 — pre-merge candidate audit:** candidate source state, sampled evidence, independently reproduced commands, findings, remediation requirements, and candidate verdict. It is never the final canonical-source verdict.
2. **E-02R-136 — post-merge auditor addendum/final merge-state verdict:** canonical merge SHA, post-merge evidence and CI, confirmation that remediation survived merge, and the final verdict.

**E-02R-123** is the final combined audit control that explicitly references and binds E-02R-135 and E-02R-136. Missing either stage blocks closure.


### 34.5 Verdicts

```text
Pass
Pass with non-blocking observations
Fail
```

Any unresolved Critical or High finding requires `Fail`.

---

