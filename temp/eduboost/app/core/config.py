"""Application configuration via Pydantic Settings.

Reads environment variables (or a ``.env`` file) and exposes a single
:class:`Settings` singleton consumed everywhere in the application.  In
production the values are injected from **Azure Key Vault** via the ACA
secrets mechanism; locally a ``.env`` file is used instead.

Example:
    Access settings anywhere::

        from app.core.config import settings

        db_url = settings.DATABASE_URL
"""

from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Top-level application settings.

    All attributes map 1-to-1 with environment variables (uppercase).
    Pydantic validates types and raises a clear error on startup if a
    required variable is missing.

    Attributes:
        APP_NAME: Human-readable application name shown in OpenAPI docs.
        APP_VERSION: Semantic version string (e.g. ``"2.1.0"``).
        DEBUG: Enable debug mode. Must be ``False`` in production.
        DATABASE_URL: Async PostgreSQL DSN
            (``postgresql+asyncpg://user:pass@host/db``).
        REDIS_URL: Redis connection string used by *arq* and the cache layer.
        SECRET_KEY: 256-bit secret used for JWT signing. Rotate periodically.
        ACCESS_TOKEN_EXPIRE_MINUTES: JWT lifetime in minutes (default 60).
        ALLOWED_ORIGINS: List of CORS-allowed origins. Use specific domains
            in production — never ``["*"]``.
        GROQ_API_KEY: API key for the Groq LLM provider (primary).
        ANTHROPIC_API_KEY: API key for Anthropic Claude (fallback provider).
        STRIPE_SECRET_KEY: Stripe secret key for subscription management.
        STRIPE_WEBHOOK_SECRET: Webhook signing secret for Stripe events.
        AES_ENCRYPTION_KEY: 32-byte key for AES-GCM at-rest encryption.
        ENVIRONMENT: Deployment environment tag (``"local"``, ``"staging"``,
            ``"production"``).

    Example:
        Override a value for tests::

            import os
            os.environ["DEBUG"] = "true"
            from app.core.config import get_settings
            s = get_settings()
            assert s.DEBUG is True
    """

    APP_NAME: str = "EduBoost SA"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost/eduboost"
    REDIS_URL: str = "redis://localhost:6379"

    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    GROQ_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    AES_ENCRYPTION_KEY: str = "00000000000000000000000000000000"

    ENVIRONMENT: str = "local"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Return the cached :class:`Settings` singleton.

    Uses :func:`functools.lru_cache` so the ``.env`` file is only parsed
    once per process.  Call ``get_settings.cache_clear()`` in tests that
    need to override environment variables between runs.

    Returns:
        Settings: The fully-validated application settings object.

    Raises:
        pydantic.ValidationError: If a required environment variable is
            absent or has the wrong type.

    Example:
        ::

            from app.core.config import get_settings
            settings = get_settings()
            print(settings.APP_NAME)   # "EduBoost SA"
    """
    return Settings()


settings: Settings = get_settings()
