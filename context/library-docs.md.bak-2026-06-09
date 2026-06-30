# Library Docs

Project-specific usage patterns for all third-party libraries.

## FastAPI

- Single app instance in `app/api_v2.py`
- All routers registered in `ROUTER_REGISTRY` tuple
- All endpoints async, wrapped in try/catch, responses wrapped in EnvelopedRoute
- Always use `Depends()` for auth, database, services
- Validation with Pydantic `BaseModel`

## SQLAlchemy 2.0

- Always use `AsyncSession` with `await db.execute()`
- Always use `select()` with `where()` - never `query()` API
- Always scope queries to learner_id
- Always order results for deterministic behavior
- Use `relationship()` with `back_populates` for bidirectional relationships
- Set `cascade="all, delete-orphan"` and `ondelete="CASCADE"` on foreign keys

## Pydantic v2

- Set `model_config = ConfigDict(from_attributes=True)` for ORM conversion
- Add field constraints: `Field(ge=..., le=..., min_length=..., max_length=...)`
- Validate business logic in `@field_validator`
- Use `Literal` for enums, `str | None` for optional strings (not `Optional[str]`)

## OpenAI GPT-4o

- Use `response_format={"type": "json_object"}` for structured responses
- Always set `temperature=0.3` for deterministic results
- Never ask GPT-4o for learner data directly - load from DB first
- Always validate response against CAPS constraints before saving
- Log full prompt and response for audit

## pytest & AsyncIO

- All tests `async def test_*` with `@pytest.mark.asyncio`
- Use in-memory SQLite for tests
- Always arrange → act → assert pattern
- >80% coverage target on business logic

## Alembic

- Always review auto-generated migrations before applying
- Never modify production schema without migration
- Test migrations on copy of production DB before production

## Logging

- Use `logger.info/warning/error()` with context in `extra` dict
- Always include `learner_id` and `request_id` in logs
- Use `exc_info=True` when logging exceptions
- Never use f-strings in log messages - use `extra` dict

## Prometheus

- Include labels (grade, topic, etc.) for filtering
- Use Counter for total count events
- Use Histogram for time measurements
- Use Gauge for current state
- Scrape endpoint: `/metrics`
