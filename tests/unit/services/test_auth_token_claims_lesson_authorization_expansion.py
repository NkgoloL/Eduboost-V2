"""Batch 205: Unit tests for auth_token_claims and lesson_authorization services."""
import pytest
from dataclasses import FrozenInstanceError

from app.services.auth_token_claims import (
    AUTHZ_CLAIM_KEYS,
    AuthTokenClaims,
    build_access_token_claims,
    contains_raw_email_encrypted_assignment,
    merge_refresh_claims,
)
from app.services.lesson_authorization import (
    iter_sync_lesson_ids,
    _import_dotted,
    _first_import,
    _owner_from_result,
)


# ─────────────────────────────────────────────
# AUTHZ_CLAIM_KEYS constant
# ─────────────────────────────────────────────


class TestAuthzClaimKeys:
    def test_is_tuple(self):
        assert isinstance(AUTHZ_CLAIM_KEYS, tuple)

    def test_contains_expected_keys(self):
        assert "sub" in AUTHZ_CLAIM_KEYS
        assert "role" in AUTHZ_CLAIM_KEYS
        assert "user_id" in AUTHZ_CLAIM_KEYS

    def test_does_not_contain_email(self):
        assert "email" not in AUTHZ_CLAIM_KEYS
        assert "email_encrypted" not in AUTHZ_CLAIM_KEYS


# ─────────────────────────────────────────────
# AuthTokenClaims
# ─────────────────────────────────────────────


class TestAuthTokenClaims:
    def test_minimal_construction(self):
        claims = AuthTokenClaims(sub="user-123", user_id="user-123")
        assert claims.sub == "user-123"
        assert claims.role is None
        assert claims.roles == ()
        assert claims.guardian_learner_ids == ()

    def test_to_payload_includes_sub_and_user_id(self):
        claims = AuthTokenClaims(sub="u1", user_id="u1")
        payload = claims.to_payload()
        assert payload["sub"] == "u1"
        assert payload["user_id"] == "u1"

    def test_to_payload_includes_role_when_set(self):
        claims = AuthTokenClaims(sub="u1", user_id="u1", role="guardian")
        payload = claims.to_payload()
        assert payload["role"] == "guardian"

    def test_to_payload_excludes_none_role(self):
        claims = AuthTokenClaims(sub="u1", user_id="u1")
        payload = claims.to_payload()
        assert "role" not in payload

    def test_to_payload_includes_roles_when_set(self):
        claims = AuthTokenClaims(sub="u1", user_id="u1", roles=("guardian", "admin"))
        payload = claims.to_payload()
        assert payload["roles"] == ["guardian", "admin"]

    def test_to_payload_excludes_empty_roles(self):
        claims = AuthTokenClaims(sub="u1", user_id="u1", roles=())
        payload = claims.to_payload()
        assert "roles" not in payload

    def test_to_payload_includes_guardian_learner_ids(self):
        claims = AuthTokenClaims(sub="u1", user_id="u1", guardian_learner_ids=("l1", "l2"))
        payload = claims.to_payload()
        assert payload["guardian_learner_ids"] == ["l1", "l2"]

    def test_to_payload_includes_learner_id(self):
        claims = AuthTokenClaims(sub="u1", user_id="u1", learner_id="l-99")
        payload = claims.to_payload()
        assert payload["learner_id"] == "l-99"

    def test_to_payload_includes_email_verified(self):
        claims = AuthTokenClaims(sub="u1", user_id="u1", email_verified=True)
        payload = claims.to_payload()
        assert payload["email_verified"] is True

    def test_to_payload_includes_extra_keys(self):
        claims = AuthTokenClaims(sub="u1", user_id="u1", extra={"custom_key": "value"})
        payload = claims.to_payload()
        assert payload["custom_key"] == "value"

    def test_extra_does_not_override_core_keys(self):
        # extra "sub" should not override the canonical sub
        claims = AuthTokenClaims(sub="u1", user_id="u1", extra={"sub": "evil", "user_id": "evil"})
        payload = claims.to_payload()
        assert payload["sub"] == "u1"
        assert payload["user_id"] == "u1"

    def test_frozen_immutable(self):
        claims = AuthTokenClaims(sub="u1", user_id="u1")
        with pytest.raises(Exception):
            claims.sub = "mutated"


