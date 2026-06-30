from __future__ import annotations

import inspect
from enum import Enum
from typing import Any, get_args, get_origin, Union
from uuid import UUID

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.api_v2 import app
from app.api_v2_deps.auth_service import get_auth_application_service


def _model_fields(model: type[Any]) -> dict[str, Any]:
    return getattr(model, "model_fields", None) or getattr(model, "__fields__", {}) or {}


def _field_alias(name: str, field: Any) -> str:
    alias = getattr(field, "alias", None)
    return alias or name


def _field_annotation(field: Any) -> Any:
    return getattr(field, "annotation", None) or getattr(field, "outer_type_", None) or getattr(field, "type_", None)


def _is_basemodel_type(annotation: Any) -> bool:
    try:
        return isinstance(annotation, type) and issubclass(annotation, BaseModel)
    except TypeError:
        return False


def _sample_value(name: str, annotation: Any = None) -> Any:
    lowered = name.lower()
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin in {list, tuple, set, frozenset}:
        inner = args[0] if args else str
        return [_sample_value(name.rstrip("s") or name, inner)]

    if origin in {Union} or str(origin).endswith("Union"):
        non_none = [arg for arg in args if arg is not type(None)]
        return _sample_value(name, non_none[0] if non_none else str)

    if _is_basemodel_type(annotation):
        return _payload_for_model(annotation)

    try:
        if isinstance(annotation, type) and issubclass(annotation, Enum):
            return next(iter(annotation)).value
    except TypeError:
        pass

    if annotation is bool or lowered.startswith(("is_", "has_")) or lowered in {
        "terms_accepted",
        "accepted_terms",
        "consent",
        "remember_me",
    }:
        return True

    if annotation is int or lowered in {"age", "grade", "expires_in", "ttl"}:
        return 4 if lowered == "grade" else 3600

    if annotation is float:
        return 1.0

    if annotation is UUID:
        return "00000000-0000-0000-0000-000000000001"

    if "email" in lowered:
        return "guardian.success@example.com"
    if "password" in lowered:
        return "Violet-Quartz-Mango-42!"
    if "confirm" in lowered and "password" in lowered:
        return "Violet-Quartz-Mango-42!"
    if lowered in {"name", "full_name", "guardian_name", "display_name"}:
        return "Guardian Success"
    if "first_name" in lowered:
        return "Guardian"
    if "last_name" in lowered:
        return "Success"
    if "refresh" in lowered and "token" in lowered:
        return "refresh-token-success"
    if lowered in {"token", "refresh_token"}:
        return "refresh-token-success"
    if "access" in lowered and "token" in lowered:
        return "access-token-success"
    if lowered in {"token_type", "type"}:
        return "bearer"
    if "guardian_learner" in lowered or "learner_ids" in lowered:
        return ["learner-1", "learner-2"]
    if "learner" in lowered and "id" in lowered:
        return "learner-1"
    if "guardian" in lowered and "id" in lowered:
        return "guardian-1"
    if lowered in {"user_id", "id", "sub"}:
        return "user-1"
    if lowered == "role":
        return "parent"
    if lowered in {"user_role", "account_type", "user_type"}:
        return "guardian"
    if "permission" in lowered or "scope" in lowered:
        return ["learner:read", "learner:write"]
    if "curriculum" in lowered:
        return "CAPS"
    if "province" in lowered:
        return "Gauteng"
    if "subject" in lowered:
        return "Mathematics"
    if "language" in lowered or lowered == "locale":
        return "en"
    if "phone" in lowered:
        return "+27110000000"
    if "cookie" in lowered:
        return "refresh-token-success"

    return f"{lowered or 'value'}-success"


def _payload_for_model(model: type[Any] | None) -> dict[str, Any]:
    if model is None:
        return {}
    fields = _model_fields(model)
    payload: dict[str, Any] = {}
    for name, field in fields.items():
        alias = _field_alias(name, field)
        annotation = _field_annotation(field)
        payload[alias] = _sample_value(name, annotation)
    return payload


def _universal_token_payload() -> dict[str, Any]:
    return {
        "access_token": "access-token-success",
        "refresh_token": "refresh-token-success",
        "token_type": "bearer",
        "expires_in": 3600,
        "guardian_learner_ids": ["learner-1", "learner-2"],
        "permissions": ["learner:read", "learner:write"],
        "role": "guardian",
        "user_role": "guardian",
        "user_id": "user-1",
        "guardian_id": "guardian-1",
        "learner_id": "learner-1",
        "email": "guardian.success@example.com",
        "message": "ok",
        "success": True,
        "user": {
            "id": "user-1",
            "email": "guardian.success@example.com",
            "role": "guardian",
            "guardian_learner_ids": ["learner-1", "learner-2"],
        },
    }


