# Phase 2R Appendix C — Evidence Inventory and Integrity Rules

**Document version:** 1.4  
**Plan date:** 2026-06-16  
**Status:** Draft — approval required with the main Phase 2R execution plan  
**Canonical path:** `docs/roadmap/execution/atlas/phase_02r_appendix_c_evidence_inventory.md`  
**Parent plan:** `docs/roadmap/execution/atlas/phase_02r_execution_plan.md`  
**Purpose:** Evidence structure, record schema, start-gate/candidate/post-merge evidence lifecycle, sensitivity, hashes, and revalidation triggers.

> This appendix is controlled by the main execution plan. A change that alters scope, architecture, success criteria, rights, thresholds, evidence, or audit requirements is a material plan amendment.

---

## 32. Evidence-Pack Plan

### 32.1 Evidence structure

```text
docs/release-evidence/atlas/phase-02r/
├── phase_02r_evidence_index.md
├── phase_02r_audit_report.md
└── raw/
    ├── baseline/
    ├── source_inventory/
    ├── rights/
    ├── acquisition/
    ├── extraction/
    ├── mappings/
    ├── corpus/
    ├── generation/
    ├── answer_verification/
    ├── tutor/
    ├── legacy/
    ├── evaluation/
    ├── security/
    ├── regressions/
    ├── merge/
    └── SHA256SUMS.txt
```

### 32.2 Evidence record schema

Every evidence item must include:

```text
evidence_id
claim
artifact_path
source_commit
canonical_branch
worktree_state
environment
command_or_review_method
exit_code
started_at
finished_at
duration
operator/reviewer
tool_versions
test_counts
failures
skips
xfails
warnings
retries
sensitivity
redaction_status
sha256
custodian
revalidation_trigger
status
supersedes_evidence_id
```

### 32.3 Planned evidence inventory

