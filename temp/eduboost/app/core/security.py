"""Authentication, authorisation, and cryptography utilities.

Provides JWT token issuance/validation, role-based access control (RBAC),
bcrypt password hashing, and AES-GCM authenticated encryption for PII
fields stored in the database.

Warning:
    The AES-CBC placeholder (SEC-002) **must** be replaced with
    :func:`encrypt_aes_gcm` before any PII is ingested in production.
    AES-CBC is malleable and provides no authentication guarantee.

Example:
    Create and verify a token::

        token = create_access_token({"sub": "user-uuid", "role": "parent"})
        payload = verify_token(token)
        assert payload["role"] == "parent"
"""

import base64
import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


class UserRole(str, Enum):
    """Enumeration of all supported RBAC roles.

    Attributes:
        STUDENT: Learner account — read-only access to own lessons/progress.
        PARENT: Guardian account — manages learner profiles and consent.
        TEACHER: Educator account — read access to class-level analytics.
        ADMIN: Platform administrator — full access.

    Example:
        ::

            from app.core.security import UserRole
            role = UserRole.PARENT
            assert role == "parent"
    """

    STUDENT = "student"
    PARENT = "parent"
    TEACHER = "teacher"
    ADMIN = "admin"


def hash_password(plain: str) -> str:
    """Hash a plaintext password using bcrypt.

    Args:
        plain: The raw password provided by the user at registration.

    Returns:
        str: A bcrypt hash string suitable for storage in the database.

    Example:
        ::

            hashed = hash_password("MyS3cretP@ss")
            assert hashed != "MyS3cretP@ss"
            assert verify_password("MyS3cretP@ss", hashed)
    """
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash.

    Args:
        plain: The raw password provided at login.
        hashed: The bcrypt hash retrieved from the database.

    Returns:
        bool: ``True`` if the password matches, ``False`` otherwise.

    Example:
        ::

            h = hash_password("correct")
            assert verify_password("correct", h) is True
            assert verify_password("wrong", h) is False
    """
    return _pwd_context.verify(plain, hashed)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Issue a signed JWT access token.

    Args:
        data: Payload claims to encode.  Must include ``"sub"`` (subject
            UUID) and ``"role"`` (:class:`UserRole` value).
        expires_delta: Token lifetime.  Defaults to
            :attr:`~app.core.config.Settings.ACCESS_TOKEN_EXPIRE_MINUTES`.

    Returns:
        str: A compact, URL-safe JWT string.

    Raises:
        ValueError: If ``data`` does not contain a ``"sub"`` key.

    Example:
        ::

            token = create_access_token({"sub": "abc-123", "role": "student"})
            assert isinstance(token, str)
    """
    if "sub" not in data:
        raise ValueError("Token payload must contain 'sub'")
    payload = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload.update({"exp": expire, "jti": base64.urlsafe_b64encode(os.urandom(16)).decode()})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT access token.

    Args:
        token: The compact JWT string from the ``Authorization: Bearer``
            header.

    Returns:
        Dict[str, Any]: The decoded payload containing at minimum ``"sub"``,
        ``"role"``, ``"exp"``, and ``"jti"``.

    Raises:
        jose.JWTError: If the token is expired, has an invalid signature, or
            is otherwise malformed.

    Example:
        ::

            token = create_access_token({"sub": "x", "role": "admin"})
            payload = verify_token(token)
            assert payload["sub"] == "x"
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])


def encrypt_aes_gcm(plaintext: str) -> str:
    """Encrypt a string with AES-256-GCM authenticated encryption.

    Generates a random 96-bit nonce per call, prepends it to the
    ciphertext, and returns the whole payload as a base-64 string.
    The authentication tag (16 bytes) is appended by the GCM mode and
    verified automatically on decryption.

    Args:
        plaintext: The sensitive string to encrypt (e.g. an email address).

    Returns:
        str: Base-64-encoded ``nonce || ciphertext || tag`` blob.

    Raises:
        ValueError: If :attr:`~app.core.config.Settings.AES_ENCRYPTION_KEY`
            is not exactly 32 bytes when decoded.

    Example:
        ::

            blob = encrypt_aes_gcm("user@example.com")
            assert isinstance(blob, str)
            assert decrypt_aes_gcm(blob) == "user@example.com"
    """
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    key = bytes.fromhex(settings.AES_ENCRYPTION_KEY)
    nonce = os.urandom(12)
    ct = AESGCM(key).encrypt(nonce, plaintext.encode(), None)
    return base64.b64encode(nonce + ct).decode()


def decrypt_aes_gcm(blob: str) -> str:
    """Decrypt an AES-256-GCM encrypted blob produced by :func:`encrypt_aes_gcm`.

    Args:
        blob: Base-64-encoded ``nonce || ciphertext || tag`` string.

    Returns:
        str: The original plaintext string.

    Raises:
        cryptography.exceptions.InvalidTag: If the ciphertext has been
            tampered with or the wrong key is used.

    Example:
        ::

            blob = encrypt_aes_gcm("secret")
            assert decrypt_aes_gcm(blob) == "secret"
    """
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    key = bytes.fromhex(settings.AES_ENCRYPTION_KEY)
    raw = base64.b64decode(blob)
    nonce, ct = raw[:12], raw[12:]
    return AESGCM(key).decrypt(nonce, ct, None).decode()


def hash_email(email: str) -> str:
    """Produce a SHA-256 hex digest of an email address for index lookups.

    The hash is used as a pseudonymous lookup key so the plaintext email
    is never stored in a queryable column.

    Args:
        email: The raw email address (lowercased before hashing).

    Returns:
        str: Lowercase hex SHA-256 digest (64 characters).

    Example:
        ::

            h = hash_email("User@Example.com")
            assert len(h) == 64
            assert h == hash_email("user@example.com")  # case-insensitive
    """
    import hashlib

    return hashlib.sha256(email.lower().encode()).hexdigest()
