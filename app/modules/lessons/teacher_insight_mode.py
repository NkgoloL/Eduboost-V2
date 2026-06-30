"""
teacher_insight_mode.py
=======================
Phase 4 — L4-07

Teacher Insight Mode: aggregates misconception_tags across a learner cohort
for a given CAPS reference and generates a class-level misconception report
with intervention group suggestions.

Teachers receive:
  1. A ranked list of misconceptions across the class (how many learners, which tags).
  2. Automatically suggested intervention groups (learners grouped by shared misconceptions).
  3. LLM-generated teaching suggestions per misconception cluster.
  4. A suggested next lesson focus per group.

Implements TODO §6.4.3: "Add teacher insight mode: aggregate misconception_tags
across a learner cohort for a caps_ref; generate class misconception report
with intervention group suggestions."
"""

from __future__ import annotations

import json
import logging
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

TEACHER_INSIGHT_PROMPT_VERSION = "teacher_insight_v1"


# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------

class LearnerMisconceptionRecord(BaseModel):
    """
    A single learner's misconception data for a given CAPS topic.
    Sourced from diagnostic session records.
    NOTE: Only anonymised learner_id (UUID) is passed — no names or PII.
    """
    learner_id: UUID
    misconception_tags: list[str]
    questions_correct: int
    questions_attempted: int
    last_session_at: datetime


class TeacherInsightRequest(BaseModel):
    """Input to the teacher insight generator."""
    teacher_id: UUID
    caps_ref: str
    topic: str
    subtopic: str
    grade: int
    subject: str
    cohort_label: str = Field(
        description="Human label for this cohort (e.g. 'Grade 4A', 'Term 1 Maths Group')."
    )
    learner_records: list[LearnerMisconceptionRecord] = Field(
        min_length=1,
        description="All learner records for this caps_ref in the cohort.",
    )


# ---------------------------------------------------------------------------
# Output models
# ---------------------------------------------------------------------------

class MisconceptionCluster(BaseModel):
    """A cluster of learners sharing a dominant misconception."""
    misconception_tag: str
    plain_language_description: str = Field(
        description="Human-readable description of the misconception for the teacher."
    )
    learner_count: int
    learner_ids: list[UUID] = Field(
        description="Anonymised learner IDs in this cluster (for teacher's class list lookup)."
    )
    prevalence_pct: float = Field(description="Percentage of cohort affected.")
    suggested_intervention: str = Field(
        description="LLM-generated 2–3 sentence teaching strategy for this misconception."
    )
    suggested_next_caps_ref: Optional[str] = Field(
        None,
        description="Optional: CAPS ref to revisit as a prerequisite for this misconception.",
    )


class InterventionGroup(BaseModel):
    """A small-group intervention suggestion."""
    group_label: str = Field(description="E.g. 'Group A — Place Value Confusion'")
    priority: str = Field(description="high | medium | low")
    learner_ids: list[UUID]
    learner_count: int
    shared_misconceptions: list[str]
    recommended_lesson_variant: str = Field(
        description=(
            "Which lesson variant type is recommended for this group: "
            "visual | story | step_by_step | exam_style | multilingual | re_explain | "
            "worked_example_focus | practice_drill | misconception_correction"
        )
    )
    intervention_note: str = Field(
        description="2–3 sentence teaching note for the teacher."
    )


class TeacherInsightResponse(BaseModel):
    caps_ref: str
    topic: str
    subtopic: str
    cohort_label: str
    cohort_size: int
    generated_at: datetime
    prompt_template_version: str

    # Aggregate stats
    class_average_score_pct: float
    learners_below_70_pct: int
    most_common_misconceptions: list[str] = Field(
        description="Top 5 misconception tags by prevalence, most common first."
    )

    # Misconception clusters (one per significant misconception)
    misconception_clusters: list[MisconceptionCluster]

    # Intervention groups
    intervention_groups: list[InterventionGroup]

    # Overall class teaching suggestion
    whole_class_teaching_note: str = Field(
        description="2–3 sentence summary for the teacher about the whole class's state."
    )

    # Ready-to-share summary (can be printed or copied)
    printable_summary: str = Field(
        description=(
            "Plain-text summary of the class report, suitable for printing "
            "or sharing in a staff meeting."
        )
    )


# ---------------------------------------------------------------------------
# Aggregation logic (no LLM needed for stats)
# ---------------------------------------------------------------------------

