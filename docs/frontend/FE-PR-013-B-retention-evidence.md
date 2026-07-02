---
title: "FE-PR-013-B Retention Evidence"
status: current-evidence
owner: frontend
reviewers: [frontend, product, privacy]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-24
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: [app/frontend, docs/frontend/README.md]
---

# FE-PR-013-B Retention Evidence

This document summarizes the retention policy evidence for parent-review records.

- Default retention window: 90 days (`DEFAULT_RETENTION_DAYS` in `retention.ts`).
- API-level storage is redacted via `redaction.ts` before persistence.
- Repository abstraction (`ParentReviewRepository`) is provided to avoid leaking implementation details.
- Tests cover redaction of email, phone, and child-name-like fields.
