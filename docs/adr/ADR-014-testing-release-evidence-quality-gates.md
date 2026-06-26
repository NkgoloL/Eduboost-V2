---
title: "ADR-014: Testing, Release Evidence, and Quality Gates Decision"
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
# ADR-014: Testing, Release Evidence, and Quality Gates Decision

## Status

Accepted for repository-side production-readiness evidence.

## Decision

EduBoost V2 will use layered automated testing, release evidence bundles, explicit quality gates, defect triage, coverage ratchets, known-issues review, smoke tests, and manual approval for beta and production release stages.

## Rationale

Production readiness requires more than a passing unit suite. The platform needs deterministic gates across backend, frontend, API contract, security, accessibility, performance, smoke, and release-evidence domains.

## Required Controls

- pytest unit tests are required
- integration tests are required
- API contract tests are required
- frontend and E2E tests are required
- security tests are required
- accessibility tests are required
- performance smoke tests are required
- release evidence bundle is required
- quality gate waiver policy is required
- manual approval is required for beta and production
- release blockers must block production
- known issues review is required

## Boundary

This ADR records testing and release quality-gate decision evidence. It does not configure external branch protection, run CI jobs, approve releases, or authorize production launch.
