"""Comprehensive unit tests covering edge cases and validation error paths for Knowledge Graph domain modules.

Batch 428: Achieving >98% coverage across app/domain.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import pytest
from pydantic import ValidationError

from app.domain import (
    knowledge_graph_authority_switch as kg_auth,
    knowledge_graph_post_switch_review as kg_post,
    knowledge_graph_runtime_activation as kg_act,
    knowledge_graph_product_alignment as kg_prod,
)
from app.domain.item_schema import ItemCreate, ItemType
from app.domain.llm_schemas import DiagnosticItemContract


class TestItemSchemaAndLLMSchemasEdgeCases:
    def test_item_create_options_must_be_list_or_none(self):
        with pytest.raises(ValidationError) as exc:
            ItemCreate(
                caps_ref="NUM.1",
                subject="Mathematics",
                grade=4,
                term=1,
                topic="Numbers",
                subtopic="Whole numbers",
                skill="Addition",
                difficulty=0.5,
                discrimination=1.0,
                stem="2 + 2 = ?",
                answer_key="4",
                explanation="2 plus 2 is 4",
                item_type=ItemType.MCQ,
                options="not-a-list",
            )
        assert "options must be a list of dicts or None" in str(exc.value)

    def test_diagnostic_item_contract_distractors_validation(self):
        with pytest.raises(ValidationError) as exc:
            DiagnosticItemContract(
                item_id="item-1",
                subject="Mathematics",
                grade=4,
                topic="Numbers",
                skill="Addition",
                difficulty=0.0,
                discrimination=1.0,
                correct_answer="A",
                distractors={"A": "10", "B": "11", "C": "12"},
                caps_reference="CAPS:v1:NUM1",
                explanation="10 is correct",
            )
        assert "distractors must contain exactly A, B, C and D" in str(exc.value)

    def test_diagnostic_item_contract_caps_reference_canonical(self):
        with pytest.raises(ValidationError) as exc:
            DiagnosticItemContract(
                item_id="item-1",
                subject="Mathematics",
                grade=4,
                topic="Numbers",
                skill="Addition",
                difficulty=0.0,
                discrimination=1.0,
                correct_answer="A",
                distractors={"A": "10", "B": "11", "C": "12", "D": "13"},
                caps_reference="NOTCAPS:v1:NUM1",
                explanation="10 is correct",
            )
        assert "caps_reference must use canonical CAPS:<version>:... format" in str(exc.value)


class TestKGAuthoritySwitchValidationPaths:
    def test_item_key_invalid_collection(self):
        with pytest.raises(KeyError):
            kg_auth._source_item_key("unsupported_collection", {"key": "123"})

    def test_build_authority_switch_readiness_pack_bad_boundaries(self, tmp_path):
        base = {
            "boundary": {"preview_only": True, "uses_live_learner_data": False, "uses_guardian_pii": False},
            "tutor_previews": [{"tutor_preview_key": "t1"}],
            "study_plan_items": [{"study_plan_item_key": "s1"}],
            "gamification_award_candidates": [{"award_candidate_key": "g1"}],
            "parent_alignment_summaries": [{"parent_summary_key": "p1"}],
        }
        # preview_only false
        b1 = copy.deepcopy(base)
        b1["boundary"]["preview_only"] = False
        p1 = tmp_path / "b1.json"
        p1.write_text(json.dumps(b1), encoding="utf-8")
        with pytest.raises(ValueError, match="preview-only"):
            kg_auth.build_authority_switch_readiness_pack(p1)

        # uses_live_learner_data true
        b2 = copy.deepcopy(base)
        b2["boundary"]["uses_live_learner_data"] = True
        p2 = tmp_path / "b2.json"
        p2.write_text(json.dumps(b2), encoding="utf-8")
        with pytest.raises(ValueError, match="no live learner data"):
            kg_auth.build_authority_switch_readiness_pack(p2)

        # uses_guardian_pii true
        b3 = copy.deepcopy(base)
        b3["boundary"]["uses_guardian_pii"] = True
        p3 = tmp_path / "b3.json"
        p3.write_text(json.dumps(b3), encoding="utf-8")
        with pytest.raises(ValueError, match="no guardian PII"):
            kg_auth.build_authority_switch_readiness_pack(p3)

        # missing collection
        b4 = copy.deepcopy(base)
        b4["tutor_previews"] = []
        p4 = tmp_path / "b4.json"
        p4.write_text(json.dumps(b4), encoding="utf-8")
        with pytest.raises(ValueError, match="all KG-6 product-alignment collections"):
            kg_auth.build_authority_switch_readiness_pack(p4)

    def test_validate_authority_switch_readiness_pack_error_branches(self):
        valid = kg_auth.build_authority_switch_readiness_pack()
        res = kg_auth.validate_authority_switch_readiness_pack(valid)
        assert res["valid"] is True

        # Mutate to trigger all failure branches
        bad = copy.deepcopy(valid)
        bad["graph_id"] = "wrong-graph-id"
        bad["status"] = "wrong-status"
        bad["boundary"]["database_schema_migration_authorised"] = True
        bad["boundary"]["readiness_only"] = False
        bad["boundary"]["uses_live_learner_data"] = True
        bad["boundary"]["uses_guardian_pii"] = True
        bad["counts"]["authority_readiness_checks"] = -1
        bad["counts"]["legacy_projection_mappings"] = 10
        bad["authority_readiness_checks"][0]["passed"] = False
        bad["legacy_projection_mappings"][0]["readiness_only"] = False
        bad["legacy_cleanup_tasks"][0]["executed"] = True
        bad["rollback_controls"][0]["available"] = False
        bad["switch_control_edges"][0]["source_key"] = "orphan-key-xyz"

        bad_res = kg_auth.validate_authority_switch_readiness_pack(bad)
        assert bad_res["valid"] is False
        assert len(bad_res["errors"]) >= 10


class TestKGPostSwitchReviewValidationPaths:
    def test_build_post_switch_review_pack_bad_boundaries(self, tmp_path):
        base = {
            "graph_id": "KG-ACT-001",
            "boundary": {
                "runtime_kg_implementation_claimed": True,
                "runtime_kg_authority_switch_authorised": True,
                "authority_switch_executed": True,
                "database_schema_migration_authorised": False,
                "learner_facing_model_change_authorised": False,
                "learner_graph_persistence_authorised": False,
                "legacy_cleanup_executed": False,
                "llm_provider_call_authorised": False,
                "production_release_authorised": False,
                "deployment_authorised": False,
                "release_tag_authorised": False,
                "public_beta_authorised": False,
                "public_beta_live_traffic_authorised": False,
                "billing_launch_authorised": False,
                "live_payment_processing_authorised": False,
                "uses_live_learner_data": False,
                "uses_guardian_pii": False,
            },
            "counts": {"activation_controls": 4},
        }

        # boundary false keys true
        b1 = copy.deepcopy(base)
        b1["boundary"]["database_schema_migration_authorised"] = True
        p1 = tmp_path / "p1.json"
        p1.write_text(json.dumps(b1), encoding="utf-8")
        with pytest.raises(ValueError, match="protected boundary false"):
            kg_post.build_post_switch_review_pack(p1)

        # live learner data true
        b2 = copy.deepcopy(base)
        b2["boundary"]["uses_live_learner_data"] = True
        p2 = tmp_path / "p2.json"
        p2.write_text(json.dumps(b2), encoding="utf-8")
        with pytest.raises(ValueError, match="no live learner data"):
            kg_post.build_post_switch_review_pack(p2)

        # guardian pii true
        b3 = copy.deepcopy(base)
        b3["boundary"]["uses_guardian_pii"] = True
        p3 = tmp_path / "p3.json"
        p3.write_text(json.dumps(b3), encoding="utf-8")
        with pytest.raises(ValueError, match="no guardian PII"):
            kg_post.build_post_switch_review_pack(p3)

    def test_validate_post_switch_review_pack_error_branches(self):
        valid = kg_post.build_post_switch_review_pack()
        res = kg_post.validate_post_switch_review_pack(valid)
        assert res["valid"] is True

        bad = copy.deepcopy(valid)
        bad["graph_id"] = "wrong-id"
        bad["status"] = "wrong-status"
        bad["boundary"]["runtime_kg_authority_switch_authorised"] = False
        bad["boundary"]["database_schema_migration_authorised"] = True
        bad["boundary"]["optimisation_execution_authorised"] = True
        bad["boundary"]["uses_live_learner_data"] = True
        bad["boundary"]["uses_guardian_pii"] = True
        bad["boundary"]["uses_llm_provider"] = True
        bad["counts"]["optimisation_candidates"] = 2
        bad["counts"]["scale_review_checks"] = 2
        bad["counts"]["monitoring_requirements"] = 2
        bad["counts"]["rollback_observability_checks"] = 2
        bad["counts"]["readiness_checks_inherited"] = 2
        bad["counts"]["legacy_projection_mappings_inherited"] = 2
        bad["post_switch_review_edges"][0]["source_key"] = "orphan-source-key"

        bad_res = kg_post.validate_post_switch_review_pack(bad)
        assert bad_res["valid"] is False
        assert len(bad_res["errors"]) >= 10


class TestKGRuntimeActivationValidationPaths:
    def test_build_runtime_activation_pack_bad_boundaries(self, tmp_path):
        base = {
            "boundary": {
                "readiness_only": True,
                "uses_live_learner_data": False,
                "uses_guardian_pii": False,
            },
            "authority_readiness_checks": [{"check": 1}],
            "legacy_projection_mappings": [{"mapping": 1}],
            "rollback_controls": [{"rb": 1}],
            "switch_control_edges": [{"edge": 1}],
        }

        # uses live data
        b1 = copy.deepcopy(base)
        b1["boundary"]["uses_live_learner_data"] = True
        p1 = tmp_path / "a1.json"
        p1.write_text(json.dumps(b1), encoding="utf-8")
        with pytest.raises(ValueError, match="no live learner data"):
            kg_act.build_runtime_activation_pack(p1)

        # uses guardian pii
        b2 = copy.deepcopy(base)
        b2["boundary"]["uses_guardian_pii"] = True
        p2 = tmp_path / "a2.json"
        p2.write_text(json.dumps(b2), encoding="utf-8")
        with pytest.raises(ValueError, match="no guardian PII"):
            kg_act.build_runtime_activation_pack(p2)

        # missing checks
        b3 = copy.deepcopy(base)
        b3["authority_readiness_checks"] = []
        p3 = tmp_path / "a3.json"
        p3.write_text(json.dumps(b3), encoding="utf-8")
        with pytest.raises(ValueError, match="requires KG-7"):
            kg_act.build_runtime_activation_pack(p3)

    def test_validate_runtime_activation_pack_error_branches(self):
        valid = kg_act.build_runtime_activation_pack()
        res = kg_act.validate_runtime_activation_pack(valid)
        assert res["valid"] is True

        bad = copy.deepcopy(valid)
        bad["graph_id"] = "wrong-act-id"
        bad["status"] = "wrong-act-status"
        bad["boundary"]["runtime_kg_authority_switch_authorised"] = False
        bad["boundary"]["runtime_kg_implementation_claimed"] = False
        bad["boundary"]["database_schema_migration_authorised"] = True
        bad["boundary"]["uses_live_learner_data"] = True
        bad["boundary"]["uses_guardian_pii"] = True
        bad["boundary"]["uses_llm_provider"] = True
        bad["counts"]["activation_controls"] = 0
        bad["counts"]["activation_edges"] = 0
        bad["counts"]["readiness_checks_inherited"] = 0
        bad["counts"]["legacy_projection_mappings_inherited"] = 0
        bad["activation_controls"][0]["executed"] = False
        bad["activation_edges"][0]["source_key"] = "orphan-control-key"

        bad_res = kg_act.validate_runtime_activation_pack(bad)
        assert bad_res["valid"] is False
        assert len(bad_res["errors"]) >= 10


class TestKGProductAlignmentValidationPaths:
    def test_build_product_alignment_pack_bad_lessons_or_assessments(self, tmp_path):
        base = {
            "boundary": {"generation_preview_only": True, "uses_live_learner_data": False, "uses_guardian_pii": False},
            "lesson_drafts": [
                {
                    "lesson_key": "l1",
                    "learner_alias": "kg3-synthetic-1",
                    "target_key": "t1",
                    "target_type": "subtopic",
                    "title": "Lesson 1",
                    "priority_bucket": "high",
                    "priority_score": 10,
                    "no_live_learner_data": True,
                    "human_review_required": True,
                }
            ],
            "assessment_drafts": [
                {
                    "assessment_key": "a1",
                    "lesson_key": "l1",
                    "learner_alias": "kg3-synthetic-1",
                    "no_live_learner_data": True,
                    "human_review_required": True,
                }
            ],
        }

        # empty lessons
        b0 = copy.deepcopy(base)
        b0["lesson_drafts"] = []
        p0 = tmp_path / "pr0.json"
        p0.write_text(json.dumps(b0), encoding="utf-8")
        with pytest.raises(ValueError, match="KG-6 requires KG-5 lesson and assessment drafts"):
            kg_prod.build_product_alignment_pack(p0)

        # lesson has live data
        b1 = copy.deepcopy(base)
        b1["lesson_drafts"][0]["no_live_learner_data"] = False
        p1 = tmp_path / "pr1.json"
        p1.write_text(json.dumps(b1), encoding="utf-8")
        with pytest.raises(ValueError, match="no-live-data, review-gated lesson drafts"):
            kg_prod.build_product_alignment_pack(p1)

        # missing assessment draft
        b2 = copy.deepcopy(base)
        b2["assessment_drafts"] = []
        p2 = tmp_path / "pr2.json"
        p2.write_text(json.dumps(b2), encoding="utf-8")
        with pytest.raises(ValueError, match="has no assessment draft"):
            kg_prod.build_product_alignment_pack(p2)

        # assessment has live data
        b3 = copy.deepcopy(base)
        b3["assessment_drafts"][0]["no_live_learner_data"] = False
        p3 = tmp_path / "pr3.json"
        p3.write_text(json.dumps(b3), encoding="utf-8")
        with pytest.raises(ValueError, match="no-live-data, review-gated assessment drafts"):
            kg_prod.build_product_alignment_pack(p3)

    def test_validate_product_alignment_pack_error_branches(self):
        valid = kg_prod.build_product_alignment_pack()
        res = kg_prod.validate_product_alignment_pack(valid)
        assert res["valid"] is True

        bad = copy.deepcopy(valid)
        bad["tutor_previews"][0]["learner_alias"] = "real_live_learner_999"
        bad["study_plan_items"][0]["human_review_required"] = False
        bad["gamification_award_candidates"][0]["advisory_only"] = False
        bad["product_alignment_edges"][0]["source_key"] = "orphan-source-key"

        bad_res = kg_prod.validate_product_alignment_pack(bad)
        assert bad_res["valid"] is False
        assert len(bad_res["errors"]) >= 1
