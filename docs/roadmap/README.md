---
title: EduBoost Roadmap Documentation
status: active
owner: roadmap-governance
reviewers: [engineering, product, privacy, security, operations]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-07-16
review_interval_days: 30
evidence_command: PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_prd1100r_runtime_restore_execution_7_coverage_static_security_green.py --json
code_anchors: [docs/roadmap/production_readiness/production_readiness_register.json]
---

# EduBoost Roadmap Documentation

This directory contains roadmap documentation for EduBoost V2.

## Current roadmap truth

The old phase-roadmap and reconciliation streams are not the active next-work authority. The current state is:

```text
RR roadmap/TODO register: closed
KG roadmap: closed through KG-8
Controlled runtime KG authority switch: executed
Production-readiness stream: open
Current authorised item: PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7
PRD-0 through PRD-10: closed
```

The active roadmap authority is:

- [`production_readiness/production_readiness_register.json`](production_readiness/production_readiness_register.json)
- [`production_readiness/production_readiness_boundary_contract.md`](production_readiness/production_readiness_boundary_contract.md)
- [`production_readiness/prd_1100r_runtime_restore_execution_7_coverage_static_security_green_record.json`](production_readiness/prd_1100r_runtime_restore_execution_7_coverage_static_security_green_record.json)

## Active PRD Sequence

All initial phases (PRD-0 through PRD-10) are completed and closed. The active sequence is:

```text
PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7  Coverage, Static Quality, and Security Gates (ACTIVE)
```

## Production-readiness sequence status

The production-readiness phases have progressed as follows:

- **PRD-0 through PRD-10:** Completed and Closed
- **PRD-11 (Runtime Restore):** Open / Active (Currently at Execution-7)

The historical sequence is preserved below:
```text
PRD-1  Required CI and Release Gate Convergence (Closed)
PRD-2  Runtime KG Integration and Persistence (Closed)
PRD-3  Learner and Parent Vertical Journey Hardening (Closed)
PRD-4  Content, CAPS, and Educational Quality Readiness (Closed)
PRD-5  POPIA Live Data Operations and Privacy Assurance (Closed)
PRD-6  Security Assurance and External Review (Closed)
PRD-7  Observability, SRE, and Incident Readiness (Closed)
PRD-8  Performance, Scale, and Cost Execution (Closed)
PRD-9  Billing and Commercial Launch Readiness (Closed)
PRD-10 Controlled Beta / Live Learner Traffic Authorisation (Closed)
PRD-11 Production Release and Deployment Authorisation (Active - Execution-7)
```

## Closed roadmap streams

| Stream | State | Current authority |
|---|---|---|
| RR roadmap/TODO reconciliation | Closed through RR-018 | Historical/evidence only |
| Knowledge Graph roadmap | Closed through KG-8 plus KG-ACT-001 | No new KG slice authorised |
| PRD production-readiness | Open at PRD-11 | Active next-work authority |

## Protected boundaries

The following remain unauthorised until future PRD gates explicitly change them:

```text
production_release_authorised: false
deployment_authorised: false
release_tag_authorised: false
public_beta_authorised: false
public_beta_live_traffic_authorised: false
live_learner_traffic_authorised: false
billing_launch_authorised: false
live_payment_processing_authorised: false
new_kg_slice_authorised: false
prd12_implementation_authorised: false
```

## Historical roadmap documents

Historical phase plans, old audit roadmaps, and archived register entries may remain for traceability. They must not be treated as live next-work authority unless a current PRD document explicitly references them.
