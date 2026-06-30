# Consent Runtime Repair Slice 002

**Status:** compatibility orchestrator active

## Scope

This slice introduces `app/services/consent_runtime_orchestrator.py` to summarize consent runtime constructor surfaces and build audit-compatible consent runtime payloads.

## Guardrails

- No consent table merge.
- No direct repository rewrite.
- No POPIA authorization boundary change.
- No deletion of `consent_records` or `parental_consents`.
