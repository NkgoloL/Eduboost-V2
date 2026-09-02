import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import HTTPException

from app.services.ai_budget_guard import AIBudgetGuard
from app.services.billing_guard import (
    BillingLockError,
    assert_billing_authorized,
    check_live_billing_authorization,
    sanitize_billing_webhook,
)
from app.services.learner_service import LearnerService


def test_ai_budget_guard_edge_cases():
    guard = AIBudgetGuard(max_tokens_per_request=1000, daily_budget=5000)

    # 1. Non-positive tokens (line 39)
    with pytest.raises(ValueError, match="Estimated tokens must be positive"):
        guard.check_and_reserve(0)

    with pytest.raises(ValueError, match="Estimated tokens must be positive"):
        guard.check_and_reserve(-50)

    # 2. reset_usage (line 56)
    guard.check_and_reserve(500)
    assert guard._current_usage == 500
    guard.reset_usage()
    assert guard._current_usage == 0


def test_billing_guard_complete(tmp_path: Path):
    # 1. Missing register file returns False (fail-closed)
    assert check_live_billing_authorization(tmp_path) is False

    # 2. Corrupt/unparseable register returns False (fail-closed)
    reg_dir = tmp_path / "docs/roadmap/production_readiness"
    reg_dir.mkdir(parents=True)
    reg_file = reg_dir / "true_state_remediation_register.json"
    reg_file.write_text("not json", encoding="utf-8")
    assert check_live_billing_authorization(tmp_path) is False

    # 3. Valid JSON with partial permissions (still False)
    reg_file.write_text(json.dumps({
        "authority_boundaries": {
            "live_payment_processing_authorised": True,
            "billing_launch_authorised": False,
        }
    }), encoding="utf-8")
    assert check_live_billing_authorization(tmp_path) is False

    # 4. Valid JSON with full permissions (True)
    reg_file.write_text(json.dumps({
        "authority_boundaries": {
            "live_payment_processing_authorised": True,
            "billing_launch_authorised": True,
        }
    }), encoding="utf-8")
    assert check_live_billing_authorization(tmp_path) is True

    # 5. assert_billing_authorized and sanitize_billing_webhook
    # When authorized
    assert_billing_authorized(tmp_path)
    res = sanitize_billing_webhook({"id": "evt-123"}, root_dir=tmp_path)
    assert res == {"status": "processed", "event_id": "evt-123"}

    # When locked
    with pytest.raises(BillingLockError) as exc_info:
        assert_billing_authorized("/nonexistent/path")
    assert exc_info.value.status_code == 403
    assert exc_info.value.headers and exc_info.value.headers.get("X-Billing-Lock") == "LOCKED_FAIL_CLOSED"



