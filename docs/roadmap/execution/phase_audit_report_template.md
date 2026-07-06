---
title: Phase <NN> Audit Report — <Phase Title>
status: template
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

# Phase <NN> Audit Report — <Phase Title>

**Audit-report version:** 1.0  
**Phase:** <NN>  
**Status:** Draft | Audit In Progress | Final — Pass | Final — Pass with Non-Blocking Observations | Final — Fail  
**Auditor:** <name/role>  
**Competence/authority:** <description>  
**Independence declaration:** Independent | Partial independence with mitigations | Conflict identified  
**Conflicts and mitigations:** <details>  
**Release manager:** <name/role>  
**Execution plan audited:** <path/version>  
**Implementation report audited:** <path/version>  
**Evidence index audited:** <path/version>  
**Sprint codename:** `<codename>`  
**Canonical merge commit:** <SHA>  
**Environment/artifact identity:** <identity/digest>  
**Audit dates:** <UTC start–end>

> The audit independently assesses whether the phase can be marked Verified Complete. It does not rewrite the acceptance criteria after implementation.

## 1. Audit Objective and Scope

State what was audited, what was excluded, and why the scope is sufficient for the phase risk.

## 2. Audit Criteria

- Governing roadmap phase outcomes and exit criteria.
- Approved execution plan and amendments.
- Implementation report claims.
- Evidence-pack completeness and authenticity.
- Applicable security, privacy, safety, accessibility, content, data, migration, deployment, operations, rollback, and governance requirements.
- Programme closure-integrity rules.

## 3. Method, Sampling, and Limitations

| Area | Method | Sample / coverage | Tools | Limitation |
|---|---|---|---|---|
| Plan timing | Git/history and approval review | 100% | ... | ... |
| Critical gates | Independent reproduction/observation | ... | ... | ... |

Disclose any inability to independently reproduce evidence and the compensating procedure used.

## 4. Independence Assessment

Explain whether the auditor was involved in planning, implementation, evidence collection, or approval. In a single-developer project, document automated reproduction, external review, or release-manager challenge used to mitigate limited independence.

## 5. Control-Set Integrity Review

| Control | Audit question | Result | Evidence / finding |
|---|---|---|---|
| Execution plan | Was it approved before substantive execution? | Pass/Fail | ... |
| Implementation report | Does it accurately reconcile all planned work and deviations? | Pass/Fail | ... |
| Evidence pack | Is every mandatory claim supported by attributable proof? | Pass/Fail | ... |
| Source identity | Do report, evidence, CI, artifact, and environment refer to the same state? | Pass/Fail | ... |

## 6. Exit-Criterion Audit

| Criterion ID | Criterion | Auditor procedure | Evidence sampled | Independent result | Finding ID |
|---|---|---|---|---|---|
| ... | ... | ... | ... | Pass/Fail | ... |

## 7. Independent Reproduction / Observation Results

Record exact commands, tool versions, environment, expected counts, actual pass/fail/skip/xfail/warning totals, exit codes, and raw audit evidence IDs.

## 8. Failures, Warnings, Skips, Exceptions, and Deferred Work

Assess whether each disclosed item is genuinely non-blocking and correctly classified. Identify omissions or understatement.

## 9. Risk and Domain-Control Assessment

Assess applicable security, privacy, safeguarding, accessibility, content quality, data integrity, migrations, deployment, observability, operational support, rollback, and external-governance controls.

## 10. Findings

| Finding ID | Severity | Description | Criterion/control | Required action | Owner | Due date | Re-audit required |
|---|---|---|---|---|---|---|---|
| A-<NN>-001 | Critical/High/Medium/Low/Observation | ... | ... | ... | ... | ... | Yes/No |

Severity policy:

- **Critical:** immediate safety, privacy, security, data-loss, or release-integrity failure.
- **High:** mandatory criterion failed or material evidence/report contradiction.
- **Medium:** significant weakness not presently defeating the phase outcome.
- **Low:** minor control weakness.
- **Observation:** improvement with no material phase impact.

Critical or High findings require a `Fail` verdict.

## 11. Corrective Actions and Re-Audit

| Finding ID | Corrective action evidence | Auditor retest | Result | Closed date |
|---|---|---|---|---|
| ... | ... | ... | Pass/Fail | ... |

## 12. Audit Conclusion

### Verdict

`Pass` | `Pass with non-blocking observations` | `Fail`

### Basis

Explain the verdict and explicitly state whether the phase may enter Closure Review.

A passing verdict requires:

- all mandatory criteria pass;
- no Critical or High finding remains;
- evidence is complete and attributable;
- source/artifact/environment identity is consistent;
- deviations were approved before closure;
- residual risks are within policy.

## 13. Sign-Off

| Role | Name | Decision | Date | Signature / immutable reference |
|---|---|---|---|---|
| Phase Auditor | | Pass / Pass with observations / Fail | | |
| Phase Approver | | Accept / Reject audit | | |
| Release Manager | | Admit to closure review / Return for remediation | | |
