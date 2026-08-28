"""Comprehensive unit tests for ContentScopeRegistry queries and validations."""
from __future__ import annotations

import pytest

from app.services.content_scope_registry import (
    ContentScopeRegistryError,
    ContentScopeRegistry,
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
            assert registry.is_scope_active(first_scope.scope_id) == (fetched.status == "active")

    def test_get_unknown_scope_raises_lookup_error(self):
        registry = ContentScopeRegistry()
        with pytest.raises(LookupError, match="Unknown content scope"):
            registry.get_scope("non_existent_scope_12345")
