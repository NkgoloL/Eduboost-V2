# Backend Implementation 371-375 Report

Generated at: `2026-05-17T22:09:49Z`

| Check | Return code | Command |
|---|---:|---|
| backend implementation 371-375 | 0 | `/usr/bin/python3 scripts/check_backend_implementation_371_375.py` |
| audit registry | 0 | `/usr/bin/python3 scripts/check_audit_canonicalization_registry.py` |
| consent runtime | 0 | `/usr/bin/python3 scripts/check_consent_runtime_compatibility_slice.py` |
| deep readiness | 0 | `/usr/bin/python3 scripts/check_deep_readiness_readonly_guard.py` |

## Boundary

This report proves non-destructive implementation progress only.

## backend implementation 371-375

Command: `/usr/bin/python3 scripts/check_backend_implementation_371_375.py`

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

## audit registry

Command: `/usr/bin/python3 scripts/check_audit_canonicalization_registry.py`

Return code: `0`

```text
Audit canonicalization migration registry check
- PASS ready non-destructive candidates: 2
  - consent_audit_events: migration_ready
  - popia_data_rights_audit: adapter_ready
- PASS no destructive candidates are marked ready
- PASS audit migration registry doc present
```

## consent runtime

Command: `/usr/bin/python3 scripts/check_consent_runtime_compatibility_slice.py`

Return code: `0`

```text
Consent runtime compatibility slice check
- PASS consent operation normalizes to audit-compatible write event
- PASS constructor probes returned 3 surface(s)
- PASS probe app.services.consent_service.ConsentService: importable=True, class_found=True, required=('consent_repo', 'audit_repo'), error=None
- PASS probe app.modules.consent.service.ConsentService: importable=True, class_found=True, required=(), error=None
- PASS probe app.services.popia_service.POPIADataRightsService: importable=True, class_found=True, required=('db',), error=None
- PASS consent compatibility slice doc present
```

## deep readiness

Command: `/usr/bin/python3 scripts/check_deep_readiness_readonly_guard.py`

Return code: `0`

```text
Deep-readiness read-only guard
- PASS [specs] 5 read-only readiness specs
- PASS [guard] rejected 'session.commit()'
- PASS [guard] rejected 'INSERT INTO audit_events'
- PASS [guard] rejected 'alembic stamp head'
- PASS [contract] deep readiness checklist present
- PASS deep-readiness read-only guard
```
