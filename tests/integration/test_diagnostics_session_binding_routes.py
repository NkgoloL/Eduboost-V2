from __future__ import annotations

from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException

import app.api_v2_routers.diagnostics as diagnostics

@pytest.fixture(autouse=True)
def integration_db():
    pass


class FakeLearnerRepository:
    def __init__(self, db):
        self.db = db

    async def get_by_id(self, learner_id):
        return SimpleNamespace(id=str(learner_id), guardian_id="guardian-1")


class FakeItemBankRepository:
    seen_caps_ref = None

    def __init__(self, db):
        self.db = db

    async def list_by_caps_ref(self, caps_ref, limit=200):
        type(self).seen_caps_ref = caps_ref
        return [SimpleNamespace(item_id=uuid4(), caps_ref=caps_ref, stem="Stem", options=["A", "B"])]

    async def get_item(self, item_id):
        return SimpleNamespace(item_id=item_id, caps_ref="CAPS-A", misconception_tags=[])


class FakeSessionService:
    snapshot = None
    submitted = None

    def __init__(self, *args, **kwargs):
        pass

    async def recover_session(self, session_id):
        return type(self).snapshot

    async def get_next_item(self, session_id, items):
        return items[0]

    async def submit_response(self, session_id, item, *, correct, response=None):
        type(self).submitted = (session_id, item, correct, response)
        return SimpleNamespace(
            session_id=str(session_id),
            theta=0.1,
            se_estimate=0.9,
            items_served=1,
            should_complete=False,
            termination_reason=None,
            gap_topics=[],
            misconception_tags=[],
        )


async def _noop_active_consent(db, current_user, learner_id):
    return None


def _noop_auth(*args, **kwargs):
    return None


@pytest.fixture(autouse=True)
def patch_route_dependencies(monkeypatch):
    # Support both the older direct-router dependency attributes and the newer
    # api_v2_deps diagnostic repository boundary.
    monkeypatch.setattr(diagnostics, "LearnerRepository", FakeLearnerRepository, raising=False)
    monkeypatch.setattr(diagnostics, "ItemBankRepository", FakeItemBankRepository, raising=False)
    monkeypatch.setattr(diagnostics, "DiagnosticSessionService", FakeSessionService, raising=False)
    monkeypatch.setattr(diagnostics, "require_active_consent_for_current_user", _noop_active_consent, raising=False)
    monkeypatch.setattr(diagnostics, "require_learner_read_for_current_user", _noop_auth, raising=False)
    monkeypatch.setattr(diagnostics, "require_learner_write_for_current_user", _noop_auth, raising=False)

    monkeypatch.setattr(diagnostics.diagnostic_repositories, "learner", lambda db: FakeLearnerRepository(db), raising=False)
    monkeypatch.setattr(diagnostics.diagnostic_repositories, "item_bank", lambda db: FakeItemBankRepository(db), raising=False)

    FakeItemBankRepository.seen_caps_ref = None
    FakeSessionService.submitted = None


@pytest.mark.asyncio
async def test_next_item_rejects_caps_ref_mismatch_no_skips():
    session_id = uuid4()
    FakeSessionService.snapshot = SimpleNamespace(
        session_id=str(session_id), learner_id="learner-1", caps_ref="CAPS-A", served_item_ids=[]
    )
    with pytest.raises(HTTPException) as exc:
        await diagnostics.diagnostic_next_item(session_id=session_id, caps_ref="CAPS-B", db=object(), current_user={"sub": "guardian-1"})
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_next_item_uses_recovered_session_caps_ref_no_skips():
    session_id = uuid4()
    FakeSessionService.snapshot = SimpleNamespace(
        session_id=str(session_id), learner_id="learner-1", caps_ref="CAPS-A", served_item_ids=[], theta=0.0
    )
    result = await diagnostics.diagnostic_next_item(session_id=session_id, caps_ref="CAPS-A", db=object(), current_user={"sub": "guardian-1"})
    assert result["completed"] is False
    assert FakeItemBankRepository.seen_caps_ref == "CAPS-A"


@pytest.mark.asyncio
async def test_respond_rejects_unserved_item_no_skips():
    session_id = uuid4()
    served_item = uuid4()
    unserved_item = uuid4()
    FakeSessionService.snapshot = SimpleNamespace(
        session_id=str(session_id), learner_id="learner-1", caps_ref="CAPS-A", served_item_ids=[str(served_item)]
    )
    body = diagnostics.DiagnosticSessionResponseRequest(item_id=unserved_item, correct=True, caps_ref="CAPS-A")
    with pytest.raises(HTTPException) as exc:
        await diagnostics.diagnostic_respond(session_id=session_id, body=body, db=object(), current_user={"sub": "guardian-1"})
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_respond_rejects_caps_ref_mismatch_no_skips():
    session_id = uuid4()
    served_item = uuid4()
    FakeSessionService.snapshot = SimpleNamespace(
        session_id=str(session_id), learner_id="learner-1", caps_ref="CAPS-A", served_item_ids=[str(served_item)]
    )
    body = diagnostics.DiagnosticSessionResponseRequest(item_id=served_item, correct=True, caps_ref="CAPS-B")
    with pytest.raises(HTTPException) as exc:
        await diagnostics.diagnostic_respond(session_id=session_id, body=body, db=object(), current_user={"sub": "guardian-1"})
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_respond_accepts_served_item_no_skips():
    session_id = uuid4()
    served_item = uuid4()
    FakeSessionService.snapshot = SimpleNamespace(
        session_id=str(session_id), learner_id="learner-1", caps_ref="CAPS-A", served_item_ids=[str(served_item)]
    )
    body = diagnostics.DiagnosticSessionResponseRequest(item_id=served_item, correct=True, caps_ref="CAPS-A")
    result = await diagnostics.diagnostic_respond(session_id=session_id, body=body, db=object(), current_user={"sub": "guardian-1"})
    assert result["session_id"] == str(session_id)
    assert isinstance(FakeSessionService.submitted[1].item_id, UUID)
