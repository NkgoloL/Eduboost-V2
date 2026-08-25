"""
Unit tests for app.services.content_scope_registry:
  - ContentScopeRegistry via real data files
  - ContentScopeRegistryError
  - All public methods
"""
from __future__ import annotations

import pytest

from app.services.content_scope_registry import (
    ContentScopeRegistry,
    ContentScopeRegistryError,
)


@pytest.fixture(scope="module")
def registry() -> ContentScopeRegistry:
    """Use the actual data files bundled with the project."""
    return ContentScopeRegistry()


class TestContentScopeRegistry:
    def test_list_scopes_returns_list(self, registry):
        scopes = registry.list_scopes()
        assert isinstance(scopes, list)
        assert len(scopes) > 0

    def test_list_active_scopes_are_active(self, registry):
        active = registry.list_active_scopes()
        from app.domain.content_scope import ContentScopeStatus
        for scope in active:
            assert scope.status == ContentScopeStatus.ACTIVE

    def test_get_scope_known(self, registry):
        scopes = registry.list_scopes()
        first_scope = scopes[0]
        retrieved = registry.get_scope(first_scope.scope_id)
        assert retrieved.scope_id == first_scope.scope_id

    def test_get_scope_unknown_raises(self, registry):
        with pytest.raises(LookupError, match="Unknown content scope"):
            registry.get_scope("nonexistent_scope_12345")

    def test_is_scope_active_first_active_scope(self, registry):
        active = registry.list_active_scopes()
        if active:
            assert registry.is_scope_active(active[0].scope_id) is True

    def test_require_active_scope_succeeds(self, registry):
        active = registry.list_active_scopes()
        if active:
            scope = registry.require_active_scope(active[0].scope_id)
            assert scope is not None

    def test_get_scope_caps_refs_returns_list(self, registry):
        scopes = registry.list_scopes()
        first = scopes[0]
        refs = registry.get_scope_caps_refs(first.scope_id)
        assert isinstance(refs, list)

    def test_validate_scope_exists_does_not_raise(self, registry):
        scopes = registry.list_scopes()
        # Should not raise
        registry.validate_scope_exists(scopes[0].scope_id)

    def test_validate_scope_exists_unknown_raises(self, registry):
        with pytest.raises(LookupError):
            registry.validate_scope_exists("no_such_scope")

    def test_get_scope_targets_returns_list(self, registry):
        active = registry.list_active_scopes()
        if active:
            targets = registry.get_scope_targets(active[0].scope_id)
            assert isinstance(targets, list)


class TestContentScopeRegistryError:
    def test_is_value_error(self):
        err = ContentScopeRegistryError("duplicate scope_id")
        assert isinstance(err, ValueError)
        assert "duplicate scope_id" in str(err)