@pytest.mark.asyncio
async def test_learner_service_complete():
    db = AsyncMock()
    mock_repo = AsyncMock()
    service = LearnerService(db=db, repository=mock_repo)

    # 1. Passthrough methods (lines 20-32)
    mock_repo.get_by_id.return_value = {"id": "l1"}
    assert await service.get_learner_summary("l1") == {"id": "l1"}

    mock_repo.get_by_guardian.return_value = [{"id": "l1"}]
    assert await service.list_by_guardian("g1") == [{"id": "l1"}]

    mock_repo.create.return_value = {"id": "l2"}
    created = await service.create_learner("g1", "Child", 4, "en")
    assert created == {"id": "l2"}

    # 2. get_mastery learner not found (line 39-40)
    mock_repo.get_by_id.return_value = None
    with patch("app.services.learner_service.ConsentService.require_active_consent", AsyncMock()):
        with pytest.raises(HTTPException) as exc:
            await service.get_mastery("unknown-learner")
        assert exc.value.status_code == 404

    # 3. get_mastery with existing topic mastery rows (lines 43-56)
    mock_learner = SimpleNamespace(id="l1", guardian_id="g1", pseudonym_id="pseudo-1")
    mock_repo.get_by_id.return_value = mock_learner
    now = datetime.now(timezone.utc)
    mock_mastery_row = SimpleNamespace(
        caps_ref="CAPS.MATH.1",
        mastery_score=0.85,
        mastery_label="proficient",
        last_updated_at=now,
    )

    with patch("app.services.learner_service.ConsentService.require_active_consent", AsyncMock()), \
         patch("app.services.learner_service.MasteryRepository.list_topic_mastery_by_learner", AsyncMock(return_value=[mock_mastery_row])):
        res_mastery = await service.get_mastery("l1")
        assert res_mastery["learner_id"] == "l1"
        assert len(res_mastery["mastery"]) == 1
        assert res_mastery["mastery"][0]["caps_ref"] == "CAPS.MATH.1"

    # 4. get_mastery fallback with active gaps (lines 58-73)
    mock_gap = SimpleNamespace(subject="MATH", severity=2.0)
    mock_gap_repo = AsyncMock()
    mock_gap_repo.get_active_gaps.return_value = [mock_gap]

    with patch("app.services.learner_service.ConsentService.require_active_consent", AsyncMock()), \
         patch("app.services.learner_service.MasteryRepository.list_topic_mastery_by_learner", AsyncMock(return_value=[])), \
         patch("app.services.learner_service.KnowledgeGapRepository", return_value=mock_gap_repo):
        res_gap_fallback = await service.get_mastery("l1")
        assert res_gap_fallback["learner_id"] == "l1"
        math_entry = next(m for m in res_gap_fallback["mastery"] if m["subject_code"] == "MATH")
        assert math_entry["mastery_score"] < 0.72


    # 5. get_topic_mastery (lines 76-100)
    mock_repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as exc:
        await service.get_topic_mastery("unknown", "CAPS.M.1")
    assert exc.value.status_code == 404

    mock_repo.get_by_id.return_value = mock_learner
    mock_topic_mastery = SimpleNamespace(mastery_score=0.9, mastery_label="mastered")
    mock_snapshot = SimpleNamespace(
        snapshot_at=now,
        mastery_score=0.8,
        mastery_label="proficient",
        trigger="quiz_submit",
    )
    with patch("app.services.learner_service.MasteryRepository.get_topic_mastery", AsyncMock(return_value=mock_topic_mastery)), \
         patch("app.services.learner_service.MasteryRepository.get_snapshots_for_learner_topic", AsyncMock(return_value=[mock_snapshot])):
        res_topic = await service.get_topic_mastery("l1", "CAPS.M.1")
        assert res_topic["mastery"]["mastery_score"] == 0.9
        assert len(res_topic["timeline"]) == 1

    # 6. get_subject_mastery_summary (lines 102-127)
    mock_repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as exc:
        await service.get_subject_mastery_summary("unknown")
    assert exc.value.status_code == 404

    mock_repo.get_by_id.return_value = mock_learner
    mock_sci_row = SimpleNamespace(caps_ref="CAPS.SCI.1", mastery_score=0.7)
    mock_nodot_row = SimpleNamespace(caps_ref="NODOT", mastery_score=0.6)
    with patch("app.services.learner_service.MasteryRepository.list_topic_mastery_by_learner", AsyncMock(return_value=[mock_mastery_row, mock_sci_row, mock_nodot_row])), \
         patch("app.modules.progress.learning_velocity_service.LearningVelocityService.next_best_activities", return_value=["act-1"]):
        # With subject filter (hits line 115 continue)
        res_summary = await service.get_subject_mastery_summary("l1", subject="MATH")
        assert res_summary["learner_id"] == "l1"
        assert res_summary["subjects"][0]["subject_code"] == "MATH"

        # Without subject filter (hits else 'unknown')
        res_summary_all = await service.get_subject_mastery_summary("l1")
        codes = [s["subject_code"] for s in res_summary_all["subjects"]]
        assert "unknown" in codes

    # 7. request_erasure (lines 129-160)
    mock_repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as exc:
        await service.request_erasure("unknown", {"sub": "g1"})
    assert exc.value.status_code == 404

    # Unauthorized
    mock_repo.get_by_id.return_value = mock_learner
    with pytest.raises(HTTPException) as exc:
        await service.request_erasure("l1", {"sub": "wrong_guardian", "role": "learner"})
    assert exc.value.status_code == 403

    # Authorized (admin or guardian)
    with patch("app.services.learner_service.ConsentService") as mock_consent_cls, \
         patch("app.services.learner_service.AuditService") as mock_audit_cls:
        mock_consent = AsyncMock()
        mock_consent_cls.return_value = mock_consent
        mock_audit = AsyncMock()
        mock_audit_cls.return_value = mock_audit

        lid, pseudo = await service.request_erasure("l1", {"sub": "admin_user", "role": "admin"})
        assert lid == "l1"
        assert pseudo == "pseudo-1"
        mock_repo.soft_delete.assert_awaited_once_with("l1")
        mock_consent.execute_erasure.assert_awaited_once_with("admin_user", "l1")
        mock_audit.record.assert_awaited_once()

    # 8. process_onboarding (lines 162-179)
    mock_repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as exc:
        await service.process_onboarding("unknown", [])
    assert exc.value.status_code == 404

    mock_repo.get_by_id.return_value = mock_learner
    mock_archetype_enum = SimpleNamespace(value="explorer")
    with patch("app.services.archetype_service.ArchetypeService.classify_archetype", return_value=(mock_archetype_enum, "Explorer archetype", {"explorer": 0.8})):
        res_onboard = await service.process_onboarding("l1", [{"q": 1, "a": "A"}])
        assert res_onboard["archetype"] == "explorer"
        assert res_onboard["description"] == "Explorer archetype"
        mock_repo.update_archetype.assert_awaited_once_with("l1", "explorer")

