---
title: "ADR Lifecycle Contract"
status: active
owner: documentation-governance
reviewers: [engineering, release-management]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 180
evidence_command: make docs-housekeeping-stage3-check
code_anchors: []
---
# ADR Lifecycle Contract

## Required ADR Statuses

- proposed
- accepted
- superseded
- rejected

## Required ADR Sections

- context
- decision
- consequences
- status
- owner
- decision date
- superseded-by reference where applicable

## Required Rules

- accepted ADR requires decision section
- ADR context section is required
- ADR consequences section is required
- superseded ADR must identify successor
- ADR path must live under docs/adr/
- ADR ID must follow ADR-### format

## Boundary

This contract records ADR lifecycle readiness. It does not approve architecture decisions automatically.
