"""Comprehensive branch coverage expansion for IRTQualityService."""
from __future__ import annotations

import math
import uuid
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domain.irt_quality_schemas import (
    IRTCalibrationDecision,
    IRTCalibrationMetrics,
    IRTCalibrationObservation,
    IRTInterventionAction,
    IRTQualityPolicy,
    IRTQualityState,
)
from app.models.content_factory import ContentArtifactStatus, ContentGenerationArtifact
from app.models.diagnostic_item import DiagnosticItem, LanguageEnum, ReviewStatusEnum, SubjectCodeEnum
from app.models.item_exposure import ItemExposure
from app.models.irt_quality import IRTCalibrationEvent, IRTCalibrationRun
from app.services.irt_quality_service import (
    IRTQualityConflict,
    IRTQualityError,
    IRTQualityService,
    _sigmoid,
    answer_position_distribution,
    correct_answer_position,
    decide_intervention,
    fit_two_parameter_logistic,
)


@pytest.mark.unit
def test_fit_two_parameter_logistic_convergence():
    # Construct synthetic observations that converge quickly
    obs = [
        IRTCalibrationObservation(learner_id=uuid.uuid4(), session_id=uuid.uuid4(), ability_proxy=-2.0, is_correct=False),
        IRTCalibrationObservation(learner_id=uuid.uuid4(), session_id=uuid.uuid4(), ability_proxy=-1.0, is_correct=False),
        IRTCalibrationObservation(learner_id=uuid.uuid4(), session_id=uuid.uuid4(), ability_proxy=1.0, is_correct=True),
        IRTCalibrationObservation(learner_id=uuid.uuid4(), session_id=uuid.uuid4(), ability_proxy=2.0, is_correct=True),
    ]
    a, b, rmse, converged = fit_two_parameter_logistic(obs, iterations=500)
    assert a > 0
    assert rmse < 1.0


@pytest.mark.unit
def test_irt_quality_service_init_default():
    svc = IRTQualityService()
    assert svc.policy is not None
    assert svc.policy.min_responses > 0


@pytest.mark.asyncio
async def test_manual_override_and_clear_override():
    svc = IRTQualityService()
    db = AsyncMock()
    item_id = uuid.uuid4()

    # 1. Item not found on manual_override
    db.scalar = AsyncMock(return_value=None)
    with pytest.raises(LookupError, match="not found"):
        await svc.manual_override(
            db,
            item_id=item_id,
            state=IRTQualityState.HEALTHY,
            reason="Educator validated",
            expires_at=datetime.now(UTC) + timedelta(days=7),
            actor_id="admin-1",
        )

    # 2. Item found on manual_override
    item = DiagnosticItem(
        item_id=item_id,
        stem="What is 2+2?",
        answer_key="4",
        options=["2", "3", "4", "5"],
        irt_quality_state=IRTQualityState.UNCALIBRATED.value,
        irt_row_version=1,
    )
    db.scalar = AsyncMock(return_value=item)
    db.flush = AsyncMock()
    db.commit = AsyncMock()

    overridden = await svc.manual_override(
        db,
        item_id=item_id,
        state=IRTQualityState.HEALTHY,
        reason="Educator validated",
        expires_at=datetime.now(UTC) + timedelta(days=7),
        actor_id="admin-1",
    )
    assert overridden.irt_quality_state == IRTQualityState.HEALTHY.value
    assert overridden.irt_manual_override_reason == "Educator validated"
    assert overridden.irt_row_version == 2
    assert db.add.call_count >= 2

    # 3. Item not found on clear_override
    db.scalar = AsyncMock(return_value=None)
    with pytest.raises(LookupError, match="not found"):
        await svc.clear_override(db, item_id=item_id, actor_id="admin-1")

    # 4. Item found on clear_override
    db.scalar = AsyncMock(return_value=item)
    cleared = await svc.clear_override(db, item_id=item_id, actor_id="admin-1")
    assert cleared.irt_quality_state == IRTQualityState.UNCALIBRATED.value
    assert cleared.irt_manual_override_reason is None
    assert cleared.irt_manual_override_until is None
    assert cleared.irt_row_version == 3


@pytest.mark.asyncio
async def test_run_idempotent_existing_run():
    svc = IRTQualityService()
    db = AsyncMock()
    run_id = uuid.uuid4()

    existing_run = IRTCalibrationRun(
        run_id=run_id,
        idempotency_key="key-123",
        status="completed",
        summary={"evaluated": 5, "healthy": 5},
    )
    db.scalar = AsyncMock(return_value=existing_run)

    res = await svc.run(db, idempotency_key="key-123")
    assert res["run_id"] == str(run_id)
    assert res["status"] == "completed"
    assert res["evaluated"] == 5


