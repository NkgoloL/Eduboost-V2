---
title: "Release Blockers — Release Blocker Waiver Policy"
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
# Release Blocker Waiver Policy

## Required Waiver Rules

- low severity waiver requires release owner
- medium severity waiver requires release owner and engineering
- high severity waiver requires release owner and security
- waiver expiry must be between 1 and 30 days
- waiver requires compensating controls
- release-blocker severity cannot be waived
- waiver evidence must live under docs/release_blockers/

## Boundary

This policy records waiver governance. It does not approve waivers automatically.
