from __future__ import annotations

from datetime import datetime, timezone, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from app.core.jwt_compat import JWTError

from app.api_v2_deps import (
    auth,
    auth_runtime,
    auth_service,
    consent_lifecycle,
    diagnostic_repositories,
)
from app.api_v2_deps.auth import AuthContext, TokenType, UserRole
from app.core.config import settings


# ── AUTH_RUNTIME & AUTH_SERVICE ───────────────────────────────────────────────


def test_auth_runtime_and_auth_service(monkeypatch):
    mock_db = MagicMock()

    # auth_runtime
    monkeypatch.setattr(auth_runtime, "build_auth_runtime_context", lambda db: "runtime_ctx")
    assert auth_runtime.get_auth_runtime_context(mock_db) == "runtime_ctx"

    # auth_service
    monkeypatch.setattr(auth_service, "build_auth_application_service", lambda db: "app_svc")
    assert auth_service.get_auth_application_service(mock_db) == "app_svc"


# ── DIAGNOSTIC_REPOSITORIES ───────────────────────────────────────────────────


def test_diagnostic_repositories():
    # 1. _split_dotted_path
    mod, attr = diagnostic_repositories._split_dotted_path("a.b.c")
    assert mod == "a.b" and attr == "c"

    with pytest.raises(diagnostic_repositories.DiagnosticRepositoryBoundaryError):
        diagnostic_repositories._split_dotted_path("invalidpath")

    with pytest.raises(diagnostic_repositories.DiagnosticRepositoryBoundaryError):
        diagnostic_repositories._split_dotted_path(".invalid")

    # 2. resolve_repository_class
    # cached
    diagnostic_repositories._CLASS_CACHE["fake_repo"] = MagicMock
    assert diagnostic_repositories.resolve_repository_class("fake_repo") is MagicMock

    # unknown name
    with pytest.raises(diagnostic_repositories.DiagnosticRepositoryBoundaryError) as exc_un:
        diagnostic_repositories.resolve_repository_class("non_existent_target")
    assert "Unknown diagnostics repository" in str(exc_un.value)

    # all targets resolution
    targets = [
        "learner",
        "guardian",
        "irt",
        "diagnostic",
        "knowledge_gap",
        "item_bank",
        "diagnostic_session",
        "mastery",
    ]
    mock_db = MagicMock()
    for name in targets:
        cls = diagnostic_repositories.resolve_repository_class(name)
        assert cls is not None
        inst = diagnostic_repositories.repository(name, mock_db)
        assert inst is not None

    # test helper functions
    assert diagnostic_repositories.learner(mock_db) is not None
    assert diagnostic_repositories.guardian(mock_db) is not None
    assert diagnostic_repositories.irt(mock_db) is not None
    assert diagnostic_repositories.diagnostic(mock_db) is not None
    assert diagnostic_repositories.knowledge_gap(mock_db) is not None
    assert diagnostic_repositories.item_bank(mock_db) is not None
    assert diagnostic_repositories.diagnostic_session(mock_db) is not None
    assert diagnostic_repositories.mastery(mock_db) is not None

    # Failure when all candidates fail
    with patch.dict(diagnostic_repositories._REPOSITORY_TARGETS, {"fail_repo": ("non.existent.Module.Repo",)}):
        if "fail_repo" in diagnostic_repositories._CLASS_CACHE:
            del diagnostic_repositories._CLASS_CACHE["fail_repo"]
        with pytest.raises(diagnostic_repositories.DiagnosticRepositoryBoundaryError) as exc_fail:
            diagnostic_repositories.resolve_repository_class("fail_repo")
        assert "Could not resolve diagnostics repository" in str(exc_fail.value)


