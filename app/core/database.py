"""
EduBoost V2 — Database Engine & Session Factory
SQLAlchemy async engine wired to PostgreSQL via asyncpg.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

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
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all_tables() -> None:
    """Drop all tables (test teardown only)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def init_test_schema() -> None:
    """Legacy helper alias retained while tests migrate to app.core.database."""
    await create_all_tables()
