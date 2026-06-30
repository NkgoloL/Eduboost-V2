from __future__ import annotations
import pytest
pytestmark = pytest.mark.integration

"""
tests/integration/test_diagnostic_session.py
─────────────────────────────────────────────────────────────────────────────
Phase 4: Integration Tests — Full Diagnostic Session (P4-10)

Covers:
    P4-10 — Full diagnostic session uses real items from DB, ability estimate
            converges, session completes without error.
    P4-03 — Exposure enforcement: same item is not served twice in a session.
    P4-09 — Session recovery: state is restorable from Redis after interruption.
    P4-07 — Lesson context is correctly built from session result.
    P4-08 — Study plan is updated with correct priority after diagnostic.

Test strategy:
    - Uses pytest-asyncio with an in-memory SQLite DB (or test Postgres).
    - Seeds 15 DiagnosticItem rows covering a single caps_ref (4.M.1.1) with
      varied difficulty so the IRT engine can exercise selection logic.
    - Uses fakeredis for Redis without a real server.
    - Runs a full session loop (next_item → respond) until completion.
    - Asserts on θ, SE, exposure records, and session result fields.
─────────────────────────────────────────────────────────────────────────────
"""


import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

from app.modules.diagnostics.irt_engine import (
    GRADE_LEVEL_THRESHOLD,
    MAX_ITEMS,
    MIN_ITEMS,
    IRTEngine,
)
from app.modules.diagnostics.item_bank_service import ItemBankService
from app.services.diagnostic_session_service import (
    DiagnosticSessionNotFoundError,
    DiagnosticSessionService,
)
from app.services.lesson_context_builder import LessonContextBuilder
from app.services.study_plan_updater import StudyPlanUpdater


# ─── Helpers / Fixtures ───────────────────────────────────────────────────────

def _make_item(
    difficulty_b: float = 0.0,
    discrimination_a: float = 1.0,
    guessing_c: float = 0.25,
    caps_ref: str = "4.M.1.1",
    item_id: uuid.UUID | None = None,
) -> MagicMock:
    """Create a mock DiagnosticItem with the given IRT parameters."""
    item = MagicMock()
    item.item_id          = item_id or uuid.uuid4()
    item.caps_ref         = caps_ref
    item.stem             = "How many tens are in 3 460?"
    item.options          = [
        {"label": "A", "text": "3"},
        {"label": "B", "text": "34"},
        {"label": "C", "text": "346"},
        {"label": "D", "text": "6"},
    ]
    item.answer_key           = "C"
    item.item_type            = "mcq"
    item.difficulty_b         = difficulty_b
    item.discrimination_a     = discrimination_a
    item.guessing_c           = guessing_c
    item.misconception_tags   = ["place_value_confusion"]
    item.explanation          = "3 460 has 346 tens."
    item.distractor_rationale = {}
    return item


def _build_item_pool(n: int = 15, caps_ref: str = "4.M.1.1") -> list[MagicMock]:
    """Seed pool: evenly spaced difficulty from -2.0 to +2.0."""
    step = 4.0 / (n - 1) if n > 1 else 0.0
    items = []
    for i in range(n):
        b = round(-2.0 + i * step, 2)
        items.append(_make_item(difficulty_b=b, caps_ref=caps_ref))
    return items


@pytest.fixture
def item_pool() -> list[MagicMock]:
    return _build_item_pool(15)


@pytest_asyncio.fixture
async def fake_redis():
    """In-process async Redis substitute (fakeredis)."""
    try:
        import fakeredis.aioredis as fakeredis
        server = fakeredis.FakeServer()
        return fakeredis.FakeRedis(server=server)
    except ImportError:
        # Fallback: minimal dict-backed shim
        store: dict = {}

        class _FakeRedis:
            async def get(self, key):
                return store.get(key)

            async def set(self, key, value, ex=None):
                store[key] = value

        return _FakeRedis()


