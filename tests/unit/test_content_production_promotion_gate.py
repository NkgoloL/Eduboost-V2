"""Unit tests for production promotion gate service."""
from __future__ import annotations

from types import SimpleNamespace


from app.services.content_production_promotion_gate import (
    ContentProductionPromotionGate,
    ProductionGateStatus,
)


class FakeCoverageService:
    async def get_scope_coverage(self, scope_id, layers=None):
        return SimpleNamespace(
            scope_id=scope_id,
            summary={},
            per_caps_ref=[],
        )


def test_gate_service_can_be_instantiated() -> None:
    """Gate service can be instantiated."""
    coverage_service = FakeCoverageService()
    gate = ContentProductionPromotionGate(coverage_service=coverage_service)
    assert gate is not None


def test_gate_has_evaluate_scope_method() -> None:
    """Gate has evaluate_scope method."""
    coverage_service = FakeCoverageService()
    gate = ContentProductionPromotionGate(coverage_service=coverage_service)
    assert hasattr(gate, "evaluate_scope")


def test_gate_has_assert_promotable_method() -> None:
    """Gate has assert_promotable method."""
    coverage_service = FakeCoverageService()
    gate = ContentProductionPromotionGate(coverage_service=coverage_service)
    assert hasattr(gate, "assert_promotable")


def test_production_gate_status_enum_exists() -> None:
    """ProductionGateStatus enum exists."""
    assert hasattr(ProductionGateStatus, "PROMOTABLE")
    assert hasattr(ProductionGateStatus, "BLOCKED_BY_COVERAGE")
    assert hasattr(ProductionGateStatus, "BLOCKED_BY_REVIEW")
    assert hasattr(ProductionGateStatus, "BLOCKED_BY_PROVENANCE")
    assert hasattr(ProductionGateStatus, "BLOCKED_BY_VALIDATION")
    assert hasattr(ProductionGateStatus, "BLOCKED_BY_STAGING")
