# Active Consent Route Sources

## Purpose

All active-consent route boundaries should use the centralized consent adapter:

```python
require_active_consent_for_current_user
```

Routes should not call `ConsentService(db).require_active_consent` directly,
because centralization preserves consistent actor attribution and evidence
semantics.

## Command

```bash
make popia-consent-source-check
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_active_consent_route_sources.py -q --no-cov
```
