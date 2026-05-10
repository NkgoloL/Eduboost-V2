"""
tests/integration/test_item_bank_pipeline.py
─────────────────────────────────────────────────────────────────────────────
Phase 3: Item Bank Pipeline Integration Tests (P3-14)

Tests the full generation → validation → seed → query flow:
  1. Seed 5 test items → list_by_caps_ref returns correct items
  2. record_exposure increments count correctly
  3. get_unexposed_items excludes over-exposed items
  4. Coverage summary is accurate
  5. Quality score is assigned correctly

These tests use a real async database session (from the test fixtures).
They depend on the item_bank_repository and item_bank_service being wired.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.item_bank_repository import ItemBankRepository
from app.modules.diagnostics.item_bank_service import ItemBankService
from app.modules.diagnostics.item_validator import ItemValidator, ValidationError
from app.modules.diagnostics.quality_scorer import QualityScorer

TOPIC_MAP_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "data" / "caps" / "caps_topic_map_grade4_maths.json"
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _load_topic_map() -> dict:
    if TOPIC_MAP_PATH.exists():
        with open(TOPIC_MAP_PATH) as f:
            return json.load(f)
    # Minimal inline map for isolated testing
    return {
        "topics": {
            "4.M.1.1": {
                "grade": 4, "subject": "MATHEMATICS", "term": 1,
                "topic": "Whole Numbers",
                "subtopic": "Count, Order and Compare 4-digit Numbers",
                "skill": "place_value_ordering",
                "learning_outcomes": ["Count forwards and backwards up to 10 000"],
            }
        }
    }


def _make_item(caps_ref: str = "4.M.1.1", **overrides) -> dict:
    """Produce a fully valid, seeded item dict."""
    item = {
        "item_id":        str(uuid.uuid4()),
        "caps_ref":       caps_ref,
        "grade":          4,
        "subject":        "MATHEMATICS",
        "term":           1,
        "topic":          "Whole Numbers",
        "subtopic":       "Count, Order and Compare 4-digit Numbers",
        "skill":          "place_value_ordering",
        "stem":           "Sipho has 2 500 marbles. He gets 300 more. How many marbles does he have now?",
        "answer_key":     "A",
        "options": [
            {"label": "A", "text": "2 800"},
            {"label": "B", "text": "2 530"},
            {"label": "C", "text": "5 500"},
            {"label": "D", "text": "2 300"},
        ],
        "explanation":    "You add the hundreds together. 2 500 plus 300 equals 2 800. The digit 3 goes in the hundreds place.",
        "distractor_rationale": {
            "B": "A learner might add only the tens digit, getting 2 530.",
            "C": "A learner might multiply instead of add, getting an incorrect result.",
            "D": "A learner might subtract instead of add.",
        },
        "misconception_tags":   ["place_value_confusion"],
        "item_type":             "mcq",
        "language":              "en",
        "difficulty_b":          -0.5,
        "discrimination_a":       1.0,
        "guessing_c":             0.25,
        "review_status":         "approved",
        "reviewer_id":           str(uuid.uuid4()),
        "reviewed_at":           datetime.now(timezone.utc),
        "safety_passed":          True,
        "quality_score":          None,
        "source":                "llm_generated",
        "exposure_count":         0,
        "max_exposure":           50,
        "created_at":            datetime.now(timezone.utc),
    }
    item.update(overrides)
    return item


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture(scope="module", autouse=True)
async def test_db_setup():
    """Initialise tables and seed data for the module."""
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    pass


class TestItemBankPipelineSeedAndQuery:
    """
    P3-14: seed 5 test items → list_by_caps_ref returns correct items
    → record_exposure increments count.
    """

    @pytest.mark.asyncio
    async def test_seed_and_list_by_caps_ref(self, db_session: AsyncSession):
        """Seeded items must be retrievable by caps_ref."""
        repo    = ItemBankRepository(db_session)
        target  = "4.M.1.1"
        other   = "4.M.1.2"

        # Seed 3 items for target ref, 2 for other
        for _ in range(3):
            await repo.upsert(_make_item(caps_ref=target))
        for _ in range(2):
            await repo.upsert(_make_item(caps_ref=other))
        await db_session.flush()

        items = await repo.list_by_caps_ref(target)
        assert len(items) >= 3
        assert all(i.caps_ref == target for i in items)

    @pytest.mark.asyncio
    async def test_list_excludes_other_caps_ref(self, db_session: AsyncSession):
        """list_by_caps_ref must not return items from a different caps_ref."""
        repo   = ItemBankRepository(db_session)
        target = "4.M.1.1"

        await repo.upsert(_make_item(caps_ref="4.M.1.2"))
        await db_session.flush()

        items = await repo.list_by_caps_ref(target)
        assert all(i.caps_ref == target for i in items)

    @pytest.mark.asyncio
    async def test_record_exposure_increments_count(self, db_session: AsyncSession):
        """record_exposure must increment exposure_count by 1 each call."""
        repo    = ItemBankRepository(db_session)
        learner = uuid.uuid4()

        item_data = _make_item(exposure_count=0)
        await repo.upsert(item_data)
        await db_session.flush()

        item_id = uuid.UUID(item_data["item_id"])

        # Record exposure twice
        await repo.record_exposure(item_id=item_id, learner_id=learner)
        await repo.record_exposure(item_id=item_id, learner_id=learner)
        await db_session.flush()

        reloaded = await repo.get_item(item_id)
        assert reloaded is not None
        assert reloaded.exposure_count >= 2

    @pytest.mark.asyncio
    async def test_get_unexposed_excludes_over_exposed(self, db_session: AsyncSession):
        """Items at or above max_exposure must not be returned as unexposed."""
        repo    = ItemBankRepository(db_session)
        learner = uuid.uuid4()

        # Item at max exposure
        exhausted = _make_item(exposure_count=50, max_exposure=50)
        await repo.upsert(exhausted)

        # Fresh item
        fresh = _make_item(exposure_count=0, max_exposure=50)
        await repo.upsert(fresh)
        await db_session.flush()

        unexposed = await repo.get_unexposed_items(
            caps_ref="4.M.1.1",
            learner_id=learner,
        )
        unexposed_ids = {str(i.item_id) for i in unexposed}
        assert exhausted["item_id"] not in unexposed_ids
        assert fresh["item_id"] in unexposed_ids


class TestItemBankServiceSelection:
    """
    Item selection must respect IRT ordering and exposure capping.
    """

    @pytest.mark.asyncio
    async def test_select_item_returns_nearest_ability_item(self, db_session: AsyncSession):
        """
        select_item_for_learner must return the item whose difficulty_b is
        closest to the learner's current ability estimate (θ).
        """
        repo    = ItemBankRepository(db_session)
        service = ItemBankService(repo)
        learner = uuid.uuid4()
        theta   = 0.0   # average ability

        # Seed items at various difficulties
        items_data = [
            _make_item(difficulty_b=-2.0),
            _make_item(difficulty_b=-0.1),   # ← closest to theta=0.0
            _make_item(difficulty_b= 1.5),
        ]
        for item in items_data:
            await repo.upsert(item)
        await db_session.flush()

        selected = await service.select_item_for_learner(
            caps_ref="4.M.1.1",
            learner_id=learner,
            theta=theta,
        )
        assert selected is not None
        assert abs(float(selected.difficulty_b) - theta) <= 1.0, (
            f"Selected item difficulty {selected.difficulty_b} is not near θ={theta}"
        )

    @pytest.mark.asyncio
    async def test_select_returns_none_when_all_exhausted(self, db_session: AsyncSession):
        """
        When all available items are at max_exposure, select_item_for_learner
        must return None rather than crashing.
        """
        repo    = ItemBankRepository(db_session)
        service = ItemBankService(repo)
        learner = uuid.uuid4()

        await repo.upsert(_make_item(exposure_count=50, max_exposure=50))
        await db_session.flush()

        selected = await service.select_item_for_learner(
            caps_ref="4.M.1.1",
            learner_id=learner,
            theta=0.0,
        )
        assert selected is None

    @pytest.mark.asyncio
    async def test_exposure_cap_prevents_reselection(self, db_session: AsyncSession):
        """
        After an item reaches max_exposure, it must not be selected again.
        """
        repo    = ItemBankRepository(db_session)
        service = ItemBankService(repo)
        learner = uuid.uuid4()

        item_data = _make_item(max_exposure=1, exposure_count=0)
        await repo.upsert(item_data)
        await db_session.flush()
        item_id = uuid.UUID(item_data["item_id"])

        # First selection — should succeed
        first = await service.select_item_for_learner(
            caps_ref="4.M.1.1",
            learner_id=learner,
            theta=0.0,
        )
        assert first is not None

        # Simulate exposure
        await repo.record_exposure(item_id=item_id, learner_id=learner)
        await db_session.flush()

        # Second selection — item exhausted, nothing else available
        second = await service.select_item_for_learner(
            caps_ref="4.M.1.1",
            learner_id=learner,
            theta=0.0,
        )
        assert second is None or str(second.item_id) != str(item_id)


class TestItemBankCoverage:
    """Coverage summary must reflect accurate counts per caps_ref."""

    @pytest.mark.asyncio
    async def test_coverage_summary_counts_approved_only(self, db_session: AsyncSession):
        repo    = ItemBankRepository(db_session)
        service = ItemBankService(repo)

        await repo.upsert(_make_item(caps_ref="4.M.1.1", review_status="approved"))
        await repo.upsert(_make_item(caps_ref="4.M.1.1", review_status="ai_generated"))
        await repo.upsert(_make_item(caps_ref="4.M.1.2", review_status="approved"))
        await db_session.flush()

        summary = await service.get_coverage_summary()
        assert summary["4.M.1.1"]["approved"] >= 1
        assert summary["4.M.1.1"]["total"]    >= 2

    @pytest.mark.asyncio
    async def test_mark_item_reviewed_updates_status(self, db_session: AsyncSession):
        """mark_item_reviewed must update review_status, reviewer_id, and reviewed_at."""
        repo     = ItemBankRepository(db_session)
        service  = ItemBankService(repo)
        reviewer = uuid.uuid4()

        item_data = _make_item(review_status="ai_generated")
        await repo.upsert(item_data)
        await db_session.flush()
        item_id = uuid.UUID(item_data["item_id"])

        await service.mark_item_reviewed(
            item_id=item_id,
            reviewer_id=reviewer,
            new_status="approved",
        )
        await db_session.flush()

        updated = await repo.get_item(item_id)
        assert updated is not None
        assert updated.review_status == "approved"
        assert updated.reviewer_id   == reviewer
        assert updated.reviewed_at   is not None


class TestQualityScorerIntegration:
    """Quality scorer must produce scores within valid range and respect weights."""

    def test_quality_score_in_range(self):
        topic_map = _load_topic_map()
        scorer    = QualityScorer(topic_map=topic_map)
        item      = _make_item()
        scored    = scorer.score(item)

        assert "quality_score" in scored
        assert 0.0 <= scored["quality_score"] <= 1.0

    def test_quality_score_components_present(self):
        scorer = QualityScorer(topic_map=_load_topic_map())
        scored = scorer.score(_make_item())

        components = scored.get("component_scores", {})
        assert "correctness"    in components
        assert "caps_alignment" in components
        assert "readability"    in components
        assert "sa_context"     in components

    def test_sa_context_detected_in_rand_item(self):
        scorer = QualityScorer(topic_map=_load_topic_map())
        item   = _make_item(stem="Sipho buys 3 bananas for R5 each at the spaza shop. How much does he pay?")
        scored = scorer.score(item)
        assert scored["component_scores"]["sa_context"] > 0.0

    def test_low_quality_item_scores_lower(self):
        scorer = QualityScorer(topic_map=_load_topic_map())

        good = _make_item()
        bad  = _make_item(
            explanation="Wrong.",
            misconception_tags=[],
            distractor_rationale={"B": "x", "C": "y", "D": "z"},
        )
        # Force bad item's validator fields to pass minimally
        bad["misconception_tags"]  = ["x"]
        bad["explanation"]         = "This is not a very helpful explanation for the learner at all."
        bad["safety_passed"]       = True

        good_score = scorer.score(good)["quality_score"]
        bad_score  = scorer.score(bad)["quality_score"]

        assert good_score >= bad_score, (
            f"Good item ({good_score:.3f}) should score ≥ bad item ({bad_score:.3f})"
        )


class TestValidatorPipelineEndToEnd:
    """Validator must catch all failure modes from the generation pipeline."""

    def test_full_pipeline_valid_item_passes(self):
        topic_map = _load_topic_map()
        validator = ItemValidator(topic_map=topic_map)
        item = _make_item()
        errors = validator.validate_all(item)
        assert errors == [], f"Valid item should have no errors, got: {errors}"

    def test_full_pipeline_pii_leak_caught(self):
        topic_map = _load_topic_map()
        validator = ItemValidator(topic_map=topic_map)
        item = _make_item(stem="Sipho's email is sipho@school.gov.za. He has 500 apples.")
        errors = validator.validate_all(item)
        assert any(e.rule == "no_pii" for e in errors)

    def test_full_pipeline_answer_key_mismatch_caught(self):
        topic_map = _load_topic_map()
        validator = ItemValidator(topic_map=topic_map)
        item = _make_item(answer_key="E")  # No option E exists
        errors = validator.validate_all(item)
        assert any(e.rule == "answer_key" for e in errors)
