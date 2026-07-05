---
title: "Database Restore Runbook"
status: "active-runbook"
owner: "operations"
reviewers: ["operations", "security", "privacy"]
audience: "operator"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[docs/disaster_recovery, scripts]"
---

# Database Restore Runbook

## Pre-Restore Checks

- confirm target environment is isolated
- confirm backup manifest checksum
- confirm restore target timestamp
- confirm migration baseline

## Restore Steps

- restore database snapshot
- apply WAL archive to target timestamp
- run migration status check
- rotate target-only credentials

## Post-Restore Validation

- run application smoke tests
- run data integrity checks
- verify selected learner and audit rows in isolated environment
- verify no production traffic is pointed at the restored target

## Rollback Steps

- discard target database
- restore previous staging snapshot
- record restore failure evidence

## Boundary

This runbook is repository-side evidence and does not restore live data automatically.
