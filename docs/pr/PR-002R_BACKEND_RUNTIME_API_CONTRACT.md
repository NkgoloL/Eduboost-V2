---
title: "PR-002R Backend Runtime API Contract (Pr 002R Backend Runtime Api Contract)"
status: "active"
owner: "engineering"
reviewers: ['engineering', 'architecture']
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# PR-002R Backend Runtime API Contract

**Runtime entrypoint:** `app.api_v2:app`  
**Integration branch:** `master`  
**Reference merge:** Merge pull request #52

## Contract

This document records the backend runtime/API contract used by the PR-002R evidence tests. It confirms that the canonical runtime entrypoint remains `app.api_v2:app` and that the PR evidence was traced back to the historical `master` integration line and `Merge pull request #52` context.

## Evidence Artifacts

- Generated OpenAPI: docs/openapi.json
- Generated route inventory: docs/route_inventory.md
- Runtime entrypoint verifier: scripts/check_runtime_entrypoints.py

## Explicit Non-Scope

This contract does not approve production release readiness, live database migration, destructive data operations, frontend closure, E2E closure, or runtime knowledge-graph implementation.
