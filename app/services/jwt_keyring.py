from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from jose import jwt


PLACEHOLDER_JWT_SECRETS = {
    "",
    "dev-insecure-secret-change-me",
    "change_me_in_production_at_least_32_chars",
    "changeme",
    "change-me",
    "secret",
    "super-secret",
    "your-secret-key",
    "replace-me",
}


@dataclass(frozen=True)
class JWTKey:
    kid: str
    secret: str
    algorithm: str = "HS256"
    status: str = "current"


class JWTKeyringError(RuntimeError):
    """Raised when JWT key-ring configuration is invalid."""


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _settings() -> Any | None:
    try:
        from app.core.config import get_settings
        get_settings.cache_clear()
        return get_settings()
    except Exception:
        return None


def _settings_value(*names: str) -> str:
    settings = _settings()
    if settings is None:
        return ""
    for name in names:
        value = getattr(settings, name, None)
        if value is not None:
            text = str(value).strip()
            if text and not is_placeholder_secret(text):
                return text
    return ""


def current_environment() -> str:
    return (
        _env("ENVIRONMENT")
        or _env("APP_ENV")
        or _env("ENV")
        or _settings_value("ENVIRONMENT", "APP_ENV", "ENV", "environment")
        or "development"
    ).lower()


def is_production_environment() -> bool:
    return current_environment() in {"prod", "production", "live"}


def _configured_legacy_secret() -> str:
    """Resolve legacy single-key JWT secret.

    Resolution order:
    1. settings.JWT_SECRET
    2. JWT_SECRET
    3. settings.JWT_SECRET_KEY
    4. JWT_SECRET_KEY
    5. SECRET_KEY / ACCESS_TOKEN_SECRET_KEY compatibility names
    6. development-only fallback
    """
    candidates = [
        _env("JWT_SECRET"),
        _env("JWT_SECRET_KEY"),
        _settings_value("JWT_SECRET"),
        _settings_value("JWT_SECRET_KEY"),
        _env("SECRET_KEY"),
        _settings_value("SECRET_KEY"),
        _env("ACCESS_TOKEN_SECRET_KEY"),
        _settings_value("ACCESS_TOKEN_SECRET_KEY"),
    ]
    for value in candidates:
        if value:
            return value
    return "dev-insecure-secret-change-me"


def _default_algorithm() -> str:
    return _env("JWT_ALGORITHM") or _settings_value("JWT_ALGORITHM", "ALGORITHM") or "HS256"


def _default_kid() -> str:
    return _env("JWT_CURRENT_KID") or _settings_value("JWT_CURRENT_KID") or "legacy"


def _normalize_status(value: str | None) -> str:
    status = (value or "previous").strip().lower()
    if status in {"active", "primary"}:
        return "current"
    if status in {"old", "secondary", "legacy"}:
        return "previous"
    return status


def _key_from_mapping(item: dict[str, Any]) -> JWTKey:
    kid = str(item.get("kid") or item.get("key_id") or "").strip()
    secret = str(item.get("secret") or item.get("value") or "").strip()
    algorithm = str(item.get("algorithm") or item.get("alg") or "HS256").strip()
    status = _normalize_status(str(item.get("status") or "previous"))
    if not kid:
        raise JWTKeyringError("JWT key-ring entry is missing kid")
    if not secret:
        raise JWTKeyringError(f"JWT key-ring entry {kid!r} is missing secret")
    return JWTKey(kid=kid, secret=secret, algorithm=algorithm, status=status)


