"""Pure graph-grounded lesson and assessment generation helpers for KG-5.

KG-5 consumes the approved KG-4 advisory gap/intervention plan and produces a
source-grounded, non-authoritative lesson-and-assessment preview pack. It has no
database dependency, does not call an LLM provider, does not use live learner
records, and does not make learner-facing content authoritative. Runtime KG
authority, persistence, database migrations, public beta, deployment, and
learner-facing model changes remain out of scope.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

KG5_GRAPH_ID = "KG-5-GRAPH-GROUNDED-LESSON-ASSESSMENT-GENERATION-GRADE-4-MATHEMATICS"
KG5_GRAPH_VERSION = "kg5-graph-grounded-generation-v1"
DEFAULT_GAP_PLAN = Path("data/knowledge_graph/gap_engine/grade4_mathematics_gap_intervention_plan.json")
DEFAULT_TARGET_GRAPH = Path("data/knowledge_graph/target_graph/grade4_mathematics_target_graph.json")


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


def _target_lookup(target_graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    targets = target_graph.get("target_states", [])
    if not isinstance(targets, list):
        raise ValueError("target_graph.target_states must be a list")
    return {target["target_key"]: target for target in targets}


def _gap_lookup(gap_plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    gaps = gap_plan.get("gap_items", [])
    if not isinstance(gaps, list):
        raise ValueError("gap_plan.gap_items must be a list")
    return {gap["gap_key"]: gap for gap in gaps}


def _lesson_strategy(intervention_type: str) -> str:
    if intervention_type == "reteach_with_guided_practice":
        return "Reteach concept, model worked example, then guided practice with immediate feedback."
    if intervention_type == "prerequisite_review_and_mini_lesson":
        return "Review prerequisite idea, connect it to the CAPS target, then practise two scaffolded examples."
    if intervention_type == "targeted_practice_with_feedback":
        return "Give focused practice on the target with misconception checks and corrective feedback."
    return "Use a short confidence check followed by spaced practice and reflection."


def _assessment_stem(label: str, target_type: str) -> str:
    if target_type == "assessment_statement":
        return f"Show your working for a Grade 4 Mathematics task about: {label}."
    if target_type == "subtopic":
        return f"Complete a short practice problem that checks understanding of: {label}."
    return f"Explain the key idea for: {label}."


@dataclass(frozen=True)
class LessonDraft:
    lesson_id: str
    lesson_key: str
    intervention_key: str
    gap_key: str
    learner_alias: str
    target_key: str
    target_id: str
    target_type: str
    title: str
    priority_bucket: str
    priority_score: float
    learning_objective: str
    instructional_strategy: str
    grounded_generation_prompt: str
    lesson_sections: list[dict[str, str]]
    expected_evidence_event_type: str
    source_ref: str
    source_sha256: str
    gap_plan_sha256: str
    target_graph_sha256: str
    advisory_only: bool = True
    generation_preview_only: bool = True
    shadow_mode: bool = True
    no_live_learner_data: bool = True
    human_review_required: bool = True
    review_status: str = "approved_for_shadow_evidence"
    version: str = KG5_GRAPH_VERSION
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "lesson_id": self.lesson_id,
            "lesson_key": self.lesson_key,
            "intervention_key": self.intervention_key,
            "gap_key": self.gap_key,
            "learner_alias": self.learner_alias,
            "target_key": self.target_key,
            "target_id": self.target_id,
            "target_type": self.target_type,
            "title": self.title,
            "priority_bucket": self.priority_bucket,
            "priority_score": self.priority_score,
            "learning_objective": self.learning_objective,
            "instructional_strategy": self.instructional_strategy,
            "grounded_generation_prompt": self.grounded_generation_prompt,
            "lesson_sections": self.lesson_sections,
            "expected_evidence_event_type": self.expected_evidence_event_type,
            "source_ref": self.source_ref,
            "source_sha256": self.source_sha256,
            "gap_plan_sha256": self.gap_plan_sha256,
            "target_graph_sha256": self.target_graph_sha256,
            "advisory_only": self.advisory_only,
            "generation_preview_only": self.generation_preview_only,
            "shadow_mode": self.shadow_mode,
            "no_live_learner_data": self.no_live_learner_data,
            "human_review_required": self.human_review_required,
            "review_status": self.review_status,
            "version": self.version,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class AssessmentDraft:
    assessment_id: str
    assessment_key: str
    lesson_key: str
    gap_key: str
    learner_alias: str
    target_key: str
    target_type: str
    item_type: str
    prompt: str
    expected_answer_contract: str
    rubric: list[str]
    source_ref: str
    source_sha256: str
    gap_plan_sha256: str
    target_graph_sha256: str
    advisory_only: bool = True
    generation_preview_only: bool = True
    shadow_mode: bool = True
    no_live_learner_data: bool = True
    human_review_required: bool = True
    review_status: str = "approved_for_shadow_evidence"
    version: str = KG5_GRAPH_VERSION

    def as_dict(self) -> dict[str, Any]:
        return {
            "assessment_id": self.assessment_id,
            "assessment_key": self.assessment_key,
            "lesson_key": self.lesson_key,
            "gap_key": self.gap_key,
            "learner_alias": self.learner_alias,
            "target_key": self.target_key,
            "target_type": self.target_type,
            "item_type": self.item_type,
            "prompt": self.prompt,
            "expected_answer_contract": self.expected_answer_contract,
            "rubric": self.rubric,
            "source_ref": self.source_ref,
            "source_sha256": self.source_sha256,
            "gap_plan_sha256": self.gap_plan_sha256,
            "target_graph_sha256": self.target_graph_sha256,
            "advisory_only": self.advisory_only,
            "generation_preview_only": self.generation_preview_only,
            "shadow_mode": self.shadow_mode,
            "no_live_learner_data": self.no_live_learner_data,
            "human_review_required": self.human_review_required,
            "review_status": self.review_status,
            "version": self.version,
        }


@dataclass(frozen=True)
class GenerationEdge:
    edge_id: str
    source_key: str
    target_key: str
    edge_type: str
    label: str
    source_ref: str
    source_sha256: str
    advisory_only: bool = True
    generation_preview_only: bool = True
    shadow_mode: bool = True
    no_live_learner_data: bool = True
    review_status: str = "approved_for_shadow_evidence"
    version: str = KG5_GRAPH_VERSION

    def as_dict(self) -> dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "source_key": self.source_key,
            "target_key": self.target_key,
            "edge_type": self.edge_type,
            "label": self.label,
            "source_ref": self.source_ref,
            "source_sha256": self.source_sha256,
            "advisory_only": self.advisory_only,
            "generation_preview_only": self.generation_preview_only,
            "shadow_mode": self.shadow_mode,
            "no_live_learner_data": self.no_live_learner_data,
            "review_status": self.review_status,
            "version": self.version,
        }


def build_graph_grounded_generation_pack(
    gap_plan_path: Path = DEFAULT_GAP_PLAN,
    target_graph_path: Path = DEFAULT_TARGET_GRAPH,
) -> dict[str, Any]:
    gap_plan_path = Path(gap_plan_path)
    target_graph_path = Path(target_graph_path)
    gap_plan = _load_json(gap_plan_path)
    target_graph = _load_json(target_graph_path)
    gap_hash = file_sha256(gap_plan_path)
    target_hash = file_sha256(target_graph_path)

    if gap_plan.get("boundary", {}).get("advisory_only") is not True:
        raise ValueError("KG-5 requires a KG-4 advisory gap plan")
    if gap_plan.get("boundary", {}).get("uses_live_learner_data") is not False:
        raise ValueError("KG-5 requires KG-4 evidence with no live learner data")

    gaps = _gap_lookup(gap_plan)
    targets = _target_lookup(target_graph)
    interventions = gap_plan.get("intervention_recommendations", [])
    if not isinstance(interventions, list) or not interventions:
        raise ValueError("KG-5 requires KG-4 intervention recommendations")

    lesson_drafts: list[dict[str, Any]] = []
    assessment_drafts: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    learner_summaries: dict[str, dict[str, Any]] = {}

    for intervention in interventions:
        if intervention.get("advisory_only") is not True or intervention.get("no_live_learner_data") is not True:
            raise ValueError("KG-5 only accepts advisory, no-live-data KG-4 interventions")
        gap_key = intervention["gap_key"]
        gap = gaps.get(gap_key)
        if gap is None:
            raise ValueError(f"intervention references missing gap: {gap_key}")
        target_key = intervention["target_key"]
        target = targets.get(target_key)
        if target is None:
            raise ValueError(f"intervention references missing target: {target_key}")
        learner_alias = intervention["learner_alias"]
        label = gap.get("label") or target.get("label") or target_key
        lesson_key = f"lesson:{intervention['intervention_key']}"
        assessment_key = f"assessment:{lesson_key}:exit-check"
        strategy = _lesson_strategy(intervention.get("intervention_type", ""))
        lesson = LessonDraft(
            lesson_id=stable_id("kglesson", lesson_key),
            lesson_key=lesson_key,
            intervention_key=intervention["intervention_key"],
            gap_key=gap_key,
            learner_alias=learner_alias,
            target_key=target_key,
            target_id=gap["target_id"],
            target_type=gap["target_type"],
            title=f"Graph-grounded mini lesson: {label}",
            priority_bucket=intervention["priority_bucket"],
            priority_score=float(intervention["priority_score"]),
            learning_objective=f"Improve mastery of {label} using CAPS-grounded practice for Grade 4 Mathematics.",
            instructional_strategy=strategy,
            grounded_generation_prompt=(
                "Use only the KG-2 target state, KG-3 shadow state summary, and KG-4 advisory gap rationale. "
                f"Target: {target_key}. Gap: {gap_key}. Intervention: {intervention['intervention_type']}."
            ),
            lesson_sections=[
                {"section": "diagnostic_context", "text": intervention["rationale"]},
                {"section": "teacher_model", "text": f"Model the idea: {label}. Keep examples Grade 4 appropriate and CAPS aligned."},
                {"section": "guided_practice", "text": "Provide two scaffolded practice turns with feedback before independent work."},
                {"section": "reflection", "text": "Ask the learner to explain the strategy they used and where they still need help."},
            ],
            expected_evidence_event_type="kg5_shadow_lesson_exit_check",
            source_ref=intervention["intervention_key"],
            source_sha256=intervention["source_sha256"],
            gap_plan_sha256=gap_hash,
            target_graph_sha256=target_hash,
            metadata={
                "caps_node_key": gap.get("metadata", {}).get("caps_node_key") or target.get("caps_node_key"),
                "caps_source_ref": gap.get("metadata", {}).get("caps_source_ref") or target.get("caps_source_ref"),
                "pacing_window": gap.get("pacing_window") or target.get("pacing_window"),
                "required_mastery": gap.get("required_mastery"),
                "observed_mastery": gap.get("observed_mastery"),
                "generation_policy": "kg5-graph-grounded-shadow-generation-policy",
            },
        ).as_dict()
        assessment = AssessmentDraft(
            assessment_id=stable_id("kgassess", assessment_key),
            assessment_key=assessment_key,
            lesson_key=lesson_key,
            gap_key=gap_key,
            learner_alias=learner_alias,
            target_key=target_key,
            target_type=gap["target_type"],
            item_type="shadow_exit_check",
            prompt=_assessment_stem(label, gap["target_type"]),
            expected_answer_contract="Learner response must show Grade 4-appropriate reasoning and be reviewed before learner-facing use.",
            rubric=[
                "Identifies the relevant mathematical idea.",
                "Shows a correct method or explanation.",
                "Uses feedback to correct or improve the answer.",
            ],
            source_ref=lesson_key,
            source_sha256=intervention["source_sha256"],
            gap_plan_sha256=gap_hash,
            target_graph_sha256=target_hash,
        ).as_dict()
        lesson_edge = GenerationEdge(
            edge_id=stable_id("kggenedge", f"{intervention['intervention_key']}|grounds_lesson|{lesson_key}"),
            source_key=intervention["intervention_key"],
            target_key=lesson_key,
            edge_type="grounds_lesson_draft",
            label="KG-4 advisory intervention grounds a KG-5 lesson draft",
            source_ref=intervention["intervention_key"],
            source_sha256=intervention["source_sha256"],
        ).as_dict()
        assessment_edge = GenerationEdge(
            edge_id=stable_id("kggenedge", f"{lesson_key}|checks|{assessment_key}"),
            source_key=lesson_key,
            target_key=assessment_key,
            edge_type="checks_lesson_outcome",
            label="KG-5 lesson draft has a KG-5 shadow assessment item",
            source_ref=lesson_key,
            source_sha256=intervention["source_sha256"],
        ).as_dict()
        lesson_drafts.append(lesson)
        assessment_drafts.append(assessment)
        edges.extend([lesson_edge, assessment_edge])
        summary = learner_summaries.setdefault(learner_alias, {
            "learner_alias": learner_alias,
            "synthetic": True,
            "no_live_learner_data": True,
            "lesson_drafts": 0,
            "assessment_drafts": 0,
            "highest_priority_score": 0.0,
        })
        summary["lesson_drafts"] += 1
        summary["assessment_drafts"] += 1
        summary["highest_priority_score"] = max(float(summary["highest_priority_score"]), float(intervention["priority_score"]))

    lesson_drafts.sort(key=lambda item: (item["learner_alias"], -item["priority_score"], item["target_key"]))
    assessment_drafts.sort(key=lambda item: (item["learner_alias"], item["target_key"]))
    learner_profiles = sorted(learner_summaries.values(), key=lambda item: item["learner_alias"])

    return {
        "graph_id": KG5_GRAPH_ID,
        "graph_version": KG5_GRAPH_VERSION,
        "status": "graph_grounded_lesson_assessment_pack_generated",
        "scope": {
            "curriculum": "CAPS",
            "grade": 4,
            "subject": "mathematics",
            "mode": "shadow_generation_preview",
            "data_classification": "synthetic_non_identifying",
        },
        "source": {
            "gap_plan_path": str(gap_plan_path),
            "gap_plan_sha256": gap_hash,
            "target_graph_path": str(target_graph_path),
            "target_graph_sha256": target_hash,
            "source_ref": "KG-5 graph-grounded generation over KG-4 advisory plan",
        },
        "counts": {
            "synthetic_learners": len(learner_profiles),
            "target_states_referenced": len({item["target_key"] for item in lesson_drafts}),
            "lesson_drafts": len(lesson_drafts),
            "assessment_drafts": len(assessment_drafts),
            "generation_edges": len(edges),
            "human_review_required_items": len(lesson_drafts) + len(assessment_drafts),
        },
        "learner_generation_profiles": learner_profiles,
        "lesson_drafts": lesson_drafts,
        "assessment_drafts": assessment_drafts,
        "generation_edges": edges,
        "review": {
            "review_status": "approved_for_shadow_evidence",
            "review_scope": "synthetic shadow lesson and assessment generation only",
            "educator_review_required_before_learner_facing_use": True,
            "content_safety_review_required_before_runtime_use": True,
        },
        "boundary": {
            "advisory_only": True,
            "generation_preview_only": True,
            "shadow_mode_only": True,
            "uses_live_learner_data": False,
            "no_live_learner_data_used": True,
            "runtime_authority": False,
            "generation_runtime_authority_authorised": False,
            "assessment_runtime_authority_authorised": False,
            "learner_facing_model_change_authorised": False,
            "database_schema_migration_authorised": False,
            "llm_provider_call_authorised": False,
        },
    }


def validate_graph_grounded_generation_pack(pack: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if pack.get("graph_id") != KG5_GRAPH_ID:
        errors.append("unexpected KG-5 generation pack graph_id")
    boundary = pack.get("boundary", {})
    if boundary.get("generation_preview_only") is not True:
        errors.append("KG-5 pack must be generation preview only")
    if boundary.get("uses_live_learner_data") is not False:
        errors.append("KG-5 pack must not use live learner data")
    if boundary.get("llm_provider_call_authorised") is not False:
        errors.append("KG-5 pack must not authorise LLM provider calls")

    lessons = pack.get("lesson_drafts", [])
    assessments = pack.get("assessment_drafts", [])
    edges = pack.get("generation_edges", [])
    lesson_keys = {item.get("lesson_key") for item in lessons}
    assessment_keys = {item.get("assessment_key") for item in assessments}
    intervention_keys = {item.get("intervention_key") for item in lessons}
    {item.get("gap_key") for item in lessons}

    if len(lesson_keys) != len(lessons):
        errors.append("duplicate lesson keys found")
    if len(assessment_keys) != len(assessments):
        errors.append("duplicate assessment keys found")

    all_lessons_reference_interventions = all(str(item.get("source_ref", "")).startswith("intervention:") for item in lessons)
    all_lessons_source_grounded = all(
        item.get("source_sha256") and item.get("gap_plan_sha256") and item.get("target_graph_sha256")
        for item in lessons
    )
    all_assessments_reference_lessons = all(item.get("source_ref") in lesson_keys and item.get("lesson_key") in lesson_keys for item in assessments)
    all_assessments_source_grounded = all(
        item.get("source_sha256") and item.get("gap_plan_sha256") and item.get("target_graph_sha256")
        for item in assessments
    )
    all_generation_items_review_required = all(
        item.get("human_review_required") is True and item.get("generation_preview_only") is True and item.get("no_live_learner_data") is True
        for item in lessons + assessments
    )
    all_lessons_advisory_only = all(item.get("advisory_only") is True and item.get("shadow_mode") is True for item in lessons)
    all_assessments_advisory_only = all(item.get("advisory_only") is True and item.get("shadow_mode") is True for item in assessments)
    no_live_learner_aliases = all(str(item.get("learner_alias", "")).startswith("kg3-synthetic-") for item in lessons + assessments)

    orphan_edges = []
    for edge in edges:
        if edge.get("edge_type") == "grounds_lesson_draft" and (edge.get("source_key") not in intervention_keys or edge.get("target_key") not in lesson_keys):
            orphan_edges.append(edge)
        if edge.get("edge_type") == "checks_lesson_outcome" and (edge.get("source_key") not in lesson_keys or edge.get("target_key") not in assessment_keys):
            orphan_edges.append(edge)

    if not all_lessons_reference_interventions:
        errors.append("not all lessons reference KG-4 interventions")
    if not all_lessons_source_grounded:
        errors.append("not all lessons are source grounded")
    if not all_assessments_reference_lessons:
        errors.append("not all assessments reference KG-5 lessons")
    if not all_assessments_source_grounded:
        errors.append("not all assessments are source grounded")
    if not all_generation_items_review_required:
        errors.append("not all generation items require human review and preview-only mode")
    if not all_lessons_advisory_only:
        errors.append("not all lessons are advisory shadow-mode drafts")
    if not all_assessments_advisory_only:
        errors.append("not all assessments are advisory shadow-mode drafts")
    if not no_live_learner_aliases:
        errors.append("generation pack contains non-synthetic learner aliases")
    if orphan_edges:
        errors.append("orphan generation edges found")

    counts = pack.get("counts", {})
    if int(counts.get("lesson_drafts") or 0) != len(lessons):
        errors.append("lesson draft count mismatch")
    if int(counts.get("assessment_drafts") or 0) != len(assessments):
        errors.append("assessment draft count mismatch")
    if int(counts.get("generation_edges") or 0) != len(edges):
        errors.append("generation edge count mismatch")

    return {
        "valid": not errors,
        "errors": errors,
        "counts": counts,
        "all_lessons_reference_interventions": all_lessons_reference_interventions,
        "all_lessons_source_grounded": all_lessons_source_grounded,
        "all_assessments_reference_lessons": all_assessments_reference_lessons,
        "all_assessments_source_grounded": all_assessments_source_grounded,
        "all_generation_items_review_required": all_generation_items_review_required,
        "all_lessons_advisory_only": all_lessons_advisory_only,
        "all_assessments_advisory_only": all_assessments_advisory_only,
        "no_live_learner_aliases": no_live_learner_aliases,
        "duplicate_lesson_keys_found_false": len(lesson_keys) == len(lessons),
        "duplicate_assessment_keys_found_false": len(assessment_keys) == len(assessments),
        "orphan_generation_edges_found_false": not orphan_edges,
    }