def aggregate_cohort_misconceptions(
    request: TeacherInsightRequest,
) -> dict[str, Any]:
    """
    Computes aggregate stats from learner records without an LLM call.
    Returns a structured dict used to build the LLM prompt and the response.
    """
    total_learners = len(request.learner_records)

    # Score aggregation
    all_scores_pct = [
        round(r.questions_correct / r.questions_attempted * 100)
        if r.questions_attempted > 0 else 0
        for r in request.learner_records
    ]
    class_avg = round(sum(all_scores_pct) / total_learners, 1) if total_learners > 0 else 0
    below_70 = sum(1 for s in all_scores_pct if s < 70)

    # Misconception frequency
    all_tags: list[str] = []
    for record in request.learner_records:
        all_tags.extend(record.misconception_tags)

    tag_counts = Counter(all_tags)
    top_tags = [tag for tag, _ in tag_counts.most_common(5)]

    # Per-tag learner lists
    tag_to_learners: dict[str, list[UUID]] = {}
    for record in request.learner_records:
        for tag in set(record.misconception_tags):  # set: don't double-count same tag
            tag_to_learners.setdefault(tag, []).append(record.learner_id)

    return {
        "total_learners": total_learners,
        "class_avg": class_avg,
        "below_70": below_70,
        "top_tags": top_tags,
        "tag_counts": dict(tag_counts),
        "tag_to_learners": tag_to_learners,
        "all_scores_pct": all_scores_pct,
    }


def build_intervention_groups(
    tag_to_learners: dict[str, list[UUID]],
    tag_counts: dict[str, int],
    total_learners: int,
) -> list[InterventionGroup]:
    """
    Builds intervention groups from misconception clusters.
    Uses heuristics to assign learners to groups and recommend lesson variants.
    """
    groups: list[InterventionGroup] = []

    # Sort tags by prevalence
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

    for i, (tag, count) in enumerate(sorted_tags[:4]):  # Cap at 4 groups
        prevalence = count / total_learners
        priority = "high" if prevalence >= 0.4 else ("medium" if prevalence >= 0.2 else "low")

        # Recommend a lesson variant based on tag category
        variant = _recommend_variant_for_tag(tag)

        group_label = f"Group {chr(65 + i)} — {tag.replace('_', ' ').title()}"

        groups.append(
            InterventionGroup(
                group_label=group_label,
                priority=priority,
                learner_ids=tag_to_learners.get(tag, []),
                learner_count=len(tag_to_learners.get(tag, [])),
                shared_misconceptions=[tag],
                recommended_lesson_variant=variant,
                intervention_note=(
                    f"These learners have shown the '{tag.replace('_', ' ')}' pattern "
                    f"in {count} of {total_learners} learners ({round(prevalence * 100)}% of class). "
                    f"Recommended approach: {variant.replace('_', ' ')} lesson variant."
                ),
            )
        )

    return groups


def _recommend_variant_for_tag(tag: str) -> str:
    """Heuristic: map misconception tag patterns to recommended lesson variants."""
    tag_lower = tag.lower()
    if "confusion" in tag_lower or "conflates" in tag_lower:
        return "misconception_correction"
    if "fluency" in tag_lower or "slow" in tag_lower:
        return "practice_drill"
    if "procedure" in tag_lower or "carry" in tag_lower or "borrow" in tag_lower:
        return "worked_example_focus"
    if "visual" in tag_lower or "shape" in tag_lower or "spatial" in tag_lower:
        return "visual"
    if "general" in tag_lower:
        return "re_explain"
    return "step_by_step"


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def build_teacher_insight_prompt(
    request: TeacherInsightRequest,
    agg: dict[str, Any],
) -> str:
    """Builds the LLM prompt for teacher insight generation."""
    tag_summary = "\n".join(
        f"  - {tag.replace('_', ' ').title()}: "
        f"{count} learner(s) ({round(count / agg['total_learners'] * 100)}%)"
        for tag, count in sorted(
            agg["tag_counts"].items(), key=lambda x: x[1], reverse=True
        )[:6]
    )

    return f"""You are an expert South African Grade {request.grade} Mathematics curriculum specialist
writing a professional report for a teacher.

=== CLASS DATA ===
CAPS Reference  : {request.caps_ref}
Topic           : {request.topic}
Subtopic        : {request.subtopic}
Cohort          : {request.cohort_label}
Learners assessed: {agg['total_learners']}
Class average   : {agg['class_avg']}%
Learners below 70%: {agg['below_70']} of {agg['total_learners']}

Most common misconceptions (by number of learners affected):
{tag_summary if tag_summary else "  No significant misconception patterns detected."}

=== YOUR TASK ===

Generate a teacher insight report as a JSON object with this exact structure:

{{
  "misconception_clusters": [
    {{
      "misconception_tag": "exact_tag_string",
      "plain_language_description": "1 sentence — what this misconception looks like in a learner's work. Write for a teacher, not a researcher.",
      "suggested_intervention": "2–3 sentences. Practical teaching strategy for a South African Grade {request.grade} classroom. Must be doable without special resources.",
      "suggested_next_caps_ref": "optional — a prerequisite CAPS ref to revisit, e.g. '3.M.2.1', or null"
    }}
  ],
  "whole_class_teaching_note": "2–3 sentences summarising the class's overall state and ONE whole-class teaching priority for the next lesson. Be direct and specific.",
  "printable_summary": "A plain-text paragraph (5–8 sentences) summarising: what the class practised, how they performed overall, what the main challenge is, and what the teacher should focus on next. Write in professional but accessible English. No bullet points — flowing paragraph."
}}

=== RULES ===
- Write for a South African teacher, not an international audience.
- Use CAPS terminology correctly (term, topic, subtopic, assessment standard).
- Do NOT mention individual learner IDs or any personal information.
- Teaching strategies must be practical for a South African classroom context
  (potentially large classes, limited resources, multilingual learners).
- Do NOT recommend purchasing materials. Use what's in the classroom.
- Output ONLY the JSON object. No preamble, no markdown fences.
"""


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

