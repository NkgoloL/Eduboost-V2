---
title: "Roadmap — Deferred Scope Register"
status: "active"
owner: "engineering"
reviewers: ['engineering', 'product']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Deferred Scope Register

## Deferred Scope Items

| ID | Title | Reason Deferred | Unblock Condition | Owner |
| --- | --- | --- | --- | --- |
| DEF-001 | Live payment processing | Provider credentials and approvals are external | Provider account, pricing approval, and legal/commercial signoff complete | commercial-owner |
| DEF-002 | General availability launch | Requires beta outcome evidence and manual launch approval | Beta exit criteria met and production launch approval completed | release-owner |

## Required Rules

- deferred ID must follow DEF-### format
- deferred reason is required
- unblock condition is required
- risk if deferred is required
- deferred scope owner is required
- deferred scope review date must not be stale

## Boundary

This register records deferred scope. It does not complete or approve deferred work.
