---
title: Phase 7 Execution Plan — Curriculum Coverage Expansion, Multilingual Quality, and Training Dataset Governance
status: active-control
owner: roadmap-governance
reviewers: [roadmap-governance, release-management, documentation-governance]
audience: roadmap-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 30
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/roadmap, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Phase 7 Execution Plan — Curriculum Coverage Expansion, Multilingual Quality, and Training Dataset Governance

**Document version:** 1.0  
**Date:** 2026-06-15  
**Status:** Draft — approval required before execution  
**Phase:** 07  
**Branch:** `feature/atlas-phase-07-curriculum-expansion-and-training-governance`  
**Base branch:** `master`  
**Base commit:** TBD at start gate  
**Phase owner:** TBD  
**Engineering approver:** TBD  
**Curriculum/content owner:** TBD  
**Language-quality reviewer:** TBD  
**Privacy/safeguarding reviewer:** TBD  
**Evidence custodian:** TBD  
**Independent auditor:** TBD  
**Canonical plan path:** `docs/roadmap/execution/atlas/phase_07_execution_plan.md`  
**Evidence path:** `docs/release-evidence/atlas/phase-07/`

`PHASE_07_START_APPROVED=true`

> No approved and committed execution plan, no Phase 7 implementation. No complete implementation report, evidence pack, independent audit, canonical merge, and post-merge verification, no Phase 7 completion.

---

## 1. Objective

Expand EduBoost curriculum coverage through a deterministic, governed planning and evidence process, while creating a privacy-safe, source-grounded training dataset pipeline that exports only eligible, published, educator-reviewed content.

Phase 7 must not turn curriculum gaps into automatic learner-facing publication. Generation remains subject to Phase 1 source grounding, Phase 2 retrieval controls, Phase 3 educator consensus, Phase 4 item-quality controls, Phase 5 learner-safety controls, and Phase 6 durable AI budget authority.

## 2. Measurable outcomes

Phase 7 succeeds only when:

1. Coverage targets and active scopes are available from a clean checkout through a deterministic registry preflight.
2. Coverage snapshots are attributable to a commit, scope, language, targets, and approved/published artifact counts.
3. Expansion plans are deterministic and identify gaps without bypassing generation, review, publication, or budget gates.
4. Training exports contain only published or explicitly policy-eligible artifacts with source provenance and allowed licences.
5. Rejected, quarantined, superseded, pending-review, unsafe, low-quality, or ungrounded artifacts are excluded.
6. Training records contain no learner, guardian, reviewer, or free-text operational data.
7. Dataset manifests and entries are immutable after approval and have reproducible SHA-256 identities.
8. Multilingual content receives language-specific validation and cannot be claimed complete without qualified human review.
9. Adapter training is gated by an approved dataset manifest and remains a separate controlled operation; CI performs dry-run validation only.
10. Phase 1–6 regressions remain green and the full Atlas control set is complete.

## 3. Preconditions

- [ ] Phase 6 is `Verified Complete` in `docs/roadmap/PHASE_STATUS_REGISTER.md`.
- [ ] Phase 6 execution plan, implementation report, evidence index, audit report, and raw evidence exist under Atlas paths.
- [ ] Any legacy Phase 6 control files are migrated to the Atlas hierarchy and register links are corrected.
- [ ] Clean canonical checkout and base SHA are recorded.
- [ ] Current migration head is `20260615_1500_p6_ai_ops`.
- [ ] Phase 1–6 fast verifiers pass.
- [ ] PostgreSQL/pgvector Docker verification is available.
- [ ] Python selected through `PYTHON_BIN`, `.venv/bin/python`, or `python3` is Python 3.11 or newer.
- [ ] Curriculum owner approves active launch scopes and coverage targets.
- [ ] Language reviewers and supported beta languages are named.
- [ ] Training-data eligibility, licensing, quality, and publication policy is approved.
- [ ] Auditor scope and independence are accepted.

## 4. In scope

