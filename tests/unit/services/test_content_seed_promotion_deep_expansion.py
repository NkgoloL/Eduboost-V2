"""Comprehensive unit tests for ContentSeedPromotionService and GateResult."""
from __future__ import annotations

from unittest.mock import MagicMock
import pytest

from app.services.content_seed_promotion import (
    GateResult,
    ContentSeedPromotionService,
)


class TestContentSeedPromotion:
    def test_gate_result_dataclass(self):
        res = GateResult(
            passed=True,
            errors=[],
            summary={"stageable_approved": 40},
        )
        assert res.passed is True
        assert len(res.errors) == 0
        assert res.summary["stageable_approved"] == 40

    def test_content_seed_promotion_service_init(self):
        mock_coverage = MagicMock()
        mock_verification = MagicMock()
        mock_executor = MagicMock()
        mock_gate = MagicMock()

        service = ContentSeedPromotionService(
            coverage_service=mock_coverage,
            verification_service=mock_verification,
            seed_executor=mock_executor,
            production_gate=mock_gate,
        )
        assert service.coverage_service == mock_coverage
        assert service.verification_service == mock_verification
        assert service.seed_executor == mock_executor
        assert service.production_gate == mock_gate
