"""
auth_extended.py — EduBoost SA V2
Handles: password-reset, email-verification, onboarding, profile update,
         privacy controls, POPIA export/deletion requests.

Place at:
    app/api_v2_routers/auth_extended.py

Register in app/api_v2.py:
    from app.api_v2_routers.auth_extended import router as auth_ext_router
    app.include_router(auth_ext_router, prefix="/api/v2/auth", tags=["auth-extended"])

Install dependencies:
    pip install passlib[bcrypt] httpx jinja2 slowapi
"""

from __future__ import annotations

import logging
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api_v2_deps.auth import AuthContext, require_auth_context
from app.core.config import settings
from app.core.security import get_current_user  # noqa: F401
from app.core.security import decrypt_pii, hash_email, hash_password
from app.models.auth_extensions import (
    OnboardingState,
    PrivacySettings,
    SecureToken,
    TokenPurpose,
)
from app.services.email_service import (
    send_email_verification,
    send_onboarding_complete_email,
    send_password_reset_email,
)

logger  = logging.getLogger(__name__)
router  = APIRouter(prefix="/auth", tags=["auth-extended"])
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Use settings.PUBLIC_FRONTEND_URL (Phase 7.1 consolidation — was os.getenv("FRONTEND_BASE_URL")).
# Set PUBLIC_FRONTEND_URL in your environment; defaults to http://localhost:3000 for dev.
FRONTEND_BASE  = settings.PUBLIC_FRONTEND_URL
RESET_TTL_MIN  = 30
VERIFY_TTL_HR  = 24

# ─── In-memory rate limiter for forgot-password (replace with Redis in prod) ──
# Stores {ip: [timestamp, ...]} — max 5 requests per 15 min per IP
from collections import defaultdict
import time as _time
_reset_attempts: dict[str, list[float]] = defaultdict(list)
_RATE_WINDOW    = 15 * 60   # 15 minutes
_RATE_MAX       = 5         # max requests per window


def _check_rate_limit(ip: str) -> None:
    now  = _time.monotonic()
    hits = _reset_attempts[ip]
    # Evict stale entries
    _reset_attempts[ip] = [t for t in hits if now - t < _RATE_WINDOW]
    if len(_reset_attempts[ip]) >= _RATE_MAX:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please wait 15 minutes before trying again.",
            headers={"Retry-After": "900"},
        )
    _reset_attempts[ip].append(now)


# ─────────────────────────────────────────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────────────────────────────────────────

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        errors: list[str] = []
        if len(v) < 8:
            errors.append("at least 8 characters")
        if not any(c.isupper() for c in v):
            errors.append("one uppercase letter")
        if not any(c.isdigit() for c in v):
            errors.append("one digit")
        if errors:
            raise ValueError("Password must contain: " + ", ".join(errors))
        return v


class VerifyEmailRequest(BaseModel):
    token: str


class ProfileUpdateRequest(BaseModel):
    """Update learner display name, grade, and home language."""
    display_name:  str
    grade:         str
    home_language: str

    @field_validator("display_name")
    @classmethod
    def non_empty_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("display_name cannot be blank")
        return v.strip()

    @field_validator("grade")
    @classmethod
    def valid_grade(cls, v: str) -> str:
        if v not in {"R","1","2","3","4","5","6","7","8","9","10","11","12"}:
            raise ValueError("grade must be R or 1–12")
        return v

    @field_validator("home_language")
    @classmethod
    def valid_language(cls, v: str) -> str:
        valid = {"en", "zu", "af", "xh"}
        if v not in valid:
            raise ValueError(f"home_language must be one of {sorted(valid)}")
        return v


class OnboardingStepUpdate(BaseModel):
    step:  str
    value: bool = True


class PrivacySettingsUpdate(BaseModel):
    analytics_enabled:   bool | None = None
    ai_improvement:      bool | None = None
    marketing_emails:    bool | None = None
    data_retention_days: int  | None = None
    show_leaderboard:    bool | None = None

    @field_validator("data_retention_days")
    @classmethod
    def valid_retention(cls, v: int | None) -> int | None:
        if v is not None and v not in (90, 365, 730, 0):
            raise ValueError("data_retention_days must be 90, 365, 730, or 0 (unlimited)")
        return v



def _current_user_id(current_user: dict | AuthContext) -> str:
    if isinstance(current_user, AuthContext):
        return current_user.user_id
    user_id = current_user.get("sub") or current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth token")
    return str(user_id)


async def _get_guardian(session: AsyncSession, guardian_id: str):
    from app.models import Guardian

    guardian = await session.get(Guardian, guardian_id)
    if guardian is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guardian not found.")
    return guardian


