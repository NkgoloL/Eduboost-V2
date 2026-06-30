---
title: "API Documentation"
status: active
owner: backend
reviewers: [frontend, qa]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 30
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/api/README.md, docs/openapi.json]
---

# API Documentation

The generated OpenAPI specification is the API contract source of truth. Human-authored API documents must not contradict `docs/openapi.json`.

Frontend client route documentation must be validated against backend routes before it is treated as current.
