from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.services.diagnostic_data_integrity import DiagnosticIntegrityError
from app.services.diagnostic_route_integrity import (
    assert_caps_ref_matches_session,
    served_items_from_snapshot,
    validate_adaptive_diagnostic_response,
)


def test_served_items_from_snapshot_normalizes_session_and_caps():
    session_id = uuid4()
    item_id = uuid4()
    snapshot = SimpleNamespace(served_item_ids=[item_id], caps_ref="CAPS-1")

    assert served_items_from_snapshot(snapshot, session_id=session_id) == [
        {"item_id": item_id, "session_id": str(session_id), "caps_code": "CAPS-1"}
    ]


def test_caps_ref_mismatch_rejected():
    with pytest.raises(DiagnosticIntegrityError):
        assert_caps_ref_matches_session(submitted_caps_ref="CAPS-B", session_caps_ref="CAPS-A")


def test_adaptive_response_rejects_unserved_item():
    session_id = uuid4()
    served_item = uuid4()
    unserved_item = uuid4()
    snapshot = SimpleNamespace(served_item_ids=[served_item], caps_ref="CAPS-A")
    payload = SimpleNamespace(item_id=unserved_item, caps_ref="CAPS-A")

    with pytest.raises(DiagnosticIntegrityError):
        validate_adaptive_diagnostic_response(payload, snapshot=snapshot, session_id=session_id)


def test_adaptive_response_accepts_served_item():
    session_id = uuid4()
    served_item = uuid4()
    snapshot = SimpleNamespace(served_item_ids=[served_item], caps_ref="CAPS-A")
    payload = SimpleNamespace(item_id=served_item, caps_ref="CAPS-A")

    validate_adaptive_diagnostic_response(payload, snapshot=snapshot, session_id=session_id)


def test_adaptive_response_rejects_empty_served_history():
    session_id = uuid4()
    payload = SimpleNamespace(item_id=uuid4(), caps_ref="CAPS-A")
    snapshot = SimpleNamespace(served_item_ids=[], caps_ref="CAPS-A")

    with pytest.raises(DiagnosticIntegrityError):
        validate_adaptive_diagnostic_response(payload, snapshot=snapshot, session_id=session_id)
