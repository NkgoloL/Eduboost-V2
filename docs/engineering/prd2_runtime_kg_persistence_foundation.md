# PRD-2 Runtime KG Persistence Foundation

This document records the first PRD-2 implementation bundle.  It moves the
knowledge-graph pivot from evidence-only artifacts toward runtime application
plumbing while keeping learner-facing rollout behind a disabled-by-default
feature flag.

## Implemented in PRD-2.0-2.3

- Runtime KG persistence tables and Alembic migration.
- SQLAlchemy models for runtime graph loads, nodes, edges, learner node states,
  and append-only runtime KG events.
- Idempotent graph-load validation and repository boundary.
- Deterministic learner projection service for diagnostic evidence.
- Runtime lesson-context hook behind `EDUBOOST_RUNTIME_KG_ENABLED`.
- Study-plan focus helper that consumes runtime KG gaps when available.
- Rollback-safe default: legacy behaviour remains active unless the feature flag
  is explicitly enabled and an active graph version is present.

## Deferred

- Production graph data loading from reviewed CAPS artifacts.
- Full route-level diagnostic write integration.
- Parent dashboard graph visualisation.
- Performance/index tuning under PRD-8.
- Live learner activation under PRD-10.

## Rollback

Unset `EDUBOOST_RUNTIME_KG_ENABLED` or set it to `false`. The lesson context hook
falls back to the existing `KnowledgeGap` query path, and no public route needs to
change.
