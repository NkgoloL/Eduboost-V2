"""Comprehensive test suite for Knowledge Graph domain modules and curriculum graph."""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from app.domain import (
    knowledge_graph_caps,
    knowledge_graph_target,
    knowledge_graph_learner_shadow,
    knowledge_graph_gap_engine,
    knowledge_graph_grounded_generation,
    knowledge_graph_authority_switch,
    knowledge_graph_product_alignment,
    knowledge_graph_post_switch_review,
    knowledge_graph_runtime_activation,
)
from app.services.curriculum import graph as curr_graph


def test_caps_domain_helpers(tmp_path: Path):
    sample_topic_map = {
        "_meta": {"source": "Test Source", "schema_version": "1.0.0"},
        "grade": 4,
        "subject": "Mathematics",
        "subject_code": "MATH",
        "terms": [
            {
                "term": 1,
                "weeks": "1-10",
                "topics": [
                    {
                        "topic": "Numbers",
                        "caps_ref": "NUM1",
                        "topic_index": 1,
                        "subtopics": [
                            {
                                "subtopic": "Whole numbers",
                                "caps_ref": "NUM1.1",
                                "subtopic_index": 1,
                                "prerequisites": [],
                                "assessment_standards": ["Count forwards", "Count backwards"],
                                "common_misconceptions": ["place_value_confusion"],
                            }
                        ],
                    }
                ],
            },
            {"term": 2, "topics": [{"topic": f"T{i}", "caps_ref": f"T{i}", "subtopics": [{"subtopic": f"S{i}", "caps_ref": f"S{i}", "assessment_standards": ["Std"], "common_misconceptions": []}]} for i in range(1, 10)]},
            {"term": 3, "topics": [{"topic": f"T3_{i}", "caps_ref": f"T3_{i}", "subtopics": [{"subtopic": f"S3_{i}", "caps_ref": f"S3_{i}", "assessment_standards": ["Std"], "common_misconceptions": []}]} for i in range(1, 10)]},
            {"term": 4, "topics": [{"topic": f"T4_{i}", "caps_ref": f"T4_{i}", "subtopics": [{"subtopic": f"S4_{i}", "caps_ref": f"S4_{i}", "assessment_standards": ["Std"], "common_misconceptions": []}]} for i in range(1, 10)]},
        ],
    }
    src_file = tmp_path / "test_topic_map.json"
    src_file.write_text(json.dumps(sample_topic_map), encoding="utf-8")

    graph = knowledge_graph_caps.build_caps_graph(src_file)
    assert graph["graph_id"] == knowledge_graph_caps.KG1_GRAPH_ID
    assert graph["counts"]["terms"] == 4
    assert len(graph["nodes"]) > 0
    assert len(graph["edges"]) > 0

    validation = knowledge_graph_caps.validate_caps_graph(graph)
    assert validation["valid"] is True

    # Test error handling in validate_caps_graph
    invalid_graph = dict(graph)
    invalid_graph["counts"] = dict(graph["counts"])
    invalid_graph["counts"]["terms"] = 3
    with pytest.raises(ValueError, match="Grade 4 Mathematics CAPS graph must contain 4 terms"):
        knowledge_graph_caps.validate_caps_graph(invalid_graph)

    # Test stable_id and sha256_text
    assert len(knowledge_graph_caps.sha256_text("abc")) == 64
    assert knowledge_graph_caps.stable_id("test", "key").startswith("test_")


def test_target_graph_domain_helpers(tmp_path: Path):
    caps_file = Path("data/knowledge_graph/caps_graph_foundation/grade4_mathematics_caps_graph.json")
    if caps_file.exists():
        target_graph = knowledge_graph_target.build_target_graph(caps_file)
        assert target_graph["graph_id"] == knowledge_graph_target.KG2_GRAPH_ID
        val = knowledge_graph_target.validate_target_graph(target_graph)
        assert val["valid"] is True

    # Test TargetState dataclass
    ts = knowledge_graph_target.TargetState(
        target_id="t1",
        target_key="tk1",
        target_type="topic",
        caps_node_key="cnk1",
        caps_node_id="cni1",
        label="Target 1",
        grade=4,
        subject="mathematics",
        term=1,
        required_mastery=0.85,
        required_confidence=0.8,
        priority=0.9,
        pacing_window="Term 1 Week 1-2",
        source_ref="ref1",
        source_sha256="hash1",
        caps_source_ref="caps_ref1",
        caps_source_sha256="caps_hash1",
    )
    d = ts.as_dict()
    assert d["target_id"] == "t1"
    assert d["required_mastery"] == 0.85

    te = knowledge_graph_target.TargetEdge(
        target_edge_id="te1",
        source_target_key="sk1",
        target_target_key="tk1",
        edge_type="prerequisite_of",
        label="Prereq",
        source_ref="ref1",
        source_sha256="hash1",
    )
    assert te.as_dict()["target_edge_id"] == "te1"


def test_learner_shadow_domain_helpers(tmp_path: Path):
    assert knowledge_graph_learner_shadow.clamp(1.5) == 1.0
    assert knowledge_graph_learner_shadow.clamp(-0.5) == 0.0
    assert knowledge_graph_learner_shadow.clamp(0.5) == 0.5

    target_file = Path("data/knowledge_graph/target_graph/grade4_mathematics_target_graph.json")
    obs_file = Path("data/knowledge_graph/learner_shadow_mode/kg003_shadow_observation_fixture.json")
    if target_file.exists() and obs_file.exists():
        shadow_graph = knowledge_graph_learner_shadow.build_learner_shadow_graph(target_file, obs_file)
        assert shadow_graph["graph_id"] == knowledge_graph_learner_shadow.KG3_GRAPH_ID
        val = knowledge_graph_learner_shadow.validate_learner_shadow_graph(shadow_graph)
        assert val["valid"] is True


