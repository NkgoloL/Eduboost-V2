from __future__ import annotations

from app.modules.learners.ether_service import EtherService


def test_all_ten_archetypes_are_reachable() -> None:
    service = EtherService()
    answer_sets = {
        "Keter": ["A", "A", "D", "C", "A"],
        "Chokmah": ["B", "C", "A", "C", "A"],
        "Binah": ["A", "A", "C", "A", "A"],
        "Chesed": ["B", "C", "B", "D", "D"],
        "Gevurah": ["D", "D", "D", "A", "B"],
        "Tiferet": ["B", "C", "B", "B", "C"],
        "Netzach": ["C", "C", "C", "B", "C"],
        "Hod": ["C", "B", "C", "A", "A"],
        "Yesod": ["D", "D", "A", "D", "B"],
        "Malkuth": ["C", "B", "A", "D", "D"],
    }

    for expected, answers in answer_sets.items():
        payload = [
            {"question_id": index + 1, "answer": answer}
            for index, answer in enumerate(answers)
        ]
        label, _description, probabilities = service.classify_archetype(payload)
        assert label.value == expected
        assert abs(sum(probabilities.values()) - 1.0) < 0.02


def test_posterior_distribution_rewards_consistent_signal() -> None:
    service = EtherService()
    label, _description, probabilities = service.classify_archetype(
        [
            {"question_id": 1, "answer": "D"},
            {"question_id": 2, "answer": "D"},
            {"question_id": 3, "answer": "A"},
            {"question_id": 4, "answer": "D"},
            {"question_id": 5, "answer": "B"},
        ]
    )

    assert label.value == "Yesod"
    assert probabilities["Yesod"] > probabilities["Chesed"]