def _guardian_email(guardian) -> str | None:
    try:
        return decrypt_pii(guardian.email_encrypted)
    except Exception:
        logger.warning("Could not decrypt guardian email for user_id=%s", guardian.id)
        return None


def _grade_to_int(grade: str) -> int:
    return 0 if grade == "R" else int(grade)

# ─────────────────────────────────────────────────────────────────────────────
# Internal token helpers
# ─────────────────────────────────────────────────────────────────────────────

async def _invalidate_existing_tokens(
    session: AsyncSession,
    user_id: str,
    purpose: TokenPurpose,
) -> None:
    """Mark all existing unused tokens of a given purpose as consumed."""
    now    = datetime.now(timezone.utc)
    result = await session.execute(
        select(SecureToken).where(
            SecureToken.user_id == user_id,
            SecureToken.purpose == purpose,
            SecureToken.used_at.is_(None),
        )
    )
    for token in result.scalars():
        token.used_at = now


async def _create_secure_token(
    session: AsyncSession,
    user_id: str,
    purpose: TokenPurpose,
    ttl_seconds: int,
) -> str:
    """Persist a bcrypt-hashed token; return the raw value for email delivery."""
    raw    = secrets.token_urlsafe(32)
    hashed = pwd_ctx.hash(raw)
    token  = SecureToken(
        user_id    = user_id,
        purpose    = purpose,
        token_hash = hashed,
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds),
    )
    session.add(token)
    await session.flush()
    return raw


async def _consume_token(
    session: AsyncSession,
    raw_token: str,
    purpose: TokenPurpose,
) -> SecureToken:
    """
    Verify and consume a one-use token.
    Uses bcrypt verify for constant-time comparison (timing-attack mitigation).
    Raises HTTP 400 on any failure.
    """
    result = await session.execute(
        select(SecureToken).where(
            SecureToken.purpose  == purpose,
            SecureToken.used_at.is_(None),
            SecureToken.expires_at > datetime.now(timezone.utc),
        )
    )
    for token in result.scalars():
        if pwd_ctx.verify(raw_token, token.token_hash):
            token.used_at = datetime.now(timezone.utc)
            return token

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired token.",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Password Reset
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(
    request: Request,
    body:    ForgotPasswordRequest,
    session: AsyncSession = Depends(get_db),
):
    """
    Request a password-reset email.
    Always returns 202 regardless of whether the email exists (OWASP A07
    user-enumeration prevention). Rate-limited to 5 requests / 15 min / IP.
    """
    client_ip = request.client.host if request.client else "unknown"
    _check_rate_limit(client_ip)

    from app.models import Guardian
    result = await session.execute(select(Guardian).where(Guardian.email_hash == hash_email(body.email)))
    user: Guardian | None = result.scalar_one_or_none()

    if user:
        await _invalidate_existing_tokens(session, user.id, TokenPurpose.PASSWORD_RESET)
        raw = await _create_secure_token(
            session, user.id, TokenPurpose.PASSWORD_RESET,
            ttl_seconds=RESET_TTL_MIN * 60,
        )
        await session.commit()
        reset_url = f"{FRONTEND_BASE}/auth/reset-password?token={raw}"
        await send_password_reset_email(
            to_email        = body.email,
            learner_name    = getattr(user, "display_name", None) or "Learner",
            reset_url       = reset_url,
            expires_minutes = RESET_TTL_MIN,
        )

    return {"detail": "If that email exists, a reset link has been sent."}  # envelope-exempt: simple detail message, no learner data


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    body:    ResetPasswordRequest,
    session: AsyncSession = Depends(get_db),
):
    """Consume a password-reset token and update the hashed password."""
    token = await _consume_token(session, body.token, TokenPurpose.PASSWORD_RESET)

    user = await _get_guardian(session, token.user_id)

    user.password_hash = hash_password(body.new_password)
    await session.commit()
    logger.info("Password reset completed for user_id=%s", user.id)
    return {"detail": "Password updated successfully."}  # envelope-exempt: simple detail message, no learner data


