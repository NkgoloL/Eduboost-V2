"""
EduBoost SA — Security Helpers
JWT tokens, PII encryption, password hashing, pseudonymisation.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from cryptography.fernet import Fernet
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Password Hashing ──────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


# ── JWT Tokens ────────────────────────────────────────────────────────────────

def create_access_token(subject: str | UUID, extra: dict[str, Any] | None = None) -> str:
    cfg = get_settings()
    expires = datetime.now(UTC) + timedelta(minutes=cfg.jwt_access_token_expire_minutes)
    payload = {
        "sub": str(subject),
        "exp": expires,
        "iat": datetime.now(UTC),
        "type": "access",
        **(extra or {}),
    }
    return jwt.encode(payload, cfg.jwt_secret, algorithm=cfg.jwt_algorithm)


def create_refresh_token(subject: str | UUID) -> str:
    cfg = get_settings()
    expires = datetime.now(UTC) + timedelta(days=cfg.jwt_refresh_token_expire_days)
    payload = {
        "sub": str(subject),
        "exp": expires,
        "iat": datetime.now(UTC),
        "type": "refresh",
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, cfg.jwt_secret, algorithm=cfg.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT. Raises JWTError on failure."""
    cfg = get_settings()
    return jwt.decode(token, cfg.jwt_secret, algorithms=[cfg.jwt_algorithm])


def verify_access_token(token: str) -> str:
    """Return the subject (user ID) or raise JWTError."""
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise JWTError("Not an access token")
    return payload["sub"]


# ── PII Encryption (Fernet symmetric) ────────────────────────────────────────

def _get_fernet() -> Fernet:
    cfg = get_settings()
    # Derive a 32-byte key from config secret using HKDF-like approach
    key_material = hmac.new(
        cfg.encryption_key.encode(),
        cfg.encryption_salt.encode(),
        hashlib.sha256,
    ).digest()
    import base64
    fernet_key = base64.urlsafe_b64encode(key_material)
    return Fernet(fernet_key)


def encrypt_pii(plaintext: str) -> str:
    """Encrypt PII (e.g., guardian email). Returns hex-encoded ciphertext."""
    return _get_fernet().encrypt(plaintext.encode()).hex()


def decrypt_pii(ciphertext_hex: str) -> str:
    """Decrypt PII ciphertext."""
    return _get_fernet().decrypt(bytes.fromhex(ciphertext_hex)).decode()


def hash_email(email: str) -> str:
    """SHA-256 hash of email for lookup without storing plaintext."""
    cfg = get_settings()
    return hashlib.sha256(
        f"{email.lower().strip()}{cfg.encryption_salt}".encode()
    ).hexdigest()


# ── Pseudonymisation ──────────────────────────────────────────────────────────

def generate_pseudonym_id() -> str:
    """Generate a stable pseudonym for LLM calls — never the real learner UUID."""
    return f"learner_{secrets.token_hex(12)}"


def pseudonymise_for_llm(learner_id: UUID, session_seed: str = "") -> str:
    """
    Deterministic pseudonym for a learner within an LLM context.
    Changes per session so it cannot be correlated across calls.
    Real learner UUIDs are NEVER sent to external LLM providers.
    """
    cfg = get_settings()
    h = hmac.new(
        cfg.encryption_key.encode(),
        f"{learner_id}{session_seed}{cfg.encryption_salt}".encode(),
        hashlib.sha256,
    ).hexdigest()[:16]
    return f"learner_{h}"


# ── Token Generation ──────────────────────────────────────────────────────────

def generate_secure_token(length: int = 32) -> str:
    """URL-safe random token for email verification, consent links, etc."""
    return secrets.token_urlsafe(length)
