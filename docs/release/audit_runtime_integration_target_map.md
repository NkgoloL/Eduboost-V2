---
title: Audit Runtime Integration Target Map
status: release-record
owner: release-management
reviewers: [release-management, evidence-custodian, documentation-governance]
audience: release-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 180
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/release, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Audit Runtime Integration Target Map

**Status:** dry-run only

## Target

| Target ID | Candidate | Runtime wiring |
|---|---|---|
| BIR-451-AUDIT-CONSENT | BCW-421-AUDIT-CONSENT-GRANTED | blocked until scoped PR approval |

## Boundary

The audit target uses an in-memory sink for dry-run proof. It does not write to production audit persistence.
