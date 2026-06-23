---
title: "ADR-018: Beta Launch, Staging Acceptance, and Product Scope"
status: active
owner: architecture
reviewers: [engineering, architecture]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 180
evidence_command: make docs-housekeeping-stage3-check
code_anchors: []
---
# ADR-018: Beta Launch, Staging Acceptance, and Product Scope

## Status

Accepted for repository-side production-readiness evidence.

## Decision

EduBoost V2 will use an explicit beta-launch readiness model with controlled product scope, staging acceptance criteria, entry and exit criteria, cohort limits, consent-aware participation, feedback intake, known-issues review, no-go authority, and post-beta review.

## Required Controls

- beta product scope is required
- staging acceptance criteria are required
- beta entry criteria are required
- beta exit criteria are required
- controlled cohort limits are required
- participant consent is required
- feedback intake is required
- known issues review is required
- support readiness is required
- rollback support is required
- no-go authority is required

## Boundary

This ADR records beta launch, staging acceptance, and product-scope evidence. It does not enroll beta participants, deploy staging, approve general availability, or authorize production launch.
