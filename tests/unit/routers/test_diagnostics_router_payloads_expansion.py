import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.api_v2_routers.diagnostics import (
    _subject_code,
    _option_payload,
    _serialise_item_bank_item,
    _engine_item_from_item_bank,
    ReviewItemRequest,
    _require_item_bank_admin,
)
from app.api_v2_deps.auth import AuthContext
from fastapi import HTTPException


def test_subject_code_and_option_payload():
    assert _subject_code("mathematics") == "MATH"
    assert _subject_code("natural sciences") == "NS"
    assert _subject_code("Other Subject") == "Other Subject"

    opts = _option_payload({"A": "Option A", "B": "Option B"})
    assert len(opts) == 2
    assert opts[0]["key"] == "A"
    assert opts[0]["label"] == "Option A"

    opts_list = _option_payload(["One", "Two"])
    assert len(opts_list) == 2
    assert opts_list[0]["key"] == "A"
    assert opts_list[0]["label"] == "One"


def test_serialise_and_engine_conversion():
    item = MagicMock()
    item.item_id = uuid.uuid4()
    item.stem = "What is 2+2?"
    item.options = ["3", "4", "5"]
    item.subject = "mathematics"
    item.topic = "Addition"
    item.skill = "Basic addition"
    item.difficulty_b = 0.5
    item.discrimination_a = 1.2
    item.caps_ref = "4.M.1.1"
    item.grade = 4
    item.review_status = "approved"

    ser = _serialise_item_bank_item(item)
    assert ser["id"] == str(item.item_id)
    assert ser["subject"] == "MATH"
    assert ser["difficulty"] == 0.5

    eng = _engine_item_from_item_bank(item)
    assert eng.id == str(item.item_id)
    assert eng.grade == 4
    assert eng.subject == "MATH"
    assert eng.b_param == 0.5


def test_require_item_bank_admin():
    admin_ctx = AuthContext(
        user_id="adm-1",
        role="admin",
        roles=["admin"],
        email="admin@test.za",
        token_type="access",
        raw_claims={},
        jti="jti-1",
    )
    _require_item_bank_admin(admin_ctx)

    user_ctx = AuthContext(
        user_id="usr-1",
        role="parent",
        roles=["parent"],
        email="parent@test.za",
        token_type="access",
        raw_claims={},
        jti="jti-2",
    )
    with pytest.raises(HTTPException) as exc_info:
        _require_item_bank_admin(user_ctx)
    assert exc_info.value.status_code == 403
