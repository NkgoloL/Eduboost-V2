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
| `app/api_v2_routers/diagnostics.py` | `diagnostic` |
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
| `app/domain/api_v2_models.py` | `remediation` |
| `app/domain/consent.py` | `llm, diagnostic` |
| `app/domain/item_schema.py` | `llm, diagnostic` |
| `app/domain/lesson.py` | `llm` |
| `app/domain/llm_schemas.py` | `diagnostic` |
| `app/domain/roles.py` | `diagnostic` |
| `app/domain/schemas.py` | `diagnostic` |
| `app/models/__init__.py` | `prompt, llm, groq, diagnostic, remediation` |
| `app/models/diagnostic_item.py` | `llm, diagnostic` |
| `app/models/item_exposure.py` | `diagnostic` |
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
| `app/modules/jobs.py` | `diagnostic` |
| `app/modules/learners/__init__.py` | `prompt, llm, diagnostic` |
| `app/modules/learners/ether_service.py` | `prompt, llm, diagnostic` |
| `app/modules/lessons/__init__.py` | `llm, anthropic, groq` |
| `app/modules/lessons/adaptive_remediation.py` | `prompt, diagnostic, remediation` |
| `app/modules/lessons/answer_key_verifier.py` | `prompt, llm` |
| `app/modules/lessons/budget_guardrails.py` | `prompt, llm` |
| `app/modules/lessons/caps_topic_map_service.py` | `prompt` |
| `app/modules/lessons/lesson_coverage_router.py` | `llm` |
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
| `app/modules/lessons/service.py` | `llm, groq, generate_lesson` |
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
| `app/repositories/repositories.py` | `diagnostic` |
| `app/services/backend_consolidation_runtime.py` | `diagnostic` |
| `app/services/content_safety/__init__.py` | `llm` |
| `app/services/content_safety/lesson_contracts.py` | `llm, remediation` |
| `app/services/content_safety/pii.py` | `prompt, llm` |
| `app/services/curriculum/coverage.py` | `diagnostic` |
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
| `app/services/executive.py` | `llm` |
| `app/services/lesson_context_builder.py` | `prompt, diagnostic, remediation` |
| `app/services/lesson_service_v2.py` | `llm, generate_lesson` |
| `app/services/llm/__init__.py` | `llm` |
| `app/services/llm/gateway.py` | `prompt, llm` |
| `app/services/pii_sweep.py` | `anthropic` |
| `app/services/popia_service.py` | `diagnostic` |
| `app/services/quota_service.py` | `llm` |
| `app/services/rlhf_service.py` | `anthropic` |
| `app/services/study_plan_updater.py` | `diagnostic, remediation` |
| `app/services/system_service_v2.py` | `diagnostic` |
| `scripts/assign_irt_params.py` | `diagnostic` |
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
| `scripts/check_diagnostic_generation_safety_contract.py` | `diagnostic` |
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
| `scripts/check_runtime_blockers_after_followup_audit.py` | `diagnostic` |
| `scripts/check_runtime_integration_proof.py` | `diagnostic` |
| `scripts/check_security_posture_threat_modeling_production_readiness.py` | `prompt, remediation` |
| `scripts/check_transaction_boundary_guardrails.py` | `diagnostic` |
| `scripts/ci/check_diagnostics_assessment.py` | `diagnostic` |
| `scripts/compare_orm_tables_to_database.py` | `diagnostic` |
| `scripts/evaluate_pedagogy.py` | `prompt, llm` |
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
| `scripts/generate_items.py` | `llm, diagnostic` |
| `scripts/generate_learner_authz_matrix.py` | `diagnostic` |
| `scripts/generate_popia_consent_boundary_matrix.py` | `generate_lesson, diagnostic` |
| `scripts/generate_route_inventory.py` | `diagnostic` |
| `scripts/generate_runtime_integration_proof_reports.py` | `diagnostic` |
| `scripts/generate_service_family_map.py` | `diagnostic` |
| `scripts/inspect_diagnostics_and_jobs_integrity.py` | `diagnostic` |
| `scripts/inventory_services.py` | `diagnostic` |
| `scripts/lessons/generate_lessons.py` | `llm, generate_lesson, remediation` |
| `scripts/lessons/validate_lessons.py` | `prompt, llm, groq` |
| `scripts/maintenance/audit_todo_backlog.py` | `prompt, llm, diagnostic, remediation` |
| `scripts/merge_lora.py` | `llm` |
| `scripts/patch_diagnostics_dynamic_repository_boundary.py` | `diagnostic` |
| `scripts/patch_diagnostics_scoring_snapshot.py` | `diagnostic` |
| `scripts/patch_diagnostics_session_binding.py` | `diagnostic` |
| `scripts/popia_sweep.py` | `prompt, llm, anthropic, groq, diagnostic` |
| `scripts/prepare_training_data.py` | `llm` |
| `scripts/refresh_current_state_doc.py` | `llm` |
| `scripts/repair_arq_dependency_worker_import.py` | `diagnostic` |
| `scripts/repair_diagnostics_data_integrity.py` | `diagnostic` |
| `scripts/repair_runtime_blockers_after_followup_audit.py` | `diagnostic` |
| `scripts/route_tx_auth_slice.py` | `llm` |
| `scripts/route_tx_impl_plan.py` | `diagnostic` |
| `scripts/route_tx_popia_slice.py` | `llm` |
| `scripts/seed_irt_items.py` | `diagnostic` |
| `scripts/seed_item_bank.py` | `diagnostic` |
| `scripts/staging_acceptance_evidence.py` | `llm` |
| `scripts/sync_git_to_redmine.py` | `diagnostic` |
| `scripts/train_qlora.py` | `prompt, llm` |
| `scripts/transaction_boundary_inventory.py` | `diagnostic` |
| `scripts/transaction_rollback_rollup.py` | `diagnostic` |
| `scripts/tx_route_wiring_inventory.py` | `diagnostic` |
| `scripts/validate_ai_output_fixtures.py` | `prompt, diagnostic, remediation` |
| `scripts/validate_focused_adapter.py` | `llm` |
| `scripts/validate_item_bank.py` | `diagnostic` |
| `scripts/validate_ops_assets.py` | `llm` |
| `scripts/validate_runtime_env.py` | `anthropic, groq` |
| `scripts/validate_schema_integrity.py` | `diagnostic` |

## Command

```bash
python scripts/generate_ai_prompt_surface_inventory.py
```
