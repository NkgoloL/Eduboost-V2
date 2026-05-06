"""Guardian authentication and account lifecycle service.

Handles guardian registration, login, email verification, and profile
retrieval for the EduBoost parent portal.  All personally identifiable
information (PII) is encrypted at rest via :func:`~app.core.security.encrypt_pii`
and hashed for lookup via :func:`~app.core.security.hash_email`.

Every authentication event is recorded in the audit trail via
:func:`~app.core.audit.write_audit_event` for POPIA compliance.

Example:
    Register and authenticate a guardian::

        from app.modules.auth.service import AuthService

        auth = AuthService()
        guardian = await auth.register_guardian(
            db, email="parent@example.com", password="s3cure!",
            full_name="Thabo Mokoena",
        )
        access, refresh = await auth.authenticate(
            db, email="parent@example.com", password="s3cure!",
        )
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
    profile retrieval while preserving encrypted personal data and audit
    trail behaviour.

    All public methods are async and require a
    :class:`~sqlalchemy.ext.asyncio.AsyncSession` for transactional
    database access.

    Example:
        ::

            auth = AuthService()
            guardian = await auth.register_guardian(
                db, email="parent@example.com", password="s3cure!",
                full_name="Thabo Mokoena",
            )
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

        Creates a :class:`~app.models.Guardian` with encrypted PII,
        a hashed password, and a verification token.  An audit event
        of type :attr:`~app.core.audit.AuditAction.USER_REGISTERED`
        is recorded.

        Args:
            db: Async database session for repository operations.
            email: Guardian email address (stored encrypted).
            password: Plaintext password to hash via
                :func:`~app.core.security.hash_password`.
            full_name: Guardian full name to encrypt for storage.
            phone: Optional guardian phone number.

        Returns:
            Guardian: The newly created :class:`~app.models.Guardian`
            model instance with ``is_verified=False``.

        Raises:
            DuplicateError: When an account already exists for the
                given email address.

        Example:
            ::

                guardian = await auth.register_guardian(
                    db,
                    email="sipho@example.com",
                    password="secure-password",
                    full_name="Sipho Ndlovu",
                    phone="+27821234567",
                )
                assert guardian.is_verified is False
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
        """Authenticate a guardian and return JWT token pair.

        Verifies the email/password combination, records an audit event,
        and issues an access token and a refresh token.

        Args:
            db: Async database session.
            email: Guardian email address.
            password: Plaintext password to verify against the stored hash.
            ip_address: Optional client IP for audit logging.

        Returns:
            Tuple[str, str]: ``(access_token, refresh_token)`` JWT pair.

        Raises:
            AuthenticationError: When the email/password combination is
                invalid or the account is deactivated.

        Example:
            ::

                access, refresh = await auth.authenticate(
                    db, email="parent@example.com", password="s3cure!",
                )
        """
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
        """Verify a guardian's email address using a one-time token.

        Marks the :class:`~app.models.Guardian` as verified and clears
        the verification token to prevent reuse.

        Args:
            token: Email verification token issued during registration.
            db: Async database session.

        Returns:
            Guardian: The updated :class:`~app.models.Guardian` with
            ``is_verified=True``.

        Raises:
            NotFoundError: When the token is invalid or has expired.

        Example:
            ::

                guardian = await auth.verify_email("abc123token", db)
                assert guardian.is_verified is True
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
        """Retrieve a decrypted guardian profile for the parent portal.

        Decrypts PII fields (email, full name) using
        :func:`~app.core.security.decrypt_pii` for display in the
        parent-facing dashboard.

        Args:
            guardian_id: UUID of the guardian to retrieve.
            db: Async database session.

        Returns:
            dict: Dictionary with keys ``id``, ``email``, ``full_name``,
            ``is_verified``, and ``created_at``.

        Example:
            ::

                profile = await auth.get_guardian_profile(guardian.id, db)
                assert "email" in profile
        """
        guardian = await _guardian_repo.get_or_404(guardian_id, db)
        return {
            "id": str(guardian.id),
            "email": decrypt_pii(guardian.email_encrypted),
            "full_name": decrypt_pii(guardian.full_name_encrypted),
            "is_verified": guardian.is_verified,
            "created_at": guardian.created_at.isoformat(),
        }
