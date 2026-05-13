"""
app/services/auth_service.py
------------------------------
Authentication service for EduBoost SA V2.

Implements §3.1 (all auth flows), §3.2 (password security),
§3.3 (token policy), §3.1 P1 (lockout + security alerts).

This service contains ALL auth business logic.
The router (app/api_v2_routers/auth.py) calls these methods and maps
results to HTTP responses — no business logic lives in the router.
"""

from __future__ import annotations

import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.password import (
    check_password_strength,
    hash_password,
    is_password_breached,
    needs_rehash,
    verify_password,
)
from app.core.token_config import (
    TokenPair,
    add_persistent_revocation_fallback,
    create_access_token,
    create_refresh_token,
    is_family_revoked,
    revoke_jti,
    revoke_token_family,
    verify_access_token,
)

logger = logging.getLogger("eduboost.auth")

# ---------------------------------------------------------------------------
# Account lockout config (§3.1 P1)
# ---------------------------------------------------------------------------
_MAX_FAILED_ATTEMPTS = 5
_LOCKOUT_DURATION_MINUTES = 15

# ---------------------------------------------------------------------------
# Password reset token TTL
# ---------------------------------------------------------------------------
_RESET_TOKEN_TTL_MINUTES = 30
_EMAIL_VERIFY_TOKEN_TTL_HOURS = 24


# ---------------------------------------------------------------------------
# Result models (avoid coupling to FastAPI schemas)
# ---------------------------------------------------------------------------

class AuthError(Exception):
    """Raised by auth service on business-rule failures.

    Callers map to HTTP 400/401/403/409 as appropriate.
    """
    def __init__(self, message: str, code: str = "auth_error") -> None:
        super().__init__(message)
        self.code = code


class SignupResult:
    def __init__(self, user_id: str, email: str) -> None:
        self.user_id = user_id
        self.email = email


class LoginResult:
    def __init__(self, token_pair: TokenPair, raw_refresh_token: str) -> None:
        self.token_pair = token_pair
        self.raw_refresh_token = raw_refresh_token


# ---------------------------------------------------------------------------
# AuthService
# ---------------------------------------------------------------------------

