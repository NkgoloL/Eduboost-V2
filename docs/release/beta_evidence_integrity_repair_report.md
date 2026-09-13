---
title: "Release — Beta Evidence Integrity Repair Report"
status: "active"
owner: "release"
reviewers: ['release', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Beta Evidence Integrity Repair Report

Generated at: `2026-08-29T09:32:52Z`

## Summary

This repair quarantines placeholder/manual-bypass/local-mock/synthetic evidence and restores truthful beta readiness semantics.

| Gate | Previous status | Repaired status | Source type | Integrity |
|---|---|---|---|---|
| remote_ci | pending_remote_ci_evidence | pending_remote_ci_evidence | unknown | pending_real_evidence |
| branch_protection | pending_branch_protection_evidence | pending_branch_protection_evidence | unknown | synthetic_invalid |
| content_gate | pass | pass | educator_review_log | valid |
| staging_smoke | synthetic_invalid | synthetic_invalid | unknown | synthetic_invalid |
| backup_drill | pending_backup_evidence | pending_backup_evidence | unknown | pending_real_evidence |
| restore_drill | synthetic_invalid | synthetic_invalid | unknown | synthetic_invalid |
| rollback_drill | synthetic_invalid | synthetic_invalid | unknown | synthetic_invalid |
| alertmanager_drill | synthetic_invalid | synthetic_invalid | unknown | synthetic_invalid |

## Release rule

Beta readiness is blocked unless every required gate has trusted real evidence or an explicit approved waiver for the content gate only.
