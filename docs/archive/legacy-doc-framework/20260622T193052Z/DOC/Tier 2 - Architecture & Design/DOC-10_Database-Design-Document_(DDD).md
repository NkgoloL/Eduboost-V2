# Database Design Document (DDD)

| Field | Value |
|---|---|
| Document ID | EDB-DDD-010 |
| Product | EduBoost SA / EduBoost V2 |
| Version | 2.0 aligned baseline |
| Generated | 2026-06-22 |
| Status | Aligned baseline draft |
| Classification | Internal - controlled |
| Replacement note | Replaces stale DBE policy-advisory content previously found in `docs/DOC` |

## Authoritative project baseline

This document is aligned to the EduBoost V2 repository supplied on 2026-06-22. It replaces the prior `docs/DOC` material that described a different DBE policy-advisory system.

| Area | Current baseline |
|---|---|
| Product | EduBoost SA, a CAPS-aligned adaptive learning platform for South African primary learners |
| Active backend | `app/api_v2.py` FastAPI modular monolith, mounted under `/api/v2` and `/v2` |
| Frontend | `app/frontend`, package `eduboost-sa-frontend`, Next.js `16.2.7`, React `18.3.1`, TypeScript `5.4.5` |
| Package manager | pnpm `9.14.4` for frontend |
| Python runtime | Python `3.12.3` |
| Persistence | PostgreSQL via SQLAlchemy/Alembic; 44 Alembic revision files in the supplied archive |
| Queue/cache | Redis and ARQ worker path (`app.modules.jobs.WorkerSettings`); V2 should not introduce Celery/RabbitMQ for new work |
| Launch curriculum scope | `grade4_mathematics_en`: CAPS refs 4.M.1.1, 4.M.1.2, 4.M.1.3 |
| Content targets | 40 approved diagnostic items, 8 approved lessons, 1 assessment blueprint, and 1 study-plan template per launch CAPS ref |
| API surface | 205 route handlers discovered by static router scan, plus health/readiness/metrics root routes |
| Tests | 767 backend test files and approximately 44 frontend test/spec files in the archive |
| Workflows | 44 GitHub Actions workflow files |

### Claim discipline

Unless fresh CI, staging, backup/restore, security, POPIA and release evidence is attached, these documents describe the current implementation and target operating model. They must not be used to claim that the system is production-ready.

## Database baseline

The supplied codebase uses PostgreSQL through SQLAlchemy ORM models and Alembic migrations. SQLite may appear in tests or local utility contexts, but PostgreSQL is the operational persistence baseline.

## ORM table inventory from static scan

