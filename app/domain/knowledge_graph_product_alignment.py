"""Pure product-alignment helpers for KG-6.

KG-6 consumes the approved KG-5 graph-grounded lesson/assessment generation
pack and produces non-authoritative preview artifacts for tutor alignment,
study-plan sequencing, gamification signals, and parent/guardian summaries.
It has no database dependency, uses no live learner records, does not call an
LLM provider, and does not make any learner-facing behaviour authoritative.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

KG6_GRAPH_ID = "KG-6-TUTOR-STUDY-PLAN-GAMIFICATION-PARENT-ALIGNMENT-GRADE-4-MATHEMATICS"
KG6_GRAPH_VERSION = "kg6-product-alignment-v1"
DEFAULT_GENERATION_PACK = Path("data/knowledge_graph/grounded_generation/grade4_mathematics_graph_grounded_generation_pack.json")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_id(prefix: str, key: str) -> str:
    return f"{prefix}_{sha256_text(key)[:24]}"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _estimated_minutes(priority_bucket: str) -> int:
    return {"critical": 30, "high": 25, "medium": 20, "low": 15}.get(priority_bucket, 20)


def _points(priority_bucket: str) -> int:
    return {"critical": 30, "high": 25, "medium": 20, "low": 15}.get(priority_bucket, 20)


def _badge(priority_bucket: str, target_type: str) -> str:
    if priority_bucket in {"critical", "high"}:
        return "Gap Closer"
    if target_type == "assessment_statement":
        return "Evidence Builder"
    return "CAPS Explorer"


def build_product_alignment_pack(generation_pack_path: Path = DEFAULT_GENERATION_PACK) -> dict[str, Any]:
    generation_pack_path = Path(generation_pack_path)
    pack = _load_json(generation_pack_path)
    generation_hash = file_sha256(generation_pack_path)

    boundary = pack.get("boundary", {})
    if boundary.get("generation_preview_only") is not True:
        raise ValueError("KG-6 requires KG-5 preview-only generation evidence")
    if boundary.get("uses_live_learner_data") is not False:
        raise ValueError("KG-6 requires KG-5 evidence with no live learner data")

    lessons = pack.get("lesson_drafts", [])
    assessments = pack.get("assessment_drafts", [])
    if not isinstance(lessons, list) or not isinstance(assessments, list) or not lessons:
        raise ValueError("KG-6 requires KG-5 lesson and assessment drafts")

    assessment_by_lesson = {item["lesson_key"]: item for item in assessments}
    tutor_previews: list[dict[str, Any]] = []
    study_plan_items: list[dict[str, Any]] = []
    gamification_award_candidates: list[dict[str, Any]] = []
    product_alignment_edges: list[dict[str, Any]] = []
    learner_rollup: dict[str, dict[str, Any]] = {}

    for lesson in lessons:
        if lesson.get("no_live_learner_data") is not True or lesson.get("human_review_required") is not True:
            raise ValueError("KG-6 only accepts KG-5 no-live-data, review-gated lesson drafts")
        lesson_key = lesson["lesson_key"]
        learner_alias = lesson["learner_alias"]
        assessment = assessment_by_lesson.get(lesson_key)
        if assessment is None:
            raise ValueError(f"KG-5 lesson has no assessment draft: {lesson_key}")
        if assessment.get("no_live_learner_data") is not True or assessment.get("human_review_required") is not True:
            raise ValueError("KG-6 only accepts KG-5 no-live-data, review-gated assessment drafts")

        priority_bucket = lesson.get("priority_bucket", "medium")
        tutor_key = f"tutor-preview:{lesson_key}"
        study_plan_key = f"study-plan-item:{lesson_key}"
        gamification_key = f"gamification-award:{assessment['assessment_key']}"
        source_ref = lesson_key
        source_hash = generation_hash

        tutor_previews.append({
            "tutor_preview_id": stable_id("kgtutor", tutor_key),
            "tutor_preview_key": tutor_key,
            "lesson_key": lesson_key,
            "assessment_key": assessment["assessment_key"],
            "learner_alias": learner_alias,
            "target_key": lesson["target_key"],
            "target_type": lesson["target_type"],
            "mode": "shadow_tutor_preview",
            "opening_prompt": f"Let us practise {lesson['title']} using the reviewed KG-5 lesson draft.",
            "scaffold_steps": [
                "Confirm what the learner already understands from the shadow gap summary.",
                "Use the reviewed lesson sections to model the idea without adding ungrounded content.",
                "Ask one reflection question and route the result back to human review before runtime use.",
            ],
            "expected_evidence_event_type": "kg6_shadow_tutor_alignment_check",
            "generation_pack_sha256": generation_hash,
            "source_ref": source_ref,
            "source_sha256": source_hash,
            "advisory_only": True,
            "shadow_mode": True,
            "preview_only": True,
            "no_live_learner_data": True,
            "human_review_required": True,
            "review_status": "approved_for_shadow_evidence",
            "version": KG6_GRAPH_VERSION,
        })

        study_plan_items.append({
            "study_plan_item_id": stable_id("kgstudy", study_plan_key),
            "study_plan_item_key": study_plan_key,
            "lesson_key": lesson_key,
            "learner_alias": learner_alias,
            "target_key": lesson["target_key"],
            "priority_bucket": priority_bucket,
            "priority_score": lesson.get("priority_score", 0),
            "pacing_window": lesson.get("metadata", {}).get("pacing_window", "shadow-review-window"),
            "estimated_minutes": _estimated_minutes(priority_bucket),
            "sequence_rule": "order by priority score, prerequisite context, and CAPS pacing window after educator review",
            "generation_pack_sha256": generation_hash,
            "source_ref": source_ref,
            "source_sha256": source_hash,
            "advisory_only": True,
            "shadow_mode": True,
            "preview_only": True,
            "no_live_learner_data": True,
            "human_review_required": True,
            "review_status": "approved_for_shadow_evidence",
            "version": KG6_GRAPH_VERSION,
        })

        gamification_award_candidates.append({
            "award_candidate_id": stable_id("kgaward", gamification_key),
            "award_candidate_key": gamification_key,
            "assessment_key": assessment["assessment_key"],
            "lesson_key": lesson_key,
            "learner_alias": learner_alias,
            "badge_candidate": _badge(priority_bucket, lesson["target_type"]),
            "points_preview": _points(priority_bucket),
            "award_rule": "candidate only; award cannot be issued until human-reviewed learner-facing authority is separately approved",
            "generation_pack_sha256": generation_hash,
            "source_ref": assessment["assessment_key"],
            "source_sha256": source_hash,
            "advisory_only": True,
            "shadow_mode": True,
            "preview_only": True,
            "no_live_learner_data": True,
            "human_review_required": True,
            "review_status": "approved_for_shadow_evidence",
            "version": KG6_GRAPH_VERSION,
        })

        product_alignment_edges.extend([
            {
                "edge_id": stable_id("kgproductedge", f"{lesson_key}->tutor"),
                "source_key": lesson_key,
                "target_key": tutor_key,
                "edge_type": "aligns_lesson_to_tutor_preview",
                "source_ref": source_ref,
                "source_sha256": source_hash,
                "advisory_only": True,
                "shadow_mode": True,
                "preview_only": True,
                "no_live_learner_data": True,
                "version": KG6_GRAPH_VERSION,
            },
            {
                "edge_id": stable_id("kgproductedge", f"{lesson_key}->study"),
                "source_key": lesson_key,
                "target_key": study_plan_key,
                "edge_type": "aligns_lesson_to_study_plan_item",
                "source_ref": source_ref,
                "source_sha256": source_hash,
                "advisory_only": True,
                "shadow_mode": True,
                "preview_only": True,
                "no_live_learner_data": True,
                "version": KG6_GRAPH_VERSION,
            },
            {
                "edge_id": stable_id("kgproductedge", f"{assessment['assessment_key']}->award"),
                "source_key": assessment["assessment_key"],
                "target_key": gamification_key,
                "edge_type": "aligns_assessment_to_gamification_candidate",
                "source_ref": assessment["assessment_key"],
                "source_sha256": source_hash,
                "advisory_only": True,
                "shadow_mode": True,
                "preview_only": True,
                "no_live_learner_data": True,
                "version": KG6_GRAPH_VERSION,
            },
        ])

        rollup = learner_rollup.setdefault(learner_alias, {
            "learner_alias": learner_alias,
            "lesson_count": 0,
            "assessment_count": 0,
            "study_plan_item_count": 0,
            "badge_candidate_count": 0,
            "priority_buckets": {},
            "no_live_learner_data": True,
            "synthetic": True,
        })
        rollup["lesson_count"] += 1
        rollup["assessment_count"] += 1
        rollup["study_plan_item_count"] += 1
        rollup["badge_candidate_count"] += 1
        rollup["priority_buckets"][priority_bucket] = rollup["priority_buckets"].get(priority_bucket, 0) + 1

    parent_alignment_summaries: list[dict[str, Any]] = []
    for learner_alias, rollup in sorted(learner_rollup.items()):
        key = f"parent-summary:{learner_alias}"
        parent_alignment_summaries.append({
            "parent_summary_id": stable_id("kgparent", key),
            "parent_summary_key": key,
            "learner_alias": learner_alias,
            "summary_scope": "synthetic shadow alignment summary only",
            "summary_text": "Guardian-facing summary preview: show study focus areas, reviewed lesson count, and badge candidates without exposing learner PII.",
            "lesson_count": rollup["lesson_count"],
            "assessment_count": rollup["assessment_count"],
            "study_plan_item_count": rollup["study_plan_item_count"],
            "badge_candidate_count": rollup["badge_candidate_count"],
            "priority_buckets": rollup["priority_buckets"],
            "generation_pack_sha256": generation_hash,
            "source_ref": learner_alias,
            "source_sha256": generation_hash,
            "advisory_only": True,
            "shadow_mode": True,
            "preview_only": True,
            "no_live_learner_data": True,
            "no_guardian_pii": True,
            "human_review_required": True,
            "review_status": "approved_for_shadow_evidence",
            "version": KG6_GRAPH_VERSION,
        })

    counts = {
        "tutor_previews": len(tutor_previews),
        "study_plan_items": len(study_plan_items),
        "gamification_award_candidates": len(gamification_award_candidates),
        "parent_alignment_summaries": len(parent_alignment_summaries),
        "product_alignment_edges": len(product_alignment_edges),
        "synthetic_learners": len(parent_alignment_summaries),
    }
    return {
        "graph_id": KG6_GRAPH_ID,
        "graph_version": KG6_GRAPH_VERSION,
        "status": "product_alignment_pack_generated",
        "scope": {
            "grade": 4,
            "subject": "mathematics",
            "curriculum": "CAPS",
            "mode": "shadow_product_alignment_preview",
            "data_classification": "synthetic_non_identifying",
        },
        "source": {
            "generation_pack_path": str(generation_pack_path),
            "generation_pack_sha256": generation_hash,
            "source_ref": pack.get("graph_id"),
        },
        "boundary": {
            "advisory_only": True,
            "shadow_mode": True,
            "preview_only": True,
            "uses_live_learner_data": False,
            "uses_guardian_pii": False,
            "tutor_runtime_authority_authorised": False,
            "study_plan_runtime_authority_authorised": False,
            "gamification_runtime_authority_authorised": False,
            "parent_portal_runtime_authority_authorised": False,
        },
        "review": {
            "educator_review_required_before_learner_facing_use": True,
            "product_review_required_before_runtime_use": True,
            "privacy_review_required_before_parent_surface_use": True,
            "review_scope": "synthetic shadow product alignment only",
        },
        "counts": counts,
        "tutor_previews": tutor_previews,
        "study_plan_items": study_plan_items,
        "gamification_award_candidates": gamification_award_candidates,
        "parent_alignment_summaries": parent_alignment_summaries,
        "product_alignment_edges": product_alignment_edges,
    }


def validate_product_alignment_pack(pack: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    tutor = pack.get("tutor_previews", [])
    study = pack.get("study_plan_items", [])
    awards = pack.get("gamification_award_candidates", [])
    parents = pack.get("parent_alignment_summaries", [])
    edges = pack.get("product_alignment_edges", [])

    lesson_keys = {item.get("lesson_key") for item in tutor}
    study_lesson_keys = {item.get("lesson_key") for item in study}
    award_assessment_keys = {item.get("assessment_key") for item in awards}
    edge_sources = {edge.get("source_key") for edge in edges}
    edge_targets = {edge.get("target_key") for edge in edges}
    tutor_keys = [item.get("tutor_preview_key") for item in tutor]
    study_keys = [item.get("study_plan_item_key") for item in study]
    award_keys = [item.get("award_candidate_key") for item in awards]
    parent_keys = [item.get("parent_summary_key") for item in parents]

    def all_true(items: list[dict[str, Any]], key: str) -> bool:
        return bool(items) and all(item.get(key) is True for item in items)

    all_tutor_source_grounded = all(item.get("source_ref") and item.get("source_sha256") for item in tutor)
    all_study_source_grounded = all(item.get("source_ref") and item.get("source_sha256") for item in study)
    all_awards_source_grounded = all(item.get("source_ref") and item.get("source_sha256") for item in awards)
    all_parent_source_grounded = all(item.get("source_ref") and item.get("source_sha256") for item in parents)
    all_edges_source_grounded = all(edge.get("source_ref") and edge.get("source_sha256") for edge in edges)

    duplicate_tutor_keys_found_false = len(tutor_keys) == len(set(tutor_keys))
    duplicate_study_plan_keys_found_false = len(study_keys) == len(set(study_keys))
    duplicate_award_keys_found_false = len(award_keys) == len(set(award_keys))
    duplicate_parent_summary_keys_found_false = len(parent_keys) == len(set(parent_keys))
    expected_targets = set(tutor_keys) | set(study_keys) | set(award_keys)
    orphan_product_edges_found_false = expected_targets.issubset(edge_targets) and lesson_keys.issubset(edge_sources) and award_assessment_keys.issubset(edge_sources)

    all_tutor_previews_reference_lessons = bool(tutor) and all(item.get("lesson_key") for item in tutor)
    all_study_plan_items_reference_lessons = bool(study) and lesson_keys == study_lesson_keys
    all_gamification_candidates_reference_assessments = bool(awards) and all(item.get("assessment_key") for item in awards)
    all_parent_summaries_synthetic_only = all(item.get("learner_alias", "").startswith("kg3-synthetic-") and item.get("no_guardian_pii") is True for item in parents)
    no_live_learner_aliases = all(item.get("learner_alias", "").startswith("kg3-synthetic-") for item in tutor + study + awards + parents)

    checks = {
        "all_tutor_previews_reference_lessons": all_tutor_previews_reference_lessons,
        "all_tutor_previews_source_grounded": all_tutor_source_grounded,
        "all_study_plan_items_reference_lessons": all_study_plan_items_reference_lessons,
        "all_study_plan_items_source_grounded": all_study_source_grounded,
        "all_gamification_candidates_reference_assessments": all_gamification_candidates_reference_assessments,
        "all_gamification_candidates_source_grounded": all_awards_source_grounded,
        "all_parent_summaries_synthetic_only": all_parent_summaries_synthetic_only,
        "all_parent_summaries_source_grounded": all_parent_source_grounded,
        "all_product_edges_source_grounded": all_edges_source_grounded,
        "all_product_items_review_required": all_true(tutor, "human_review_required") and all_true(study, "human_review_required") and all_true(awards, "human_review_required") and all_true(parents, "human_review_required"),
        "all_product_items_advisory_only": all_true(tutor, "advisory_only") and all_true(study, "advisory_only") and all_true(awards, "advisory_only") and all_true(parents, "advisory_only"),
        "no_live_learner_aliases": no_live_learner_aliases,
        "duplicate_tutor_preview_keys_found_false": duplicate_tutor_keys_found_false,
        "duplicate_study_plan_item_keys_found_false": duplicate_study_plan_keys_found_false,
        "duplicate_award_candidate_keys_found_false": duplicate_award_keys_found_false,
        "duplicate_parent_summary_keys_found_false": duplicate_parent_summary_keys_found_false,
        "orphan_product_edges_found_false": orphan_product_edges_found_false,
        "counts": pack.get("counts", {}),
    }
    for name, ok in checks.items():
        if name != "counts" and ok is not True:
            errors.append(f"validation failed: {name}")
    return {"valid": not errors, "errors": errors, **checks}
