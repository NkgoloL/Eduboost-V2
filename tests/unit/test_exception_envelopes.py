"""Tests for canonical V2 global exception envelopes."""
from __future__ import annotations

from functools import partial
from typing import Any

import anyio
import pytest
from fastapi import Body, FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel, EmailStr


class SignupRequest(BaseModel):
    email: EmailStr
    password: str


def _build_app() -> FastAPI:
    from app.core.exceptions import ConsentRequiredError, DuplicateError, register_exception_handlers

    app = FastAPI()
    register_exception_handlers(app)

    @app.middleware("http")
    async def add_request_id(request, call_next):  # type: ignore[no-untyped-def]
        request.state.request_id = "req_test"
        return await call_next(request)

    @app.get("/http-not-found")
    async def http_not_found() -> None:
        raise HTTPException(status_code=404, detail="Missing learner")

    @app.get("/http-dict-detail")
    async def http_dict_detail() -> None:
        raise HTTPException(
            status_code=403,
            detail={
                "message": "Forbidden learner access",
                "resource": "learner",
            },
        )

    @app.get("/domain-consent")
    async def domain_consent() -> None:
        raise ConsentRequiredError("Consent is required", {"learner_id": "learner_123"})

    @app.get("/domain-conflict")
    async def domain_conflict() -> None:
        raise DuplicateError("Resource already exists")

    @app.post("/validation")
    async def validation(payload: SignupRequest = Body(...)) -> dict[str, Any]:
        return payload.model_dump()

    @app.get("/unhandled")
    async def unhandled() -> None:
        raise RuntimeError("database password should not leak")

    return app


async def _request(path: str, *, method: str = "get", json: dict[str, Any] | None = None):
    transport = ASGITransport(app=_build_app(), raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.request(method.upper(), path, json=json)


@pytest.mark.unit
def test_http_exception_uses_canonical_error_envelope() -> None:
    response = anyio.run(_request, "/http-not-found")

    assert response.status_code == 404
    assert response.json() == {
        "data": None,
        "error": {
            "code": "not_found",
            "message": "Missing learner",
            "field_errors": [],
            "remediation": None,
            "details": {},
        },
        "meta": {
            "api_version": "v2",
            "request_id": "req_test",
            "pagination": None,
        },
    }


@pytest.mark.unit
def test_http_exception_with_dict_detail_preserves_safe_details() -> None:
    response = anyio.run(_request, "/http-dict-detail")

    assert response.status_code == 403
    payload = response.json()
    assert payload["data"] is None
    assert payload["error"]["code"] == "forbidden"
    assert payload["error"]["message"] == "Forbidden learner access"
    assert payload["error"]["details"] == {"resource": "learner"}
    assert payload["meta"]["request_id"] == "req_test"


@pytest.mark.unit
def test_domain_exception_uses_domain_code_and_details() -> None:
    response = anyio.run(_request, "/domain-consent")

    assert response.status_code == 403
    payload = response.json()
    assert payload["data"] is None
    assert payload["error"]["code"] == "consent_required"
    assert payload["error"]["message"] == "Consent is required"
    assert payload["error"]["details"] == {"learner_id": "learner_123"}
    assert payload["meta"]["request_id"] == "req_test"


@pytest.mark.unit
def test_duplicate_error_maps_to_conflict_code() -> None:
    response = anyio.run(_request, "/domain-conflict")

    assert response.status_code == 409
    payload = response.json()
    assert payload["error"]["code"] == "conflict"
    assert payload["error"]["message"] == "Resource already exists"


@pytest.mark.unit
def test_validation_exception_uses_field_errors() -> None:
    response = anyio.run(partial(_request, "/validation", method="post", json={"email": "not-an-email"}))

    assert response.status_code == 422
    payload = response.json()
    assert payload["data"] is None
    assert payload["error"]["code"] == "validation_error"
    assert payload["error"]["message"] == "Request validation failed"
    assert {"field": "email", "message": "value is not a valid email address", "code": "value_error"} in payload["error"]["field_errors"] or any(
        item["field"] == "email" for item in payload["error"]["field_errors"]
    )
    assert payload["error"]["details"]["errors"]
    assert payload["meta"]["request_id"] == "req_test"


@pytest.mark.unit
def test_unhandled_exception_uses_safe_internal_error_message() -> None:
    response = anyio.run(_request, "/unhandled")

    assert response.status_code == 500
    payload = response.json()
    assert payload["data"] is None
    assert payload["error"]["code"] == "internal_error"
    assert payload["error"]["message"] == "An unexpected error occurred"
    assert "database password should not leak" not in str(payload)
    assert payload["meta"]["request_id"] == "req_test"
