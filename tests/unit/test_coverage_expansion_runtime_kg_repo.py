"""
Unit tests for app.services.runtime_kg.repository to expand coverage.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.runtime_kg.repository import RuntimeKGRepository


@pytest.mark.asyncio
async def test_get_active_graph():
    db = AsyncMock()
    mock_result = MagicMock()
    mock_load = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_load
    db.execute.return_value = mock_result

    repo = RuntimeKGRepository(db)
    active = await repo.get_active_graph(graph_version="v1.0")

    assert active == mock_load
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_load_graph_idempotent_existing():
    db = AsyncMock()
    mock_result = MagicMock()
    existing_load = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_load
    db.execute.return_value = mock_result

    from app.services.runtime_kg.schemas import RuntimeKGGraphInput, RuntimeKGNodeInput
    node = RuntimeKGNodeInput(
        stable_code="NODE-01",
        node_type="concept",
        label="Test Node",
        curriculum_code="CAPS",
        grade=4,
        subject_code="MATH",
    )
    graph_input = RuntimeKGGraphInput(
        graph_version="v1.0",
        curriculum_code="CAPS",
        grade=4,
        subject_code="MATH",
        source_ref="ref",
        source_sha256="a" * 64,
        loaded_by="tester",
        nodes=(node,),
        edges=(),
    )

    repo = RuntimeKGRepository(db)
    res = await repo.load_graph_idempotent(graph_input)

    assert res == existing_load


@pytest.mark.asyncio
async def test_load_graph_idempotent_new():
    db = AsyncMock()
    db.add = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    from app.services.runtime_kg.schemas import (
        RuntimeKGGraphInput,
        RuntimeKGNodeInput,
        RuntimeKGEdgeInput,
    )
    node1 = RuntimeKGNodeInput(stable_code="N1", label="Node 1", topic="T1")
    node2 = RuntimeKGNodeInput(stable_code="N2", label="Node 2", topic="T2")
    edge = RuntimeKGEdgeInput(from_stable_code="N1", to_stable_code="N2", edge_type="prerequisite")

    graph_input = RuntimeKGGraphInput(
        graph_version="v1.0",
        curriculum_code="CAPS",
        grade=4,
        subject_code="MATH",
        source_ref="ref",
        source_sha256="a" * 64,
        loaded_by="tester",
        nodes=(node1, node2),
        edges=(edge,),
    )

    repo = RuntimeKGRepository(db)
    res = await repo.load_graph_idempotent(graph_input)

    assert res.graph_version == "v1.0"
    assert db.add.call_count >= 4  # graph_load + 2 nodes + 1 edge + 1 event
    assert db.flush.await_count >= 3


@pytest.mark.asyncio
async def test_activate_graph():
    db = AsyncMock()
    db.add = MagicMock()

    # 1. Missing graph
    db.scalar.return_value = None
    repo = RuntimeKGRepository(db)
    assert await repo.activate_graph("missing-v") is None

    # 2. Existing graph
    mock_graph = MagicMock()
    mock_graph.status = "staged"
    db.scalar.return_value = mock_graph
    activated = await repo.activate_graph("v1.0")
    assert activated is mock_graph
    assert mock_graph.status == "active"
    db.execute.assert_awaited()
    db.add.assert_called()
    db.flush.assert_awaited()


@pytest.mark.asyncio
async def test_upsert_learner_projection():
    db = AsyncMock()
    db.add = MagicMock()
    from app.services.runtime_kg.schemas import LearnerKGNodeProjection

    projection = LearnerKGNodeProjection(
        stable_code="N1",
        label="Node 1",
        mastery_score=0.8,
        confidence=0.9,
        gap_open=False,
        evidence_count=5,
    )

    # 1. New state
    db.scalar.return_value = None
    repo = RuntimeKGRepository(db)
    state = await repo.upsert_learner_projection(
        learner_id="l-1",
        graph_node_id=10,
        projection=projection,
    )
    assert state.learner_id == "l-1"
    assert state.graph_node_id == 10
    db.add.assert_called()
    db.flush.assert_awaited()

    # 2. Existing state update
    existing = MagicMock()
    db.scalar.return_value = existing
    res = await repo.upsert_learner_projection(
        learner_id="l-1",
        graph_node_id=10,
        projection=projection,
    )
    assert res is existing
    assert existing.mastery_score == 0.8


@pytest.mark.asyncio
async def test_get_active_nodes_and_evidence():
    db = AsyncMock()
    repo = RuntimeKGRepository(db)

    # 1. get_active_nodes when graph is None
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(repo, "get_active_graph", AsyncMock(return_value=None))
        assert await repo.get_active_nodes() is None
        assert await repo.project_and_persist_evidence(learner_id="l1", subject_code="MATH", evidence=[]) is None
        assert await repo.get_learner_gap_focus(learner_id="l1", subject_code="MATH") == []

    # 2. get_active_nodes when graph is present
    mock_graph = MagicMock(id=1, graph_version="v1.0")
    node_m = MagicMock(id=10, stable_code="N1", label="Node 1", topic="T1", mastery_weight=1.0, properties_json={}, strand=None, grade=4, subject_code="MATH", node_type="concept", curriculum_code="CAPS")
    mock_res = MagicMock()
    mock_res.scalars.return_value.all.return_value = [node_m]
    db.add = MagicMock()
    db.execute.return_value = mock_res

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(repo, "get_active_graph", AsyncMock(return_value=mock_graph))
        active_res = await repo.get_active_nodes(graph_version="v1.0", subject_code="MATH")
        assert active_res is not None
        g, nodes = active_res
        assert g is mock_graph
        assert len(nodes) == 1

        # project_and_persist_evidence
        from app.services.runtime_kg.schemas import LearnerEvidence
        ev = [LearnerEvidence(stable_code="N1", correct=True, confidence=0.8)]
        proj = await repo.project_and_persist_evidence(learner_id="l1", subject_code="MATH", evidence=ev)
        assert proj is not None
        assert db.add.called
        assert db.flush.awaited

        # get_learner_gap_focus
        state_m = MagicMock(mastery_score=0.4, confidence=0.7)
        mock_gap_res = MagicMock()
        mock_gap_res.scalars.return_value.all.return_value = [node_m]
        mock_gap_res.all.return_value = [(state_m, node_m)]
        db.execute.return_value = mock_gap_res
        focus = await repo.get_learner_gap_focus(learner_id="l1", subject_code="MATH", limit=3)
        assert len(focus) == 1
        assert focus[0]["stable_code"] == "N1"
        assert focus[0]["recommended_action"] == "targeted_practice"

        # record_rollback
        await repo.record_rollback(learner_id="l1", graph_version="v1.0", reason="testing")
        assert db.add.called



@pytest.mark.asyncio
async def test_runtime_kg_integration_flows():
    from app.services.runtime_kg.integration import (
        build_lesson_context_with_runtime_kg,
        runtime_kg_study_plan_focus,
    )
    from app.services.runtime_kg.feature_flags import RuntimeKGFeatureFlags
    from app.services.runtime_kg.schemas import RuntimeKGNodeInput

    db = AsyncMock()

    # 1. Disabled flags
    fallback_called = False
    async def _fallback(lid, subj):
        nonlocal fallback_called
        fallback_called = True
        return {"legacy": True, "subject": subj}

    flags_disabled = RuntimeKGFeatureFlags(enabled=False)
    ctx1 = await build_lesson_context_with_runtime_kg(
        db, "l-1", "math", fallback_builder=_fallback, flags=flags_disabled
    )
    assert ctx1["legacy"] is True
    assert fallback_called

    # 2. Enabled but graph not found
    flags_enabled = RuntimeKGFeatureFlags(enabled=True, graph_version="v1.0")
    db.scalar.return_value = None
    ctx2 = await build_lesson_context_with_runtime_kg(
        db, "l-1", "math", fallback_builder=_fallback, flags=flags_enabled
    )
    assert ctx2["legacy"] is True

    # 3. Enabled and graph found
    mock_graph = MagicMock()
    mock_graph.id = 10
    mock_graph.graph_version = "v1.0"
    db.scalar.return_value = mock_graph

    node_model = MagicMock(
        stable_code="N1",
        label="Place Value",
        node_type="concept",
        curriculum_code="CAPS",
        grade=4,
        subject_code="math",
        strand="Numbers",
        topic="Fractions",
        mastery_weight=1.0,
        properties_json={},
    )
    mock_exec = MagicMock()
    mock_exec.scalars.return_value.all.return_value = [node_model]
    db.execute.return_value = mock_exec

    ctx3 = await build_lesson_context_with_runtime_kg(
        db, "l-1", "math", fallback_builder=_fallback, flags=flags_enabled
    )
    assert ctx3["legacy_context_preserved"] is True
    assert ctx3["runtime_kg_enabled"] is True

    # 4. runtime_kg_study_plan_focus
    assert runtime_kg_study_plan_focus({"runtime_kg_enabled": False}) == []
    focus = runtime_kg_study_plan_focus({
        "runtime_kg_enabled": True,
        "knowledge_gaps": [{"stable_code": "N1", "topic": "Fractions"}],
    })
    assert len(focus) == 1
    assert focus[0]["stable_code"] == "N1"

