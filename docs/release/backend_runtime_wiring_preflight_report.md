# Backend Runtime Wiring Preflight Report

Generated at: `2026-05-19T23:01:43Z`

| Check | Return code | Command |
|---|---:|---|
| runtime wiring preflight | 0 | `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/check_backend_runtime_wiring_preflight.py` |
| implementation 371-375 | 0 | `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/check_backend_implementation_371_375.py` |
| implementation progress | 0 | `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/generate_backend_consolidation_progress_report.py` |
| schema drift disposable proof dry-run | 0 | `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/run_disposable_schema_drift_proof.py --database-url postgresql+asyncpg://real_user:real_password@localhost:5432/eduboost_test --dry-run` |

## Boundary

This report does not approve runtime wiring or destructive changes.

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

## implementation 371-375

Command: `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/check_backend_implementation_371_375.py`

Return code: `0`

```text
Backend implementation 371-375 check
- PASS audit migration allowed candidates: ('consent_audit_events', 'popia_data_rights_audit')
- PASS audit migration event maps learner to resource
- PASS consent runtime payload classifies write
- PASS consent probe summary: importable=3, missing=0, required_params=3
- PASS no unsafe public deep-readiness checks
- PASS deep-readiness required/public check catalogue present
- PASS [doc] docs/release/backend_implementation_slice_371_375.md: present
- PASS [doc] docs/release/audit_callsite_migration_slice_002.md: present
- PASS [doc] docs/release/consent_runtime_repair_slice_002.md: present
- PASS [doc] docs/release/deep_readiness_route_contract_slice_002.md: present
- PASS [doc] docs/release/schema_drift_execution_state.md: present
```

## implementation progress

Command: `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/generate_backend_consolidation_progress_report.py`

Return code: `0`

```text
Wrote /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/docs/release/backend_consolidation_progress_report.md
```

## schema drift disposable proof dry-run

Command: `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/run_disposable_schema_drift_proof.py --database-url postgresql+asyncpg://real_user:real_password@localhost:5432/eduboost_test --dry-run`

Return code: `0`

```text
{
  "captured_at": "2026-05-19T23:01:43Z",
  "database_url_redacted": "postgresql+asyncpg://real_user:***@localhost:5432/eduboost_test",
  "dry_run": true,
  "passed": true,
  "results": [
    {
      "command": [
        "/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python",
        "scripts/capture_migration_evidence.py"
      ],
      "name": "migration_evidence_capture",
      "output": "dry-run",
      "passed": true,
      "return_code": 0
    },
    {
      "command": [
        "/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python",
        "scripts/capture_migration_evidence.py",
        "--validate",
        "--require-pass"
      ],
      "name": "migration_evidence_check",
      "output": "dry-run",
      "passed": true,
      "return_code": 0
    },
    {
      "command": [
        "/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python",
        "scripts/compare_orm_tables_to_database.py",
        "--require-db",
        "--fail-on-drift"
      ],
      "name": "schema_drift_db",
      "output": "dry-run",
      "passed": true,
      "return_code": 0
    }
  ]
}
```
