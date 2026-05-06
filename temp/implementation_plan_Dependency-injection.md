# Dependency Injection and Cross-Cutting Concerns Refactoring

This plan addresses section `2.3` of the production TODO backlog: standardising FastAPI dependencies, implementing robust service dependency providers, configuring test dependency overrides, and extending correlation ID propagation.

## User Review Required

> [!WARNING]
> This refactoring will centralize how services are instantiated. We propose creating an `app/core/providers.py` to act as the primary factory for all services (e.g., `get_learner_service`, `get_audit_service`). Please confirm if this approach aligns with your vision for the "dependency providers" requirement, or if you prefer using a third-party DI framework (like `dependency-injector`).

## Proposed Changes

### Core Dependencies (`app/core/dependencies.py`)
- **[MODIFY]** Expand `dependencies.py` to standardize dependency functions:
  - Role checks (`require_role(role)`)
  - Guardian relationship checks (`require_guardian_link`)
  - Request ID provider (`get_request_id` using contextvars/starlette state)
  - Audit context provider (`get_audit_context`)
  - Rate-limit identity provider

### Service Providers (`app/core/providers.py`)
- **[NEW]** Create a centralized service provider module to replace ad-hoc construction in individual routers.
  - Implement functions like `get_learner_service()`, `get_lesson_service()`, `get_audit_service()`, etc.
  - These providers will handle injecting `db: AsyncSession` and any other required infrastructural dependencies (like Redis, LLM gateways) into the services.

### Routers (`app/api_v2_routers/*.py`)
- **[MODIFY]** Refactor all routers to use the new centralized service providers.
  - Remove local `get_X_service` functions.
  - Example: `service: LessonService = Depends(providers.get_lesson_service)`

### Context and Correlation ID (`app/core/context.py`)
- **[NEW]** Create a context utility (using `contextvars`) to access the current `request_id` outside of the FastAPI request scope, ensuring it propagates seamlessly to audit events and external calls without passing `request` objects down the call stack.
- **[MODIFY]** Update `RequestIDMiddleware` to populate this context variable.

### Test Overrides (`tests/conftest.py`)
- **[MODIFY]** Update `conftest.py` to provide standard FastAPI `app.dependency_overrides` for DB, Redis, LLM provider, and email provider. This ensures unit tests do not accidentally hit real infrastructure.

## Verification Plan

### Automated Tests
- Run the full `pytest` suite.
- Ensure all routers continue to function correctly with the new service providers.
- Verify that dependency overrides in tests successfully mock out real infrastructure.

### Manual Verification
- Check the structured logs to confirm that `request_id` is consistently present in both web requests and background tasks.
- Verify the OpenAPI schema (`/docs`) cleanly reflects the standardized dependencies (like consent and role checks).
