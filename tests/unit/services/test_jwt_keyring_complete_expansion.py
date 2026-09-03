from types import SimpleNamespace
from unittest.mock import patch
import pytest

from app.services.jwt_keyring import (
    JWTKey,
    JWTKeyringError,
    _configured_legacy_secret,
    _default_algorithm,
    _default_kid,
    _settings_value,
    current_jwt_signing_key,
    decode_jwt_with_keyring,
)


def test_jwt_keyring_edge_cases():
    # 1. current_jwt_signing_key (line 185)
    signing_key = current_jwt_signing_key()
    assert isinstance(signing_key, str)
    assert len(signing_key) > 0

    # 2. _settings_value with valid non-placeholder secret (lines 53-59)
    mock_settings = SimpleNamespace(
        CUSTOM_SECRET="valid_production_secret_value_1234567890",
        PLACEHOLDER_VAL="change_me_please",
    )
    with patch("app.services.jwt_keyring._settings", return_value=mock_settings):
        # Hits lines 54-58 returning text
        assert _settings_value("CUSTOM_SECRET") == "valid_production_secret_value_1234567890"
        # Placeholder secret returns empty string (line 57 condition)
        assert _settings_value("PLACEHOLDER_VAL") == ""
        # Nonexistent attribute returns empty string
        assert _settings_value("NONEXISTENT") == ""

    # 3. _configured_legacy_secret fallback to dev default (line 100)
    with patch("os.getenv", return_value=""), \
         patch("app.services.jwt_keyring._settings_value", return_value=""):
        secret = _configured_legacy_secret()
        assert secret == "dev-insecure-secret-change-me"

    # 4. _default_algorithm and _default_kid fallbacks
    with patch("os.getenv", return_value=""), \
         patch("app.services.jwt_keyring._settings_value", return_value=""):
        assert _default_algorithm() == "HS256"
        assert _default_kid() == "legacy"

    # 5. decode_jwt_with_keyring when no keys in keyring (line 239)
    import app.services.jwt_keyring as keyring
    with patch("app.services.jwt_keyring.validate_jwt_keyring_environment"), \
         patch("jwt.get_unverified_header", return_value={"kid": "k1"}), \
         patch("app.services.jwt_keyring.parse_jwt_keyring", return_value=[]):
        with pytest.raises(keyring.JWTKeyringError, match="Unable to decode JWT with configured key-ring"):
            keyring.decode_jwt_with_keyring("dummy.token.here")

