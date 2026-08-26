---
title: "Frontend Runtime Inventory"
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
code_anchors: ["docs/frontend/frontend_runtime_inventory.md"]
---

# Frontend Runtime Inventory

## Purpose

This inventory records frontend package scripts and runtime command assumptions for Cluster G.

## Package Manager

- inferred package manager: `pnpm`

## Required Command Areas

- install dependencies
- start development server
- build frontend
- run frontend unit tests
- run Playwright E2E
- run accessibility scaffold

## Package Scripts

### `package.json`

| Script | Command |
| --- | --- |
| _none_ | _none_ |

## Cluster G Commands

```bash
make frontend-route-inventory
make frontend-api-client-inventory
make frontend-playwright-scaffold-check
make frontend-playwright-specs-check
make frontend-e2e
```
