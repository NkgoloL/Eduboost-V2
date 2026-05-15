"""
EduBoost V2 — Database Engine & Session Factory
SQLAlchemy async engine wired to PostgreSQL via asyncpg.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event, text
import time

from app.core.config import settings

# Configure engine based on database type
engine_kwargs = {
    "echo": settings.DEBUG,
    "pool_pre_ping": True,
}

# PostgreSQL-specific settings
if settings.DATABASE_URL.startswith("postgresql") and settings.APP_ENV in {"development", "test"}:
    engine_kwargs["poolclass"] = NullPool
elif settings.DATABASE_URL.startswith("postgresql"):
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
    })

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Compatibility aliases while the remaining legacy tests and helper modules
# are migrated onto the V2 core package.
AsyncSessionFactory = AsyncSessionLocal

def get_async_engine():
    """Returns the global async engine instance."""
    return engine


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields an async DB session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_all_tables() -> None:
    """Create all tables (dev/test only — use Alembic in production)."""
    import app.models  # noqa: F401
    import app.models.diagnostic_item  # noqa: F401
    import app.models.item_exposure  # noqa: F401
    import app.repositories.study_plan_repository  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        if settings.DATABASE_URL.startswith("postgresql"):
            await conn.execute(text("DROP RULE IF EXISTS audit_events_no_update ON audit_events"))
            await conn.execute(text("DROP RULE IF EXISTS audit_events_no_delete ON audit_events"))
            await conn.execute(
                text(
                    """
                    CREATE RULE audit_events_no_update AS
                    ON UPDATE TO audit_events
                    DO INSTEAD NOTHING
                    """
                )
            )
            await conn.execute(
                text(
                    """
                    CREATE RULE audit_events_no_delete AS
                    ON DELETE TO audit_events
                    DO INSTEAD NOTHING
                    """
                )
            )


async def drop_all_tables() -> None:
    """Drop all tables (test teardown only)."""
    if settings.APP_ENV != "test":
        return
    import app.models  # noqa: F401
    import app.models.diagnostic_item  # noqa: F401
    import app.models.item_exposure  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def init_test_schema() -> None:
    """Legacy helper alias retained while tests migrate to app.core.database."""
    await create_all_tables()


# Slow-query instrumentation
# Registers SQLAlchemy event listeners on the underlying sync engine to measure
# query execution time and emit structured logs for queries exceeding the
# configured threshold. Parameter values are not logged to avoid PII leakage.
try:
    slow_threshold = float(getattr(settings, "SLOW_QUERY_SECONDS", 0) or 0)
except Exception:
    slow_threshold = 0.0

if slow_threshold > 0:
    try:
        # Prefer structured logger if available
        from app.core.logging import get_logger

        slow_log = get_logger("sqlalchemy.slow")
    except Exception:
        import logging as _logging

        slow_log = _logging.getLogger("sqlalchemy.slow")

    def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault("query_start_time", []).append(time.time())

    def _after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        start_times = conn.info.get("query_start_time", [])
        if not start_times:
            return
        start_time = start_times.pop(-1)
        duration = time.time() - start_time
        if duration >= slow_threshold:
            try:
                param_count = len(parameters) if parameters is not None else 0
            except Exception:
                param_count = 0
            # Avoid logging parameter values to prevent leaking sensitive data
            try:
                slow_log.warning(
                    "slow_query",
                    duration_seconds=round(duration, 4),
                    param_count=param_count,
                    statement=statement,
                )
            except Exception:
                # Fallback to stdlib logging message format
                import logging as _logging

                _logging.getLogger("sqlalchemy.slow").warning(
                    "Slow query: %.4fs params=%d statement=%s",
                    duration,
                    param_count,
                    statement,
                )

    # Register listeners on the sync engine wrapped by the async engine
    event.listen(engine.sync_engine, "before_cursor_execute", _before_cursor_execute)
    event.listen(engine.sync_engine, "after_cursor_execute", _after_cursor_execute)
