# ADR 0001: Modular Monolith Architecture

## Status
Accepted

## Context
EduBoost V2 needs to be maintainable, testable, and scalable without the complexity of microservices.

## Decision
We adopt a **Strict Modular Monolith** architecture.
- All code resides in a single repository.
- Domains are separated into modules under `app/modules/`.
- Each module has its own router, service, and repository layer.
- Cross-module communication is strictly controlled via service interfaces.
- Legacy code in `app/api/` is maintained as a shim for backward compatibility but is deprecated.

## Consequences
- **Pros**: Simplified deployment, unified testing, strong consistency, easier debugging.
- **Cons**: Requires discipline to prevent tight coupling between modules.
