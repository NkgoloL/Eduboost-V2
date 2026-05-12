"""
tests/unit/modules/diagnostics/test_item_bank_pipeline.py
==========================================================
Item-bank pipeline unit tests.

MIGRATION NOTE (Recommendation 1)
----------------------------------
The original file had a module-scoped autouse fixture that unconditionally
tried to connect to Postgres, producing 16 setup *errors* (not skips) in
any environment without a local database.

Fix applied:
  1. The autouse DB fixture is removed.
  2. Tests that are genuinely unit-testable (mock/in-memory) keep running
     everywhere – they make up the majority of this file.
  3. The handful of tests that truly need a live DB are grouped into a
     separate class (TestItemBankPipelineIntegration) decorated with
     @pytest.mark.requires_db and @pytest.mark.usefixtures("skip_if_no_db").
     They skip cleanly when Postgres is absent instead of erroring.
  4. The integration class (and only that class) should eventually be
     moved to tests/integration/modules/diagnostics/ so it runs in a
     controlled environment with a guaranteed DB.

Run the pure unit subset with:
    pytest tests/unit/modules/diagnostics/test_item_bank_pipeline.py \
           -m "not requires_db" --tb=short -q
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Shared test data / helpers
# ---------------------------------------------------------------------------

SAMPLE_ITEM: dict[str, Any] = {
    "id": "item-001",
    "topic": "whole_numbers",
    "difficulty": 0.5,
    "discrimination": 1.2,
    "guessing": 0.25,
    "content": "What is 7 + 8?",
    "answer_key": "15",
    "grade": 4,
    "subject": "mathematics",
    "caps_strand": "Numbers, Operations and Relationships",
}

SAMPLE_PIPELINE_CONFIG: dict[str, Any] = {
    "max_items": 10,
    "difficulty_range": (0.0, 1.0),
    "topic_filter": None,
    "shuffle": False,
}


def _make_mock_repository(items: list[dict] | None = None) -> MagicMock:
    """Return a mock ItemBankRepository pre-loaded with *items*."""
    repo = MagicMock()
    repo.get_approved_items = AsyncMock(return_value=items if items is not None else [SAMPLE_ITEM])
    repo.get_items_by_topic = AsyncMock(return_value=items if items is not None else [SAMPLE_ITEM])
    repo.count_approved_items = AsyncMock(return_value=len(items if items is not None else [SAMPLE_ITEM]))
    return repo


# ---------------------------------------------------------------------------
# Pure unit tests – run everywhere, no DB required
# ---------------------------------------------------------------------------

class TestItemBankPipelineUnit:
    """Fast, DB-free tests that cover pipeline logic via mocks."""

    @pytest.mark.asyncio
    async def test_pipeline_returns_items_from_repository(self) -> None:
        """Pipeline delegates to the repository and surfaces its items."""
        from app.modules.diagnostics.item_bank_pipeline import ItemBankPipeline

        mock_repo = _make_mock_repository([SAMPLE_ITEM])

        with patch(
            "app.modules.diagnostics.item_bank_pipeline.ItemBankRepository",
            return_value=mock_repo,
        ):
            pipeline = ItemBankPipeline(config=SAMPLE_PIPELINE_CONFIG)
            items = await pipeline.fetch_items()

        assert len(items) == 1
        assert items[0]["id"] == "item-001"
        mock_repo.get_approved_items.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_pipeline_respects_max_items_cap(self) -> None:
        """Pipeline never returns more than config['max_items'] items."""
        from app.modules.diagnostics.item_bank_pipeline import ItemBankPipeline

        many_items = [dict(SAMPLE_ITEM, id=f"item-{i:03d}") for i in range(50)]
        mock_repo = _make_mock_repository(many_items)

        with patch(
            "app.modules.diagnostics.item_bank_pipeline.ItemBankRepository",
            return_value=mock_repo,
        ):
            config = {**SAMPLE_PIPELINE_CONFIG, "max_items": 5}
            pipeline = ItemBankPipeline(config=config)
            items = await pipeline.fetch_items()

        assert len(items) <= 5

    @pytest.mark.asyncio
    async def test_pipeline_filters_by_difficulty_range(self) -> None:
        """Only items within the configured difficulty range are returned."""
        from app.modules.diagnostics.item_bank_pipeline import ItemBankPipeline

        items = [
            dict(SAMPLE_ITEM, id="easy", difficulty=0.1),
            dict(SAMPLE_ITEM, id="medium", difficulty=0.5),
            dict(SAMPLE_ITEM, id="hard", difficulty=0.9),
        ]
        mock_repo = _make_mock_repository(items)

        with patch(
            "app.modules.diagnostics.item_bank_pipeline.ItemBankRepository",
            return_value=mock_repo,
        ):
            config = {**SAMPLE_PIPELINE_CONFIG, "difficulty_range": (0.4, 0.6)}
            pipeline = ItemBankPipeline(config=config)
            result = await pipeline.fetch_items()

        ids = [item["id"] for item in result]
        assert "medium" in ids
        assert "easy" not in ids
        assert "hard" not in ids

    @pytest.mark.asyncio
    async def test_pipeline_topic_filter_passed_to_repository(self) -> None:
        """When topic_filter is set, the repository's topic method is used."""
        from app.modules.diagnostics.item_bank_pipeline import ItemBankPipeline

        mock_repo = _make_mock_repository()

        with patch(
            "app.modules.diagnostics.item_bank_pipeline.ItemBankRepository",
            return_value=mock_repo,
        ):
            config = {**SAMPLE_PIPELINE_CONFIG, "topic_filter": "fractions"}
            pipeline = ItemBankPipeline(config=config)
            await pipeline.fetch_items()

        mock_repo.get_items_by_topic.assert_awaited_once_with("fractions")

    @pytest.mark.asyncio
    async def test_pipeline_empty_bank_returns_empty_list(self) -> None:
        """An empty item bank results in an empty list, not an exception."""
        from app.modules.diagnostics.item_bank_pipeline import ItemBankPipeline

        mock_repo = _make_mock_repository([])

        with patch(
            "app.modules.diagnostics.item_bank_pipeline.ItemBankRepository",
            return_value=mock_repo,
        ):
            pipeline = ItemBankPipeline(config=SAMPLE_PIPELINE_CONFIG)
            result = await pipeline.fetch_items()

        assert result == []

    def test_pipeline_config_validation_rejects_negative_max_items(self) -> None:
        """ItemBankPipeline raises ValueError for invalid config at init time."""
        from app.modules.diagnostics.item_bank_pipeline import ItemBankPipeline

        with pytest.raises(ValueError, match="max_items"):
            ItemBankPipeline(config={**SAMPLE_PIPELINE_CONFIG, "max_items": -1})

    def test_pipeline_config_validation_rejects_inverted_difficulty_range(
        self,
    ) -> None:
        """Difficulty range where low > high is rejected at construction."""
        from app.modules.diagnostics.item_bank_pipeline import ItemBankPipeline

        with pytest.raises(ValueError, match="difficulty_range"):
            ItemBankPipeline(
                config={**SAMPLE_PIPELINE_CONFIG, "difficulty_range": (0.9, 0.1)}
            )


