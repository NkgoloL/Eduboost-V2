from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.domain.content_coverage import ContentLayer
from app.services.content_scope_registry import ContentScopeRegistry, ContentScopeRegistryError


pytestmark = pytest.mark.unit


def test_loads_grade4_mathematics_launch_scope() -> None:
    scope = ContentScopeRegistry().get_scope("grade4_mathematics_en")

    assert scope.grade == 4
    assert scope.subject == "Mathematics"
    assert scope.language == "en"
    assert scope.curriculum == "CAPS"
    assert scope.status.value == "active"
    assert scope.caps_refs == ["4.M.1.1", "4.M.1.2", "4.M.1.3"]


def test_rejects_unknown_scope_id() -> None:
    with pytest.raises(LookupError, match="Unknown content scope"):
        ContentScopeRegistry().get_scope("grade9_science_en")


def test_returns_deterministic_scope_list_ordering(tmp_path: Path) -> None:
    scopes_path = tmp_path / "scopes.json"
    targets_path = tmp_path / "targets.json"
    topic_map_path = tmp_path / "topic_map.json"
    topic_map_path.write_text(_topic_map_json(["4.M.1.1"]), encoding="utf-8")
    scopes_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "scopes": [
                    _scope("z_scope", topic_map_path, ["4.M.1.1"]),
                    _scope("a_scope", topic_map_path, ["4.M.1.1"]),
                ],
            }
        ),
        encoding="utf-8",
    )
    targets_path.write_text(json.dumps({"schema_version": "1.0", "targets": []}), encoding="utf-8")

    registry = ContentScopeRegistry(scopes_path=scopes_path, targets_path=targets_path, project_root=tmp_path)

    assert [scope.scope_id for scope in registry.list_scopes()] == ["a_scope", "z_scope"]


def test_returns_coverage_target_for_diagnostic_items_and_lessons() -> None:
    registry = ContentScopeRegistry()

    assert registry.get_coverage_target("grade4_mathematics_en", "4.M.1.1", ContentLayer.DIAGNOSTIC_ITEMS) == 40
    assert registry.get_coverage_target("grade4_mathematics_en", "4.M.1.1", ContentLayer.LESSONS) == 8


def test_missing_caps_ref_target_raises_lookup_error() -> None:
    with pytest.raises(LookupError, match="No coverage target"):
        ContentScopeRegistry().get_coverage_target(
            "grade4_mathematics_en",
            "4.M.9.9",
            ContentLayer.DIAGNOSTIC_ITEMS,
        )


def test_validates_every_target_caps_ref_belongs_to_scope_topic_map(tmp_path: Path) -> None:
    scopes_path = tmp_path / "scopes.json"
    targets_path = tmp_path / "targets.json"
    topic_map_path = tmp_path / "topic_map.json"
    topic_map_path.write_text(_topic_map_json(["4.M.1.1"]), encoding="utf-8")
    scopes_path.write_text(
        json.dumps({"schema_version": "1.0", "scopes": [_scope("scope", topic_map_path, ["4.M.1.1"])]}),
        encoding="utf-8",
    )
    targets_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "targets": [
                    {
                        "scope_id": "scope",
                        "caps_ref": "4.M.9.9",
                        "targets": {"diagnostic_items.approved": 40},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    registry = ContentScopeRegistry(scopes_path=scopes_path, targets_path=targets_path, project_root=tmp_path)

    with pytest.raises(ContentScopeRegistryError, match="outside the declared scope refs"):
        registry.get_scope_targets("scope")


def _scope(scope_id: str, topic_map_path: Path, caps_refs: list[str]) -> dict[str, object]:
    return {
        "scope_id": scope_id,
        "grade": 4,
        "subject_code": "M",
        "subject": "Mathematics",
        "language": "en",
        "curriculum": "CAPS",
        "status": "active",
        "topic_map_path": topic_map_path.name,
        "caps_refs": caps_refs,
    }


def _topic_map_json(caps_refs: list[str]) -> str:
    topics = [{"caps_ref": caps_ref, "topic_index": index, "topic": caps_ref, "subtopics": []} for index, caps_ref in enumerate(caps_refs, 1)]
    return json.dumps(
        {
            "_meta": {"schema_version": "1.0", "scope": "test", "source": "test"},
            "grade": 4,
            "subject": "Mathematics",
            "subject_code": "M",
            "terms": [{"term": 1, "weeks": "1", "topics": topics}],
        }
    )
