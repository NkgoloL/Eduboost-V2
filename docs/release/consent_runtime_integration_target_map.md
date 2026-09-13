---
title: "Release — Consent Runtime Integration Target Map"
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
# Consent Runtime Integration Target Map

**Status:** dry-run only

## Target

| Target ID | Candidate | Runtime wiring |
|---|---|---|
| BIR-452-CONSENT-GRANT | BCW-431-CONSENT-GRANT-PAYLOAD | blocked until scoped PR approval |

## Boundary

The consent target produces an audit-compatible payload only. It does not merge consent tables or alter POPIA boundaries.
