# Consent Renewal Admin Authorization Boundary

## Endpoint

```text
POST /api/v2/admin/consent/trigger-renewal-reminders
```

## Policy

The route is an operational/admin trigger and is protected with:

```python
Depends(require_admin)
```

The learner-authorization matrix now recognizes `require_admin` as an
authorization marker, so this route is tracked as covered rather than
allowlisted.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_consent_renewal_admin_auth_boundary.py -q --no-cov
make learner-authz-check
```
