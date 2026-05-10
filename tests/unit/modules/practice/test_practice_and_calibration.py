from __future__ import annotations

from types import SimpleNamespace

from app.modules.diagnostics.calibration_service import CalibrationService
from app.modules.practice.practice_generator import PracticeGenerator
from app.modules.practice.spaced_repetition_scheduler import SpacedRepetitionScheduler


def item(item_id, caps_ref="4.M.1.1", b=0.0):
    return SimpleNamespace(item_id=item_id, caps_ref=caps_ref, difficulty_b=b, review_status="approved")


def test_practice_generator_selects_near_theta():
    items = [item("near", b=0.2), item("far", b=2.0)]
    selected = PracticeGenerator().select_items(items, gap_topics=["4.M.1.1"], theta=0.0)
    assert [x.item_id for x in selected] == ["near"]


def test_spaced_repetition_scheduler():
    scheduler = SpacedRepetitionScheduler()
    first = scheduler.update_schedule(correct=True)
    second = scheduler.update_schedule(correct=True, interval_days=first.interval_days, easiness_factor=first.easiness_factor)
    reset = scheduler.update_schedule(correct=False, interval_days=10, easiness_factor=2.5)
    assert second.interval_days >= first.interval_days
    assert reset.interval_days == 1


def test_calibration_flags_large_difficulty_shift():
    source_item = SimpleNamespace(item_id="i1", difficulty_b=0.0, discrimination_a=1.0, guessing_c=0.25)
    responses = [SimpleNamespace(is_correct=False) for _ in range(100)]
    result = CalibrationService().calibrate_item(source_item, responses)
    assert result.response_count == 100
    assert result.review_required is True
