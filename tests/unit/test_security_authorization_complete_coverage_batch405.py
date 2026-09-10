from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
import pytest
from fastapi import HTTPException

from app.api_v2_deps.auth import AuthContext, TokenType, UserRole
from app.security import authorization, dependencies, object_authorization
from app.security.object_authorization import (
    Actor,
    AuthorizationDecision,
    LearnerOwnedObject,
    OwnershipScope,
    Permission,
    Role,
)


# ── APP.SECURITY.AUTHORIZATION ────────────────────────────────────────────────


def test_security_authorization_policies():
    admin_auth = AuthContext(
        user_id="admin_1",
        roles=[UserRole.ADMIN],
        token_type=TokenType.ACCESS,
        raw_claims={"sub": "admin_1"},
        jti="jti_admin",
    )
    learner_auth = AuthContext(
        user_id="learner_1",
        learner_id="l_100",
        roles=[UserRole.STUDENT],
        token_type=TokenType.ACCESS,
        raw_claims={"sub": "learner_1"},
        jti="jti_learner",
    )
    guardian_auth = AuthContext(
        user_id="guardian_1",
        guardian_id="g_200",
        roles=[UserRole.PARENT],
        token_type=TokenType.ACCESS,
        raw_claims={"sub": "guardian_1"},
        jti="jti_guardian",
    )
    teacher_auth = AuthContext(
        user_id="teacher_1",
        roles=[UserRole.TEACHER],
        token_type=TokenType.ACCESS,
        raw_claims={"sub": "teacher_1"},
        jti="jti_teacher",
    )
    other_auth = AuthContext(
        user_id="other_1",
        roles=[],
        token_type=TokenType.ACCESS,
        raw_claims={"sub": "other_1"},
        jti="jti_other",
    )

    lesson_100: Any = SimpleNamespace(learner_id="l_100")
    lesson_999: Any = SimpleNamespace(learner_id="l_999")

    # 1. can_access_lesson & require_lesson_access
    assert authorization.can_access_lesson(admin_auth, lesson_999) is True
    assert authorization.can_access_lesson(learner_auth, lesson_100) is True
    assert authorization.can_access_lesson(learner_auth, lesson_999) is False
    assert authorization.can_access_lesson(guardian_auth, lesson_100) is False
    assert authorization.can_access_lesson(teacher_auth, lesson_100) is False
    assert authorization.can_access_lesson(other_auth, lesson_100) is False

    authorization.require_lesson_access(admin_auth, lesson_999)
    with pytest.raises(HTTPException) as exc_less_acc:
        authorization.require_lesson_access(other_auth, lesson_100)
    assert exc_less_acc.value.status_code == 403

    # 2. can_write_lesson & require_lesson_write
    assert authorization.can_write_lesson(admin_auth, lesson_999) is True
    assert authorization.can_write_lesson(learner_auth, lesson_100) is True
    assert authorization.can_write_lesson(learner_auth, lesson_999) is False
    assert authorization.can_write_lesson(guardian_auth, lesson_100) is False

    authorization.require_lesson_write(admin_auth, lesson_999)
    with pytest.raises(HTTPException) as exc_less_wr:
        authorization.require_lesson_write(guardian_auth, lesson_100)
    assert exc_less_wr.value.status_code == 403

    # 3. can_access_learner & require_learner_access
    learner_obj: Any = SimpleNamespace(id="l_100", guardian_id="g_200")
    learner_other: Any = SimpleNamespace(id="l_999", guardian_id="g_other")

    assert authorization.can_access_learner(admin_auth, learner_other) is True
    assert authorization.can_access_learner(learner_auth, learner_obj) is True
    assert authorization.can_access_learner(guardian_auth, learner_obj) is True
    assert authorization.can_access_learner(guardian_auth, learner_other) is False
    assert authorization.can_access_learner(teacher_auth, learner_obj) is False
    assert authorization.can_access_learner(other_auth, learner_obj) is False

    authorization.require_learner_access(admin_auth, learner_obj)
    with pytest.raises(HTTPException) as exc_lrn_acc:
        authorization.require_learner_access(other_auth, learner_obj)
    assert exc_lrn_acc.value.status_code == 403

    # 4. can_write_learner & require_learner_write
    assert authorization.can_write_learner(admin_auth, learner_other) is True
    assert authorization.can_write_learner(guardian_auth, learner_obj) is True
    assert authorization.can_write_learner(guardian_auth, learner_other) is False
    assert authorization.can_write_learner(learner_auth, learner_obj) is False
    assert authorization.can_write_learner(other_auth, learner_obj) is False

    authorization.require_learner_write(admin_auth, learner_obj)
    with pytest.raises(HTTPException) as exc_lrn_wr:
        authorization.require_learner_write(learner_auth, learner_obj)
    assert exc_lrn_wr.value.status_code == 403

    # 5. placeholders
    assert authorization._guardian_has_learner_relationship("g_1", "l_1") is False
    assert authorization._teacher_has_learner_assignment("t_1", "l_1") is False


