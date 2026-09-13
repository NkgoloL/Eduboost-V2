---
title: "Roadmap — Service Boundary Consolidation"
status: "active"
owner: "engineering"
reviewers: ['engineering', 'product']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Service Boundary Consolidation

**Status:** pending targeted refactor

Do not delete `app/services/` wholesale. After post-530 runtime facades, `app/services/` contains active cross-cutting runtime code.

Only delete files proven unused by import/call-site scan and full tests.