@pytest.mark.asyncio
async def test_run_failure_rollback():
    svc = IRTQualityService()
    db = AsyncMock()
    run_id = uuid.uuid4()

    db.scalar = AsyncMock(return_value=None)
    run_obj = IRTCalibrationRun(run_id=run_id, idempotency_key="key-fail", status="running")
    db.get = AsyncMock(return_value=run_obj)

    item = DiagnosticItem(
        item_id=uuid.uuid4(),
        stem="Faulty Item",
        options=["A", "B"],
        answer_key="A",
        irt_quality_state=IRTQualityState.UNCALIBRATED.value,
        review_status=ReviewStatusEnum.APPROVED,
    )

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [item]
    db.scalars = AsyncMock(return_value=mock_scalars)

    # _calibrate_item throws inside the try loop
    svc._calibrate_item = AsyncMock(side_effect=RuntimeError("Calibration computation failed"))
    db.commit = AsyncMock()
    db.rollback = AsyncMock()

    with pytest.raises(RuntimeError, match="Calibration computation failed"):
        await svc.run(db, idempotency_key="key-fail")

    db.rollback.assert_awaited_once()
    assert run_obj.status == "failed"


@pytest.mark.asyncio
async def test_run_comprehensive_item_lifecycle():
    policy = IRTQualityPolicy(
        min_responses=30,
        min_unique_learners=20,
        min_sessions=10,
        min_answered_ratio=0.5,
        retire_after_strikes=2,
        max_correct_position_share=0.4,
    )
    svc = IRTQualityService(policy=policy)
    db = AsyncMock()
    run_id = uuid.uuid4()

    db.scalar = AsyncMock(return_value=None)
    run_obj = IRTCalibrationRun(run_id=run_id, idempotency_key="key-comprehensive", status="running")
    db.get = AsyncMock(return_value=run_obj)

    # 1. Healthy item
    item_healthy = DiagnosticItem(
        item_id=uuid.uuid4(),
        stem="Healthy Item",
        options=[{"value": "A"}, {"value": "B"}, {"value": "C"}, {"value": "D"}],
        answer_key="A",
        review_status=ReviewStatusEnum.APPROVED,
        grade=5,
        subject=SubjectCodeEnum.MATHEMATICS,
        language=LanguageEnum.EN,
        caps_ref="5.M.1",
        discrimination_a=1.2,
        difficulty_b=0.0,
        guessing_c=0.25,
        irt_quality_state=IRTQualityState.UNCALIBRATED.value,
    )

    # 2. Insufficient data item
    item_insufficient = DiagnosticItem(
        item_id=uuid.uuid4(),
        stem="Insufficient Item",
        options=[{"value": "A"}, {"value": "B"}, {"value": "C"}, {"value": "D"}],
        answer_key="B",
        review_status=ReviewStatusEnum.APPROVED,
        grade=5,
        subject=SubjectCodeEnum.MATHEMATICS,
        language=LanguageEnum.EN,
        caps_ref="5.M.1",
        irt_quality_state=IRTQualityState.UNCALIBRATED.value,
    )

    # 3. Quarantined item (catastrophic failure on first strike)
    item_quarantined = DiagnosticItem(
        item_id=uuid.uuid4(),
        stem="Quarantined Item",
        options=[{"value": "A"}, {"value": "B"}, {"value": "C"}, {"value": "D"}],
        answer_key="C",
        review_status=ReviewStatusEnum.APPROVED,
        grade=5,
        subject=SubjectCodeEnum.MATHEMATICS,
        language=LanguageEnum.EN,
        caps_ref="5.M.1",
        irt_strike_count=0,
        irt_quality_state=IRTQualityState.UNCALIBRATED.value,
    )

    # 4. Retired item (persistent catastrophic failure -> 2 strikes -> rewrite created)
    item_retired = DiagnosticItem(
        item_id=uuid.uuid4(),
        stem="Retired Item",
        options=[{"value": "A"}, {"value": "B"}, {"value": "C"}, {"value": "D"}],
        answer_key="D",
        review_status=ReviewStatusEnum.APPROVED,
        grade=5,
        subject=SubjectCodeEnum.MATHEMATICS,
        language=LanguageEnum.EN,
        caps_ref="5.M.1",
        irt_strike_count=1,
        irt_quality_state=IRTQualityState.UNCALIBRATED.value,
    )

    # 5. Monitor item (discrimination between monitor_discrimination_min 0.50 and healthy_discrimination_min 0.70)
    item_monitor = DiagnosticItem(
        item_id=uuid.uuid4(),
        stem="Monitor Item",
        options=[{"value": "A"}, {"value": "B"}, {"value": "C"}, {"value": "D"}],
        answer_key="A",
        review_status=ReviewStatusEnum.APPROVED,
        grade=5,
        subject=SubjectCodeEnum.MATHEMATICS,
        language=LanguageEnum.EN,
        caps_ref="5.M.1",
        discrimination_a=0.60,
        irt_quality_state=IRTQualityState.UNCALIBRATED.value,
    )

    # 6. Review required item (weak discrimination between 0.35 and 0.50)
    item_review = DiagnosticItem(
        item_id=uuid.uuid4(),
        stem="Review Required Item",
        options=[{"value": "A"}, {"value": "B"}, {"value": "C"}, {"value": "D"}],
        answer_key="A",
        review_status=ReviewStatusEnum.APPROVED,
        grade=5,
        subject=SubjectCodeEnum.MATHEMATICS,
        language=LanguageEnum.EN,
        caps_ref="5.M.1",
        discrimination_a=0.45,
        irt_quality_state=IRTQualityState.UNCALIBRATED.value,
    )

    items = [item_healthy, item_insufficient, item_quarantined, item_retired, item_monitor, item_review]

    def make_scalars_result(res_items):
        m = MagicMock()
        m.all.return_value = res_items
        return m

    # Mock _calibrate_item directly to test decision routing & rewrite generation
    metrics_healthy = IRTCalibrationMetrics(
        response_count=100, unique_learners=50, session_count=50, answered_ratio=1.0,
        accuracy=0.6, difficulty_b=0.0, discrimination_a=1.2, guessing_c=0.25, fit_rmse=0.15,
        converged=True, data_quality_passed=True, data_quality_reasons=[],
    )
    metrics_insufficient = IRTCalibrationMetrics(
        response_count=2, unique_learners=1, session_count=1, answered_ratio=1.0,
        accuracy=0.5, difficulty_b=0.0, discrimination_a=1.0, guessing_c=0.25, fit_rmse=0.2,
        converged=True, data_quality_passed=False, data_quality_reasons=["responses<30"],
    )
    metrics_catastrophic = IRTCalibrationMetrics(
        response_count=100, unique_learners=50, session_count=50, answered_ratio=1.0,
        accuracy=0.05, difficulty_b=2.5, discrimination_a=0.20, guessing_c=0.25, fit_rmse=0.8,
        converged=True, data_quality_passed=True, data_quality_reasons=[],
    )
    metrics_monitor = IRTCalibrationMetrics(
        response_count=100, unique_learners=50, session_count=50, answered_ratio=1.0,
        accuracy=0.6, difficulty_b=0.0, discrimination_a=0.60, guessing_c=0.25, fit_rmse=0.18,
        converged=True, data_quality_passed=True, data_quality_reasons=[],
    )
    metrics_review = IRTCalibrationMetrics(
        response_count=100, unique_learners=50, session_count=50, answered_ratio=1.0,
        accuracy=0.6, difficulty_b=0.0, discrimination_a=0.45, guessing_c=0.25, fit_rmse=0.35,
        converged=True, data_quality_passed=True, data_quality_reasons=[],
    )



    svc._calibrate_item = AsyncMock(side_effect=[
        metrics_healthy,
        metrics_insufficient,
        metrics_catastrophic,
        metrics_catastrophic,
        metrics_monitor,
        metrics_review,
    ])

    db.scalars = AsyncMock(return_value=make_scalars_result(items))
    db.flush = AsyncMock()
    db.commit = AsyncMock()

    res = await svc.run(db, idempotency_key="key-comprehensive", dry_run=False, item_ids=[item.item_id for item in items])
    assert res["status"] == "completed"
    assert res["evaluated"] == 6
    assert res["healthy"] == 1
    assert res["insufficient_data"] == 1
    assert res["quarantined"] == 1
    assert res["retired"] == 1
    assert res["rewrites_created"] == 1
    assert res["monitor"] == 1
    assert res["review_required"] == 1
    assert item_quarantined.safety_passed is False
    assert item_retired.review_status == ReviewStatusEnum.RETIRED


