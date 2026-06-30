# Audit Call-Site Migration Slice 002

**Status:** adapter-backed migration orchestrator active

## Scope

This slice introduces `app/services/audit_migration_orchestrator.py` to create canonical audit events only for migration candidates already marked adapter-ready.

## Guardrails

- Candidate must be listed in the audit canonicalization registry.
- Candidate must be non-destructive.
- Event is routed through `AuditRepositoryCompatAdapter`.
- Legacy deletion remains blocked.
