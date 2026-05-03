"""
EduBoost V2 — Core Configuration
Pydantic BaseSettings with environment-variable loading and validation.
"""
from functools import lru_cache
from typing import Any
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


KEY_VAULT_SECRET_NAMES = {
    "JWT_SECRET": "eduboost-jwt-secret",
    "ENCRYPTION_KEY": "eduboost-encryption-key",
    "ENCRYPTION_SALT": "eduboost-encryption-salt",
    "GROQ_API_KEY": "eduboost-groq-api-key",
    "ANTHROPIC_API_KEY": "eduboost-anthropic-api-key",
}


def _fetch_key_vault_secret_values(vault_url: str) -> dict[str, str]:
    from azure.identity import DefaultAzureCredential
    from azure.keyvault.secrets import SecretClient

    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)
    return {
        field_name: client.get_secret(secret_name).value
        for field_name, secret_name in KEY_VAULT_SECRET_NAMES.items()
    }


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # ── Application ──────────────────────────────────────────────────────────
    APP_NAME: str = "EduBoost SA"
    APP_VERSION: str = "2.0.0"
    APP_BASE_URL: str = "https://eduboost.co.za"
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
    ENCRYPTION_SALT: str = "test-encryption-salt"

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
    SENDGRID_FROM_EMAIL: str = ""
    SENDGRID_FROM_NAME: str = "EduBoost SA"

    # ── Azure / Observability ────────────────────────────────────────────────
    AZURE_KEY_VAULT_URL: str = ""
    AZURE_CLIENT_ID: str = ""
    AZURE_CLIENT_SECRET: str = ""
    AZURE_TENANT_ID: str = ""
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
        return self.APP_ENV == "production" or self.ENVIRONMENT == "production"

    @model_validator(mode="after")
    def load_production_secrets_from_key_vault(self) -> "Settings":
        if not self.is_production():
            return self
        if not self.AZURE_KEY_VAULT_URL:
            raise ValueError("AZURE_KEY_VAULT_URL is required when APP_ENV is production")

        secret_values = _fetch_key_vault_secret_values(self.AZURE_KEY_VAULT_URL)
        for field_name, value in secret_values.items():
            if not value:
                raise ValueError(f"Azure Key Vault returned an empty value for {field_name}")
            setattr(self, field_name, value)
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


# Exported singleton
settings = get_settings()
