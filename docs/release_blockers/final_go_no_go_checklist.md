---
title: "Release Blockers — Final Go/No-Go Checklist"
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
# Final Go/No-Go Checklist

## Required Review Areas

- known issues reviewed
- rollback reviewed
- support reviewed
- privacy/security reviewed
- external dependencies reviewed
- blocker register reviewed
- evidence bundle reviewed
- release owner approval reviewed

## Required Approvers

- release owner
- engineering
- security
- privacy
- support

## Required Rules

- final go/no-go approvers are required
- release owner approval is required
- required domains are required
- GO decision must include external/manual dependency review
- GO decision must not conflict with computed blocker state

## Boundary

This checklist records final go/no-go discipline. It does not authorize production launch by itself.
