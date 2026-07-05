"""Pure learner graph shadow-mode helpers for KG-3.

KG-3 derives a pseudonymous learner shadow graph from the approved KG-2 target
read model and a synthetic observation fixture. It intentionally has no database
dependency, does not mutate learner records, and does not become the authority
for learner-facing decisions. Runtime KG authority, learner graph persistence,
DB migrations, and learner-facing model changes remain out of scope.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

KG3_GRAPH_ID = "KG-3-LEARNER-SHADOW-GRAPH-GRADE-4-MATHEMATICS"
KG3_GRAPH_VERSION = "kg3-learner-shadow-mode-v1"
DEFAULT_TARGET_GRAPH = Path("data/knowledge_graph/target_graph/grade4_mathematics_target_graph.json")
DEFAULT_OBSERVATIONS = Path("data/knowledge_graph/learner_shadow_mode/kg003_shadow_observation_fixture.json")


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


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


@dataclass(frozen=True)
class LearnerShadowState:
    shadow_state_id: str
    shadow_state_key: str
    learner_alias: str
    target_key: str
    target_id: str
    target_type: str
    label: str
    term: int
    required_mastery: float
    required_confidence: float
    observed_mastery: float
    observed_confidence: float
    mastery_gap: float
    shadow_status: str
    source_ref: str
    source_sha256: str
    target_graph_sha256: str
    shadow_mode: bool = True
    no_live_learner_data: bool = True
    review_status: str = "approved"
    version: str = KG3_GRAPH_VERSION
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "shadow_state_id": self.shadow_state_id,
            "shadow_state_key": self.shadow_state_key,
            "learner_alias": self.learner_alias,
            "target_key": self.target_key,
            "target_id": self.target_id,
            "target_type": self.target_type,
            "label": self.label,
            "term": self.term,
            "required_mastery": self.required_mastery,
            "required_confidence": self.required_confidence,
            "observed_mastery": self.observed_mastery,
            "observed_confidence": self.observed_confidence,
            "mastery_gap": self.mastery_gap,
            "shadow_status": self.shadow_status,
            "source_ref": self.source_ref,
            "source_sha256": self.source_sha256,
            "target_graph_sha256": self.target_graph_sha256,
            "shadow_mode": self.shadow_mode,
            "no_live_learner_data": self.no_live_learner_data,
            "review_status": self.review_status,
            "version": self.version,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class LearnerShadowEvent:
    event_id: str
    event_key: str
    learner_alias: str
    target_key: str
    event_type: str
    observed_mastery: float
    observed_confidence: float
    source_ref: str
    source_sha256: str
    shadow_mode: bool = True
    no_live_learner_data: bool = True
    review_status: str = "approved"
    version: str = KG3_GRAPH_VERSION

    def as_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_key": self.event_key,
            "learner_alias": self.learner_alias,
            "target_key": self.target_key,
            "event_type": self.event_type,
            "observed_mastery": self.observed_mastery,
            "observed_confidence": self.observed_confidence,
            "source_ref": self.source_ref,
            "source_sha256": self.source_sha256,
            "shadow_mode": self.shadow_mode,
            "no_live_learner_data": self.no_live_learner_data,
            "review_status": self.review_status,
            "version": self.version,
        }


@dataclass(frozen=True)
class LearnerShadowEdge:
    edge_id: str
    source_key: str
    target_key: str
    edge_type: str
    label: str
    source_ref: str
    source_sha256: str
    shadow_mode: bool = True
    no_live_learner_data: bool = True
    review_status: str = "approved"
    version: str = KG3_GRAPH_VERSION

    def as_dict(self) -> dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "source_key": self.source_key,
            "target_key": self.target_key,
            "edge_type": self.edge_type,
            "label": self.label,
            "source_ref": self.source_ref,
            "source_sha256": self.source_sha256,
            "shadow_mode": self.shadow_mode,
            "no_live_learner_data": self.no_live_learner_data,
            "review_status": self.review_status,
            "version": self.version,
        }


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _target_states(target_graph: dict[str, Any]) -> list[dict[str, Any]]:
    states = target_graph.get("target_states", [])
    if not isinstance(states, list):
        raise ValueError("target_graph.target_states must be a list")
    return states


def _shadow_value(profile: dict[str, Any], target: dict[str, Any], index: int) -> tuple[float, float]:
    baseline = float(profile.get("baseline_mastery", 0.55))
    type_adjustments = profile.get("target_type_adjustments", {})
    term_adjustments = profile.get("term_adjustments", {})
    type_delta = float(type_adjustments.get(target.get("target_type"), 0.0))
    term_delta = float(term_adjustments.get(str(target.get("term")), 0.0))
    # Stable, deterministic variation from the target key avoids flat synthetic data.
    variation = ((int(sha256_text(str(target.get("target_key")))[:4], 16) % 17) - 8) / 100.0
    mastery = clamp(baseline + type_delta + term_delta + variation, 0.05, 0.98)
    confidence_offset = float(profile.get("confidence_offset", -0.04))
    confidence = clamp(mastery + confidence_offset + (0.02 if index % 3 == 0 else 0.0), 0.05, 0.98)
    return round(mastery, 3), round(confidence, 3)


def _status(observed_mastery: float, observed_confidence: float, required_mastery: float, required_confidence: float) -> str:
    if observed_mastery >= required_mastery and observed_confidence >= required_confidence:
        return "shadow_mastered"
    if observed_mastery >= required_mastery - 0.15:
        return "shadow_developing"
    return "shadow_gap"


def build_learner_shadow_graph(
    target_graph_path: Path = DEFAULT_TARGET_GRAPH,
    observation_fixture_path: Path = DEFAULT_OBSERVATIONS,
) -> dict[str, Any]:
    target_graph_path = Path(target_graph_path)
    observation_fixture_path = Path(observation_fixture_path)
    target_graph = _load_json(target_graph_path)
    fixture = _load_json(observation_fixture_path)
    target_hash = file_sha256(target_graph_path)
    fixture_hash = file_sha256(observation_fixture_path)

    learners = fixture.get("synthetic_learners", [])
    if not learners:
        raise ValueError("KG-3 fixture must include synthetic_learners")

    states: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    status_counts = {"shadow_mastered": 0, "shadow_developing": 0, "shadow_gap": 0}

    target_states = _target_states(target_graph)
    for learner in learners:
        alias = learner["learner_alias"]
        if not alias.startswith("kg3-synthetic-"):
            raise ValueError("KG-3 learner aliases must be synthetic and non-identifying")
        learner_node_key = f"shadow-learner:{alias}"
        for idx, target in enumerate(target_states):
            target_key = target["target_key"]
            mastery, confidence = _shadow_value(learner, target, idx)
            required_mastery = float(target["required_mastery"])
            required_confidence = float(target["required_confidence"])
            gap = round(required_mastery - mastery, 3)
            status = _status(mastery, confidence, required_mastery, required_confidence)
            status_counts[status] += 1
            state_key = f"shadow-state:{alias}:{target_key}"
            event_key = f"shadow-event:{alias}:{target_key}:synthetic-observation"
            state = LearnerShadowState(
                shadow_state_id=stable_id("kgls", state_key),
                shadow_state_key=state_key,
                learner_alias=alias,
                target_key=target_key,
                target_id=target["target_id"],
                target_type=target["target_type"],
                label=target["label"],
                term=int(target.get("term") or 0),
                required_mastery=required_mastery,
                required_confidence=required_confidence,
                observed_mastery=mastery,
                observed_confidence=confidence,
                mastery_gap=gap,
                shadow_status=status,
                source_ref=f"KG-3 synthetic fixture:{alias}",
                source_sha256=fixture_hash,
                target_graph_sha256=target_hash,
                metadata={
                    "target_graph_id": target_graph.get("graph_id"),
                    "target_graph_version": target_graph.get("graph_version"),
                    "pacing_window": target.get("pacing_window"),
                    "priority": target.get("priority"),
                    "caps_node_key": target.get("caps_node_key"),
                },
            )
            event = LearnerShadowEvent(
                event_id=stable_id("kgle", event_key),
                event_key=event_key,
                learner_alias=alias,
                target_key=target_key,
                event_type="synthetic_shadow_observation",
                observed_mastery=mastery,
                observed_confidence=confidence,
                source_ref=f"KG-3 synthetic fixture:{alias}",
                source_sha256=fixture_hash,
            )
            edge = LearnerShadowEdge(
                edge_id=stable_id("kglee", f"{learner_node_key}|shadow_observed|{state_key}"),
                source_key=learner_node_key,
                target_key=state_key,
                edge_type="shadow_observed",
                label="Synthetic learner shadow observation creates learner-target state",
                source_ref=event.event_key,
                source_sha256=fixture_hash,
            )
            target_edge = LearnerShadowEdge(
                edge_id=stable_id("kglee", f"{state_key}|shadows_target|{target_key}"),
                source_key=state_key,
                target_key=target_key,
                edge_type="shadows_target",
                label="Learner shadow state references approved KG-2 target state",
                source_ref=f"KG-2:{target_key}",
                source_sha256=target_hash,
            )
            states.append(state.as_dict())
            events.append(event.as_dict())
            edges.extend([edge.as_dict(), target_edge.as_dict()])

    graph = {
        "graph_id": KG3_GRAPH_ID,
        "graph_version": KG3_GRAPH_VERSION,
        "status": "learner_shadow_graph_generated",
        "scope": {
            "curriculum": "CAPS",
            "grade": 4,
            "subject": "mathematics",
            "mode": "shadow",
            "data_classification": "synthetic_non_identifying",
        },
        "source": {
            "target_graph_path": str(target_graph_path),
            "target_graph_sha256": target_hash,
            "observation_fixture_path": str(observation_fixture_path),
            "observation_fixture_sha256": fixture_hash,
            "source_ref": fixture.get("source_ref", "KG-3 synthetic learner observation fixture"),
        },
        "counts": {
            "synthetic_learners": len(learners),
            "target_states_referenced": len(target_states),
            "learner_shadow_states": len(states),
            "shadow_evidence_events": len(events),
            "shadow_edges": len(edges),
            **status_counts,
        },
        "learner_profiles": [
            {
                "learner_alias": learner["learner_alias"],
                "synthetic": True,
                "no_pii": True,
                "fixture_ref": learner.get("fixture_ref"),
            }
            for learner in learners
        ],
        "learner_shadow_states": states,
        "shadow_evidence_events": events,
        "shadow_edges": edges,
        "review": {
            "review_status": "approved",
            "review_scope": "KG-3 shadow mode fixture and generated read model",
            "runtime_authority": False,
        },
        "boundary": {
            "shadow_mode": True,
            "no_live_learner_data": True,
            "runtime_kg_implementation_claimed": False,
            "runtime_kg_authority_switch_authorised": False,
            "database_schema_migration_authorised": False,
            "learner_facing_model_change_authorised": False,
            "learner_graph_persistence_authorised": False,
            "production_release_authorised": False,
        },
    }
    return graph


def validate_learner_shadow_graph(graph: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    states = graph.get("learner_shadow_states", [])
    events = graph.get("shadow_evidence_events", [])
    edges = graph.get("shadow_edges", [])
    counts = graph.get("counts", {})
    target_refs = {state.get("target_key") for state in states}
    state_keys = [state.get("shadow_state_key") for state in states]
    event_keys = [event.get("event_key") for event in events]

    if graph.get("graph_id") != KG3_GRAPH_ID:
        errors.append("unexpected KG-3 graph_id")
    if counts.get("synthetic_learners", 0) < 2:
        errors.append("KG-3 requires at least two synthetic learners")
    if counts.get("target_states_referenced", 0) < 100:
        errors.append("KG-3 must reference at least 100 KG-2 target states")
    if len(states) != counts.get("learner_shadow_states"):
        errors.append("learner shadow state count mismatch")
    if len(events) != counts.get("shadow_evidence_events"):
        errors.append("shadow evidence event count mismatch")
    if len(edges) != counts.get("shadow_edges"):
        errors.append("shadow edge count mismatch")
    if len(state_keys) != len(set(state_keys)):
        errors.append("duplicate learner shadow state keys found")
    if len(event_keys) != len(set(event_keys)):
        errors.append("duplicate shadow event keys found")
    if not target_refs:
        errors.append("KG-3 states must reference KG-2 target keys")

    for state in states:
        if state.get("shadow_mode") is not True:
            errors.append("all learner shadow states must be shadow_mode true")
            break
        if state.get("no_live_learner_data") is not True:
            errors.append("all learner shadow states must confirm no_live_learner_data")
            break
        if not str(state.get("learner_alias", "")).startswith("kg3-synthetic-"):
            errors.append("learner aliases must be synthetic and non-identifying")
            break
        if state.get("target_key") is None or state.get("target_graph_sha256") is None:
            errors.append("shadow states must carry target provenance")
            break
        if state.get("source_sha256") is None:
            errors.append("shadow states must carry fixture provenance")
            break
    for event in events:
        if event.get("shadow_mode") is not True or event.get("no_live_learner_data") is not True:
            errors.append("shadow events must preserve shadow/no-live-data flags")
            break
    if graph.get("boundary", {}).get("runtime_kg_authority_switch_authorised") is not False:
        errors.append("runtime KG authority switch must remain false")
    if graph.get("boundary", {}).get("database_schema_migration_authorised") is not False:
        errors.append("database schema migration must remain false")
    return {
        "valid": not errors,
        "errors": errors,
        "counts": counts,
        "all_shadow_states_reference_targets": all(str(s.get("target_key", "")).startswith("target:g4m:") for s in states),
        "all_shadow_states_source_grounded": all(s.get("source_sha256") and s.get("target_graph_sha256") for s in states),
        "all_shadow_events_source_grounded": all(e.get("source_sha256") for e in events),
        "synthetic_only": all(str(s.get("learner_alias", "")).startswith("kg3-synthetic-") for s in states),
    }
