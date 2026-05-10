from __future__ import annotations

import pytest

from app.security.dependencies import actor_id_from_current_user


@pytest.mark.unit
def test_actor_id_from_current_user_prefers_subject_claim() -> None:
    assert actor_id_from_current_user({"sub": "guardian-1", "id": "fallback"}) == "guardian-1"


@pytest.mark.unit
def test_actor_id_from_current_user_falls_back_to_stable_identity_fields() -> None:
    assert actor_id_from_current_user({"id": "user-1"}) == "user-1"
    assert actor_id_from_current_user({"user_id": "user-2"}) == "user-2"
    assert actor_id_from_current_user({"guardian_id": "guardian-2"}) == "guardian-2"


@pytest.mark.unit
def test_actor_id_from_current_user_handles_missing_actor() -> None:
    assert actor_id_from_current_user({}) is None
    assert actor_id_from_current_user(None) is None


@pytest.mark.unit
def test_consent_dependency_adapter_delegates_denial_to_consent_service_contract() -> None:
    """Source-level denial regression until DB-backed consent fixtures are available.

    The adapter must not swallow ConsentRequiredError or ConsentExpiredError.
    It delegates directly to ConsentService.require_active_consent, whose
    service contract emits consent.access_rejected audit evidence before
    raising the denial.
    """
    import inspect

    from app.security import dependencies

    source = inspect.getsource(dependencies.require_active_consent_for_current_user)

    assert "ConsentService(db).require_active_consent" in source
    assert "try:" not in source
    assert "except" not in source
    assert "actor_id=actor_id_from_current_user(current_user)" in source
