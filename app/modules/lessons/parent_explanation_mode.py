"""
parent_explanation_mode.py
==========================
Phase 4 — L4-06

Parent Explanation Mode: generates a concise, jargon-free 3-bullet summary
for parents/caregivers after a lesson is completed by a learner.

The summary answers three questions:
  1. What did your child practice today?
  2. What did they find hard?
  3. How can you help them in 10 minutes at home?

This is a SEPARATE LLM call from lesson generation — it takes the completed
lesson record and the learner's session performance data as input and generates
a parent-facing narrative in plain, accessible language.

Implements TODO §6.4.3: "Add parent explanation mode"
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Prompt template version for this mode
PARENT_SUMMARY_PROMPT_VERSION = "parent_explanation_v1"


# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------

class LearnerSessionPerformance(BaseModel):
    """
    Performance data from a completed lesson session, provided by the
    diagnostic/session tracking service.
    """
    learner_id: UUID
    lesson_id: UUID
    caps_ref: str
    topic: str
    subtopic: str
    grade: int

    # Session performance metrics
    questions_attempted: int
    questions_correct: int
    time_spent_seconds: int

    # Misconception signals (from wrong answer patterns)
    triggered_misconception_tags: list[str] = Field(
        default_factory=list,
        description="Misconception tags triggered by wrong answers in this session.",
    )

    # Difficulty self-report (optional — from learner UI)
    learner_self_reported_difficulty: Optional[str] = Field(
        None,
        description="Optional: learner's self-reported difficulty (easy/ok/hard/very_hard).",
    )


class ParentSummaryRequest(BaseModel):
    """Input to the parent summary generator."""
    lesson_id: UUID
    caps_ref: str
    topic: str
    subtopic: str
    grade: int
    subject: str
    difficulty_level: str

    # Learning objectives from the lesson
    learning_objectives: list[str]

    # Session performance
    performance: LearnerSessionPerformance

    # Optional: learner name (used to personalise the summary — must NOT be stored in LLM logs)
    learner_first_name: Optional[str] = Field(
        None,
        description=(
            "Learner's first name for personalisation. "
            "This is injected into the prompt locally and MUST NOT be logged or stored."
        ),
    )


# ---------------------------------------------------------------------------
# Output models
# ---------------------------------------------------------------------------

class ParentSummaryBullet(BaseModel):
    heading: str = Field(description="Short heading for this bullet (displayed in bold).")
    body: str = Field(description="1–3 sentence explanation for parents.")
    emoji: str = Field(description="Single emoji to visually anchor this bullet.")


class ParentSummaryResponse(BaseModel):
    lesson_id: UUID
    caps_ref: str
    generated_at: datetime
    prompt_template_version: str
    bullets: list[ParentSummaryBullet] = Field(
        min_length=3,
        max_length=3,
        description="Exactly 3 bullets: what they practiced, what was hard, how to help.",
    )
    home_activity_suggestion: str = Field(
        description="A single concrete 10-minute home activity suggestion for the parent.",
    )
    encouragement_note: str = Field(
        description=(
            "A warm, encouraging sentence about the learner's effort "
            "(not about the result — about the process)."
        ),
    )


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def build_parent_summary_prompt(request: ParentSummaryRequest) -> str:
    """
    Builds the LLM prompt for parent summary generation.

    NOTE: The learner's name is interpolated locally here and NEVER passed
    through the LLM logging pipeline. The LLM only sees a first name —
    no surname, ID, or other PII.
    """
    learner_ref = request.learner_first_name or "your child"
    score_pct = (
        round(request.performance.questions_correct / request.performance.questions_attempted * 100)
        if request.performance.questions_attempted > 0
        else 0
    )
    time_minutes = round(request.performance.time_spent_seconds / 60)

    misconception_context = ""
    if request.performance.triggered_misconception_tags:
        misconception_context = (
            "\n\nThe learner made errors that suggest these specific misunderstandings:\n"
            + "\n".join(
                f"  - {tag.replace('_', ' ').title()}"
                for tag in request.performance.triggered_misconception_tags
            )
            + "\n\nWhen describing what was hard, refer to these patterns in plain language "
            "that a parent (not a teacher) can understand. Do NOT use the tag names directly — "
            "translate them into everyday language."
        )

    difficulty_context = ""
    if request.performance.learner_self_reported_difficulty:
        d = request.performance.learner_self_reported_difficulty
        difficulty_context = f"\nThe learner said the lesson felt: {d}."

    return f"""You are writing a short, warm message to the parent or caregiver of a Grade {request.grade}
South African learner who just completed a maths lesson.

=== LESSON DETAILS ===
Subject : {request.subject}
Topic   : {request.topic}
Subtopic: {request.subtopic}
CAPS Ref: {request.caps_ref}

Learning Objectives:
{chr(10).join(f"  {i+1}. {obj}" for i, obj in enumerate(request.learning_objectives))}

=== LEARNER'S SESSION PERFORMANCE ===
Score         : {request.performance.questions_correct}/{request.performance.questions_attempted} ({score_pct}%)
Time on task  : approximately {time_minutes} minute(s){difficulty_context}{misconception_context}

