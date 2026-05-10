"""
app/services/lesson_context_builder.py
─────────────────────────────────────────────────────────────────────────────
Phase 4: Lesson Generator Context Injection (P4-07)

After a diagnostic session completes, the IRT engine returns three key signals:
    1. theta            — learner's ability estimate for the topic
    2. gap_topics       — caps_refs where θ is below grade-level threshold
    3. misconception_tags — aggregated from items answered incorrectly

This service translates those signals into a structured LessonContext that the
existing lesson generator (POST /api/v2/lessons/generate) can consume directly.
The lesson generator receives targeted, misconception-aware context instead of
just a generic topic label — making remediation lessons far more effective.

Usage:
    builder = LessonContextBuilder(caps_topic_map)
    context = builder.build(session_result, learner_profile)
    # pass context to LessonGeneratorService.generate(context)
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Grade-level threshold from irt_engine.py
GRADE_LEVEL_THRESHOLD = 0.0


@dataclass
class LessonContext:
    """
    Structured context passed to the lesson generator after a diagnostic.

    This is the P4-07 output contract. Every field maps to a variable in the
    lesson generation Jinja2 prompt template.
    """
    # Core identification
    learner_id:    str
    caps_ref:      str
    grade:         int
    subject:       str
    term:          int
    topic:         str
    subtopic:      str
    language:      str = "en"

    # IRT signals
    theta:               float = 0.0       # Learner's ability estimate
    below_grade_level:   bool  = False     # True when θ < GRADE_LEVEL_THRESHOLD
    severity:            str   = "moderate"  # "mild" | "moderate" | "severe"

    # Misconception-aware context (the key value-add of P4-07)
    misconception_tags:  list[str] = field(default_factory=list)
    gap_topics:          list[str] = field(default_factory=list)

    # Lesson generation hints
    remediation_focus:   str = ""          # Human-readable description of what to fix
    suggested_examples:  list[str] = field(default_factory=list)  # From topic map
    prior_correct_count: int = 0
    prior_attempted:     int = 0

    def to_prompt_dict(self) -> dict:
        """
        Serialise to a flat dict for Jinja2 template injection.
        All values are JSON-safe (str, int, float, bool, list[str]).
        """
        return {
            "learner_id":          self.learner_id,
            "caps_ref":            self.caps_ref,
            "grade":               self.grade,
            "subject":             self.subject,
            "term":                self.term,
            "topic":               self.topic,
            "subtopic":            self.subtopic,
            "language":            self.language,
            "theta":               round(self.theta, 3),
            "below_grade_level":   self.below_grade_level,
            "severity":            self.severity,
            "misconception_tags":  self.misconception_tags,
            "gap_topics":          self.gap_topics,
            "remediation_focus":   self.remediation_focus,
            "suggested_examples":  self.suggested_examples,
            "prior_correct_count": self.prior_correct_count,
            "prior_attempted":     self.prior_attempted,
            "accuracy_pct":        round(
                self.prior_correct_count / self.prior_attempted * 100, 1
            ) if self.prior_attempted > 0 else 0.0,
        }


class LessonContextBuilder:
    """
    Builds a LessonContext from an IRT session result.

    caps_topic_map is a dict keyed by caps_ref, e.g.:
        {
          "4.M.1.1": {
            "grade": 4, "subject": "Mathematics", "term": 1,
            "topic": "Whole Numbers", "subtopic": "Count and Order",
            "skill": "place_value_ordering",
            "suggested_examples": ["Order 1 234, 2 341, 3 412 from smallest."]
          }
        }
    This map is loaded from data/caps/caps_topic_map_grade4_maths.json at
    app startup and injected into this service.
    """

    def __init__(self, caps_topic_map: dict[str, dict]) -> None:
        self._map = caps_topic_map

    def build(
        self,
        session_result: dict,
        learner_language: str = "en",
    ) -> LessonContext:
        """
        Convert a session result dict (from IRTEngine.session_result) into a
        LessonContext ready for the lesson generator.

        Args:
            session_result:   Output of DiagnosticSessionService.finalise_session().
            learner_language: Learner's preferred language for the lesson ("en", "zu", "af", "xh").

        Returns:
            LessonContext with all fields populated.
        """
        caps_ref = session_result.get("caps_ref", "")
        theta    = float(session_result.get("theta", 0.0))

        topic_meta = self._map.get(caps_ref, {})
        if not topic_meta:
            logger.warning(
                "caps_ref %s not found in topic map — using minimal context.", caps_ref
            )

        # Determine severity of the learning gap
        severity = self._classify_severity(theta)

        # Build a human-readable remediation focus string for the prompt
        misconception_tags: list[str] = session_result.get("misconception_tags", [])
        remediation_focus = self._build_remediation_focus(
            topic=topic_meta.get("topic", caps_ref),
            subtopic=topic_meta.get("subtopic", ""),
            misconception_tags=misconception_tags,
            severity=severity,
        )

        context = LessonContext(
            learner_id=session_result.get("learner_id", ""),
            caps_ref=caps_ref,
            grade=topic_meta.get("grade", 4),
            subject=topic_meta.get("subject", "Mathematics"),
            term=topic_meta.get("term", 1),
            topic=topic_meta.get("topic", caps_ref),
            subtopic=topic_meta.get("subtopic", ""),
            language=learner_language,
            theta=theta,
            below_grade_level=session_result.get("below_grade_level", False),
            severity=severity,
            misconception_tags=misconception_tags,
            gap_topics=session_result.get("gap_topics", []),
            remediation_focus=remediation_focus,
            suggested_examples=topic_meta.get("suggested_examples", []),
            prior_correct_count=session_result.get("items_correct", 0),
            prior_attempted=session_result.get("items_attempted", 0),
        )

        logger.info(
            "Built lesson context: caps_ref=%s θ=%.3f severity=%s misconceptions=%s",
            caps_ref, theta, severity, misconception_tags,
        )
        return context

    # ─── Internal helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _classify_severity(theta: float) -> str:
        """
        Translate an ability estimate into a remediation severity level.

        Severity guides the lesson generator's tone and depth:
          - "mild"     → learner is slightly below grade level; light review needed
          - "moderate" → learner is below grade level; targeted practice needed
          - "severe"   → learner is significantly below grade level; foundational
                         concepts must be re-taught before grade-level content
        """
        if theta >= GRADE_LEVEL_THRESHOLD:
            return "mild"       # At or above grade level — reinforcement only
        elif theta >= -1.0:
            return "moderate"   # Slightly below
        else:
            return "severe"     # Significantly below — foundational re-teaching

    @staticmethod
    def _build_remediation_focus(
        topic: str,
        subtopic: str,
        misconception_tags: list[str],
        severity: str,
    ) -> str:
        """
        Build a plain-English focus string for the lesson prompt template.

        Examples:
          "Focus on correcting place_value_confusion in Whole Numbers
           (Counting and Ordering). The learner shows severe gaps and needs
           foundational re-teaching before advancing."
        """
        parts = [f"Focus on {topic}"]
        if subtopic:
            parts.append(f"({subtopic})")

        if misconception_tags:
            tags_str = ", ".join(misconception_tags[:3])  # top 3 for prompt brevity
            parts.append(f"with emphasis on correcting: {tags_str}")

        severity_hints = {
            "mild":     "Light reinforcement and extension activities are appropriate.",
            "moderate": "Targeted practice with worked examples is recommended.",
            "severe":   (
                "The learner needs foundational re-teaching. "
                "Start from first principles before advancing to grade-level content."
            ),
        }
        parts.append(severity_hints.get(severity, ""))

        return " ".join(parts)
