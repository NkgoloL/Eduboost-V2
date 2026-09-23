---
title: "Architecture Documentation"
status: active
owner: architecture
reviewers: [backend, frontend, security, operations]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: '2026-09-22'
review_interval_days: 60
evidence_command: make docs-housekeeping-check
code_anchors:
  - app/core/arq_worker.py
  - app/frontend/package.json
  - docs/roadmap/production_readiness/coverage_contract.json
  - docs/roadmap/production_readiness/prd_4a_longitudinal_educational_validation_register.json
  - docs/roadmap/knowledge_graph/kg_roadmap_closure_record.json
---

# Architecture Documentation

Architecture documents must describe the real EduBoost V2 implementation and must not import stale concepts from unrelated systems.

Canonical architectural claims should be anchored to code paths, OpenAPI generation, migration checks, ADRs, or roadmap/evidence verifiers.

## Current architecture truth

```text
FastAPI V2 backend: active (modular monolith, port 8000)
Background workers: active (Redis 7 + ARQ, app/core/arq_worker.py; no Celery)
Next.js frontend: active (Next.js 16.3.3, React 19, @next/swc, port 3050)
PostgreSQL 16 / Alembic: active consolidated persistence path (DEF-12 append-only triggers)
Coverage contract: 90% floor enforced across product, runtime, governance, advisory classes
Knowledge Graph roadmap: closed through KG-8
Controlled runtime KG authority switch: executed
Longitudinal Educational Validation (LEV): PRD-4A task register active (222 tasks across 15 workstreams)
Production release/deployment/public beta/billing/live learner traffic: not authorised (fail-closed)
```

## Knowledge Graph architecture state

The Knowledge Graph learning-state roadmap is closed. The controlled runtime KG authority switch was authorised and executed through KG-ACT-001 and reviewed through KG-8.

Canonical KG architecture documents include:

- [Architecture Diagram](architecture_diagram.md)
- [Knowledge Graph Learning-State Architecture](knowledge_graph_learning_state_architecture.md)
- [Knowledge Graph Data Model](knowledge_graph_data_model.md)
- [Knowledge Graph Transition Plan](knowledge_graph_transition_plan.md)
- [KG Roadmap Closure Record](../roadmap/knowledge_graph/kg_roadmap_closure_record.json)

No new KG slice is authorised by the closure state. Further KG runtime optimisation, persistence expansion, production release, or live learner traffic must be governed through the production-readiness PRD stream.

## Longitudinal Educational Validation (LEV) Integration

All pedagogical and mastery claims are governed under the **PRD-4A Longitudinal Educational Validation (LEV)** framework:
- 222 tasks across 15 workstreams defined in [`docs/roadmap/production_readiness/prd_4a_longitudinal_educational_validation_register.json`](../roadmap/production_readiness/prd_4a_longitudinal_educational_validation_register.json).
- Technical execution without errors does not constitute educational validity.
- Mastery confidence is bounded by `MAX_CONFIDENCE_THRESHOLD`, and unvalidated states are explicitly tagged as tentative or inferred.

## Production-readiness architecture boundary

The current authorised work is PRD-11.0R.RUNTIME-RESTORE.EXECUTION-8. Production release,
deployment, public beta, billing, live learner traffic, and new KG slices remain blocked
until their explicit authority gates are satisfied.

Future architecture changes must preserve these boundaries unless explicitly changed by a future PRD gate:

```text
production_release_authorised: false
deployment_authorised: false
release_tag_authorised: false
public_beta_authorised: false
public_beta_live_traffic_authorised: false
billing_launch_authorised: false
live_payment_processing_authorised: false
```

