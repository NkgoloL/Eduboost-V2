---
title: "Phase 18 Controlled Beta Observability Plan (Controlled Beta Observability Plan)"
status: "active"
owner: "operations"
reviewers: ['operations', 'sre', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Phase 18 Controlled Beta Observability Plan

This controlled beta observability plan supports launch governance only. It does not authorise production release, deployment, public beta, controlled beta launch activation, live learner traffic, or runtime KG implementation.

## Required Signals

- API readiness and deep health
- Postgres connectivity
- Redis connectivity
- Auth/dev-session success rate for test environments
- Diagnostic item fetch success/failure
- Lesson completion success/failure
- Parent portal report load success/failure
- Consent/data-rights route success/failure

## Evidence Boundary

Observability readiness is a prerequisite for a later launch activation gate, not a launch authorisation by itself.
