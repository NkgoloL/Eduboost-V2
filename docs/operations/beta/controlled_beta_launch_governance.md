---
title: Phase 18 Controlled Beta Launch Governance
status: active-policy
owner: operations
reviewers: [operations, security, release-management]
audience: operator
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 90
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/operations, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Phase 18 Controlled Beta Launch Governance

This document defines the controlled beta launch-governance package for EduBoost. It is intentionally a governance-readiness artifact and does not authorise production release, deployment, public beta, controlled beta launch activation, live learner traffic, learner data migration, or runtime KG implementation.

## Governance Objective

Ensure the controlled beta can be reviewed with clear owners, evidence, operational boundaries, consent controls, support routes, incident response, rollback, and observability before any learner-facing launch activation is considered.

## Required Owners

- Product / beta owner
- Engineering owner
- Data protection / POPIA reviewer
- Support owner
- Incident commander
- Evidence custodian

## Launch Decision Boundary

A later launch-activation gate must explicitly claim controlled beta launch and live learner traffic. This Phase 18 governance gate records only that the launch governance pack is present and reviewable.