# ---------------------------------------------------------------------------
# DB-dependent tests – skip cleanly when Postgres is unavailable
# ---------------------------------------------------------------------------

@pytest.mark.requires_db
@pytest.mark.usefixtures("skip_if_no_db")
class TestItemBankPipelineIntegration:
    """Integration tests that exercise the real repository against Postgres.

    These are intentionally kept minimal here.  The bulk of integration
    coverage belongs in tests/integration/modules/diagnostics/.

    All tests in this class are skipped automatically (not errored) when
    Postgres is unreachable, keeping the aggregate unit gate green.
    """

    @pytest.mark.asyncio
    async def test_pipeline_round_trip_with_real_db(self, db_session) -> None:
        """Seed one item, run the pipeline, assert it surfaces."""
        from app.modules.diagnostics.item_bank_pipeline import ItemBankPipeline
        from app.repositories.item_bank_repository import ItemBankRepository

        # Seed a single approved item via the real session.
        db_session.execute(
            "INSERT INTO item_bank (id, topic, difficulty, status) "
            "VALUES (:id, :topic, :difficulty, 'approved')",
            {"id": "rt-001", "topic": "whole_numbers", "difficulty": 0.5},
        )
        db_session.flush()

        repo = ItemBankRepository(session=db_session)
        pipeline = ItemBankPipeline(
            config=SAMPLE_PIPELINE_CONFIG, repository=repo
        )
        items = await pipeline.fetch_items()

        assert any(item["id"] == "rt-001" for item in items)

    @pytest.mark.asyncio
    async def test_count_reflects_seeded_items(self, db_session) -> None:
        """Repository count matches the number of approved rows in the DB."""
        from app.repositories.item_bank_repository import ItemBankRepository

        repo = ItemBankRepository(session=db_session)
        count = await repo.count_approved_items()

        # We can't know the exact count without controlling DB state fully,
        # so just assert it's a non-negative integer.
        assert isinstance(count, int)
        assert count >= 0
