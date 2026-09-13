---
title: "Release — Next Execution Queue After DEPLOY-FE-RUNTIME-001R / code_2471_2510R"
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
# Next Execution Queue After DEPLOY-FE-RUNTIME-001R / code_2471_2510R

## Recommended next batch

`AUTH-SERVICE-CLEANUP-001 / code_2511_2550` — remove auth service monkey-patching and move logout/revoke-all route logic into AuthApplicationService.

## Runtime deployment evidence remains separate

After this repair, runtime release proof still requires real frontend build/container/nginx/browser evidence.
