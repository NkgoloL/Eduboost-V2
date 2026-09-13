---
title: "Roadmap Dependency Register (Roadmap Dependency Register)"
status: "active"
owner: "engineering"
reviewers: ['engineering', 'product']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
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