@pytest.mark.asyncio
async def test_calibrate_item_and_build_observations_real_db_queries():
    svc = IRTQualityService()
    db = AsyncMock()

    item = DiagnosticItem(
        item_id=uuid.uuid4(),
        stem="Test Question",
        options=["A", "B", "C", "D"],
        answer_key="A",
        discrimination_a=1.0,
        difficulty_b=0.0,
        guessing_c=0.25,
    )

    s1 = uuid.uuid4()
    l1 = uuid.uuid4()

    exp1 = ItemExposure(
        id=1,
        item_id=item.item_id,
        session_id=s1,
        learner_id=l1,
        is_correct=True,
        served_at=datetime.now(UTC),
    )
    peer1 = ItemExposure(id=2, item_id=uuid.uuid4(), session_id=s1, learner_id=l1, is_correct=True, served_at=datetime.now(UTC))
    peer2 = ItemExposure(id=3, item_id=uuid.uuid4(), session_id=s1, learner_id=l1, is_correct=False, served_at=datetime.now(UTC))
    peer3 = ItemExposure(id=4, item_id=uuid.uuid4(), session_id=s1, learner_id=l1, is_correct=True, served_at=datetime.now(UTC))

    def make_scalars_result(items):
        m = MagicMock()
        m.all.return_value = items
        return m

    # 1. exposures for item
    # 2. all exposures for session s1 (including peers)
    db.scalars = AsyncMock(side_effect=[
        make_scalars_result([exp1]),
        make_scalars_result([exp1, peer1, peer2, peer3]),
    ])