# ─────────────────────────────────────────────
# build_access_token_claims
# ─────────────────────────────────────────────


class TestBuildAccessTokenClaims:
    def _user(self, **kwargs):
        from types import SimpleNamespace
        defaults = dict(
            id="user-123", role=None, roles=None,
            guardian_learner_ids=None, learner_id=None,
            parent_id=None, email_verified=None,
        )
        defaults.update(kwargs)
        return SimpleNamespace(**defaults)

    def test_builds_claims_from_user_object(self):
        user = self._user(id="u-1", role="guardian")
        claims = build_access_token_claims(user)
        assert isinstance(claims, dict)
        assert claims["user_id"] == "u-1"
        assert claims["sub"] == "u-1"
        assert claims["role"] == "guardian"

    def test_builds_claims_with_role(self):
        user = self._user(id="u-2", role="learner")
        claims = build_access_token_claims(user)
        assert claims["role"] == "learner"


# ─────────────────────────────────────────────
# contains_raw_email_encrypted_assignment
# ─────────────────────────────────────────────


class TestContainsRawEmailEncryptedAssignment:
    def test_detects_direct_assignment(self):
        text = "obj.email_encrypted=email"
        assert contains_raw_email_encrypted_assignment(text) is True

    def test_detects_spaced_assignment(self):
        text = "obj.email_encrypted = user.email"
        assert contains_raw_email_encrypted_assignment(text) is True

    def test_clean_code_returns_false(self):
        text = "email_encrypted = encrypt(email)"
        assert contains_raw_email_encrypted_assignment(text) is False

    def test_empty_string_returns_false(self):
        assert contains_raw_email_encrypted_assignment("") is False


# ─────────────────────────────────────────────
# lesson_authorization helpers
# ─────────────────────────────────────────────


class TestImportDotted:
    def test_imports_real_symbol(self):
        result = _import_dotted("app.services.auth_token_claims.AuthTokenClaims")
        assert result is AuthTokenClaims

    def test_returns_none_for_nonexistent(self):
        result = _import_dotted("app.services.nonexistent_xyz.FakeClass")
        assert result is None

    def test_returns_none_for_bad_module(self):
        result = _import_dotted("completely.fake.module.Symbol")
        assert result is None


class TestFirstImport:
    def test_returns_first_importable(self):
        candidates = (
            "nonexistent.module.Symbol",
            "app.services.auth_token_claims.AuthTokenClaims",
        )
        result = _first_import(candidates)
        assert result is AuthTokenClaims

    def test_returns_none_when_all_fail(self):
        candidates = ("fake.module.A", "fake.module.B")
        result = _first_import(candidates)
        assert result is None


class TestOwnerFromResult:
    def test_none_returns_none(self):
        assert _owner_from_result(None) is None

    def test_dict_with_learner_id(self):
        result = {"learner_id": "l-1", "other": "value"}
        assert _owner_from_result(result) == "l-1"

    def test_dict_with_owner_learner_id(self):
        result = {"owner_learner_id": "l-2"}
        assert _owner_from_result(result) == "l-2"

    def test_object_with_learner_id(self):
        from types import SimpleNamespace
        obj = SimpleNamespace(learner_id="l-3")
        assert _owner_from_result(obj) == "l-3"

    def test_tuple_returns_second_element(self):
        result = ("lesson-data", "l-4")
        assert _owner_from_result(result) == "l-4"

    def test_nested_dict_with_lesson_key(self):
        result = {"lesson": {"learner_id": "l-5"}}
        assert _owner_from_result(result) == "l-5"


