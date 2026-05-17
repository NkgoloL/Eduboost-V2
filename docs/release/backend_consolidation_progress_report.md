# Backend Consolidation Progress Report

Generated at: `2026-05-17T09:35:55Z`

| Check | Return code | Command |
|---|---:|---|
| consent runtime compatibility | 0 | `/usr/bin/python3 scripts/check_consent_runtime_compatibility_slice.py` |
| audit registry | 0 | `/usr/bin/python3 scripts/check_audit_canonicalization_registry.py` |
| implementation foundation | 0 | `/usr/bin/python3 scripts/check_backend_consolidation_implementation_foundation.py` |
| schema/deep/audit slice | 0 | `/usr/bin/python3 scripts/check_audit_canonicalization_slice.py` |

## Boundary

This report tracks non-destructive implementation progress only.

## consent runtime compatibility

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

## implementation foundation

Command: `/usr/bin/python3 scripts/check_backend_consolidation_implementation_foundation.py`

Return code: `0`

```text
Backend consolidation implementation foundation check
- PASS [file] app/services/backend_consolidation_runtime.py: present
- PASS [content] app/services/backend_consolidation_runtime.py: contains 'record_canonical_audit_event'
- PASS [content] app/services/backend_consolidation_runtime.py: contains 'record_consent_audit_event'
- PASS [content] app/services/backend_consolidation_runtime.py: contains 'probe_constructor'
- PASS [file] docs/adr/ADR-022-audit-consent-table-ownership-options.md: present
- PASS [content] docs/adr/ADR-022-audit-consent-table-ownership-options.md: contains 'Option A'
- PASS [content] docs/adr/ADR-022-audit-consent-table-ownership-options.md: contains 'Option B'
- PASS [content] docs/adr/ADR-022-audit-consent-table-ownership-options.md: contains 'Option C'
- PASS [content] docs/adr/ADR-022-audit-consent-table-ownership-options.md: contains 'Option D'
- PASS [content] docs/adr/ADR-022-audit-consent-table-ownership-options.md: contains 'Not approved'
- PASS [file] docs/release/backend_consolidation_implementation_foundation.md: present
- PASS [content] docs/release/backend_consolidation_implementation_foundation.md: contains 'non-destructive implementation foundation'
- PASS [content] docs/release/backend_consolidation_implementation_foundation.md: contains 'Explicitly excluded'
- PASS [compile] backend_consolidation_runtime.py
- PASS backend consolidation implementation foundation
```

## schema/deep/audit slice

Command: `/usr/bin/python3 scripts/check_audit_canonicalization_slice.py`

Return code: `0`

```text
Audit canonicalization slice check
- PASS audit canonicalization slice
```
