# EduBoost V2 Service Layer

This directory is the V2 modular-monolith target for business logic.

Rules:
- API handlers should depend on this layer, not on repository internals.
- Repositories encapsulate persistence access.
- Domain entities remain free of FastAPI request objects and third-party LLM client types.
- The current `app/api/services/` code remains the operational runtime while V2 migration proceeds incrementally.