| Model | Table | Source |
|---|---|---|
| `Guardian` | `guardians` | `app/models/__init__.py` |
| `LearnerProfile` | `learner_profiles` | `app/models/__init__.py` |
| `ParentalConsent` | `parental_consents` | `app/models/__init__.py` |
| `ConsentVersionHistory` | `consent_version_history` | `app/models/__init__.py` |
| `ErasureRequest` | `erasure_request` | `app/models/__init__.py` |
| `AuditEvent` | `audit_events` | `app/models/__init__.py` |
| `IRTItem` | `irt_items` | `app/models/__init__.py` |
| `DiagnosticSession` | `diagnostic_sessions` | `app/models/__init__.py` |
| `KnowledgeGap` | `knowledge_gaps` | `app/models/__init__.py` |
| `SubjectMastery` | `subject_mastery` | `app/models/__init__.py` |
| `TopicMastery` | `topic_mastery` | `app/models/__init__.py` |
| `MasterySnapshot` | `mastery_snapshots` | `app/models/__init__.py` |
| `PracticeQueue` | `practice_queue` | `app/models/__init__.py` |
| `SpacedReviewSchedule` | `spaced_review_schedule` | `app/models/__init__.py` |
| `PracticeSession` | `practice_sessions` | `app/models/__init__.py` |
| `CalibrationAudit` | `calibration_audits` | `app/models/__init__.py` |
| `Lesson` | `lessons` | `app/models/__init__.py` |
| `LessonFeedback` | `lesson_feedback` | `app/models/__init__.py` |
| `RLHFExport` | `rlhf_exports` | `app/models/__init__.py` |
| `AuditLog` | `audit_logs` | `app/models/__init__.py` |
| `StripeWebhookEvent` | `stripe_webhook_events` | `app/models/__init__.py` |
| `AIBudgetCounter` | `ai_budget_counters` | `app/models/ai_operations.py` |
| `AIUsageReservation` | `ai_usage_reservations` | `app/models/ai_operations.py` |
| `AIUsageEvent` | `ai_usage_events` | `app/models/ai_operations.py` |
| `SecureToken` | `secure_tokens` | `app/models/auth_extensions.py` |
| `OnboardingState` | `onboarding_states` | `app/models/auth_extensions.py` |
| `PrivacySettings` | `privacy_settings` | `app/models/auth_extensions.py` |
| `ContentScope` | `content_scopes` | `app/models/content_factory.py` |
| `ContentCoverageTarget` | `content_coverage_targets` | `app/models/content_factory.py` |
| `ContentGenerationRun` | `content_generation_runs` | `app/models/content_factory.py` |
| `ContentGenerationTask` | `content_generation_tasks` | `app/models/content_factory.py` |
| `ContentGenerationArtifact` | `content_generation_artifacts` | `app/models/content_factory.py` |
| `ContentArtifactSource` | `content_artifact_sources` | `app/models/content_factory.py` |
| `ContentValidationReport` | `content_validation_reports` | `app/models/content_factory.py` |
| `ContentAnswerKeyVerification` | `content_answer_key_verifications` | `app/models/content_factory.py` |
| `ContentArtifactReview` | `content_artifact_reviews` | `app/models/content_factory.py` |
| `ContentReviewAssignment` | `content_review_assignments` | `app/models/content_factory.py` |
| `ContentReviewDecision` | `content_review_decisions` | `app/models/content_factory.py` |
| `ContentStateTransitionEvent` | `content_state_transition_events` | `app/models/content_factory.py` |
| `ContentSeedRun` | `content_seed_runs` | `app/models/content_factory.py` |
| `ContentStagingVerificationRun` | `content_staging_verification_runs` | `app/models/content_factory.py` |
| `ContentStagingVerificationScopeResult` | `content_staging_verification_scope_results` | `app/models/content_factory.py` |
| `ContentPromotionEvent` | `content_promotion_events` | `app/models/content_factory.py` |
| `LessonBank` | `lesson_bank` | `app/models/content_factory.py` |
| `AssessmentBlueprint` | `assessment_blueprints` | `app/models/content_factory.py` |
| `StudyPlanTemplate` | `study_plan_templates` | `app/models/content_factory.py` |
| `ContentStagingSeedItem` | `content_staging_seed_items` | `app/models/content_factory.py` |
| `ContentStagingArtifact` | `content_staging_artifacts` | `app/models/content_factory.py` |
| `ContentProductionArtifact` | `content_production_artifacts` | `app/models/content_factory.py` |
| `CurriculumSource` | `curriculum_sources` | `app/models/curriculum_authority.py` |
| `CurriculumSourceVersion` | `curriculum_source_versions` | `app/models/curriculum_authority.py` |
| `CurriculumRightsDecision` | `curriculum_rights_decisions` | `app/models/curriculum_authority.py` |
| `CurriculumInventoryVersion` | `curriculum_inventory_versions` | `app/models/curriculum_authority.py` |
| `CurriculumInventoryItem` | `curriculum_inventory_items` | `app/models/curriculum_authority.py` |
| `CurriculumReviewDecision` | `curriculum_review_decisions` | `app/models/curriculum_authority.py` |
| `CurriculumCoverageSnapshot` | `curriculum_coverage_snapshots` | `app/models/curriculum_expansion.py` |
| `CurriculumExpansionRun` | `curriculum_expansion_runs` | `app/models/curriculum_expansion.py` |
| `TrainingDatasetManifest` | `training_dataset_manifests` | `app/models/curriculum_expansion.py` |
| `TrainingDatasetEntry` | `training_dataset_entries` | `app/models/curriculum_expansion.py` |
| `CurriculumSourceAcquisitionRun` | `curriculum_source_acquisition_runs` | `app/models/curriculum_grounding.py` |
| `CurriculumOriginalObject` | `curriculum_original_objects` | `app/models/curriculum_grounding.py` |
| `CurriculumExtractionRun` | `curriculum_extraction_runs` | `app/models/curriculum_grounding.py` |
| `CurriculumSourcePage` | `curriculum_source_pages` | `app/models/curriculum_grounding.py` |
| `CurriculumSourceSection` | `curriculum_source_sections` | `app/models/curriculum_grounding.py` |
| `CurriculumChunkVersion` | `curriculum_chunk_versions` | `app/models/curriculum_grounding.py` |
| `CurriculumGraphNode` | `curriculum_graph_nodes` | `app/models/curriculum_grounding.py` |
| `CurriculumMappingVersion` | `curriculum_mapping_versions` | `app/models/curriculum_grounding.py` |
| `CurriculumCorpusVersion` | `curriculum_corpus_versions` | `app/models/curriculum_grounding.py` |
| `CurriculumCorpusMembership` | `curriculum_corpus_memberships` | `app/models/curriculum_grounding.py` |
| `CurriculumCorpusActivationEvent` | `curriculum_corpus_activation_events` | `app/models/curriculum_grounding.py` |
| `CurriculumCorpusActiveBinding` | `curriculum_corpus_active_bindings` | `app/models/curriculum_grounding.py` |
| `CurriculumCorpusOutboxEvent` | `curriculum_corpus_outbox_events` | `app/models/curriculum_grounding.py` |
| `CurriculumGenerationGroundingRecord` | `curriculum_generation_grounding_records` | `app/models/curriculum_grounding.py` |
| `CurriculumClaimValidationRecord` | `curriculum_claim_validation_records` | `app/models/curriculum_grounding.py` |
| `CurriculumAnswerVerificationRecord` | `curriculum_answer_verification_records` | `app/models/curriculum_grounding.py` |
| `TutorGroundingRecord` | `tutor_grounding_records` | `app/models/curriculum_grounding.py` |
| `CurriculumLegacyDisposition` | `curriculum_legacy_dispositions` | `app/models/curriculum_grounding.py` |
| `CurriculumRetrievalEvaluationRun` | `curriculum_retrieval_evaluation_runs` | `app/models/curriculum_grounding.py` |
| `CurriculumRetrievalEvaluationCase` | `curriculum_retrieval_evaluation_cases` | `app/models/curriculum_grounding.py` |
| `Phase02RAuditFinding` | `phase02r_audit_findings` | `app/models/curriculum_grounding.py` |
| `DiagnosticItem` | `diagnostic_items` | `app/models/diagnostic_item.py` |
| `IRTCalibrationRun` | `irt_calibration_runs` | `app/models/irt_quality.py` |
| `IRTCalibrationEvent` | `irt_calibration_events` | `app/models/irt_quality.py` |
| `ItemExposure` | `item_exposures` | `app/models/item_exposure.py` |
| `RetrievalSourceDocument` | `retrieval_source_documents` | `app/models/retrieval.py` |
| `RetrievalSourceChunk` | `retrieval_source_chunks` | `app/models/retrieval.py` |
| `TutorSession` | `tutor_sessions` | `app/models/tutor.py` |
| `TutorMessage` | `tutor_messages` | `app/models/tutor.py` |
| `TutorEscalation` | `tutor_escalations` | `app/models/tutor.py` |

