"""Batch 196: Unit tests for content_blueprint_validation and content_scope_registry services."""
import json
import tempfile
from pathlib import Path

import pytest

from app.services.content_blueprint_validation import (
    AssessmentBlueprintValidationService,
    BlueprintValidationResult,
)


# ─────────────────────────────────────────────
# BlueprintValidationResult
# ─────────────────────────────────────────────


class TestBlueprintValidationResult:
    def test_passed_is_true_when_no_errors(self):
        result = BlueprintValidationResult(passed=True, errors=[])
        assert result.passed is True
        assert result.errors == []

    def test_passed_is_false_when_errors_present(self):
        result = BlueprintValidationResult(passed=False, errors=["error 1"])
        assert result.passed is False
        assert len(result.errors) == 1

    def test_frozen_immutable(self):
        result = BlueprintValidationResult(passed=True, errors=[])
        with pytest.raises(Exception):
            result.passed = False


# ─────────────────────────────────────────────
# AssessmentBlueprintValidationService
# ─────────────────────────────────────────────


class TestAssessmentBlueprintValidationService:
    def _service(self) -> AssessmentBlueprintValidationService:
        return AssessmentBlueprintValidationService()

    def test_valid_blueprint_with_approved_items(self):
        blueprint = {
            "content_json": {"questions": []},
            "referenced_artifact_ids": ["item-1", "item-2"],
        }
        approved = {"item-1", "item-2"}
        result = self._service().validate(blueprint, approved)
        assert result.passed is True
        assert result.errors == []

    def test_valid_blueprint_json_field_accepted(self):
        blueprint = {
            "blueprint_json": {"questions": []},
            "referenced_artifact_ids": [],
        }
        result = self._service().validate(blueprint, approved_diagnostic_item_ids=set())
        assert result.passed is True

    def test_missing_content_and_blueprint_json_adds_error(self):
        blueprint = {"referenced_artifact_ids": []}
        result = self._service().validate(blueprint, approved_diagnostic_item_ids=set())
        assert result.passed is False
        assert any("content_json or blueprint_json" in e for e in result.errors)

    def test_unapproved_items_adds_error(self):
        blueprint = {
            "content_json": {"questions": [{"id": 1}]},  # non-empty so truthy
            "referenced_artifact_ids": ["item-unknown"],
        }
        approved = {"item-1"}
        result = self._service().validate(blueprint, approved)
        assert result.passed is False
        assert any("approved diagnostic items" in e for e in result.errors)
        assert "item-unknown" in result.errors[-1]

    def test_empty_blueprint_and_empty_approved_produces_errors(self):
        blueprint = {}
        result = self._service().validate(blueprint, approved_diagnostic_item_ids=set())
        # No content_json or blueprint_json
        assert result.passed is False
        assert len(result.errors) >= 1

    def test_multiple_unapproved_items_listed_sorted(self):
        blueprint = {
            "content_json": {},
            "referenced_artifact_ids": ["item-zzz", "item-aaa"],
        }
        approved = set()
        result = self._service().validate(blueprint, approved)
        assert result.passed is False
        # Both items should be in the error message
        assert "item-aaa" in result.errors[-1]
        assert "item-zzz" in result.errors[-1]
        # Errors should be sorted alphabetically
        assert result.errors[-1].index("item-aaa") < result.errors[-1].index("item-zzz")

    def test_no_referenced_items_with_content_json_passes(self):
        blueprint = {"content_json": {"q": []}}
        result = self._service().validate(blueprint, approved_diagnostic_item_ids=set())
        assert result.passed is True

    def test_partially_approved_items_fails(self):
        blueprint = {
            "content_json": {},
            "referenced_artifact_ids": ["item-1", "item-2", "item-3"],
        }
        approved = {"item-1"}
        result = self._service().validate(blueprint, approved)
        assert result.passed is False
        assert "item-2" in result.errors[-1]
        assert "item-3" in result.errors[-1]


# ─────────────────────────────────────────────
# ContentScopeRegistry — real data integration smoke test
# ─────────────────────────────────────────────


class TestContentScopeRegistry:
    """Smoke tests that load the real registry data files from the project."""

    def test_list_scopes_returns_list(self):
        from app.services.content_scope_registry import ContentScopeRegistry
        registry = ContentScopeRegistry()
        scopes = registry.list_scopes()
        assert isinstance(scopes, list)

    def test_list_active_scopes_subset_of_all(self):
        from app.services.content_scope_registry import ContentScopeRegistry
        registry = ContentScopeRegistry()
        all_scopes = registry.list_scopes()
        active = registry.list_active_scopes()
        assert len(active) <= len(all_scopes)

    def test_get_scope_known_scope_id(self):
        from app.services.content_scope_registry import ContentScopeRegistry
        registry = ContentScopeRegistry()
        scopes = registry.list_scopes()
        if not scopes:
            pytest.skip("No scopes defined")
        scope = registry.get_scope(scopes[0].scope_id)
        assert scope.scope_id == scopes[0].scope_id

    def test_get_scope_unknown_raises_lookup_error(self):
        from app.services.content_scope_registry import ContentScopeRegistry
        registry = ContentScopeRegistry()
        with pytest.raises(LookupError):
            registry.get_scope("nonexistent-scope-id-xyz")

    def test_validate_scope_exists_raises_for_unknown(self):
        from app.services.content_scope_registry import ContentScopeRegistry
        registry = ContentScopeRegistry()
        with pytest.raises(LookupError):
            registry.validate_scope_exists("totally-fake-scope")

    def test_require_active_scope_raises_for_inactive(self):
        from app.services.content_scope_registry import ContentScopeRegistry
        from app.domain.content_scope import ContentScopeStatus
        registry = ContentScopeRegistry()
        inactive = [s for s in registry.list_scopes() if s.status != ContentScopeStatus.ACTIVE]
        if not inactive:
            pytest.skip("No inactive scopes available")
        with pytest.raises(LookupError, match="not active"):
            registry.require_active_scope(inactive[0].scope_id)

    def test_require_active_scope_returns_scope_when_active(self):
        from app.services.content_scope_registry import ContentScopeRegistry
        registry = ContentScopeRegistry()
        active = registry.list_active_scopes()
        if not active:
            pytest.skip("No active scopes available")
        scope = registry.require_active_scope(active[0].scope_id)
        assert scope.scope_id == active[0].scope_id

    def test_is_scope_active_true_for_active(self):
        from app.services.content_scope_registry import ContentScopeRegistry
        registry = ContentScopeRegistry()
        active = registry.list_active_scopes()
        if not active:
            pytest.skip("No active scopes")
        assert registry.is_scope_active(active[0].scope_id) is True

    def test_get_scope_caps_refs_returns_list(self):
        from app.services.content_scope_registry import ContentScopeRegistry
        registry = ContentScopeRegistry()
        scopes = registry.list_scopes()
        if not scopes:
            pytest.skip("No scopes")
        refs = registry.get_scope_caps_refs(scopes[0].scope_id)
        assert isinstance(refs, list)
