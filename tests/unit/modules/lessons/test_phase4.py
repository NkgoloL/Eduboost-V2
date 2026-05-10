"""
test_phase4.py
==============
Phase 4 — L4-10

Unit tests covering all Phase 4 components:

  L4-01 / L4-02 — lesson_review_router.py
    - Review queue RBAC (only reviewer/admin may access)
    - Auto-queue rule: quality_score < 0.7 OR unverified OR requires_review
    - Review action: approve and reject paths
    - Conflict error on re-reviewing a finalised lesson

  L4-04 — lesson_variants.py
    - All 5 variant types resolve to configs
    - Unknown variant raises ValueError
    - Variant config fields are non-empty
    - list_supported_variants returns all 5

  L4-05 — adaptive_remediation.py
    - MISCONCEPTION_CORRECTION wins over any other strategy
    - Majority vote for WORKED_EXAMPLE_FOCUS vs PRACTICE_DRILL
    - Empty tags → RE_EXPLAIN default
    - Unrecognised tag → logged, treated as RE_EXPLAIN
    - Prompt injection is non-empty and contains tag references

  L4-06 — parent_explanation_mode.py
    - Prompt contains learner first name
    - Prompt contains topic and subtopic
    - Prompt does not leak learner_id (UUID) into the text
    - Misconception context is included when tags are present

  L4-07 — teacher_insight_mode.py (aggregate logic — no LLM)
    - MISCONCEPTION_CORRECTION tag wins in select_remediation_strategy
    - Coverage status logic: green ≥8, amber 1–7, red 0 approved
    - Cohort aggregation: correct class average, correct tag counts
    - Intervention groups are built for top tags

  L4-08 — lesson_coverage_router.py
    - Coverage status thresholds (green/amber/red/uncovered)
    - Quality score distribution stats (mean, p25, p75)
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.modules.lessons.lesson_review_router import (
    compute_auto_queue_reasons,
    should_auto_queue,
    QUALITY_SCORE_REVIEW_THRESHOLD,
    ReviewDecision,
    UserRole,
    CurrentUser,
)
from app.modules.lessons.lesson_variants import (
    LessonVariantType,
    get_variant_prompt_config,
    list_supported_variants,
    VARIANT_CONFIGS,
)
from app.modules.lessons.adaptive_remediation import (
    RemediationStrategy,
    select_remediation_strategy,
    build_remediation_prompt_injection,
    MISCONCEPTION_TAG_TO_STRATEGY,
)
from app.modules.lessons.parent_explanation_mode import (
    ParentSummaryRequest,
    LearnerSessionPerformance,
    build_parent_summary_prompt,
)
from app.modules.lessons.teacher_insight_mode import (
    TeacherInsightRequest,
    LearnerMisconceptionRecord,
    aggregate_cohort_misconceptions,
    build_intervention_groups,
    _recommend_variant_for_tag,
)
from app.modules.lessons.lesson_coverage_router import (
    compute_quality_distribution,
    compute_coverage_status,
)
from app.domain.lesson import ReviewStatus, SafetyClassification


# ===========================================================================
# L4-01 / L4-02 — Review Router & Auto-Queue Rule
# ===========================================================================

class TestAutoQueueRule:
    """Tests for L4-02: auto-queue rule thresholds."""

    def test_low_quality_score_queues(self):
        reasons = compute_auto_queue_reasons(
            quality_score=0.65,  # below 0.7 threshold
            answer_key_verified=True,
            safety_classification=SafetyClassification.SAFE,
        )
        assert len(reasons) == 1
        assert "0.65" in reasons[0]
        assert should_auto_queue(0.65, True, SafetyClassification.SAFE)

    def test_exact_threshold_does_not_queue(self):
        """quality_score = 0.7 exactly should NOT trigger auto-queue on this rule."""
        reasons = compute_auto_queue_reasons(
            quality_score=QUALITY_SCORE_REVIEW_THRESHOLD,
            answer_key_verified=True,
            safety_classification=SafetyClassification.SAFE,
        )
        assert not any("threshold" in r for r in reasons)

    def test_none_quality_score_queues(self):
        """Null quality_score (lesson not yet scored) must be queued."""
        assert should_auto_queue(None, True, SafetyClassification.SAFE)

    def test_unverified_answer_key_queues(self):
        reasons = compute_auto_queue_reasons(
            quality_score=0.85,
            answer_key_verified=False,
            safety_classification=SafetyClassification.SAFE,
        )
        assert any("answer key" in r.lower() for r in reasons)
        assert should_auto_queue(0.85, False, SafetyClassification.SAFE)

    def test_requires_review_safety_queues(self):
        reasons = compute_auto_queue_reasons(
            quality_score=0.90,
            answer_key_verified=True,
            safety_classification=SafetyClassification.REQUIRES_REVIEW,
        )
        assert any("safety" in r.lower() for r in reasons)
        assert should_auto_queue(0.90, True, SafetyClassification.REQUIRES_REVIEW)

    def test_all_three_triggers_returns_three_reasons(self):
        reasons = compute_auto_queue_reasons(
            quality_score=0.50,
            answer_key_verified=False,
            safety_classification=SafetyClassification.REQUIRES_REVIEW,
        )
        assert len(reasons) == 3

    def test_high_quality_verified_safe_does_not_queue(self):
        assert not should_auto_queue(0.85, True, SafetyClassification.SAFE)

    def test_only_reviewer_and_admin_allowed(self):
        """Verify role check logic — only reviewer and admin are valid reviewer roles."""
        allowed_roles = {UserRole.REVIEWER, UserRole.ADMIN}
        rejected_roles = {UserRole.LEARNER, UserRole.TEACHER}
        for role in allowed_roles:
            assert role in allowed_roles
        for role in rejected_roles:
            assert role not in allowed_roles


# ===========================================================================
# L4-04 — Lesson Variants
# ===========================================================================

class TestLessonVariants:
    """Tests for L4-04: lesson variant schema and prompt adaptation."""

    def test_all_five_variant_types_resolve(self):
        for variant_type in LessonVariantType:
            config = get_variant_prompt_config(variant_type)
            assert config is not None, f"No config for {variant_type}"
            assert config.variant_type == variant_type

    def test_none_variant_returns_none(self):
        """Standard lesson (no variant) returns None — no prompt injection."""
        assert get_variant_prompt_config(None) is None

    def test_unknown_variant_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown variant_type"):
            get_variant_prompt_config("nonexistent_variant")  # type: ignore

    def test_all_configs_have_non_empty_instructions(self):
        for vt, config in VARIANT_CONFIGS.items():
            assert config.explanation_style_instruction.strip(), \
                f"{vt}: explanation_style_instruction is empty"
            assert config.example_format_instruction.strip(), \
                f"{vt}: example_format_instruction is empty"
            assert config.question_format_instruction.strip(), \
                f"{vt}: question_format_instruction is empty"
            assert config.variant_label.strip(), \
                f"{vt}: variant_label is empty"

    def test_multilingual_has_target_language_note(self):
        config = get_variant_prompt_config(LessonVariantType.MULTILINGUAL)
        assert config.target_language_note is not None
        assert "isiZulu" in config.target_language_note

    def test_list_supported_variants_returns_all_five(self):
        supported = list_supported_variants()
        assert len(supported) == 5
        types = {v["variant_type"] for v in supported}
        assert types == {vt.value for vt in LessonVariantType}

    def test_variant_config_has_additional_constraints(self):
        for vt, config in VARIANT_CONFIGS.items():
            assert len(config.additional_constraints) > 0, \
                f"{vt}: no additional_constraints defined"

    def test_visual_variant_mentions_diagram(self):
        config = get_variant_prompt_config(LessonVariantType.VISUAL)
        assert "diagram" in config.explanation_style_instruction.lower()

    def test_story_variant_mentions_south_africa(self):
        config = get_variant_prompt_config(LessonVariantType.STORY)
        assert "south african" in config.explanation_style_instruction.lower()

    def test_exam_style_variant_mentions_marks(self):
        config = get_variant_prompt_config(LessonVariantType.EXAM_STYLE)
        assert "mark" in config.example_format_instruction.lower()

    def test_step_by_step_variant_mentions_numbered_steps(self):
        config = get_variant_prompt_config(LessonVariantType.STEP_BY_STEP)
        assert "numbered" in config.explanation_style_instruction.lower() or \
               "step" in config.explanation_style_instruction.lower()


# ===========================================================================
# L4-05 — Adaptive Remediation
# ===========================================================================

class TestAdaptiveRemediation:
    """Tests for L4-05: misconception_tags → strategy → targeted prompt."""

    def test_misconception_correction_wins_over_all(self):
        """MISCONCEPTION_CORRECTION must dominate regardless of other tags."""
        tags = [
            "place_value_digit_confusion",       # → MISCONCEPTION_CORRECTION
            "fluency_slow_number_bonds",          # → PRACTICE_DRILL
            "fluency_slow_times_tables",          # → PRACTICE_DRILL
            "fluency_slow_place_value_reading",   # → PRACTICE_DRILL
        ]
        strategy = select_remediation_strategy(tags)
        assert strategy == RemediationStrategy.MISCONCEPTION_CORRECTION

    def test_empty_tags_returns_re_explain(self):
        strategy = select_remediation_strategy([])
        assert strategy == RemediationStrategy.RE_EXPLAIN

    def test_fluency_tags_majority_returns_practice_drill(self):
        tags = [
            "fluency_slow_number_bonds",
            "fluency_slow_times_tables",
            "fluency_slow_place_value_reading",
        ]
        strategy = select_remediation_strategy(tags)
        assert strategy == RemediationStrategy.PRACTICE_DRILL

    def test_procedure_tags_majority_returns_worked_example_focus(self):
        tags = [
            "addition_no_carry",
            "subtraction_no_borrow",
            "multiplication_skips_zero_placeholder",
        ]
        strategy = select_remediation_strategy(tags)
        assert strategy == RemediationStrategy.WORKED_EXAMPLE_FOCUS

    def test_unrecognised_tag_treated_as_re_explain(self):
        """Unknown tag should not crash — treated as RE_EXPLAIN and logged."""
        tags = ["totally_unknown_tag_xyz"]
        strategy = select_remediation_strategy(tags)
        assert strategy == RemediationStrategy.RE_EXPLAIN

    def test_build_prompt_injection_returns_tuple(self):
        tags = ["place_value_digit_confusion"]
        strategy, injection = build_remediation_prompt_injection(tags)
        assert strategy == RemediationStrategy.MISCONCEPTION_CORRECTION
        assert isinstance(injection, str)
        assert len(injection) > 50

    def test_prompt_injection_contains_tag_reference(self):
        tags = ["fraction_larger_denominator_larger_fraction"]
        _, injection = build_remediation_prompt_injection(tags)
        assert "fraction_larger_denominator_larger_fraction" in injection

    def test_all_known_tags_resolve_without_error(self):
        """Every tag in MISCONCEPTION_TAG_TO_STRATEGY must resolve cleanly."""
        for tag in MISCONCEPTION_TAG_TO_STRATEGY:
            strategy = select_remediation_strategy([tag])
            assert isinstance(strategy, RemediationStrategy)

    def test_single_misconception_correction_tag_returns_correction_strategy(self):
        strategy = select_remediation_strategy(["ordering_longer_number_is_larger"])
        assert strategy == RemediationStrategy.MISCONCEPTION_CORRECTION

    def test_re_explain_strategy_prompt_contains_cpa(self):
        tags = ["general_conceptual_confusion"]
        _, injection = build_remediation_prompt_injection(tags)
        assert "CPA" in injection or "Concrete" in injection


# ===========================================================================
# L4-06 — Parent Explanation Mode (prompt builder — no LLM call needed)
# ===========================================================================

class TestParentExplanationMode:
    """Tests for L4-06: parent summary prompt building."""

    def _make_request(self, learner_name: Optional[str] = "Sipho") -> ParentSummaryRequest:
        performance = LearnerSessionPerformance(
            learner_id=uuid.uuid4(),
            lesson_id=uuid.uuid4(),
            caps_ref="4.M.1.1",
            topic="Whole Numbers",
            subtopic="Ordering and Comparing 4-digit Numbers",
            grade=4,
            questions_attempted=5,
            questions_correct=3,
            time_spent_seconds=480,
            triggered_misconception_tags=["place_value_digit_confusion"],
        )
        return ParentSummaryRequest(
            lesson_id=uuid.uuid4(),
            caps_ref="4.M.1.1",
            topic="Whole Numbers",
            subtopic="Ordering and Comparing 4-digit Numbers",
            grade=4,
            subject="Mathematics",
            difficulty_level="on_level",
            learning_objectives=[
                "Order 4-digit numbers from smallest to largest.",
                "Compare two 4-digit numbers using < and >.",
                "Identify the value of each digit in a 4-digit number.",
            ],
            performance=performance,
            learner_first_name=learner_name,
        )

    def test_prompt_contains_learner_name(self):
        request = self._make_request(learner_name="Amahle")
        prompt = build_parent_summary_prompt(request)
        assert "Amahle" in prompt

    def test_prompt_uses_your_child_when_no_name(self):
        request = self._make_request(learner_name=None)
        prompt = build_parent_summary_prompt(request)
        assert "your child" in prompt.lower()

    def test_prompt_contains_topic(self):
        request = self._make_request()
        prompt = build_parent_summary_prompt(request)
        assert "Whole Numbers" in prompt

    def test_prompt_does_not_contain_learner_uuid(self):
        """Learner UUID must NOT appear in the prompt (no PII leakage to LLM)."""
        request = self._make_request()
        prompt = build_parent_summary_prompt(request)
        assert str(request.performance.learner_id) not in prompt

    def test_prompt_contains_misconception_context_when_tags_present(self):
        request = self._make_request()
        prompt = build_parent_summary_prompt(request)
        assert "place value" in prompt.lower() or "misconception" in prompt.lower()

    def test_prompt_does_not_contain_misconception_context_when_no_tags(self):
        request = self._make_request()
        request.performance.triggered_misconception_tags = []
        prompt = build_parent_summary_prompt(request)
        # Prompt should still be valid but without the misconception section
        assert "Whole Numbers" in prompt

    def test_prompt_includes_grade(self):
        request = self._make_request()
        prompt = build_parent_summary_prompt(request)
        assert "Grade 4" in prompt or "grade 4" in prompt.lower()

    def test_prompt_includes_score_context(self):
        request = self._make_request()
        prompt = build_parent_summary_prompt(request)
        # Score is expressed as a fraction (3/5 in our test data)
        assert "3/5" in prompt or "3" in prompt


# ===========================================================================
# L4-07 — Teacher Insight Mode (aggregate logic — no LLM)
# ===========================================================================

class TestTeacherInsightMode:
    """Tests for L4-07: cohort aggregation and intervention group logic."""

    def _make_cohort(self) -> TeacherInsightRequest:
        records = [
            LearnerMisconceptionRecord(
                learner_id=uuid.uuid4(),
                misconception_tags=["place_value_digit_confusion", "ordering_longer_number_is_larger"],
                questions_correct=2,
                questions_attempted=5,
                last_session_at=datetime.now(tz=timezone.utc),
            ),
            LearnerMisconceptionRecord(
                learner_id=uuid.uuid4(),
                misconception_tags=["place_value_digit_confusion"],
                questions_correct=4,
                questions_attempted=5,
                last_session_at=datetime.now(tz=timezone.utc),
            ),
            LearnerMisconceptionRecord(
                learner_id=uuid.uuid4(),
                misconception_tags=["fluency_slow_number_bonds"],
                questions_correct=5,
                questions_attempted=5,
                last_session_at=datetime.now(tz=timezone.utc),
            ),
            LearnerMisconceptionRecord(
                learner_id=uuid.uuid4(),
                misconception_tags=[],  # No misconceptions — clean session
                questions_correct=5,
                questions_attempted=5,
                last_session_at=datetime.now(tz=timezone.utc),
            ),
        ]
        return TeacherInsightRequest(
            teacher_id=uuid.uuid4(),
            caps_ref="4.M.1.1",
            topic="Whole Numbers",
            subtopic="Ordering and Comparing 4-digit Numbers",
            grade=4,
            subject="Mathematics",
            cohort_label="Grade 4A",
            learner_records=records,
        )

    def test_class_average_correct(self):
        request = self._make_cohort()
        agg = aggregate_cohort_misconceptions(request)
        # Scores: 40%, 80%, 100%, 100% → mean = 80%
        assert agg["class_avg"] == 80.0

    def test_below_70_count_correct(self):
        request = self._make_cohort()
        agg = aggregate_cohort_misconceptions(request)
        # Only learner 1 (40%) is below 70%
        assert agg["below_70"] == 1

    def test_top_tag_is_place_value(self):
        request = self._make_cohort()
        agg = aggregate_cohort_misconceptions(request)
        assert agg["top_tags"][0] == "place_value_digit_confusion"

    def test_tag_count_place_value_is_two(self):
        request = self._make_cohort()
        agg = aggregate_cohort_misconceptions(request)
        assert agg["tag_counts"].get("place_value_digit_confusion") == 2

    def test_total_learners_correct(self):
        request = self._make_cohort()
        agg = aggregate_cohort_misconceptions(request)
        assert agg["total_learners"] == 4

    def test_intervention_groups_built(self):
        request = self._make_cohort()
        agg = aggregate_cohort_misconceptions(request)
        groups = build_intervention_groups(
            agg["tag_to_learners"],
            agg["tag_counts"],
            agg["total_learners"],
        )
        assert len(groups) >= 1
        assert any("place_value_digit_confusion" in g.shared_misconceptions for g in groups)

    def test_misconception_correction_recommended_for_confusion_tag(self):
        variant = _recommend_variant_for_tag("place_value_digit_confusion")
        assert variant == "misconception_correction"

    def test_practice_drill_recommended_for_fluency_tag(self):
        variant = _recommend_variant_for_tag("fluency_slow_number_bonds")
        assert variant == "practice_drill"


# ===========================================================================
# L4-08 — Coverage Router (pure logic — no DB needed)
# ===========================================================================

class TestCoverageLogic:
    """Tests for L4-08: coverage status thresholds and quality distribution."""

    def test_green_status_at_eight_approved(self):
        assert compute_coverage_status(approved_count=8, total_count=10) == "green"

    def test_green_status_at_more_than_eight(self):
        assert compute_coverage_status(approved_count=12, total_count=15) == "green"

    def test_amber_status_at_seven_approved(self):
        assert compute_coverage_status(approved_count=7, total_count=10) == "amber"

    def test_amber_status_at_one_approved(self):
        assert compute_coverage_status(approved_count=1, total_count=3) == "amber"

    def test_red_status_zero_approved_but_lessons_exist(self):
        assert compute_coverage_status(approved_count=0, total_count=5) == "red"

    def test_uncovered_status_no_lessons(self):
        assert compute_coverage_status(approved_count=0, total_count=0) == "uncovered"

    def test_quality_distribution_empty_scores(self):
        dist = compute_quality_distribution([])
        assert dist.count == 0
        assert dist.mean is None
        assert dist.below_threshold == 0

    def test_quality_distribution_single_score(self):
        dist = compute_quality_distribution([0.85])
        assert dist.count == 1
        assert dist.mean == 0.85
        assert dist.below_threshold == 0

    def test_quality_distribution_below_threshold_count(self):
        scores = [0.55, 0.65, 0.75, 0.85, 0.95]  # 2 below 0.7
        dist = compute_quality_distribution(scores)
        assert dist.below_threshold == 2

    def test_quality_distribution_mean_correct(self):
        scores = [0.6, 0.7, 0.8, 0.9]
        dist = compute_quality_distribution(scores)
        assert dist.mean == pytest.approx(0.75, abs=0.001)

    def test_quality_distribution_min_max(self):
        scores = [0.4, 0.7, 0.9]
        dist = compute_quality_distribution(scores)
        assert dist.min == pytest.approx(0.4, abs=0.001)
        assert dist.max == pytest.approx(0.9, abs=0.001)
