---
title: Phase <NN> Implementation Report — <Phase Title>
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

# Phase <NN> Implementation Report — <Phase Title>

**Document version:** 1.0  
**Date:** YYYY-MM-DD  
**Status:** Draft | Verification Pending | Evidence Complete | Audit Review | Closure Review | Approved — Verified Complete | Rejected  
**Phase:** <NN>  
**Phase owner:** <name/role>  
**Phase approver:** <name/role>  
**Release manager:** <name/role>  
**Evidence custodian:** <name/role>  
**Phase auditor:** <name/role>  
**Sprint codename:** `<codename>`  
**Execution plan:** `docs/roadmap/execution/<codename>/phase_<NN>_execution_plan.md`, version <x>  
**Evidence index:** `docs/release-evidence/<codename>/phase-<NN>/phase_<NN>_evidence_index.md`, version <x>  
**Audit report:** `docs/release-evidence/<codename>/phase-<NN>/phase_<NN>_audit_report.md`, version <x or Pending>  
**Branch:** `<phase branch>`  
**Base commit:** `<SHA>`  
**Merge commit:** `<SHA — required before closure>`  
**Evidence frozen at:** <UTC>  
**Evidence environment:** <environment>

> This report is one part of the mandatory four-artefact closure set. It cannot by itself mark the phase complete.

## 1. Objective and Approved Scope

Restate the approved objective and scope. Link every approved plan amendment.

## 2. Executive Delivery Summary

Summarise what was delivered, what changed, what was not delivered, and whether the phase outcome was achieved without redefining success.

## 3. Plan-to-Actual Traceability

| Plan ID / roadmap criterion | Planned result | Actual result | Evidence ID | Audit procedure/result | Status |
|---|---|---|---|---|---|
| ... | ... | ... | E-<NN>-... | Pending / result | Passed / Failed / Approved Scope Change / N/A |

Every execution-plan item, amendment, roadmap exit criterion, evidence item, and audit procedure must be reconciled.

## 4. Delivered Changes and Artefacts

| File / artefact / service | Change | Purpose | Review reference |
|---|---|---|---|
| ... | ... | ... | ... |

## 5. Deviations and Approved Amendments

| Amendment | Plan version | Reason | Impact | Approval | Actual result |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

Unapproved deviations prevent closure.

## 6. Verification Results

Record exact commands, tool versions, source state, environment, expected test count, actual pass/fail/skip/xfail counts, warnings, collection errors, retries, duration, exit code, and immutable raw output.

| Gate | Command / review | Expected | Actual | Result | Evidence ID |
|---|---|---|---|---|---|
| ... | ... | ... | ... | Pass / Fail | E-<NN>-... |

Scripts, workflows, or test files that merely exist are not evidence unless executed successfully.

## 7. Security, Privacy, Safety, Accessibility, Content, and Data Results

Document controls tested, findings, approvals, data handling, learner impact, and residual risk.

## 8. Migration, Deployment, Rollback, and Recovery Results

Record migrations applied, compatibility checks, deployment identity, backups, rollback/forward-fix rehearsal, recovery verification, timing, and failures.

## 9. Observability and Operational Readiness

Record telemetry, alerts, dashboards, runbooks, support readiness, privacy-safe logging, live validation, and ownership.

## 10. Planned vs Actual Effort and Schedule

| Measure | Planned | Actual | Variance | Explanation |
|---|---:|---:|---:|---|
| Engineering hours | | | | |
| Calendar duration | | | | |

## 11. Defects, Residual Risks, Exceptions, and Deferred Work

| ID | Item | Severity | Phase/release blocking | Decision | Owner | Target | Approval / evidence |
|---|---|---|---|---|---|---|---|
| ... | ... | ... | Yes/No | ... | ... | ... | ... |

Mandatory criteria may not be deferred at closure. Any scope change must have been approved before the affected work was accepted.

## 12. Evidence-Pack Reconciliation

- Evidence index version: ...
- Evidence freeze timestamp: ...
- Evidence source commit/environment: ...
- Evidence completeness declaration: Signed / Pending
- Missing or contextual evidence: ...
- Sensitive evidence controls and retention: ...

| Evidence ID | Claim / criterion | File or immutable link | Hash | Result | Revalidation trigger |
|---|---|---|---|---|---|
| E-<NN>-001 | ... | ... | ... | Pass/Fail | ... |

## 13. Audit Readiness and Findings Reconciliation

Before audit begins, confirm:

- [ ] Plan and all amendments are final.
- [ ] Every mandatory criterion has evidence.
- [ ] Evidence pack is frozen and signed by the custodian.
- [ ] Canonical merge commit and post-merge CI are available.
- [ ] Known failures, warnings, skips, exceptions, and limitations are disclosed.
- [ ] Auditor has read access to required evidence and no undisclosed conflict.

After audit, reconcile all findings:

| Finding ID | Severity | Finding | Corrective action | Evidence | Status | Re-audit result |
|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | Open/Closed | ... |

## 14. Source-State and Merge Verification

- Canonical branch: `<branch>`
- Merge commit: `<SHA>`
- Worktree/evidence source state: clean / explain
- Post-merge required CI run: `<immutable link>`
- Built artefact/image digest where applicable: `<digest>`
- Environment identity where applicable: `<identity>`

## 15. Definition-of-Done Reconciliation

- [ ] Execution plan was approved before substantive execution.
- [ ] Every plan item and amendment is reconciled.
- [ ] Every mandatory acceptance criterion passes.
- [ ] No mandatory work remains pending, failed, unverified, or deferred.
- [ ] Work is merged into the canonical branch.
- [ ] Post-merge CI passes on the merge commit.
- [ ] Evidence refers to the merge commit and intended environment/artefact.
- [ ] Evidence index maps every criterion and is signed by the Evidence Custodian.
- [ ] Required live, external, migration, rollback, and operational verification is complete.
- [ ] Warnings, skips, collection failures, retries, and known defects are disclosed and assessed.
- [ ] Residual risks and permitted exceptions are approved and within policy.
- [ ] Phase audit report exists and has a passing verdict.
- [ ] Every blocking audit finding is closed and re-audited where required.
- [ ] Downstream plans, risks, estimates, and documentation are updated.

## 16. Closure Recommendation

**Recommended status:** Audit Pending | Verified Complete | Remain In Progress | Blocked | Rejected

Explain the recommendation. `Verified Complete` is invalid while the audit report is missing, failing, or contains unresolved blocking findings.

## 17. Closure Approval

| Role | Name | Decision | Date | Signature / immutable reference |
|---|---|---|---|---|
| Phase Owner | | Recommend | | |
| Evidence Custodian | | Evidence complete / incomplete | | |
| Phase Auditor | | Pass / Pass with observations / Fail | | |
| Phase Approver | | Approve / Reject | | |
| Release Manager | | Closure gate passed / failed | | |

The roadmap status may change to `Verified Complete` only after the full plan/report/evidence/audit set is approved for the recorded merge commit.
