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
    ENVIRONMENT: Literal["development", "test", "staging", "production"] = "development"
    APP_ENV: Literal["development", "test", "staging", "production"] = "development"
    DEBUG: bool = False
    LEGACY_RETIREMENT_DATE: str = "2026-08-01"

    # ── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/eduboost"

    # ── Redis (cache + sessions only — NO streams) ───────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL_SECONDS: int = 3600          # 1-hour default cache TTL
    SEMANTIC_CACHE_TTL_SECONDS: int = 604800      # 7-day semantic cache

    # ── JWT ───────────────────────────────────────────────────────────────────
    JWT_SECRET: str = "CHANGE_ME_IN_PRODUCTION_AT_LEAST_32_CHARS"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Encryption ───────────────────────────────────────────────────────────
    ENCRYPTION_KEY: str = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="  # dev-only 32-byte base64 placeholder

    # ── LLM Providers ────────────────────────────────────────────────────────
    ANTHROPIC_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-5"
    LLM_TIMEOUT_SECONDS: int = 30
    LLM_MAX_RETRIES: int = 2

    # ── AI Cost-Control ──────────────────────────────────────────────────────
    FREE_DAILY_REQUEST_QUOTA: int = 20
    PREMIUM_DAILY_REQUEST_QUOTA: int = 9999

    # ── Stripe ───────────────────────────────────────────────────────────────
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_ID_PREMIUM: str = ""

    # ── Email ────────────────────────────────────────────────────────────────
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "noreply@eduboost.co.za"
    SENDGRID_FROM_NAME: str = "EduBoost SA"

    # ── Azure / Observability ────────────────────────────────────────────────
    AZURE_KEY_VAULT_URL: str = ""
    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_STORAGE_CONTAINER: str = "eduboost-assets"
    GRAFANA_CLOUD_PROMETHEUS_URL: str = ""
    GRAFANA_CLOUD_LOKI_URL: str = ""
    GRAFANA_CLOUD_API_KEY: str = ""
    PROMETHEUS_METRICS_PATH: str = "/metrics"
    LOG_LEVEL: str = "INFO"

    # ── Rate Limiting / Jobs ────────────────────────────────────────────────
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_AUTH: str = "10/minute"
    RATE_LIMIT_LLM: str = "20/minute"
    ARQ_MAX_JOBS: int = 10
    ARQ_JOB_TIMEOUT: int = 300

    # ── CORS ──────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3002"]

    # ── Validation ───────────────────────────────────────────────────────────
    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if v != "test-jwt-secret" and len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters")
        return v

    @field_validator("ENCRYPTION_KEY")
    @classmethod
    def validate_encryption_key(cls, v: str) -> str:
        if v.startswith("test-"):
            return v
        if len(v) != 44:  # Base64 encoded 32 bytes
            raise ValueError("ENCRYPTION_KEY must be 44 characters (32 bytes base64 encoded)")
        return v

    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production" or self.APP_ENV == "production"

    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development" or self.APP_ENV == "development"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    return _load_from_key_vault(settings)


def _load_from_key_vault(settings: Settings) -> Settings:
    """Fetch secrets from Azure Key Vault and patch settings (production only)."""
    if not settings.AZURE_KEY_VAULT_URL:
        return settings

    try:
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient

        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=settings.AZURE_KEY_VAULT_URL, credential=credential)

        secret_map = {
            "jwt-secret": "JWT_SECRET",
            "encryption-key": "ENCRYPTION_KEY",
            "groq-api-key": "GROQ_API_KEY",
            "anthropic-api-key": "ANTHROPIC_API_KEY",
            "sendgrid-api-key": "SENDGRID_API_KEY",
            "database-url": "DATABASE_URL",
            "redis-url": "REDIS_URL",
            "azure-storage-connection-string": "AZURE_STORAGE_CONNECTION_STRING",
            "grafana-cloud-api-key": "GRAFANA_CLOUD_API_KEY",
        }

        overrides: dict[str, str] = {}
        for vault_name, field_name in secret_map.items():
            try:
                overrides[field_name] = client.get_secret(vault_name).value or ""
            except Exception:
                pass  # Secret not in vault — keep env/default value

        if overrides:
            return settings.model_copy(update=overrides)

    except ImportError:
        pass  # azure-identity not installed — local dev

    return settings


settings = get_settings()
