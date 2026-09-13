---
title: "Release — Dormant Router Inventory"
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
# Dormant Router Inventory

**RR item:** RR-003  
**Status:** inventory baseline

This inventory records router modules that need explicit review before retirement, archival, or route consolidation work. This document does not remove routes.

| Router | Current classification | Required next action |
|---|---|---|
| `app/modules/diagnostics/bias_review_router.py` | specialist diagnostic governance route | confirm active use or archive under RR-005 |
| `app/modules/lessons/lesson_coverage_router.py` | specialist lesson coverage route | confirm active use or archive under RR-005 |
| `app/modules/lessons/lesson_review_router.py` | specialist lesson review route | confirm active use or archive under RR-005 |
| `app/modules/practice/router.py` | practice module route | confirm active use or archive under RR-005 |

## Boundary

Dormant router retirement is deferred to RR-005 technical debt burn-down unless a route is proven unsafe.
