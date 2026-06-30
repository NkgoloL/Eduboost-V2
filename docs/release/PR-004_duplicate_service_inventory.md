# PR-004 Duplicate Service Inventory

**Date:** 2026-06-01
**Phase:** Phase 4 - Duplicate Service Cleanup

---

## Known Duplicates (from Audit)

### 1. AuthService
| Location | Type | Status | Action |
|----------|------|--------|--------|
| `app/services/auth_service.py` | SQLAlchemy | Duplicate | Archive |
| `app/modules/auth/service.py` | SQLAlchemy | Canonical | Keep |

**Rationale:** `app/modules/auth/service.py` is canonical (module pattern, co-located with other module services)

### 2. ConsentService
| Location | Type | Status | Action | Notes |
|----------|------|--------|--------|-------|
| `app/services/consent_service.py` | asyncpg-style | Duplicate | Archive | Incompatible with SQLAlchemy |
| `app/modules/consent/service.py` | SQLAlchemy | Canonical | Keep | Used by V2 routers via adapter |

**Rationale:** `app/modules/consent/service.py` is canonical (SQLAlchemy, versioning support, audit integration)

### 3. LessonService
| Location | Type | Status | Action | Notes |
|----------|------|--------|--------|-------|
| `app/services/lesson_service_v2.py` | SQLAlchemy | Duplicate | Archive | V2 naming suggests legacy |
| `app/modules/lessons/service.py` | SQLAlchemy | Canonical | Keep | Module pattern |

**Rationale:** `app/modules/lessons/service.py` is canonical (module pattern)

### 4. DiagnosticSessionService
| Location | Type | Status | Action | Notes |
|----------|------|--------|--------|-------|
| `app/services/diagnostic_session_service.py` | SQLAlchemy | Duplicate | Archive | V2 naming suggests legacy |
| `app/modules/diagnostics/diagnostic_session_service.py` | SQLAlchemy | Canonical | Keep | Module pattern |

**Rationale:** `app/modules/diagnostics/diagnostic_session_service.py` is canonical (module pattern)

### 5. EtherService
| Location | Type | Status | Action | Notes |
|----------|------|--------|--------|-------|
| `app/services/ether_service.py` | SQLAlchemy | Duplicate | Archive | V2 naming suggests legacy |
| `app/modules/learners/ether_service.py` | SQLAlchemy | Canonical | Keep | Module pattern |

**Rationale:** `app/modules/learners/ether_service.py` is canonical (module pattern)

### 6. StripeService
| Location | Type | Status | Action | Notes |
|----------|------|--------|--------|-------|
| `app/services/stripe_service.py` | Wrapper | Duplicate | Archive | Wraps _StripeService |
| `app/core/stripe_client.py` | Wrapper | Canonical | Keep | Core location |

**Rationale:** `app/core/stripe_client.py` is canonical (core infrastructure)

### 7. AuditRepository
| Location | Type | Status | Action | Notes |
|----------|------|--------|--------|-------|
| `app/repositories/audit_repository.py` | Dedicated | Duplicate | Archive | Standalone |
| `app/repositories/repositories.py` | Aggregate | Canonical | Keep | Aggregate pattern |

**Rationale:** `app/repositories/repositories.py` is canonical (aggregate repository pattern)

### 8. ConsentRepository
| Location | Type | Status | Action | Notes |
|----------|------|--------|--------|-------|
| `app/repositories/consent_repository.py` | Dedicated (asyncpg-style) | Duplicate | Archive | Incompatible API |
| `app/repositories/repositories.py` | Aggregate (SQLAlchemy) | Canonical | Keep | Aggregate pattern |

**Rationale:** `app/repositories/repositories.py` is canonical (SQLAlchemy, aggregate pattern)

---

## Additional Services (No Duplicates Found)

The following services appear to be unique and should be kept:

### Core Services
- `app/core/llm_gateway.py:ExecutiveService` - LLM orchestration
- `app/core/audit.py:FourthEstateService` - Audit logging
- `app/core/judiciary.py:JudiciaryService` - Content moderation
- `app/core/stripe_client.py:StripeService` - Stripe payments (canonical)

### Module Services (Canonical Pattern)
- `app/modules/progress/progress_timeline_service.py:ProgressTimelineService`
- `app/modules/progress/learning_velocity_service.py:LearningVelocityService`
- `app/modules/diagnostics/session_recovery_service.py:SessionRecoveryService`
- `app/modules/diagnostics/item_bank_service.py:ItemBankService`
- `app/modules/diagnostics/termination_service.py:TerminationService`
- `app/modules/diagnostics/calibration_service.py:CalibrationService`
- `app/modules/diagnostics/item_selection_service.py:ItemSelectionService`
- `app/modules/diagnostics/service.py:ConsentService` (diagnostic-specific consent checks)
- `app/modules/lessons/caps_topic_map_service.py:CAPSTopicMapService`

