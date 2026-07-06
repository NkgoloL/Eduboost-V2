---
title: First Consent Runtime Wiring PR
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

# First Consent Runtime Wiring PR

**Status:** scoped implementation candidate active

## Scope

This PR introduces the first non-destructive consent runtime wiring helper for exactly one selected candidate:

```text
BCW-431-CONSENT-GRANT-PAYLOAD
```

## Boundary

This PR does not merge consent tables, delete records, alter POPIA authorization boundaries, mutate a database, or change route registration.
