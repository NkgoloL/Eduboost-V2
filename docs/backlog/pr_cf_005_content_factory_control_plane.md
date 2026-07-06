---
title: PR-CF-005 Content Factory Control Plane
status: active-control
owner: delivery-planning
reviewers: [delivery-planning, engineering, documentation-governance]
audience: delivery-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 30
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/backlog, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# PR-CF-005 Content Factory Control Plane

Status: implemented locally on `pr-cf-005-content-factory-control-plane`; CI, staging migration, and production promotion proof remain pending.

## Scope

This batch adds the Content Factory control-plane foundation:

- expanded artifact provenance fields for ETL document/chunk citations
- centralized artifact lifecycle transitions
- DB-backed generation run/task ledger
- deterministic dry-run orchestrator skeleton
- staging seed and production promotion gates that fail closed
- assessment blueprint and study-plan template validation skeletons
- expanded admin Content Factory API
- read-only admin ETL visibility API
- live dashboard API wiring with mock fallback behind `NEXT_PUBLIC_CONTENT_FACTORY_MOCK=true`
- startup launch-content seed gate behind `CONTENT_STARTUP_SEED_ENABLED=false`

## Non-Goals

- No external LLM provider execution is enabled by default.
- No worker queue is required for tests.
- No learner-facing generated content route is added.
- No production promotion can bypass coverage/provenance/review gates.

## Feature Flags

- `CONTENT_FACTORY_GENERATION_ENABLED=false` keeps generation execution disabled; run creation remains dry-run/planned.
- `CONTENT_STARTUP_SEED_ENABLED=false` keeps startup launch seeding disabled unless explicitly enabled.