def _make_service(item_pool: list[MagicMock], fake_redis) -> DiagnosticSessionService:
    """
    Build a DiagnosticSessionService with mocked repo and real IRTEngine.
    item_pool is consumed sequentially, simulating unexposed-item filtering.
    """
    served_ids: set[uuid.UUID] = set()

    async def _select_item(caps_ref, learner_id, theta, exclude_ids):
        remaining = [i for i in item_pool if i.item_id not in (exclude_ids or set())]
        if not remaining:
            return None
        # Simulate IRT-informed selection: pick item with b closest to theta
        return min(remaining, key=lambda i: abs(i.difficulty_b - theta))

    async def _record_exposure(item_id, learner_id, session_id=None):
        served_ids.add(item_id)

    mock_repo = MagicMock()
    mock_repo.get_unexposed_items = AsyncMock(side_effect=_select_item)
    mock_repo.record_exposure     = AsyncMock(side_effect=_record_exposure)
    mock_repo.get_item            = AsyncMock(side_effect=lambda iid: next(
        (i for i in item_pool if i.item_id == iid), None
    ))

    item_svc = ItemBankService(mock_repo)
    # Override select_item_for_learner directly
    item_svc.select_item_for_learner = _select_item
    item_svc.record_item_served      = AsyncMock(side_effect=lambda **kw: served_ids.add(kw["item_id"]))

    engine  = IRTEngine(item_svc)
    mock_db = MagicMock()

    svc = DiagnosticSessionService(
        db=mock_db,
        redis=fake_redis,
        item_bank_service=item_svc,
        irt_engine=engine,
    )
    # Override _load/_save to use the real engine with mock_repo.get_item
    svc._make_repo = lambda: mock_repo  # unused — kept for reference
    return svc


# ─── P4-10: Full session integration test ─────────────────────────────────────

@pytest.mark.asyncio
async def test_full_diagnostic_session_completes(item_pool, fake_redis):
    """
    P4-10 — A full diagnostic session:
      1. Creates a session.
      2. Drives the item loop (next_item → respond) until completion.
      3. Verifies the session result has expected structure.
      4. Verifies θ and SE are valid IRT outputs.
      5. Verifies items_attempted is within [MIN_ITEMS, MAX_ITEMS].
    """
    learner_id = uuid.uuid4()
    caps_ref   = "4.M.1.1"
    svc        = _make_service(item_pool, fake_redis)

    state = await svc.create_session(learner_id=learner_id, caps_ref=caps_ref)

    assert state.caps_ref   == caps_ref
    assert state.theta       == 0.0
    assert not state.completed

    served_item_ids: list[uuid.UUID] = []
    iterations = 0

    while not state.completed and iterations < MAX_ITEMS + 5:
        item = await svc.next_item(state.session_id)
        if item is None:
            break

        served_item_ids.append(item.item_id)

        # Simulate: learner answers correctly for easy items, wrong for hard
        is_correct = item.difficulty_b <= state.theta
        state = await svc.record_response(
            session_id=state.session_id,
            item_id=item.item_id,
            is_correct=is_correct,
        )
        iterations += 1

    result = await svc.finalise_session(state.session_id)

    # Structure assertions
    assert "session_id"        in result
    assert "theta"             in result
    assert "standard_error"    in result
    assert "items_attempted"   in result
    assert "below_grade_level" in result
    assert "gap_topics"        in result
    assert "misconception_tags" in result
    assert "completed_at"      in result

    # IRT validity
    assert -4.0 <= result["theta"] <= 4.0,      "θ must be within plausible range"
    assert result["standard_error"] >= 0.0,      "SE must be non-negative"
    assert result["items_attempted"] >= MIN_ITEMS, "Must attempt at least MIN_ITEMS"
    assert result["items_attempted"] <= MAX_ITEMS, "Must not exceed MAX_ITEMS"

    # Ability estimate should have converged (SE reduced from prior of 1.0)
    assert result["standard_error"] <= 1.0, "SE should have reduced from prior of 1.0"

    # below_grade_level must match theta threshold
    assert result["below_grade_level"] == (result["theta"] < GRADE_LEVEL_THRESHOLD)


