import pytest

from app.services.auth_service import AuthService


def test_auth_service_creates_and_rotates_session(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    service = AuthService()

    session = service.create_session(subject="guardian-1", role="Parent")
    assert session.access_token
    assert session.refresh_token

    rotated = service.rotate_refresh_token(session.refresh_token)
    assert rotated.access_token
    assert rotated.refresh_token


def test_auth_service_rejects_access_token_for_refresh(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    service = AuthService()
    session = service.create_session(subject="guardian-1", role="Parent")

    with pytest.raises(ValueError):
        service.rotate_refresh_token(session.access_token)
