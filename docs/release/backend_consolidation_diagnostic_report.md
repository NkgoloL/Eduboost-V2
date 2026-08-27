# Backend Consolidation Diagnostic Report

Generated at: `2026-08-26T17:24:45Z`

| Check | Return code | Command |
|---|---:|---|
| backend dragons | 0 | `/home/nkgolol/Dev/SandBox/Eduboost-V2-coverage-clean-20260817/.venv/bin/python scripts/check_backend_consolidation_dragons.py` |
| audit inventory | 0 | `/home/nkgolol/Dev/SandBox/Eduboost-V2-coverage-clean-20260817/.venv/bin/python scripts/generate_audit_callsite_inventory.py --fail-empty` |
| consent inventory | 0 | `/home/nkgolol/Dev/SandBox/Eduboost-V2-coverage-clean-20260817/.venv/bin/python scripts/generate_consent_callsite_inventory.py --fail-empty` |
| health readiness contract | 0 | `/home/nkgolol/Dev/SandBox/Eduboost-V2-coverage-clean-20260817/.venv/bin/python scripts/check_health_readiness_contract.py` |
| schema drift contract | 0 | `/home/nkgolol/Dev/SandBox/Eduboost-V2-coverage-clean-20260817/.venv/bin/python scripts/check_schema_drift_contract.py` |

## Interpretation

- This report is diagnostic evidence only.
- It does not approve deletion of audit or consent code.
- It does not approve consent table consolidation.
- It does not approve Alembic stamping/baselining.

## backend dragons

Command: `/home/nkgolol/Dev/SandBox/Eduboost-V2-coverage-clean-20260817/.venv/bin/python scripts/check_backend_consolidation_dragons.py`

Return code: `0`

