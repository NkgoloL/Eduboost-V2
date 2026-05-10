"""
Unit Tests — ItemBankService (P2-10 / P3 Refactor)
==================================================
Verifies:
  • Exposure cap prevents re-serving exhausted items
  • IRT-informed selection picks the item closest to learner's θ
  • Fisher information computation is correct for 3-PL model
  • Coverage ratio calculations
  • mark_item_reviewed enforces reviewer_id requirement

Run with: pytest tests/unit/modules/diagnostics/test_item_bank_service.py -v
"""

from __future__ import annotations

import math
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.diagnostic_item import DiagnosticItem
from app.domain.item_schema import ReviewStatus
from app.modules.diagnostics.item_bank_service import (
    LAUNCH_TARGET_ITEMS,
    ItemBankService,
    ItemSelectionError,
    fisher_information_3pl,
    select_maximum_information_item,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_item(
    *,
    item_id: uuid.UUID | None = None,
    caps_ref: str = "4.M.1.1",
    difficulty_b: float = 0.0,
    discrimination_a: float = 1.0,
    guessing_c: float = 0.25,
    review_status: ReviewStatus = ReviewStatus.APPROVED,
    exposure_count: int = 0,
    max_exposure: int = 50,
    safety_passed: bool = True,
) -> DiagnosticItem:
    item = MagicMock(spec=DiagnosticItem)
    item.item_id = item_id or uuid.uuid4()
    item.caps_ref = caps_ref
    item.difficulty_b = difficulty_b
    item.discrimination_a = discrimination_a
    item.guessing_c = guessing_c
    item.review_status = review_status
    item.exposure_count = exposure_count
    item.max_exposure = max_exposure
    item.safety_passed = safety_passed
    return item


@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.get_item = AsyncMock()
    repo.list_by_caps_ref = AsyncMock()
    repo.get_unexposed_items = AsyncMock()
    repo.get_coverage_summary = AsyncMock()
    repo.record_exposure = AsyncMock()
    repo.update_review_status = AsyncMock()
    return repo


@pytest.fixture
def service(mock_repo):
    return ItemBankService(mock_repo)


# ---------------------------------------------------------------------------
# Fisher Information — 3-PL model
# ---------------------------------------------------------------------------


def test_fisher_information_positive_for_valid_params():
    info = fisher_information_3pl(theta=0.0, a=1.0, b=0.0, c=0.25)
    assert info > 0


def test_fisher_information_maximised_near_b_param():
    """Fisher information peaks when θ is close to the item's b-parameter."""
    b = 0.5
    info_at_b = fisher_information_3pl(theta=b, a=1.0, b=b, c=0.25)
    info_far = fisher_information_3pl(theta=-2.0, a=1.0, b=b, c=0.25)
    assert info_at_b > info_far


def test_fisher_information_zero_for_degenerate_params():
    """Very extreme ability values → denominator → 0 → return 0."""
    info = fisher_information_3pl(theta=100.0, a=1.0, b=0.0, c=0.25)
    assert info == 0.0 or info < 1e-5


def test_fisher_information_increases_with_discrimination():
    """Higher discrimination → higher information."""
    low_a = fisher_information_3pl(theta=0.0, a=0.5, b=0.0, c=0.25)
    high_a = fisher_information_3pl(theta=0.0, a=2.0, b=0.0, c=0.25)
    assert high_a > low_a


# ---------------------------------------------------------------------------
# select_maximum_information_item
# ---------------------------------------------------------------------------


def test_select_max_info_picks_mathematically_best_item():
    theta = 0.0
    best  = _make_item(difficulty_b=0.0, discrimination_a=2.0)    # high discrimination, perfectly matched
    okay  = _make_item(difficulty_b=0.0, discrimination_a=1.0)
    poor  = _make_item(difficulty_b=2.5, discrimination_a=1.0)    # mismatched b-param

    selected = select_maximum_information_item([poor, okay, best], theta)
    assert selected.item_id == best.item_id


def test_select_max_info_handles_empty_list():
    with pytest.raises(ValueError, match="Candidate pool is empty"):
        select_maximum_information_item([], 0.0)


# ---------------------------------------------------------------------------
# select_item_for_learner — happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_select_item_picks_nearest_b_to_theta(service, mock_repo):
    """
    Given three unexposed items, the selector should pick the one
    whose difficulty_b is closest to the learner's current theta.
    """
    learner_id = uuid.uuid4()
    theta = 0.3

    item_near = _make_item(difficulty_b=0.4)   # nearest to 0.3
    item_far_above = _make_item(difficulty_b=2.5)
    item_far_below = _make_item(difficulty_b=-2.0)

    mock_repo.get_unexposed_items.return_value = [item_near, item_far_above, item_far_below]

    selected = await service.select_item_for_learner("4.M.1.1", learner_id, theta=theta)

    assert selected.item_id == item_near.item_id


@pytest.mark.asyncio
async def test_select_item_expands_window_when_neighbourhood_empty(service, mock_repo):
    """
    When the ability-windowed call returns nothing, the service should
    fall back to the full unexposed pool.
    """
    learner_id = uuid.uuid4()
    fallback_item = _make_item(difficulty_b=3.0)

    # First call (windowed) returns empty, second call (full) returns fallback
    mock_repo.get_unexposed_items.side_effect = [[], [fallback_item]]

    selected = await service.select_item_for_learner("4.M.1.1", learner_id, theta=0.0)

    assert selected.item_id == fallback_item.item_id
    assert mock_repo.get_unexposed_items.call_count == 2


@pytest.mark.asyncio
async def test_select_item_returns_none_when_fully_exhausted(service, mock_repo):
    """If no items are available at all (even outside window), return None."""
    mock_repo.get_unexposed_items.return_value = []

    selected = await service.select_item_for_learner("4.M.1.1", uuid.uuid4())
    assert selected is None


# ---------------------------------------------------------------------------
# record_item_served
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_record_item_served_proxies_to_repo(service, mock_repo):
    item_id = uuid.uuid4()
    learner_id = uuid.uuid4()

    await service.record_item_served(item_id, learner_id)

    mock_repo.record_exposure.assert_called_once_with(
        item_id, learner_id, session_id=None
    )


# ---------------------------------------------------------------------------
# Coverage and Launch Readiness
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_coverage_summary_calculates_ratios(service, mock_repo):
    # Mock repo response keyed by caps_ref
    mock_repo.get_coverage_summary.return_value = {
        "4.M.1.1": {"caps_ref": "4.M.1.1", "approved": 20, "total": 30},
    }

    summary = await service.get_coverage_summary(["4.M.1.1"])

    assert "4.M.1.1" in summary
    assert summary["4.M.1.1"]["coverage_ratio"] == 0.5  # 20 / 40 (target)
    assert summary["4.M.1.1"]["target"] == 40


@pytest.mark.asyncio
async def test_is_launch_ready_returns_false_when_under_target(service, mock_repo):
    # Only 10 items approved for 4.M.1.1 (target 40)
    mock_repo.get_coverage_summary.return_value = {
        "4.M.1.1": {"approved": 10},
        "4.M.1.2": {"approved": 40},
        "4.M.1.3": {"approved": 40},
    }

    ready = await service.is_launch_ready()
    assert ready is False


@pytest.mark.asyncio
async def test_is_launch_ready_returns_true_at_capacity(service, mock_repo):
    # All targets met
    mock_repo.get_coverage_summary.return_value = {
        "4.M.1.1": {"approved": 40},
        "4.M.1.2": {"approved": 40},
        "4.M.1.3": {"approved": 40},
    }

    ready = await service.is_launch_ready()
    assert ready is True


# ---------------------------------------------------------------------------
# Review Workflow
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mark_item_reviewed_updates_repo(service, mock_repo):
    item_id = uuid.uuid4()
    reviewer = uuid.uuid4()

    await service.mark_item_reviewed(
        item_id, "approved", reviewer_id=reviewer, quality_score=0.95
    )

    mock_repo.update_review_status.assert_called_once_with(
        item_id=item_id,
        new_status="approved",
        reviewer_id=reviewer,
        quality_score=0.95,
    )


@pytest.mark.asyncio
async def test_mark_item_reviewed_requires_reviewer_id_for_approval(service):
    with pytest.raises(ValueError, match="reviewer_id is required"):
        await service.mark_item_reviewed(
            uuid.uuid4(), "approved", reviewer_id=None
        )
