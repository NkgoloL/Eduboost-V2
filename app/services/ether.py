"""Deterministic onboarding archetype service compatibility layer."""

from __future__ import annotations

from app.models import ArchetypeLabel


class EtherService:
    def get_onboarding_questions(self) -> list[dict[str, object]]:
        return [
            {"id": 1, "prompt": "How do you like to learn?", "options": ["pictures", "practice", "stories"]},
            {"id": 2, "prompt": "What helps you focus?", "options": ["quiet", "music", "movement"]},
            {"id": 3, "prompt": "Pick a challenge style.", "options": ["guided", "solo", "team"]},
            {"id": 4, "prompt": "Choose a reward.", "options": ["stars", "badges", "levels"]},
            {"id": 5, "prompt": "Choose a pace.", "options": ["steady", "fast", "review"]},
        ]

    def classify_archetype(self, answers: list[dict[str, object]]) -> tuple[ArchetypeLabel, str, dict[str, float]]:
        answered = max(1, len(answers))
        label = ArchetypeLabel.TIFERET
        return (
            label,
            "Balanced learner profile generated from deterministic onboarding answers.",
            {label.value: 1.0, ArchetypeLabel.NETZACH.value: round(min(answered, 5) / 10, 2)},
        )


__all__ = ["EtherService"]
