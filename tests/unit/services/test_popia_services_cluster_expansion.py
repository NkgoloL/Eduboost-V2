from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.services.popia_dsr_service import DSRServiceError, POPIADSRService
from app.services.popia_erasure_safety import learner_has_legal_hold
from app.services.popia_transactional_lifecycle import _filter_kwargs


def test_popia_erasure_safety_missing_branches():
    from app.services.popia_erasure_safety import build_erasure_preflight_decision

    # 1. learner is None (line 49)
    assert learner_has_legal_hold(None) is False

    # 2. learner with truthy legal hold attribute (line 52)
    assert learner_has_legal_hold(SimpleNamespace(legal_hold=True)) is True
    assert learner_has_legal_hold(SimpleNamespace(retention_hold="active")) is True
    assert learner_has_legal_hold(SimpleNamespace(legal_hold=False)) is False

    # 3. build_erasure_preflight_decision and to_dict (lines 42, 72-90)
    decision = build_erasure_preflight_decision(
        learner=SimpleNamespace(id="l1"),
        requester_authorized=True,
        export_offered=True,
    )
    assert decision.all_checks_passed is True
    assert decision.requires_admin_review is False
    d = decision.to_dict()
    assert d["all_checks_passed"] is True

    # When learner has legal hold
    decision_hold = build_erasure_preflight_decision(
        learner=SimpleNamespace(legal_hold=True),
        requester_authorized=True,
        export_offered=False,
        export_waived=False,
    )
    assert decision_hold.all_checks_passed is False
    assert decision_hold.requires_admin_review is True


def test_popia_transactional_lifecycle_kwargs_filter():
    from unittest.mock import patch
    # Builtin/C functions where inspect.signature raises (lines 47-48)
    kwargs = {"a": 1, "b": 2}
    with patch("inspect.signature", side_effect=TypeError("no signature")):
        filtered = _filter_kwargs(lambda: None, kwargs)
        assert filtered == kwargs



@pytest.mark.asyncio
async def test_popia_dsr_service_complete():
    db = AsyncMock()
    service = POPIADSRService(db=db)

    # 1. initiate_erasure_request learner not found (lines 56-58)
    mock_res_empty = MagicMock()
    mock_res_empty.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_res_empty

    with pytest.raises(DSRServiceError, match="Learner learner-1 not found"):
        await service.initiate_erasure_request("learner-1", "user-1", "guardian")

    # 2. initiate_erasure_request success (lines 60-73)
    mock_learner = SimpleNamespace(id="learner-1")
    mock_res_learner = MagicMock()
    mock_res_learner.scalar_one_or_none.return_value = mock_learner
    db.execute.return_value = mock_res_learner

    req = await service.initiate_erasure_request(
        learner_id="learner-1",
        requester_id="user-1",
        requester_role="guardian",
        reason="Account closing",
    )
    assert req.learner_id == "learner-1"
    assert req.state == "requested"
    db.add.assert_called_once_with(req)
    db.flush.assert_awaited_once()

    # 3. execute_erasure_cascade request not found (lines 83-85)
    db.execute.return_value = mock_res_empty
    with pytest.raises(DSRServiceError, match="Erasure request req-1 not found"):
        await service.execute_erasure_cascade("req-1")

    # 4. execute_erasure_cascade success (lines 87-156)
    mock_req = SimpleNamespace(
        id="req-1",
        learner_id="learner-12345678",
        requester_id="user-1",
        state="requested",
        executed_at=None,
        execution_method=None,
        postflight_result=None,
    )
    mock_res_req = MagicMock()
    mock_res_req.scalar_one_or_none.return_value = mock_req
    db.execute.return_value = mock_res_req

    result = await service.execute_erasure_cascade("req-1", execution_method="soft_and_purge")
    assert result["erasure_request_id"] == "req-1"
    assert result["state"] == "executed"
    assert result["learner_id"] == "learner-12345678"
    assert mock_req.state == "executed"
    assert mock_req.postflight_result == {"status": "success", "tables_cascaded": 6}

    # Verify db.commit and audit log addition
    db.commit.assert_awaited_once()
    assert db.add.call_count >= 2  # from earlier req + audit_entry
