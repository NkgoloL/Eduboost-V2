# Coverage Priority Inventory

Source: `var/prd11/runtime-restore/execution-7/coverage-baseline-stabilisation/coverage.json`

Current coverage: 62.97%

| Rank | Path | Missing stmts | Missing branches | Coverage | Domain | Tranche |
|---:|---|---:|---:|---:|---|---|
| 1 | `app/api_v2_routers/content_factory.py` | 339 | 46 | 35.0% | general_application | tranche_2_negative_branch_paths |
| 2 | `app/services/etl/etl_pipeline_v2.py` | 324 | 98 | 22.3% | general_application | tranche_2_negative_branch_paths |
| 3 | `app/services/content_review_governance.py` | 269 | 131 | 20.8% | general_application | tranche_2_negative_branch_paths |
| 4 | `app/services/llm_provider.py` | 231 | 62 | 22.1% | general_application | tranche_2_negative_branch_paths |
| 5 | `app/services/irt_quality_service.py` | 223 | 76 | 10.2% | general_application | tranche_2_negative_branch_paths |
| 6 | `app/services/etl/etl_pipeline_v3_additions.py` | 210 | 42 | 0.0% | general_application | tranche_2_negative_branch_paths |
| 7 | `app/services/batch_generation.py` | 202 | 62 | 18.0% | general_application | tranche_2_negative_branch_paths |
| 8 | `app/services/etl/etl_pipeline.py` | 196 | 77 | 68.5% | general_application | tranche_2_negative_branch_paths |
| 9 | `app/api_v2_routers/auth_extended.py` | 188 | 66 | 26.8% | authentication_authorization | tranche_1_highest_yield_behaviour |
| 10 | `app/services/curriculum_expansion.py` | 176 | 82 | 14.9% | general_application | tranche_2_negative_branch_paths |
| 11 | `app/modules/security_posture/production_readiness_contracts.py` | 147 | 120 | 38.2% | readiness_dependency_paths | tranche_2_negative_branch_paths |
| 12 | `app/services/learner_tutor.py` | 146 | 32 | 17.2% | learner_guardian_boundaries | tranche_1_highest_yield_behaviour |
| 13 | `app/modules/documentation_governance/production_readiness_contracts.py` | 145 | 122 | 35.5% | readiness_dependency_paths | tranche_2_negative_branch_paths |
| 14 | `app/modules/roadmap/production_readiness_contracts.py` | 144 | 122 | 36.2% | readiness_dependency_paths | tranche_2_negative_branch_paths |
| 15 | `app/modules/beta_launch/production_readiness_contracts.py` | 141 | 118 | 35.7% | readiness_dependency_paths | tranche_2_negative_branch_paths |
| 16 | `app/core/llm.py` | 140 | 57 | 48.6% | general_application | tranche_2_negative_branch_paths |
| 17 | `app/modules/final_release_blockers/production_readiness_contracts.py` | 136 | 118 | 36.8% | readiness_dependency_paths | tranche_2_negative_branch_paths |
| 18 | `app/modules/disaster_recovery/production_readiness_contracts.py` | 134 | 116 | 34.6% | readiness_dependency_paths | tranche_2_negative_branch_paths |
| 19 | `app/modules/operations_support/production_readiness_contracts.py` | 134 | 112 | 38.7% | readiness_dependency_paths | tranche_2_negative_branch_paths |
| 20 | `app/api_v2_routers/content_review.py` | 128 | 18 | 24.0% | general_application | tranche_1_highest_yield_behaviour |
| 21 | `app/modules/lessons/lesson_generator.py` | 124 | 40 | 27.8% | lesson_generation_completion | tranche_2_negative_branch_paths |
| 22 | `app/modules/deployment/production_readiness_contracts.py` | 122 | 106 | 35.2% | readiness_dependency_paths | tranche_2_negative_branch_paths |
| 23 | `app/services/curriculum/graph.py` | 121 | 68 | 70.4% | general_application | tranche_2_negative_branch_paths |
| 24 | `app/modules/jobs.py` | 121 | 20 | 40.3% | general_application | tranche_1_highest_yield_behaviour |
| 25 | `app/services/ai_operations.py` | 118 | 32 | 18.9% | general_application | tranche_2_negative_branch_paths |
| 26 | `app/modules/notifications/production_readiness_contracts.py` | 117 | 90 | 39.3% | readiness_dependency_paths | tranche_2_negative_branch_paths |
| 27 | `app/services/auth_service.py` | 116 | 52 | 46.7% | authentication_authorization | tranche_1_highest_yield_behaviour |
| 28 | `app/modules/quality_gates/production_readiness_contracts.py` | 115 | 96 | 38.1% | readiness_dependency_paths | tranche_2_negative_branch_paths |
| 29 | `app/repositories/item_bank_repository.py` | 113 | 54 | 15.2% | general_application | tranche_2_negative_branch_paths |
| 30 | `app/services/pii_sweep.py` | 109 | 46 | 0.0% | general_application | tranche_2_negative_branch_paths |
| 31 | `app/api_v2_routers/test_services.py` | 105 | 2 | 0.0% | general_application | tranche_1_highest_yield_behaviour |
| 32 | `app/services/runtime_kg/repository.py` | 97 | 26 | 0.0% | runtime_kg_projections | tranche_2_negative_branch_paths |
| 33 | `app/repositories/audit_repository.py` | 96 | 37 | 38.1% | audit_event_recording | tranche_2_negative_branch_paths |
| 34 | `app/services/launch_content_seed.py` | 96 | 39 | 23.7% | general_application | tranche_2_negative_branch_paths |
| 35 | `app/core/health.py` | 95 | 36 | 13.2% | readiness_dependency_paths | tranche_2_negative_branch_paths |
| 36 | `app/services/content_staging_seed_executor.py` | 92 | 29 | 65.1% | general_application | tranche_2_negative_branch_paths |
| 37 | `app/api_v2_routers/diagnostics.py` | 91 | 30 | 50.6% | assessments_diagnostics | tranche_1_highest_yield_behaviour |
| 38 | `app/services/data_subject_rights_service.py` | 89 | 14 | 27.0% | general_application | tranche_1_highest_yield_behaviour |
| 39 | `app/modules/lessons/answer_key_verifier.py` | 85 | 34 | 24.7% | lesson_generation_completion | tranche_2_negative_branch_paths |
| 40 | `app/services/content_production_promotion_executor.py` | 83 | 24 | 28.7% | general_application | tranche_2_negative_branch_paths |
| 41 | `app/services/content_generation/providers/llm.py` | 81 | 42 | 13.4% | general_application | tranche_2_negative_branch_paths |
| 42 | `app/repositories/repositories.py` | 79 | 2 | 49.7% | general_application | tranche_2_negative_branch_paths |
| 43 | `app/modules/diagnostics/irt_engine.py` | 78 | 33 | 66.4% | assessments_diagnostics | tranche_1_highest_yield_behaviour |
| 44 | `app/api_v2_routers/parents.py` | 77 | 24 | 22.9% | parent_dashboard | tranche_2_negative_branch_paths |
| 45 | `app/services/content_production_promotion_gate.py` | 74 | 42 | 26.1% | general_application | tranche_2_negative_branch_paths |
| 46 | `app/services/auth_application_service.py` | 73 | 34 | 58.4% | authentication_authorization | tranche_1_highest_yield_behaviour |
| 47 | `app/services/consent_renewal_service.py` | 73 | 12 | 25.4% | consent_popia | tranche_1_highest_yield_behaviour |
| 48 | `app/core/authorization.py` | 72 | 53 | 58.6% | authentication_authorization | tranche_1_highest_yield_behaviour |
| 49 | `app/modules/lessons/caps_topic_map_service.py` | 65 | 44 | 59.6% | lesson_generation_completion | tranche_2_negative_branch_paths |
| 50 | `app/services/content_validator.py` | 64 | 26 | 22.4% | general_application | tranche_2_negative_branch_paths |
| 51 | `app/repositories/lesson_repository.py` | 59 | 16 | 26.5% | lesson_generation_completion | tranche_2_negative_branch_paths |
| 52 | `app/services/job_dependency_factory.py` | 59 | 34 | 11.4% | general_application | tranche_2_negative_branch_paths |
| 53 | `app/modules/lessons/mock_llm_provider.py` | 57 | 10 | 0.0% | lesson_generation_completion | tranche_2_negative_branch_paths |
| 54 | `app/modules/diagnostics/production_readiness_contracts.py` | 56 | 32 | 33.3% | assessments_diagnostics | tranche_1_highest_yield_behaviour |
| 55 | `app/modules/billing/production_readiness_contracts.py` | 55 | 47 | 62.5% | billing_entitlement_boundaries | tranche_1_highest_yield_behaviour |
| 56 | `app/modules/lessons/budget_guardrails.py` | 55 | 12 | 37.4% | lesson_generation_completion | tranche_2_negative_branch_paths |
| 57 | `app/core/database.py` | 54 | 12 | 34.7% | readiness_dependency_paths | tranche_2_negative_branch_paths |
| 58 | `app/services/content_generation_run_lock.py` | 53 | 18 | 26.0% | general_application | tranche_2_negative_branch_paths |
| 59 | `app/services/semantic_retrieval/indexing.py` | 52 | 22 | 42.2% | general_application | tranche_2_negative_branch_paths |
| 60 | `app/api_v2_routers/tutor.py` | 51 | 10 | 35.1% | general_application | tranche_2_negative_branch_paths |
| 61 | `app/services/content_factory.py` | 51 | 10 | 67.0% | general_application | tranche_2_negative_branch_paths |
| 62 | `app/modules/observability/production_readiness_contracts.py` | 50 | 50 | 72.6% | readiness_dependency_paths | tranche_2_negative_branch_paths |
| 63 | `app/services/diagnostic_session_service.py` | 50 | 10 | 29.4% | assessments_diagnostics | tranche_1_highest_yield_behaviour |
| 64 | `app/services/content_staging_preview_service.py` | 50 | 18 | 39.3% | general_application | tranche_2_negative_branch_paths |
| 65 | `app/services/consent_service.py` | 49 | 12 | 30.7% | consent_popia | tranche_1_highest_yield_behaviour |
| 66 | `app/core/dependencies.py` | 49 | 10 | 0.0% | general_application | tranche_2_negative_branch_paths |
| 67 | `app/services/curriculum/corpus.py` | 48 | 41 | 81.7% | general_application | tranche_2_negative_branch_paths |
| 68 | `app/api_v2_routers/generation.py` | 48 | 14 | 53.0% | general_application | tranche_2_negative_branch_paths |
| 69 | `app/core/stripe_client.py` | 47 | 20 | 22.1% | general_application | tranche_2_negative_branch_paths |
| 70 | `app/services/auth_db_lifecycle_proof.py` | 46 | 28 | 54.6% | authentication_authorization | tranche_1_highest_yield_behaviour |
| 71 | `app/services/content_generation_executor.py` | 46 | 16 | 66.5% | general_application | tranche_2_negative_branch_paths |
| 72 | `app/services/content_generation/generated_lesson_contract.py` | 45 | 40 | 70.0% | lesson_generation_completion | tranche_2_negative_branch_paths |
| 73 | `app/services/curriculum/extraction.py` | 45 | 31 | 78.6% | general_application | tranche_2_negative_branch_paths |
| 74 | `app/services/semantic_retrieval/service.py` | 45 | 16 | 29.1% | general_application | tranche_2_negative_branch_paths |
| 75 | `app/api_v2_routers/learners.py` | 44 | 12 | 35.6% | learner_guardian_boundaries | tranche_1_highest_yield_behaviour |
| 76 | `app/modules/diagnostics/service.py` | 44 | 10 | 0.0% | assessments_diagnostics | tranche_1_highest_yield_behaviour |
| 77 | `app/modules/lessons/lesson_coverage_router.py` | 44 | 10 | 59.7% | lesson_generation_completion | tranche_2_negative_branch_paths |
| 78 | `app/services/content_artifact_lifecycle.py` | 44 | 14 | 43.7% | general_application | tranche_2_negative_branch_paths |
| 79 | `app/api_v2_routers/test_api.py` | 44 | 0 | 0.0% | general_application | tranche_2_negative_branch_paths |
| 80 | `app/services/semantic_retrieval/embedding.py` | 43 | 21 | 46.2% | general_application | tranche_2_negative_branch_paths |
