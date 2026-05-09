# POPIA Consent and Audit Baseline

## Scope

This baseline starts the next security cluster after Phase 2 authorization
closure. It records the existing consent lifecycle and audit-event guarantees
before adding stricter consent gates to learner-data routes.

## Existing Components

| Component | Responsibility |
| --- | --- |
| `app/modules/consent/service.py` | consent lifecycle, active-consent enforcement, audit append fallback |
| `app/core/audit.py` | durable Fourth Estate audit event service |
| `app/api_v2_routers/consent.py` | V2 consent grant/revoke/status route surface |
| `scripts/generate_consent_gate_inventory.py` | learner-related consent-gate candidate inventory |
| `scripts/check_audit_event_contracts.py` | baseline audit marker check |

## Verification

```bash
python3 scripts/generate_consent_gate_inventory.py
make audit-contract-check
pytest -c pytest.ini tests/unit/test_generate_consent_gate_inventory.py tests/unit/test_audit_event_contracts.py -q --no-cov
```

## Next Hardening Targets

1. Convert consent-gate inventory candidates into explicit route/service gates.
2. Add request-level audit evidence for consent-protected reads and writes.
3. Add CI drift protection for consent and audit contracts.
