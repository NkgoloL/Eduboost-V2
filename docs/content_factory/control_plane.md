---
title: "Content Factory Control Plane"
status: active
owner: content-factory
reviewers: [content-factory, curriculum, engineering]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-06-24
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: [app/services/content_factory, data/content_factory, docs/content_factory]
---

# Content Factory Control Plane

The Content Factory control plane coordinates generated content without making generation execution the default behavior.

Core pieces:

- `ContentFactoryService` validates generated artifact payloads and ETL provenance.
- `ContentArtifactLifecycleService` owns artifact status transitions.
- `ContentGenerationRunService` persists run and task ledger state.
- `ContentFactoryOrchestrator` creates deterministic dry-run task plans.
- `ContentSeedPromotionService` verifies coverage and artifact gates before staging or production movement.

Generation execution is disabled unless `CONTENT_FACTORY_GENERATION_ENABLED=true`.
