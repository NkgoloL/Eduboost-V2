---
title: "Release — Next Execution Queue After ARQ-001 / code_1111_1150"
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
# Next Execution Queue After ARQ-001 / code_1111_1150

## Next batch

`POPIA-001 / code_1151_1190` — POPIA lifecycle HTTP response-contract proof.

## Scope candidates

1. Decide canonical lifecycle response shape.
2. Normalize deny/withdraw/renew outputs to declared response models.
3. Add HTTP tests with `raise_server_exceptions=True`.
4. Add unauthorized learner mutation denial tests.
5. Add audit event assertions for grant/deny/withdraw/renew.
