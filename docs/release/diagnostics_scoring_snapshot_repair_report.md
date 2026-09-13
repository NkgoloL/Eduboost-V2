---
title: "Release — Diagnostics Scoring Snapshot Repair Report"
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
# Diagnostics Scoring Snapshot Repair Report

**Status:** implemented

- Diagnostic responses now persist per-response scoring parameters.
- Historical IRT recalculation rebuilds item objects from each response snapshot.
- The current item object is no longer reused for all historical responses.
