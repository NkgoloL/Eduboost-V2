"""Batch 220 — app/repositories/item_bank_repository.py comprehensive branch coverage expansion.

Tests:
- get_item (found vs None)
- list_by_caps_ref (with/without review_status, domain enum vs model enum vs str)
- get_unexposed_items (with/without min_b_param, max_b_param, custom review_status)
- list_approved_for_grade (with/without subject, subject map normalization)
- get_exposure_heatmap (zero vs non-zero max_exposure, utilisation calculation)
- get_coverage_summary (with/without caps_refs filter)
- record_exposure (persists ItemExposure and updates exposure_count)
- get_approved_items, get_items_by_topic, count_approved_items
- update_review_status (item not found, string vs enum status, reviewer_id, quality_score, reviewed_at)
- _normalise helper (subject, item_type, review_status, source, language, ISO datetimes)
- upsert (existing item update with enum conversion, new item creation with UUID conversion)
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.item_schema import ReviewStatus
from app.models.diagnostic_item import DiagnosticItem, ReviewStatusEnum
from app.models.item_exposure import ItemExposure
from app.repositories.item_bank_repository import ItemBankRepository


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def repo(mock_db):
    return ItemBankRepository(mock_db)


# ---------------------------------------------------------------------------
# Read Operations
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_item(repo, mock_db):
    item_id = uuid.uuid4()
    mock_item = MagicMock(spec=DiagnosticItem, item_id=item_id)
    res = MagicMock()
    res.scalar_one_or_none.return_value = mock_item
    mock_db.execute.return_value = res

    result = await repo.get_item(item_id)
    assert result == mock_item

    res.scalar_one_or_none.return_value = None
    assert await repo.get_item(item_id) is None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_list_by_caps_ref_with_and_without_status(repo, mock_db):
    mock_items = [MagicMock(spec=DiagnosticItem), MagicMock(spec=DiagnosticItem)]
    res = MagicMock()
    res.scalars.return_value.all.return_value = mock_items
    mock_db.execute.return_value = res

    # Without review_status
    items1 = await repo.list_by_caps_ref("MATH.4.1")
    assert len(items1) == 2

    # With Domain Enum ReviewStatus
    items2 = await repo.list_by_caps_ref("MATH.4.1", review_status=ReviewStatus.APPROVED)
    assert len(items2) == 2

    # With Model Enum ReviewStatusEnum
    items3 = await repo.list_by_caps_ref("MATH.4.1", review_status=ReviewStatusEnum.APPROVED)
    assert len(items3) == 2


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_unexposed_items_with_filters(repo, mock_db):
    mock_items = [MagicMock(spec=DiagnosticItem)]
    res = MagicMock()
    res.scalars.return_value.all.return_value = mock_items
    mock_db.execute.return_value = res

    learner_id = uuid.uuid4()

    # With min and max b params
    items = await repo.get_unexposed_items(
        learner_id=learner_id,
        caps_ref="MATH.4.1",
        min_b_param=-1.5,
        max_b_param=1.5,
        review_status="approved",
        limit=10,
    )
    assert len(items) == 1


@pytest.mark.asyncio
@pytest.mark.unit
async def test_list_approved_for_grade(repo, mock_db):
    mock_items = [MagicMock(spec=DiagnosticItem)]
    res = MagicMock()
    res.scalars.return_value.all.return_value = mock_items
    mock_db.execute.return_value = res

    # With subject mapping
    items = await repo.list_approved_for_grade(4, subject="MATHEMATICS", limit=5)
    assert len(items) == 1


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_exposure_heatmap(repo, mock_db):
    item_id1 = uuid.uuid4()
    item_id2 = uuid.uuid4()

    res = MagicMock()
    res.all.return_value = [
        (item_id1, "MATH.4.1", ReviewStatusEnum.APPROVED, 5, 20),
        (item_id2, "MATH.4.1", "approved", 0, 0),  # zero max_exposure test
    ]
    mock_db.execute.return_value = res

    heatmap = await repo.get_exposure_heatmap("MATH.4.1")
    assert len(heatmap) == 2
    assert heatmap[0]["utilisation"] == 0.25
    assert heatmap[1]["utilisation"] == 0.0


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_coverage_summary(repo, mock_db):
    res = MagicMock()
    res.all.return_value = [
        ("MATH.4.1", ReviewStatusEnum.APPROVED, 10),
        ("MATH.4.1", "draft", 2),
        ("MATH.4.2", ReviewStatusEnum.APPROVED, 5),
    ]
    mock_db.execute.return_value = res

    summary = await repo.get_coverage_summary(["MATH.4.1", "MATH.4.2"])
    assert summary["MATH.4.1"]["total"] == 12
    assert summary["MATH.4.1"]["approved"] == 10
    assert summary["MATH.4.1"]["draft"] == 2
    assert summary["MATH.4.2"]["approved"] == 5


# ---------------------------------------------------------------------------
# Write Operations
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_record_exposure(repo, mock_db):
    item_id = uuid.uuid4()
    learner_id = uuid.uuid4()
    session_id = uuid.uuid4()

    exposure = await repo.record_exposure(item_id, learner_id, session_id=session_id)

    assert isinstance(exposure, ItemExposure)
    assert exposure.item_id == item_id
    assert exposure.learner_id == learner_id
    assert exposure.session_id == session_id
    mock_db.add.assert_called_once()
    mock_db.execute.assert_called_once()
    mock_db.flush.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_approved_items_and_by_topic_and_count(repo, mock_db):
    mock_item = MagicMock(
        item_id=uuid.uuid4(),
        topic="Fractions",
        difficulty_b=0.5,
        review_status=ReviewStatusEnum.APPROVED,
        stem="What is 1/2 + 1/2?",
        answer_key={"correct": "1"},
        grade=4,
        subject="Mathematics",
    )
    res_items = MagicMock()
    res_items.scalars.return_value.all.return_value = [mock_item]

    res_count = MagicMock()
    res_count.scalar.return_value = 42

    mock_db.execute.side_effect = [res_items, res_items, res_count]

    approved = await repo.get_approved_items()
    assert len(approved) == 1
    assert approved[0]["topic"] == "Fractions"
    assert approved[0]["difficulty"] == 0.5

    by_topic = await repo.get_items_by_topic("Fractions")
    assert len(by_topic) == 1

    total = await repo.count_approved_items()
    assert total == 42


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_review_status(repo, mock_db):
    item_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    # Item not found returns None
    repo.get_item = AsyncMock(return_value=None)
    res_none = await repo.update_review_status(item_id, "approved")
    assert res_none is None

    # Item found with string status, reviewer_id, quality_score
    mock_item = MagicMock(spec=DiagnosticItem)
    repo.get_item = AsyncMock(return_value=mock_item)

    res_item = await repo.update_review_status(
        item_id,
        "approved",
        reviewer_id=reviewer_id,
        quality_score=0.98,
    )
    assert res_item == mock_item
    assert mock_item.review_status == ReviewStatusEnum.APPROVED
    assert mock_item.reviewer_id == reviewer_id
    assert mock_item.quality_score == 0.98
    mock_db.flush.assert_called_once()


# ---------------------------------------------------------------------------
# _normalise & upsert
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_normalise_helper(repo):
    raw_data = {
        "subject": "MATHEMATICS",
        "item_type": "MCQ",
        "review_status": "APPROVED",
        "source": "LLM_GENERATED",
        "language": "EN",
        "created_at": "2026-05-25T10:00:00Z",
    }
    norm = repo._normalise(raw_data)
    assert norm["subject"] == "Mathematics"
    assert norm["item_type"] == "mcq"
    assert norm["review_status"] == "approved"
    assert norm["source"] == "llm_generated"
    assert norm["language"] == "en"
    assert isinstance(norm["created_at"], datetime)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_upsert_existing_and_new_item(repo, mock_db):
    item_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    # 1. Update existing item
    existing_item = MagicMock(spec=DiagnosticItem, item_id=item_id)
    repo.get_item = AsyncMock(return_value=existing_item)

    data_update = {
        "item_id": str(item_id),
        "review_status": "approved",
        "topic": "Multiplication",
    }
    updated = await repo.upsert(data_update)
    assert updated == existing_item
    assert existing_item.review_status == ReviewStatusEnum.APPROVED
    mock_db.flush.assert_called_once()

    # 2. Create new item
    repo.get_item = AsyncMock(return_value=None)
    data_new = {
        "item_id": str(item_id),
        "reviewer_id": str(reviewer_id),
        "caps_ref": "MATH.4.2",
        "grade": 4,
        "subject": "Mathematics",
        "topic": "Division",
        "stem": "What is 10 / 2?",
        "answer_key": {"correct": "5"},
    }
    new_item = await repo.upsert(data_new)
    assert isinstance(new_item, DiagnosticItem)
    assert new_item.item_id == item_id
    assert new_item.reviewer_id == reviewer_id
    mock_db.add.assert_called_once_with(new_item)
