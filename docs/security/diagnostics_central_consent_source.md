# Diagnostics Central Consent Source

## Purpose

Diagnostics routes must use the centralized active-consent adapter and must not
call `ConsentService(db).require_active_consent` directly.

## Covered Routes

```text
GET /api/v2/diagnostics/items/{learner_id}
POST /api/v2/diagnostics/submit
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_diagnostics_central_consent_source.py -q --no-cov
make popia-consent-source-check
```
