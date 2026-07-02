---
title: "ADR-035 — Supabase versus Raw Postgres Product Quality Gate"
status: proposed
owner: architecture
reviewers: [engineering, architecture, operations]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-02
review_interval_days: 180
evidence_command: "PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_rr007_product_quality_gates.py --json"
code_anchors: []
---
# ADR-035 — Supabase versus Raw Postgres Product Quality Gate

Supabase versus raw Postgres decision recorded: true

## Status

Proposed / pending final architecture approval.

## Context

EduBoost currently uses PostgreSQL directly for canonical application persistence while some workflows and local testing have used Supabase-oriented conventions. Product-quality gates need a stable decision record so authentication, migrations, observability, backup/restore, and learner data handling are not split across ungoverned database assumptions.

## Decision

For RR-007, record the decision boundary rather than changing infrastructure:

1. PostgreSQL remains the canonical application database until a later ADR changes this.
2. Supabase-specific behaviour must be isolated behind adapters or explicit environment profiles.
3. Migrations remain Alembic-governed unless a later migration authority changes this.
4. Product quality evidence must state which database profile was used.
5. No production deployment or public beta is authorised by this ADR.

## Consequences

- Quality gates can distinguish local Supabase-backed tests from canonical PostgreSQL release expectations.
- Future work can choose Supabase services deliberately, but not implicitly.
- Runtime KG implementation remains out of scope.