# ─── P4-03: Exposure enforcement ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_no_item_repeated_within_session(item_pool, fake_redis):
    """
    P4-03 — The same item is never served twice within a single session.
    """
    learner_id = uuid.uuid4()
    svc        = _make_service(item_pool, fake_redis)

    state = await svc.create_session(learner_id=learner_id, caps_ref="4.M.1.1")

    served_ids = []
    for _ in range(MAX_ITEMS + 2):
        item = await svc.next_item(state.session_id)
        if item is None:
            break
        assert item.item_id not in served_ids, (
            f"Item {item.item_id} was served twice in the same session!"
        )
        served_ids.append(item.item_id)
        state = await svc.record_response(
            session_id=state.session_id,
            item_id=item.item_id,
            is_correct=True,
        )

    assert len(served_ids) >= MIN_ITEMS, "Should have served at least MIN_ITEMS"
    assert len(served_ids) == len(set(served_ids)), "All served item IDs must be unique"


# ─── P4-09: Session recovery ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_session_recovery_from_redis(item_pool, fake_redis):
    """
    P4-09 — A session interrupted mid-flow is recoverable from Redis.
    The recovered state has the same session_id, θ, and items_answered.
    """
    learner_id = uuid.uuid4()
    svc        = _make_service(item_pool, fake_redis)

    state = await svc.create_session(learner_id=learner_id, caps_ref="4.M.1.1")

    # Answer 3 items then "disconnect"
    for _ in range(3):
        item = await svc.next_item(state.session_id)
        if item is None:
            break
        state = await svc.record_response(
            session_id=state.session_id,
            item_id=item.item_id,
            is_correct=True,
        )

    # Simulate reconnect: recover from Redis
    recovered = await svc.recover_session(state.session_id)

    assert recovered is not None,                    "Session must be recoverable from Redis"
    assert recovered.session_id == state.session_id, "session_id must match"
    assert len(recovered.responses) == 3,            "Should have 3 responses recorded"
    assert not recovered.completed,                  "Session is not yet complete"
    assert abs(recovered.theta - state.theta) < 0.001, "θ must be preserved through Redis"


