"""
app/core/token_config.py
--------------------------
JWT signing-key configuration with `kid`-based rotation support.

Implements §3.3:
  - Access-token TTL: 15 minutes (P0)
  - Refresh-token TTL: 7 days (P0)
  - kid rotation: current key + previous-key validation window (P1)
  - Redis-backed revocation store (P0)
  - Graceful degradation when Redis is unavailable (P0 decision: DENY access)
  - Emergency revoke-all procedure (P1)
"""

from __future__ import annotations

import hashlib
import os
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import redis.asyncio as aioredis
from jose import JWTError, jwt
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# TTL constants (§3.3 P0)
# ---------------------------------------------------------------------------
ACCESS_TOKEN_TTL_MINUTES: int = int(os.getenv("ACCESS_TOKEN_TTL_MINUTES", "15"))
REFRESH_TOKEN_TTL_DAYS: int = int(os.getenv("REFRESH_TOKEN_TTL_DAYS", "7"))

ALGORITHM = "HS256"

# ---------------------------------------------------------------------------
# Signing key config (§3.3 P1 — kid rotation)
# ---------------------------------------------------------------------------
# Set JWT_SIGNING_KEY and JWT_PREVIOUS_KEY in environment.
# JWT_SIGNING_KEY_ID / JWT_PREVIOUS_KEY_ID name each key.
# When rotating: copy current → previous, generate new current.

CURRENT_KEY = os.environ["JWT_SIGNING_KEY"]          # required
CURRENT_KID = os.getenv("JWT_SIGNING_KEY_ID", "k1")

PREVIOUS_KEY = os.getenv("JWT_PREVIOUS_KEY")         # optional — validation window
PREVIOUS_KID = os.getenv("JWT_PREVIOUS_KEY_ID", "k0")

# Map kid → secret for O(1) validation lookup
_KEY_STORE: dict[str, str] = {CURRENT_KID: CURRENT_KEY}
if PREVIOUS_KEY:
    _KEY_STORE[PREVIOUS_KID] = PREVIOUS_KEY


def _secret_for_kid(kid: str) -> str:
    key = _KEY_STORE.get(kid)
    if not key:
        raise JWTError(f"Unknown signing key id: {kid!r}")
    return key


# ---------------------------------------------------------------------------
# Redis revocation (§3.3 P0)
# ---------------------------------------------------------------------------
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REVOCATION_KEY_PREFIX = "revoked_jti:"
FAMILY_PREFIX = "token_family:"
REVOKE_ALL_EPOCH_KEY = "revoke_all_epoch"

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis


# ---------------------------------------------------------------------------
# Token models
# ---------------------------------------------------------------------------

