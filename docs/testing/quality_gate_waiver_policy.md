---
title: "Quality Gate Waiver Policy"
status: active
owner: quality
reviewers: [quality, engineering, release-management]
audience: quality-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-24
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: [tests, pytest.ini, Makefile]
---

# Quality Gate Waiver Policy

## Purpose

This policy defines when a quality-gate failure may be waived.

## Waiver Rules

- release blockers cannot be waived for production
- critical defects cannot be waived for production without release-owner and privacy/security review where applicable
- security scan failures require security-owner review
- accessibility failures require documented impact and remediation owner
- performance regressions require documented risk acceptance
- waiver must include owner, expiry, affected release stage, and evidence link
- waiver must be retained in the release evidence bundle

## Boundary

This policy records waiver governance. It does not approve a waiver automatically.
