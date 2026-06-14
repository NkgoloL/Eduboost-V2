# Phase <NN> Execution Plan — <Phase Title>

**Document version:** 1.0  
**Date:** YYYY-MM-DD  
**Status:** Draft | In Review | Approved for Execution | Superseded  
**Phase:** <NN>  
**Phase owner:** <name/role>  
**Phase approver:** <name/role>  
**Release manager:** <name/role>  
**Evidence custodian:** <name/role>  
**Planned phase auditor:** <name/role or independent reviewer profile>  
**Auditor independence:** Independent | Partially independent with controls | TBD before start  
**Branch:** `phase-<NN>/<slug>`  
**Base branch:** `<canonical branch>`  
**Base commit:** `<SHA>`  
**Target milestone/date:** <value>  
**Governing roadmap:** `<version/path>`  
**Evidence directory:** `docs/release-evidence/phase-<NN>/`

> Substantive phase execution may not begin until this plan is approved and committed. The plan must define the complete plan/report/evidence/audit closure set before implementation starts.

## 1. Objective and Measurable Outcome

State the phase objective, the observable outcome, and the business/learner risk reduced by the phase.

## 2. Dependencies and Preconditions

| Dependency / precondition | Required state | Evidence | Owner | Status |
|---|---|---|---|---|
| Previous phase | Verified Complete with full control set | Link | | ☐ |

## 3. Pre-Execution Baseline

Record the exact branch, commit, worktree state, environment, toolchain, current tests, open defects, existing implementation, historical claims, and known evidence gaps relevant to the phase.

## 4. Scope

### In scope

- ...

### Out of scope

- ...

## 5. Roadmap and Control-Set Traceability

| Roadmap outcome / exit criterion | Planned work | Verification method | Evidence item ID | Audit procedure | Owner |
|---|---|---|---|---|---|
| ... | ... | ... | E-<NN>-001 | ... | ... |

Every roadmap exit criterion must appear in this table or be marked Not Applicable with an approved rationale. Every mandatory criterion must have both planned evidence and an audit procedure.

## 6. Work Breakdown and Execution Order

| ID | Work item | Acceptance criteria | Estimate | Owner | Depends on | Status |
|---|---|---|---:|---|---|---|
| P<NN>-001 | ... | ... | ... | ... | ... | Not started |

## 7. Test and Verification Plan

For each command or review, state the expected minimum test count, expected result, environment, and raw evidence output.

| Gate | Command / review | Environment | Expected count/result | Failure policy | Evidence item ID |
|---|---|---|---|---|---|
| ... | ... | ... | ... | Fail closed | E-<NN>-... |

## 8. Security, Privacy, Safety, Accessibility, Content, and Data Impact

Document applicable controls, threat/abuse cases, reviewers, data classifications, retention, redaction, learner-safeguarding impact, and non-applicable rationale.

## 9. Migration, Deployment, Rollback, and Recovery

Describe schema/configuration/content migrations, deployment method, compatibility constraints, rollback triggers, rollback steps, forward-fix limits, backup requirements, and recovery verification.

## 10. Observability and Operations

Define logs, metrics, traces, dashboards, alerts, runbooks, support impact, on-call ownership, privacy-safe fields, and operational acceptance tests required by the phase.

## 11. Risks, Assumptions, External Dependencies, and Stop Conditions

| ID | Risk / assumption | Probability | Impact | Mitigation | Trigger / stop condition | Owner |
|---|---|---:|---:|---|---|---|
| ... | ... | ... | ... | ... | ... | ... |

## 12. Evidence-Pack Plan

### 12.1 Required index

The phase must produce:

`docs/release-evidence/phase-<NN>/phase_<NN>_evidence_index.md`

### 12.2 Planned evidence inventory

| Evidence ID | Criterion / claim | Artifact or raw output | Source state/environment | Sensitivity | Custodian | Revalidation trigger |
|---|---|---|---|---|---|---|
| E-<NN>-001 | ... | ... | ... | Public/Internal/Restricted | ... | ... |

### 12.3 Evidence quality rules

- Raw or machine-readable output is required where practical.
- Screenshots must identify source state, environment, timestamp, and operator.
- Every artifact must have a hash or immutable reference where practical.
- Evidence from another commit/environment must be labelled contextual.
- Test counts, warnings, skips, xfails, collection errors, and retries must be retained.
- Sensitive evidence must be redacted, access-controlled, and assigned a retention period.

## 13. Phase Audit Plan

### 13.1 Auditor and independence

State the planned auditor, competence needed, independence level, conflicts, and mitigations for a single-developer context.

### 13.2 Audit scope and sampling

| Audit area | Criteria | Independent procedure | Sample / minimum coverage | Expected evidence |
|---|---|---|---|---|
| Plan timing | Plan approved before execution | Inspect git/history and approvals | 100% | ... |
| Critical gates | ... | Reproduce / observe | ... | ... |

### 13.3 Mandatory audit procedures

- Trace roadmap → execution plan → implementation report → evidence index.
- Reproduce or observe every critical/high-risk gate.
- Assess failures, warnings, skipped tests, exceptions, and deferred work.
- Verify canonical merge commit, post-merge CI, environment identity, and artifact digest.
- Issue `Pass`, `Pass with non-blocking observations`, or `Fail`.

## 14. Required Implementation Report

The phase must produce:

`docs/roadmap/execution/phase_<NN>_implementation_report.md`

The report must reconcile every task, criterion, amendment, evidence item, defect, exception, and audit-readiness requirement in this plan.

## 15. Change Control

Material changes require a versioned amendment before affected work is accepted. Mandatory criteria may not be silently weakened, removed, or deferred.

### Change log

| Version | Date | Change | Reason | Impact on evidence/audit | Approved by |
|---|---|---|---|---|---|
| 1.0 | ... | Initial plan | ... | ... | ... |

## 16. Start-Gate Checklist

- [ ] Canonical execution-plan path is correct.
- [ ] Objective and measurable outcome are clear.
- [ ] Dependencies and preconditions are satisfied or approved.
- [ ] Every roadmap exit criterion is mapped.
- [ ] Scope and exclusions are explicit.
- [ ] Work, estimates, ownership, and WIP order are defined.
- [ ] Tests, minimum counts, evidence, and environments are defined.
- [ ] Security/privacy/safety/accessibility/content/data impacts are addressed.
- [ ] Migration/deployment/rollback/recovery are addressed where applicable.
- [ ] Risks, stop conditions, and escalation triggers are recorded.
- [ ] Evidence custodian and evidence inventory are defined.
- [ ] Auditor, independence level, audit scope, and sampling are defined.
- [ ] Implementation-report path is reserved.
- [ ] Phase owner, approver, and Release Manager are named.
- [ ] Plan is committed before substantive implementation.

## 17. Approval to Start

| Role | Name | Decision | Date | Signature / immutable reference |
|---|---|---|---|---|
| Phase Owner | | Accept | | |
| Evidence Custodian | | Evidence plan accepted | | |
| Planned Phase Auditor | | Audit plan accepted / conflict disclosed | | |
| Phase Approver | | Approve / Reject | | |
| Release Manager | | Start gate passed / failed | | |
