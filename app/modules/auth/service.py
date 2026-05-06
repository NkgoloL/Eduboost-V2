"""
EduBoost SA — Auth Module Service
Guardian registration, login, token refresh, email verification.
"""
from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import AuditAction, write_audit_event
from app.core.exceptions import AuthenticationError, DuplicateError, NotFoundError
from app.core.security import (
    create_access_token, create_refresh_token,
    decrypt_pii, encrypt_pii, generate_secure_token,
    hash_email, hash_password, verify_password,
)
from app.models import Guardian
from app.repositories import GuardianRepository

_guardian_repo = GuardianRepository()


class AuthService:
    """Authentication and guardian lifecycle service.

    Responsible for guardian registration, login, email verification, and
    profile retrieval while preserving encrypted personal data and audit trail
    behavior.
    """

    async def register_guardian(
        self,
        db: AsyncSession,
        *,
        email: str,
        password: str,
        full_name: str,
        phone: str | None = None,
    ) -> Guardian:
        """Register a new guardian account.

        Args:
            db: Async database session for repository operations.
            email: Guardian email address.
            password: Plaintext password to hash and store securely.
            full_name: Guardian full name to encrypt for storage.
            phone: Optional guardian phone number.

        Returns:
            Created Guardian model instance.

        Raises:
            DuplicateError: When an account already exists for the email.
        """
        email_hash = hash_email(email)
        existing = await _guardian_repo.get_by_email_hash(email_hash, db)
        if existing:
            raise DuplicateError("An account with this email already exists")

        guardian = await _guardian_repo.create(
            db,
            email_hash=email_hash,
            email_encrypted=encrypt_pii(email.lower().strip()),
            password_hash=hash_password(password),
            full_name_encrypted=encrypt_pii(full_name),
            phone_encrypted=encrypt_pii(phone) if phone else None,
            is_active=True,
            is_verified=False,
            verification_token=generate_secure_token(48),
        )

        await write_audit_event(
            db,
            action=AuditAction.USER_REGISTERED,
            actor_id=guardian.id,
            resource_type="guardian",
            resource_id=str(guardian.id),
        )
        return guardian

    async def authenticate(
        self,
        db: AsyncSession,
        *,
        email: str,
        password: str,
        ip_address: str | None = None,
    ) -> tuple[str, str]:
        """Authenticate and return (access_token, refresh_token)."""
        email_hash = hash_email(email)
        guardian = await _guardian_repo.get_by_email_hash(email_hash, db)

        if guardian is None or not verify_password(password, guardian.password_hash):
            await write_audit_event(
                db,
                action=AuditAction.USER_LOGIN_FAILED,
                actor_id=None,
                metadata={"email_hash": email_hash[:8] + "..."},
                ip_address=ip_address,
            )
            raise AuthenticationError("Invalid email or password")

        if not guardian.is_active:
            raise AuthenticationError("Account is deactivated")

        await _guardian_repo.update(guardian, db, last_login_at=datetime.now(UTC))
        await write_audit_event(
            db,
            action=AuditAction.USER_LOGIN,
            actor_id=guardian.id,
            ip_address=ip_address,
        )

        access_token = create_access_token(
            guardian.id,
            extra={"role": "guardian", "verified": guardian.is_verified},
        )
        refresh_token = create_refresh_token(guardian.id)
        return access_token, refresh_token

    async def verify_email(self, token: str, db: AsyncSession) -> Guardian:
        """Verify a guardian's email address using a token.

        Args:
            token: Email verification token issued during registration.
            db: Async database session.

        Returns:
            Guardian model instance with ``is_verified`` set to ``True``.

        Raises:
            NotFoundError: When the token is invalid or expired.
        """
        guardian = await _guardian_repo.get_by_verification_token(token, db)
        if guardian is None:
            raise NotFoundError("Invalid or expired verification token")
        return await _guardian_repo.update(
            guardian, db,
            is_verified=True,
            verification_token=None,
        )

    async def get_guardian_profile(self, guardian_id: UUID, db: AsyncSession) -> dict:
        """Retrieve a guardian profile for the parent portal.

        Args:
            guardian_id: UUID of the guardian.
            db: Async database session.

        Returns:
            Dictionary containing decrypted guardian profile fields.
        """
        guardian = await _guardian_repo.get_or_404(guardian_id, db)
        return {
            "id": str(guardian.id),
            "email": decrypt_pii(guardian.email_encrypted),
            "full_name": decrypt_pii(guardian.full_name_encrypted),
            "is_verified": guardian.is_verified,
            "created_at": guardian.created_at.isoformat(),
        }
