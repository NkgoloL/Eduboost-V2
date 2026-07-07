---
title: EduBoost Roadmap Documentation
status: active
owner: roadmap-governance
reviewers: [engineering, product, privacy, security, operations]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-07-07
review_interval_days: 30
evidence_command: PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_prd001_canonical_current_state_documentation_refresh.py --json
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
Current authorised item: PRD-0.1
PRD-1 implementation: blocked until PRD-0.10 closure
```

The active roadmap authority is:

- [`production_readiness/production_readiness_register.json`](production_readiness/production_readiness_register.json)
- [`production_readiness/production_readiness_boundary_contract.md`](production_readiness/production_readiness_boundary_contract.md)
- [`production_readiness/prd_0_expanded_post_closure_current_state_authority_refresh.md`](production_readiness/prd_0_expanded_post_closure_current_state_authority_refresh.md)

## Active PRD-0 sequence

PRD-0 is a cleanup-first mini-program. It must close before PRD-1 starts:

```text
PRD-0.0  Production-readiness stream authority and register
PRD-0.1  Canonical current-state documentation refresh
PRD-0.2  Historical report and stale-source quarantine
PRD-0.3  Documentation housekeeping ratchet refresh
PRD-0.4  Test/dependency bootstrap baseline
PRD-0.5  Test failure and collection stabilisation register
PRD-0.6  Workflow command hygiene and CI inventory
PRD-0.7  OpenAPI and generated artifact canonicalisation
PRD-0.8  Branch/release naming reconciliation
PRD-0.9  Repository hygiene and generated/local artifact audit
PRD-0.10 PRD-0 closure evidence and handoff to PRD-1
```

## Production-readiness sequence after PRD-0

PRD-1 through PRD-11 are registered but blocked until PRD-0 closes:

```text
PRD-1  Required CI and Release Gate Convergence
PRD-2  Runtime KG Integration and Persistence
PRD-3  Learner and Parent Vertical Journey Hardening
PRD-4  Content, CAPS, and Educational Quality Readiness
PRD-5  POPIA Live Data Operations and Privacy Assurance
PRD-6  Security Assurance and External Review
PRD-7  Observability, SRE, and Incident Readiness
PRD-8  Performance, Scale, and Cost Execution
PRD-9  Billing and Commercial Launch Readiness
PRD-10 Controlled Beta / Live Learner Traffic Authorisation
PRD-11 Production Release and Deployment Authorisation
```

## Closed roadmap streams

| Stream | State | Current authority |
|---|---|---|
| RR roadmap/TODO reconciliation | Closed through RR-018 | Historical/evidence only |
| Knowledge Graph roadmap | Closed through KG-8 plus KG-ACT-001 | No new KG slice authorised |
| PRD production-readiness | Open at PRD-0 | Active next-work authority |

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
prd1_implementation_authorised: false
```

## Historical roadmap documents

Historical phase plans, old audit roadmaps, and archived register entries may remain for traceability. They must not be treated as live next-work authority unless a current PRD document explicitly references them.
