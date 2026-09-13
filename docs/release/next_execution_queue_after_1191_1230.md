---
title: "Release — Next Execution Queue After EVID-001 / code_1191_1230"
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
# Next Execution Queue After EVID-001 / code_1191_1230

## Next batch

`DIAG-001 / code_1231_1270` — diagnostics served-item/session/CAPS binding.

## Scope candidates

1. Persist or reconstruct served item IDs.
2. Wire `validate_session_served_item_binding` into adaptive response route behavior.
3. Reject mismatched `caps_ref`.
4. Add negative tests for unserved item, duplicate item, wrong session, wrong learner, and CAPS mismatch.
5. Update evidence registry status after runtime proof.
