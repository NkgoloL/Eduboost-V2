"""
EduBoost V2 — Unit Tests
Covers: IRT engine, Judiciary schema validation, Ether archetype classification.
"""
import json
import math
import pytest

from app.services.diagnostic import DiagnosticEngine, p_correct, update_theta_mle
from app.services.judiciary import ConstitutionalViolation, PolicyService
from app.services.archetype_service import ArchetypeService
from app.domain.models import ArchetypeLabel


# ── IRT Engine Tests ──────────────────────────────────────────────────────────

class MockItem:
    def __init__(self, id_, a, b, subject="Math", topic="Fractions", grade=4):
        self.id = id_
        self.a_param = a
        self.b_param = b
        self.subject = subject
        self.topic = topic
        self.grade = grade
        self.correct_option = "A"


class TestIRTEngine:
    def test_p_correct_at_equal_theta_b(self):
        # When theta == b, P should be exactly 0.5
        p = p_correct(theta=1.0, a=1.5, b=1.0)
        assert abs(p - 0.5) < 0.001

    def test_p_correct_increases_with_theta(self):
        p_low = p_correct(theta=-1.0, a=1.0, b=0.0)
        p_high = p_correct(theta=1.0, a=1.0, b=0.0)
        assert p_high > p_low

    def test_theta_update_all_correct(self):
        items = [MockItem(str(i), a=1.0, b=float(i - 2)) for i in range(5)]
        # All correct — theta should increase
        theta = update_theta_mle(0.0, [(item, True) for item in items])
        assert theta > 0.0

    def test_theta_update_all_wrong(self):
        items = [MockItem(str(i), a=1.0, b=float(i - 2)) for i in range(5)]
        theta = update_theta_mle(0.0, [(item, False) for item in items])
        assert theta < 0.0

    def test_theta_clamped(self):
        items = [MockItem(str(i), a=2.0, b=4.0) for i in range(10)]
        theta = update_theta_mle(0.0, [(item, True) for item in items])
        assert theta <= 4.0
        theta2 = update_theta_mle(0.0, [(item, False) for item in items])
        assert theta2 >= -4.0

    def test_identify_gaps(self):
        engine = DiagnosticEngine()
        items = [
            MockItem("i1", 1.0, 0.0, "Math", "Fractions", 4),
            MockItem("i2", 1.0, 0.5, "Math", "Decimals", 4),
            MockItem("i3", 1.0, -0.5, "English", "Grammar", 4),
        ]
        # i2 is missed
        gaps = engine.identify_gaps(items, correct_item_ids={"i1", "i3"})
        assert len(gaps) == 1
        assert gaps[0]["topic"] == "Decimals"

    def test_select_next_item_max_information(self):
        engine = DiagnosticEngine()
        items = [
            MockItem("easy", 1.0, -3.0),
            MockItem("optimal", 1.5, 0.0),  # highest info at theta=0
            MockItem("hard", 1.0, 3.0),
        ]
        best = engine.select_next_item(theta=0.0, administered_ids=set(), bank=items)
        assert best.id == "optimal"

    def test_select_skips_administered(self):
        engine = DiagnosticEngine()
        items = [MockItem("a", 2.0, 0.0), MockItem("b", 1.5, 0.0)]
        best = engine.select_next_item(theta=0.0, administered_ids={"a"}, bank=items)
        assert best.id == "b"


# ── Judiciary Tests ───────────────────────────────────────────────────────────

VALID_LESSON = {
    "title": "Fractions",
    "introduction": "Let's learn fractions.",
    "main_content": "A fraction has a numerator and denominator.",
    "worked_example": "1/2 of 8 = 4.",
    "practice_question": "What is 1/4 of 12?",
    "answer": "3",
    "cultural_hook": "Think of cutting a braaibroodjie into equal pieces.",
}


class TestJudiciary:
    def test_valid_lesson_passes(self):
        svc = PolicyService()
        result = svc.stamp_lesson(json.dumps(VALID_LESSON))
        assert result.title == "Fractions"

    def test_invalid_json_raises(self):
        svc = PolicyService()
        with pytest.raises(ConstitutionalViolation, match="valid JSON"):
            svc.stamp_lesson("not json at all")

    def test_missing_field_raises(self):
        svc = PolicyService()
        bad = dict(VALID_LESSON)
        del bad["cultural_hook"]
        with pytest.raises(ConstitutionalViolation, match="schema violation"):
            svc.stamp_lesson(json.dumps(bad))

    def test_content_policy_blocks_violence(self):
        svc = PolicyService()
        bad = dict(VALID_LESSON)
        bad["main_content"] = "This lesson is about violence and weapons."
        with pytest.raises(ConstitutionalViolation, match="policy violation"):
            svc.stamp_lesson(json.dumps(bad))

    def test_markdown_fences_stripped(self):
        svc = PolicyService()
        wrapped = f"```json\n{json.dumps(VALID_LESSON)}\n```"
        result = svc.stamp_lesson(wrapped)
        assert result.answer == "3"


# ── Ether Service Tests ───────────────────────────────────────────────────────

class TestEther:
    def test_returns_valid_archetype(self):
        svc = ArchetypeService()
        answers = [
            {"question_id": 1, "answer": "A"},
            {"question_id": 2, "answer": "A"},
            {"question_id": 3, "answer": "C"},
            {"question_id": 4, "answer": "A"},
            {"question_id": 5, "answer": "A"},
        ]
        archetype, description = svc.classify_archetype(answers)
        assert archetype in ArchetypeLabel
        assert len(description) > 0

    def test_five_questions_returned(self):
        svc = ArchetypeService()
        questions = svc.get_onboarding_questions()
        assert len(questions) == 5
        for q in questions:
            assert "id" in q
            assert "options" in q
            assert len(q["options"]) == 4

    def test_prompt_modifier_applied(self):
        svc = ArchetypeService()
        base = "Teach fractions."
        modified = svc.modify_prompt_for_archetype(base, ArchetypeLabel.BINAH)
        assert "step" in modified.lower() or "structured" in modified.lower() or "Binah" in modified

    def test_no_archetype_returns_base_prompt(self):
        svc = ArchetypeService()
        base = "Teach fractions."
        result = svc.modify_prompt_for_archetype(base, None)
        assert result == base
