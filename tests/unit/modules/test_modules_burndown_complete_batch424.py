"""Unit tests for Batch 424:
- app/modules/consent/service.py
- app/modules/lessons/parent_explanation_mode.py
- app/modules/lessons/teacher_insight_mode.py
- app/modules/lessons/caps_topic_map_service.py
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

# ---------------------------------------------------------------------------
# Target 1: app/modules/consent/service.py
# ---------------------------------------------------------------------------
from app.core.consent_policy import ConsentPolicyDecision
from app.core.exceptions import ConsentExpiredError, ConsentRequiredError
from app.models import ConsentState, ParentalConsent
from app.modules.consent.service import ConsentService
from app.utils.versioning import VersionChangeType


class TestConsentService:
    @pytest.mark.asyncio
    async def test_init_validation(self):
        # Neither db nor consent_repo provided
        with pytest.raises(ValueError, match="ConsentService requires a db session or consent_repo"):
            ConsentService(db=None, consent_repo=None)

        # db provided, auto-creates repos
        mock_db = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()
        svc = ConsentService(db=mock_db)
        assert svc._repo is not None
        assert svc._audit_repo is not None
        assert svc._required_policy_version == "1.0.0"

        # Explicit repos and custom version
        mock_repo = MagicMock()
        mock_audit = MagicMock()
        svc_custom = ConsentService(
            consent_repo=mock_repo,
            audit_repo=mock_audit,
            required_policy_version="2.0.0",
        )
        assert svc_custom._repo is mock_repo
        assert svc_custom._audit_repo is mock_audit
        assert svc_custom._required_policy_version == "2.0.0"

    @pytest.mark.asyncio
    async def test_consent_decision_none(self):
        mock_repo = AsyncMock()
        mock_repo.get_latest_for_learner.return_value = None
        svc = ConsentService(consent_repo=mock_repo)

        decision = await svc.consent_decision("learner-123")
        assert decision.active is False
        assert decision.learner_id == "learner-123"

    @pytest.mark.asyncio
    async def test_consent_decision_active_and_stale(self):
        mock_repo = AsyncMock()
        consent = MagicMock(spec=ParentalConsent)
        consent.policy_version = "1.0.0"
        consent.state = "granted"
        consent.status = "granted"
        consent.revoked_at = None
        consent.expires_at = None
        consent.granted_at = datetime.now(timezone.utc)
        mock_repo.get_latest_for_learner.return_value = consent

        svc = ConsentService(consent_repo=mock_repo, required_policy_version="2.0.0")
        with patch.object(svc, "_is_consent_stale", return_value=True):
            decision = await svc.consent_decision("learner-123")
            assert decision.active is False
            assert decision.state == ConsentState.RENEWAL_REQUIRED
            assert "stale" in decision.reason

    @pytest.mark.asyncio
    async def test_consent_decision_active_not_stale(self):
        mock_repo = AsyncMock()
        consent = MagicMock(spec=ParentalConsent)
        consent.policy_version = "1.0.0"
        consent.state = "granted"
        consent.status = "granted"
        consent.revoked_at = None
        consent.expires_at = None
        consent.granted_at = datetime.now(timezone.utc)
        mock_repo.get_latest_for_learner.return_value = consent

        svc = ConsentService(consent_repo=mock_repo, required_policy_version="1.0.0")
        with patch.object(svc, "_is_consent_stale", return_value=False):
            decision = await svc.consent_decision("learner-123")
            assert decision.active is True

    def test_is_consent_stale(self):
        mock_repo = MagicMock()
        svc = ConsentService(consent_repo=mock_repo, required_policy_version="2.0.0")
        # Major version difference -> stale
        assert svc._is_consent_stale("1.0.0") is True
        # Same version -> not stale
        assert svc._is_consent_stale("2.0.0") is False
        # Malformed version -> returns True
        assert svc._is_consent_stale("invalid-semver") is True

    def test_detect_version_change_type(self):
        mock_repo = MagicMock()
        svc = ConsentService(consent_repo=mock_repo)
        assert svc.detect_version_change_type("1.0.0", "1.0.1") == VersionChangeType.PATCH
        assert svc.detect_version_change_type("1.0.0", "1.1.0") == VersionChangeType.MINOR
        assert svc.detect_version_change_type("1.0.0", "2.0.0") == VersionChangeType.MAJOR
        # Invalid version fallback
        assert svc.detect_version_change_type("invalid", "2.0.0") == VersionChangeType.MAJOR

    @pytest.mark.asyncio
    async def test_require_active_consent_success(self):
        mock_repo = MagicMock()
        svc = ConsentService(consent_repo=mock_repo)
        active_decision = ConsentPolicyDecision(
            learner_id="l-1",
            state=ConsentState.GRANTED,
            active=True,
            reason="Consent granted",
        )
        with patch.object(svc, "consent_decision", return_value=active_decision):
            res = await svc.require_active_consent("l-1", actor_id="actor-1")
            assert res is active_decision

    @pytest.mark.asyncio
    async def test_require_active_consent_expired(self):
        mock_repo = MagicMock()
        svc = ConsentService(consent_repo=mock_repo)
        expired_decision = ConsentPolicyDecision(
            learner_id="l-1",
            state=ConsentState.EXPIRED,
            active=False,
            reason="Consent expired",
        )
        with patch.object(svc, "consent_decision", return_value=expired_decision):
            with patch.object(svc, "_append_audit", new_callable=AsyncMock) as mock_audit:
                with pytest.raises(ConsentExpiredError, match="Guardian consent has expired"):
                    await svc.require_active_consent("l-1", actor_id="actor-1")
                mock_audit.assert_called_once_with(
                    "consent.access_rejected",
                    actor_id="actor-1",
                    resource_id="l-1",
                    payload={"learner_id": "l-1", "reason": "Consent expired", "state": "expired"},
                )

    @pytest.mark.asyncio
    async def test_require_active_consent_missing(self):
        mock_repo = MagicMock()
        svc = ConsentService(consent_repo=mock_repo)
        missing_decision = ConsentPolicyDecision(
            learner_id="l-1",
            state=ConsentState.PENDING,
            active=False,
            reason="Consent pending",
        )
        with patch.object(svc, "consent_decision", return_value=missing_decision):
            with patch.object(svc, "_append_audit", new_callable=AsyncMock) as mock_audit:
                with pytest.raises(ConsentRequiredError, match="Active parental consent required"):
                    await svc.require_active_consent("l-1")
                mock_audit.assert_called_once()

    @pytest.mark.asyncio
    async def test_grant(self):
        mock_repo = AsyncMock()
        mock_consent = MagicMock(spec=ParentalConsent)
        mock_consent.id = "consent-123"
        mock_repo.grant.return_value = mock_consent

        svc = ConsentService(consent_repo=mock_repo)
        with patch.object(svc, "_append_audit", new_callable=AsyncMock) as mock_audit:
            with patch.object(svc, "_record_version_history", new_callable=AsyncMock) as mock_vh:
                res = await svc.grant(
                    guardian_id="g-1",
                    learner_id="l-1",
                    consent_version="1.0.0",
                    ip_address="127.0.0.1",
                    user_agent="pytest-agent",
                )
                assert res is mock_consent
                mock_repo.grant.assert_called_once_with(
                    learner_id="l-1",
                    guardian_id="g-1",
                    consent_version="1.0.0",
                    ip_address="127.0.0.1",
                    user_agent="pytest-agent",
                    state="granted",
                )
                mock_audit.assert_called_once_with(
                    "consent.granted",
                    actor_id="g-1",
                    resource_id="consent-123",
                    payload={"learner_id": "l-1", "consent_version": "1.0.0", "state": "granted"},
                )
                mock_vh.assert_called_once_with(mock_consent, "granted", "initial_grant")

    @pytest.mark.asyncio
    async def test_grant_with_ip_hash_fallback(self):
        mock_repo = AsyncMock()
        mock_consent = MagicMock(spec=ParentalConsent)
        mock_consent.id = "consent-456"
        mock_repo.grant.return_value = mock_consent

        svc = ConsentService(consent_repo=mock_repo)
        with patch.object(svc, "_append_audit", new_callable=AsyncMock):
            with patch.object(svc, "_record_version_history", new_callable=AsyncMock):
                await svc.grant(
                    guardian_id="g-1",
                    learner_id="l-1",
                    consent_version="1.0.0",
                    ip_hash="hash-123",
                )
                mock_repo.grant.assert_called_once_with(
                    learner_id="l-1",
                    guardian_id="g-1",
                    consent_version="1.0.0",
                    ip_address="hash-123",
                    user_agent=None,
                    state="granted",
                )

    @pytest.mark.asyncio
    async def test_revoke_active_found(self):
        mock_repo = AsyncMock()
        mock_active = MagicMock(spec=ParentalConsent)
        mock_active.id = "consent-99"
        mock_repo.get_active.return_value = mock_active
        mock_repo.revoke.return_value = 1

        svc = ConsentService(consent_repo=mock_repo)
        with patch.object(svc, "_append_audit", new_callable=AsyncMock) as mock_audit:
            with patch.object(svc, "_record_version_history", new_callable=AsyncMock) as mock_vh:
                count = await svc.revoke("l-1", guardian_id="g-1", reason="test_revocation")
                assert count == 1
                mock_audit.assert_called_once_with(
                    "consent.revoked",
                    actor_id="g-1",
                    resource_id="consent-99",
                    payload={"learner_id": "l-1", "reason": "test_revocation", "state": "withdrawn"},
                )
                mock_vh.assert_called_once_with(mock_active, "withdrawn", "test_revocation")

    @pytest.mark.asyncio
    async def test_revoke_no_active(self):
        mock_repo = AsyncMock()
        mock_repo.get_active.return_value = None
        mock_repo.revoke.return_value = 0

        svc = ConsentService(consent_repo=mock_repo)
        with patch.object(svc, "_append_audit", new_callable=AsyncMock) as mock_audit:
            with patch.object(svc, "_record_version_history", new_callable=AsyncMock) as mock_vh:
                count = await svc.revoke("l-1")
                assert count == 0
                mock_audit.assert_not_called()
                mock_vh.assert_not_called()

    @pytest.mark.asyncio
    async def test_renew(self):
        mock_repo = AsyncMock()
        prev_consent = MagicMock(spec=ParentalConsent, policy_version="1.0.0")
        renewed_consent = MagicMock(spec=ParentalConsent, id="consent-renewed")
        mock_repo.get_latest_for_learner.return_value = prev_consent
        mock_repo.renew.return_value = (prev_consent, renewed_consent)

        svc = ConsentService(consent_repo=mock_repo)
        with patch.object(svc, "_append_audit", new_callable=AsyncMock) as mock_audit:
            with patch.object(svc, "_record_version_history", new_callable=AsyncMock) as mock_vh:
                res = await svc.renew("g-1", "l-1", "1.1.0")
                assert res is renewed_consent
                mock_audit.assert_called_once()
                call_args = mock_audit.call_args[1]
                assert call_args["actor_id"] == "g-1"
                assert call_args["resource_id"] == "consent-renewed"
                assert call_args["payload"]["change_type"] == "minor"
                mock_vh.assert_called_once_with(renewed_consent, "granted", "renewed_from_1.0.0")

    @pytest.mark.asyncio
    async def test_renew_no_previous(self):
        mock_repo = AsyncMock()
        renewed_consent = MagicMock(spec=ParentalConsent, id="consent-fresh")
        mock_repo.get_latest_for_learner.return_value = None
        mock_repo.renew.return_value = (None, renewed_consent)

        svc = ConsentService(consent_repo=mock_repo)
        with patch.object(svc, "_append_audit", new_callable=AsyncMock):
            with patch.object(svc, "_record_version_history", new_callable=AsyncMock):
                res = await svc.renew("g-1", "l-1", "1.0.0")
                assert res is renewed_consent

    @pytest.mark.asyncio
    async def test_execute_erasure(self):
        mock_repo = AsyncMock()
        svc = ConsentService(consent_repo=mock_repo)
        with patch.object(svc, "revoke", new_callable=AsyncMock) as mock_revoke:
            with patch.object(svc, "_append_audit", new_callable=AsyncMock) as mock_audit:
                await svc.execute_erasure("g-1", "l-1")
                mock_revoke.assert_called_once_with("l-1", guardian_id="g-1", reason="erasure_requested")
                mock_audit.assert_called_once_with(
                    "consent.erasure_requested",
                    actor_id="g-1",
                    resource_id="l-1",
                    payload={"learner_id": "l-1"},
                )

    @pytest.mark.asyncio
    async def test_get_status_and_expiring(self):
        mock_repo = AsyncMock()
        mock_repo.get_latest_for_learner.return_value = "status-mock"
        mock_repo.get_expiring_soon.return_value = ["expiring-1", "expiring-2"]

        svc = ConsentService(consent_repo=mock_repo)
        assert await svc.get_status("l-1") == "status-mock"
        assert await svc.get_expiring_consents(days=14) == ["expiring-1", "expiring-2"]
        mock_repo.get_expiring_soon.assert_called_once_with(None, days=14)

    @pytest.mark.asyncio
    async def test_append_audit_paths(self):
        # 1. Audit repo path
        mock_repo = MagicMock()
        mock_audit = AsyncMock()
        svc1 = ConsentService(consent_repo=mock_repo, audit_repo=mock_audit)
        await svc1._append_audit("event.1", actor_id="a1", resource_id="r1", payload={"foo": "bar"})
        mock_audit.append.assert_called_once_with(
            event_type="event.1", actor_id="a1", resource_id="r1", payload={"foo": "bar"}
        )

        # 2. FourthEstate fallback path
        mock_db = AsyncMock()
        svc2 = ConsentService(consent_repo=mock_repo, audit_repo=mock_audit, db=mock_db)
        svc2._audit_repo = None  # Force None to test fallback
        with patch("app.modules.consent.service.FourthEstateService") as mock_fe_cls:
            mock_fe = AsyncMock()
            mock_fe_cls.return_value = mock_fe
            await svc2._append_audit("event.2", actor_id="a2", resource_id="r2", payload={"baz": "qux"})
            mock_fe_cls.assert_called_once_with(mock_db)
            mock_fe.record.assert_called_once_with(
                event_type="event.2", actor_id="a2", payload={"baz": "qux"}
            )

        # 3. Neither audit_repo nor db
        svc3 = ConsentService(consent_repo=mock_repo, audit_repo=None, db=None)
        await svc3._append_audit("event.3", actor_id="a3", resource_id="r3", payload={})

    @pytest.mark.asyncio
    async def test_record_version_history(self):
        mock_repo = MagicMock()
        # db is None -> no-op
        svc_no_db = ConsentService(consent_repo=mock_repo, db=None)
        await svc_no_db._record_version_history(MagicMock(), "granted", "reason")

        # db is present -> add & flush
        mock_db = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()
        svc_db = ConsentService(consent_repo=mock_repo, db=mock_db)
        consent = MagicMock(spec=ParentalConsent)
        consent.id = "c-1"
        consent.policy_version = "1.0.0"
        consent.granted_at = datetime.now(timezone.utc)
        consent.expires_at = None
        consent.revoked_at = None

        await svc_db._record_version_history(consent, "granted", "initial")
        mock_db.add.assert_called_once()
        mock_db.flush.assert_called_once()


# ---------------------------------------------------------------------------
# Target 2: app/modules/lessons/parent_explanation_mode.py
# ---------------------------------------------------------------------------
from app.modules.lessons.parent_explanation_mode import (
    LearnerSessionPerformance,
    ParentSummaryBullet,
    ParentSummaryGenerationError,
    ParentSummaryRequest,
    ParentSummaryResponse,
    build_parent_summary_prompt,
    generate_parent_summary,
)


class TestParentExplanationMode:
    @staticmethod
    def _make_sample_request(lesson_id=None, **kwargs) -> ParentSummaryRequest:
        lid = lesson_id or uuid4()
        return ParentSummaryRequest(
            lesson_id=lid,
            caps_ref="4.M.1.1.1",
            topic="Numbers",
            subtopic="Place Value",
            grade=4,
            subject="Mathematics",
            difficulty_level="medium",
            learning_objectives=["Identify thousands", "Round to nearest ten"],
            performance=LearnerSessionPerformance(
                learner_id=uuid4(),
                lesson_id=lid,
                caps_ref="4.M.1.1.1",
                topic="Numbers",
                subtopic="Place Value",
                grade=4,
                questions_attempted=5,
                questions_correct=4,
                time_spent_seconds=180,
                triggered_misconception_tags=["place_value_confusion", "zero_as_placeholder"],
                learner_self_reported_difficulty="hard",
            ),
            learner_first_name="Thabo",
            **kwargs,
        )

    def test_build_parent_summary_prompt_comprehensive(self):
        req1 = self._make_sample_request()
        prompt1 = build_parent_summary_prompt(req1)
        assert "Thabo" in prompt1
        assert "Score         : 4/5 (80%)" in prompt1
        assert "Time on task  : approximately 3 minute(s)" in prompt1
        assert "The learner said the lesson felt: hard." in prompt1
        assert "Place Value Confusion" in prompt1

        # Fallback: No learner name, 0 attempted questions, no tags
        req2 = ParentSummaryRequest(
            lesson_id=uuid4(),
            caps_ref="4.M.1.1.1",
            topic="Numbers",
            subtopic="Place Value",
            grade=4,
            subject="Mathematics",
            difficulty_level="easy",
            learning_objectives=["Counting"],
            performance=LearnerSessionPerformance(
                learner_id=uuid4(),
                lesson_id=uuid4(),
                caps_ref="4.M.1.1.1",
                topic="Numbers",
                subtopic="Place Value",
                grade=4,
                questions_attempted=0,
                questions_correct=0,
                time_spent_seconds=45,
                triggered_misconception_tags=[],
                learner_self_reported_difficulty=None,
            ),
            learner_first_name=None,
        )
        prompt2 = build_parent_summary_prompt(req2)
        assert "your child" in prompt2
        assert "Score         : 0/0 (0%)" in prompt2

    @pytest.mark.asyncio
    async def test_generate_parent_summary_success(self):
        req = self._make_sample_request()
        valid_payload = {
            "bullets": [
                {"heading": "Practice", "body": "Practiced counting numbers.", "emoji": "📚"},
                {"heading": "Tricky part", "body": "Worked on zero placeholder.", "emoji": "🤔"},
                {"heading": "Home activity", "body": "Count bottle caps together.", "emoji": "🏠"},
            ],
            "home_activity_suggestion": "Use 10 beans to count in groups.",
            "encouragement_note": "Great persistence and careful thinking!",
        }

        gateway = AsyncMock()
        # Wrap in ```json markdown fence to test stripping logic
        gateway.complete.return_value = f"```json\n{json.dumps(valid_payload)}\n```"

        res = await generate_parent_summary(req, gateway)
        assert isinstance(res, ParentSummaryResponse)
        assert res.lesson_id == req.lesson_id
        assert len(res.bullets) == 3
        assert res.home_activity_suggestion == "Use 10 beans to count in groups."
        assert res.encouragement_note == "Great persistence and careful thinking!"

    @pytest.mark.asyncio
    async def test_generate_parent_summary_gateway_error(self):
        req = self._make_sample_request()
        gateway = AsyncMock()
        gateway.complete.side_effect = RuntimeError("API unavailable")

        with pytest.raises(ParentSummaryGenerationError, match="LLM gateway call failed"):
            await generate_parent_summary(req, gateway)

    @pytest.mark.asyncio
    async def test_generate_parent_summary_non_json(self):
        req = self._make_sample_request()
        gateway = AsyncMock()
        gateway.complete.return_value = "Sorry, I am unable to generate a response."

        with pytest.raises(ParentSummaryGenerationError, match="LLM returned non-JSON parent summary"):
            await generate_parent_summary(req, gateway)

    @pytest.mark.asyncio
    async def test_generate_parent_summary_invalid_bullet_count(self):
        req = self._make_sample_request()
        gateway = AsyncMock()
        bad_payload = {
            "bullets": [
                {"heading": "One", "body": "Single bullet", "emoji": "📚"},
            ],
            "home_activity_suggestion": "Count beans.",
            "encouragement_note": "Good job.",
        }
        gateway.complete.return_value = json.dumps(bad_payload)

        with pytest.raises(ParentSummaryGenerationError, match="Parent summary schema validation failed"):
            await generate_parent_summary(req, gateway)

    @pytest.mark.asyncio
    async def test_generate_parent_summary_missing_fields(self):
        req = self._make_sample_request()
        gateway = AsyncMock()
        gateway.complete.return_value = json.dumps({"bullets": []})

        with pytest.raises(ParentSummaryGenerationError, match="Parent summary schema validation failed"):
            await generate_parent_summary(req, gateway)


# ---------------------------------------------------------------------------
# Target 3: app/modules/lessons/teacher_insight_mode.py
# ---------------------------------------------------------------------------
from app.modules.lessons.teacher_insight_mode import (
    InterventionGroup,
    LearnerMisconceptionRecord,
    MisconceptionCluster,
    TeacherInsightGenerationError,
    TeacherInsightRequest,
    TeacherInsightResponse,
    _recommend_variant_for_tag,
    aggregate_cohort_misconceptions,
    build_intervention_groups,
    build_teacher_insight_prompt,
    generate_teacher_insight,
)


class TestTeacherInsightMode:
    @staticmethod
    def _make_sample_request() -> TeacherInsightRequest:
        learner_id = uuid4()
        return TeacherInsightRequest(
            teacher_id=uuid4(),
            caps_ref="4.M.1.1",
            topic="Numbers",
            subtopic="Operations",
            grade=4,
            subject="Mathematics",
            cohort_label="Grade 4A",
            learner_records=[
                LearnerMisconceptionRecord(
                    learner_id=learner_id,
                    misconception_tags=["place_value_confusion"],
                    questions_correct=4,
                    questions_attempted=5,
                    last_session_at=datetime.now(timezone.utc),
                )
            ],
        )

    def test_aggregate_cohort_misconceptions(self):
        l1 = uuid4()
        l2 = uuid4()
        records = [
            LearnerMisconceptionRecord(
                learner_id=l1,
                misconception_tags=["place_value_confusion", "conflates_factors_multiples"],
                questions_correct=4,
                questions_attempted=5,
                last_session_at=datetime.now(timezone.utc),
            ),
            LearnerMisconceptionRecord(
                learner_id=l2,
                misconception_tags=["place_value_confusion", "spatial_reasoning"],
                questions_correct=1,
                questions_attempted=5,
                last_session_at=datetime.now(timezone.utc),
            ),
            LearnerMisconceptionRecord(
                learner_id=uuid4(),
                misconception_tags=[],
                questions_correct=0,
                questions_attempted=0,
                last_session_at=datetime.now(timezone.utc),
            ),
        ]
        req = TeacherInsightRequest(
            teacher_id=uuid4(),
            caps_ref="4.M.1.1",
            topic="Numbers",
            subtopic="Operations",
            grade=4,
            subject="Mathematics",
            cohort_label="Grade 4A",
            learner_records=records,
        )

        agg = aggregate_cohort_misconceptions(req)
        assert agg["total_learners"] == 3
        # Scores: 80%, 20%, 0% -> avg = 100/3 = 33.3%
        assert agg["class_avg"] == 33.3
        assert agg["below_70"] == 2
        assert "place_value_confusion" in agg["top_tags"]
        assert agg["tag_counts"]["place_value_confusion"] == 2
        assert len(agg["tag_to_learners"]["place_value_confusion"]) == 2

    def test_recommend_variant_for_tag(self):
        assert _recommend_variant_for_tag("place_value_confusion") == "misconception_correction"
        assert _recommend_variant_for_tag("conflates_terms") == "misconception_correction"
        assert _recommend_variant_for_tag("multiplication_fluency") == "practice_drill"
        assert _recommend_variant_for_tag("slow_recall") == "practice_drill"
        assert _recommend_variant_for_tag("long_division_procedure") == "worked_example_focus"
        assert _recommend_variant_for_tag("carry_error") == "worked_example_focus"
        assert _recommend_variant_for_tag("borrow_confusion") == "misconception_correction"  # confusion matches first
        assert _recommend_variant_for_tag("borrow_issue") == "worked_example_focus"
        assert _recommend_variant_for_tag("visual_fractions") == "visual"
        assert _recommend_variant_for_tag("shape_properties") == "visual"
        assert _recommend_variant_for_tag("spatial_awareness") == "visual"
        assert _recommend_variant_for_tag("general_error") == "re_explain"
        assert _recommend_variant_for_tag("unknown_error") == "step_by_step"

    def test_build_intervention_groups(self):
        l1, l2, l3, l4, l5 = [uuid4() for _ in range(5)]
        tag_to_learners = {
            "high_prev_tag": [l1, l2, l3],
            "med_prev_tag": [l4],
            "low_prev_tag": [l5],
        }
        tag_counts = {
            "high_prev_tag": 3,
            "med_prev_tag": 1,
            "low_prev_tag": 1,
        }
        groups = build_intervention_groups(tag_to_learners, tag_counts, total_learners=5)
        assert len(groups) == 3
        assert groups[0].priority == "high"
        assert groups[1].priority == "medium"
        assert groups[0].group_label.startswith("Group A")

        # Test low priority with total_learners=10
        groups_low = build_intervention_groups(tag_to_learners, tag_counts, total_learners=10)
        assert groups_low[1].priority == "low"  # 1/10 = 10% < 20%

    def test_build_teacher_insight_prompt(self):
        req = self._make_sample_request()
        agg_with_tags = {
            "total_learners": 1,
            "class_avg": 100.0,
            "below_70": 0,
            "tag_counts": {"place_value_confusion": 1},
        }
        p1 = build_teacher_insight_prompt(req, agg_with_tags)
        assert "Place Value Confusion" in p1

        agg_no_tags = {
            "total_learners": 1,
            "class_avg": 100.0,
            "below_70": 0,
            "tag_counts": {},
        }
        p2 = build_teacher_insight_prompt(req, agg_no_tags)
        assert "No significant misconception patterns detected." in p2

    @pytest.mark.asyncio
    async def test_generate_teacher_insight_success(self):
        req = self._make_sample_request()
        llm_payload = {
            "misconception_clusters": [
                {
                    "misconception_tag": "place_value_confusion",
                    "plain_language_description": "Learners swap tens and hundreds columns.",
                    "suggested_intervention": "Use base-10 blocks to demonstrate place value.",
                    "suggested_next_caps_ref": "3.M.1.1",
                }
            ],
            "whole_class_teaching_note": "Overall solid performance with minor column confusion.",
            "printable_summary": "The Grade 4A cohort completed number operations successfully.",
        }

        gateway = AsyncMock()
        gateway.complete.return_value = f"```json\n{json.dumps(llm_payload)}\n```"

        res = await generate_teacher_insight(req, gateway)
        assert isinstance(res, TeacherInsightResponse)
        assert res.caps_ref == "4.M.1.1"
        assert len(res.misconception_clusters) == 1
        assert res.misconception_clusters[0].misconception_tag == "place_value_confusion"
        assert res.misconception_clusters[0].prevalence_pct == 100.0
        assert len(res.intervention_groups) == 1
        assert res.intervention_groups[0].intervention_note == "Use base-10 blocks to demonstrate place value."

    @pytest.mark.asyncio
    async def test_generate_teacher_insight_gateway_error(self):
        req = self._make_sample_request()
        gateway = AsyncMock()
        gateway.complete.side_effect = RuntimeError("API failed")

        with pytest.raises(TeacherInsightGenerationError, match="LLM call failed"):
            await generate_teacher_insight(req, gateway)

    @pytest.mark.asyncio
    async def test_generate_teacher_insight_unmatched_cluster(self):
        req = self._make_sample_request()
        # clusters does not match the group's misconception tag
        llm_payload = {
            "misconception_clusters": [
                {
                    "misconception_tag": "different_tag",
                    "plain_language_description": "Different misconception.",
                    "suggested_intervention": "Intervention text.",
                }
            ],
            "whole_class_teaching_note": "Teaching note.",
            "printable_summary": "Summary.",
        }

        gateway = AsyncMock()
        gateway.complete.return_value = json.dumps(llm_payload)

        res = await generate_teacher_insight(req, gateway)
        assert len(res.intervention_groups) == 1
        # intervention_note was not overwritten because no cluster matched
        assert "recommended approach" in res.intervention_groups[0].intervention_note.lower()

    @pytest.mark.asyncio
    async def test_generate_teacher_insight_non_json(self):
        req = self._make_sample_request()
        gateway = AsyncMock()
        gateway.complete.return_value = "Non-JSON response text"

        with pytest.raises(TeacherInsightGenerationError, match="LLM returned non-JSON teacher insight"):
            await generate_teacher_insight(req, gateway)


# ---------------------------------------------------------------------------
# Target 4: app/modules/lessons/caps_topic_map_service.py
# ---------------------------------------------------------------------------
from app.modules.lessons.caps_topic_map_service import (
    CAPSTopicMap,
    CAPSTopicMapService,
    SubtopicEntry,
    TermEntry,
    TopicEntry,
    TopicMapMeta,
    _discover_default_map_paths,
    get_caps_service,
    get_caps_topic_map_service,
)


class TestCAPSTopicMapService:
    def test_discover_default_map_paths(self):
        paths = _discover_default_map_paths()
        assert isinstance(paths, list)
        assert len(paths) > 0
        assert all(isinstance(p, Path) for p in paths)

    def test_caps_topic_map_dataclass(self):
        sub = SubtopicEntry(
            caps_ref="4.M.1.1.1",
            subtopic_index=1,
            subtopic="Counting",
            assessment_standards=["AS1"],
            prerequisites=["3.M.1.1.1"],
            common_misconceptions=["skip_count_error"],
        )
        top = TopicEntry(
            caps_ref="4.M.1.1",
            topic_index=1,
            topic="Numbers",
            subtopics=[sub],
        )
        term = TermEntry(
            term=1,
            weeks="1-2",
            topics=[top],
        )
        meta = TopicMapMeta(
            schema_version="1.0",
            scope="Grade 4 Maths",
            source="DBE CAPS",
            grade=4,
            subject="Mathematics",
            subject_code="M",
        )
        cmap = CAPSTopicMap(meta=meta, terms=[term])

        assert cmap.resolve("4.M.1.1") == top
        assert cmap.resolve("4.M.1.1.1") == sub
        assert cmap.resolve("invalid") is None
        assert "4.M.1.1" in cmap.all_refs
        assert "4.M.1.1.1" in cmap.all_refs

    def test_service_lifecycle_and_errors(self, tmp_path: Path):
        # 1. Non-existent path handling
        missing_path = tmp_path / "does_not_exist.json"
        svc = CAPSTopicMapService(map_paths=[missing_path])
        assert svc.summary()["maps_loaded"] == 0

        # 2. Corrupt JSON file handling
        bad_json = tmp_path / "bad.json"
        bad_json.write_text("{bad-json-content", encoding="utf-8")
        with pytest.raises(RuntimeError, match="Could not load CAPS topic map"):
            CAPSTopicMapService(map_paths=[bad_json])

        # 3. _ensure_loaded raises when not loaded
        svc_unloaded = CAPSTopicMapService(map_paths=[])
        svc_unloaded._loaded = False
        with pytest.raises(RuntimeError, match="load_maps\\(\\) has not been called"):
            svc_unloaded._ensure_loaded()

    def test_service_with_real_map_data(self):
        svc = CAPSTopicMapService()
        assert svc._loaded is True

        # Idempotent call
        svc.load_maps()
        assert svc._loaded is True

        # validate_caps_ref & is_valid_ref
        assert svc.validate_caps_ref("4.M.1.1") is True
        assert svc.is_valid_ref("4.M.1.1") is True
        assert svc.validate_caps_ref("99.Z.99.99") is False

        # get_topic_metadata
        top_meta = svc.get_topic_metadata("4.M.1.1")
        assert top_meta is not None
        assert isinstance(top_meta, TopicEntry)

        sub_meta = svc.get_topic_metadata("4.M.1.1.1")
        assert sub_meta is not None
        assert isinstance(sub_meta, SubtopicEntry)

        assert svc.get_topic_metadata("nonexistent") is None

        # get_assessment_standards
        standards_sub = svc.get_assessment_standards("4.M.1.1.1")
        assert isinstance(standards_sub, list)
        standards_top = svc.get_assessment_standards("4.M.1.1")
        assert standards_top == []

        # get_prerequisites
        prereqs_sub = svc.get_prerequisites("4.M.1.1.1")
        assert isinstance(prereqs_sub, list)
        assert svc.get_prerequisites("4.M.1.1") == []

        # get_misconceptions
        misc_sub = svc.get_misconceptions("4.M.1.1.1")
        assert isinstance(misc_sub, list)
        assert svc.get_misconceptions("4.M.1.1") == []

        # get_topic_context
        ctx_top = svc.get_topic_context("4.M.1.1")
        assert ctx_top is not None
        assert ctx_top["caps_ref"] == "4.M.1.1"
        assert ctx_top["grade"] == 4

        ctx_sub = svc.get_topic_context("4.M.1.1.1")
        assert ctx_sub is not None
        assert ctx_sub["caps_ref"] == "4.M.1.1.1"

        assert svc.get_topic_context("99.99.99") is None

        # iter_topic_contexts
        all_ctxs = svc.iter_topic_contexts()
        assert len(all_ctxs) > 0

        # With grade filter matching and non-matching
        g4_ctxs = svc.iter_topic_contexts(grade=4)
        assert len(g4_ctxs) > 0
        g9_ctxs = svc.iter_topic_contexts(grade=9)
        assert len(g9_ctxs) == 0

        # With subject_code filter matching and non-matching
        math_ctxs = svc.iter_topic_contexts(subject_code="M")
        assert len(math_ctxs) > 0
        sci_ctxs = svc.iter_topic_contexts(subject_code="SCIENCE")
        assert len(sci_ctxs) == 0

        # With include_subtopics=False
        top_only = svc.iter_topic_contexts(include_subtopics=False)
        assert len(top_only) < len(all_ctxs)

        # list_topics with various filters
        topics_all = svc.list_topics()
        assert len(topics_all) > 0
        topics_g4_term1 = svc.list_topics(grade=4, term=1)
        assert len(topics_g4_term1) > 0
        topics_none = svc.list_topics(grade=12)
        assert len(topics_none) == 0
        topics_subj_none = svc.list_topics(subject_code="NONEXISTENT")
        assert len(topics_subj_none) == 0
        topics_term_none = svc.list_topics(term=99)
        assert len(topics_term_none) == 0

        # list_all_caps_refs
        refs = svc.list_all_caps_refs()
        assert len(refs) > 0
        assert "4.M.1.1" in refs

        # summary
        summary = svc.summary()
        assert summary["maps_loaded"] >= 1
        assert summary["total_refs"] > 0
        assert len(summary["scopes"]) >= 1

    def test_singleton_functions(self):
        s1 = get_caps_topic_map_service()
        s2 = get_caps_service()
        assert s1 is s2
        assert isinstance(s1, CAPSTopicMapService)
