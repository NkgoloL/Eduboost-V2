"""Study-plan template generator linked to scope lessons and assessments."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.services.content_generation.generated_lesson_contract import LESSON_VARIANTS


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _slug(scope_id: str) -> str:
    return scope_id.replace("_", "-")


class ScopeStudyPlanGenerator:
    """Build term-aware study plans with remediation and extension mappings."""

    def generate(
        self,
        scope_id: str,
        caps_refs: list[str],
        contexts: dict[str, dict[str, Any]],
        *,
        source_context_hashes: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        source_context_hashes = source_context_hashes or {}
        first = contexts[caps_refs[0]]
        slug = _slug(scope_id)
        weekly_template = self._weekly_template(scope_id, slug, caps_refs, contexts)
        topic_sequence = []
        remediation_mappings = []
        extension_mappings = []

        for ref in caps_refs:
            context = contexts[ref]
            misconception_tags = context.get("common_misconceptions") or ["needs_step_by_step_support"]
            safe_ref = ref.replace(".", "-")
            topic_sequence.append(
                {
                    "caps_ref": ref,
                    "topic": context["topic"],
                    "subtopic": context.get("subtopic") or context["topic"],
                    "term": context.get("term", 1),
                    "prerequisites": context.get("prerequisites", []),
                    "misconception_tags": misconception_tags,
                    "assessment_standards": (context.get("assessment_standards") or [])[:2],
                    "source_context_hash": source_context_hashes.get(ref),
                    "recommended_lesson_variants": list(LESSON_VARIANTS[:4]),
                }
            )
            for tag in misconception_tags:
                remediation_mappings.append(
                    {
                        "misconception_tag": tag,
                        "caps_ref": ref,
                        "topic": context["topic"],
                        "lesson_variant": "step_by_step",
                        "assessment_blueprint_id": f"{slug}-{safe_ref}-recheck-v2",
                        "activity_type": "remediation",
                        "minutes": 20,
                    }
                )
            extension_mappings.append(
                {
                    "caps_ref": ref,
                    "topic": context["topic"],
                    "lesson_variant": "exam_style",
                    "activity_type": "challenge",
                    "assessment_blueprint_id": f"{slug}-{safe_ref}-mastery-check-v2",
                    "minutes": 25,
                }
            )

        return {
            "schema_version": "1.0",
            "generated_at": _now_utc(),
            "scope": scope_id,
            "grade": first["grade"],
            "subject": first["subject"],
            "weekly_template": weekly_template,
            "topic_sequence": topic_sequence,
            "remediation_mappings": remediation_mappings,
            "extension_mappings": extension_mappings,
            "pacing_guidance": {
                "lesson_block_minutes": 25,
                "practice_block_minutes": 15,
                "review_day": "Fri",
                "notes": (
                    "Alternate lesson and practice days. Use recheck blueprints after practice "
                    "when misconception tags were missed."
                ),
            },
        }

    def _weekly_template(
        self,
        scope_id: str,
        slug: str,
        caps_refs: list[str],
        contexts: dict[str, dict[str, Any]],
    ) -> list[dict[str, Any]]:
        days = ("Mon", "Tue", "Wed", "Thu", "Fri")
        activities = ("lesson", "practice", "lesson", "practice", "review")
        template: list[dict[str, Any]] = []
        for index, day in enumerate(days):
            ref = caps_refs[index % len(caps_refs)]
            context = contexts[ref]
            safe_ref = ref.replace(".", "-")
            activity = activities[index]
            if activity == "review":
                blueprint_id = f"{slug}-{safe_ref}-recheck-v2"
            else:
                blueprint_id = f"{slug}-{safe_ref}-short-practice-v2"
            template.append(
                {
                    "day": day,
                    "caps_ref": ref,
                    "topic": context["topic"],
                    "activity_type": activity,
                    "lesson_variant": _cycle(LESSON_VARIANTS, index),
                    "assessment_blueprint_id": blueprint_id,
                    "minutes": 40 if activity == "lesson" else 25,
                    "teacher_cue": _teacher_cue(activity, context["topic"]),
                }
            )
        return template


def _cycle(values: tuple[str, ...], index: int) -> str:
    return values[index % len(values)]


def _teacher_cue(activity: str, topic: str) -> str:
    if activity == "lesson":
        return f"Teach {topic} using the worked examples, then set the short practice blueprint."
    if activity == "practice":
        return f"Run the short practice quiz for {topic} and note missed misconception tags."
    return f"Use the recheck blueprint for {topic} and assign step-by-step remediation where needed."
