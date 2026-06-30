from __future__ import annotations

import pytest

from app.core import config as config_module


def test_production_settings_load_secrets_from_key_vault(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        config_module,
        "_fetch_key_vault_secret_values",
        lambda vault_url: {
            "JWT_SECRET": "x" * 32,
            "ENCRYPTION_KEY": "A" * 44,
            "ENCRYPTION_SALT": "salt-from-kv",
            "GROQ_API_KEY": "groq-from-kv",
            "ANTHROPIC_API_KEY": "anthropic-from-kv",
        },
    )

    settings = config_module.Settings(
        APP_ENV="production",
        ENVIRONMENT="production",
        AZURE_KEY_VAULT_URL="https://eduboost.vault.azure.net/",
        JWT_SECRET="should-be-overridden-but-valid-value",
        ENCRYPTION_KEY="B" * 44,
        ENCRYPTION_SALT="env-salt",
    )

    assert settings.JWT_SECRET == "x" * 32
    assert settings.ENCRYPTION_KEY == "A" * 44
    assert settings.ENCRYPTION_SALT == "salt-from-kv"
    assert settings.GROQ_API_KEY == "groq-from-kv"
    assert settings.ANTHROPIC_API_KEY == "anthropic-from-kv"


def test_production_settings_require_key_vault_url(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_if_called(_: str) -> dict[str, str]:
        raise AssertionError("Key Vault should not be used without AZURE_KEY_VAULT_URL")

    monkeypatch.setattr(config_module, "_fetch_key_vault_secret_values", fail_if_called)

    with pytest.raises(ValueError, match="AZURE_KEY_VAULT_URL is required when APP_ENV is production"):
        config_module.Settings(
            APP_ENV="production",
            ENVIRONMENT="production",
            AZURE_KEY_VAULT_URL="",
            JWT_SECRET="x" * 32,
            ENCRYPTION_KEY="A" * 44,
            ENCRYPTION_SALT="salt",
        )


def test_non_production_settings_do_not_call_key_vault(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_if_called(_: str) -> dict[str, str]:
        raise AssertionError("Key Vault should not be used outside production")

    monkeypatch.setattr(config_module, "_fetch_key_vault_secret_values", fail_if_called)

    settings = config_module.Settings(
        APP_ENV="development",
        ENVIRONMENT="development",
        JWT_SECRET="x" * 32,
        ENCRYPTION_KEY="A" * 44,
        ENCRYPTION_SALT="dev-salt",
    )

    assert settings.JWT_SECRET == "x" * 32
    assert settings.ENCRYPTION_SALT == "dev-salt"


def test_database_url_normalizes_render_postgres_scheme() -> None:
    settings = config_module.Settings(
        DATABASE_URL="postgresql://user:pass@render-postgres.example.com:5432/eduboost",
        JWT_SECRET="x" * 32,
        ENCRYPTION_KEY="A" * 44,
    )

    assert settings.DATABASE_URL == "postgresql+asyncpg://user:pass@render-postgres.example.com:5432/eduboost"


def test_database_url_keeps_async_and_non_postgres_schemes() -> None:
    async_settings = config_module.Settings(
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/eduboost",
        JWT_SECRET="x" * 32,
        ENCRYPTION_KEY="A" * 44,
    )
    sqlite_settings = config_module.Settings(
        DATABASE_URL="sqlite+aiosqlite:///./test.db",
        JWT_SECRET="x" * 32,
        ENCRYPTION_KEY="A" * 44,
    )

    assert async_settings.DATABASE_URL == "postgresql+asyncpg://user:pass@localhost:5432/eduboost"
    assert sqlite_settings.DATABASE_URL == "sqlite+aiosqlite:///./test.db"


def test_database_url_normalizes_sslmode_for_asyncpg() -> None:
    settings = config_module.Settings(
        DATABASE_URL="postgresql://user:pass@db.example.com:5432/eduboost?sslmode=require",
        JWT_SECRET="x" * 32,
        ENCRYPTION_KEY="A" * 44,
    )

    assert settings.DATABASE_URL == "postgresql+asyncpg://user:pass@db.example.com:5432/eduboost?ssl=require"
