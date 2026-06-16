from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import ProgrammingError

from app.models.ai_operations import AIBudgetCounter, AIUsageReservation
from app.modules.diagnostics.item_bank_service import _irt_item_is_learner_eligible
from app.services.ai_operations import AIOperationsService, BudgetLimits
from app.services.content_answer_key_verification import ContentAnswerKeyVerificationService
from app.services.semantic_retrieval.indexing import _metadata_allows_generated_artifact
from app.services.semantic_retrieval.service import SemanticRetrievalService
from app.services.semantic_retrieval.types import RetrievalFilters


def test_generated_metadata_without_status_fails_closed():
    assert _metadata_allows_generated_artifact({"source_origin": "generated_artifact"}) is False
    assert _metadata_allows_generated_artifact({"artifact_id": "a"}) is False
    assert _metadata_allows_generated_artifact({"source_origin": "generated", "artifact_status": "published"}) is True
    assert _metadata_allows_generated_artifact({}) is True


def test_expired_override_is_not_learner_eligible():
    now = datetime.now(UTC)
    expired = SimpleNamespace(irt_quality_state="overridden", irt_manual_override_until=now - timedelta(seconds=1))
    active = SimpleNamespace(irt_quality_state="overridden", irt_manual_override_until=now + timedelta(minutes=5))
    assert _irt_item_is_learner_eligible(expired, now=now) is False
    assert _irt_item_is_learner_eligible(active, now=now) is True


@pytest.mark.asyncio
async def test_programming_error_does_not_fallback_to_full_text():
    provider = AsyncMock()
    provider.model = "test"
    provider.version = "v1"
    provider.embed_query.return_value = [0.0] * 1536
    repository = MagicMock()
    repository.semantic_search = AsyncMock(side_effect=ProgrammingError("sql", {}, Exception("bad schema")))
    repository.full_text_search = AsyncMock(return_value=[])
    service = SemanticRetrievalService(embedding_provider=provider, repository=repository)
    with pytest.raises(ProgrammingError):
        await service.search(
            AsyncMock(),
            query="whole numbers",
            filters=RetrievalFilters(scope_id="g4-math"),
        )
    repository.full_text_search.assert_not_awaited()


@pytest.mark.asyncio
async def test_answer_key_verification_is_separate_from_quorum():
    artifact_id = uuid.uuid4()
    artifact = SimpleNamespace(
        artifact_id=artifact_id,
        version_number=1,
        artifact_hash="sha256:" + "a" * 64,
        content_layer=SimpleNamespace(value="diagnostic_items"),
        artifact_type=SimpleNamespace(value="diagnostic_item"),
        status=SimpleNamespace(value="approved"),
        answer_key_verified=False,
        publication_eligible=False,
    )
    db = AsyncMock()
    db.scalar = AsyncMock(side_effect=[None, artifact])
    db.add = MagicMock(side_effect=lambda obj: setattr(obj, "verification_id", uuid.uuid4()))
    db.flush = AsyncMock()
    result = await ContentAnswerKeyVerificationService().record(
        db,
        artifact_id=artifact_id,
        expected_version=1,
        expected_artifact_hash=artifact.artifact_hash,
        method="deterministic_recompute",
        passed=True,
        verifier_actor_id="curriculum-lead",
        idempotency_key="verify-0001",
        details={"verification_basis": "independent recomputation of each item"},
    )
    assert result.passed is True
    assert artifact.answer_key_verified is True
    assert artifact.publication_eligible is True


@pytest.mark.asyncio
async def test_actual_usage_overage_is_accounted_and_flagged():
    reservation = AIUsageReservation(
        operation_id="op-1",
        user_id="u1",
        tenant_id="t1",
        purpose="tutor",
        estimated_tokens=10,
        status="pending",
        metadata_json={},
        reserved_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(minutes=5),
    )
    reservation.reservation_id = uuid.uuid4()
    user_counter = AIBudgetCounter(
        scope_type="user", scope_id="u1", period_key="2026-06-15",
        used_tokens=95, reserved_tokens=10, used_cost_usd=Decimal("0"),
    )
    tenant_counter = AIBudgetCounter(
        scope_type="tenant", scope_id="t1", period_key="2026-06",
        used_tokens=95, reserved_tokens=10, used_cost_usd=Decimal("0"),
    )
    db = AsyncMock()
    db.scalar = AsyncMock(side_effect=[reservation, None])
    db.add = MagicMock()
    db.flush = AsyncMock()
    service = AIOperationsService(
        db,
        limits=BudgetLimits(
            user_daily_tokens=100,
            tenant_monthly_tokens=100,
            alert_threshold=0.8,
            reservation_ttl_seconds=300,
        ),
    )
    service._locked_counter = AsyncMock(side_effect=[user_counter, tenant_counter])
    event = await service.finalize(
        operation_id="op-1",
        provider="fallback",
        model="safe",
        prompt_tokens=10,
        completion_tokens=10,
    )
    assert event.outcome == "blocked"
    assert event.metadata_json["budget_overage"]
    assert reservation.failure_reason == "actual_usage_exceeded_budget"
    assert user_counter.used_tokens == 115
    assert tenant_counter.used_tokens == 115
