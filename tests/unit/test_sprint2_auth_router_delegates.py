from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from starlette.responses import Response

from app.api_v2_routers import auth


class FakeAuthService:
    async def register(self, **kwargs):
        return {"op": "register", "kwargs": kwargs}

    async def login(self, **kwargs):
        return {"op": "login", "kwargs": kwargs}

    async def create_dev_session(self, **kwargs):
        return {"op": "dev-session", "kwargs": kwargs}

    async def refresh(self, **kwargs):
        return {"op": "refresh", "kwargs": kwargs}

    async def logout(self, **kwargs):
        return Response(status_code=204)

    async def revoke_all_tokens(self, **kwargs):
        return Response(status_code=204)


def _unwrap(func):
    while hasattr(func, "__wrapped__"):
        func = func.__wrapped__
    return func


@pytest.mark.asyncio
async def test_router_helper_claim_merges_delegate_to_services(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(auth, "build_access_token_claims", lambda user, existing_claims=None, extra=None: {"user": user, "extra": extra})
    monkeypatch.setattr(auth, "merge_refresh_claims", lambda existing_claims, user: {"merged": True, "user": user, "existing": existing_claims})

    access = auth._canonical_access_claims({"id": "u1"}, existing_claims={"a": 1}, extra={"x": 2})
    refresh = auth._canonical_refresh_claims({"a": 1}, {"id": "u1"})

    assert access["user"]["id"] == "u1"
    assert access["extra"]["x"] == 2
    assert refresh["merged"] is True


def test_legacy_refresh_error_response_shape():
    response = auth._legacy_refresh_error_response("invalid refresh", status_code=401)
    body = response.body.decode("utf-8")

    assert response.status_code == 401
    assert "invalid_refresh_token" in body
    assert "invalid refresh" in body


@pytest.mark.asyncio
async def test_me_register_login_refresh_delegation_paths():
    service = FakeAuthService()
    request = SimpleNamespace()
    response = Response()
    body = SimpleNamespace()

    register = _unwrap(auth.register)
    login = _unwrap(auth.login)
    refresh = _unwrap(auth.refresh)

    assert await auth.me({"sub": "u1"}) == {"sub": "u1"}

    register_result = await register(request=request, body=body, response=response, db=None, auth_runtime=SimpleNamespace(), auth_service=service)
    assert register_result["op"] == "register"

    login_result = await login(request=request, body=body, response=response, db=None, auth_runtime=SimpleNamespace(), auth_service=service)
    assert login_result["op"] == "login"

    refresh_result = await refresh(
        request=request,
        response=response,
        body=None,
        db=None,
        cookie_refresh="refresh-cookie",
        auth_runtime=SimpleNamespace(),
        auth_service=service,
    )
    assert refresh_result["op"] == "refresh"


@pytest.mark.asyncio
async def test_create_dev_session_production_and_non_production(monkeypatch: pytest.MonkeyPatch):
    service = FakeAuthService()
    response = Response()

    monkeypatch.setattr(type(auth.settings), "is_production", lambda _self: True)
    with pytest.raises(HTTPException) as exc_info:
        await auth.create_dev_session(response=response, db=None, auth_runtime=SimpleNamespace(), auth_service=service)
    assert exc_info.value.status_code == 404

    monkeypatch.setattr(type(auth.settings), "is_production", lambda _self: False)
    result = await auth.create_dev_session(response=response, db=None, auth_runtime=SimpleNamespace(), auth_service=service)
    assert result["op"] == "dev-session"


@pytest.mark.asyncio
async def test_sessions_logout_and_revoke_all_paths(monkeypatch: pytest.MonkeyPatch):
    service = FakeAuthService()
    monkeypatch.setattr(auth, "list_user_refresh_sessions", AsyncMock(return_value=[{"jti": "j1"}]))

    sessions = await auth.list_sessions(current_user={"sub": "user-123"})
    assert sessions == {"sessions": [{"jti": "j1"}]}

    logout_response = await auth.logout(
        response=Response(),
        current_user={"sub": "user-123"},
        db=None,
        cookie_refresh="r1",
        auth_service=service,
    )
    assert logout_response.status_code == 204

    revoke_response = await auth.revoke_all_tokens(
        response=Response(),
        current_user={"sub": "user-123"},
        db=None,
        cookie_refresh="r1",
        auth_service=service,
    )
    assert revoke_response.status_code == 204


def test_set_refresh_cookie_sets_expected_security_flags():
    response = Response()

    auth._set_refresh_cookie(response, "refresh-token-value")

    cookie = response.headers["set-cookie"]
    assert f"{auth.REFRESH_COOKIE}=refresh-token-value" in cookie
    assert "HttpOnly" in cookie
    assert "Secure" in cookie
    assert "SameSite=strict" in cookie
    assert "Path=/api/v2/auth" in cookie