class AuthService:
    """All authentication business logic for EduBoost SA V2.

    Dependencies are injected via constructor to keep the service testable
    without FastAPI or Redis running.
    """

    def __init__(self, user_repo: Any, token_repo: Any, email_service: Any) -> None:
        self._users = user_repo
        self._tokens = token_repo
        self._email = email_service

    # ------------------------------------------------------------------
    # §3.1 — Signup
    # ------------------------------------------------------------------

    async def guardian_signup(
        self,
        email: str,
        password: str,
        full_name: str,
    ) -> SignupResult:
        """Register a new guardian account.

        Verifies: duplicate email (§3.1), password strength (§3.2),
        optionally breached-password check (§3.2 P1).
        """
        # Duplicate email check (§3.1 P0)
        existing = await self._users.find_by_email(email)
        if existing:
            raise AuthError("An account with this email already exists.", code="duplicate_email")

        # Password strength (§3.2 P0)
        strength = check_password_strength(password)
        if not strength.valid:
            raise AuthError(" ".join(strength.errors), code="weak_password")

        # Breached password check (§3.2 P1 — fail open on HIBP timeout)
        if await is_password_breached(password):
            raise AuthError(
                "This password has appeared in a known data breach. Please choose a different password.",
                code="breached_password",
            )

        hashed = hash_password(password)
        user_id = str(uuid.uuid4())
        await self._users.create(
            user_id=user_id,
            email=email,
            password_hash=hashed,
            full_name=full_name,
            role="guardian",
            is_verified=False,
        )

        # Trigger email verification (§3.1 P0)
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(tz=timezone.utc) + timedelta(hours=_EMAIL_VERIFY_TOKEN_TTL_HOURS)
        await self._tokens.store_email_verify_token(user_id=user_id, token=token, expires_at=expires_at)
        await self._email.send_verification_email(email=email, token=token)

        logger.info("guardian_signup", extra={"user_id": user_id, "email": email})
        return SignupResult(user_id=user_id, email=email)

    # ------------------------------------------------------------------
    # §3.1 — Login
    # ------------------------------------------------------------------

    async def login(self, email: str, password: str, ip: str = "") -> LoginResult:
        """Authenticate a user and issue a token pair.

        Handles: success, wrong password, nonexistent account, lockout (§3.1 P1).
        """
        user = await self._users.find_by_email(email)

        # Nonexistent account — same error as wrong password to prevent enumeration
        if not user:
            await self._record_failed_attempt(None, ip)
            raise AuthError("Invalid email or password.", code="invalid_credentials")

        # Lockout check (§3.1 P1)
        if await self._is_locked_out(user["user_id"]):
            raise AuthError(
                f"Account temporarily locked after too many failed attempts. "
                f"Try again in {_LOCKOUT_DURATION_MINUTES} minutes.",
                code="account_locked",
            )

        # Wrong password
        if not verify_password(password, user["password_hash"]):
            failed = await self._record_failed_attempt(user["user_id"], ip)
            if failed >= _MAX_FAILED_ATTEMPTS:
                await self._lock_account(user["user_id"])
                await self._emit_security_alert("account_locked_after_failures", user, ip)
            raise AuthError("Invalid email or password.", code="invalid_credentials")

        # Success — clear lockout state
        await self._clear_failed_attempts(user["user_id"])

        # Rehash if cost has changed (§3.2 P0)
        if needs_rehash(user["password_hash"]):
            new_hash = hash_password(password)
            await self._users.update_password_hash(user["user_id"], new_hash)

        return await self._issue_token_pair(user)

    # ------------------------------------------------------------------
    # §3.1 — Logout
    # ------------------------------------------------------------------

    async def logout(self, access_jti: str, refresh_token_hash: str | None = None) -> None:
        """Revoke the current access token and optionally clear the refresh token.

        §3.1 P0: logout revokes current token; clears refresh cookie where applicable.
        """
        # Revoke access token JTI
        await revoke_jti(access_jti, ttl_seconds=15 * 60)

        # Revoke refresh token if provided
        if refresh_token_hash:
            record = await self._tokens.find_refresh_token(refresh_token_hash)
            if record:
                await revoke_token_family(record["family_id"])
                await self._tokens.delete_refresh_token(refresh_token_hash)

        logger.info("logout", extra={"jti": access_jti})

    # ------------------------------------------------------------------
    # §3.3 — Refresh token
    # ------------------------------------------------------------------

    async def refresh(self, raw_refresh_token: str) -> LoginResult:
        """Rotate a refresh token and issue a new token pair.

        Implements: success path, expiry, reuse detection, family revocation (§3.1 P0 / §3.3 P0).
        """
        import hashlib
        hashed = hashlib.sha256(raw_refresh_token.encode()).hexdigest()
        record = await self._tokens.find_refresh_token(hashed)

        if not record:
            # Possible reuse of a deleted token — if it had a family, revoke it
            raise AuthError("Refresh token not found or already used.", code="invalid_refresh_token")

        # Expiry check
        expires_at = record["expires_at"]
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at).replace(tzinfo=timezone.utc)
        if datetime.now(tz=timezone.utc) > expires_at:
            await self._tokens.delete_refresh_token(hashed)
            raise AuthError("Refresh token has expired. Please log in again.", code="refresh_token_expired")

        # Reuse detection / family revocation (§3.3 P0)
        family_id = record["family_id"]
        if await is_family_revoked(family_id):
            # Token theft detected — family already revoked; do nothing more
            raise AuthError("Security violation detected. Please log in again.", code="token_reuse_detected")

        # Delete the used token (rotation — one-time use)
        await self._tokens.delete_refresh_token(hashed)

        # Fetch user
        user = await self._users.find_by_id(record["user_id"])
        if not user:
            raise AuthError("User not found.", code="user_not_found")

        return await self._issue_token_pair(user, family_id=family_id)

    # ------------------------------------------------------------------
    # §3.1 — Email verification
    # ------------------------------------------------------------------

    async def verify_email(self, token: str) -> None:
        """Mark a user's email as verified (§3.1 P0)."""
        record = await self._tokens.find_email_verify_token(token)
        if not record:
            raise AuthError("Invalid or expired verification token.", code="invalid_token")

        if datetime.now(tz=timezone.utc) > record["expires_at"].replace(tzinfo=timezone.utc):
            raise AuthError("Verification token has expired. Request a new one.", code="token_expired")

        await self._users.mark_email_verified(record["user_id"])
        await self._tokens.delete_email_verify_token(token)
        logger.info("email_verified", extra={"user_id": record["user_id"]})

    # ------------------------------------------------------------------
    # §3.1 — Password reset
    # ------------------------------------------------------------------

    async def request_password_reset(self, email: str) -> None:
        """Send a password reset email (§3.1 P0). Always returns without error to prevent enumeration."""
        user = await self._users.find_by_email(email)
        if not user:
            return  # Silent success

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(tz=timezone.utc) + timedelta(minutes=_RESET_TOKEN_TTL_MINUTES)
        await self._tokens.store_reset_token(user_id=user["user_id"], token=token, expires_at=expires_at)
        await self._email.send_password_reset_email(email=email, token=token)
        logger.info("password_reset_requested", extra={"user_id": user["user_id"]})

    async def complete_password_reset(self, token: str, new_password: str) -> None:
        """Validate reset token and set the new password (§3.1 P0).

        Verifies: token validity, expiry, invalid token, and new password strength.
        """
        record = await self._tokens.find_reset_token(token)
        if not record:
            raise AuthError("Invalid or expired reset token.", code="invalid_token")

        expires_at = record["expires_at"]
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at).replace(tzinfo=timezone.utc)
        if datetime.now(tz=timezone.utc) > expires_at:
            await self._tokens.delete_reset_token(token)
            raise AuthError("Reset token has expired. Please request a new one.", code="token_expired")

        # Validate new password strength (§3.2 P0)
        strength = check_password_strength(new_password)
        if not strength.valid:
            raise AuthError(" ".join(strength.errors), code="weak_password")

        hashed = hash_password(new_password)
        await self._users.update_password_hash(record["user_id"], hashed)
        await self._tokens.delete_reset_token(token)

        # Revoke all existing refresh token families for this user (§3.3 — security hygiene)
        families = await self._tokens.list_token_families(record["user_id"])
        for fid in families:
            await revoke_token_family(fid)

        logger.info("password_reset_completed", extra={"user_id": record["user_id"]})

    # ------------------------------------------------------------------
    # §3.2 P1 — Password change (authenticated flow)
    # ------------------------------------------------------------------

    async def change_password(
        self, user_id: str, current_password: str, new_password: str
    ) -> None:
        """Change password for an authenticated user (§3.2 P1)."""
        user = await self._users.find_by_id(user_id)
        if not user or not verify_password(current_password, user["password_hash"]):
            raise AuthError("Current password is incorrect.", code="invalid_credentials")

        strength = check_password_strength(new_password)
        if not strength.valid:
            raise AuthError(" ".join(strength.errors), code="weak_password")

        hashed = hash_password(new_password)
        await self._users.update_password_hash(user_id, hashed)

        # Audit event (§3.2 P1)
        logger.info("password_changed", extra={"user_id": user_id, "event": "password_change"})

    # ------------------------------------------------------------------
    # §3.3 P1 — Emergency revoke-all
    # ------------------------------------------------------------------

    async def emergency_revoke_all_tokens(self, initiated_by: str) -> datetime:
        """Revoke all access tokens globally by setting an epoch (§3.3 P1)."""
        from app.core.token_config import emergency_revoke_all  # noqa: PLC0415
        epoch = await emergency_revoke_all()
        logger.warning(
            "emergency_revoke_all",
            extra={"initiated_by": initiated_by, "epoch": epoch.isoformat()},
        )
        return epoch

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _issue_token_pair(self, user: dict, *, family_id: str | None = None) -> LoginResult:
        access_token = create_access_token(
            user_id=user["user_id"],
            role=user["role"],
        )
        raw_refresh, hashed_refresh, record = create_refresh_token(family_id)
        record = record.model_copy(update={"user_id": user["user_id"]})

        await self._tokens.store_refresh_token(
            hashed=hashed_refresh,
            user_id=user["user_id"],
            family_id=record.family_id,
            expires_at=record.expires_at,
        )

        token_pair = TokenPair(access_token=access_token)
        return LoginResult(token_pair=token_pair, raw_refresh_token=raw_refresh)

    async def _record_failed_attempt(self, user_id: str | None, ip: str) -> int:
        """Increment and return the failure count for this user/IP."""
        if user_id:
            return await self._users.increment_failed_attempts(user_id)
        return 0

    async def _is_locked_out(self, user_id: str) -> bool:
        user = await self._users.find_by_id(user_id)
        if not user:
            return False
        locked_until = user.get("locked_until")
        if not locked_until:
            return False
        if isinstance(locked_until, str):
            locked_until = datetime.fromisoformat(locked_until).replace(tzinfo=timezone.utc)
        return datetime.now(tz=timezone.utc) < locked_until

    async def _lock_account(self, user_id: str) -> None:
        locked_until = datetime.now(tz=timezone.utc) + timedelta(minutes=_LOCKOUT_DURATION_MINUTES)
        await self._users.set_locked_until(user_id, locked_until)

    async def _clear_failed_attempts(self, user_id: str) -> None:
        await self._users.reset_failed_attempts(user_id)

    async def _emit_security_alert(self, event: str, user: dict, ip: str) -> None:
        """§3.1 P1 — Emit a structured security alert event."""
        logger.warning(
            "security_alert",
            extra={
                "alert_event": event,
                "user_id": user.get("user_id"),
                "email": user.get("email"),
                "ip": ip,
            },
        )
