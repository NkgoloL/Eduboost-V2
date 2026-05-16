# Backend Data Retention Decision Checklist

**Status:** pending legal/security/release-owner decision

This checklist prevents accidental loss of audit or consent history during backend consolidation.

## Audit data

| Question | Decision | Evidence |
|---|---|---|
| Does `audit_logs` exist in any deployed database? | TODO | schema drift / DB inventory |
| Does `audit_logs` contain historical security or POPIA-relevant data? | TODO | DB query evidence |
| Is `audit_events` canonical for future append-only audit? | TODO | ADR / repository evidence |
| Will historical audit data be migrated, retained in place, or archived? | TODO | legal/security decision |
| Is fresh-start audit acceptable? | default: NO | explicit approval required |

## Consent data

| Question | Decision | Evidence |
|---|---|---|
| Does `consent_records` represent current state, history, or both? | TODO | inventory / schema docs |
| Does `parental_consents` represent current state, relationship consent, or legacy? | TODO | inventory / schema docs |
| Are consent history records required for POPIA accountability? | default: YES | legal/security decision |
| Will any consent rows be merged or deleted? | default: NO | migration plan required |
| Is table consolidation required before beta? | TODO | release decision |

## Approval

No destructive backend consolidation is approved until this checklist is completed.
