---
title: PR-009 Product/ops/future differentiation
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

# PR-009 Product/ops/future differentiation

## Scope

This PR closes the final cross-functional launch-readiness batch: degraded-mode behavior for optional dependencies, product/legal/support operating docs, beta transparency UI, POPIA-safe analytics schema, experimentation guardrails, and future differentiation roadmap.

## Runtime behavior

- Added capability registry for optional services: LLM generation, billing, email, analytics.
- `/api/v2/system/capabilities` exposes non-sensitive capability/fallback state.
- `/ready` now reports optional capability degradation without failing critical readiness.
- Telemetry dispatch becomes safe no-op when PostHog is not configured.
- Billing facade returns a structured `503 capability_unavailable` when Stripe is not configured.

## Frontend behavior

- Added visible private-beta/limited-scope label.
- Added report issue feedback link in learner shell and lesson views.

## Documents added

- Launch scope.
- Pricing operations and refund process.
- Support model.
- Legal document index.
- Policy versioning workflow.
- Learning event schema.
- Ethical experimentation guidelines.
- Transparent roadmap.
- Differentiation strategy.

## External follow-up

The repository now documents the process, but actual legal approval, support inbox setup, payment-provider go-live, backup restore drills, monitoring verification, and beta cohort operations still require live environment execution.
