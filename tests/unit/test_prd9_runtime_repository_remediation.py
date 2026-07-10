from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1].parent


@pytest.mark.unit
def test_subscription_service_constructs_bound_modern_guardian_repository_contract():
    source = (ROOT / "app/services/subscription_service.py").read_text(encoding="utf-8")
    repo_source = (ROOT / "app/repositories/auth_repository.py").read_text(encoding="utf-8")

    assert "from app.repositories.auth_repository import GuardianRepository" in source
    assert "GuardianRepository(db)" in source
    assert "def __init__(self, db: AsyncSession | None = None)" in repo_source
    assert "async def update_subscription" in repo_source
    assert "async def get_by_stripe_customer_id" in repo_source


@pytest.mark.unit
def test_stripe_service_uses_bound_guardian_repository_contract():
    source = (ROOT / "app/core/stripe_client.py").read_text(encoding="utf-8")
    repo_source = (ROOT / "app/repositories/auth_repository.py").read_text(encoding="utf-8")

    assert "GuardianRepository(db)" in source
    assert "get_by_stripe_customer_id" in source
    assert "async def get_by_id" in repo_source
    assert "async def update_subscription" in repo_source


@pytest.mark.unit
def test_assessment_repository_exposes_service_runtime_contract():
    source = (ROOT / "app/repositories/assessment_repository.py").read_text(encoding="utf-8")

    assert "def __init__(self, db: AsyncSession | None = None)" in source
    assert "async def list_assessments" in source
    assert "async def get_assessment" in source
    assert "async def create_attempt" in source
    assert "def to_payload" in source


@pytest.mark.unit
def test_assessment_service_and_router_bind_session_before_live_calls():
    service = (ROOT / "app/services/assessment_service_v2.py").read_text(encoding="utf-8")
    router = (ROOT / "app/api_v2_routers/assessments.py").read_text(encoding="utf-8")

    assert "def with_db" in service
    assert "service = AssessmentServiceV2()" in router
    assert "service.with_db(db)" in router
    assert "db: AsyncSession = Depends(get_db)" in router
