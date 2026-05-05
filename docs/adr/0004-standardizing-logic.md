# ADR 0004: Standardizing Business Logic Location and Naming

## Status
Proposed

## Context
The codebase currently has logic split between `app/services/` and `app/modules/`, with some services using metaphorical names (Judiciary, Ether, etc.) which increases cognitive load for new developers.

## Decision
1. **Canonical Location**: All domain-specific business logic will reside in `app/modules/<domain>/service.py`.
2. **Descriptive Naming**: Metaphorical service names will be replaced with descriptive ones:
    - `EtherService` -> `LLMService` (under `app/modules/lessons/` or `app/core/`)
    - `JudiciaryService` -> `ContentSafetyService`
    - `FourthEstateService` -> `AuditService`
    - `ExecutiveService` -> `SystemOrchestrator`
3. **Thin Routers**: Routers must only handle request validation, authentication, and calling services. No business logic should reside in `app/api_v2_routers/`.

## Consequences
- **Pros**: Improved code discoverability, clearer domain boundaries, easier onboarding.
- **Cons**: Requires a significant refactoring of existing imports and file structures.
