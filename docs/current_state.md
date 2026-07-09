---
title: EduBoost Current State
status: active
owner: release-management
reviewers: [engineering, product, privacy, security, operations]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-07-02
review_interval_days: 14
evidence_command: PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_prd001_canonical_current_state_documentation_refresh.py --json
code_anchors: [app/api_v2.py, app/frontend/package.json, docs/roadmap/production_readiness/production_readiness_register.json]
---

# EduBoost Current State

This file is the canonical current-state summary for EduBoost V2 after the reconciled RR roadmap, Knowledge Graph roadmap, and PRD-0.0 production-readiness stream authority were closed.

It is intentionally conservative. It records what is true now and what remains unauthorised before production, deployment, public beta, billing, live learner traffic, or further production-readiness implementation work can proceed.

## Product identity

EduBoost V2 is a South African Grade 4 Mathematics learning platform. Its product direction remains:

- CAPS-aligned curriculum coverage.
- Diagnostic assessment and adaptive learner support.
- Knowledge-graph-grounded learning-state modelling.
- AI-assisted tutoring through controlled and grounded service boundaries.
- Parent/guardian visibility into progress, consent history, and reports.
- Personalised study plans based on curriculum coverage and mastery gaps.
- Gamification through achievements, points, and badges.
- POPIA-aware privacy, consent, audit, and data-rights workflows.

## Technical identity

The active technical direction is:

- FastAPI V2 backend.
- Next.js frontend under `app/frontend`.
- PostgreSQL persistence with Alembic migrations.
- Redis-backed sessions, jobs, or runtime support where configured.
- Content Factory and curriculum tooling for controlled source ingestion and lesson material production.
- Generated OpenAPI contract under `docs/openapi.json`.
- Release and evidence automation under scripts, Makefile targets, and `docs/release-evidence/`.
- Controlled runtime KG authority switch recorded through the KG activation and closure evidence stream.

## Canonical closure state

The current closed roadmap state is:

```text
RR roadmap/TODO register: closed
Final RR roadmap reconciliation closure: valid
KG roadmap: closed through KG-8
KG-ACT-001 controlled runtime KG authority activation: valid
KG roadmap closure report: valid
PRD-0.0 production-readiness stream authority: valid
Production-readiness stream: open
Current authorised item: PRD-0.1
PRD-1 implementation: blocked until PRD-0.10 closure
New KG slice: not authorised
```

## Runtime KG authority state

The controlled KG authority switch is recorded as active in governance evidence:

```text
runtime_kg_implementation_claimed: true
runtime_kg_authority_switch_authorised: true
authority_switch_executed: true
```

This does **not** by itself authorise production release, public beta, live learner traffic, billing, deployment, or release tagging.

## Current production-readiness boundaries

Current-state refresh cadence recorded: true
RR-### governance rule: this file is refreshed against the outstanding_work_register.md cadence and remains the canonical current-state document for release governance.

These remain unauthorised:

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

## Active production-readiness sequence

The active production-readiness stream is governed by:

- `docs/roadmap/production_readiness/production_readiness_register.json`
- `docs/roadmap/production_readiness/production_readiness_boundary_contract.md`
- `docs/roadmap/production_readiness/prd_0_expanded_post_closure_current_state_authority_refresh.md`

PRD-0 must close before PRD-1 starts. PRD-0 contains documentation truth refresh, stale-source quarantine, housekeeping ratchets, test/dependency baselines, workflow inventory, generated artifact canonicalisation, branch/release naming reconciliation, repository hygiene, and PRD-0 closure evidence.

## Known caveats carried forward

The following caveats remain visible and must not be hidden by later status documents:

- RR-003 is valid, but its fallback coverage baseline recorded `0.0` because full test collection had pre-existing blockers.
- RR-006 is valid, but its evidence PR merged with only the required branch-protection check blocking; other non-required checks were red.
- RR-016 is valid, but one captured git-state caveat was preserved for historical transparency.
- KG-8 is valid, but one non-required GitHub Actions job failed because the runner called `pytest` directly and it was not on `PATH`.
- PRD-0.0 introduced the production-readiness stream and blocked PRD-1 until PRD-0.10 closure.

## Documentation truth boundary

This file is not a production approval. It is a current-state navigation document. Release, deployment, billing, public beta, live learner traffic, or optimisation-execution decisions must be made through future PRD gates and evidence commands.

**Current-state refresh recorded: PRD-0.1**
