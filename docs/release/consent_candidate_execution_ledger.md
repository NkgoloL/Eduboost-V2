---
title: "Release — Consent Candidate Execution Ledger"
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
# Consent Candidate Execution Ledger

**Status:** consent runtime execution harness active

## Executable candidates

| Candidate | Harness | Destructive? |
|---|---|---|
| consent.granted | normalized audit-compatible payload | no |
| consent.status.read | normalized audit-compatible payload | no |

## Boundary

The harness proves consent operation normalization. It does not merge `consent_records` and `parental_consents`.
