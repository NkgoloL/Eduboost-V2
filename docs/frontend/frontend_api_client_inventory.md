---
title: "Frontend API Client Inventory"
status: "active"
owner: "quality"
reviewers: ["quality", "engineering"]
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-08-26"
review_interval_days: 60
evidence_command: "make docs-housekeeping-check"
code_anchors: ["docs/frontend/frontend_api_client_inventory.md"]
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
