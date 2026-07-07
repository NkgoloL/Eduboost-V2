---
title: "Architecture Documentation"
status: active
owner: architecture
reviewers: [backend, frontend, security, operations]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-07-07
review_interval_days: 60
evidence_command: PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_prd001_canonical_current_state_documentation_refresh.py --json
code_anchors: [docs/architecture/README.md, docs/roadmap/knowledge_graph/kg_roadmap_closure_record.json]
---

# Architecture Documentation

Architecture documents must describe the real EduBoost V2 implementation and must not import stale concepts from unrelated systems.

Canonical architectural claims should be anchored to code paths, OpenAPI generation, migration checks, ADRs, or roadmap/evidence verifiers.

## Current architecture truth

```text
FastAPI V2 backend: active
Next.js frontend: active
PostgreSQL/Alembic: active persistence path
Redis: configured runtime support where enabled
Knowledge Graph roadmap: closed through KG-8
Controlled runtime KG authority switch: executed
Production release/deployment/public beta/billing/live learner traffic: not authorised
```

## Knowledge Graph architecture state

The Knowledge Graph learning-state roadmap is closed. The controlled runtime KG authority switch was authorised and executed through KG-ACT-001 and reviewed through KG-8.

Canonical KG architecture documents include:

- [Knowledge Graph Learning-State Architecture](knowledge_graph_learning_state_architecture.md)
- [Knowledge Graph Data Model](knowledge_graph_data_model.md)
- [Knowledge Graph Transition Plan](knowledge_graph_transition_plan.md)
- [KG Roadmap Closure Record](../roadmap/knowledge_graph/kg_roadmap_closure_record.json)

No new KG slice is authorised by the closure state. Further KG runtime optimisation, persistence expansion, production release, or live learner traffic must be governed through the production-readiness PRD stream.

## Production-readiness architecture boundary

The current authorised work is PRD-0.1. PRD-1 and later implementation work remain blocked until PRD-0.10 closure.

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