async def generate_teacher_insight(
    request: TeacherInsightRequest,
    llm_gateway,  # type: LLMGateway
) -> TeacherInsightResponse:
    """
    Generates a teacher insight report for a given cohort and CAPS reference.

    Aggregation (stats, grouping) is computed locally without an LLM call.
    The LLM is only used to generate natural-language descriptions,
    intervention suggestions, and the printable summary.

    Args:
        request: TeacherInsightRequest with cohort data.
        llm_gateway: Production LLM gateway (Groq/Anthropic).

    Returns:
        TeacherInsightResponse with full class report.
    """
    logger.info(
        "Generating teacher insight: caps_ref=%s cohort=%s learners=%d",
        request.caps_ref,
        request.cohort_label,
        len(request.learner_records),
    )

    # Step 1: aggregate stats locally
    agg = aggregate_cohort_misconceptions(request)

    # Step 2: build intervention groups (no LLM needed)
    intervention_groups = build_intervention_groups(
        agg["tag_to_learners"],
        agg["tag_counts"],
        agg["total_learners"],
    )

    # Step 3: LLM call for natural language descriptions
    prompt = build_teacher_insight_prompt(request, agg)

    try:
        raw_response = await llm_gateway.complete(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.3,
            prompt_template_version=TEACHER_INSIGHT_PROMPT_VERSION,
            log_safe_metadata={
                "mode": "teacher_insight",
                "caps_ref": request.caps_ref,
                "cohort_label": request.cohort_label,
                "cohort_size": agg["total_learners"],
                # No learner IDs in log metadata
            },
        )
    except Exception as exc:
        raise TeacherInsightGenerationError(
            f"LLM call failed for teacher insight (caps_ref={request.caps_ref}): {exc}"
        ) from exc

    # Step 4: parse LLM response
    try:
        clean = raw_response.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        data: dict[str, Any] = json.loads(clean)
    except json.JSONDecodeError as exc:
        raise TeacherInsightGenerationError(
            f"LLM returned non-JSON teacher insight: {exc}\n"
            f"Raw (first 500): {raw_response[:500]}"
        ) from exc

    # Step 5: build MisconceptionCluster objects (merge LLM descriptions with local stats)
    clusters: list[MisconceptionCluster] = []
    llm_clusters = data.get("misconception_clusters", [])
    for llm_cluster in llm_clusters:
        tag = llm_cluster.get("misconception_tag", "")
        learner_ids = agg["tag_to_learners"].get(tag, [])
        count = agg["tag_counts"].get(tag, 0)
        clusters.append(
            MisconceptionCluster(
                misconception_tag=tag,
                plain_language_description=llm_cluster.get("plain_language_description", ""),
                learner_count=count,
                learner_ids=learner_ids,
                prevalence_pct=round(count / agg["total_learners"] * 100, 1)
                if agg["total_learners"] > 0 else 0,
                suggested_intervention=llm_cluster.get("suggested_intervention", ""),
                suggested_next_caps_ref=llm_cluster.get("suggested_next_caps_ref"),
            )
        )

    # Update intervention group notes with LLM-enriched descriptions
    for group in intervention_groups:
        for cluster in clusters:
            if cluster.misconception_tag in group.shared_misconceptions:
                group.intervention_note = cluster.suggested_intervention
                break

    response = TeacherInsightResponse(
        caps_ref=request.caps_ref,
        topic=request.topic,
        subtopic=request.subtopic,
        cohort_label=request.cohort_label,
        cohort_size=agg["total_learners"],
        generated_at=datetime.now(tz=timezone.utc),
        prompt_template_version=TEACHER_INSIGHT_PROMPT_VERSION,
        class_average_score_pct=agg["class_avg"],
        learners_below_70_pct=agg["below_70"],
        most_common_misconceptions=agg["top_tags"],
        misconception_clusters=clusters,
        intervention_groups=intervention_groups,
        whole_class_teaching_note=data.get("whole_class_teaching_note", ""),
        printable_summary=data.get("printable_summary", ""),
    )

    logger.info(
        "Teacher insight generated: caps_ref=%s clusters=%d groups=%d",
        request.caps_ref,
        len(clusters),
        len(intervention_groups),
    )
    return response


class TeacherInsightGenerationError(Exception):
    """Raised when teacher insight generation fails."""
