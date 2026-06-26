from __future__ import annotations

import json
from pathlib import Path

from scripts.audit_remediation.verify_content_scope_registry_expansion import verify

ROOT = Path(__file__).resolve().parents[3]


def test_expanded_registry_has_expected_scope_count_and_visibility_boundary() -> None:
    result = verify(static_only=True)

    assert result["valid"] is True, result["errors"]
    assert result["scope_count"] == 51
    assert result["active_scopes"] == ["grade4_mathematics_en"]
    assert result["generation_ready_scope_count"] == 51
    assert result["staging_ready_scope_count"] == 51


def test_grade5_mathematics_is_review_scope_not_learner_visible() -> None:
    raw = json.loads((ROOT / "data/content_factory/scopes.json").read_text(encoding="utf-8"))
    grade5 = next(scope for scope in raw["scopes"] if scope["scope_id"] == "grade5_mathematics_en")

    assert grade5["status"] == "review"
    assert grade5["topic_map_path"] == "data/caps/topic_maps/grade5_mathematics_en.json"
    assert len(grade5["caps_refs"]) == 16
    assert set(grade5["artifact_paths"]) == {
        "diagnostic_items",
        "lessons",
        "assessment_blueprints",
        "study_plan_templates",
    }


def test_grade4_launch_scope_remains_the_only_active_scope() -> None:
    raw = json.loads((ROOT / "data/content_factory/scopes.json").read_text(encoding="utf-8"))
    active = [scope for scope in raw["scopes"] if scope["status"] == "active"]

    assert [scope["scope_id"] for scope in active] == ["grade4_mathematics_en"]
    assert active[0]["caps_refs"] == ["4.M.1.1", "4.M.1.2", "4.M.1.3"]


def test_scope_registry_import_contract_accepts_expanded_registry() -> None:
    result = verify(static_only=False)

    assert result["valid"] is True, result["errors"]
    assert result["registry_import_valid"] is True
