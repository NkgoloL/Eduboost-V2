"""Comprehensive unit tests for production read verification service."""
from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.content_factory import ContentArtifactStatus
from app.services.content_production_read_verification import (
    ContentProductionReadVerificationService,
    ProductionReadVerificationReport,
    ScopeProductionReadReport,
)


def test_verification_service_instantiation_and_dataclasses() -> None:
    service = ContentProductionReadVerificationService()
    assert service is not None

    uid = uuid.uuid4()
    rep = ProductionReadVerificationReport(promotion_event_id=uid, passed=True, verified_count=5)
    assert rep.promotion_event_id == uid
    assert rep.passed is True
    assert rep.verified_count == 5

    scope_rep = ScopeProductionReadReport(scope_id="s1", passed=False, production_artifacts_count=0, errors=["err"])
    assert scope_rep.scope_id == "s1"
    assert scope_rep.passed is False


@pytest.mark.asyncio
async def test_verify_promotion_event_branches():
    service = ContentProductionReadVerificationService()
    session = AsyncMock()
    event_id = uuid.uuid4()
    art_id1 = uuid.uuid4()
    art_id2 = uuid.uuid4()

    # 1. Event not found
    mock_res_empty = MagicMock()
    mock_res_empty.scalar_one_or_none.return_value = None
    session.execute.return_value = mock_res_empty

    rep_not_found = await service.verify_promotion_event(session, event_id)
    assert rep_not_found.passed is False
    assert any("not found" in e for e in rep_not_found.errors)

    # 2. Event found, artifacts with various error conditions
    mock_event = SimpleNamespace(event_id=event_id)
    mock_prod_inactive = SimpleNamespace(artifact_id=art_id1, production_status="disabled")
    mock_prod_no_source = SimpleNamespace(artifact_id=art_id2, production_status="active")
    mock_prod_valid = SimpleNamespace(artifact_id=uuid.uuid4(), production_status="active")

    mock_event_res = MagicMock()
    mock_event_res.scalar_one_or_none.return_value = mock_event

    mock_prod_list_res = MagicMock()
    mock_prod_list_res.scalars.return_value.all.return_value = [
        mock_prod_inactive,
        mock_prod_no_source,
        mock_prod_valid,
    ]

    mock_src_missing = MagicMock()
    mock_src_missing.scalar_one_or_none.return_value = None

    mock_src_valid = MagicMock()
    mock_src_valid.scalar_one_or_none.return_value = SimpleNamespace(status=ContentArtifactStatus.APPROVED)

    session.execute.side_effect = [
        mock_event_res,
        mock_prod_list_res,
        mock_src_missing,
        mock_src_valid,
    ]

    rep = await service.verify_promotion_event(session, event_id)
    assert rep.passed is False
    assert rep.verified_count == 1
    assert any("not active" in e for e in rep.errors)
    assert any("Source artifact" in e and "not found" in e for e in rep.errors)


@pytest.mark.asyncio
async def test_verify_scope_production_branches():
    service = ContentProductionReadVerificationService()
    session = AsyncMock()
    art_id_pending = uuid.uuid4()
    art_id_approved = uuid.uuid4()

    mock_prod_pending = SimpleNamespace(artifact_id=art_id_pending, production_status="active")
    mock_prod_approved = SimpleNamespace(artifact_id=art_id_approved, production_status="active")

    mock_prod_res = MagicMock()
    mock_prod_res.scalars.return_value.all.return_value = [mock_prod_pending, mock_prod_approved]

    mock_src_pending = MagicMock()
    mock_src_pending.scalar_one_or_none.return_value = SimpleNamespace(status=ContentArtifactStatus.PENDING_REVIEW)

    mock_src_approved = MagicMock()
    mock_src_approved.scalar_one_or_none.return_value = SimpleNamespace(status=ContentArtifactStatus.APPROVED)

    session.execute.side_effect = [
        mock_prod_res,
        mock_src_pending,
        mock_src_approved,
    ]

    rep = await service.verify_scope_production(session, "term_1_maths")
    assert rep.passed is False
    assert rep.production_artifacts_count == 2
    assert any("points to non-approved artifact" in e for e in rep.errors)