# ── APP.SECURITY.OBJECT_AUTHORIZATION ─────────────────────────────────────────


def test_security_object_authorization(monkeypatch):
    # 1. _permission_roles
    assert object_authorization._permission_roles(Permission.ADMIN) == object_authorization.ADMIN_ROLES
    with pytest.raises(ValueError):
        object_authorization._permission_roles("unsupported_perm")  # type: ignore

    # 2. _scope_for_learner
    sys_actor = Actor.from_values(subject_id="sys_1", roles=(Role.SYSTEM,))
    assert object_authorization._scope_for_learner(sys_actor, "l_1") == OwnershipScope.SYSTEM

    supp_actor = Actor.from_values(subject_id="supp_1", roles=(Role.SUPPORT,))
    assert object_authorization._scope_for_learner(supp_actor, "l_1") == OwnershipScope.SUPPORT

    # 3. Support scope is read-only
    supp_and_learner = Actor.from_values(
        subject_id="supp_user",
        roles=(Role.SUPPORT, Role.LEARNER),
        learner_ids=(),
    )
    dec_supp_write = object_authorization.can_access_learner(supp_and_learner, "l_1", permission=Permission.WRITE)
    assert dec_supp_write.allowed is False
    assert "Support scope is read-only" in dec_supp_write.reason

    # 4. Delete/admin access requires admin or system scope
    admin_actor = Actor.from_values(subject_id="adm_1", roles=(Role.ADMIN,))
    monkeypatch.setattr(object_authorization, "_scope_for_learner", lambda a, lid: OwnershipScope.SELF)
    dec_admin_delete = object_authorization.can_access_learner(admin_actor, "l_1", permission=Permission.DELETE)
    assert dec_admin_delete.allowed is False
    assert "Delete/admin access requires admin or system scope" in dec_admin_delete.reason
    monkeypatch.undo()

    # 5. can_access_object
    self_actor = Actor.from_values(subject_id="l_1", roles=(Role.LEARNER,), learner_ids=("l_1",))
    mock_obj = MagicMock(spec=LearnerOwnedObject)
    mock_obj.learner_id = "l_1"
    dec_obj = object_authorization.can_access_object(self_actor, mock_obj, permission=Permission.READ)
    assert dec_obj.allowed is True

    # 6. require_learner_access raises PermissionError
    with pytest.raises(PermissionError):
        object_authorization.require_learner_access(self_actor, "l_other", permission=Permission.READ)


