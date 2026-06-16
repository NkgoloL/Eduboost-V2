# Phase 2R Gate 2R.0 Closure Report

**Generated:** 2026-06-16T11:12:21Z
**Status:** Failed / remediation required
**Branch:** `feature/atlas-phase-02r-authoritative-caps-corpus`
**baseline_capture_sha:** `8d972b5f229fc5595e486e0649f0223405c55932`
**base_against_origin_master:** `4b3805b700869aaeacce4141bb565e1963777163`
**gate_report_commit_sha:** pending until this report is committed
**eventual_gate_approval_commit_sha:** not issued

## Result

Gate 2R.0 closure evidence was collected. The approval flag must remain
`PHASE_02R_START_APPROVED=false` unless every raw command exits zero and the
worktree is clean.

## Source State

```text
 M .gitignore
 D .phase4-backup-20260615T085507Z/app/api_v2.py
 D .phase4-backup-20260615T085507Z/app/core/metrics.py
 D .phase4-backup-20260615T085507Z/app/models/__init__.py
 D .phase4-backup-20260615T085507Z/app/models/diagnostic_item.py
 D .phase4-backup-20260615T085507Z/app/modules/diagnostics/item_bank_service.py
 D .phase4-backup-20260615T085507Z/app/modules/jobs.py
 D .phase4-backup-20260615T085507Z/docs/roadmap/PHASE_STATUS_REGISTER.md
 D .phase5-backup-20260615T113102Z/.env.example
 D .phase5-backup-20260615T113102Z/app/api_v2.py
 D .phase5-backup-20260615T113102Z/app/core/config.py
 D .phase5-backup-20260615T113102Z/app/core/metrics.py
 D .phase5-backup-20260615T113102Z/app/frontend/src/components/eduboost/InteractiveLesson.tsx
 D .phase5-backup-20260615T113102Z/app/models/__init__.py
 D .phase5-backup-20260615T113102Z/docs/roadmap/PHASE_STATUS_REGISTER.md
 D .phase6-backup-20260615T135247Z/app/api_v2.py
 D .phase6-backup-20260615T135247Z/app/core/config.py
 D .phase6-backup-20260615T135247Z/app/core/metrics.py
 D .phase6-backup-20260615T135247Z/app/models/__init__.py
 D .phase6-backup-20260615T135247Z/app/modules/jobs.py
 D .phase6-backup-20260615T135247Z/app/services/content_generation/provider_factory.py
 D .phase6-backup-20260615T135247Z/app/services/learner_tutor.py
 D .phase6-backup-20260615T135247Z/docs/openapi.json
 D .phase6-backup-20260615T135247Z/docs/roadmap/PHASE_STATUS_REGISTER.md
 D .phase7-backup-20260615T151055Z/.gitignore
 D .phase7-backup-20260615T151055Z/app/api_v2.py
 D .phase7-backup-20260615T151055Z/app/core/config.py
 D .phase7-backup-20260615T151055Z/app/core/metrics.py
 D .phase7-backup-20260615T151055Z/app/models/__init__.py
 D .phase7-backup-20260615T151055Z/app/modules/jobs.py
 D .phase7-backup-20260615T151055Z/docs/openapi.json
 D .phase7-backup-20260615T151055Z/docs/roadmap/PHASE_STATUS_REGISTER.md
 M app/api_v2_routers/content_review.py
 M app/api_v2_routers/curriculum_expansion.py
 M app/domain/content_review_schemas.py
 M app/models/__init__.py
 M app/models/content_factory.py
 M app/models/curriculum_expansion.py
 M app/modules/diagnostics/item_bank_service.py
 M app/services/ai_operations.py
 M app/services/content_file_artifact_import.py
 M app/services/content_review_governance.py
 M app/services/curriculum_expansion.py
 M app/services/semantic_retrieval/indexing.py
 M app/services/semantic_retrieval/repository.py
 M app/services/semantic_retrieval/service.py
 M data/retrieval/phase2_evaluation_set.json
 M docs/docs_inventory.md
 D docs/release-evidence/atlas/phase-04/raw/SHA256SUMS
 M docs/release-evidence/atlas/phase-05/raw/SHA256SUMS.txt
 M docs/release-evidence/atlas/phase-06/phase_06_audit_report.md
 M docs/release-evidence/atlas/phase-06/phase_06_evidence_index.md
 M docs/release-evidence/atlas/phase-07/raw/SHA256SUMS.txt
 D docs/release-evidence/phase-02/phase2_live_closure_evidence.json
 D docs/release-evidence/phase-02/phase2_live_closure_evidence.md
 D docs/release-evidence/phase-02/phase_02_audit_report.md
 D docs/release-evidence/phase-02/phase_02_evidence_index.md
 D docs/release-evidence/phase-03/phase_01_02_integration_audit.md
 D docs/release-evidence/phase-03/phase_03_audit_report.md
 D docs/release-evidence/phase-03/phase_03_evidence_index.md
 D docs/release-evidence/phase-03/raw/environment.txt
 D docs/release-evidence/phase-03/raw/migration_graph.txt
 D docs/release-evidence/phase-03/raw/phase3_fast_verification.txt
 D docs/release-evidence/phase-03/raw/phase3_postgres_verification.txt
 D docs/release-evidence/phase-03/raw/ruff.txt
 M docs/roadmap/EduBoost_Full_Lifecycle_Delivery_and_Beta_Readiness_Plan.md
 M docs/roadmap/PHASE_QUICK_REFERENCE.md
 M docs/roadmap/PHASE_STATUS_REGISTER.md
 M docs/roadmap/README.md
 M docs/roadmap/execution/atlas/phase_02r_execution_plan.md
 M docs/roadmap/execution/atlas/phase_02r_gate_2r0_report.md
 M docs/roadmap/execution/atlas/phase_06_implementation_report.md
 D docs/roadmap/execution/phase_02_execution_plan.md
 D docs/roadmap/execution/phase_02_implementation_report.md
 D docs/roadmap/execution/phase_03_execution_plan.md
 D docs/roadmap/execution/phase_03_implementation_report.md
 D docs/roadmap/execution/phase_1_execution_plan.md
 D docs/roadmap/execution/phase_1_implementation_report.md
 D docs/roadmap/execution/phase_3_execution_plan.md
 D docs/roadmap/execution/phase_3_implementation_report.md
 D docs/roadmap/execution/phase_4_execution_plan.md
 D docs/roadmap/execution/phase_4_implementation_report.md
 D docs/roadmap/execution/phase_5_execution_plan.md
 D docs/roadmap/execution/phase_5_implementation_report.md
 D docs/roadmap/execution/phase_6_execution_plan.md
 D docs/roadmap/execution/phase_7_execution_plan.md
 D docs/roadmap/execution/phase_7_implementation_report.md
 M docs/roadmap/execution/phase_evidence_pack_template.md
 M docs/roadmap/execution/phase_execution_plan_template.md
 M scripts/phase2_evaluate_retrieval.py
 M tests/phase02/test_service.py
?? alembic/versions/20260615_2100_p17_reconcile.py
?? app/services/content_answer_key_verification.py
?? data/retrieval/phase2_closure_evaluation_v2.json
?? docs/archive/legacy-phase-controls/
?? docs/release-evidence/atlas/phase-02/
?? docs/release-evidence/atlas/phase-02r/
?? docs/release-evidence/atlas/phase-03/
?? docs/release-evidence/atlas/phase-04/raw/REVALIDATION_REQUIRED.txt
?? docs/release-evidence/atlas/phase-04/raw/SHA256SUMS.txt
?? docs/release-evidence/atlas/phase-05/raw/REVALIDATION_REQUIRED.txt
?? docs/release-evidence/atlas/phase-06/raw/REVALIDATION_REQUIRED.txt
?? docs/release-evidence/atlas/phase-06/raw/SHA256SUMS.txt
?? docs/release-evidence/atlas/phase-07/raw/REVALIDATION_REQUIRED.txt
?? docs/release-evidence/atlas/programme-reconciliation-01-07/
?? docs/roadmap/execution/atlas/phase_00_execution_plan.md
?? docs/roadmap/execution/atlas/phase_02_execution_plan.md
?? docs/roadmap/execution/atlas/phase_02_implementation_report.md
?? docs/roadmap/execution/atlas/phase_02r_gate_2r0_closure_report.md
?? docs/roadmap/execution/atlas/phase_03_execution_plan.md
?? docs/roadmap/execution/atlas/phase_03_governance_revalidation_addendum.md
?? docs/roadmap/execution/atlas/phase_03_implementation_report.md
?? docs/roadmap/execution/atlas/phases_01_07_reconciliation_plan.md
?? scripts/apply_phase02r_patch.sh
?? scripts/collect_phase02r_evidence.sh
?? scripts/collect_phases_01_07_reconciliation_evidence.sh
?? scripts/collect_phases_01_07_reconciliation_evidence_impl.sh
?? scripts/preflight_phase02r.sh
?? scripts/validate_phase2_evaluation_dataset.py
?? scripts/validate_phase_control_sets.py
?? scripts/validate_phase_identifier_compatibility.py
?? scripts/verify_phase02r.sh
?? scripts/verify_phase0_or_equivalent_baseline.py
?? scripts/verify_phase2_retrieval_fallback_hotfix.sh
?? scripts/verify_phases_01_07_reconciliation.sh
?? scripts/verify_phases_01_07_reconciliation_postgres.sh
?? tests/reconciliation/
```

## Evidence

See `docs/release-evidence/atlas/phase-02r/gate-2r0/`.

## Recommendation

Gate 2R.1 remains blocked. Remediate the failing raw commands before approval.
