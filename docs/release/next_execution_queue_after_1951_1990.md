---
title: "Release — Next Execution Queue After CI-RUN-001 / code_1951_1990"
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
# Next Execution Queue After CI-RUN-001 / code_1951_1990

## Recommended next batch

`APPROVAL-EVID-001 / code_1991_2030` — legal/security/content approval evidence attachment support.

## Scope candidates

1. Add controlled helpers for attaching LEGAL-001, SEC-001, and CONTENT-001 metadata.
2. Keep each approval external-blocked until approver, date, decision, and evidence URL are present.
3. Regenerate external approval status, release go/no-go, and blocker burn-down after attachment.
4. Avoid treating templates or local commands as approval.