def test_gap_engine_domain_helpers(tmp_path: Path):
    shadow_file = Path("data/knowledge_graph/learner_shadow_mode/grade4_mathematics_learner_shadow_graph.json")
    target_file = Path("data/knowledge_graph/target_graph/grade4_mathematics_target_graph.json")
    if shadow_file.exists() and target_file.exists():
        plan = knowledge_graph_gap_engine.build_gap_intervention_plan(shadow_file, target_file)
        assert plan["graph_id"] == knowledge_graph_gap_engine.KG4_GRAPH_ID
        val = knowledge_graph_gap_engine.validate_gap_intervention_plan(plan)
        assert val["valid"] is True

    # Test bucket helpers
    assert knowledge_graph_gap_engine._priority_bucket(0.8) == "urgent"
    assert knowledge_graph_gap_engine._priority_bucket(0.6) == "high"
    assert knowledge_graph_gap_engine._priority_bucket(0.4) == "medium"
    assert knowledge_graph_gap_engine._priority_bucket(0.2) == "watch"

    # Test intervention rationale
    state = {
        "observed_mastery": 0.4,
        "observed_confidence": 0.5,
        "required_mastery": 0.85,
        "required_confidence": 0.8,
    }
    rationale = knowledge_graph_gap_engine._intervention_rationale(state, 0.7)
    assert "Observed mastery 0.40" in rationale


def test_grounded_generation_domain_helpers(tmp_path: Path):
    gap_file = Path("data/knowledge_graph/gap_engine/grade4_mathematics_gap_intervention_plan.json")
    target_file = Path("data/knowledge_graph/target_graph/grade4_mathematics_target_graph.json")
    if gap_file.exists() and target_file.exists():
        pack = knowledge_graph_grounded_generation.build_graph_grounded_generation_pack(gap_file, target_file)
        assert pack["graph_id"] == knowledge_graph_grounded_generation.KG5_GRAPH_ID
        val = knowledge_graph_grounded_generation.validate_graph_grounded_generation_pack(pack)
        assert val["valid"] is True

    # Test strategy and stem helpers
    assert "Reteach" in knowledge_graph_grounded_generation._lesson_strategy("reteach_with_guided_practice")
    assert "prerequisite" in knowledge_graph_grounded_generation._lesson_strategy("prerequisite_review_and_mini_lesson")
    assert "Show your working" in knowledge_graph_grounded_generation._assessment_stem("Addition", "assessment_statement")
    assert "Complete a short practice" in knowledge_graph_grounded_generation._assessment_stem("Addition", "subtopic")


def test_authority_switch_domain_helpers(tmp_path: Path):
    product_file = Path("data/knowledge_graph/product_alignment/grade4_mathematics_product_alignment_pack.json")
    if product_file.exists():
        rec = knowledge_graph_authority_switch.build_authority_switch_readiness_pack(product_file)
        assert rec["graph_id"] == knowledge_graph_authority_switch.KG7_GRAPH_ID
        val = knowledge_graph_authority_switch.validate_authority_switch_readiness_pack(rec)
        assert val["valid"] is True


def test_product_alignment_domain_helpers(tmp_path: Path):
    grounded_file = Path("data/knowledge_graph/grounded_generation/grade4_mathematics_grounded_lesson_assessment_pack.json")
    if grounded_file.exists():
        rec = knowledge_graph_product_alignment.build_product_alignment_pack(grounded_file)
        assert rec["graph_id"] == knowledge_graph_product_alignment.KG6_GRAPH_ID
        val = knowledge_graph_product_alignment.validate_product_alignment_pack(rec)
        assert val["valid"] is True


def test_post_switch_review_domain_helpers(tmp_path: Path):
    authority_file = Path("data/knowledge_graph/authority_switch/grade4_mathematics_authority_switch_readiness.json")
    if authority_file.exists():
        rec = knowledge_graph_post_switch_review.build_post_switch_review_pack(authority_file)
        assert rec["graph_id"] == knowledge_graph_post_switch_review.KG8_GRAPH_ID
        val = knowledge_graph_post_switch_review.validate_post_switch_review_pack(rec)
        assert val["valid"] is True


def test_runtime_activation_domain_helpers(tmp_path: Path):
    post_switch_file = Path("data/knowledge_graph/post_switch_review/grade4_mathematics_post_switch_review_pack.json")
    if post_switch_file.exists():
        rec = knowledge_graph_runtime_activation.build_runtime_activation_pack(post_switch_file)
        assert rec["graph_id"] == knowledge_graph_runtime_activation.KGACT001_GRAPH_ID
        val = knowledge_graph_runtime_activation.validate_runtime_activation_pack(rec)
        assert val["valid"] is True


def test_curriculum_graph_service_comprehensive():
    # Test curriculum graph service classes, methods, errors
    assert curr_graph.ReviewStatus.APPROVED == "approved"
    assert curr_graph.EdgeType.PREREQUISITE_OF == "prerequisite_of"
    assert curr_graph.NodeStatus.DRAFT == "draft"

    # Test error classes
    err = curr_graph.Gate2R4ValidationError("Validation failed")
    assert isinstance(err, ValueError)
    err2 = curr_graph.MappingRejectedError("Mapping rejected")
    assert isinstance(err2, curr_graph.Gate2R4ValidationError)