@pytest.mark.asyncio
async def test_run_dry_run_and_answer_position_bias_detected():
    policy = IRTQualityPolicy(
        min_responses=30,
        min_unique_learners=20,
        min_sessions=10,
        min_answered_ratio=0.5,
        max_correct_position_share=0.25,
    )

    svc = IRTQualityService(policy=policy)
    db = AsyncMock()
    run_id = uuid.uuid4()

    db.scalar = AsyncMock(return_value=None)
    run_obj = IRTCalibrationRun(run_id=run_id, idempotency_key="key-dry-run", status="running")
    db.get = AsyncMock(return_value=run_obj)

    # 25 items where correct option is always index 0 (Option A) to trigger bias with sample_size >= 20
    items = [
        DiagnosticItem(
            item_id=uuid.uuid4(),
            stem=f"Item {i}",
            options=["A", "B", "C", "D"],
            answer_key="A",
            review_status=ReviewStatusEnum.APPROVED,
            irt_quality_state=IRTQualityState.UNCALIBRATED.value,
        )
        for i in range(25)
    ]

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = items
    db.scalars = AsyncMock(return_value=mock_scalars)

    metrics_healthy = IRTCalibrationMetrics(
        response_count=100, unique_learners=50, session_count=50, answered_ratio=1.0,
        accuracy=0.6, difficulty_b=0.0, discrimination_a=1.2, guessing_c=0.25, fit_rmse=0.15,
        converged=True, data_quality_passed=True, data_quality_reasons=[],
    )
    svc._calibrate_item = AsyncMock(return_value=metrics_healthy)
    db.flush = AsyncMock()
    db.commit = AsyncMock()

    res = await svc.run(db, idempotency_key="key-dry-run", dry_run=True)
    assert res["status"] == "completed"
    assert res["answer_position_bias_detected"] is True
    assert "policy_warning" in res


@pytest.mark.asyncio
async def test_calibrate_item_and_build_observations_real_db_queries():
    svc = IRTQualityService()
    db = AsyncMock()

    item = DiagnosticItem(
        item_id=uuid.uuid4(),
        stem="Test Question",
        options=["A", "B", "C", "D"],
        answer_key="A",
        discrimination_a=1.0,
        difficulty_b=0.0,
        guessing_c=0.25,
    )

    # Construct 35 exposures across 25 sessions and learners with 3 peers per session
    target_exposures = []
    all_exposures = []
    for i in range(35):
        s_id = uuid.uuid4()
        l_id = uuid.uuid4()
        exp = ItemExposure(
            id=i + 1,
            item_id=item.item_id,
            session_id=s_id,
            learner_id=l_id,
            is_correct=(i % 2 == 0),
            served_at=datetime.now(UTC),
        )
        target_exposures.append(exp)
        all_exposures.append(exp)

        # Add 3 peers for each session so len(peers) >= 3
        for p in range(3):
            peer = ItemExposure(
                id=1000 + i * 10 + p,
                item_id=uuid.uuid4(),
                session_id=s_id,
                learner_id=l_id,
                is_correct=(p % 2 == 0),
                served_at=datetime.now(UTC),
            )
            all_exposures.append(peer)

    def make_scalars_result(items):
        m = MagicMock()
        m.all.return_value = items
        return m

    # 1. exposures for item
    # 2. all exposures for sessions
    db.scalars = AsyncMock(side_effect=[
        make_scalars_result(target_exposures),
        make_scalars_result(all_exposures),
    ])

    metrics = await svc._calibrate_item(db, item)
    assert metrics.response_count == 35
    assert isinstance(metrics.data_quality_passed, bool)
    assert metrics.unique_learners == 35
    assert metrics.session_count == 35
    assert metrics.accuracy > 0
    assert metrics.discrimination_a > 0



