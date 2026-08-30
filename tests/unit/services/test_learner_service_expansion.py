"""Batch 212 — LearnerService coverage expansion.

Covers all missing lines in app/services/learner_service.py:
  lines 22, 30-46, 58-85, 88-99
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_service(repository=None):
    """Construct LearnerService with an injected mock repository."""
    from app.services.learner_service import LearnerService

    db = AsyncMock()
    svc = LearnerService(db=db, repository=repository)
    return svc


def _mock_learner(learner_id="learner-1", guardian_id="guardian-1", pseudonym_id="pseudo-1"):
    m = MagicMock()
    m.learner_id = learner_id
    m.guardian_id = guardian_id
    m.pseudonym_id = pseudonym_id
    return m


def _mock_mastery_row(caps_ref="MATH.GR4.NUM", mastery_score=0.85, mastery_label="Proficient", last_updated_at=None, trigger="assessment"):
    from datetime import datetime, timezone
    m = MagicMock()
    m.caps_ref = caps_ref
    m.mastery_score = mastery_score
    m.mastery_label = mastery_label
    m.last_updated_at = last_updated_at or datetime(2026, 8, 1, tzinfo=timezone.utc)
    m.trigger = trigger
    return m


def _mock_snapshot(snapshot_at=None, mastery_score=0.8, mastery_label="Developing", trigger="practice"):
    from datetime import datetime, timezone
    m = MagicMock()
    m.snapshot_at = snapshot_at or datetime(2026, 7, 1, tzinfo=timezone.utc)
    m.mastery_score = mastery_score
    m.mastery_label = mastery_label
    m.trigger = trigger
    return m


def _mock_gap(subject="MATH", severity=0.5):
    m = MagicMock()
    m.subject = subject
    m.severity = severity
    return m


# ---------------------------------------------------------------------------
# get_learner_summary
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_learner_summary_delegates_to_repo():
    repo = AsyncMock()
    learner = _mock_learner()
    repo.get_by_id.return_value = learner
    svc = _make_service(repository=repo)
    result = await svc.get_learner_summary("learner-1")
    repo.get_by_id.assert_awaited_once_with("learner-1")
    assert result is learner


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_learner_summary_returns_none_when_not_found():
    repo = AsyncMock()
    repo.get_by_id.return_value = None
    svc = _make_service(repository=repo)
    result = await svc.get_learner_summary("nonexistent")
    assert result is None


# ---------------------------------------------------------------------------
# list_by_guardian
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_list_by_guardian_delegates():
    repo = AsyncMock()
    repo.get_by_guardian.return_value = [_mock_learner()]
    svc = _make_service(repository=repo)
    result = await svc.list_by_guardian("guardian-1")
    repo.get_by_guardian.assert_awaited_once_with("guardian-1")
    assert len(result) == 1


# ---------------------------------------------------------------------------
# create_learner
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_learner_delegates_to_repo():
    repo = AsyncMock()
    learner = _mock_learner()
    repo.create.return_value = learner
    svc = _make_service(repository=repo)
    result = await svc.create_learner(
        guardian_id="guardian-1",
        display_name="Thabo",
        grade=4,
        language="en",
    )
    repo.create.assert_awaited_once_with(
        guardian_id="guardian-1",
        display_name="Thabo",
        grade=4,
        language="en",
    )
    assert result is learner


# ---------------------------------------------------------------------------
# get_mastery — with mastery rows
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_mastery_returns_mastery_rows_when_present():
    repo = AsyncMock()
    repo.get_by_id.return_value = _mock_learner()
    svc = _make_service(repository=repo)

    row = _mock_mastery_row(caps_ref="MATH.GR4.NUM", mastery_score=0.85, mastery_label="Proficient")

    with (
        patch("app.services.learner_service.ConsentService") as MockConsent,
        patch("app.services.learner_service.MasteryRepository") as MockMastery,
    ):
        consent_inst = AsyncMock()
        MockConsent.return_value = consent_inst
        mastery_inst = AsyncMock()
        mastery_inst.list_topic_mastery_by_learner.return_value = [row]
        MockMastery.return_value = mastery_inst

        result = await svc.get_mastery("learner-1", actor_id="actor-x")

    assert result["learner_id"] == "learner-1"
    assert len(result["mastery"]) == 1
    assert result["mastery"][0]["caps_ref"] == "MATH.GR4.NUM"
    assert result["mastery"][0]["mastery_score"] == 0.85
    assert "last_updated_at" in result["mastery"][0]
    consent_inst.require_active_consent.assert_awaited_once_with("learner-1", actor_id="actor-x")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_mastery_raises_404_when_learner_missing():
    from fastapi import HTTPException

    repo = AsyncMock()
    repo.get_by_id.return_value = None
    svc = _make_service(repository=repo)

    with (
        patch("app.services.learner_service.ConsentService") as MockConsent,
        patch("app.services.learner_service.MasteryRepository"),
    ):
        consent_inst = AsyncMock()
        MockConsent.return_value = consent_inst

        with pytest.raises(HTTPException) as exc_info:
            await svc.get_mastery("nonexistent")

    assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# get_mastery — without mastery rows (gap-based fallback)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_mastery_falls_back_to_gap_based_scores():
    repo = AsyncMock()
    repo.get_by_id.return_value = _mock_learner()
    svc = _make_service(repository=repo)

    gap = _mock_gap(subject="MATH", severity=0.5)

    with (
        patch("app.services.learner_service.ConsentService") as MockConsent,
        patch("app.services.learner_service.MasteryRepository") as MockMastery,
        patch("app.services.learner_service.KnowledgeGapRepository") as MockGap,
    ):
        MockConsent.return_value = AsyncMock()
        mastery_inst = AsyncMock()
        mastery_inst.list_topic_mastery_by_learner.return_value = []  # No mastery rows
        MockMastery.return_value = mastery_inst

        gap_inst = AsyncMock()
        gap_inst.get_active_gaps.return_value = [gap]
        MockGap.return_value = gap_inst

        result = await svc.get_mastery("learner-1")

    assert result["learner_id"] == "learner-1"
    subjects = {entry["subject_code"]: entry["mastery_score"] for entry in result["mastery"]}
    # MATH should be reduced by gap
    assert "MATH" in subjects
    assert subjects["MATH"] < 0.72  # baseline was 0.72, gap reduces it
    assert subjects["MATH"] >= 0.15  # minimum floor enforced


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_mastery_gap_based_clamps_to_floor():
    repo = AsyncMock()
    repo.get_by_id.return_value = _mock_learner()
    svc = _make_service(repository=repo)

    # Extreme severity gap — should clamp to 0.15
    gap = _mock_gap(subject="MATH", severity=5.0)

    with (
        patch("app.services.learner_service.ConsentService") as MockConsent,
        patch("app.services.learner_service.MasteryRepository") as MockMastery,
        patch("app.services.learner_service.KnowledgeGapRepository") as MockGap,
    ):
        MockConsent.return_value = AsyncMock()
        mastery_inst = AsyncMock()
        mastery_inst.list_topic_mastery_by_learner.return_value = []
        MockMastery.return_value = mastery_inst

        gap_inst = AsyncMock()
        gap_inst.get_active_gaps.return_value = [gap]
        MockGap.return_value = gap_inst

        result = await svc.get_mastery("learner-1")

    subjects = {e["subject_code"]: e["mastery_score"] for e in result["mastery"]}
    assert subjects["MATH"] == 0.15


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_mastery_gap_subject_not_in_defaults_uses_baseline():
    repo = AsyncMock()
    repo.get_by_id.return_value = _mock_learner()
    svc = _make_service(repository=repo)

    gap = _mock_gap(subject="HIST", severity=0.2)  # Not in default_subjects

    with (
        patch("app.services.learner_service.ConsentService") as MockConsent,
        patch("app.services.learner_service.MasteryRepository") as MockMastery,
        patch("app.services.learner_service.KnowledgeGapRepository") as MockGap,
    ):
        MockConsent.return_value = AsyncMock()
        mastery_inst = AsyncMock()
        mastery_inst.list_topic_mastery_by_learner.return_value = []
        MockMastery.return_value = mastery_inst

        gap_inst = AsyncMock()
        gap_inst.get_active_gaps.return_value = [gap]
        MockGap.return_value = gap_inst

        result = await svc.get_mastery("learner-1")

    subjects = {e["subject_code"]: e["mastery_score"] for e in result["mastery"]}
    # HIST should appear with gap-adjusted value from 0.7 baseline
    assert "HIST" in subjects
    assert 0.15 <= subjects["HIST"] <= 0.98


# ---------------------------------------------------------------------------
# get_topic_mastery
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_topic_mastery_returns_mastery_and_timeline():
    repo = AsyncMock()
    repo.get_by_id.return_value = _mock_learner()
    svc = _make_service(repository=repo)

    mastery_obj = MagicMock(mastery_score=0.9, mastery_label="Advanced")
    snap = _mock_snapshot(mastery_score=0.75, mastery_label="Developing", trigger="assessment")

    with patch("app.services.learner_service.MasteryRepository") as MockMastery:
        mastery_inst = AsyncMock()
        mastery_inst.get_topic_mastery.return_value = mastery_obj
        mastery_inst.get_snapshots_for_learner_topic.return_value = [snap]
        MockMastery.return_value = mastery_inst

        result = await svc.get_topic_mastery("learner-1", "MATH.GR4.NUM")

    assert result["learner_id"] == "learner-1"
    assert result["caps_ref"] == "MATH.GR4.NUM"
    assert result["mastery"]["mastery_score"] == 0.9
    assert len(result["timeline"]) == 1
    assert result["timeline"][0]["trigger"] == "assessment"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_topic_mastery_raises_404_when_learner_missing():
    from fastapi import HTTPException

    repo = AsyncMock()
    repo.get_by_id.return_value = None
    svc = _make_service(repository=repo)

    with pytest.raises(HTTPException) as exc_info:
        await svc.get_topic_mastery("nonexistent", "MATH.GR4.NUM")

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_topic_mastery_returns_none_mastery_when_no_mastery():
    repo = AsyncMock()
    repo.get_by_id.return_value = _mock_learner()
    svc = _make_service(repository=repo)

    with patch("app.services.learner_service.MasteryRepository") as MockMastery:
        mastery_inst = AsyncMock()
        mastery_inst.get_topic_mastery.return_value = None
        mastery_inst.get_snapshots_for_learner_topic.return_value = []
        MockMastery.return_value = mastery_inst

        result = await svc.get_topic_mastery("learner-1", "MATH.GR4.NUM")

    assert result["mastery"] is None
    assert result["timeline"] == []


# ---------------------------------------------------------------------------
# get_subject_mastery_summary
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_subject_mastery_summary_groups_by_subject():
    repo = AsyncMock()
    repo.get_by_id.return_value = _mock_learner()
    svc = _make_service(repository=repo)

    row1 = _mock_mastery_row(caps_ref="MATH.GR4.NUM", mastery_score=0.8)
    row2 = _mock_mastery_row(caps_ref="MATH.GR4.ALG", mastery_score=0.9)

    with (
        patch("app.services.learner_service.MasteryRepository") as MockMastery,
        patch("app.modules.progress.learning_velocity_service.LearningVelocityService") as MockVelocity,
    ):
        mastery_inst = AsyncMock()
        mastery_inst.list_topic_mastery_by_learner.return_value = [row1, row2]
        MockMastery.return_value = mastery_inst

        vel_inst = MagicMock()
        vel_inst.next_best_activities.return_value = ["practice_quiz"]
        MockVelocity.return_value = vel_inst

        result = await svc.get_subject_mastery_summary("learner-1")

    assert result["learner_id"] == "learner-1"
    assert "subjects" in result


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_subject_mastery_summary_raises_404_when_not_found():
    from fastapi import HTTPException

    repo = AsyncMock()
    repo.get_by_id.return_value = None
    svc = _make_service(repository=repo)

    with pytest.raises(HTTPException) as exc_info:
        await svc.get_subject_mastery_summary("nonexistent")

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_subject_mastery_summary_filters_by_subject():
    repo = AsyncMock()
    repo.get_by_id.return_value = _mock_learner()
    svc = _make_service(repository=repo)

    # caps_ref.split('.')[1] yields 'GR4' as the group key, so filtering works at caps_ref level
    row1 = _mock_mastery_row(caps_ref="MATH.GR4.NUM", mastery_score=0.8)
    row2 = _mock_mastery_row(caps_ref="ENG.GR4.READ", mastery_score=0.7)

    with (
        patch("app.services.learner_service.MasteryRepository") as MockMastery,
        patch("app.modules.progress.learning_velocity_service.LearningVelocityService") as MockVelocity,
    ):
        mastery_inst = AsyncMock()
        mastery_inst.list_topic_mastery_by_learner.return_value = [row1, row2]
        MockMastery.return_value = mastery_inst

        vel_inst = MagicMock()
        vel_inst.next_best_activities.return_value = []
        MockVelocity.return_value = vel_inst

        # subject="MATH" filters to rows where "MATH" is in caps_ref
        result = await svc.get_subject_mastery_summary("learner-1", subject="MATH")

    # The filter reduces to only MATH rows so subjects list should be non-empty
    assert isinstance(result["subjects"], list)
    # groups are keyed by caps_ref.split('.')[1] (e.g. 'GR4') for MATH rows
    assert len(result["subjects"]) >= 1


# ---------------------------------------------------------------------------
# request_erasure
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_request_erasure_succeeds_as_guardian():
    repo = AsyncMock()
    learner = _mock_learner(learner_id="learner-1", guardian_id="guardian-1")
    repo.get_by_id.return_value = learner
    svc = _make_service(repository=repo)

    current_user = {"sub": "guardian-1", "role": "guardian"}

    with (
        patch("app.services.learner_service.ConsentService") as MockConsent,
        patch("app.services.learner_service.AuditService") as MockAudit,
    ):
        consent_inst = AsyncMock()
        MockConsent.return_value = consent_inst
        audit_inst = AsyncMock()
        MockAudit.return_value = audit_inst

        learner_id, pseudonym = await svc.request_erasure("learner-1", current_user)

    assert learner_id == "learner-1"
    assert pseudonym == "pseudo-1"
    consent_inst.execute_erasure.assert_awaited_once()
    repo.soft_delete.assert_awaited_once_with("learner-1")
    audit_inst.record.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_request_erasure_succeeds_as_admin():
    repo = AsyncMock()
    learner = _mock_learner(learner_id="learner-1", guardian_id="other-guardian")
    repo.get_by_id.return_value = learner
    svc = _make_service(repository=repo)

    current_user = {"sub": "admin-x", "role": "admin"}

    with (
        patch("app.services.learner_service.ConsentService") as MockConsent,
        patch("app.services.learner_service.AuditService") as MockAudit,
    ):
        MockConsent.return_value = AsyncMock()
        MockAudit.return_value = AsyncMock()

        learner_id, pseudonym = await svc.request_erasure("learner-1", current_user)

    assert learner_id == "learner-1"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_request_erasure_raises_403_for_unrelated_guardian():
    from fastapi import HTTPException

    repo = AsyncMock()
    learner = _mock_learner(guardian_id="other-guardian")
    repo.get_by_id.return_value = learner
    svc = _make_service(repository=repo)

    current_user = {"sub": "attacker", "role": "guardian"}

    with pytest.raises(HTTPException) as exc_info:
        await svc.request_erasure("learner-1", current_user)

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
@pytest.mark.unit
async def test_request_erasure_raises_404_when_learner_not_found():
    from fastapi import HTTPException

    repo = AsyncMock()
    repo.get_by_id.return_value = None
    svc = _make_service(repository=repo)

    with pytest.raises(HTTPException) as exc_info:
        await svc.request_erasure("nonexistent", {"sub": "x", "role": "guardian"})

    assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# process_onboarding
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_process_onboarding_returns_archetype():
    repo = AsyncMock()
    repo.get_by_id.return_value = _mock_learner()
    svc = _make_service(repository=repo)

    mock_archetype = MagicMock()
    mock_archetype.value = "visual_learner"

    with patch("app.services.archetype_service.ArchetypeService") as MockArchetype:
        arch_inst = MagicMock()
        arch_inst.classify_archetype.return_value = (mock_archetype, "Visual learner description", {"visual_learner": 0.85})
        MockArchetype.return_value = arch_inst

        result = await svc.process_onboarding("learner-1", [{"q": "a"}])

    assert result["archetype"] == "visual_learner"
    assert result["learner_id"] == "learner-1"
    assert "description" in result
    assert "probabilities" in result
    repo.update_archetype.assert_awaited_once_with("learner-1", "visual_learner")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_process_onboarding_raises_404_when_learner_missing():
    from fastapi import HTTPException

    repo = AsyncMock()
    repo.get_by_id.return_value = None
    svc = _make_service(repository=repo)

    with pytest.raises(HTTPException) as exc_info:
        await svc.process_onboarding("nonexistent", [])

    assert exc_info.value.status_code == 404
