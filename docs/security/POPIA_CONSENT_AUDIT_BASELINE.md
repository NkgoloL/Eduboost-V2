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

## POPIA Consent Gate Check

- `make popia-consent-gate-check` guards consent-gate inventory drift.

## POPIA Consent Audit CI

- `.github/workflows/popia-consent-audit.yml` runs consent/audit drift checks in CI.

## POPIA Consent Dependency Adapter

- `app/security/dependencies.py` exposes `require_active_consent_for_current_user` for route-level consent gates.

## Study Plan Consent Gate

- Study-plan generation routes require active POPIA consent before job enqueue.

## Learner Read Consent Gate

- Learner read/mastery routes use centralized active-consent gates after read authorization.

## Gamification Consent Gate

- Gamification profile and award-xp routes use centralized active-consent gates after object authorization.

## Parent Routes Consent Gate

- Parent dashboard/export/progress learner-data reads use centralized active-consent gates.

## POPIA Data-Rights Consent Boundary

- POPIA data export requires active consent; DSR workflows remain object-authorized rights-exercise routes.

## Assessment Consent Gate

- Assessment attempt submission requires active POPIA consent; assessment list remains an authenticated catalog boundary.

## Onboarding Consent Gate

- Onboarding submit/archetype routes require active POPIA consent; questions remains an authenticated catalog boundary.

## Ether Onboarding Consent Gate

- Ether onboarding submit requires active POPIA consent.

## Ether Onboarding Consent Boundary

- Ether onboarding submit is authenticated but not learner-scoped; canonical onboarding writes carry active consent.

## POPIA Consent Gate Closure

- `docs/security/POPIA_CONSENT_GATE_CLOSURE.md` records first-pass consent-gate closure evidence.

## POPIA Consent CI Closure

- POPIA CI includes boundary, route-order, and consent-rejection audit checks.

## Diagnostics Central Consent Source

- Diagnostics active-consent routes use central consent adapter source only.

## POPIA Negative Consent Evidence

- Negative consent evidence includes denial-path and route-source guards.