# ── CONSENT_LIFECYCLE ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_consent_lifecycle(monkeypatch):
    mock_db = AsyncMock()

    # 1. _load_learner_write_helper
    helper = consent_lifecycle._load_learner_write_helper()
    assert callable(helper)

    # failure branch in _load_learner_write_helper
    with patch("builtins.__import__", side_effect=ImportError("Blocked")):
        with pytest.raises(RuntimeError) as exc_load:
            consent_lifecycle._load_learner_write_helper()
        assert "No learner-write authorization helper found" in str(exc_load.value)

    # 2. _maybe_await
    assert await consent_lifecycle._maybe_await("sync_val") == "sync_val"

    async def async_fn():
        return "async_val"

    assert await consent_lifecycle._maybe_await(async_fn()) == "async_val"

    # 3. authenticated_actor_id
    # dict formats
    assert consent_lifecycle.authenticated_actor_id({"id": "id_1"}) == "id_1"
    assert consent_lifecycle.authenticated_actor_id({"user_id": "uid_2"}) == "uid_2"
    assert consent_lifecycle.authenticated_actor_id({"sub": "sub_3"}) == "sub_3"

    # object formats
    assert consent_lifecycle.authenticated_actor_id(SimpleNamespace(id="obj_id")) == "obj_id"
    assert consent_lifecycle.authenticated_actor_id(SimpleNamespace(user_id="obj_uid")) == "obj_uid"
    assert consent_lifecycle.authenticated_actor_id(SimpleNamespace(sub="obj_sub")) == "obj_sub"

    # error format
    with pytest.raises(HTTPException) as exc_auth:
        consent_lifecycle.authenticated_actor_id(SimpleNamespace())
    assert exc_auth.value.status_code == 401

    with pytest.raises(HTTPException) as exc_dict_fail:
        consent_lifecycle.authenticated_actor_id({"unknown": "val"})
    assert exc_dict_fail.value.status_code == 401

    # 4. enforce_popia_learner_write
    # Success via first attempt
    mock_helper = MagicMock(return_value=True)
    monkeypatch.setattr(consent_lifecycle, "_load_learner_write_helper", lambda: mock_helper)
    assert await consent_lifecycle.enforce_popia_learner_write("user_a", "learner_b") is True

    # Success via kwargs attempt
    def kwargs_only_helper(*args, **kwargs):
        if args:
            raise TypeError("No positional args")
        return kwargs.get("current_user") or kwargs.get("user")

    monkeypatch.setattr(consent_lifecycle, "_load_learner_write_helper", lambda: kwargs_only_helper)
    assert await consent_lifecycle.enforce_popia_learner_write("user_kw", "learner_kw") == "user_kw"

    # Exhausted attempts
    def fail_helper(*args, **kwargs):
        raise TypeError("Failed all")

    monkeypatch.setattr(consent_lifecycle, "_load_learner_write_helper", lambda: fail_helper)
    with pytest.raises(RuntimeError) as exc_enf:
        await consent_lifecycle.enforce_popia_learner_write("user_a", "learner_b")
    assert "Could not call learner-write helper" in str(exc_enf.value)

    # 5. get_canonical_consent_service
    # canonical session param
    class FakeServiceSession:
        def __init__(self, session=None):
            self.session = session

    monkeypatch.setattr(consent_lifecycle, "ConsentService", FakeServiceSession)
    svc1 = consent_lifecycle.get_canonical_consent_service(mock_db)
    assert svc1 is not None

    # canonical db param
    class FakeServiceDb:
        def __init__(self, db=None):
            self.db = db

    monkeypatch.setattr(consent_lifecycle, "ConsentService", FakeServiceDb)
    svc2 = consent_lifecycle.get_canonical_consent_service(mock_db)
    assert svc2 is not None

    # canonical consent_repository param
    class FakeServiceRepo:
        def __init__(self, consent_repository=None):
            self.consent_repository = consent_repository

    monkeypatch.setattr(consent_lifecycle, "ConsentService", FakeServiceRepo)
    svc3 = consent_lifecycle.get_canonical_consent_service(mock_db)
    assert svc3 is not None

    # canonical consent_repo param
    class FakeServiceRepoShort:
        def __init__(self, consent_repo=None):
            self.consent_repo = consent_repo

    monkeypatch.setattr(consent_lifecycle, "ConsentService", FakeServiceRepoShort)
    svc4 = consent_lifecycle.get_canonical_consent_service(mock_db)
    assert svc4 is not None

    # positional db fallback
    class FakeServicePositional:
        def __init__(self, some_arg):
            self.some_arg = some_arg

    monkeypatch.setattr(consent_lifecycle, "ConsentService", FakeServicePositional)
    svc5 = consent_lifecycle.get_canonical_consent_service(mock_db)
    assert svc5 is not None

    # constructor failure
    class FakeServiceFail:
        def __init__(self, arg1, arg2):
            pass

    monkeypatch.setattr(consent_lifecycle, "ConsentService", FakeServiceFail)
    with pytest.raises(RuntimeError) as exc_cs:
        consent_lifecycle.get_canonical_consent_service(mock_db)
    assert "Cannot construct canonical ConsentService" in str(exc_cs.value)

    # 6. get_canonical_data_rights_service
    rights_svc = consent_lifecycle.get_canonical_data_rights_service(mock_db)
    assert rights_svc is not None


