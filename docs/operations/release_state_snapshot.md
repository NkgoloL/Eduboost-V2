# Release State Snapshot

## Metadata

- generated_at_utc: `2026-05-17T22:12:28.718701+00:00`
- branch: `codex/production_readiness`
- commit: `02f3babd855703460eefc1727f5fdc71f44d2a60`
- release_candidate: `unset`

## Working Tree Status

```text
M Makefile
 M app/api_v2_routers/diagnostics.py
 M app/core/jobs.py
 M app/modules/jobs.py
 M docs/ai/ai_prompt_surface_inventory.md
 M docs/architecture/import_linter_availability.md
 M docs/architecture/import_linter_contract_run.md
 M docs/architecture/legacy_learner_access_guard_report.json
 M docs/architecture/legacy_learner_access_guard_report.md
 M docs/architecture/router_repository_boundary_matrix.json
 M docs/architecture/router_repository_boundary_matrix.md
 M docs/architecture/router_service_dependency_map.json
 M docs/architecture/router_service_dependency_map.md
 M docs/architecture/service_boundary_inventory.json
 M docs/architecture/service_boundary_inventory.md
 M docs/architecture/service_family_map.json
 M docs/architecture/service_family_map.md
 M docs/beta/beta_content_hard_gate.json
 M docs/beta/beta_content_hard_gate.md
 M docs/operations/beta_release_evidence_bundle.md
 M docs/operations/beta_release_pr_body.md
 M docs/operations/beta_signoff_manifest.md
 M docs/operations/database_backup_manifest.md
 M docs/operations/database_restore_evidence.md
 M docs/operations/release_candidate_tag_manifest.md
 M docs/operations/release_evidence_manifest.md
 M docs/operations/staging_smoke_evidence_manifest.md
 M docs/release/EVIDENCE_INDEX.md
 M docs/release/alertmanager_drill_evidence.json
 M docs/release/audit_callsite_inventory.md
 M docs/release/backend_consolidation_diagnostic_report.md
 M docs/release/backend_consolidation_evidence_manifest.md
 M docs/release/backend_consolidation_execution_report.md
 M docs/release/backend_consolidation_implementation_foundation_report.md
 M docs/release/backend_consolidation_progress_report.md
 M docs/release/backend_consolidation_readiness_report.md
 M docs/release/backend_consolidation_terminal_report.md
 M docs/release/backend_deletion_candidate_inventory.md
 M docs/release/backend_first_wiring_candidates_report.md
 M docs/release/backend_implementation_371_375_report.md
 M docs/release/backend_runtime_compatibility_report.md
 M docs/release/backend_runtime_enablement_report.md
 M docs/release/backend_runtime_integration_readiness_report.md
 M docs/release/backend_runtime_probe_report.md
 M docs/release/backend_runtime_wiring_cases_report.md
 M docs/release/backend_runtime_wiring_preflight_report.md
 M docs/release/backup_drill_evidence.json
 M docs/release/backup_drill_evidence.md
 M docs/release/beta_evidence_integrity_repair_report.json
 M docs/release/beta_evidence_integrity_repair_report.md
 M docs/release/beta_readiness_status.json
 M docs/release/branch_protection_evidence.json
 M docs/release/branch_protection_evidence.md
 M docs/release/ci_evidence.json
 M docs/release/ci_evidence.md
 M docs/release/consent_callsite_inventory.md
 M docs/release/disposable_db_schema_proof_execution_report.md
 M docs/release/first_audit_runtime_wiring_report.md
 M docs/release/release_owner_beta_go_no_go_memo.md
 M docs/release/restore_drill_evidence.json
 M docs/release/rollback_drill_evidence.json
 M docs/release/runtime_wiring_431_450_report.md
 M docs/release/schema_drift_disposable_latest.json
 M docs/release/schema_drift_disposable_latest.md
 M docs/release/staging_smoke_final_evidence.json
 M docs/release/staging_smoke_final_evidence.md
?? app/services/diagnostic_data_integrity.py
?? app/services/job_runtime_integrity.py
?? docs/release/arq_consent_job_repair_report.md
?? docs/release/diagnostics_data_integrity_repair_report.md
?? docs/release/diagnostics_jobs_integrity_introspection.json
?? docs/release/diagnostics_jobs_integrity_introspection.md
?? docs/release/diagnostics_jobs_remaining_blockers.md
?? scripts/check_diagnostics_jobs_integrity.py
?? scripts/inspect_diagnostics_and_jobs_integrity.py
?? scripts/repair_arq_consent_reminder_job.py
?? scripts/repair_diagnostics_data_integrity.py
?? tests/unit/test_diagnostics_jobs_integrity_contracts.py
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
| `PR_INTEGRATION_SUMMARY.md` | `yes` |
| `docs/project_status.md` | `yes` |

## Snapshot Boundary

This release state snapshot records local repository state at generation time.
It does not replace CI logs, platform approvals, or release tag history.

## Command

```bash
make release-state-snapshot
```
