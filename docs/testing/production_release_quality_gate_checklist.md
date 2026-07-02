---
title: "Production Release Quality Gate Checklist"
status: "current-evidence"
owner: "quality"
reviewers: "[quality, engineering, release-management]"
audience: "quality-reviewer"
source_of_truth: "false"
supersedes: "[]"
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: "60"
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[tests, pytest.ini, Makefile]"
---

# Production Release Quality Gate Checklist

## Required Checks

- beta evidence bundle reviewed
- production test report reviewed
- coverage report reviewed
- security scan reviewed
- accessibility report reviewed
- performance report reviewed
- production smoke test plan reviewed
- known issues register reviewed
- rollback plan reviewed
- privacy/security approvals reviewed where applicable
- release owner approval recorded

## Boundary

This checklist records production quality-gate expectations. It does not approve production launch automatically.
