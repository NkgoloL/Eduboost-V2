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


def test_jwt_keyring_normalization_and_mapping():
    import app.services.jwt_keyring as keyring

    # _normalize_status tests
    assert keyring._normalize_status(None) == "previous"
    assert keyring._normalize_status("ACTIVE") == "current"
    assert keyring._normalize_status("primary") == "current"
    assert keyring._normalize_status("OLD") == "previous"
    assert keyring._normalize_status("secondary") == "previous"
    assert keyring._normalize_status("legacy") == "previous"
    assert keyring._normalize_status("custom") == "custom"

    # _key_from_mapping errors
    with pytest.raises(keyring.JWTKeyringError, match="missing kid"):
        keyring._key_from_mapping({"secret": "sec"})

    with pytest.raises(keyring.JWTKeyringError, match="missing secret"):
        keyring._key_from_mapping({"kid": "k1", "secret": ""})

    # _key_from_mapping valid
    k = keyring._key_from_mapping({"key_id": "k2", "value": "sec2", "alg": "HS384", "status": "active"})
    assert k.kid == "k2"
    assert k.secret == "sec2"
    assert k.algorithm == "HS384"
    assert k.status == "current"


def test_jwt_keyring_parsing_formats():
    import app.services.jwt_keyring as keyring

    # Semicolon format
    with pytest.raises(keyring.JWTKeyringError, match="Invalid JWT key-ring entry"):
        keyring.parse_jwt_keyring("singlepart")

    with pytest.raises(keyring.JWTKeyringError, match="Invalid JWT key-ring entry"):
        keyring.parse_jwt_keyring(" :secret:HS256:current")

    with pytest.raises(keyring.JWTKeyringError, match="must contain one current key"):
        keyring.parse_jwt_keyring("k1:sec1:HS256:previous;k2:sec2:HS256:old")

    keys = keyring.parse_jwt_keyring("k1:sec1:HS256:current;k2:sec2:HS384:previous")
    assert len(keys) == 2
    assert keys[0].kid == "k1"
    assert keys[0].status == "current"

    # JSON format
    import json
    with pytest.raises(keyring.JWTKeyringError, match="Invalid JWT_KEYRING JSON"):
        keyring.parse_jwt_keyring("[{invalid_json")

    with pytest.raises(keyring.JWTKeyringError, match="must be a list"):
        keyring.parse_jwt_keyring('{"kid": "k1", "secret": "sec1"}')

    with pytest.raises(keyring.JWTKeyringError, match="cannot be empty"):
        keyring.parse_jwt_keyring("[]")

    data = json.dumps([
        {"kid": "k1", "secret": "sec1", "status": "current"},
        {"kid": "k2", "secret": "sec2", "status": "previous"}
    ])
    keys_json = keyring.parse_jwt_keyring(data)
    assert len(keys_json) == 2


def test_jwt_keyring_helpers_and_validation():
    import app.services.jwt_keyring as keyring

    # current_jwt_key error when no current
    with pytest.raises(keyring.JWTKeyringError, match="No current JWT key configured"):
        keyring.current_jwt_key([keyring.JWTKey(kid="k1", secret="s1", status="previous")])

    # helpers
    current_key = keyring.JWTKey(kid="k-current", secret="sec123", algorithm="HS512", status="current")
    with patch("app.services.jwt_keyring.parse_jwt_keyring", return_value=[current_key]):
        assert keyring.current_jwt_algorithm() == "HS512"
        assert keyring.current_jwt_headers() == {"kid": "k-current"}

    # is_placeholder_secret
    assert keyring.is_placeholder_secret(None) is True
    assert keyring.is_placeholder_secret("") is True
    assert keyring.is_placeholder_secret("changeme") is True
    assert keyring.is_placeholder_secret("change_me_later") is True
    assert keyring.is_placeholder_secret("placeholder_key") is True
    assert keyring.is_placeholder_secret("safe_real_production_secret_32_chars") is False

    # validate_jwt_keyring_environment
    keys = [keyring.JWTKey(kid="k1", secret="changeme", status="current")]
    with patch("app.services.jwt_keyring.parse_jwt_keyring", return_value=keys):
        with patch("app.services.jwt_keyring.is_production_environment", return_value=False):
            keyring.validate_jwt_keyring_environment()

        with patch("app.services.jwt_keyring.is_production_environment", return_value=True):
            with pytest.raises(keyring.JWTKeyringError, match="Production environment cannot use placeholder"):
                keyring.validate_jwt_keyring_environment()


def test_jwt_keyring_encode_and_decode_cycle():
    import app.services.jwt_keyring as keyring
    from app.core.jwt_compat import jwt

    sec_current = "super_secure_keyring_signing_secret_current_32chars"
    sec_old = "super_secure_keyring_signing_secret_old_32chars"
    keys = [
        keyring.JWTKey(kid="cur", secret=sec_current, algorithm="HS256", status="current"),
        keyring.JWTKey(kid="old", secret=sec_old, algorithm="HS256", status="previous"),
    ]

    with patch("app.services.jwt_keyring.is_production_environment", return_value=False):
        with patch("app.services.jwt_keyring.parse_jwt_keyring", return_value=keys):
            payload = {"sub": "user-456", "role": "learner"}
            token = keyring.encode_jwt_with_keyring(payload)
            decoded = keyring.decode_jwt_with_keyring(token)
            assert decoded["sub"] == "user-456"

            # decode token signed with old key
            old_token = jwt.encode(payload, sec_old, algorithm="HS256", headers={"kid": "old"})
            decoded_old = keyring.decode_jwt_with_keyring(old_token)
            assert decoded_old["sub"] == "user-456"

            # decode token with invalid signature raises
            bad_token = jwt.encode(payload, "unrelated_different_secret_key_32c", algorithm="HS256")
            with pytest.raises(Exception):
                keyring.decode_jwt_with_keyring(bad_token)


def test_jwt_keyring_environment_and_secret_resolution():
    import app.services.jwt_keyring as keyring

    # current_environment and is_production_environment
    with patch("os.getenv", return_value="prod"):
        assert keyring.is_production_environment() is True

    with patch("os.getenv", return_value="staging"):
        assert keyring.is_production_environment() is False

    # _configured_legacy_secret when candidate found
    with patch.dict("os.environ", {"JWT_SECRET": "custom-legacy-secret-123"}):
        assert keyring._configured_legacy_secret() == "custom-legacy-secret-123"

    # semicolon format with empty chunk (line 157)
    keys = keyring.parse_jwt_keyring(";;k1:sec1:HS256:current;;")
    assert len(keys) == 1
    assert keys[0].kid == "k1"



