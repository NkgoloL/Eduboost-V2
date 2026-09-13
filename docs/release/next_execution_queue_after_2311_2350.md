---
title: "Release — Next Execution Queue After EVIDENCE-ATTACHMENT-RUNBOOK-001 / code_2311_2350"
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
# Next Execution Queue After EVIDENCE-ATTACHMENT-RUNBOOK-001 / code_2311_2350

## Recommended next action

Attach real evidence using `docs/release/evidence_attachment_runbook.md`.

## Execution order

1. Attach CI evidence.
2. Attach legal/security/content approval evidence.
3. Attach staging acceptance evidence.
4. Attach live DB transaction evidence for auth, POPIA, and diagnostics.
5. Run `make final-gate-refresh`.
6. Run all release-mode checks.
7. Obtain release-owner sign-off only if generated status is `GO`.