def parse_jwt_keyring(raw: str | None = None) -> list[JWTKey]:
    """Parse JWT_KEYRING or build a single-key ring from safe fallback resolution."""
    raw_value = (raw if raw is not None else _env("JWT_KEYRING")).strip()
    if not raw_value:
        return [
            JWTKey(
                kid=_default_kid(),
                secret=_configured_legacy_secret(),
                algorithm=_default_algorithm(),
                status="current",
            )
        ]

    if raw_value.startswith("["):
        try:
            parsed = json.loads(raw_value)
        except json.JSONDecodeError as exc:
            raise JWTKeyringError(f"Invalid JWT_KEYRING JSON: {exc}") from exc
        if not isinstance(parsed, list):
            raise JWTKeyringError("JWT_KEYRING JSON must be a list")
        keys = [_key_from_mapping(item) for item in parsed]
    else:
        keys = []
        for chunk in raw_value.split(";"):
            if not chunk.strip():
                continue
            parts = chunk.split(":")
            if len(parts) < 2:
                raise JWTKeyringError(f"Invalid JWT key-ring entry: {chunk!r}")
            kid = parts[0].strip()
            secret = parts[1].strip()
            algorithm = parts[2].strip() if len(parts) >= 3 and parts[2].strip() else "HS256"
            status = _normalize_status(parts[3] if len(parts) >= 4 else "previous")
            if not kid or not secret:
                raise JWTKeyringError(f"Invalid JWT key-ring entry: {chunk!r}")
            keys.append(JWTKey(kid=kid, secret=secret, algorithm=algorithm, status=status))

    if not keys:
        raise JWTKeyringError("JWT key-ring cannot be empty")
    if not any(key.status == "current" for key in keys):
        raise JWTKeyringError("JWT key-ring must contain one current key")
    return keys


def current_jwt_key(keys: list[JWTKey] | None = None) -> JWTKey:
    keyring = keys or parse_jwt_keyring()
    for key in keyring:
        if key.status == "current":
            return key
    raise JWTKeyringError("No current JWT key configured")


def current_jwt_signing_key() -> str:
    return current_jwt_key().secret


def current_jwt_algorithm(default: str = "HS256") -> str:
    key = current_jwt_key()
    return key.algorithm or default


def current_jwt_headers() -> dict[str, str]:
    return {"kid": current_jwt_key().kid}


def is_placeholder_secret(secret: str | None) -> bool:
    if secret is None:
        return True
    normalised = secret.strip().lower()
    if normalised in PLACEHOLDER_JWT_SECRETS:
        return True
    # Catch any "CHANGE_ME*" or "PLACEHOLDER*" sentinel defaults from .env
    return normalised.startswith("change_me") or normalised.startswith("placeholder")


def validate_jwt_keyring_environment() -> None:
    """Fail closed when production would use a placeholder JWT secret."""
    keys = parse_jwt_keyring()
    placeholder_kids = [key.kid for key in keys if is_placeholder_secret(key.secret)]
    if is_production_environment() and placeholder_kids:
        raise JWTKeyringError(
            "Production environment cannot use placeholder JWT secrets. "
            f"Invalid kid(s): {', '.join(placeholder_kids)}"
        )


def encode_jwt_with_keyring(payload: dict[str, Any]) -> str:
    validate_jwt_keyring_environment()
    key = current_jwt_key()
    return jwt.encode(payload, key.secret, algorithm=key.algorithm, headers={"kid": key.kid})


def decode_jwt_with_keyring(token: str, *, options: dict[str, Any] | None = None) -> dict[str, Any]:
    validate_jwt_keyring_environment()
    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")
    keys = parse_jwt_keyring()
    ordered = sorted(keys, key=lambda key: 0 if key.kid == kid else 1)
    last_error: Exception | None = None
    for key in ordered:
        try:
            return jwt.decode(token, key.secret, algorithms=[key.algorithm], options=options)
        except Exception as exc:
            last_error = exc
            continue
    if last_error is not None:
        raise last_error
    raise JWTKeyringError("Unable to decode JWT with configured key-ring")


__all__ = [
    "JWTKey",
    "JWTKeyringError",
    "PLACEHOLDER_JWT_SECRETS",
    "current_environment",
    "current_jwt_algorithm",
    "current_jwt_headers",
    "current_jwt_key",
    "current_jwt_signing_key",
    "decode_jwt_with_keyring",
    "encode_jwt_with_keyring",
    "is_placeholder_secret",
    "is_production_environment",
    "parse_jwt_keyring",
    "validate_jwt_keyring_environment",
]
