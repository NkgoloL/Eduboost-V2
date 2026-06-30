from types import SimpleNamespace

import pytest

from app.api_v2_deps.auth import AuthContext, TokenType
from app.models import UserRole
from app.services.popia_service import (
    POPIADataRightsService,
    _current_user_actor_id,
    _current_user_role,
)


def _auth_context() -> AuthContext:
    return AuthContext(
        user_id="guardian-1",
        guardian_id="guardian-1",
        roles=[UserRole.PARENT],
        token_type=TokenType.ACCESS,
        raw_claims={"sub": "guardian-1", "role": "parent"},
        jti="test-jti",
    )


def test_popia_actor_helpers_accept_auth_context_and_legacy_dict() -> None:
    context = _auth_context()

    assert _current_user_actor_id(context) == "guardian-1"
    assert _current_user_role(context) == "parent"
    assert _current_user_actor_id({"sub": "admin-1", "role": "admin"}) == "admin-1"
    assert _current_user_role({"sub": "admin-1", "role": "admin"}) == "admin"


@pytest.mark.asyncio
async def test_build_learner_export_accepts_auth_context(monkeypatch: pytest.MonkeyPatch) -> None:
    service = POPIADataRightsService.__new__(POPIADataRightsService)
    service.consent = SimpleNamespace(called_with=None)
    service.audit = SimpleNamespace(events=[])
    learner = SimpleNamespace(pseudonym_id="learner-pseudo")

    async def load_learner_for_read(learner_id, current_user):
        assert learner_id == "learner-1"
        assert isinstance(current_user, AuthContext)
        return learner

    async def require_active_consent(learner_id, *, actor_id):
        service.consent.called_with = (learner_id, actor_id)

    async def append(event_type, *, actor_id, resource_id, payload):
        service.audit.events.append((event_type, actor_id, resource_id, payload))

    async def export_payload(export_learner):
        assert export_learner is learner
        return {"learner": {"id": "learner-pseudo"}}

    service.load_learner_for_read = load_learner_for_read
    service.consent.require_active_consent = require_active_consent
    service.audit.append = append
    service._export_payload = export_payload

    result = await service.build_learner_export("learner-1", _auth_context())

    assert result["content_type"] == "application/json"
    assert service.consent.called_with == ("learner-1", "guardian-1")
    assert service.audit.events[0][0] == "data_export.requested"
    assert service.audit.events[0][1] == "guardian-1"