- Deterministic Content Factory registry preflight and bootstrap guidance.
- Durable curriculum coverage snapshots.
- Gap planning by scope, CAPS reference, content layer, and language.
- Protected administrative coverage and training-governance APIs.
- Training dataset manifests and immutable manifest entries.
- Eligible artifact selection from Phase 3-published content.
- Source-provenance and licence enforcement.
- Quality, CAPS-alignment, safety, answer-key, and publication eligibility gates.
- Privacy-safe deterministic JSONL export.
- Dataset SHA-256 and per-record SHA-256 identity.
- Multilingual static validation and human-review requirement.
- Training-readiness verification and LoRA/QLoRA dry-run handoff.
- Scheduled weekly coverage snapshots.
- Prometheus metrics and operations runbook.
- Alembic migration, PostgreSQL tests, regressions, evidence, and audit.

## 5. Out of scope

- Automatically publishing newly generated content.
- Treating machine translation as educator-reviewed translation.
- Training a production model in CI.
- Deploying a fine-tuned adapter to learner traffic.
- Expanding beyond approved scopes without change control.
- Using learner conversations, diagnostic responses, parent data, review comments, or audit records as training data.
- Weakening Phase 1–6 controls to increase dataset volume.
- Phase 8 technical-debt remediation.
- Phase 9 CI authority and release governance.

## 6. Architecture decision

Coverage, generation planning, review, publication, dataset export, model training, and deployment are distinct gates:

```text
registry and targets
  → coverage snapshot
  → deterministic gap plan
  → governed generation
  → Phase 3 review quorum
  → publication
  → Phase 7 eligibility filter
  → immutable dataset manifest
  → approved export
  → controlled adapter training
  → independent evaluation
  → separate deployment decision
```

PostgreSQL is the authority for snapshots and dataset manifests. Exported JSONL is a derived, checksummed artifact and must be reproducible from the approved manifest.

## 7. Data model

### `curriculum_coverage_snapshots`

Stores:

- scope and language;
- capture time and source commit SHA;
- approved/published and target totals;
- gap count and status;
- deterministic coverage payload.

### `curriculum_expansion_runs`

Stores:

- requested scopes/languages/layers;
- dry-run status;
- deterministic plan payload;
- requesting actor and timestamps;
- no automatic publication or training action.

### `training_dataset_manifests`

Stores:

- unique dataset version;
- policy/rubric versions;
- status (`draft`, `ready`, `approved`, `rejected`, `superseded`);
- artifact, language, and scope counts;
- export path and dataset SHA-256;
- creator/approver attribution;
- timestamps.

### `training_dataset_entries`

Stores:

- manifest and source artifact identity;
- artifact/content/source hashes;
- artifact version;
- scope, CAPS reference, language, and content layer;
- quality and CAPS-alignment scores;
- deterministic record SHA-256.

Entries are append-only. An approved manifest is immutable.

## 8. Eligibility policy

An artifact is eligible only when all required conditions are true:

- current non-superseded version;
- `published`, unless an explicitly approved policy permits `approved`;
- Phase 3 quorum and publication gate satisfied;
- not rejected, quarantined, revision-required, retired, or superseded;
- safety status is approved;
- quality score meets the configured threshold;
- CAPS-alignment score meets the configured threshold;
- source snapshot and artifact hash exist;
- every required source has an allowed licence;
- diagnostic answer key is independently verified where applicable;
- content contains no forbidden operational or personal-data fields;
- requested language matches the artifact and passes language validation;
- no learner/user-generated content is included.

Volume thresholds never override eligibility.

## 9. Multilingual quality policy

Machine checks may detect obvious language mismatch, mixed-script anomalies, missing locale metadata, and forbidden placeholders. They do not constitute educational or linguistic approval.

Every language included in the release manifest requires:

- a named qualified reviewer;
- sampling methodology;
- minimum review size;
- recorded findings and corrections;
- explicit sign-off;
- no unresolved Critical/High language-quality finding.

## 10. Work breakdown

