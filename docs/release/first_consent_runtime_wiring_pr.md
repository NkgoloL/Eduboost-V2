---
title: "Release — First Consent Runtime Wiring PR"
status: "active"
owner: "release"
reviewers: ['release', 'engineering']
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# First Consent Runtime Wiring PR

**Status:** scoped implementation candidate active

## Scope

This PR introduces the first non-destructive consent runtime wiring helper for exactly one selected candidate:

```text
BCW-431-CONSENT-GRANT-PAYLOAD
```

## Boundary

This PR does not merge consent tables, delete records, alter POPIA authorization boundaries, mutate a database, or change route registration.
