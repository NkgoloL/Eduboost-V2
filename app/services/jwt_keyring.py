from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from jose import jwt


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


def _legacy_secret() -> str:
    for name in ("JWT_SECRET_KEY", "SECRET_KEY", "ACCESS_TOKEN_SECRET_KEY"):
        value = _env(name)
        if value:
            return value
    return "dev-insecure-secret-change-me"


def parse_jwt_keyring(raw: str | None = None) -> list[JWTKey]:
    """Parse JWT key-ring configuration.

    Supported formats:
    - JSON list: [{"kid":"2026-05","secret":"...","status":"current"}]
    - Semicolon: 2026-05:secret:HS256:current;2026-04:old:HS256:previous
    """
    raw_value = (raw if raw is not None else _env("JWT_KEYRING")).strip()
    if not raw_value:
        return [
            JWTKey(
                kid=_env("JWT_CURRENT_KID", "legacy"),
                secret=_legacy_secret(),
                algorithm=_env("JWT_ALGORITHM", "HS256"),
                status="current",
            )
        ]

    if raw_value.startswith("["):
        parsed = json.loads(raw_value)
        keys = [
            JWTKey(
                kid=str(item["kid"]),
                secret=str(item["secret"]),
                algorithm=str(item.get("algorithm", "HS256")),
                status=str(item.get("status", "previous")),
            )
            for item in parsed
        ]
    else:
        keys = []
        for chunk in raw_value.split(";"):
            if not chunk.strip():
                continue
            parts = chunk.split(":")
            if len(parts) < 2:
                raise JWTKeyringError(f"Invalid JWT key-ring entry: {chunk!r}")
            kid, secret = parts[0], parts[1]
            algorithm = parts[2] if len(parts) >= 3 and parts[2] else "HS256"
            status = parts[3] if len(parts) >= 4 and parts[3] else "previous"
            keys.append(JWTKey(kid=kid, secret=secret, algorithm=algorithm, status=status))

    if not keys:
        raise JWTKeyringError("JWT key-ring cannot be empty")
    if not any(key.status == "current" for key in keys):
        raise JWTKeyringError("JWT key-ring must contain one current key")
    return keys


def current_jwt_key(keys: list[JWTKey] | None = None) -> JWTKey:
    for key in keys or parse_jwt_keyring():
        if key.status == "current":
            return key
    raise JWTKeyringError("No current JWT key configured")


def current_jwt_signing_key() -> str:
    return current_jwt_key().secret


def current_jwt_algorithm(default: str = "HS256") -> str:
    return current_jwt_key().algorithm or default


def current_jwt_headers() -> dict[str, str]:
    return {"kid": current_jwt_key().kid}


def encode_jwt_with_keyring(payload: dict[str, Any]) -> str:
    key = current_jwt_key()
    return jwt.encode(payload, key.secret, algorithm=key.algorithm, headers={"kid": key.kid})


def decode_jwt_with_keyring(token: str, *, options: dict[str, Any] | None = None) -> dict[str, Any]:
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
    "current_jwt_algorithm",
    "current_jwt_headers",
    "current_jwt_key",
    "current_jwt_signing_key",
    "decode_jwt_with_keyring",
    "encode_jwt_with_keyring",
    "parse_jwt_keyring",
]
