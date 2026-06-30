---
title: "Architectural Decision Records (ADR)"
status: active
owner: architecture
reviewers: [engineering, architecture]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 180
evidence_command: make docs-housekeeping-stage3-check
code_anchors: []
---
# Architectural Decision Records (ADR)

This directory contains records of significant architectural decisions made during the development of EduBoost V2.

## ADR index

| ADR | Title | Status |
|---|---|---|
| [ADR-0001](0001-modular-monolith.md) | Modular Monolith Architecture | Accepted |
| [ADR-0002](0002-popia-first-design.md) | POPIA-First Design | Accepted |
| [ADR-0003](0003-llm-provider-abstraction.md) | LLM Provider Abstraction | Accepted |
| [ADR-0004](0004-standardizing-logic.md) | Standardizing Business Logic Location and Naming | Proposed |
| [ADR-0005](0005-fastapi-v2-entrypoint.md) | FastAPI V2 Entrypoint | Accepted |
| [ADR-0006](0006-nextjs-frontend.md) | Next.js Frontend | Accepted |
| [ADR-0007](0007-postgresql-audit-ledger.md) | PostgreSQL Audit Ledger | Proposed |
| [ADR-0008](0008-redis-token-revocation.md) | Redis Token Revocation | Proposed |
| [ADR-0009](0009-caps-alignment.md) | CAPS Alignment | Proposed |

## Status meanings

- **Proposed**: recommended but still open to design review.
- **Accepted**: current architectural direction.
- **Superseded**: replaced by a newer ADR.
- **Deprecated**: no longer recommended but still relevant to historical context.

## Stage 3 ADR numbering rule

ADR numbers in `docs/adr/*.md` must be unique. Stage 3 resolved the prior duplicate root-level `ADR-030` and `ADR-031` numbers by preserving the original decisions and renumbering the later conflicting records to `ADR-033` and `ADR-034`.

Run `make docs-housekeeping-stage3-check` before merging ADR changes.
