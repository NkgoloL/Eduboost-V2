"""Assessment blueprint generator aligned with scope item banks and lessons."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.services.content_generation.generated_lesson_contract import LESSON_VARIANTS


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _slug(scope_id: str) -> str:
    return scope_id.replace("_", "-")


def _safe_ref(caps_ref: str) -> str:
    return caps_ref.replace(".", "-")


class ScopeBlueprintGenerator:
    """Build scope assessment blueprints with difficulty mix aligned to item bands."""

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
        blueprints: list[dict[str, Any]] = [
            self._baseline_blueprint(
                scope_id=scope_id,
                slug=slug,
                refs=caps_refs,
                subject=first["subject"],
                grade=first["grade"],
            )
        ]
        for ref_index, ref in enumerate(caps_refs):
            context = contexts[ref]
            safe = _safe_ref(ref)
            misconception_tags = context.get("common_misconceptions") or ["needs_step_by_step_support"]
            blueprints.extend(
                [
                    self._topic_diagnostic(
                        slug=slug,
                        safe_ref=safe,
                        ref=ref,
                        context=context,
                        misconception_tags=misconception_tags,
                        source_hash=source_context_hashes.get(ref),
                    ),
                    self._short_practice(
                        slug=slug,
                        safe_ref=safe,
                        ref=ref,
                        context=context,
                        lesson_variant=LESSON_VARIANTS[ref_index % len(LESSON_VARIANTS)],
                    ),
                    self._mastery_check(
                        slug=slug,
                        safe_ref=safe,
                        ref=ref,
                        context=context,
                    ),
                ]
            )
        return {
            "schema_version": "1.0",
            "generated_at": _now_utc(),
            "scope": scope_id,
            "grade": first["grade"],
            "subject": first["subject"],
            "source_item_bank": "diagnostic_items",
            "item_difficulty_bands": list(("easy", "moderate", "on_level", "challenging")),
            "blueprints": blueprints,
        }

    def _baseline_blueprint(
        self,
        *,
        scope_id: str,
        slug: str,
        refs: list[str],
        subject: str,
        grade: int,
    ) -> dict[str, Any]:
        return {
            "blueprint_id": f"{slug}-baseline-diagnostic-v2",
            "type": "baseline_diagnostic",
            "title": f"Grade {grade} {subject} Baseline Diagnostic",
            "description": (
                f"Samples approved items across all {len(refs)} CAPS topics in {scope_id} "
                "to establish a starting mastery profile."
            ),
            "selection_rules": {
                "caps_refs": refs,
                "item_count": min(24, len(refs) * 2),
                "review_status": "approved",
                "difficulty_mix": {"easy": 6, "moderate": 6, "on_level": 6, "challenging": 6},
                "require_unique_stems": True,
                "max_items_per_caps_ref": 2,
            },
            "review_status": "approved",
        }

    def _topic_diagnostic(
        self,
        *,
        slug: str,
        safe_ref: str,
        ref: str,
        context: dict[str, Any],
        misconception_tags: list[str],
        source_hash: str | None,
    ) -> dict[str, Any]:
        topic = context["topic"]
        return {
            "blueprint_id": f"{slug}-{safe_ref}-topic-diagnostic-v2",
            "type": "topic_diagnostic",
            "title": f"{topic} Topic Diagnostic",
            "description": f"Diagnostic covering CAPS {ref} with balanced difficulty and misconception coverage.",
            "selection_rules": {
                "caps_refs": [ref],
                "item_count": 12,
                "review_status": "approved",
                "difficulty_mix": {"easy": 3, "moderate": 3, "on_level": 3, "challenging": 3},
                "misconception_tags": misconception_tags,
                "require_unique_stems": True,
                "source_context_hash": source_hash,
            },
            "linked_lesson_variant": "standard",
            "review_status": "approved",
        }

    def _short_practice(
        self,
        *,
        slug: str,
        safe_ref: str,
        ref: str,
        context: dict[str, Any],
        lesson_variant: str,
    ) -> dict[str, Any]:
        topic = context["topic"]
        return {
            "blueprint_id": f"{slug}-{safe_ref}-short-practice-v2",
            "type": "short_practice_quiz",
            "title": f"{topic} Short Practice",
            "description": f"Short practice quiz after the {lesson_variant.replace('_', ' ')} lesson variant.",
            "selection_rules": {
                "caps_refs": [ref],
                "item_count": 8,
                "review_status": "approved",
                "difficulty_mix": {"easy": 2, "moderate": 2, "on_level": 2, "challenging": 2},
                "require_unique_stems": True,
            },
            "linked_lesson_variant": lesson_variant,
            "review_status": "approved",
        }

    def _recheck(
        self,
        *,
        slug: str,
        safe_ref: str,
        ref: str,
        context: dict[str, Any],
        misconception_tags: list[str],
    ) -> dict[str, Any]:
        topic = context["topic"]
        return {
            "blueprint_id": f"{slug}-{safe_ref}-recheck-v2",
            "type": "recheck_assessment",
            "title": f"{topic} Recheck",
            "description": "Targets previously missed misconceptions with on-level and challenging items.",
            "selection_rules": {
                "caps_refs": [ref],
                "item_count": 8,
                "review_status": "approved",
                "difficulty_mix": {"moderate": 2, "on_level": 3, "challenging": 3},
                "prefer_previously_missed_misconception_tags": True,
                "misconception_tags": misconception_tags,
                "require_unique_stems": True,
            },
            "linked_lesson_variant": "step_by_step",
            "review_status": "approved",
        }

    def _mastery_check(
        self,
        *,
        slug: str,
        safe_ref: str,
        ref: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        topic = context["topic"]
        return {
            "blueprint_id": f"{slug}-{safe_ref}-mastery-check-v2",
            "type": "mastery_check",
            "title": f"{topic} Mastery Check",
            "description": "End-of-topic check emphasising on-level and challenging application items.",
            "selection_rules": {
                "caps_refs": [ref],
                "item_count": 6,
                "review_status": "approved",
                "difficulty_mix": {"on_level": 3, "challenging": 3},
                "require_unique_stems": True,
            },
            "linked_lesson_variant": "exam_style",
            "review_status": "approved",
        }
