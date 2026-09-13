---
title: "Controlled Beta Activation Preflight Checklist (Controlled Beta Activation Preflight Checklist)"
status: "active"
owner: "operations"
reviewers: ['operations', 'sre', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Controlled Beta Activation Preflight Checklist

This checklist does not authorise controlled beta launch, deployment, learner
data migration, or live learner traffic.

- Controlled beta launch authorised: false
- Live learner traffic authorised: false

## Preflight Review Items

- Confirm Phase 17 controlled beta readiness evidence is valid.
- Confirm Phase 18 launch-governance evidence is valid.
- Confirm support owner, engineering owner, incident commander, and evidence custodian are named.
- Confirm rollback plan has been reviewed.
- Confirm observability dashboards and alert routes are known.
- Confirm no production release or public beta is implied.
- Confirm runtime KG implementation remains out of scope.

## Evidence Required Before Activation Gate

- Signed go/no-go decision record.
- Candidate cohort manifest with guardian consent references.
- Support coverage confirmation.
- Data handling register review.
- Incident response rota.
- Rollback dry-run notes or explicit waiver.
