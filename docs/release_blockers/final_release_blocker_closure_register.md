---
title: "Release Blockers — Final Release Blocker Closure Register"
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
# Final Release Blocker Closure Register

## Required Fields

- closure ID
- blocker ID
- closed on
- closed by
- evidence checksum
- evidence path
- residual risk
- follow-up required

## Required Rules

- closure ID must follow CLOSE-### format
- blocker ID must follow RB-### format
- evidence checksum must be 64 lowercase hex
- closure evidence path must be controlled
- residual risk summary is required

## Boundary

This register records repository-side closure evidence. It does not approve external launch.
