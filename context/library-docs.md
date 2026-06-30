# Library Docs

**Last updated:** 2026-06-09
**Verified against:** Current codebase state (June 2026)

Project-specific usage patterns for all third-party libraries.

## FastAPI

- Single app instance in app/api_v2.py
- All routers registered in ROUTER_REGISTRY tuple
- All endpoints async, wrapped in try/catch, responses wrapped in EnvelopedRoute
- Always use Depends() for auth, database, services
- Validation with Pydantic BaseModel
- **Note:** 355 routes registered; some dormant routers still in tree (Phase 11 cleanup)

## SQLAlchemy 2.0

- Always use AsyncSession with await db.execute()
- Always use select() with where() -- never query() API
- Always scope queries to learner_id
- Always order results for deterministic behavior
- Use relationship() with back_populates for bidirectional
- Set cascade="all, delete-orphan" and ondelete="CASCADE" on foreign keys
- **Note:** 35 Alembic migrations; Phase 5 will remove startup schema repair

## Pydantic v2

- Set model_config = ConfigDict(from_attributes=True) for ORM conversion
- Add field constraints: Field(ge=..., le=..., min_length=..., max_length=...)
- Validate business logic in @field_validator
- Use Literal for enums, str | None for optional (not Optional[str])

## LLM Providers (Multi-Provider)

The project uses 4 LLM providers, not just OpenAI:

- **Groq (primary):** llama3-8b-8192 -- fast, cheap. Used via groq SDK.
- **Anthropic (fallback):** claude-sonnet-4-6. Used via anthropic SDK.
- **Google Gemini:** gemini-2.5-flash. Preferred for lesson generation.
- **HuggingFace (local):** SmolLM2-360M-Instruct with CAPS adapter. Local inference only.

Provider selection: LLM_PROVIDER env var (auto|google|groq|anthropic|local_hf|mock).
Auto mode selects based on availability and task.
All providers accessed through the LLM gateway abstraction in core/llm_gateway.py (695 lines).

- Use structured output formats (JSON mode where available)
- Set temperature=0.3 for deterministic results
- Never send learner PII to LLM providers
- Always validate response against CAPS constraints before saving
- Log full prompt and response for audit (content safety service)

## pytest & AsyncIO

- All tests async def test_* with @pytest.mark.asyncio
- Use in-memory SQLite for tests where possible
- Always arrange -> act -> assert pattern
- Target: >80% coverage (currently 40.9%; Phase 9)
- **Current:** 2051 passed, 1 skipped, 1 warning (local)

## Alembic

- Always review auto-generated migrations before applying
- Never modify production schema without migration
- Test migrations on copy of production DB before production
- **Current:** 35 migrations; Phase 5 will verify migration integrity

## ARQ (Background Jobs)

- ARQ replaces Celery for async task queue (Redis-backed)
- Define jobs in app/jobs/
- Worker started via arq command
- **Current gap:** ARQ not wired into Compose; BackgroundTasks used as placeholder (Phase 6)

## Logging

- Use logger.info/warning/error() with context in extra dict
- Always include learner_id and request_id in logs
- Use exc_info=True when logging exceptions
- Never use f-strings in log messages -- use extra dict

## Prometheus

- Include labels (grade, topic, etc.) for filtering
- Use Counter for total count events
- Use Histogram for time measurements
- Use Gauge for current state
- Scrape endpoint: /metrics
- **Current gap:** /metrics is unauthenticated (Phase 12 decision pending)
