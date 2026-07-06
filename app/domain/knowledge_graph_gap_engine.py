"""Pure gap-engine and intervention-planner helpers for KG-4.

KG-4 consumes the approved KG-3 learner shadow graph and produces an
explainable, non-authoritative gap profile plus advisory intervention plan. It
has no database dependency, does not mutate learner records, and does not make
learner-facing decisions authoritative. Runtime KG authority, persistence,
database migrations, and learner-facing model changes remain out of scope.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

KG4_GRAPH_ID = "KG-4-GAP-ENGINE-INTERVENTION-PLAN-GRADE-4-MATHEMATICS"
KG4_GRAPH_VERSION = "kg4-gap-engine-intervention-planner-v1"
DEFAULT_SHADOW_GRAPH = Path("data/knowledge_graph/learner_shadow_mode/grade4_mathematics_learner_shadow_graph.json")
DEFAULT_TARGET_GRAPH = Path("data/knowledge_graph/target_graph/grade4_mathematics_target_graph.json")
NON_MASTERED_STATUSES = {"shadow_gap", "shadow_developing"}


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


def _priority_bucket(score: float) -> str:
    if score >= 0.75:
        return "urgent"
    if score >= 0.55:
        return "high"
    if score >= 0.35:
        return "medium"
    return "watch"


def _intervention_type(state: dict[str, Any], priority_score: float) -> str:
    if state.get("shadow_status") == "shadow_gap" and state.get("target_type") == "assessment_statement":
        return "reteach_with_guided_practice"
    if state.get("shadow_status") == "shadow_gap":
        return "prerequisite_review_and_mini_lesson"
    if priority_score >= 0.55:
        return "targeted_practice_with_feedback"
    return "confidence_check_and_spaced_practice"


def _intervention_rationale(state: dict[str, Any], priority_score: float) -> str:
    return (
        f"Observed mastery {state['observed_mastery']:.2f} and confidence "
        f"{state['observed_confidence']:.2f} are below required mastery "
        f"{state['required_mastery']:.2f} / confidence {state['required_confidence']:.2f}; "
        f"planner priority score {priority_score:.3f}."
    )


@dataclass(frozen=True)
class GapItem:
    gap_id: str
    gap_key: str
    learner_alias: str
    target_key: str
    target_id: str
    target_type: str
    label: str
    term: int
    shadow_status: str
    required_mastery: float
    required_confidence: float
    observed_mastery: float
    observed_confidence: float
    mastery_gap: float
    confidence_gap: float
    target_priority: float
    priority_score: float
    priority_bucket: str
    pacing_window: str | None
    source_ref: str
    source_sha256: str
    shadow_graph_sha256: str
    target_graph_sha256: str
    advisory_only: bool = True
    shadow_mode: bool = True
    no_live_learner_data: bool = True
    review_status: str = "approved"
    version: str = KG4_GRAPH_VERSION
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "gap_id": self.gap_id,
            "gap_key": self.gap_key,
            "learner_alias": self.learner_alias,
            "target_key": self.target_key,
            "target_id": self.target_id,
            "target_type": self.target_type,
            "label": self.label,
            "term": self.term,
            "shadow_status": self.shadow_status,
            "required_mastery": self.required_mastery,
            "required_confidence": self.required_confidence,
            "observed_mastery": self.observed_mastery,
            "observed_confidence": self.observed_confidence,
            "mastery_gap": self.mastery_gap,
            "confidence_gap": self.confidence_gap,
            "target_priority": self.target_priority,
            "priority_score": self.priority_score,
            "priority_bucket": self.priority_bucket,
            "pacing_window": self.pacing_window,
            "source_ref": self.source_ref,
            "source_sha256": self.source_sha256,
            "shadow_graph_sha256": self.shadow_graph_sha256,
            "target_graph_sha256": self.target_graph_sha256,
            "advisory_only": self.advisory_only,
            "shadow_mode": self.shadow_mode,
            "no_live_learner_data": self.no_live_learner_data,
            "review_status": self.review_status,
            "version": self.version,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class InterventionRecommendation:
    intervention_id: str
    intervention_key: str
    gap_key: str
    learner_alias: str
    target_key: str
    intervention_type: str
    recommendation_rank: int
    priority_bucket: str
    priority_score: float
    rationale: str
    expected_evidence_event_type: str
    source_ref: str
    source_sha256: str
    shadow_graph_sha256: str
    target_graph_sha256: str
    advisory_only: bool = True
    shadow_mode: bool = True
    no_live_learner_data: bool = True
    review_status: str = "approved"
    version: str = KG4_GRAPH_VERSION

    def as_dict(self) -> dict[str, Any]:
        return {
            "intervention_id": self.intervention_id,
            "intervention_key": self.intervention_key,
            "gap_key": self.gap_key,
            "learner_alias": self.learner_alias,
            "target_key": self.target_key,
            "intervention_type": self.intervention_type,
            "recommendation_rank": self.recommendation_rank,
            "priority_bucket": self.priority_bucket,
            "priority_score": self.priority_score,
            "rationale": self.rationale,
            "expected_evidence_event_type": self.expected_evidence_event_type,
            "source_ref": self.source_ref,
            "source_sha256": self.source_sha256,
            "shadow_graph_sha256": self.shadow_graph_sha256,
            "target_graph_sha256": self.target_graph_sha256,
            "advisory_only": self.advisory_only,
            "shadow_mode": self.shadow_mode,
            "no_live_learner_data": self.no_live_learner_data,
            "review_status": self.review_status,
            "version": self.version,
        }


@dataclass(frozen=True)
class PlannerEdge:
    edge_id: str
    source_key: str
    target_key: str
    edge_type: str
    label: str
    source_ref: str
    source_sha256: str
    advisory_only: bool = True
    shadow_mode: bool = True
    no_live_learner_data: bool = True
    review_status: str = "approved"
    version: str = KG4_GRAPH_VERSION

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
            "shadow_mode": self.shadow_mode,
            "no_live_learner_data": self.no_live_learner_data,
            "review_status": self.review_status,
            "version": self.version,
        }


def _target_lookup(target_graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    targets = target_graph.get("target_states", [])
    if not isinstance(targets, list):
        raise ValueError("target_graph.target_states must be a list")
    return {target["target_key"]: target for target in targets}


def build_gap_intervention_plan(
    shadow_graph_path: Path = DEFAULT_SHADOW_GRAPH,
    target_graph_path: Path = DEFAULT_TARGET_GRAPH,
) -> dict[str, Any]:
    shadow_graph_path = Path(shadow_graph_path)
    target_graph_path = Path(target_graph_path)
    shadow_graph = _load_json(shadow_graph_path)
    target_graph = _load_json(target_graph_path)
    shadow_hash = file_sha256(shadow_graph_path)
    target_hash = file_sha256(target_graph_path)
    targets = _target_lookup(target_graph)

    if shadow_graph.get("boundary", {}).get("no_live_learner_data") is not True:
        raise ValueError("KG-4 requires a KG-3 shadow graph with no live learner data")

    shadow_states = shadow_graph.get("learner_shadow_states", [])
    if not isinstance(shadow_states, list) or not shadow_states:
        raise ValueError("KG-4 requires KG-3 learner_shadow_states")

    gap_items: list[dict[str, Any]] = []
    interventions: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    learner_summaries: dict[str, dict[str, Any]] = {}
    status_counts = {"shadow_gap": 0, "shadow_developing": 0}
    bucket_counts = {"urgent": 0, "high": 0, "medium": 0, "watch": 0}

    for state in shadow_states:
        if state.get("shadow_mode") is not True or state.get("no_live_learner_data") is not True:
            raise ValueError("KG-4 only accepts KG-3 shadow states with no live learner data")
        if state.get("shadow_status") not in NON_MASTERED_STATUSES:
            continue
        target_key = state["target_key"]
        target = targets.get(target_key)
        if target is None:
            raise ValueError(f"shadow state references missing target: {target_key}")

        mastery_gap = max(0.0, round(float(state["required_mastery"]) - float(state["observed_mastery"]), 3))
        confidence_gap = max(0.0, round(float(state["required_confidence"]) - float(state["observed_confidence"]), 3))
        target_priority = float(target.get("priority") or state.get("metadata", {}).get("priority") or 0.5)
        status_weight = 0.25 if state["shadow_status"] == "shadow_gap" else 0.1
        priority_score = round(min(1.0, (mastery_gap * 0.45) + (confidence_gap * 0.25) + (target_priority * 0.2) + status_weight), 3)
        bucket = _priority_bucket(priority_score)
        alias = state["learner_alias"]
        gap_key = f"gap:{alias}:{target_key}"
        intervention_key = f"intervention:{alias}:{target_key}:primary"
        pacing_window = state.get("metadata", {}).get("pacing_window") or target.get("pacing_window")
        gap_item = GapItem(
            gap_id=stable_id("kggap", gap_key),
            gap_key=gap_key,
            learner_alias=alias,
            target_key=target_key,
            target_id=state["target_id"],
            target_type=state["target_type"],
            label=state["label"],
            term=int(state.get("term") or 0),
            shadow_status=state["shadow_status"],
            required_mastery=float(state["required_mastery"]),
            required_confidence=float(state["required_confidence"]),
            observed_mastery=float(state["observed_mastery"]),
            observed_confidence=float(state["observed_confidence"]),
            mastery_gap=mastery_gap,
            confidence_gap=confidence_gap,
            target_priority=round(target_priority, 3),
            priority_score=priority_score,
            priority_bucket=bucket,
            pacing_window=pacing_window,
            source_ref=state["shadow_state_key"],
            source_sha256=state["source_sha256"],
            shadow_graph_sha256=shadow_hash,
            target_graph_sha256=target_hash,
            metadata={
                "caps_node_key": state.get("metadata", {}).get("caps_node_key") or target.get("caps_node_key"),
                "caps_source_ref": target.get("caps_source_ref"),
                "planner_policy": "kg4-default-advisory-gap-policy",
            },
        ).as_dict()
        intervention = InterventionRecommendation(
            intervention_id=stable_id("kgint", intervention_key),
            intervention_key=intervention_key,
            gap_key=gap_key,
            learner_alias=alias,
            target_key=target_key,
            intervention_type=_intervention_type(state, priority_score),
            recommendation_rank=1,
            priority_bucket=bucket,
            priority_score=priority_score,
            rationale=_intervention_rationale(state, priority_score),
            expected_evidence_event_type="post_intervention_shadow_observation",
            source_ref=gap_key,
            source_sha256=state["source_sha256"],
            shadow_graph_sha256=shadow_hash,
            target_graph_sha256=target_hash,
        ).as_dict()
        state_edge = PlannerEdge(
            edge_id=stable_id("kgge", f"{state['shadow_state_key']}|has_gap|{gap_key}"),
            source_key=state["shadow_state_key"],
            target_key=gap_key,
            edge_type="has_gap",
            label="KG-3 shadow state produces KG-4 advisory gap item",
            source_ref=state["shadow_state_key"],
            source_sha256=state["source_sha256"],
        ).as_dict()
        intervention_edge = PlannerEdge(
            edge_id=stable_id("kgge", f"{gap_key}|recommends_intervention|{intervention_key}"),
            source_key=gap_key,
            target_key=intervention_key,
            edge_type="recommends_intervention",
            label="KG-4 advisory gap item recommends a non-authoritative intervention",
            source_ref=gap_key,
            source_sha256=state["source_sha256"],
        ).as_dict()
        gap_items.append(gap_item)
        interventions.append(intervention)
        edges.extend([state_edge, intervention_edge])
        status_counts[state["shadow_status"]] += 1
        bucket_counts[bucket] += 1
        summary = learner_summaries.setdefault(alias, {
            "learner_alias": alias,
            "synthetic": True,
            "no_live_learner_data": True,
            "gap_items": 0,
            "urgent": 0,
            "high": 0,
            "medium": 0,
            "watch": 0,
            "top_priority_score": 0.0,
        })
        summary["gap_items"] += 1
        summary[bucket] += 1
        summary["top_priority_score"] = max(float(summary["top_priority_score"]), priority_score)

    gap_items.sort(key=lambda item: (item["learner_alias"], -item["priority_score"], item["target_key"]))
    interventions.sort(key=lambda item: (item["learner_alias"], -item["priority_score"], item["target_key"]))
    learner_profiles = sorted(learner_summaries.values(), key=lambda item: item["learner_alias"])

    return {
        "graph_id": KG4_GRAPH_ID,
        "graph_version": KG4_GRAPH_VERSION,
        "status": "gap_engine_intervention_plan_generated",
        "scope": {
            "curriculum": "CAPS",
            "grade": 4,
            "subject": "mathematics",
            "mode": "shadow_advisory",
            "data_classification": "synthetic_non_identifying",
        },
        "source": {
            "shadow_graph_path": str(shadow_graph_path),
            "shadow_graph_sha256": shadow_hash,
            "target_graph_path": str(target_graph_path),
            "target_graph_sha256": target_hash,
            "source_ref": "KG-4 advisory gap engine over KG-3 learner shadow graph",
        },
        "counts": {
            "synthetic_learners": len(learner_profiles),
            "target_states_referenced": len({item["target_key"] for item in gap_items}),
            "gap_items": len(gap_items),
            "intervention_recommendations": len(interventions),
            "planner_edges": len(edges),
            "shadow_gap_items": status_counts["shadow_gap"],
            "shadow_developing_items": status_counts["shadow_developing"],
            "urgent_items": bucket_counts["urgent"],
            "high_items": bucket_counts["high"],
            "medium_items": bucket_counts["medium"],
            "watch_items": bucket_counts["watch"],
        },
        "learner_gap_profiles": learner_profiles,
        "gap_items": gap_items,
        "intervention_recommendations": interventions,
        "planner_edges": edges,
        "review": {
            "review_status": "approved",
            "review_scope": "synthetic shadow advisory gap planning only",
            "review_required_before_runtime_use": True,
        },
        "boundary": {
            "advisory_only": True,
            "shadow_mode_only": True,
            "uses_live_learner_data": False,
            "no_live_learner_data_used": True,
            "runtime_authority": False,
            "intervention_runtime_authority_authorised": False,
            "learner_facing_model_change_authorised": False,
            "database_schema_migration_authorised": False,
        },
    }


def validate_gap_intervention_plan(plan: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if plan.get("graph_id") != KG4_GRAPH_ID:
        errors.append("unexpected KG-4 plan graph_id")
    if plan.get("boundary", {}).get("advisory_only") is not True:
        errors.append("KG-4 plan must be advisory only")
    if plan.get("boundary", {}).get("uses_live_learner_data") is not False:
        errors.append("KG-4 plan must not use live learner data")
    gap_items = plan.get("gap_items", [])
    interventions = plan.get("intervention_recommendations", [])
    edges = plan.get("planner_edges", [])
    gap_keys = {item.get("gap_key") for item in gap_items}
    intervention_keys = {item.get("intervention_key") for item in interventions}
    if len(gap_keys) != len(gap_items):
        errors.append("duplicate gap keys found")
    if len(intervention_keys) != len(interventions):
        errors.append("duplicate intervention keys found")
    all_gap_items_reference_shadow_states = all(str(item.get("source_ref", "")).startswith("shadow-state:") for item in gap_items)
    all_gap_items_source_grounded = all(item.get("source_sha256") and item.get("shadow_graph_sha256") and item.get("target_graph_sha256") for item in gap_items)
    all_interventions_source_grounded = all(item.get("source_ref") in gap_keys and item.get("source_sha256") for item in interventions)
    all_interventions_advisory = all(item.get("advisory_only") is True and item.get("shadow_mode") is True for item in interventions)
    orphan_edges = [edge for edge in edges if edge.get("edge_type") == "recommends_intervention" and edge.get("target_key") not in intervention_keys]
    orphan_edges.extend(edge for edge in edges if edge.get("edge_type") == "recommends_intervention" and edge.get("source_key") not in gap_keys)
    if not all_gap_items_reference_shadow_states:
        errors.append("not all gap items reference KG-3 shadow states")
    if not all_gap_items_source_grounded:
        errors.append("not all gap items are source grounded")
    if not all_interventions_source_grounded:
        errors.append("not all interventions are source grounded")
    if not all_interventions_advisory:
        errors.append("not all interventions are advisory shadow-mode recommendations")
    if orphan_edges:
        errors.append("orphan planner edges found")
    counts = plan.get("counts", {})
    if int(counts.get("gap_items") or 0) != len(gap_items):
        errors.append("gap item count mismatch")
    if int(counts.get("intervention_recommendations") or 0) != len(interventions):
        errors.append("intervention count mismatch")
    if int(counts.get("planner_edges") or 0) != len(edges):
        errors.append("planner edge count mismatch")
    return {
        "valid": not errors,
        "errors": errors,
        "counts": counts,
        "all_gap_items_reference_shadow_states": all_gap_items_reference_shadow_states,
        "all_gap_items_source_grounded": all_gap_items_source_grounded,
        "all_interventions_source_grounded": all_interventions_source_grounded,
        "all_interventions_advisory": all_interventions_advisory,
        "duplicate_gap_keys_found_false": len(gap_keys) == len(gap_items),
        "duplicate_intervention_keys_found_false": len(intervention_keys) == len(interventions),
        "orphan_planner_edges_found_false": not orphan_edges,
    }
