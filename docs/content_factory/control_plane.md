# Content Factory Control Plane

The Content Factory control plane coordinates generated content without making generation execution the default behavior.

Core pieces:

- `ContentFactoryService` validates generated artifact payloads and ETL provenance.
- `ContentArtifactLifecycleService` owns artifact status transitions.
- `ContentGenerationRunService` persists run and task ledger state.
- `ContentFactoryOrchestrator` creates deterministic dry-run task plans.
- `ContentSeedPromotionService` verifies coverage and artifact gates before staging or production movement.

Generation execution is disabled unless `CONTENT_FACTORY_GENERATION_ENABLED=true`.
