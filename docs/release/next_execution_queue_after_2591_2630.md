---
title: "Release — Next Execution Queue After AUTH-LIFECYCLE-HTTP-PROOF-001 / code_2591_2630"
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
# Next Execution Queue After AUTH-LIFECYCLE-HTTP-PROOF-001 / code_2591_2630

## Recommended next batch

`AUTH-LIFECYCLE-SEMANTIC-PROOF-001 / code_2631_2670` — focused semantic tests for logout/revoke refresh-token and cookie behavior, using mocked repositories/session boundaries where live DB is not available.

## Boundary

Keep live DB proof separate from mocked semantic proof.
