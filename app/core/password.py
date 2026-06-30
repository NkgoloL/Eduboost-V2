"""
app/core/password.py
---------------------
Password security utilities for EduBoost SA V2.

Implements §3.2:
  - bcrypt with production-safe rounds (P0)
  - Password strength policy (P0)
  - Breached-password check via HIBP k-Anonymity API (P1)
  - Password change flow support (P1)
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

import httpx
from passlib.context import CryptContext

# ---------------------------------------------------------------------------
# Hashing configuration (§3.2 P0)
# ---------------------------------------------------------------------------
# bcrypt with 12 rounds is production-safe as of 2026 (~250 ms on modern hardware).
# To switch to Argon2id: change schemes to ["argon2"] and set deprecated=["bcrypt"].
BCRYPT_ROUNDS = 12

_pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=BCRYPT_ROUNDS,
)


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of *plain*."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Constant-time comparison of *plain* against *hashed*."""
    return _pwd_context.verify(plain, hashed)


def needs_rehash(hashed: str) -> bool:
    """True if the stored hash was created with an outdated cost factor."""
    return _pwd_context.needs_update(hashed)


# ---------------------------------------------------------------------------
# Strength policy (§3.2 P0)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PasswordStrengthResult:
    valid: bool
    errors: list[str]


# Minimum requirements — tuned for guardians / teachers of SA primary-school platform
_MIN_LENGTH = 10
_REQUIRES_UPPERCASE = True
_REQUIRES_LOWERCASE = True
_REQUIRES_DIGIT = True
_REQUIRES_SPECIAL = True
_SPECIAL_CHARS = r"!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?`~"

# Common-password blocklist (short; extend from a full list in production)
_COMMON_PASSWORDS = frozenset(
    {
        "password", "password1", "Password1!", "12345678", "iloveyou",
        "qwerty123", "admin1234", "letmein1", "eduboost1",
    }
)


def check_password_strength(password: str) -> PasswordStrengthResult:
    """Validate *password* against the platform strength policy.

    Returns a PasswordStrengthResult; callers raise HTTPException on
    ``valid=False``.
    """
    errors: list[str] = []

    if len(password) < _MIN_LENGTH:
        errors.append(f"Password must be at least {_MIN_LENGTH} characters.")

    if _REQUIRES_UPPERCASE and not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter.")

    if _REQUIRES_LOWERCASE and not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter.")

    if _REQUIRES_DIGIT and not re.search(r"\d", password):
        errors.append("Password must contain at least one digit.")

    if _REQUIRES_SPECIAL and not re.search(f"[{_SPECIAL_CHARS}]", password):
        errors.append("Password must contain at least one special character.")

    if password.lower() in _COMMON_PASSWORDS:
        errors.append("Password is too common. Please choose a more unique password.")

    return PasswordStrengthResult(valid=not errors, errors=errors)


# ---------------------------------------------------------------------------
# Breached-password check — HIBP k-Anonymity (§3.2 P1)
# ---------------------------------------------------------------------------
_HIBP_URL = "https://api.pwnedpasswords.com/range/{prefix}"
_HIBP_TIMEOUT = 3.0  # seconds — fail open on timeout to avoid blocking signup


async def is_password_breached(password: str) -> bool:
    """Check whether *password* has appeared in a known breach via HIBP.

    Uses the k-Anonymity model — only the first 5 hex chars of the SHA-1
    hash are sent to the HIBP API. Returns False on network error (fail open).
    """
    sha1 = hashlib.sha1(password.encode("utf-8"), usedforsecurity=False).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    try:
        async with httpx.AsyncClient(timeout=_HIBP_TIMEOUT) as client:
            resp = await client.get(
                _HIBP_URL.format(prefix=prefix),
                headers={"Add-Padding": "true"},
            )
            resp.raise_for_status()
            for line in resp.text.splitlines():
                hash_suffix, count = line.split(":", 1)
                if hash_suffix.upper() == suffix and int(count) > 0:
                    return True
        return False
    except Exception:
        # Fail open — do not block signup if HIBP is unreachable
        return False


# ---------------------------------------------------------------------------
# Passphrase guidance (§3.2 P2)
# ---------------------------------------------------------------------------
PASSPHRASE_GUIDANCE = (
    "Consider using a passphrase — four or more unrelated words joined together "
    "(e.g. 'purple-giraffe-sunrise-42!'). These are easy to remember and very secure."
)
