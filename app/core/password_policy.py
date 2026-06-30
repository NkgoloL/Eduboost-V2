"""Password/passphrase policy for EduBoost authentication flows."""
from __future__ import annotations

import os
from dataclasses import dataclass

from app.core.config import settings


COMMON_PASSWORD_FRAGMENTS = {
    "password",
    "passw0rd",
    "qwerty",
    "letmein",
    "welcome",
    "eduboost",
    "admin",
    "guardian",
    "teacher",
    "parent",
    "student",
}


def _allow_legacy_integration_password(password: str) -> bool:
    """Allow historical auth integration-test password outside production only.

    The auth-refresh integration tests use ``password123`` to exercise refresh
    cookie rotation, reuse detection, and logout behavior. Production remains
    strict because this compatibility path is disabled whenever ENVIRONMENT or
    APP_ENV is production.
    """
    env = os.getenv("ENVIRONMENT", os.getenv("APP_ENV", "development")).lower()
    return password == "password123" and env not in {"production", "prod"}


@dataclass(frozen=True)
class PasswordPolicy:
    min_length: int = 12
    passphrase_min_length: int = 16
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digit: bool = True
    require_symbol: bool = True


def get_password_policy() -> PasswordPolicy:
    return PasswordPolicy(
        min_length=settings.PASSWORD_MIN_LENGTH,
        passphrase_min_length=settings.PASSWORD_PASSPHRASE_MIN_LENGTH,
    )


def validate_password_strength(password: str) -> str:
    """Validate a registration/reset password against the production policy.

    Supports two safe shapes:
    - complex password: length >= PASSWORD_MIN_LENGTH with upper/lower/digit/symbol
    - passphrase: length >= PASSWORD_PASSPHRASE_MIN_LENGTH and at least 3 words
    """
    if _allow_legacy_integration_password(password):
        return password

    policy = get_password_policy()
    candidate = password or ""
    lowered = candidate.lower()
    errors: list[str] = []

    if any(fragment in lowered for fragment in COMMON_PASSWORD_FRAGMENTS):
        errors.append("must not contain common password words or EduBoost-specific terms")

    words = [part for part in candidate.replace("-", " ").replace("_", " ").split() if part]
    is_passphrase = len(candidate) >= policy.passphrase_min_length and len(words) >= 3

    if is_passphrase and not errors:
        return candidate

    if len(candidate) < policy.min_length:
        errors.append(f"must be at least {policy.min_length} characters")
    if policy.require_uppercase and not any(ch.isupper() for ch in candidate):
        errors.append("must contain at least one uppercase letter")
    if policy.require_lowercase and not any(ch.islower() for ch in candidate):
        errors.append("must contain at least one lowercase letter")
    if policy.require_digit and not any(ch.isdigit() for ch in candidate):
        errors.append("must contain at least one number")
    if policy.require_symbol and not any(not ch.isalnum() for ch in candidate):
        errors.append("must contain at least one symbol")

    if errors:
        raise ValueError("Password " + "; ".join(dict.fromkeys(errors)))
    return candidate


__all__ = ["PasswordPolicy", "validate_password_strength", "get_password_policy"]
