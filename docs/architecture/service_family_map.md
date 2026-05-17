# Service Family Map

Generated at: `2026-05-17T22:07:36Z`

| Domain | Path | Classification | Classes |
|---|---|---|---|
| other | `app/services/ai_safety.py` | unclassified | `ContentQualityScore` |
| assessment | `app/services/assessment_service_v2.py` | duplicate_domain_service | `AssessmentServiceV2` |
| audit | `app/services/audit_canonicalization_registry.py` | unclassified | `AuditMigrationCandidate`, `MigrationStatus` |
| audit | `app/services/audit_canonicalization_slice.py` | unclassified | `CanonicalAuditCommand` |
| audit | `app/services/audit_migration_orchestrator.py` | migration_or_compat_helper | `AuditMigrationEnvelope` |
| audit | `app/services/audit_service.py` | duplicate_domain_service | `AuditService` |
| auth | `app/services/auth_service.py` | duplicate_domain_service | `AuthError`, `AuthService`, `CompatSession`, `CompatSession`, `LoginResult`, `SignupResult` |
| auth | `app/services/auth_token_claims.py` | unclassified | `AuthTokenClaims` |
| other | `app/services/backend_adapter_wiring_service.py` | duplicate_domain_service | `AdapterWiringResult`, `InMemoryAuditSink` |
| other | `app/services/backend_candidate_execution_harness.py` | unclassified | `HarnessResult` |
| other | `app/services/backend_consolidation_runtime.py` | active_runtime_facade | `CanonicalAuditWrite`, `ConstructorProbeResult` |
| other | `app/services/backend_first_wiring_candidates.py` | unclassified | `WiringArea`, `WiringCandidate`, `WiringCandidatePayload` |
| other | `app/services/backend_runtime_integration_readiness.py` | active_runtime_facade | `IntegrationArea`, `RuntimeIntegrationDryRunResult`, `RuntimeIntegrationTarget` |
| other | `app/services/backend_runtime_wiring_cases.py` | active_runtime_facade | `WiringCaseResult` |
| other | `app/services/backend_runtime_wiring_preflight.py` | active_runtime_facade | `PreflightArea`, `RuntimeWiringPreflightResult` |
| other | `app/services/caps_validator.py` | unclassified | `CAPSAlignmentValidator`, `CAPSValidationResult` |
| consent | `app/services/consent.py` | unclassified | - |
| consent | `app/services/consent_compat.py` | migration_or_compat_helper | `ConsentAuditEvent` |
| consent | `app/services/consent_expiry_service.py` | duplicate_domain_service | - |
| consent | `app/services/consent_renewal_service.py` | duplicate_domain_service | `ConsentRecord`, `ConsentRenewalService`, `EmailGateway`, `GuardianRecord`, `SendGridEmailGateway` |
| consent | `app/services/consent_runtime_compatibility.py` | active_runtime_facade | `ConsentRuntimeOperation`, `ConstructorProbe` |
| consent | `app/services/consent_runtime_orchestrator.py` | active_runtime_facade | `ConsentRuntimeCompatibilitySummary` |
| consent | `app/services/consent_service.py` | deprecated_legacy_service | `ConsentService` |
| lesson | `app/services/content_safety/lesson_contracts.py` | unclassified | `LessonOutput`, `LessonValidationResult` |
| other | `app/services/content_safety/pii.py` | unclassified | `PIIFinding` |
| other | `app/services/curriculum/caps_topic_map.py` | unclassified | `CAPSTopic`, `CAPSTopicMap` |
| other | `app/services/curriculum/coverage.py` | unclassified | `CurriculumCoverageAnalyzer`, `CurriculumGap` |
| other | `app/services/data_subject_rights_service.py` | duplicate_domain_service | `DataSubjectRightsService` |
| other | `app/services/deep_readiness_readonly.py` | unclassified | `ReadinessCheckResult`, `ReadinessCheckSpec`, `ReadinessSeverity` |
| other | `app/services/deep_readiness_route_contracts.py` | unclassified | `DeepReadinessRouteCheck`, `ReadinessCheckMode` |
| other | `app/services/deep_readiness_runtime.py` | active_runtime_facade | `DeepReadinessCheckResult`, `DeepReadinessRuntimeResult` |
| diagnostic | `app/services/diagnostic.py` | unclassified | - |
| diagnostic | `app/services/diagnostic_data_integrity.py` | unclassified | `DiagnosticIntegrityError`, `DiagnosticSubmissionIntegrityResult` |
| diagnostic | `app/services/diagnostic_safety.py` | unclassified | `DiagnosticItemValidation`, `DiagnosticItemValidator` |
| diagnostic | `app/services/diagnostic_service_v2.py` | duplicate_domain_service | `DiagnosticServiceV2` |
| diagnostic | `app/services/diagnostic_session_service.py` | duplicate_domain_service | `DiagnosticSessionNotFoundError`, `DiagnosticSessionService` |
| other | `app/services/ether.py` | unclassified | - |
| other | `app/services/ether_service.py` | duplicate_domain_service | `OnboardingResponse` |
| other | `app/services/executive.py` | unclassified | - |
| audit | `app/services/first_audit_runtime_wiring.py` | active_runtime_facade | `FirstAuditRuntimeCandidate`, `FirstAuditRuntimePayload`, `FirstAuditRuntimeRecordResult`, `InMemoryFirstAuditRuntimeSink` |
| consent | `app/services/first_consent_runtime_wiring.py` | active_runtime_facade | `FirstConsentRuntimeCandidate`, `FirstConsentRuntimePayload` |
| other | `app/services/first_deep_readiness_runtime_wiring.py` | active_runtime_facade | `DeepReadinessRuntimePlan`, `FirstDeepReadinessRuntimeCandidate` |
| other | `app/services/fourth_estate.py` | unclassified | - |
| gamification | `app/services/gamification_service_v2.py` | duplicate_domain_service | `GamificationServiceV2`, `_EmptyGamificationRepository` |
| other | `app/services/job_runtime_integrity.py` | active_runtime_facade | `JobRuntimeIntegrityError` |
| other | `app/services/judiciary.py` | unclassified | - |
| learner | `app/services/learner_service.py` | duplicate_domain_service | `LearnerService` |
| auth | `app/services/lesson_authorization.py` | authorization_helper | - |
| lesson | `app/services/lesson_context_builder.py` | unclassified | `LessonContext`, `LessonContextBuilder` |
| lesson | `app/services/lesson_service_v2.py` | duplicate_domain_service | `LessonServiceV2` |
| other | `app/services/llm/gateway.py` | unclassified | `CanonicalLLMGateway`, `DeterministicMockProvider`, `LLMGatewayMetadata`, `LLMGatewayRequest`, `LLMGatewayResponse`, `LLMProvider`, `ProviderHealth`, `ProviderPolicy`, `ProviderResult`, `TokenUsage` |
| other | `app/services/parent_report_service_v2.py` | duplicate_domain_service | `ParentReportServiceV2` |
| other | `app/services/pii_sweep.py` | unclassified | `PIIFinding`, `PIIScanner`, `PIISweepError`, `SweepResult` |
| popia | `app/services/popia_service.py` | duplicate_domain_service | `POPIADataRightsService`, `RightsRequestStatus` |
| other | `app/services/quota_service.py` | duplicate_domain_service | `QuotaExceededError`, `QuotaService`, `SemanticCacheService` |
| other | `app/services/rlhf_service.py` | duplicate_domain_service | `RLHFService` |
| audit | `app/services/runtime_audit_facade.py` | active_runtime_facade | `AuditRecordRepository`, `RuntimeAuditRecord` |
| consent | `app/services/runtime_consent_facade.py` | active_runtime_facade | `ConsentRuntimeEmission` |
| other | `app/services/stripe_service.py` | duplicate_domain_service | `StripeService` |
| other | `app/services/study_plan_service_v2.py` | duplicate_domain_service | `StudyPlanServiceV2`, `_MemoryStudyPlanRepository`, `_MissingLearnerRepository` |
| other | `app/services/study_plan_updater.py` | unclassified | `StudyPlanUpdater` |
| other | `app/services/subscription_service.py` | duplicate_domain_service | `SubscriptionService` |
| other | `app/services/system_service_v2.py` | duplicate_domain_service | `SystemServiceV2` |
| other | `app/services/telemetry.py` | unclassified | `TelemetryService` |
| auth | `app/modules/auth/service.py` | canonical_domain_service | `AuthService` |
| other | `app/modules/beta_launch/production_readiness_contracts.py` | unclassified | `AcceptanceStatus`, `BetaCohortPlan`, `BetaEntryCriterion`, `BetaExitCriterion`, `BetaLaunchDecision`, `BetaStage`, `FeedbackIntakeRule`, `FeedbackSeverity`, `KnownIssue`, `LaunchDecision`, `LaunchReadinessReview`, `ProductScopeArea`, `ProductScopeItem`, `StagingAcceptanceCriterion` |
| billing | `app/modules/billing/production_readiness_contracts.py` | unclassified | `BillingAuditEvent`, `BillingPlan`, `BillingProvider`, `BillingProviderDecision`, `PricingPolicy`, `SubscriptionSnapshot`, `SubscriptionState`, `WebhookIdempotencyStore`, `WebhookRetryPolicy` |
| consent | `app/modules/consent/service.py` | canonical_domain_service | `ConsentService` |
| other | `app/modules/deployment/production_readiness_contracts.py` | unclassified | `ArtifactProvenance`, `DeploymentGate`, `DeploymentStrategy`, `DockerImageContract`, `EnvironmentContract`, `EnvironmentName`, `InfrastructureProviderDecision`, `PipelineCheck`, `PipelineStage`, `RollbackContract`, `RuntimeRole` |
| diagnostic | `app/modules/diagnostics/bias_review_router.py` | unclassified | `BiasReviewRequest` |
| diagnostic | `app/modules/diagnostics/calibration_service.py` | canonical_domain_service | `CalibrationResult`, `CalibrationService` |
| diagnostic | `app/modules/diagnostics/diagnostic_session_service.py` | canonical_domain_service | `DiagnosticResponseResult`, `DiagnosticSessionService` |
| diagnostic | `app/modules/diagnostics/irt_engine.py` | unclassified | `DiagnosticEngine`, `DiagnosticSessionState`, `IRTEngine`, `IrtParameterError`, `_ItemProxy` |
| diagnostic | `app/modules/diagnostics/irt_params.py` | unclassified | - |
| diagnostic | `app/modules/diagnostics/item_bank_pipeline.py` | unclassified | `ItemBankPipeline` |
| diagnostic | `app/modules/diagnostics/item_bank_service.py` | canonical_domain_service | `ItemBankService`, `ItemSelectionError` |
| diagnostic | `app/modules/diagnostics/item_generator.py` | unclassified | `AnswerKeyMismatchError`, `ItemGenerationError`, `ItemGenerator` |
| diagnostic | `app/modules/diagnostics/item_selection_service.py` | canonical_domain_service | `ItemSelectionService`, `SelectionResult` |
| diagnostic | `app/modules/diagnostics/item_validator.py` | unclassified | `ItemValidator`, `ValidationError` |
| diagnostic | `app/modules/diagnostics/production_readiness_contracts.py` | unclassified | `BiasDimension`, `DiagnosticItemSpec`, `ItemReviewStatus` |
| diagnostic | `app/modules/diagnostics/quality_scorer.py` | unclassified | `QualityScorer` |
| diagnostic | `app/modules/diagnostics/service.py` | canonical_domain_service | `ConsentService` |
| diagnostic | `app/modules/diagnostics/session_recovery_service.py` | canonical_domain_service | `DiagnosticSessionSnapshot`, `SessionRecoveryService`, `_MemoryRedis` |
| diagnostic | `app/modules/diagnostics/termination_service.py` | canonical_domain_service | `TerminationDecision`, `TerminationService` |
| other | `app/modules/disaster_recovery/production_readiness_contracts.py` | unclassified | `BackupFrequency`, `BackupManifestEntry`, `BackupPolicy`, `BackupProviderDecision`, `BackupScope`, `DisasterRecoveryPlan`, `DrillOutcome`, `RecoveryObjective`, `RecoveryTier`, `RestoreDrillEvidence`, `RestoreEnvironment`, `RestoreRunbook` |
| other | `app/modules/documentation_governance/production_readiness_contracts.py` | unclassified | `AdrRecord`, `AdrStatus`, `ClaimConfidence`, `ClaimDisciplineRule`, `ClaimRecord`, `ClaimType`, `DocumentationAudience`, `DocumentationGovernanceDecision`, `DocumentationInventoryEntry`, `DocumentationReviewGate`, `DocumentationStatus`, `ReleaseNoteEntry`, `ReleaseNoteType`, `StaleDocumentationFinding` |
| other | `app/modules/final_release_blockers/production_readiness_contracts.py` | unclassified | `BlockerSeverity`, `BlockerStatus`, `ExternalManualDependency`, `FinalDecision`, `FinalGoNoGoChecklist`, `FinalReleaseBlockerDecision`, `LaunchAuthority`, `ReleaseBlockerClosureRecord`, `ReleaseBlockerDomain`, `ReleaseBlockerDomainSummary`, `ReleaseBlockerItem`, `ReleaseWaiverRule` |
| other | `app/modules/jobs.py` | unclassified | `WorkerSettings` |
| learner | `app/modules/learners/ether_service.py` | canonical_domain_service | `EtherService` |
| lesson | `app/modules/lessons/adaptive_remediation.py` | unclassified | `RemediationPromptConfig`, `RemediationStrategy` |
| lesson | `app/modules/lessons/answer_key_verifier.py` | unclassified | `AnswerKeyVerifier`, `QuestionVerification`, `VerificationResult` |
| lesson | `app/modules/lessons/budget_guardrails.py` | unclassified | `BudgetConfig`, `BudgetExceededError`, `BudgetGuardrails`, `_InProcessCounter`, `_RedisCounter` |
| lesson | `app/modules/lessons/caps_topic_map_service.py` | canonical_domain_service | `CAPSTopicMap`, `CAPSTopicMapService`, `SubtopicEntry`, `TermEntry`, `TopicEntry`, `TopicMapMeta` |
| lesson | `app/modules/lessons/lesson_coverage_router.py` | unclassified | `CapsRefCoverage`, `CoverageResponse`, `CoverageSummary`, `QualityScoreDistribution` |
| lesson | `app/modules/lessons/lesson_generator.py` | unclassified | `LessonGenerationError`, `LessonGenerator`, `VerificationResult` |
| lesson | `app/modules/lessons/lesson_metrics.py` | unclassified | `LessonMetrics` |
| lesson | `app/modules/lessons/lesson_review_router.py` | unclassified | `CurrentUser`, `LessonReviewRequest`, `QueuedLessonSummary`, `ReviewActionResponse`, `ReviewDecision`, `ReviewQueueResponse`, `UserRole` |
| lesson | `app/modules/lessons/lesson_schema_v1.py` | unclassified | `AnswerKeyEntry`, `DifficultyLevel`, `LLMProvider`, `LessonCreate`, `LessonResponse`, `PracticeQuestion`, `RemediationHint`, `ReviewStatus`, `SafetyClassification`, `SubjectEnum`, `TokenUsage`, `VariantType`, `WorkedExample` |
| lesson | `app/modules/lessons/lesson_validator.py` | unclassified | `LessonValidationError`, `LessonValidator`, `ValidationResult` |
| lesson | `app/modules/lessons/lesson_variants.py` | unclassified | `LessonVariantType`, `VariantPromptConfig` |
| lesson | `app/modules/lessons/llm_gateway.py` | unclassified | `LLMGateway`, `LLMResponse` |
| lesson | `app/modules/lessons/llm_gateway_v2.py` | unclassified | `AnthropicAdapter`, `CircuitBreaker`, `CircuitState`, `GroqAdapter`, `LLMGatewayError`, `LLMGatewayV2`, `ProviderUnavailableError` |
| lesson | `app/modules/lessons/mock_llm_provider.py` | unclassified | `MockLLMProvider`, `MockMode` |
| lesson | `app/modules/lessons/parent_explanation_mode.py` | unclassified | `LearnerSessionPerformance`, `ParentSummaryBullet`, `ParentSummaryGenerationError`, `ParentSummaryRequest`, `ParentSummaryResponse` |
| lesson | `app/modules/lessons/prompt_version_registry.py` | unclassified | `PromptTemplateRegistry` |
| lesson | `app/modules/lessons/service.py` | canonical_domain_service | `LessonService` |
| lesson | `app/modules/lessons/teacher_insight_mode.py` | unclassified | `InterventionGroup`, `LearnerMisconceptionRecord`, `MisconceptionCluster`, `TeacherInsightGenerationError`, `TeacherInsightRequest`, `TeacherInsightResponse` |
| notification | `app/modules/notifications/production_readiness_contracts.py` | unclassified | `CommunicationProviderDecision`, `DeliveryRetryPolicy`, `DeliveryStatus`, `NotificationAudience`, `NotificationAuditEvent`, `NotificationChannel`, `NotificationOutbox`, `NotificationPolicy`, `NotificationPreference`, `NotificationPurpose`, `NotificationRequest`, `NotificationTemplate` |
| other | `app/modules/observability/production_readiness_contracts.py` | unclassified | `AlertRule`, `AlertSeverity`, `DashboardDefinition`, `IncidentRoute`, `LogEventContract`, `MetricDefinition`, `ObservabilityProviderDecision`, `ServiceTier`, `SloDefinition`, `TelemetryRetentionPolicy`, `TelemetrySignal`, `TraceSpanContract` |
| other | `app/modules/operations_support/production_readiness_contracts.py` | unclassified | `CustomerImpact`, `IncidentClassificationRule`, `IncidentRecord`, `IncidentSeverity`, `IncidentStatus`, `OnCallEscalationPolicy`, `OperationalHandoverChecklist`, `OperationalRole`, `OperationalRunbook`, `OperationsSupportDecision`, `PostIncidentReview`, `StatusCommunicationTemplate`, `SupportChannel`, `SupportPriority`, `SupportSla` |
| other | `app/modules/practice/practice_generator.py` | unclassified | `PracticeGenerator` |
| other | `app/modules/practice/router.py` | unclassified | `PracticeResponseRequest`, `PracticeSessionRequest` |
| other | `app/modules/practice/spaced_repetition_scheduler.py` | unclassified | `SpacedRepetitionScheduler`, `SpacedReviewPlan` |
| other | `app/modules/progress/learning_velocity_service.py` | canonical_domain_service | `LearningVelocityService` |
| other | `app/modules/progress/mastery_model.py` | unclassified | `MasteryLabel` |
| other | `app/modules/progress/progress_timeline_service.py` | canonical_domain_service | `ProgressTimelineService` |
| other | `app/modules/quality_gates/production_readiness_contracts.py` | unclassified | `CoverageThreshold`, `DefectSeverity`, `DefectTriageRule`, `EvidenceType`, `QualityGate`, `QualityGateStatus`, `ReleaseChecklist`, `ReleaseEvidenceItem`, `ReleaseStage`, `TestLayer`, `TestSuiteContract`, `TestingStrategyDecision` |
| other | `app/modules/roadmap/production_readiness_contracts.py` | unclassified | `BaselineBoundary`, `BaselineBoundaryItem`, `DeferredScopeItem`, `DependencyType`, `GraduationCriterion`, `PostBaselineRisk`, `PriorityLevel`, `RoadmapCategory`, `RoadmapDependency`, `RoadmapGovernanceDecision`, `RoadmapHorizon`, `RoadmapItem`, `RoadmapReviewCadence`, `RoadmapStatus` |
| other | `app/modules/security_posture/production_readiness_contracts.py` | unclassified | `ControlStatus`, `IncidentSeverity`, `RiskAcceptanceRecord`, `SecretHygieneRule`, `SecurityControl`, `SecurityDomain`, `SecurityIncidentRunbook`, `SecurityPostureDecision`, `SecurityTestContract`, `SecurityTestType`, `SupplyChainControl`, `ThreatCategory`, `ThreatModelEntry`, `VulnerabilityPolicy`, `VulnerabilitySeverity` |
