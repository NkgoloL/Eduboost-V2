from __future__ import annotations

import inspect
from enum import Enum
from typing import Any, get_args, get_origin
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.api_v2 import app
from app.api_v2_deps.auth_service import get_auth_application_service
from app.services.auth_db_lifecycle_proof import (
    AuthDBProofApplicationService,
    SQLiteAuthLifecycleProofStore,
)


def _model_fields(model: type[Any]) -> dict[str, Any]:
    return getattr(model, "model_fields", None) or getattr(model, "__fields__", {}) or {}


def _field_annotation(field: Any) -> Any:
    return getattr(field, "annotation", None) or getattr(field, "outer_type_", None) or getattr(field, "type_", None)


def _field_alias(name: str, field: Any) -> str:
    return getattr(field, "alias", None) or name


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
        return [_sample_value(name.rstrip("s") or name, args[0] if args else str)]
    if origin is not None and str(origin).endswith("Union"):
        non_none = [arg for arg in args if arg is not type(None)]
        return _sample_value(name, non_none[0] if non_none else str)
    if _is_basemodel_type(annotation):
        return _payload_for_model(annotation)
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        return next(iter(annotation)).value
    if annotation is bool or lowered in {"terms_accepted", "accepted_terms", "consent"}:
        return True
    if annotation is int or lowered in {"grade", "age"}:
        return 4 if lowered == "grade" else 30
    if annotation is float:
        return 1.0
    if annotation is UUID:
        return "00000000-0000-0000-0000-000000000001"
    if "email" in lowered or lowered == "username":
        return "guardian.dbproof@example.com"
    if "password" in lowered:
        return "Violet-Quartz-Mango-42!"
    if "name" in lowered:
        return "Guardian DB Proof"
    if "refresh" in lowered and "token" in lowered:
        return "placeholder-refresh-token"
    if lowered == "role":
        return "parent"
    if lowered in {"user_role", "account_type", "user_type"}:
        return "guardian"
    if "learner" in lowered and "id" in lowered:
        return "learner-1"
    if "guardian" in lowered and "id" in lowered:
        return "guardian-1"
    if "language" in lowered or lowered == "locale":
        return "en"
    if "subject" in lowered:
        return "Mathematics"
    if "curriculum" in lowered:
        return "CAPS"
    if "province" in lowered:
        return "Gauteng"
    return f"{lowered or 'value'}-dbproof"


def _payload_for_model(model: type[Any] | None) -> dict[str, Any]:
    if model is None:
        return {}
    payload: dict[str, Any] = {}
    for name, field in _model_fields(model).items():
        payload[_field_alias(name, field)] = _sample_value(name, _field_annotation(field))
    return payload


def _post_routes():
    rows = []
    for route in getattr(app, "routes", []):
        methods = getattr(route, "methods", set()) or set()
        if "POST" not in methods:
            continue
        path = getattr(route, "path", "")
        lowered = path.lower()
        endpoint = getattr(getattr(route, "endpoint", None), "__name__", "").lower()
        route_name = getattr(route, "name", "").lower()
        rows.append((f"{lowered} {endpoint} {route_name}", route))
    return rows


def _route_for(token: str):
    candidates = [route for combined, route in _post_routes() if token in combined]
    assert candidates, f"No POST route found for {token!r}"
    candidates.sort(key=lambda route: ("/auth" not in getattr(route, "path", "").lower(), len(getattr(route, "path", ""))))
    return candidates[0]


def _payload_for_route(route) -> dict[str, Any]:
    signature = inspect.signature(route.endpoint)
    for param in signature.parameters.values():
        annotation = param.annotation
        if annotation is inspect.Signature.empty:
            continue
        if _is_basemodel_type(annotation):
            return _payload_for_model(annotation)
    return {}


@pytest.fixture
def store():
    return SQLiteAuthLifecycleProofStore()