# ── AUTH.PY ───────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_auth_deps_complete(monkeypatch):
    # 1. AuthContext properties
    now = datetime.now(timezone.utc)
    ctx_admin = AuthContext(
        user_id="u_admin",
        roles=[UserRole.ADMIN, UserRole.TEACHER],
        token_type=TokenType.ACCESS,
        raw_claims={"sub": "u_admin"},
        expires_at=now + timedelta(hours=1),
        jti="jti_admin_404",
    )
    assert ctx_admin.is_admin is True
    assert ctx_admin.is_teacher is True
    assert ctx_admin.is_parent is False
    assert ctx_admin.is_student is False
    assert ctx_admin.is_expired is False
    assert ctx_admin.subject == "u_admin"

    ctx_parent = AuthContext(
        user_id="u_parent",
        roles=[UserRole.PARENT, UserRole.STUDENT],
        token_type=TokenType.ACCESS,
        raw_claims={"sub": "u_parent"},
        expires_at=now - timedelta(hours=1),
        jti="jti_parent_404",
    )
    assert ctx_parent.is_parent is True
    assert ctx_parent.is_student is True
    assert ctx_parent.is_admin is False
    assert ctx_parent.is_expired is True

    # 2. _parse_roles
    assert auth._parse_roles(None) == []
    assert auth._parse_roles("admin") == [UserRole.ADMIN]
    assert auth._parse_roles(UserRole.PARENT) == [UserRole.PARENT]
    assert auth._parse_roles(["admin", UserRole.TEACHER]) == [UserRole.ADMIN, UserRole.TEACHER]
    assert auth._parse_roles(12345) == []

    # 3. _validate_issuer_and_audience
    # valid or none
    auth._validate_issuer_and_audience({})
    auth._validate_issuer_and_audience({
        "iss": settings.APP_BASE_URL.rstrip("/"),
        "aud": "eduboost-api",
    })

    # invalid issuer
    with pytest.raises(HTTPException) as exc_iss:
        auth._validate_issuer_and_audience({"iss": "https://malicious.issuer"})
    assert exc_iss.value.status_code == 401

    # invalid audience
    with pytest.raises(HTTPException) as exc_aud:
        auth._validate_issuer_and_audience({"aud": "wrong-audience"})
    assert exc_aud.value.status_code == 401

    # 4. _claims_to_auth_context
    # missing sub
    with pytest.raises(HTTPException) as exc_sub:
        auth._claims_to_auth_context({})
    assert exc_sub.value.status_code == 401

    # invalid token type
    with pytest.raises(HTTPException) as exc_type:
        auth._claims_to_auth_context({"sub": "u1", "type": "invalid_type"})
    assert exc_type.value.status_code == 401

    # int/float timestamps & guardian/learner/iss/aud
    full_claims = {
        "sub": "u_full",
        "type": "access",
        "role": ["parent"],
        "iat": 1600000000.0,
        "exp": 1700000000,
        "jti": "jti_full",
        "guardian_id": "g_123",
        "learner_id": "l_456",
        "iss": settings.APP_BASE_URL.rstrip("/"),
        "aud": "eduboost-api",
    }
    ctx_full = auth._claims_to_auth_context(full_claims)
    assert ctx_full.user_id == "u_full"
    assert ctx_full.guardian_id == "g_123"
    assert ctx_full.learner_id == "l_456"
    assert ctx_full.jti == "jti_full"
    assert ctx_full.issued_at is not None and ctx_full.issued_at.timestamp() == 1600000000.0

    # datetime timestamps
    dt_iat = datetime.now(timezone.utc)
    dt_exp = dt_iat + timedelta(hours=2)
    dt_claims = {
        "sub": "u_dt",
        "iat": dt_iat,
        "exp": dt_exp,
    }
    ctx_dt = auth._claims_to_auth_context(dt_claims)
    assert ctx_dt.issued_at == dt_iat
    assert ctx_dt.expires_at == dt_exp

    # fallback timestamps
    ctx_fallback = auth._claims_to_auth_context({"sub": "u_fallback"})
    assert ctx_fallback.issued_at is not None
    assert ctx_fallback.expires_at is not None

    # 5. get_auth_context
    # credentials None -> 401
    with pytest.raises(HTTPException) as exc_none:
        await auth.get_auth_context(None)
    assert exc_none.value.status_code == 401

    cred = HTTPAuthorizationCredentials(scheme="Bearer", credentials="jwt_token_sample")

    # JWTError -> 401
    monkeypatch.setattr(auth, "decode_token", MagicMock(side_effect=JWTError("Invalid sig")))
    with pytest.raises(HTTPException) as exc_jwt:
        await auth.get_auth_context(cred)
    assert exc_jwt.value.status_code == 401

    # Refresh token cannot be used here -> 401
    monkeypatch.setattr(auth, "decode_token", MagicMock(return_value={"sub": "u1", "type": "refresh"}))
    with pytest.raises(HTTPException) as exc_ref:
        await auth.get_auth_context(cred)
    assert exc_ref.value.status_code == 401

    # Token revoked by JTI -> 401
    valid_claims = {"sub": "u1", "type": "access", "jti": "revoked_jti"}
    monkeypatch.setattr(auth, "decode_token", MagicMock(return_value=valid_claims))
    monkeypatch.setattr(auth, "is_token_revoked", AsyncMock(return_value=True))
    with pytest.raises(HTTPException) as exc_rev_jti:
        await auth.get_auth_context(cred)
    assert exc_rev_jti.value.status_code == 401

    # User revoked -> 401
    monkeypatch.setattr(auth, "is_token_revoked", AsyncMock(return_value=False))
    monkeypatch.setattr(auth, "is_user_revoked", AsyncMock(return_value=True))
    with pytest.raises(HTTPException) as exc_rev_usr:
        await auth.get_auth_context(cred)
    assert exc_rev_usr.value.status_code == 401

    # Success
    monkeypatch.setattr(auth, "is_user_revoked", AsyncMock(return_value=False))
    ctx_res = await auth.get_auth_context(cred)
    assert ctx_res.user_id == "u1"

    # 6. require_auth_context
    ctx_req = await auth.require_auth_context({"sub": "u_req", "type": "access"})
    assert ctx_req.user_id == "u_req"

    # 7. get_auth_context_optional
    assert await auth.get_auth_context_optional(None) is None
    opt_res = await auth.get_auth_context_optional(cred)
    assert opt_res is not None and opt_res.user_id == "u1"

    # 8. get_current_user_compat
    compat_res = await auth.get_current_user_compat(ctx_res)
    assert compat_res["sub"] == "u1"

    # 9. require_roles & convenience role dependencies
    admin_checker = auth.require_roles(UserRole.ADMIN)
    assert admin_checker(ctx_admin) == ctx_admin

    with pytest.raises(HTTPException) as exc_role_denied:
        admin_checker(ctx_parent)
    assert exc_role_denied.value.status_code == 403

    assert auth.require_admin(ctx_admin) == ctx_admin
    assert auth.require_parent_or_admin(ctx_parent) == ctx_parent
    assert auth.require_teacher_or_admin(ctx_admin) == ctx_admin
    assert auth.require_student_or_admin(ctx_parent) == ctx_parent