# ─────────────────────────────────────────────────────────────────────────────
# Email Verification
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/send-verification", status_code=status.HTTP_202_ACCEPTED)
async def send_verification(
    current_user: AuthContext = Depends(require_auth_context),
    session: AsyncSession = Depends(get_db),
):
    """Resend (or send initial) email verification link. Requires auth."""
    if bool(current_user.raw_claims.get("email_verified")):
        return {"detail": "Email is already verified."}  # envelope-exempt: simple detail message, no learner data

    guardian = await _get_guardian(session, _current_user_id(current_user))
    email = _guardian_email(guardian)
    if not email:
        raise HTTPException(status_code=500, detail="Guardian email is unavailable.")

    await _invalidate_existing_tokens(session, _current_user_id(current_user), TokenPurpose.EMAIL_VERIFY)
    raw = await _create_secure_token(
        session, _current_user_id(current_user), TokenPurpose.EMAIL_VERIFY,
        ttl_seconds=VERIFY_TTL_HR * 3600,
    )
    await session.commit()
    verify_url = f"{FRONTEND_BASE}/auth/verify-email?token={raw}"
    await send_email_verification(
        to_email     = email,
        learner_name = guardian.display_name or "Learner",
        verify_url   = verify_url,
        expires_hours= VERIFY_TTL_HR,
    )
    return {"detail": "Verification email sent."}  # envelope-exempt: simple detail message, no learner data


@router.get("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    token:   str,
    session: AsyncSession = Depends(get_db),
):
    """Consume an email-verification token (linked from email)."""
    secure = await _consume_token(session, token, TokenPurpose.EMAIL_VERIFY)

    user = await _get_guardian(session, secure.user_id)

    user.email_verified = True

    # Mirror into onboarding state (create row if missing)
    result = await session.execute(
        select(OnboardingState).where(OnboardingState.user_id == user.id)
    )
    state: OnboardingState | None = result.scalar_one_or_none()
    if state:
        state.email_verified = True
        state.updated_at     = datetime.now(timezone.utc)
    else:
        state = OnboardingState(user_id=user.id, email_verified=True)
        session.add(state)

    await session.commit()
    return {"detail": "Email verified successfully."}  # envelope-exempt: simple detail message, no learner data


# ─────────────────────────────────────────────────────────────────────────────
# Onboarding
# ─────────────────────────────────────────────────────────────────────────────

VALID_ONBOARDING_STEPS = {
    "email_verified",
    "profile_complete",
    "guardian_consent",
    "diagnostic_done",
    "plan_accepted",
}


@router.get("/onboarding", status_code=status.HTTP_200_OK)
async def get_onboarding(
    current_user: AuthContext = Depends(require_auth_context),
    session:      AsyncSession = Depends(get_db),
):
    """Return current onboarding state. Auto-creates row on first request."""
    result = await session.execute(
        select(OnboardingState).where(OnboardingState.user_id == _current_user_id(current_user))
    )
    state: OnboardingState | None = result.scalar_one_or_none()
    if not state:
        state = OnboardingState(
            user_id        = _current_user_id(current_user),
            email_verified = bool(current_user.raw_claims.get("email_verified")) or False,
        )
        session.add(state)
        await session.commit()
        await session.refresh(state)
    return state.to_dict()


@router.patch("/onboarding/step", status_code=status.HTTP_200_OK)
async def update_onboarding_step(
    body:         OnboardingStepUpdate,
    current_user: AuthContext = Depends(require_auth_context),
    session:      AsyncSession = Depends(get_db),
):
    """Mark an individual onboarding step complete."""
    if body.step not in VALID_ONBOARDING_STEPS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unknown step '{body.step}'. Valid: {sorted(VALID_ONBOARDING_STEPS)}",
        )

    result = await session.execute(
        select(OnboardingState).where(OnboardingState.user_id == _current_user_id(current_user))
    )
    state: OnboardingState | None = result.scalar_one_or_none()
    if not state:
        state = OnboardingState(user_id=_current_user_id(current_user))
        session.add(state)

    setattr(state, body.step, body.value)
    state.updated_at = datetime.now(timezone.utc)

    # Seal completion timestamp and send congratulations email
    if state.is_complete and not state.completed_at:
        state.completed_at = datetime.now(timezone.utc)
        guardian = await _get_guardian(session, _current_user_id(current_user))
        email = _guardian_email(guardian)
        if email:
            await send_onboarding_complete_email(
                to_email      = email,
                learner_name  = guardian.display_name or "Learner",
                dashboard_url = f"{FRONTEND_BASE}/dashboard",
            )

    await session.commit()
    return state.to_dict()