## Migration controls

| Control | Purpose |
|---|---|
| `alembic/versions/` | Versioned schema changes. |
| `scripts/verify_migration_graph.py` | Detects migration graph issues and multiple heads. |
| `scripts/validate_schema_integrity.py` | Validates model/migration schema integrity. |
| `alembic heads` | Confirms current migration head count. |

## Data design principles

- Learner, guardian, consent, diagnostic, mastery, lesson, feedback and audit data must remain relational and auditable.
- Content Factory governance data must capture provenance, review, verification, staging and promotion history.
- POPIA erasure must respect retention/legal constraints and record action evidence.
- Generated content artifacts are not automatically trusted; approval state controls learner-facing exposure.

## Source-of-truth references

- Runtime entrypoint: `app/api_v2.py`
- Backend routers: `app/api_v2_routers/` and `app/modules/practice/router.py`
- Domain contracts: `app/domain/`
- Persistence models: `app/models/`, `app/repositories/`, `alembic/versions/`
- Content Factory: `app/services/content_factory*.py`, `app/api_v2_routers/content_factory.py`, `data/content_factory/`
- Diagnostics and IRT: `app/services/diagnostic*.py`, `app/api_v2_routers/diagnostics.py`, `app/api_v2_routers/irt_quality.py`
- Parent portal and POPIA: `app/api_v2_routers/parents.py`, `app/api_v2_routers/popia.py`, `app/services/popia_service.py`
- Frontend: `app/frontend/package.json`, `app/frontend/src/`
- Operations: `docker-compose.yml`, `docker-compose.prod.yml`, `.github/workflows/`, `docs/operations/`

## Standard verification gate

Run the closest applicable subset before accepting a document-controlled change:

```bash
python3 -m compileall -q app scripts
python3 -m ruff check app tests scripts --select E9,F63,F7,F82,F821
python3 scripts/verify_migration_graph.py
python3 scripts/validate_schema_integrity.py
python3 scripts/check_runtime_entrypoints.py
python3 scripts/generate_openapi.py --check
python3 scripts/generate_route_inventory.py --check
make test-fast
cd app/frontend && pnpm run env-check && pnpm run lint && pnpm run type-check && pnpm run test
```

For release claims add integration tests, Docker Compose validation, staging smoke tests, Playwright E2E, backup/restore proof, rollback proof, and security/POPIA evidence.
