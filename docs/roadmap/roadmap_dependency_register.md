---
title: Roadmap Dependency Register
status: active-control
owner: roadmap-governance
reviewers: [roadmap-governance, release-management, documentation-governance]
audience: roadmap-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 30
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/roadmap, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Roadmap Dependency Register

## Required Dependency Fields

- dependency ID
- source roadmap ID
- dependency type
- description
- owner
- external flag
- mitigation
- evidence path

## Required Rules

- dependency ID must follow DEP-### format
- source roadmap ID must follow RM-### format
- external dependencies require mitigation
- roadmap dependency evidence path must live under docs/roadmap/

## Boundary

This register records roadmap dependencies. It does not satisfy external dependencies.
