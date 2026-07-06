---
title: Service Boundary Consolidation
status: active-control
owner: roadmap-governance
reviewers: [roadmap-governance, release-management, documentation-governance]
audience: roadmap-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 30
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/roadmap, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Service Boundary Consolidation

**Status:** pending targeted refactor

Do not delete `app/services/` wholesale. After post-530 runtime facades, `app/services/` contains active cross-cutting runtime code.

Only delete files proven unused by import/call-site scan and full tests.
