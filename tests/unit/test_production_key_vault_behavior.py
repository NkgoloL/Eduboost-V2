from __future__ import annotations

import pytest


@pytest.mark.unit
def test_production_settings_fail_closed_without_key_vault(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.core import config

    monkeypatch.setattr(
        config,
        "_fetch_key_vault_secret_values",
        lambda vault_url: pytest.fail("Key Vault fetch should not run without a URL"),
    )

    with pytest.raises(ValueError, match="AZURE_KEY_VAULT_URL is required when APP_ENV is production"):
        config.Settings(
            APP_ENV="production",
            ENVIRONMENT="production",
            AZURE_KEY_VAULT_URL="",
        )


@pytest.mark.unit
def test_production_settings_refresh_required_key_vault_secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.core import config

    fetched = {
        "JWT_SECRET": "prod-jwt-secret-value-that-is-long-enough",
        "ENCRYPTION_KEY": "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=",
        "ENCRYPTION_SALT": "prod-encryption-salt",
        "GROQ_API_KEY": "prod-groq-key",
        "ANTHROPIC_API_KEY": "prod-anthropic-key",
    }

    monkeypatch.setattr(config, "_fetch_key_vault_secret_values", lambda vault_url: fetched)

    settings = config.Settings(
        APP_ENV="production",
        ENVIRONMENT="production",
        AZURE_KEY_VAULT_URL="https://example-vault.vault.azure.net/",
    )

    assert settings.JWT_SECRET == fetched["JWT_SECRET"]
    assert settings.ENCRYPTION_KEY == fetched["ENCRYPTION_KEY"]
    assert settings.ENCRYPTION_SALT == fetched["ENCRYPTION_SALT"]
    assert settings.GROQ_API_KEY == fetched["GROQ_API_KEY"]
    assert settings.ANTHROPIC_API_KEY == fetched["ANTHROPIC_API_KEY"]


@pytest.mark.unit
def test_key_vault_empty_secret_value_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.core import config

    fetched = {
        "JWT_SECRET": "prod-jwt-secret-value-that-is-long-enough",
        "ENCRYPTION_KEY": "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=",
        "ENCRYPTION_SALT": "prod-encryption-salt",
        "GROQ_API_KEY": "",
        "ANTHROPIC_API_KEY": "prod-anthropic-key",
    }

    monkeypatch.setattr(config, "_fetch_key_vault_secret_values", lambda vault_url: fetched)

    with pytest.raises(ValueError, match="Azure Key Vault returned an empty value for GROQ_API_KEY"):
        config.Settings(
            APP_ENV="production",
            ENVIRONMENT="production",
            AZURE_KEY_VAULT_URL="https://example-vault.vault.azure.net/",
        )
