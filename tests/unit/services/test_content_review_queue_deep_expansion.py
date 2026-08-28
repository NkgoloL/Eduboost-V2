"""Comprehensive unit tests for ContentReviewQueue data models and service structure."""
from __future__ import annotations

import uuid
from unittest.mock import MagicMock
import pytest

from app.services.content_review_risk import ReviewRisk
from app.services.content_review_queue import (
    ReviewQueueItem,
    ReviewQueuePage,
    ReviewSummary,
    ArtifactReviewBundle,
    ContentReviewQueueService,
)


class TestContentReviewQueueModels:
    def test_review_queue_item_dataclass(self):
        aid = uuid.uuid4()
        item = ReviewQueueItem(
            artifact_id=aid,
            scope_id="grade4_mathematics_en",
            content_layer="diagnostic_items",
            artifact_type="diagnostic_item",
            caps_ref="4.M.1.1",
            status="pending_review",
            risk_level="low",
            risk_reasons=[],
            validation_status="passed",
            provenance_status="verified",
        )
        assert item.artifact_id == aid
        assert item.scope_id == "grade4_mathematics_en"
        assert item.status == "pending_review"

    def test_review_queue_page_dataclass(self):
        page = ReviewQueuePage(
            items=[],
            total=0,
            limit=20,
            offset=0,
        )
        assert page.total == 0
        assert page.limit == 20

    def test_review_summary_dataclass(self):
        summary = ReviewSummary(
            pending_review=12,
            low_risk=8,
            medium_risk=3,
            high_risk=1,
            critical_risk=0,
            assigned=5,
        )
        assert summary.pending_review == 12
        assert summary.low_risk == 8
        assert summary.assigned == 5

    def test_artifact_review_bundle_dataclass(self):
        risk = ReviewRisk(level="low", score=10, reasons=[])
        bundle = ArtifactReviewBundle(
            artifact={"title": "Test Item"},
            validation_report={"passed": True},
            provenance={"hash": "abc"},
            sources=[],
            review_risk=risk,
            generation_metadata={"model": "gpt-4o"},
        )
        assert bundle.artifact["title"] == "Test Item"
        assert bundle.review_risk.level == "low"

    def test_content_review_queue_service_init(self):
        mock_risk = MagicMock()
        mock_factory = MagicMock()
        service = ContentReviewQueueService(risk_service=mock_risk, factory_service=mock_factory)
        assert service.risk_service == mock_risk
        assert service.factory_service == mock_factory
