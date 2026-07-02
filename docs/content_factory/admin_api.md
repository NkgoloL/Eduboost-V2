---
title: "Content Factory Admin API"
status: active
owner: content-factory
reviewers: [content-factory, curriculum, engineering]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-24
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: [app/services/content_factory, data/content_factory, docs/content_factory]
---

# Content Factory Admin API

Canonical prefix: `/api/v2/admin/content-factory`.

The API exposes admin-only routes for scopes, coverage, dry-run generation runs, artifacts, provenance, review queue, seed checks, and reports. There is no public `/api/v2/content-factory` route.

Important route groups:

- `/scopes/*` for registry-backed scope, target, and coverage reads
- `/runs/*` for dry-run run/task ledger visibility and cancellation/retry controls
- `/artifacts/*` for artifact/provenance reads and lifecycle actions
- `/review-queue` for pending review visibility
- `/scopes/{scope_id}/dry-run-seed`, `/seed-staging`, `/staging-verification`, and `/promote-production` for gated movement
