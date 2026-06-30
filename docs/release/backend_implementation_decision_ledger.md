# Backend Implementation Decision Ledger

**Status:** implementation decisions pending approval

This ledger tracks decisions required before backend consolidation moves from preflight to runtime wiring or deletion.

| ID | Decision | Default | Required evidence | Approved? |
|---|---|---|---|---|
| BCI-001 | Audit writes should use canonical adapter-backed event shape | yes | audit registry + preflight | pending |
| BCI-002 | Consent runtime payloads should normalize to audit-compatible events | yes | consent preflight | pending |
| BCI-003 | Deep readiness public route must be read-only | yes | deep-readiness preflight | pending |
| BCI-004 | Disposable DB schema proof required before migration fixes | yes | schema drift proof | pending |
| BCI-005 | `audit_logs` deletion allowed | no | data-retention decision + release-owner approval | blocked |
| BCI-006 | `consent_records` / `parental_consents` merge allowed | no | ADR + migration proof + legal/security approval | blocked |
| BCI-007 | `alembic stamp head` allowed as repair | no | explicit written exception | blocked |

## Rule

All destructive decisions default to blocked.
