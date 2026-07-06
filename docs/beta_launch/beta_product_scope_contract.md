---
title: Beta Product Scope Contract
status: active
owner: product
reviewers: [product, release-management, privacy]
audience: product-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 90
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/beta_launch, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Beta Product Scope Contract

## Included Beta Scope

- learner onboarding
- diagnostics
- lesson generation with AI safety controls
- study plan
- parent dashboard
- POPIA rights
- notifications
- support

## Explicit Exclusions

- billing is disabled for beta launch
- public beta is not approved by this evidence
- general availability is not approved by this evidence
- production launch is not approved by this evidence

## Required Rules

- each scope item requires owner
- excluded beta scope must be explicitly marked as exclusion
- billing must be explicitly excluded or disabled for beta unless approved
- product scope evidence must live under docs/beta_launch/

## Boundary

This contract records beta product-scope readiness. It does not change runtime feature flags or enroll users.
