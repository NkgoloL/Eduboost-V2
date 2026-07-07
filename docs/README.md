---
title: EduBoost Documentation Index
status: active
owner: documentation-governance
reviewers: [engineering, product, privacy, security, operations]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-07-07
review_interval_days: 30
evidence_command: PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_prd001_canonical_current_state_documentation_refresh.py --json
code_anchors: [docs/current_state.md, docs/roadmap/production_readiness/production_readiness_register.json]
---

# EduBoost Documentation Index

This directory contains the curated documentation for EduBoost V2.

EduBoost is a South African Grade 4 Mathematics learning platform with a FastAPI V2 backend, Next.js frontend, PostgreSQL/Alembic persistence, Redis-backed operational services, CAPS-aligned curriculum workflows, controlled Knowledge Graph learning-state authority, POPIA controls, learner diagnostics, parent/guardian visibility, study planning, and release evidence automation.

## Current source-of-truth order

Use these first:

1. [`current_state.md`](current_state.md) — current project truth, closures, active stream, and boundaries.
2. [`roadmap/production_readiness/production_readiness_register.json`](roadmap/production_readiness/production_readiness_register.json) — active PRD-0 and PRD-1+ sequencing.
3. [`roadmap/production_readiness/production_readiness_boundary_contract.md`](roadmap/production_readiness/production_readiness_boundary_contract.md) — authority boundaries.
4. [`documentation/source_of_truth.yml`](documentation/source_of_truth.yml) — documentation governance register.

Documents outside the source-of-truth register may still be useful, but they are not automatically authoritative.

## Active closure state

```text
RR roadmap/TODO register: closed
KG roadmap: closed through KG-8
Controlled runtime KG authority switch: executed
Production-readiness stream: open
Current authorised item: PRD-0.1
PRD-1 implementation: blocked until PRD-0.10 closure
Production release/deployment/public beta/billing/live learner traffic: not authorised
New KG slice: not authorised
```

## Active documentation sections

| Section | Purpose |
|---|---|
| [`current_state.md`](current_state.md) | Current project state, limitations, active stream, and evidence boundaries. |
| [`roadmap/production_readiness/`](roadmap/production_readiness/) | Active production-readiness roadmap and PRD-0 cleanup sequence. |
| [`product/`](product/) | Product scope, learner/guardian/curriculum capabilities, beta boundaries. |
| [`architecture/`](architecture/) | Runtime architecture, KG authority state, boundaries, and key decisions. |
| [`engineering/`](engineering/) | Local development, testing, CI, contribution standards. |
| [`api/`](api/) | API contracts, OpenAPI ownership, client compatibility. |
| [`compliance/`](compliance/) | POPIA, privacy, legal, consent, rights workflows. |
| [`security/`](security/) | Security posture, threat model, operational security. |
| [`operations/`](operations/) | Runbooks, deployment, monitoring, incident handling. |
| [`release/current/`](release/current/) | Current release decision and evidence index summary. |
| [`generated/`](generated/) | Generated indexes and machine-readable reports. |
| [`archive/`](archive/) | Historical, superseded, migrated, or non-authoritative documents. |
| [`documentation/`](documentation/) | Documentation governance policies, manifests, and checks. |

## Knowledge Graph roadmap state

The Knowledge Graph roadmap is closed through KG-8 and its closure report is valid. The controlled runtime KG authority switch was authorised and executed through KG-ACT-001.

No new KG slice is authorised by this state. Further KG optimisation or live-traffic work must come through a future production-readiness gate.

## Rule of thumb

If a document makes a claim about current architecture, readiness, compliance, testing, deployment, release status, KG runtime authority, public beta, billing, or live learner traffic, it must either be listed as canonical in `source_of_truth.yml` or clearly marked as generated, evidence, draft, archived, historical, or superseded.
