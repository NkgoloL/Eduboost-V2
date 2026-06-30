# Code Standards

## Engineering Mindset

- **Understand first** — read project-overview.md and architecture.md before coding
- **Learning science matters** — understand IRT, spaced repetition, mastery-based progression
- **POPIA compliance non-negotiable** — every feature touching learner data must audit consent
- **Tests first-class** — code is incomplete if untestable immediately after writing
- **Simplicity** — readable code preferred over clever abstractions
- **One feature at a time** — complete features fully before moving to next
- **Failures expected** — wrap all I/O in try/catch, log failures, never cascade failures
- **Performance** — diagnostic/practice sessions must respond <200ms

## Python Standards

- Python 3.11+ with type hints throughout
- `mypy` in strict mode - no `Any` except rare cases
- All functions must be typed (parameters and return types)
- Docstrings required on every module, class, function
- Async by default for all I/O operations
- Never let exceptions bubble up unhandled
- No bare `except` - always catch specific types

## FastAPI Conventions

- Single `FastAPI()` instance in `app/api_v2.py`
- All routers registered in `ROUTER_REGISTRY` tuple
- Endpoints: async, validate → delegate to service → return EnvelopedRoute
- Always use `Depends()` for auth, database, shared services
- Use Pydantic `BaseModel` for all request/response schemas
- Support `skip` and `limit` query params for list endpoints

## SQLAlchemy & Database

- Always use `AsyncSession` with async context managers
- Always scope to learner_id - never return another learner's data
- Define ORM models in `app/models/` - one model per file
- Use `select()` with `where()` - never use deprecated `query()` API
- Set `index=True` on frequently queried columns
- Use Alembic for all schema changes

## Testing

- pytest + pytest-cov
- >80% coverage target on business logic modules
- Use in-memory SQLite for tests (fast, isolated)
- All tests `async def test_*` with `@pytest.mark.asyncio`
- Always arrange → act → assert pattern

## File Naming

- Folders: snake_case (app/api_v2_routers, app/modules/learners)
- Modules: snake_case (irt_engine.py, practice_generator.py)
- Classes: PascalCase (PracticeGenerator, IrtEngine)
- Functions: snake_case (select_items, calculate_theta)
- Constants: UPPER_SNAKE_CASE (MAX_ITEMS_PER_SESSION)
- One class per file

## POPIA Compliance

Every feature must:
1. Check consent before accessing learner data
2. Audit all operations to audit_logs table
3. Support data export (learner downloads as JSON)
4. Support data erasure (delete from DB within 48h)
5. Never use learner data for analytics without consent

## Dependencies

Approved packages: fastapi, sqlalchemy, asyncpg, pydantic, pytest, openai, posthog, prometheus-client, alembic, apscheduler, python-jose, passlib

## Invariants

- Router code: no business logic, only validation and delegation
- Service code: no SQL, only delegation to repositories
- Repository code: only SQL queries, no business logic
- All responses wrapped in EnvelopedRoute
- All writes include audit logging
- All learner queries scoped to learner_id
- IRT theta/SE updated together, never stale
- POPIA consent always checked before analytics
- All async operations wrapped in try/catch