| ID | Work item | Acceptance criterion |
|---|---|---|
| P7-001 | Approve plan and baseline | Plan committed before code; Phase 6 Atlas boundary verified |
| P7-010 | Add curriculum/training models and migration | Empty DB and Phase 6-head upgrades pass |
| P7-011 | Add immutability triggers and constraints | Entry mutation and approved-manifest mutation fail |
| P7-020 | Add registry preflight and coverage authority | Clean checkout has deterministic registry behavior |
| P7-021 | Implement snapshot and gap-plan service | Plans are deterministic and never publish |
| P7-022 | Implement training eligibility service | Ineligible statuses, licences, safety, quality, and PII are excluded |
| P7-023 | Implement reproducible export | Record and dataset SHA-256 values reproduce exactly |
| P7-024 | Implement multilingual validation | Static findings and human-review requirements are represented |
| P7-025 | Implement training-readiness handoff | Only approved manifests can enter training dry-run |
| P7-030 | Add protected admin API | Coverage, plans, manifests, approval, and export are admin-only |
| P7-031 | Add weekly snapshot job | Job registered, scheduled, idempotent, and non-publishing |
| P7-032 | Add metrics, ADR, and runbook | Operations visibility and response procedures exist |
| P7-040 | Add unit and registration tests | Zero failures, unexpected skips, or warnings |
| P7-041 | Add PostgreSQL tests | Constraints, triggers, eligibility, and migration paths pass |
| P7-042 | Run Phase 1–6 regressions | No prior-phase regression |
| P7-050 | Complete report/evidence/audit | Atlas control set complete and attributable |
| P7-051 | Merge and post-merge verify | Master CI and local gates green on merge SHA |

## 11. Verification gates

### Fast gate

```bash
bash scripts/verify_phase7.sh
```

Must include:

- Python compilation;
- release-blocking Ruff checks;
- Phase 7 unit and registration tests;
- route and ARQ inventory;
- registry preflight;
- deterministic export and PII-field tests;
- training-script dry run with an approved synthetic manifest;
- migration graph and schema integrity;
- OpenAPI drift check;
- Phase 1–6 fast regressions;
- Atlas path validation.

### PostgreSQL gate

```bash
bash scripts/verify_phase7_postgres.sh
```

Must include:

- clean upgrade to Phase 7 head;
- upgrade from Phase 6 head;
- snapshot and manifest constraints;
- manifest/entry immutability triggers;
- published-only eligibility;
- excluded status, licence, safety, quality, and missing-provenance cases;
- deterministic export identity;
- downgrade to Phase 6 and re-upgrade;
- Phase 1–7 PostgreSQL regressions;
- zero database-gated skips.

### Expected migration head

```text
20260615_1800_p7_curriculum
```

## 12. Evidence requirements

Create:

```text
docs/roadmap/execution/atlas/phase_07_implementation_report.md
docs/release-evidence/atlas/phase-07/phase_07_evidence_index.md
docs/release-evidence/atlas/phase-07/phase_07_audit_report.md
docs/release-evidence/atlas/phase-07/raw/
```

Raw evidence must include:

- exact Python and package-tool versions;
- branch, base SHA, candidate SHA, and merge SHA when available;
- fast and PostgreSQL verifier output;
- migration graph and schema integrity;
- registry preflight;
- route and ARQ inventory;
- OpenAPI check;
- coverage snapshot sample;
- eligibility and excluded-artifact sample;
- deterministic dataset hash reproduction;
- multilingual review/sign-off references;
- training dry-run output;
- test counts, warnings, skips, retries, and exit codes;
- SHA-256 manifest.

The collector must not mark the audit Pass or the phase complete.

## 13. Security, privacy, and safeguarding rules

- Admin identity comes from canonical authenticated context.
- No actor identity is accepted from payloads.
- Training export excludes learner, guardian, educator-review-comment, tutor-message, diagnostic-response, consent, billing, and audit data.
- Export paths are constrained to an approved artifact directory.
- Dataset versions and paths reject traversal and unsafe characters.
- Free-text artifact content is scanned for forbidden operational fields and obvious PII patterns before export.
- Dataset entries store hashes and provenance, not private operational text.
- Licensing status must be explicitly allowed.
- Unknown API fields are rejected.
- Training does not imply deployment.
- A model adapter cannot be marked deployable without a separate evaluation and release decision.

## 14. Rollback and recovery

Rollback triggers:

- unpublished or quarantined content exported;
- personal data in a dataset;
- disallowed source licence;
- non-reproducible dataset hash;
- mutable approved manifest or entries;
- registry unavailable from clean checkout;
- multilingual completion claimed without qualified review;
- migration corruption;
- Phase 1–6 regression.

Recovery:

