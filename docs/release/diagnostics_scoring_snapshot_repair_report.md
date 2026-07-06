---
title: Diagnostics Scoring Snapshot Repair Report
status: release-record
owner: release-management
reviewers: [release-management, evidence-custodian, documentation-governance]
audience: release-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 180
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/release, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Diagnostics Scoring Snapshot Repair Report

**Status:** implemented

- Diagnostic responses now persist per-response scoring parameters.
- Historical IRT recalculation rebuilds item objects from each response snapshot.
- The current item object is no longer reused for all historical responses.
