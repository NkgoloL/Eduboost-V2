# Audit Candidate Execution Ledger

**Status:** adapter-backed execution harness active

## Executable candidates

| Candidate | Harness | Destructive? |
|---|---|---|
| consent_audit_events | in-memory adapter-backed sink | no |
| popia_data_rights_audit | in-memory adapter-backed sink | no |

## Boundary

The harness proves canonical payload compatibility. It does not write to production audit persistence and does not delete legacy audit paths.
