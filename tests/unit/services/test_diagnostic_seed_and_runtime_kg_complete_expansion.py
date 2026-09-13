import os
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.services.dev_diagnostic_seed import (
    DEV_DIAGNOSTIC_ITEMS,
    seed_dev_diagnostic_items,
)
from app.services.runtime_kg.feature_flags import RuntimeKGFeatureFlags
from app.services.runtime_kg.loader import (
    RuntimeKGLoadError,
    RuntimeKGLoadPlan,
    RuntimeKGLoader,
)
from app.services.runtime_kg.route_integration import (
    RuntimeKGRouteResult,
    build_runtime_kg_diagnostic_projection,
    build_runtime_kg_study_plan_payload,
    legacy_runtime_kg_result,
    projection_to_route_result,
)
from app.services.runtime_kg.schemas import (
    LearnerKGNodeProjection,
    RuntimeKGEdgeInput,
    RuntimeKGGraphInput,
    RuntimeKGNodeInput,
    RuntimeKGProjection,
)


@pytest.mark.asyncio
async def test_dev_diagnostic_seed():
    db = AsyncSession_mock = AsyncMock()
    # Mock ItemBankRepository.upsert
    with pytest.MonkeyPatch.context() as mp:
        repo_mock = MagicMock()
        repo_mock.upsert = AsyncMock()
        mp.setattr("app.services.dev_diagnostic_seed.ItemBankRepository", lambda session: repo_mock)

        count_g3 = await seed_dev_diagnostic_items(db, grade=3)
        assert count_g3 == len(DEV_DIAGNOSTIC_ITEMS)
        assert repo_mock.upsert.await_count == len(DEV_DIAGNOSTIC_ITEMS)

        # Non-matching grade returns 0
        repo_mock.upsert.reset_mock()
        count_g4 = await seed_dev_diagnostic_items(db, grade=4)
        assert count_g4 == 0
        assert repo_mock.upsert.await_count == 0


def test_runtime_kg_feature_flags():
    flags_default = RuntimeKGFeatureFlags()
    assert flags_default.enabled is False
    assert flags_default.graph_version == "caps-grade4-math-runtime-v1"

    # from_env enabled
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("EDUBOOST_RUNTIME_KG_ENABLED", "1")
        mp.setenv("EDUBOOST_RUNTIME_KG_VERSION", "custom-version")
        flags_env = RuntimeKGFeatureFlags.from_env()
        assert flags_env.enabled is True
        assert flags_env.graph_version == "custom-version"


def test_runtime_kg_loader_success_and_errors():
    loader = RuntimeKGLoader()

    valid_node = RuntimeKGNodeInput(stable_code="NODE_1", label="Node 1")
    valid_node2 = RuntimeKGNodeInput(stable_code="NODE_2", label="Node 2")
    valid_edge = RuntimeKGEdgeInput(from_stable_code="NODE_1", to_stable_code="NODE_2", weight=1.0)
    valid_graph = RuntimeKGGraphInput(
        graph_version="v1",
        source_ref="ref",
        source_sha256="a" * 64,
        loaded_by="tester",
        nodes=(valid_node, valid_node2),
        edges=(valid_edge,),
    )

    plan = loader.plan(valid_graph)
    assert isinstance(plan, RuntimeKGLoadPlan)
    assert plan.node_count == 2
    assert plan.edge_count == 1
    assert "v1:" in plan.idempotency_key

    # 1. Missing graph_version
    with pytest.raises(RuntimeKGLoadError, match="graph_version is required"):
        loader.plan(RuntimeKGGraphInput("", "ref", "a" * 64, "tester", nodes=(valid_node,)))

    # 2. Invalid source_sha256
    with pytest.raises(RuntimeKGLoadError, match="64 character SHA-256"):
        loader.plan(RuntimeKGGraphInput("v1", "ref", "bad_sha", "tester", nodes=(valid_node,)))

    # 3. Empty nodes
    with pytest.raises(RuntimeKGLoadError, match="at least one runtime KG node"):
        loader.plan(RuntimeKGGraphInput("v1", "ref", "a" * 64, "tester", nodes=()))

    # 4. Blank stable code
    blank_node = RuntimeKGNodeInput(stable_code="   ", label="Blank")
    with pytest.raises(RuntimeKGLoadError, match="node stable_code cannot be blank"):
        loader.plan(RuntimeKGGraphInput("v1", "ref", "a" * 64, "tester", nodes=(blank_node,)))

    # 5. Duplicate stable codes
    with pytest.raises(RuntimeKGLoadError, match="must be unique"):
        loader.plan(RuntimeKGGraphInput("v1", "ref", "a" * 64, "tester", nodes=(valid_node, valid_node)))

    # 6. Edge referencing nonexistent node
    bad_edge = RuntimeKGEdgeInput(from_stable_code="NODE_1", to_stable_code="NONEXISTENT")
    with pytest.raises(RuntimeKGLoadError, match="all edges must reference nodes in the same graph load"):
        loader.plan(RuntimeKGGraphInput("v1", "ref", "a" * 64, "tester", nodes=(valid_node, valid_node2), edges=(bad_edge,)))

    # 7. Self edge
    self_edge = RuntimeKGEdgeInput(from_stable_code="NODE_1", to_stable_code="NODE_1")
    with pytest.raises(RuntimeKGLoadError, match="self-edges are not allowed"):
        loader.plan(RuntimeKGGraphInput("v1", "ref", "a" * 64, "tester", nodes=(valid_node, valid_node2), edges=(self_edge,)))

    # 8. Negative edge weight
    neg_edge = RuntimeKGEdgeInput(from_stable_code="NODE_1", to_stable_code="NODE_2", weight=-0.5)
    with pytest.raises(RuntimeKGLoadError, match="must be non-negative"):
        loader.plan(RuntimeKGGraphInput("v1", "ref", "a" * 64, "tester", nodes=(valid_node, valid_node2), edges=(neg_edge,)))


