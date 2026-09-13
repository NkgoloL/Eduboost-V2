import math
import uuid
import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from app.services.diagnostic_data_integrity import (
    DiagnosticIntegrityError,
    DiagnosticSubmissionIntegrityResult,
    clamp_theta,
    extract_diagnostic_item_ids,
    validate_diagnostic_submission_payload,
    validate_mastery_update_payload,
    validate_theta_update,
)
from app.services.diagnostic_transactional_response import (
    DiagnosticTransactionError,
    DiagnosticTransactionInput,
    TransactionalDiagnosticResponseService,
)


def test_diagnostic_data_integrity_complete():
    # 1. extract_diagnostic_item_ids with cycle, strings, None, child attributes, and key aliases (lines 27, 30, 34, 38-41, 52)
    obj = SimpleNamespace()
    obj.self_ref = obj  # cycle
    obj.text = "ignored string"
    obj.none_val = None
    obj.responses = [
        {"item_id": "i1"},
        {"itemId": "i2"},
        {"diagnostic_item_id": "i3"},
        {"question_id": "i4"},
        {"questionId": "i5"},
    ]
    ids = extract_diagnostic_item_ids(obj)
    assert ids == ["i1", "i2", "i3", "i4", "i5"]

    # 2. validate_diagnostic_submission_payload branches (lines 70, 72-88)
    # Empty
    with pytest.raises(DiagnosticIntegrityError, match="contains no item_id values"):
        validate_diagnostic_submission_payload({}, require_items=True)

    # Duplicates (lines 80-81)
    dup_payload = {"items": [{"item_id": "i1"}, {"item_id": "i1"}]}
    with pytest.raises(DiagnosticIntegrityError, match="Duplicate diagnostic item responses are not allowed"):
        validate_diagnostic_submission_payload(dup_payload)

    # Unserved items (lines 84-86)
    unserved_payload = {"items": [{"item_id": "i1"}, {"item_id": "i2"}]}
    with pytest.raises(DiagnosticIntegrityError, match="includes unserved item IDs"):
        validate_diagnostic_submission_payload(unserved_payload, served_item_ids={"i1"})

    # Success (lines 88-92)
    valid_payload = {"items": [{"item_id": "i1"}]}
    res = validate_diagnostic_submission_payload(valid_payload, served_item_ids={"i1"})
    assert isinstance(res, DiagnosticSubmissionIntegrityResult)
    assert res.item_ids == ("i1",)

    # 3. _number error handling (lines 98-99, 101)
    with pytest.raises(DiagnosticIntegrityError, match="must be numeric"):
        validate_theta_update(old_theta="not_a_number", new_theta=0.0)

    with pytest.raises(DiagnosticIntegrityError, match="must be finite"):
        validate_theta_update(old_theta=0.0, new_theta=float("nan"))

    # 4. validate_theta_update out of bounds (line 116) and delta too large (line 118)
    with pytest.raises(DiagnosticIntegrityError, match="new_theta out of bounds"):
        validate_theta_update(old_theta=0.0, new_theta=5.0, min_theta=-4.0, max_theta=4.0)

    with pytest.raises(DiagnosticIntegrityError, match="theta update delta too large"):
        validate_theta_update(old_theta=-2.0, new_theta=2.0, max_abs_delta=1.5)

    # 5. validate_mastery_update_payload with None, dict, and object payload (lines 125, 128-129, 131-135)
    # None payload
    validate_mastery_update_payload(None)

    # Dict payload (lines 128-129)
    validate_mastery_update_payload({"old_theta": 0.0, "new_theta": 0.5})

    # Object payload (lines 131-135)
    obj_payload = SimpleNamespace(old_theta=0.5, new_theta=0.8)
    validate_mastery_update_payload(obj_payload)

    # Object with only one theta present (line 134->exit)
    validate_mastery_update_payload(SimpleNamespace(old_theta=1.0, new_theta=None))

    # 6. clamp_theta
    assert clamp_theta(10.0, min_theta=-4.0, max_theta=4.0) == 4.0
    assert clamp_theta(-10.0, min_theta=-4.0, max_theta=4.0) == -4.0
    assert clamp_theta(1.5, min_theta=-4.0, max_theta=4.0) == 1.5


@pytest.mark.asyncio
async def test_diagnostic_transactional_response_failures():
    mock_session = AsyncMock()
    mock_context = AsyncMock()
    mock_session.begin = MagicMock(return_value=mock_context)

    mock_resp_table = MagicMock()
    mock_resp_table.insert.return_value.values.return_value = "insert_resp"

    mock_mastery_table = MagicMock()
    mock_mastery_table.insert.return_value.values.return_value = "insert_mastery"

    mock_audit_table = MagicMock()
    mock_audit_table.insert.return_value.values.return_value = "insert_audit"

    service = TransactionalDiagnosticResponseService(
        session=mock_session,
        responses_table=mock_resp_table,
        mastery_table=mock_mastery_table,
        audit_events_table=mock_audit_table,
    )

    data_base = {
        "learner_id": "l-1",
        "session_id": "s-1",
        "item_id": "i-1",
        "caps_ref": "4.M.1",
        "is_correct": True,
        "theta_delta": 0.2,
    }

    # 1. fail_after_mastery (lines 92-93)
    data_fail_mastery = DiagnosticTransactionInput(
        **data_base,
        fail_after_mastery=True,
    )
    with pytest.raises(DiagnosticTransactionError, match="simulated failure after mastery update"):
        await service.submit_response(data_fail_mastery)

    # 2. fail_after_audit (lines 104-105)
    data_fail_audit = DiagnosticTransactionInput(
        **data_base,
        fail_after_audit=True,
    )
    with pytest.raises(DiagnosticTransactionError, match="simulated failure after diagnostic audit event insert"):
        await service.submit_response(data_fail_audit)
