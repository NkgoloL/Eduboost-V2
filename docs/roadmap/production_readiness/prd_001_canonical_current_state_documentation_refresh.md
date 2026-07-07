---
title: PRD-0.1 Canonical Current-State Documentation Refresh
status: active
owner: production-readiness
reviewers: [engineering, product, privacy, security, operations, documentation-governance]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-07-07
review_interval_days: 30
evidence_command: PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_prd001_canonical_current_state_documentation_refresh.py --json
code_anchors: [docs/current_state.md, README.md, docs/README.md, docs/roadmap/README.md, docs/architecture/README.md]
---

# PRD-0.1 — Canonical Current-State Documentation Refresh

## Purpose

Refresh the canonical human-facing documentation after RR closure, KG closure, KG-ACT-001 controlled runtime activation, KG-8 post-switch review, KG roadmap closure, and PRD-0.0 production-readiness stream authority.

This slice aligns the first documents that engineers, reviewers, and stakeholders read before more production-readiness work starts.

## Scope

In scope:

- `docs/current_state.md`
- `README.md`
- `docs/README.md`
- `docs/roadmap/README.md`
- `docs/architecture/README.md`
- PRD-0.1 authority and evidence records
- verification that stale RR/KG statements no longer appear in canonical current-state files

Out of scope:

- Historical-report quarantine, handled by PRD-0.2.
- Documentation housekeeping ratchet regeneration, handled by PRD-0.3.
- Test/dependency baseline work, handled by PRD-0.4 and PRD-0.5.
- Workflow inventory and CI cleanup beyond this slice, handled by PRD-0.6.
- OpenAPI/generated artifact canonicalisation, handled by PRD-0.7.
- Branch/release naming reconciliation, handled by PRD-0.8.
- Production release, deployment, public beta, billing, live learner traffic, or new KG work.

## Required truth statements

The refreshed documents must state:

```text
RR roadmap/TODO register: closed
KG roadmap: closed through KG-8
Controlled runtime KG authority switch: executed
Production-readiness stream: open
Current authorised item: PRD-0.1
PRD-1 implementation: blocked until PRD-0.10 closure
Production release: not authorised
Deployment: not authorised
Public beta/live learner traffic: not authorised
Billing/live payments: not authorised
New KG slice: not authorised
```

## Exit criteria

- PRD-0.0 verifier remains valid.
- Canonical current-state files exist and include the required truth statements.
- Stale claims from older RR/KG states are removed from canonical current-state files.
- Production/beta/billing/deployment boundaries remain false.
- Runtime KG authority state remains true/executed.
- PRD-0.2 becomes the next authorised PRD-0 item after evidence capture.
