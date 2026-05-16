# Consent Runtime Repair Checklist

**Status:** pending implementation

## Required implementation slices

| Slice | Description | Evidence |
|---|---|---|
| Consent inventory reviewed | Review `docs/release/consent_callsite_inventory.md` | TODO |
| Constructor compatibility checked | Verify `ConsentService` and `POPIADataRightsService` construction paths | TODO |
| Active consent path selected | Identify canonical `require_active_consent` owner | TODO |
| Audit normalization applied | Use consent audit normalizer where needed | TODO |
| Read/write authz preserved | Preserve explicit learner read/write authorization boundaries | TODO |
| Table semantics documented | Decide `consent_records` vs `parental_consents` roles | TODO |

## Minimum tests

- consent grant/revoke runtime paths do not crash
- active consent check has deterministic allow/deny behavior
- POPIA service construction is deterministic
- consent audit event maps learner/resource ID correctly
