---
title: "Release Blockers — Final Release Blocker Register"
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
# Final Release Blocker Register

## Required Fields

- blocker ID
- domain
- title
- severity
- status
- owner
- evidence path
- closure path
- waiver path
- external dependency
- blocks launch flag

## Required Rules

- blocker ID must follow RB-### format
- release blocker owner is required
- closed blockers require closure evidence
- waived blockers require waiver evidence
- external pending blockers require external dependency note
- critical/release-blocker items cannot remain open
- release-blocker severity cannot be waived by default

## Boundary

This register records repository-side blocker status. It does not approve launch.
