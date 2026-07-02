---
title: "Restore Drill Evidence Contract"
status: current-evidence
owner: operations
reviewers: [operations, security, privacy]
audience: operator
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-24
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: [docs/disaster_recovery, scripts]
---

# Restore Drill Evidence Contract

## Purpose

This contract defines required restore drill evidence.

## Required Drill Evidence Fields

- drill ID
- backup scope
- target environment
- started at UTC
- completed at UTC
- outcome
- observed RPO minutes
- observed RTO minutes
- checksum verified
- application smoke test passed
- data integrity test passed
- evidence path

## Required Drill Rules

- drill timestamps must be timezone-aware
- drill completion must be after start
- passing drill requires checksum verification
- passing drill requires application smoke test
- passing drill requires data integrity test
- drill evidence must be retained under docs/disaster_recovery/evidence/

## Boundary

This contract records restore-drill evidence expectations. It does not execute restore drills.