class TestIterSyncLessonIds:
    def test_extracts_from_dict(self):
        payload = {"lesson_id": "les-1"}
        ids = iter_sync_lesson_ids(payload)
        assert "les-1" in ids

    def test_extracts_from_list(self):
        payload = [{"lesson_id": "les-A"}, {"lesson_id": "les-B"}]
        ids = iter_sync_lesson_ids(payload)
        assert "les-A" in ids
        assert "les-B" in ids

    def test_camel_case_lesson_id(self):
        payload = {"lessonId": "les-X"}
        ids = iter_sync_lesson_ids(payload)
        assert "les-X" in ids

    def test_none_returns_empty(self):
        assert iter_sync_lesson_ids(None) == []

    def test_string_returns_empty(self):
        assert iter_sync_lesson_ids("not_a_dict") == []

    def test_circular_reference_and_nested_objects(self):
        from types import SimpleNamespace
        child = SimpleNamespace(lesson_id="les-nested")
        parent = SimpleNamespace(events=[child], items=[])
        # Add circular reference
        child.parent = parent

        ids = iter_sync_lesson_ids(parent)
        assert "les-nested" in ids


class TestLessonAuthorizationExecution:
    @pytest.mark.asyncio
    async def test_lesson_owner_learner_id_from_db_model(self):
        from unittest.mock import AsyncMock, MagicMock, patch
        from app.services.lesson_authorization import lesson_owner_learner_id

        mock_db = AsyncMock()
        mock_repo = MagicMock()
        mock_repo.get_by_id_with_learner = AsyncMock(return_value={"learner_id": "learner-db-1"})
        mock_repo_cls = MagicMock(return_value=mock_repo)

        with patch("app.services.lesson_authorization._first_import", return_value=mock_repo_cls):
            owner = await lesson_owner_learner_id(mock_db, "lesson-1")
            assert owner == "learner-db-1"

    @pytest.mark.asyncio
    async def test_lesson_owner_not_found_raises_404(self):
        from unittest.mock import AsyncMock, patch
        from fastapi import HTTPException
        from app.services.lesson_authorization import lesson_owner_learner_id

        mock_db = AsyncMock()
        with patch("app.services.lesson_authorization._first_import", return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await lesson_owner_learner_id(mock_db, "lesson-missing")
            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_require_lesson_read_and_write_access(self):
        from unittest.mock import AsyncMock, MagicMock, patch
        from app.services.lesson_authorization import (
            require_lesson_read_access_for_current_user,
            require_lesson_write_access_for_current_user,
            _current_user_claims,
        )
        from app.api_v2_deps.auth import AuthContext

        mock_db = AsyncMock()
        mock_auth_fn = AsyncMock(return_value=True)

        with patch("app.services.lesson_authorization.lesson_owner_learner_id", AsyncMock(return_value="learner-1")):
            with patch("app.services.lesson_authorization._first_import", return_value=mock_auth_fn):
                # Using AuthContext
                from app.api_v2_deps.auth import TokenType
                ctx = AuthContext(
                    user_id="guard-1",
                    guardian_id="guard-1",
                    token_type=TokenType.ACCESS,
                    jti="jti-1",
                    raw_claims={"sub": "guard-1", "role": "guardian"},
                )
                assert _current_user_claims(ctx) == {"sub": "guard-1", "role": "guardian"}

                read_ok = await require_lesson_read_access_for_current_user(mock_db, ctx, "les-1")
                assert read_ok is True

                write_ok = await require_lesson_write_access_for_current_user(mock_db, ctx, "les-1")
                assert write_ok is True


class TestMergeRefreshClaims:
    def test_merge_refresh_claims_basic(self):
        token_claims = {"sub": "user-1", "role": "guardian"}
        user_claims = {"roles": ["guardian", "admin"], "guardian_learner_ids": ["l1"]}
        merged = merge_refresh_claims(token_claims, user_claims)
        assert merged["sub"] == "user-1"
        assert merged["role"] == "guardian"
        assert merged["roles"] == ["guardian", "admin"]
        assert merged["guardian_learner_ids"] == ["l1"]