class TokenPair(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_TTL_MINUTES * 60


class RefreshTokenRecord(BaseModel):
    """Stored alongside the hashed refresh token."""
    family_id: str
    user_id: str
    issued_at: datetime
    expires_at: datetime


# ---------------------------------------------------------------------------
# Issue tokens
# ---------------------------------------------------------------------------

def create_access_token(
    user_id: str,
    role: str,
    *,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Create a signed access JWT with kid header."""
    now = datetime.now(tz=timezone.utc)
    claims: dict[str, Any] = {
        "sub": user_id,
        "role": role,
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_TTL_MINUTES),
        "kid": CURRENT_KID,
    }
    if extra_claims:
        claims.update(extra_claims)
    return jwt.encode(claims, CURRENT_KEY, algorithm=ALGORITHM, headers={"kid": CURRENT_KID})


def create_refresh_token(family_id: str | None = None) -> tuple[str, str, RefreshTokenRecord]:
    """Return (raw_token, hashed_token, record).

    Refresh tokens are opaque random bytes — not JWTs.
    The raw token is sent to the client; only the hash is stored.
    """
    raw = secrets.token_urlsafe(64)
    hashed = _hash_token(raw)
    fid = family_id or str(uuid.uuid4())
    now = datetime.now(tz=timezone.utc)
    record = RefreshTokenRecord(
        family_id=fid,
        user_id="",            # caller fills in
        issued_at=now,
        expires_at=now + timedelta(days=REFRESH_TOKEN_TTL_DAYS),
    )
    return raw, hashed, record


def _hash_token(raw: str) -> str:
    """SHA-256 hash of a raw token for at-rest storage (§3.3 P0)."""
    return hashlib.sha256(raw.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Verify access token
# ---------------------------------------------------------------------------

async def verify_access_token(token: str) -> dict[str, Any]:
    """Decode and validate an access JWT.

    Raises JWTError on any failure.
    Behaviour when Redis is unavailable: DENY (fail closed) — §3.3 P0 decision.
    """
    # Peek at header to get kid before full decode
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid", CURRENT_KID)
        secret = _secret_for_kid(kid)
        claims = jwt.decode(token, secret, algorithms=[ALGORITHM])
    except JWTError:
        raise

    jti = claims.get("jti")
    if not jti:
        raise JWTError("Token missing jti claim")

    # Check per-token revocation
    try:
        r = await get_redis()
        if await r.exists(f"{REVOCATION_KEY_PREFIX}{jti}"):
            raise JWTError("Token has been revoked")

        # Check global revoke-all epoch (§3.3 P1 emergency revoke-all)
        epoch_str = await r.get(REVOKE_ALL_EPOCH_KEY)
        if epoch_str:
            epoch = datetime.fromisoformat(epoch_str).replace(tzinfo=timezone.utc)
            iat = datetime.fromtimestamp(claims["iat"], tz=timezone.utc)
            if iat < epoch:
                raise JWTError("Token predates global revocation epoch")

    except aioredis.RedisError as exc:
        # Redis unavailable → fail closed (deny access) per §3.3 P0 decision
        raise JWTError(f"Revocation store unavailable: {exc}") from exc

    return claims


# ---------------------------------------------------------------------------
# Revocation helpers (§3.3 P0 / P1)
# ---------------------------------------------------------------------------

async def revoke_jti(jti: str, ttl_seconds: int = ACCESS_TOKEN_TTL_MINUTES * 60) -> None:
    """Add a single jti to the Redis deny-list."""
    r = await get_redis()
    await r.setex(f"{REVOCATION_KEY_PREFIX}{jti}", ttl_seconds, "1")


async def revoke_token_family(family_id: str) -> None:
    """Revoke all tokens belonging to a family (reuse detection, §3.3 P0)."""
    r = await get_redis()
    key = f"{FAMILY_PREFIX}{family_id}:revoked"
    await r.set(key, "1", ex=REFRESH_TOKEN_TTL_DAYS * 86400)


async def is_family_revoked(family_id: str) -> bool:
    r = await get_redis()
    return bool(await r.exists(f"{FAMILY_PREFIX}{family_id}:revoked"))


async def emergency_revoke_all() -> datetime:
    """Set a global epoch — all tokens issued before now are invalid (§3.3 P1)."""
    now = datetime.now(tz=timezone.utc)
    r = await get_redis()
    await r.set(REVOKE_ALL_EPOCH_KEY, now.isoformat())
    return now


async def add_persistent_revocation_fallback(jti: str, expires_at: datetime) -> None:
    """Write revocation to Redis AND the DB fallback table (§3.3 P1).

    Callers should import and call this instead of revoke_jti when a persistent
    fallback is required (e.g. refresh token revocation that must survive Redis restart).

    The DB-side write is delegated to app.repositories.revocation_repository.
    """
    # Redis fast path
    ttl = max(1, int((expires_at - datetime.now(tz=timezone.utc)).total_seconds()))
    await revoke_jti(jti, ttl)
    # DB fallback — import lazily to honour import-boundary rules
    from app.repositories.revocation_repository import persist_revocation  # noqa: PLC0415
    await persist_revocation(jti, expires_at)
