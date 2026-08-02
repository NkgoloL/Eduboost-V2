"""
Unit tests for app.core.consent_gate, app.modules.diagnostics.irt_params,
and app.modules.lessons.prompt_version_registry to expand test coverage.
"""
from __future__ import annotations

import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.core.consent_gate import _get_learner_id_from_request, require_active_consent
from app.modules.diagnostics.irt_params import assign_irt_params, BAND_MIDPOINTS, BAND_BOUNDS


@pytest.mark.asyncio
async def test_get_learner_id_from_request_path_param():
    uid = uuid.uuid4()
    request = MagicMock()
    request.path_params = {"learner_id": str(uid)}
    
    res = await _get_learner_id_from_request(request)
    assert res == uid


@pytest.mark.asyncio
async def test_get_learner_id_from_request_jwt_state():
    uid = uuid.uuid4()
    request = MagicMock()
    request.path_params = {}
    request.state.learner_id = str(uid)

    res = await _get_learner_id_from_request(request)
    assert res == uid


@pytest.mark.asyncio
async def test_get_learner_id_from_request_missing():
    request = MagicMock()
    request.path_params = {}
    request.state = MagicMock(spec=[])

    with pytest.raises(HTTPException) as exc_info:
        await _get_learner_id_from_request(request)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_get_learner_id_from_request_invalid_uuid():
    request = MagicMock()
    request.path_params = {"learner_id": "invalid-uuid"}

    with pytest.raises(HTTPException) as exc_info:
        await _get_learner_id_from_request(request)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_require_active_consent_success():
    uid = uuid.uuid4()
    request = MagicMock()
    request.path_params = {"learner_id": str(uid)}

    consent_service = MagicMock()
    mock_record = MagicMock()
    consent_service.assert_active_consent = AsyncMock(return_value=mock_record)

    res = await require_active_consent(request, consent_service)
    assert res == mock_record
    consent_service.assert_active_consent.assert_awaited_once_with(uid)


@pytest.mark.asyncio
async def test_require_active_consent_permission_error():
    uid = uuid.uuid4()
    request = MagicMock()
    request.path_params = {"learner_id": str(uid)}

    consent_service = MagicMock()
    consent_service.assert_active_consent = AsyncMock(side_effect=PermissionError("No active consent"))

    with pytest.raises(HTTPException) as exc_info:
        await require_active_consent(request, consent_service)
    assert exc_info.value.status_code == 403


def test_assign_irt_params_defaults():
    item = {"item_type": "mcq", "difficulty_band": "easy"}
    res = assign_irt_params(item)
    assert res["discrimination_a"] == 1.0
    assert res["guessing_c"] == 0.25
    assert res["difficulty_b"] == BAND_MIDPOINTS["easy"]


def test_assign_irt_params_non_mcq():
    item = {"item_type": "open_response", "difficulty_band": "challenging"}
    res = assign_irt_params(item)
    assert res["guessing_c"] == 0.0
    assert res["difficulty_b"] == BAND_MIDPOINTS["challenging"]


def test_assign_irt_params_existing_valid_b():
    item = {"item_type": "mcq", "difficulty_band": "moderate", "difficulty_b": -0.7}
    res = assign_irt_params(item)
    assert res["difficulty_b"] == -0.7


def test_assign_irt_params_existing_invalid_b():
    item = {"item_type": "mcq", "difficulty_band": "moderate", "difficulty_b": 2.5}
    res = assign_irt_params(item)
    assert res["difficulty_b"] == BAND_MIDPOINTS["moderate"]


def test_assign_irt_params_non_numeric_b():
    item = {"item_type": "mcq", "difficulty_band": "on_level", "difficulty_b": "not-a-number"}
    res = assign_irt_params(item)
    assert res["difficulty_b"] == BAND_MIDPOINTS["on_level"]
