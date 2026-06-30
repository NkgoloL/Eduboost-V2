# First Audit Runtime Wiring PR

**Status:** scoped implementation candidate active

## Scope

This PR introduces the first adapter-backed audit runtime wiring helper for exactly one selected candidate:

```text
BCW-421-AUDIT-CONSENT-GRANTED
```

## Candidate

| Field | Value |
|---|---|
| Source candidate | `consent_audit_events` |
| Action | `consent.granted` |
| Resource type | `learner_consent` |
| Runtime route change | no |
| Schema change | no |
| Destructive action | no |
| DB-writing test | no |

## Boundary

This PR does not delete repositories, merge consent tables, drop `audit_logs`, stamp Alembic, mutate production databases, or change route registration.
