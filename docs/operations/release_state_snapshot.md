# Release State Snapshot

## Metadata

- generated_at_utc: `2026-06-12T17:40:52.295314+00:00`
- branch: `phase-11/technical-debt-burn-down`
- commit: `a70b57616bb29572fcb57961b91a3f68f0c66329`
- release_candidate: `unset`

## Working Tree Status

```text
M app/api_v2_routers/lessons.py
 M app/core/authorization.py
 M app/models/__init__.py
 M app/modules/diagnostics/item_bank_service.py
 M app/modules/diagnostics/item_validator.py
 M app/repositories/repositories.py
 M app/services/data_subject_rights_service.py
 M app/services/etl/etl_pipeline_v2.py
 M app/services/popia_service.py
 M app/services/study_plan_service_v2.py
 M docs/docs_gap_report.md
 M docs/docs_inventory.json
 M docs/docs_inventory.md
 M docs/operations/beta_release_evidence_bundle.md
 M docs/operations/beta_signoff_manifest.md
 M docs/operations/database_backup_manifest.md
 M docs/operations/database_restore_evidence.md
 M docs/operations/release_candidate_tag_manifest.md
 M docs/operations/staging_smoke_evidence_manifest.md
 M docs/release/backend_consolidation_progress_report.md
 M docs/release/db_live_only_table_ownership_status.json
 M docs/release/db_live_only_table_ownership_status.md
 M docs/release/db_migration_seed_repeatability_status.json
 M docs/release/db_migration_seed_repeatability_status.md
 M docs/release/diag_deep_health_runtime_status.json
 M docs/release/diag_deep_health_runtime_status.md
 M docs/release/diagnostic_item_bank_canonicality_status.json
 M docs/release/diagnostic_item_bank_canonicality_status.md
 M docs/release/disposable_db_schema_proof_execution_report.md
 M docs/release/evidence_attachment_runbook.md
 M docs/release/evidence_attachment_runbook_manifest.json
 M docs/release/evidence_status_registry.yml
 M docs/release/external_approval_status.json
 M docs/release/external_approval_status.md
 M docs/release/final_beta_gate_refresh.json
 M docs/release/final_beta_gate_refresh.md
 M docs/release/first_audit_runtime_wiring_report.md
 M docs/release/live_db_transaction_evidence_status.json
 M docs/release/live_db_transaction_evidence_status.md
 M docs/release/popia_response_contract_no_skip_status.json
 M docs/release/popia_response_contract_no_skip_status.md
 M docs/release/popia_route_transaction_gap_plan.json
 M docs/release/popia_route_transaction_gap_plan.md
 M docs/release/production_frontend_deployment_status.json
 M docs/release/production_frontend_deployment_status.md
 M docs/release/production_frontend_runtime_status.json
 M docs/release/production_frontend_runtime_status.md
 M docs/release/release_go_no_go_status.json
 M docs/release/release_go_no_go_status.md
 M docs/release/runtime_wiring_431_450_report.md
 M docs/security/PHASE2_AUTHORIZATION_CLOSURE.md
 M docs/security/dependency_pin_report.json
 M docs/security/dependency_pin_report.md
 M docs/security/jwt_rotation_introspection.json
 M docs/security/jwt_rotation_introspection.md
 M docs/security/jwt_rotation_repair_report.md
 M docs/security/popia_consent_boundary_matrix.md
 M scripts/deduplicate_makefile_targets.py
 M scripts/ingestion/queue_manager.py
 M scripts/ingestion/sources/huggingface_datasets.py
 M scripts/maintenance/audit_todo_backlog.py
 M scripts/populate_md_with_pdfs.py
 M scripts/refresh_current_state_doc.py
 M scripts/run_staging_smoke.py
 M scripts/scrape_teaching_materials.py
 M tests/api/test_content_factory_production_promotion_routes.py
 M tests/conftest.py
 M tests/integration/test_audit_immutability.py
 M tests/integration/test_content_factory_migrations.py
 M tests/integration/test_lesson_sync.py
 M tests/integration/test_practice_session_durability.py
 M tests/legacy/unit/test_gamification_service.py
 M tests/smoke/test_content_factory_admin_api_smoke.py
 M tests/test_e2e_integration.py
 M tests/unit/test_audit_callsite_inventory_and_adapter.py
 M tests/unit/test_etl_pipeline.py
 M tests/unit/test_guardian_consent_withdrawal.py
 M tests/unit/test_popia_service.py
 M tests/unit/test_popia_transactional_lifecycle_contracts.py
 M tests/unit/test_production_key_vault_behavior.py
 M tests/unit/test_role_authorization.py
 M tests/unit/test_secret_rotation.py
 M tests/unit/test_study_plan_updater.py
 M tests/unit/test_v2_services_full.py
?? scripts/phase11_ruff_status.sh
```

## State Artifacts

| Artifact | Present |
| --- | --- |
| `docs/operations/beta_release_readiness_contract.md` | `yes` |
| `docs/operations/beta_release_evidence_bundle.md` | `yes` |
| `docs/operations/beta_release_final_checklist.md` | `yes` |
| `docs/operations/beta_release_execution_plan.md` | `yes` |
| `docs/operations/beta_release_pr_body.md` | `yes` |
| `docs/operations/final_release_verification_bundle.md` | `yes` |
| `docs/operations/project_release_closure_index.md` | `yes` |
| `docs/operations/CLUSTER_H_CLOSURE.md` | `yes` |
| `audits/reports/PR_INTEGRATION_SUMMARY.md` | `yes` |
| `docs/project_status.md` | `yes` |

## Snapshot Boundary

This release state snapshot records local repository state at generation time.
It does not replace CI logs, platform approvals, or release tag history.

## Command

```bash
make release-state-snapshot
```
