# Backend Adapter Wiring Service Contract

**Status:** test-sink adapter wiring active

## Scope

`app/services/backend_adapter_wiring_service.py` proves that safe wiring candidates can be recorded through `AuditRepositoryCompatAdapter` using an in-memory sink.

## Boundary

The service does not write to production persistence. It exists to validate payload compatibility before a later narrowly scoped runtime PR.
