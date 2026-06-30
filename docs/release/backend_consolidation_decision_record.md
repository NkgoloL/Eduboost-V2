# Backend Consolidation Decision Record

**Status:** pending implementation decisions

This document records release-owner decisions for backend consolidation work.

## Audit persistence

| Question | Decision | Evidence |
|---|---|---|
| Is `audit_events` the canonical append-only table? | TODO | `docs/release/audit_callsite_inventory.md` |
| Is `audit_logs` legacy, active, or historical data? | TODO | `docs/release/audit_callsite_inventory.md` |
| Will historical audit data be migrated, archived, or retained in place? | TODO | Legal/security approval required |
| Which repository is canonical? | TODO | `app/repositories/audit_repository.py` / adapter evidence |

## Consent persistence

| Question | Decision | Evidence |
|---|---|---|
| Is `consent_records` current state, event history, or both? | TODO | `docs/release/consent_callsite_inventory.md` |
| Is `parental_consents` current state, relationship consent, or legacy? | TODO | `docs/release/consent_callsite_inventory.md` |
| Which service owns `require_active_consent` at runtime? | TODO | call-site inventory |
| Is table consolidation required? | TODO | ADR required before migration |

## Schema drift

| Question | Decision | Evidence |
|---|---|---|
| Does a fresh disposable DB pass `alembic upgrade head`? | TODO | `docs/release/migration_latest.md` |
| Does ORM-vs-DB table comparison pass? | TODO | `make schema-drift-check-db` |
| Are extra legacy DB tables intentional? | TODO | schema drift output |

## Health/readiness

| Question | Decision | Evidence |
|---|---|---|
| What remains lightweight health? | TODO | health contract |
| What belongs in deep health? | TODO | health contract |
| Are any deep checks internal/admin-only? | TODO | route policy |

## Deletion approval

No backend consolidation deletion is approved until all rows above have decisions and evidence.
