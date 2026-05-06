from __future__ import annotations

from types import SimpleNamespace

from app.modules.diagnostics.irt_engine import DiagnosticEngine, fisher_information


def _item(item_id: str, b_param: float, topic: str = "fractions"):
    return SimpleNamespace(
        id=item_id,
        grade=4,
        subject="Mathematics",
        topic=topic,
        a_param=1.2,
        b_param=b_param,
    )


def test_gap_probe_cascade_uses_eap_and_returns_ranked_gaps() -> None:
    engine = DiagnosticEngine()
    items = [
        _item("item-1", -1.0, "place value"),
        _item("item-2", -0.3, "fractions"),
        _item("item-3", 0.2, "fractions"),
        _item("item-4", 1.1, "geometry"),
        _item("item-5", 1.8, "geometry"),
    ]

    analysis = engine.run_gap_probe_cascade(
        learner_grade=4,
        items=items,
        correct_item_ids={"item-1", "item-2", "item-3"},
    )

    assert analysis["theta"] > -0.5
    assert analysis["standard_error"] < 1.0
    assert analysis["grade_equivalent"] >= 4
    assert analysis["ranked_gaps"][0]["topic"] == "geometry"
    assert analysis["stopped"] in {True, False}


def test_select_next_item_uses_maximum_fisher_information() -> None:
    engine = DiagnosticEngine()
    theta = 0.0
    bank = [_item("easy", -2.0), _item("target", 0.0), _item("hard", 2.0)]

    chosen = engine.select_next_item(theta, set(), bank)

    assert chosen is not None
    assert chosen.id == "target"
    assert fisher_information(theta, chosen.a_param, chosen.b_param) >= fisher_information(theta, 1.2, -2.0)

