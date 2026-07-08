# PRD-2.4-2.6 Runtime KG Route Projection Behaviour

This slice integrates the runtime KG foundation into learner-facing backend paths while preserving rollback to legacy behaviour.

Implemented boundaries:

- Diagnostic submission now attempts a feature-flagged runtime KG projection after the legacy diagnostic result and legacy `KnowledgeGap` persistence complete.
- Study-plan job enqueueing includes optional runtime KG focus metadata when persisted learner graph gaps exist.
- Lesson generation continues to use the PRD-2.0-2.3 feature-flagged context hook.
- Runtime KG remains disabled by default through `EDUBOOST_RUNTIME_KG_ENABLED=false`.
- Missing active graphs, unmapped diagnostic items, or disabled flags return explicit legacy fallback metadata instead of failing the request.

This slice does not authorise live learner traffic, production release, deployment, billing, or PRD-3 implementation.
