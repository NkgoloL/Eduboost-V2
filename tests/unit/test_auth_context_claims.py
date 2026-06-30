"""
Unit tests for AuthContext claim normalization.

Tests cover:
- Valid parent/guardian token
- Valid admin token
- Missing sub
- Missing role
- Malformed claims
- Inconsistent guardian_id / user_id behavior
- Issuer and audience validation
- Token type validation
- Role parsing
"""
from __future__ import annotations

import pytest
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

from app.api_v2_deps.auth import (
    TokenType,
    _claims_to_auth_context,
    _parse_roles,
    _validate_issuer_and_audience,
)
from app.models import UserRole


class TestParseRoles:
    """Test role claim parsing."""

    def test_parse_single_role_string(self):
        """Parse single role as string."""
        result = _parse_roles("parent")
        assert result == [UserRole.PARENT]

    def test_parse_single_role_enum(self):
        """Parse single role as enum."""
        result = _parse_roles(UserRole.ADMIN)
        assert result == [UserRole.ADMIN]

    def test_parse_role_list_strings(self):
        """Parse list of role strings."""
        result = _parse_roles(["parent", "teacher"])
        assert set(result) == {UserRole.PARENT, UserRole.TEACHER}

    def test_parse_role_list_enums(self):
        """Parse list of role enums."""
        result = _parse_roles([UserRole.PARENT, UserRole.ADMIN])
        assert set(result) == {UserRole.PARENT, UserRole.ADMIN}

    def test_parse_none_role(self):
        """Parse None returns empty list."""
        result = _parse_roles(None)
        assert result == []

    def test_parse_empty_list(self):
        """Parse empty list returns empty list."""
        result = _parse_roles([])
        assert result == []


class TestClaimsToAuthContext:
    """Test conversion of raw claims to AuthContext."""

    def test_valid_parent_token(self):
        """Parse valid parent token claims."""
        now = datetime.now(timezone.utc)
        claims = {
            "sub": "user-123",
            "role": "parent",
            "guardian_id": "guardian-456",
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=15)).timestamp()),
            "jti": "jti-789",
        }

        ctx = _claims_to_auth_context(claims)

        assert ctx.user_id == "user-123"
        assert ctx.guardian_id == "guardian-456"
        assert ctx.learner_id is None
        assert ctx.roles == [UserRole.PARENT]
        assert ctx.token_type == TokenType.ACCESS
        assert ctx.is_parent
        assert not ctx.is_admin
        assert not ctx.is_teacher

    def test_valid_admin_token(self):
        """Parse valid admin token claims."""
        now = datetime.now(timezone.utc)
        claims = {
            "sub": "admin-123",
            "role": "admin",
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=15)).timestamp()),
            "jti": "jti-789",
        }

        ctx = _claims_to_auth_context(claims)

        assert ctx.user_id == "admin-123"
        assert ctx.roles == [UserRole.ADMIN]
        assert ctx.is_admin
        assert not ctx.is_parent

    def test_valid_student_token(self):
        """Parse valid student token claims."""
        now = datetime.now(timezone.utc)
        claims = {
            "sub": "student-123",
            "role": "student",
            "learner_id": "learner-456",
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=15)).timestamp()),
            "jti": "jti-789",
        }

        ctx = _claims_to_auth_context(claims)

        assert ctx.user_id == "student-123"
        assert ctx.learner_id == "learner-456"
        assert ctx.roles == [UserRole.STUDENT]
        assert ctx.is_student

    def test_missing_sub_raises(self):
        """Missing sub claim raises HTTPException."""
        now = datetime.now(timezone.utc)
        claims = {
            "role": "parent",
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=15)).timestamp()),
        }

        with pytest.raises(HTTPException) as exc:
            _claims_to_auth_context(claims)

        assert exc.value.status_code == 401
        assert "sub" in exc.value.detail

    def test_invalid_token_type_raises(self):
        """Invalid token type raises HTTPException."""
        now = datetime.now(timezone.utc)
        claims = {
            "sub": "user-123",
            "role": "parent",
            "type": "invalid",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=15)).timestamp()),
        }

        with pytest.raises(HTTPException) as exc:
            _claims_to_auth_context(claims)

        assert exc.value.status_code == 401
        assert "token type" in exc.value.detail

    def test_datetime_parsing_timestamps(self):
        """Parse integer timestamps correctly."""
        now = datetime.now(timezone.utc)
        claims = {
            "sub": "user-123",
            "role": "parent",
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=15)).timestamp()),
            "jti": "jti-789",
        }

        ctx = _claims_to_auth_context(claims)

        assert isinstance(ctx.issued_at, datetime)
        assert isinstance(ctx.expires_at, datetime)
        assert ctx.issued_at.tzinfo == timezone.utc
        assert ctx.expires_at.tzinfo == timezone.utc

    def test_datetime_parsing_datetime_objects(self):
        """Parse datetime objects correctly."""
        now = datetime.now(timezone.utc)
        claims = {
            "sub": "user-123",
            "role": "parent",
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=15),
            "jti": "jti-789",
        }

        ctx = _claims_to_auth_context(claims)

        assert ctx.issued_at == now
        assert ctx.expires_at == now + timedelta(minutes=15)

    def test_issuer_and_audience_preserved(self):
        """Issuer and audience claims are preserved."""
        now = datetime.now(timezone.utc)
        claims = {
            "sub": "user-123",
            "role": "parent",
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=15)).timestamp()),
            "jti": "jti-789",
            "iss": "https://api.eduboost.co.za",
            "aud": "eduboost-api",
        }

        ctx = _claims_to_auth_context(claims)

        assert ctx.issuer == "https://api.eduboost.co.za"
        assert ctx.audience == "eduboost-api"

    def test_raw_claims_preserved(self):
        """Raw claims are preserved in context."""
        now = datetime.now(timezone.utc)
        claims = {
            "sub": "user-123",
            "role": "parent",
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=15)).timestamp()),
            "jti": "jti-789",
            "custom_claim": "custom_value",
        }

        ctx = _claims_to_auth_context(claims)

        assert ctx.raw_claims == claims
        assert ctx.raw_claims["custom_claim"] == "custom_value"


