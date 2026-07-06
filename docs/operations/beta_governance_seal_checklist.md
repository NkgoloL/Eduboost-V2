---
title: Beta Governance Seal Checklist
status: active-policy
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

# Beta Governance Seal Checklist

## Purpose

The beta governance seal checklist records the final governance evidence required before the controlled staging/beta release package may be treated as complete.

## Required Seal Inputs

- Cluster H release readiness check is green
- Cluster H terminal closure assertion is present
- beta release final index is present
- post-beta evidence archive manifest is present
- beta outcome report template is present
- beta retrospective action register is present
- beta acceptance exit criteria are present
- final beta operator packet index is present
- release audit trail index is present
- release owner accountability matrix is present
- beta release decision log is present

## Required Seal Reviewers

| Role | Evidence |
| --- | --- |
| Release owner | final beta operator packet index |
| Technical approver | final PR merge readiness contract |
| Privacy/POPIA approver | POPIA consent gate closure |
| AI safety owner | Cluster F AI safety closure |
| Data resilience owner | Cluster E data resilience closure |
| Frontend owner | Cluster G frontend closure |
| Support owner | beta participant support handoff checklist |

## Seal Rules

- seal cannot be recorded while Cluster H release readiness check is failing
- seal cannot override unresolved blocker issues
- seal cannot bypass release owner accountability
- seal cannot replace manual approval workflow evidence
- seal must reference release candidate and commit SHA
- seal must reference post-beta evidence archive manifest

## Boundary

This governance seal records final evidence completeness. It does not approve production launch, execute deployment, create release tags, or override unresolved blocker issues.

## Command

```bash
make beta-governance-seal-check
```
