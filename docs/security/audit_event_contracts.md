# Audit Event Contracts

## Purpose

`scripts/check_audit_event_contracts.py` verifies that the POPIA and security
audit baseline still exposes the required audit markers.

## Required Coverage

- `FourthEstateService.record`
- consent grant/revoke audit events
- consent renewal audit event
- consent erasure-request audit event
- consent access-rejected audit event
- V2 consent router delegation to `ConsentService`

## Verification

```bash
make audit-contract-check
pytest -c pytest.ini tests/unit/test_audit_event_contracts.py -q --no-cov
```
