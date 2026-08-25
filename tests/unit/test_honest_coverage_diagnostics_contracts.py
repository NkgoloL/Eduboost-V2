from __future__ import annotations

from app.modules.diagnostics.production_readiness_contracts import (
    DiagnosticItemSpec,
    ItemReviewStatus,
    audit_minimum_viable_item_bank,
    can_transition_review_status,
    fisher_information,
    grade_equivalent_from_theta,
    identify_gap_topics,
    irt_probability,
    remediation_tags_from_misconceptions,
    required_bias_review_dimensions,
    select_item_by_fisher_information,
    validate_diagnostic_item_schema,
)


def _item(**overrides) -> DiagnosticItemSpec:
    data = {
        "item_id": "item-1",
        "subject": "mathematics",
        "grade": 4,
        "topic": "place value",
        "skill": "compare whole numbers",
        "difficulty": 0.0,
        "discrimination": 1.2,
        "correct_answer": "42",
        "distractors": ("24", "40", "44"),
        "explanation": "The tens and ones positions determine the value.",
        "caps_reference": "4.M.1.1",
        "review_status": ItemReviewStatus.APPROVED,
        "misconception_tags": (" Reversal ", "place-value", "reversal"),
        "exposure_count": 0,
        "max_exposure": 50,
    }
    data.update(overrides)
    return DiagnosticItemSpec(**data)


def test_diagnostic_item_schema_accepts_valid_items_and_rejects_malformed_items() -> None:
    valid = _item()
    invalid = _item(
        item_id="",
        subject="",
        grade=13,
        topic="",
        skill="",
        difficulty=9.0,
        discrimination=0.0,
        correct_answer="42",
        distractors=("42",),
        explanation="",
        caps_reference="",
        exposure_count=-1,
        max_exposure=0,
    )

    failures = validate_diagnostic_item_schema(invalid)

    assert validate_diagnostic_item_schema(valid) == []
    assert "item_id is required" in failures
    assert "grade must be between 0 and 12" in failures
    assert "correct answer must not appear as a distractor" in failures
    assert "max_exposure must be positive" in failures


def test_irt_selection_uses_approved_valid_unexhausted_items_only() -> None:
    high_information = _item(item_id="high", difficulty=0.1, discrimination=2.0)
    retired = _item(item_id="retired", review_status=ItemReviewStatus.RETIRED)
    exhausted = _item(item_id="exhausted", exposure_count=50, max_exposure=50)
    malformed = _item(item_id="bad", distractors=())

    selected = select_item_by_fisher_information(
        0.0,
        [retired, exhausted, malformed, high_information],
        used_item_ids={"already-used"},
    )

    assert selected == high_information
    assert select_item_by_fisher_information(0.0, [retired, exhausted, malformed]) is None
    assert 0.0 < irt_probability(theta=0.0, difficulty=0.0, discrimination=1.0) < 1.0
    assert fisher_information(0.0, high_information) > fisher_information(0.0, _item(discrimination=0.2))


def test_diagnostic_gap_review_and_launch_contracts_are_explicit() -> None:
    gaps = identify_gap_topics(
        [
            {"topic": "fractions", "correct": False},
            {"topic": "place value", "correct": False},
            {"topic": "fractions", "correct": False},
            {"topic": "geometry", "correct": True},
            {"topic": " ", "correct": False},
        ]
    )
    items = [
        _item(item_id="math-4", grade=4, subject="mathematics"),
        _item(item_id="english-5", grade=5, subject="english"),
    ]

    assert gaps == ["fractions", "place value"]
    assert grade_equivalent_from_theta(99.0, learner_grade=4) == 5.5
    assert can_transition_review_status(ItemReviewStatus.DRAFT, ItemReviewStatus.AI_GENERATED)
    assert not can_transition_review_status(ItemReviewStatus.APPROVED, ItemReviewStatus.DRAFT)
    assert audit_minimum_viable_item_bank(
        items,
        launch_grades=[4, 5],
        launch_subjects=["mathematics", "english"],
        min_items_per_grade_subject=1,
    ) == [
        "grade 4 subject english has 0 approved item(s); requires 1",
        "grade 5 subject mathematics has 0 approved item(s); requires 1",
    ]
    assert {dimension.value for dimension in required_bias_review_dimensions()} == {
        "language",
        "region",
        "socioeconomic_context",
    }
    assert remediation_tags_from_misconceptions(_item()) == ("place-value", "reversal")
