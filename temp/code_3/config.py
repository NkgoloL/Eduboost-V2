"""
EduBoost V2 — Core Configuration
Pydantic BaseSettings with environment-variable loading and validation.
"""
from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # ── Application ──────────────────────────────────────────────────────────
    APP_NAME: str = "EduBoost SA"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False

    # ── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/eduboost"

    # ── Redis (cache + sessions only — NO streams) ───────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL_SECONDS: int = 3600          # 1-hour default cache TTL
    SEMANTIC_CACHE_TTL_SECONDS: int = 86400      # 24-hour semantic cache

    # ── JWT ───────────────────────────────────────────────────────────────────
    JWT_SECRET: str = "CHANGE_ME_IN_PRODUCTION_AT_LEAST_32_CHARS"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── Encryption ───────────────────────────────────────────────────────────
    ENCRYPTION_KEY: str = "CHANGE_ME_32_BYTE_KEY_BASE64_ENCODED"  # AES-256

    # ── LLM Providers ────────────────────────────────────────────────────────
    ANTHROPIC_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    # ── AI Cost-Control ──────────────────────────────────────────────────────
    FREE_DAILY_REQUEST_QUOTA: int = 10
    PREMIUM_DAILY_REQUEST_QUOTA: int = 9999

    # ── Stripe ───────────────────────────────────────────────────────────────
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_ID_PREMIUM: str = ""

    # ── PostHog Telemetry ─────────────────────────────────────────────────────
    POSTHOG_API_KEY: str = ""
    POSTHOG_HOST: str = "https://app.posthog.com"

    # ── CORS ─────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    # ── POPIA ────────────────────────────────────────────────────────────────
    CONSENT_VALIDITY_DAYS: int = 365
    ERASURE_WINDOW_DAYS: int = 30

    @field_validator("JWT_SECRET")
    @classmethod
    def jwt_secret_min_length(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters")
        return v

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
