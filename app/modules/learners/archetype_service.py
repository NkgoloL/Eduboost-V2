"""Psychological archetype profiling and cold-start onboarding.

Learner Archetype Profiling Service.  Assigns a Kabbalistic archetype
on the learner's first session via a five-question micro-diagnostic,
eliminating the legacy 8–10 event lag.

The archetype drives LLM prompt-tone modifiers so that lesson content
is personalised for the learner's cognitive style (e.g. visual, hands-on,
narrative).  See :meth:`ArchetypeService.modify_prompt_for_archetype`.

Example:
    Classify a learner during onboarding::

        from app.modules.learners.archetype_service import ArchetypeService

        svc = ArchetypeService()
        answers = [
            {"question_id": 1, "answer": "A"},
            {"question_id": 2, "answer": "C"},
            {"question_id": 3, "answer": "D"},
            {"question_id": 4, "answer": "B"},
            {"question_id": 5, "answer": "A"},
        ]
        label, description, scores = svc.classify_archetype(answers)
        print(f"{label.value}: {description}")
"""
from __future__ import annotations

from collections.abc import Iterable

from app.domain.models import ArchetypeLabel

# ── Cold-start onboarding questions ──────────────────────────────────────────
ONBOARDING_QUESTIONS: list[dict] = [
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
"""Five-question micro-diagnostic for first-session archetype assignment.

Each question has four options (A–D) mapped to archetype likelihood
scores in :data:`_LIKELIHOOD_MAP`.
"""

# ── Scoring matrix: (q_id, answer) → archetype scores ─────────────────────────
_LIKELIHOOD_MAP: dict[tuple[int, str], dict[str, float]] = {
    (1, "A"): {"Keter": 0.64, "Binah": 0.23},
    (1, "B"): {"Chokmah": 0.65, "Chesed": 0.22},
    (1, "C"): {"Hod": 0.62, "Netzach": 0.24},
    (1, "D"): {"Yesod": 0.63, "Gevurah": 0.24},
    (2, "A"): {"Binah": 0.62, "Keter": 0.24},
    (2, "B"): {"Malkuth": 0.64, "Hod": 0.22},
    (2, "C"): {"Tiferet": 0.65, "Netzach": 0.22},
    (2, "D"): {"Gevurah": 0.62, "Yesod": 0.24},
    (3, "A"): {"Malkuth": 0.62, "Yesod": 0.24},
    (3, "B"): {"Chesed": 0.64, "Tiferet": 0.22},
    (3, "C"): {"Hod": 0.64, "Binah": 0.22},
    (3, "D"): {"Keter": 0.63, "Gevurah": 0.24},
    (4, "A"): {"Binah": 0.66, "Hod": 0.2},
    (4, "B"): {"Tiferet": 0.64, "Netzach": 0.22},
    (4, "C"): {"Chokmah": 0.65, "Keter": 0.21},
    (4, "D"): {"Yesod": 0.65, "Chesed": 0.22},
    (5, "A"): {"Keter": 0.62, "Chokmah": 0.24},
    (5, "B"): {"Gevurah": 0.65, "Yesod": 0.21},
    (5, "C"): {"Netzach": 0.66, "Tiferet": 0.2},
    (5, "D"): {"Chesed": 0.63, "Malkuth": 0.23},
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


class ArchetypeService:
    """Learner Archetype Profiling Service — archetype profiling service.

    Assigns a psychological archetype on the learner's first session
    by scoring five onboarding questions against a Bayesian likelihood
    matrix.  The resulting :class:`~app.domain.models.ArchetypeLabel`
    is persisted on the learner profile and used to tailor LLM prompts.

    Example:
        ::

            svc = ArchetypeService()
            label, desc, scores = svc.classify_archetype(answers)
    """

    def get_onboarding_questions(self) -> list[dict]:
        """Return the cold-start onboarding questions.

        Returns:
            list[dict]: List of question dictionaries from
            :data:`ONBOARDING_QUESTIONS`, each containing ``id``,
            ``text``, and ``options``.

        Example:
            ::

                questions = svc.get_onboarding_questions()
                assert len(questions) == 5
        """
        return ONBOARDING_QUESTIONS

    def classify_archetype(self, answers: list[dict]) -> tuple[ArchetypeLabel, str, dict[str, float]]:
        """Classify a learner archetype from onboarding answers.

        Computes the posterior distribution via
        :meth:`posterior_distribution`, selects the maximum-probability
        archetype, and returns its :class:`~app.domain.models.ArchetypeLabel`
        with a human-readable description.

        Args:
            answers: List of answer dictionaries, each containing
                ``question_id`` (``int``) and ``answer`` (``str``,
                one of ``"A"``–``"D"``).

        Returns:
            tuple[ArchetypeLabel, str, dict[str, float]]:
            ``(label, description, posterior_scores)``.

        Example:
            ::

                label, desc, scores = svc.classify_archetype([
                    {"question_id": 1, "answer": "A"},
                    {"question_id": 2, "answer": "C"},
                    {"question_id": 3, "answer": "D"},
                    {"question_id": 4, "answer": "B"},
                    {"question_id": 5, "answer": "A"},
                ])
                assert isinstance(label, ArchetypeLabel)
        """
        scores = self.posterior_distribution(answers)
        best = max(scores, key=scores.get)
        label = ArchetypeLabel(best)
        description = _ARCHETYPE_DESCRIPTIONS.get(best, "")
        return label, description, scores

    def posterior_distribution(self, answers: Iterable[dict]) -> dict[str, float]:
        """Compute the posterior archetype distribution.

        Applies Bayesian updating over the :data:`_LIKELIHOOD_MAP`
        evidence for each answer, starting from a uniform prior over
        all :class:`~app.domain.models.ArchetypeLabel` values.

        Args:
            answers: Iterable of answer dictionaries with
                ``question_id`` and ``answer`` keys.

        Returns:
            dict[str, float]: Normalised probability distribution
            over archetype label strings, rounded to 4 decimal places.

        Example:
            ::

                scores = svc.posterior_distribution([
                    {"question_id": 1, "answer": "B"},
                ])
                assert abs(sum(scores.values()) - 1.0) < 0.01
        """
        posterior: dict[str, float] = {a.value: 1.0 / len(ArchetypeLabel) for a in ArchetypeLabel}
        for answer in answers:
            key = (int(answer["question_id"]), str(answer["answer"]).upper())
            evidence = _LIKELIHOOD_MAP.get(key, {})
            for archetype in posterior:
                posterior[archetype] *= evidence.get(archetype, 0.04)
            total = sum(posterior.values()) or 1.0
            posterior = {archetype: weight / total for archetype, weight in posterior.items()}
        return {archetype: round(weight, 4) for archetype, weight in posterior.items()}

    def modify_prompt_for_archetype(self, base_prompt: str, archetype: ArchetypeLabel | None) -> str:
        """Append an archetype-specific tone modifier to an LLM prompt.

        Each :class:`~app.domain.models.ArchetypeLabel` maps to a
        one-sentence instruction that adjusts the LLM's pedagogical
        tone (e.g. visual emphasis for Hod, hands-on for Yesod).

        Args:
            base_prompt: The original LLM prompt text.
            archetype: The learner's assigned archetype, or ``None``
                to leave the prompt unmodified.

        Returns:
            str: The prompt with an appended ``Tone modifier:`` line,
            or the original prompt if ``archetype`` is ``None``.

        Example:
            ::

                modified = svc.modify_prompt_for_archetype(
                    "Explain multiplication.",
                    ArchetypeLabel.HOD,
                )
                assert "diagrams" in modified.lower()
        """
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