```text
Backend consolidation dragon diagnostic
- audit_repository: 50 match(es)
  - app/core/audit.py
  - app/modules/consent/service.py
  - app/repositories/__init__.py
  - app/repositories/audit_repository.py
  - app/repositories/repositories.py
  - app/services/auth_application_service.py
  - app/services/consent_service.py
  - app/services/data_subject_rights_service.py
  - app/services/job_dependency_factory.py
  - app/services/popia_service.py
  - scripts/audit_write_flow_command.py
  - scripts/check_auth_service_extraction.py
  - ... 9 more file(s)
- audit_events: 154 match(es)
  - alembic/versions/0006_v2_audit_events.py
  - alembic/versions/20260507_1200_popia_consent_audit_hardening.py
  - alembic/versions/20260507_1330_database_integrity_constraints.py
  - alembic/versions/20260510_0300_popia_consent_audit_dsr.py
  - alembic/versions/20260516_0100_remove_base_sentinel.py
  - alembic/versions/_deprecated/0001_phase2_baseline.py
  - alembic/versions/_deprecated/0001_schema_from_technical_report.py
  - app/core/database.py
  - app/core/health.py
  - app/core/runtime_readiness.py
  - app/models/__init__.py
  - app/repositories/audit_repository.py
  - ... 24 more file(s)
- audit_logs: 26 match(es)
  - alembic/versions/0001_v2_consolidated_schema.py
  - app/models/__init__.py
  - app/modules/disaster_recovery/production_readiness_contracts.py
  - app/services/audit_canonicalization_registry.py
  - scripts/check_backend_consolidation_dragons.py
  - scripts/check_backend_destructive_action_blocklist.py
  - scripts/check_first_audit_runtime_wiring_no_destructive_actions.py
  - scripts/db_migration_seed_repeatability.py
  - scripts/generate_audit_callsite_inventory.py
  - scripts/generate_backend_deletion_candidate_inventory.py
  - scripts/generate_release_owner_beta_go_no_go.py
  - scripts/generate_truthful_release_owner_beta_go_no_go.py
  - ... 3 more file(s)
- consent_records: 17 match(es)
  - alembic/env.py
  - alembic/versions/20260510_0300_popia_consent_audit_dsr.py
  - app/repositories/consent_repository.py
  - app/services/data_subject_rights_service.py
  - scripts/check_backend_consolidation_dragons.py
  - scripts/check_first_audit_runtime_wiring_no_destructive_actions.py
  - scripts/check_runtime_wiring_no_destructive_actions.py
  - scripts/compare_orm_tables_to_database.py
  - scripts/db_live_only_table_ownership.py
  - scripts/generate_consent_callsite_inventory.py
- parental_consents: 54 match(es)
  - alembic/versions/0001_v2_consolidated_schema.py
  - alembic/versions/20260505_1734_add_missing_production_indexes.py
  - alembic/versions/20260507_1200_popia_consent_audit_hardening.py
  - alembic/versions/20260507_1330_database_integrity_constraints.py
  - alembic/versions/20260528_1600_popia_consent_versioning.py
  - alembic/versions/_deprecated/0001_initial_consolidated_schema.py
  - alembic/versions/_deprecated/0001_schema_from_technical_report.py
  - app/models/__init__.py
  - app/services/popia_service.py
  - scripts/check_backend_consolidation_dragons.py
  - scripts/check_first_audit_runtime_wiring_no_destructive_actions.py
  - scripts/check_runtime_wiring_no_destructive_actions.py
  - ... 7 more file(s)
- consent_service: 173 match(es)
  - app/api_v2_deps/consent_lifecycle.py
  - app/api_v2_routers/consent.py
  - app/api_v2_routers/popia.py
  - app/api_v2_routers/vertical_journey.py
  - app/core/consent_gate.py
  - app/modules/consent/__init__.py
  - app/modules/consent/service.py
  - app/modules/diagnostics/service.py
  - app/modules/lessons/service.py
  - app/security/dependencies.py
  - app/services/consent.py
  - app/services/consent_runtime_compatibility.py
  - ... 39 more file(s)
- deep_health: 52 match(es)
  - app/api_v2.py
  - app/core/health.py
  - scripts/check_backend_consolidation_dragons.py
  - scripts/check_diag_deep_health_runtime.py
  - scripts/check_runtime_entrypoints.py
  - scripts/diag_deep_health_runtime_evidence.py
  - scripts/generate_route_inventory.py
  - scripts/run_staging_smoke.py
  - scripts/runtime_readiness/capture_backend_backed_e2e_evidence.py
  - scripts/runtime_readiness/capture_backend_backed_seeded_e2e_evidence.py
  - scripts/runtime_readiness/capture_live_stack_readiness_evidence.py
  - scripts/runtime_readiness/verify_backend_backed_e2e.py
  - ... 9 more file(s)
- PASS backend consolidation dragons documented and inventoried
```

## audit inventory

Command: `/home/nkgolol/Dev/SandBox/Eduboost-V2-coverage-clean-20260817/.venv/bin/python scripts/generate_audit_callsite_inventory.py --fail-empty`

Return code: `0`

```text
Wrote /home/nkgolol/Dev/SandBox/Eduboost-V2-coverage-clean-20260817/docs/release/audit_callsite_inventory.md (6056 row(s))
```

## consent inventory

Command: `/home/nkgolol/Dev/SandBox/Eduboost-V2-coverage-clean-20260817/.venv/bin/python scripts/generate_consent_callsite_inventory.py --fail-empty`

Return code: `0`

```text
Wrote /home/nkgolol/Dev/SandBox/Eduboost-V2-coverage-clean-20260817/docs/release/consent_callsite_inventory.md (596 row(s))
```

## health readiness contract

Command: `/home/nkgolol/Dev/SandBox/Eduboost-V2-coverage-clean-20260817/.venv/bin/python scripts/check_health_readiness_contract.py`

Return code: `0`

