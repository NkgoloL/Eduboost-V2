# Audit Canonicalization Migration Registry

**Status:** first implementation registry active

## Current migration candidates

| Candidate | Scope | Status | Destructive? |
|---|---|---|---|
| consent_audit_events | Consent runtime audit events | migration_ready | no |
| popia_data_rights_audit | POPIA service audit events | adapter_ready | no |
| legacy_audit_logs | Historical/legacy audit persistence | deferred | no |

## Rule

Only non-destructive candidates with adapter coverage may proceed to runtime wiring. Legacy deletion remains blocked by the deletion candidate inventory, data-retention checklist, and release-owner approval.