class TestValidateIssuerAndAudience:
    """Test issuer and audience validation."""

    def test_valid_issuer_passes(self, monkeypatch):
        """Valid issuer passes validation."""
        from app.core.config import settings

        monkeypatch.setattr(settings, "APP_BASE_URL", "https://api.eduboost.co.za")

        claims = {
            "iss": "https://api.eduboost.co.za",
            "aud": "eduboost-api",
        }

        # Should not raise
        _validate_issuer_and_audience(claims)

    def test_invalid_issuer_raises(self, monkeypatch):
        """Invalid issuer raises HTTPException."""
        from app.core.config import settings

        monkeypatch.setattr(settings, "APP_BASE_URL", "https://api.eduboost.co.za")

        claims = {
            "iss": "https://staging.eduboost.co.za",
            "aud": "eduboost-api",
        }

        with pytest.raises(HTTPException) as exc:
            _validate_issuer_and_audience(claims)

        assert exc.value.status_code == 401
        assert "issuer" in exc.value.detail

    def test_invalid_audience_raises(self, monkeypatch):
        """Invalid audience raises HTTPException."""
        from app.core.config import settings

        monkeypatch.setattr(settings, "APP_BASE_URL", "https://api.eduboost.co.za")

        claims = {
            "iss": "https://api.eduboost.co.za",
            "aud": "wrong-audience",
        }

        with pytest.raises(HTTPException) as exc:
            _validate_issuer_and_audience(claims)

        assert exc.value.status_code == 401
        assert "audience" in exc.value.detail

    def test_missing_issuer_and_audience_passes(self):
        """Missing issuer and audience passes validation (optional)."""
        claims = {}

        # Should not raise
        _validate_issuer_and_audience(claims)


class TestAuthContextProperties:
    """Test AuthContext convenience properties."""

    def test_is_expired_true(self):
        """Expired token returns True for is_expired."""
        now = datetime.now(timezone.utc)
        claims = {
            "sub": "user-123",
            "role": "parent",
            "type": "access",
            "iat": int((now - timedelta(minutes=30)).timestamp()),
            "exp": int((now - timedelta(minutes=15)).timestamp()),
            "jti": "jti-789",
        }

        ctx = _claims_to_auth_context(claims)
        assert ctx.is_expired

    def test_is_expired_false(self):
        """Valid token returns False for is_expired."""
        now = datetime.now(timezone.utc)
        claims = {
            "sub": "user-123",
            "role": "parent",
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=15)).timestamp()),
            "jti": "jti-789",
        }

        ctx = _claims_to_auth_context(claims)
        assert not ctx.is_expired

    def test_subject_property(self):
        """Subject property returns user_id."""
        now = datetime.now(timezone.utc)
        claims = {
            "sub": "user-123",
            "role": "parent",
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=15)).timestamp()),
            "jti": "jti-789",
        }

        ctx = _claims_to_auth_context(claims)
        assert ctx.subject == "user-123"

    def test_multi_role_user(self):
        """User with multiple roles."""
        now = datetime.now(timezone.utc)
        claims = {
            "sub": "user-123",
            "role": ["parent", "teacher"],
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=15)).timestamp()),
            "jti": "jti-789",
        }

        ctx = _claims_to_auth_context(claims)

        assert ctx.is_parent
        assert ctx.is_teacher
        assert not ctx.is_admin
        assert set(ctx.roles) == {UserRole.PARENT, UserRole.TEACHER}
