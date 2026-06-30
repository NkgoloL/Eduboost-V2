# Audit Canonicalization Implementation Checklist

**Status:** pending implementation

## Required implementation slices

| Slice | Description | Evidence |
|---|---|---|
| Audit inventory reviewed | Review `docs/release/audit_callsite_inventory.md` | TODO |
| Canonical repository selected | Confirm canonical repository and method shape | TODO |
| Adapter used where needed | Use `AuditRepositoryCompatAdapter` for legacy call shapes | TODO |
| Security/POPIA actions covered | Verify sensitive actions emit canonical audit events | TODO |
| Legacy data retained | Decide retain/migrate/archive for historical audit data | TODO |
| Deletion postponed | Legacy deletion deferred until release guard approves | TODO |

## Minimum tests

- canonical audit record call succeeds
- legacy append-style call maps to canonical payload
- POPIA/consent audit event preserves learner/resource identifiers
- no historical audit table deletion without decision record
