"""Unit tests for production read verification service."""
from __future__ import annotations



from app.services.content_production_read_verification import (
    ContentProductionReadVerificationService,
)


def test_verification_service_can_be_instantiated() -> None:
    """Verification service can be instantiated."""
    service = ContentProductionReadVerificationService()
    assert service is not None


def test_verification_service_has_verify_promotion_event_method() -> None:
    """Verification service has verify_promotion_event method."""
    service = ContentProductionReadVerificationService()
    assert hasattr(service, "verify_promotion_event")


def test_verification_service_has_verify_scope_production_method() -> None:
    """Verification service has verify_scope_production method."""
    service = ContentProductionReadVerificationService()
    assert hasattr(service, "verify_scope_production")
