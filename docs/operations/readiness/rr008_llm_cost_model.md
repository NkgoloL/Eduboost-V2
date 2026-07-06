---
title: RR-008 LLM Cost Model
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

# RR-008 LLM Cost Model

LLM cost model recorded: true

## Cost drivers

- diagnostic explanations;
- adaptive lesson generation;
- remediation hints;
- parent/guardian summaries;
- content-review support workflows.

## Required controls

- Route LLM calls through the AI gateway.
- Prefer cached or reviewed content where available.
- Track requests by route, learner cohort, and feature area.
- Apply per-session and per-cohort budget alerts before expanding usage.
- Record anomalous spend as an operational incident if it threatens service continuity.

## Reporting cadence

During controlled beta, LLM usage should be reviewed at least weekly alongside learner session metrics and support volume.

## Boundary

This model is an operational guardrail. It does not authorise production release, public beta, or runtime KG implementation.
