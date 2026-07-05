---
title: RR-016 Operational Drills
status: active
owner: operations
reviewers: [operations, reliability, security, privacy]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-05
review_interval_days: 60
evidence_command: make roadmap-reconciliation-check
code_anchors: [docs/roadmap/reconciliation, scripts/roadmap_reconciliation]
---

# RR-016 Operational Drills

## Register citation

- RR item: `RR-016`
- Register title: `Operational drills`
- Source: `EduBoost_V2_North_Star_TODO.md`
- Priority: `P0`

## Purpose

RR-016 records executable operational drill proof for the release-readiness backlog:

- backup drill
- restore drill
- rollback drill
- monitoring dashboard verification
- incident handoff verification

This slice records drill evidence only. It does not authorise production release, deployment, release tagging, public beta activation, expanded learner traffic, billing launch, live payment processing, or runtime KG implementation.

## Dependency

RR-016 requires RR-015 external approvals to be valid before evidence capture.

## Required final evidence outputs

- `docs/operations/drills/rr016_backup_drill_report.md`
- `docs/operations/drills/rr016_restore_drill_report.md`
- `docs/operations/drills/rr016_rollback_drill_report.md`
- `docs/operations/drills/rr016_monitoring_dashboard_verification.md`
- `docs/operations/drills/rr016_incident_handoff_verification.md`

## Explicit boundary

- Backup drill completed: false until final evidence capture
- Restore drill completed: false until final evidence capture
- Rollback drill completed: false until final evidence capture
- Monitoring dashboard verified: false until final evidence capture
- Incident handoff verified: false until final evidence capture
- Production release authorised: false
- Deployment authorised: false
- Release tag authorised: false
- Public beta authorised: false
- Public beta live traffic authorised: false
- Billing launch authorised: false
- Live payment processing authorised: false
- Runtime KG implementation claimed: false

## Verification

```bash
PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_rr016_operational_drills.py --json
```