=== YOUR TASK ===

Write a parent summary with EXACTLY this structure (JSON format):

{{
  "bullets": [
    {{
      "emoji": "📚",
      "heading": "What {learner_ref} practised today",
      "body": "1–2 sentences. Plain language. No jargon. Describe the maths concept in everyday terms a non-teacher parent can understand."
    }},
    {{
      "emoji": "🤔",
      "heading": "What {learner_ref} found tricky",
      "body": "1–2 sentences. Describe the specific difficulty in plain language. If the score was high (80%+), be encouraging and say what the small remaining challenge is. If score was low, be gentle and normalising — 'This is a tricky concept that many Grade {request.grade} learners find hard at first.'"
    }},
    {{
      "emoji": "🏠",
      "heading": "How you can help in 10 minutes",
      "body": "1–3 sentences. ONE very specific, practical activity a parent can do at home RIGHT NOW with no special resources. Use everyday SA objects (coins, beans, bottle caps, a ruler, paper). Do NOT say 'ask their teacher' or 'do more worksheets'."
    }}
  ],
  "home_activity_suggestion": "A single sentence describing the 10-minute activity in action-oriented language (e.g. 'Lay out 24 bottle caps on the table and ask {learner_ref} to share them equally between 4 cups.').",
  "encouragement_note": "One warm sentence about {learner_ref}'s effort — focus on the process, not the score. Mention something specific from the session (time spent, questions attempted, topic tackled). South African warmth — ubuntu spirit."
}}

=== RULES ===
- Write for a parent, not a teacher. No curriculum jargon. No abbreviations.
- Do NOT mention the score percentage in the bullets (it may discourage parents who see a low score).
- Do NOT say 'click here', 'see the app', or refer to the EduBoost platform by name in the text.
- Keep total word count under 200 words across all fields.
- The home activity must require NO screen time and NO printed materials.
- Output ONLY the JSON object. No preamble, no explanation, no markdown fences.
"""


# ---------------------------------------------------------------------------
# Generator service function
# ---------------------------------------------------------------------------

async def generate_parent_summary(
    request: ParentSummaryRequest,
    llm_gateway,  # avoid circular import
) -> ParentSummaryResponse:
    """
    Calls the LLM gateway to generate a parent-facing lesson summary.

    The learner's first name is injected into the prompt locally.
    The LLM call is logged WITHOUT the learner name (the name is stripped
    from the prompt before logging — handled in the gateway).

    Args:
        request: ParentSummaryRequest with lesson + performance data.
        llm_gateway: The production LLM gateway instance (Groq/Anthropic).

    Returns:
        ParentSummaryResponse with 3 bullets + home activity + encouragement.

    Raises:
        ParentSummaryGenerationError: If the LLM response cannot be parsed
        or does not match the expected schema.
    """
    prompt = build_parent_summary_prompt(request)

    logger.info(
        "Generating parent summary for lesson=%s caps_ref=%s",
        request.lesson_id,
        request.caps_ref,
    )

    try:
        raw_response = await llm_gateway.complete(
            prompt=prompt,
            max_tokens=600,
            temperature=0.4,  # Lower temperature for consistent, factual summaries
            prompt_template_version=PARENT_SUMMARY_PROMPT_VERSION,
            log_safe_metadata={
                "mode": "parent_summary",
                "lesson_id": str(request.lesson_id),
                "caps_ref": request.caps_ref,
                # NOTE: learner_id deliberately excluded from log metadata
            },
        )
    except Exception as exc:
        raise ParentSummaryGenerationError(
            f"LLM gateway call failed for parent summary (lesson={request.lesson_id}): {exc}"
        ) from exc

    # Parse and validate response
    try:
        clean = raw_response.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        data: dict[str, Any] = json.loads(clean)
    except json.JSONDecodeError as exc:
        raise ParentSummaryGenerationError(
            f"LLM returned non-JSON parent summary for lesson={request.lesson_id}: {exc}\n"
            f"Raw response (first 500 chars): {raw_response[:500]}"
        ) from exc

    # Validate and construct response
    try:
        bullets = [ParentSummaryBullet(**b) for b in data["bullets"]]
        if len(bullets) != 3:
            raise ValueError(f"Expected exactly 3 bullets, got {len(bullets)}")

        response = ParentSummaryResponse(
            lesson_id=request.lesson_id,
            caps_ref=request.caps_ref,
            generated_at=datetime.now(tz=timezone.utc),
            prompt_template_version=PARENT_SUMMARY_PROMPT_VERSION,
            bullets=bullets,
            home_activity_suggestion=data["home_activity_suggestion"],
            encouragement_note=data["encouragement_note"],
        )
    except (KeyError, ValueError) as exc:
        raise ParentSummaryGenerationError(
            f"Parent summary schema validation failed for lesson={request.lesson_id}: {exc}"
        ) from exc

    logger.info(
        "Parent summary generated successfully for lesson=%s",
        request.lesson_id,
    )
    return response


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------

class ParentSummaryGenerationError(Exception):
    """Raised when parent summary generation fails at any stage."""
