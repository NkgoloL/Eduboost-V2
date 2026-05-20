# Backend Consolidation Diagnostic Report

Generated at: `2026-05-19T22:59:25Z`

| Check | Return code | Command |
|---|---:|---|
| backend dragons | 0 | `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/check_backend_consolidation_dragons.py` |
| audit inventory | 0 | `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/generate_audit_callsite_inventory.py --fail-empty` |
| consent inventory | 0 | `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/generate_consent_callsite_inventory.py --fail-empty` |
| health readiness contract | 0 | `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/check_health_readiness_contract.py` |
| schema drift contract | 0 | `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/check_schema_drift_contract.py` |

## Interpretation

- This report is diagnostic evidence only.
- It does not approve deletion of audit or consent code.
- It does not approve consent table consolidation.
- It does not approve Alembic stamping/baselining.

## backend dragons

Command: `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/check_backend_consolidation_dragons.py`

Return code: `0`

```text
Backend consolidation dragon diagnostic
- audit_repository: 49 match(es)
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
  - scripts/check_auth_service_extraction.py
  - scripts/check_backend_runtime_compatibility.py
  - ... 8 more file(s)
- audit_events: 116 match(es)
  - alembic/versions/0006_v2_audit_events.py
  - alembic/versions/20260507_1200_popia_consent_audit_hardening.py
  - alembic/versions/20260507_1330_database_integrity_constraints.py
  - alembic/versions/20260510_0300_popia_consent_audit_dsr.py
  - alembic/versions/20260516_0100_remove_base_sentinel.py
  - alembic/versions/_deprecated/0001_phase2_baseline.py
  - alembic/versions/_deprecated/0001_schema_from_technical_report.py
  - app/core/database.py
  - app/core/health.py
  - app/models/__init__.py
  - app/repositories/audit_repository.py
  - app/services/data_subject_rights_service.py
  - ... 12 more file(s)
- audit_logs: 23 match(es)
  - alembic/versions/0001_v2_consolidated_schema.py
  - app/models/__init__.py
  - app/modules/disaster_recovery/production_readiness_contracts.py
  - app/services/audit_canonicalization_registry.py
  - scripts/check_backend_consolidation_dragons.py
  - scripts/check_backend_destructive_action_blocklist.py
  - scripts/check_first_audit_runtime_wiring_no_destructive_actions.py
  - scripts/generate_audit_callsite_inventory.py
  - scripts/generate_backend_deletion_candidate_inventory.py
  - scripts/generate_release_owner_beta_go_no_go.py
  - scripts/generate_truthful_release_owner_beta_go_no_go.py
  - tests/unit/test_backend_runtime_enablement_pack.py
  - ... 1 more file(s)
- consent_records: 18 match(es)
  - alembic/versions/20260510_0300_popia_consent_audit_dsr.py
  - app/repositories/consent_repository.py
  - app/services/data_subject_rights_service.py
  - scripts/check_backend_consolidation_dragons.py
  - scripts/check_first_audit_runtime_wiring_no_destructive_actions.py
  - scripts/check_runtime_wiring_no_destructive_actions.py
  - scripts/compare_orm_tables_to_database.py
  - scripts/generate_consent_callsite_inventory.py
  - tests/legacy/integration/test_api_contracts.py
  - tests/legacy/integration/test_parent_portal_integration.py
- parental_consents: 46 match(es)
  - alembic/versions/0001_v2_consolidated_schema.py
  - alembic/versions/20260505_1734_add_missing_production_indexes.py
  - alembic/versions/20260507_1200_popia_consent_audit_hardening.py
  - alembic/versions/20260507_1330_database_integrity_constraints.py
  - alembic/versions/_deprecated/0001_initial_consolidated_schema.py
  - alembic/versions/_deprecated/0001_schema_from_technical_report.py
  - app/models/__init__.py
  - app/services/popia_service.py
  - scripts/check_backend_consolidation_dragons.py
  - scripts/check_first_audit_runtime_wiring_no_destructive_actions.py
  - scripts/check_runtime_wiring_no_destructive_actions.py
  - scripts/generate_backend_deletion_candidate_inventory.py
  - ... 2 more file(s)
- consent_service: 140 match(es)
  - app/api_v2_deps/consent_lifecycle.py
  - app/api_v2_routers/consent.py
  - app/api_v2_routers/learners.py
  - app/api_v2_routers/parents.py
  - app/api_v2_routers/popia.py
  - app/core/consent_gate.py
  - app/modules/consent/__init__.py
  - app/modules/consent/service.py
  - app/modules/diagnostics/service.py
  - app/modules/lessons/service.py
  - app/security/dependencies.py
  - app/services/consent.py
  - ... 36 more file(s)
- deep_health: 29 match(es)
  - app/api_v2.py
  - app/core/health.py
  - scripts/check_backend_consolidation_dragons.py
  - scripts/check_runtime_entrypoints.py
  - scripts/check_runtime_release_evidence.py
  - scripts/generate_route_inventory.py
  - scripts/run_staging_smoke.py
  - tests/integration/test_deep_health.py
  - tests/test_entrypoints.py
  - tests/test_health_checks.py
  - tests/test_ready_endpoint.py
  - tests/unit/test_staging_smoke_tooling.py
- PASS backend consolidation dragons documented and inventoried
```

## audit inventory

Command: `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/generate_audit_callsite_inventory.py --fail-empty`

Return code: `0`

```text
Wrote /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/docs/release/audit_callsite_inventory.md (2343 row(s))
```

## consent inventory

Command: `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/generate_consent_callsite_inventory.py --fail-empty`

Return code: `0`

```text
Wrote /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/docs/release/consent_callsite_inventory.md (467 row(s))
```

## health readiness contract

Command: `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/check_health_readiness_contract.py`

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

Command: `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/check_schema_drift_contract.py`

Return code: `0`

```text
Schema drift contract check
- PASS [file] scripts/compare_orm_tables_to_database.py: present
- PASS [file] docs/release/schema_drift_evidence_contract.md: present
ORM tables
- audit_events
- audit_logs
- calibration_audits
- diagnostic_items
- diagnostic_sessions
- guardians
- irt_items
- item_exposures
- knowledge_gaps
- learner_profiles
- lesson_feedback
- lessons
- mastery_snapshots
- parental_consents
- practice_queue
- rlhf_exports
- spaced_review_schedule
- stripe_webhook_events
- subject_mastery
- topic_mastery
DATABASE_URL not supplied; database comparison skipped.

- PASS [command] ORM-only schema drift check runs without DB
```
