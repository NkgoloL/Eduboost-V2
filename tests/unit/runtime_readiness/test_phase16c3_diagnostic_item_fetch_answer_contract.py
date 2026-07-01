from __future__ import annotations

from types import SimpleNamespace

from app.api_v2_routers.diagnostics import _option_payload, _serialise_item_bank_item, _subject_code


def test_subject_codes_are_normalised_for_seeded_frontend_filtering() -> None:
    assert _subject_code("Mathematics") == "MATH"
    assert _subject_code("English") == "ENG"


def test_option_payload_preserves_answer_keys_without_exposing_answer_key() -> None:
    assert _option_payload({"A": "one", "B": "two"}) == [
        {"key": "A", "label": "one"},
        {"key": "B", "label": "two"},
    ]
    assert _option_payload([{"key": "A", "label": "one"}, "two"])[1] == {"key": "B", "label": "two"}


def test_serialised_item_bank_item_uses_frontend_subject_and_option_keys() -> None:
    item = SimpleNamespace(
        item_id="item-1",
        stem="What is 1 + 1?",
        options=[{"key": "A", "label": "1"}, {"key": "B", "label": "2"}],
        subject="Mathematics",
        topic="Numbers",
        skill="Addition",
        difficulty_b=0.0,
        discrimination_a=1.0,
        caps_ref="CAPS:G3:MATHEMATICS:T1:NUMBERS:ADDITION",
        review_status="approved",
    )

    payload = _serialise_item_bank_item(item)

    assert payload["subject"] == "MATH"
    assert payload["options"] == [{"key": "A", "label": "1"}, {"key": "B", "label": "2"}]
    assert payload["option_keys"] == ["A", "B"]
    assert "answer_key" not in payload
