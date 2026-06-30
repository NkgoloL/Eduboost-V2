from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_diagnostics_assessment_production_readiness import run_checks
from app.modules.diagnostics.production_readiness_contracts import (
    DiagnosticItemSpec,
    ItemReviewStatus,
    audit_minimum_viable_item_bank,
    can_transition_review_status,
    grade_equivalent_from_theta,
    identify_gap_topics,
    remediation_tags_from_misconceptions,
    select_item_by_fisher_information,
    validate_diagnostic_item_schema,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _approved_item(item_id: str, *, difficulty: float = 0.0, topic: str = "Fractions") -> DiagnosticItemSpec:
    return DiagnosticItemSpec(
        item_id=item_id,
        subject="Mathematics",
        grade=4,
        topic=topic,
        skill="Compare fractions",
        difficulty=difficulty,
        discrimination=1.2,
        correct_answer="A",
        distractors=("B", "C", "D"),
        explanation="Compare equal denominator fractions.",
        caps_reference="4.M.1.1",
        review_status=ItemReviewStatus.APPROVED,
        misconception_tags=("denominator-confusion",),
    )


@pytest.mark.unit
def test_diagnostics_assessment_production_readiness_check_passes() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_diagnostics_assessment_production_readiness_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_diagnostics_assessment_production_readiness.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Diagnostics assessment production readiness check" in result.stdout


@pytest.mark.unit
def test_diagnostic_item_schema_and_item_bank_audit_contract() -> None:
    item = _approved_item("item-1")
    assert validate_diagnostic_item_schema(item) == []
    assert audit_minimum_viable_item_bank(
        [item],
        launch_grades=[4],
        launch_subjects=["Mathematics"],
        min_items_per_grade_subject=1,
    ) == []


@pytest.mark.unit
def test_review_workflow_and_fisher_information_selection_contract() -> None:
    assert can_transition_review_status(ItemReviewStatus.DRAFT, ItemReviewStatus.AI_GENERATED)
    assert can_transition_review_status(ItemReviewStatus.HUMAN_REVIEWED, ItemReviewStatus.APPROVED)
    assert not can_transition_review_status(ItemReviewStatus.RETIRED, ItemReviewStatus.APPROVED)

    selected = select_item_by_fisher_information(
        0.0,
        [_approved_item("easy", difficulty=-2.0), _approved_item("target", difficulty=0.0)],
    )
    assert selected is not None
    assert selected.item_id == "target"


@pytest.mark.unit
def test_grade_equivalent_gap_identification_and_misconception_routing_contract() -> None:
    assert grade_equivalent_from_theta(0.0, 4) == 4.0
    assert grade_equivalent_from_theta(4.0, 4) <= 5.5
    assert identify_gap_topics(
        [
            {"topic": "Fractions", "correct": False},
            {"topic": "Fractions", "correct": False},
            {"topic": "Measurement", "correct": False},
            {"topic": "Patterns", "correct": True},
        ]
    ) == ["Fractions", "Measurement"]
    assert remediation_tags_from_misconceptions(_approved_item("tagged")) == ("denominator-confusion",)
