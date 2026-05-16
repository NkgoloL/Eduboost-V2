# Audit Repository Compatibility Contract

This contract defines how EduBoost will migrate from split audit implementations to one canonical append-only audit path.

## Scope

This document covers audit repository compatibility only. It does not consolidate consent tables or mutate production data.

## Canonical event shape

| Field | Meaning |
|---|---|
| `action` | Required event/action identifier |
| `actor_id` | Optional user/system actor |
| `resource_type` | Optional resource domain |
| `resource_id` | Optional affected resource identifier |
| `payload` | Structured metadata, including legacy fields such as learner pseudonym |

## Migration rule

1. Inventory call sites.
2. Add adapter support.
3. Migrate call sites to canonical event shape.
4. Preserve legal/security audit history.
5. Delete legacy audit repository only after full-suite and migration evidence pass.

## Non-goals

- No deletion in the diagnostic phase.
- No audit table data migration without explicit decision record.
- No change to POPIA retention semantics without legal/security approval.
