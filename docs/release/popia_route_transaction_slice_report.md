# POPIA Route Transaction Slice Report

Generated at: `2026-05-19T18:42:44Z`
Commit: `2a9ad9e37ede787422d202cd0fde4fb71b28e15d`

- Route file: `app/api_v2_routers/popia.py`
- Local status: `route-popia-delegation-passing`
- Live DB status: `external-blocked`
- Selected route count: `5`

## Route findings

| Route function | Line | Delegate calls | Direct DB mutations | Status |
|---|---:|---|---|---|
| `grant_consent` | 102 | `consent_svc.grant` | `-` | `route-delegates-to-service-boundary` |
| `deny_consent` | 120 | `consent_svc.deny` | `-` | `route-delegates-to-service-boundary` |
| `withdraw_consent` | 138 | `consent_svc.withdraw` | `-` | `route-delegates-to-service-boundary` |
| `renew_consent` | 153 | `consent_svc.renew` | `-` | `route-delegates-to-service-boundary` |
| `create_export_request` | 173 | `dsr_svc.build_learner_export` | `-` | `route-delegates-to-service-boundary` |

## Transaction service markers found

- `.begin()`
- `TransactionalPOPIA`
- `TransactionalPOPIAConsentLifecycleService`

## Blockers

- live-db: Live DB evidence URL is pending
- live-db: Test result is pending
- live-db: Database is pending
- live-db: Commit SHA is pending
- live-db: Verified by is pending
- live-db: Date verified is pending
- live-db: Live DB evidence URL must be a URL
- live-db: Test result must be passed/pass/green/ok
- live-db: Commit SHA must look like a git SHA

## No false-closure rules

- POPIA route delegation does not prove live database rollback.
- Service markers do not prove the production route path by themselves.
- ROUTE-TX-POPIA-001 release mode requires live DB evidence.
- TX-ROUTE-001 remains open until all mutation route slices are wired and proven.

## Interpretation

This report proves only the local POPIA route delegation slice. It does not prove live database rollback.
