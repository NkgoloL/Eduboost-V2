# Gamification Consent Gate

## Routes

```text
GET /api/v2/gamification/profile/{learner_id}
POST /api/v2/gamification/award-xp
```

## Policy

Gamification profile reads and XP writes process learner data and must pass:

1. learner object authorization
2. active POPIA consent

## Verification

```bash
pytest -c pytest.ini tests/unit/test_gamification_consent_gate_wiring.py -q --no-cov
```
