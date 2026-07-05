---
title: EduBoost Documentation Index
status: active
owner: documentation-governance
reviewers: [engineering, product, privacy, security, operations]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-06-22
review_interval_days: 30
evidence_command: make docs-housekeeping-check
code_anchors: [docs/documentation/source_of_truth.yml]
---

# EduBoost Documentation Index

This directory contains the curated documentation for EduBoost V2.

EduBoost is a South African Grade 4 Mathematics learning platform with a FastAPI V2 backend, Next.js frontend, PostgreSQL/Alembic persistence, Redis-backed operational services, CAPS-aligned curriculum workflows, Content Factory tooling, POPIA controls, learner diagnostics, parent/guardian visibility, study planning, and release evidence automation.

## Canonical documentation map

The source-of-truth register is:

- [`docs/documentation/source_of_truth.yml`](documentation/source_of_truth.yml)

Use that register to decide which document is current for a topic. Documents outside the register may still be useful, but they are not automatically authoritative.

## Active documentation sections

| Section | Purpose |
|---|---|
| [`current_state.md`](current_state.md) | Current project state, limitations, blockers, and evidence boundaries. |
| [`product/`](product/) | Product scope, learner/guardian/curriculum capabilities, beta boundaries. |
| [`architecture/`](architecture/) | Runtime architecture, boundaries, and key decisions. |
| [`engineering/`](engineering/) | Local development, testing, CI, contribution standards. |
| [`api/`](api/) | API contracts, OpenAPI ownership, client compatibility. |
| [`compliance/`](compliance/) | POPIA, privacy, legal, consent, rights workflows. |
| [`security/`](security/) | Security posture, threat model, operational security. |
| [`operations/`](operations/) | Runbooks, deployment, monitoring, incident handling. |
| [`release/current/`](release/current/) | Current release decision and evidence index summary. |
| [`generated/`](generated/) | Generated indexes and machine-readable reports. |
| [`archive/`](archive/) | Historical, superseded, migrated, or non-authoritative documents. |
| [`documentation/`](documentation/) | Documentation governance policies, manifests, and checks. |

## Rule of thumb

If a document makes a claim about current architecture, readiness, compliance, testing, deployment, or release status, it must either be listed as canonical in `source_of_truth.yml` or clearly marked as generated, evidence, draft, archived, or superseded.

<!-- KG000_FORMAL_ROADMAP_APPROVAL:start -->
## Knowledge graph learning-state roadmap

The Knowledge Graph learning-state roadmap is opened after final RR closure and is governed by:

- [Knowledge Graph Learning-State Architecture](architecture/knowledge_graph_learning_state_architecture.md)
- [Knowledge Graph Data Model](architecture/knowledge_graph_data_model.md)
- [KG Implementation Roadmap](roadmap/knowledge_graph/kg_implementation_roadmap.md)
- [KG-0 Formal KG Roadmap Approval](roadmap/knowledge_graph/kg_000_formal_kg_roadmap_approval.md)
<!-- KG000_FORMAL_ROADMAP_APPROVAL:end -->
