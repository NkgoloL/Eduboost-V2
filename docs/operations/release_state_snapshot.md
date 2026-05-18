# Release State Snapshot

## Metadata

- generated_at_utc: `2026-05-18T08:39:37.235851+00:00`
- branch: `fix/github-ci-cd-errors`
- commit: `996786f9faffec5ada9651e9637d40c3ce574e97`
- release_candidate: `unset`

## Working Tree Status

```text
M .env.example
 M Makefile
 M app/core/security.py
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
 M docs/release/beta_readiness_status.json
 M docs/release/branch_protection_evidence.json
 M docs/release/branch_protection_evidence.md
 M docs/release/ci_evidence.json
 M docs/release/ci_evidence.md
 M docs/release/disposable_db_schema_proof_execution_report.md
 M docs/release/first_audit_runtime_wiring_report.md
 M docs/release/release_owner_beta_go_no_go_memo.md
 M docs/release/runtime_wiring_431_450_report.md
 M docs/release/schema_drift_disposable_latest.json
 M docs/release/schema_drift_disposable_latest.md
 M docs/release/staging_smoke_final_evidence.json
 M docs/release/staging_smoke_final_evidence.md
?? app/services/jwt_keyring.py
?? docs/architecture/auth_service_extraction_followup.json
?? docs/architecture/auth_service_extraction_followup.md
?? docs/release/next_content_ops_evidence_queue.md
?? docs/security/dependency_constraints_snapshot.md
?? docs/security/dependency_pin_report.json
?? docs/security/dependency_pin_report.md
?? docs/security/jwt_rotation_introspection.json
?? docs/security/jwt_rotation_introspection.md
?? docs/security/jwt_rotation_plan.md
?? docs/security/jwt_rotation_repair_report.md
?? docs/security/pip_audit_report.md
?? requirements/constraints.snapshot.txt
?? scripts/check_jwt_rotation.py
?? scripts/generate_auth_extraction_followup.py
?? scripts/generate_constraints_snapshot.py
?? scripts/generate_dependency_pin_report.py
?? scripts/inspect_jwt_rotation.py
?? scripts/repair_jwt_rotation.py
?? scripts/run_optional_pip_audit.py
?? tests/unit/test_jwt_rotation_dependency_security.py
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