```text
Health/readiness diagnostic contract check
- PASS [file] docs/release/health_readiness_diagnostic_contract.md: present
- PASS [content] docs/release/health_readiness_diagnostic_contract.md: contains 'Lightweight health'
- PASS [content] docs/release/health_readiness_diagnostic_contract.md: contains 'Deep health'
- PASS [content] docs/release/health_readiness_diagnostic_contract.md: contains 'database connectivity'
- PASS [content] docs/release/health_readiness_diagnostic_contract.md: contains 'Alembic current revision'
- PASS [content] docs/release/health_readiness_diagnostic_contract.md: contains 'required core table presence'
- PASS [content] docs/release/health_readiness_diagnostic_contract.md: contains 'no unsafe public write operations'
- PASS [file] docs/release/schema_drift_evidence_contract.md: present
- PASS [content] docs/release/schema_drift_evidence_contract.md: contains 'make schema-drift-check'
- PASS [content] docs/release/schema_drift_evidence_contract.md: contains 'make schema-drift-check-db'
- PASS [content] docs/release/schema_drift_evidence_contract.md: contains 'alembic upgrade head'
- PASS [content] docs/release/schema_drift_evidence_contract.md: contains 'alembic stamp head'
- WARN [source] no known health router source found
- PASS health/readiness diagnostics documented
```

## schema drift contract

Command: `/home/nkgolol/Dev/SandBox/Eduboost-V2-coverage-clean-20260817/.venv/bin/python scripts/check_schema_drift_contract.py`

Return code: `0`

```text
Schema drift contract check
- PASS [file] scripts/compare_orm_tables_to_database.py: present
- PASS [file] docs/release/schema_drift_evidence_contract.md: present
ORM tables
- ai_budget_counters
- ai_usage_events
- ai_usage_reservations
- assessment_attempts
- assessment_blueprints
- assessments
- audit_events
- audit_logs
- calibration_audits
- consent_version_history
- content_answer_key_verifications
- content_artifact_reviews
- content_artifact_sources
- content_coverage_targets
- content_generation_artifacts
- content_generation_runs
- content_generation_tasks
- content_production_artifacts
- content_promotion_events
- content_review_assignments
- content_review_decisions
- content_scopes
- content_seed_runs
- content_staging_artifacts
- content_staging_seed_items
- content_staging_verification_runs
- content_staging_verification_scope_results
- content_state_transition_events
- content_validation_reports
- curriculum_answer_verification_records
- curriculum_chunk_versions
- curriculum_claim_validation_records
- curriculum_corpus_activation_events
- curriculum_corpus_active_bindings
- curriculum_corpus_memberships
- curriculum_corpus_outbox_events
- curriculum_corpus_versions
- curriculum_coverage_snapshots
- curriculum_edge_versions
- curriculum_expansion_runs
- curriculum_extraction_runs
- curriculum_generation_grounding_records
- curriculum_graph_nodes
- curriculum_inventory_items
- curriculum_inventory_versions
- curriculum_language_links
- curriculum_legacy_dispositions
- curriculum_mapping_review_events
- curriculum_mapping_versions
- curriculum_node_versions
- curriculum_nodes
- curriculum_original_objects
- curriculum_retrieval_evaluation_cases
- curriculum_retrieval_evaluation_runs
- curriculum_review_decisions
- curriculum_rights_decisions
- curriculum_source_acquisition_runs
- curriculum_source_mapping_versions
- curriculum_source_pages
- curriculum_source_sections
- curriculum_source_versions
- curriculum_sources
- diagnostic_items
- diagnostic_sessions
- erasure_request
- guardians
- irt_calibration_events
- irt_calibration_runs
- irt_items
- item_exposures
- knowledge_gaps
- learner_kg_node_states
- learner_profiles
- lesson_bank
- lesson_feedback
- lessons
- mastery_snapshots
- onboarding_states
- parental_consents
- phase02r_audit_findings
- practice_queue
- practice_sessions
- privacy_settings
- retrieval_source_chunks
- retrieval_source_documents
- rlhf_exports
- runtime_kg_edges
- runtime_kg_events
- runtime_kg_graph_loads
- runtime_kg_nodes
- secure_tokens
- spaced_review_schedule
- stripe_webhook_events
- study_plan_templates
- study_plans
- subject_mastery
- topic_mastery
- training_dataset_entries
- training_dataset_manifests
- tutor_escalations
- tutor_grounding_records
- tutor_messages
- tutor_sessions
DATABASE_URL not supplied; database comparison skipped.

- PASS [command] ORM-only schema drift check runs without DB
```
