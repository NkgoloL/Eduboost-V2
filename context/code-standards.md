# Code Standards

**Last updated:** 2026-06-09
**Enforced by:** CI gates (RoadMap Phase 9), ruff (Phase 1.2), mypy (Phase 9)

## Engineering Mindset

- **Understand first** -- read project-overview.md and architecture.md before coding
- **Check RoadMap and TODO** -- know which phase is active and what gaps are open
- **Learning science matters** -- understand IRT, spaced repetition, mastery-based progression
- **POPIA compliance non-negotiable** -- every feature touching learner data must audit consent
- **Tests first-class** -- code is incomplete if untestable immediately after writing
- **Simplicity** -- readable code preferred over clever abstractions
- **One feature at a time** -- complete features fully before moving to next
- **Failures expected** -- wrap all I/O in try/catch, log failures, never cascade failures
- **Performance** -- diagnostic/practice sessions must respond <200ms

## Python Standards

- Python 3.12.3 (target; RoadMap Phase 4 will align Docker/CI/local)
- Type hints throughout -- mypy in strict mode once Phase 9 gates are active
- No Any except rare, documented cases
- All functions typed (parameters and return types)
- Docstrings on every module, class, function
- Async by default for all I/O operations
- Never let exceptions bubble up unhandled
- No bare except -- always catch specific types
- **Current gap:** 861 Ruff findings; Phase 1.2 fixes F821 (undefined names); Phase 11 burns down the rest

## FastAPI Conventions

- Single FastAPI() instance in app/api_v2.py
- All routers registered in ROUTER_REGISTRY tuple
- Endpoints: async, validate -> delegate to service -> return EnvelopedRoute
- Always use Depends() for auth, database, shared services
- Use Pydantic BaseModel for all request/response schemas
- Support skip and limit query params for list endpoints
- **Known issue:** Routes registered twice (under /api/v2 AND /v2) -- Phase 11 will deduplicate

## SQLAlchemy & Database

- Always use AsyncSession with async context managers
- Always scope to learner_id -- never return another learner's data
- Define ORM models in app/models/ -- one model per file
- Use select() with where() -- never use deprecated query() API
- Set index=True on frequently queried columns
- Use Alembic for ALL schema changes -- no startup schema repair (Phase 5)

## Testing

- pytest + pytest-cov
- Target: >80% coverage on business logic (currently 40.9%; Phase 9)
- Use in-memory SQLite for tests (fast, isolated) -- or skip DB fixtures when unavailable
- All tests async def test_* with @pytest.mark.asyncio
- Always arrange -> act -> assert pattern
- **Current:** 2051 passed, 1 skipped, 1 warning (local)

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
- **Current gaps:** Legal-hold checks, export-offered flows (Phase 8)

## Dependencies

Approved: fastapi, sqlalchemy, asyncpg, pydantic, pytest, groq, anthropic, google-generativeai, transformers (optional), prometheus-client, alembic, arq, python-jose, passlib, httpx, redis

## Invariants

- Router code: no business logic, only validation and delegation
- Service code: no SQL, only delegation to repositories
- Repository code: only SQL queries, no business logic
- All responses wrapped in EnvelopedRoute
- All writes include audit logging
- All learner queries scoped to learner_id
- Use logger.info/warning/error() with context in extra dict