@router.patch("/onboarding/profile", status_code=status.HTTP_200_OK)
async def update_learner_profile(
    body:         ProfileUpdateRequest,
    current_user: AuthContext = Depends(require_auth_context),
    session:      AsyncSession = Depends(get_db),
):
    """
    Save learner profile data (display name, grade, home language) and
    automatically mark the profile_complete onboarding step as done.
    """
    from app.models import Language, LearnerProfile

    user = await _get_guardian(session, _current_user_id(current_user))
    user.display_name = body.display_name

    result = await session.execute(
        select(LearnerProfile)
        .where(LearnerProfile.guardian_id == user.id, LearnerProfile.is_deleted == False)
        .order_by(LearnerProfile.created_at.asc())
        .limit(1)
    )
    learner = result.scalar_one_or_none()
    if learner:
        learner.display_name = body.display_name
        learner.grade = _grade_to_int(body.grade)
        learner.language = Language(body.home_language)

    # Mark profile step complete
    result = await session.execute(
        select(OnboardingState).where(OnboardingState.user_id == user.id)
    )
    state: OnboardingState | None = result.scalar_one_or_none()
    if not state:
        state = OnboardingState(user_id=user.id)
        session.add(state)

    state.profile_complete = True
    state.updated_at       = datetime.now(timezone.utc)

    await session.commit()
    return {  # envelope-exempt: onboarding helper endpoint, UI reads state directly
        "detail":       "Profile saved.",
        "onboarding":   state.to_dict(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Privacy Controls (POPIA)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/privacy", status_code=status.HTTP_200_OK)
async def get_privacy_settings(
    current_user: AuthContext = Depends(require_auth_context),
    session:      AsyncSession = Depends(get_db),
):
    """Return current privacy settings. Auto-creates defaults on first request."""
    result = await session.execute(
        select(PrivacySettings).where(PrivacySettings.user_id == _current_user_id(current_user))
    )
    ps: PrivacySettings | None = result.scalar_one_or_none()
    if not ps:
        ps = PrivacySettings(user_id=_current_user_id(current_user))
        session.add(ps)
        await session.commit()
        await session.refresh(ps)
    return ps.to_dict()


@router.patch("/privacy", status_code=status.HTTP_200_OK)
async def update_privacy_settings(
    body:         PrivacySettingsUpdate,
    current_user: AuthContext = Depends(require_auth_context),
    session:      AsyncSession = Depends(get_db),
):
    """Partial-update privacy settings. Only supplied fields are changed."""
    result = await session.execute(
        select(PrivacySettings).where(PrivacySettings.user_id == _current_user_id(current_user))
    )
    ps: PrivacySettings | None = result.scalar_one_or_none()
    if not ps:
        ps = PrivacySettings(user_id=_current_user_id(current_user))
        session.add(ps)

    for field, val in body.model_dump(exclude_none=True).items():
        setattr(ps, field, val)
    ps.updated_at = datetime.now(timezone.utc)

    await session.commit()
    logger.info("Privacy settings updated for user_id=%s", _current_user_id(current_user))
    return ps.to_dict()


@router.post("/privacy/request-export", status_code=status.HTTP_202_ACCEPTED)
async def request_data_export(
    current_user: AuthContext = Depends(require_auth_context),
    session:      AsyncSession = Depends(get_db),
):
    """POPIA section 23 right-of-access — queue a data export job."""
    result = await session.execute(
        select(PrivacySettings).where(PrivacySettings.user_id == _current_user_id(current_user))
    )
    ps: PrivacySettings | None = result.scalar_one_or_none()
    if not ps:
        ps = PrivacySettings(user_id=_current_user_id(current_user))
        session.add(ps)

    if ps.export_requested_at:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A data export has already been requested.",
        )

    ps.export_requested_at = datetime.now(timezone.utc)
    await session.commit()
    # TODO: enqueue Celery task → export_user_data.delay(_current_user_id(current_user))
    logger.info("Data export requested for user_id=%s", _current_user_id(current_user))
    return {"detail": "Data export requested. You will receive an email within 30 days."}  # envelope-exempt: POPIA 202 acknowledgement, no data payload


@router.post("/privacy/request-deletion", status_code=status.HTTP_202_ACCEPTED)
async def request_account_deletion(
    current_user: AuthContext = Depends(require_auth_context),
    session:      AsyncSession = Depends(get_db),
):
    """POPIA right-to-erasure — soft-flag the account for scheduled deletion."""
    result = await session.execute(
        select(PrivacySettings).where(PrivacySettings.user_id == _current_user_id(current_user))
    )
    ps: PrivacySettings | None = result.scalar_one_or_none()
    if not ps:
        ps = PrivacySettings(user_id=_current_user_id(current_user))
        session.add(ps)

    if ps.deletion_requested_at:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A deletion request is already pending.",
        )

    ps.deletion_requested_at = datetime.now(timezone.utc)
    await session.commit()
    # TODO: enqueue Celery task → schedule_account_deletion.delay(_current_user_id(current_user))
    logger.info("Account deletion requested for user_id=%s", _current_user_id(current_user))
    return {"detail": "Deletion request received. Your account will be erased within 30 days."}  # envelope-exempt: POPIA 202 acknowledgement, no data payload
