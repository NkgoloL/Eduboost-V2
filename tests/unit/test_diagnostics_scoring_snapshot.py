from __future__ import annotations

from uuid import uuid4

import pytest

from app.modules.diagnostics.session_recovery_service import DiagnosticSessionSnapshot
from app.modules.diagnostics import diagnostic_session_service as service_module
from app.modules.diagnostics.diagnostic_session_service import DiagnosticSessionService
from app.services.diagnostic_scoring_snapshot import diagnostic_item_from_response, diagnostic_response_snapshot


class MemoryRecovery:
    def __init__(self, snap: DiagnosticSessionSnapshot) -> None:
        self.snap = snap

    async def read_session_snapshot(self, session_id: str):
        return self.snap

    async def write_session_snapshot(self, session_id: str, state):
        self.snap = state


class Item:
    def __init__(self, item_id: str, *, difficulty_b: float, caps_ref: str = "CAPS-A") -> None:
        self.item_id = item_id
        self.discrimination_a = 1.0
        self.difficulty_b = difficulty_b
        self.guessing_c = 0.25
        self.a_param = 1.0
        self.b_param = difficulty_b
        self.caps_ref = caps_ref
        self.misconception_tags = []


def test_diagnostic_response_snapshot_persists_item_parameters():
    item = Item("item-1", difficulty_b=-2.0)

    row = diagnostic_response_snapshot(item, item_id="item-1")

    assert row["scoring"]["item_id"] == "item-1"
    assert row["scoring"]["difficulty_b"] == -2.0
    assert row["scoring"]["b_param"] == -2.0


def test_diagnostic_item_from_response_rebuilds_historical_item():
    row = {"item_id": "item-1", "scoring": {"item_id": "item-1", "difficulty_b": -3.0, "b_param": -3.0}}

    rebuilt = diagnostic_item_from_response(row)

    assert rebuilt.item_id == "item-1"
    assert rebuilt.difficulty_b == -3.0
    assert rebuilt.b_param == -3.0


@pytest.mark.asyncio
async def test_submit_response_uses_per_response_item_parameters(monkeypatch):
    session_id = str(uuid4())
    snap = DiagnosticSessionSnapshot(session_id=session_id, learner_id="learner-1", caps_ref="CAPS-A")
    recovery = MemoryRecovery(snap)
    service = DiagnosticSessionService(recovery_service=recovery)
    easy = Item("easy", difficulty_b=-3.0)
    hard = Item("hard", difficulty_b=3.0)
    captured: list[list[float]] = []

    def fake_eap_update_3pl(responses, *, prior_mean=0.0):
        captured.append([float(getattr(item, "difficulty_b", getattr(item, "b_param", 0.0))) for item, _ in responses])
        return 0.0, 1.0

    monkeypatch.setattr(service_module, "eap_update_3pl", fake_eap_update_3pl)

    await service.submit_response(session_id, easy, correct=True)
    await service.submit_response(session_id, hard, correct=False)

    assert captured[-1] == [-3.0, 3.0]
    assert recovery.snap.responses[0]["scoring"]["difficulty_b"] == -3.0
    assert recovery.snap.responses[1]["scoring"]["difficulty_b"] == 3.0


def test_diagnostic_session_service_no_longer_scores_history_with_current_item():
    source = service_module.__loader__.get_source(service_module.__name__)  # type: ignore[union-attr]

    assert 'responses = [(item, bool(row["correct"])) for row in snap.responses]' not in source
    assert "diagnostic_item_from_response(row, fallback_item=item)" in source
