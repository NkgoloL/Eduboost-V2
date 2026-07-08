from __future__ import annotations

import os

import pytest

from app.modules.study_plans.runtime_kg_planner import build_runtime_kg_week_focus
from app.services.runtime_kg.feature_flags import RuntimeKGFeatureFlags
from app.services.runtime_kg.integration import diagnostic_evidence_to_runtime_kg, runtime_kg_study_plan_focus
from app.services.runtime_kg.loader import RuntimeKGLoadError, RuntimeKGLoader
from app.services.runtime_kg.schemas import LearnerEvidence, RuntimeKGEdgeInput, RuntimeKGGraphInput, RuntimeKGNodeInput
from app.services.runtime_kg.service import RuntimeKGProjectionService


def _graph() -> RuntimeKGGraphInput:
    return RuntimeKGGraphInput(
        graph_version="caps-grade4-math-runtime-v1",
        source_ref="reviewed-caps-graph-export.json",
        source_sha256="a" * 64,
        loaded_by="unit-test",
        nodes=(
            RuntimeKGNodeInput(stable_code="G4.MATH.NUM.001", label="Place value", topic="Numbers"),
            RuntimeKGNodeInput(stable_code="G4.MATH.NUM.002", label="Expanded notation", topic="Numbers"),
        ),
        edges=(RuntimeKGEdgeInput(from_stable_code="G4.MATH.NUM.001", to_stable_code="G4.MATH.NUM.002"),),
    )


def test_runtime_kg_loader_is_idempotent_for_same_graph() -> None:
    loader = RuntimeKGLoader()
    first = loader.plan(_graph())
    second = loader.plan(_graph())
    assert first.idempotency_key == second.idempotency_key
    assert first.node_count == 2
    assert first.edge_count == 1


def test_runtime_kg_loader_rejects_duplicate_nodes() -> None:
    graph = RuntimeKGGraphInput(
        graph_version="dup",
        source_ref="x",
        source_sha256="b" * 64,
        loaded_by="unit-test",
        nodes=(
            RuntimeKGNodeInput(stable_code="same", label="A"),
            RuntimeKGNodeInput(stable_code="same", label="B"),
        ),
    )
    with pytest.raises(RuntimeKGLoadError, match="unique"):
        RuntimeKGLoader().plan(graph)


def test_runtime_kg_loader_rejects_edges_to_unknown_nodes() -> None:
    graph = RuntimeKGGraphInput(
        graph_version="bad-edge",
        source_ref="x",
        source_sha256="c" * 64,
        loaded_by="unit-test",
        nodes=(RuntimeKGNodeInput(stable_code="known", label="Known"),),
        edges=(RuntimeKGEdgeInput(from_stable_code="known", to_stable_code="missing"),),
    )
    with pytest.raises(RuntimeKGLoadError, match="same graph"):
        RuntimeKGLoader().plan(graph)


def test_runtime_kg_projection_opens_mastery_gaps() -> None:
    projection = RuntimeKGProjectionService(mastery_threshold=0.7).project_from_evidence(
        learner_id="learner-1",
        subject_code="Mathematics",
        graph_version="caps-grade4-math-runtime-v1",
        nodes=list(_graph().nodes),
        evidence=[
            LearnerEvidence(stable_code="G4.MATH.NUM.001", correct=True, confidence=0.9),
            LearnerEvidence(stable_code="G4.MATH.NUM.002", correct=False, confidence=0.9),
        ],
    )
    assert len(projection.open_gaps) == 1
    assert projection.open_gaps[0].stable_code == "G4.MATH.NUM.002"
    assert projection.lesson_context()["runtime_kg_enabled"] is True


def test_diagnostic_evidence_mapping_ignores_unmapped_items() -> None:
    evidence = diagnostic_evidence_to_runtime_kg(
        {"item-1": True, "item-2": False},
        {"item-1": "G4.MATH.NUM.001"},
    )
    assert evidence == [LearnerEvidence(stable_code="G4.MATH.NUM.001", correct=True, confidence=0.7, evidence_source="diagnostic")]


def test_runtime_kg_feature_flag_defaults_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EDUBOOST_RUNTIME_KG_ENABLED", raising=False)
    assert RuntimeKGFeatureFlags.from_env().enabled is False
    monkeypatch.setenv("EDUBOOST_RUNTIME_KG_ENABLED", "true")
    assert RuntimeKGFeatureFlags.from_env().enabled is True


def test_study_plan_projection_uses_runtime_kg_context() -> None:
    context = {
        "runtime_kg_enabled": True,
        "graph_version": "caps-grade4-math-runtime-v1",
        "knowledge_gaps": [{"stable_code": "G4.MATH.NUM.002", "topic": "Expanded notation"}],
    }
    focus = runtime_kg_study_plan_focus(context)
    assert focus[0]["reason"] == "runtime_kg_gap"
    assert build_runtime_kg_week_focus(context)["runtime_kg_enabled"] is True
