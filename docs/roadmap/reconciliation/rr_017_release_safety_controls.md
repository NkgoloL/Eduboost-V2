---
title: RR-017 Release Safety Controls
status: active
owner: release-engineering
reviewers: [release, operations, security, privacy]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 60
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/roadmap, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# RR-017 Release Safety Controls

## Register citation

- RR item: `RR-017`
- Register title: `Production deployment blockers`
- Source: `EduBoost_V2_North_Star_TODO.md`
- Priority: `P0`

## Purpose

RR-017 records release-safety controls for operations that must stay blocked unless a later, explicit governance gate authorises them.

The controls cover:

- destructive audit/consent database changes
- `alembic stamp head` repair on production databases
- production database mutation outside an approved migration window
- mutating health probes
- break-glass exception handling
- release change-control boundaries

This slice records safety controls only. It also carries the RR-016 clean-state caveat from the uploaded snapshot where `docs/reports/` appeared as untracked local residue during capture. It does not authorise production release, deployment, release tagging, public beta activation, billing launch, live payment processing, or runtime KG implementation.

## Dependency

RR-017 requires RR-016 operational drills to be valid before evidence capture.

## Required final evidence outputs

- `docs/release_safety/rr017_release_safety_control_attestation.md`
- `docs/release_safety/rr017_prohibited_operations_register.md`
- `docs/release_safety/rr017_migration_window_control.md`
- `docs/release_safety/rr017_health_probe_immutability_validation.md`
- `docs/release_safety/rr017_release_change_control_boundary.md`

## Explicit boundary

- Release safety controls recorded: false until final evidence capture
- Destructive audit consent DB changes blocked: true
- Alembic stamp head repair blocked: true
- Production DB mutation requires migration window: true
- Mutating health probes blocked: true
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
PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_rr017_release_safety_controls.py --json
```
