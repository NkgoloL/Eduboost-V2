---
title: Diagnostics Session Binding Repair Report
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

# Diagnostics Session Binding Repair Report

Generated at: `2026-05-19T19:36:16Z`

**Status:** implemented at route-runtime level

- diagnostics router patched: `False`
- evidence registry patched: `False`
- adaptive next-item rejects mismatched query caps_ref against recovered session caps_ref
- adaptive respond rejects item IDs not recorded in recovered session served_item_ids
- adaptive respond rejects mismatched response caps_ref when supplied
