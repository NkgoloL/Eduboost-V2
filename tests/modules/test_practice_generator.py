from __future__ import annotations

from types import SimpleNamespace

from app.modules.practice.practice_generator import PracticeGenerator


def make_item(caps_ref, item_id, b, status="approved"):
    return SimpleNamespace(caps_ref=caps_ref, item_id=item_id, difficulty_b=b, review_status=status)


def test_select_items_filters_and_sorts():
    items = [
        make_item("gap1", "1", 0.4),
        make_item("gap1", "2", 0.6),
        make_item("gap1", "3", 0.9),
        make_item("gap2", "4", 0.5),
        make_item("gap2", "5", 0.2, status="draft"),
    ]

    gen = PracticeGenerator()

    # theta near 0.5 should pick items with difficulty within 0.5 distance
    selected = gen.select_items(items, gap_topics=["gap1", "gap2"], theta=0.5, served_ids={"3"}, per_gap=2)

    # item '3' should be excluded (served); item '5' excluded (not approved)
    ids = {str(getattr(i, "item_id")) for i in selected}
    assert "3" not in ids
    assert "5" not in ids
    assert "1" in ids or "2" in ids
