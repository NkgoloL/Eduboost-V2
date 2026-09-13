---
title: "Release — Next Execution Queue After EVID-001R + DIAG-SCORE-001 / code_1631_1670"
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
# Next Execution Queue After EVID-001R + DIAG-SCORE-001 / code_1631_1670

## Recommended next batch

`CI-001 / code_1671_1710` — CI authority and release evidence gate.

## Scope candidates

1. Verify required workflow files exist.
2. Add local CI-equivalent bundle target.
3. Add `docs/release/ci_evidence.md` template requiring real GitHub Actions run URL.
4. Keep CI-001 external-blocked until the run URL is attached.
