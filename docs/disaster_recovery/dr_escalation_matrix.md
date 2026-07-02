---
title: "Disaster Recovery Escalation Matrix"
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

# Disaster Recovery Escalation Matrix

## Roles

| Role | Owner |
| --- | --- |
| Incident Commander | release-owner |
| Technical Lead | engineering |
| Privacy Owner | privacy |
| Communications Owner | support |
| Database Owner | database-owner |
| Platform Owner | platform-owner |

## Escalation Rules

- critical database recovery escalates to engineering and release owner
- audit log recovery escalates to privacy owner
- communications impact escalates to support owner
- learner data risk escalates to privacy owner
- production restoration requires release-owner approval

## Boundary

This matrix records escalation ownership. It does not page owners automatically.
