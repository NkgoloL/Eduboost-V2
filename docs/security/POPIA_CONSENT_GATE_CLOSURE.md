# POPIA Consent Gate Closure Report

## Scope

This report closes the first POPIA consent-gate wiring pass for learner-data
routes.

## Evidence

| Evidence | Command |
| --- | --- |
| Consent-gate inventory | `make popia-consent-gate-check` |
| Audit-event contract | `make audit-contract-check` |
| POPIA aggregate evidence | `make popia-consent-audit-check` |
| Explicit consent-boundary matrix | `make popia-consent-boundary-check` |

## Boundary Decisions

| Decision | Meaning |
| --- | --- |
| `active_consent_required` | learner-data processing requires active parental consent |
| `rights_exercise_not_active_consent_blocked` | data-subject rights routes remain available even after consent withdrawal/expiry |
| `authenticated_catalog_boundary` | authenticated but not learner-record processing |
| `non_learner_scoped` | outside learner-consent boundary |

## Verification

```bash
python3 scripts/generate_consent_gate_inventory.py
python3 scripts/generate_popia_consent_boundary_matrix.py
make popia-consent-gate-check
make audit-contract-check
make popia-consent-audit-check
make popia-consent-boundary-check
```

## Next Hardening Targets

1. Add negative HTTP tests for expired/withdrawn consent on active-consent routes.
2. Add audit assertions for rejected learner-data access.
3. Add route-level documentation for every remaining allowlisted scanner candidate.

## Ether Onboarding Consent Boundary

- Ether onboarding submit is classified as an authenticated, non-learner-record boundary.

## POPIA Consent CI Closure

- CI now enforces consent-boundary, route-order, and rejection-audit checks.

## Diagnostics Central Consent Source

- Diagnostics routes now use the central consent adapter without direct consent-service bypasses.

## POPIA Negative Consent Evidence

- Negative consent evidence now covers adapter denial paths and central route-source usage.

## Cluster C Closure Stamp

Stamped: 2026-05-10T01:14:17Z

The first-pass POPIA consent/audit boundary is closed by:

- `make popia-consent-closure-check`
- `make popia-consent-gate-check`
- `make audit-contract-check`
- `make popia-consent-audit-check`
- `make popia-consent-boundary-check`
- `make popia-consent-order-check`
- `make popia-consent-source-check`
- `make popia-consent-rejection-audit-check`

Closure artifacts:

- `docs/security/popia_consent_gate_inventory.md`
- `docs/security/popia_consent_boundary_matrix.md`
- `docs/security/popia_consent_closure_check.md`
- `docs/security/popia_consent_closure_ci.md`

