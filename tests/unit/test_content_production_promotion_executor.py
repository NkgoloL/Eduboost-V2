"""Unit tests for production promotion executor service."""
from __future__ import annotations



from app.services.content_production_promotion_executor import (
    ContentProductionPromotionExecutor,
)
from app.services.content_production_promotion_gate import ContentProductionPromotionGate


def test_executor_can_be_instantiated() -> None:
    """Executor can be instantiated."""
    gate = ContentProductionPromotionGate(coverage_service=None)
    executor = ContentProductionPromotionExecutor(gate=gate)
    assert executor is not None


def test_executor_has_dry_run_promotion_method() -> None:
    """Executor has dry_run_promotion method."""
    gate = ContentProductionPromotionGate(coverage_service=None)
    executor = ContentProductionPromotionExecutor(gate=gate)
    assert hasattr(executor, "dry_run_promotion")


def test_executor_has_promote_scope_method() -> None:
    """Executor has promote_scope method."""
    gate = ContentProductionPromotionGate(coverage_service=None)
    executor = ContentProductionPromotionExecutor(gate=gate)
    assert hasattr(executor, "promote_scope")


def test_executor_has_get_promotion_event_method() -> None:
    """Executor has get_promotion_event method."""
    gate = ContentProductionPromotionGate(coverage_service=None)
    executor = ContentProductionPromotionExecutor(gate=gate)
    assert hasattr(executor, "get_promotion_event")


def test_executor_has_list_promotion_events_method() -> None:
    """Executor has list_promotion_events method."""
    gate = ContentProductionPromotionGate(coverage_service=None)
    executor = ContentProductionPromotionExecutor(gate=gate)
    assert hasattr(executor, "list_promotion_events")


def test_executor_has_rollback_promotion_method() -> None:
    """Executor has rollback_promotion method."""
    gate = ContentProductionPromotionGate(coverage_service=None)
    executor = ContentProductionPromotionExecutor(gate=gate)
    assert hasattr(executor, "rollback_promotion")
