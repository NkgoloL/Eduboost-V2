"""
EduBoost V2 — Ether Service (Pillar 5)
Psychological archetype profiling and cold-start onboarding micro-diagnostic.
Assigns a Kabbalistic archetype on session 1 — eliminates the legacy 8–10 event lag.
"""
from __future__ import annotations

from app.domain.models import ArchetypeLabel

# ── Cold-start onboarding questions ──────────────────────────────────────────
ONBOARDING_QUESTIONS = [
    {
        "id": 1,
        "text": "When you don't understand something, what do you prefer to do?",
        "options": {
            "A": "Think about it quietly on my own",
            "B": "Ask lots of questions",
            "C": "Draw a picture or diagram",
            "D": "Try it out straight away",
        },
    },
    {
        "id": 2,
        "text": "Which type of activity sounds most fun?",
        "options": {
            "A": "Solving a puzzle or mystery",
            "B": "Creating something with my hands",
            "C": "Reading a story",
            "D": "Competing in a game",
        },
    },
    {
        "id": 3,
        "text": "When you get something right, how do you feel best rewarded?",
        "options": {
            "A": "A badge or star",
            "B": "A compliment from a teacher",
            "C": "Seeing my progress on a chart",
            "D": "Moving on to a harder challenge",
        },
    },
    {
        "id": 4,
        "text": "How do you prefer to learn something new?",
        "options": {
            "A": "Step-by-step instructions",
            "B": "An exciting real-life story",
            "C": "A quick summary, then dive in",
            "D": "Watching someone else first",
        },
    },
    {
        "id": 5,
        "text": "Pick the word that best describes you:",
        "options": {
            "A": "Curious",
            "B": "Determined",
            "C": "Creative",
            "D": "Caring",
        },
    },
]

# ── Scoring matrix: (q_id, answer) → archetype scores ─────────────────────────
_SCORE_MAP: dict[tuple[int, str], dict[str, int]] = {
    (1, "A"): {"Keter": 2, "Binah": 1},
    (1, "B"): {"Chokmah": 2, "Chesed": 1},
    (1, "C"): {"Hod": 2, "Netzach": 1},
    (1, "D"): {"Yesod": 2, "Gevurah": 1},
    (2, "A"): {"Keter": 2, "Binah": 1},
    (2, "B"): {"Malkuth": 2, "Hod": 1},
    (2, "C"): {"Tiferet": 2, "Netzach": 1},
    (2, "D"): {"Gevurah": 2, "Yesod": 1},
    (3, "A"): {"Malkuth": 2, "Yesod": 1},
    (3, "B"): {"Chesed": 2, "Tiferet": 1},
    (3, "C"): {"Hod": 2, "Binah": 1},
    (3, "D"): {"Keter": 2, "Gevurah": 1},
    (4, "A"): {"Binah": 2, "Hod": 1},
    (4, "B"): {"Tiferet": 2, "Netzach": 1},
    (4, "C"): {"Chokmah": 2, "Keter": 1},
    (4, "D"): {"Yesod": 2, "Chesed": 1},
    (5, "A"): {"Keter": 2, "Chokmah": 1},
    (5, "B"): {"Gevurah": 2, "Yesod": 1},
    (5, "C"): {"Netzach": 2, "Tiferet": 1},
    (5, "D"): {"Chesed": 2, "Malkuth": 1},
}

_ARCHETYPE_DESCRIPTIONS = {
    "Keter": "A deep thinker who loves abstract puzzles and self-discovery.",
    "Chokmah": "A fast, intuitive learner who grasps ideas in a flash.",
    "Binah": "A methodical analyst who loves structured, step-by-step learning.",
    "Chesed": "A social learner who thrives on encouragement and group activities.",
    "Gevurah": "A driven competitor who needs challenges and clear milestones.",
    "Tiferet": "A balanced, narrative learner who connects knowledge to real life.",
    "Netzach": "A creative explorer who learns through art, music, and imagination.",
    "Hod": "A visual learner who processes information through diagrams and models.",
    "Yesod": "A hands-on learner who learns best by doing and experimenting.",
    "Malkuth": "A grounded, practical learner who values tangible rewards and routine.",
}


class EtherService:
    """
    Constitutional Pillar 5: The Ether.
    Assigns a psychological archetype on first session, bypassing the legacy lag.
    """

    def get_onboarding_questions(self) -> list[dict]:
        return ONBOARDING_QUESTIONS

    def classify_archetype(self, answers: list[dict]) -> tuple[ArchetypeLabel, str]:
        """
        answers: [{"question_id": int, "answer": str}, ...]
        Returns (ArchetypeLabel, description_string).
        """
        scores: dict[str, int] = {a.value: 0 for a in ArchetypeLabel}
        for a in answers:
            key = (int(a["question_id"]), str(a["answer"]).upper())
            for archetype, pts in _SCORE_MAP.get(key, {}).items():
                scores[archetype] = scores.get(archetype, 0) + pts

        best = max(scores, key=lambda k: scores[k])
        label = ArchetypeLabel(best)
        description = _ARCHETYPE_DESCRIPTIONS.get(best, "")
        return label, description

    def modify_prompt_for_archetype(self, base_prompt: str, archetype: ArchetypeLabel | None) -> str:
        """Append archetype-specific tone modifier to an LLM prompt."""
        modifiers = {
            ArchetypeLabel.KETER: "Use abstract reasoning and philosophical framing.",
            ArchetypeLabel.CHOKMAH: "Be concise and spark intuition — skip verbose explanations.",
            ArchetypeLabel.BINAH: "Use numbered steps and logical structure throughout.",
            ArchetypeLabel.CHESED: "Use warm, encouraging language and collaborative examples.",
            ArchetypeLabel.GEVURAH: "Frame as a challenge — use milestone markers and progress cues.",
            ArchetypeLabel.TIFERET: "Weave in a real-life SA story that connects the topic to daily life.",
            ArchetypeLabel.NETZACH: "Use vivid imagery, metaphors, and creative analogies.",
            ArchetypeLabel.HOD: "Emphasise diagrams, tables, and visual structures in text.",
            ArchetypeLabel.YESOD: "Include a hands-on activity or experiment the learner can try.",
            ArchetypeLabel.MALKUTH: "Use clear routines, concrete examples, and reward language.",
        }
        modifier = modifiers.get(archetype, "") if archetype else ""
        return f"{base_prompt}\n\nTone modifier: {modifier}" if modifier else base_prompt
