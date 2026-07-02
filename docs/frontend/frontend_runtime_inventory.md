---
title: "Frontend Runtime Inventory"
status: current-evidence
owner: frontend
reviewers: [frontend, product, privacy]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-24
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: [app/frontend, docs/frontend/README.md]
---

# Frontend Runtime Inventory

## Purpose

This inventory records frontend package scripts and runtime command assumptions for Cluster G.

## Package Manager

- inferred package manager: `npm`

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
