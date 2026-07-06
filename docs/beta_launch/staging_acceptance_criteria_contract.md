---
title: Staging Acceptance Criteria Contract
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

# Staging Acceptance Criteria Contract

## Required Staging Acceptance Areas

- backend API smoke evidence
- frontend journey smoke evidence
- privacy and consent evidence
- support handoff evidence
- rollback evidence
- monitoring evidence
- known issues review evidence

## Required Fields

- criterion ID
- name
- status
- evidence path
- owner
- blocks beta flag
- waiver path where waived

## Required Rules

- failed blocking criteria block beta launch
- blocked criteria block beta launch
- waived criteria require waiver path
- evidence path must be controlled
- staging acceptance owner is required

## Boundary

This contract records staging acceptance readiness. It does not deploy staging or approve beta launch.
