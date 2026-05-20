# Transaction Boundary Inventory

Generated at: `2026-05-19T23:09:41Z`

Candidate count: `96`
Critical candidate count: `47`

Policy: Multi-write candidates remain not-proven until rollback/integration tests demonstrate atomicity.

| File | Function | Line | Status | Critical areas | Mutation calls | Transaction markers |
|---|---|---:|---|---|---|---|
| `app/api_v2_routers/0005_irt_seed.py` | `downgrade` | 225 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/api_v2_routers/consent.py` | `grant_consent` | 36 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `grant` | `-` |
| `app/api_v2_routers/consent.py` | `revoke_consent` | 69 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `revoke` | `-` |
| `app/api_v2_routers/diagnostics.py` | `submit_diagnostic` | 81 | `multi-write-candidate-not-proven` | `diagnostics_response` | `upsert` | `-` |
| `app/api_v2_routers/gamification.py` | `award_xp` | 46 | `multi-write-candidate-not-proven` | `lesson_completion` | `commit` | `-` |
| `app/api_v2_routers/learners.py` | `create_learner` | 24 | `single-mutation-candidate` | `-` | `create` | `-` |
| `app/api_v2_routers/learners.py` | `request_erasure` | 122 | `single-mutation-candidate` | `-` | `delete` | `-` |
| `app/api_v2_routers/parents.py` | `get_parent_trust_dashboard` | 105 | `multi-write-candidate-not-proven` | `lesson_completion` | `execute` | `-` |
| `app/api_v2_routers/parents.py` | `get_learner_progress` | 219 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/api_v2_routers/parents.py` | `request_erasure` | 271 | `single-mutation-candidate` | `-` | `delete` | `-` |
| `app/api_v2_routers/popia.py` | `grant_consent` | 102 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `grant` | `-` |
| `app/api_v2_routers/popia.py` | `deny_consent` | 120 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `deny` | `-` |
| `app/api_v2_routers/popia.py` | `withdraw_consent` | 138 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `withdraw` | `-` |
| `app/api_v2_routers/popia.py` | `renew_consent` | 153 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `renew` | `-` |
| `app/modules/auth/service.py` | `register_guardian` | 66 | `single-mutation-candidate` | `-` | `create` | `-` |
| `app/modules/auth/service.py` | `authenticate` | 136 | `multi-write-candidate-not-proven` | `auth_refresh` | `update` | `-` |
| `app/modules/auth/service.py` | `verify_email` | 200 | `single-mutation-candidate` | `-` | `update` | `-` |
| `app/modules/billing/production_readiness_contracts.py` | `process` | 239 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/modules/consent/service.py` | `grant` | 113 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `grant` | `-` |
| `app/modules/consent/service.py` | `revoke` | 163 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `revoke` | `-` |
| `app/modules/consent/service.py` | `renew` | 196 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `renew` | `-` |
| `app/modules/consent/service.py` | `execute_erasure` | 233 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `revoke` | `-` |
| `app/modules/diagnostics/irt_engine.py` | `record_response` | 595 | `multi-write-candidate-not-proven` | `diagnostics_response` | `add` | `-` |
| `app/modules/diagnostics/item_generator.py` | `_call_llm_for_json` | 224 | `single-mutation-candidate` | `-` | `complete` | `-` |
| `app/modules/diagnostics/item_validator.py` | `__init__` | 136 | `single-mutation-candidate` | `-` | `update` | `-` |
| `app/modules/diagnostics/item_validator.py` | `_index_topic_list` | 151 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/modules/diagnostics/service.py` | `grant_consent` | 46 | `transaction-marker-present` | `popia_lifecycle` | `grant` | `atomic, transaction` |
| `app/modules/diagnostics/service.py` | `revoke_consent` | 107 | `transaction-marker-present` | `popia_lifecycle` | `revoke` | `transaction` |
| `app/modules/diagnostics/session_recovery_service.py` | `invalidate_session_snapshot` | 69 | `single-mutation-candidate` | `-` | `delete` | `-` |
| `app/modules/jobs.py` | `expire_stale_diagnostic_sessions` | 85 | `multi-write-candidate-not-proven` | `-` | `commit, execute, update` | `-` |
| `app/modules/lessons/answer_key_verifier.py` | `verify` | 167 | `multi-write-candidate-not-proven` | `lesson_completion` | `complete` | `-` |
| `app/modules/lessons/budget_guardrails.py` | `add` | 101 | `transaction-marker-present` | `lesson_completion` | `execute` | `atomic` |
| `app/modules/lessons/budget_guardrails.py` | `record_usage` | 219 | `multi-write-candidate-not-proven` | `lesson_completion` | `add` | `-` |
| `app/modules/lessons/caps_topic_map_service.py` | `load_maps` | 149 | `single-mutation-candidate` | `-` | `update` | `-` |
| `app/modules/lessons/lesson_generator.py` | `generate` | 118 | `multi-write-candidate-not-proven` | `lesson_completion` | `commit` | `-` |
| `app/modules/lessons/llm_gateway.py` | `_call_groq` | 123 | `single-mutation-candidate` | `-` | `create` | `-` |
| `app/modules/lessons/llm_gateway.py` | `_call_anthropic` | 177 | `single-mutation-candidate` | `-` | `create` | `-` |
| `app/modules/lessons/llm_gateway_v2.py` | `complete` | 144 | `multi-write-candidate-not-proven` | `lesson_completion` | `create` | `-` |
| `app/modules/lessons/llm_gateway_v2.py` | `complete` | 200 | `multi-write-candidate-not-proven` | `lesson_completion` | `create` | `-` |
| `app/modules/lessons/llm_gateway_v2.py` | `complete` | 292 | `multi-write-candidate-not-proven` | `lesson_completion` | `complete` | `-` |
| `app/modules/lessons/parent_explanation_mode.py` | `generate_parent_summary` | 222 | `multi-write-candidate-not-proven` | `lesson_completion` | `complete` | `-` |
| `app/modules/lessons/service.py` | `generate_lesson_for_learner` | 85 | `multi-write-candidate-not-proven` | `-` | `commit, create` | `-` |
| `app/modules/lessons/service.py` | `complete_lesson` | 189 | `multi-write-candidate-not-proven` | `lesson_completion` | `commit` | `-` |
| `app/modules/lessons/service.py` | `record_feedback` | 198 | `single-mutation-candidate` | `-` | `commit` | `-` |
| `app/modules/lessons/service.py` | `get_lesson_by_id` | 208 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/modules/lessons/service.py` | `_build_learner_context` | 220 | `multi-write-candidate-not-proven` | `lesson_completion` | `execute` | `-` |
| `app/modules/lessons/teacher_insight_mode.py` | `generate_teacher_insight` | 319 | `multi-write-candidate-not-proven` | `lesson_completion` | `complete` | `-` |
| `app/modules/notifications/production_readiness_contracts.py` | `enqueue` | 256 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/audit_migration_orchestrator.py` | `build_audit_migration_event` | 40 | `single-mutation-candidate` | `-` | `update` | `-` |
| `app/services/auth_db_lifecycle_proof.py` | `_create_schema` | 44 | `multi-write-candidate-not-proven` | `auth_refresh` | `commit` | `-` |
| `app/services/auth_db_lifecycle_proof.py` | `register` | 81 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/auth_db_lifecycle_proof.py` | `login` | 114 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/auth_db_lifecycle_proof.py` | `refresh` | 129 | `multi-write-candidate-not-proven` | `auth_refresh` | `execute` | `-` |
| `app/services/auth_db_lifecycle_proof.py` | `learner_ids_for_guardian` | 141 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/auth_db_lifecycle_proof.py` | `_issue_tokens` | 148 | `multi-write-candidate-not-proven` | `auth_refresh` | `execute` | `-` |
| `app/services/auth_lifecycle_impl.py` | `create_dev_session_impl` | 58 | `multi-write-candidate-not-proven` | `auth_refresh` | `create` | `-` |
| `app/services/auth_lifecycle_impl.py` | `register_impl` | 208 | `multi-write-candidate-not-proven` | `auth_refresh` | `create` | `-` |
| `app/services/auth_service.py` | `guardian_signup` | 147 | `single-mutation-candidate` | `-` | `create` | `-` |
| `app/services/auth_transactional_registration.py` | `register` | 55 | `transaction-marker-present` | `-` | `execute` | `begin, transaction` |
| `app/services/consent_compat.py` | `normalize_consent_audit_event` | 48 | `single-mutation-candidate` | `-` | `update` | `-` |
| `app/services/consent_renewal_service.py` | `_fetch_expiring_consents` | 276 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `execute` | `-` |
| `app/services/consent_renewal_service.py` | `_fetch_guardian` | 299 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `execute` | `-` |
| `app/services/consent_runtime_compatibility.py` | `normalize_consent_runtime_operation` | 110 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `update` | `-` |
| `app/services/consent_service.py` | `grant` | 42 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `create, grant, update` | `-` |
| `app/services/consent_service.py` | `deny` | 83 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `create, deny, update` | `-` |
| `app/services/consent_service.py` | `withdraw` | 115 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `update, withdraw` | `-` |
| `app/services/consent_service.py` | `renew` | 135 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `renew, update` | `-` |
| `app/services/consent_service.py` | `process_expiry` | 159 | `single-mutation-candidate` | `-` | `update` | `-` |
| `app/services/consent_service.py` | `flag_approaching_renewals` | 192 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `update` | `-` |
| `app/services/data_subject_rights_service.py` | `create_export_request` | 41 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/data_subject_rights_service.py` | `build_and_complete_export` | 75 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/data_subject_rights_service.py` | `create_erasure_request` | 123 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/data_subject_rights_service.py` | `approve_erasure` | 152 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/data_subject_rights_service.py` | `execute_erasure` | 173 | `transaction-marker-present` | `lesson_completion` | `execute` | `transaction` |
| `app/services/data_subject_rights_service.py` | `create_correction_request` | 248 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/data_subject_rights_service.py` | `complete_correction` | 276 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/data_subject_rights_service.py` | `create_restriction_request` | 295 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/data_subject_rights_service.py` | `lift_restriction` | 317 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/deep_readiness_runtime.py` | `_execute` | 19 | `single-mutation-candidate` | `-` | `execute` | `-` |
| `app/services/diagnostic_data_integrity.py` | `extract_diagnostic_item_ids` | 20 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/diagnostic_data_integrity.py` | `walk` | 25 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/diagnostic_data_integrity.py` | `validate_diagnostic_submission_payload` | 63 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/diagnostic_session_integrity.py` | `served_item_ids` | 42 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/diagnostic_transactional_response.py` | `submit_response` | 60 | `transaction-marker-present` | `diagnostics_response` | `execute` | `begin, transaction` |
| `app/services/job_runtime_integrity.py` | `assert_no_runtime_objects` | 29 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/job_runtime_integrity.py` | `walk` | 32 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/lesson_authorization.py` | `lesson_owner_learner_id` | 105 | `multi-write-candidate-not-proven` | `lesson_completion` | `execute` | `-` |
| `app/services/lesson_authorization.py` | `iter_sync_lesson_ids` | 162 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/lesson_authorization.py` | `walk` | 166 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/lesson_service_v2.py` | `generate_lesson` | 29 | `single-mutation-candidate` | `-` | `create` | `-` |
| `app/services/lesson_transactional_completion.py` | `complete_lesson` | 54 | `transaction-marker-present` | `lesson_completion` | `execute, update` | `begin, transaction` |
| `app/services/llm/gateway.py` | `complete` | 140 | `multi-write-candidate-not-proven` | `lesson_completion` | `complete` | `-` |
| `app/services/pii_sweep.py` | `scan_record` | 132 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/pii_sweep.py` | `_check_sa_id` | 163 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/pii_sweep.py` | `_check_email` | 175 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/pii_sweep.py` | `_check_phone_regex` | 185 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/pii_sweep.py` | `_check_phone_lib` | 195 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/pii_sweep.py` | `_check_salutation` | 209 | `single-mutation-candidate` | `-` | `add` | `-` |
| `app/services/popia_service.py` | `request_erasure` | 110 | `multi-write-candidate-not-proven` | `-` | `add, flush` | `-` |
| `app/services/popia_service.py` | `cancel_erasure` | 148 | `multi-write-candidate-not-proven` | `-` | `add, flush` | `-` |
| `app/services/popia_service.py` | `request_correction` | 165 | `multi-write-candidate-not-proven` | `-` | `add, flush` | `-` |
| `app/services/popia_service.py` | `restrict_processing` | 192 | `multi-write-candidate-not-proven` | `popia_lifecycle` | `flush, revoke` | `-` |
| `app/services/study_plan_service_v2.py` | `generate_plan` | 13 | `single-mutation-candidate` | `-` | `create` | `-` |
