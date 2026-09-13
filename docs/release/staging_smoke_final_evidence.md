---
title: "Release — Staging Smoke Final Evidence"
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
# Staging Smoke Final Evidence

**Status:** pass

| Field | Value |
|---|---|
| Source | docs/release/staging_smoke_latest.json |
| Base URL | https://staging.example.com |
| Passed | True |
| Result count | 5 |
| Captured at | 2026-08-29T09:32:52Z |

Run `make staging-smoke` and `make staging-smoke-check` against a real staging URL before beta.
