"""Deterministic lesson generator used by the V2 lesson service."""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any


class QuotaExceededError(Exception):
    """Raised when a metered lesson provider refuses a generation request."""


@dataclass
class _LessonPayload:
    title: str
    introduction: str
    explanation: str
    examples: list[str]
    practice: list[str]
    summary: str
    caps_reference: str
    alignment_confidence: float = 1.0
    quality_score: float = 1.0
    trust_label: Any = None


class LessonGenerator:
    """Small deterministic provider for local/runtime-readiness generation.

    The production LLM stack remains out of scope for the seeded E2E authority
    slice; this class supplies stable CAPS-shaped content without external LLM
    calls or runtime KG claims.
    """

    async def generate_lesson(
        self,
        *,
        grade: int,
        subject: str,
        topic: str,
        language: str = "en",
        **_: Any,
    ) -> tuple[_LessonPayload, bool]:
        topic_text = topic or "Fractions"
        subject_text = subject or "Mathematics"
        return (
            _LessonPayload(
                title=f"Grade {grade} {subject_text}: {topic_text}",
                introduction=f"Today we explore {topic_text} using clear examples and practice.",
                explanation=(
                    f"{topic_text} helps learners connect ideas, explain their reasoning, "
                    "and solve problems step by step."
                ),
                examples=[
                    f"Worked example for {topic_text}: identify the key information first.",
                    "Check the answer by explaining why it makes sense.",
                ],
                practice=[
                    "Try one guided question with support.",
                    "Try one independent question and explain your method.",
                ],
                summary=f"You practised {topic_text} in {language}.",
                caps_reference=f"Grade {grade} {subject_text} seeded runtime-readiness lesson",
                trust_label=SimpleNamespace(model_dump=lambda: {"source": "deterministic_seeded_e2e"}),
            ),
            False,
        )


__all__ = ["LessonGenerator", "QuotaExceededError"]
