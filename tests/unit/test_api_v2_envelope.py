"""Unit tests for the canonical V2 API envelope helpers."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
def test_ok_builds_success_envelope() -> None:
    from app.domain.api_v2_models import ok

    envelope = ok({"learner_id": "learner_123"}, request_id="req_123")
    payload = envelope.model_dump(mode="json")

    assert payload == {
        "data": {"learner_id": "learner_123"},
        "error": None,
        "meta": {
            "api_version": "v2",
            "request_id": "req_123",
            "pagination": None,
        },
    }


@pytest.mark.unit
def test_fail_builds_error_envelope() -> None:
    from app.domain.api_v2_models import fail

    envelope = fail(
        code="forbidden",
        message="You do not have access to this learner.",
        request_id="req_456",
        remediation="Confirm the learner is linked to your account.",
        details={"resource": "learner"},
    )
    payload = envelope.model_dump(mode="json")

    assert payload["data"] is None
    assert payload["error"] == {
        "code": "forbidden",
        "message": "You do not have access to this learner.",
        "field_errors": [],
        "remediation": "Confirm the learner is linked to your account.",
        "details": {"resource": "learner"},
    }
    assert payload["meta"] == {
        "api_version": "v2",
        "request_id": "req_456",
        "pagination": None,
    }


@pytest.mark.unit
def test_fail_supports_field_errors() -> None:
    from app.domain.api_v2_models import FieldError, fail

    envelope = fail(
        code="validation_error",
        message="Request validation failed",
        field_errors=[
            FieldError(field="email", message="Enter a valid email address.", code="email"),
            FieldError(field="password", message="Password is too short.", code="too_short"),
        ],
    )
    payload = envelope.model_dump(mode="json")

    assert payload["data"] is None
    assert payload["error"]["code"] == "validation_error"
    assert payload["error"]["field_errors"] == [
        {"field": "email", "message": "Enter a valid email address.", "code": "email"},
        {"field": "password", "message": "Password is too short.", "code": "too_short"},
    ]


@pytest.mark.unit
def test_paginated_builds_success_envelope_with_pagination_meta() -> None:
    from app.domain.api_v2_models import paginated

    envelope = paginated(
        [{"id": "lesson_1"}],
        limit=25,
        offset=0,
        total=51,
        has_more=True,
        next_cursor="cursor_2",
        request_id="req_789",
    )
    payload = envelope.model_dump(mode="json")

    assert payload["data"] == [{"id": "lesson_1"}]
    assert payload["error"] is None
    assert payload["meta"] == {
        "api_version": "v2",
        "request_id": "req_789",
        "pagination": {
            "limit": 25,
            "offset": 0,
            "cursor": None,
            "next_cursor": "cursor_2",
            "total": 51,
            "has_more": True,
        },
    }


@pytest.mark.unit
def test_envelope_content_returns_json_serializable_dict() -> None:
    from app.domain.api_v2_models import envelope_content, ok

    assert envelope_content(ok({"status": "ok"})) == {
        "data": {"status": "ok"},
        "error": None,
        "meta": {
            "api_version": "v2",
            "request_id": None,
            "pagination": None,
        },
    }
