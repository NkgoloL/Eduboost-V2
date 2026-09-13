---
title: "Product Alignment — KG-6 Parent Alignment Privacy Boundary"
status: "active"
owner: "pedagogy"
reviewers: ['pedagogy', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# KG-6 Parent Alignment Privacy Boundary

Parent/guardian summaries in KG-6 are synthetic-only preview summaries. They must not contain guardian names, contact details, live learner identifiers, or sensitive learner records.

Required markers:

- `no_guardian_pii_used: true`
- `no_live_learner_data_used: true`
- `parent_portal_runtime_authority_authorised: false`
