---
title: API Documentation Index
status: active
owner: backend
reviewers: [frontend, qa]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-06-22
review_interval_days: 30
evidence_command: make openapi-check && make route-inventory-check
code_anchors: [app/api_v2.py, docs/openapi.json]
---

# API Documentation

The generated OpenAPI specification is the API contract source of truth. Human-authored API documents must not contradict `docs/openapi.json`.

Frontend client route documentation must be validated against backend routes before it is treated as current.
