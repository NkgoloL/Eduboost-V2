---
title: "Release — Audit Runtime Integration Target Map"
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
# Audit Runtime Integration Target Map

**Status:** dry-run only

## Target

| Target ID | Candidate | Runtime wiring |
|---|---|---|
| BIR-451-AUDIT-CONSENT | BCW-421-AUDIT-CONSENT-GRANTED | blocked until scoped PR approval |

## Boundary

The audit target uses an in-memory sink for dry-run proof. It does not write to production audit persistence.
