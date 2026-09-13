---
title: "Release — Diagnostics Session Binding Repair Report"
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
# Diagnostics Session Binding Repair Report

Generated at: `2026-05-19T19:36:16Z`

**Status:** implemented at route-runtime level

- diagnostics router patched: `False`
- evidence registry patched: `False`
- adaptive next-item rejects mismatched query caps_ref against recovered session caps_ref
- adaptive respond rejects item IDs not recorded in recovered session served_item_ids
- adaptive respond rejects mismatched response caps_ref when supplied