def _post_routes():
    routes = []
    for route in getattr(app, "routes", []):
        methods = getattr(route, "methods", set()) or set()
        path = getattr(route, "path", "")
        if "POST" not in methods:
            continue
        lowered = path.lower()
        endpoint_name = getattr(getattr(route, "endpoint", None), "__name__", "").lower()
        route_name = getattr(route, "name", "").lower()
        combined = " ".join([lowered, endpoint_name, route_name])
        routes.append((combined, route))
    return routes


def _route_for(token: str):
    candidates = [route for combined, route in _post_routes() if token in combined]
    assert candidates, f"No POST auth lifecycle route found for token {token!r}"
    candidates.sort(key=lambda route: ("/auth" not in getattr(route, "path", "").lower(), len(getattr(route, "path", ""))))
    return candidates[0]


def _request_payload_for_route(route) -> dict[str, Any]:
    endpoint = getattr(route, "endpoint", None)
    signature = inspect.signature(endpoint)
    for param in signature.parameters.values():
        annotation = param.annotation
        if annotation is inspect.Signature.empty:
            continue
        if _is_basemodel_type(annotation):
            return _payload_for_model(annotation)
    return {}


class FakeAuthApplicationService:
    def __init__(self):
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.failures: dict[str, Exception] = {}
        self.results: dict[str, dict[str, Any]] = {}

    async def register(self, **kwargs):
        self.calls.append(("register", kwargs))
        if "register" in self.failures:
            raise self.failures["register"]
        payload = _universal_token_payload()
        self.results["register"] = payload
        return payload

    async def login(self, **kwargs):
        self.calls.append(("login", kwargs))
        if "login" in self.failures:
            raise self.failures["login"]
        payload = _universal_token_payload()
        self.results["login"] = payload
        return payload

    async def refresh(self, **kwargs):
        self.calls.append(("refresh", kwargs))
        if "refresh" in self.failures:
            raise self.failures["refresh"]
        payload = _universal_token_payload()
        payload["guardian_learner_ids"] = ["learner-1", "learner-2"]
        payload["permissions"] = ["learner:read", "learner:write"]
        self.results["refresh"] = payload
        return payload

    async def create_dev_session(self, **kwargs):
        self.calls.append(("create_dev_session", kwargs))
        return _universal_token_payload()


@pytest.fixture
def fake_service():
    service = FakeAuthApplicationService()
    app.dependency_overrides[get_auth_application_service] = lambda: service
    try:
        yield service
    finally:
        app.dependency_overrides.pop(get_auth_application_service, None)


def _assert_success_response(response):
    assert response.status_code < 500
    assert response.status_code in {200, 201}
    body = response.json()
    data = body.get("data") if isinstance(body, dict) else None
    payload = data if isinstance(data, dict) else body
    assert "access_token" in payload or "message" in payload or "success" in payload
    return payload


def test_register_http_success_path_uses_service_override(fake_service):
    route = _route_for("register")
    payload = _request_payload_for_route(route)
    response = TestClient(app, raise_server_exceptions=False).post(route.path, json=payload)

    _assert_success_response(response)
    assert fake_service.calls and fake_service.calls[0][0] == "register"


def test_login_http_success_path_uses_service_override(fake_service):
    route = _route_for("login")
    payload = _request_payload_for_route(route)
    response = TestClient(app, raise_server_exceptions=False).post(route.path, json=payload)

    _assert_success_response(response)
    assert fake_service.calls and fake_service.calls[0][0] == "login"


def test_refresh_http_success_path_preserves_guardian_scope(fake_service):
    route = _route_for("refresh")
    payload = _request_payload_for_route(route)
    payload.setdefault("refresh_token", "refresh-token-success")

    client = TestClient(app, raise_server_exceptions=False)
    client.cookies.set("refresh_token", "refresh-token-success")
    response = client.post(route.path, json=payload)

    _assert_success_response(response)
    assert fake_service.calls and fake_service.calls[0][0] == "refresh"
    joined = str(fake_service.results["refresh"])
    assert "learner-1" in joined
    assert "learner-2" in joined


def test_duplicate_registration_failure_is_clean_non_500(fake_service):
    route = _route_for("register")
    payload = _request_payload_for_route(route)
    fake_service.failures["register"] = HTTPException(status_code=409, detail="email already registered")

    response = TestClient(app, raise_server_exceptions=False).post(route.path, json=payload)

    assert response.status_code == 409
    assert "registered" in response.text.lower()


def test_wrong_password_failure_is_clean_non_500(fake_service):
    route = _route_for("login")
    payload = _request_payload_for_route(route)
    fake_service.failures["login"] = HTTPException(status_code=401, detail="invalid credentials")

    response = TestClient(app, raise_server_exceptions=False).post(route.path, json=payload)

    assert response.status_code == 401
    assert "invalid" in response.text.lower()