| Evidence ID | Claim | Artifact | Sensitivity | Revalidation trigger |
|---|---|---|---|---|
| E-02R-001 | Canonical remote/branch identity | `raw/baseline/git_identity.txt` | Internal | Branch/remote change |
| E-02R-002 | Clean baseline worktree | `raw/baseline/git_status.txt` | Internal | Any source change |
| E-02R-003 | Plan approved before implementation | Plan approval + Git history | Internal | Plan amendment |
| E-02R-004 | Base and plan commit SHAs | `raw/baseline/source_state.json` | Internal | Rebase/merge |
| E-02R-005 | Actual migration head | `raw/baseline/alembic_heads.txt` | Internal | Migration change |
| E-02R-006 | Phase 1–7 baseline reconciliation | Baseline report | Internal | Regression change |
| E-02R-007 | Audit-remediation boundary accepted | Approval record | Internal | Scope change |
| E-02R-008 | Object storage configured | Redacted config/verification | Restricted | Storage change |
| E-02R-009 | Rights reviewer accepts scope | Approval record | Internal | Reviewer/scope change |
| E-02R-010 | Curriculum reviewer accepts scope | Approval record | Internal | Reviewer/scope change |
| E-02R-011 | Language review capability accepted | Approval record | Internal | Reviewer change |
| E-02R-012 | Auditor independence/scope accepted | Declaration | Internal | Auditor/scope change |
| E-02R-013 | Toolchain/environment recorded | `raw/baseline/tool_versions.txt` | Internal | Toolchain change |
| E-02R-014 | Phase 0/equivalent reproducibility start-gate dependency verified | Baseline report and raw commands | Internal | Toolchain/setup/CI change |
| E-02R-015 | `02R` identifier compatibility start-gate dependency verified | Validator output | Internal | Programme tooling change |
| E-02R-016 | Evaluation thresholds approved before execution | Signed plan/threshold record | Internal | Threshold or dataset-policy change |
| E-02R-017 | Human-review interface/CLI design approved at start gate | Approved design/UX/CLI specification | Internal | Review workflow/design change |
| E-02R-020 | Source-completeness inventory frozen | Signed register + hash | Internal | Inventory amendment |
| E-02R-021 | 100% active sources have authority decision | Catalogue export | Restricted/Internal | Source change |
| E-02R-022 | 100% active versions have per-use rights decisions | Rights register export | Restricted | Rights change/expiry |
| E-02R-023 | Training permission remains separately controlled | Policy/test output | Internal | Rights policy change |
| E-02R-030 | Original objects acquired and hashed | Acquisition manifest | Restricted | Object/source change |
| E-02R-031 | Malware scans pass | Scan reports | Restricted | New object/engine change |
| E-02R-032 | Object immutability verified | Storage verification | Restricted | Storage policy change |
| E-02R-033 | Source refresh/change detection works | Test output | Internal | Detector change |
| E-02R-034 | Database/object-store restoration verified | Restore report, hashes, ACL checks, corpus reconstruction | Restricted/Internal | Backup/storage/schema change |
| E-02R-040 | Extraction runs reproducible | Extraction manifests | Internal | Extractor/config change |
| E-02R-041 | Page provenance preserved | Sample trace report | Internal | Extraction change |
| E-02R-042 | Extraction review passes | Reviewer decisions | Internal | Source/extraction change |
| E-02R-043 | OCR pages separately identified/reviewed | OCR report | Internal | OCR engine/source change |
| E-02R-050 | Curriculum graph covers scope | Coverage export | Internal | Mapping/source change |
| E-02R-051 | Mappings human-approved | Review export | Internal | Mapping change |
| E-02R-052 | Five strands/Terms 1–4 have Tier 1 support | Traceability matrix | Internal | Corpus/source change |
| E-02R-053 | Language/translation status explicit | Language register | Internal | Translation change |
| E-02R-060 | Corpus manifest is deterministic and hashed | Manifest + rebuild output | Internal | Membership/policy change |
| E-02R-061 | Atomic activation passes | PostgreSQL test output | Internal | Activation code/schema change |
| E-02R-062 | Rollback passes | E2E output | Internal | Activation/source change |
| E-02R-063 | Retrieval projection matches manifest | Reconciliation report | Internal | Reindex/corpus change |
| E-02R-064 | No synthetic production chunks | Guard output | Internal | Corpus/build change |
| E-02R-070 | Generation fails without sufficient grounding | Negative test output | Internal | Grounding policy/code change |
| E-02R-071 | Generated artifacts persist full provenance | Sample DB/API trace | Restricted/Internal | Schema/code change |
| E-02R-072 | Unsupported claims block | Evaluation/test output | Internal | Validator/model change |
| E-02R-073 | Copying controls pass | Similarity report | Restricted | Rights/policy/model change |
| E-02R-074 | Answer verification is independent | Verification records/tests | Internal | Checker/content change |
| E-02R-075 | Artifact edits invalidate verification | Test output | Internal | Verification code change |
| E-02R-080 | Tutor uses active corpus | E2E trace | Restricted/Internal | Tutor/corpus change |
| E-02R-081 | Tutor fallback is explicit/non-authoritative | Negative tests | Internal | Tutor policy change |
| E-02R-082 | Tutor provenance persists | Sample records | Restricted/Internal | Schema/code change |
| E-02R-083 | Tutor safety/consent/budget regressions pass | Regression output | Internal | Tutor change |
| E-02R-084 | Study-plan grounding verified on candidate source | Candidate E2E/provenance/staleness report | Internal | Graph/corpus/study-plan change |
| E-02R-085 | Phase 7 coverage decomposition verified on candidate source | Candidate coverage contract/export | Internal | Coverage model change |
| E-02R-086 | Phase 6 accounting verified on candidate source | Candidate usage records and tests | Internal | Provider/job/accounting change |
| E-02R-087 | Reviewer interface/CLI implementation verified on candidate source | Candidate UI/CLI, auth, audit, accessibility output | Internal | Review interface/source change |
| E-02R-088 | Provenance displays verified on candidate source | Candidate API/UI/redaction tests | Restricted/Internal | Provenance/access-policy change |
| E-02R-090 | Compilation passes | Raw output | Internal | Source change |
| E-02R-091 | Critical Ruff passes | Raw output | Internal | Source change |
| E-02R-092 | Focused unit suite passes | Pytest output/JUnit | Internal | Source/test change |
| E-02R-093 | PostgreSQL integration suite passes | Pytest output/JUnit | Internal | Schema/source change |
| E-02R-094 | Security negative suite passes | Pytest output/JUnit | Restricted/Internal | Security/source change |
| E-02R-095 | API contract passes | Raw output | Internal | API/OpenAPI change |
| E-02R-096 | Migration graph valid | Raw output | Internal | Migration change |
| E-02R-097 | Schema integrity valid | Raw output | Internal | Schema change |
| E-02R-098 | Clean DB upgrade passes | Raw output | Internal | Migration change |
| E-02R-099 | Baseline upgrade/migration reconciles | Raw output | Restricted/Internal | Migration/data change |
| E-02R-100 | Safe roundtrip passes | Raw output | Internal | Migration change |
| E-02R-101 | Active source hashes verified | Integrity report | Restricted | Source/object change |
| E-02R-102 | Rights eligibility, translation/publication permissions, and structured conditions verified | Eligibility and policy-evaluation report | Restricted/Internal | Rights/corpus/policy change |
| E-02R-103 | Extraction quality accepted | Automated + reviewer report | Internal | Extraction/source change |
| E-02R-104 | Mapping coverage accepted | Coverage report | Internal | Mapping/source change |
| E-02R-105 | Corpus rebuild deterministic | Raw output | Internal | Policy/membership change |
| E-02R-106 | Activation concurrency passes | Test output | Internal | Activation change |
| E-02R-107 | Rollback passes | Test output | Internal | Activation/source change |
| E-02R-108 | Synthetic guard passes | Guard output | Internal | Corpus change |
| E-02R-109 | Generation E2E passes | E2E output | Restricted/Internal | Generation/corpus change |
| E-02R-110 | Claim validation passes | Evaluation output | Internal | Validator/model/corpus change |
| E-02R-111 | Answer verification passes | Evaluation output | Internal | Checker/content change |
| E-02R-112 | Tutor E2E passes | E2E output | Restricted/Internal | Tutor/corpus change |
| E-02R-113 | Legacy inventory reconciles | Migration report | Internal | Legacy data change |
| E-02R-114 | Real multilingual evaluation passes | Dataset, hash, results | Internal | Corpus/evaluator change |
| E-02R-115 | Phase 1–7 regressions pass | Raw outputs/JUnit | Internal | Source change |
| E-02R-116 | OpenAPI drift absent | Raw output | Internal | API change |
| E-02R-117 | Architecture boundaries pass | Raw output | Internal | Architecture change |
| E-02R-118 | Atlas validator passes | Raw output | Internal | Control-set change |
| E-02R-119 | Full required repository gates pass | CI/local outputs | Internal | Source/toolchain change |
| E-02R-120 | Metrics/alerts/runbooks verified | Operational report | Internal | Operations change |
| E-02R-121 | Implementation report complete | Report + validator | Internal | Plan/work change |
| E-02R-122 | Evidence hashes valid | `raw/SHA256SUMS.txt` + verification | Internal | Evidence change |
| E-02R-123 | Combined final audit control binds candidate audit and merge-state addendum into the final verdict | Final audit report referencing E-02R-135 and E-02R-136 | Internal | Remediation/source/merge change |
| E-02R-124 | Canonical merge commit recorded | Git/PR evidence | Internal | Merge/rebase |
| E-02R-125 | Post-merge CI passes | CI evidence | Internal | Merge/source change |
| E-02R-126 | Closure approval complete | Approval matrix | Internal | Finding/change |
| E-02R-127 | Phase 0/equivalent reproducibility closure-gate verification passes | Baseline report and raw commands | Internal | Toolchain/setup/CI change |
| E-02R-128 | `02R` identifier compatibility closure-gate verification passes | Validator output | Internal | Programme tooling change |
| E-02R-129 | Reviewer interface/CLI post-merge verification passes | Merge-commit UI/CLI, auth, accessibility and audit output | Internal | Merge/review workflow change |
| E-02R-130 | Study-plan grounding post-merge verification passes | Merge-commit E2E/provenance/staleness report | Internal | Merge/graph/corpus/study-plan change |
| E-02R-131 | Phase 7 coverage decomposition post-merge verification passes | Merge-commit coverage contract/export | Internal | Merge/coverage model change |
| E-02R-132 | Phase 6 accounting post-merge verification passes | Merge-commit usage records and tests | Internal | Merge/provider/job/accounting change |
| E-02R-133 | Provenance display post-merge verification passes | Merge-commit API/UI/redaction tests | Restricted/Internal | Merge/provenance/access-policy change |
| E-02R-135 | Pre-merge candidate audit report and verdict complete | Candidate audit report, sampled evidence, reproduced commands, findings | Internal | Candidate source/evidence/remediation change |
| E-02R-136 | Post-merge auditor addendum and final merge-state verdict complete | Auditor addendum, merge SHA, post-merge evidence review, final verdict | Internal | Merge/source/evidence change |
| E-02R-137 | Transactional outbox and stale-cache safety verified | Fault-injection tests, outbox records, cache/binding traces, alerts | Internal | Activation/cache/worker change |

### 32.4 Evidence quality rules

- Feature-branch evidence is provisional and labelled as such.
- Final evidence must reference the canonical merge commit and clean worktree.
- Raw stdout, stderr, command, exit code, timings, versions, counts, skips, xfails, warnings, retries, and collection errors must be retained.
- Every raw evidence file must appear in `SHA256SUMS.txt`.
- The collector must validate hashes and preserve nonzero status.
- Failure runs must produce truthful failure artifacts.
- The evidence collector may not approve reviews, close findings, mark the phase complete, or alter the plan’s approval flag.
- Restricted source text must be minimised/redacted and access-controlled.

---