@pytest.mark.asyncio
async def test_runtime_kg_route_integration_branches():
    db = AsyncMock()

    # 1. Feature flag disabled
    disabled_flags = RuntimeKGFeatureFlags(enabled=False)
    res_disabled = await build_runtime_kg_diagnostic_projection(
        db,
        learner_id="l1",
        subject_code="MATH",
        correct_by_item_id={"i1": True},
        item_to_stable_code={"i1": "NODE_1"},
        flags=disabled_flags,
    )
    assert res_disabled.runtime_kg_enabled is False
    assert res_disabled.rollback_reason == "runtime_kg_feature_flag_disabled"

    # 2. No mapped diagnostic items
    enabled_flags = RuntimeKGFeatureFlags(enabled=True)
    res_no_map = await build_runtime_kg_diagnostic_projection(
        db,
        learner_id="l1",
        subject_code="MATH",
        correct_by_item_id={"i1": True},
        item_to_stable_code={},
        flags=enabled_flags,
    )
    assert res_no_map.rollback_reason == "no_diagnostic_items_mapped_to_runtime_kg"

    # 3. Active graph missing (project_and_persist_evidence returns None)
    repo_mock = MagicMock()
    repo_mock.project_and_persist_evidence = AsyncMock(return_value=None)
    repo_mock.record_rollback = AsyncMock()

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("app.services.runtime_kg.repository.RuntimeKGRepository", lambda session: repo_mock)
        res_missing = await build_runtime_kg_diagnostic_projection(
            db,
            learner_id="l1",
            subject_code="MATH",
            correct_by_item_id={"i1": True},
            item_to_stable_code={"i1": "NODE_1"},
            flags=enabled_flags,
        )
        assert res_missing.rollback_reason == "active_runtime_kg_graph_missing"
        assert repo_mock.record_rollback.await_count == 1

    # 4. Study plan payload disabled
    sp_disabled = await build_runtime_kg_study_plan_payload(
        db,
        learner_id="l1",
        subject_code="MATH",
        flags=disabled_flags,
    )
    assert sp_disabled["runtime_kg_enabled"] is False

    # 5. Study plan payload enabled but no focus items
    repo_mock.get_learner_gap_focus = AsyncMock(return_value=[])
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("app.services.runtime_kg.repository.RuntimeKGRepository", lambda session: repo_mock)
        sp_no_focus = await build_runtime_kg_study_plan_payload(
            db,
            learner_id="l1",
            subject_code="MATH",
            flags=enabled_flags,
        )
        assert sp_no_focus["rollback_reason"] == "no_runtime_kg_focus_items"

    # 6. Study plan payload enabled with focus items
    focus_item = {"stable_code": "NODE_1", "mastery_score": 0.3}
    repo_mock.get_learner_gap_focus = AsyncMock(return_value=[focus_item])
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("app.services.runtime_kg.repository.RuntimeKGRepository", lambda session: repo_mock)
        sp_focus = await build_runtime_kg_study_plan_payload(
            db,
            learner_id="l1",
            subject_code="MATH",
            flags=enabled_flags,
        )
        assert sp_focus["runtime_kg_enabled"] is True
        assert sp_focus["behaviour"] == "runtime_kg_study_plan_focus"
        assert len(sp_focus["focus_items"]) == 1
