from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from app.modules.diagnostics.item_validator import ItemValidator
from app.modules.diagnostics.quality_scorer import QualityScorer
from app.modules.lessons.caps_topic_map_service import CAPSTopicMapService
from app.modules.lessons.lesson_validator import LessonValidator

ROOT = Path(__file__).resolve().parents[2]
LAUNCH_REFS = {"4.M.1.1", "4.M.1.2", "4.M.1.3"}


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_caps_topic_map_service_loads_launch_context_once() -> None:
    service = CAPSTopicMapService()
    summary = service.summary()
    assert summary["maps_loaded"] >= 1
    context = service.get_topic_context("4.M.1.1")
    assert context is not None
    assert context["grade"] == 4
    assert context["subject"] == "Mathematics"
    assert context["topic"] == "Whole Numbers"


def test_generated_launch_item_bank_meets_strict_targets() -> None:
    topic_map = load("data/caps/caps_topic_map_grade4_maths.json")
    item_bank = load("data/generated/items/grade4_maths_launch_item_bank.json")
    validator = ItemValidator(topic_map=topic_map)
    counts: Counter[str] = Counter()
    for item in item_bank["items"]:
        assert item["caps_ref"] in LAUNCH_REFS
        assert not validator.validate_all(item)
        assert item["review_status"] == "approved"
        assert float(item["quality_score"]) >= 0.85
        counts[item["caps_ref"]] += 1
    assert counts == {"4.M.1.1": 40, "4.M.1.2": 40, "4.M.1.3": 40}


def test_generated_launch_lessons_meet_strict_targets() -> None:
    lesson_bank = load("data/generated/lessons/grade4_maths_launch_lessons.json")
    validator = LessonValidator()
    counts: Counter[str] = Counter()
    for lesson in lesson_bank["lessons"]:
        assert lesson["caps_ref"] in LAUNCH_REFS
        result = validator.validate(lesson, require_verified=True)
        assert result.passed, result.failures
        assert lesson["review_status"] == "approved"
        assert float(lesson["quality_score"]) >= 0.85
        counts[lesson["caps_ref"]] += 1
    assert counts == {"4.M.1.1": 8, "4.M.1.2": 8, "4.M.1.3": 8}


def test_nested_topic_map_quality_alignment_for_topic_level_ref() -> None:
    topic_map = load("data/caps/caps_topic_map_grade4_maths.json")
    item = load("data/generated/items/grade4_maths_launch_item_bank.json")["items"][0]
    scored = QualityScorer(topic_map=topic_map).score(item)
    assert scored["component_scores"]["caps_alignment"] == 1.0
