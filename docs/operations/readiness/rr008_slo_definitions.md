---
title: RR-008 SLO Definitions
status: authority
owner: operations
reviewers: [operations, security, release-management]
audience: operator
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 90
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/operations, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# RR-008 SLO Definitions

SLO definitions recorded: true

## Learner-facing SLOs

| Journey | Initial target | Measurement source | Notes |
|---|---:|---|---|
| Login/session bootstrap | p95 <= 2s | application metrics / browser timing | Controlled beta target; public beta not authorised. |
| Diagnostic item fetch | p95 <= 2s | API metrics | Aligns with beta metric from roadmap Phase 16. |
| Diagnostic answer submit | p95 <= 2s | API metrics | Includes persistence and scoring latency. |
| Lesson page load | p95 <= 3s | frontend + API metrics | Excludes cold local dev starts. |
| Parent progress view | p95 <= 3s | API metrics | Includes learner progress aggregation. |

## Availability target

Controlled beta availability target remains `>= 99.5%` while production-release authority remains false.

## Error budget boundary

Any critical security, PII exposure, or consent incident consumes the relevant safety budget immediately and must be escalated through the incident response runbooks.
