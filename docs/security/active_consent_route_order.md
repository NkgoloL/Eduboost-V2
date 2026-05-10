# Active Consent Route Order

## Policy

Evidence phrase: object authorization must run before active POPIA consent.


For learner-scoped routes, object authorization must run before active POPIA
consent enforcement.

That order prevents consent checks from becoming an oracle for unauthorized
actors.

## Command

```bash
make popia-consent-order-check
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_active_consent_route_order.py -q --no-cov
```
