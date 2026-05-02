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

    # ── CORS ──────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3002"]

    # ── Validation ───────────────────────────────────────────────────────────
    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters")
        return v

    @field_validator("ENCRYPTION_KEY")
    @classmethod
    def validate_encryption_key(cls, v: str) -> str:
        if len(v) != 44:  # Base64 encoded 32 bytes
            raise ValueError("ENCRYPTION_KEY must be 44 characters (32 bytes base64 encoded)")
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
    anthropic_model: str = "claude-sonnet-4-5"
    llm_timeout_seconds: int = 30
    llm_max_retries: int = 2

    # ── Email ─────────────────────────────────────────────────────────────────
    sendgrid_api_key: str = ""
    sendgrid_from_email: str = "noreply@eduboost.co.za"
    sendgrid_from_name: str = "EduBoost SA"

    # ── Azure Storage ─────────────────────────────────────────────────────────
    azure_storage_connection_string: str = ""
    azure_storage_container: str = "eduboost-assets"

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    rate_limit_default: str = "100/minute"
    rate_limit_auth: str = "10/minute"
    rate_limit_llm: str = "20/minute"

    # ── CORS ──────────────────────────────────────────────────────────────────
    cors_origins: list[str] = ["http://localhost:3000"]
    cors_allow_credentials: bool = True

    # ── Observability ─────────────────────────────────────────────────────────
    grafana_cloud_prometheus_url: str = ""
    grafana_cloud_loki_url: str = ""
    grafana_cloud_api_key: str = ""
    prometheus_metrics_path: str = "/metrics"
    log_level: str = "INFO"

    # ── ARQ Worker ────────────────────────────────────────────────────────────
    arq_max_jobs: int = 10
    arq_job_timeout: int = 300

    @field_validator("jwt_secret", "encryption_key")
    @classmethod
    def secrets_must_be_long_enough(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("Secret must be at least 32 characters")
        return v

    def is_production(self) -> bool:
        return self.app_env == "production"

    def is_development(self) -> bool:
        return self.app_env == "development"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": False}


def _load_from_key_vault(settings: Settings) -> Settings:
    """Fetch secrets from Azure Key Vault and patch settings (production only)."""
    if not settings.azure_key_vault_url:
        return settings

    try:
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient

        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=settings.azure_key_vault_url, credential=credential)

        secret_map = {
            "jwt-secret": "jwt_secret",
            "encryption-key": "encryption_key",
            "encryption-salt": "encryption_salt",
            "groq-api-key": "groq_api_key",
            "anthropic-api-key": "anthropic_api_key",
            "sendgrid-api-key": "sendgrid_api_key",
            "database-url": "database_url",
            "redis-url": "redis_url",
            "azure-storage-connection-string": "azure_storage_connection_string",
            "grafana-cloud-api-key": "grafana_cloud_api_key",
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


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    return _load_from_key_vault(settings)
