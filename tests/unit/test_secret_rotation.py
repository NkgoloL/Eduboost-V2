import pytest

from app.core.config import settings
from app.core.secret_rotation import refresh_key_vault_secrets_once


@pytest.mark.asyncio
async def test_secret_rotation_updates_cached_settings(monkeypatch):
    monkeypatch.setattr(settings, "APP_ENV", "production")
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "AZURE_KEY_VAULT_URL", "https://vault.example")
    monkeypatch.setattr(settings, "JWT_SECRET", "x" * 32)

    refreshed = {
        "JWT_SECRET": "y" * 32,
        "ENCRYPTION_KEY": "B" * 44,
        "ENCRYPTION_SALT": "salt-value",
        "GROQ_API_KEY": "groq-key",
        "ANTHROPIC_API_KEY": "anthropic-key",
    }

    monkeypatch.setattr(
        "app.core.config._fetch_key_vault_secret_values",
        lambda _vault_url: refreshed,
    )

    updated = await refresh_key_vault_secrets_once()

    assert updated is True
    assert settings.JWT_SECRET == refreshed["JWT_SECRET"]
    assert settings.GROQ_API_KEY == "groq-key"