### V2 Services (To Evaluate)
- `app/services/parent_report_service_v2.py:ParentReportServiceV2`
- `app/services/gamification_service_v2.py:GamificationServiceV2`
- `app/services/system_service_v2.py:SystemServiceV2`
- `app/services/study_plan_service_v2.py:StudyPlanServiceV2`
- `app/services/assessment_service_v2.py:AssessmentServiceV2`
- `app/services/diagnostic_service_v2.py:DiagnosticServiceV2`

**Note:** V2 services may be canonical for their domains. Need to evaluate each.

### Other Services (Unique)
- `app/services/consent_renewal_service.py:ConsentRenewalService`
- `app/services/consent_expiry_service.py:ConsentExpiryService`
- `app/services/content_learner_read_service.py:ContentLearnerReadService`
- `app/services/rlhf_service.py:RLHFService`
- `app/services/learner_service.py:LearnerService`
- `app/services/popia_service.py:POPIADataRightsService`
- `app/services/subscription_service.py:SubscriptionService`
- `app/services/data_subject_rights_service.py:DataSubjectRightsService`
- `app/services/audit_service.py:AuditService`
- `app/services/content_coverage_service.py:ContentCoverageService`
- `app/services/quota_service.py:QuotaService`
- `app/services/quota_service.py:SemanticCacheService`
- `app/services/email_service.py:EmailService`
- `app/services/telemetry.py:TelemetryService`

### Transactional Services (Proof/Testing)
- `app/services/lesson_transactional_completion.py:TransactionalLessonCompletionService`
- `app/services/auth_transactional_registration.py:TransactionalAuthRegistrationService`
- `app/services/popia_transactional_lifecycle.py:TransactionalPOPIAConsentLifecycleService`
- `app/services/diagnostic_transactional_response.py:TransactionalDiagnosticResponseService`
- `app/services/auth_db_lifecycle_proof.py:AuthDBProofApplicationService`

**Note:** These are proof/testing services and should be kept for test fixtures.

### Content Services (Content Factory)
- `app/services/content_factory.py:ETLProvenanceService`
- `app/services/content_factory.py:ContentValidationService`
- `app/services/content_factory.py:ContentFactoryService`

**Note:** These are part of the content factory pipeline and should be kept.

### Content Review Services
- `app/services/content_review_queue.py:ContentReviewQueueService`
- `app/services/content_review_risk.py:ContentReviewRiskService`
- `app/services/content_staging_read_verification.py:ContentStagingReadVerificationService`
- `app/services/content_production_read_verification.py:ContentProductionReadVerificationService`
- `app/services/content_staging_readiness.py:ContentStagingReadinessService`
- `app/services/content_blueprint_validation.py:AssessmentBlueprintValidationService`
- `app/services/content_template_validation.py:StudyPlanTemplateValidationService`
- `app/services/content_bulk_review.py:ContentBulkReviewService`
- `app/services/content_reviewer_assignment.py:ContentReviewerAssignmentService`
- `app/services/content_staging_preview_service.py:ContentStagingPreviewService`
- `app/services/content_generation/source_context.py:ContentGenerationSourceContextService`
- `app/services/content_seed_promotion.py:ContentSeedPromotionService`
- `app/services/content_generation_runs.py:ContentGenerationRunService`
- `app/services/content_artifact_lifecycle.py:ContentArtifactLifecycleService`

**Note:** These are content workflow services and should be kept.

---

## Migration Plan

### Phase 4a: Archive Duplicates
1. Move `app/services/auth_service.py` to `app/services/archived/auth_service.py`
2. Move `app/services/consent_service.py` to `app/services/archived/consent_service.py`
3. Move `app/services/lesson_service_v2.py` to `app/services/archived/lesson_service_v2.py`
4. Move `app/services/diagnostic_session_service.py` to `app/services/archived/diagnostic_session_service.py`
5. Move `app/services/ether_service.py` to `app/services/archived/ether_service.py`
6. Move `app/services/stripe_service.py` to `app/services/archived/stripe_service.py`
7. Move `app/repositories/audit_repository.py` to `app/repositories/archived/audit_repository.py`
8. Move `app/repositories/consent_repository.py` to `app/repositories/archived/consent_repository.py`

### Phase 4b: Update Imports
1. Search for imports of archived services
2. Update to use canonical services
3. Add import shims if needed for backward compatibility

### Phase 4c: Verify Tests
1. Run test suite to ensure no breakage
2. Fix any failing tests
3. Remove import shims after verification

---

## Risk Assessment

### Low Risk
- Archiving unused services
- Moving to archived/ directory (not deleting)

### Medium Risk
- Import updates may break existing code
- Need to verify all usages

### High Risk
- None identified (archiving is safe)

---

## Success Criteria

1. All duplicate services moved to archived/ directory
2. All imports updated to use canonical services
3. Test suite passes with no regressions
4. No import errors in production code
5. Documentation updated to reflect canonical services

---

**Created:** 2026-06-01
**Status:** Inventory complete, pending migration
