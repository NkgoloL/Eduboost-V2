"""Comprehensive unit tests for ContentScopeRegistry queries and validations."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.domain.content_coverage import ContentLayer
from app.domain.content_scope import ContentScopeStatus
from app.services.content_scope_registry import (
    ContentScopeRegistry,
    ContentScopeRegistryError,
)


class TestContentScopeRegistry:
    def test_registry_error_exception_type(self):
        err = ContentScopeRegistryError("Inconsistent scope data")
        assert isinstance(err, ValueError)
        assert str(err) == "Inconsistent scope data"

    def test_registry_list_and_query_scopes(self):
        registry = ContentScopeRegistry()
        scopes = registry.list_scopes()
        assert isinstance(scopes, list)
        assert len(scopes) > 0

        active_scopes = registry.list_active_scopes()
        assert isinstance(active_scopes, list)

    def test_get_known_scope(self):
        registry = ContentScopeRegistry()
        scopes = registry.list_scopes()
        if scopes:
            first_scope = scopes[0]
            fetched = registry.get_scope(first_scope.scope_id)
            assert fetched.scope_id == first_scope.scope_id
            assert registry.is_scope_active(first_scope.scope_id) == (fetched.status == ContentScopeStatus.ACTIVE)

    def test_get_unknown_scope_raises_lookup_error(self):
        registry = ContentScopeRegistry()
        with pytest.raises(LookupError, match="Unknown content scope"):
            registry.get_scope("non_existent_scope_12345")

    def test_require_active_scope(self):
        registry = ContentScopeRegistry()
        active_scopes = registry.list_active_scopes()
        if active_scopes:
            scope = registry.require_active_scope(active_scopes[0].scope_id)
            assert scope.status == ContentScopeStatus.ACTIVE

        # Non-active scope -> LookupError
        with patch.object(registry, "get_scope", return_value=SimpleNamespace(status=ContentScopeStatus.DRAFT)):
            with pytest.raises(LookupError, match="is not active"):
                registry.require_active_scope("draft_scope")

    def test_get_scope_targets_and_coverage_target(self):
        registry = ContentScopeRegistry()
        active_scopes = registry.list_active_scopes()
        if active_scopes:
            scope_id = active_scopes[0].scope_id
            caps_refs = registry.get_scope_caps_refs(scope_id)
            assert isinstance(caps_refs, list)

            targets = registry.get_scope_targets(scope_id)
            assert isinstance(targets, list)
            if targets:
                target = targets[0]
                val = registry.get_coverage_target(target.scope_id, target.caps_ref, ContentLayer.LESSONS)
                assert isinstance(val, int)

    def test_coverage_target_errors(self):
        registry = ContentScopeRegistry()
        with pytest.raises(LookupError, match="No coverage target"):
            registry._get_target("grade4_mathematics_en", "NON_EXISTENT_CAPS_REF")

        mock_target = SimpleNamespace(targets={})
        with patch.object(registry, "_get_target", return_value=mock_target):
            with pytest.raises(LookupError, match="No coverage target for"):
                registry.get_coverage_target("s1", "ref1", ContentLayer.LESSONS)

    def test_validate_scope_topic_maps_validation_errors(self, tmp_path: Path):
        registry = ContentScopeRegistry(project_root=tmp_path)

        # 1. Active scope missing topic_map_path
        scope_no_path = SimpleNamespace(
            scope_id="s1",
            status=ContentScopeStatus.ACTIVE,
            topic_map_path=None,
            caps_refs=[],
        )
        with pytest.raises(ContentScopeRegistryError, match="must declare topic_map_path"):
            registry._validate_scope_topic_maps({"s1": scope_no_path})

        # 2. Scope declares caps_refs without topic_map_path
        scope_draft_refs = SimpleNamespace(
            scope_id="s2",
            status=ContentScopeStatus.DRAFT,
            topic_map_path=None,
            caps_refs=["4.MATH.1.1"],
        )
        with pytest.raises(ContentScopeRegistryError, match="declares CAPS refs without a topic_map_path"):
            registry._validate_scope_topic_maps({"s2": scope_draft_refs})

        # 3. Scope references CAPS refs not present in topic map file
        topic_file = tmp_path / "map.json"
        topic_file.write_text(json.dumps({"terms": [{"topics": [{"caps_ref": "4.MATH.1.1"}]}]}))

        scope_missing_ref = SimpleNamespace(
            scope_id="s3",
            status=ContentScopeStatus.ACTIVE,
            topic_map_path="map.json",
            caps_refs=["4.MATH.1.1", "4.MATH.1.2"],
        )
        with pytest.raises(ContentScopeRegistryError, match="references CAPS refs not present in"):
            registry._validate_scope_topic_maps({"s3": scope_missing_ref})

    def test_validate_targets_validation_errors(self, tmp_path: Path):
        registry = ContentScopeRegistry(project_root=tmp_path)

        # Target not in scope.caps_refs
        mock_scope = SimpleNamespace(
            scope_id="s1",
            caps_refs=["4.MATH.1.1"],
            topic_map_path="map.json",
        )
        with patch.object(registry, "get_scope", return_value=mock_scope):
            mock_target = SimpleNamespace(scope_id="s1", caps_ref="4.MATH.1.99")
            with pytest.raises(ContentScopeRegistryError, match="outside the declared scope refs"):
                registry._validate_targets([mock_target])

        # Scope missing topic_map_path
        mock_scope_no_map = SimpleNamespace(
            scope_id="s1",
            caps_refs=["4.MATH.1.1"],
            topic_map_path=None,
        )
        with patch.object(registry, "get_scope", return_value=mock_scope_no_map):
            mock_target = SimpleNamespace(scope_id="s1", caps_ref="4.MATH.1.1")
            with pytest.raises(ContentScopeRegistryError, match="requires a topic_map_path"):
                registry._validate_targets([mock_target])
