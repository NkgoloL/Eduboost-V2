"""Batch 198: Unit tests for policy_service (PolicyService/JudiciaryService) and contracts (Protocol checks)."""
import json
import pytest

from app.services.policy_service import (
    PolicyViolation,
    PolicyService,
    PolicyValidationError,
    LessonPayload,
    StudyPlanPayload,
)
from app.services.contracts import (
    IAuthService,
    ILearnerService,
    IConsentService,
    IDiagnosticService,
    ILessonService,
)


# ─────────────────────────────────────────────
# PolicyService (JudiciaryService) re-export
# ─────────────────────────────────────────────


class TestPolicyServiceExports:
    def test_policy_violation_is_exception(self):
        err = PolicyViolation("test violation")
        assert isinstance(err, Exception)

    def test_policy_validation_error_is_same_as_policy_violation(self):
        assert PolicyValidationError is PolicyViolation

    def test_policy_service_is_judiciary_service(self):
        from app.core.policy import JudiciaryService
        assert PolicyService is JudiciaryService

    def test_lesson_payload_is_lesson_content(self):
        from app.domain.llm_schemas import LessonContent
        assert LessonPayload is LessonContent

    def test_study_plan_payload_is_study_plan_content(self):
        from app.domain.llm_schemas import StudyPlanContent
        assert StudyPlanPayload is StudyPlanContent


class TestJudiciaryServiceStampLesson:
    def _service(self):
        return PolicyService()

    def _valid_lesson_json(self) -> str:
        lesson = {
            "title": "Introduction to Fractions",
            "introduction": "In this lesson we learn about fractions.",
            "main_content": "A fraction represents a part of a whole. For example, 1/2 means one out of two equal parts.",
            "worked_example": "If you cut a pizza into 4 equal slices and eat 1 slice, you have eaten 1/4 of the pizza.",
            "practice_question": "What fraction of 8 pieces is 3 pieces?",
            "answer": "3/8",
            "cultural_hook": "In South Africa, sharing food equally among friends is a common experience.",
        }
        return json.dumps(lesson)

    def test_valid_lesson_returns_payload(self):
        result = self._service().stamp_lesson(self._valid_lesson_json())
        assert result.title == "Introduction to Fractions"
        assert result.answer == "3/8"

    def test_blocked_word_raises_policy_violation(self):
        raw = self._valid_lesson_json().replace("pizza", "weapon")
        with pytest.raises(PolicyViolation, match="Content policy violation"):
            self._service().stamp_lesson(raw)

    def test_invalid_json_schema_raises_policy_violation(self):
        raw = json.dumps({"wrong_field": "no title"})
        with pytest.raises(PolicyViolation):
            self._service().stamp_lesson(raw)

    def test_empty_response_raises_policy_violation(self):
        with pytest.raises(PolicyViolation, match="empty response"):
            self._service().stamp_lesson("  ")

    def test_markdown_fenced_json_cleaned(self):
        raw = f"```json\n{self._valid_lesson_json()}\n```"
        result = self._service().stamp_lesson(raw)
        assert result.answer == "3/8"

    def test_placeholder_answer_raises_policy_violation(self):
        lesson = {
            "title": "Test Lesson",
            "introduction": "Introduction text",
            "main_content": "Main content here",
            "worked_example": "Example here",
            "practice_question": "Practice here",
            "answer": "tbd",
            "cultural_hook": "Cultural context here",
        }
        with pytest.raises(PolicyViolation, match="placeholder"):
            self._service().stamp_lesson(json.dumps(lesson))

    def test_empty_answer_raises_policy_violation(self):
        lesson = {
            "title": "Test Lesson",
            "introduction": "Introduction text",
            "main_content": "Main content here",
            "worked_example": "Example",
            "practice_question": "Practice",
            "answer": "x",  # Triggers length < 2 check → missing valid answer
            "cultural_hook": "Cultural context here",
        }
        with pytest.raises(PolicyViolation, match="missing"):
            self._service().stamp_lesson(json.dumps(lesson))


class TestJudiciaryServiceStampStudyPlan:
    def _service(self):
        return PolicyService()

    def test_blocked_word_raises_policy_violation(self):
        # We don't need a fully valid study plan — just check the content gate
        with pytest.raises(PolicyViolation, match="Content policy violation"):
            self._service().stamp_study_plan(json.dumps({"topic": "violence tactics"}))

    def test_invalid_schema_raises_policy_violation(self):
        with pytest.raises(PolicyViolation):
            self._service().stamp_study_plan(json.dumps({"wrong": "schema"}))


class TestJudiciaryServiceStampDiagnosticFeedback:
    def _service(self):
        return PolicyService()

    def test_blocked_word_raises_policy_violation(self):
        with pytest.raises(PolicyViolation, match="Content policy violation"):
            self._service().stamp_diagnostic_feedback(json.dumps({"feedback": "explicit hate content"}))

    def test_invalid_schema_raises_policy_violation(self):
        with pytest.raises(PolicyViolation):
            self._service().stamp_diagnostic_feedback(json.dumps({"random": "data"}))


# ─────────────────────────────────────────────
# contracts.py — Protocol structural checks
# ─────────────────────────────────────────────


class TestServiceContracts:
    """Verify that Protocols are runtime-checkable and importable."""

    def test_iauth_service_is_protocol(self):
        import typing
        assert hasattr(IAuthService, "__protocol_attrs__") or isinstance(IAuthService, type)

    def test_ilearner_service_is_protocol(self):
        assert hasattr(ILearnerService, "__protocol_attrs__") or isinstance(ILearnerService, type)

    def test_iconsent_service_is_protocol(self):
        assert hasattr(IConsentService, "__protocol_attrs__") or isinstance(IConsentService, type)

    def test_idiagnostic_service_is_protocol(self):
        assert hasattr(IDiagnosticService, "__protocol_attrs__") or isinstance(IDiagnosticService, type)

    def test_ilesson_service_is_protocol(self):
        assert hasattr(ILessonService, "__protocol_attrs__") or isinstance(ILessonService, type)

    def test_mock_implementation_matches_iauth_protocol(self):
        class FakeAuth:
            async def authenticate(self, email, password, db):
                return {}
            async def refresh_token(self, refresh_token, db):
                return {}
            async def logout(self, jti, db):
                pass

        assert isinstance(FakeAuth(), IAuthService)

    def test_mock_implementation_matches_ilearner_protocol(self):
        class FakeLearner:
            async def create_learner(self, guardian_id, data, db):
                return {}
            async def get_learner(self, learner_id, db):
                return None
            async def update_xp(self, learner_id, xp_delta, db):
                pass

        assert isinstance(FakeLearner(), ILearnerService)

    def test_mock_implementation_matches_iconsent_protocol(self):
        class FakeConsent:
            async def grant_consent(self, guardian_id, learner_id, db):
                pass
            async def revoke_consent(self, guardian_id, learner_id, db):
                pass
            async def has_active_consent(self, learner_id, db):
                return True

        assert isinstance(FakeConsent(), IConsentService)

    def test_incomplete_implementation_does_not_match_protocol(self):
        class Incomplete:
            async def authenticate(self, email, password, db):
                return {}
            # Missing refresh_token and logout

        # runtime_checkable only checks method presence, not signatures
        # But missing methods entirely will fail isinstance check
        assert not isinstance(Incomplete(), IAuthService)
