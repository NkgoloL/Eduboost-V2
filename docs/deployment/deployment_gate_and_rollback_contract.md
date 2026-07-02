---
title: "Deployment Gate and Rollback Contract"
status: "active"
owner: "release-management"
reviewers: "[release-management, operations, security]"
audience: "operator"
source_of_truth: "false"
supersedes: "[]"
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: "60"
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[Dockerfile, docker-compose.yml, docker-compose.prod.yml, .github/workflows]"
---

# Deployment Gate and Rollback Contract

## Purpose

This contract defines staging and production deployment gates, smoke tests, and rollback expectations.

## Required Staging Gate

- lint check
- unit test check
- security scan check
- Docker build check
- migration check
- staging smoke test
- rollback plan
- release notes

## Required Production Gate

- lint check
- typecheck check
- unit test check
- integration test check
- security scan check
- Docker build check
- migration check
- smoke test
- release notes
- manual production approval
- rollback plan

## Required Rollback Controls

- rollback command is documented
- database rollback policy is documented
- feature flag rollback is supported
- previous image is retained
- post-rollback smoke test is required
- rollback incident record is required

## Boundary

This contract records deployment-gate and rollback readiness. It does not deploy or rollback services.