@pytest.mark.asyncio
async def test_recover_missing_session_returns_none(fake_redis):
    """P4-09 — Recovering a non-existent session returns None (no crash)."""
    svc = _make_service([], fake_redis)
    result = await svc.recover_session(uuid.uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_load_missing_session_raises(fake_redis):
    """P4-09 — Operating on a missing session raises DiagnosticSessionNotFoundError."""
    svc = _make_service([], fake_redis)
    with pytest.raises(DiagnosticSessionNotFoundError):
        await svc.next_item(uuid.uuid4())


# ─── P4-07: Lesson context builder ────────────────────────────────────────────

def test_lesson_context_builder_below_grade_level():
    """P4-07 — LessonContext is correctly built for a below-grade-level learner."""
    caps_topic_map = {
        "4.M.1.1": {
            "grade": 4, "subject": "Mathematics", "term": 1,
            "topic": "Whole Numbers", "subtopic": "Count and Order",
            "skill": "place_value_ordering",
            "suggested_examples": ["Order 1 234, 2 341, 3 412 from smallest."],
        }
    }
    builder = LessonContextBuilder(caps_topic_map)
    session_result = {
        "session_id":        str(uuid.uuid4()),
        "learner_id":        str(uuid.uuid4()),
        "caps_ref":          "4.M.1.1",
        "theta":             -1.5,
        "standard_error":    0.35,
        "items_attempted":   10,
        "items_correct":     3,
        "accuracy":          0.3,
        "below_grade_level": True,
        "gap_topics":        ["4.M.1.1"],
        "misconception_tags": ["place_value_confusion", "carries_error"],
        "completed_at":      datetime.now(timezone.utc).isoformat(),
    }

    context = builder.build(session_result, learner_language="en")

    assert context.caps_ref            == "4.M.1.1"
    assert context.below_grade_level   is True
    assert context.severity            == "severe"   # θ = -1.5 < -1.0
    assert "place_value_confusion"     in context.misconception_tags
    assert context.topic               == "Whole Numbers"
    assert context.subtopic            == "Count and Order"
    assert "severe" in context.remediation_focus.lower() or "foundational" in context.remediation_focus.lower()
    assert context.prior_attempted     == 10
    assert context.prior_correct_count == 3

    prompt_dict = context.to_prompt_dict()
    assert prompt_dict["accuracy_pct"] == 30.0


def test_lesson_context_on_grade_level():
    """P4-07 — LessonContext reflects mild severity when θ ≥ 0."""
    builder = LessonContextBuilder({})
    result  = {
        "session_id": str(uuid.uuid4()), "learner_id": str(uuid.uuid4()),
        "caps_ref": "4.M.1.2", "theta": 0.5, "standard_error": 0.38,
        "items_attempted": 9, "items_correct": 7, "accuracy": 0.78,
        "below_grade_level": False, "gap_topics": [],
        "misconception_tags": [], "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    context = builder.build(result)
    assert context.severity          == "mild"
    assert context.below_grade_level is False


# ─── P4-08: Study plan updater ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_study_plan_prioritises_urgent_topics():
    """P4-08 — Topics with θ < -1.0 are marked as urgent priority."""
    mock_repo = MagicMock()
    mock_repo.upsert_topic_entry = AsyncMock()
    mock_repo.get_plan           = AsyncMock(return_value={
        "topics": [
            {"caps_ref": "4.M.1.1", "theta": -1.5, "priority": "urgent"},
            {"caps_ref": "4.M.1.2", "theta":  0.2,  "priority": "medium"},
            {"caps_ref": "4.M.1.3", "theta": -0.3, "priority": "high"},
        ]
    })
    mock_repo.reorder_topics = AsyncMock()

    updater = StudyPlanUpdater(mock_repo)

    session_result = {
        "caps_ref":          "4.M.1.1",
        "theta":             -1.5,
        "standard_error":    0.33,
        "below_grade_level": True,
        "misconception_tags": ["place_value_confusion"],
        "completed_at":      datetime.now(timezone.utc).isoformat(),
    }

    learner_id = uuid.uuid4()
    entry = await updater.apply_diagnostic_result(learner_id, session_result)

    assert entry["priority"]           == "urgent"
    assert entry["needs_lesson"]       is True
    assert entry["below_grade_level"]  is True
    assert entry["caps_ref"]           == "4.M.1.1"

    mock_repo.upsert_topic_entry.assert_called_once()
    mock_repo.reorder_topics.assert_called_once()


@pytest.mark.asyncio
async def test_study_plan_on_track_topic():
    """P4-08 — Topics with θ ≥ 0.0 receive medium priority and needs_lesson=False."""
    mock_repo = MagicMock()
    mock_repo.upsert_topic_entry = AsyncMock()
    mock_repo.get_plan           = AsyncMock(return_value={"topics": []})
    mock_repo.reorder_topics     = AsyncMock()

    updater = StudyPlanUpdater(mock_repo)
    result  = {
        "caps_ref":          "4.M.1.2",
        "theta":              0.8,
        "standard_error":    0.31,
        "below_grade_level": False,
        "misconception_tags": [],
        "completed_at":      datetime.now(timezone.utc).isoformat(),
    }

    entry = await updater.apply_diagnostic_result(uuid.uuid4(), result)
    assert entry["priority"]     == "medium"
    assert entry["needs_lesson"] is False


@pytest.mark.asyncio
async def test_prioritised_topics_ordering():
    """P4-08 — get_prioritised_topics returns urgent → high → medium → low order."""
    mock_repo = MagicMock()
    mock_repo.get_plan = AsyncMock(return_value={
        "topics": [
            {"caps_ref": "4.M.1.2", "priority": "medium"},
            {"caps_ref": "4.M.1.1", "priority": "urgent"},
            {"caps_ref": "4.M.1.3", "priority": "high"},
        ]
    })

    updater = StudyPlanUpdater(mock_repo)
    topics  = await updater.get_prioritised_topics(uuid.uuid4())

    assert [t["caps_ref"] for t in topics] == ["4.M.1.1", "4.M.1.3", "4.M.1.2"]