# ── APP.SECURITY.DEPENDENCIES ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_security_dependencies():
    # 1. get_authorization_actor via headers
    actor_hdr = await dependencies.get_authorization_actor(
        subject_id="sub_h",
        roles="admin,guardian",
        learner_ids="l1,l2",
        guardian_learner_ids="gl1",
        educator_learner_ids="el1",
    )
    assert actor_hdr.subject_id == "sub_h"
    assert Role.ADMIN in actor_hdr.roles

    # 2. raise_for_learner_access
    allowed_actor = Actor.from_values(subject_id="sub_adm", roles=(Role.ADMIN,))
    dec = dependencies.raise_for_learner_access(actor=allowed_actor, learner_id="l1", permission=Permission.READ)
    assert dec.allowed is True

    denied_actor = Actor.from_values(subject_id="sub_den", roles=())
    with pytest.raises(HTTPException) as exc_acc:
        dependencies.raise_for_learner_access(actor=denied_actor, learner_id="l1", permission=Permission.READ)
    assert exc_acc.value.status_code == 403

    # convenience require functions
    assert dependencies.require_learner_read(allowed_actor, "l1").allowed is True
    assert dependencies.require_learner_write(allowed_actor, "l1").allowed is True
    assert dependencies.require_learner_delete(allowed_actor, "l1").allowed is True

    # 3. _current_user_role_value & _role_from_current_user
    assert dependencies._current_user_role_value(UserRole.ADMIN) == "admin"
    assert dependencies._current_user_role_value(None) == ""

    for r_str, expected_role in [
        ("admin", Role.ADMIN),
        ("system", Role.SYSTEM),
        ("support", Role.SUPPORT),
        ("parent", Role.GUARDIAN),
        ("guardian", Role.GUARDIAN),
        ("student", Role.LEARNER),
        ("learner", Role.LEARNER),
        ("teacher", Role.EDUCATOR),
        ("educator", Role.EDUCATOR),
    ]:
        assert dependencies._role_from_current_user(r_str) == expected_role

    with pytest.raises(HTTPException) as exc_r_unsupp:
        dependencies._role_from_current_user("alien_role")
    assert exc_r_unsupp.value.status_code == 401

    # 4. _iter_claim_values
    assert dependencies._iter_claim_values(None) == ()
    assert dependencies._iter_claim_values("a, b ,c") == ("a", "b", "c")
    assert dependencies._iter_claim_values(["x", "y"]) == ("x", "y")
    assert dependencies._iter_claim_values(1234) == ("1234",)

    # 5. _current_user_claims & _current_user_subject
    assert dependencies._current_user_claims(None) == {}
    ctx = AuthContext(
        user_id="u_ctx",
        roles=[UserRole.ADMIN],
        token_type=TokenType.ACCESS,
        raw_claims={"sub": "u_ctx", "role": "admin"},
        jti="jti_dep",
    )
    assert dependencies._current_user_claims(ctx) == {"sub": "u_ctx", "role": "admin"}
    assert dependencies._current_user_subject(ctx) == "u_ctx"
    assert dependencies._current_user_subject({"guardian_id": "g_claim"}) == "g_claim"
    assert dependencies._current_user_subject(None) == ""

    # 6. build_actor_from_current_user_for_learner
    with pytest.raises(HTTPException) as exc_subj:
        dependencies.build_actor_from_current_user_for_learner({}, SimpleNamespace(id="l1"))
    assert exc_subj.value.status_code == 401

    learner_obj = SimpleNamespace(id="l1", guardian_id="g1")

    # LEARNER role match
    act_lrn = dependencies.build_actor_from_current_user_for_learner(
        {"sub": "l1", "role": "student"},
        learner_obj,
    )
    assert "l1" in act_lrn.learner_ids

    # GUARDIAN role match
    act_guard = dependencies.build_actor_from_current_user_for_learner(
        {"sub": "g1", "role": "parent"},
        learner_obj,
    )
    assert "l1" in act_guard.guardian_learner_ids

    # EDUCATOR role match
    act_edu = dependencies.build_actor_from_current_user_for_learner(
        {"sub": "t1", "role": "teacher", "learner_ids": ["l1", "l2"]},
        learner_obj,
    )
    assert "l1" in act_edu.educator_learner_ids

    # require_learner_read_for_current_user
    assert dependencies.require_learner_read_for_current_user(
        {"sub": "l1", "role": "student"},
        learner_obj,
    ).allowed is True

    # 7. build_actor_from_current_user_claims & require_learner_write_for_current_user
    with pytest.raises(HTTPException) as exc_clm_subj:
        dependencies.build_actor_from_current_user_claims({})
    assert exc_clm_subj.value.status_code == 401

    act_from_claims = dependencies.build_actor_from_current_user_claims({
        "sub": "u_all",
        "role": "admin",
        "learner_ids": "l1,l2",
        "guardian_learner_id": "gl1",
        "educator_learner_ids": ["el1"],
    })
    assert act_from_claims.subject_id == "u_all"
    assert "l1" in act_from_claims.learner_ids

    assert dependencies.require_learner_write_for_current_user(
        {"sub": "adm", "role": "admin"},
        "l1",
    ).allowed is True

    # 8. actor_id_from_current_user
    assert dependencies.actor_id_from_current_user(None) is None
    assert dependencies.actor_id_from_current_user(ctx) == "u_ctx"
    assert dependencies.actor_id_from_current_user({"user_id": "u_id"}) == "u_id"
    assert dependencies.actor_id_from_current_user({}) is None

    # 9. require_active_consent_for_current_user
    mock_db = AsyncMock()
    mock_consent_svc = MagicMock()
    mock_consent_svc.require_active_consent = AsyncMock(return_value={"consent": "active"})
    with patch("app.security.dependencies.ConsentService", return_value=mock_consent_svc):
        res_consent = await dependencies.require_active_consent_for_current_user(mock_db, ctx, "l1")
        assert res_consent == {"consent": "active"}
