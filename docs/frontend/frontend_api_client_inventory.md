---
title: "Frontend API Client Inventory"
status: "current-evidence"
owner: "frontend"
reviewers: "[frontend, product, privacy]"
audience: "developer"
source_of_truth: "false"
supersedes: "[]"
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: "60"
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[app/frontend, docs/frontend/README.md]"
---

# Frontend API Client Inventory

## Purpose

This inventory records frontend API client, fetch, and domain call surfaces.

## Required API Domains

- learner-scoped reads
- learner-scoped writes
- parent-scoped reads
- consent status and consent mutation
- diagnostic start and submit
- lesson generation and lesson retrieval
- study plan or assessment attempt
- progress/mastery retrieval
- error envelope parsing

## Discovered Surfaces

| Path | API markers | Domain markers |
| --- | --- | --- |
| _none found_ | _none_ | _none_ |

## Command

```bash
make frontend-api-client-inventory
```
