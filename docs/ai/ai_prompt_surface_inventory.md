---
title: "AI Prompt Surface Inventory"
status: "current-evidence"
owner: "ai-safety"
reviewers: "[ai-safety, curriculum, privacy]"
audience: "safety-reviewer"
source_of_truth: "false"
supersedes: "[]"
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: "60"
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[app/services, docs/ai]"
---

# AI Prompt Surface Inventory

## Purpose

This inventory records likely prompt construction or AI generation surfaces.

## Required Safety Markers

- CAPS alignment
- learner grade and subject
- consent-authorized learner context
- AI safety boundary instructions
- no cross-learner data leakage

## Discovered Surfaces

| Path | Markers |
| --- | --- |
| `app/api_v2.py` | `diagnostic` |
| `app/api_v2_deps/diagnostic_repositories.py` | `diagnostic` |
| `app/api_v2_routers/api_v2.py` | `diagnostic` |
| `app/api_v2_routers/auth.py` | `remediation` |
| `app/api_v2_routers/auth_extended.py` | `diagnostic` |
| `app/api_v2_routers/content_factory.py` | `llm, diagnostic` |
| `app/api_v2_routers/diagnostics.py` | `diagnostic` |
| `app/api_v2_routers/generation.py` | `prompt, llm, diagnostic` |
| `app/api_v2_routers/irt_quality.py` | `diagnostic` |
| `app/api_v2_routers/learner_content.py` | `diagnostic` |
| `app/api_v2_routers/lessons.py` | `llm, generate_lesson` |
| `app/api_v2_routers/test_services.py` | `prompt, diagnostic` |
| `app/core/analytics.py` | `diagnostic` |
| `app/core/authorization.py` | `generate_lesson, diagnostic` |
| `app/core/config.py` | `llm, anthropic, groq` |
| `app/core/database.py` | `diagnostic` |
| `app/core/degraded_mode.py` | `llm, anthropic, groq` |
| `app/core/exceptions.py` | `llm, remediation` |
| `app/core/health.py` | `llm, anthropic, groq, diagnostic` |
| `app/core/judiciary.py` | `llm, diagnostic` |
| `app/core/llm_gateway.py` | `prompt, llm, anthropic, groq, generate_lesson` |
| `app/core/metrics.py` | `llm, anthropic, groq, diagnostic` |
| `app/core/rate_limit.py` | `llm` |
| `app/domain/ai_operations_schemas.py` | `prompt` |
| `app/domain/api_v2_models.py` | `remediation` |
| `app/domain/consent.py` | `llm, diagnostic` |
| `app/domain/content_coverage.py` | `diagnostic` |
| `app/domain/content_factory_schemas.py` | `prompt, diagnostic` |
| `app/domain/curriculum_expansion_schemas.py` | `diagnostic` |
| `app/domain/item_schema.py` | `llm, diagnostic` |
| `app/domain/lesson.py` | `llm` |
| `app/domain/llm_schemas.py` | `diagnostic` |
| `app/domain/roles.py` | `diagnostic` |
| `app/domain/schemas.py` | `diagnostic` |
| `app/jobs/batch_generation_job.py` | `llm` |
| `app/jobs/irt_quality_job.py` | `diagnostic` |
| `app/models/__init__.py` | `prompt, llm, groq, diagnostic, remediation` |
| `app/models/ai_operations.py` | `prompt` |
| `app/models/auth_extensions.py` | `diagnostic` |
| `app/models/content_factory.py` | `prompt, diagnostic, remediation` |
| `app/models/curriculum_authority.py` | `prompt` |
| `app/models/curriculum_grounding.py` | `prompt` |
| `app/models/diagnostic_item.py` | `llm, diagnostic` |
| `app/models/irt_quality.py` | `diagnostic` |
| `app/models/item_exposure.py` | `diagnostic` |
| `app/models/tutor.py` | `prompt` |
| `app/modules/beta_launch/production_readiness_contracts.py` | `diagnostic` |
| `app/modules/billing/production_readiness_contracts.py` | `llm` |
| `app/modules/deployment/production_readiness_contracts.py` | `llm` |
| `app/modules/diagnostics/__init__.py` | `diagnostic` |
| `app/modules/diagnostics/diagnostic_session_service.py` | `diagnostic` |
| `app/modules/diagnostics/irt_engine.py` | `diagnostic` |
| `app/modules/diagnostics/irt_params.py` | `diagnostic` |
| `app/modules/diagnostics/item_bank_pipeline.py` | `diagnostic` |
| `app/modules/diagnostics/item_bank_service.py` | `diagnostic` |
| `app/modules/diagnostics/item_generator.py` | `prompt, llm, diagnostic` |
| `app/modules/diagnostics/item_selection_service.py` | `diagnostic` |
| `app/modules/diagnostics/item_validator.py` | `diagnostic` |
| `app/modules/diagnostics/production_readiness_contracts.py` | `diagnostic, remediation` |
| `app/modules/diagnostics/quality_scorer.py` | `llm, diagnostic` |
| `app/modules/diagnostics/service.py` | `diagnostic` |
| `app/modules/diagnostics/session_recovery_service.py` | `diagnostic` |
| `app/modules/diagnostics/termination_service.py` | `diagnostic` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | `llm` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | `llm` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | `llm` |
| `app/modules/jobs.py` | `generate_lesson, diagnostic` |
| `app/modules/learners/__init__.py` | `prompt, llm, diagnostic` |
| `app/modules/learners/ether_service.py` | `prompt, llm, diagnostic` |
| `app/modules/lessons/__init__.py` | `llm, anthropic, groq` |
| `app/modules/lessons/adaptive_remediation.py` | `prompt, diagnostic, remediation` |
| `app/modules/lessons/answer_key_verifier.py` | `prompt, llm` |
| `app/modules/lessons/budget_guardrails.py` | `prompt, llm` |
| `app/modules/lessons/caps_topic_map_service.py` | `prompt` |
| `app/modules/lessons/lesson_coverage_router.py` | `llm, diagnostic` |
| `app/modules/lessons/lesson_generator.py` | `prompt, llm, anthropic, groq, diagnostic, remediation` |
| `app/modules/lessons/lesson_metrics.py` | `llm, anthropic, groq` |
| `app/modules/lessons/lesson_review_router.py` | `prompt, llm` |
| `app/modules/lessons/lesson_schema_v1.py` | `prompt, llm, anthropic, groq, remediation` |
| `app/modules/lessons/lesson_validator.py` | `prompt, llm` |
| `app/modules/lessons/lesson_variants.py` | `prompt` |
| `app/modules/lessons/llm_gateway.py` | `prompt, llm, anthropic, groq` |
| `app/modules/lessons/llm_gateway_v2.py` | `prompt, llm, anthropic, groq` |
| `app/modules/lessons/mock_llm_provider.py` | `prompt, llm, remediation` |
| `app/modules/lessons/parent_explanation_mode.py` | `prompt, llm, anthropic, groq, diagnostic` |
| `app/modules/lessons/prompt_version_registry.py` | `prompt, llm` |
| `app/modules/lessons/service.py` | `llm, generate_lesson` |
| `app/modules/lessons/teacher_insight_mode.py` | `prompt, llm, anthropic, groq, diagnostic` |
| `app/modules/observability/production_readiness_contracts.py` | `prompt, llm, diagnostic` |
| `app/modules/practice/practice_generator.py` | `diagnostic` |
| `app/modules/quality_gates/production_readiness_contracts.py` | `llm` |
| `app/modules/roadmap/production_readiness_contracts.py` | `llm, diagnostic` |
| `app/modules/security_posture/production_readiness_contracts.py` | `prompt` |
| `app/repositories/__init__.py` | `diagnostic` |
| `app/repositories/diagnostic_repository.py` | `diagnostic` |
| `app/repositories/diagnostic_session_repository.py` | `diagnostic` |
| `app/repositories/item_bank_repository.py` | `llm, diagnostic` |
| `app/repositories/lesson_repository.py` | `prompt, llm` |
| `app/repositories/practice_session_repository.py` | `remediation` |
| `app/repositories/repositories.py` | `diagnostic` |
| `app/services/ai_operations.py` | `prompt, anthropic, groq` |
| `app/services/backend_consolidation_runtime.py` | `diagnostic` |
| `app/services/batch_generation.py` | `prompt, llm, diagnostic` |
| `app/services/content_answer_key_verification.py` | `diagnostic` |
| `app/services/content_blueprint_validation.py` | `diagnostic` |
| `app/services/content_coverage_service.py` | `diagnostic` |
| `app/services/content_factory.py` | `diagnostic` |
| `app/services/content_factory_orchestrator.py` | `generate_lesson, diagnostic` |
| `app/services/content_file_artifact_import.py` | `prompt, diagnostic` |
| `app/services/content_file_promotion_readiness.py` | `diagnostic` |
| `app/services/content_generation/blueprint_generator.py` | `llm, diagnostic` |
| `app/services/content_generation/diagnostic_generator.py` | `prompt, diagnostic` |
| `app/services/content_generation/generated_item_contract.py` | `diagnostic` |
| `app/services/content_generation/generated_lesson_contract.py` | `prompt` |
| `app/services/content_generation/lesson_generator.py` | `prompt` |
| `app/services/content_generation/prompt_payloads.py` | `prompt, diagnostic` |
| `app/services/content_generation/provider_factory.py` | `llm` |
| `app/services/content_generation/providers/base.py` | `prompt, generate_lesson, diagnostic` |
| `app/services/content_generation/providers/deterministic.py` | `prompt, generate_lesson, diagnostic, remediation` |
| `app/services/content_generation/providers/llm.py` | `prompt, llm, generate_lesson, diagnostic` |
| `app/services/content_generation/scope_blueprint_generator.py` | `diagnostic` |
| `app/services/content_generation/scope_item_generator.py` | `prompt, diagnostic` |
| `app/services/content_generation/scope_lesson_generator.py` | `prompt, remediation` |
| `app/services/content_generation/scope_mcq_templates.py` | `diagnostic` |
| `app/services/content_generation/scope_study_plan_generator.py` | `remediation` |
| `app/services/content_generation/source_context.py` | `prompt` |
| `app/services/content_generation/study_plan_template_generator.py` | `llm, diagnostic, remediation` |
| `app/services/content_generation_executor.py` | `prompt, generate_lesson, diagnostic` |
| `app/services/content_generation_planner.py` | `prompt, diagnostic` |
| `app/services/content_learner_read_service.py` | `diagnostic` |
| `app/services/content_review_governance.py` | `prompt, diagnostic` |
| `app/services/content_review_queue.py` | `prompt` |
| `app/services/content_safety/__init__.py` | `llm` |
| `app/services/content_safety/lesson_contracts.py` | `llm, remediation` |
| `app/services/content_safety/pii.py` | `prompt, llm` |
| `app/services/content_schemas.py` | `llm, diagnostic` |
| `app/services/content_validator.py` | `llm, diagnostic` |
| `app/services/curriculum/corpus.py` | `llm` |
| `app/services/curriculum/coverage.py` | `diagnostic` |
| `app/services/curriculum/extraction.py` | `prompt, llm` |
| `app/services/curriculum/generation.py` | `prompt` |
| `app/services/curriculum/graph.py` | `prompt` |
| `app/services/curriculum/legacy.py` | `diagnostic` |
| `app/services/curriculum/legacy_migration.py` | `diagnostic` |
| `app/services/curriculum/rights_policy.py` | `prompt` |
| `app/services/curriculum/tutor_grounding.py` | `prompt` |
| `app/services/curriculum_expansion.py` | `diagnostic` |
| `app/services/data_subject_rights_service.py` | `prompt, llm, diagnostic` |
| `app/services/diagnostic.py` | `diagnostic` |
| `app/services/diagnostic_data_integrity.py` | `diagnostic` |
| `app/services/diagnostic_route_integrity.py` | `diagnostic` |
| `app/services/diagnostic_safety.py` | `llm, diagnostic` |
| `app/services/diagnostic_scoring_snapshot.py` | `diagnostic` |
| `app/services/diagnostic_service_v2.py` | `diagnostic` |
| `app/services/diagnostic_session_integrity.py` | `diagnostic` |
| `app/services/diagnostic_session_service.py` | `diagnostic` |
| `app/services/diagnostic_transactional_response.py` | `diagnostic` |
| `app/services/etl/etl_pipeline.py` | `remediation` |
| `app/services/etl/etl_pipeline_v2.py` | `llm` |
| `app/services/executive.py` | `llm` |
| `app/services/irt_quality_service.py` | `prompt, diagnostic` |
| `app/services/launch_content_seed.py` | `prompt, llm, diagnostic, remediation` |
| `app/services/learner_tutor.py` | `prompt, llm` |
| `app/services/lesson_context_builder.py` | `prompt, diagnostic, remediation` |
| `app/services/lesson_service_v2.py` | `llm, generate_lesson` |
| `app/services/llm/__init__.py` | `llm` |
| `app/services/llm/gateway.py` | `prompt, llm` |
| `app/services/llm/json_completion.py` | `prompt, llm, anthropic, groq` |
| `app/services/llm_provider.py` | `prompt, llm, anthropic, groq` |
| `app/services/pii_sweep.py` | `anthropic` |
| `app/services/popia_service.py` | `prompt, llm, diagnostic, remediation` |
| `app/services/prompt_registry.py` | `prompt, diagnostic` |
| `app/services/quota_service.py` | `llm` |
| `app/services/rlhf_service.py` | `anthropic` |
| `app/services/safety_filter.py` | `prompt, llm` |
| `app/services/semantic_retrieval/generation_context.py` | `prompt` |
| `app/services/study_plan_updater.py` | `diagnostic, remediation` |
| `app/services/system_service_v2.py` | `diagnostic` |
| `app/services/tutor_safety.py` | `prompt` |
| `scripts/assign_irt_params.py` | `diagnostic` |
| `scripts/audit_baseline_refresh.py` | `llm` |
| `scripts/audit_remediation/backend_fast_failure_report.py` | `prompt, llm, diagnostic, remediation` |
| `scripts/audit_remediation/classify_backend_fast_failures.py` | `diagnostic, remediation` |
| `scripts/audit_remediation/run_backend_fast_category_probe.py` | `remediation` |
| `scripts/audit_remediation/run_backend_fast_gate.py` | `remediation` |
| `scripts/audit_remediation/verify_backend_fast_environment.py` | `llm, anthropic, groq, diagnostic` |
| `scripts/audit_remediation/verify_backend_fast_evidence.py` | `llm, diagnostic` |
| `scripts/audit_remediation/verify_backend_fast_failure_triage.py` | `diagnostic, remediation` |
| `scripts/audit_remediation/verify_backend_fast_gate_preflight.py` | `remediation` |
| `scripts/audit_remediation/verify_backend_fast_phase02d.py` | `remediation` |
| `scripts/audit_remediation/verify_backend_fast_phase02e.py` | `remediation` |
| `scripts/audit_remediation/verify_backend_fast_phase02f.py` | `diagnostic, remediation` |
| `scripts/audit_remediation/verify_backend_fast_phase02g.py` | `remediation` |
| `scripts/audit_remediation/verify_backend_fast_phase02h.py` | `diagnostic, remediation` |
| `scripts/audit_remediation/verify_backend_fast_phase02i.py` | `remediation` |
| `scripts/audit_remediation/verify_backend_fast_phase02k.py` | `remediation` |
| `scripts/audit_remediation/verify_backend_fast_phase02l.py` | `remediation` |
| `scripts/audit_remediation/verify_backend_fast_phase02m.py` | `remediation` |
| `scripts/audit_remediation/verify_backend_fast_phase02n.py` | `diagnostic, remediation` |
| `scripts/audit_remediation/verify_backend_fast_runtime_dependencies.py` | `anthropic, remediation` |
| `scripts/audit_remediation/verify_baseline_reset.py` | `remediation` |
| `scripts/audit_remediation/verify_content_scope_registry_expansion.py` | `diagnostic` |
| `scripts/audit_remediation/verify_openapi_route_contract.py` | `remediation` |
| `scripts/audit_write_flow.py` | `diagnostic` |
| `scripts/audit_write_runtime_evidence.py` | `llm` |
| `scripts/auth_refresh_db_evidence_gate.py` | `llm` |
| `scripts/auth_refresh_db_proof.py` | `llm` |
| `scripts/auto_approve_item_bank.py` | `diagnostic` |
| `scripts/beta_no_go_handoff_packet.py` | `diagnostic` |
| `scripts/build_corrective_caps_v2.py` | `prompt, llm, remediation` |
| `scripts/build_focused_caps_dataset.py` | `remediation` |
| `scripts/build_guardrails_dataset.py` | `remediation` |
| `scripts/check_ai_fixture_coverage_matrix.py` | `prompt, diagnostic` |
| `scripts/check_ai_llm_safety_caps_production_readiness.py` | `prompt, llm, remediation` |
| `scripts/check_ai_output_schema_contract.py` | `prompt, diagnostic` |
| `scripts/check_ai_prompt_input_contract.py` | `prompt, diagnostic` |
| `scripts/check_ai_prompt_secret_leakage.py` | `prompt, system_message, user_message, anthropic, groq, generate_lesson, diagnostic, remediation` |
| `scripts/check_ai_prompt_surface_inventory.py` | `prompt` |
| `scripts/check_ai_refusal_fixtures.py` | `prompt` |
| `scripts/check_ai_safety_boundary_contract.py` | `prompt` |
| `scripts/check_ai_safety_release_evidence.py` | `prompt, llm, remediation` |
| `scripts/check_answer_key_independence.py` | `prompt` |
| `scripts/check_arq_worker_import.py` | `generate_lesson` |
| `scripts/check_backend_consolidation_dragons.py` | `diagnostic` |
| `scripts/check_backend_consolidation_release_guard.py` | `diagnostic` |
| `scripts/check_backend_runtime_compatibility.py` | `diagnostic` |
| `scripts/check_beta_known_issues_register.py` | `remediation` |
| `scripts/check_beta_launch_staging_acceptance_production_readiness.py` | `diagnostic` |
| `scripts/check_beta_release_readiness_contract.py` | `prompt` |
| `scripts/check_beta_retrospective_action_register.py` | `remediation` |
| `scripts/check_beta_rollback_runbook.py` | `prompt` |
| `scripts/check_caps_ai_safety_release_evidence.py` | `llm` |
| `scripts/check_caps_alignment_contract.py` | `prompt, diagnostic, remediation` |
| `scripts/check_caps_learning_proof.py` | `diagnostic` |
| `scripts/check_cluster_f_ai_safety_evidence.py` | `prompt, llm, anthropic, diagnostic, remediation` |
| `scripts/check_cluster_f_closure.py` | `prompt, llm, diagnostic, remediation` |
| `scripts/check_cluster_g_frontend_evidence.py` | `diagnostic` |
| `scripts/check_cluster_h_release_readiness.py` | `remediation` |
| `scripts/check_database_persistence_production_readiness.py` | `diagnostic` |
| `scripts/check_diag_deep_health_runtime.py` | `diagnostic` |
| `scripts/check_diagnostic_generation_safety_contract.py` | `diagnostic` |
| `scripts/check_diagnostic_item_bank_canonicality.py` | `diagnostic` |
| `scripts/check_diagnostic_score_live_audit.py` | `diagnostic` |
| `scripts/check_diagnostics_assessment_production_readiness.py` | `diagnostic, remediation` |
| `scripts/check_diagnostics_dynamic_repository_boundary.py` | `diagnostic` |
| `scripts/check_diagnostics_jobs_integrity.py` | `diagnostic` |
| `scripts/check_diagnostics_scoring_snapshot.py` | `diagnostic` |
| `scripts/check_diagnostics_session_binding.py` | `diagnostic` |
| `scripts/check_diagnostics_transaction_rollback_proof.py` | `diagnostic` |
| `scripts/check_domain_06_ai_llm_pipeline_evidence.py` | `llm` |
| `scripts/check_domain_07_diagnostics_assessment_evidence.py` | `diagnostic` |
| `scripts/check_environment_security_contract.py` | `anthropic, groq` |
| `scripts/check_frontend_accessibility_contract.py` | `diagnostic` |
| `scripts/check_frontend_api_client_inventory.py` | `diagnostic` |
| `scripts/check_frontend_mock_api_fixtures.py` | `diagnostic` |
| `scripts/check_frontend_production_readiness.py` | `diagnostic` |
| `scripts/check_frontend_route_inventory.py` | `diagnostic` |
| `scripts/check_health_readiness_contract.py` | `diagnostic` |
| `scripts/check_learner_vertical_journey_contract.py` | `diagnostic` |
| `scripts/check_learning_evidence.py` | `diagnostic` |
| `scripts/check_llm_provider_fallback_contract.py` | `prompt, llm, anthropic` |
| `scripts/check_observability_production_readiness.py` | `prompt, llm` |
| `scripts/check_phase2_authorization_evidence.py` | `diagnostic` |
| `scripts/check_popia_consent_audit_evidence.py` | `diagnostic` |
| `scripts/check_popia_consent_boundary_matrix.py` | `generate_lesson, diagnostic` |
| `scripts/check_post_deploy_staging_smoke_checklist.py` | `prompt` |
| `scripts/check_privacy_legal_release_evidence.py` | `diagnostic` |
| `scripts/check_release_candidate_evidence_sweep.py` | `diagnostic` |
| `scripts/check_remediation_safety_contract.py` | `remediation` |
| `scripts/check_route_tx_diagnostics_slice.py` | `diagnostic` |
| `scripts/check_route_tx_slice_rollup.py` | `diagnostic` |
| `scripts/check_runtime_blockers_after_followup_audit.py` | `diagnostic` |
| `scripts/check_runtime_integration_proof.py` | `diagnostic` |
| `scripts/check_security_posture_threat_modeling_production_readiness.py` | `prompt, remediation` |
| `scripts/check_transaction_boundary_guardrails.py` | `diagnostic` |
| `scripts/ci/check_diagnostics_assessment.py` | `diagnostic` |
| `scripts/ci/content_factory_schema_contract.py` | `diagnostic, remediation` |
| `scripts/ci_evidence_acceptance.py` | `llm, diagnostic` |
| `scripts/compare_orm_tables_to_database.py` | `diagnostic` |
| `scripts/content_factory/run_full_generation.py` | `diagnostic` |
| `scripts/create_diagnostic_items.py` | `llm, diagnostic` |
| `scripts/curriculum/build_launch_content_artifacts.py` | `diagnostic` |
| `scripts/curriculum/build_launch_item_bank.py` | `diagnostic` |
| `scripts/curriculum/build_scope_content_artifacts.py` | `diagnostic, remediation` |
| `scripts/curriculum/load_phase02r_authority_records.py` | `prompt` |
| `scripts/curriculum/validate_scope_content.py` | `diagnostic, remediation` |
| `scripts/db_backup_restore_rollback_evidence.py` | `llm, diagnostic` |
| `scripts/db_migration_seed_repeatability.py` | `diagnostic` |
| `scripts/diag_deep_health_runtime_evidence.py` | `llm, diagnostic` |
| `scripts/diagnostic_item_bank_canonicality.py` | `diagnostic` |
| `scripts/diagnostic_score_live_audit.py` | `llm, diagnostic` |
| `scripts/evaluate_pedagogy.py` | `prompt, llm` |
| `scripts/evidence_attachment_runbook.py` | `diagnostic` |
| `scripts/finalize_phase02r_evidence_metadata.py` | `llm` |
| `scripts/generate_ai_prompt_surface_inventory.py` | `prompt, system_message, user_message, llm, anthropic, groq, generate_lesson, diagnostic, remediation` |
| `scripts/generate_audit_callsite_inventory.py` | `diagnostic` |
| `scripts/generate_backend_consolidation_evidence_manifest.py` | `diagnostic` |
| `scripts/generate_backend_consolidation_report.py` | `diagnostic` |
| `scripts/generate_backend_consolidation_terminal_report.py` | `diagnostic` |
| `scripts/generate_backend_deletion_candidate_inventory.py` | `diagnostic` |
| `scripts/generate_beta_signoff_manifest.py` | `prompt` |
| `scripts/generate_consent_callsite_inventory.py` | `diagnostic` |
| `scripts/generate_consent_gate_inventory.py` | `diagnostic` |
| `scripts/generate_coverage_matrix.py` | `diagnostic` |
| `scripts/generate_frontend_api_client_inventory.py` | `diagnostic` |
| `scripts/generate_frontend_route_inventory.py` | `diagnostic` |
| `scripts/generate_items.py` | `prompt, llm, diagnostic` |
| `scripts/generate_learner_authz_matrix.py` | `diagnostic` |
| `scripts/generate_popia_consent_boundary_matrix.py` | `generate_lesson, diagnostic` |
| `scripts/generate_route_inventory.py` | `diagnostic` |
| `scripts/generate_runtime_integration_proof_reports.py` | `diagnostic` |
| `scripts/generate_service_family_map.py` | `diagnostic` |
| `scripts/ingestion/capture_siyavula_playwright_network.py` | `diagnostic` |
| `scripts/ingestion/main.py` | `anthropic` |
| `scripts/ingestion/models.py` | `llm, anthropic` |
| `scripts/ingestion/pipeline/__init__.py` | `anthropic` |
| `scripts/ingestion/pipeline/training_formatter.py` | `prompt, llm, anthropic` |
| `scripts/ingestion/sources/khan_academy.py` | `prompt` |
| `scripts/inspect_diagnostics_and_jobs_integrity.py` | `diagnostic` |
| `scripts/inventory_services.py` | `diagnostic` |
| `scripts/jwt_secret_rotation_evidence.py` | `llm` |
| `scripts/lessons/generate_lessons.py` | `llm, generate_lesson, remediation` |
| `scripts/lessons/seed_lesson_bank.py` | `prompt, llm, remediation` |
| `scripts/lessons/validate_lessons.py` | `prompt, llm, groq` |
| `scripts/live_db_tx_evidence.py` | `llm, diagnostic` |
| `scripts/maintenance/audit_todo_backlog.py` | `prompt, llm, diagnostic, remediation` |
| `scripts/merge_lora.py` | `llm` |
| `scripts/patch_diag_deep_health_runtime_registry.py` | `diagnostic` |
| `scripts/patch_diagnostic_item_bank_canonicality_registry.py` | `diagnostic` |
| `scripts/patch_diagnostic_score_live_audit_registry.py` | `diagnostic` |
| `scripts/patch_diagnostics_dynamic_repository_boundary.py` | `diagnostic` |
| `scripts/patch_diagnostics_scoring_snapshot.py` | `diagnostic` |
| `scripts/patch_diagnostics_session_binding.py` | `diagnostic` |
| `scripts/patch_route_tx_diagnostics_slice_registry.py` | `diagnostic` |
| `scripts/phase02r_gate_control.py` | `llm` |
| `scripts/phase2_evaluate_retrieval.py` | `diagnostic` |
| `scripts/popia_route_tx_gap_plan.py` | `diagnostic` |
| `scripts/popia_sweep.py` | `prompt, llm, anthropic, groq, diagnostic` |
| `scripts/populate_register.py` | `prompt` |
| `scripts/prepare_training_data.py` | `llm` |
| `scripts/prod_frontend_runtime.py` | `llm` |
| `scripts/refresh_current_state_doc.py` | `llm` |
| `scripts/repair_arq_dependency_worker_import.py` | `diagnostic` |
| `scripts/repair_diagnostics_data_integrity.py` | `diagnostic` |
| `scripts/repair_runtime_blockers_after_followup_audit.py` | `diagnostic` |
| `scripts/route_tx_auth_slice.py` | `llm` |
| `scripts/route_tx_diagnostics_slice.py` | `llm, diagnostic` |
| `scripts/route_tx_impl_plan.py` | `diagnostic` |
| `scripts/route_tx_popia_slice.py` | `llm` |
| `scripts/route_tx_slice_rollup.py` | `diagnostic` |
| `scripts/seed_irt_items.py` | `diagnostic` |
| `scripts/seed_item_bank.py` | `diagnostic` |
| `scripts/staging_acceptance_evidence.py` | `llm` |
| `scripts/staging_smoke_evidence_acceptance.py` | `llm, diagnostic` |
| `scripts/staging_smoke_probe.py` | `diagnostic` |
| `scripts/sync_git_to_redmine.py` | `diagnostic` |
| `scripts/train_qlora.py` | `prompt, llm` |
| `scripts/transaction_boundary_inventory.py` | `diagnostic` |
| `scripts/transaction_rollback_rollup.py` | `diagnostic` |
| `scripts/tx_route_wiring_inventory.py` | `diagnostic` |
| `scripts/validate_ai_output_fixtures.py` | `prompt, diagnostic, remediation` |
| `scripts/validate_focused_adapter.py` | `llm` |
| `scripts/validate_item_bank.py` | `diagnostic` |
| `scripts/validate_ops_assets.py` | `llm` |
| `scripts/validate_phase02r_authority_schema.py` | `prompt` |
| `scripts/validate_runtime_env.py` | `anthropic, groq` |
| `scripts/validate_schema_integrity.py` | `diagnostic` |
| `scripts/verify_phase02r_gate2r2.py` | `diagnostic` |

## Command

```bash
python scripts/generate_ai_prompt_surface_inventory.py
```
