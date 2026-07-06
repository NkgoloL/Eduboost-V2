---
title: Next Execution Queue After ARQ-001 / code_1111_1150
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

# Next Execution Queue After ARQ-001 / code_1111_1150

## Next batch

`POPIA-001 / code_1151_1190` — POPIA lifecycle HTTP response-contract proof.

## Scope candidates

1. Decide canonical lifecycle response shape.
2. Normalize deny/withdraw/renew outputs to declared response models.
3. Add HTTP tests with `raise_server_exceptions=True`.
4. Add unauthorized learner mutation denial tests.
5. Add audit event assertions for grant/deny/withdraw/renew.
