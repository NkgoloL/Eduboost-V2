# Backend Runtime Compatibility Report

Generated at: `2026-05-17T22:09:17Z`

| Check | Return code | Command |
|---|---:|---|
| runtime compatibility | 0 | `/usr/bin/python3 scripts/check_backend_runtime_compatibility.py` |
| audit compatibility | 0 | `/usr/bin/python3 scripts/generate_audit_callsite_inventory.py --fail-empty` |
| consent compatibility | 0 | `/usr/bin/python3 scripts/generate_consent_callsite_inventory.py --fail-empty` |
| health readiness | 0 | `/usr/bin/python3 scripts/check_health_readiness_contract.py` |

## Boundary

This report proves compatibility surfaces exist. It does not approve deletion, table merging, or runtime rewiring.

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

## audit compatibility

Command: `/usr/bin/python3 scripts/generate_audit_callsite_inventory.py --fail-empty`

Return code: `0`

```text
Wrote /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/docs/release/audit_callsite_inventory.md (1833 row(s))
```

## consent compatibility

Command: `/usr/bin/python3 scripts/generate_consent_callsite_inventory.py --fail-empty`

Return code: `0`

```text
Wrote /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/docs/release/consent_callsite_inventory.md (396 row(s))
```

## health readiness

Command: `/usr/bin/python3 scripts/check_health_readiness_contract.py`

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
