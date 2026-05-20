# Backend First Wiring Candidates Report

Generated at: `2026-05-19T23:00:32Z`

| Check | Return code | Command |
|---|---:|---|
| first wiring candidates | 0 | `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/check_backend_first_wiring_candidates.py` |
| runtime wiring cases | 0 | `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/check_backend_runtime_wiring_cases.py` |
| runtime wiring preflight | 0 | `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/check_backend_runtime_wiring_preflight.py` |

## Boundary

This report proves first wiring candidates only; it does not approve route rewiring or destructive changes.

## first wiring candidates

Command: `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/check_backend_first_wiring_candidates.py`

Return code: `0`

```text
Backend first wiring candidate check
- PASS safe wiring candidates: 4
- PASS no unsafe wiring candidates in registry
- PASS payloads generated for all safe candidates: 4
- PASS adapter recording: recorded 4 safe candidate(s)
- PASS [doc] docs/release/backend_first_wiring_candidate_registry.md: present
- PASS [doc] docs/release/backend_adapter_wiring_service_contract.md: present
- PASS [doc] docs/release/backend_implementation_slice_391_400.md: present
- PASS [doc] docs/release/deep_readiness_route_implementation_gate.md: present
- PASS [doc] docs/release/schema_drift_real_db_execution_blocker.md: present
- PASS backend first wiring candidates
```

## runtime wiring cases

Command: `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/check_backend_runtime_wiring_cases.py`

Return code: `0`

```text
Backend runtime wiring fixture case check
- PASS [file] tests/fixtures/backend_consolidation/audit_runtime_wiring_cases.json: present
- PASS [file] tests/fixtures/backend_consolidation/consent_runtime_wiring_cases.json: present
- PASS [file] tests/fixtures/backend_consolidation/deep_readiness_route_wiring_cases.json: present
- PASS [file] docs/release/backend_runtime_wiring_fixture_contract.md: present
- PASS [file] docs/release/backend_runtime_wiring_test_pack.md: present
- PASS [consent_granted_canonical_event] audit fixture maps to canonical payload: {'payload': {'action': 'consent.granted', 'actor_id': 'guardian-fixture', 'resource_type': 'learner_consent', 'resource_id': 'learner-fixture', 'payload': {'migration_candidate': 'consent_audit_events', 'learner_id': 'learner-fixture'}}}
- PASS [popia_export_requested_canonical_event] audit fixture maps to canonical payload: {'payload': {'action': 'popia.export.requested', 'actor_id': 'guardian-fixture', 'resource_type': 'popia_data_export', 'resource_id': 'learner-fixture', 'payload': {'migration_candidate': 'popia_data_rights_audit', 'learner_id': 'learner-fixture'}}}
- PASS [consent_granted_write] consent fixture maps to audit-compatible payload: {'payload': {'action': 'consent.granted', 'actor_id': 'guardian-fixture', 'resource_type': 'learner_consent', 'resource_id': 'learner-fixture', 'metadata': {'learner_id': 'learner-fixture', 'operation_type': 'write', 'consent_runtime_orchestrated': True}}}
- PASS [consent_status_read] consent fixture maps to audit-compatible payload: {'payload': {'action': 'consent.status.read', 'actor_id': 'guardian-fixture', 'resource_type': 'learner_consent', 'resource_id': 'learner-fixture', 'metadata': {'learner_id': 'learner-fixture', 'operation_type': 'read', 'consent_runtime_orchestrated': True}}}
- PASS [database_connectivity] deep-readiness fixture matches catalogue: {'mode': 'deep_readonly', 'dependency': 'database', 'public_safe': True, 'mutates_state': False, 'required_for_release': True}
- PASS [alembic_revision] deep-readiness fixture matches catalogue: {'mode': 'deep_readonly', 'dependency': 'database_schema', 'public_safe': True, 'mutates_state': False, 'required_for_release': True}
- PASS [required_table_presence] deep-readiness fixture matches catalogue: {'mode': 'deep_readonly', 'dependency': 'database_schema', 'public_safe': True, 'mutates_state': False, 'required_for_release': True}
- PASS [mutating_audit_probe] deep-readiness fixture matches catalogue: {'mode': 'internal_mutating', 'dependency': 'audit', 'public_safe': False, 'mutates_state': True, 'required_for_release': False}
- PASS backend runtime wiring fixture cases
```

## runtime wiring preflight

Command: `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/check_backend_runtime_wiring_preflight.py`

Return code: `0`

```text
Backend runtime wiring preflight check
- PASS [audit] audit adapter-ready candidate produces canonical payload: {'candidate': 'consent_audit_events', 'payload_keys': ['action', 'actor_id', 'payload', 'resource_id', 'resource_type']}
- PASS [consent] consent runtime normalization and constructor probes are stable: {'importable_surfaces': 3, 'missing_surfaces': 0, 'required_parameter_total': 3}
- PASS [deep_readiness] deep-readiness catalogue separates public read-only checks from unsafe probes: {'public_check_count': 5, 'unsafe_public_check_count': 0, 'public_checks': ['database_connectivity', 'alembic_revision', 'required_table_presence', 'audit_persistence_capability', 'consent_persistence_capability']}
- PASS [schema_drift] schema-drift runtime wiring is gated by disposable DB proof commands: {'requires_real_disposable_db': True, 'forbidden_repairs': ['alembic stamp head', 'production DB mutation']}
- PASS [doc] docs/release/backend_runtime_wiring_preflight.md: present
- PASS [doc] docs/release/backend_implementation_decision_ledger.md: present
- PASS [doc] docs/release/backend_implementation_terminal_progress_packet.md: present
- PASS [doc] docs/release/schema_drift_execution_gate_hardening.md: present
- PASS [ledger] contains 'destructive decisions default to blocked'
- PASS [ledger] contains 'alembic stamp head'
- PASS [ledger] contains 'blocked'
- PASS backend runtime wiring preflight
```
