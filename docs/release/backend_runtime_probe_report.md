# Backend Runtime Probe Report

Generated at: `2026-05-16T16:59:31Z`

| Check | Return code | Command |
|---|---:|---|
| runtime probe fixtures | 0 | `/usr/bin/python3 scripts/check_backend_runtime_probe_fixtures.py` |
| runtime compatibility | 0 | `/usr/bin/python3 scripts/check_backend_runtime_compatibility.py` |
| execution packet | 0 | `/usr/bin/python3 scripts/check_backend_consolidation_execution_packet.py` |
| no-op guard | 0 | `/usr/bin/python3 scripts/check_backend_consolidation_noop_guard.py` |

## Boundary

This report validates fixture-based compatibility probes only. It does not approve runtime rewiring or deletion.

## runtime probe fixtures

Command: `/usr/bin/python3 scripts/check_backend_runtime_probe_fixtures.py`

Return code: `0`

```text
Backend runtime probe fixture check
- PASS [file] tests/fixtures/backend_consolidation/audit_canonical_events.json: present
- PASS [file] tests/fixtures/backend_consolidation/consent_runtime_events.json: present
- PASS [file] tests/fixtures/backend_consolidation/deep_readiness_expected_checks.json: present
Audit fixture probe: 2 event(s)
- PASS [audit] consent_granted: normalized
- PASS [audit] popia_export_requested: normalized
Consent fixture probe: 2 event(s)
- PASS [consent] consent_status_read: classified=read
- PASS [consent] consent_revoked: classified=write
Deep-readiness fixture probe: 7 check(s)
- PASS [readiness] database_connectivity: mode=read_only
- PASS [readiness] alembic_current_revision: mode=read_only
- PASS [readiness] required_core_tables: mode=read_only
- PASS [readiness] audit_persistence_available: mode=read_only
- PASS [readiness] consent_persistence_available: mode=read_only
- PASS [readiness] redis_connectivity: mode=ping_only
- PASS [readiness] audit_write_probe: mode=internal_only_disabled_by_default
- PASS backend runtime probe fixtures
```

## runtime compatibility

Command: `/usr/bin/python3 scripts/check_backend_runtime_compatibility.py`

Return code: `0`

```text
Audit runtime compatibility surface
- PASS [audit compat] AuditRepositoryCompatAdapter: present
- PASS [audit compat] AuditEventInput: present
- PASS [audit compat] normalize_audit_kwargs: present
- PASS [audit repository] exposes record/append/create-compatible method
Consent runtime compatibility surface
- PASS [consent compat] ConsentAuditEvent: present
- PASS [consent compat] normalize_consent_audit_event: present
- PASS [consent compat] classify_consent_action: present
- PASS [consent import] app.services.consent_service: importable
- PASS [consent import] app.modules.consent.service: importable
- PASS [consent import] app.services.popia_service: importable
Deep-health compatibility surface
- PASS [health contract] contains 'database connectivity'
- PASS [health contract] contains 'Alembic current revision'
- PASS [health contract] contains 'required core table presence'
- PASS backend runtime compatibility surface
```

## execution packet

Command: `/usr/bin/python3 scripts/check_backend_consolidation_execution_packet.py`

Return code: `0`

```text
Backend consolidation execution packet check
- PASS [file] docs/release/backend_consolidation_execution_packet.md: present
- PASS [content] docs/release/backend_consolidation_execution_packet.md: contains 'implementation sequencing only'
- PASS [content] docs/release/backend_consolidation_execution_packet.md: contains 'Explicitly forbidden'
- PASS [content] docs/release/backend_consolidation_execution_packet.md: contains 'alembic stamp head'
- PASS [file] docs/release/audit_canonicalization_implementation_checklist.md: present
- PASS [content] docs/release/audit_canonicalization_implementation_checklist.md: contains 'AuditRepositoryCompatAdapter'
- PASS [content] docs/release/audit_canonicalization_implementation_checklist.md: contains 'Legacy data retained'
- PASS [content] docs/release/audit_canonicalization_implementation_checklist.md: contains 'Deletion postponed'
- PASS [file] docs/release/consent_runtime_repair_checklist.md: present
- PASS [content] docs/release/consent_runtime_repair_checklist.md: contains 'ConsentService'
- PASS [content] docs/release/consent_runtime_repair_checklist.md: contains 'POPIADataRightsService'
- PASS [content] docs/release/consent_runtime_repair_checklist.md: contains 'Read/write authz preserved'
- PASS [file] docs/release/schema_drift_db_execution_checklist.md: present
- PASS [content] docs/release/schema_drift_db_execution_checklist.md: contains 'make migration-evidence-capture'
- PASS [content] docs/release/schema_drift_db_execution_checklist.md: contains 'make schema-drift-check-db'
- PASS [content] docs/release/schema_drift_db_execution_checklist.md: contains 'no blind stamp'
- PASS [file] docs/release/deep_readiness_implementation_checklist.md: present
- PASS [content] docs/release/deep_readiness_implementation_checklist.md: contains 'read-only'
- PASS [content] docs/release/deep_readiness_implementation_checklist.md: contains 'internal/admin only'
- PASS [content] docs/release/deep_readiness_implementation_checklist.md: contains 'must not write to the DB'
- PASS backend consolidation execution packet
```

## no-op guard

Command: `/usr/bin/python3 scripts/check_backend_consolidation_noop_guard.py`

Return code: `0`

```text
Backend consolidation no-op/deletion guard
- PASS [file] docs/release/backend_consolidation_readiness_matrix.md: present
- PASS [file] docs/release/backend_data_retention_decision_checklist.md: present
- PASS [file] docs/release/backend_consolidation_decision_record.md: present
- PASS [file] docs/release/backend_deletion_candidate_inventory.md: present
- PASS [decision] implementation decisions remain pending
- PASS [retention] default retention/destructive-decision safeguards present
- PASS [phrase] docs/release/backend_consolidation_decision_record.md: no forbidden approval phrase detected
- PASS [phrase] docs/release/backend_data_retention_decision_checklist.md: no forbidden approval phrase detected
- PASS [phrase] docs/release/backend_deletion_candidate_inventory.md: no forbidden approval phrase detected
- PASS [inventory] candidates default to not approved
- PASS backend consolidation no-op/deletion guard
```