1. Revoke affected dataset manifests and block training/deployment.
2. Preserve manifests, hashes, and audit evidence.
3. Remove derived export files from active artifact storage.
4. Roll back application code.
5. Prefer forward-fix migrations when downgrade risks evidence loss.
6. Rebuild from the approved manifest after remediation.
7. Re-run all Phase 1–7 gates.

## 15. Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Dataset volume pressure weakens eligibility | High | Fail-closed policy and tests |
| Learner or reviewer data enters training | Critical | Explicit source tables, forbidden keys, PII scan |
| Unpublished content exported | Critical | Published-only query and PostgreSQL tests |
| Licence incompatibility | High | Allowed-licence filter and evidence |
| Translation quality overstated | High | Human reviewer/sign-off requirement |
| Training output mistaken for deployment approval | High | Separate statuses, ADR, and runbook |
| Registry files missing from clean checkout | High | Preflight and deterministic bootstrap contract |
| Dataset cannot be reproduced | High | Manifest entries and SHA-256 verification |
| Approved evidence mutated | High | Database triggers |
| Expansion creates runaway AI spend | High | Dry-run default and Phase 6 budget authority |

## 16. Start gate

- [ ] Plan is reviewed, approved, and committed.
- [ ] Phase 6 is `Verified Complete`.
- [ ] Phase 6 Atlas control files and raw evidence exist.
- [ ] Phase 6 register links point to Atlas paths.
- [ ] Base SHA and clean worktree are recorded.
- [ ] Migration head is `20260615_1500_p6_ai_ops`.
- [ ] Phase 1–6 fast gates pass.
- [ ] Curriculum scopes and targets are approved.
- [ ] Training eligibility and licence policies are approved.
- [ ] Supported languages and qualified reviewers are named.
- [ ] Privacy and safeguarding review is complete.
- [ ] Auditor scope is accepted.

### Start approval

| Role | Name | Decision | Date | Reference |
|---|---|---|---|---|
| Phase owner | | ☐ Approve / ☐ Reject | | |
| Engineering approver | | ☐ Approve / ☐ Reject | | |
| Curriculum/content owner | | ☐ Approve / ☐ Reject | | |
| Language-quality reviewer | | ☐ Approve / ☐ Reject | | |
| Privacy/safeguarding reviewer | | ☐ Approve / ☐ Reject | | |
| Evidence custodian | | ☐ Ready / ☐ Not ready | | |
| Independent auditor | | ☐ Scope accepted / ☐ Changes required | | |

## 17. Completion gate

- [ ] All mandatory work items and roadmap outcomes pass.
- [ ] Registry preflight passes from a clean checkout.
- [ ] Coverage snapshots and gap plans are deterministic.
- [ ] No ineligible artifact is exported.
- [ ] Dataset and per-record hashes reproduce.
- [ ] Approved manifests and entries are immutable.
- [ ] Multilingual sign-offs are complete for claimed languages.
- [ ] Training dry run accepts only an approved manifest.
- [ ] Phase 1–6 regressions are green.
- [ ] Empty-DB and Phase 6-head migration paths pass.
- [ ] PostgreSQL verification has zero unexpected skips.
- [ ] OpenAPI and architecture checks pass.
- [ ] Implementation report and evidence pack are complete.
- [ ] Independent audit issues Pass or Pass with non-blocking observations.
- [ ] No Critical or High finding remains.
- [ ] Feature branch is merged to `master`.
- [ ] Post-merge CI passes on the merge commit.
- [ ] Final evidence references the merge SHA.
- [ ] Phase register is updated last.

### Closure approval

| Role | Name | Decision | Date | Reference |
|---|---|---|---|---|
| Phase owner | | ☐ Recommend close / ☐ Keep open | | |
| Engineering approver | | ☐ Approve / ☐ Reject | | |
| Curriculum/content owner | | ☐ Approve / ☐ Reject | | |
| Language-quality reviewer | | ☐ Approve / ☐ Reject | | |
| Privacy/safeguarding reviewer | | ☐ Approve / ☐ Reject | | |
| Independent auditor | | ☐ Pass / ☐ Pass with observations / ☐ Fail | | |
| Release manager | | ☐ Merge/CI verified / ☐ Not verified | | |
| Final approver | | ☐ Verified Complete / ☐ Not complete | | |
