---
title: Beta Known Issues Register
status: active
owner: operations
reviewers: [operations, security, release-management]
audience: operator
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 90
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/operations, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Beta Known Issues Register

## Purpose

The beta known issues register records known limitations, accepted risks, and unresolved issues before and after controlled beta validation.

## Required Issue Fields

| Field | Value |
| --- | --- |
| Issue ID | pending |
| Source | feedback / smoke / monitoring / support / approval |
| Release Candidate | pending |
| Commit SHA | pending |
| Severity | low / medium / high / blocker |
| Area | learner / parent / consent / privacy / AI safety / deployment / data resilience |
| Owner | pending |
| Status | accepted risk / fix required / deferred / closed |
| Mitigation | pending |
| Evidence Link | pending |

## Required Rules

- blocker known issue blocks beta acceptance until resolved or release is rejected
- privacy known issue requires POPIA owner review
- consent known issue requires consent boundary review
- AI safety known issue requires AI safety evidence owner review
- data resilience known issue requires backup or restore evidence review
- support known issue must link to participant support handoff
- accepted risk must record approver and mitigation
- deferred issue must record target milestone and owner

## Evidence Links

- `docs/operations/beta_feedback_intake_contract.md`
- `docs/operations/beta_monitoring_incident_trigger_matrix.md`
- `docs/operations/beta_participant_support_handoff_checklist.md`
- `docs/operations/beta_release_decision_log.md`
- `docs/security/POPIA_CONSENT_GATE_CLOSURE.md`
- `docs/ai/CLUSTER_F_CLOSURE.md`
- `docs/operations/data_resilience_evidence_index.md`

## Boundary

This known issues register records release risk evidence. It does not accept risk automatically, approve release, execute remediation, or override incident triggers.

## Command

```bash
make beta-known-issues-register-check
```
