"""Comprehensive unit test suite for complete app/security burndown (Batch 420).

Covers:
- app/security/authorization.py
- app/security/dependencies.py
- app/security/object_authorization.py
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

# ---------------------------------------------------------------------------
# 1. app/security/authorization.py
# ---------------------------------------------------------------------------
from typing import Any, cast

from app.api_v2_deps.auth import AuthContext, TokenType
from app.domain.learner import Learner
from app.domain.lesson import Lesson
from app.models import UserRole
from app.security.authorization import (
    can_access_learner as authz_can_access_learner,
    can_access_lesson as authz_can_access_lesson,
    can_write_learner as authz_can_write_learner,
    can_write_lesson as authz_can_write_lesson,
    require_learner_access as authz_require_learner_access,
    require_learner_write as authz_require_learner_write,
    require_lesson_access as authz_require_lesson_access,
    require_lesson_write as authz_require_lesson_write,
)


def _make_auth_context(
    *,
    user_id: str = "user-1",
    role: str = "learner",
    learner_id: str | None = None,
    guardian_id: str | None = None,
) -> AuthContext:
    role_map = {
        "admin": UserRole.ADMIN,
        "parent": UserRole.PARENT,
        "guardian": UserRole.PARENT,
        "teacher": UserRole.TEACHER,
        "educator": UserRole.TEACHER,
        "learner": UserRole.STUDENT,
        "student": UserRole.STUDENT,
    }
    user_role = role_map.get(role.lower(), UserRole.STUDENT)
    return AuthContext(
        user_id=user_id,
        guardian_id=guardian_id,
        learner_id=learner_id,
        roles=[user_role],
        token_type=TokenType.ACCESS,
        jti="jti-123",
        raw_claims={"sub": user_id, "role": role},
    )


def test_can_access_and_write_lesson():
    dummy_lesson = cast(Lesson, SimpleNamespace(id=uuid4(), learner_id="learner-1"))

    # Admin access & write
    admin_ctx = _make_auth_context(role="admin")
    assert authz_can_access_lesson(admin_ctx, dummy_lesson)
    assert authz_can_write_lesson(admin_ctx, dummy_lesson)
    authz_require_lesson_access(admin_ctx, dummy_lesson)
    authz_require_lesson_write(admin_ctx, dummy_lesson)

    # Learner matching
    learner_ctx = _make_auth_context(role="learner", learner_id="learner-1")
    assert authz_can_access_lesson(learner_ctx, dummy_lesson)
    assert authz_can_write_lesson(learner_ctx, dummy_lesson)

    # Learner mismatch
    mismatch_ctx = _make_auth_context(role="learner", learner_id="other-learner")
    assert not authz_can_access_lesson(mismatch_ctx, dummy_lesson)
    assert not authz_can_write_lesson(mismatch_ctx, dummy_lesson)
    with pytest.raises(HTTPException) as exc_access:
        authz_require_lesson_access(mismatch_ctx, dummy_lesson)
    assert exc_access.value.status_code == 403

    with pytest.raises(HTTPException) as exc_write:
        authz_require_lesson_write(mismatch_ctx, dummy_lesson)
    assert exc_write.value.status_code == 403

    # Guardian & Educator access (read-only and placeholder relationship check)
    parent_ctx = _make_auth_context(role="parent", guardian_id="guardian-1")
    assert not authz_can_access_lesson(parent_ctx, dummy_lesson)  # placeholder returns False
    assert not authz_can_write_lesson(parent_ctx, dummy_lesson)

    teacher_ctx = _make_auth_context(role="teacher")
    assert not authz_can_access_lesson(teacher_ctx, dummy_lesson)  # placeholder returns False
    assert not authz_can_write_lesson(teacher_ctx, dummy_lesson)

    other_ctx = _make_auth_context(role="other")
    assert not authz_can_access_lesson(other_ctx, dummy_lesson)


def test_can_access_and_write_learner():
    dummy_learner = cast(Learner, SimpleNamespace(id="learner-1", guardian_id="guardian-1"))

    # Admin access & write
    admin_ctx = _make_auth_context(role="admin")
    assert authz_can_access_learner(admin_ctx, dummy_learner)
    assert authz_can_write_learner(admin_ctx, dummy_learner)
    authz_require_learner_access(admin_ctx, dummy_learner)
    authz_require_learner_write(admin_ctx, dummy_learner)

    # Learner access (can read own, cannot write own)
    learner_ctx = _make_auth_context(role="learner", learner_id="learner-1")
    assert authz_can_access_learner(learner_ctx, dummy_learner)
    assert not authz_can_write_learner(learner_ctx, dummy_learner)

    # Guardian matching (can read and write)
    guardian_ctx = _make_auth_context(role="parent", guardian_id="guardian-1")
    assert authz_can_access_learner(guardian_ctx, dummy_learner)
    assert authz_can_write_learner(guardian_ctx, dummy_learner)

    # Guardian mismatch
    mismatch_guardian = _make_auth_context(role="parent", guardian_id="other-guardian")
    assert not authz_can_access_learner(mismatch_guardian, dummy_learner)
    assert not authz_can_write_learner(mismatch_guardian, dummy_learner)

    # Teacher access (placeholder check)
    teacher_ctx = _make_auth_context(role="teacher")
    assert not authz_can_access_learner(teacher_ctx, dummy_learner)
    assert not authz_can_write_learner(teacher_ctx, dummy_learner)

    # Other role
    other_ctx = _make_auth_context(role="other")
    assert not authz_can_access_learner(other_ctx, dummy_learner)
    with pytest.raises(HTTPException) as exc_read:
        authz_require_learner_access(other_ctx, dummy_learner)
    assert exc_read.value.status_code == 403

    with pytest.raises(HTTPException) as exc_write:
        authz_require_learner_write(other_ctx, dummy_learner)
    assert exc_write.value.status_code == 403


# ---------------------------------------------------------------------------
# 2. app/security/dependencies.py
# ---------------------------------------------------------------------------
from app.security.dependencies import (
    _current_user_claims,
    _current_user_role_value,
    _current_user_subject,
    _iter_claim_values,
    _parse_roles,
    _role_from_current_user,
    _split_header_values,
    actor_id_from_current_user,
    build_actor_from_current_user_claims,
    build_actor_from_current_user_for_learner,
    build_actor_from_headers,
    get_authorization_actor,
    raise_for_learner_access,
    require_active_consent_for_current_user,
    require_learner_delete,
    require_learner_read,
    require_learner_read_for_current_user,
    require_learner_write,
    require_learner_write_for_current_user,
)
from app.security.object_authorization import (
    Actor,
    AuthorizationDecision,
    OwnershipScope,
    Permission,
    Role,
)


def test_split_and_parse_roles():
    assert _split_header_values(None) == ()
    assert _split_header_values("") == ()
    assert _split_header_values("admin, learner, , educator") == ("admin", "learner", "educator")

    roles = _parse_roles(["admin", "guardian"])
    assert roles == (Role.ADMIN, Role.GUARDIAN)

    with pytest.raises(HTTPException) as exc_role:
        _parse_roles(["invalid_role"])
    assert exc_role.value.status_code == 401


@pytest.mark.asyncio
async def test_build_actor_from_headers_and_dependency():
    # Missing subject
    with pytest.raises(HTTPException) as exc_sub:
        build_actor_from_headers(subject_id=None, roles="admin")
    assert exc_sub.value.status_code == 401

    # Missing roles
    with pytest.raises(HTTPException) as exc_no_roles:
        build_actor_from_headers(subject_id="user-1", roles=None)
    assert exc_no_roles.value.status_code == 401

    # Valid actor
    actor = build_actor_from_headers(
        subject_id="user-1",
        roles="admin,educator",
        learner_ids="l1,l2",
        guardian_learner_ids="g1",
        educator_learner_ids="e1",
    )
    assert actor.subject_id == "user-1"
    assert Role.ADMIN in actor.roles
    assert "l1" in actor.learner_ids
    assert "g1" in actor.guardian_learner_ids
    assert "e1" in actor.educator_learner_ids

    # get_authorization_actor async wrapper
    dep_actor = await get_authorization_actor(subject_id="user-1", roles="admin")
    assert dep_actor.subject_id == "user-1"


def test_raise_for_learner_access_and_wrappers():
    admin_actor = Actor.from_values(subject_id="admin-1", roles=[Role.ADMIN])
    dec = raise_for_learner_access(actor=admin_actor, learner_id="l1", permission=Permission.READ)
    assert dec.allowed

    read_dec = require_learner_read(admin_actor, "l1")
    assert read_dec.allowed

    write_dec = require_learner_write(admin_actor, "l1")
    assert write_dec.allowed

    delete_dec = require_learner_delete(admin_actor, "l1")
    assert delete_dec.allowed

    # Denied access raises HTTPException 403 with detailed payload
    stranger = Actor.from_values(subject_id="stranger", roles=[Role.LEARNER])
    with pytest.raises(HTTPException) as exc_denied:
        require_learner_read(stranger, "other-learner")
    assert exc_denied.value.status_code == 403
    assert isinstance(exc_denied.value.detail, dict)
    assert exc_denied.value.detail["code"] == "object_forbidden"


def test_role_from_current_user_and_actor_builders():
    assert _current_user_role_value(Role.ADMIN) == "admin"
    assert _current_user_role_value("Guardian") == "guardian"
    assert _current_user_role_value(None) == ""

    # All mapped roles
    assert _role_from_current_user("admin") == Role.ADMIN
    assert _role_from_current_user("system") == Role.SYSTEM
    assert _role_from_current_user("support") == Role.SUPPORT
    assert _role_from_current_user("parent") == Role.GUARDIAN
    assert _role_from_current_user("guardian") == Role.GUARDIAN
    assert _role_from_current_user("student") == Role.LEARNER
    assert _role_from_current_user("learner") == Role.LEARNER
    assert _role_from_current_user("teacher") == Role.EDUCATOR
    assert _role_from_current_user("educator") == Role.EDUCATOR

    with pytest.raises(HTTPException) as exc_unsupported:
        _role_from_current_user("unknown_role")
    assert exc_unsupported.value.status_code == 401

    # build_actor_from_current_user_for_learner
    learner_obj = SimpleNamespace(id="learner-1", guardian_id="guardian-1")

    # Learner self
    learner_payload = {"sub": "learner-1", "role": "learner"}
    actor_l = build_actor_from_current_user_for_learner(learner_payload, learner_obj)
    assert "learner-1" in actor_l.learner_ids
    read_self = require_learner_read_for_current_user(learner_payload, learner_obj)
    assert read_self.allowed

    # Guardian linking
    guardian_payload = {"sub": "guardian-1", "role": "guardian"}
    actor_g = build_actor_from_current_user_for_learner(guardian_payload, learner_obj)
    assert "learner-1" in actor_g.guardian_learner_ids

    # Educator with learner_ids in claims
    educator_payload = {"sub": "teacher-1", "role": "teacher", "learner_ids": ["learner-1"]}
    actor_e = build_actor_from_current_user_for_learner(educator_payload, learner_obj)
    assert "learner-1" in actor_e.educator_learner_ids

    # Missing subject in current user
    with pytest.raises(HTTPException) as exc_no_sub:
        build_actor_from_current_user_for_learner({"role": "admin"}, learner_obj)
    assert exc_no_sub.value.status_code == 401


def test_claim_helpers_and_write_dependencies():
    # _iter_claim_values
    assert _iter_claim_values(None) == ()
    assert _iter_claim_values("a, b") == ("a", "b")
    assert _iter_claim_values(["a", "b"]) == ("a", "b")
    assert _iter_claim_values(123) == ("123",)

    # _current_user_claims and _current_user_subject
    auth_ctx = _make_auth_context(user_id="user-1", role="admin")
    assert _current_user_claims(auth_ctx) == {"sub": "user-1", "role": "admin"}
    assert _current_user_claims(None) == {}
    assert _current_user_claims({"role": "learner"}) == {"role": "learner"}

    assert _current_user_subject(auth_ctx) == "user-1"
    assert _current_user_subject({"id": "id-1"}) == "id-1"
    assert _current_user_subject({"user_id": "uid-1"}) == "uid-1"
    assert _current_user_subject({"guardian_id": "gid-1"}) == "gid-1"
    assert _current_user_subject({}) == ""

    # build_actor_from_current_user_claims
    with pytest.raises(HTTPException):
        build_actor_from_current_user_claims({})

    actor_claims = build_actor_from_current_user_claims({
        "sub": "user-1",
        "role": "guardian",
        "guardian_learner_ids": "l1,l2",
    })
    assert actor_claims.subject_id == "user-1"
    assert "l1" in actor_claims.guardian_learner_ids

    # require_learner_write_for_current_user
    admin_payload = {"sub": "admin-1", "role": "admin"}
    write_res = require_learner_write_for_current_user(admin_payload, "l1")
    assert write_res.allowed

    # actor_id_from_current_user
    assert actor_id_from_current_user(None) is None
    assert actor_id_from_current_user(auth_ctx) == "user-1"
    assert actor_id_from_current_user({"sub": "user-2"}) == "user-2"


@pytest.mark.asyncio
async def test_require_active_consent_for_current_user():
    db = AsyncMock()
    with patch("app.security.dependencies.ConsentService") as mock_consent_cls:
        mock_svc = AsyncMock()
        mock_consent_cls.return_value = mock_svc
        mock_svc.require_active_consent.return_value = True

        res = await require_active_consent_for_current_user(db, {"sub": "user-1"}, "learner-1")
        assert res is True
        mock_svc.require_active_consent.assert_awaited_once_with("learner-1", actor_id="user-1")


# ---------------------------------------------------------------------------
# 3. app/security/object_authorization.py
# ---------------------------------------------------------------------------
from app.security.object_authorization import (
    _permission_roles,
    _scope_for_learner,
    actor_has_role,
    can_access_learner,
    can_access_object,
    normalize_permission,
    require_learner_access,
)


def test_object_authorization_core_logic():
    # normalize_permission
    assert normalize_permission("read") == Permission.READ
    assert normalize_permission(Permission.WRITE) == Permission.WRITE

    # actor_has_role
    actor = Actor.from_values(subject_id="u1", roles=[Role.ADMIN, Role.EDUCATOR])
    assert actor_has_role(actor, Role.ADMIN)
    assert not actor_has_role(actor, Role.GUARDIAN)

    # _permission_roles
    assert Role.ADMIN in _permission_roles(Permission.READ)
    assert Role.ADMIN in _permission_roles(Permission.WRITE)
    assert Role.ADMIN in _permission_roles(Permission.DELETE)
    assert Role.ADMIN in _permission_roles(Permission.ADMIN)
    with pytest.raises(ValueError, match="Unsupported permission"):
        _permission_roles(cast(Permission, "invalid"))

    # _scope_for_learner
    admin_act = Actor.from_values(subject_id="admin-1", roles=[Role.ADMIN])
    assert _scope_for_learner(admin_act, "l1") == OwnershipScope.ADMIN

    system_act = Actor.from_values(subject_id="sys-1", roles=[Role.SYSTEM])
    assert _scope_for_learner(system_act, "l1") == OwnershipScope.SYSTEM

    self_act = Actor.from_values(subject_id="l1", roles=[Role.LEARNER])
    assert _scope_for_learner(self_act, "l1") == OwnershipScope.SELF

    self_in_ids = Actor.from_values(subject_id="u1", roles=[Role.LEARNER], learner_ids=["l1"])
    assert _scope_for_learner(self_in_ids, "l1") == OwnershipScope.SELF

    guard_act = Actor.from_values(subject_id="g1", roles=[Role.GUARDIAN], guardian_learner_ids=["l1"])
    assert _scope_for_learner(guard_act, "l1") == OwnershipScope.GUARDIAN

    edu_act = Actor.from_values(subject_id="e1", roles=[Role.EDUCATOR], educator_learner_ids=["l1"])
    assert _scope_for_learner(edu_act, "l1") == OwnershipScope.EDUCATOR

    support_act = Actor.from_values(subject_id="s1", roles=[Role.SUPPORT])
    assert _scope_for_learner(support_act, "l1") == OwnershipScope.SUPPORT

    unrelated_act = Actor.from_values(subject_id="u2", roles=[Role.LEARNER])
    assert _scope_for_learner(unrelated_act, "l1") is None


def test_can_access_learner_decisions():
    # 1. Deny on role missing permitted roles
    # Support role cannot write
    support_act = Actor.from_values(subject_id="s1", roles=[Role.SUPPORT])
    dec_supp_write = can_access_learner(support_act, "l1", permission=Permission.WRITE)
    assert not dec_supp_write.allowed
    assert "do not allow write access" in dec_supp_write.reason

    # 2. Deny on scope is None
    stranger = Actor.from_values(subject_id="stranger", roles=[Role.LEARNER])
    dec_no_scope = can_access_learner(stranger, "l1", permission=Permission.READ)
    assert not dec_no_scope.allowed
    assert "no ownership" in dec_no_scope.reason

    # 3. Deny on Support scope attempting write/delete/admin (even if role permitted)
    # Give support both roles just to test line 233
    support_dual = Actor.from_values(subject_id="s1", roles=[Role.SUPPORT, Role.SYSTEM])
    # System role gives system scope, but let's test support scope specifically:
    support_only = Actor.from_values(subject_id="s1", roles=[Role.SUPPORT, Role.GUARDIAN], guardian_learner_ids=[])
    # Role GUARDIAN is in WRITE_ROLES, but scope for learner is SUPPORT:
    dec_supp_only = can_access_learner(support_only, "l1", permission=Permission.WRITE)
    assert not dec_supp_only.allowed
    assert "Support scope is read-only" in dec_supp_only.reason

    # 4. Deny on DELETE/ADMIN when scope is not ADMIN or SYSTEM
    self_act = Actor.from_values(subject_id="l1", roles=[Role.LEARNER, Role.ADMIN])
    # When role has ADMIN, scope is ADMIN, but if scope is SELF and role is SYSTEM:
    # Test line 241: normalized_permission in {DELETE, ADMIN} and scope not in {ADMIN, SYSTEM}:
    self_with_delete_role = Actor.from_values(subject_id="l1", roles=[Role.LEARNER, Role.SYSTEM], learner_ids=["l1"])
    # If role has SYSTEM, _scope_for_learner returns SYSTEM. So create an actor where scope is SELF or GUARDIAN:
    # We patch _scope_for_learner to return OwnershipScope.SELF while actor has Role.ADMIN in permitted roles:
    with patch("app.security.object_authorization._scope_for_learner", return_value=OwnershipScope.SELF):
        admin_act = Actor.from_values(subject_id="a1", roles=[Role.ADMIN])
        dec_del_self = can_access_learner(admin_act, "l1", permission=Permission.DELETE)
        assert not dec_del_self.allowed
        assert "Delete/admin access requires admin or system scope" in dec_del_self.reason

    # 5. Allow decision
    admin_act = Actor.from_values(subject_id="admin-1", roles=[Role.ADMIN])
    dec_allow = can_access_learner(admin_act, "l1", permission=Permission.READ)
    assert dec_allow.allowed
    assert dec_allow.scope == OwnershipScope.ADMIN
    assert "Actor authorized through admin scope" in dec_allow.reason

    # can_access_object
    obj = SimpleNamespace(learner_id="l1")
    assert can_access_object(admin_act, obj).allowed

    # require_learner_access
    assert require_learner_access(admin_act, "l1").allowed
    with pytest.raises(PermissionError):
        require_learner_access(stranger, "l1")
