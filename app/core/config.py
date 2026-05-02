"""
EduBoost SA — Core Configuration
Loads secrets from Azure Key Vault in production; falls back to .env locally.
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Environment ──────────────────────────────────────────────────────────
    app_env: Literal["development", "test", "staging", "production"] = "development"
    app_name: str = "EduBoost SA API"
    app_version: str = "2.0.0"
    debug: bool = False

    # ── Azure Key Vault ───────────────────────────────────────────────────────
    azure_key_vault_url: str = ""          # e.g. https://eduboost-kv.vault.azure.net/
    # In production, all secrets below are fetched from Key Vault at startup.
    # Locally, they are read from .env / environment variables.

    # ── Database ─────────────────────────────────────────────────────────────
    database_url: str = Field(
        default="postgresql+asyncpg://eduboost:password@localhost:5432/eduboost",
    )
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_pre_ping: bool = True

    # ── Redis ─────────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 20

    # ── Security ──────────────────────────────────────────────────────────────
    jwt_secret: str = Field(default="change-me-in-production-32-chars-min")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 30
    encryption_key: str = Field(default="change-me-in-production-32-chars-min")
    encryption_salt: str = Field(default="change-me-in-production-16-chars")

    # ── LLM Providers ─────────────────────────────────────────────────────────
    groq_api_key: str = ""
    anthropic_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
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