@pytest.fixture
def client(store):
    service = AuthDBProofApplicationService(store)
    app.dependency_overrides[get_auth_application_service] = lambda: service
    try:
        yield TestClient(app, raise_server_exceptions=False)
    finally:
        app.dependency_overrides.pop(get_auth_application_service, None)


def test_db_store_register_persists_guardian_and_learner_scope(store):
    tokens = store.register(email="guardian.dbproof@example.com", password="Violet-Quartz-Mango-42!")
    assert tokens.guardian_learner_ids == ["learner-1"]
    user = store.connection.execute("SELECT * FROM users WHERE email = ?", ("guardian.dbproof@example.com",)).fetchone()
    guardian = store.connection.execute("SELECT * FROM guardians WHERE user_id = ?", (tokens.user_id,)).fetchone()
    learners = store.connection.execute("SELECT * FROM learners WHERE guardian_id = ?", (tokens.guardian_id,)).fetchall()
    assert user is not None
    assert guardian is not None
    assert len(learners) == 1


def test_db_store_duplicate_registration_rejected(store):
    store.register(email="guardian.dbproof@example.com", password="Violet-Quartz-Mango-42!")
    with pytest.raises(Exception) as exc:
        store.register(email="guardian.dbproof@example.com", password="Violet-Quartz-Mango-42!")
    assert getattr(exc.value, "status_code", None) == 409


def test_db_store_login_hash_success_and_wrong_password_failure(store):
    store.register(email="guardian.dbproof@example.com", password="Violet-Quartz-Mango-42!")
    tokens = store.login(email="guardian.dbproof@example.com", password="Violet-Quartz-Mango-42!")
    assert tokens.access_token.startswith("access-")
    with pytest.raises(Exception) as exc:
        store.login(email="guardian.dbproof@example.com", password="Crimson-Quartz-Mango-42!")
    assert getattr(exc.value, "status_code", None) == 401


def test_db_store_refresh_persists_scope_and_rejects_replay(store):
    first = store.register(email="guardian.dbproof@example.com", password="Violet-Quartz-Mango-42!")
    refreshed = store.refresh(refresh_token=first.refresh_token)
    assert refreshed.guardian_learner_ids == ["learner-1"]
    with pytest.raises(Exception) as exc:
        store.refresh(refresh_token=first.refresh_token)
    assert getattr(exc.value, "status_code", None) == 401


def test_http_register_login_refresh_success_paths_backed_by_transactional_store(client, store):
    register_route = _route_for("register")
    login_route = _route_for("login")
    refresh_route = _route_for("refresh")

    register_payload = _payload_for_route(register_route)
    register_payload["email"] = "guardian.dbproof@example.com"
    register_payload["password"] = "Violet-Quartz-Mango-42!"
    register_response = client.post(register_route.path, json=register_payload)
    assert register_response.status_code in {200, 201}
    register_body = register_response.json()
    register_data = register_body.get("data", register_body)
    assert "learner-1" in store.learner_ids_for_guardian("guardian-1")

    login_payload = _payload_for_route(login_route)
    login_payload["email"] = "guardian.dbproof@example.com"
    login_payload["password"] = "Violet-Quartz-Mango-42!"
    login_response = client.post(login_route.path, json=login_payload)
    assert login_response.status_code in {200, 201}
    refresh_row = store.connection.execute(
        "SELECT token FROM refresh_tokens ORDER BY rowid DESC LIMIT 1"
    ).fetchone()
    refresh_token = refresh_row["token"] if refresh_row else register_data.get("refresh_token")
    assert refresh_token

    refresh_payload = _payload_for_route(refresh_route)
    refresh_payload["refresh_token"] = refresh_token
    refresh_response = client.post(refresh_route.path, json=refresh_payload)
    assert refresh_response.status_code in {200, 201}
    assert "learner-1" in store.learner_ids_for_guardian("guardian-1")

    replay_response = client.post(refresh_route.path, json=refresh_payload)
    assert replay_response.status_code in {401, 403}
